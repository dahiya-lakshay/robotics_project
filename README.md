# 6-DOF Robotic Arm Pick-and-Place Using Denavit–Hartenberg Kinematics

<p align="center">
  <strong>Algorithms for Intelligent Systems and Robotics | CSAI4014</strong><br>
  B.Tech CSE (Artificial Intelligence & Machine Learning) · Semester VII<br>
  Project P02 · Group G04 · Batch B3
</p>

---

## Overview

This project implements a **six-degree-of-freedom (6-DOF) robotic arm pick-and-place system** using the Universal Robots UR5 manipulator. It combines robot kinematics, inverse kinematics, trajectory planning, motion control, and simulator communication to demonstrate an automated object manipulation workflow.

The mathematical foundation of the system is the **Denavit–Hartenberg (D-H) convention**, which is used to represent the robot's link geometry and derive homogeneous transformation matrices.

The implementation is developed in Python and is designed to communicate with CoppeliaSim through its ZeroMQ Remote API. A standalone execution mode is also available for development and testing when the simulator is not connected.

The objective is to demonstrate how mathematical models and intelligent control algorithms can be integrated into a practical robotic manipulation pipeline.

## Project Objectives

- Model a 6-DOF serial robotic manipulator using standard D-H parameters.
- Implement forward kinematics to determine the end-effector pose.
- Implement inverse kinematics to calculate joint configurations for target poses.
- Generate smooth joint-space and Cartesian trajectories.
- Develop a motion-control pipeline for coordinated robot movement.
- Execute a sequential pick-and-place task with gripper actuation.
- Evaluate trajectory behaviour and kinematic accuracy through experimental results.

## Key Features

| Component | Description |
|---|---|
| D-H Kinematics | Standard Denavit–Hartenberg parameterisation and transformation matrices |
| Forward Kinematics | Computes end-effector position and orientation |
| Inverse Kinematics | Analytical and numerical solution approaches |
| Jacobian Analysis | Geometric Jacobian for differential motion analysis |
| Trajectory Planning | Cubic, quintic, trapezoidal and Cartesian trajectory methods |
| Motion Control | Joint waypoint dispatch and coordinated movement |
| Pick-and-Place | Sequential manipulation workflow with gripper control |
| Simulator Interface | ZeroMQ Remote API bridge for CoppeliaSim |
| Performance Evaluation | Benchmark data, CSV outputs and visual comparisons |

## System Architecture

The project follows a modular architecture in which each subsystem is responsible for a distinct part of the robotic manipulation process.

```text
                 USER / COMMAND LINE
                         |
                         v
                  MAIN APPLICATION
                         |
                         v
               PICK-AND-PLACE ENGINE
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
     INVERSE IK     TRAJECTORY       MOTION
     KINEMATICS      PLANNER        CONTROLLER
          |              |              |
          +--------------+--------------+
                         |
                         v
                FORWARD KINEMATICS
                  AND D-H ENGINE
                         |
                         v
                ROBOT CONNECTION
                    AND GRIPPER
                         |
              +----------+----------+
              |                     |
              v                     v
         COPPELIASIM          STANDALONE
          SIMULATION           MODE
```

## Pick-and-Place Workflow

The manipulation process is implemented as a scripted 10-stage execution pipeline:

1. **Initialisation:** Establish robot interface (or fallback to virtual mode) and initialise gripper state.
2. **Home Position:** Move the manipulator to its predefined starting joint configuration.
3. **Target Definition:** Define pick and place coordinates.
4. **Pre-Pick Approach:** Move the end effector to a clearance waypoint above the object.
5. **Pick Descent:** Execute controlled descent towards the target object.
6. **Grasp:** Trigger gripper close actuation (in virtual mode, proximity threshold is 5 cm).
7. **Lift:** Raise the end effector back to clearance height.
8. **Transfer:** Transfer the payload towards the destination pre-place waypoint.
9. **Place and Release:** Lower the arm, trigger gripper open, and retract vertically.
10. **Return Home:** Return the manipulator to its resting home configuration.

## Technology Stack

- **Programming Language:** Python
- **Numerical Computing:** NumPy, SciPy
- **Data Analysis:** Pandas
- **Visualisation:** Matplotlib
- **Symbolic Mathematics:** SymPy
- **Robotics Simulation:** CoppeliaSim
- **Communication:** ZeroMQ Remote API
- **Testing & Validation:** Python standalone verification modules (unit test suite not committed)
- **Version Control:** Git and GitHub

## Repository Structure

```text
robotics_project/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── dh_parameters.py
│   ├── forward_kinematics.py
│   ├── inverse_kinematics.py
│   ├── trajectory_planner.py
│   ├── motion_controller.py
│   ├── robot_connection.py
│   ├── gripper_controller.py
│   ├── pick_and_place.py
│   ├── live_demo_visualizer.py
│   └── benchmark_experiments.py
│
├── docs/
│   ├── project_overview.md
│   ├── PROJECT_AUDIT.md
│   ├── dh_parameters.md
│   ├── system_architecture.md
│   ├── references.md
│   ├── DEMO_RECORDING_SCRIPT.md
│   ├── PRESENTATION_SPEAKER_SCRIPT.md
│   └── VIVA_QUESTION_BANK.md
│
├── results/
│   ├── metrics.csv
│   ├── comparison.csv
│   └── plots/
│
├── report/
│   └── project_report.pdf
│
└── presentation/
    └── project_presentation.pdf
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- Git
- CoppeliaSim (for live simulator integration)
- A compatible UR5 scene configured for the ZeroMQ Remote API

### 1. Clone the repository

```bash
git clone https://github.com/dahiya-lakshay/robotics_project.git
cd robotics_project
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 4. Install the CoppeliaSim Remote API client

```bash
python3 -m pip install coppeliasim-zmqremoteapi-client
```

### 5. Run the application

Display the D-H parameter table:

```bash
python3 -m src.main dh-table
```

Compute forward kinematics:

```bash
python3 -m src.main fk --joints 0 -1.5708 1.5708 -1.5708 -1.5708 0
```

Execute the pick-and-place workflow:

```bash
python3 -m src.main pick-and-place --planner quintic
```

Run the trajectory visualisation:

```bash
python3 -m src.live_demo_visualizer --planner quintic
```

**Note on Operational Modes:** The pick-and-place and visualisation commands operate in standalone virtual mode when CoppeliaSim is unavailable. This mode utilizes a simplified kinematic representation (5 cm proximity grasp threshold) rather than a dynamic physics engine. Live CoppeliaSim integration has not been independently verified in this QA audit.

## Experimental Results & QA Validation Status

The repository includes experimental outputs evaluating kinematics and trajectory-planning implementations.

### Verified Numerical Results (from CSV files)

- **Inverse Kinematics (`results/metrics.csv`):**
  - Total trials evaluated: 100
  - Successful convergence: 81 trials (81.0% convergence rate)
  - Unconverged trials: 19 trials (19.0%)
  - Mean Cartesian position error (successful trials): **0.0462 mm** ($46.2\ \mu\text{m}$)
  - Maximum Cartesian position error (successful trials): **0.0996 mm** ($99.6\ \mu\text{m}$)
  - Mean solver computation time (all 100 trials): **9.67 ms** (~5.57 ms among successful trials)
  - Mean DLS iterations (successful trials): **~26.1 iterations**

- **Trajectory Benchmark (`results/comparison.csv`):**
  - **Trapezoidal (LSPB):** Duration 1.53 s, $C^1$ continuity (continuous position and velocity; acceleration has step discontinuities at blending boundaries), computed jerk metric: **414.742**
  - **Cartesian SLERP:** Duration 3.00 s, task-space linear $C^1$, computed jerk metric: **48.6895**
  - **Quintic Polynomial:** Duration 3.00 s, mathematical $C^2$ continuity, computed jerk metric: **7.913**
  - **Cubic Polynomial:** Duration 3.00 s, $C^1$ continuity, lowest computed jerk metric: **1.545**
  - **Jerk Metric Reduction:** The quintic polynomial reduces the computed jerk metric by **98.1%** compared with trapezoidal LSPB. Note that Cubic exhibits the lowest computed jerk metric, and these figures reflect mathematical trajectory derivatives rather than measured physical vibration.

### Verification Levels

| Subsystem / Module | Source Inspection | Syntax Validation | Standalone Execution | Functional / Integration Testing | Status Summary |
|---|---|---|---|---|---|
| D-H Parameters (`src.dh_parameters`) | PASSED | PASSED | VERIFIED | VERIFIED (Kinematic) | Mathematically verified standard D-H table |
| Forward Kinematics (`src.forward_kinematics`) | PASSED | PASSED | VERIFIED | VERIFIED (Kinematic) | Closed-form transform and Jacobian calculations verified |
| Inverse Kinematics (`src.inverse_kinematics`) | PASSED | PASSED | VERIFIED | VERIFIED (Kinematic) | 81% convergence on 100 random trials; sub-0.1 mm accuracy on success |
| Trajectory Planner (`src.trajectory_planner`) | PASSED | PASSED | VERIFIED | VERIFIED (Kinematic) | Cubic ($C^1$), Quintic ($C^2$), LSPB ($C^1$), SLERP verified |
| Motion Controller (`src.motion_controller`) | PASSED | PASSED | VERIFIED | NOT VERIFIED (Hardware) | Configured 50 Hz waypoint interval (20 ms; real-time execution not guaranteed); no tracking-error threshold check |
| Gripper Controller (`src.gripper_controller`) | PASSED | PASSED | VERIFIED (Virtual) | NOT VERIFIED (Physics) | Returns True on open/close; no force/contact feedback |
| Pick-and-Place (`src.pick_and_place`) | PASSED | PASSED | VERIFIED (Virtual) | NOT VERIFIED (Physics) | Scripted 10-stage execution pipeline verified in virtual mode |
| Robot Connection (`src.robot_connection`) | PASSED | PASSED | VERIFIED (Fallback) | NOT VERIFIED (Live Sim) | Automatic fallback verified; live CoppeliaSim connection unverified |
| Automated Test Suite (`tests/`) | N/A | N/A | NOT RUN | NOT RUN | No committed `tests/` directory; `pytest` collected 0 items |

### Available Result Artifacts

- `results/metrics.csv` — 100-trial empirical IK data
- `results/comparison.csv` — comparative trajectory data
- `results/plots/` — publication plots (D-H frames, joint profiles, Cartesian paths, IK errors, trajectory comparisons)

## Documentation

For additional technical details, refer to:

- [Project Overview](docs/project_overview.md)
- [D-H Parameters](docs/dh_parameters.md)
- [System Architecture](docs/system_architecture.md)
- [Technical References](docs/references.md)
- [Viva Question Bank](docs/VIVA_QUESTION_BANK.md)

The detailed project report and presentation are available in their respective directories.

## Team

| Name | SAP ID | Responsibility |
|---|---:|---|
| Lakshay Dahiya | 500121078 | Project Lead and System Integration |
| Suraj Singh | 500122962 | Simulation and Scene Setup |
| Sudhanshu Kumar | 500125146 | Kinematics and Literature Review |
| Abhay Chand Thakur | 500122020 | Trajectory Experiments and Results |
| Khushi | 500122966 | Quality Assurance and Validation |

## Academic Information

**Course:** CSAI4014 – Algorithms for Intelligent Systems and Robotics  
**Programme:** B.Tech CSE (AI & ML)  
**Semester:** VII  
**Project:** P02 – 6-DOF Robotic Arm Pick-and-Place using D-H Kinematics  
**Group:** G04  
**Batch:** B3  
**Institution:** UPES, Dehradun

---

<p align="center">
  <strong>From mathematical modelling to robotic manipulation.</strong><br>
  A practical exploration of kinematics, motion planning and intelligent robotics.
</p>
