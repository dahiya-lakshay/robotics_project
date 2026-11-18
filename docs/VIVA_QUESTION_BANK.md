# Comprehensive Viva Voce Question Bank & Model Answers

**Course:** CSAI4014 – Algorithms for Intelligent Systems and Robotics  
**Group:** G04 | **Project:** P02 | **Batch:** B3  
**Target Manipulator:** Universal Robots UR5 6-DOF Serial Articulated Arm  

---

### Q1: What are the four Denavit–Hartenberg (D-H) parameters, and what physical/geometric quantities do they represent?
**Model Answer:**  
The four standard D-H parameters describe the spatial relationship between consecutive joint coordinate frames $\{F_{i-1}\}$ and $\{F_i\}$:
1. **Link Length ($a_i$):** The distance along the common normal axis $x_i$ from the intersection with axis $z_{i-1}$ to the origin of frame $i$. It represents the physical link length.
2. **Link Twist ($\alpha_i$):** The angle of rotation about axis $x_i$ required to align axis $z_{i-1}$ with axis $z_i$ via the right-hand rule.
3. **Link Offset ($d_i$):** The distance along joint axis $z_{i-1}$ from origin $i-1$ to the intersection of the common normal $x_i$. For revolute joints, $d_i$ is a fixed constant; for prismatic joints, it is variable.
4. **Joint Angle ($\theta_i$):** The angle of rotation about joint axis $z_{i-1}$ needed to align axis $x_{i-1}$ with axis $x_i$. For revolute joints, $\theta_i$ is the generalized variable coordinate.

---

### Q2: What is the fundamental difference between the Standard D-H convention and the Modified (Craig) D-H convention?
**Model Answer:**  
- In the **Standard D-H convention** (Denavit & Hartenberg, 1955), frame $i$ is attached to the distal end of link $i$. Axis $z_i$ is aligned with the axis of joint $i+1$, and the transformation order is:
  $$T_{i-1}^i = \text{Rot}(z, \theta_i) \cdot \text{Trans}(z, d_i) \cdot \text{Trans}(x, a_i) \cdot \text{Rot}(x, \alpha_i)$$
- In the **Modified D-H convention** (Craig, 1986), frame $i$ is attached to the proximal end of link $i$, axis $z_i$ aligns with joint $i$, and the transformation order is:
  $$T_{i-1}^i = \text{Rot}(x, \alpha_{i-1}) \cdot \text{Trans}(x, a_{i-1}) \cdot \text{Rot}(z, \theta_i) \cdot \text{Trans}(z, d_i)$$
Our project strictly implements the **Standard D-H convention**.

---

### Q3: Why is the Universal Robots UR5 manipulator uniquely suited for analytical Inverse Kinematics?
**Model Answer:**  
The UR5 satisfies **Pieper's criteria**: a 6-DOF serial manipulator possesses a closed-form analytical inverse kinematics solution if three consecutive joint axes intersect at a single common point (forming a spherical wrist) or if three consecutive axes are parallel. In the UR5, joint axes 4, 5, and 6 intersect at the wrist center (frame 5 origin), decoupling position control (joints 1, 2, 3) from orientation control (joints 4, 5, 6).

---

### Q4: How is kinematic decoupling mathematically formulated for a spherical wrist?
**Model Answer:**  
Given the desired end-effector pose $T_{\text{target}} = \begin{bmatrix} R & p \\ 0 & 1 \end{bmatrix}$, the location of the wrist center $p_{wc}$ depends solely on position $p$ and the approach vector $a$ (the 3rd column of rotation matrix $R$):
$$p_{wc} = p - d_6 \cdot a = p - d_6 \cdot R \begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix}$$
Because joint 6 simply rotates about axis $a$, the coordinates of $p_{wc}$ are completely independent of wrist orientation angles ($\theta_4, \theta_5, \theta_6$), allowing joints $\theta_1, \theta_2, \theta_3$ to be solved first.

---

### Q5: What are the three primary kinematic singularities of the UR5, and when do they occur?
**Model Answer:**  
A kinematic singularity occurs when the $6 \times 6$ geometric Jacobian loses rank ($\det(J(q)) = 0$):
1. **Wrist Singularity:** Occurs when $\theta_5 = 0$ or $\pm \pi$. Joint axes 4 and 6 become collinear ($z_3 \parallel z_5$), causing the loss of one rotational degree of freedom.
2. **Shoulder Singularity:** Occurs when the wrist center point $p_{wc}$ intersects the base z-axis ($z_0$). The arm cannot translate radially outward without infinite shoulder velocity.
3. **Elbow Singularity:** Occurs when the elbow is fully extended or folded ($\theta_3 = 0$ or $\pm \pi$), placing the arm at the boundary of its physical reach envelope.

---

### Q6: How does the Damped Least Squares (DLS / Levenberg–Marquardt) method prevent numerical explosion near singularities?
**Model Answer:**  
Standard Jacobian pseudoinverse $J^+ = J^T (J J^T)^{-1}$ blows up near singularities because singular values of $J$ approach zero, driving joint velocities $\dot{q} = J^+ V$ to infinity. DLS introduces a damping regularization factor $\lambda^2$:
$$J^* = J^T (J J^T + \lambda^2 I)^{-1}$$
In non-singular regions ($\lambda \to 0$), $J^*$ acts as the exact pseudoinverse. Near singularities, the $\lambda^2 I$ term bounds the matrix eigenvalues away from zero, sacrificing a small amount of instantaneous tracking accuracy to ensure bounded, physically realizable joint velocities.

---

### Q7: What is the Yoshikawa Manipulability Measure, and how did your team use it?
**Model Answer:**  
The Yoshikawa manipulability index $w(q)$ is defined as:
$$w(q) = \sqrt{\det(J(q) J(q)^T)} = \sigma_1 \sigma_2 \dots \sigma_m$$
where $\sigma_i$ are the singular values of the Jacobian. When the robot approaches a singularity, $w(q) \to 0$. In our inverse kinematics engine, we use $w(q)$ as an adaptive trigger: when $w(q)$ falls below a threshold $w_0$, the damping factor dynamically increases: $\lambda^2 = \lambda_0^2 (1 - w/w_0)^2$.

---

### Q8: What is the mathematical and mechanical difference between a Cubic ($C^1$) and a Quintic ($C^2$) polynomial trajectory?
**Model Answer:**  
- **Cubic Polynomial ($q(t) = a_0 + a_1 t + a_2 t^2 + a_3 t^3$):** Satisfies 4 boundary conditions ($q(0), q(t_f), \dot{q}(0), \dot{q}(t_f)$). It guarantees continuous position and velocity ($C^1$), but acceleration is linear, meaning jerk (the derivative of acceleration) has step changes, inducing mechanical vibration.
- **Quintic Polynomial ($q(t) = \sum_{k=0}^5 a_k t^k$):** Satisfies 6 boundary conditions by additionally enforcing zero initial and final accelerations: $\ddot{q}(0) = 0$ and $\ddot{q}(t_f) = 0$. This ensures $C^2$ continuity, resulting in continuous acceleration and smooth jerk profiles. Our benchmark empirically proved a 98.1% reduction in jerk cost with quintic polynomials.

---

### Q9: Why is a Trapezoidal (LSPB) velocity profile considered $C^0$ in acceleration, and what problem does that cause?
**Model Answer:**  
Linear Segments with Parabolic Blends (LSPB) consists of constant acceleration, constant cruise velocity, and constant deceleration phases. Because acceleration transitions instantaneously between $0$, $+a_{\max}$, and $-a_{\max}$, its derivative (jerk) is mathematically infinite at the switching boundaries ($\delta$-Dirac pulses). In physical robots, infinite jerk causes mechanical shock, structural vibration, and premature wear on harmonic drive gearboxes.

---

### Q10: How does the Python ZeroMQ Remote API communicate with CoppeliaSim, and what is synchronous stepping?
**Model Answer:**  
The ZeroMQ Remote API uses high-speed ZeroMQ sockets (`REQ/REP` or `PUB/SUB`) with CBOR binary serialization over TCP port 23000. Under default asynchronous mode, CoppeliaSim advances physics independently of Python, causing race conditions and variable control delays. By setting `client.setStepping(True)`, we lock the simulator clock: CoppeliaSim computes exactly one 50 ms physics step only when Python explicitly invokes `client.step()`, guaranteeing deterministic, lockstep co-simulation.
