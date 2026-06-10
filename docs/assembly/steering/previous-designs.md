# Previous Steering Designs

The current steering — a salvaged DC motor turning the column through a 3D-printed planetary — is not where this started. Two earlier directions were built and abandoned. This page records them and **why** they were dropped, so the reasoning isn't lost and nobody re-walks a dead end.

## The Maxon EPOS linear actuator (2023–2024)

The first autonomous-steering design didn't turn the column at all — it **pushed the steering linkage with a linear actuator**, the way a lot of Formula Student driverless cars do.

The hardware was a sponsored Maxon stack:

| Part | Spec |
|---|---|
| Motor | **Maxon EC-i 30** brushless — 12 V, 30 W, ~9200 rpm |
| Encoder | **Maxon ENC 16 EASY** |
| Gearhead | **GP32** spindle drive with ball screw — 4.8:1, 200 mm spindle, 517 N continuous / 1369 N peak feed force, ~56 mm/s |
| Controller | **EPOS4** positioning controller, driven over **CANopen** |
| Angle feedback | **Vert-X 31E** contactless hall sensor |

<!-- TODO image: 2024 steering assembly with the Maxon actuator + EPOS mount → images/maxon-linear-actuator.png -->

**Why it was dropped:**

- **Cost.** The Maxon stack was a sponsored quote, but it's a whole-kart's-budget part — not reproducible or repairable on our own money. A failure mid-season had no cheap path back.
- **Commissioning pain.** Bringing up the EPOS4 over CANopen fought us the whole way — position-sensor index errors (`0x7382`), hall-angle detection errors (`0x738a`), sensor-resolution errors (`0x7381`). The control chain was a black box we didn't own.
- **It tied steering to one supplier's ecosystem** (EPOS Studio, CANopen object dictionary, Maxon-specific firmware) instead of plain PWM we could debug ourselves.

So the team pivoted to something we could build, break, and reprint for a few euros: a motor on the column.

## The first rotary reducer (3-planet nylon, ≈16:1)

The first column-drive reducer was also a printed planetary, but with the older geometry:

| Stage | Then | Now |
|---|---|---|
| Planetary | sun 10t / planet 17t / ring 44t, **3 planets**, **5.4:1** | sun 12 / planet 16 / ring 44, **4 planets**, **4.67:1** |
| Output pair | **3:1** | 13t / 31t, m3, **2.38:1** |
| Total | **≈ 16:1** | **≈ 11.1:1** |

<!-- TODO image: the grey 3-planet printed set (superseded geometry) → images/planetary-3planet-old.png -->

**What changed and why:**

- **3 → 4 planets.** With a 12-tooth sun and a 44-tooth ring, the assembly condition `(Z_sun + Z_ring)/N` only divides evenly for 4 planets, not 3 — so the move to an off-the-shelf 12-tooth sun *forced* 4 planets. The upside: load is shared across four meshes instead of three.
- **Ratio rebalanced** from ≈16:1 to ≈11.1:1 when the sun moved to the off-the-shelf Norelem hub geometry. The column still gets the ~8 Nm it needs (see [sizing](index.md#sizing-the-actuator)); the planetary dropped from 5.4:1 to 4.67:1 as a side effect of buying the sun rather than printing it.

## The gear-material saga

The reducer went through several materials before the failure mode was actually understood — it's the **motor-shaft D-flat**, not the gear teeth. Full version on the [reducer page](reducer.md#gear-materials-the-real-problem); the short history:

| Material | What happened |
|---|---|
| **PLA** | brittle — teeth snapped, gears split within minutes of load. Broke after ~5 laps. |
| **ABS** | tougher than PLA, takes more heat — the **current printed material** for planets and carrier. |
| **Nylon (PA)** | low friction and tough, but **creeps**: the motor-shaft D-flat rounds off and slips. Absorbs moisture too. |
| **Steel sun (Norelem)** | the endgame for the one part that matters — the off-the-shelf steel hub sun fixes the D-flat regardless of what the rest is printed in. |

## CAD lineage

The design has churned through many versions in Fusion 360 — the planetary alone went past **v50**, and the full `kart_assembly` past **v110**. The gears themselves are generated with the **GF Gear Generator** plugin (see [reducer](reducer.md#gear-generation)).

<!-- TODO image: Fusion design-tree / version history shot (e.g. planetary v53, kart_assembly v114) → images/cad-version-history.png -->

