# PROJECT AUDIT: AISR 6-DOF Robotic Arm Pick-and-Place using D-H Kinematics

**Course:** CSAI4014 – Algorithms for Intelligent Systems and Robotics
**Project ID:** P02 | **Group ID:** G04 | **Batch:** B3
**Audit Date:** 19 November 2026 (Updated QA & Validation Audit)
**Lead Coordinator:** Lakshay Dahiya (SAP ID: 500121078)
**QA & Validation Lead:** Khushi (SAP ID: 500122966)

---

## 1. System Inventory and Verification Levels

All subsystems in the repository have been inspected and audited across four specific verification levels:
- **Source Inspection:** Static examination of Python source code structure, imports, and logic.
- **Syntax Validation:** Automated compilation via `python -m py_compile`.
- **Standalone Execution:** Running individual modules in isolated Python CLI sessions without external simulator services.
- **Functional / Integration Testing:** Automated test discovery via `pytest` and dynamic closed-loop verification with physical or simulator feedback.

### Detailed Verification Matrix

| Subsystem / Module | Source File | Source Inspection | Syntax Validation | Standalone Execution | Functional / Integration Testing | Status Summary |
|---|---|---|---|---|---|---|
| D-H Parameters | `src/dh_parameters.py` | PASSED | PASSED | VERIFIED | VERIFIED (Kinematic) | Correct link offsets and frame angles for UR5. |
| Forward Kinematics | `src/forward_kinematics.py` | PASSED | PASSED | VERIFIED | VERIFIED (Kinematic) | Transformation matrix composition and 6x6 geometric Jacobian verified. |
| Inverse Kinematics | `src/inverse_kinematics.py` | PASSED | PASSED | VERIFIED | VERIFIED (Kinematic) | Closed-form Pieper and DLS numerical solver; 81% convergence on 100 trials. |
| Trajectory Planner | `src/trajectory_planner.py` | PASSED | PASSED | VERIFIED | VERIFIED (Kinematic) | Cubic ($C^1$), Quintic ($C^2$), LSPB ($C^1$), SLERP profiles generate valid waypoints. |
| Motion Controller | `src/motion_controller.py` | PASSED | PASSED | VERIFIED | NOT VERIFIED (Hardware) | Dispatches waypoints at configured 50 Hz interval (20 ms; real-time execution not guaranteed); no tracking-error threshold check. |
| Gripper Controller | `src/gripper_controller.py` | PASSED | PASSED | VERIFIED (Virtual) | NOT VERIFIED (Physics) | Returns `True` on open/close without physical contact force feedback. |
| Pick-and-Place Engine | `src/pick_and_place.py` | PASSED | PASSED | VERIFIED (Virtual) | NOT VERIFIED (Physics) | Scripted 10-stage execution pipeline verified in virtual mode. |
| Robot Connection Bridge | `src/robot_connection.py` | PASSED | PASSED | VERIFIED (Fallback) | NOT VERIFIED (Live Sim) | Falls back to internal virtual mode; live CoppeliaSim unverified in QA environment. |
| Benchmark Engine | `src/benchmark_experiments.py`| PASSED | PASSED | VERIFIED | VERIFIED (Artifacts) | Produced verified CSV outputs (`metrics.csv`, `comparison.csv`) and figures. |
| Automated Test Suite | `tests/` directory | FAILED | N/A | NOT RUN | NOT RUN | No committed `tests/` directory; `pytest` collected 0 items. |

---

## 2. Confirmed & Verified Numerical Results

All reported figures are confirmed against the repository's empirical CSV artifacts:

### Inverse Kinematics Benchmarks (`results/metrics.csv`)
- **Total Tested Poses:** 100 random task-space poses within the workspace envelope.
- **Successful Convergences:** 81 poses (IK convergence rate = **81.0%**).
- **Failed Convergences:** 19 poses (19.0% did not satisfy the tolerance within 150 iterations).
- **Mean Cartesian Position Error (Successful Trials):** **0.0462 mm** ($46.2\ \mu\text{m}$).
- **Maximum Cartesian Position Error (Successful Trials):** **0.0996 mm** ($99.6\ \mu\text{m}$).
- **Mean Orientation Error (Successful Trials):** **0.0140 mrad**.
- **Mean Solve Time (Across all 100 trials):** **9.67 ms** per pose.
- **Mean Solve Time (Successful trials):** **~5.57 ms** per pose.
- **Mean DLS Iterations (Successful trials):** **~26.1 iterations**.

### Trajectory Smoothness Comparison (`results/comparison.csv`)
- **Trapezoidal LSPB:** Duration 1.53 s, $C^1$ continuity (continuous position and velocity; acceleration has step discontinuities at blending boundaries), computed jerk metric: **414.742**.
- **Cartesian Straight-Line SLERP:** Duration 3.00 s, task-space linear $C^1$, computed jerk metric: **48.6895**.
- **Joint Quintic Polynomial:** Duration 3.00 s, mathematical $C^2$ continuity, computed jerk metric: **7.913**.
- **Joint Cubic Polynomial:** Duration 3.00 s, $C^1$ continuity, computed jerk metric: **1.545**.
- **Relative Comparison:** The quintic polynomial trajectory achieves a **98.1% reduction in computed jerk metric** compared with trapezoidal LSPB ($414.742 \to 7.913$). Cubic polynomial achieves the lowest computed jerk metric among all planners.
- *Clarification:* These values represent the analytical cost metric $\int \|\dddot{q}(t)\|^2 dt$ computed from trajectory polynomials, not physical accelerometer measurements or mechanical vibration readings.

---

## 3. Known Technical Limitations & Source-Code Findings

The QA audit identified the following specific architectural and implementation limits:

1. **No Committed Test Suite:** The repository contains no `tests/` directory or committed pytest files. `pytest` executes with exit code 1 (`collected 0 items`).
2. **Simplified Virtual Kinematic Mode:** Standalone execution operates using an internal virtual kinematic mode rather than a dynamic rigid-body physics simulator.
3. **Kinematic Proximity Grasping:** The virtual grasp mechanism operates via a 5 cm Cartesian proximity threshold between the tool flange and the target object, rather than simulated physical friction or jaw contact dynamics.
4. **Unchecked Gripper Confirmation:** `gripper.open()` and `gripper.close()` return `True` unconditionally; `gripper.status()` is not queried during state machine execution.
5. **Ignored Trajectory Return Codes:** In `pick_and_place.py`, the boolean return values of trajectory execution calls are not evaluated to verify stage completion before advancing.
6. **No Explicit Tracking-Error Threshold:** The motion controller dispatches waypoints sequentially at configured 50 Hz intervals (20 ms; real-time execution not guaranteed) without halting on excessive joint tracking error.
7. **Absence of Collision Detection:** No geometric collision checking or obstacle avoidance was found in the inspected Python source code.
8. **Scripted Mission Sequencing:** The pick-and-place state machine reports success upon completing its 10-stage scripted sequence without independent closed-loop physical confirmation of payload delivery.
9. **Unverified Live CoppeliaSim Connection:** Live ZeroMQ socket communication with a running CoppeliaSim instance has not been independently verified during this QA audit; the system automatically defaulted to standalone virtual mode.
10. **Timestep Characterization:** 50 Hz represents the configured software control and waypoint interval (20 ms; real-time wall-clock execution is not guaranteed as `execute_trajectory()` defaults to `real_time=False`); simulator physics timestep has not been established as 20 ms.

---

## 4. Software Dependencies and Deliverables

### Dependencies
- **Core Environment:** Python 3.12+ (NumPy, SciPy, Matplotlib, Pandas, SymPy, PyZMQ).
- **Document Generation:** `reportlab` (>= 5.1.0) and `pypdf` (>= 7.1.0) installed for report and presentation compilation.

### Verified Deliverables
- **Presentation Deck:** `presentation/project_presentation.pdf` (17 slides, verified free of unsupported unit test, reliability, or vibration claims).
- **Academic Project Report:** `report/project_report.pdf` (formal report conforming to course guidelines, verified accurate numerical metrics and limitations).
- **Original Backups Preserved:** `presentation/project_presentation_backup.pdf` and `report/project_report_backup.pdf`.
