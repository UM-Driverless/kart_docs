
# Throttle Pedal Sensor

## Overview

The throttle pedal sensor uses a linear Hall effect sensor (typically SS49E or similar) that converts pedal position into an electrical signal for motor speed control.

## Common Hall Sensor Specifications

### SS49E Linear Hall-Effect Sensor
- **Manufacturer:** Honeywell / Various
- **Type:** Bipolar linear Hall effect sensor
- **Operating Voltage:** 2.7V to 6.5V DC (typically 5V)
- **Current Consumption:** ~6mA at 5V
- **Sensitivity:** 1.4-1.8 mV/Gauss
- **Output Type:** Ratiometric analog voltage
- **Null Output:** VCC/2 (2.5V at 5V supply with no magnetic field)
- **Output Range:**
  - ~0.86V with north pole magnetic field
  - ~2.5V with no magnetic field
  - ~4.2V with south pole magnetic field
- **Operating Temperature:** -40°C to +85°C (up to +150°C for some variants)
- **Package:** TO-92 (3-pin)
- **Datasheet:** [Honeywell SS49E](https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/siot/ja/products/sensors/magnetic-sensors/linear-and-angle-sensor-ics/common/documents/sps-siot-ss39et-ss49e-ss59et-product-sheet-005850-3-en-ciid-50359.pdf)

## Pedal Assembly Specifications

- **Output Range (configured):**
  - 0-1V = 0% throttle (pedal released)
  - 4-5V = 100% throttle (pedal fully pressed)
- **Connector:** 3-wire cable
- **Mechanical:** Spring-return foot pedal with integrated magnet

## Product Sources

### Complete Pedal Assembly
- **AliExpress:** <a href="https://es.aliexpress.com/item/1005007243711390.html" target="_blank">Foot Pedal Accelerator (~2.46€)</a>
- **Amazon:** Various electric scooter throttle pedal listings

### Replacement Hall Sensors (SS49E)
- **Honeywell (Official):** <a href="https://www.mouser.com/ProductDetail/Honeywell/SS49E" target="_blank">Mouser Electronics - SS49E</a>
- **Addicore:** <a href="https://www.addicore.com/products/ss49e-linear-hall-effect-sensor" target="_blank">SS49E Linear Hall-Effect Sensor</a>
- **eBay:** <a href="https://www.ebay.com/itm/281782377861" target="_blank">5x SS49E Hall Sensors for Throttle Repair</a>
- **Sunrom Electronics:** <a href="https://www.sunrom.com/p/ss49e-hall-sensor-linear-analog" target="_blank">SS49E Hall Sensor Linear Analog</a>

!!! note "Replacement Parts"
    SS49E sensors commonly fail and typically need replacement yearly in high-use applications. Having spare sensors available is recommended for maintenance.

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