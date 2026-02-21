# Packages

Detailed reference for each package in the workspace: what it does, its nodes, topics, and parameters.

## kart_perception

**Type:** Python (`ament_python`)
**Purpose:** Detect cones in camera images and compute their 3D positions.

This package contains the full perception pipeline: YOLO-based 2D detection, depth-based 3D projection, and RViz visualization. It works with both the real ZED camera and simulated Gazebo camera.

### Nodes

#### `yolo_detector`

Runs YOLOv5 inference on RGB images to detect cones.

| | |
|---|---|
| **Subscribes** | Image topic (default `/zed/zed_node/rgb/image_rect_color`) |
| **Publishes** | `/perception/cones_2d` (`Detection2DArray`) |
| | `/perception/yolo/annotated` (`Image` — debug view with bounding boxes) |

| Parameter | Default | Description |
|---|---|---|
| `model_path` | `models/perception/yolo/best_adri.pt` | Path to YOLOv5 weights |
| `conf_threshold` | 0.25 | Minimum confidence to keep a detection |
| `iou_threshold` | 0.45 | Non-max suppression IoU threshold |
| `imgsz` | 640 | Input image size for inference |
| `device` | `cpu` | PyTorch device (`cpu`, `cuda:0`) |

#### `cone_depth_localizer`

Projects 2D detections into 3D using depth data. Synchronizes three inputs using `ApproximateTimeSynchronizer`.

| | |
|---|---|
| **Subscribes** | `/perception/cones_2d` (`Detection2DArray`) |
| | `/zed/zed_node/depth/depth_registered` (`Image`) |
| | `/zed/zed_node/rgb/camera_info` (`CameraInfo`) |
| **Publishes** | `/perception/cones_3d` (`Detection3DArray`) |

For each 2D detection, it takes the median depth value in a small region around the bounding box center and uses the camera intrinsics to compute the 3D position in the camera frame.

#### `cone_marker_viz_3d`

Converts 3D detections to colored RViz markers (spheres + text labels).

| | |
|---|---|
| **Subscribes** | `/perception/cones_3d` (`Detection3DArray`) |
| **Publishes** | `/perception/cones_3d_markers` (`MarkerArray`) |

Colors: blue → blue, yellow → yellow, orange → orange, large_orange → dark orange.

#### `cone_marker_viz`

Converts 2D detections to RViz markers (cubes + text). Useful for debugging YOLO output without depth.

| | |
|---|---|
| **Subscribes** | `/perception/cones_2d` (`Detection2DArray`) |
| **Publishes** | `/perception/cones_markers` (`MarkerArray`) |

#### `image_source`

Publishes images from a file, directory, or video to an image topic. Useful for testing the YOLO pipeline offline without a camera.

| | |
|---|---|
| **Publishes** | `/image_raw` (`Image`) |

| Parameter | Default | Description |
|---|---|---|
| `source` | (required) | Path to image file, directory, or video |
| `rate` | 10.0 | Publish rate in Hz |
| `loop` | true | Loop back to start when source is exhausted |

### Launch Files

**`perception_3d.launch.py`** — Live/simulation perception pipeline:

- `yolo_detector` + `cone_depth_localizer` + `cone_marker_viz_3d`
- Subscribes to ZED camera topics by default

**`perception_test.launch.py`** — Offline testing:

- `image_source` + `yolo_detector` + `cone_marker_viz` + static TF
- Publishes images from a file and shows 2D detections in RViz

---

## kart_sim

**Type:** CMake (`ament_cmake`) with Python scripts
**Purpose:** Gazebo Fortress simulation environment with ground-truth perception and a simple controller.

### Nodes

#### `perfect_perception_node`

Ground-truth cone detection that bypasses the camera + YOLO pipeline entirely. Reads cone positions directly from the world SDF file and uses odometry to determine which cones are visible.

| | |
|---|---|
| **Subscribes** | `/model/kart/odometry` (`Odometry`) |
| **Publishes** | `/perception/cones_3d` (`Detection3DArray`) |
| | `/tf` (odom → base_link → camera_link) |

| Parameter | Default | Description |
|---|---|---|
| `world_sdf` | (required) | Path to Gazebo world SDF file |
| `kart_start_x` | 20.0 | Kart's initial X position in world frame |
| `kart_start_y` | 0.0 | Kart's initial Y position in world frame |
| `kart_start_yaw` | 1.5708 | Kart's initial heading (radians) |
| `max_range` | 20.0 | Maximum detection range (meters) |
| `fov_deg` | 120.0 | Field of view (degrees) |
| `publish_rate` | 10.0 | Detection publish rate (Hz) |

!!! warning "Start position must match world SDF"
    The `kart_start_x/y/yaw` parameters must match the kart's `<pose>` in `fs_track.sdf`. If they don't, the node will compute wrong world positions and detect zero cones. See the [error log](https://github.com/UM-Driverless/KART_SW) for this past mistake.

#### `cone_follower_node`

Simple autonomous controller that steers toward the midpoint between the nearest blue (left) and yellow (right) cones.

| | |
|---|---|
| **Subscribes** | `/perception/cones_3d` (`Detection3DArray`) |
| **Publishes** | `/kart/cmd_vel` (`Twist`) |

| Parameter | Default | Description |
|---|---|---|
| `max_speed` | 2.0 | Maximum forward speed (m/s) |
| `min_speed` | 0.5 | Minimum speed on sharp turns (m/s) |
| `steering_gain` | 1.5 | Proportional steering gain |

**Algorithm:**

1. Separate cones by class: blue = left boundary, yellow = right boundary
2. Find the nearest blue cone and the nearest yellow cone
3. Compute the midpoint between them
4. Steer toward the midpoint with proportional control: `angular_z = -steering_gain * atan2(midpoint_y, midpoint_x)`
5. Speed = max_speed when driving straight, decreasing to min_speed on sharp turns
6. Safety: if no cones are detected for 1 second, publish zero velocity (stop)

### Models

| Model | Geometry | Dimensions |
|---|---|---|
| `kart` | Box chassis + 4 cylinder wheels | 1.4 x 0.8 x 0.2 m, 80 kg |
| `cone_blue` | Cylinder | r = 0.114 m, h = 0.325 m |
| `cone_yellow` | Cylinder | r = 0.114 m, h = 0.325 m |
| `cone_orange` | Cylinder | r = 0.114 m, h = 0.505 m (taller) |

!!! note "Why cylinders instead of cones?"
    Gazebo Fortress (SDF 1.6) does not support `<cone>` geometry — it silently renders nothing. All cones are modeled as colored cylinders.

### World: `fs_track.sdf`

An oval Formula Student track with 44 cones. See [Simulation](simulation.md) for the full track layout and launch instructions.

---

## joy_to_cmd_vel

**Type:** C++ (`ament_cmake`)
**Purpose:** Convert gamepad (joystick) input to Ackermann steering commands for manual driving.

| | |
|---|---|
| **Subscribes** | `/joy` (`sensor_msgs/Joy`) |
| **Publishes** | `/actuation_cmd` (`ackermann_msgs/AckermannDriveStamped`) |

### Gamepad Mapping

| Input | Control | Notes |
|---|---|---|
| R2 (axis 4) | Throttle | Normalized 0–1 |
| L2 (axis 3) | Brake | Normalized 0–1 |
| Left stick horizontal (axis 0) | Steering | Inverted: positive = right |
| R1 (button 5) | Enable | Must be held — releases to zero output (deadman switch) |

The `acceleration` field is computed as `throttle - brake`, so both can be active simultaneously.

---

## msgs_to_micro

**Type:** C++ (`ament_cmake`)
**Purpose:** Bridge between ROS 2 and the Kart Medulla (ESP32 microcontroller) over UART serial.

| | |
|---|---|
| **Subscribes** | `/actuation_cmd` (`ackermann_msgs/AckermannDriveStamped`) |
| **Output** | 4-byte UART packet at 115200 baud |

### Serial Protocol

Each message is a 4-byte packet:

| Byte | Value | Description |
|---|---|---|
| 0 | `0xAA` | Start/sync byte |
| 1 | `steering_s8` | Signed byte: `steering_angle × 127` |
| 2 | `throttle_u8` | Unsigned byte: `acceleration × 255` (if positive) |
| 3 | `brake_u8` | Unsigned byte: `|acceleration| × 255` (if negative) |

Default serial port: `/dev/ttyUSB0`, 115200 baud, 8N1.

---

## kart_bringup

**Type:** CMake (`ament_cmake`, launch + config only)
**Purpose:** Orchestrate all nodes needed for real hardware operation.

### `teleop_launch.py`

Launches three nodes for manual driving with a gamepad:

1. **`joy_node`** (from `joy` package) — reads gamepad at `/dev/input/js0`
2. **`joy_to_cmd_vel`** — converts joystick axes to Ackermann commands
3. **`comms_micro`** — sends commands to ESP32 over UART

Configuration is in `config/teleop_params.yaml`.
