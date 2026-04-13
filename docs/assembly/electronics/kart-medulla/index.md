# Kart Medulla (ESP32-S3)

The Kart Medulla is the MCU-based control hub between the Orin computer and the kart's sensors and actuators. The next revision is an interface PCB built around the **ESP32-S3**, with external level shifting, analog conditioning, and Wago-style push-in connectors replacing the hand-wired Dupont setup.

!!! info "Currently hand-wired in the kart: classic ESP32"
    The kart is currently running a hand-wired classic-ESP32 (no PCB). That setup is documented on the [Legacy wiring](legacy-wiring.md) page and will be removed once the ESP32-S3 board is deployed.

**Firmware repository:** [UM-Driverless/kart_medulla](https://github.com/UM-Driverless/kart_medulla)

## Why ESP32-S3

The classic ESP32 ran out of usable GPIOs once CAN, SPI, status RGB, buzzer, and the Orin link were added on top of the existing I/O (3× halls, 3× pressure, accelerator, brake, SDC, steering, relay). The S3 solves this and adds several quality-of-life wins:

- **~45 GPIOs** (vs ~34 on the classic), with fewer of them reserved or strap-pin traps.
- **Native USB-OTG** — the Orin link becomes a direct USB cable (CDC-ACM), dropping the USB-UART bridge IC and moving from ~1 Mbit/s UART to ~12 Mbit/s full-speed USB.
- **Built-in USB-Serial-JTAG** — flashing, serial monitor, and step-debugging all over the same USB cable. No external ESP-Prog / FT2232H needed.
- **External DAC on the PCB** (see hardware decisions below) — replaces the classic ESP32's built-in 8-bit DAC with a 12-bit I²C DAC. More resolution, cleaner output, no op-amp gain stage.

Variants considered and rejected: **S2** (has DAC but single-core, no BT), **C3** (too few GPIOs), **C6** (no DAC, Wi-Fi 6 overkill for a kart), **H2** (no Wi-Fi).

## ESP32-S3 Overview

[![ESP32-S3-DevKitC-1 pinout (high resolution — click to open reference page)](images/esp32-s3-devkitc-1-pinout-mischianti.png)](https://mischianti.org/esp32-s3-devkitc-1-high-resolution-pinout-and-specs/)

*Click the image for the full high-resolution pinout and specs page at [mischianti.org](https://mischianti.org/esp32-s3-devkitc-1-high-resolution-pinout-and-specs/).*

- **CPU:** Xtensa dual-core 32-bit LX7, up to 240 MHz
- **GPIOs:** ~45 usable
- **ADCs:** 2× 12-bit, multi-channel
- **DACs:** none (external DAC on the interface PCB)
- **USB:** native USB-OTG + USB-Serial-JTAG
- **Wireless:** Wi-Fi 4 + BLE 5
- **Communication Interfaces:** SPI, I²C, UART, CAN (TWAI), I²S

## ESP32-S3 Pin Assignment

Pin map for the ESP32-S3 module on the interface PCB. H1 is the left header, H2 is the right header. This is a draft — pin counts and some signal assignments will be finalized during PCB layout.

| Pin | Header | GPIO | Signal | Type | Notes |
|-----|--------|------|--------|------|-------|
| 1 | H1.1 | - | 3V3 | Power | 3.3V supply |
| 2 | H1.2 | - | 3V3 | Power | 3.3V supply |
| 3 | H1.3 | - | RST | Reset | Reset pin |
| 4 | H1.4 | 4 | PEDAL_ACC | ADC1_CH3 | Accelerator pedal input |
| 5 | H1.5 | 5 | PEDAL_BRAKE | ADC1_CH4 | Brake pedal input |
| 6 | H1.6 | 6 | PRESSURE_1 | ADC1_CH5 | Festo pressure sensor 1 (24V via divider) |
| 7 | H1.7 | 7 | PRESSURE_2 | ADC1_CH6 | Festo pressure sensor 2 (24V via divider) |
| 8 | H1.8 | 15 | CS1 | SPI | SPI chip select 1 |
| 9 | H1.9 | 16 | — | — | Reserved / spare |
| 10 | H1.10 | 17 | TX1 | UART1 | UART1 TX |
| 11 | H1.11 | 18 | RX1 | UART1 | UART1 RX |
| 12 | H1.12 | 8 | I2C_SDA | I²C | AS5600 steering angle sensor data; also DAC (MCP4728) |
| 13 | H1.13 | 3 | NC | — | STRAP pin (flash/boot risk) |
| 14 | H1.14 | 46 | NC | — | STRAP pin (flash/boot risk) |
| 15 | H1.15 | 9 | I2C_SCL | I²C | AS5600 steering angle sensor clock; also DAC (MCP4728) |
| 16 | H1.16 | 10 | — | ADC1_CH9 | Reserved for ADC use |
| 17 | H1.17 | 11 | MOSI | SPI | SPI MOSI |
| 18 | H1.18 | 12 | CLK | SPI | SPI clock |
| 19 | H1.19 | 13 | MISO | SPI | SPI MISO |
| 20 | H1.20 | 14 | CS2 | SPI | SPI chip select 2 |
| 21 | H1.21 | - | 5V | Power | 5V supply |
| 22 | H1.22 | - | GND | Power | Ground |
| 23 | H2.1 | - | GND | Power | Ground |
| 24 | H2.2 | 43 | TX0 | UART0 | UART0 TX (debug) |
| 25 | H2.3 | 44 | RX0 | UART0 | UART0 RX (debug) |
| 26 | H2.4 | 1 | PRESSURE_3 | ADC1_CH0 | Festo pressure sensor 3 (24V via divider) |
| 27 | H2.5 | 2 | — | ADC1_CH1 | Reserved for ADC use |
| 28 | H2.6 | 42 | CAN_TX | CAN (TWAI) | CAN bus TX |
| 29 | H2.7 | 41 | CAN_RX | CAN (TWAI) | CAN bus RX |
| 30 | H2.8 | 40 | — | — | Spare |
| 31 | H2.9 | 39 | SDC_ENABLE | Digital Out | Shutdown-circuit relay drive |
| 32 | H2.10 | 38 | SDC_STATUS | Digital In | Shutdown-circuit status feedback |
| 33 | H2.11 | 37 | MOTOR_HALL_1 | Digital In | Motor hall sensor 1 (5V → 3.3V level-shifted) |
| 34 | H2.12 | 36 | BUZZER | Digital Out | Debug/status buzzer |
| 35 | H2.13 | 35 | — | — | Spare |
| 36 | H2.14 | 0 | NC | — | STRAP pin (boot mode) |
| 37 | H2.15 | 45 | NC | — | STRAP pin (VDD_SPI) |
| 38 | H2.16 | 48 | STATUS_LED | PWM | RGB status LED |
| 39 | H2.17 | 47 | MOTOR_HALL_2 | Digital In | Motor hall sensor 2 (5V → 3.3V level-shifted) |
| 40 | H2.18 | 21 | MOTOR_HALL_3 | Digital In | Motor hall sensor 3 (5V → 3.3V level-shifted) |
| 41 | H2.19 | 20 | USB_DP | USB | Native USB D+ (to Orin) |
| 42 | H2.20 | 19 | USB_DM | USB | Native USB D- (to Orin) |
| 43 | H2.21 | - | GND | Power | Ground |
| 44 | H2.22 | - | GND | Power | Ground |

!!! note "CMD_ACC is via the external I²C DAC"
    The classic ESP32 exposed `CMD_ACC` on a dedicated DAC pin. On the S3 there is no native DAC — `CMD_ACC` is generated by the **MCP4728** (see hardware decisions below) and rides the existing I²C bus. No additional pin is required.

!!! note "GPIO restrictions (ESP32-S3)"
    Strap/boot pins on the S3 — notably GPIO 0, 3, 45, 46 — must be left at safe levels at reset and are marked NC in the table above. On WROOM-1 modules some of GPIO 26–32 / 33–37 may be tied to SPI flash or PSRAM depending on the module variant; confirm against the module datasheet before using those ranges.

## Kart Medulla Interface PCB

Interface PCB hosting the ESP32-S3 module, signal conditioning, and outside-world connectors. Design lineage (EasyEDA `.epro` project files) lives in the Drive folder `formula_24-25-26/dv/kart/kart-medulla/project-backups/`.

### Hardware Decisions

- **Shutdown:** MOSFET (N-channel low-side or P-channel high-side) driven by `SDC_ENABLE`, with `SDC_STATUS` reading back the state. Exact topology TBD.
- **Analog throttle output (`CMD_ACC`):** external **MCP4728** — quad 12-bit I²C DAC. Shares the AS5600 I²C bus. Three spare channels available for future `CMD_BRAKE` or similar needs.
- **Pressure sensor inputs (3× Festo, 24V):** voltage divider + input clamp / TVS protection on each channel to bring the signal into the S3's ADC range (≤3.3V).
- **Hall sensor inputs (3× 5V):** level translation to 3.3V before the GPIO pins.
- **Orin link:** native USB-OTG on GPIO 19/20 (D±). No USB-UART bridge chip.

### Connector Pinout (Outside World)

The main connector is a set of green push-in headers labeled CN1..CN4 in the schematic.

![Kart Medulla main connector (green push-in)](images/kart-medulla-main-connector.png)

| Connector | Pin | Signal | Notes |
|-----------|-----|--------|-------|
| CN1 | 1 | HALL3_5V | |
| CN1 | 2 | HALL2_5V | |
| CN1 | 3 | HALL1_5V | |
| CN2 | 1 | PRESSURE1_24V | Festo pressure sensor 1 |
| CN2 | 2 | PRESSURE2_24V | Festo pressure sensor 2 |
| CN2 | 3 | PRESSURE3_24V | Festo pressure sensor 3 |
| CN3 | 1 | GND | |
| CN3 | 2 | STEER_CMD_DIR_3.3V | |
| CN3 | 3 | STEER_CMD_PWM_3.3V | |
| CN4 | 1 | 3.3V | |
| CN4 | 2 | STEER_SDA | |
| CN4 | 3 | STEER_SCL | |
