# Getting Started

## Prerequisites

The software runs on **Ubuntu 22.04** with **ROS 2 Humble**. For development, we use a UTM virtual machine on macOS, but any Ubuntu 22.04 machine (native, WSL2, or VM) works.

### Install ROS 2 Humble

Follow the [official installation guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html). Install the desktop variant:

```bash
sudo apt install ros-humble-desktop
```

### Install Dependencies

```bash
sudo apt install \
  ros-humble-ros-gz \
  ros-humble-vision-msgs \
  ros-humble-xacro \
  ros-humble-tf2-ros \
  ros-humble-joy \
  ros-humble-ackermann-msgs \
  mesa-utils libegl1-mesa-dev libgles2-mesa-dev
```

`ros-humble-ros-gz` installs Gazebo Fortress and the ROS bridge (~3–4 GB).

## Clone & Build

```bash
# Clone the repository
cd ~
git clone https://github.com/UM-Driverless/KART_SW.git kart_sw

# Build
source /opt/ros/humble/setup.bash
cd ~/kart_sw
colcon build
source install/setup.bash
```

!!! tip "Add to `.bashrc` for convenience"
    ```bash
    echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
    echo 'source ~/kart_sw/install/setup.bash 2>/dev/null' >> ~/.bashrc
    echo 'export IGN_GAZEBO_RESOURCE_PATH=$(ros2 pkg prefix kart_sim 2>/dev/null)/share/kart_sim/models' >> ~/.bashrc
    ```
    After this, you can launch the simulation with a single command from any terminal.

## Run the Simulation

```bash
ros2 launch kart_sim simulation.launch.py
```

This starts Gazebo (headless), the topic bridge, ground-truth perception, visualization markers, and the cone-following controller. The kart will start driving around the oval track autonomously.

### Verify it's working

In a second terminal:

```bash
# Check topics are active
ros2 topic list

# See cone detections
ros2 topic echo /perception/cones_3d --once

# See controller output
ros2 topic echo /kart/cmd_vel --once
```

### Visualize in RViz

```bash
rviz2
```

1. Set **Fixed Frame** to `odom`
2. Add **MarkerArray** → `/perception/cones_3d_markers`
3. Add **TF** to see the kart's position
4. Add **Odometry** → `/model/kart/odometry` for velocity arrows

See [Simulation](simulation.md) for more visualization options (Foxglove Studio, Gazebo GUI).

## Run on Real Hardware

### Manual Driving (Teleop)

Connect a gamepad and the ESP32 via USB, then:

```bash
ros2 launch kart_bringup teleop_launch.py
```

Hold **R1** (deadman switch) and use **R2** for throttle, **L2** for brake, **left stick** for steering.

### Autonomous Perception

With the ZED camera connected:

```bash
ros2 launch kart_perception perception_3d.launch.py
```

This starts YOLO detection, depth-based 3D localization, and RViz visualization.

## Rebuilding After Changes

```bash
# Rebuild everything
cd ~/kart_sw && colcon build && source install/setup.bash

# Rebuild only the package you changed (faster)
colcon build --packages-select kart_sim && source install/setup.bash
```

!!! warning "Always re-source after building"
    After `colcon build`, you must run `source install/setup.bash` for the changes to take effect in your current terminal. New terminals that source it from `.bashrc` will pick it up automatically.

## Useful Commands

```bash
# List all active topics
ros2 topic list

# See message rate
ros2 topic hz /perception/cones_3d

# Echo a topic (one message)
ros2 topic echo /kart/cmd_vel --once

# Publish a manual velocity command
ros2 topic pub /kart/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0}, angular: {z: 0.0}}" -r 10

# List running nodes
ros2 node list

# Stop the simulation
pkill -9 ign; pkill -f parameter_bridge; pkill -f perfect_perception; pkill -f cone_follower
```
