# EBS - Original Conservative Design (Diego's Design)

This was the initial hybrid pneumatic circuit design. It integrated both the Emergency Braking System (EBS) and the Autonomous Service Brake (ASB) with maximum redundancy.

It included an explicit **ASB Electrovalve (V2)** to physically cut the air supply to the proportional valve during an emergency, ensuring isolation. Later analysis showed the VPPM Proportional Valve itself vents to atmosphere when unpowered, making this extra valve redundant (but safer in theory against a stuck-open VPPM).

## Schematic
![](Diego's_diagram)

## Design Logic
1.  **EBS (Fail-Safe):** The cylinder is normally extended (braking) by spring/external force. Air pressure retracts it (release). The EBS Electrovalve cuts pressure and exhausts air to atmosphere to trigger emergency braking.
2.  **ASB (Proportional):** Controlled by the VPPM valve. It regulates pressure to modulate braking force during dynamic driving.
3.  **Integration:** An OR Valve (Shuttle) isolates both lines so they don't interfere with each other.

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
