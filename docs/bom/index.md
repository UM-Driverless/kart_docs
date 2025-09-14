# Bill of Materials (BOM)

## Overview

This page provides a comprehensive list of all components required to build the driverless kart. Each component is documented with specifications, suppliers, costs, and alternatives.

!!! info "BOM Management"
    Component details are maintained in the individual hardware documentation pages using YAML frontmatter. This page provides consolidated views and summaries.

## Summary by Category

### Core Systems

| Component | Quantity | Unit Cost | Total Cost | Status | Documentation |
|-----------|----------|-----------|------------|--------|---------------|
| ESP32 WROOM 32 | 1 | €3.50 | €3.50 | Active | [ESP32](../hardware/esp32/index.md) |
| Kunray MY1020 Motor | 1 | €150.00 | €150.00 | Active | [Motor](../hardware/motor/index.md) |
| AS5600 Angle Sensor | 1 | €2.00 | €2.00 | Active | [Steering Sensor](../hardware/steering/sensor/index.md) |
| Throttle Pedal (w/ SS49E) | 1 | €2.46 | €2.46 | Active | [Throttle Pedal](../hardware/throttle-pedal/index.md) |

### Transmission System

| Component | Quantity | Unit Cost | Total Cost | Status | Documentation |
|-----------|----------|-----------|------------|--------|---------------|
| IRIS 219 Chain (100 links) | 1 | €15.00 | €15.00 | Active | [Transmission](../hardware/transmission/index.md) |
| 219 Aluminum Sprocket | 1 | €20.00 | €20.00 | Needs Replacement | [Transmission](../hardware/transmission/index.md) |
| Custom 219 Front Sprocket | 1 | €5.00 | €5.00 | Active | [Transmission](../hardware/transmission/index.md) |

## Cost Summary

| Category | Total Cost | Items |
|----------|------------|-------|
| Core Electronics | €157.96 | 4 |
| Transmission | €40.00 | 3 |
| **Project Total** | **€197.96** | **7** |

### Cost Breakdown Details
- **ESP32 WROOM 32**: €3.50
- **Kunray MY1020 Motor**: €150.00
- **AS5600 Angle Sensor**: €2.00
- **Throttle Pedal (SS49E)**: €2.46
- **IRIS 219 Chain**: €15.00
- **219 Aluminum Sprocket**: €20.00 (needs replacement)
- **Custom 219 Front Sprocket**: €5.00

!!! warning "Incomplete BOM"
    This BOM is being migrated from existing documentation. Additional components (battery, chassis, wiring, etc.) will be added as the migration continues.

## Component Status

- **Active**: Currently used in the kart
- **Needs Replacement**: Known to be damaged/worn
- **Deprecated**: No longer used but kept for reference
- **Optional**: Not required for basic functionality

## Supplier Recommendations

### Primary Suppliers
- **Electronic Components**: Mouser, Addicore, Sunrom
- **Karting Parts**: KPS Racing
- **General Parts**: AliExpress, Amazon

### Quality Notes
- Always prefer official distributors for critical electronic components
- AliExpress/Amazon acceptable for mechanical parts and sensors
- Verify component specifications before ordering

## Assembly Priority

1. **Core Electronics** (ESP32, sensors)
2. **Motor System** (Motor, controller)
3. **Transmission** (Chain, sprockets)
4. **Mechanical** (Chassis, steering)
5. **Power Systems** (Battery, wiring)

---

## Adding Components to BOM

To add a new component to the BOM:

1. Add YAML frontmatter to the component's documentation page
2. Use the standardized structure shown in individual hardware pages
3. The BOM summary will be updated manually or via script