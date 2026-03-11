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
