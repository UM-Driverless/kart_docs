# Alternative Reducer Designs

The [planetary](../reducer.md) is what we run. These are the other reducer types we weighed, and the two we're keeping as **live alternatives** to print and test.

## Why the others lost (for this application)

Requirements: ~11:1, small + coaxial, cheap to reprint, **backdrivable** (manual fallback if the electronics die).

| Type | Verdict | Reason |
|---|---|---|
| **Planetary** ✅ | **in use** | coaxial, compact, load shared across planets, backdrivable. Least forgiving of print error. → [reducer](../reducer.md) |
| **Folded compound gear train** | live alternative | each mesh is one *adjustable* pair → far more print-forgiving than the planetary. But two axes (wider) and stacked backlash. → [folded compound train](folded-compound-gear-train.md) |
| **Cycloidal** | live alternative (shelved) | highest torque + shock tolerance, and printable. But the eccentric mounts on the same D-flat, and it's a pile of pins + bearings. → [cycloidal](cycloidal.md) |
| **Worm** | rejected | self-locking → not backdrivable; the wheels lock if power dies. |
| **Harmonic (strain wave)** | rejected | needs a spring-steel flexspline you can't print with any strength; overkill ratio. |
| **Belt** | rejected | needs a tensioner; low ratio per stage; creeps under a held load. |

## Torque-capacity ranking

How much output torque a design can hold comes down to **how many contacts share the load** — it fails at its single most-stressed contact:

> **cycloidal > planetary > spur / folded train > belt**

A cycloidal spreads load across many lobe + pin contacts at once; a planetary splits it across its planets; a spur/folded train runs the full torque through a single tooth pair per mesh. A printed **harmonic** would invert to *last* — its thin flexspline can't carry torque in plastic.

So note the tension: the **folded train** (most print-forgiving) is the **weakest** on torque, and the **cycloidal** (shelved) is the **strongest**. The planetary in use sits in the middle.
