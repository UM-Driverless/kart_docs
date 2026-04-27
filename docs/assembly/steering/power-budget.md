# Steering Power Budget

Back-of-envelope sizing for the steering actuator. Used to decide whether a salvaged motor + 3D-printed planetary is enough, or whether a purpose-bought gearmotor is justified.

## Required torque at the steering shaft

The dominant load is **standstill steering** — pivoting the front tyres while the kart isn't rolling. At speed the required torque drops 3–5×.

For a kart with rubber on dry tarmac:

$$T_{\text{kingpin, per wheel}} \approx \mu \cdot N \cdot a$$

| Parameter | Value | Source |
|---|---|---|
| $\mu$ — static friction coefficient | 0.8 | Warm slick on dry asphalt |
| $N$ — load per front wheel | ~294 N | Kart + robot ≈ 150 kg, ~40 % on front axle = ~60 kg total front, ~30 kg per wheel |
| $a$ — effective scrub arm | ~0.03 m | Half the contact-patch length (~60 mm patch on a kart slick) |

Per wheel: $T \approx 0.8 \cdot 294 \cdot 0.03 \approx 7$ Nm. Both wheels together at the kingpins: **~14 Nm**.

Kart steering is roughly 1 : 1 (no rack-and-pinion reduction; the steering arm and tie rod just transmit), so the **steering shaft sees ~15–20 Nm at standstill** — consistent with published FSAE / kart numbers (15–30 Nm depending on tyre, weight, patch).

Above ~5 km/h this drops to **3–8 Nm** because the patch slips dynamically rather than pivoting from rest.

## Required angular speed

Target: lock-to-lock in **0.3 s** (aggressive, suitable for autonomous emergency cone-dodge from a stop). Lock-to-lock ≈ 180° = π rad.

$$\omega = \frac{\pi}{0.3} \approx 10.5 \text{ rad/s} \approx 100 \text{ rpm}$$

For comparison: 0.5 s lock-to-lock = 60 rpm; 1.0 s = 30 rpm. Most autonomous systems are happy with 0.5 s.

## Power

The two extremes don't happen at the same instant — at peak torque you're stationary; at peak speed the torque is low. Treat them as separate budgets:

| Operating point | Torque | ω | Mechanical P | Electrical P (η ≈ 0.4) |
|---|---:|---:|---:|---:|
| Continuous corrections (rolling) | ~5 Nm | ~6 rad/s | ~30 W | ~70 W |
| Peak slew (mid-stroke) | ~8 Nm | ~10.5 rad/s | ~85 W | ~210 W |
| Stationary lock-to-lock (worst case) | ~20 Nm | ~10.5 rad/s | ~210 W | ~520 W |

The reduction-stage efficiency η ≈ 0.4 assumes worm gearing inside the motor (~60 %) plus the 3D-printed planetary (~70 %).

**Design target:**
- Stall torque at the steering shaft: **≥ 25 Nm** (60 % margin over the 20 Nm static estimate).
- Free-running speed at the steering shaft: **≥ 100 rpm**.
- Continuous mechanical power: ~50 W.
- Peak mechanical power (worst case): ~200 W.
- 12 V supply current: 17 A continuous / ~40 A peak. The Cytron MD25HV (25 A continuous, 60 A peak, 7–58 V) on the BOM is a clean match.

!!! info "Available headroom — ~2 kW stall capacity"
    The figures above describe normal operation. At full stall the salvaged motor with the 15 : 1 planetary can pull about 2 kW, which is roughly four times the worst case in the operating envelope. In normal autonomous driving the system sits comfortably within the 50–200 W band; the stall figure is reserve for unusual situations like cold tyres, full lock from a dead stop, or mechanical bind in the linkage. We don't expect to hit it.

    The 15 : 1 reduction is what lets the salvage motor cover that range without overheating its windings. The off-the-shelf wiper motors below don't have the same margin unless paired with a similar reduction stage.

## Why a Bosch wiper motor is interesting

A wiper motor is a permanent-magnet DC motor with a **worm gearbox built into the same casting**. That gives motor + reduction + IP rating + automotive duty cycle in one part. Worm gearing is non-backdrivable, so the steering holds position with the power off — useful for failsafe.

Typical generic-Bosch front-wiper motor (e.g. F006-B20-063, F006-B20-047): ~25 Nm peak, ~33/51 rpm two-speed, ~80 W mech. **Just barely enough** for our spec; runs at 12 V. Salvage cost €5–15, new ~€50–80.

Worm-gear caveats:
- Non-backdrivable — fine for autonomous, but a manual-override fallback can't assume the motor freewheels when off.
- Output stub is designed for the wiper arm, not for a 10 mm coupling — needs an adapter.
- Two-speed wiper motors have three brushes; the third gives a higher-RPM tap.

## Current setup (kept)

The steering actuator is a 24 V geared DC motor pulled out of a discarded massage chair, run at 12 V, driving the steering shaft through a 3D-printed planetary at 15 : 1. Position feedback comes from an AS5600 magnetic encoder mounted on the shaft. At full stall the motor has roughly 2 kW available, which we're unlikely to ever use; normal driving sits in the 50–200 W band. The motor was free, the planetary is a few euros of filament plus four 608 bearings and some M3 hardware, and nothing here had to be ordered.

The candidates below are worth knowing about but don't replace this setup.

## Interesting alternatives (not currently planned)

These are off-the-shelf parts worth keeping in mind if the salvage motor fails or the team gets a procurement window. None of them match the current setup's torque on their own, so a swap would still need the planetary or something like it.

| Part | V | Output speed | Torque | Power | Feedback | Indicative price | Comment |
|---|---:|---:|---:|---:|---|---:|---|
| **Bosch F006-B20-0xx** generic wiper | 12 | 33 / 51 rpm | ~23 Nm peak | ~80 W | none | ~€50–80 new, €5–15 salvage | Cheap; well below the measured 2 kW load even with reduction. Reference point only. |
| **Bosch WDD2** (0390249101) Wiper Direct Drive | 12 / 24 | up to ~63 cpm (≈ 80 rpm) | 12 Nm cont, 34 Nm stall | 50 W cont (8.3 A) | LIN/CAN bus, programmable angle/speed/torque | ~£972 / ~€1 140 ex VAT | Industrial closed-loop wiper actuator — programmable angle, speed, torque over CAN. Costs more than the rest of the kart and is still under-powered for the measured peak load. Skip. |
| **Doga 319H** (e.g. 319.4846.30.00) wiper motor *with feedback* | 12 / 24 | 30 / 45 / **100 rpm** variants | 4–9 Nm nominal, **>60 Nm starting** | 70–170 W | Hall, up to 972 ppr | ~€150–250 (RS / OEM Automatic) | The most engineering-elegant option — IP65 + integrated 972 ppr Hall feedback in one part. But peak power is ~10× below what we measure on the kart, so we'd still need a reduction stage. Only worth procuring if a clean integrated feedback path matters more than torque headroom. |
| **Doga 319.4860.30.00** | 24 | 30 rpm | 50 Nm | ~150 W | none | ~€200 (RS) | High torque, low speed. Too slow for the 0.3–0.5 s slew target (~1.7 s lock-to-lock). |
| Generic 24 V planetary gearmotor (GEMS / ISL / AliExpress) | 24 | 100 rpm typical | 20–30 Nm | 100–200 W | optional encoder | ~€80–150 | Spur-gear planetary is *backdrivable* — different failsafe behaviour from a worm. Still needs an external reduction to match the current setup. |

None of these replace the current setup for three practical reasons. The salvage motor with 15 : 1 reduction has stall headroom none of the off-the-shelf options reach without their own reduction stage. Buying anything is slow for the team in a way that filament and a salvage bin are not. And the current parts cost essentially nothing, so swapping them only makes sense once something breaks or a real performance gap shows up.

If procurement ever opens up, the Doga 319H at 100 rpm is the most interesting of the bunch — its 972 ppr Hall feedback would let us drop the AS5600 and one I²C bus from the Kart Medulla. Useful to know, not a planned change.

Sources for the candidate motors:

- [Bosch WDD2 Wiper Direct Drive — official product page](https://www.bosch-motorsport.com/products/actuators/wiper-direct-drive/wiper-direct-drive-wdd2/)
- [Bosch WDD2 retail listing — Swindon Powertrain](https://webshop.swindonpowertrain.com/index.php?route=product/product&product_id=62)
- [Doga 319H DC wiper motor with feedback — OEM Automatic](https://www.oem.co.uk/products/motors/dc-motors/dc-motor-with-right-angle-gearbox-_-C31193/doga-319h---dc-wiper-motor-with-feedback-_-P1965277)
- [Doga 319.4860.30.00 (50 Nm / 30 rpm) — RS Components](https://int.rsdelivers.com/product/doga/31948603000/doga-brushed-geared-dc-geared-motor-24-v-dc-50-nm/7736800)
- [Generic 24 V planetary gearmotors — GEMS Motor catalogue](https://gemsmotor.com/12v-24v-dc-gear-motor)
