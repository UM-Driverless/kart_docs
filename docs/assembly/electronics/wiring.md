# Electrical Wiring

Complete electrical wiring diagram for the kart, covering the shutdown circuit, power distribution at multiple voltages, and signal routing between all subsystems.

## Wire Color Code

This is the colour convention **for the wiring we build ourselves** — the hand-made harness between subsystems. It is a house guideline, not a rule the whole kart obeys: this is a prototype assembled from third-party parts, and those parts keep their vendors' own colour codes. Two notable exceptions:

- **Off-the-shelf DC-DC power regulators** land on the rear **Wago** connectors with their own fixed output-wire colours, following the module's standard rather than this table.
- **Festo** sensor and valve cables follow **EN 60947-5-2** (see the [pressure-sensor note](#festo-pressure-sensor-connector-m8-3-pin) below) — e.g. blue is ground and black is a signal output, the opposite of this table.

Where we do run our own wire:

| Color | Meaning | Hex |
|---|---|---|
| **Black** | Power GND — return for motors, valves, coils, and the power rails | `#333` |
| **Black + white stripe** | Signal GND — return for sensors and analog/logic references | `#333` / `#fff` |
| **Red** | 12 V power | `#d32f2f` |
| **Orange** | 5 V power | `#e65100` |
| **Yellow** | 3.3 V power | `#f9a825` |
| **White / Gray** | Deliberately unassigned — carries no meaning | `#bbb` |

**White and gray are the escape hatch, and that is their job.** Every other colour in the
table is a promise about what the wire carries, so using one wrongly is worse than using
none: someone later reads the promise and trusts it. White carries no promise, so you can
wire anything with it — a one-off, a bodge, a bus nobody has a convention for — without
breaking the code or having to invent a new colour first. Reach for white whenever the
right colour is not obvious. Signal wires we run ourselves (I²C, analog, PWM) use white or
gray by default, unless a specific convention applies to that bus.

A **stripe** modifies the base colour rather than adding a second meaning, so the white
stripe on signal ground is not an exception to this: the wire is black, and black means
ground. Solid white and striped black are hard to confuse in the harness.

### Why two grounds

Motor, valve, and coil currents are large and switch fast. Sharing a return wire with a
sensor puts that current's voltage drop directly in series with the sensor reading, so the
measurement moves when the motor does. Separating the returns keeps that drop out of the
sensitive path.

Both grounds are the same electrical node — they are **joined at exactly one point**, the
star point. On this kart that point is the **rear ground Wago terminal block**, near the
battery and the 12 V / 24 V regulators; it appears in the wire list below as the device
`wago_gnd`. Two joins would create a loop and undo the separation, so no other place in the
harness may bond the two. The stripe is there so that anyone tracing the harness can tell,
without a meter, which return a wire belongs to and therefore where it is allowed to land.

If striped wire is hard to source in a given gauge, use plain black with a **white
heatshrink band at both ends** — same meaning, same rule.

## Global Wiring Diagram

Hand-crafted SVG. Real Festo product photos for the pneumatic brake chain (VPPM, EBS, ADN actuator); inline schematic-style symbols for the rest (battery cell stack, BLDC motor with U/V/W terminals, mushroom kill switches, op-amp triangle, SDC relay coil + NO contacts). [**Open full-size in a new tab ↗**](wiring/images/wiring-global.svg){ target="_blank" }

<object data="wiring/images/wiring-global.svg" type="image/svg+xml" style="width:100%;max-width:2000px;"></object>

> **Tip:** All switches in the shutdown chain are in series — opening any one cuts power to the relay coil, which disables the motor controller.

## Wire list (whole kart)

One row per **net** (electrical node) across the whole kart — the tabular companion to the diagram above. The **Connected pins** column lists every `device.pin` tied together; medulla (the kart's ESP32-S3 interface PCB) `CNx.y` terminals map to GPIOs on the [Kart Medulla connector pinout](kart-medulla/index.md#connector-pinout-outside-world). This table is **generated** from [`wiring/wiring.yaml`](https://github.com/um-driverless/kart-docs/blob/main/docs/assembly/electronics/wiring/wiring.yaml) — edit the YAML, not the table; completeness is checked by `scripts/check_wiring.py`.

!!! note "Scope and source of truth"
    Only the **kart-medulla PCB** has a KiCad project (`dv-hardware`) as its authoritative netlist — trust that for the medulla-internal nets. The rest of the kart (power distribution, traction, shutdown chain, motor) is **not** in KiCad; those rows are transcribed from the diagram and subsystem docs and should be **field-verified** before you rely on them. Wire colours follow the [house code](#wire-color-code) for wiring we run ourselves; vendor cables (Festo, power modules) keep their own colours, and 48 V pack cabling has no assigned code colour.

<!-- WIRING_TABLE -->

## Festo pressure sensor connector (M8, 3-pin)

The three pneumatic-pressure sensors are **[Festo SDE5-D10-NF-Q6E-V-M8](https://www.festo.com/es/es/a/567465/)** (part 567465, 0–10 bar range, 0–10 V analog output; [datasheet](../../assets/datasheets/567465datasheet.pdf)). Each has an **M8×1, A-coded, 3-pin** plug and connects with the **[NEBU-M8G3-K-2.5-LE3](https://www.festo.com/es/es/a/541333/)** cable (part 541333, wire colours to EN 60947-5-2). All three sensors share this identical pinout.

| M8 pin | Cable wire | Function | On the kart |
|---|---|---|---|
| **1** | Brown (BN) | Supply + | 24 V rail — sensor rated 15–30 V DC. This 24 V is a *planned* shared supply with the VPPM valve (from a 9–36 V → 24 V buck-boost, **not yet fitted**); the SDE5 also runs fine at 15–19 V. |
| **3** | Blue (BU) | 0 V / GND | Common ground |
| **4** | Black (BK) | Analog output 0–10 V | Proportional to 0–10 bar; divided + clamped on the medulla (ESP32-S3 PCB) to ≤ 3.3 V before its ADC |

Socket face (looking into the cable's M8 socket): pin **4** top, **3** left, **1** right.

> **Watch the colours:** these are Festo's standard cable colours per EN 60947-5-2 — they do **not** follow the kart's colour code above. On this cable **black is the signal output (not ground)** and **blue is ground**. Wire by pin number, not by colour.

The outputs feed the ESP32 medulla as `PRESSURE_1` and `PRESSURE_2` (terminals CN7.1 / CN7.2) — see [Kart Medulla → Connector pinout](kart-medulla/index.md#connector-pinout-outside-world). The former `PRESSURE_3` terminal (CN5.2) has been **repurposed to the steering-angle PWM input** (see below), so it no longer reads a pressure sensor. Each sensor's supply and its divider/clamp live on the medulla PCB, not in the harness.

## Steering angle sensor wiring

The steering-angle sensor tells the medulla where the front wheels point, closing the steering position loop.

**Current (validated):** an **AS5600** magnetic encoder at the front of the steering, read over **I²C** (medulla `SDA` = GPIO 8, `SCL` = GPIO 9; address 0x36). The bus run is short, and it works today.

**Planned (rear-mounted board): MT6701 over single-wire PWM.** Once the medulla PCB moves to the rear near the Orin, the I²C run (~1.2–2 m) becomes unreliable — a single glitch can hang the shared bus (the on-board PCF8574 sits on the same bus). The fix is a **MagnTek MT6701** encoder that sends its angle as a **PWM duty cycle on a single wire** (3.3 V CMOS square wave, ~994 Hz frame). It reuses the freed `PRESSURE_3` terminal.

| MT6701 module pin | Medulla terminal / ESP32-S3 | Notes |
|---|---|---|
| VCC | 3.3 V (CN1.1 / CN6.3) | 5 V only needed for a one-time EEPROM burn |
| GND | Signal GND (`GND_SIG`) | **Not yet resolved to a terminal.** CN1.3 / CN9.3 / CN10.3 are the medulla's ground terminals, but they are currently recorded on the *power* ground net, and this sensor's return belongs on [signal GND](#why-two-grounds). Landing it on a power-ground terminal would bond the two grounds a second time. Check the KiCad project for the board's analog ground before wiring — see the open task in `tasks.md`. |
| SDA | GPIO 8 (I²C) | MT6701 address 0x06 (PCF8574 is 0x20 — no clash). Used for config + a bench angle cross-check |
| SCL | GPIO 9 (I²C) | |
| OUT (PWM) | **CN5.2 → R8 → R9 → GPIO 1** | 20 kΩ series into the ESP32-S3 MCPWM capture. **Board rework: remove R10 only** (keep R8 + R9). |
| MODE | Tie for I²C/SSI | If left in ABZ mode, I²C won't respond |

The PWM wire is a plain signal line (kart color code: white/gray); keep it short and ideally twisted with its ground or shielded. Board topology after rework: `CN5.2 —[R8 10k]— node —[R9 10k]— GPIO 1 —[R10 removed]`. See [Angle Sensor](../steering/sensor/index.md) for why the MT6701 was chosen, and [Kart Medulla](kart-medulla/index.md#connector-pinout-outside-world) for the terminal-level detail.

## Festo valve & actuator connectors

Beyond the pressure sensors, the pneumatic brake chain uses two more Festo connector types. Full part detail is in the [Pneumatic Braking BOM](../pneumatic-braking/bom.md); the wiring-relevant summary:

- **[VPPM proportional brake valve](https://www.festo.com/es/es/a/571293/)** (VPPM-8L-L-1-G14-0L10H-V1P-S1C1, part 571293; [catalog doc](../../assets/datasheets/205274_documentation.pdf) · [datasheet](../../assets/datasheets/VPPM_en.pdf)) — sets the autonomous brake pressure. Cable **[NEBU-M12W8-K-2-N-LE8](https://www.festo.com/es/es/a/542256/)** (part 542256), **M12 8-pin shielded**. Supply 24 V (21.6–26.4 V), setpoint 0–10 V from the medulla brake DAC (MCP4922 channel B → ×2 op-amp), max draw ~300 mA. **Pins 1 and 5 are digital inputs D1/D2** (control-response select) — energising them locks out the valve's front-panel button config, so leave them per the datasheet. Take the per-wire colour map from the 542256 cable datasheet (linked in the BOM); it is deliberately not reproduced here rather than risk an unverified pinout.
- **Solenoid valve coils** (EBS = Emergency Braking System, plus the spare ASB = Autonomous Service Brake) — DIN form connectors, **not** M8/M12. The EBS coil ([VACF-B-C1-5](https://www.festo.com/es/es/a/8030810/), part 8030810) is **form C** and mates with the **[MSSD-EB](https://www.festo.com/es/es/a/151687/)** plug (part 151687); the spare ASB coil ([VACF-B-B2-5](https://www.festo.com/es/es/a/8030801/), part 8030801) is **form B** and needs its own plug — they are not interchangeable. Both coils are 12 V DC / 3.4 W off the 12 V rail. See the [BOM](../pneumatic-braking/bom.md) for the coil-interchangeability warning.

## Related Pages

- [Net Name Nomenclature](net-naming.md) — signal naming conventions across PCBs
- [Throttle Pedal](../powertrain/throttle-pedal.md) — pedal sensor wiring
- [Steering Angle Sensor](../steering/sensor/index.md) — AS5600 → MT6701 sensor choice and calibration
- [Kart Medulla (ESP32)](kart-medulla/index.md#connector-pinout-outside-world) — microcontroller wiring connections
- [Pneumatic Braking](../pneumatic-braking/index.md) — ASB + EBS pneumatic circuit and valve coil wiring
