# Packages

Detailed reference for each package in the workspace: what it does, its nodes, topics, and parameters.

## kart_perception

**Type:** Python (`ament_python`)
**Purpose:** Detect cones in camera images and compute their 3D positions.

This package contains the full perception pipeline: YOLO-based 2D detection, depth-based 3D projection, and RViz visualization. It works with both the real ZED camera and simulated Gazebo camera.

### Nodes

#### `yolo_detector`

Runs YOLOv11 inference on RGB images to detect cones.

| | |
|---|---|
| **Subscribes** | Image topic (default `/zed/zed_node/rgb/image_rect_color`) |
| **Publishes** | `/perception/cones_2d` (`Detection2DArray`) |
| | `/perception/yolo/annotated` (`Image` — debug view with bounding boxes) |

| Parameter | Default | Description |
|---|---|---|
| `model_path` | `models/perception/yolo/nava_yolov11_2026_02.pt` | Path to YOLO weights |
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
**Purpose:** Convert gamepad (joystick) input to Twist velocity commands for manual driving.

| | |
|---|---|
| **Subscribes** | `/joy` (`sensor_msgs/Joy`) |
| **Publishes** | `/kart/cmd_vel` (`geometry_msgs/Twist`) |

### Gamepad Mapping

| Input | Control | Notes |
|---|---|---|
| R2 (axis 4) | Throttle | Normalized 0–1 |
| L2 (axis 3) | Brake | Normalized 0–1 |
| Left stick horizontal (axis 0) | Steering | Inverted: positive = right |
| R1 (button 5) | Enable | Must be held — releases to zero output (deadman switch) |

`linear.x` is computed as `throttle - brake` (range [-1, 1]). `angular.z` carries the steering angle in radians.

---

## kb_coms_micro

**Type:** C++ (`ament_cmake`)
**Purpose:** Bidirectional serial bridge between ROS 2 and the Kart Medulla (ESP32 microcontroller) over UART.

The node is **payload-agnostic** — it forwards raw bytes between ROS 2 `Frame` messages and the UART wire protocol without interpreting the payload contents.

| | |
|---|---|
| **Subscribes** | `/esp32/tx` (`kb_interfaces/Frame`) — messages to send to ESP32 |
| **Publishes** | `/esp32/rx` (`kb_interfaces/Frame`) — messages received from ESP32 |
| **Serial port** | `/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0` |

### Wire Protocol

Each frame on the UART:

```
+------+-----+------+---------+------+
| SOF  | LEN | TYPE | PAYLOAD | CRC  |
+------+-----+------+---------+------+
  1B     1B    1B      N B      1B
```

| Field | Size | Description |
|---|---|---|
| SOF | 1 byte | Start-of-frame marker: `0xAA` |
| LEN | 1 byte | Payload length (0–251) |
| TYPE | 1 byte | Message type (see table below) |
| PAYLOAD | N bytes | **Protobuf-encoded** message (nanopb on ESP32, standard protobuf on Orin) |
| CRC | 1 byte | CRC-8 (polynomial `0x07`) over LEN + TYPE + PAYLOAD |

UART: 115200 baud, 8N1. Max frame size: 255 bytes.

### Message Types

All message schemas are defined in `proto/kart_msgs.proto` and auto-generated for both Python and C.

**ESP32 → Orin (telemetry, 0x01–0x1F):**

| Type | Name | Protobuf Message | Fields |
|---|---|---|---|
| `0x01` | `ESP_ACT_SPEED` | `ActSpeed` | `float speed_mps` |
| `0x02` | `ESP_ACT_ACCELERATION` | `ActAcceleration` | `float lateral_mps2, longitudinal_mps2` |
| `0x03` | `ESP_ACT_BRAKING` | `ActBraking` | `float effort` |
| `0x04` | `ESP_ACT_STEERING` | `ActSteering` | `float angle_rad, uint32 raw_encoder` |
| `0x08` | `ESP_HEARTBEAT` | `Heartbeat` | `uint32 uptime_ms` |
| `0x0B` | `ESP_HEALTH_STATUS` | `HealthStatus` | `bool magnet_ok, i2c_ok, heap_ok; uint32 agc, heap_kb, i2c_errors` |

**Orin → ESP32 (commands, 0x20–0x3F):**

| Type | Name | Protobuf Message | Fields |
|---|---|---|---|
| `0x20` | `ORIN_TARG_THROTTLE` | `TargThrottle` | `float effort` (0.0–1.0) |
| `0x21` | `ORIN_TARG_BRAKING` | `TargBraking` | `float effort` (0.0–1.0) |
| `0x22` | `ORIN_TARG_STEERING` | `TargSteering` | `float angle_rad` |
| `0x27` | `ORIN_COMPLETE` | `OrinComplete` | `float throttle, braking, steering_rad; uint32 mission, machine_state; bool shutdown` |
| `0x28` | `ORIN_CALIBRATE_STEERING` | `CalibrateSteering` | `uint32 center_offset` |

### Protobuf Schema

The single source of truth is `proto/kart_msgs.proto`. Generated bindings:

- **Python** (Orin): `src/kb_dashboard/kb_dashboard/generated/kart_msgs_pb2.py`
- **C** (ESP32): `proto/generated_c/kart_msgs.pb.{c,h}` (nanopb)

To regenerate after schema changes: `bash proto/generate.sh`

---

## kb_dashboard

**Type:** Python (`ament_python`)
**Purpose:** Web-based dashboard for real-time kart telemetry and mission control.

| | |
|---|---|
| **Subscribes** | `/esp32/rx` (`kb_interfaces/Frame`) — ESP32 telemetry |
| **Publishes** | `/esp32/tx` (`kb_interfaces/Frame`) — commands to ESP32 |
| **Web UI** | `http://<orin-ip>:8080` (WebSocket + HTTP) |

### Features

- Live telemetry: steering angle + raw encoder, speed, acceleration, throttle/brake effort
- Health status: magnet (AGC), I2C bus, free heap
- Heartbeat monitoring with staleness indicator
- Mission selection (Manual, Accel, Skidpad, Autocross, Trackdrive, Inspect)
- Machine state control (Start, Stop, EBS)

### Protocol Layer

All encode/decode logic lives in `protocol.py`, which uses protobuf `SerializeToString()` / `ParseFromString()`. The dashboard decodes ESP32 telemetry frames and encodes command frames using the same `kart_msgs.proto` schema as the ESP32 firmware.

---

## kart_bringup

**Type:** CMake (`ament_cmake`, launch + config only)
**Purpose:** Orchestrate all nodes needed for real hardware and simulation operation.

### Launch Files

**`autonomous.launch.py`** — Full autonomous pipeline (main launcher):

1. **ZED camera** — stereo camera driver (zed2)
2. **Perception** — `yolo_detector` + `cone_depth_localizer` + `cone_marker_viz_3d`
3. **Steering HUD** — overlays cone highlights, steering arrow, and gauge on the annotated image → `/perception/hud`
4. **Cone follower** — autonomous controller (`geometric` by default)
5. **cmd_vel_bridge** — converts `/kart/cmd_vel` to ESP32 Frame commands
6. **KB_Coms_micro** — serial bridge to ESP32
7. **Dashboard** — web UI on port 8080
8. **HUD viewer** — `rqt_image_view` GUI showing `/perception/hud`

**`dashboard.launch.py`** — Minimal/safe mode (no actuation):

1. **KB_Coms_micro** — serial comms only
2. **Dashboard** — web UI on port 8080

Use this for firmware testing — no commands are sent to the kart.

**`teleop_launch.py`** — Manual driving with a gamepad:

1. **`joy_node`** (from `joy` package) — reads gamepad at `/dev/input/js0`
2. **`joy_to_cmd_vel`** — converts joystick axes to Twist on `/kart/cmd_vel`
3. **`cmd_vel_bridge`** — converts Twist to protobuf ESP32 Frame commands
4. **`KB_Coms_micro`** — serial bridge to ESP32

Configuration is in `config/teleop_params.yaml`.

**`sim.launch.py`** — Launches the Gazebo simulation (delegates to `kart_sim/simulation.launch.py`).
