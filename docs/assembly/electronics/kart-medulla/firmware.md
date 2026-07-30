# Kart Medulla Firmware

The firmware side of the Kart Medulla ESP32 — the software that receives commands from the Orin, runs the steering PID loop, and drives the throttle/brake/steering actuators. The board itself, its pinout, and the wiring live on the [Kart Medulla](index.md) page; this page covers how the firmware is built and how it is structured.

**Repository:** [UM-Driverless/kart-medulla](https://github.com/UM-Driverless/kart-medulla)

!!! warning "The S3 build is the one on the kart — several repo docs still say otherwise"
    The board is an **ESP32-S3** and `esp32-s3-devkitc-1` is the environment that is built and flashed to it. Verified on the kart's Orin on 2026-07-30: the only build directory present is `~/kart_medulla/.pio/build/esp32-s3-devkitc-1/`, there is no `esp32dev` build at all, and the ESP32 enumerates as `/dev/ttyACM0` behind a WCH CH343 bridge (`lsusb` → `1a86:55d3`) — the classic board's CP2102 would have appeared as `/dev/ttyUSB0`, and no `/dev/ttyUSB*` exists.

    Three statements in the firmware repo are **stale** and should not be believed: the comment above `[env:esp32-s3-devkitc-1]` in `platformio.ini` saying the env "does NOT link yet"; `.agents/esp32s3-pinmap.md` saying "The S3 build does not exist. `platformio.ini` has only `esp32dev` and `native`"; and the classic-ESP32 pin table in `README.md`. The S3 target has built and uploaded successfully from the Orin since 2026-07-26.

    **The pin map is fine — checked 2026-07-30.** `components/km_gpio/km_gpio.h` carries *both* maps, selected at compile time by `#if defined(CONFIG_IDF_TARGET_ESP32S3)`. Building the `esp32-s3-devkitc-1` env takes the S3 branch: `PIN_STEER_PWM` = GPIO 40, `PIN_STEER_DIR` = GPIO 17, `PIN_SDC_NOT_EMERGENCY` = GPIO 18. The classic map — where `PIN_STEER_PWM` is GPIO 18, the gate of Q3 — sits in the `#else` branch and is not compiled. `.agents/esp32s3-pinmap.md`'s claim that the header "still holds the classic-ESP32 map" is stale; `AGENTS.md` is correct. The schematic and `dv-hardware/projects/kart-medulla/docs/pinout-esp32-s3.md` still win over any of these docs.

## Framework and build environments

- **Framework:** ESP-IDF (5.x) via **PlatformIO**, platform pinned to `espressif32@6.4.0`. The firmware is bare-metal FreeRTOS with no ROS dependency — its own toolchain and flashing process, deliberately decoupled from the Orin's ROS 2 workspace.
- **Build environments** in `platformio.ini`:

| Env | Board | Purpose | State |
|---|---|---|---|
| `esp32-s3-devkitc-1` | `esp32-s3-devkitc-1` | **ESP32-S3 — the kart's MCU. This is the image that runs on the kart.** | Working — builds and uploads from the Orin |
| `esp32dev` | `esp32dev` | Classic ESP32-WROOM-32E. Kept as a fallback only; not flashed to the kart | Present in `platformio.ini`, never built on the Orin |
| `native` | – | Host-side unit tests with hardware fakes | Working |

The classic and S3 chips are not interchangeable images — the classic ESP32 is Xtensa LX6 and the S3 is LX7, so an `esp32dev` binary will not boot on the kart's board and `esptool` rejects the chip-ID mismatch. The two envs are separate targets, not two ways of building the same thing.

## Building and flashing

Flashing happens **from the Orin**, which is where the ESP32 is plugged in; the Mac has no ESP-IDF toolchain. The `kart-brain` service holds the serial port, so it has to be stopped first and restarted afterwards:

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
- **Upload baud:** `platformio.ini` sets `upload_speed = 921600` for the S3 env. The old 115200 cap belonged to the *classic* board's CP2102 and does not apply to the CH343 (rated to 6 Mbps). The 921600 figure is annotated in `platformio.ini` as raised from the datasheet rather than proven on hardware — if a flash fails to connect or fails verification, try 460800, then 115200.
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
