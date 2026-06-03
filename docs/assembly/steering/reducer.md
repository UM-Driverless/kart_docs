# Steering Reducer

The salvage motor spins fast and weak; the steering column needs the opposite — slow and strong. The reducer trades the motor's cheap speed for torque. See [Sizing the actuator](index.md#sizing-the-actuator) for why (torque is heat-limited, speed is basically free) and the numbers (~8 Nm at the column, ~47 W, ~11:1 reduction).

## Why a planetary

We needed ~11:1 in a small, **coaxial** package, cheap enough to reprint when it breaks, and **backdrivable** (so the wheels still turn by hand if the electronics die). A planetary packs the whole reduction into one ring of gears around the shaft — coaxial and compact, load shared across the planets, and it stays backdrivable.

The other reducer types either don't backdrive (worm, ball-screw), can't be printed with any strength (harmonic flexspline), or sprawl across two axes (plain gear train). Full comparison and the two alternatives we're keeping live: **[Alternative reducer designs](alternatives/index.md)**.

The price of the planetary is that it's the **least forgiving of print error** — every planet has to mesh the sun *and* the ring simultaneously, so all the tolerances have to agree at once. That's the source of most of the failures below.

## Current design (~11:1, two stages)

| Stage | Type | Teeth | Module | Ratio |
|---|---|---|---|---|
| 1 — planetary | sun → 4 planets → fixed ring | sun 12, planet 16, ring 44 | 2 | 4.67 : 1 |
| 2 — output pair | pinion → big gear (to column) | pinion 13, gear 31 | 3 | 2.38 : 1 |
| **Total** | | | | **≈ 11.1 : 1** |

The planetary was 5.4:1 with a 10-tooth sun; it dropped to 4.67:1 when the sun/planets moved to the **Norelem hub geometry** (12-tooth sun, off-the-shelf steel option). Full Fusion parameters live in the team's `kart/steering/` files (`planetary_reducer_parameters.md`, `output_pinion_parameters.md`).

## Gear materials — the real problem

Choosing a gear material isn't picking "the best" one; it's deciding **what to optimise** — every property trades against another:

> low friction ↔ creep resistance ↔ rigidity ↔ wear ↔ toughness (not brittle) ↔ printability ↔ cost

| Material | Why considered | Why it fell short |
|---|---|---|
| **PLA** | stiff, trivial to print | brittle → poor fatigue; teeth snap, gears split. Broke after 5 laps. Fine only for the big, low-stress gears. |
| **ABS** | tougher than PLA, more heat | not slippery, still creeps — wears, no better at the D-flat. |
| **Nylon (PA)** | low friction, tough — the classic gear plastic | **creeps** under sustained load → the D-flat on the motor shaft rounds off and slips. Absorbs moisture. |
| **PPA** | aromatic-ring nylon: stiffer, far less creep, low moisture | the step up; harder + dimensionally stable, better wear under load. |
| **PPA-CF** | carbon adds stiffness | CF is abrasive (wears the steel it grips) and embrittles → can *worsen* the cracking it's meant to fix. Test before committing. |
| **Brass / steel** | the endgame for the part that matters | machined / off-the-shelf (Norelem hub sun); no plastic wins at the motor interface. |

### The root cause: the D-flat, not the gears

The real weak point is the **motor-shaft interface** — a D-flat + set screw in a creeping plastic. Fix the material *there* (brass / Norelem steel sun) and the root failure goes away regardless of what the rest is printed in. This is also why a [cycloidal drive](alternatives/cycloidal.md) wouldn't dodge it — its eccentric input mounts on the same D-flat.

### Failure modes seen

- **PLA** — brittle fracture: snapped teeth, gears split, within minutes of load.
- **Nylon** — D-flat creep (the flat rounds off → slip); teeth round off under sustained load.
- **Holder / carrier deformation** — the mount flexing under load lets the gears separate and skip; a failure path independent of the gears themselves.

!!! note "Status: still iterating"
    Six print generations in, it works — kind of. Current path: a Norelem steel hub sun for the D-flat, PPA(-CF) for the printed gears, and watching the carrier stiffness. Not solved.

## CAD

The CAD lives in shared cloud storage (kept out of this repo to keep it light). The folder holds the **Fusion F3D** — the parametric source: open it in Fusion to edit teeth counts, module, and sketches with the full timeline intact — plus a **STEP** (universal geometry, any CAD, non-parametric) and per-gear **STLs** for printing.

!!! todo "CAD download link pending"
    Public share link to the steering-reducer CAD folder to be added here. Files: `planetary-reducer.f3d` (parametric), `planetary-reducer-assembly.step` (geometry), `planetary-{sun,planet,ring}-gear.stl` (print). Still to export: output-pinion pair (13 / 31), carrier, lid, separator.
