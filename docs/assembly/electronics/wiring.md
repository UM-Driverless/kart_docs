# Electrical Wiring

Complete electrical wiring diagram for the kart, covering the shutdown circuit, power distribution at multiple voltages, and signal routing between all subsystems.

## Wire Color Code

This is the colour convention **for the wiring we build ourselves** — the hand-made harness between subsystems. It is a house guideline, not a rule the whole kart obeys: this is a prototype assembled from third-party parts, and those parts keep their vendors' own colour codes. Two notable exceptions:

- **Off-the-shelf DC-DC power regulators** land on the rear **Wago** connectors with their own fixed output-wire colours, following the module's standard rather than this table.
- **Festo** sensor and valve cables follow **EN 60947-5-2** (see the [pressure-sensor note](#festo-pressure-sensor-connector-m8-3-pin) below) — e.g. blue is ground and black is a signal output, the opposite of this table.

Where we do run our own wire:

| Color | Meaning | Hex |
|---|---|---|
| **Black** | GND (common ground, all systems) | `#333` |
| **Red** | 12 V power | `#d32f2f` |
| **Orange** | 5 V power | `#e65100` |
| **Yellow** | 3.3 V power | `#f9a825` |
| **White / Gray** | Unmarked — no voltage meaning | `#bbb` |

Signal wires we run ourselves (I2C, analog, PWM) use **white/gray** unless a specific convention applies to that bus.

## Global Wiring Diagram

Hand-crafted SVG. Real Festo product photos for the pneumatic brake chain (VPPM, EBS, ADN actuator); inline schematic-style symbols for the rest (battery cell stack, BLDC motor with U/V/W terminals, mushroom kill switches, op-amp triangle, SDC relay coil + NO contacts). [**Open full-size in a new tab ↗**](wiring/images/wiring-global.svg){ target="_blank" }

<object data="wiring/images/wiring-global.svg" type="image/svg+xml" style="width:100%;max-width:2000px;"></object>

> **Tip:** All switches in the shutdown chain are in series — opening any one cuts power to the relay coil, which disables the motor controller.

## Wire list (whole kart)

One row per wire/net across the whole kart — the tabular companion to the diagram above. Read `From` → `To` as the two physical ends; medulla terminals are written `CNx.y` and map to GPIOs on the [Kart Medulla connector pinout](kart-medulla/index.md#connector-pinout-outside-world).

!!! note "Scope and source of truth"
    Only the **kart-medulla PCB** has a KiCad project (`dv-hardware`) as its authoritative netlist — trust that for the medulla-internal nets. The rest of the kart (power distribution, traction, shutdown chain, motor) is **not** in KiCad; those rows are transcribed from the diagram and subsystem docs and should be **field-verified** before you rely on them. Wire colours follow the [house code](#wire-color-code) for wiring we run ourselves; vendor cables (Festo, power modules) keep their own colours, and 48 V pack cabling has no assigned code colour.

| System | Signal / net | From | To | Nominal | Colour | Notes |
|---|---|---|---|---|---|---|
| Power | 48 V pack + | Battery 13S + | Motor Controller (ESC) V+ | 48 V | red (heavy) | High-current traction feed |
| Power | 48 V pack + | Battery 13S + | Buck Regulator in + | 48 V | red (heavy) | Feeds the 48→12 V converter |
| Power | GND | Battery 13S − | Common ground | 0 V | black (heavy) | Pack negative = system GND |
| Power | 12 V rail | Buck Regulator out | 12 V distribution | 12 V | red | Single 48→12 V conversion (Weishuo Y3-T4812) |
| Power | 12 V | 12 V rail | Jetson AGX Orin barrel jack | 12 V | red | Orin power |
| Power | 12 V | 12 V rail | Cytron H-bridge V+ | 12 V | red | Steering driver — always powered, **not** switched by mode |
| Power | 12 V | 12 V rail | SDC chain (Kill 1) | 12 V | red | Source for the shutdown circuit |
| Power | 5 V + data | Jetson Orin USB-C | Medulla dev-board VBUS | 5 V | orange | Powers the ESP32 board and carries the USB-serial link (split-rail; may instead come from a 12→5 V buck) |
| Traction | U / V / W | Motor Controller (ESC) | 3-phase BLDC motor | 48 V | — | Traction motor drive |
| Traction | CMD_ACC (gated) | Mode Switch out | ESC throttle in | 0–5 V | white/gray | Auto = DAC, manual = pedal (SPDT select) |
| Throttle | PEDAL_ACC | Accelerator pedal (linear Hall) | Medulla CN6.2 (GPIO 4, ADC) | 0–5 V | white/gray | Pedal position; scaled to ADC on the PCB |
| Throttle | Acc pedal (manual) | Accelerator pedal | Mode Switch (NC contact) | 0–5 V | white/gray | Manual passthrough when ESP32 is not driving |
| Throttle | CMD_ACC (DAC) | Medulla CN10.1 (MCP4922 A) | Mode Switch (auto input) | 0–5 V | white/gray | Autonomous throttle command |
| Steering | Angle (I²C, current) | Steering sensor AS5600 | Medulla CN4.1/4.2 (SCL GPIO 9 / SDA GPIO 8) | 3.3 V | white/gray | Front-mounted, short I²C run |
| Steering | Angle PWM (planned) | MT6701 OUT | Medulla CN5.2 (GPIO 1) | 3.3 V | white/gray | Future rear sensor, single-wire PWM (R10 removed) |
| Steering | CMD_STEER_PWM | Medulla CN9.1 (GPIO 40) | Cytron H-bridge PWM | 3.3 V | white/gray | Steering speed |
| Steering | CMD_STEER_DIR | Medulla CN8.3 (GPIO 17) | Cytron H-bridge DIR | 3.3 V | white/gray | Steering direction |
| Steering | M+ / M− | Cytron H-bridge out | Steering motor | 12 V | — | Motor drive |
| Brake | PEDAL_BRAKE | Brake pedal (linear Hall) | Medulla CN6.1 (GPIO 5, ADC) | 0–5 V | white/gray | Pedal position; scaled on PCB |
| Brake | CMD_BRAKE (0–5 V) | Medulla CN10.2 (MCP4922 B) | Op-amp ×2 in | 0–5 V | white/gray | Brake setpoint from DAC |
| Brake | CMD_BRAKE (0–10 V) | Op-amp ×2 out | VPPM setpoint | 0–10 V | white/gray | Proportional brake pressure command |
| Brake | Air (regulated) | VPPM valve | Brake actuator (Festo ADN) | pneumatic | — | Autonomous service brake |
| Brake | Air (full) | EBS solenoid (Festo VUVS) | Brake actuator (Festo ADN) | pneumatic | — | Emergency braking |
| Brake | EBS coil 12 V | SDC Relay (gated 12 V) | EBS solenoid coil | 12 V | red | Energised only when SDC is closed; Festo form-C connector |
| SDC | Chain source | 12 V rail | Kill 1 | 12 V | red | Chain start (no panel ignition key) |
| SDC | Chain | Kill 1 | Impact switch | 12 V | white/gray | Series |
| SDC | Chain | Impact switch | Remote E-Stop (RES) | 12 V | white/gray | Series |
| SDC | Chain | Remote E-Stop (RES) | Kill 2 | 12 V | white/gray | Series |
| SDC | Chain | Kill 2 | Kill 3 | 12 V | white/gray | Series |
| SDC | Chain → coil | Kill 3 | SDC Relay coil | 12 V | white/gray | Opening any switch drops the coil |
| SDC | Relay NO | SDC Relay NO contacts | ESC 2-wire key loop | — | — | Closing arms the ESC (kit pigtail) |
| SDC | Medulla tie-in | Medulla CN8.1 (SDC) | Shutdown chain (Q3 low side) | — | white/gray | On the S3 PCB the medulla can pull the chain low via Q3 (GPIO 18 internal) |
| Sensors | PRESSURE_1 | Festo SDE5 sensor 1 | Medulla CN7.1 (GPIO 6, ADC) | 24 V / 0–10 V | brown·blue·black | Festo M8, EN 60947-5-2 (see below) |
| Sensors | PRESSURE_2 | Festo SDE5 sensor 2 | Medulla CN7.2 (GPIO 7, ADC) | 24 V / 0–10 V | brown·blue·black | Festo M8, EN 60947-5-2 |
| Sensors | HYDRAULIC_1 | Hydraulic pressure sensor 1 | Medulla CN9.2 (GPIO 10, ADC) | ? | white/gray | Supply/range to confirm |
| Sensors | HYDRAULIC_2 | Hydraulic pressure sensor 2 | Medulla CN5.1 (GPIO 2, ADC) | ? | white/gray | Supply/range to confirm |
| Sensors | MOTOR_HALL_1 | BLDC motor Hall 1 | Medulla CN7.3 (GPIO 16) | 5 V | white/gray | Level-shifted to 3.3 V on PCB |
| Sensors | MOTOR_HALL_2 | BLDC motor Hall 2 | Medulla CN2.2 (GPIO 47) | 5 V | white/gray | Level-shifted on PCB |
| Sensors | MOTOR_HALL_3 | BLDC motor Hall 3 | Medulla CN2.1 (GPIO 21) | 5 V | white/gray | Level-shifted on PCB |
| Compute | USB serial | Jetson Orin USB | Medulla (ESP32 USB) | 5 V + data | orange | Orin↔ESP32 command/telemetry link (no CAN) |
| Compute | USB 3.0 | ZED2 stereo camera | Jetson Orin | 5 V + data | — | Perception camera |
| Medulla supply | +3V3 | Medulla CN1.1, CN6.3 | External 3.3 V sensors (e.g. MT6701) | 3.3 V | yellow | Medulla supplies sensor power |
| Medulla supply | +5V | Medulla CN2.3 | External 5 V loads | 5 V | orange | |
| Medulla supply | +12V | Medulla CN1.2 | 12 V available at terminal | 12 V | red | |
| Medulla supply | GND | Medulla CN1.3, CN9.3, CN10.3 | Common ground | 0 V | black | |
| Medulla I/O | EXP_P1–P4 | Medulla CN3.1–3, CN5.3 (PCF8574 0x20) | Spare I²C-expander I/O terminals | 3.3 V | white/gray | On-board GPIO-expander pins brought to terminals |
| Medulla I/O | REVERSE | Medulla CN4.3 | Kart electronics-box reverse wire | 5 V | white/gray | Driven by U12; pull to 0 V to engage reverse |

Rows marked `?` or "to confirm" are not yet verified — treat them as gaps to close, not facts. Medulla-internal nets are authoritative in the `dv-hardware` KiCad project.

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
| GND | GND (CN1.3 / CN9.3 / CN10.3) | Common ground |
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
