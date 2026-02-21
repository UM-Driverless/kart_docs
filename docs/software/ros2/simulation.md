# Simulation

The simulation uses **Gazebo Fortress** running headless on an Ubuntu 22.04 ARM64 VM. It provides a closed-loop environment: simulated world → camera → perception → control → kart movement.

## Quick Start

```bash
source /opt/ros/humble/setup.bash
source ~/kart_sw/install/setup.bash
ros2 launch kart_sim simulation.launch.py
```

This launches 5 processes:

1. **Gazebo server** — headless physics + rendering (OGRE2 on LLVMpipe)
2. **ros_gz_bridge** — bridges Gazebo topics to ROS 2
3. **perfect_perception_node** — ground-truth cone detection (bypasses YOLO)
4. **cone_marker_viz_3d** — RViz marker visualization
5. **cone_follower_node** — midpoint-following controller

## Track Layout

An oval Formula Student track with 44 cones:

- **20 blue cones** — left boundary
- **20 yellow cones** — right boundary
- **4 orange cones** — start/finish zone markers

The kart spawns at position (20, 0) facing +Y (north), at the start/finish straight.

## Visualization

### RViz (on the VM desktop)

```bash
rviz2
```

1. Set **Fixed Frame** to `odom`
2. Add **MarkerArray** → `/perception/cones_3d_markers` (colored cone markers)
3. Add **TF** (kart position + orientation)
4. Add **Odometry** → `/model/kart/odometry` (velocity arrow)

### Foxglove Studio (from Mac, best experience)

```bash
# On the VM
sudo apt install ros-humble-rosbridge-server
ros2 launch rosbridge_server rosbridge_websocket_launch.xml

# On Mac: open Foxglove Studio, connect to ws://192.168.65.2:9090
```

## Kart Model

| Parameter | Value |
|---|---|
| Wheelbase | 1.05 m |
| Track width | 1.2 m |
| Wheel radius | 0.15 m |
| Chassis mass | 80 kg |
| Camera | Front-mounted, 640x360 @ 10 Hz, 80° FOV |
| Max speed | 5 m/s |
| Max steering | 0.5 rad (~29°) |
| Steering | Ackermann (4-wheel, front-steer) |

## Perfect Perception Node

Since YOLO was trained on real cones (not Gazebo cylinders), the simulation uses `perfect_perception_node` by default. It:

- Parses cone world positions from the SDF file
- Transforms kart odometry from spawn-relative to world coordinates
- Filters cones by range (20 m) and field of view (120°)
- Publishes `Detection3DArray` with correct class IDs (`blue_cone`, `yellow_cone`, etc.)
- Broadcasts TF: `odom` → `base_link` → `camera_link`

!!! warning "Odometry offset"
    Gazebo odometry is **relative to the spawn pose**, not world coordinates. The node has `kart_start_x`, `kart_start_y`, `kart_start_yaw` parameters that must match the kart's `<pose>` in the world SDF.

## Cone Follower Controller

A simple midpoint-following algorithm:

1. Separate detected cones by color (blue = left boundary, yellow = right boundary)
2. Find the nearest blue and nearest yellow cone
3. Steer toward the midpoint between them (proportional control)
4. Speed inversely proportional to steering angle (slow down on curves)
5. Safety timeout: publishes zero velocity if no cones detected for 1 second

## Physics Configuration

| Setting | Value | Reason |
|---|---|---|
| Physics engine | ODE | Default, stable |
| Real-time factor | 1.0 | Prevents drift during startup |
| Step size | 0.004 s (250 Hz) | Smooth Ackermann steering |
| Shadows | Disabled | Performance (CPU rendering) |
| Camera rate | 10 Hz | LLVMpipe budget |

## Gazebo Fortress Notes

- CLI is **`ign`**, not `gz` (Fortress uses Ignition-era naming)
- Message types are `ignition.msgs.*`, not `gz.msgs.*`
- **No `<cone>` geometry** — Fortress doesn't support it; cones are modeled as colored cylinders
- Headless rendering via EGL works on ARM64 with LLVMpipe (software GPU)

## Troubleshooting

| Issue | Fix |
|---|---|
| No `/clock` topic | Gazebo not running. Check `ps aux \| grep ign`. |
| Cones detected but kart doesn't move | Check `/kart/cmd_vel` is being published. Bridge might not be running. |
| Kart drifts far before controller starts | Ensure `real_time_factor: 1` in world SDF. |
| `Frame [camera] does not exist` in RViz | Set Fixed Frame to `odom`, not `camera`. The frame is `camera_link`. |
| Black camera images | OGRE2 rendering issue. Try adding `<render_engine>ogre</render_engine>` to Sensors plugin. |
