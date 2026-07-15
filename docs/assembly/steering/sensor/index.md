# Steering Angle Sensor

The steering angle sensor measures the column angle for the steering PID loop. It reads a magnet mounted on the steering shaft and reports the absolute angle to the Kart Medulla ESP32.

## Current sensor: AS5600 over I²C (validated)

The **AS5600** magnetic angle encoder, read over **I²C**, is the sensor currently on the kart. It is **mounted at the FRONT** of the kart, close to the steering shaft, so the I²C run is short. It has been reading steering angle with the kart's magnets already installed, working, for a long time — it is the validated, in-use sensor.

![](images/20250608181732.png)

### AS5600 wiring (I²C)

!!! warning "Temporary color code"
    This color code is specific to the hand-wired setup and is not official. Verify connections before use.

| Color | Signal |
|-------|--------|
| Grey / Black | GND |
| White | 3.3 V |
| Green | SDA |
| Blue | SCL |

(The `dv`/kart-medulla wiring note from 2026-03 lists GND as **black**; the earlier 2025 harness used grey. Check the actual wire before trusting the colour.) For which ESP32 pins the I²C bus lands on, see the [Kart Medulla](../../electronics/kart-medulla/index.md) and [Wiring](../../electronics/wiring.md) pages.

## Plan of record: MagnTek MT6701 (single-wire PWM, rear)

The next sensor is the **MagnTek MT6701**, a magnetic angle encoder read over its **single-wire PWM output**. It will be **mounted at the REAR**, near the Orin and the Kart Medulla, feeding the ESP32 over one robust signal wire.

**Why swap — cable distance.** The plan is to relocate the Kart Medulla PCB to the rear (it must sit near the Orin — the two boards connect over USB). That puts the ESP32 roughly **1.2 m** from the steering shaft. I²C does not survive that run: it is noise-sensitive, and one glitch can hang the **shared PCF8574 bus** on the medulla, taking down more than just the steering read. A single-wire PWM angle signal is robust over the distance and never touches the shared I²C bus. Source: `dv/kart/steering/history.md` 2026-07-11 and 2026-07-14.

**Hardware status:** the MT6701 module was purchased on AliExpress (~€10) and is expected to arrive around **2026-07-22**. Until then the AS5600 stays in front; the swap is non-gating cleanup, not a blocker for starting steering tests.

### MT6701 details

| Property | MT6701 | vs AS5600 |
|---|---|---|
| Sensing principle | In-plane (x-y) field **direction** — magnetic angle encoder | AS5600 senses the axial (Bz) gradient over a 1 mm circle |
| I²C address | **0x06** (7-bit) | AS5600 is 0x36 — driver must change |
| I²C angle registers | **0x03** (Angle[13:6]) then **0x04** (Angle[5:0] in bits 7:2), 14-bit | AS5600 is 0x0C/0x0D, 12-bit |
| Config storage | **EEPROM — reprogrammable** | AS5600 is one-shot OTP (irreversible) |
| Output-mode register | **0x38**, `OUT_MODE` = **bit 5** (0 = analog, 1 = PWM); bit 7 = `PWM_FREQ`, bit 6 = `PWM_POL` | AS5600 uses CONF `OUTS` bits |
| PWM frame frequency | **~994.4 Hz** (or 497.2 Hz via `PWM_FREQ`) | AS5600 PWM was 920 Hz |
| EEPROM programming voltage | 4.5–5.5 V to program; reads/operates fine at 3.3 V | AS5600 OTP burns at 3.3 V |

The MT6701 handles the kart's big, roughly-uniform shaft field better than the AS5600 because it senses field **direction** rather than a gradient — but it still wants a reasonably centred magnet at a sane air gap; it is not a licence for arbitrary mounting sloppiness. Source: `dv/kart/steering/mt6701-pwm-bringup-runbook.md`, `kart-medulla/history.md` 2026-07-12.

### Abandoned / alternative sensors

- **AS5600 PWM output** — briefly attempted so the front AS5600 could send a single wire to the rear, but abandoned: the OUT stage on the bench module was dead (never produced PWM), and I²C-only left it unable to survive the long run. Its PWM mode also needs a one-time OTP burn (irreversible).
- **MagAlpha MA732** — a documented fallback (same in-plane direction-sensing class, native PWM, and better off-axis tolerance). It was the sensor-research *pick*, but it is a bare QFN chip needing a breakout, pricier and slower to source. It was **not bought**; the cheaper, in-hand MT6701 is the plan of record. Keep the MA732 in mind only if the MT6701's on-axis mounting fights the kart's sideways-magnet geometry.

## Electrical connection

The wiring and firmware detail for the sensor input — the CN5.2 terminal, GPIO 1 on the ESP32-S3, removing the R10 pulldown, and MCPWM pulse capture — is **not duplicated here**. See:

- [Wiring](../../electronics/wiring.md) — the electrical connection (which terminal, which GPIO, resistor changes).
- [Kart Medulla](../../electronics/kart-medulla/index.md) — the board and pinout.

## Operating point (steering actuator context)

The sensor closes a loop around a column-driven steering actuator (there is **no rack** on the kart). Ballpark operating point, for context:

| Quantity | Value |
|---|---|
| Column torque target | ~8 Nm (sized with margin; ~4 Nm minimum to break the tyres loose stopped) |
| Total reduction | ~**11:1** (4.67:1 planetary × 2.38:1 pinion) |
| Steering range | ~±25° at the column (≈50° lock-to-lock) |
| Nominal power | ~**47 W** (8 Nm × ~6 rad/s during a ~0.15 s lock-to-lock) |
| Stall (worst case) | ~**2 kW** (≈47 V × 43 A into the windings — reserve, almost all heat, not an operating point) |

Source: `dv/kart/steering/README.md` (kart canonical operating point). The dv README points at a `power-budget.md` that does not exist; these numbers are consolidated here for reference.

## Code repository

Basic code to read the steering angle sensor (Arduino HAL with VSCode PlatformIO, no IDE): <https://github.com/rubenayla/bluepill-angle-arduino.git>

![](images/20250608181003.png)
![](images/20250608181018.png)
