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

Hand-crafted SVG. Real Festo product photos for the pneumatic brake chain (VPPM, EBS, ADN actuator); inline schematic-style symbols for the rest (battery cell stack, BLDC motor with U/V/W terminals, mushroom kill switches, op-amp triangle, SDC relay coil + NO contacts). [**Open full-size in a new tab ↗**](wiring/images/wiring-global.svg){ target="_blank" }

<object data="wiring/images/wiring-global.svg" type="image/svg+xml" style="width:100%;max-width:2000px;"></object>

> **Tip:** All switches in the shutdown chain are in series — opening any one cuts power to the relay coil, which disables the motor controller.

## Festo pressure sensor connector (M8, 3-pin)

The three pneumatic-pressure sensors are **Festo SDE5-D10-NF-Q6E-V-M8** (part 567465, 0–10 bar range, 0–10 V analog output). Each has an **M8×1, A-coded, 3-pin** plug and connects with the **NEBU-M8G3-K-2.5-LE3** cable (part 541333, wire colours to EN 60947-5-2). All three sensors share this identical pinout.

| M8 pin | Cable wire | Function | On the kart |
|---|---|---|---|
| **1** | Brown (BN) | Supply + | 24 V (sensor rated 15–30 V DC; the 12 V rail is boosted to 24 V for these sensors) |
| **3** | Blue (BU) | 0 V / GND | Common ground |
| **4** | Black (BK) | Analog output 0–10 V | Proportional to 0–10 bar; divided + clamped on the medulla (ESP32-S3 PCB) to ≤ 3.3 V before its ADC |

Socket face (looking into the cable's M8 socket): pin **4** top, **3** left, **1** right.

> **Watch the colours:** these are Festo's standard cable colours per EN 60947-5-2 — they do **not** follow the kart's colour code above. On this cable **black is the signal output (not ground)** and **blue is ground**. Wire by pin number, not by colour.

The output feeds the ESP32 medulla as signals `PRESSURE_1..3` — see [Kart Medulla → Pressure sensor inputs](kart-medulla/index.md#connector-pinout-outside-world). The sensor's own supply and the divider/clamp are on the medulla PCB, not in the harness.

## Related Pages

- [Net Name Nomenclature](net-naming.md) — signal naming conventions across PCBs
- [Throttle Pedal](../powertrain/throttle-pedal.md) — pedal sensor wiring
- [Kart Medulla (ESP32)](kart-medulla/index.md#connector-pinout-outside-world) — microcontroller wiring connections
- [Pneumatic Braking](../pneumatic-braking/index.md) — ASB + EBS pneumatic circuit and valve coil wiring
