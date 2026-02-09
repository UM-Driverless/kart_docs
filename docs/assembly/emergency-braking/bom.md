# Bill of Materials

All pneumatic ports standardized to **G1/4** unless noted. Tubing is **6 mm OD / 4 mm ID** throughout. FS 2026 rules: push-in fittings are allowed for ASB/EBS, but we prefer compression (union nut) fittings. Exception: the SDE5 sensor has an integrated QS-6 push-in port.

The BOM follows the pneumatic path from tank output to actuator.

## Tubing

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 197384 | PUN-H-6X1-BL tubing, 6 mm OD / 4 mm ID, blue (3 m) | [Festo](https://www.festo.com/es/es/a/197384/) |

## Pressure Sensor 1 (tank side, before regulator)

Monitors tank/supply pressure. Connects directly to tubing via integrated 6 mm push-in fitting.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 567465 | SDE5-D10-NF-Q6E-V-M8 pressure sensor, 0-10 bar, 0-10V analog, M8 connector, QS-6 push-in | [Festo](https://www.festo.com/es/es/a/567465/) |

> TODO: Verify this sensor can handle >10 bar on the tank side without damage. If not, place it after the regulator only.

## Manual Valve (brake release / isolation)

Manual ball valve for brake release during maintenance and system isolation. Reuse existing on-hand valve.

| Status | Part No. | Description | Notes |
|---|---|---|---|
| Reuse | — | Manual ball valve, G1/4 | On-hand from previous seasons |

## Low-Pressure Regulator

Adjustable regulator to set maximum system working pressure downstream of the tank.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 527690 | MS4-LR-1/4-D6-AD10 pressure regulator, G1/4, 0.5-10 bar | [Festo](https://www.festo.com/es/es/a/527690/) |

## Pressure Sensor 2 (regulated side, before valves)

Monitors regulated pressure entering the valve stage. Same model as sensor 1.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 567465 | SDE5-D10-NF-Q6E-V-M8 (second unit) | [Festo](https://www.festo.com/es/es/a/567465/) |

## EBS Electrovalve (emergency braking, in parallel with VPPM)

Normally-open solenoid valve. When powered (driving): closed. When unpowered (emergency): opens and delivers full supply pressure to the actuator.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 8035174 | VUVS-LT25-M32U-MD-G14-F8, 3/2-way, Normally Open, G1/4 | [Festo](https://www.festo.com/es/es/a/8035174/) |

## VPPM Proportional Valve (ASB, in parallel with EBS)

Proportionally controls brake pressure during autonomous driving. All ports blocked when unpowered (see [VPPM analysis](index.md#vppm-unpowered-behavior-what-does-unregulated-mean)).

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Buy | 571293 | VPPM-8L-L-1-G14-0L10H-V1P-S1C1, 0-10 bar, 0-10V setpoint, G1/4 | [Festo](https://www.festo.com/es/es/a/571293/) |
| | | [VPPM catalog documentation (local)](../../assets/datasheets/205274_documentation.pdf) | [online](https://www.festo.com/media/catalog/205274_documentation.pdf) |
| | | [Part-specific datasheet (local)](../../assets/datasheets/VPPM_en.pdf) | [online](https://www.festo.com/us/en/a/571293/) |

## Pneumatic Actuator

Spring-return cylinder. **G1/8 ports** — requires G1/4 → G1/8 adapter.

| Status | Part No. | Description | Festo link |
|---|---|---|---|
| Reuse | 8084714 | ADN-S-50-45-I-P-A, bore 50 mm, stroke 45 mm, G1/8, 0.4-10 bar | [Festo](https://www.festo.com/gb/en/a/8084714/) |

## Compression Fittings

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 2029 | ~10 | CK-1/4-PK-4 straight, G1/4 → tube 6 mm (all valve ports and general connections) | [Festo](https://www.festo.com/es/es/a/2029/) |
| Buy | 4487 | 2 | TCK-1/4-PK-4 T-fitting, G1/4 → tube 6 mm (split to parallel valves + merge outputs) | [Festo](https://www.festo.com/es/es/a/4487/) |
| Buy | 4469 | 1 | LCK-1/8-PK-4 elbow, G1/8 → tube 6 mm (actuator connection) | [Festo](https://www.festo.com/es/es/a/4469/) |
| Buy | — | 1 | G1/4 female → G1/8 male adapter (actuator port) | TODO: find part number |

## Silencers

On exhaust ports (port 3) of both valves.

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 2316 | 2 | U-1/4 silencer, G1/4 (EBS valve + VPPM exhaust) | [Festo](https://www.festo.com/es/es/a/2316/) |

## Cables & Connectors

| Status | Part No. | Qty | Description | Festo link |
|---|---|---|---|---|
| Buy | 542256 | 1 | NEBU-M12W8-K-2-N-LE8, M12 8-pin shielded cable (VPPM control) | [Festo](https://www.festo.com/es/es/a/542256/) |
| Check | 541333 | 2 | NEBU-M8G3-K-2.5-LE3, M8 3-pin cable (pressure sensors) | [Festo](https://www.festo.com/es/es/a/541333/) |
| Buy | 151687 | 1 | MSSD-EB connector for EBS valve coil | [Festo](https://www.festo.com/es/es/a/151687/) |

## Not needed in simplified design (but keep for reference)

These parts were in Diego's conservative design but are **not required** because the VPPM blocks all ports when unpowered:

| Part No. | Description | Why not needed |
|---|---|---|
| 8035167 | ASB Electrovalve V2 (VUVS-LT25-M32C-MD-G14-F8) | VPPM self-isolates, no series isolation valve needed |
| 6682 | Shuttle valve / OR (OS-1/4-B) | No leakage through VPPM to block |
