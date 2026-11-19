# AISR 6-DOF Robotic Arm Pick-and-Place using D-H Kinematics
## Project Overview & Mission Statement

**Course Code:** CSAI4014 – Algorithms for Intelligent Systems and Robotics  
**Academic Degree:** B.Tech Computer Science & Engineering (Artificial Intelligence & Machine Learning)  
**Semester:** VII  
**Project ID:** P02  
**Group ID:** G04  
**Batch:** B3  
**Submission Deadline:** 18 November 2026  

---

## 1. Team Composition & Role Matrix

| S. No. | Student Name | SAP ID | Primary Engineering Role | Focus Modules |
|---|---|---|---|---|
| 16 | **Suraj Singh** | 500122962 | Simulation & Scene Engineer | CoppeliaSim scene configuration, joint handle hierarchy, physics parameters |
| 17 | **Sudhanshu Kumar** | 500125146 | Kinematics & Literature Lead | Theoretical D-H derivations, literature review, mathematical validation |
| 18 | **Abhay Chand Thakur** | 500122020 | Trajectory & Experiments Specialist | Trajectory benchmarking, data acquisition, CSV metrics & comparative analysis |
| 19 | **Lakshay Dahiya** | 500121078 | Coordinator & Systems Architect | Kinematics implementation, ZeroMQ bridge, state machine integration, master testing |
| 20 | **Khushi** | 500122966 | Quality Assurance & Validation Lead | Pick-and-place testing, boundary conditions, visualization plots, documentation |

---

## 2. Project Executive Summary

This project delivers a mathematically rigorous, fully automated six-degree-of-freedom (6-DOF) robotic manipulation system executing pick-and-place operations in industrial simulation. Utilizing the Universal Robots UR5 articulated manipulator, the project bridges formal theoretical robotics algorithms with software engineering practices.

### Core Technical Pillars:
1. **Mathematical Kinematics Engine:**
   - Standard Denavit-Hartenberg (D-H) modeling of 6 revolute links.
   - Forward Kinematics ($T_0^6$) generating homogeneous transformations, position vectors, and ZYX Euler angles.
   - 6x6 Geometric Jacobian $J(q)$ computation and Yoshikawa manipulability tracking.
   - Dual-mode Inverse Kinematics incorporating closed-form analytical decoupling and Damped Least Squares (DLS / Levenberg-Marquardt) iterative numerical optimization with null-space singularity damping.
2. **Trajectory Generation & Smoothness Optimization:**
   - Joint-space cubic ($C^1$) and quintic ($C^2$) polynomial trajectory planning.
   - Linear Segments with Parabolic Blends (LSPB) trapezoidal velocity profiling.
   - Cartesian-space straight-line trajectory generation with SLERP matrix Lie algebra orientation interpolation.
   - Quantitative jerk metric analysis $\int \|\dddot{q}\|^2 dt$.
3. **Simulation Bridge & Actuation:**
   - Python ZeroMQ Remote API client communicating synchronously with CoppeliaSim at 50 Hz control loops.
   - 10-stage sequential pick-and-place state machine with pre-approach stances, contact detection, gripper control, and home restoration.
   - Autonomous high-fidelity standalone virtual execution mode ensuring 100% deterministic reproducibility across development platforms.

---

## 3. Syllabus Mapping (CSAI4014 Rubric Alignment)

| AISR Curriculum Module | Applied Project Implementation | Verifiable Artifact |
|---|---|---|
| **Coordinate Frames & Spatial Transformations** | Homogeneous $4 \times 4$ transformation matrices, $SO(3)$ rotation matrices, ZYX Euler angle parameterization | `src/forward_kinematics.py`, `docs/dh_parameters.md` |
| **Denavit-Hartenberg (D-H) Representation** | Systematic derivation of 4 kinematic parameters ($a_i, \alpha_i, d_i, \theta_i$) for all 6 revolute axes | `src/dh_parameters.py`, `results/plots/fig1_dh_kinematic_frames.png` |
| **Forward Kinematics Analysis** | Serial product $T_0^6 = \prod_{i=1}^6 T_{i-1}^i$, link frame extraction, and pose reconstruction | `src/forward_kinematics.py`, `tests/test_forward_kinematics.py` |
| **Differential Kinematics & Jacobians** | 6x6 geometric Jacobian relating joint rates to end-effector twist $\begin{bmatrix} v \\ \omega \end{bmatrix} = J(q)\dot{q}$, singularity detection | `src/forward_kinematics.py` (`compute_geometric_jacobian`) |
| **Inverse Kinematics & Singularity Handling** | Analytical decoupling (Pieper's criteria) & Damped Least Squares $(J^T(JJ^T + \lambda^2 I)^{-1})$ | `src/inverse_kinematics.py`, `tests/test_inverse_kinematics.py` |
| **Trajectory Planning** | Polynomial boundary-value interpolation, velocity profiling, and jerk smoothness minimization | `src/trajectory_planner.py`, `results/comparison.csv`, `results/plots/fig2_trajectory_joint_profiles.png` |
| **Robotic Control & Sensor Integration** | Synchronous ZeroMQ closed-loop stepping, waypoint dispatching, and end-effector gripper actuation | `src/robot_connection.py`, `src/motion_controller.py`, `src/pick_and_place.py` |
