# Jetson AGX Orin — Setup from Scratch

Complete guide for setting up the Jetson AGX Orin with NVMe boot and all software for the autonomous kart.

## Hardware Overview

| Component | Value |
|---|---|
| Board | NVIDIA Jetson AGX Orin Developer Kit |
| Architecture | aarch64 (ARM64), 12 CPU cores, 62 GB RAM |
| GPU | Ampere (CUDA 12.6) |
| Storage | 57 GB eMMC (soldered) + 476 GB NVMe M.2 SSD |
| Display | **DisplayPort only** (no HDMI). Requires DP-to-HDMI adapter |
| Camera | ZED 2 stereo (USB) |
| ESP32 link | USB serial to the Kart Medulla ESP32 (no CAN — see note) |

!!! warning "No CAN bus on the kart"
    The kart has **no CAN bus anywhere**. The Orin talks to the Kart Medulla ESP32 over **USB serial** (a plain USB cable presenting a serial port), and the ZED camera is USB too. Sensors reach the ESP32 as analog signals or I²C, not CAN. Earlier versions of this page listed `can0`/`can1` for ESP32 communication — that was wrong.

    CAN only enters the picture on the **Formula Student car**, where it becomes the vehicle bus (a CAN-reader PCB for the Orin exists for that integration). Adding CAN to the kart would only introduce transceivers, drivers, and an extra encode/decode hop for no benefit. If you find CAN setup steps (`can0`/`can1`, `ip link set canX`, SocketCAN) anywhere in the kart docs or configs, they do not apply to the kart. Source: `dv/history.md` 2026-07-14 "The kart uses no CAN"; `kart-brain/README.md` (ESP32 over UART/USB).

## Boot Chain

The Orin uses three storage devices to boot:

```
QSPI flash (on-chip)     →  First-stage bootloader (firmware)
eMMC (57 GB, soldered)    →  Second-stage bootloader + boot partition
NVMe M.2 SSD (476 GB)    →  Ubuntu root filesystem (where the OS lives)
```

**Boot sequence:** QSPI → eMMC bootloader → NVMe root filesystem

- **QSPI**: Tiny on-chip flash. Holds the first code the CPU runs at power-on.
- **eMMC**: Internal storage soldered to the board. After NVMe flash, it only holds a small bootloader — not a full OS.
- **NVMe**: The M.2 SSD plugged into the board. This is where Ubuntu and all software lives, with ~435 GB available.

The flash tool writes to all three. This is expected.

!!! tip "Verify NVMe boot"
    After setup, `df -h /` should show `/dev/nvme0n1p1`, NOT `/dev/mmcblk0p1`.

## Software Stack

| Software | Version | Installed via |
|---|---|---|
| JetPack | 6.2.2 (L4T R36.5) | Flash (see below) |
| Ubuntu | 22.04 | Flash |
| CUDA | 12.6 | `sudo apt install nvidia-jetpack` |
| cuDNN | 9.x | `sudo apt install nvidia-jetpack` |
| TensorRT | 10.x | `sudo apt install nvidia-jetpack` |
| ROS 2 | Humble | apt (ROS 2 repos) |
| ZED SDK | 4.2 | Installer from Stereolabs (L4T 36.4 build, compatible with 36.5) |
| PyTorch | 2.5.0 (Jetson build) | NVIDIA Jetson AI Lab wheels |
| Python | 3.10 (system) | Pre-installed |

!!! note "Why ZED SDK 4.2 and not 5.2?"
    ZED SDK 5.2 does not provide a build for L4T 36.5 as of February 2026. The 4.2 build for L4T 36.4 installs successfully on L4T 36.5 with a compatibility warning. Upgrade when a 5.2 build for L4T 36.5 becomes available.

!!! note "Why JetPack 6.2.2 and not JetPack 7?"
    JetPack 7 does not support AGX Orin as of February 2026. Only the newer Jetson Thor family is supported. Orin support is expected in JetPack 7.2 (Q2 2026). Our full stack (ROS 2 Humble, ZED SDK, PyTorch, YOLOv5) is confirmed compatible with JetPack 6.2.2.

## Flashing to NVMe

### What you need

- **Flash host**: x86_64 Linux machine (Ubuntu 22.04 or 24.04). We use the y540 laptop.
- **USB-C cable**: Data-capable (not charge-only)
- **Monitor + keyboard**: For the first-boot setup wizard

### Step 1: Prepare the flash host

```bash
# Install dependencies
sudo apt-get install -y abootimg binfmt-support binutils cpio cpp \
  device-tree-compiler dosfstools lbzip2 libxml2-utils nfs-kernel-server \
  python3-yaml sshpass udev

# Download L4T R36.5 BSP and root filesystem (~2.4 GB total)
mkdir -p ~/jetson-flash && cd ~/jetson-flash
wget https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v5.0/release/Jetson_Linux_r36.5.0_aarch64.tbz2
wget https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v5.0/release/Tegra_Linux_Sample-Root-Filesystem_r36.5.0_aarch64.tbz2

# Extract
tar xf Jetson_Linux_r36.5.0_aarch64.tbz2
sudo tar xpf Tegra_Linux_Sample-Root-Filesystem_r36.5.0_aarch64.tbz2 -C Linux_for_Tegra/rootfs/
cd Linux_for_Tegra/
sudo ./tools/l4t_flash_prerequisites.sh
sudo ./apply_binaries.sh
```

### Step 2: Put the Orin in Recovery Mode

Connect the USB-C cable from the flash host to the Orin's **flashing port** (the USB-C port next to the 40-pin GPIO header, NOT the power port).

**If the Orin is powered off:**

1. Press and hold the **Force Recovery button** (middle button)
2. Power on (press the Power button)
3. Release both buttons after ~2 seconds

**If the Orin is powered on:**

1. Press and hold the **Force Recovery button** (middle button)
2. Press and release the **Reset button** (leftmost button)
3. Release the Force Recovery button after ~2 seconds

**Verify** on the flash host:

```bash
lsusb | grep -i nvidia
# Should show: 0955:7023 NVIDIA Corp. APX  (recovery mode)
# NOT: 0955:7020  (normal mode)
```

### Step 3: Flash

```bash
cd ~/jetson-flash/Linux_for_Tegra

sudo ./tools/kernel_flash/l4t_initrd_flash.sh \
  --external-device nvme0n1p1 \
  -c tools/kernel_flash/flash_l4t_t234_nvme.xml \
  --showlogs \
  -p "-c bootloader/generic/cfg/flash_t234_qspi.xml" \
  --network usb0 \
  jetson-agx-orin-devkit \
  nvme0n1p1
```

This takes ~10-20 minutes. The output ends with `Flash is successful`.

### Step 4: First boot

!!! warning "First boot takes time"
    After flash, the Orin takes ~5 minutes with no display signal while initializing. If no signal after 5 minutes, power cycle (hold power button 5 seconds, then press again). After power cycle, BIOS appears in seconds, then Ubuntu boots in ~2 minutes. There may be brief periods of no signal during boot — this is normal.

Complete the Ubuntu setup wizard:

- Username: `orin`
- Password: See `.env` file (not committed — ask the team)
- Computer name: `orin`

## Post-Flash Setup

!!! warning "Credentials required"
    Several steps below need passwords that are **not committed to this repo**. Copy `.env.example` to `.env` and fill in the values before starting. Ask the team if you don't have them.

### Connect to WiFi

Connect to the university network during the first-boot wizard or from Settings:

| Field | Value |
|---|---|
| Network | `Robots_urjc` |
| Password | See `.env` file (not committed — ask the team) |

### Software Installation

### 1. Set power mode

The Orin defaults to 30W. Switch to 50W for full performance (requires reboot):

```bash
sudo nvpmodel -m 3   # MODE_50W (type "yes" when prompted to reboot)
```

After reboot, verify: `sudo nvpmodel -q` → `MODE_50W`.

### 2. JetPack SDK (CUDA, cuDNN, TensorRT)

JetPack comes pre-installed with the flash. Add CUDA to your PATH:

```bash
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
nvcc --version   # Should show CUDA 12.6
dpkg -l | grep tensorrt   # Should show TensorRT 10.x
```

### 3. Max clocks on boot

By default the Orin throttles CPU/GPU clocks to save power. `jetson_clocks` unlocks maximum frequency — essential for real-time YOLO inference (~75 Hz vs ~39 Hz without it).

```bash
# Run now
sudo jetson_clocks

# Persist across reboots
sudo tee /etc/systemd/system/jetson-clocks.service > /dev/null << 'EOF'
[Unit]
Description=Maximize Jetson clocks
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/jetson_clocks

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable jetson-clocks
```

### 4. ROS 2 Humble

```bash
sudo apt install -y software-properties-common curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt-get update
sudo apt-get install -y ros-humble-desktop ros-humble-vision-msgs ros-dev-tools
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

### 5. ZED SDK

```bash
cd /tmp
wget -q "https://download.stereolabs.com/zedsdk/4.2/l4t36.4/jetsons" -O ZED_SDK.run
chmod +x ZED_SDK.run
./ZED_SDK.run -- silent skip_tools skip_samples
```

Install the JPEG dependency needed by the ZED ROS wrapper:

```bash
sudo apt-get install -y libturbojpeg0-dev
```

After installing, add the `orin` user to the `zed` and `dialout` groups (SDK access + serial port):

```bash
sudo usermod -aG zed,dialout orin
```

Log out and back in (or reboot) for the group to take effect.

### 6. PyTorch

!!! warning "Use `--index-url`, not `--extra-index-url`"
    Using `--extra-index-url` may pull the CPU-only wheel from PyPI instead of the Jetson CUDA build. Use `--index-url` to prioritize the Jetson index.

```bash
pip3 install --no-cache-dir \
  --index-url https://pypi.jetson-ai-lab.dev/jp6/cu126 \
  --extra-index-url https://pypi.org/simple \
  torch torchvision
pip3 install --no-cache-dir 'numpy<2' ultralytics pyyaml
```

PyTorch on Jetson needs NVIDIA shared libraries in `LD_LIBRARY_PATH`:

```bash
echo 'export LD_LIBRARY_PATH=$HOME/.local/lib/python3.10/site-packages/nvidia/cusparselt/lib:$HOME/.local/lib/python3.10/site-packages/nvidia/nvjitlink/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available())"
# Should show: 2.5.0a0+... True
```

!!! warning "numpy must be < 2"
    OpenCV on the Jetson was compiled against numpy 1.x. Installing numpy 2 will break `cv2`.

### 7. Export YOLO TensorRT engine

The YOLO model ships as a `.pt` (PyTorch) file. For real-time inference on the Orin, export it to a TensorRT `.engine` file (takes ~3-4 minutes, only needed once per model):

```bash
cd ~/kart-brain
python3 -c "from ultralytics import YOLO; m = YOLO('models/perception/yolo/ruben_yolov11n_2026_03.pt'); m.export(format='engine', imgsz=320, half=True)"
```

Rename the output to include the hardware and TensorRT version:

```bash
mv models/perception/yolo/ruben_yolov11n_2026_03_320.engine \
   models/perception/yolo/ruben_yolov11n_2026_03_320_orin_trt10.engine
```

!!! warning "Always export with `half=True`"
    FP16 inference is ~2x faster than FP32 on the Orin's Ampere GPU. Never export without `half=True`.

This `.engine` file is committed to the repo. Re-export when the model changes or after a CUDA/TensorRT upgrade.

### 8. Clone repositories

```bash
cd ~
git clone https://github.com/UM-Driverless/kart-brain.git
git clone https://github.com/UM-Driverless/kart-medulla.git
```

### 9. Build kart-brain

First install all ROS 2 dependencies automatically:

```bash
cd ~/kart-brain
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

Then build (always use `--symlink-install` so Python/launch file edits take effect without rebuilding):

```bash
colcon build --symlink-install
echo "source ~/kart-brain/install/setup.bash" >> ~/.bashrc
```

See the [kart-brain repo](https://github.com/UM-Driverless/kart-brain) for package details and usage.

### 10. PlatformIO (ESP32 flashing)

Install PlatformIO to flash [kart-medulla](https://github.com/UM-Driverless/kart-medulla) firmware to the ESP32 directly from the Orin:

```bash
pip3 install platformio
```

Flash the firmware (ESP32 must be connected via USB):

```bash
cd ~/kart-medulla
# Legacy hand-wired classic ESP32 (currently in the kart):
pio run --target upload --environment esp32dev

# Next-revision ESP32-S3 PCB (once firmware migrates):
pio run --target upload --environment esp32-s3-devkitc-1
```

!!! note "ESP32 bootloader mode"
    If flashing the classic ESP32 hangs at "Connecting...", put it in bootloader mode: hold **BOOT**, press **EN**, release **BOOT**. The ESP32-S3 has built-in USB-Serial-JTAG and typically does not need this.

### 11. AnyDesk (remote desktop)

```bash
curl -fsSL https://keys.anydesk.com/repos/DEB-GPG-KEY \
  | sudo gpg --dearmor -o /usr/share/keyrings/anydesk-archive-keyring.gpg
echo "deb [arch=arm64 signed-by=/usr/share/keyrings/anydesk-archive-keyring.gpg] \
  http://deb.anydesk.com/ all main" \
  | sudo tee /etc/apt/sources.list.d/anydesk-stable.list > /dev/null
sudo apt-get update
sudo apt-get install -y anydesk
```

After installing AnyDesk, configure Xorg for headless operation (no physical monitor):

```bash
sudo mkdir -p /etc/X11/xorg.conf.d
sudo tee /etc/X11/xorg.conf.d/10-virtual-display.conf > /dev/null << 'EOF'
Section "Device"
    Identifier "Tegra"
    Driver "nvidia"
    Option "AllowEmptyInitialConfiguration" "true"
    Option "ConnectedMonitor" "DFP-0"
EndSection

Section "Screen"
    Identifier "Default Screen"
    Device "Tegra"
    DefaultDepth 24
    SubSection "Display"
        Depth 24
        Virtual 1920 1080
    EndSubSection
EndSection
EOF
sudo systemctl enable anydesk
```

Set a password for unattended access (so you can connect without anyone at the screen):

```bash
echo "$ANYDESK_PASSWORD" | sudo anydesk --set-password
```

Get the AnyDesk ID (share this with the team):

```bash
anydesk --get-id
```

After reboot, the display may default to 1024x768. Set 1600x900 (max supported by the dummy plug):

```bash
DISPLAY=:0 xrandr --output DP-0 --mode 1600x900
```

!!! note "Why `ConnectedMonitor DFP-0`?"
    The DP-to-HDMI adapter with a dummy HDMI plug doesn't provide proper EDID. Without this option, the NVIDIA driver sees both DFP-0 and DFP-1 as "disconnected", so Xorg has no screen and AnyDesk gets a black framebuffer. Forcing `ConnectedMonitor DFP-0` makes the driver create a framebuffer on the DisplayPort output regardless. The dummy plug caps resolution at 1600x900.

### 12. Disable WiFi Power Saving

WiFi power management causes intermittent SSH dropouts — the kernel puts the adapter to sleep under load. Disable it permanently:

```bash
# Disable now
sudo iw dev wlP1p1s0 set power_save off

# Persist across reboots (runs on every WiFi connect)
echo '#!/bin/bash
iw dev wlP1p1s0 set power_save off' | sudo tee /etc/NetworkManager/dispatcher.d/99-wifi-powersave-off
sudo chmod +x /etc/NetworkManager/dispatcher.d/99-wifi-powersave-off
```

!!! note "Interface name"
    The WiFi interface is `wlP1p1s0` on the AGX Orin (not `wlan0`). Verify with `ip link show`.

### 13. Cloudflare Tunnel (remote SSH from anywhere)

This lets anyone on the team SSH into the Orin from outside the university network — no open ports, no VPN.

#### On the Orin

```bash
# Install cloudflared (ARM64)
wget -O /tmp/cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i /tmp/cloudflared.deb

# Authenticate with Cloudflare (opens a browser — select the rubenayla.xyz zone)
cloudflared tunnel login

# Create the tunnel and DNS route
cloudflared tunnel create orin
cloudflared tunnel route dns orin orin.rubenayla.xyz
cloudflared tunnel route dns orin kart.rubenayla.xyz
```

Then create the config file. Replace `TUNNEL_ID` with the ID printed by `tunnel create`:

```bash
sudo mkdir -p /etc/cloudflared
sudo tee /etc/cloudflared/config.yml > /dev/null << EOF
tunnel: TUNNEL_ID
credentials-file: /etc/cloudflared/TUNNEL_ID.json

ingress:
  - hostname: orin.rubenayla.xyz
    service: ssh://localhost:22
  - hostname: kart.rubenayla.xyz
    service: http://localhost:9090
  - service: http_status:404
EOF

# Copy credentials to the system config directory
sudo cp ~/.cloudflared/TUNNEL_ID.json /etc/cloudflared/

# Install and start as a system service
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

#### On each team member's machine

1. Install `cloudflared`:
    - macOS: `brew install cloudflared`
    - Ubuntu/Debian: `wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared-linux-amd64.deb`
    - Windows: `winget install Cloudflare.cloudflared`

2. Create the sockets directory and add to `~/.ssh/config`:
    ```bash
    mkdir -p ~/.ssh/sockets
    ```
    ```
    Host orin-remote
        HostName orin.rubenayla.xyz
        User orin
        IdentityFile ~/.ssh/id_ed25519
        ProxyCommand cloudflared access ssh --hostname %h
        ControlMaster auto
        ControlPath ~/.ssh/sockets/%r@%h-%p
        ControlPersist 10m
    ```

    `ControlMaster` reuses a single SSH connection for all sessions — subsequent commands connect in ~50ms instead of ~400ms.

3. Send their public key (`cat ~/.ssh/id_ed25519.pub`) to be added to the Orin's `~/.ssh/authorized_keys`.

No Cloudflare account needed for team members — only the tunnel owner.

!!! tip "Generate an SSH key if you don't have one"
    ```bash
    ssh-keygen -t ed25519
    ```

### 14. Wi-Fi access-point mode (`kart-ap`)

Since 2026-07-06 the Orin boots as **its own Wi-Fi access point** instead of joining lab Wi-Fi. Phones and laptops connect directly to the kart's own network and reach the dashboard at a fixed address — no router, no venue Wi-Fi, no IP hunting in the middle of a field.

| Field | Value |
|---|---|
| Connection name (NetworkManager) | `kart-ap` |
| SSID | `kart` |
| Host IP (dashboard) | `http://10.42.0.1` |
| Autoconnect priority | 200 (wins over `Robots_urjc`, which is 10) |

The Orin's single Wi-Fi radio can hold **one** Wi-Fi connection at a time — either it joins an existing network for internet, or it serves its own AP. Access-point mode is a **NetworkManager hotspot** (shared mode): NetworkManager runs DHCP + NAT and places the host at its default shared-subnet address `10.42.0.1`. A quick one-off hotspot on the Orin looks like:

```bash
# wlP1p1s0 is the Orin's Wi-Fi interface (see step 12; NOT wlan0)
nmcli dev wifi hotspot ifname wlP1p1s0 ssid kart password <pw>
```

The deployed setup makes this a persistent connection profile named `kart-ap` with `autoconnect-priority 200`, so it comes up automatically at boot. A second phone joins SSID `kart` and opens `http://10.42.0.1` for the dashboard.

!!! note "Internet while in AP mode (optional)"
    Because the radio is busy serving the AP, the Orin has no internet from Wi-Fi. To give it internet anyway, plug a phone into the Orin over USB with USB tethering on — it appears as a `usb0` interface and carries the connection over the cable, leaving the radio free for the AP. NetworkManager shared mode NATs, so a dashboard phone on the AP can even reach the internet through the Orin → cable → tethering-phone chain. Source: `dv/tasks/usb-tethering-dashboard.md`, `dv/README.md`, `dv/history.md` 2026-07-06/07-14.

## Verification Checklist

- [ ] Power mode: `sudo nvpmodel -q` → `MODE_50W`
- [ ] Max clocks: `sudo jetson_clocks` and service enabled
- [ ] NVMe is root: `df -h /` shows `/dev/nvme0n1p1`
- [ ] CUDA: `nvcc --version` → 12.6
- [ ] TensorRT: `dpkg -l | grep tensorrt` → 10.x
- [ ] PyTorch GPU: `python3 -c "import torch; print(torch.cuda.is_available())"` → True
- [ ] ROS 2: `ros2 --help`
- [ ] ZED camera: `ls /dev/video*` (after plugging in)
- [ ] kart-brain built: `ros2 pkg list | grep kart`
- [ ] SSH access: `ssh orin` from Mac
- [ ] AnyDesk: working with dummy HDMI plug, unattended password set
- [ ] Cloudflare Tunnel: `ssh orin-remote` works from outside the network
- [ ] Dashboard: [kart.rubenayla.xyz](https://kart.rubenayla.xyz) loads and accepts password
- [ ] WiFi power save off: `iw dev wlP1p1s0 get power_save` → `Power save: off`
- [ ] Access point: SSID `kart` is broadcast and `http://10.42.0.1` loads the dashboard from a phone

## Network Access

| Method | Address | Notes |
|---|---|---|
| Kart access point | Join Wi-Fi `kart`, open `http://10.42.0.1` | Default field method. Orin is its own AP (`kart-ap`) — no router needed |
| SSH (local WiFi) | `ssh orin` (10.7.20.x, DHCP) | Only if the Orin is joined to lab Wi-Fi instead of AP mode. IP may change |
| SSH (remote) | `ssh orin-remote` (via Cloudflare Tunnel) | Works from anywhere. Requires `cloudflared` installed locally |
| Dashboard (local) | `http://<orin-ip>:9090` | Must be on same network |
| Dashboard (remote) | [kart.rubenayla.xyz](https://kart.rubenayla.xyz) (via Cloudflare Tunnel) | Works from any network. Password required (default: `0`) |
| AnyDesk | Via ID (see `.env` for password) | Needs dummy HDMI plug for display |

!!! tip "Always verify IPs"
    The university network uses DHCP. Run `hostname -I` on the Orin to get the current IP. Update `~/.ssh/config` if it changed.

## Known Issues

| Issue | Workaround |
|---|---|
| ZED "CAMERA NOT DETECTED" | Kill all stale ROS processes (`sudo killall -9 component_container_isolated`), clean shared memory (`rm -rf /dev/shm/fastrtps_*`), then relaunch. Do NOT unplug the camera. |
| torch `libcusparseLt.so.0` not found | Add NVIDIA pip package libs to `LD_LIBRARY_PATH` (done in step 5) |
| PyTorch installs CPU-only wheel | Use `--index-url` (not `--extra-index-url`) for the Jetson AI Lab index (see step 5) |
| numpy >= 2 breaks cv2 | Pin to `numpy<2` |
| ZED SDK not readable by `orin` user | Add `orin` to `zed` group: `sudo usermod -aG zed orin` (done in step 4) |
| AnyDesk resolution too low | Run `DISPLAY=:0 xrandr --output DP-0 --mode 1600x900` after reboot |
| No HDMI port | Use DP-to-HDMI adapter + dummy HDMI plug for headless AnyDesk |
