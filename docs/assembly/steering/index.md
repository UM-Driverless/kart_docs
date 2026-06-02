
# Steering System

## Mechanical Overview

??? example "View steering mechanism with measurements"
    ![Steering mechanism with dimensions](images/steering-mechanism.jpg)

The steering system uses a salvaged DC motor geared down to the steering column through a ~11:1 reducer. Key dimensions:
- Steering column diameter: 20mm
- Motor mount spacing: 50mm
- Connection diameter: 10mm (internal)

## CAD

!!! todo "Steering assembly CAD"
    Fusion model of the full steering assembly (motor mount, reducer, column coupling) to be embedded here — add a Fusion 360 **Share → Public link** as an Autodesk Viewer iframe + a STEP download. Reducer-specific CAD is on the [Reducer](reducer.md#cad) page.

## Motor Data
![Motor specifications](index/20250622200050.png)

24 V geared DC motor (salvaged), driven from the battery through the Cytron H-bridge with PWM. At stall it pulls 47 V × 43 A ≈ 2 kW; normal steering work is only ~47 W (see sizing below).

## Main process
We need to move the steering shaft to the target angle.

1. Micro controller reads target position from main computer (Orin) and current position from the Hall effect sensor
    - Micro controller may be a Blue Pill, Teensy 4.0, or one with CAN transceiver builtin.
2. Calculates PWM % value with PID. Sends PWM 3.3V to H-bridge
3. H-bridge (MD25HV) receives PWM and powers the DC motor
    - The MD25HV accepts control voltages from 1.8V-30V, so 3.3V PWM from ESP32 works perfectly
    - [Datasheet](https://docs.google.com/document/d/1xJHVG2dc3aEtedCHf3L9NzUy5KqpxeWjeS9Lfh9XuqA)

## H-bridge data
See [H-bridge](h-bridge.md) for more details.

## Sizing the actuator

What the steering needs, all measured at the steering column (after the 11:1 reduction). Figures from experience with the built actuator.

**Torque.** Turning the stopped wheels takes ~4 Nm to break the tyres loose; we size for **~8 Nm** with margin — the figure specified to Maxon in the 2025-01-07 YEP application.

**Speed.** The wheels swing ~±25° (≈50° lock-to-lock). The current motor sweeps that side to side in ~0.15 s on the ground, faster with the wheels lifted — about 6 rad/s (~56 rpm).

**Power** = torque × speed = 8 Nm × 6 rad/s ≈ **47 W**.

Power is never the constraint here. The 13S pack (~48 V) through the Cytron driver supplies far more than 47 W; at stall the motor pulls 47 V × 43 A ≈ 2 kW, nearly all of it heat. What the 11:1 reduction buys is torque — it trades the motor's cheap speed for the ~8 Nm the column needs, so the motor isn't sitting near stall (and overheating) just to hold an angle.

Off-the-shelf motors considered (none adopted) are listed under [steering motor options](motor-options.md).

### Design Constraints
- **Available voltages**:
  - Battery: 13S (41.6V - 54.6V)
  - Regulated: 12V, 5V, 3.3V
- **Budget**: < 1000€ for new components
- **Note**: Consider integrated servos as an alternative to separate electronics

### Power Alternatives Under Investigation

??? info "Motor Driver Alternatives (Click to expand)"

    #### VESC (Vedder Electronic Speed Controller)
    - **Advantages**: Multi-purpose, can be reused for other systems
    - **Implementation**:
        - Test with existing unit first
        - ESP32 communication via UART at 3.3V
        - Keep AS5600 magnetic sensor on I2C
        - Note: VESC DC mode doesn't include position control, external PID needed
    - **Alternative unit**: [Flysky FSESC67100 V2 Pro on Wallapop](https://es.wallapop.com/item/flysky-fsesc67100-v2-pro-1133224964)

    #### Kelly Controller KDS Series
    - **Link**: [Kelly Controller Shop](https://kellycontroller.com/shop/kds/)
    - **Specs**: ~60€, 48V (max 60V), 50A
    - **Control**:
        - 0-5V analog signal for power
        - REV/DIR signal for direction
        - Requires external microcontroller with PID for position control

    #### AllMotion EZSV23WV Servo Controller
    - **Link**: [AllMotion EZSV23WV](https://www.allmotion.com/ezsv23wv-servo-control)
    - Integrated servo control solution

    #### Generic PWM Motor Controller
    - **Link**: [Component Authority DC Motor Controller](https://componentauthority.com/products/dc-10-55v-max-60a-pwm-motor-speed-controller-cw-ccw-reversible-12v-24v-36v)
    - **Specs**: 10-55V DC, Max 60A, CW/CCW reversible
    - Works like current Cytron solution
    - Use with ESP32 for same control method

    #### Decision Matrix
    *To be completed once alternatives are evaluated*

## Reducer & alternative designs

The motor's speed is geared down to torque through a **~11:1 two-stage reducer** (a 3D-printed planetary + an output gear pair). The design, the gear-material saga (PLA → nylon → PPA-CF → steel), and the failure modes are on the **[Reducer](reducer.md)** page.

The other reducer types we weighed — cycloidal, folded compound gear train, worm, harmonic, belt — and the two we're keeping as live alternatives to print and test, are on **[Alternative reducer designs](alternatives/index.md)**.
