# Denavit–Hartenberg Kinematics Formulation: Universal Robots UR5

**Course:** CSAI4014 – Algorithms for Intelligent Systems and Robotics  
**Group:** G04 | **Project:** P02 | **Batch:** B3  
**Manipulator:** Universal Robots UR5 (6-DOF Serial Revolute Manipulator)  

---

## 1. Theoretical Foundations of the D-H Convention

The Denavit–Hartenberg (D-H) convention establishes a standardized framework for assigning orthonormal reference frames $\{F_0, F_1, \dots, F_n\}$ to adjacent links in a serial kinematic chain. Under the standard D-H representation, four kinematic parameters completely describe the relative spatial transformation between consecutive joint coordinate systems:

1. **Link Length ($a_i$):** Distance along the common normal axis $x_i$ from the intersection with $z_{i-1}$ to the origin of frame $i$.
2. **Link Twist ($\alpha_i$):** Angle of rotation about the common normal axis $x_i$ required to align axis $z_{i-1}$ with axis $z_i$ (measured via right-hand rule).
3. **Link Offset ($d_i$):** Distance along joint axis $z_{i-1}$ from frame origin $i-1$ to the intersection of the common normal $x_i$.
4. **Joint Angle ($\theta_i$):** Angle of rotation about joint axis $z_{i-1}$ required to align axis $x_{i-1}$ with axis $x_i$ (the variable generalized coordinate for revolute joints).

---

## 2. Homogeneous Transformation Matrix Derivation

The homogeneous transformation matrix $T_{i-1}^i$ translating and rotating coordinate frame $i-1$ into coordinate frame $i$ is formulated as the composite product of four elementary screw transformations:

$$T_{i-1}^i = \text{Rot}(z, \theta_i) \cdot \text{Trans}(z, d_i) \cdot \text{Trans}(x, a_i) \cdot \text{Rot}(x, \alpha_i)$$

Expanding the elementary transformation matrices:

$$\text{Rot}(z, \theta_i) = \begin{bmatrix} \cos\theta_i & -\sin\theta_i & 0 & 0 \\ \sin\theta_i & \cos\theta_i & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}, \quad \text{Trans}(z, d_i) = \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & d_i \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

$$\text{Trans}(x, a_i) = \begin{bmatrix} 1 & 0 & 0 & a_i \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}, \quad \text{Rot}(x, \alpha_i) = \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & \cos\alpha_i & -\sin\alpha_i & 0 \\ 0 & \sin\alpha_i & \cos\alpha_i & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

Multiplying these matrices yields the standard Denavit–Hartenberg homogeneous transformation matrix:

$$T_{i-1}^i = \begin{bmatrix} 
\cos\theta_i & -\sin\theta_i \cos\alpha_i & \sin\theta_i \sin\alpha_i & a_i \cos\theta_i \\
\sin\theta_i & \cos\theta_i \cos\alpha_i & -\cos\theta_i \sin\alpha_i & a_i \sin\theta_i \\
0 & \sin\alpha_i & \cos\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{bmatrix}$$

---

## 3. Universal Robots UR5 Standard D-H Parameter Table

Based on manufacturer kinematic calibration and mechanical specifications of the UR5 arm, the link dimensions are:
- $d_1 = 0.089159\text{ m}$ (Height from base mounting surface to shoulder axis)
- $a_2 = -0.42500\text{ m}$ (Upper arm link length between shoulder and elbow)
- $a_3 = -0.39225\text{ m}$ (Forearm link length between elbow and wrist 1)
- $d_4 = 0.10915\text{ m}$ (Wrist 1 lateral offset)
- $d_5 = 0.09465\text{ m}$ (Wrist 2 lateral offset)
- $d_6 = 0.08230\text{ m}$ (Wrist 3 axial flange offset to end-effector mount)

The complete verified Standard D-H Parameter Table is given below:

| Frame ($i$) | Joint Name | $a_i\text{ (m)}$ | $\alpha_i\text{ (rad)}$ | $d_i\text{ (m)}$ | $\theta_i\text{ (rad)}$ | Joint Range (rad) |
|---|---|---|---|---|---|---|
| **1** | Base to Shoulder | $0.0$ | $+\pi/2$ ($+1.5708$) | $0.089159$ | $\theta_1^*$ | $[-\pi, +\pi]$ |
| **2** | Shoulder to Elbow | $-0.42500$ | $0.0$ | $0.0$ | $\theta_2^*$ | $[-\pi, +\pi]$ |
| **3** | Elbow to Wrist 1 | $-0.39225$ | $0.0$ | $0.0$ | $\theta_3^*$ | $[-\pi, +\pi]$ |
| **4** | Wrist 1 to Wrist 2 | $0.0$ | $+\pi/2$ ($+1.5708$) | $0.10915$ | $\theta_4^*$ | $[-\pi, +\pi]$ |
| **5** | Wrist 2 to Wrist 3 | $0.0$ | $-\pi/2$ ($-1.5708$) | $0.09465$ | $\theta_5^*$ | $[-\pi, +\pi]$ |
| **6** | Wrist 3 to Flange | $0.0$ | $0.0$ | $0.08230$ | $\theta_6^*$ | $[-\pi, +\pi]$ |

*Note: Asterisk ($\theta_i^*$) denotes the time-varying joint angle variable.*

---

## 4. Overall End-Effector Kinematic Chain

The cumulative forward kinematic transformation matrix $T_0^6$ expressing the position and orientation of the robot tool flange with respect to the stationary base coordinate frame $F_0$ is evaluated through sequential matrix multiplication:

$$T_0^6(q) = T_0^1(\theta_1) \cdot T_1^2(\theta_2) \cdot T_2^3(\theta_3) \cdot T_3^4(\theta_4) \cdot T_4^5(\theta_5) \cdot T_5^6(\theta_6)$$

where:
$$T_0^6(q) = \begin{bmatrix} 
R_{0}^6(q)_{3 \times 3} & p_{0}^6(q)_{3 \times 1} \\
0_{1 \times 3} & 1
\end{bmatrix} = \begin{bmatrix}
n_x & s_x & a_x & p_x \\
n_y & s_y & a_y & p_y \\
n_z & s_z & a_z & p_z \\
0 & 0 & 0 & 1
\end{bmatrix}$$

- $n = [n_x, n_y, n_z]^T$: Normal vector (x-axis of tool frame)
- $s = [s_x, s_y, s_z]^T$: Slide vector (y-axis of tool frame)
- $a = [a_x, a_y, a_z]^T$: Approach vector (z-axis pointing outward along tool axis)
- $p = [p_x, p_y, p_z]^T$: Cartesian translation position vector in base meters.
