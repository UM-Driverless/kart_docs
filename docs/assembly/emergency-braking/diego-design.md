# EBS - Original Conservative Design (Diego's Design)

This was the initial hybrid pneumatic circuit design. It integrated both the Emergency Braking System (EBS) and the Autonomous Service Brake (ASB) with maximum redundancy.

It included an explicit **ASB Electrovalve (V2)** in series before the proportional valve, to physically cut its air supply during an emergency. Later analysis — confirmed by physical testing in May 2026 — showed the VPPM **blocks all of its ports when unpowered** (it does *not* vent), so emergency air cannot escape through it. Combined with the OR valve isolating the branch, that makes the series valve redundant, and it was removed. See the [validated design](index.md) for the full reasoning.

## Schematic
![](Diego's_diagram)

## Design Logic
1.  **EBS (Fail-Safe):** The actuator is air-to-apply — pressure extends the cylinder onto the brake, the return spring releases it when vented. The normally-open EBS electrovalve delivers full stored pressure to the actuator on power loss, so the kart brakes hard whenever the shutdown circuit opens.
2.  **ASB (Proportional):** Controlled by the VPPM valve. It regulates pressure to modulate braking force during dynamic driving.
3.  **Integration:** An OR Valve (Shuttle) merges both lines so the active branch can't lose its air through the other branch's open exhaust.

## Components (Archive)

### Actuators & Valves
- [x] **Pneumatic Actuator** (ADN-S-50-45-I-P-A) - Reuse
- [x] **EBS Electrovalve V1** (Reuse)
    - Festo VUVS-LT25-M32U-MD-G14-F8 (8035174).
- [ ] **ASB Electrovalve V2** (New - **REMOVED IN FINAL DESIGN**)
    - Festo VUVS-LT25-M32C-MD-G14-F8 (8035167).
- [ ] **Proportional Valve** (VPPM-8L-L-1-G14-0L10H-V1P-S1C1, 571293)
- [ ] **Shuttle Valve (OR)** (OS-1/4-B)

[Return to Current Design](index.md)
