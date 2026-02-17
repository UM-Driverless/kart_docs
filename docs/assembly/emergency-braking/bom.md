# Bill of Materials

All pneumatic ports standardized to **G1/4** unless noted. Tubing is **6 mm OD / 4 mm ID** throughout. FS 2026 rules: push-in fittings are allowed for ASB/EBS, but we prefer compression (union nut) fittings. Exception: the SDE5 sensor has an integrated QS-6 push-in port.

This BOM covers the **full design** (ASB + OR valve). The simplified design uses the same parts minus the ASB valve, OR valve, ASB coil, and one silencer/connector.

The BOM follows the pneumatic path from compressor/tank to actuator.

## Compressor & Tank

12V portable compressor with integrated 6 L tank. Fills the system and maintains pressure.

| Status | Part No. | Description | Link |
|---|---|---|---|
| Buy | — | VEVOR air compressor, 12V, 90-120 psi (6.2-8.3 bar), 6 L tank | [VEVOR](https://www.vevor.es/bocina-aire-comprimido-c_11496/vevor-compresor-de-aire-para-kit-de-bocina-90-120-psi-bomba-de-aire-con-tanque-de-6-l-para-inflar-neumaticos-colchones-de-aire-compatible-con-todos-los-vehiculos-de-12-v-trenes-barcos-coches-taller-p_010247980894) |

## Tubing

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 197384 | PUN-H-6X1-BL tubing, 6 mm OD / 4 mm ID, blue (3 m) | [Festo](https://www.festo.com/es/es/a/197384/) |

Datasheet (local): [`197384datasheet.pdf`](../../assets/datasheets/197384datasheet.pdf)

## Pressure Sensor 1 (tank side, before regulator)

Monitors tank/supply pressure. Connects directly to tubing via integrated 6 mm push-in fitting. **Max measurement range: 10 bar** — no overpressure rating documented.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 567465 | SDE5-D10-NF-Q6E-V-M8 pressure sensor, 0-10 bar, 0-10V analog, M8 connector, QS-6 push-in | [Festo](https://www.festo.com/es/es/a/567465/) |

Datasheet (local): [`567465datasheet.pdf`](../../assets/datasheets/567465datasheet.pdf)

> **Warning:** This sensor is rated 0-10 bar. The tank side may see up to 8.3 bar (compressor max). If placed before the regulator, ensure supply pressure stays within 10 bar or the sensor may be damaged.

## Manual Valve (brake release / isolation)

Manual ball valve for brake release during maintenance and system isolation. Reuse existing on-hand valve.

| Status | Part No. | Description | Notes |
|---|---|---|---|
| Reuse | — | Manual ball valve, G1/4 | On-hand from previous seasons |

## Low-Pressure Regulator

Adjustable regulator to set maximum system working pressure downstream of the tank. Updated to **D7** variant for higher output range (0.5-12 bar vs D6's 0.5-10 bar).

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 527690 | MS4-LR-1/4-D7-AD10 pressure regulator, G1/4, 0.5-12 bar | [Festo](https://www.festo.com/es/es/a/527690/) |

Datasheet (local): [`527690datasheet.pdf`](../../assets/datasheets/527690datasheet.pdf)

> **Note:** The D7-AD10 subtype is selected within the same Festo product page as the D6 variant. The D6 maxes out at 7 bar (confirmed on unit label: p2 max 7 bar / 105 psi), which is too low for our system. The D7 extends output to 0.5-12 bar — there is no intermediate variant capping at 10 bar.

> **Warning — max system pressure is 10 bar.** The D7 regulator can output up to 12 bar, but all downstream components are rated at 10 bar or below (VUVS valves: 10 bar, SDE5 sensors: 10 bar, ADN-S actuator: 10 bar, VPPM inlet: 11 bar). **Never set the regulator above 10 bar** or downstream components may be damaged. There is no MS4-LR variant that caps at exactly 10 bar (D6 = 7 bar, D7 = 12 bar), so operational discipline or a downstream relief valve is required.

## Pressure Sensor 2 (regulated side, before valves)

Monitors regulated pressure entering the valve stage. Same model as sensor 1.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 567465 | SDE5-D10-NF-Q6E-V-M8 (second unit) | [Festo](https://www.festo.com/es/es/a/567465/) |

Datasheet (local): [`567465datasheet.pdf`](../../assets/datasheets/567465datasheet.pdf)

## EBS Electrovalve (emergency braking)

Normally-open solenoid valve. When powered (driving): closed. When unpowered (emergency): opens and delivers full supply pressure to the actuator. In both simplified and full designs. **Max operating pressure: 10 bar** (2.5-10 bar range).

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 8035174 | VUVS-LT25-M32U-MD-G14-F8, 3/2-way, Normally Open, G1/4, 2.5-10 bar | [Festo](https://www.festo.com/es/es/a/8035174/) |
| | 575488 | [Datasheet (local)](../../assets/datasheets/575488datasheet.pdf) | (matches VUVS-L25-M32U-MD-G14-F8) |

## ASB Electrovalve (VPPM supply isolation)

Normally-closed solenoid valve in series before the VPPM. When powered (driving): open, allowing regulated pressure to reach the VPPM. When unpowered (emergency): closes, cutting supply to the VPPM to prevent any potential seal-degradation leakage. **Full design only** — not needed in simplified design. **Max operating pressure: 10 bar** (2.5-10 bar range).

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 8035167 | VUVS-LT25-M32C-MD-G14-F8, 3/2-way, Normally Closed, G1/4, 2.5-10 bar | [Festo](https://www.festo.com/es/es/a/8035167/) |

## VPPM Proportional Valve (ASB)

Proportionally controls brake pressure during autonomous driving. All ports blocked when unpowered (see [VPPM analysis](index.md#vppm-unpowered-behavior-what-does-unregulated-mean)). **Max inlet pressure: 11 bar** (port 1). Output regulation range: 0-10 bar.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 571293 | VPPM-8L-L-1-G14-0L10H-V1P-S1C1, 0-10 bar output, max 11 bar inlet, 0-10V setpoint, G1/4 | [Festo](https://www.festo.com/es/es/a/571293/) |
| | | [VPPM catalog documentation (local)](../../assets/datasheets/205274_documentation.pdf) | [online](https://www.festo.com/media/catalog/205274_documentation.pdf) |
| | | [Part-specific datasheet (local)](../../assets/datasheets/VPPM_en.pdf) | [online](https://www.festo.com/us/en/a/571293/) |

## Shuttle Valve (OR valve)

Ball-type shuttle valve that merges the EBS and VPPM output lines. Whichever side has higher pressure pushes the ball to seal the other port, preventing backflow. **Full design only** — not needed in simplified design.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 6682 | OS-1/4-B shuttle valve, G1/4 | [Festo](https://www.festo.com/es/es/a/6682/) |

## Pneumatic Actuator

Spring-return cylinder. **G1/8 ports** — requires G1/4 → G1/8 adapter. **Max operating pressure: 10 bar** (0.4-10 bar for 50mm bore).

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 8084714 | ADN-S-50-45-I-P-A, bore 50 mm, stroke 45 mm, G1/8, 0.4-10 bar | [Festo](https://www.festo.com/gb/en/a/8084714/) |

Datasheet (local): [`adn-s-enus.pdf`](../../assets/datasheets/adn-s-enus.pdf)

## Compression Fittings

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 2029 | ~15 | CK-1/4-PK-4 straight, G1/4 → tube 6 mm (all valve ports, NPFC-T ports, and general connections) | [Festo](https://www.festo.com/es/es/a/2029/) |
| Buy | 8030236 | 2 | NPFC-T-3G14-F threaded T-adapter, 3× G1/4 female (split to parallel valves + merge outputs). Each port needs a CK-1/4 fitting. | [Festo](https://www.festo.com/es/es/a/8030236/) |
| Buy | 4469 | 1 | LCK-1/8-PK-4 elbow, G1/8 → tube 6 mm (actuator connection) | [Festo](https://www.festo.com/es/es/a/4469/) |
| Buy | — | 1 | G1/4 female → G1/8 male adapter (actuator port) | TODO: find part number |

> **Note:** CK-1/4 qty increased from ~10 to ~15. The 6 extra fittings are for the NPFC-T threaded ports (3 ports × 2 T-adapters = 6 CK fittings).

> **Change:** TCK-1/4-PK-4 (4487) replaced by NPFC-T-3G14-F (8030236). The TCK was a push-in T-fitting; the NPFC-T is a threaded T-adapter that accepts CK compression fittings at each port, giving a more secure connection.

Datasheets (local):

- [`2029datasheet.pdf`](../../assets/datasheets/2029datasheet.pdf)
- [`4469datasheet.pdf`](../../assets/datasheets/4469datasheet.pdf)

## Silencers

On exhaust ports of all valves and the actuator exhaust.

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 2316 | 3 | U-1/4 silencer, G1/4 (EBS valve + VPPM exhaust + ASB valve exhaust) | [Festo](https://www.festo.com/es/es/a/2316/) |
| Buy | 2307 | 1 | U-1/8 silencer, G1/8 (actuator exhaust port) | [Festo](https://www.festo.com/es/es/a/2307/) |

Datasheet (local): [`2316datasheet.pdf`](../../assets/datasheets/2316datasheet.pdf)

## Cables & Connectors

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 542256 | 1 | NEBU-M12W8-K-2-N-LE8, M12 8-pin shielded cable (VPPM control) | [Festo](https://www.festo.com/es/es/a/542256/) |
| Check | 541333 | 2 | NEBU-M8G3-K-2.5-LE3, M8 3-pin cable (pressure sensors) | [Festo](https://www.festo.com/es/es/a/541333/) |
| Buy | 8030801 | 1 | Solenoid coil for ASB valve (VUVS-LT25) | [Festo](https://www.festo.com/es/es/a/8030801/) |
| Buy | 151687 | 2 | MSSD-EB connector for valve coils (1× EBS + 1× ASB) | [Festo](https://www.festo.com/es/es/a/151687/) |
