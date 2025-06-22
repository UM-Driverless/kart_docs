
# Motor Data
![](index/20250622200050.png)

24V motor, we will use it at 12V, estimated about 300W

## Gpt controller suggestions
- Pololu VNH5019 Driver (12 A cont, 30 A peak)
- Cytron MD30C (30 A cont, 80 A peak)
- Sabertooth 2x32: Overkill but excellent for dual motors, up to 32 A per channel
- Simple BTS7960: Cheap dual half-bridge module, supports 43 A per channel, needs external PWM and logic control

Most controllers required 5V PWM input. Neither the Nvidia Jetson Orin nor the Blue Pill can do that. To simplify and not use level shifters or external pcbs with can drivers, we choose a Teensy 4.0 (or similar), which is capable of 5V PWM output (via its GPIO pins) and includes a CAN driver.

Orin will send data to Teensy, Teensy sends PWM to the MD30C H-bridge controller, which powers the DC motor.
