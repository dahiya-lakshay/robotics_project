# Complete Member-by-Member Presentation Speaker Script

**Course:** CSAI4014 – Algorithms for Intelligent Systems and Robotics  
**Project:** P02 — 6-DOF Robotic Arm Pick-and-Place using D-H Kinematics  
**Group:** G04 | **Batch:** B3  
**Target Duration:** 20:00 Minutes (Strict Faculty Range: 18:00 – 22:00 Minutes)  
**Slide Deck:** `presentation/project_presentation.pdf` (17 Slides)  

---

## Master Time Budget & Presenter Allocation

| Slide | Title | Presenter | Allocated Time | Cumulative Clock |
|---|---|---|---|---|
| **1** | Title Slide & Individual Introductions | **Suraj Singh (M1)** + All | 1 min 30 sec | 00:00 – 01:30 |
| **2** | Problem Statement & Industrial Need | **Suraj Singh (M1)** | 1 min 15 sec | 01:30 – 02:45 |
| **3** | Measurable Project Objectives | **Suraj Singh (M1)** | 1 min 15 sec | 02:45 – 04:00 |
| **4** | Existing Solutions & The Technical Gap | **Sudhanshu Kumar (M2)** | 1 min 15 sec | 04:00 – 05:15 |
| **5** | Project Novelty (Mandatory Points) | **Sudhanshu Kumar (M2)** | 1 min 15 sec | 05:15 – 06:30 |
| **6** | CSAI4014 Syllabus Mapping | **Sudhanshu Kumar (M2)** | 1 min 15 sec | 06:30 – 07:45 |
| **7** | System Architecture | **Abhay Chand Thakur (M3)** | 1 min 15 sec | 07:45 – 09:00 |
| **8** | Robot & Environment Model | **Abhay Chand Thakur (M3)** | 1 min 15 sec | 09:00 – 10:15 |
| **9** | Algorithm 1: Forward Kinematics & D-H | **Abhay Chand Thakur (M3)** | 1 min 15 sec | 10:15 – 11:30 |
| **10** | Algorithm 2: IK Solvers & Trajectory | **Lakshay Dahiya (M4)** | 1 min 15 sec | 11:30 – 12:45 |
| **11** | Simulation Setup & ZeroMQ Interface | **Lakshay Dahiya (M4)** | 1 min 00 sec | 12:45 – 13:45 |
| **12** | Live Demonstration (Screen Share) | **Lakshay Dahiya (M4)** | 4 min 15 sec | 13:45 – 18:00 |
| **13** | Results 1: Kinematic Precision | **Khushi (M5)** | 1 min 00 sec | 18:00 – 19:00 |
| **14** | Results 2: Trajectory Benchmark & Jerk | **Khushi (M5)** | 1 min 00 sec | 19:00 – 20:00 |
| **15** | Team Technical Contributions | **Khushi (M5)** | 1 min 00 sec | 20:00 – 21:00 |
| **16** | Conclusion & Industrial Deployment | **All Members (M1 – M5)** | 0 min 45 sec | 21:00 – 21:45 |
| **17** | End Slide & Q&A Close | **Lakshay Dahiya (Lead)** | 0 min 15 sec | 21:45 – 22:00 |

---

## PART 1: MEMBER 1 — SURAJ SINGH (SAP ID: 500122962)
**Total Stage Time: 04:00 Minutes (00:00 – 04:00)**

### Slide 1: Title Slide & Introductions (00:00 – 01:30)
*(Screen shows Slide 1: Title, Project P02, Group G04, Batch B3, Team Table)*

> **Suraj Singh (00:00 – 00:30):**  
> *"Good day respected faculty and evaluators. Welcome to our final project presentation for course CSAI4014, Algorithms for Intelligent Systems and Robotics. We are Group G04 representing Batch B3, presenting Project P02 titled: **'6-DOF Robotic Arm Pick-and-Place using D-H Kinematics'**, realized on the Universal Robots UR5 manipulator. I am Suraj Singh, SAP ID 500122962, and my focus was configuring the CoppeliaSim virtual scene, joint handles, and collision environment. I now invite each of my group members to introduce themselves."*

- **Sudhanshu Kumar (00:30 – 00:45):**  
  *"Greetings everyone, I am Sudhanshu Kumar, SAP ID 500125146. My primary responsibilities encompassed the theoretical Denavit-Hartenberg derivations, literature review, and syllabus mapping."*
- **Abhay Chand Thakur (00:45 – 01:00):**  
  *"Hello respected faculty, I am Abhay Chand Thakur, SAP ID 500122020. I led the trajectory generation experiments, quantitative data acquisition over 100 trials, and comparative analysis."*
- **Lakshay Dahiya (01:00 – 01:15):**  
  *"Good day everyone, I am Lakshay Dahiya, SAP ID 500121078, coordinating Group G04. I engineered the pure-Python D-H kinematics engine, closed-form and DLS inverse kinematics solvers, ZeroMQ Remote API co-simulation bridge, and system integration."*
- **Khushi (01:15 – 01:30):**  
  *"Greetings respected evaluators, I am Khushi, SAP ID 500122966. My core work focused on pick-and-place workspace validation, edge-case testing, error convergence plotting, and academic report compilation."*

---

### Slide 2: Problem Statement & Industrial Need (01:30 – 02:45)
*(Screen shows Slide 2: Bullet points on Industrial Need, 6-DOF, Motion Quality)*

> **Suraj Singh:**  
> *"Moving to Slide 2, let us examine the fundamental problem and industrial motivation. In modern industrial automation—such as electronics manufacturing, automotive stamping, and pharmaceutical packaging—robotic arms must autonomously pick components from feed stations and transfer them to target positions with sub-millimeter precision.  
> 
> The central technical challenge is to achieve this without human manual teaching, without singular configuration lockups, and without collisions. To achieve full spatial manipulation in three dimensions, a robot requires 6 degrees of freedom: 3 translational axes (X, Y, Z) to locate the point in space, and 3 rotational axes (Roll, Pitch, Yaw) to orient the gripper perpendicular to the workpiece surface.  
> 
> Furthermore, real industrial manipulators suffer from motion quality issues: abrupt changes in acceleration introduce mechanical jerk, which creates gearbox vibrations, premature motor wear, and dropped payloads. Our project solves this through analytical D-H kinematics coupled with jerk-minimized polynomial trajectory planning."*

---

### Slide 3: Measurable Project Objectives (02:45 – 04:00)
*(Screen shows Slide 3: 5 Measurable Objectives)*

> **Suraj Singh:**  
> *"On Slide 3, we established five concrete, measurable engineering objectives to evaluate our project:  
> 
> 1. **D-H Mathematical Modeling:** Establish the standard Denavit-Hartenberg parameter table for the Universal Robots UR5 serial manipulator from link geometry.  
> 2. **Pure-Python Kinematics:** Implement independent forward and inverse kinematics engines achieving an end-effector positioning accuracy under 0.1 millimeters.  
> 3. **Jerk-Minimized Trajectories:** Implement quintic polynomial trajectories enforcing continuous acceleration and zero jerk at trajectory boundaries.  
> 4. **Synchronous Co-Simulation:** Establish a 50 Hz lockstep client-server link with CoppeliaSim using the ZeroMQ Remote API with non-blocking failover.  
> 5. **High Reliability:** Achieve a 100% success rate across an automated 10-stage pick-and-place state machine.  
> 
> I now hand over the presentation to Sudhanshu Kumar to discuss existing solutions and our novelty."*

---

## PART 2: MEMBER 2 — SUDHANSHU KUMAR (SAP ID: 500125146)
**Total Stage Time: 03:45 Minutes (04:00 – 07:45)**

### Slide 4: Existing Solutions & The Technical Gap (04:00 – 05:15)
*(Screen shows Slide 4: Bullet points and comparison table of Analytical vs Numerical vs Hybrid)*

> **Sudhanshu Kumar:**  
> *"Thank you Suraj. Respected faculty, examining Slide 4, classical literature by Denavit, Hartenberg, Craig, and Siciliano establishes matrix transformation conventions for open serial kinematic chains. However, in typical robotics laboratory setups, students rely on CoppeliaSim's built-in Inverse Kinematics plugin. This operates as a black-box, completely concealing the mathematical matrix products, Jacobian inversion, and frame transformations.  
> 
> Moreover, traditional industrial robots often default to trapezoidal velocity profiles. As shown in our comparison table, while trapezoidal profiles are easy to compute, their instantaneous steps in acceleration produce severe mechanical jerk.  
> 
> Looking at kinematics solvers, purely analytical solvers fail when the wrist is close to singular alignments, whereas purely numerical solvers are computationally slow and sensitive to initial guesses. This gap motivated our hybrid architecture, combining closed-form Pieper geometric decoupling with an adaptive Damped Least Squares solver."*

---

### Slide 5: Project Novelty — Mandatory Contributions (05:15 – 06:30)
*(Screen shows Slide 5: 4 Distinct Novelty Points)*

> **Sudhanshu Kumar:**  
> *"Turning to Slide 5, our work introduces four distinct, mandatory engineering contributions:  
> 
> 1. **Independent Pure-Python D-H Engine:** All 4x4 homogeneous transformation matrices, the 6x6 geometric Jacobian, and forward/inverse kinematics equations are formulated in Python from first principles, completely external to the simulator.  
> 2. **Hybrid Analytical and DLS Solver:** We combine closed-form Pieper spherical wrist decoupling with an adaptive Levenberg-Marquardt Damped Least Squares optimizer. When manipulability drops near singularities, dynamic damping ensures stable convergence without mathematical blowups.  
> 3. **98.1% Mechanical Jerk Reduction:** By generating quintic polynomials with $C^2$ continuity, we reduced the integral jerk cost from 414.7 down to 7.9 compared to standard trapezoidal profiles.  
> 4. **Zero-Downtime Virtual Fallback:** We engineered a fast 200 ms TCP pre-probe. If CoppeliaSim is offline, the system seamlessly transitions to our internal physics-consistent virtual simulation engine, ensuring 100% automated test coverage."*

---

### Slide 6: CSAI4014 Syllabus Mapping (06:30 – 07:45)
*(Screen shows Slide 6: Table mapping AISR syllabus topics to project code)*

> **Sudhanshu Kumar:**  
> *"Slide 6 demonstrates the rigorous alignment of our project with the CSAI4014 syllabus across five core theoretical domains:  
> 
> - **Coordinate Frames & Transformations:** Applied via 4x4 homogeneous matrices in our serial kinematic chain module.  
> - **D-H Representation:** Formulated through standard parameters $(a, \alpha, d, \theta)$ to model the six revolute links of the UR5.  
> - **Differential Kinematics:** Implemented via the $6 \times 6$ geometric Jacobian matrix $V = J(q)\dot{q}$ to map joint rates to end-effector spatial twist and compute Yoshikawa manipulability.  
> - **Inverse Kinematics:** Realized through Damped Least Squares regularisation with Singularity Robust damping.  
> - **Trajectory Generation:** Applied through quintic polynomial interpolation to satisfy boundary constraints in velocity and acceleration.  
> 
> I now invite Abhay Chand Thakur to present our system architecture and robot models."*

---

## PART 3: MEMBER 3 — ABHAY CHAND THAKUR (SAP ID: 500122020)
**Total Stage Time: 03:45 Minutes (07:45 – 11:30)**

### Slide 7: System Architecture (07:45 – 09:00)
*(Screen shows Slide 7: Figure 0 System Architecture Block Diagram)*

> **Abhay Chand Thakur:**  
> *"Thank you Sudhanshu. Respected faculty, Slide 7 presents our overall system architecture block diagram. The software pipeline is structured into clean, decoupled layers:  
> 
> - The **Mission Planner** defines the 3D target coordinates for the pick and place operation.  
> - The **Trajectory Planner** interpolates smooth Cartesian waypoints and joint profiles using quintic polynomials.  
> - The **Kinematics Engine** computes the joint angles $\theta_1$ through $\theta_6$ for every waypoint via our hybrid analytical/DLS solver.  
> - The **Motion Controller** performs safety boundary checks and streams joint commands over the **ZeroMQ Remote API Bridge** to the CoppeliaSim physics environment at 50 Hz.  
> 
> Crucially, our architecture operates under synchronous lockstep control using `client.setStepping(True)`. This means CoppeliaSim's physics engine only advances by 50 milliseconds once our controller has delivered the next waypoint, guaranteeing deterministic reproducibility."*

---

### Slide 8: Robot & Environment Model (09:00 – 10:15)
*(Screen shows Slide 8: Figure 1 Kinematic Frames + UR5 Specs Table)*

> **Abhay Chand Thakur:**  
> *"Turning to Slide 8, on the left you see our 3D kinematic frame assignment diagram, and on the right our workstation layout.  
> 
> We chose the **Universal Robots UR5**, an industrial 6-DOF articulated manipulator with an 850 mm reach radius, a 5.0 kg payload capacity, and $\pm 0.1\text{ mm}$ repeatability. Its six revolute joints consist of a base yaw, shoulder pitch, elbow pitch, and a three-axis spherical wrist comprising wrist 1, wrist 2, and wrist 3.  
> 
> In our simulation scene, the robot stands at world origin $(0, 0, 0)$. The pick target is placed on the workstation table at $[0.35, 0.15, 0.05]\text{ m}$, and the destination target is located at $[0.10, 0.38, 0.05]\text{ m}$. To prevent collisions with the table and neighbouring fixtures, our controller enforces a pre-pick and pre-place clearance altitude of $+12\text{ cm}$. End-effector grasping is executed by a Robotiq RG2 parallel jaw gripper."*

---

### Slide 9: Algorithm 1: Forward Kinematics & D-H Modeling (10:15 – 11:30)
*(Screen shows Slide 9: D-H Transformation Rule, UR5 Geometry, Jacobian equation)*

> **Abhay Chand Thakur:**  
> *"Slide 9 details our mathematical formulation for Algorithm 1: Forward Kinematics. Under standard Denavit-Hartenberg convention, the relative homogeneous transformation between frame $i-1$ and frame $i$ is formulated as:  
> $T_{i-1}^i = \text{Rot}(z, \theta_i) \cdot \text{Trans}(z, d_i) \cdot \text{Trans}(x, a_i) \cdot \text{Rot}(x, \alpha_i)$.  
> 
> For the UR5, the link lengths and offsets are: link offset $d_1 = 89.2\text{ mm}$, link length $a_2 = -425.0\text{ mm}$, $a_3 = -392.3\text{ mm}$, offset $d_4 = 109.2\text{ mm}$, $d_5 = 94.7\text{ mm}$, and end-effector tool offset $d_6 = 82.3\text{ mm}$.  
> 
> The global tool pose is obtained by serial chain multiplication: $T_0^6 = T_0^1 \cdot T_1^2 \cdot T_2^3 \cdot T_3^4 \cdot T_4^5 \cdot T_5^6$. From this $4 \times 4$ matrix, we extract the position vector $(p_x, p_y, p_z)$ and the Roll-Pitch-Yaw orientation Euler angles. We also derive the $6 \times 6$ geometric Jacobian relating joint angular velocities to spatial linear and angular velocities: $V = J(q)\dot{q}$.  
> 
> I now hand over the presentation to our group coordinator, Lakshay Dahiya, to discuss Algorithm 2, our simulation setup, and lead the live demonstration."*

---

## PART 4: MEMBER 4 — LAKSHAY DAHIYA (LEAD) (SAP ID: 500121078)
**Total Stage Time: 06:30 Minutes (11:30 – 18:00)**

### Slide 10: Algorithm 2: Inverse Kinematics & Trajectory Planning (11:30 – 12:45)
*(Screen shows Slide 10: Pieper Decoupling, Damped Least Squares equation, Quintic Trajectory)*

> **Lakshay Dahiya:**  
> *"Thank you Abhay. Respected faculty, on Slide 10 we present Algorithm 2: Inverse Kinematics and Trajectory Planning.  
> 
> The UR5 features three intersecting wrist axes, allowing us to implement Pieper's analytical decoupling. We first compute the wrist center position $p_w = p_{ee} - d_6 R [0, 0, 1]^T$, isolating the first three joint angles $(\theta_1, \theta_2, \theta_3)$ algebraically. The remaining spherical wrist joints $(\theta_4, \theta_5, \theta_6)$ are then extracted using Euler angle extraction from the residual rotation matrix $R_3^6$.  
> 
> However, when joint 5 approaches zero, the arm approaches a wrist singularity where the classical Jacobian determinant vanishes. To guarantee robustness, we engineered an adaptive Levenberg-Marquardt Damped Least Squares solver:  
> $\Delta q = J^T (J J^T + \lambda^2 I)^{-1} e$.  
> The damping parameter $\lambda$ dynamically scales based on Yoshikawa's manipulability index $w = \sqrt{\det(J J^T)}$. As $w \to 0$, $\lambda$ smoothly increases, ensuring joint increments remain strictly bounded.  
> 
> For trajectory planning, we compute a 5th-order (quintic) polynomial: $s(t) = a_0 + a_1 t + a_2 t^2 + a_3 t^3 + a_4 t^4 + a_5 t^5$, enforcing zero velocity and zero acceleration at both boundaries. This provides $C^2$ continuity, eliminating instantaneous acceleration steps."*

---

### Slide 11: Simulation Setup & ZeroMQ Interface (12:45 – 13:45)
*(Screen shows Slide 11: Platform Specs, ZeroMQ, Automated CLI Commands)*

> **Lakshay Dahiya:**  
> *"On Slide 11, we detail our simulation platform and co-simulation bridge. We interface Python 3.11 with CoppeliaSim Edu V4.3+ utilizing the ZeroMQ Remote API over TCP port 23000 with CBOR binary serialization.  
> 
> To prevent communication latency from destabilizing the controller, we enforce synchronous execution. The Python controller computes the kinematic waypoint, streams joint targets via `sim.setJointTargetPosition`, commands gripper actuation, and triggers the next simulation tick with `sim.step()`.  
> 
> We have packaged our software into standard, reproducible CLI commands: running `pytest tests/ -v` verifies our 11 unit tests, while `python3 -m src.main pick-and-place` executes the end-to-end mission.  
> 
> We now transition to Slide 12 for our Live Simulation Demonstration."*

---

### Slide 12: Live Demonstration Execution (13:45 – 18:00)
*(Screen shows Slide 12 briefly, then Lakshay switches screen share to Terminal & Simulation Dashboard)*

> **Lakshay Dahiya (13:45 – 14:45) — Unit Tests & Kinematics CLI:**  
> *"I am now switching my screen share to our live terminal environment. Respected evaluators, before running the pick-and-place sequence, we first demonstrate the mathematical validity of our engine by running our automated test suite:*
> 
> *(Lakshay types and runs):*  
> ```bash
> python3 -m pytest tests/ -v
> ```
> 
> *As seen on screen, all 11 unit tests pass in 0.15 seconds. This verifies transformation orthonormality, forward kinematics accuracy, DLS reachability, and quintic zero-acceleration boundary conditions.  
> 
> Next, we inspect our D-H table and forward kinematics at home stance:*
> 
> *(Lakshay types and runs):*  
> ```bash
> python3 -m src.main dh-table
> python3 -m src.main fk --joints 0 -1.5708 1.5708 -1.5708 -1.5708 0
> ```
> 
> *The output confirms the exact UR5 D-H parameters and computes the end-effector home coordinates at $[0.8172, 0.1915, -0.0055]\text{ m}$ with zero position error."*

> **Lakshay Dahiya & Suraj Singh (14:45 – 18:00) — 10-Stage Mission Execution:**  
> *"We now launch our interactive 3D live demonstration visualizer executing the full 10-stage pick-and-place mission:*
> 
> *(Lakshay types and runs):*  
> ```bash
> python3 -m src.live_demo_visualizer --planner quintic
> ```
> 
> *(Narrating live as the 3D arm and telemetry animate on screen):*  
> - **Stage 1 & 2 (Initialization & Home):** *The ZeroMQ client completes its handshake and the UR5 arm moves smoothly into its standard Home configuration: $[0, -90^\circ, +90^\circ, -90^\circ, -90^\circ, 0^\circ]$.*  
> - **Stage 3 & 4 (Target Localization & Pre-Pick Approach):** *The target workpiece is located at $[0.35, 0.15, 0.05]\text{ m}$. The arm elevates to a pre-pick stance $12\text{ cm}$ directly above the target with tool orientation pointing vertically downward $[180^\circ, 0^\circ, 0^\circ]$.*  
> - **Stage 5 & 6 (Descent & Grasp):** *The arm performs a controlled vertical descent along the tool z-axis down to $z = 0.05\text{ m}$. The Robotiq RG2 gripper closes, verifying contact and locking the payload.*  
> - **Stage 7 & 8 (Clearance Lift & Quintic Transfer):** *The arm ascends back to clearance height and executes a smooth $C^2$ continuous quintic transfer across the workspace to the pre-place stance at $[0.10, 0.38, 0.17]\text{ m}$. Notice the end-effector breadcrumb trail: no sudden dips, zero overshoot.*  
> - **Stage 9 & 10 (Place, Release & Return Home):** *The arm descends to the target destination, the gripper opens releasing the workpiece, ascends to clearance, and returns to Home. The final telemetry report logs zero joint limit violations and sub-millimeter precision throughout the mission.*  
> 
> *I now hand over the presentation back to our slide deck, where Khushi will present our quantitative experimental results and team contributions."*

---

## PART 5: MEMBER 5 — KHUSHI (SAP ID: 500122966)
**Total Stage Time: 03:00 Minutes (18:00 – 21:00)**

### Slide 13: Results 1: Kinematic Precision & Convergence (18:00 – 19:00)
*(Screen switches back to Slide 13: Figure 4 Error Distribution & Convergence Summary)*

> **Khushi:**  
> *"Thank you Lakshay. Respected faculty, on Slide 13 we examine the quantitative precision of our inverse kinematics solver evaluated across 100 randomly sampled reachable workspace configurations:  
> 
> - **Mean Position Error:** Our hybrid DLS solver achieved an average positioning error of just **0.0462 millimeters** (46.2 micrometers). This is more than 21 times better than the standard 1.0 mm industrial tolerance.  
> - **Mean Orientation Error:** The average tool angular deviation was **0.014 milliradians** (equivalent to 0.0008 degrees), ensuring near-perfect orthogonal alignment.  
> - **Computational Efficiency:** The average solver execution time was **9.67 milliseconds** per pose, converging in an average of **14.2 iterations**, making it suitable for real-time control at 50 Hz.  
> - **Mission Reliability:** In 20 consecutive automated pick-and-place runs, the system achieved a **100% success rate** with zero dropped payloads and zero singularities."*

---

### Slide 14: Results 2: Trajectory Benchmark & Jerk Cost (19:00 – 20:00)
*(Screen shows Slide 14: Figure 5 Bar Charts and Trajectory Comparison Table)*

> **Khushi:**  
> *"On Slide 14, we present our comparative benchmark across three trajectory planning profiles: Trapezoidal LSPB, Cubic Polynomial, and Quintic Polynomial.  
> 
> While Trapezoidal LSPB achieved the fastest transit time of 1.53 seconds, its discontinuous acceleration steps generated an extreme jerk metric of **414.74**. In physical hardware, this level of jerk causes severe mechanical resonance and gearbox chatter.  
> 
> The Cubic polynomial improves continuity but retains non-zero acceleration at the endpoints.  
> 
> Our implemented **Quintic polynomial** enforces zero acceleration and zero velocity at both endpoints ($C^2$ continuity), yielding a jerk cost of just **7.91**. This represents a **98.1% reduction in mechanical jerk** compared to trapezoidal motion, proving that the Quintic profile is optimal for preserving robotic hardware longevity."*

---

### Slide 15: Team Technical Contributions (20:00 – 21:00)
*(Screen shows Slide 15: Table of Verifiable Contributions for all 5 Members)*

> **Khushi:**  
> *"Slide 15 records our verifiable individual contributions across the project lifecycle:  
> 
> - **Suraj Singh (M1):** Configured the CoppeliaSim virtual scene, mapped revolute joint handles, RG2 gripper signals, and proximity sensor collision masks.  
> - **Sudhanshu Kumar (M2):** Led theoretical D-H matrix verification, mathematical literature review, and IEEE reference compilation.  
> - **Abhay Chand Thakur (M3):** Conducted trajectory benchmarking, 100-trial experimental data logging, and comparative metric CSV generation.  
> - **Lakshay Dahiya (M4):** Engineered the pure-Python D-H kinematics engine, hybrid Pieper/DLS solvers, 50 Hz ZeroMQ bridge, and the 10-stage state machine.  
> - **Khushi (M5):** Designed pick-and-place boundary test cases, error tolerance analysis, generated 300-DPI publication plots, and formatted the academic report.  
> 
> We now bring our presentation to a close with Slide 16 and 17."*

---

## PART 6: ALL TEAM MEMBERS — CONCLUSION & Q&A
**Total Stage Time: 01:00 Minute (21:00 – 22:00)**

### Slide 16: Conclusion & Industrial Deployment (21:00 – 21:45)
*(Screen shows Slide 16: 4 Key Takeaways — each member speaks one point)*

- **Suraj Singh (21:00 – 21:11):**  
  *"In conclusion, we successfully demonstrated a fully integrated, pure-Python 6-DOF robotic arm manipulation system achieving sub-50 micrometer accuracy and 100% pick-and-place reliability."*
- **Sudhanshu Kumar (21:11 – 21:22):**  
  *"Our hybrid D-H and DLS kinematics solver successfully eliminates singular divergence, proving that complex robotics algorithms can be realized transparently without simulator black boxes."*
- **Abhay Chand Thakur (21:22 – 21:33):**  
  *"Our trajectory analysis validated that quintic polynomials eliminate mechanical jerk spikes by 98.1%, providing a mathematically proven trajectory strategy for industrial manipulators."*
- **Khushi (21:33 – 21:45):**  
  *"This architecture translates directly to industrial applications, including semiconductor wafer handling, electronics sorting, and automated pharmaceutical packaging."*

---

### Slide 17: End Slide & Q&A Close (21:45 – 22:00)
*(Screen shows Slide 17: Thank You, GitHub Repo Link, Contact Details, Q&A)*

> **Lakshay Dahiya (Lead):**  
> *"On Slide 17, our complete open-source codebase, test suite, and 26-page academic report are available on GitHub. On behalf of Group G04, we express our sincere gratitude to our course faculty for their guidance throughout CSAI4014. We now conclude our 20-minute presentation and welcome questions from the evaluators. Thank you."*

---

## Pre-Recording Rehearsal Checklist

- [ ] **Timer Check:** Designate one member (e.g. Khushi) to keep a stopwatch visible to ensure every speaker stays within their allocated window.
- [ ] **Audio Transition:** When passing to the next speaker (e.g. *"I now invite Sudhanshu..."*), the next speaker immediately unmutes without awkward silence.
- [ ] **Slide Transitions:** Lakshay (or whoever is sharing their screen) advances the slide promptly when the speaker introduces the slide number.
- [ ] **Live Demo Rehearsal:** Practice executing the 3 terminal commands once before the final recording to verify window sizes and screen sharing layout.
