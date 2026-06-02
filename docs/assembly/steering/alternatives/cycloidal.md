# Cycloidal Drive (alternative)

!!! warning "Status: in progress / shelved"
    A live alternative, not built. Shelved for now because (1) its eccentric input mounts on the **same motor-shaft D-flat** that is our actual failure point, so it doesn't dodge the root cause, and (2) it needs a lot of extra pins + bearings. Kept on the table for its torque/shock advantage. **TODO:** prototype + measure.

## Why it's interesting

Of all the options it holds the **most output torque** and tolerates **shock** best — a large fraction of the lobes press the ring pins at once, so a reversal spreads across many contacts instead of hammering one tooth. That is exactly the load that keeps shearing the planetary. It is also coaxial, low-backlash, and routinely 3D-printed.

## Ratio

Single stage, ring fixed: **reduction = number of lobes** (with ring pins = lobes + 1). So **11 lobes / 12 ring pins → 11:1 in one compact stage** — our whole target in one stage vs the planetary's two.

## Components (printable build)

- **Eccentric** on the input shaft (a bearing on an off-centre hub) — makes the disc orbit. Use **two discs 180° apart** to balance it (one disc alone is an unbalanced spinning mass and shakes).
- **Cycloidal disc(s)** — printed: lobed edge + holes for the output pins + central bore for the eccentric bearing.
- **Ring pins** (outer) — fixed in the housing; count = lobes + 1. Steel dowels or bolts, ideally with a roller bearing over each.
- **Output pins** (inner) — on the output plate, through oversized holes in the disc (oversize = 2 × eccentricity); they pick off the slow rotation and ignore the orbit. ~6–8, with rollers.
- **Bearings**: one eccentric bearing per disc, a roller per ring/output pin (~18–20 small bearings), plus 2 main bearings for input and output.
- **Output flange + shaft** to the column; **housing** holds the ring pins.

## The catch

The eccentric still mounts on the motor-shaft **D-flat** (same creep risk as the planetary's sun), and it is a lot of parts to keep concentric. **TODO:** decide whether the torque/shock gain is worth the component count once the planetary's material path (PPA / steel sun) is exhausted.

## CAD

!!! todo "Not modelled yet"
    No CAD. If prototyped: model in Fusion, add a public-link embed + STEP, and a lobe-profile generator note (module, eccentricity, lobe count).
