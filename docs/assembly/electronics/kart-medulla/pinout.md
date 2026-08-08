<!-- sync_pinout source-sha256: 4c007950a4b6fbab3b441a112788482767e1653f03925b96a5a09a23b91621df -->
!!! info "Generated page — edit it in `dv-hardware`, not here"
    This is a verbatim copy of [`projects/kart-medulla/docs/pinout-cn-connectors.md`](https://github.com/rubenayla/dv-hardware/blob/main/projects/kart-medulla/docs/pinout-cn-connectors.md) in the **dv-hardware**
    repo, which holds the KiCad schematic that defines these assignments. Changes
    made here are overwritten. To update: edit the file in dv-hardware, then run
    `uv run python scripts/sync_pinout.py` in kart-docs and commit the result.

    Related: [Kart Medulla board](index.md) · [whole-kart wire list](../wiring.md#wire-list-whole-kart)
    · ESP32-S3 GPIO map in dv-hardware's `pinout-esp32-s3.md`.

# Push-in connector pinout (CN1–CN10)

> **Authoritative source: the schematic in this same project folder (`../kart-medulla.kicad_sch` + `../kart-medulla_P1.kicad_sch`).** This document mirrors the per-CN pin assignments for human reading. When this doc and the schematic disagree, the schematic wins; fix this file. Re-verify before each fab release.

The medulla PCB has 10 three-pin push-in (1990012) connectors arranged around the ESP32-S3 dev module. Each CN is a 3-pin Wago-style cage-clamp terminal; wires terminate independently per pin (no per-CN cable grouping is required — see `history.md` 2026-05-08 for context).

Connectors are placed in a "chip-pinout" layout to minimize jumper-wire length to the ESP32 module:

  - CN1–CN5 sit on the **right** side of the PCB, **bottom→top** (CN1 closest to USB, CN5 closest to the top edge). They map onto ESP32 pins 1–22 (right edge, RIGHT_HEADER).
  - CN6–CN10 sit on the **left** side, **top→bottom** (CN6 closest to the top edge, CN10 closest to USB). They map onto ESP32 pins 23–44 (left edge, LEFT_HEADER).

Pin numbering within each CN (verified against `kart-medulla.kicad_pcb`, 2026-07-10 — this
used to read "pin 1/2/3 from top to bottom", which is only true of the right-hand side):

  - **CN1–CN5** (right, footprint rotation −90°): pin **1 at top**, pin 3 at bottom.
  - **CN6–CN10** (left, footprint rotation +90°): pin **1 at bottom**, pin 3 at top.

Note the consequence: on the right the CNs advance bottom→top while their pins advance
top→bottom; on the left the CNs advance top→bottom while their pins advance bottom→top. So on
**both** sides the pin numbering runs *counter* to the CN numbering, and on both sides the wire
entry faces **inward**, toward the middle of the board. See the "flip the connectors" task in
`../tasks.md`.

Footprint is `CONN-TH_3P-P2.50-S5.00_1990012`: 2.50 mm pitch, and the pads are **staggered** —
pins 1 and 3 in one row, pin 2 in a row 5.00 mm across. A 180° rotation therefore moves pin 2's
pad row to the opposite side and is not a free change; the copper under each connector must be
re-routed.

## Silkscreen is the authority (v1, the only board that exists)

The table below is transcribed from the **v1 PCB silkscreen** — v1 is the only revision built, so
this is what is physically in front of you:

```
CN1        CN2        CN3        CN4       CN5        CN6        CN7        CN8         CN9          CN10
1 +3V3     1 HALL3    1 EXP_P1   1 SCL     1 HYD2     1 PED_BRK  1 PRES1    1 SDC       1 STEER_PWM  1 CMD_ACC
2 +12V     2 HALL2    2 EXP_P2   2 SDA     2 PRES3    2 PED_ACC  2 PRES2    2 BUZZ      2 HYD1       2 CMD_BRK
3 GND      3 +5V      3 EXP_P3   3 REV     3 EXP_P4   3 +3V3     3 HALL1    3 STEER_DIR 3 GND        3 GND
```

**Two naming traps, both of which have already caused confusion:**

1. **`BUZZ` on CN8.2 is an OLD name.** There is no buzzer on it. The net was repurposed to
   `CMD_COMPRESSOR_PWM` — GPIO 3 driving the EBS compressor MOSFET gate. Wherever `BUZZER` appears
   in this repo it should be read as *(old name)*. Note this collides with the rules-mandated ASSI
   buzzer, which still needs a home — see `projects/kart-medulla/tasks.md`.
2. **`EXP_P2` is CN3.2, and always has been.** The exported netlist
   (`projects/kart-medulla/output/netlist.net`, dated 7 May) lists `CN8.2 → /EXP_P2`, which is
   **wrong** — that file is the known-stale export flagged in `tasks.md`, and it also shows Q3's and
   Q4's gates on no net at all. Trust the silkscreen and this table over that netlist for any
   connectivity question until it is re-exported.

## Assignment table

| CN | Side | Pin 1 | Pin 2 | Pin 3 | Function |
|---|---|---|---|---|---|
| **CN1**  | R, bottom | +3V3 | +12V | GND | **Power input + 3V3 export.** Pin 1 exports the ESP32-derived +3V3 rail (carries PWR_FLAG). Pin 2 = +12V from kart battery. Pin 3 = GND return. |
| **CN2**  | R         | MOTOR_HALL_3 (5V) | MOTOR_HALL_2 (5V) | +5V_REG | Motor hall sensors 2 & 3. Pin 3 supplies +5V from the on-board rail to the hall sensor IC. |
| **CN3**  | R         | EXP_P1 | EXP_P2 | EXP_P3 | Three PCF8574 expander GPIOs clustered next to U25 (PCF8574 placed on the right side of the PCB near CN3 — see `history.md` 2026-05-08 for the cluster decision). |
| **CN4**  | R         | SCL (I²C, 3V3) | SDA (I²C, 3V3) | REVERSE_WIRE | Pins 1 & 2 = I²C bus to the AS5600 steering encoder *and* to U25 (PCF8574); U25 is the only on-PCB I²C device, AS5600 lives off-board on the steering shaft. Pin 3 = REVERSE_WIRE (PCF8574 P0 open-drain output to kart's REVERSE line, wired-OR with manual reverse button on the motor-controller side). |
| **CN5**  | R, top    | HYDRAULIC_2 (0–5V) | PRESSURE_3 (0–10V) | EXP_P4 | Hydraulic-2 pressure sensor + Pressure-3 sensor + spare PCF8574 expander GPIO P4. |
| **CN6**  | L, top    | PEDAL_BRAKE (0–5V) | PEDAL_ACC (0–5V) | +3V3 | Both pedal-position signals + 3V3 power output to whichever sensor needs it. (Carries PWR_FLAG on +3V3.) |
| **CN7**  | L         | PRESSURE_1 (0–10V) | PRESSURE_2 (0–10V) | MOTOR_HALL_1 (5V) | Pressure-1 & Pressure-2 sensors + Motor hall 1. (Halls span CN2 + CN7 because GPIO 16 sits on the left side of the ESP32; see `history.md` 2026-05-08 for why no swap.) |
| **CN8**  | L         | SDC_IN_LOW_SIDE | `BUZZ` **(old name)** = CMD_COMPRESSOR_PWM (3V3) | CMD_STEER_DIR (3V3) | Pin 1 = SDC chain return (Q3 drain). **Pin 2 is silkscreened `BUZZ` but is NOT a buzzer** — the net was repurposed to drive the EBS compressor MOSFET's gate (GPIO 3). It carries a 3.3 V logic signal, not power: the compressor MOSFET is external, added after the board was built, and this pin feeds its gate resistor. Pin 3 = Cytron H-bridge direction. |
| **CN9**  | L         | CMD_STEER_PWM (3V3) | HYDRAULIC_1 (0–5V) | GND | Pin 1 = Cytron H-bridge PWM. Pin 2 = Hydraulic-1 sensor. Pin 3 = GND return for the left-side analog/SDC group. |
| **CN10** | L, bottom | CMD_ACC (0–5V) | CMD_PRES (0–10V) | GND | Pin 1 = throttle command, MCP4922 VOUTA via the MAX4660 mux, to the motor controller. Pin 2 = **pressure command to the Festo VPPM proportional regulator, not to the motor controller** — braking on this kart is pneumatic. It is VOUTB amplified ×2 by the LM358 (U1A), so 0–10 V leaves the board, not the DAC's 0–5 V. The net was called `CMD_BRAKE` until 2026-07-31; it is `CMD_PRES__0_10V` now, because the signal is a pressure setpoint for a proportional regulator rather than a brake-force command. The silkscreen on the built board still reads `CMD_BRK`. Pin 3 = GND, and it is also the **return the VPPM's setpoint is measured against**: the valve runs from a separate 24 V supply, so that supply's 0 V must be common with the medulla's GND or the commanded pressure shifts by whatever the offset is. |

## The pneumatic side — three devices, three supplies, only one of them on a medulla pin

Written 2026-07-31 because "the valve" was being used to mean different things. Sources:
`~/dv/kart/pneumatics/README.md` and `~/dv/kart/pneumatics/history.md` (2026-05-30).

| Device | Festo part | Its own supply | What the medulla does |
|---|---|---|---|
| **VPPM-8L proportional pressure regulator** | 571293 | **24 V DC** (21.6–26.4 V, 300 mA, 7 W) from a UENPO 9–36 V → 24 V buck-boost | Drives its **0–10 V setpoint** out of **CN10.2** (`CMD_PRES__0_10V`). GND on **CN10.3** is the return that setpoint is measured against. The medulla does **not** supply its 24 V. |
| **EBS emergency electrovalve** (and the ASB valve) | 8035174 / 8035167, VUVS-LT25 | **12 V** coils, switched by the **shutdown relay** | Nothing. No medulla pin touches it. |
| **SDE5 pressure sensors** | 567465 | 15–30 V, fed from the same 24 V rail | Reads their **0–10 V outputs** on `PRESSURE_1`/`PRESSURE_2` (CN7.1, CN7.2) through dividers |

The setpoint and the supply are different things on the VPPM: 0–10 V is the command, 24 V is what
powers the valve. When a note here says a 24 V fault could reach a medulla pin, it means the VPPM's
supply appearing on CN10.2 through a harness fault — not the EBS valve, which is 12 V and not wired
to this board at all.

The VPPM setpoint is a signal input and the LM358 drives it directly; its input impedance was
treated as an open question until 2026-07-31 and is not one.
## Voltage levels — quick reference

| Suffix in signal name | Meaning |
|---|---|
| `__3V3` | 3.3 V logic level (ESP32 native) |
| `__5V` | 5 V logic level (motor hall, level-shifted by U5 to 3V3 before reaching the ESP32) |
| `__0_5V` | analog 0–5 V (sensors, DAC outputs) |
| `__0_10V` | analog 0–10 V (pressure sensors) |
| no suffix on power names (`+12V`, `+3V3`, `+5V_REG`) | rail of that nominal voltage |

`SDC_IN_LOW_SIDE` is the drain of Q3 (IRLZ44N): nominally 0 V when Q3 conducts (no emergency), floats up to whatever the upstream SDC node sits at (≤ 12 V) when Q3 is off (emergency). Treat it as a 12-V-tolerant line.

## Power architecture summary (where each rail comes from)

  - `+12V`         — externally, from the kart battery, via **CN1 pin 2**.
  - `+5V_REG`      — on-board L7805CDT linear regulator (U19), or the external XW-1224 5 V rail tied in via the same net, feeds the `+5V_REG` global net.
  - `+3V3`         — generated by the ESP32-S3 module's on-board LDO from its 5 V input. Available on LEFT_HEADER pins 23/24 of the dev module.
  - `+5V_USB`      — independent 5 V rail from the medulla USB-C connector; powers only the ESP32 dev module (split-rail design, see `pinout-esp32-s3.md`).

The single `power:+12V` symbol that asserts the `+12V` rail name is placed at CN1 pin 2 (the entry point). Same convention applies to `+3V3` and `+5V_REG` symbols on whichever CN exports them — the symbol just declares the rail and can sit anywhere on the net.

## Cross-reference

  - ESP32 module pinout → `pinout-esp32-s3.md` (which GPIO drives which signal in the table above).
  - PCB physical layout / silkscreen → the `kart-medulla.kicad_pcb` file in this folder. The silkscreen legend that lists the 21 numbered external signals is being updated to match this assignment.
  - Decision history → `../../../history.md` entry `2026-05-08 — kart-medulla CN1–CN10 pin assignments locked to ESP32 geometry`.
