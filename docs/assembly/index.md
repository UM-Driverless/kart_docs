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
| **Microcontroller** | ESP32 "Kart Medulla" | UART 115200 baud to Orin, controls actuators | [Kart Medulla](electronics/kart-medulla/index.md) |
| **Steering** | DC motor + H-bridge | Analog position sensor, closed-loop control on ESP32 | [Steering](steering/index.md), [H-bridge](steering/h-bridge.md) |
| **Throttle** | DAC → motor controller | 0–3.3V analog signal (66% max until 5V DAC available) | [Throttle Pedal](powertrain/throttle-pedal.md) |
| **Motor** | Electric kart motor | Controlled via motor controller + throttle signal | [Motor](powertrain/motor.md) |
| **Power** | Battery pack | Supplies 12V to Orin (via barrel jack 9–20V) + motor controller | [Battery](electronics/power/battery.md) |
| **Pneumatic braking** | ASB (proportional) + EBS (emergency) | VPPM + solenoid valve merged by an OR valve; EBS in shutdown circuit | [Pneumatic Braking](pneumatic-braking/index.md) |
| **Wiring** | Custom harness | Color-coded: black=GND, red=12V, orange=5V, yellow=3.3V | [Wiring](electronics/wiring.md), [Net Naming](electronics/net-naming.md) |

## Notes

- The red plastic piece of the steering column goes on top of the bolt that holds it
- The bearings on the wheels are separated with tube of ? ID x ? OD x ? length to allow compressing them with the bolts without applying constant shear force on the bearings
- ...