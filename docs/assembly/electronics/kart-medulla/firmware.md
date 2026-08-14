# Kart Medulla Firmware

The firmware side of the Kart Medulla ESP32 — the software that receives commands from the Orin, runs the steering PID loop, and drives the throttle/brake/steering actuators. The board itself, its pinout, and the wiring live on the [Kart Medulla](index.md) page; this page covers how the firmware is built and how it is structured.

**Repository:** [UM-Driverless/kart-medulla](https://github.com/UM-Driverless/kart-medulla)

## Framework and build environments

- **Framework:** ESP-IDF (5.x) via **PlatformIO**, platform pinned to `espressif32@6.4.0`. The firmware is bare-metal FreeRTOS with no ROS dependency — its own toolchain and flashing process, deliberately decoupled from the Orin's ROS 2 workspace.
- **Build environments** in `platformio.ini`:

| Env | Board | Purpose | State |
|---|---|---|---|
| `esp32-s3-devkitc-1` | `esp32-s3-devkitc-1` | **ESP32-S3 — the kart's MCU. This is the image that runs on the kart.** | Working — builds and uploads from the Orin |
| `esp32dev` | `esp32dev` | Classic ESP32-WROOM-32E. Kept as a fallback only; not flashed to the kart | Present in `platformio.ini`, never built on the Orin |
| `native` | – | Host-side unit tests with hardware fakes | Working |

The classic and S3 chips are not interchangeable images — the classic ESP32 is Xtensa LX6 and the S3 is LX7, so an `esp32dev` binary will not boot on the kart's board and `esptool` rejects the chip-ID mismatch. The two envs are separate targets, not two ways of building the same thing.

`components/km_gpio/km_gpio.h` carries **both** pin maps and picks between them at compile time on `#if defined(CONFIG_IDF_TARGET_ESP32S3)`. Building the `esp32-s3-devkitc-1` env takes the S3 branch: `PIN_STEER_PWM` = GPIO 40, `PIN_STEER_DIR` = GPIO 17, `PIN_SDC_NOT_EMERGENCY` = GPIO 18. The classic map — where `PIN_STEER_PWM` is GPIO 18, which on the S3 board is the gate of Q3, the shutdown-circuit MOSFET — sits in the `#else` and is not compiled. That overlap is why the two must never be mixed up: reasoning from the wrong branch can fire or disable the emergency brake.

The schematic in `dv-hardware` is the authority on any pin claim, with `dv-hardware/projects/kart-medulla/docs/pinout-esp32-s3.md` as its readable form. This page does not restate the pin map — see the [Kart Medulla](index.md) board page and the [CN connector pinout](pinout.md).

## Building and flashing

!!! danger "De-power the steering before any flash"
    Flashing hard-resets the ESP32 into the download bootloader, and for that whole window `CMD_STEER_PWM` (GPIO 40) and `CMD_STEER_DIR` (GPIO 17) float — neither has a pulldown, unlike GPIO 3 and GPIO 18 — while the Cytron H-bridge stays powered from the 48 V pack. The steering motor can then drive uncontrolled. This swung the steering to full lock and **broke teeth off the steering gears on 2026-08-08**.

    De-power the Cytron or unplug the steering motor before flashing, or have the kart in manual with actuator power off. No firmware change can cover this — the firmware is not running during that window. The permanent fix is a pulldown on `CMD_STEER_PWM`, tracked as REQ-08 in `dv-hardware/projects/kart-medulla/requirements.md`.

Flashing happens **from the Orin**, which is where the ESP32 is plugged in. The Mac can compile-check a change first — PlatformIO is installed there at `~/.platformio/penv/bin/pio` (not on `PATH`, so call it by full path) and builds both envs to a linked binary — but the board is on the Orin, so that is where uploads happen. The `kart-brain` service holds the serial port, so it has to be stopped first and restarted afterwards:

```bash
ssh orin-remote 'echo 0 | sudo -S systemctl stop kart-brain'
ssh orin-remote 'cd ~/kart_medulla && ~/.local/bin/pio run -e esp32-s3-devkitc-1 --target upload --upload-port /dev/ttyACM0'
ssh orin-remote 'echo 0 | sudo -S systemctl start kart-brain'
```

```bash
# Serial monitor
pio device monitor

# Run unit tests on the host (no hardware needed)
pio test -e native
```

- **Port:** the S3 enumerates on the Orin as **`/dev/ttyACM0`** — the CH343 is a CDC-ACM device. It is *not* `/dev/ttyUSB0`; that was the classic board's CP2102.
- **USB bridge:** WCH **CH343** (`lsusb` → `1a86:55d3`, "QinHeng Electronics USB Single Serial"). On macOS the same board appears as `/dev/cu.usbmodem*`. The S3's two USB-C ports are silkscreened `COM` (the bridge) and `USB` (native USB-OTG / USB-Serial-JTAG).
- **Upload baud:** `platformio.ini` sets `upload_speed = 921600` for the S3 env. The old 115200 cap belonged to the *classic* board's CP2102 and does not apply to the CH343 (rated to 6 Mbps). Confirmed on hardware — the 2026-08-10 flash from the Orin wrote 338 kB in 2.6 s, about 1.05 Mbit/s effective, hash verified. If a flash ever fails to connect or fails verification, try 460800, then 115200.
- **BOOT-button recovery:** if a flash hangs at `Connecting...`, hold **BOOT**, press **EN**, release **BOOT**; press **EN** afterwards to restart if needed.

Source: `kart-medulla/README.md`, `kart-medulla/AGENTS.md`.

## FreeRTOS task architecture

The firmware runs four FreeRTOS tasks. The period argument in the task-creation calls is in **milliseconds**, not Hz — a detail worth knowing before reading `main.c`.

| Task | Period → rate | Stack | Priority | Role |
|---|---|---|---|---|
| `comms` | 10 ms → 100 Hz | 4096 B | 2 | UART RX/TX — receive commands from the Orin, send telemetry |
| `control` | 2 ms → 500 Hz | 4096 B | 1 | Read the steering angle, run the PID, drive the actuators, decide the shutdown circuit, apply the comms/manual safety, send steering feedback |
| `heartbeat` | 1000 ms → 1 Hz | 2048 B | 1 | Send a heartbeat to the Orin |
| `health` | 1 Hz | 4096 B | 1 | Monitor sensor / I²C / heap and report to the Orin. Started with its own `xTaskCreate`, not via the `KM_RTOS` periodic wrapper |

500 Hz is measured on the kart (the `control_iters` field of the `ESP_PNEUMATIC` telemetry frame counts it), not just a target. Nothing in the loop blocks: the steering sensor is read through hardware MCPWM capture rather than an I²C transaction. The rate cap is the UART — the per-cycle steering frame uses about 87 % of the 115200-baud link and TX is unbuffered.

Source: `main/main.c`, `system_init()`.

### Firmware components

The tasks are built from components under `components/`:

| Component | Role |
|---|---|
| `km_coms` | UART framed binary protocol to/from the Orin |
| `km_rtos` | FreeRTOS periodic-task manager |
| `km_pid` | PID controller |
| `km_sdir` | Steering angle sensor. `km_sdir_pwm` decodes the MT6701's PWM output through MCPWM capture — this is the kart's path. The AS5600 I²C driver in the same component is the classic-board fallback |
| `km_gpio` | GPIO / ADC / DAC / PWM / I²C hardware abstraction (holds the pin map) |
| `km_act` | Actuator control (DAC throttle/brake, PWM+DIR steering) |
| `km_objects` | Thread-safe shared object store (targets, actuals) |
| `km_sta` | State machine |
| `km_gamc` | Gamepad controller (Bluepad32) |

## Steering PID pipeline

The steering control path, per `control_task` in `main/main.c`:

1. The Orin sends a target steering angle over the serial protocol.
2. `control_task` reads the target from the `km_objects` store.
3. The **MT6701** angle sensor is read from its ~994 Hz PWM output on GPIO 1, captured in hardware by MCPWM → actual angle in radians. Positive = left already, matching the body-frame convention, so no negation. The sensor is on CN5.2, the terminal originally labelled Pressure 3.
4. `km_pid` computes an output in `[-1.0, 1.0]`.
5. `km_act` drives the steering motor: PWM duty = magnitude, DIR pin = sign, into the Cytron H-bridge.
6. The actual angle is sent back to the Orin as steering feedback.

There is also a **direct-PWM mode** (`STEER_MODE = 1`): the target is interpreted straight as a PWM value in `[-1.0, 1.0]` and the PID is bypassed (its integral is reset so it does not wind up while inactive). Default is PID mode.

### Gains

The compiled defaults are `PID_DEFAULT_KP` / `KI` / `KD` / `PWM_LIMIT` at the top of `main/main.c`: **Kp = 1.00, Ki = 0.0, Kd = 0.05, output limit 0.50**. The limit is deliberately held below 100 % to protect the steering gears during testing; raise it as the loop is validated.

These are being actively tuned, so read them from `main.c` rather than from any table when the exact value matters. The Orin can also override all four at runtime with the `ORIN_STEER_PID` (0x2B) frame; the firmware reports what it is actually running back in `ESP_STEER_PID` (0x0D), which is what the dashboard displays. A dashboard value that differs from the numbers above means an override is live, not that something is wrong.

## Orin ↔ ESP32 protocol

The framed binary serial protocol between the Orin and the ESP32 (message types, encoding, CRC) is **not re-specified here** to avoid two copies drifting apart. See the canonical protocol reference on the [ROS 2 packages](../../../software/ros2/packages.md) page. In short: it is a plain **USB serial** link (UART over the USB bridge) — there is no CAN anywhere on the kart.

## Comms-loss watchdog (safety-relevant)

A comms watchdog runs inside `control_task` with `COMMS_WATCHDOG_MS = 1000`. If no command has arrived within that window **or** the mission is `MISSION_MANUAL`, the firmware hands the throttle mux back to the driver's pedal, calls `KM_ACT_Stop()` on throttle, brake **and** steering, and resets the PID.

!!! danger "On comms loss the firmware coasts — it does NOT brake"
    `KM_ACT_Stop()` **zeroes** the actuator outputs. Zeroing the brake command **releases the brake**, so on lost comms the kart **coasts** rather than stopping.

    **The two sides disagree.** `kart-brain/docs/ACTUATION_PROTOCOL.md:26` specifies that on timeout the actuator should "apply full brake, zero steering, zero throttle." The medulla firmware does not do this. Anyone relying on the ACTUATION_PROTOCOL behaviour for safety must fix the firmware first, not assume it already brakes. Making loss of comms assert braking is an open task in `kart-medulla/tasks.md`.

    Source: `main/main.c` (`control_task`), `kart-brain/docs/ACTUATION_PROTOCOL.md:26`.

## Shutdown circuit (SDC)

`control_task` decides the level of the shutdown-circuit line, GPIO 18 — the gate of Q3 — on every 2 ms cycle. It is written as a **whitelist**: the chain closes only while *all* of these hold, and opens in every other case, including states nobody anticipated.

- The Orin reports `AS_READY` or `AS_DRIVING`. `AS_OFF`, `AS_FINISHED` and `AS_EMERGENCY` all leave it open, so the ESP32 never arms the kart on its own initiative — the Orin has to keep asking, every cycle.
- Comms are fresh (same watchdog as above).
- Tank pressure is above `EBS_TANK_ARM_BAR` = 6.5 bar, falling back below 6.0 bar to open it again. The hysteresis stops the line chattering while the tank sits on the threshold. An empty kart therefore sits in emergency until the compressor brings the tank up, which is how Formula Student expects it to behave.
- The steering-fault latch is clear.
- The operator has not disabled the compressor from the dashboard — a kart that cannot refill its EBS reservoir must not look ready to drive.

!!! warning "The gate is not wired downstream yet"
    Q3's gate does not connect to anything, so nothing physically brakes or arms when this line changes. Check the logic through the pin readback — field 8 of the `ESP_PNEUMATIC` telemetry frame, shown on the dashboard's EBS page — or with a meter on the pin. Do not check it by expecting the kart to react.
