<!-- TODO
Hay que agregar el uso de los sensores, ademas de que habria que hacer una documentacion de los topics que se usan de la camara.

Hay que agregar tambien cuales paquetes hay que instalar para poder visualizar la deteccion de los conos en rviz2
-->

# ZED2 Camera Integration Documentation

## Overview

This document describes the integration of the **ZED2 stereo camera** into the kart, its usage through the **ROS 2 wrapper**, and the combination with **YOLOv5** for cone detection. 

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

## Cone Detection with YOLOv5

In this project, **YOLOv5** is used to perform **real-time cone detection** on images captured by the ZED2 camera.
The ZED ROS 2 Wrapper supports custom object detection models through **ONNX integration**, allowing you to run your own trained detectors such as YOLOv5 directly on the GPU using **TensorRT** for real-time inference.

### Exporting and Using a Custom YOLOv5 Model

If you have trained a YOLOv5 model (e.g., for cone detection), follow these steps to integrate it into the ZED wrapper:

1. **Export the model to ONNX format**:  
   You can do this using PyTorch and the YOLOv5 export tools (e.g., `export.py` script from the [YOLOv5 repository](https://github.com/ultralytics/yolov5)):

   This will generate a `.onnx` file.

2. **Enable object detection in the ZED wrapper** by editing the configuration file:

   Open your `common_stereo.yaml` (located in your ROS 2 workspace, inside `zed-ros2-wrapper/zed_wrapper/config`), and modify or add the following lines:

   ```yaml
   object_detection:
        od_enabled: true 
        model: 'CUSTOM_YOLOLIKE_BOX_OBJECTS'
        custom_onnx_file: '$path to model'
   ```

### First-Time Optimization

The first time you launch the node with your custom ONNX model, **TensorRT will optimize the model for inference**, which may take additional time (several seconds to minutes depending on the system).  
Subsequent runs will be much faster, as the optimized engine will be cached and reused.

---

Once all dependencies are correctly installed and the YOLOv5 model is configured, you should be able to run real-time object detection with the ZED2 camera using ROS 2.
