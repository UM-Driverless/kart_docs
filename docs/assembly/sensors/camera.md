<!-- Two gaps on this page are tracked in tasks.md, "Document the ZED2's published topics and the
     RViz2 cone-detection setup": (1) which ZED topics the stack consumes — the commented-out table
     further down was never corrected; (2) which packages to install to see cone detections in
     RViz2. -->

# ZED2 Camera Integration Documentation

## Overview

This document describes the integration of the **ZED2 stereo camera** into the kart and its usage through the **ROS 2 wrapper**.

Cone detection itself is not done by the camera — it is a separate ROS 2 node. This page covers getting images out of the ZED; what happens to them is on the [ROS 2 packages](../../software/ros2/packages.md#kart_perception) page.

## Official Resources

- **ZED2 Camera Overview**: [https://www.stereolabs.com/zed-2/](https://www.stereolabs.com/zed-2/)
- **ZED ROS 2 Wrapper Documentation**: [https://docs.stereolabs.com/ros2/](https://docs.stereolabs.com/ros2/)

## Hardware: ZED2 Camera

The [ZED2](https://www.stereolabs.com/zed-2/) camera by Stereolabs is a stereo vision camera capable of providing:

- High-definition left and right stereo images
- Depth sensing
- 3D point clouds
- Positional tracking (6DoF)
- Integrated IMU sensors (accelerometer, gyroscope, magnetometer)
- Environmental sensors (barometer, temperature sensor)

## ROS 2 Integration

The ZED2 camera is integrated into the project using the **official Stereolabs ZED ROS 2 Wrapper**:

- GitHub: [https://github.com/stereolabs/zed-ros2-wrapper](https://github.com/stereolabs/zed-ros2-wrapper)


### Installation Requirements

To properly install and run the **ZED ROS 2 Wrapper** with the ZED2 camera, you must ensure the following dependencies and system configuration are in place.

- Operating System

    - **Ubuntu 24.04 LTS** is the recommended version for this setup.
    - Other Ubuntu versions may be used; however, note that dependencies such as CUDA, TensorRT, ROS2, and the ZED SDK may require different versions and additional compatibility testing.

- ROS 2 Jazzy

    - Install **ROS 2 Jazzy** by following the official instructions here:  
  [https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)

- CUDA Toolkit (12.0 to 12.9)

    - Install **CUDA 12.x** (any version from 12.0 to 12.9 is compatible).
    - Download from the official NVIDIA website:  
  [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)

- ZED SDK (v5.0)

    - Download and install **ZED SDK v5.0** for Ubuntu 24.04 with CUDA 12 and TensorRT 10 from the official release page:  
  [https://www.stereolabs.com/en-es/developers/release/5.0#82af3640d775](https://www.stereolabs.com/en-es/developers/release/5.0#82af3640d775)

- TensorRT 10

    - Download the **TensorRT 10** `.deb` package for Ubuntu 24.04 + CUDA 12.9 from the official NVIDIA repository:  
  [https://developer.nvidia.com/downloads/compute/machine-learning/tensorrt/10.10.0/local_repo/nv-tensorrt-local-repo-ubuntu2404-10.10.0-cuda-12.9_1.0-1_amd64.deb](https://developer.nvidia.com/downloads/compute/machine-learning/tensorrt/10.10.0/local_repo/nv-tensorrt-local-repo-ubuntu2404-10.10.0-cuda-12.9_1.0-1_amd64.deb)
  

    After downloading the `.deb` file, run the following commands to install it:

```bash
sudo dpkg -i nv-tensorrt-local-repo-ubuntu2404-10.10.0-cuda-12.9_1.0-1_amd64.deb
sudo apt update
```

If you encounter **GPG key errors**, follow these additional steps:

```bash
sudo cp /var/nv-tensorrt-local-repo-ubuntu2404-10.10.0-cuda-12.9/*.gpg /usr/share/keyrings/

sudo nano /etc/apt/sources.list.d/nv-tensorrt-local-repo-ubuntu2404-10.10.0-cuda-12.9.list
```

Replace the content of the file with:

```bash
deb [signed-by=/usr/share/keyrings/nv-tensorrt-local-CD20EDBE-keyring.gpg] file:///var/nv-tensorrt-local-repo-ubuntu2404-10.10.0-cuda-12.9 /
```

Then update again:

```bash
sudo apt update
```

This should resolve the key issues.

Finally, install the required TensorRT runtime libraries:

```bash
sudo apt-get install libnvinfer10 libnvinfer-dev libnvinfer-plugin-dev python3-libnvinfer
```

- ZED ROS 2 Wrapper

    - Clone and build the **zed-ros2-wrapper** package in your existing ROS 2 workspace:

```bash
cd ~/ros2_ws/src
git clone https://github.com/stereolabs/zed-ros2-wrapper.git
cd ..
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

Official repository:  
[https://github.com/stereolabs/zed-ros2-wrapper](https://github.com/stereolabs/zed-ros2-wrapper)

---

Once all the dependencies are installed and the wrapper is successfully built, you should be able to launch the ZED2 ROS 2 node without issues.

### Launching the Camera

The camera is launched using a provided launch file, typically:

```bash
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2
```

<!-- ### Published Topics of Interest

CORREGIR POR TOPICS CORRECTOS

| Topic Name                             | Message Type                | Description                                    |
|----------------------------------------|-----------------------------|------------------------------------------------|
| `/zed2/zed_node/left/image_rect_color` | `sensor_msgs/Image`         | Rectified color image from left camera         |
| `/zed2/zed_node/depth/depth_registered`| `sensor_msgs/Image`         | Depth image aligned to the left camera         |
| `/zed2/zed_node/imu/data`              | `sensor_msgs/Imu`           | IMU data (accelerometer + gyroscope + orientation) |
| `/zed2/zed_node/point_cloud/cloud_registered` | `sensor_msgs/PointCloud2` | Registered 3D point cloud                      |
| `/zed2/zed_node/odom`                  | `nav_msgs/Odometry`         | Visual odometry (pose estimation)              | -->

## Where cone detection happens

There are two ways to detect cones from this camera, and the kart normally uses the first.

### 1. Our own YOLO node (default)

`kart_perception/yolo_detector_node.py` subscribes to the ZED's rectified RGB topic and runs **YOLOv11n** through Ultralytics at `imgsz` 320, with TensorRT `.engine` weights on the Orin. The ZED wrapper is left as a plain image source — its built-in object detection stays off. Launch it with `perception_3d.launch.py`.

This is the path that is tuned and tested: the detector's parameters, the weights files, and the 2D → 3D projection that follows are documented under [ROS 2 → Packages → kart_perception](../../software/ros2/packages.md#kart_perception).

### 2. The ZED SDK's built-in object detection (alternative)

The ZED wrapper can also run a custom detector itself, on the GPU, and publish `ObjectsStamped` with 3D positions already resolved — which removes our depth-projection step. `perception_zed_od.launch.py` runs the pipeline in this mode; it launches only the marker visualiser, because the detector and the depth localiser are not needed.

To enable it, export the model to ONNX and point the wrapper at it in `common_stereo.yaml` (in `zed-ros2-wrapper/zed_wrapper/config`):

```yaml
object_detection:
     od_enabled: true
     model: 'CUSTOM_YOLOLIKE_BOX_OBJECTS'
     custom_onnx_file: '<path to model>'
```

The first launch with a new ONNX file is slow — TensorRT optimises the model then, taking seconds to minutes depending on the machine. The optimised engine is cached, so later runs start quickly.
