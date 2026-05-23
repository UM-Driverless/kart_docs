# EBS — Design History (superseded)

> The current, physically-validated circuit is on the [**Emergency Braking page**](index.md): VPPM and EBS in parallel, merged by an **OR / shuttle valve**, with **no isolation valve in series with the proportional valve**.

This page keeps the two earlier candidate circuits for reference. Both were considered before the May 2026 bench test settled the design.

## Candidate 1 — Super-simplified (no OR valve, no ASB valve)

VPPM and EBS in parallel, wired straight to the actuator. With no OR valve to separate the branches, the EBS solenoid's exhaust port was blanked with a plug ([B-1/4, 3569](https://www.festo.com/es/es/a/3569/)) instead of a silencer, so the VPPM's regulated air couldn't escape through the open EBS exhaust. The EBS became on/off emergency air only; the VPPM handled all regulation and exhaust.

<object data="images/ebs-simplified.svg" type="image/svg+xml" style="width:100%;max-width:870px;"></object>

**Why it was dropped:** the blanked EBS exhaust is a workaround — it forces all venting through the VPPM and gives the EBS no fast dump path. The OR valve does the branch isolation cleanly and lets the EBS exhaust through a silencer.

## Candidate 2 — Full / conservative (ASB valve + OR valve) — *Diego's design*

The maximum-redundancy version. It added an **ASB isolation solenoid in series** ahead of the VPPM ([8035167](https://www.festo.com/es/es/a/8035167/)) to physically cut the proportional valve's supply during an emergency, on top of the OR / shuttle valve.

<object data="images/ebs-full.svg" type="image/svg+xml" style="width:100%;max-width:920px;"></object>

**Why it was dropped:** the series ASB valve is redundant. Bench testing confirmed the VPPM **blocks all of its ports when unpowered** (it does *not* vent), and the OR valve already isolates the VPPM branch during an emergency — so emergency air cannot escape through the proportional valve with or without the series valve. Removing it saves a valve, a coil, a connector and one leak path. See [Why no isolation valve in series with the proportional valve](index.md#why-no-isolation-valve-in-series-with-the-proportional-valve).

## Design Logic (common to all variants)

1.  **EBS (fail-safe):** the actuator is air-to-apply — pressure extends the cylinder onto the brake, the return spring releases it when vented. The normally-open EBS electrovalve delivers full stored pressure to the actuator on power loss, so the kart brakes hard whenever the shutdown circuit opens.
2.  **ASB (proportional):** controlled by the VPPM valve, which regulates pressure to modulate braking force during dynamic driving.
3.  **Integration (validated):** an OR / shuttle valve merges both lines so the active branch can't lose its air through the other branch's open exhaust.

## Components (archive)

- [x] **Pneumatic actuator** — ADN-S-50-45-I-P-A (8084714) — reuse
- [x] **EBS electrovalve** — Festo VUVS-LT25-M32U-MD-G14-F8 (8035174) — reuse
- [x] **Proportional valve (VPPM)** — VPPM-8L-L-1-G14-0L10H-V1P-S1C1 (571293)
- [x] **Shuttle valve (OR)** — OS-1/4-B (6682) — *kept in the validated design*
- [ ] **ASB electrovalve** — Festo VUVS-LT25-M32C-MD-G14-F8 (8035167) — **removed from the validated design** (owned, kept as a spare)

[Return to the validated design](index.md)
