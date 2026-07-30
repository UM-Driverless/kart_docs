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
| `weights_path` | `models/perception/yolo/ruben_yolov11n_2026_03_320.engine` | Path to YOLO weights (`.pt` or TensorRT `.engine`) |
| `conf_threshold` | 0.25 | Minimum confidence to keep a detection |
| `iou_threshold` | 0.45 | Non-max suppression IoU threshold |
| `imgsz` | 640 | Input image size for inference |
| `device` | `cpu` | PyTorch device (`cpu`, `cuda:0`) |

!!! note "YOLO version"
    The current model is **YOLOv11** (Ultralytics backend, loads `.pt` or TensorRT `.engine` weights). The default weights above are the node's own default; the launch files override it — `perception_3d.launch.py` defaults to `ruben_yolov11n_2026_03_320_orin_trt10.engine` (TensorRT, for the Orin), and `perception_test.launch.py` to `ruben_yolov11n_2026_03.pt` (portable). The older YOLOv5 model (`best_adri.pt`) was the 2024 stack and is no longer the default.

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
**Purpose:** Gazebo Fortress simulation environment with ground-truth perception and a simulated ESP32. The autonomous controller itself lives in [`kart_control`](#kart_control) and is shared with real hardware.

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
    The `kart_start_x/y/yaw` parameters must match the kart's `<pose>` in `fs_track.sdf`. If they don't, the node will compute wrong world positions and detect zero cones. See the [error log](https://github.com/UM-Driverless/kart-brain) for this past mistake.

#### `esp32_sim_node`

Stands in for the real ESP32 during simulation. It emulates the actuation feedback the firmware would send (steering angle, speed, etc.) so the dashboard and any feedback-dependent logic behave the same as on the kart. Other helper scripts in `kart_sim/scripts/` include `ackermann_to_vel.py` (Twist → Gazebo Ackermann), `camera_info_fix_node.py` (corrects Gazebo's camera intrinsics), and `ign_cmd_relay.py`.

!!! note "Where is the controller?"
    The autonomous cone-following controller (`cone_follower_node`) used in simulation is the **same** node used on real hardware. It lives in [`kart_control`](#kart_control), not `kart_sim`, so simulation and the kart run identical control code.

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

## kart_control

**Type:** CMake (`ament_cmake`) with Python scripts
**Purpose:** The kart's control layer — the autonomous cone-following controller, the mission/AS-state machine, and the bridge that turns velocity commands into ESP32 frames. All three nodes are shared between simulation and real hardware.

Installed nodes (`src/kart_control/scripts/`): `cone_follower_node.py`, `state_machine_node.py`, `cmd_vel_bridge_node.py`.

### `cone_follower_node`

The autonomous controller. It subscribes to 3D cone detections and publishes a `Twist` steering + speed command. It supports several interchangeable steering and speed controllers, selected at runtime by parameter.

| | |
|---|---|
| **Subscribes** | `/perception/cones_3d` (`Detection3DArray`) |
| **Publishes** | `/kart/cmd_vel` (`Twist`) |

Cone positions arrive in the camera optical frame (Z = forward, X = right, Y = down).

#### Steering controllers (`controller_type` param)

| `controller_type` | Description |
|---|---|
| `geometric` (default) | Nearest blue/yellow midpoint → `atan2` → steer. Six tunable params. |
| `pure_pursuit` | Pure-pursuit geometry toward a lookahead point on the midpoint path. |
| `neural` | Small feed-forward net (8 → 8 → 2), 90 weights. Loads `config/neural_weights.json`. |
| `neural_v2` | Larger net (17 → 16 → 2): 4 cones per side + speed feedback, 322 weights. Trained for lap-time. Loads `config/neural_v2_weights.json`. |
| `mpc` | Kinematic-bicycle-model MPC. Builds a midpoint reference path and minimises lateral cross-track error + steering-rate over a receding horizon with SciPy SLSQP. Needs `scipy`. |
| `stanley` | Stanley cross-track + heading controller. |

MPC tunables: `mpc_horizon` (default 8 steps), `mpc_dt` (0.10 s), `mpc_w_cte` (3.0), `mpc_w_dsteer` (40.0), `mpc_w_heading` (2.0), `mpc_lookahead` (15.0 m).

#### Speed controllers (`speed_controller_type` param)

| `speed_controller_type` | Description |
|---|---|
| `curve_factor` (default) | Speed scales down with path curvature via `speed_curve_factor`. |
| `constant` | Fixed speed. |
| `constant_stop` | Constant speed that stops on cone loss. |
| `neural_v2` | Speed comes from the `neural_v2` network's second output. |
| `zero` | No motion (steering-only testing). |

!!! note "Neural weight files"
    `config/neural_weights.json` and `config/neural_v2_weights.json` hold the flattened network weights (`genes`) plus training metadata (`fitness`, `generations`, `optimizer`, etc.). They are produced by the sim2d training loop (below) and loaded at node startup when the matching `controller_type` is selected.

### `state_machine_node`

Central safety and control authority. Muxes autonomous vs manual `cmd_vel` based on the selected mission and the Autonomous-System (AS) state, and publishes the mission / machine-state / steering-mode to the ESP32. Full behaviour, state diagram, and topic list are on the **[State Machine](../state_machine.md)** page.

- **Subscribes:** `/dashboard/mission`, `/dashboard/state_cmd` (`String`); `/kart/cmd_vel`, `/kart/cmd_vel_manual` (`Twist`)
- **Publishes:** `/kart/cmd_vel_muxed` (`Twist`, 100 Hz), `/kart/state` (`String`, 10 Hz); `/orin/machine_state`, `/orin/mision`, `/orin/steer_mode` (`kb_interfaces/Frame`, on change)

### `cmd_vel_bridge_node`

Turns the muxed velocity command into the per-signal ESP32 command frames.

| | |
|---|---|
| **Subscribes** | `/kart/cmd_vel_muxed` (`Twist`, param `input_topic`); `/orin/steer_mode` (`Frame`) |
| **Publishes** | `/orin/throttle`, `/orin/brake`, `/orin/steering` (`kb_interfaces/Frame`) |

At a fixed rate (default 100 Hz) it maps `linear.x` to a throttle **or** brake effort (positive → throttle, negative → brake, normalised by `max_speed`) and `angular.z` to steering. When steer mode is PID (0) it clamps steering to `max_steer` (default 1.222 rad); in direct-PWM mode (1) it clamps to [-1, 1]. Payloads are int32-encoded by the helpers in `kb_dashboard/protocol.py` (steering ×1000, throttle/brake ×255) — see [kb_coms_micro](#kb_coms_micro) for the wire format.

### sim2d — 2D simulator & autoresearch training loop

**Location:** `tools/sim2d/` (a tool tree, not a ROS package).

A lightweight 2D kinematic simulator used to develop and **train** the controllers above without Gazebo. A kart drives the autocross track (~250 m lap) seeing cones within ±35°, 0.5–15 m. Controllers (`controllers.py`) receive cone positions and output steering + speed; fitness is scored on laps completed and lap time (`sim.py`).

The **autoresearch** loop (inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch)) lets an agent edit `strategy.py`, run an experiment via `evaluate.py`, log results to `results.tsv`, and keep or revert each change based on whether loss improved. Optimizers include a genetic algorithm and CMA-ES (`ga.py`). Winning weights are exported as the `neural_v2_weights.json` / `best_*.json` files that `cone_follower_node` loads. Typical commands:

```bash
cd tools/sim2d
python evaluate.py      # score the current strategy
python visualize.py     # animate the best controller on a track
```

---

## kb_coms_micro

**Type:** C++ (`ament_cmake`)
**Purpose:** Bidirectional serial bridge between ROS 2 and the Kart Medulla (ESP32 microcontroller) over UART.

The node is **payload-agnostic** — it forwards raw bytes between ROS 2 `Frame` messages and the UART wire protocol without interpreting the payload contents.

The node does not use one `/esp32/tx` + `/esp32/rx` pair — it exposes **one ROS topic per signal**. Each Orin→ESP32 topic maps to a frame `TYPE`; each ESP32→Orin frame is republished on its own topic. All are `kb_interfaces/Frame`.

| Direction | Topics |
|---|---|
| **Subscribes** (Orin → ESP32) | `/orin/throttle`, `/orin/brake`, `/orin/steering`, `/orin/machine_state`, `/orin/mision`, `/orin/heartbeat`, `/orin/shutdown`, `/orin/steer_mode` |
| **Publishes** (ESP32 → Orin) | `/esp32/heartbeat`, `/esp32/speed`, `/esp32/acceleration`, `/esp32/braking`, `/esp32/steering`, `/esp32/mision`, `/esp32/machine_state`, `/esp32/shutdown`, `/esp32/health/flags`, `/esp32/health/data`, `/esp32/diag_steering`; plus `/esp32/fps` (`std_msgs/Float32`) |

| Parameter | Default |
|---|---|
| `serial_port` | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5C37207028-if00` (resolves to `/dev/ttyACM0`) |
| `baudrate` | `115200` |

The node is **payload-agnostic**: a `Frame` carries a `type` byte and an `int32[]` payload, and the node frames/deframes it onto the UART without interpreting the numbers.

### Wire Protocol

The protocol is a **custom binary framing** — not protobuf. It is defined in the ESP32 firmware `kart-medulla/components/km_coms/km_coms.c` and mirrored on the Orin by the encode/decode helpers in `kb_dashboard/kb_dashboard/protocol.py`. Each frame:

```
+------+-----+------+---------+------+
| SOF  | LEN | TYPE | PAYLOAD | CRC  |
+------+-----+------+---------+------+
  1B     1B    1B      N B      1B
```

| Field | Size | Description |
|---|---|---|
| SOF | 1 byte | Start-of-frame marker: `0xAA` (`KM_COMS_SOM`) |
| LEN | 1 byte | Payload length **in bytes** (a multiple of 4; max 251) |
| TYPE | 1 byte | Message type (see table below) |
| PAYLOAD | N bytes | Zero or more **int32, big-endian** values (4 bytes each) |
| CRC | 1 byte | CRC-8, polynomial `0x07`, computed over LEN + TYPE + PAYLOAD |

UART: **115200 baud**, 8N1. Max total frame size: 255 bytes, so up to 251 payload bytes; since LEN is a multiple of 4, that is at most 62 int32 values (248 bytes).

!!! note "Payload is scaled integers, not floats"
    There are no float fields on the wire. Floats are scaled to int32 before sending and divided back on receipt (`kb_dashboard/protocol.py`):

    - Steering angle → radians × 1000 (milliradians), signed
    - Throttle / brake effort → × 255 (0–255)
    - Speed → m/s × 1000; acceleration → m/s² × 1000

### Message Types

Type IDs are defined by the `message_type_t` enum in `km_coms.h`. ESP32→Orin telemetry uses `0x01–0x1F`; Orin→ESP32 commands use `0x20–0x3F`.

**ESP32 → Orin (telemetry, 0x01–0x1F):**

These names come from `kb_interfaces/msg/Frame.msg`, which is what the Orin bridge (`kb_coms_micro`) and dashboard actually use.

| Type | Name | Payload (int32 values) |
|---|---|---|
| `0x01` | `ESP_ACT_SPEED` | `[speed_mps × 1000]` |
| `0x02` | `ESP_ACT_ACCELERATION` | `[lateral × 1000, longitudinal × 1000]` |
| `0x03` | `ESP_ACT_BRAKING` | `[effort × 255]` |
| `0x04` | `ESP_ACT_STEERING` | `[angle_rad × 1000, raw_encoder, pid_out × 1000]` |
| `0x05` | `ESP_MISION` | `[mission_id]` |
| `0x06` | `ESP_MACHINE_STATE` | `[state_id]` |
| `0x07` | `ESP_ACT_SHUTDOWN` | `[shutdown]` |
| `0x08` | `ESP_HEARTBEAT` | `[uptime_ms]` |
| `0x09` | `ESP_COMPLETE` | full telemetry bundle |
| `0x0A` | `ESP_DIAG_STEERING` | AS5600 diagnostic registers (debug) |
| `0x0B` | `ESP_HEALTH_STATUS` | `[flags, agc, heap_kb, i2c_errors]` (flags bit0=magnet_ok, bit1=i2c_ok, bit2=heap_ok) |

!!! warning "Firmware vs Orin naming mismatch at `0x02`"
    The ESP32 firmware enum (`km_coms.h`) names type `0x02` `ESP_ACT_THROTTLE`, but the Orin side (`Frame.msg`, `kb_coms_micro`, `protocol.py`) names it `ESP_ACT_ACCELERATION` and decodes it as two int32s. The command IDs agree across both sides, and `0x02` is the confirmed telemetry mismatch. This is unresolved in the code — verify against firmware before relying on `0x02` telemetry. If you consume other telemetry IDs (for example `0x0B` health), check the payload layout against the firmware send code too, since the firmware enum comment and the Orin decoder do not obviously match there.

**Orin → ESP32 (commands, 0x20–0x3F):**

| Type | Name | Payload (int32 values) |
|---|---|---|
| `0x20` | `ORIN_TARG_THROTTLE` | `[effort × 255]` (1 value) |
| `0x21` | `ORIN_TARG_BRAKING` | `[effort × 255]` (1 value) |
| `0x22` | `ORIN_TARG_STEERING` | `[angle_rad × 1000]` (1 value, signed) |
| `0x23` | `ORIN_MISION` | `[mission_id]` |
| `0x24` | `ORIN_MACHINE_STATE` | `[state_id]` |
| `0x25` | `ORIN_HEARTBEAT` | *(no payload)* |
| `0x26` | `ORIN_SHUTDOWN` | `[shutdown]` |
| `0x27` | `ORIN_COMPLETE` | `[throttle×255, brake×255, steering×1000, mission, machine_state, shutdown]` (6 values) |
| `0x28` | `ORIN_CALIBRATE_STEERING` | `[center_offset]` |
| `0x29` | `ORIN_STEER_MODE` | `[mode]` — `0` = PID (closed-loop angle), `1` = direct PWM |

The firmware validates the element count per type (e.g. it drops a `THROTTLE`/`BRAKE`/`STEERING` frame whose payload is not exactly 1 int32, and `COMPLETE` unless it is exactly 6) and ignores frames that fail CRC. Any received command frame (`0x20–0x3F`) also refreshes the firmware's command watchdog.

!!! warning "The old protobuf/`kart_msgs.proto` description is obsolete"
    Earlier docs described this link as protobuf/nanopb with float fields, and `kart-brain/docs/ACTUATION_PROTOCOL.md` describes a different 4-byte scheme. Both are outdated — the framed int32 protocol above (as implemented in `km_coms.c` and `protocol.py`) is what actually runs.

---

## kb_dashboard

**Type:** Python (`ament_python`)
**Purpose:** Web-based dashboard for real-time kart telemetry and mission control.

| | |
|---|---|
| **Subscribes** | The per-signal `/esp32/*` telemetry `Frame` topics from [`kb_coms_micro`](#kb_coms_micro); `/kart/state` (`String`); `/battery/state` (`sensor_msgs/BatteryState`) from [`kb_bms`](#kb_bms) |
| **Publishes** | `/dashboard/mission`, `/dashboard/state_cmd` (`String`) to the state machine |
| **Web UI** | `http://<orin-ip>` — port **80**, no suffix (WebSocket + HTTP) |

### Features

- Live telemetry: steering angle + raw encoder, speed, acceleration, throttle/brake effort
- Battery gauge and a dedicated battery tab (voltage, SOC, current, per-cell strip, temperatures) fed by `/battery/state`
- Health status: magnet (AGC), I2C bus, free heap
- Heartbeat monitoring with staleness indicator
- Mission selection — eight buttons (Manual, Remote control, Inspection, Autonomous, Accel, Skidpad, Autocross, Trackdrive); see the [full mission list](../state_machine.md)
- Machine state control (Start, Stop, EBS, Restart)

### Protocol Layer

All encode/decode logic lives in `protocol.py` — pure Python helpers with **no protobuf**. They pack/unpack the `int32[]` payloads of the framed protocol described under [kb_coms_micro](#kb_coms_micro) (e.g. `encode_steering()` = `[angle_rad × 1000]`, `decode_speed()` = `payload[0] / 1000`). The same module is imported by `cmd_vel_bridge_node` so encoding is shared across the stack.

---

## kb_bms

**Type:** Python (`ament_python`)
**Purpose:** Read the pack's smart BMS over Bluetooth LE (directly from the Orin, no ESP32 or CAN) and publish `sensor_msgs/BatteryState` on `/battery/state`.

| | |
|---|---|
| **Publishes** | `/battery/state` (`sensor_msgs/BatteryState`) |

Full node behaviour, the JBD BLE GATT command/parse protocol, published fields, and how the dashboard consumes it are on the dedicated **[BMS (battery node)](bms.md)** page.

---

## kb_serial_driver_lib

**Type:** C++ CMake subdirectory library (no `package.xml` of its own — it is built as part of [`kb_coms_micro`](#kb_coms_micro), not as a standalone colcon package)
**Purpose:** Low-level framed-UART serial driver used by [`kb_coms_micro`](#kb_coms_micro). It owns the serial port and TX/RX thread, and assembles/validates the `SOF | LEN | TYPE | PAYLOAD | CRC8` frames so the bridge node only deals with `Frame` messages. This is a library, not a runnable node.

---

## kb_interfaces

**Type:** CMake (`rosidl` message package)
**Purpose:** Custom ROS 2 message definitions shared across the workspace. The key type is `Frame` (a `type` byte plus an `int32[]` payload), which carries every Orin↔ESP32 command and telemetry signal and defines the `ORIN_*` / `ESP_*` type constants used by `cmd_vel_bridge` and the dashboard.

---

## kart_bringup

**Type:** CMake (`ament_cmake`, launch + config only)
**Purpose:** Orchestrate all nodes needed for real hardware and simulation operation.

### Launch Files

Actual files in `src/kart_bringup/launch/`: `launch.py`, `teleop.launch.py`, `remote_control.launch.py`, `dashboard.launch.py`, `gui.launch.py`.

**`launch.py`** — Full pipeline (main launcher). Pass `perception:=false` for remote-control-only:

1. **ZED camera** — stereo camera driver (zed2)
2. **Perception** — `yolo_detector` + `cone_depth_localizer` + `cone_marker_viz_3d`
3. **Steering HUD** — overlays cone highlights, steering arrow, and gauge on the annotated image → `/perception/hud`
4. **Cone follower** — autonomous controller (`geometric` by default)
5. **cmd_vel_bridge** — converts `/kart/cmd_vel_muxed` to `/orin/*` ESP32 Frame commands
6. **kb_coms_micro** — serial bridge to ESP32
7. **Dashboard** — web UI on port 80

**`teleop.launch.py`** — Manual driving with a gamepad:

1. **`joy_node`** (from `joy` package) — reads gamepad at `/dev/input/js0`
2. **`joy_to_cmd_vel`** — converts joystick axes to Twist on `/kart/cmd_vel`
3. **`cmd_vel_bridge`** — converts Twist to `/orin/*` ESP32 Frame commands
4. **`kb_coms_micro`** — serial bridge to ESP32

**`remote_control.launch.py`** — Drive from the dashboard (no gamepad, no perception).

**`dashboard.launch.py`** — Minimal/safe mode: `kb_coms_micro` + dashboard only. No commands are sent to the kart, so it is safe for firmware testing.

**`gui.launch.py`** — HUD viewer window on the Orin display (`rqt_image_view` showing `/perception/hud`), launched separately from the autonomous stack.

The Gazebo simulation is launched from its own package: `ros2 launch kart_sim simulation.launch.py`.
