# Software

The autonomous system has evolved through two major versions, both targeting the same kart hardware but with very different software architectures.

| | 2024 — Python | 2025 — ROS 2 |
|---|---|---|
| **Language** | Python 3.12 | Python + C++ (ROS 2 Humble) |
| **Framework** | Custom pipeline (`main.py`) | ROS 2 nodes, launch files, topics |
| **Perception** | YOLOv5 + ZED SDK | YOLOv5 + ZED ROS wrapper |
| **Communication** | Direct CAN bus (Kvaser) | ROS 2 topics + micro-ROS (ESP32) |
| **Simulation** | FSDS (AirSim/Unreal Engine) | Gazebo Fortress (headless) |
| **Compute** | NVIDIA Jetson Xavier NX / Orin | NVIDIA Jetson + UTM VM for dev |
| **Repository** | [UM-Driverless/driverless](https://github.com/UM-Driverless/driverless) | [UM-Driverless/KART_SW](https://github.com/UM-Driverless/KART_SW) |

The ROS 2 version was introduced to gain modularity (independent nodes for perception, control, and hardware), standardized message types, and a richer simulation ecosystem (Gazebo). The Python version remains a good reference for understanding the core autonomous driving algorithms.
