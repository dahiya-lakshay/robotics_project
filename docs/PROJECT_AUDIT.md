# PROJECT AUDIT: AISR 6-DOF Robotic Arm Pick-and-Place using D-H Kinematics

**Course:** CSAI4014 – Algorithms for Intelligent Systems and Robotics  
**Project ID:** P02 | **Group ID:** G04 | **Batch:** B3  
**Audit Date:** 17 November 2026  
**Auditor / Coordinator:** Lakshay Dahiya (SAP ID: 500121078)  

---

## 1. What Already Exists

1. **Workspace Root:** `/Users/lakshaydahiya/Developer/robotics_project`
2. **Environment & Runtimes:**
   - Operating System: macOS (Darwin arm64)
   - Python Runtime: Python 3.11.6 (`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`)
   - Git Version: 2.x (`/opt/homebrew/bin/git`)
   - Initialized Git repository with clean working tree.
3. **Core Libraries Installed & Verified:**
   - Numerical Computing: `numpy` (2.4.6), `scipy` (1.17.1), `sympy` (1.14.0)
   - Data & Plotting: `pandas` (3.1.1), `matplotlib` (3.11.2)
   - Simulator Communication: `pyzmq` (27.3.0), `cbor` (1.0.0), `coppeliasim-zmqremoteapi-client` (2.0.4)
4. **Project Scaffolding:**
   - Directory hierarchy established (`docs/`, `simulation/`, `src/`, `tests/`, `results/plots/`, `screenshots/`, `report/`, `presentation/`).
   - Standard `.gitignore` and `requirements.txt` generated.

---

## 2. What Is Working

- **Python Runtime & Scientific Stack:** Verified via sandboxed execution; matrix mathematics, symbolic computation, numerical root-finding, and data visualization libraries load without error.
- **Remote API Client & Serializer:** `coppeliasim-zmqremoteapi-client` and `cbor` are properly linked to Python 3.11.
- **Repository Architecture:** Directory layout strictly matches the project specification.

---

## 3. What Is Incomplete

- **Robot Model Selection:**
  - *Option A: Universal Robots UR5.* 6-DOF, revolute joints, planar arm with spherical wrist (3 intersecting wrist axes: joint 4, 5, 6), well-established standard Denavit-Hartenberg parameterization. Readily available in CoppeliaSim model repository (`robots/non-mobile/UR5.ttm`).
  - *Option B: ABB IRB 140.* 6-DOF industrial articulated arm.
  - *Decision:* Universal Robots UR5 is selected as the primary manipulator. Its physical geometry, link offsets ($d_1, a_2, a_3, d_4, d_5, d_6$), and spherical wrist structure provide clean analytical and numerical D-H formulations, zero ambiguity in academic literature, and full compatibility with CoppeliaSim's standard assets.

---

## 4. What Is Missing

1. **Mathematical & Kinematics Modules (`src/`):**
   - `dh_parameters.py`: Standard D-H parameter definitions, physical robot link constants, and coordinate frame derivations.
   - `forward_kinematics.py`: Homogeneous transformation matrices $T_{i-1}^i$, cumulative forward kinematics $T_0^6$, position vector and rotation matrix extraction, roll-pitch-yaw Euler angle conversions.
   - `inverse_kinematics.py`: Dual-mode IK engine:
     - Analytical geometric IK (Pieper-style closed form for spherical wrists).
     - Numerical iterative Jacobian IK (Damped Least Squares / Levenberg-Marquardt with null-space optimization and joint limit constraints).
   - `trajectory_planner.py`: Joint-space trajectory generators (cubic and quintic polynomials) and Cartesian-space linear path with trapezoidal velocity profiling (LSPB).
   - `motion_controller.py`: Low-level waypoint streaming, velocity/acceleration limit enforcement, and simulation synchronization.
   - `gripper_controller.py`: Suction/two-finger parallel gripper actuation interface, proximity sensing, and object grasping state machine.
   - `pick_and_place.py`: Master state machine orchestrating home configuration $\rightarrow$ pre-pick $\rightarrow$ pick descend $\rightarrow$ grasp $\rightarrow$ post-pick lift $\rightarrow$ transport $\rightarrow$ pre-place $\rightarrow$ place descend $\rightarrow$ release $\rightarrow$ retract $\rightarrow$ home.
   - `robot_connection.py`: Robust ZeroMQ Remote API wrapper with fallback/mock mode for standalone verification.
2. **Verification Suite (`tests/`):**
   - Comprehensive unit tests covering FK precision, FK-IK closure ($q \rightarrow T \rightarrow q^* \rightarrow T \approx T$), joint limit enforcement, singularity avoidance, and trajectory boundary condition satisfaction.
3. **Empirical Benchmarks & Experimental Output (`results/`):**
   - Performance evaluation scripts measuring end-effector positioning error ($\text{mm}$), orientation error ($\text{rad}$), trajectory execution time ($s$), joint angular velocities, and comparison between joint-space vs. Cartesian-space planners.
   - Auto-generated CSV files (`metrics.csv`, `comparison.csv`) and publication-quality Matplotlib figures (`results/plots/`).
4. **CoppeliaSim Scene Documentation & Asset Instructions (`simulation/`):**
   - Scene setup documentation (`robot_configuration.md`), object dimension definitions, target drop zone coordinates, and Lua/Python interface instructions.
5. **Academic Report & Presentation (`report/`, `presentation/`):**
   - Comprehensive 25–35 page formal academic report conforming to the faculty rubric.
   - 17-slide high-density technical presentation deck.

---

## 5. Technical Risks & Mitigation Strategies

| Risk | Impact | Likelihood | Mitigation Strategy |
|---|---|---|---|
| **CoppeliaSim GUI Availability** | Simulator GUI or specific binary might not be running continuously during automated CLI testing. | High | Implement dual-mode architecture in `robot_connection.py`: a live ZeroMQ connection to CoppeliaSim when the server is active, and a physics-consistent internal simulation engine for automated headless testing and regression evaluation. |
| **Kinematic Singularities** | Division by zero or explosive joint velocities near wrist/shoulder singularities during numerical IK. | Medium | Use Damped Least Squares (DLS / Levenberg-Marquardt) with adaptive damping factor $\lambda^2$: $J^* = J^T (J J^T + \lambda^2 I)^{-1}$. Enforce joint velocity saturation limits. |
| **Multiple IK Solutions & Branch Jumping** | A 6-DOF arm has up to 8 analytical solutions; naive IK might pick configurations requiring large joint jumps between consecutive waypoints. | Medium | Implement nearest-neighbor configuration selector using weighted Euclidean joint distance metric: $q^* = \arg\min_k \|q_k - q_{\text{current}}\|_W$. |
| **Numerical Round-off in Rotation Matrices** | Cumulative matrix products can drift from $SO(3)$ orthonormality. | Low | Re-orthonormalize rotation matrices using SVD or Gram-Schmidt QR decomposition during trajectory validation. |

---

## 6. Software & Mathematical Dependencies

```text
Python 3.11+
├── numpy (>= 1.25.0)       # Core matrix operations, vector math, homogeneous transformations
├── scipy (>= 1.11.0)       # Numerical optimization, spatial rotations, interpolation
├── matplotlib (>= 3.8.0)   # Scientific plotting, trajectory visualization, 3D kinematic diagrams
├── pandas (>= 2.1.0)       # Experimental metric tabularization and CSV export
├── sympy (>= 1.12.0)       # Analytical Jacobian derivation and symbolic D-H verification
├── pyzmq (>= 25.1.0)       # ZeroMQ messaging substrate
├── cbor (>= 1.0.0)         # Binary object serialization for CoppeliaSim Remote API
└── coppeliasim-zmqremoteapi-client (>= 2.0.4) # Official Python bridge to CoppeliaSim
```

---

## 7. Recommended Execution Order

1. **Step 1 — Module M2 (Denavit-Hartenberg Kinematics):**
   Implement `src/dh_parameters.py` with the standard D-H parameter table for Universal Robots UR5.
2. **Step 2 — Module M3 (Forward Kinematics):**
   Implement `src/forward_kinematics.py`, transformation matrix generator, forward kinematics pipeline, and pose extractors (position $[x, y, z]^T$, rotation matrix $R$, Euler angles roll-pitch-yaw).
3. **Step 3 — Module M4 (Inverse Kinematics):**
   Implement `src/inverse_kinematics.py` featuring analytical geometric closed-form solver and Damped Least Squares (DLS) numerical Jacobian solver.
4. **Step 4 — Module M5 (Trajectory Planning):**
   Implement `src/trajectory_planner.py` with joint-space cubic/quintic polynomial interpolation and Cartesian linear interpolation with trapezoidal velocity profiles.
5. **Step 5 — Module M6 (Controller & Remote API Communication):**
   Implement `src/robot_connection.py`, `src/motion_controller.py`, `src/gripper_controller.py`, and `src/pick_and_place.py`.
6. **Step 6 — Unit Testing & Validation (`tests/`):**
   Write and execute `test_forward_kinematics.py`, `test_inverse_kinematics.py`, and `test_trajectory.py` using `pytest`.
7. **Step 7 — Module M7 (Empirical Experiments & Plot Generation):**
   Execute trajectory experiments, log positioning errors, compare joint-space vs. Cartesian trajectories, export `metrics.csv`, `comparison.csv`, and generate publication plots in `results/plots/`.
8. **Step 8 — Simulation Scene Setup & Documentation:**
   Document exact CoppeliaSim scene parameters, object placement, gripper configuration, and connection protocol in `simulation/robot_configuration.md`.
9. **Step 9 — Documentation & Deliverables:**
   Compile comprehensive academic report (`report/project_report.md` / PDF), presentation deck (`presentation/project_presentation.md` / PDF), contribution register, and master GitHub `README.md`.
