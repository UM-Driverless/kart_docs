# 2025 — ROS 2

!!! info "Repository"
    [github.com/UM-Driverless/KART_SW](https://github.com/UM-Driverless/KART_SW)

The current autonomous system, built on **ROS 2 Humble** (Ubuntu 22.04). Each component runs as an independent **node** communicating via typed **topics**. This enables isolated testing, hot-swapping of components, and a full simulation workflow with Gazebo.

!!! note "Why ROS 2 Humble?"
    The ROS 2 version is dictated by the NVIDIA Jetson Orin (our onboard computer). JetPack for Orin ships Ubuntu 22.04, and Humble is the ROS 2 LTS release targeting that version.

## File Structure

```
kart_sw/                          # Colcon workspace root
├── src/                          # All packages live here
│   ├── kart_perception/          # Cone detection pipeline (Python)
│   │   ├── kart_perception/      #   Node source files
│   │   │   ├── yolo_detector_node.py
│   │   │   ├── cone_depth_localizer_node.py
│   │   │   ├── cone_marker_viz_node.py
│   │   │   ├── cone_marker_viz_3d_node.py
│   │   │   └── image_source_node.py
│   │   ├── launch/               #   Launch files
│   │   │   ├── perception_3d.launch.py
│   │   │   └── perception_test.launch.py
│   │   ├── models/               #   YOLO weights
│   │   ├── setup.py              #   Python package config
│   │   └── package.xml           #   ROS 2 package manifest
│   │
│   ├── kart_sim/                 # Gazebo simulation (cmake + Python scripts)
│   │   ├── scripts/              #   Node source files
│   │   │   ├── perfect_perception_node.py
│   │   │   └── cone_follower_node.py
│   │   ├── worlds/               #   Gazebo world files
│   │   │   └── fs_track.sdf
│   │   ├── models/               #   SDF models (kart, cones)
│   │   │   ├── kart/
│   │   │   ├── cone_blue/
│   │   │   ├── cone_yellow/
│   │   │   └── cone_orange/
│   │   ├── launch/
│   │   │   └── simulation.launch.py
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── joy_to_cmd_vel/           # Joystick → Ackermann commands (C++)
│   │   └── src/
│   │       └── joy_to_cmd_vel_main.cpp
│   │
│   ├── msgs_to_micro/            # ROS 2 → microcontroller UART bridge (C++)
│   │   ├── include/msgs_to_micro/
│   │   │   └── comms_micro.hpp
│   │   └── src/msgs_to_micro/
│   │       └── comms_micro.cpp
│   │
│   ├── kart_bringup/             # Launch files for real hardware
│   │   ├── launch/
│   │   │   └── teleop_launch.py
│   │   └── config/
│   │       └── teleop_params.yaml
│   │
│   └── ThirdParty/               # External packages
│       ├── rviz_plugin_zed_od/   #   RViz ZED object detection plugin
│       └── zed_display_rviz2/    #   RViz ZED visualization config
│
├── build/                        # Build artifacts (generated)
├── install/                      # Installed packages (generated)
└── log/                          # Build logs (generated)
```

!!! note "ROS 2 workspace convention"
    In ROS 2, a **workspace** is a directory with a `src/` folder containing **packages**. You build with `colcon build` from the workspace root, which populates `build/`, `install/`, and `log/`. Never edit files in those three folders — they're generated from `src/`.

## Packages

| Package | Type | Purpose |
|---|---|---|
| [`kart_perception`](packages.md#kart_perception) | Python | Cone detection: YOLO → depth projection → 3D positions |
| [`kart_sim`](packages.md#kart_sim) | CMake + Python | Gazebo simulation: world, models, ground-truth perception, controller |
| [`joy_to_cmd_vel`](packages.md#joy_to_cmd_vel) | C++ | Converts gamepad input to Ackermann steering commands |
| [`msgs_to_micro`](packages.md#msgs_to_micro) | C++ | Sends Ackermann commands to ESP32 over UART serial |
| [`kart_bringup`](packages.md#kart_bringup) | CMake (launch only) | Launch files that start all nodes for real hardware operation |

## Simulation vs Real Hardware

The system supports two operating modes. The perception and control layers are designed to be **identical** in both — only the data source and actuator output change.

### Simulation (development & testing)

```bash
ros2 launch kart_sim simulation.launch.py
```

- **Data source:** Gazebo Fortress generates camera images, odometry, and physics
- **Perception:** `perfect_perception_node` reads cone positions directly from the world file (ground truth), or optionally the full YOLO pipeline processes simulated camera images
- **Control:** `cone_follower_node` steers the kart via `/kart/cmd_vel` → Gazebo's Ackermann plugin
- **No hardware needed** — runs entirely on the VM

See [Simulation](simulation.md) for full details.

### Real Hardware (on the kart)

```bash
ros2 launch kart_bringup teleop_launch.py          # Manual driving (gamepad)
ros2 launch kart_perception perception_3d.launch.py  # Autonomous perception
```

- **Data source:** ZED stereo camera provides RGB + depth images
- **Perception:** `yolo_detector_node` → `cone_depth_localizer_node` (real YOLO inference on camera frames)
- **Control:** Commands go through `msgs_to_micro` → UART → ESP32 (Kart Medulla) → physical actuators
- **Requires:** ZED camera, gamepad, ESP32 connected via USB

### What's shared between both modes

| Component | Simulation | Real Hardware |
|---|---|---|
| **Perception output** | `/perception/cones_3d` (`Detection3DArray`) | Same topic, same message type |
| **Cone class IDs** | `blue_cone`, `yellow_cone`, `orange_cone`, `large_orange_cone` | Same IDs |
| **Visualization** | `/perception/cones_3d_markers` in RViz | Same |
| **TF tree** | `odom → base_link → camera_link` | Same |

This means a controller node subscribing to `/perception/cones_3d` works identically in both modes — it doesn't know or care whether the detections come from simulation ground truth or real YOLO + depth.

## Build & Run

```bash
# Source ROS 2
source /opt/ros/humble/setup.bash

# Build all packages (always use --symlink-install)
cd ~/kart_brain
colcon build --symlink-install
source install/setup.bash

# Build only one package (faster)
colcon build --symlink-install --packages-select kart_sim

# Run simulation
ros2 launch kart_sim simulation.launch.py

# Run teleop on real hardware
ros2 launch kart_bringup teleop_launch.py
```

!!! tip "One-line launch"
    If you add the ROS 2 and workspace sourcing to `~/.bashrc`, you can launch with a single command. See [Getting Started](getting-started.md).

## Cone Class IDs

These string identifiers must be consistent across all nodes (YOLO labels, perception, control, visualization).

| Class ID | Color | Size (h × base ⌀) | Track meaning |
|---|---|---|---|
| `blue_cone` | Blue | 325 × 228 mm | Left boundary |
| `yellow_cone` | Yellow | 325 × 228 mm | Right boundary |
| `orange_cone` | Orange | 325 × 228 mm | Start/finish zone |
| `large_orange_cone` | Large orange | 505 × 285 mm | Start/finish gate |

Dimensions follow the [FSG Competition Handbook](https://www.formulastudent.de/fsg/rules/). The 3D meshes used in simulation come from [AMZ-Racing/fssim](https://github.com/AMZ-Racing/fssim/tree/master/fssim_gazebo/models) (COLLADA `.dae` files).
