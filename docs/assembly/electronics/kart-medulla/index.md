# Kart Medulla (ESP32)

The Kart Medulla is the ESP32-based control hub that interfaces between the Orin computer, sensors, and actuators. The standard board is the ESP32-DevKitC V4 (38-pin, USB-C) with an ESP32-WROOM-32D module; the older 30-pin board is legacy-only. The system is moving to a dedicated interface PCB that consolidates level shifting, analog conditioning, and IO breakout.

**Firmware repository:** [UM-Driverless/kart_medulla](https://github.com/UM-Driverless/kart_medulla)

## ESP32 Overview

[![ESP32-DevKitC V4 Pinout](images/esp32-devkitc-v4-pinout.png)](https://docs.espressif.com/projects/esp-idf/en/v5.1/esp32/hw-reference/esp32/get-started-devkitc.html)

*   **CPU:** Xtensa dual-core (or single-core) 32-bit LX6 microprocessor
*   **Clock Speed:** Up to 240 MHz
*   **Wi-Fi:** 802.11 b/g/n
*   **Bluetooth:** Bluetooth v4.2 BR/EDR and BLE
*   **Flash Memory:** Up to 16 MB
*   **SRAM:** 520 KB
*   **GPIOs:** 34
*   **ADCs:** 18-channel, 12-bit
*   **DACs:** 2-channel, 8-bit
*   **Communication Interfaces:** SPI, I2C, UART, CAN, I2S

## ESP32 Standardization Decision

The project previously used a 30-pin ESP32 development board with a non-standard pinout that is not DevKitC-compatible. To ensure long-term repeatability, predictable wiring, and easy replacement across builds, the project now standardizes on the ESP32-DevKitC V4 (38-pin, USB-C) using the ESP32-WROOM-32D module with an integrated PCB antenna. DevKitC V4 is Espressif's reference design with a stable pinout, reliable auto-reset/boot circuitry, and wide toolchain support. The ESP32 core is identical across boards; the change is driven by hardware consistency and robustness, not performance. The 30-pin board remains deprecated and should not be used for new builds.

### ESP32-DevKitC Dimensions

![ESP32 DevKitC dimensions](images/ESP32-DevKitC-Dimensions.png)

## Current ESP32-DevKitC V4 Configuration

The ESP32-DevKitC V4 (with ESP32-WROOM-32D module) serves as the medulla of the kart, interfacing between the Orin computer, steering angle sensor, and motor controllers.

### Pin Assignments

#### Motor Control Outputs

| GPIO Pin | Function    | Type    | Range   | Description |
|----------|-------------|---------|---------|-------------|
| GPIO 26  | Throttle    | DAC2    | 0-255   | Analog throttle control |
| GPIO 25  | Brake       | DAC1    | 0-255   | Analog brake control |
| GPIO 27  | Steering PWM| LEDC    | 0-255   | Steering motor PWM |
| GPIO 14  | Steering DIR| Digital | 0/1     | Steering motor direction |

#### Sensor Interface (AS5600)

| GPIO Pin | Function | Connected To | Description |
|----------|----------|--------------|-------------|
| GPIO 22  | I2C SCL  | AS5600 SCL   | Clock signal |
| GPIO 21  | I2C SDA  | AS5600 SDA   | Data signal |

!!! note "AS5600 Status"
    The AS5600 magnetic angle sensor remains disabled in firmware until hardware is physically connected.

#### Auxiliary Pins

| GPIO Pin | Function     | Connected To | Description |
|----------|--------------|--------------|-------------|
| GPIO 2   | Status LED   | Onboard LED  | Status indicator |
| GPIO 18  | UART TX      | Orin RX      | Serial communication to Orin |
| GPIO 19  | UART RX      | Orin TX      | Serial communication from Orin |

## Wiring Connections

### ESP32 to AS5600 Angle Sensor

| AS5600 Pin | ESP32 Pin | Wire Color (2025) |
|------------|-----------|-------------------|
| SCL        | GPIO 22   | Blue |
| SDA        | GPIO 21   | Green |
| VCC        | 3.3V      | White |
| GND        | GND       | Grey |

!!! warning "Temporary Color Code"
    Wire colors are specific to the 2025 version and not official. Always verify connections.

### ESP32 to Motor Controllers

#### Throttle Control

| Motor Driver Pin | ESP32 Pin | Signal Type |
|------------------|-----------|-------------|
| Analog Input     | GPIO 26   | DAC2 (0-255)|
| VCC              | 5V        | Power       |
| GND              | GND       | Ground      |

#### Brake Control

| Motor Driver Pin | ESP32 Pin | Signal Type |
|------------------|-----------|-------------|
| Analog Input     | GPIO 25   | DAC1 (0-255)|
| VCC              | 5V        | Power       |
| GND              | GND       | Ground      |

#### Steering Control

| Steering Driver Pin | ESP32 Pin | Signal Type |
|---------------------|-----------|-------------|
| PWM                 | GPIO 27   | LEDC (0-255)|
| DIR                 | GPIO 14   | Digital (0/1)|
| VCC                 | 5V        | Power       |
| GND                 | GND       | Ground      |

### ESP32 to Orin (UART Communication)

| Orin Pin | ESP32 Pin | Direction |
|----------|-----------|-----------|
| RX       | GPIO 18   | ESP32 -> Orin |
| TX       | GPIO 19   | Orin -> ESP32 |
| GND      | GND       | Ground |

!!! info "UART Configuration"
    Serial communication enables future integration between the Orin computer and ESP32 for command/telemetry exchange.

## Kart Medulla Interface PCB (In Progress)

The interface PCB (a.k.a. `esp32_expander` in the repo) hosts the electrical conditioning and connectors so the ESP32 module can be swapped while keeping wiring consistent.

### Draft Hardware Decisions

- Shutdown: use a MOSFET (N-channel low-side or P-channel high-side).
- Analog outputs: use ESP32 DACs with a dual op-amp for gain (x1.5 to 5V throttle, x3 to ~9.99V Festo pressure sensor).

### Connector Pinout (Outside World)

The main connector is a set of green push-in headers labeled CN1..CN4 in the schematic.

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

### ESP32 Header Pinout (Software Names)

Mapping between the ESP32 38-pin numbering and the DevKitC V4 Type-C headers (H1/H2). ESP32 pins 1-19 correspond to H2 pins 1-19, and ESP32 pins 20-38 correspond to H1 pins 1-19. Pin numbers match the header labels in the diagram.

![ESP32 DevKitC V4 Type-C header pinout](images/esp32-devkitc-v4-typec-header-pinout.png)
![Kart Medulla main connector (green push-in)](images/kart-medulla-main-connector.png)

| ESP32 Pin | H1 Pin | H2 Pin | Signal |
|-----------|--------|--------|--------|
| 1 | - | 1 | 3V3 |
| 2 | - | 2 | EN |
| 3 | - | 3 | PRESSURE_1_0_3V3 |
| 4 | - | 4 | PRESSURE_2_0_3V3 |
| 5 | - | 5 | PRESSURE_3_0_3V3 |
| 6 | - | 6 | PEDAL_ACC_3V3 |
| 7 | - | 7 | PEDAL_BRAKE_3V3 |
| 8 | - | 8 | MOTOR_HALL_2_3V3 |
| 9 | - | 9 | CMD_ACC_0_3V3 |
| 10 | - | 10 | CMD_BRAKE_0_3V3 |
| 11 | - | 11 | HYDRAULIC_1_0_3V3 |
| 12 | - | 12 | HYDRAULIC_2_0_3V3 |
| 13 | - | 13 | NC (STRAP pin - flash/boot config risk) |
| 14 | - | 14 | GND |
| 15 | - | 15 | SDC_NOT_EMERGENCY_3V3 |
| 16 | - | 16 | RESERVED (FLASH/SDIO) |
| 17 | - | 17 | RESERVED (FLASH/SDIO) |
| 18 | - | 18 | RESERVED (FLASH/SDIO) |
| 19 | - | 19 | 5V |
| 20 | 1 | - | RESERVED (FLASH/SDIO) |
| 21 | 2 | - | RESERVED (FLASH/SDIO) |
| 22 | 3 | - | RESERVED (FLASH/SDIO) |
| 23 | 4 | - | NC (STRAP pin - boot config risk) |
| 24 | 5 | - | NC (STRAP pin - boot config risk) |
| 25 | 6 | - | NC (STRAP pin - BOOT mode pin) |
| 26 | 7 | - | NC (STRAP pin - boot config risk) |
| 27 | 8 | - | MOTOR_HALL_3_3V3 |
| 28 | 9 | - | MOTOR_HALL_1_3V3 |
| 29 | 10 | - | NC (STRAP pin - boot config risk) |
| 30 | 11 | - | CMD_STEER_PWM_3V3 |
| 31 | 12 | - | CMD_STEER_DIR_3V3 |
| 32 | 13 | - | GND |
| 33 | 14 | - | STEER_SDA_I2C |
| 34 | 15 | - | RESERVED (USB UART0 RX) |
| 35 | 16 | - | RESERVED (USB UART0 TX) |
| 36 | 17 | - | STEER_SCL_I2C |
| 37 | 18 | - | SPARE_3V3 |
| 38 | 19 | - | GND |
