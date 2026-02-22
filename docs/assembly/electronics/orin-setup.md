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
| CAN bus | `can0`, `can1` (for ESP32 communication) |

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
| PyTorch | 2.10 | NVIDIA Jetson AI Lab wheels |
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
- Password: `0`
- Computer name: `orin`

## Post-Flash Software Installation

After the first-boot wizard, install everything:

### 1. JetPack SDK (CUDA, cuDNN, TensorRT)

```bash
sudo apt-get update
sudo apt-get install -y nvidia-jetpack
```

This is a large install (~5-7 GB). Verify:

```bash
nvcc --version   # Should show CUDA 12.6
dpkg -l | grep tensorrt   # Should show TensorRT 10.x
```

### 2. ROS 2 Humble

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

### 3. ZED SDK

```bash
cd /tmp
wget -q "https://download.stereolabs.com/zedsdk/4.2/l4t36.4/jetsons" -O ZED_SDK.run
chmod +x ZED_SDK.run
./ZED_SDK.run -- silent skip_tools skip_samples
```

### 4. PyTorch

```bash
pip3 install --no-cache-dir \
  --extra-index-url https://pypi.jetson-ai-lab.dev/jp6/cu126 \
  torch torchvision
pip3 install --no-cache-dir 'numpy<2' ultralytics pyyaml
```

!!! warning "numpy must be < 2"
    OpenCV on the Jetson was compiled against numpy 1.x. Installing numpy 2 will break `cv2`.

### 5. Clone and build kart_brain

```bash
cd ~
git clone git@github.com:UM-Driverless/kart_brain.git
cd kart_brain
source /opt/ros/humble/setup.bash
colcon build
echo "source ~/kart_brain/install/setup.bash" >> ~/.bashrc
```

### 6. AnyDesk (remote desktop)

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

!!! note "Why `ConnectedMonitor DFP-0`?"
    The DP-to-HDMI adapter with a dummy HDMI plug doesn't provide proper EDID. Without this option, the NVIDIA driver sees both DFP-0 and DFP-1 as "disconnected", so Xorg has no screen and AnyDesk gets a black framebuffer. Forcing `ConnectedMonitor DFP-0` makes the driver create a framebuffer on the DisplayPort output regardless.

## Verification Checklist

- [ ] NVMe is root: `df -h /` shows `/dev/nvme0n1p1`
- [ ] CUDA: `nvcc --version` → 12.6
- [ ] TensorRT: `dpkg -l | grep tensorrt` → 10.x
- [ ] PyTorch GPU: `python3 -c "import torch; print(torch.cuda.is_available())"` → True
- [ ] ROS 2: `ros2 --help`
- [ ] ZED camera: `ls /dev/video*` (after plugging in)
- [ ] kart_brain built: `ros2 pkg list | grep kart`
- [ ] SSH access: `ssh orin` from Mac
- [ ] AnyDesk: working with dummy HDMI plug

## Network Access

| Method | Address | Notes |
|---|---|---|
| SSH (WiFi) | `ssh orin` (10.7.20.x, DHCP) | IP may change |
| SSH (Ethernet) | `ssh orin_wire` (10.0.255.177) | Static, cable required |
| AnyDesk | Via ID | Needs dummy HDMI plug |

!!! tip "Always verify IPs"
    The Robots_urjc network uses DHCP. Run `hostname -I` on the Orin to get the current IP. Update `~/.ssh/config` on your Mac if it changed.

## Known Issues

| Issue | Workaround |
|---|---|
| ZED needs re-plug after reboot | Unplug and replug USB |
| torch needs `LD_LIBRARY_PATH` | `export LD_LIBRARY_PATH=/home/orin/.local/lib/python3.10/site-packages/nvidia/nvjitlink/lib:$LD_LIBRARY_PATH` |
| numpy >= 2 breaks cv2 | Pin to `numpy<2` |
| BGR/RGB swap in YOLO debug image | Fixed in `yolo_detector_node.py` — always convert RGB back to BGR before publishing as "bgr8" |
| No HDMI port | Use DP-to-HDMI adapter |
