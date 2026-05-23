# Full BOM (shareable)

A consolidated, shareable bill of materials for the autonomous kart. Two cost columns:

- **Team cost (€)** — what the team actually paid to acquire the part. Donated and sponsored items are €0.
- **Market cost (€)** — what a new team would pay to buy the same part today, with no donations or sponsorship.

Use the per-assembly `bom.yaml` files for the full machine-readable record (part numbers, suppliers, specs). This page is the human-readable summary suitable for sharing.

!!! info "Source legend"
    - **Donated** — given to the team by an external partner (kart shop, sponsor, alumnus).
    - **Sponsored** — supplied at no cost (or heavily discounted) by a named sponsor in exchange for visibility.
    - **Purchased** — bought by the team from project funds.
    - **Salvage** — pulled from a discarded appliance / scrap (e.g. massage-chair motor). Team cost €0; market cost is the price of an equivalent new part.
    - **Custom** — designed and fabricated by the team (cost = materials + service like PCB / laser cut / 3D-print filament).

!!! note "VAT and shipping"
    All amounts are in EUR and include VAT and shipping where applicable. Some team purchases were intra-EU B2B with VAT reverse-charged (invoiced at 0 % VAT); in those cases the team-cost column reflects the amount actually transferred to the supplier. Market-cost figures are *retail incl. 21 % Spanish VAT* — what a new team paying out of pocket would see.

Numbers marked **`~`** are estimates pending confirmation from receipts.

---

## Chassis

| Part | Qty | Source | Team cost (€) | Market cost (€) | Notes |
|---|---:|---|---:|---:|---|
| Tony Kart Extreme frame (1999 ICA homologation) | 1 | Donated | 0 | ~800 | Used competition kart chassis. Verde Tony 30/32 mm chromoly, 40 mm rear axle. Equivalent used kart chassis market estimate. |
| Wheels and tyres (slicks set) | 1 set | Donated | 0 | ~200 | Came with the donated chassis. New set cost depends on compound. |
| Brake system (mechanical, OEM kart) | 1 | Donated | 0 | ~150 | Original kart hydraulic brake retained. |
| Steering column + tie rods | 1 | Donated | 0 | ~80 | Stock with chassis. |

**Chassis subtotal — team: €0 · market: ~€1230**

---

## Powertrain

| Part | Qty | Source | Team cost (€) | Market cost (€) | Notes |
|---|---:|---|---:|---:|---|
| Kunray MY1020 brushless motor + controller, 72 V 3000 W | 1 | Purchased | 150 | 150 | 10 mm shaft, no keyway. |
| IRIS 219 chain (100 links) | 1 | Purchased | 15 | 15 | KPS Racing. |
| 219 aluminium rear sprocket | 1 | Purchased | 20 | 20 | Currently damaged — needs replacement. |
| Custom 10 mm-bore 219 front sprocket (laser cut) | 1 | Custom | 5 | 5 | Material + laser-cut service. |
| Hall-effect throttle pedal (SS49E) | 1 | Purchased | 2.50 | 2.50 | AliExpress. |

**Powertrain subtotal — team: ~€192.50 · market: ~€192.50**

---

## Steering

| Part | Qty | Source | Team cost (€) | Market cost (€) | Notes |
|---|---:|---|---:|---:|---|
| Cytron MD25HV H-bridge (25 A, 7–58 V) | 1 | Purchased | 55 | 55 | Replaces older MD30C. |
| 24 V DC steering motor (operated at 12 V) | 1 | Salvage | 0 | ~50 | Pulled from a discarded massage chair. Drives the steering through the 15 : 1 3D-printed planetary below. Has ~2 kW stall reserve (rarely hit; normal operation is ~50–200 W). Off-the-shelf wiper motors are noted as **interesting alternatives** in the [Steering Power Budget](../assembly/steering/power-budget.md), not as replacements. |
| 3D-printed planetary reducer, **15 : 1** (PLA/PETG) | 1 | Custom | ~6 | ~6 | ~150 g filament @ €25/kg + 4× 608 bearings (~€2) + M3 hardware. Print time on team printer not costed. Gives the salvage motor the torque headroom needed to cover edge cases without procurement. |
| AS5600 magnetic angle sensor module | 1 | Purchased | 2 | 2 | I²C, 12-bit. |
| 10 mm shaft coupling | 1 | Purchased | 15 | 15 | Aluminium. |
| Steering fasteners (M3/M6/M8 set) | — | Purchased | ~5 | ~5 | See `steering/fasteners/bom.yaml`. |

**Steering subtotal — team: ~€83 · market: ~€133**

---

## Electronics — Compute & control

| Part | Qty | Source | Team cost (€) | Market cost (€) | Notes |
|---|---:|---|---:|---:|---|
| NVIDIA Jetson AGX Orin Developer Kit (64 GB) | 1 | Purchased | 1857.29 | ~2200 | Silicon Highway invoice 2023-04: net €1 821.29 + €36 shipping, intra-EU reverse charge (VAT 0 % on invoice). True project cost is **~€2 247** once URJC self-accounts the 21 % reverse-charge VAT[^vat]; this column shows what was actually transferred to the supplier. Today's retail incl. 21 % VAT for the 64 GB devkit is ~€2 200. |
| Custom Orin adapter PCB (v1.0) | 1 | Custom | ~25 | ~25 | EasyEDA design + JLCPCB-style fabrication. |
| ESP32-WROOM-32 dev board (legacy, hand-wired in current kart) | 1 | Purchased | ~3.50 | ~3.50 | Currently flying-wired. |
| ESP32-S3-WROOM-1-N8R2 dev board (next-revision Kart Medulla) | 1 | Purchased | 8.69 | 8.69 | AliExpress, ordered 2026 for the new interface PCB. |
| MCP4728 quad 12-bit I²C DAC | 1 | Planned | ~3 | ~3 | For CMD_ACC analogue out. |
| Kart Medulla interface PCB (next revision, blank) | 1 | Custom | ~15 | ~15 | Estimate — small 2-layer board, JLCPCB-style. |
| Wago-style push-in terminal blocks (Medulla) | ~30 | Planned | ~10 | ~10 | Replaces Dupont harness. |
| Logic-level shifters + op-amps + passives (incl. motor-Hall conditioning) | — | Planned | ~10 | ~10 | Reads the motor's three Hall sensors via the Medulla PCB; no external wheel-speed sensors needed. |
| 500 GB M.2 NVMe SSD (Orin storage) | 1 | Salvage | 0 | ~40 | Pulled out of a laptop during a 2 TB upgrade. Big improvement on dev/install work for the Orin (`apt`, builds, repos); no effect on the runtime FPS of the autonomy stack. |

**Compute & control subtotal — team: ~€1932 · market: ~€2315**

---

## Electronics — Power (traction battery)

The traction pack was assembled by the team from individual components rather than bought as a unit. Listing the breakdown so a new team can reproduce it. There is **no separate 12 V auxiliary battery** — the 12 V rail for sensors is generated from the traction pack via a buck regulator (see wiring diagram).

| Part | Qty | Source | Team cost (€) | Market cost (€) | Notes |
|---|---:|---|---:|---:|---|
| Molicel P42A 21700 Li-ion cell | 52 | Purchased | 198 | ~234 | 13S4P pack. NKON bulk: 60 cells for €230 (€3.83/cell), 52 used in the pack. Retail ~€4.50/cell. |
| Jiabaida JBD-SP22S003B smart BMS, 100 A | 1 | Purchased | 85 | 85 | 13S, Bluetooth + UART. |
| Pure-nickel strip (0.15 × 8 mm, ~2 m) | 1 | Purchased | ~10 | ~10 | For series/parallel interconnects. |
| Cell holders (4×13 21700 plastic frames) | 1 set | Purchased | ~8 | ~8 | AliExpress. |
| Kapton tape + fish-paper insulators | — | Purchased | ~5 | ~5 | Insulation under nickel. |
| Heat-shrink + double-sided tape | — | Purchased | ~5 | ~5 | Pack assembly. |
| 3D-printed enclosure (PETG, ~600 g) | 1 | Custom | ~15 | ~15 | Filament cost only; print time on team printer. |
| Fire-retardant foam liner (mica/ceramic blanket) | 1 | Purchased | ~15 | ~15 | Inside the enclosure. |
| Anderson SB50 / XT90 pack connectors | 2 | Purchased | ~10 | ~10 | Main + charge ports. |
| 8 AWG silicone power cable (~1 m) | 1 | Purchased | ~6 | ~6 | Pack output. |
| 12 V buck regulator (from 48 V pack) | 1 | Purchased | ~10 | ~10 | Replaces the previous 12 V lead-acid aux battery. |

**Power subtotal — team: ~€367 · market: ~€403**

---

## Sensors

| Part | Qty | Source | Team cost (€) | Market cost (€) | Notes |
|---|---:|---|---:|---:|---|
| Stereolabs ZED 2 stereo camera | 1 | Purchased | 450 | 450 | Primary perception sensor. |
| Custom YOLOv5 cone-detection model | 1 | Custom | 0 | 0 | Trained in-house. |
| Motor Hall sensors (×3) | 0 | Built-in | 0 | 0 | Internal to the Kunray motor; read via level shifters on the Kart Medulla PCB. No external sensors needed. |

**Sensors subtotal — team: €450 · market: €450**

---

## Emergency Braking System (pneumatic, sponsored)

The full pneumatic EBS / ASB stack is supplied by **Festo Automation, S.A.U.**, an official sponsor of the team. Item-level part numbers, datasheets, quantities and reuse status are tracked in the [Emergency Braking BOM](../assembly/emergency-braking/bom.md). Per-line market prices are intentionally redacted on this public page (see note below).

!!! note "Why prices are redacted in this section"
    Per-component market values for the Festo-supplied parts are not published here, as a courtesy to the sponsor relationship and consistent with the confidentiality obligations of the team's collaboration agreement with Festo. Public distributor reference prices for these parts have been collected and are kept in the team's internal Drive for project bookkeeping. The team's monetary cost for these items is **€0**; the team's contribution under the agreement is visibility (logo on the kart, social-media tagging, sponsor listing on the team site, invitations to Formula Student events) rather than a cash payment.

| Festo PN | Description | Qty | Source | Team cost (€) | Market value (€) |
|---|---|---:|---|---:|---:|
| 8084714 | ADN-S-50-45-I-P-A pneumatic actuator | 1 | Sponsored | 0 | redacted |
| 8035174 | VUVS-LT25-M32U-MD-G14-F8 EBS electrovalve (NO) | 1 | Sponsored | 0 | redacted |
| 8035167 | VUVS-LT25-M32C-MD-G14-F8 ASB electrovalve (NC) — spare, not in validated circuit | 1 | Sponsored † | 0 | redacted |
| 571293 | VPPM-8L-L-1-G14-0L10H-V1P-S1C1 proportional regulator | 1 | Sponsored † | 0 | redacted |
| 6682 | OS-1/4-B shuttle valve / OR gate | 1 | Sponsored † | 0 | redacted |
| 527690 | MS4-LR-1/4-D7-AD10 low-pressure regulator | 1 | Sponsored † | 0 | redacted |
| 567465 | SDE5-D10-NF-Q6E-V-M8 pressure sensor (0–10 bar) | 2 | Sponsored | 0 | redacted |
| 197384 | PUN-H-6X1-BL pneumatic tubing | 3 m | Sponsored | 0 | redacted |
| 2029 | CK-1/4-PK-4 push-in fitting | 15 | Sponsored | 0 | redacted |
| 8030236 | NPFC-T-3G14-F threaded T-adapter | 2 | Sponsored | 0 | redacted |
| 4469 | LCK-1/8-PK-4 elbow fitting | 1 | Sponsored | 0 | redacted |
| 2316 | U-1/4 silencer | 3 | Sponsored | 0 | redacted |
| 2307 | U-1/8 silencer | 1 | Sponsored | 0 | redacted |
| 542256 | NEBU-M12W8-K-2-N-LE8 M12 cable (VPPM control) | 1 | Sponsored † | 0 | redacted |
| 541333 | NEBU-M8G3-K-2.5-LE3 M8 cable (sensor wiring) | 2 | Sponsored | 0 | redacted |
| 8030801 | VACF-B-B2-5 solenoid coil (ASB valve) — spare, not in validated circuit | 1 | Sponsored | 0 | redacted |
| 151687 | MSSD-EB valve-coil connector | 2 | Sponsored | 0 | redacted |
| — | Sensata PTE/700-33 hydraulic pressure sensor | 1 | Sponsored | 0 | redacted |

**EBS subtotal — team: €0. Market values redacted under the Festo sponsorship agreement.**

† Items marked with the dagger were requested under the current Festo sponsorship cycle and are pending delivery at time of writing — the rest of the stack is reused from earlier sponsorship cycles and is already on the kart.

> The pneumatic schematic and component photos live under [Emergency Braking](../assembly/emergency-braking/index.md). The 12 V air compressor + tank is on the planned-purchase list but not yet on the kart, so it isn't counted here.

---

## Wiring & misc hardware

| Part | Qty | Source | Team cost (€) | Market cost (€) | Notes |
|---|---:|---|---:|---:|---|
| Powertrain fasteners (M6/M8 + nuts) | — | Purchased | ~5 | ~5 | See `powertrain/fasteners/bom.yaml`. |
| 24 V → 5 V / 3.3 V buck converters | 2 | Purchased | ~6 | ~6 | Rail generation. |
| XT90-S anti-spark connector (pack switch) | 1 | Purchased | ~10 | ~10 | Currently doubles as the precharge mechanism. A proper main contactor should be added in a future revision. |
| Generic harness wire, lugs, heat-shrink | — | Purchased | ~30 | ~30 | Whole-vehicle harness. |
| Wheel-axle bearings (replacement set) | — | Purchased | ~20 | ~20 | Replaced during build. |

**Wiring subtotal — team: ~€71 · market: ~€71**

---

## Totals

| Section | Team cost (€) | Market cost (€) |
|---|---:|---:|
| Chassis | 0 | ~1230 |
| Powertrain | ~192.50 | ~192.50 |
| Steering | ~83 | ~133 |
| Electronics — compute & control | ~1932 | ~2315 |
| Electronics — power | ~367 | ~403 |
| Sensors | 450 | 450 |
| Emergency braking (pneumatic) | 0 | redacted |
| Wiring & misc hardware | ~71 | ~71 |
| **Total (transferred to suppliers)** | **~€3095** | redacted |
| Reverse-charge VAT on the Orin (self-accounted by URJC) | +~390 | — |
| **Total incl. VAT actually borne by the project** | **~€3485** | redacted |

The market column for the EBS section is redacted under the Festo sponsorship agreement, which makes the page-level market total non-disclosable as well. Excluding the Festo-supplied stack, the rest of the kart at retail comes to ~€4 815 incl. VAT (chassis ~€1 230, powertrain ~€192.50, steering ~€133, compute & control ~€2 315, power ~€403, sensors €450, wiring ~€71).

The ~€1.5 k delta between team cost and that priced-but-non-Festo market subtotal comes from the donated chassis (~€1 230), the salvaged steering motor (~€50), and the salvaged Orin SSD (~€40).

---

## Tooling required to build / maintain the kart

Not consumed by the build, but required to do it. Costs here are rough market prices for hobby/entry-grade equipment that's adequate for this project — a new team can borrow most of these from a university workshop.

### Mechanical

| Tool | Used for | Indicative cost (€) |
|---|---|---:|
| TIG welder (small, 200 A class) | Chassis modifications, motor mount welding | ~600 |
| MIG welder (entry hobby) | Battery box / mounting brackets | ~300 |
| Angle grinder (115 mm) + cutting/flap discs | General metalwork | ~80 |
| Cordless drill + HSS bit set | Mounting holes, brackets | ~120 |
| Bench vice (100 mm) | Holding parts for cutting / filing | ~70 |
| Hand files, deburring tools | Edge finishing | ~30 |
| Torque wrench set (5–25 Nm and 20–100 Nm) | Critical fasteners (steering, motor mount, axle) | ~100 |
| Metric hex key set + sockets + ratchet | Generic fastening | ~80 |
| Digital caliper (0–150 mm) | Layout / verification | ~25 |
| Tape measure, combination square | Layout | ~15 |

### Fabrication (outsource-friendly)

| Tool | Used for | Indicative cost (€) |
|---|---|---:|
| 3D printer (Bambu A1 / P1S class) | Battery box, sensor mounts, brackets | ~400 |
| Laser cutting (sheet metal / acrylic) | Front sprocket, brackets — outsourced per cut | per-job |
| PCB fabrication (JLCPCB-style) | Orin adapter, Kart Medulla — outsourced | per-job |

### Electronics

| Tool | Used for | Indicative cost (€) |
|---|---|---:|
| Soldering station (60 W, temp controlled) | Through-hole and SMD rework | ~100 |
| SMD hot-air station | QFN/QFP rework | ~80 |
| Wire stripper / crimper (10–24 AWG) | Signal and power harness | ~30 |
| Heavy-duty crimper (8–2 AWG) | Battery cables, lugs | ~60 |
| Digital multimeter | Continuity, voltage, current | ~50 |
| Oscilloscope (entry, ~50 MHz) | UART/I²C/CAN debug, PWM checks | ~250 |
| USB–CAN adapter | CAN bus monitoring | ~40 |
| 12 V / 24 V bench PSU (or smart battery charger) | Aux battery test, sensor power | ~80 |

### Battery assembly (specific tools)

| Tool | Used for | Indicative cost (€) |
|---|---|---:|
| Spot welder (capacitor or pulse, ~1 kJ) | Welding nickel strip to cells | ~150 |
| Cell-level fuse wire / fuse holders | Per-cell fusing (safety) | ~10 |
| IR thermometer | Verifying weld/joint temperature | ~25 |
| Insulating mat + safety glasses + nitrile gloves | PPE for cell handling | ~30 |

**Tooling indicative total (one-time): ~€2700** — most can be borrowed; only consumables and PCB/laser-cut service are recurring.

---

## What this page deliberately omits

- **Invoice numbers, vendor account IDs, supplier-specific PO numbers** — kept in the team's private archive, not in this public repo.
- **Donor names** beyond the agreed-public sponsors. If you need credits/acknowledgements, see the team contact page.
- **Per-cell serial numbers** for the traction pack — tracked in the private inventory.

For machine-readable component data (part numbers, specs, suppliers) consult the per-assembly `bom.yaml` files linked from [BOM overview](index.md).

[^vat]: Intra-EU B2B sales are zero-rated on the supplier side under reverse charge (Council Directive 2006/112/EC, Art. 138 + Art. 196). The buyer self-accounts VAT in its own return. URJC, as a public university whose activity is mainly non-economic, generally has no (or very limited) VAT-deduction right, so the self-accounted 21 % is a real cost to the project — paid to the Spanish tax agency rather than to the supplier. Buying the same kit from outside the EU would not be tax-free either: import VAT (21 %) is charged at the border, plus a courier handling fee.
