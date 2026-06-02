# Steering Motor

The actuator sizing — torque, speed, and the power that follows — lives on the [steering page](index.md). Short version: the column needs ~8 Nm to turn the stopped wheels and ~56 rpm to sweep lock-to-lock in ~0.15 s, so about 47 W of mechanical work. With a ~48 V pack and the Cytron driver, electrical power is never the limit; the only real design lever is getting enough torque at the column, which the 11:1 reduction provides.

This page records the motor in use and the off-the-shelf alternatives the team looked at.

## Current setup (kept)

The steering actuator is a 24 V geared DC motor pulled out of a discarded massage chair, driven from the battery through the Cytron H-bridge, turning the steering column through a 3D-printed planetary at 11:1. Position feedback comes from an AS5600 magnetic encoder on the column. It turns the stopped wheels with ~8 Nm and sweeps lock-to-lock in ~0.15 s; at stall it has roughly 2 kW available, far more than the ~47 W the job actually needs. The motor was free, the planetary is a few euros of filament plus four 608 bearings and some M3 hardware, and nothing here had to be ordered.

The candidates below are worth knowing about but don't replace this setup.

## Why a Bosch wiper motor is interesting

A wiper motor is a permanent-magnet DC motor with a **worm gearbox built into the same casting**: motor + reduction + IP rating + automotive duty cycle in one part. Worm gearing is non-backdrivable, so the steering holds position with the power off — useful for failsafe.

Caveats:

- Non-backdrivable — fine for autonomous, but a manual-override fallback can't assume the motor freewheels when off.
- The output stub is built for the wiper arm, not a 10 mm coupling — needs an adapter.
- Two-speed wiper motors have three brushes; the third gives a higher-rpm tap.

## Interesting alternatives (not currently planned)

Off-the-shelf parts worth remembering if the salvage motor fails or a procurement window opens. The bar to clear is ~8 Nm at the column (more for cold-tyre / full-lock hard cases) at ~56 rpm. Most of these still need a reduction stage to get there.

| Part | V | Output speed | Torque | Power | Feedback | Indicative price | Comment |
|---|---:|---:|---:|---:|---|---:|---|
| **Bosch F006-B20-0xx** generic wiper | 12 | 33 / 51 rpm | ~23 Nm peak | ~80 W | none | ~€50–80 new, €5–15 salvage | Built-in worm clears the torque bar with margin; 51 rpm is just under the ~56 rpm target. Cheap reference point. |
| **Bosch WDD2** (0390249101) Wiper Direct Drive | 12 / 24 | up to ~63 cpm (≈ 80 rpm) | 12 Nm cont, 34 Nm stall | 50 W cont (8.3 A) | LIN/CAN bus, programmable angle/speed/torque | ~£972 / ~€1 140 ex VAT | Programmable angle/speed/torque over CAN, but costs more than the rest of the kart. Skip. |
| **Doga 319H** (e.g. 319.4846.30.00) wiper motor *with feedback* | 12 / 24 | 30 / 45 / **100 rpm** variants | 4–9 Nm nominal, **>60 Nm starting** | 70–170 W | Hall, up to 972 ppr | ~€150–250 (RS / OEM Automatic) | Most elegant — IP65 + 972 ppr Hall feedback in one part. The 100 rpm variant clears the speed target; nominal torque is marginal, so it may still want a light reduction. Worth it only if integrated feedback matters more than headroom. |
| **Doga 319.4860.30.00** | 24 | 30 rpm | 50 Nm | ~150 W | none | ~€200 (RS) | Plenty of torque, but 30 rpm is too slow for the ~56 rpm target. Skip. |
| Generic 24 V planetary gearmotor (GEMS / ISL / AliExpress) | 24 | 100 rpm typical | 20–30 Nm | 100–200 W | optional encoder | ~€80–150 | Backdrivable (different failsafe behaviour from a worm); still needs external reduction to match the current setup. |

If procurement ever opens up, the Doga 319H at 100 rpm is the most interesting — its 972 ppr Hall feedback would let us drop the AS5600 and one I²C bus from the Kart Medulla. Useful to know, not a planned change.

Sources for the candidate motors:

- [Bosch WDD2 Wiper Direct Drive — official product page](https://www.bosch-motorsport.com/products/actuators/wiper-direct-drive/wiper-direct-drive-wdd2/)
- [Bosch WDD2 retail listing — Swindon Powertrain](https://webshop.swindonpowertrain.com/index.php?route=product/product&product_id=62)
- [Doga 319H DC wiper motor with feedback — OEM Automatic](https://www.oem.co.uk/products/motors/dc-motors/dc-motor-with-right-angle-gearbox-_-C31193/doga-319h---dc-wiper-motor-with-feedback-_-P1965277)
- [Doga 319.4860.30.00 (50 Nm / 30 rpm) — RS Components](https://int.rsdelivers.com/product/doga/31948603000/doga-brushed-geared-dc-geared-motor-24-v-dc-50-nm/7736800)
- [Generic 24 V planetary gearmotors — GEMS Motor catalogue](https://gemsmotor.com/12v-24v-dc-gear-motor)
