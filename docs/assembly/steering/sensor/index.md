# Steering Angle Sensor

The steering angle sensor measures the column angle for the steering PID loop. It reads a magnet
mounted on the steering shaft and reports the absolute angle to the Kart Medulla ESP32.

## Current sensor: MagnTek MT6701, read as PWM

The **MT6701** is the sensor on the kart. It is a magnetic angle encoder, permanently configured in
its EEPROM to output the angle on a **single wire as a PWM signal** — the angle is encoded in the
duty cycle, not sent over a bus.

| Property | Value |
|---|---|
| Output | Single-wire PWM, ~994.4 Hz frame rate, high-valid |
| Resolution | 12 bits over a frame of 4119 clock periods — one count is 0.088°, a 244 ns slice of edge timing |
| Read by | ESP32-S3 MCPWM capture on **GPIO 1** (terminal CN5.2), both edges timestamped in hardware |
| I²C address | 0x06, if ever needed — but the kart's angle does **not** come over I²C |
| Recommended magnet | Ø6 × 2.5 mm diametric, air gap 0.5–2.0 mm, off-axis ≤ 0.3 mm |

**It is validated on the kart, not just wired up.** The firmware counts accepted and rejected PWM
frames and reports both in its health telemetry. On the kart that counter climbs at **993 frames
per second with zero rejects**, against the sensor's nominal 994.4 Hz. That is the measurement that
separates "reading the sensor" from "reading something": a capture triggering on electrical noise
would show rejects climbing, and a dead line would show the count flat. Neither happens.

The reading is never smoothed or held: the firmware returns the newest decoded frame, and returns
an explicit *invalid* rather than a number whenever no fresh frame has arrived. The PID stops the
steering motor instead of acting on an unknown angle.

!!! note "Off-axis mounting degrades, it does not fail"
    Past the 0.3 mm off-axis figure the MT6701 does not drop out — the error grows smoothly as a
    once-per-revolution distortion, and the angle stays continuous and repeatable. That number is
    where the datasheet *guarantees* rated accuracy, not a cliff. For kart steering, where a few
    degrees is acceptable, mounting tolerance is not a hard constraint. This is a different failure
    class from the AS5600's reported bench behaviour, which was a *detection* failure.

## Why this sensor, and not the AS5600

**Mounted at the front**, on a 3D-printed adjustable mount, close to the steering shaft. The mount is
adjustable so the magnet-to-sensor air gap and the angular zero can be trimmed after assembly rather
than being fixed by the print.

!!! warning "The two repos give different reasons for the swap — unresolved"
    This page cannot state the reason as settled, because the sources disagree and the difference
    matters for anyone choosing a sensor later.

    **`kart-medulla/history.md` (2026-07-11/12)** says the AS5600 could not work here at all. It
    reconstructs the angle from how the *axial* field varies across a 1 mm circle on its die, and the
    kart's shaft magnet is two large magnets stuck sideways, giving a field that is strong but nearly
    uniform over that span. On the bench, with the chip touching the magnet, its magnet-detect flag
    stayed at zero and it gated its own output. The MT6701 senses in-plane field *direction* at a
    point instead, which a large magnet defines cleanly.

    **`~/dv/kart/steering/history.md` (2026-07-31)** says the opposite: *"magnet tolerance turned out
    not to be a real risk on this kart — the AS5600 already read the installed magnets fine, and the
    MT6701 confirms it."* On that reading, the MT6701 won on its single-wire PWM output rather than on
    magnet handling.

    Both may be true of different setups — the bench magnet was handheld, the kart's is mounted — but
    nobody has reconciled them. Filed in `tasks.md`.

### The cable-length argument no longer applies

Earlier docs give the reason as distance, and that needs untangling because the wording survives in
several places.

On 2026-07-11 the plan was to **move the Kart Medulla PCB to the rear**, next to the Orin — the two
have to connect over USB, and the compressor and Hall sensors are already back there. The steering
sensor would have stayed on the shaft at the front, leaving the board about **1.2 m** from it. I²C
does not survive that run: it is single-ended open-drain, easy to glitch next to the 48 V motor
phases, and one glitch on SCL hangs the bus — which the on-board PCF8574 shares. So a single-wire
PWM sensor was the recommended fix.

**That board relocation never happened and is not pending.** Board and sensor are both at the front,
the run is short, and since no I²C mode is used for the angle the shared-bus concern does not arise
either. The MT6701 stayed regardless: it was already bought, configured and validated, and PWM
works fine over a short run too.

!!! note "A bigger magnet is not a licence for sloppy mounting"
    The MT6701's datasheet asks for essentially the same small diametric magnet, tight air gap and
    centring as the AS5600. Whatever it tolerates, it is not arbitrary mounting error — which is why
    the mount is adjustable.

## Electrical connection

The wiring and firmware detail for the sensor input — the CN5.2 terminal, GPIO 1 on the ESP32-S3,
removing the R10 pulldown, and MCPWM pulse capture — is **not duplicated here**. See:

- [Wiring](../../electronics/wiring.md) — the electrical connection (which terminal, which GPIO, resistor changes).
- [Kart Medulla](../../electronics/kart-medulla/index.md) — the board and pinout.
- [Firmware](../../electronics/kart-medulla/firmware.md) — how the angle feeds the steering PID.

## Operating point (steering actuator context)

The sensor closes a loop around a column-driven steering actuator (there is **no rack** on the
kart). Ballpark operating point, for context:

| Quantity | Value |
|---|---|
| Column torque target | ~8 Nm (sized with margin; ~4 Nm minimum to break the tyres loose stopped) |
| Total reduction | ~**11:1** (4.67:1 planetary × 2.38:1 pinion) |
| Steering range | ~±25° at the column (≈50° lock-to-lock) |
| Nominal power | ~**47 W** (8 Nm × ~6 rad/s during a ~0.15 s lock-to-lock) |
| Stall (worst case) | ~**2 kW** (≈47 V × 43 A into the windings — reserve, almost all heat, not an operating point) |

Source: `dv/kart/steering/README.md` (kart canonical operating point). The dv README points at a
`power-budget.md` that does not exist; these numbers are consolidated here for reference.

## History

Everything below describes hardware that is **no longer on the kart**. It is kept so the reasoning
can be re-checked, not followed.

??? info "The AS5600 — the previous sensor, retired 2026-07-12"
    An **AS5600** magnetic encoder read over **I²C**, mounted at the front of the kart near the
    steering shaft to keep the I²C run short. It was in use through the 2025 bench work and into
    2026.

    Retired 2026-07-12 after bench work in which it would not report a valid angle: with the chip
    touching a handheld magnet its magnitude reading peaked erratically and its magnet-detect flag
    stayed mostly at zero, and with that flag clear the chip gates its output regardless of output
    mode. That was not a wiring fault. Whether the same would have happened with the kart's *mounted*
    magnet is the open question in the callout above.

    ![AS5600 breakout board, as bought — with its header strip and a small diametric magnet](images/20250608181732.png)

    **Hand-wired bench setup (June 2025):** AS5600 breakout, an STM32 "Blue Pill", and a USB-serial
    adapter, before any of it moved onto the medulla PCB.

    ![AS5600 and Blue Pill hand-wired on the kart](images/20250608181003.png)
    ![Second view of the same hand-wired bench setup](images/20250608181018.png)

    Basic Blue Pill reading code from that era, kept for reference:
    <https://github.com/rubenayla/bluepill-angle-arduino.git>

??? info "AS5600 wiring colours (obsolete — hand-wired harness only)"
    This colour code belonged to the hand-wired AS5600 setup and was never official. It does not
    describe anything currently on the kart.

    | Colour | Signal |
    |-------|--------|
    | Grey / Black | GND |
    | White | 3.3 V |
    | Green | SDA |
    | Blue | SCL |

    The 2026-03 wiring note listed GND as **black**; the earlier 2025 harness used grey. Both
    existed, which is why this was never trustworthy without checking the actual wire.

??? info "Options considered and not used"
    - **AS5600 in PWM mode.** Attempted so that the front-mounted AS5600 could send a single wire
      to the rear, back when the plan still had the medulla moving there.
      It never produced a usable signal on the bench: the output pin read as floating, which
      traced to an open connection somewhere in the path from the chip's OUT pad through the
      terminal and its series resistors to the ESP32 — not to a proven dead chip. It also needs a
      one-time, irreversible OTP burn to enable, which made it a poor thing to gamble on.
    - **MPS MagAlpha MA732.** The sensor-research pick, and in the same in-plane direction-sensing
      class as the MT6701, with better off-axis tolerance. Not bought: it is a bare QFN chip
      needing a breakout, pricier and slower to source, and the ~€10 MT6701 module solves the same
      magnet problem and was already in hand. Worth revisiting only if the MT6701's mounting ever
      fights the kart's sideways-magnet geometry.

    Detailed comparison of the two sensing principles, with the datasheet citations behind them, is
    in `kart-medulla/history.md` (2026-07-11 and 2026-07-12).
