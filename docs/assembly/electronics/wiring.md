# Electrical Wiring

Complete electrical wiring diagram for the kart, covering the shutdown circuit, power distribution at multiple voltages, and signal routing between all subsystems.

## Wire Color Code

All wiring on the kart follows this color convention:

| Color | Meaning | Hex |
|---|---|---|
| **Black** | GND (common ground, all systems) | `#333` |
| **Red** | 12 V power | `#d32f2f` |
| **Orange** | 5 V power | `#e65100` |
| **Yellow** | 3.3 V power | `#f9a825` |
| **White / Gray** | Unmarked — no voltage meaning | `#bbb` |

Signal wires (CAN, I2C, analog, PWM) use **white/gray** unless a specific convention applies to that bus.

## Global Wiring Diagram

<object data="images/wiring-global.svg" type="image/svg+xml" style="width:100%;max-width:1100px;"></object>

> **Tip:** All switches in the shutdown chain are in series — opening any one cuts power to the relay coil, which disables the motor controller.

## Related Pages

- [Net Name Nomenclature](net-naming.md) — signal naming conventions across PCBs
- [Throttle Pedal](../powertrain/throttle-pedal.md) — pedal sensor wiring
- [Kart Medulla (ESP32)](kart-medulla/index.md#wiring-connections) — microcontroller wiring connections
- [Emergency Braking](../emergency-braking/index.md) — EBS pneumatic circuit and valve coil wiring
