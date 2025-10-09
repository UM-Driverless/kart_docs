# About the Driverless Kart Project

## What is Formula Student Driverless?

Formula Student Driverless (FSD) is a category within the Formula Student competition where teams must develop a vehicle capable of driving **autonomously**, using only sensors, algorithms, and automatic control—without a driver.

### Competition Characteristics

The circuit is delimited by **cones** that define the track boundaries. Teams don't know the circuit layout in advance, so the vehicle must:

- **Detect the cones** using perception systems
- **Infer track boundaries** from sensory information
- **Plan a safe trajectory** that optimizes speed and stability
- **Execute maneuvers** (acceleration, braking, turns) without human intervention

### Competition Tests

Tests include autonomous versions of classic Formula Student disciplines:

- **Acceleration**: Maximum speed straight line
- **Skid-pad**: Figure-8 track to evaluate lateral handling
- **Autocross**: One complete lap on the unknown circuit
- **Trackdrive**: Multiple laps following the track consistently

### Technical Challenges

Developing a Driverless vehicle involves solving multiple engineering challenges:

**Perception**
- Cone detection and classification (blue, yellow, orange)
- Environment segmentation and noise filtering
- Multi-sensor data fusion

**Localization and Estimation**
- Vehicle state estimation (position, velocity, orientation)
- Real-time local map construction
- Correction using inertial sensors (IMU) and other systems

**Trajectory Planning**
- Generation of viable paths within detected boundaries
- Optimization considering vehicle dynamics
- Real-time adaptation to obstacles or incorrect detections

**Control and Actuation**
- Longitudinal control (throttle/braking)
- Lateral control (steering)
- System coordination to follow the planned trajectory

**Safety**
- Emergency stop systems
- Sensor and software integrity validation
- Redundancies and fail-safes

### Technologies Employed

Teams typically use a combination of:

- **Sensors**: Cameras, LIDAR, inertial sensors (IMU), GNSS/INS
- **Software**: Robotics frameworks (ROS), computer vision, SLAM algorithms
- **Actuators**: Steer-by-wire systems, brake-by-wire, electronic throttle control

---

## What Our Driverless Section Does

The Driverless section of U-Motorsport URJC is responsible for designing and implementing the complete autonomous driving system. Our goal is to develop these systems on the **kart as a testing platform** and subsequently integrate them into the **main competition single-seater**.

### 1. Perception and Sensing

**Objective**: Detect the environment and extract relevant information for navigation.

- Cone and track boundary detection using **cameras** and image processing (computer vision)
- Use of **inertial sensors (IMU)** to estimate orientation, accelerations, and vehicle attitude
- **Sensor data fusion** for robustness against noise or individual sensor failures

### 2. Localization and State Estimation

**Objective**: Know where the vehicle is and how it's moving.

- Estimation of **relative position** within the track (where each track boundary is)
- **Dynamic local map registration** without relying on a prior map (SLAM)
- **Sensor correction** to maintain precision over time

### 3. Trajectory Planning

**Objective**: Decide where the vehicle should drive.

- Generation of a **viable path** within detected boundaries
- Optimization of parameters like **minimum curvature, smoothness, and safety**
- **Real-time adaptation** to obstacles or poorly detected cones

### 4. Control and Actuation

**Objective**: Make the vehicle follow the planned trajectory.

**Longitudinal control**
- Throttle and braking management to reach and maintain target speed
- Response to track changes (braking before curves, acceleration on straights)

**Lateral control**
- Turn execution to follow optimal trajectory
- Compensation for slipping and disturbances

**Physical actuators**
- **Motorized steering** system (steer-by-wire)
- **Emergency braking** system
- Electronic throttle control

### 5. Safety and Redundancies

**Objective**: Ensure safe operation at all times.

- **Emergency braking** mechanism (brake fail-safe) to stop the vehicle if automatic decisions fail
- **Integrity validations** of sensors and software
- **Real-time monitoring** systems
- **Telemetry** for post-execution analysis

### 6. Hardware-Software Integration and Physical Testing

**Objective**: Validate the entire system under real conditions.

- Adaptation of **electronic architecture** to the real vehicle
- **Testing and calibration** on the kart as a testing platform
- Real circuit test iterations:
  - Cone tracks on campus
  - Slalom courses
  - Unknown curves
  - Increasing speed tests

---

## Previous Season (2024-2025)

During the previous season, the Driverless section laid the groundwork for the project:

### Software Development in Simulation

- **Complete Python prototype** for autonomous driving
- Development and validation **entirely in simulation**
- Testing of perception, planning, and control algorithms in virtual environment

### Physical Architecture Design

- Initial **mechanical architecture** design for automatic steering
- **Electronic system** planning (sensors, actuators, computation)
- Specification of braking and sensing components

### Virtual Validation

- **Tests in simulated environments** with different track configurations
- **Algorithm adjustments** based on simulation metrics
- Development of visualization and debugging tools

---

## Improvements and Advances This Season (2025-2026)

This season we've made a significant qualitative leap, moving from simulation to real implementation:

### 1. Migration to ROS (Robot Operating System)

**Why ROS:**
- **Mature ecosystem** with proven libraries for mobile robotics
- **Modularity**: Clear separation between perception, planning, control
- **Development tools**: RViz, rqt, rosbag for visualization and debugging
- **Compatibility** with future more complex systems on the single-seater
- **Active community** and extensive documentation

**Impact:**
- Complete migration from monolithic Python stack to **ROS node-based architecture**
- Better integration with commercial sensors and actuators
- Facilitates collaboration between different team subsystems

### 2. Introduction of the Real Kart (HenaKart)

**Testing platform advantages:**
- **Physical validation** of all subsystems before integrating on the single-seater
- **Real environment** without compromising the competition vehicle
- **Rapid iterations**: Simpler and safer than testing directly on the Formula car
- **Outdoor testbed** for perception and control algorithms
- **Educational platform** for students, professors, and researchers

**Addressing a Critical Need:**

Several professors from the Robotics department expressed the **need for an outdoor mobile robot platform** where they could test and validate their algorithms. Until now, autonomous navigation software and robotic experiments were limited to indoor environments.

This kart project solves two problems simultaneously:
1. Provides a testbed for Driverless technology development
2. Offers researchers an outdoor platform that can navigate the university campus

**Current status:**
- Kart fully operational in **manual mode**
- Actuation systems for **steering and braking ordered**
- Cone detection camera **mounted and functional**

### 3. Motorized Steering System (Steer-by-Wire)

**Functionality:**
- Allows the kart to **turn based on autonomous controller decisions**
- Integration with lateral control system in the ROS stack
- **Preservation of manual mode** for supervised operation

**Development:**
- Finalization of mechanical and electronic design
- Selection of actuators with adequate torque and speed
- Implementation of control interface from ROS

### 4. Emergency Braking System

**Purpose:**
- **Critical safety subsystem** to stop the vehicle in case of failure
- Automatic activation when:
  - Loss of communication with control system
  - Detection of dangerous conditions
  - Operator emergency commands

**Characteristics:**
- System **independent** from main control
- **Redundancies** to ensure reliable activation
- Integration with telemetry for event logging

### 5. Perception Optimization without LIDAR

**Technical decision:**
- Operation **using only cameras and IMU**
- **Reduction of cost, weight, and complexity**
- Greater technical challenge, but more aligned with available resources

**Implemented improvements:**
- **Optimized cone detection** algorithms for higher precision
- **Reduced latency** in image processing
- **Improved camera calibration** for different lighting conditions
- **Robust filtering** to eliminate false positives

### 6. Improved Planning and Control Algorithms

**Approach:**
- Designed for **unknown tracks** delimited by cones
- **Minimized latency** for real-time response
- **Robustness** to imperfect or missing detections

**Advances:**
- Implementation of **adaptive controllers** that adjust parameters according to conditions
- **Predictive models** to anticipate vehicle behavior
- **Continuous validation** with real kart data

---

## Project Final Objectives

### Short Term (This Season)

1. **Functional autonomous kart** capable of:
   - Detecting cones with high precision
   - Navigating simple tracks autonomously
   - Executing emergency braking reliably

2. **ROS architecture validation** for migration to the single-seater

3. **Real data collection** to train and improve algorithms

### Medium Term

1. **Technology transfer** from kart to Formula Student single-seater

2. **Participation in competitions** of Formula Student Driverless

3. **Research platform** available for:
   - Students developing bachelor's/master's theses
   - Professors testing algorithms
   - Researchers validating new techniques

### Long Term

1. **Robust development ecosystem** documented for future team generations

2. **Open-source contributions** to the mobile robotics and autonomous vehicle community

3. **Academic and industrial collaborations** based on the developed platform

---

*For more detailed technical information, see the [Assembly](assembly/index.md), [Software](software/index.md), and [BOM](bom/index.md) sections.*
