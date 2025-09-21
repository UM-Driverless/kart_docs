# Bill of Materials (BOM)

## Overview

This page provides a comprehensive list of all components required to build the driverless kart. Component data is now stored in YAML files within each assembly folder, following the project structure.

!!! info "New BOM Management System"
    Components are now managed via separate YAML files in each assembly folder. The folder structure represents the BOM tree itself, eliminating synchronization issues.

## How to Add Components to BOM

Adding a new component is simple:

1. **Find the right folder** - Navigate to the appropriate assembly folder (e.g., `docs/assembly/steering/`)
2. **Edit the bom.yaml file** - Open the `bom.yaml` file in that folder
3. **Add your component** - Copy an existing component entry and modify it with your new component's details
4. **Include key information**:
   - `id`: unique identifier (e.g., "motor_controller_v2")
   - `part_number`: manufacturer part number
   - `description`: what it is
   - `quantity`: how many needed
   - `unit_cost`: price per unit
   - `suppliers`: where to buy it (name, url)

That's it! The component will automatically appear in BOM reports.

## BOM Structure

The BOM is organized by assembly with YAML files containing detailed component specifications:

```
docs/assembly/
├── powertrain/
│   ├── bom.yaml              # Motor, throttle pedal
│   ├── transmission/bom.yaml # Chain, sprockets
│   └── fasteners/bom.yaml    # All powertrain fasteners
├── steering/
│   ├── bom.yaml              # H-bridge, motor, sensor, coupling
│   └── fasteners/bom.yaml    # All steering fasteners
├── electronics/
│   ├── bom.yaml              # Orin, ESP32, DAC, level shifter
│   └── power/bom.yaml        # Battery cells, BMS, auxiliary battery
└── sensors/bom.yaml          # ZED2 camera, YOLOv5 models
```

## Assembly Overview

### 🔧 Powertrain Assembly
**Components**: Motor, transmission system, throttle control
- **Main Components**: [Powertrain BOM](../assembly/powertrain/bom.yaml)
- **Transmission**: [Transmission BOM](../assembly/powertrain/transmission/bom.yaml)
- **Fasteners**: [Powertrain Fasteners BOM](../assembly/powertrain/fasteners/bom.yaml)
- **Documentation**: [Powertrain Assembly](../assembly/powertrain/index.md)

**Key Components:**
- Kunray MY1020 3000W motor (€150.00)
- IRIS 219 chain and sprocket system (€40.00)
- Hall effect throttle pedal (€2.46)

### 🎮 Steering Assembly
**Components**: Motor, sensor, H-bridge, coupling
- **Main Components**: [Steering BOM](../assembly/steering/bom.yaml)
- **Fasteners**: [Steering Fasteners BOM](../assembly/steering/fasteners/bom.yaml)
- **Documentation**: [Steering Assembly](../assembly/steering/index.md)

**Key Components:**
- Cytron MD30C H-bridge (€45.00)
- AS5600 magnetic angle sensor (€2.00)
- 24V DC steering motor (€80.00)

### 💻 Electronics Assembly
**Components**: Computing, control, communication
- **Main Components**: [Electronics BOM](../assembly/electronics/bom.yaml)
- **Documentation**: [Electronics Assembly](../assembly/electronics/microcontroller.md)

**Key Components:**
- NVIDIA Jetson AGX Orin (€1500.00)
- ESP32 WROOM-32 microcontroller (€3.50)
- Custom Orin adapter board (€25.00)

### ⚡ Power Assembly
**Components**: Main battery pack, BMS, auxiliary power
- **Main Components**: [Power BOM](../assembly/electronics/power/bom.yaml)
- **Documentation**: [Power Assembly](../assembly/electronics/power/battery.md)

**Key Components:**
- 52x Molicel P42A cells in 13S4P (€234.00)
- Jiabaida Smart BMS 100A (€85.00)
- 12V auxiliary battery (€60.00)

### 📷 Sensors Assembly
**Components**: Vision system, AI models
- **Main Components**: [Sensors BOM](../assembly/sensors/bom.yaml)
- **Documentation**: [Sensors Assembly](../assembly/sensors/camera.md)

**Key Components:**
- Stereolabs ZED2 stereo camera (€450.00)
- Custom YOLOv5 cone detection model

## Estimated Project Costs

| Assembly | Estimated Cost | Key Items |
|----------|----------------|-----------|
| **Powertrain** | **€195** | Motor (€150), transmission (€40), fasteners (€5) |
| **Steering** | **€135** | H-bridge (€45), motor (€80), sensor (€2), fasteners (€8) |
| **Electronics** | **€1530** | Orin computer (€1500), ESP32 (€4), adapter (€25) |
| **Power** | **€380** | Li-ion cells (€234), BMS (€85), 12V battery (€60) |
| **Sensors** | **€450** | ZED2 camera (€450) |
| **Total** | **€2690** | *Excludes chassis, wiring, mechanical hardware* |

!!! warning "Cost Estimates"
    Prices are approximate and subject to change. Always verify current pricing from suppliers.

## Component Status

### ✅ Active Components
Currently used and functional in the kart.

### ⚠️ Needs Replacement
Known to be damaged or worn:
- 219 aluminum rear sprocket (damaged from incompatible chain use)

### 🔧 Custom Components
Require fabrication:
- Custom 219 front sprocket (laser cut for 10mm shaft)
- Orin adapter board (EasyEDA design available)
- Battery pack assembly (professional assembly recommended)

## Supplier Information

### Primary Suppliers
- **Electronics**: Mouser, Digi-Key, Adafruit
- **Karting Parts**: KPS Racing
- **Batteries**: Authorized Molicel distributors
- **Vision Systems**: Stereolabs
- **General Components**: AliExpress, Amazon (for non-critical parts)

### Quality Guidelines
- ✅ Use official distributors for critical electronic components
- ✅ Verify specifications before ordering
- ⚠️ AliExpress/Amazon acceptable for mechanical parts and sensors
- ❌ Avoid counterfeit components for safety-critical systems

## Assembly Priority

1. **Power System** - Battery pack, BMS, charging setup
2. **Core Electronics** - Orin computer, ESP32 microcontroller
3. **Sensors** - ZED2 camera, angle sensors
4. **Propulsion** - Motor, controller, transmission
5. **Steering** - Motor, H-bridge, coupling
6. **Integration** - Wiring, mounting, calibration

## Working with YAML BOM Files

### Adding New Components
1. Locate the appropriate assembly folder
2. Edit the `bom.yaml` file
3. Follow the existing structure for consistency
4. Include all required fields: id, part_number, description, quantity, cost, suppliers

### YAML File Structure
```yaml
assembly: "assembly_name"
description: "Assembly description"
components:
  - id: "unique_component_id"
    part_number: "MANUFACTURER-PART-NUMBER"
    description: "Component description"
    quantity: 1
    unit_cost: 0.00
    currency: "EUR"
    status: "active"
    criticality: "essential"
    suppliers:
      - name: "Supplier Name"
        url: "https://supplier.com/product"
        verified: true
    specifications:
      key: "value"
    notes: "Additional information"
```

### Future Automation
A BOM aggregation script is planned to automatically generate:
- Complete cost summaries
- Supplier contact lists
- Component status reports
- Assembly checklists

---

*This BOM system reflects the complete restructure from hardware-based to assembly-based organization, with component data stored in YAML files following the project's folder structure.*