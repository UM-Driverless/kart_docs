# 2025 — ROS 2

!!! info "Repository"
    [github.com/UM-Driverless/kart-brain](https://github.com/UM-Driverless/kart-brain) — cloned and built at `~/kart-brain`

The current autonomous system, built on **ROS 2 Humble** (Ubuntu 22.04). Each component runs as an independent **node** communicating via typed **topics**. This enables isolated testing, hot-swapping of components, and a full simulation workflow with Gazebo.

!!! note "Why ROS 2 Humble?"
    The ROS 2 version is dictated by the NVIDIA Jetson Orin (our onboard computer). JetPack for Orin ships Ubuntu 22.04, and Humble is the ROS 2 LTS release targeting that version.

## File Structure

```
kart-brain/                       # Colcon workspace root (~/kart-brain)
├── src/                          # All packages live here
│   ├── kart_perception/          # Cone detection pipeline (Python)
│   │   ├── kart_perception/      #   Node source files
│   │   │   ├── yolo_detector_node.py
│   │   │   ├── cone_depth_localizer_node.py
│   │   │   ├── ground_plane_localizer_node.py
│   │   │   ├── cone_marker_viz_node.py
│   │   │   ├── cone_marker_viz_3d_node.py
│   │   │   ├── steering_hud_node.py
│   │   │   ├── hud_viewer_node.py
│   │   │   └── image_source_node.py
│   │   ├── launch/               #   perception_3d / perception_test
│   │   ├── models/               #   YOLO weights (.pt / .engine)
│   │   ├── setup.py
│   │   └── package.xml
│   │
│   ├── kart_control/             # Controllers, state machine, ESP32 bridge (Python)
│   │   ├── scripts/
│   │   │   ├── cone_follower_node.py     #   geometric/neural/neural_v2/mpc controllers
│   │   │   ├── state_machine_node.py     #   mission + AS-state cmd_vel mux
│   │   │   └── cmd_vel_bridge_node.py    #   Twist → /orin/* Frame commands
│   │   ├── config/
│   │   │   ├── neural_weights.json
│   │   │   └── neural_v2_weights.json
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── kart_sim/                 # Gazebo Fortress simulation (cmake + Python scripts)
│   │   ├── scripts/              #   perfect_perception, esp32_sim, …
│   │   ├── worlds/               #   Gazebo world files
│   │   ├── models/               #   SDF models (kart, cones)
│   │   ├── launch/
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── joy_to_cmd_vel/           # Joystick → Twist commands (C++)
│   │
│   ├── kb_coms_micro/            # ROS 2 ↔ ESP32 UART serial bridge (C++)
│   │   ├── include/kb_coms_micro/
│   │   └── src/
│   │
│   ├── kb_serial_driver_lib/     # Low-level framed-UART driver used by kb_coms_micro (C++)
│   │
│   ├── kb_bms/                   # Smart-BMS reader over Bluetooth LE (Python)
│   │   └── kb_bms/bms_node.py
│   │
│   ├── kb_dashboard/             # Web telemetry + mission-control dashboard (Python)
│   │   └── kb_dashboard/
│   │       ├── dashboard_node.py
│   │       └── protocol.py       #   int32 frame encode/decode helpers
│   │
│   ├── kb_interfaces/            # Custom ROS messages (Frame, …)
│   │
│   ├── kart_bringup/             # Launch files that wire everything together
│   │   ├── launch/               #   launch.py, teleop.launch.py, dashboard.launch.py, …
│   │   └── config/
│   │
│   └── ThirdParty/               # External packages (RViz ZED plugins, etc.)
│
├── tools/sim2d/                  # 2D simulator + autoresearch training loop
├── models/perception/yolo/       # YOLO weight files
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
| [`kart_control`](packages.md#kart_control) | CMake + Python | Cone-follower controllers, state machine, and Twist → ESP32 bridge |
| [`kart_sim`](packages.md#kart_sim) | CMake + Python | Gazebo simulation: world, models, ground-truth perception (the controller is shared from `kart_control`) |
| [`joy_to_cmd_vel`](packages.md#joy_to_cmd_vel) | C++ | Converts gamepad input to Twist velocity commands |
| [`kb_coms_micro`](packages.md#kb_coms_micro) | C++ | Bidirectional UART serial bridge between ROS 2 and the ESP32 |
| [`kb_serial_driver_lib`](packages.md#kb_serial_driver_lib) | C++ | Framed-UART driver library used by `kb_coms_micro` |
| [`kb_bms`](packages.md#kb_bms) | Python | Reads the smart BMS over Bluetooth LE, publishes `BatteryState` ([BMS page](bms.md)) |
| [`kb_dashboard`](packages.md#kb_dashboard) | Python | Web telemetry + mission-control dashboard |
| [`kb_interfaces`](packages.md#kb_interfaces) | CMake (msgs) | Custom ROS message definitions (`Frame`, …) |
| [`kart_bringup`](packages.md#kart_bringup) | CMake (launch only) | Launch files that start all nodes for real hardware and simulation |

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
ros2 launch kart_bringup teleop.launch.py          # Manual driving (gamepad)
ros2 launch kart_perception perception_3d.launch.py  # Autonomous perception
```

- **Data source:** ZED stereo camera provides RGB + depth images
- **Perception:** `yolo_detector_node` → `cone_depth_localizer_node` (real YOLO inference on camera frames)
- **Control:** Commands go through `cmd_vel_bridge` → `kb_coms_micro` → UART → ESP32 (Kart Medulla) → physical actuators
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
cd ~/kart-brain
colcon build --symlink-install
source install/setup.bash

# Build only one package (faster)
colcon build --symlink-install --packages-select kart_sim

# Run simulation
ros2 launch kart_sim simulation.launch.py

# Run teleop on real hardware
ros2 launch kart_bringup teleop.launch.py
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
