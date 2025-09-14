# Wiring
TODO global diagram (Fritzing?)

## Throttle pedal sensor
It's a linear hall effect sensor, powered at 5V and outputs an analog voltage in 0-5V range. 0V = 0%, 5V = 100%.

| Cable Color       | Function |
| ----------------- | -------- |
| Red               | Vcc      |
| Yellow            | Ground   |
| Teal (Green/Blue) | Signal   |

## ESP32 wiring

For detailed ESP32 wiring connections including AS5600 sensor, motor driver, and Orin communication, see [ESP32 Hardware Documentation](../hardware/esp32/index.md#wiring-connections).