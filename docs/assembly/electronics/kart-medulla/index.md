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

Complete pin map for the ESP32-DevKitC V4 (38-pin, USB-C), matching the interface PCB wiring. Ordered by physical position on the board. H2 is the right header (pins 1-19), H1 is the left header (pins 1-19).

![ESP32 DevKitC V4 Type-C header pinout](images/esp32-devkitc-v4-typec-header-pinout.png)

| Header | GPIO | Signal | Type | Notes |
|--------|------|--------|------|-------|
| H2.1 | - | 3V3 | Power | 3.3V supply |
| H2.2 | - | EN | Reset | Active-low reset |
| H2.3 | 36 (VP) | PRESSURE_1 | ADC1_CH0 | Pressure sensor 1 (input only) |
| H2.4 | 39 (VN) | PRESSURE_2 | ADC1_CH3 | Pressure sensor 2 (input only) |
| H2.5 | 34 | PRESSURE_3 | ADC1_CH6 | Pressure sensor 3 (input only) |
| H2.6 | 35 | PEDAL_ACC | ADC1_CH7 | Accelerator pedal (input only) |
| H2.7 | 32 | PEDAL_BRAKE | ADC1_CH4 | Brake pedal |
| H2.8 | 33 | MOTOR_HALL_2 | Digital In | Motor hall sensor 2 |
| H2.9 | 25 | CMD_ACC | DAC1 | Throttle analog output (0-255) |
| H2.10 | 26 | CMD_BRAKE | DAC2 | Brake analog output (0-255) |
| H2.11 | 27 | HYDRAULIC_1 | ADC2_CH7 | Hydraulic pressure sensor 1 |
| H2.12 | 14 | HYDRAULIC_2 | ADC2_CH6 | Hydraulic pressure sensor 2 |
| H2.13 | 12 | NC | - | STRAP pin (flash/boot risk) |
| H2.14 | - | GND | Power | Ground |
| H2.15 | 13 | SDC_NOT_EMERGENCY | Digital In | Shutdown circuit emergency status |
| H2.16 | 9 | RESERVED | - | FLASH/SDIO |
| H2.17 | 10 | RESERVED | - | FLASH/SDIO |
| H2.18 | 11 | RESERVED | - | FLASH/SDIO |
| H2.19 | - | 5V | Power | 5V supply |
| H1.1 | 6 | RESERVED | - | FLASH/SDIO |
| H1.2 | 7 | RESERVED | - | FLASH/SDIO |
| H1.3 | 8 | RESERVED | - | FLASH/SDIO |
| H1.4 | 15 | NC | - | STRAP pin (boot config risk) |
| H1.5 | 2 | STATUS_LED | Digital Out | Onboard LED (strap pin, keep LOW at boot) |
| H1.6 | 0 | NC | - | STRAP pin (BOOT mode) |
| H1.7 | 4 | NC | - | STRAP pin (boot config risk) |
| H1.8 | 16 | MOTOR_HALL_3 | Digital In | Motor hall sensor 3 (also UART2 RX) |
| H1.9 | 17 | MOTOR_HALL_1 | Digital In | Motor hall sensor 1 (also UART2 TX) |
| H1.10 | 5 | NC | - | STRAP pin (boot config risk) |
| H1.11 | 18 | CMD_STEER_PWM | LEDC PWM | Steering motor PWM (Cytron H-bridge) |
| H1.12 | 19 | CMD_STEER_DIR | Digital Out | Steering motor direction (Cytron H-bridge) |
| H1.13 | - | GND | Power | Ground |
| H1.14 | 21 | I2C_SDA | I2C | AS5600 steering angle sensor data |
| H1.15 | 3 | USB_UART_RX | UART0 RX | Reserved (binary protocol from Orin) |
| H1.16 | 1 | USB_UART_TX | UART0 TX | Reserved (binary protocol to Orin) |
| H1.17 | 22 | I2C_SCL | I2C | AS5600 steering angle sensor clock |
| H1.18 | 23 | SPARE | - | Available |
| H1.19 | - | GND | Power | Ground |

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
