# 18–22 Minute Demonstration Video Recording Script & Checklist

**Course:** CSAI4014 – Algorithms for Intelligent Systems and Robotics  
**Group:** G04 | **Project:** P02 | **Batch:** B3  
**Robot:** Universal Robots UR5 6-DOF Manipulator  
**Target Video Duration:** 20 Minutes (Accepted Range: 18:00 – 22:00)  
**Distribution:** YouTube (Uploaded as **UNLISTED**)  

---

## 1. Pre-Recording Technical Checklist

- [ ] Platform: Google Meet / Microsoft Teams / Zoom (1080p recording enabled).
- [ ] Device Rule: Every team member joins from their own separate physical laptop/desktop.
- [ ] Video Rule: All 5 cameras must remain turned ON with clear face visibility throughout the 20 minutes.
- [ ] Audio Rule: Test microphone levels before hitting Record; mute when not actively presenting.
- [ ] Window Setup: Screen share 1080p monitor showing `project_presentation.pdf` and terminal/CoppeliaSim.
- [ ] No Cuts: Faculty allows only small trims at the very start and end. Do not splice or edit middle sections.

---

## 2. Minute-by-Minute Speaker Script (20 Minutes Total)

```text
TIMELINE OVERVIEW:
00:00 - 02:00 (02 min): Introductions (Name, SAP ID, Role) — ALL MEMBERS
02:00 - 04:30 (02.5 min): Problem Statement & Measurable Objectives — Suraj Singh
04:30 - 07:00 (02.5 min): Literature Review, Gaps & Novelty — Sudhanshu Kumar
07:00 - 10:00 (03 min): Mathematical D-H Theory, Kinematics & Jacobians — Sudhanshu & Lakshay
10:00 - 12:30 (02.5 min): System Architecture & State Machine Design — Lakshay Dahiya
12:30 - 18:30 (06 min): LIVE SIMULATION DEMONSTRATION — Lakshay & Suraj
18:30 - 20:30 (02 min): Experimental Results, Trajectory Comparison & Plots — Abhay Chand Thakur
20:30 - 21:30 (01 min): Team Contribution Register & Co-Learning — Khushi
21:30 - 22:00 (00.5 min): Conclusion, Industrial Scope & Q&A Close — ALL MEMBERS
```

---

### [00:00 – 02:00] Stage 1: Individual Introductions (All Members)
*Screen shows Slide 1 (Title Slide)*

- **Lakshay Dahiya (00:00 - 00:25):**  
  *"Good day respected faculty and evaluators. I am Lakshay Dahiya, SAP ID 500121078, coordinating Group G04 for Batch B3 in course CSAI4014. My primary technical responsibilities encompassed developing the Denavit-Hartenberg kinematics engine, closed-form and numerical inverse kinematics solvers, the ZeroMQ Remote API bridge, and overall system integration. I now invite my teammates to introduce themselves."*
- **Suraj Singh (00:25 - 00:45):**  
  *"Hello everyone, I am Suraj Singh, SAP ID 500122962. In this project, I configured the CoppeliaSim virtual simulation environment, mapped UR5 revolute joint handles and RG2 gripper signals, and assisted in collision modeling."*
- **Sudhanshu Kumar (00:45 - 01:10):**  
  *"Greetings, I am Sudhanshu Kumar, SAP ID 500125146. My core responsibilities included the technical literature review, theoretical D-H matrix verification, and differential Jacobian equations."*
- **Abhay Chand Thakur (01:10 - 01:35):**  
  *"Hello, I am Abhay Chand Thakur, SAP ID 500122020. I led the trajectory generation experiments, gathered quantitative performance metrics over 100 trials, and generated our comparison tables."*
- **Khushi (01:35 - 02:00):**  
  *"Greetings, I am Khushi, SAP ID 500122966. My work focused on pick-and-place boundary validation, error tolerance analysis, result visualization, and compiling our academic deliverables."*

---

### [02:00 – 04:30] Stage 2: Problem Statement & Objectives (Suraj Singh)
*Screen shows Slide 2 and Slide 3*

- **Suraj Singh:**  
  *"Turning to Slide 2, our project addresses a foundational challenge in modern robotics: automated pick-and-place manipulation. In industrial manufacturing, serial robots must acquire and transfer objects across arbitrary workspace locations with high repeatability. A 6-DOF articulated arm like the Universal Robots UR5 provides 3 translational degrees of freedom to position the tool and 3 rotational degrees of freedom to orient the gripper orthogonally. On Slide 3, our measurable objectives were: first, derive and verify standard D-H parameters; second, build pure-Python forward and inverse kinematics engines achieving sub-millimeter precision; third, minimize joint jerk using polynomial trajectory planning; and fourth, interface synchronously with CoppeliaSim via ZeroMQ at 50 Hz."*

---

### [04:30 – 07:00] Stage 3: Literature Review & Novelty (Sudhanshu Kumar)
*Screen shows Slide 4 and Slide 5*

- **Sudhanshu Kumar:**  
  *"Moving to Slide 4, classical literature by Denavit, Hartenberg, Craig, and Siciliano establishes matrix-based kinematic modeling. In typical educational setups, students rely on CoppeliaSim's internal black-box IK plugin, which hides the mathematical transformations. On Slide 5, our project presents four mandatory novel contributions: First, we developed an independent, pure-Python D-H kinematics engine that computes all matrix products and Jacobians outside the simulator. Second, we engineered a hybrid IK solver coupling closed-form Pieper decoupling with an adaptive Levenberg-Marquardt Damped Least Squares optimizer to prevent singularity blowups. Third, we conducted a multi-strategy trajectory benchmark using the integral jerk metric $\int \|\dddot{q}\|^2 dt$. Fourth, we built a zero-downtime virtual fallback engine for automated headless testing."*

---

### [07:00 – 10:00] Stage 4: Mathematical Theory & Syllabus Mapping (Sudhanshu & Lakshay)
*Screen shows Slide 6, Slide 9, and Figure 1*

- **Sudhanshu Kumar (07:00 - 08:30):**  
  *"On Slide 6 and 9, we apply the standard Denavit-Hartenberg convention. The relative transformation $T_{i-1}^i$ is formulated using link length $a_i$, twist $\alpha_i$, offset $d_i$, and variable angle $\theta_i$. For the UR5, link dimensions are $d_1 = 0.089159\text{ m}, a_2 = -0.425\text{ m}, a_3 = -0.39225\text{ m}, d_4 = 0.10915\text{ m}, d_5 = 0.09465\text{ m}, d_6 = 0.0823\text{ m}$. Forward kinematics is computed by serial matrix multiplication $T_0^6 = \prod_{i=1}^6 T_{i-1}^i$."*
- **Lakshay Dahiya (08:30 - 10:00):**  
  *"For differential kinematics, we evaluate the 6x6 geometric Jacobian relating joint rates to end-effector twist: $V = J(q)\dot{q}$. To solve inverse kinematics near singularities—such as wrist singularity at $\theta_5 = 0$—we implement Damped Least Squares: $\Delta q = J^T(J J^T + \lambda^2 I)^{-1} e$, where $\lambda$ dynamically increases as Yoshikawa manipulability $w = \sqrt{\det(J J^T)}$ drops, ensuring bounded joint increments."*

---

### [10:00 – 12:30] Stage 5: System Architecture & Trajectory Planning (Lakshay Dahiya)
*Screen shows Slide 7 and Slide 10*

- **Lakshay Dahiya:**  
  *"On Slide 7, our software architecture is structured into decoupled modules: `ForwardKinematics`, `InverseKinematics`, `TrajectoryPlanner`, `MotionController`, and `PickAndPlaceStateMachine`. On Slide 10, we implement Quintic ($C^2$) polynomial trajectories satisfying 6 boundary conditions: zero initial/final velocity and zero initial/final acceleration. This eliminates instantaneous acceleration steps, yielding smooth motion."*

---

### [12:30 – 18:30] Stage 6: LIVE SIMULATION DEMONSTRATION (Lakshay & Suraj)
*Screen switches to live terminal / CoppeliaSim GUI window*

- **Lakshay Dahiya (12:30 - 13:30):**  
  *"Now we present the live demonstration. I will first run our unit test suite to prove mathematical correctness in real time:*
  ```bash
  python3 -m pytest tests/ -v
  ```
  *As you can see on screen, all 11 unit tests pass in 0.15 seconds, verifying transformation orthonormality, Jacobian dimensions, reachability filters, and polynomial boundary conditions."*
- **Lakshay & Suraj (13:30 - 18:30):**  
  *"Next, we execute our main pick-and-place mission CLI:*
  ```bash
  python3 -m src.main pick-and-place --planner quintic
  ```
  *(Narrating the live 10-stage execution):*  
  - *Stage 1 & 2: Robot initializes and moves to standard Home stance $[0, -\pi/2, \pi/2, -\pi/2, -\pi/2, 0]^T$.*
  - *Stage 3 & 4: Identifying object at $[0.35, 0.15, 0.05]\text{ m}$; end-effector approaches pre-pick stance $12\text{ cm}$ above.*
  - *Stage 5 & 6: Controlled vertical descent along tool z-axis; gripper closes and establishes contact.*
  - *Stage 7 & 8: Vertical clearance ascent followed by smooth quintic transfer to destination pre-place stance at $[0.10, 0.38, 0.17]\text{ m}$.*
  - *Stage 9 & 10: Descent to drop zone, gripper release, clearance ascent, and return to home.*  
  *Total execution time and telemetry logs are confirmed with zero collisions."*

---

### [18:30 – 20:30] Stage 7: Empirical Results & Trajectory Comparison (Abhay Chand Thakur)
*Screen shows Slide 13 and Slide 14*

- **Abhay Chand Thakur:**  
  *"Examining our empirical results on Slide 13, over 100 random reachable configurations, our DLS solver achieved a mean positioning accuracy of $0.0462\text{ mm}$ (46.2 micrometers) and orientation accuracy of $0.014\text{ mrad}$, converging in an average of $9.67\text{ ms}$ (14.2 iterations). On Slide 14, our comparative analysis across trajectory planners shows that while Trapezoidal LSPB completes in 1.53 s, it incurs an extreme jerk metric of 414.74. The Quintic polynomial achieves a jerk cost of only 7.91—a 98.1% reduction in mechanical jerk, confirming its superiority for industrial hardware."*

---

### [20:30 – 21:30] Stage 8: Team Contributions & Co-Learning (Khushi)
*Screen shows Slide 15*

- **Khushi:**  
  *"On Slide 15, we record our genuine, verifiable individual contributions. Suraj led CoppeliaSim scene configuration; Sudhanshu led theoretical kinematics derivations; Abhay directed trajectory benchmarking; Lakshay engineered the kinematics solvers, bridge, and controller; and I led pick-and-place validation, boundary testing, and report formatting. In our co-learning reflections, each member expanded their technical breadth, bridging software development with applied robotics theory."*

---

### [21:30 – 22:00] Stage 9: Conclusion & Close (All Members)
*Screen shows Slide 16 and Slide 17*

- **Lakshay Dahiya:**  
  *"In conclusion on Slide 16, this project successfully realized a fully functional, mathematically rigorous 6-DOF pick-and-place system. Potential industrial extensions include vision-based 6D pose estimation and physical hardware deployment via ROS 2. On behalf of Group G04, we thank our course faculty. We now conclude our recording and welcome your questions."*
