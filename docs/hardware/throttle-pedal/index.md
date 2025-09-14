# Throttle Pedal Sensor

## Overview

The throttle pedal sensor is a linear Hall effect sensor that converts pedal position into an electrical signal for motor speed control.

## Specifications

- **Type:** Linear Hall effect sensor
- **Power Supply:** 5V DC
- **Output:** 0-5V analog voltage
- **Output Range:**
  - 0V = 0% throttle (pedal released)
  - 5V = 100% throttle (pedal fully pressed)
- **Connector:** 3-wire cable

## Product Information

- **Product:** Foot pedal accelerator for electric bicycle, scooter, tricycle
- **Price:** ~2.46€
- **Link:** <a href="https://es.aliexpress.com/item/1005007243711390.html" target="_blank">AliExpress - Throttle Pedal Sensor</a>
- **Rating:** 4.6/5 (11 reviews, 105+ sold)

## Wiring

### Cable Color Code

| Cable Color       | Function | Voltage |
|-------------------|----------|---------|
| Red               | Vcc      | 5V      |
| Yellow            | Ground   | GND     |
| Teal (Green/Blue) | Signal   | 0-5V    |

!!! info "Signal Output"
    The sensor outputs a linear voltage proportional to pedal position:
    - Pedal released: 0V
    - Pedal fully pressed: 5V
    - The signal can be read by any ADC (Analog-to-Digital Converter) input

## Installation Notes

- Mount the pedal securely to prevent movement during operation
- Ensure cable is properly routed to avoid interference with pedal movement
- Protect connections from moisture and dirt
- Test full range of motion before use

## Interface Requirements

The throttle signal needs to be connected to:
- An ADC-capable microcontroller pin (ESP32, Arduino, etc.)
- Or directly to a motor controller with analog throttle input

For current kart configuration, this connects to the motor controller's throttle input.