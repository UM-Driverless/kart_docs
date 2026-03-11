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

### Real Hardware Mode (Autonomous)

```
┌──────────┐
│ ZED 2    │── RGB + Depth + CameraInfo
│ Camera   │
└──────┬───┘
       │
       ▼
┌──────────────────┐     /perception/     ┌──────────────────────┐
│ yolo_detector    │──── cones_2d ──────►│ cone_depth_localizer  │
│ (YOLOv11,PyTorch)│                      │ (2D → 3D projection) │
└────────┬─────────┘                      └──────────┬───────────┘
         │                                           │
  /perception/yolo/                       /perception/cones_3d
     annotated                                       │
         │                                           ▼
         ▼                                ┌─────────────────────┐
┌──────────────────┐                      │ cone_follower       │
│ steering_hud     │                      │ (geometric/neural)  │
│ (overlay + gauge)│                      └──────────┬──────────┘
└────────┬─────────┘                                 │
         │                                    /kart/cmd_vel
  /perception/hud                                    │
         │                                           ▼
         ▼                                ┌─────────────────────┐
┌──────────────────┐                      │ cmd_vel_bridge      │
│ rqt_image_view   │                      │ (Twist → Frame)     │
│ (GUI window)     │                      └──────────┬──────────┘
└──────────────────┘                                 │
                                              /esp32/tx (Frame)
                                                     │
                                                     ▼
┌──────────────────┐    /esp32/rx    ┌───────────────────────┐    UART     ┌────────────┐
│ kb_dashboard     │◄───(Frame)─────│ KB_Coms_micro         │◄──────────►│ ESP32      │
│ (web UI :8080)   │────(Frame)────►│ (serial bridge)       │  115200    │ (Medulla)  │
└──────────────────┘    /esp32/tx    └───────────────────────┘  protobuf  └────────────┘
```

### Real Hardware Mode (Teleop)

```
┌──────────┐          ┌──────────────────┐              ┌─────────────────┐
│ Gamepad  │──/joy──►│ joy_to_cmd_vel    │─/kart/cmd_vel─►│ cmd_vel_bridge  │
└──────────┘          └──────────────────┘              └────────┬────────┘
                                                                │
                                                         /orin/* (Frame)
                                                                │
                                                                ▼
                                               ┌───────────────────────┐    UART     ┌────────────┐
                                               │ KB_Coms_micro         │───────────►│ ESP32      │
                                               │ (serial bridge)       │  115200    │ (Medulla)  │
                                               └───────────────────────┘  protobuf  └────────────┘
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
| `/perception/yolo/annotated` | `sensor_msgs/Image` | `yolo_detector` | `steering_hud`, RViz (debug) |
| `/perception/hud` | `sensor_msgs/Image` | `steering_hud` | `rqt_image_view` |

### Real Hardware Topics

| Topic | Message Type | Publisher | Subscriber |
|---|---|---|---|
| `/joy` | `sensor_msgs/Joy` | `joy_node` | `joy_to_cmd_vel` |
| `/kart/cmd_vel` | `geometry_msgs/Twist` | `cone_follower`, `joy_to_cmd_vel` | `cmd_vel_bridge`, `steering_hud` |
| `/esp32/tx` | `kb_interfaces/Frame` | `cmd_vel_bridge` / `kb_dashboard` | `KB_Coms_micro` |
| `/esp32/rx` | `kb_interfaces/Frame` | `KB_Coms_micro` | `kb_dashboard` |
| `/perception/hud` | `sensor_msgs/Image` | `steering_hud` | `rqt_image_view` |

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
5. **Act** — `Twist` sent to Gazebo via `ackermann_to_vel` (sim) or protobuf-encoded Frame sent to ESP32 via `KB_Coms_micro` (real)
6. **Feedback** — ESP32 sends telemetry (steering angle, health, heartbeat) back to the dashboard via protobuf frames
