# Blue Pill (STM32F103C6T6)

The Blue Pill is a small development board based on the STM32F103C6T6 microcontroller, which features an ARM Cortex-M3 core. It's a popular choice for hobbyists and professionals due to its low cost and powerful capabilities.

## Key Features of STM32F103C6T6

![Blue Pill Pinout](pinout.png)

*   **Core:** ARM 32-bit Cortex-M3 CPU
*   **Clock Speed:** Up to 72 MHz
*   **Flash Memory:** 32 KB
*   **SRAM:** 10 KB
*   **GPIOs:** 37
*   **ADCs:** 10-channel, 12-bit
*   **Timers:** 3 general-purpose timers, 1 advanced-control timer
*   **Communication Interfaces:** I2C, SPI, USART, USB, CAN
*   

## Pin use
| Pin Name | Physical Chip pin | Function                                                                                      |
| -------- | ----------------- | --------------------------------------------------------------------------------------------- |
| PA10     | 31                | RXD for debugging                                                                             |
| PA9      | 30                | TXD for debugging                                                                             |
| PA0      | 10                | PWM output to H-bridge, 0-3.3V                                                                |
| PA1      | 11                | DIR, gpio output, either high (3.3V) or low (0V) for the turn direction of the steering motor |
| PB6      | 42                | SCL I2C input at 3.3V, from the Hall effect sensor of steering column                         |
| PB7      | 43                | SDA I2C input at 3.3V, from the Hall effect sensor of steering column                         |
|          |                   | TODO input target angle from Orin                                                             |
|          |                   | TODO CAN TX                                                                                   |
|          |                   | TODO CAN RX                                                                                   |


