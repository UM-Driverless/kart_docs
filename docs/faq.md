# Frequently Asked Questions

## Emergency Braking System

### Why are you using a pneumatic actuator for the braking system?

If we need a force of 100 kgf at a speed of 0.5 m/s the power requirement is roughly 500 W. An electric actuator capable of that is bulky and hard to source. A cable and pulley system with a motor and pressure feedback was considered, but cables cannot bend sharply. Since we already have a pneumatic piston from our sponsor Festo, it is the simplest solution.

## Battery

### Why is the battery placed at the back?

The rear of the kart offered the most practical space for such a large and heavy component. Because the seat, wheels and pedals remain in their original positions, placing the pack behind the driver was the best compromise. Handling is less of a concern since the kart will usually run autonomously without a driver's weight.

## Motor choice

### Why not use a thermal engine?

A combustion engine would add unnecessary complexity such as fuel, exhaust and cooling. Electric motors require little maintenance and are simpler to control electronically. Since this prototype focuses on sensors, actuators and software, the type of engine does not matter as long as the vehicle moves when throttle is applied.

## Software

### Can I develop on macOS natively instead of the UTM VM?

**Partially.** The 2D simulation and training pipeline (`scripts/sim2d/`) is pure Python (numpy + matplotlib) with zero ROS dependencies — it already runs natively on macOS. This covers GA training, visualization, imitation learning and all controllers.

However, the ROS2 and Gazebo parts (`src/kart_sim/`, `src/kart_perception/`, etc.) require Linux:

- **ROS2 Humble on macOS** is Tier 3 (community/unsupported). Building from source is fragile, breaks often and many packages don't compile on Apple Silicon.
- **Gazebo Fortress** is Linux-only in practice — no macOS packages, and the `ign` CLI and `ros_gz_bridge` won't build.
- **Robostack** (conda ROS2) works for base ROS2 but lacks Gazebo Fortress packages for macOS.
- **Docker on macOS** can run ROS2 but has no GPU passthrough and GUI tools like RViz require painful X11 forwarding.

**Recommendation:** Keep using the UTM VM for ROS2/Gazebo work. Do 2D sim training natively on Mac. The VM overhead only matters for the 3D simulation, which can't run on macOS anyway.

### Why not skip the ESP32 and use the Orin's 40-pin GPIO header directly?

**It could actually work**, and it would simplify the architecture significantly. Here are the trade-offs:

**Pros:**

- **Eliminates the entire serial comms layer** between the Orin and ESP32 — no more serial debugging or protocol mismatches. (The link is USB CDC-ACM on `/dev/ttyACM0`, so baud rate is not actually a constraint.)
- **No more ESP32 flashing or crash loops** — one fewer device to maintain. (The boot-button dance belonged to the retired classic board; the S3 flashes over USB-Serial-JTAG on the same cable.)
- **Faster iteration** — change a Python file, restart the node, done. No cross-compilation or firmware uploads.
- **PID tuning from ROS** — tune parameters with `ros2 param set` or dynamic reconfigure instead of reflashing.
- **The Orin 40-pin header has some of the needed peripherals**: hardware PWM (steering, into the Cytron H-bridge) and general GPIO. It does **not** cover throttle and brake, which are analog — those come from an MCP4922 SPI DAC (0–5 V, and 0–10 V through an op-amp for the brake valve) — and it would struggle with the steering angle, which arrives as a ~994 Hz PWM signal whose *duty cycle* carries the angle. The ESP32 decodes that with a hardware capture peripheral; on Linux, timing edges to the required 244 ns from userspace is exactly the kind of job an MCU exists for. Replacing the ESP32 means moving both problems to the Orin side.

**Cons:**

- **No real-time guarantees.** Linux is not a real-time OS. The ESP32 runs a FreeRTOS task at a fixed rate with no GC pauses or scheduler preemption. On the Orin, PID loop jitter from userspace could cause steering oscillation. This can be mitigated with `SCHED_FIFO` priority and a tight C/Python loop, but it won't match a dedicated MCU.
- **No hardware safety watchdog.** Currently, if the Orin kernel panics or ROS crashes, the ESP32 detects missing heartbeats and kills the motors. With Orin-only, a kernel hang means motors keep running at the last commanded value. This is relevant for Formula Student AS rules (EBS, ASSI).
- **Limited hardware PWM** on the Jetson 40-pin header. Throttle is not PWM anyway (it is an analog DAC output), so the header alone cannot replace the medulla's analog stage.

**Middle-ground approach:** Simplify the ESP32 to a dumb I/O bridge — it receives actuator values over the serial link and applies them directly (no PID on the ESP32). Move the PID loop to a high-priority ROS2 node on the Orin. The ESP32 keeps only two jobs: (1) set PWM outputs, (2) hardware watchdog. This gives you fast iteration on PID tuning while preserving the safety watchdog, with minimal firmware to maintain (~100 lines).
