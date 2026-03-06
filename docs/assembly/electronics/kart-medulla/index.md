# Kart Medulla (ESP32)

The Kart Medulla is the ESP32-based control hub that interfaces between the Orin computer, sensors, and actuators. The standard board is the ESP32-DevKitC V4 (38-pin, USB-C) with an ESP32-WROOM-32D module; the older 30-pin board is legacy-only. The system is moving to a dedicated interface PCB that consolidates level shifting, analog conditioning, and IO breakout.

**Firmware repository:** [UM-Driverless/kart_medulla](https://github.com/UM-Driverless/kart_medulla)

## ESP32 Overview

[![ESP32-DevKitC V4 Pinout](images/esp32-devkitc-v4-pinout.png)](https://docs.espressif.com/projects/esp-idf/en/v5.1/esp32/hw-reference/esp32/get-started-devkitc.html)

*   **CPU:** Xtensa dual-core 32-bit LX6, up to 240 MHz
*   **Flash Memory:** Up to 16 MB
*   **SRAM:** 520 KB
*   **GPIOs:** 34
*   **ADCs:** 18-channel, 12-bit
*   **DACs:** 2-channel, 8-bit
*   **Communication Interfaces:** SPI, I2C, UART, CAN, I2S

## ESP32 Standardization Decision

The project previously used a 30-pin ESP32 development board with a non-standard pinout that is not DevKitC-compatible. To ensure long-term repeatability, predictable wiring, and easy replacement across builds, the project now standardizes on the ESP32-DevKitC V4 (38-pin, USB-C) using the ESP32-WROOM-32D module with an integrated PCB antenna. DevKitC V4 is Espressif's reference design with a stable pinout, reliable auto-reset/boot circuitry, and wide toolchain support. The 30-pin board remains deprecated and should not be used for new builds.

## ESP32 Pin Assignment

Complete pin map for the ESP32-DevKitC V4 (38-pin, USB-C), matching the interface PCB wiring. Ordered by physical position on the board. H1 is the left header, H2 is the right header (19 pins each).

![ESP32 DevKitC V4 Type-C header pinout](images/esp32-devkitc-v4-typec-header-pinout.png)

| Pin | Header | GPIO | Signal | Type | Notes |
|-----|--------|------|--------|------|-------|
| 1 | H1.1 | 6 | RESERVED | - | FLASH/SDIO |
| 2 | H1.2 | 7 | RESERVED | - | FLASH/SDIO |
| 3 | H1.3 | 8 | RESERVED | - | FLASH/SDIO |
| 4 | H1.4 | 15 | NC | - | STRAP pin (boot config risk) |
| 5 | H1.5 | 2 | STATUS_LED | Digital Out | Onboard LED (strap pin, keep LOW at boot) |
| 6 | H1.6 | 0 | NC | - | STRAP pin (BOOT mode) |
| 7 | H1.7 | 4 | NC | - | STRAP pin (boot config risk) |
| 8 | H1.8 | 16 | MOTOR_HALL_3 | Digital In | Motor hall sensor 3 (also UART2 RX) |
| 9 | H1.9 | 17 | MOTOR_HALL_1 | Digital In | Motor hall sensor 1 (also UART2 TX) |
| 10 | H1.10 | 5 | NC | - | STRAP pin (boot config risk) |
| 11 | H1.11 | 18 | CMD_STEER_PWM | LEDC PWM | Steering motor PWM (Cytron H-bridge) |
| 12 | H1.12 | 19 | CMD_STEER_DIR | Digital Out | Steering motor direction (Cytron H-bridge) |
| 13 | H1.13 | - | GND | Power | Ground |
| 14 | H1.14 | 21 | I2C_SDA | I2C | AS5600 steering angle sensor data |
| 15 | H1.15 | 3 | USB_UART_RX | UART0 RX | Reserved (binary protocol from Orin) |
| 16 | H1.16 | 1 | USB_UART_TX | UART0 TX | Reserved (binary protocol to Orin) |
| 17 | H1.17 | 22 | I2C_SCL | I2C | AS5600 steering angle sensor clock |
| 18 | H1.18 | 23 | SPARE | - | Available |
| 19 | H1.19 | - | GND | Power | Ground |
| 20 | H2.1 | - | 3V3 | Power | 3.3V supply |
| 21 | H2.2 | - | EN | Reset | Active-low reset |
| 22 | H2.3 | 36 (VP) | PRESSURE_1 | ADC1_CH0 | Pressure sensor 1 (input only) |
| 23 | H2.4 | 39 (VN) | PRESSURE_2 | ADC1_CH3 | Pressure sensor 2 (input only) |
| 24 | H2.5 | 34 | PRESSURE_3 | ADC1_CH6 | Pressure sensor 3 (input only) |
| 25 | H2.6 | 35 | PEDAL_ACC | ADC1_CH7 | Accelerator pedal (input only) |
| 26 | H2.7 | 32 | PEDAL_BRAKE | ADC1_CH4 | Brake pedal |
| 27 | H2.8 | 33 | MOTOR_HALL_2 | Digital In | Motor hall sensor 2 |
| 28 | H2.9 | 25 | CMD_ACC | DAC1 | Throttle analog output (0-255) |
| 29 | H2.10 | 26 | CMD_BRAKE | DAC2 | Brake analog output (0-255) |
| 30 | H2.11 | 27 | HYDRAULIC_1 | ADC2_CH7 | Hydraulic pressure sensor 1 |
| 31 | H2.12 | 14 | HYDRAULIC_2 | ADC2_CH6 | Hydraulic pressure sensor 2 |
| 32 | H2.13 | 12 | NC | - | STRAP pin (flash/boot risk) |
| 33 | H2.14 | - | GND | Power | Ground |
| 34 | H2.15 | 13 | SDC_NOT_EMERGENCY | Digital In | Shutdown circuit emergency status |
| 35 | H2.16 | 9 | RESERVED | - | FLASH/SDIO |
| 36 | H2.17 | 10 | RESERVED | - | FLASH/SDIO |
| 37 | H2.18 | 11 | RESERVED | - | FLASH/SDIO |
| 38 | H2.19 | - | 5V | Power | 5V supply |

!!! warning "GPIO 17/16 Conflict"
    GPIO 17 and 16 are used for MOTOR_HALL_1 and MOTOR_HALL_3 on the interface PCB. These are also UART2 TX/RX pins. When using the PCB, UART2 debug logging is **not available**. Hall sensors are not yet connected, so UART2 is currently usable for debug output.

!!! note "GPIO Restrictions"
    GPIO 6-11 are connected to SPI flash and must not be used. GPIO 34-39 are input-only.

## Kart Medulla Interface PCB (In Progress)

The interface PCB (a.k.a. `esp32_expander` in the repo) hosts the electrical conditioning and connectors so the ESP32 module can be swapped while keeping wiring consistent.

### Draft Hardware Decisions

- Shutdown: use a MOSFET (N-channel low-side or P-channel high-side).
- Analog outputs: use ESP32 DACs with a dual op-amp for gain (x1.5 to 5V throttle, x3 to ~9.99V Festo pressure sensor).

### Connector Pinout (Outside World)

The main connector is a set of green push-in headers labeled CN1..CN4 in the schematic.

![Kart Medulla main connector (green push-in)](images/kart-medulla-main-connector.png)

| Connector | Pin | Signal | Notes |
|-----------|-----|--------|-------|
| CN1 | 1 | HALL3_5V | |
| CN1 | 2 | HALL2_5V | |
| CN1 | 3 | HALL1_5V | |
| CN2 | 1 | PRESSURE1_0V10 | |
| CN2 | 2 | PRESSURE2_0V10 | |
| CN2 | 3 | PRESSURE3_0V10 | |
| CN3 | 1 | GND | |
| CN3 | 2 | STEER_CMD_DIR_3.3V | |
| CN3 | 3 | STEER_CMD_PWM_3.3V | |
| CN4 | 1 | 3.3V | |
| CN4 | 2 | STEER_SDA | |
| CN4 | 3 | STEER_SCL | |

## Other

### ESP32-DevKitC Dimensions

![ESP32 DevKitC dimensions](images/ESP32-DevKitC-Dimensions.png)
