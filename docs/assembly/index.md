# Assembly

This section contains all the information about the kart, organized as a tree of sub-assemblies. Each sub-assembly includes detailed specifications, components, and relevant documentation.

!!! note "Assembly Instructions"
    Step-by-step assembly instructions are still a work in progress.

## Hardware Overview

| Subsystem | Component | Key Specs | Details |
|---|---|---|---|
| **Chassis** | Tony Kart Extreme | CIK ICA 330/99, 30/32mm CrMo tubing, 40mm rear axle | [Chassis](chassis/index.md) |
| **Computer** | NVIDIA Jetson AGX Orin | 12-core ARM, 62 GB RAM, Ampere GPU (CUDA 12.6), NVMe boot | [Computer](electronics/computer.md), [Orin Setup](electronics/orin-setup.md) |
| **Camera** | ZED 2 stereo | USB 3.0, RGB + depth + IMU, used for cone detection | [Camera](sensors/camera.md) |
| **Microcontroller** | ESP32-S3 "Kart Medulla" | USB serial (CDC-ACM) to Orin, controls actuators | [Kart Medulla](electronics/kart-medulla/index.md) |
| **Steering** | DC motor + H-bridge | MT6701 magnetic angle sensor read as PWM, closed-loop PID on the ESP32 | [Steering](steering/index.md), [H-bridge](steering/h-bridge.md), [Angle Sensor](steering/sensor/index.md) |
| **Throttle** | MCP4922 SPI DAC → motor controller | 0–5 V analog signal | [Throttle Pedal](powertrain/throttle-pedal.md) |
| **Motor** | Electric kart motor | Controlled via motor controller + throttle signal | [Motor](powertrain/motor.md) |
| **Power** | Battery pack | Supplies 12V to Orin (via barrel jack 9–20V) + motor controller | [Battery](electronics/power/battery.md) |
| **Pneumatic braking** | ASB (proportional) + EBS (emergency) | VPPM + solenoid valve merged by an OR valve; EBS in shutdown circuit | [Pneumatic Braking](pneumatic-braking/index.md) |
| **Hydraulic braking** | Kart's original hydraulic circuit | M10×1.0 inverted-flare hoses, Sensata PTE7100 pressure sensor (0–200 bar) | [Hydraulics](hydraulics/index.md) |
| **Wiring** | Custom harness | Color-coded: black=GND, red=12V, orange=5V, yellow=3.3V | [Wiring](electronics/wiring.md), [Net Naming](electronics/net-naming.md) |

The two braking systems are not alternatives: the pneumatic side is what the autonomous stack and
the emergency circuit actuate, and it pushes on the kart's existing hydraulic brakes.

## Loose assembly notes

Things learned on the kart that have no better home yet. Move each one onto its subsystem page as
that page grows.

- The red plastic piece of the steering column goes on top of the bolt that holds it.
- The wheel bearings are separated by a spacer tube, so the bolts can be torqued down without
  putting a constant shear load on the bearings. **Its dimensions are not recorded** — measure the
  ID, OD and length off the kart and fill them in here.