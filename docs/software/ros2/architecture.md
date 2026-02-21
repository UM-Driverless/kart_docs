# Architecture

## Operating Modes

The system has two modes that share the same perception interface (`/perception/cones_3d`). A controller node doesn't know whether it's running in simulation or on real hardware.

### Simulation Mode

```
┌──────────────────────────────────────────────────────────────┐
│  Gazebo Fortress (headless)                                  │
│                                                              │
│  Physics (ODE) ──► Ackermann steering ──► Odometry           │
│                         ▲                    │               │
│                         │                    │               │
│  RGBD Camera (10Hz) ────│────────────────────│───────────    │
└─────────────────────────│────────────────────│───────────────┘
                          │             ros_gz_bridge
                   /kart/cmd_vel               │
                          │                    ▼
                          │         /model/kart/odometry
                          │                    │
                          │                    ▼
                          │         ┌─────────────────────┐
                          │         │ perfect_perception   │
                          │         │ (reads SDF + odom)   │
                          │         └──────────┬──────────┘
                          │                    │
                          │        /perception/cones_3d
                          │                    │
                          │                    ▼
                          │         ┌─────────────────────┐
                          └─────────│ cone_follower        │
                                    │ (midpoint steering)  │
                                    └─────────────────────┘
```

### Real Hardware Mode

```
┌──────────┐          ┌──────────────────────────────────────┐
│ Gamepad  │──/joy──►│ joy_to_cmd_vel                        │
└──────────┘          └───────────┬──────────────────────────┘
                                  │
                          /actuation_cmd
                                  │
                                  ▼
                      ┌───────────────────────┐     UART      ┌────────────┐
                      │ msgs_to_micro         │──────────────►│ ESP32      │
                      │ (Ackermann → 4 bytes) │  115200 baud  │ (Medulla)  │
                      └───────────────────────┘               └────────────┘


┌──────────┐
│ ZED      │── RGB + Depth + CameraInfo
│ Camera   │
└──────┬───┘
       │
       ▼
┌──────────────────┐     /perception/     ┌──────────────────────┐
│ yolo_detector    │──── cones_2d ──────►│ cone_depth_localizer  │
│ (YOLOv5, PyTorch)│                      │ (2D → 3D projection) │
└──────────────────┘                      └──────────┬───────────┘
                                                     │
                                          /perception/cones_3d
                                                     │
                                                     ▼
                                          ┌─────────────────────┐
                                          │ controller node     │
                                          │ (to be developed)   │
                                          └─────────────────────┘
```

## Topic Map

### Simulation Topics

| Topic | Message Type | Publisher | Subscriber |
|---|---|---|---|
| `/clock` | `rosgraph_msgs/Clock` | Gazebo (bridged) | All nodes (`use_sim_time`) |
| `/model/kart/odometry` | `nav_msgs/Odometry` | Gazebo (bridged) | `perfect_perception` |
| `/kart/cmd_vel` | `geometry_msgs/Twist` | `cone_follower` | Gazebo (bridged) |
| `/zed/.../rgb/image_rect_color` | `sensor_msgs/Image` | Gazebo camera (bridged + remapped) | `yolo_detector` |
| `/zed/.../depth/depth_registered` | `sensor_msgs/Image` | Gazebo camera (bridged + remapped) | `cone_depth_localizer` |
| `/zed/.../rgb/camera_info` | `sensor_msgs/CameraInfo` | Gazebo camera (bridged + remapped) | `cone_depth_localizer` |

### Perception Topics (shared)

| Topic | Message Type | Publisher | Subscriber |
|---|---|---|---|
| `/perception/cones_2d` | `vision_msgs/Detection2DArray` | `yolo_detector` | `cone_depth_localizer` |
| `/perception/cones_3d` | `vision_msgs/Detection3DArray` | `cone_depth_localizer` or `perfect_perception` | Controller, `cone_marker_viz_3d` |
| `/perception/cones_3d_markers` | `visualization_msgs/MarkerArray` | `cone_marker_viz_3d` | RViz |
| `/perception/yolo/annotated` | `sensor_msgs/Image` | `yolo_detector` | RViz (debug) |

### Real Hardware Topics

| Topic | Message Type | Publisher | Subscriber |
|---|---|---|---|
| `/joy` | `sensor_msgs/Joy` | `joy_node` | `joy_to_cmd_vel` |
| `/actuation_cmd` | `ackermann_msgs/AckermannDriveStamped` | `joy_to_cmd_vel` | `comms_micro` |

## TF Frame Tree

```
odom
 └── base_link              (kart chassis center)
      └── camera_link       (front-mounted camera)
```

- In simulation: `perfect_perception_node` broadcasts all transforms from odometry
- On real hardware: the ZED ROS wrapper and `robot_state_publisher` handle TF

## Message Flow

The autonomous driving loop, whether in simulation or on real hardware, follows these steps:

1. **Sense** — Camera (real ZED or simulated Gazebo) produces RGB + depth images
2. **Detect** — YOLO finds 2D cone bounding boxes, or `perfect_perception` uses ground truth
3. **Localize** — Depth image projects 2D boxes into 3D positions in camera frame
4. **Decide** — Controller separates blue (left) and yellow (right) cones, computes steering target
5. **Act** — `Twist` sent to Gazebo's Ackermann plugin (sim) or `AckermannDriveStamped` sent to ESP32 (real)
