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

### Components
- [Solenoid valve](https://www.festo.com/tw/en/a/575488/) (Emergency)
    - **Type:** 3/2-way, Normally Closed (NC).
    - [Datasheet local](../../assets/datasheets/575488datasheet.pdf) | [Datasheet online](https://www.festo.com/tw/en/a/download-document/datasheet/575488)
- [Proportional Valve](https://www.festo.com/gb/en/search/?text=VPPM-8L-L-1-G14-0L10H-V1P-S1C1) (ASB Control)
    - **Model:** VPPM-8L-L-1-G14-0L10H-V1P-S1C1 (571293)
    - 0-10V setpoint, 0-10 bar regulation, G1/4 ports.
    - [VPPM catalog documentation (local)](../../assets/datasheets/205274_documentation.pdf) | [online](https://www.festo.com/media/catalog/205274_documentation.pdf)
    - [Part-specific datasheet (local)](../../assets/datasheets/VPPM_en.pdf) | [online](https://www.festo.com/us/en/a/571293/)
    - **Action:** Requires specific M12 cable (see cables below).
- [Shuttle Valve](https://www.festo.com/es/es/a/6682/) (OR Logic)
    - **Model:** OS-1/4-B, Ports: G1/4.
- Pressure sensor
- **Cable for Proportional Valve**
    - **Ref:** `NEBU-M12W8-K-2-N-LE8` (M12, 8-pin, shielded).
- **Cable for Sensor**
    - **Ref:** `NEBU-M8G3-K-2.5-LE3` (M8, 3-pin).

---

## Historical Archive
The [Original "Conservative" Design](diego-design.md) (Diego's Design) included an additional solenoid valve for ASB isolation. This was deemed redundant after confirming the VPPM blocks all ports when unpowered.
