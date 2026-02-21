# 2024 — Python

!!! info "Repository"
    [github.com/UM-Driverless/driverless](https://github.com/UM-Driverless/driverless)
    &nbsp;&bull;&nbsp; [Video tutorial](https://youtu.be/wZSFr2eYE4M?si=K0gPpFHeWrK2Y9I8)

The original autonomous system, built as a single Python application. All components run in one process orchestrated by `main.py`.

## Architecture

```
main.py
 ├── YOLOv5 cone detection (PyTorch + CUDA)
 ├── ZED camera interface (pyzed SDK)
 ├── Path planning
 └── CAN bus control (Kvaser canlib)
```

**Pipeline:** Camera frame → YOLOv5 inference → depth projection via ZED → path planning → steering/throttle commands over CAN.

## Key Components

| Component | Description |
|---|---|
| **Perception** | YOLOv5 model trained on Formula Student cones. Weights at `src/driverless/yolov5/weights/`. |
| **Camera** | Stereolabs ZED — provides RGB + depth. Configured via ZED SDK. |
| **Control** | CAN bus communication with actuators via Kvaser interface. Setup scripts: `setup_can0.sh`, `enable_CAN.sh`. |
| **Simulator** | [Formula Student Driverless Simulator](https://github.com/FS-Driverless/Formula-Student-Driverless-Simulator) (FSDS) — AirSim-based, Unreal Engine. Config in `src/driverless/config.yaml`. |

## Hardware Targets

- **NVIDIA Jetson Xavier NX** — original onboard computer
- **NVIDIA Jetson Orin** — upgraded compute platform
- **Desktop with NVIDIA GPU** — development with CUDA 12.x / Ubuntu 24.04

## Setup

```bash
# Python environment (pyenv + venv)
pyenv install 3.12.3
pyenv local 3.12.3
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

See the [repository README](https://github.com/UM-Driverless/driverless#readme) for full setup instructions including CUDA, ZED SDK, and Jetson-specific configuration.

## Limitations

This architecture served well for initial development but had some drawbacks that motivated the move to ROS 2:

- **Monolithic** — all components tightly coupled in one process; a crash in perception takes down control
- **No standard message format** — data passed between functions via custom Python objects
- **Hard to test in isolation** — can't run perception without the full pipeline
- **Limited simulation** — FSDS requires Windows or a powerful Linux desktop with GPU
