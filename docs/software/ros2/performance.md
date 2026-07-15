# Performance & Latency

This page documents the end-to-end latency of the autonomous pipeline, what causes slowness at each stage, and the design decisions made to minimize it.

## End-to-end pipeline

The autonomous loop has six stages from photon to actuator:

```
ZED Camera → YOLO Detector → Cone Depth Localizer → Controller → Serial Bridge → ESP32
  ~33 ms       ~?? ms            ~?? ms              ~2 ms        ~5 ms         ~100 ms
```

!!! warning "Latency values are estimates"
    Most values on this page have NOT been measured on hardware yet. They are order-of-magnitude estimates based on code analysis. Actual profiling is needed — see [What we still need to measure](#what-we-still-need-to-measure).

## Stage-by-stage breakdown

### 1. Camera acquisition (~33 ms)

The ZED 2 captures stereo RGB + depth at up to 30 Hz (33 ms per frame). This is the fastest the pipeline can possibly run — everything downstream is bounded by camera FPS.

The ZED SDK does stereo matching (disparity → depth) on-board, so the depth image arrives alongside RGB with no extra ROS-side computation.

### 2. YOLO inference (not yet measured)

YOLOv11s runs on each RGB frame to detect cones. This is likely the **largest single latency contributor** in the pipeline.

**What `rclpy.spin()` is and why it matters:**
`spin()` is just an infinite loop that waits for ROS messages and calls callbacks one at a time:

```python
# Pseudocode for rclpy.spin()
while running:
    msg = wait_for_next_event()
    call_matching_callback(msg)  # blocks until callback returns
```

If YOLO inference ran directly inside the image callback, `spin()` couldn't receive new frames until inference finished. With queue depth=1 (keep-latest), frames arriving during inference would overwrite each other, but the queue slot itself can't be read until the callback returns. So the frame being processed would always be stale by one inference cycle.

**Our fix — dedicated inference thread:**
The ROS callback (`_on_image`) just stashes the latest frame behind a lock and returns immediately (~nanoseconds). A separate thread runs inference in a loop, always grabbing the most recent frame when it's ready for the next one.

```python
# ROS callback (runs in spin thread) — instant
def _on_image(self, msg):
    frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
    with self._frame_lock:          # lock held for ~nanoseconds (pointer swap)
        self._latest_frame = (msg.header, frame)
    self._frame_event.set()

# Inference thread (runs independently)
def _inference_loop(self):
    while not self._shutdown:
        self._frame_event.wait()
        self._frame_event.clear()
        with self._frame_lock:
            data = self._latest_frame
        # YOLO inference on data (~tens of ms)
```

This doesn't make inference faster (still one frame at a time), but it ensures:

- The frame being inferred is always the **freshest** one, not one that waited in the queue during the previous inference.
- The `spin()` loop stays responsive for any future callbacks (IMU, lidar, etc.).
- Lock contention is negligible — the lock only protects a Python reference swap, not a data copy.

**Queue depth = 1** on the image subscription means ROS keeps only the latest frame. Combined with the threading model, old frames are discarded at every level — we never process stale data.

### 3. Cone depth localizer (potentially high)

This node synchronizes three topics using `ApproximateTimeSynchronizer`:

- `/perception/cones_2d` (from YOLO)
- `/zed/.../depth/depth_registered` (from ZED)
- `/zed/.../rgb/camera_info` (from ZED)

The sync waits until it has messages from all three topics with timestamps within `sync_slop` of each other (default: **2.0 seconds**). The actual processing (median depth lookup + 3D projection) is fast (~5 ms), but the sync waiting can add variable latency depending on timestamp alignment.

!!! note "Is the 2.0s slop too large?"
    2.0 seconds is very conservative. If the ZED publishes RGB, depth, and camera_info in lockstep (which it should), timestamps should align within a few milliseconds. A tighter slop (0.1–0.2s) would reduce worst-case latency without dropping valid sync pairs. This needs profiling to confirm.

### 4. Controller (~2 ms)

`cone_follower_node` runs simple geometry (nearest blue+yellow cone → midpoint → `atan2` → steering angle) or a small neural net (17→16→2, 322 parameters). Either path completes in ~1–2 ms. Not a bottleneck.

A safety timer checks every 100 ms whether cones have been seen in the last second. If not, it publishes zero velocity (stop).

### 5. Serial bridge (~5 ms)

`cmd_vel_bridge` polls `/kart/cmd_vel` at 100 Hz (10 ms timer) and encodes the framed int32 binary messages for throttle, brake, and steering (see [Packages → kb_coms_micro](packages.md#kb_coms_micro)). `KB_Coms_micro` pushes these onto a TX thread queue and sends them over UART at 115200 baud.

A single frame is typically 8–15 bytes → **~1 ms on the wire** at 115200 baud. The TX thread wakes on a condition variable, so the queue-to-wire delay is near-instant.

### 6. ESP32 control loop (~100 ms)

The ESP32 runs a PID steering loop at **10 Hz** (100 ms period). When a new steering target arrives over UART, it takes effect on the next PID cycle. Worst case, the target sits for nearly 100 ms before being applied.

The AS5600 magnetic encoder is read via I2C (~1–2 ms per read) each cycle for steering feedback.

## QoS and queue depths

| Node | Topic | Queue depth | Notes |
|------|-------|-------------|-------|
| yolo_detector | image input | **1** | Keep-latest, drop old frames |
| yolo_detector | detections output | 10 | |
| cone_depth_localizer | sync buffer | 30 | ApproximateTimeSynchronizer internal buffer |
| cone_follower | cones_3d input | 10 | |
| cmd_vel_bridge | cmd_vel input | 10 | Polled at 100 Hz |
| KB_Coms_micro | all topics | 10 | |

All topics use default QoS (RELIABLE + VOLATILE) except odometry which uses BEST_EFFORT + VOLATILE.

## What we still need to measure

These are the key unknowns that require on-hardware profiling:

- [ ] **YOLO inference time** on the Orin GPU (YOLOv11s at 640px). The node already logs FPS every 2 seconds to `/perception/yolo/fps` — run the pipeline and read it.
- [ ] **Actual sync delay** in `cone_depth_localizer` — log timestamp deltas between the three synced topics to see if 2.0s slop is causing unnecessary buffering.
- [ ] **End-to-end latency** from camera frame timestamp to ESP32 PWM output. Could be measured by comparing the image header timestamp with the time the corresponding steering command arrives at the ESP32.
- [ ] **Camera FPS** under load — does ZED maintain 30 Hz when the Orin GPU is busy with YOLO?
- [ ] **ESP32 control loop jitter** — is the 10 Hz PID cycle stable, or do UART interrupts cause timing variation?
