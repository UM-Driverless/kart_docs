# Net Name Nomenclature

This document defines a simple, consistent naming scheme for all nets/signals in the PCB and system. Goal: no ambiguity, easy to read, applicable to cables/connectors.

Names describe the signal's purpose and type. Apply consistently across schematics, cables, and docs. If a signal changes, rename it—no over-future-proofing.

## Structure
Every name: `DESCRIPTOR[_NUMBER_OR_SPECIFIER]__INTERFACE`

- `DESCRIPTOR`: Signal's primary purpose (e.g., `PEDAL_ACC`, `CMD_BRAKE`, `RES_PRESSURE`).
- `NUMBER_OR_SPECIFIER`: For multiples/clarification (e.g., `1`, `2`, `3`, `DIR`, `SDA`, `SCL`, `LOW_SIDE`). Omit if unnecessary.
- `INTERFACE`: Electrical type (e.g., `__0_5V`, `__PWM_3V3`). Include voltage/range explicitly where relevant (e.g., for PWM or logic levels).

No direction words (`IN`, `OUT`, `RX`, `TX`)—descriptor implies flow. Use uppercase, underscores only.

## Allowed Descriptors (based on this PCB)
- `PEDAL_ACC`: Accelerator pedal input.
- `PEDAL_BRAKE`: Brake pedal input.
- `CMD_ACC`: Accelerator command output.
- `CMD_BRAKE`: Brake command output.
- `RES_PRESSURE`: Air reservoir pressure measurement.
- `WHEEL_HALL`: Wheel hall sensor pulse (for speed derivation).
- `CMD_STEER`: Steering command (with specifier like `DIR` or `PWM`).
- `I2C_STEER`: I2C bus for steering.
- `SDC_ENABLE`: Safety/shutdown enable (or `SDC_STAT`/`SDC_FLT` if different).

## Interface examples
`__0_5V` | `__0_10V` | `__5V` | `__3V3` | `__PWM_3V3` | `__PWM_5V` | `__PWM_12V` | `__I2C` | `__12V`

## Examples
`PEDAL_ACC__0_5V` (Accelerator from pedal to ESP32)  
`CMD_BRAKE__0_10V` (Brake command from ESP32 to valve)  
`RES_PRESSURE_1__0_10V` (First reservoir pressure sensor)  
`WHEEL_HALL_2__5V` (Second wheel hall pulse)  
`CMD_STEER_DIR__3V3` (Steering direction command)  
`CMD_STEER__PWM_3V3` (Steering PWM command)  
`I2C_STEER_SDA__I2C` (I2C data line for steering)  
`SDC_ENABLE_LOW_SIDE__12V` (Safety enable via low-side switch)
