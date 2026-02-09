# Pneumatics
We need an emergency braking system that can be activated on loss of electrical power or error from the shutdown loop, and a proportional braking system that can be controlled by the main computer when the robot is running.

## Final Simplified Design

![](simplified-design.png)

### VPPM unpowered behavior: what does "unregulated" mean?

For our emergency braking system, we need to know exactly what the VPPM proportional valve does when it loses power. The Festo datasheet uses the word **"unregulated"**, which is ambiguous. Here we break down what it actually means, based on multiple pieces of evidence from the official documentation.

**Sources:**

- Festo VPPM catalog documentation 205274 ([local](../../assets/datasheets/205274_documentation.pdf) | [online](https://www.festo.com/media/catalog/205274_documentation.pdf))
- Festo VPPM-8L-L-1-G14-0L10H-V1P-S1C1 datasheet, part 571293 ([local](../../assets/datasheets/VPPM_en.pdf) | [online](https://www.festo.com/us/en/a/571293/))

#### Evidence from the datasheets

| Evidence | Location | Implication |
|---|---|---|
| Valve function: **"3-way proportional-pressure regulator, closed"** | 205274, page 2, "Valve function" table | The valve's default state is "closed" |
| Type code position 006: **"1 = 3/2-way valve, normally closed"** | 205274, page 4, type code table | Confirms the de-energized state is "closed" |
| **"Pressure is maintained if the controller fails"** | 205274, page 2, "Operationally safe" section | Output pressure does NOT vent to exhaust |
| **"Safety position VPPM: if the power supply cable is interrupted, output pressure is maintained unregulated."** | 571293 datasheet, page 1, "Safety instructions" row | No active regulation, but pressure is _maintained_ |
| Design: **"Piloted diaphragm regulator"** | Both datasheets | Piloted = a small solenoid controls a larger diaphragm |
| Type of reset: **"Mechanical spring"** | Both datasheets | Spring returns the diaphragm to its rest (closed) position |

#### Interpretation

The VPPM is a **piloted diaphragm regulator** with a **mechanical spring return**. When powered, the electronic controller actively modulates the pilot solenoid to regulate output pressure by opening/closing the supply (1→2) and exhaust (2→3) paths. When power is lost:

1. The pilot solenoid de-energizes
2. The mechanical spring returns the diaphragm to its rest position
3. **All three ports are isolated from each other** (normally closed)

The word **"maintained"** is the critical clue:

- If port 2→3 (exhaust) were open, pressure would vent and _not_ be maintained
- If port 1→2 (supply) were open, pressure would _rise_ to supply pressure, not just be "maintained"
- "Maintained" means: pressure stays at whatever value it was at the moment of power loss

So **"unregulated"** means: the pressure at port 2 is no longer actively controlled, but it is trapped there. It will only decay slowly through natural seal leakage over time.

#### Consequence for our circuit

Since all ports are blocked when unpowered, we are in the **second-best scenario** for emergency braking. We need **one additional valve in parallel** (the EBS electrovalve) to bypass the VPPM and deliver full supply pressure to the brake actuator when power is lost.

![Original simplified circuit sketch](2025-07-11-13-57-41.png)

### Alternative scenarios and required valves

Depending on the valve's unpowered behavior, different circuit designs would be required. This section documents all cases for reference.

#### Best case: Port 1→2 connected when unpowered

If the valve passed supply pressure straight through to the output when de-energized, full supply pressure would reach the brake actuator automatically on power loss. **No additional valves would be needed** — the VPPM itself would provide emergency braking.

#### Our case: All ports blocked when unpowered

This is the VPPM's actual behavior. Port 2 holds its last pressure but receives no supply and doesn't vent. We need:

- **One valve in parallel** (normally-open solenoid valve, e.g., the EBS electrovalve): bypasses the VPPM to deliver full supply pressure for emergency braking when power is lost.

That's it — no other valves are needed because neither the supply nor the exhaust path leaks through the VPPM.

#### If output leaked to exhaust (port 2→3 leak)

If air leaked from the output to the exhaust port when unpowered, the emergency braking line would slowly lose pressure through the VPPM's port 3. We would need:

- **One valve in parallel** (normally-open solenoid): same as above, to deliver supply pressure for emergency braking.
- **One shuttle valve / OR valve** (ball type, e.g., Festo OS-1/4-B): placed between the parallel valve's output and the brake actuator. The ball blocks the path back toward port 2 of the VPPM, preventing emergency air from leaking out through the VPPM's exhaust.

#### Worst case: Both supply and exhaust paths leak (ports 1↔2 and 2↔3)

If the VPPM allowed air to flow through both paths when unpowered, emergency braking air could leak in two directions: backward through port 1 to the supply, and forward through port 3 to atmosphere. We would need:

- **One valve in series** (normally-closed solenoid) on the supply line before the VPPM's port 1: prevents emergency air from flowing backward through the VPPM to the supply tank.
- **One shuttle valve / OR valve** (ball type): same as above, prevents air from leaking out through the VPPM's exhaust port 3.
- **One valve in parallel** (normally-open solenoid) routed to the OR valve inlet: delivers supply pressure for emergency braking, merged with the VPPM line via the shuttle valve.

### Bill of Materials

All pneumatic ports standardized to **G1/4** unless noted. Tubing is **6 mm OD / 4 mm ID** throughout. FS 2026 rules: push-in fittings are allowed for ASB/EBS, but we prefer compression (union nut) fittings. Exception: the SDE5 sensor has an integrated QS-6 push-in port.

The BOM follows the pneumatic path from tank output to actuator.

#### Tubing

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 197384 | PUN-H-6X1-BL tubing, 6 mm OD / 4 mm ID, blue (3 m) | [Festo](https://www.festo.com/es/es/a/197384/) |

#### Pressure Sensor 1 (tank side, before regulator)

Monitors tank/supply pressure. Connects directly to tubing via integrated 6 mm push-in fitting.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 567465 | SDE5-D10-NF-Q6E-V-M8 pressure sensor, 0-10 bar, 0-10V analog, M8 connector, QS-6 push-in | [Festo](https://www.festo.com/es/es/a/567465/) |

> TODO: Verify this sensor can handle >10 bar on the tank side without damage. If not, place it after the regulator only.

#### Manual Valve (brake release / isolation)

Manual ball valve for brake release during maintenance and system isolation. Reuse existing on-hand valve.

| Status | Part No. | Description | Notes |
|---|---|---|---|
| Reuse | — | Manual ball valve, G1/4 | On-hand from previous seasons |

#### Low-Pressure Regulator

Adjustable regulator to set maximum system working pressure downstream of the tank.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 527690 | MS4-LR-1/4-D6-AD10 pressure regulator, G1/4, 0.5-10 bar | [Festo](https://www.festo.com/es/es/a/527690/) |

#### Pressure Sensor 2 (regulated side, before valves)

Monitors regulated pressure entering the valve stage. Same model as sensor 1.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 567465 | SDE5-D10-NF-Q6E-V-M8 (second unit) | [Festo](https://www.festo.com/es/es/a/567465/) |

#### EBS Electrovalve (emergency braking, in parallel with VPPM)

Normally-open solenoid valve. When powered (driving): closed. When unpowered (emergency): opens and delivers full supply pressure to the actuator.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 8035174 | VUVS-LT25-M32U-MD-G14-F8, 3/2-way, Normally Open, G1/4 | [Festo](https://www.festo.com/es/es/a/8035174/) |

#### VPPM Proportional Valve (ASB, in parallel with EBS)

Proportionally controls brake pressure during autonomous driving. All ports blocked when unpowered (see [analysis above](#vppm-unpowered-behavior-what-does-unregulated-mean)).

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 571293 | VPPM-8L-L-1-G14-0L10H-V1P-S1C1, 0-10 bar, 0-10V setpoint, G1/4 | [Festo](https://www.festo.com/es/es/a/571293/) |
| | | [VPPM catalog documentation (local)](../../assets/datasheets/205274_documentation.pdf) | [online](https://www.festo.com/media/catalog/205274_documentation.pdf) |
| | | [Part-specific datasheet (local)](../../assets/datasheets/VPPM_en.pdf) | [online](https://www.festo.com/us/en/a/571293/) |

#### Pneumatic Actuator

Spring-return cylinder. **G1/8 ports** — requires G1/4 → G1/8 adapter.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 8084714 | ADN-S-50-45-I-P-A, bore 50 mm, stroke 45 mm, G1/8, 0.4-10 bar | [Festo](https://www.festo.com/gb/en/a/8084714/) |

#### Compression Fittings

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 2029 | ~10 | CK-1/4-PK-4 straight, G1/4 → tube 6 mm (all valve ports and general connections) | [Festo](https://www.festo.com/es/es/a/2029/) |
| Buy | 4487 | 2 | TCK-1/4-PK-4 T-fitting, G1/4 → tube 6 mm (split to parallel valves + merge outputs) | [Festo](https://www.festo.com/es/es/a/4487/) |
| Buy | 4469 | 1 | LCK-1/8-PK-4 elbow, G1/8 → tube 6 mm (actuator connection) | [Festo](https://www.festo.com/es/es/a/4469/) |
| Buy | — | 1 | G1/4 female → G1/8 male adapter (actuator port) | TODO: find part number |

#### Silencers

On exhaust ports (port 3) of both valves.

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 2316 | 2 | U-1/4 silencer, G1/4 (EBS valve + VPPM exhaust) | [Festo](https://www.festo.com/es/es/a/2316/) |

#### Cables & Connectors

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 542256 | 1 | NEBU-M12W8-K-2-N-LE8, M12 8-pin shielded cable (VPPM control) | [Festo](https://www.festo.com/es/es/a/542256/) |
| Check | 541333 | 2 | NEBU-M8G3-K-2.5-LE3, M8 3-pin cable (pressure sensors) | [Festo](https://www.festo.com/es/es/a/541333/) |
| Buy | 151687 | 1 | MSSD-EB connector for EBS valve coil | [Festo](https://www.festo.com/es/es/a/151687/) |

#### Not needed in simplified design (but keep for reference)

These parts were in Diego's conservative design but are **not required** because the VPPM blocks all ports when unpowered:

| Part No. | Description | Why not needed |
|---|---|---|
| 8035167 | ASB Electrovalve V2 (VUVS-LT25-M32C-MD-G14-F8) | VPPM self-isolates, no series isolation valve needed |
| 6682 | Shuttle valve / OR (OS-1/4-B) | No leakage through VPPM to block |

---

## Historical Archive
The [Original "Conservative" Design](diego-design.md) (Diego's Design) included an additional solenoid valve for ASB isolation. This was deemed redundant after confirming the VPPM blocks all ports when unpowered.
