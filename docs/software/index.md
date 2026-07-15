# Software

The autonomous system has evolved through two major versions, both targeting the same kart hardware but with very different software architectures.

| | 2024 — Python | 2025 — ROS 2 |
|---|---|---|
| **Language** | Python 3.12 | Python + C++ (ROS 2 Humble) |
| **Framework** | Custom pipeline (`main.py`) | ROS 2 nodes, launch files, topics |
| **Perception** | YOLOv5 + ZED SDK | YOLOv11 + ZED ROS wrapper |
| **Communication** | Direct CAN bus (Kvaser) | ROS 2 topics + UART framed int32 protocol (ESP32) |
| **Simulation** | FSDS (AirSim/Unreal Engine) | Gazebo Fortress (headless) |
| **Compute** | NVIDIA Jetson Xavier NX / Orin | NVIDIA Jetson + UTM VM for dev |
| **Repository** | [UM-Driverless/driverless](https://github.com/UM-Driverless/driverless) | [UM-Driverless/kart-brain](https://github.com/UM-Driverless/kart-brain) |

The ROS 2 version was introduced to gain modularity (independent nodes for perception, control, and hardware), standardized message types, and a richer simulation ecosystem (Gazebo). The Python version remains a good reference for understanding the core autonomous driving algorithms.

!!! tip "Setting up the Jetson Orin from scratch?"
    See the **[Orin Setup Guide](../assembly/electronics/orin-setup.md)** for the complete flashing and installation procedure — JetPack, CUDA, ROS 2, ZED SDK, PyTorch, remote access, and all configuration needed to get the kart's computer running.
