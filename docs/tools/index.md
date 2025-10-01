# Workshop Tools & Equipment

## Overview

This section catalogs all tools and equipment used for kart assembly, maintenance, and debugging.

!!! info "Tool Management"
    Tools are tracked in the [`tools.yaml`](tools.yaml) file with status, location, and calibration information.

## Quick Reference

### Essential Tools for Assembly

**Hand Tools:**
- Torque wrench (0-30 Nm) - Required for critical fasteners
- Metric hex key set (1.5-10mm)
- Precision screwdriver set

**Electronics Tools:**
- Digital multimeter
- Soldering station
- Wire stripper/crimper

**Measurement Tools:**
- Digital caliper (0-150mm)
- Tape measure

## Tool Categories

### 🔧 Hand Tools
Basic mechanical tools for assembly and maintenance.

| Tool | Location | Status | Notes |
|------|----------|--------|-------|
| Torque Wrench (0-30 Nm) | Tool Cabinet A | Available | Required for powertrain |
| Metric Hex Key Set | Tool Cabinet A | Available | 1.5-10mm range |
| Precision Screwdriver Set | Tool Cabinet A | Available | For electronics |

### ⚡ Electronics Tools
Specialized tools for electrical work and debugging.

| Tool | Location | Status | Notes |
|------|----------|--------|-------|
| Digital Multimeter | Electronics Bench | Available | Voltage, current, resistance |
| Soldering Station | Electronics Bench | Available | 60W, temp controlled |
| Wire Stripper/Crimper | Electronics Bench | Available | 10-24 AWG |
| USB-CAN Adapter | Electronics Bench | Available | For CAN bus diagnostics |

### 🔨 Power Tools
Power tools for drilling, cutting, and grinding.

| Tool | Location | Status | Safety Requirements |
|------|----------|--------|---------------------|
| Cordless Drill (18V) | Tool Cabinet B | Available | Safety glasses |
| Angle Grinder (115mm) | Tool Cabinet B | Available | **Training required, PPE** |

!!! warning "Power Tool Safety"
    Power tools require proper training before first use. Always wear appropriate PPE:
    - Safety glasses (mandatory)
    - Gloves
    - Hearing protection (for angle grinder)

### 📏 Measuring Tools
Precision measurement equipment.

| Tool | Location | Accuracy | Calibration Status |
|------|----------|----------|-------------------|
| Digital Caliper | Tool Cabinet A | ±0.02mm | Needs yearly calibration |
| Tape Measure (5m) | Tool Cabinet A | N/A | No calibration needed |

### 🔬 Specialized Equipment
Advanced diagnostic and charging equipment.

| Equipment | Location | Purpose |
|-----------|----------|---------|
| Smart Battery Charger | Battery Station | 12V/24V charging |
| USB-CAN Adapter | Electronics Bench | CAN bus diagnostics |

## Calibration Schedule

Tools requiring periodic calibration:

| Tool | Frequency | Last Calibrated | Next Due |
|------|-----------|-----------------|----------|
| Torque Wrench (0-30 Nm) | Yearly | TBD | TBD |
| Digital Multimeter | Yearly | TBD | TBD |
| Digital Caliper | Yearly | TBD | TBD |

!!! note "Calibration Tracking"
    Update calibration dates in [`tools.yaml`](tools.yaml) after each calibration service.

## Maintenance Schedule

### Weekly
- ✓ Check torque wrench calibration sticker
- ✓ Inspect power tool batteries
- ✓ Clean soldering iron tip

### Monthly
- ✓ Organize tool cabinets
- ✓ Verify all tools present
- ✓ Lubricate moving parts on hand tools

### Yearly
- ✓ Calibrate precision tools (torque wrench, multimeter, caliper)
- ✓ Replace soldering iron tips
- ✓ Service power tools

## Safety Guidelines

!!! danger "Safety First"
    **Always follow these safety rules:**

    - Wear appropriate PPE (safety glasses mandatory)
    - Ensure workspace is well-ventilated when soldering
    - Keep power tools unplugged when changing accessories
    - Never bypass safety guards on power tools
    - Store tools properly after use
    - Report damaged or malfunctioning tools immediately
    - Complete training before using power tools

## Tool Locations

**Tool Cabinet A** (Hand Tools & Measurement)
- Torque wrench
- Hex key set
- Screwdriver set
- Digital caliper
- Tape measure

**Tool Cabinet B** (Power Tools)
- Cordless drill + batteries
- Angle grinder

**Electronics Bench**
- Multimeter
- Soldering station
- Wire stripper/crimper
- USB-CAN adapter

**Battery Charging Station**
- Smart battery charger

## Procurement List

### Needed Tools
These tools would significantly improve our capabilities:

- [ ] **Oscilloscope** - For electronics debugging and signal analysis
- [ ] **3D Printer** - For custom parts and prototyping
- [ ] **Laser Cutter** - For precision metal fabrication
- [ ] **Dedicated Workbench with Vise** - Stable work surface

### Consumables to Stock
Regularly used supplies to keep on hand:

- Solder wire (lead-free)
- Heat shrink tubing (various sizes: 3mm, 6mm, 10mm)
- Cable ties (various sizes)
- Electrical tape
- Loctite threadlocker (blue 243 and red 271)
- Dielectric grease
- Contact cleaner spray
- Isopropyl alcohol (99%)

## Reporting Issues

If you encounter any issues with tools:

1. **Mark tool as "needs_repair"** in `tools.yaml`
2. **Tag with issue description** in the notes
3. **Notify team** via appropriate channel
4. **Do not use damaged tools**

---

*For the complete tool specifications and detailed tracking, see [`tools.yaml`](tools.yaml)*
