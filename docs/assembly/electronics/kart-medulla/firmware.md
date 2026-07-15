# Kart Medulla Firmware

The firmware side of the Kart Medulla ESP32 — the software that receives commands from the Orin, runs the steering PID loop, and drives the throttle/brake/steering actuators. The board itself, its pinout, and the wiring live on the [Kart Medulla](index.md) page; this page covers how the firmware is built and how it is structured.

**Repository:** [UM-Driverless/kart-medulla](https://github.com/UM-Driverless/kart-medulla)

!!! warning "Hardware is ESP32-S3, but the firmware builds for the classic ESP32"
    The physical kart-medulla board is an **ESP32-S3**, but the firmware still builds for the **classic ESP32-WROOM-32E** — that is the only target that compiles and runs today. The S3 pin map exists in the source but its build target does **not link yet** (missing SPI-DAC, PCF8574, and safety-pin drive). Do not assume "classic" behaviour from the build target: on the real S3 board the same GPIO numbers mean different nets. The authoritative S3 pin map is `.agents/esp32s3-pinmap.md` in the repo; the schematic wins where docs disagree. Source: `kart-medulla/AGENTS.md`.

## Framework and build environments

- **Framework:** ESP-IDF (5.x) via **PlatformIO**, platform pinned to `espressif32@6.4.0`. The firmware is bare-metal FreeRTOS with no ROS dependency — its own toolchain and flashing process, deliberately decoupled from the Orin's ROS 2 workspace.
- **Build environments** in `platformio.ini`:

| Env | Purpose | State |
|---|---|---|
| `esp32dev` | Classic ESP32-WROOM-32E — the image that actually runs on the kart | Working |
| `esp32-s3-devkitc-1` | ESP32-S3 (the real PCB's MCU) | **Does not link yet** — throttle/brake DAC (MCP4922 over SPI), PCF8574, and the safety-pin/watchdog drive are still gaps. Exists so the S3 pin map is buildable-in-progress, not because a working S3 image exists (`platformio.ini` comment) |
| `native` | Host-side unit tests with hardware fakes | Working |

!!! note "Doc lag on the S3 env"
    `AGENTS.md` and `.agents/esp32s3-pinmap.md` state that `platformio.ini` "has only `esp32dev` and `native`". The file now also carries the `esp32-s3-devkitc-1` stub env above. The substance is unchanged — there is still **no working S3 image** — but the env list in those two docs is stale.

## Building and flashing

```bash
# Build the classic-ESP32 image
pio run -e esp32dev

# Flash (from the Orin, where the ESP32 is connected over USB)
pio run -t upload -e esp32dev --upload-port /dev/ttyUSB0

# Serial monitor
pio device monitor

# Run unit tests on the host (no hardware needed)
pio test -e native
```

- **Upload baud must be 115200** (`upload_speed = 115200` in `platformio.ini`). The USB-UART bridge fails to flash at higher speeds; 460800 works fine for runtime comms, just not for `esptool` upload.
- **USB bridge:** the classic hand-wired board uses a CP2102 and enumerates as `/dev/ttyUSB0`. The S3 board uses a WCH **CH343/CH9102** bridge (VID `0x1A86`) and enumerates as `/dev/cu.usbmodem*` (macOS). The S3's two USB-C ports are silkscreened `COM` (the bridge) and `USB` (native USB-OTG / USB-Serial-JTAG).
- **BOOT-button recovery:** if a flash hangs at `Connecting...`, hold **BOOT**, press **EN**, release **BOOT**; press **EN** afterwards to restart if needed.

Source: `kart-medulla/README.md`, `kart-medulla/AGENTS.md`.

## FreeRTOS task architecture

The firmware runs four FreeRTOS tasks. The values below are read from the task-creation calls in `main/main.c` (the source of truth). The rate tables in `README.md` and `AGENTS.md` are older and no longer match the code — treat them as superseded (see the note).

| Task | Period → target rate | Stack | Priority | Role |
|---|---|---|---|---|
| `comms` | 10 ms → 100 Hz | 4096 B | 2 | UART RX/TX — receive commands from the Orin, send telemetry |
| `control` | 2 ms → 500 Hz target | 4096 B | 1 | Read AS5600, run steering PID, drive actuators, apply the comms/manual safety, send steering feedback. Real rate is capped by the blocking I²C AS5600 read, so it runs below 500 Hz |
| `heartbeat` | 1000 ms → 1 Hz | 2048 B | 1 | Send a heartbeat to the Orin |
| `health` | 1 Hz | 4096 B | 1 | Monitor magnet / I²C / heap and report to the Orin. Started with its own `xTaskCreate`, not via the `KM_RTOS` periodic wrapper |

Source: `main/main.c:311-322`.

!!! warning "Older task-rate figures elsewhere are superseded"
    The code (`main/main.c`) is authoritative: comms 100 Hz (10 ms), control 500 Hz target (2 ms), heartbeat 1 Hz, health 1 Hz (`main.c:311-322`). Ignore the older, no-longer-matching numbers still sitting in other files — `README.md`'s FreeRTOS table (comms 20 Hz, control 10 Hz) and `AGENTS.md`'s Architecture table (comms 100 Hz, control 100 Hz, `health` omitted). A stale docstring inside `main.c:227` itself still says "comms (20 Hz), control (10 Hz)". These are flagged for cleanup so only the current values remain.

### Firmware components

The tasks are built from components under `components/`:

| Component | Role |
|---|---|
| `km_coms` | UART framed binary protocol to/from the Orin |
| `km_rtos` | FreeRTOS periodic-task manager |
| `km_pid` | PID controller |
| `km_sdir` | AS5600 steering angle sensor driver (I²C) |
| `km_gpio` | GPIO / ADC / DAC / PWM / I²C hardware abstraction (holds the pin map) |
| `km_act` | Actuator control (DAC throttle/brake, PWM+DIR steering) |
| `km_objects` | Thread-safe shared object store (targets, actuals) |
| `km_sta` | State machine |
| `km_gamc` | Gamepad controller (Bluepad32) |

## Steering PID pipeline

The steering control path, per `control_task` in `main/main.c`:

1. The Orin sends a target steering angle over the serial protocol.
2. `control_task` reads the target from the `km_objects` store.
3. The AS5600 is read over I²C → actual angle in radians (the driver already reports positive = left, matching the body-frame convention, so no negation).
4. `km_pid` computes an output in `[-1.0, 1.0]`.
5. `km_act` drives the steering motor: PWM duty = magnitude, DIR pin = sign, into the Cytron H-bridge.
6. The actual angle is sent back to the Orin as steering feedback.

There is also a **direct-PWM mode** (`STEER_MODE = 1`): the target is interpreted straight as a PWM value in `[-1.0, 1.0]` and the PID is bypassed (its integral is reset so it does not wind up while inactive). Default is PID mode.

!!! warning "PID gains and the steering output limit differ across sources — trust the code"
    The committed gains and limit live in `main/main.c` and are actively tuned (they drift), so treat the code as authoritative rather than any doc table:

    - **Code (`main.c:277-279`):** Kp = 1.50, Ki = 0.0, Kd = 0.02. Steering output limited to **0.50** (`main.c:267`; initialised at 0.40 on `main.c:263`).
    The gain sets quoted elsewhere are **older values, now superseded** — ignore them: `README.md` "PID Configuration" (Kp = 0.15, Kd = 0.01, limit 0.15) and `AGENTS.md` "Steering Pipeline" (Kp = 0.03, Kd = 0.0004). They are flagged for cleanup so only the code's current gains remain. The output limit is deliberately held below 100 % to protect the steering gears during testing; raise it only as the loop is validated.

## Orin ↔ ESP32 protocol

The framed binary serial protocol between the Orin and the ESP32 (message types, encoding, CRC) is **not re-specified here** to avoid two copies drifting apart. See the canonical protocol reference on the [ROS 2 packages](../../../software/ros2/packages.md) page. In short: it is a plain **USB serial** link (UART over the USB bridge) — there is no CAN anywhere on the kart.

## Comms-loss watchdog (safety-relevant)

A comms watchdog runs inside `control_task` with `COMMS_WATCHDOG_MS = 1000` (`main.c:35`). If no command has arrived within that window **or** the mission is `MISSION_MANUAL`, the firmware calls `KM_ACT_Stop()` on throttle, brake, **and** steering, and resets the PID (`main.c:106-114`).

!!! danger "On comms loss the firmware coasts — it does NOT brake"
    `KM_ACT_Stop()` **zeroes** the actuator outputs. Zeroing the brake command **releases the brake**, so on lost comms the kart **coasts** rather than stopping.

    - Making loss-of-comms **assert braking** (and/or drop the SDC — Shutdown Circuit — chain) is still a **TODO** in the firmware. On the S3 board the SDC is GPIO 18 and the firmware does not drive it yet, so the medulla currently cannot arm the kart *or* command a brake on timeout.
    - **The two sides disagree.** `kart-brain/docs/ACTUATION_PROTOCOL.md:26` states that on timeout the actuator should "apply full brake, zero steering, zero throttle." The medulla firmware does **not** do this — it coasts. Anyone relying on the ACTUATION_PROTOCOL behaviour for safety must fix the firmware first, not assume it already brakes.

    Source: `kart-medulla/AGENTS.md` (Safety), `main/main.c:100-114`, `kart-brain/docs/ACTUATION_PROTOCOL.md:26`.
