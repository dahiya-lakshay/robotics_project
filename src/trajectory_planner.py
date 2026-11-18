"""
Trajectory Planning Engine for 6-DOF Manipulator (Universal Robots UR5)
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from src.forward_kinematics import ForwardKinematics
from src.inverse_kinematics import InverseKinematics


class TrajectoryPlanner:
    """
    Multi-strategy trajectory generation engine supporting:
    1. Joint-Space Cubic Polynomial Interpolation (C^1 continuity)
    2. Joint-Space Quintic Polynomial Interpolation (C^2 continuity - smooth jerk)
    3. Joint-Space Trapezoidal Velocity Profile (LSPB)
    4. Cartesian-Space Straight-Line Trajectory with SLERP Orientation
    """

    def __init__(
        self,
        fk: Optional[ForwardKinematics] = None,
        ik: Optional[InverseKinematics] = None,
        max_joint_vel: float = 1.5,   # rad/s
        max_joint_acc: float = 2.5    # rad/s^2
    ):
        self.fk = fk if fk is not None else ForwardKinematics()
        self.ik = ik if ik is not None else InverseKinematics(self.fk)
        self.max_joint_vel = max_joint_vel
        self.max_joint_acc = max_joint_acc

    # -------------------------------------------------------------
    # 1. Joint-Space Cubic Polynomial
    # -------------------------------------------------------------
    def plan_cubic_joint_trajectory(
        self,
        q_start: np.ndarray,
        q_end: np.ndarray,
        duration: float,
        dt: float = 0.02
    ) -> Dict[str, np.ndarray]:
        """
        Generates 3rd order polynomial trajectory for each joint:
          q(t) = a0 + a1*t + a2*t^2 + a3*t^3
        Boundary conditions:
          q(0) = q_start, q(tf) = q_end, dq(0) = 0, dq(tf) = 0
        """
        assert duration > 0.0, "Duration must be positive."
        num_steps = int(np.ceil(duration / dt)) + 1
        time_vec = np.linspace(0.0, duration, num_steps)

        # Coefficients
        a0 = q_start
        a1 = np.zeros_like(q_start)
        a2 = 3.0 * (q_end - q_start) / (duration ** 2)
        a3 = -2.0 * (q_end - q_start) / (duration ** 3)

        positions = np.zeros((num_steps, 6), dtype=np.float64)
        velocities = np.zeros((num_steps, 6), dtype=np.float64)
        accelerations = np.zeros((num_steps, 6), dtype=np.float64)

        for i, t in enumerate(time_vec):
            positions[i] = a0 + a1 * t + a2 * (t ** 2) + a3 * (t ** 3)
            velocities[i] = a1 + 2.0 * a2 * t + 3.0 * a3 * (t ** 2)
            accelerations[i] = 2.0 * a2 + 6.0 * a3 * t

        return {
            "time": time_vec,
            "positions": positions,
            "velocities": velocities,
            "accelerations": accelerations,
            "method": "cubic_polynomial"
        }

    # -------------------------------------------------------------
    # 2. Joint-Space Quintic Polynomial
    # -------------------------------------------------------------
    def plan_quintic_joint_trajectory(
        self,
        q_start: np.ndarray,
        q_end: np.ndarray,
        duration: float,
        dt: float = 0.02
    ) -> Dict[str, np.ndarray]:
        """
        Generates 5th order polynomial trajectory for each joint:
          q(t) = a0 + a1*t + a2*t^2 + a3*t^3 + a4*t^4 + a5*t^5
        Boundary conditions:
          q(0)=q_start, q(tf)=q_end, dq(0)=0, dq(tf)=0, ddq(0)=0, ddq(tf)=0
        """
        assert duration > 0.0, "Duration must be positive."
        num_steps = int(np.ceil(duration / dt)) + 1
        time_vec = np.linspace(0.0, duration, num_steps)

        delta_q = q_end - q_start
        tf = duration

        a0 = q_start
        a1 = np.zeros_like(q_start)
        a2 = np.zeros_like(q_start)
        a3 = 10.0 * delta_q / (tf ** 3)
        a4 = -15.0 * delta_q / (tf ** 4)
        a5 = 6.0 * delta_q / (tf ** 5)

        positions = np.zeros((num_steps, 6), dtype=np.float64)
        velocities = np.zeros((num_steps, 6), dtype=np.float64)
        accelerations = np.zeros((num_steps, 6), dtype=np.float64)

        for i, t in enumerate(time_vec):
            positions[i] = a0 + a3 * (t ** 3) + a4 * (t ** 4) + a5 * (t ** 5)
            velocities[i] = 3.0 * a3 * (t ** 2) + 4.0 * a4 * (t ** 3) + 5.0 * a5 * (t ** 4)
            accelerations[i] = 6.0 * a3 * t + 12.0 * a4 * (t ** 2) + 20.0 * a5 * (t ** 3)

        return {
            "time": time_vec,
            "positions": positions,
            "velocities": velocities,
            "accelerations": accelerations,
            "method": "quintic_polynomial"
        }

    # -------------------------------------------------------------
    # 3. Joint-Space Trapezoidal Velocity Profile (LSPB)
    # -------------------------------------------------------------
    def plan_trapezoidal_joint_trajectory(
        self,
        q_start: np.ndarray,
        q_end: np.ndarray,
        max_vel: Optional[float] = None,
        max_acc: Optional[float] = None,
        dt: float = 0.02
    ) -> Dict[str, np.ndarray]:
        """
        Linear Segments with Parabolic Blends (LSPB) synchronized across all 6 joints.
        """
        if max_vel is None:
            max_vel = self.max_joint_vel
        if max_acc is None:
            max_acc = self.max_joint_acc

        delta_q = q_end - q_start
        max_disp = float(np.max(np.abs(delta_q)))

        if max_disp < 1e-6:
            # Stationary
            return {
                "time": np.array([0.0, dt]),
                "positions": np.array([q_start, q_end]),
                "velocities": np.zeros((2, 6)),
                "accelerations": np.zeros((2, 6)),
                "method": "trapezoidal_lspb"
            }

        # Synchronize total duration based on the slowest joint
        # Check if triangular profile is required or trapezoidal
        tb = max_vel / max_acc
        qb = 0.5 * max_acc * (tb ** 2)

        if max_disp < 2.0 * qb:
            # Triangular profile
            tb = np.sqrt(max_disp / max_acc)
            tf = 2.0 * tb
            v_cruise = max_acc * tb
        else:
            # Full trapezoidal profile
            tf = (max_disp / max_vel) + (max_vel / max_acc)
            tb = max_vel / max_acc
            v_cruise = max_vel

        num_steps = int(np.ceil(tf / dt)) + 1
        time_vec = np.linspace(0.0, tf, num_steps)

        positions = np.zeros((num_steps, 6), dtype=np.float64)
        velocities = np.zeros((num_steps, 6), dtype=np.float64)
        accelerations = np.zeros((num_steps, 6), dtype=np.float64)

        for j in range(6):
            dj = delta_q[j]
            sign_j = np.sign(dj)
            abs_dj = abs(dj)

            if abs_dj < 1e-6:
                positions[:, j] = q_start[j]
                continue

            acc_j = (abs_dj / max_disp) * max_acc
            vel_j = (abs_dj / max_disp) * v_cruise

            for i, t in enumerate(time_vec):
                if t <= tb:
                    # Acceleration phase
                    s = 0.5 * acc_j * (t ** 2)
                    sd = acc_j * t
                    sdd = acc_j
                elif t <= (tf - tb):
                    # Constant velocity phase
                    s = 0.5 * acc_j * (tb ** 2) + vel_j * (t - tb)
                    sd = vel_j
                    sdd = 0.0
                else:
                    # Deceleration phase
                    t_dec = t - (tf - tb)
                    s = 0.5 * acc_j * (tb ** 2) + vel_j * (tf - 2.0 * tb) + (vel_j * t_dec - 0.5 * acc_j * (t_dec ** 2))
                    sd = vel_j - acc_j * t_dec
                    sdd = -acc_j

                positions[i, j] = q_start[j] + sign_j * s
                velocities[i, j] = sign_j * sd
                accelerations[i, j] = sign_j * sdd

        return {
            "time": time_vec,
            "positions": positions,
            "velocities": velocities,
            "accelerations": accelerations,
            "method": "trapezoidal_lspb"
        }

    # -------------------------------------------------------------
    # 4. Cartesian Straight-Line Trajectory
    # -------------------------------------------------------------
    def plan_cartesian_straight_line(
        self,
        T_start: np.ndarray,
        T_end: np.ndarray,
        duration: float,
        q_seed: np.ndarray,
        dt: float = 0.04
    ) -> Dict[str, Any]:
        """
        Straight-line trajectory in Cartesian 3D task space.
        Interpolates Cartesian position linearly:
          p(s) = (1 - s)*p_start + s*p_end
        where s(t) follows a smooth cubic scalar profile s in [0, 1].
        Orientation interpolated via Matrix Lie algebra logarithm / SLERP.
        Inverse Kinematics resolved at each discrete waypoint.
        """
        num_steps = int(np.ceil(duration / dt)) + 1
        time_vec = np.linspace(0.0, duration, num_steps)

        p_start = T_start[0:3, 3]
        p_end = T_end[0:3, 3]
        R_start = T_start[0:3, 0:3]
        R_end = T_end[0:3, 0:3]

        # Relative rotation
        R_rel = R_end @ R_start.T
        trace = np.clip((np.trace(R_rel) - 1.0) / 2.0, -1.0, 1.0)
        angle_rel = np.arccos(trace)
        if abs(angle_rel) > 1e-5:
            axis_rel = np.array([
                R_rel[2, 1] - R_rel[1, 2],
                R_rel[0, 2] - R_rel[2, 0],
                R_rel[1, 0] - R_rel[0, 1]
            ]) / (2.0 * np.sin(angle_rel))
        else:
            axis_rel = np.array([0.0, 0.0, 1.0])

        cartesian_positions = np.zeros((num_steps, 3), dtype=np.float64)
        joint_positions = np.zeros((num_steps, 6), dtype=np.float64)
        success_flags = []

        q_prev = q_seed.copy()

        for i, t in enumerate(time_vec):
            # Normalized scalar parameter s in [0, 1] using cubic profile
            tau = t / duration
            s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)

            # Interpolated position
            p_interp = (1.0 - s) * p_start + s * p_end
            cartesian_positions[i] = p_interp

            # Interpolated orientation via Rodrigues rotation
            theta_s = s * angle_rel
            K = np.array([
                [0.0, -axis_rel[2], axis_rel[1]],
                [axis_rel[2], 0.0, -axis_rel[0]],
                [-axis_rel[1], axis_rel[0], 0.0]
            ])
            R_interp = (np.eye(3) + np.sin(theta_s) * K + (1.0 - np.cos(theta_s)) * (K @ K)) @ R_start

            # Construct intermediate transformation
            T_interp = np.eye(4)
            T_interp[0:3, 0:3] = R_interp
            T_interp[0:3, 3] = p_interp

            # Solve IK for intermediate waypoint
            ik_res = self.ik.solve(T_interp, q_current=q_prev, method="hybrid")
            if ik_res["success"]:
                q_prev = ik_res["joint_angles"]
                joint_positions[i] = q_prev
                success_flags.append(True)
            else:
                joint_positions[i] = q_prev
                success_flags.append(False)

        # Compute numerical finite-difference velocities and accelerations
        joint_velocities = np.gradient(joint_positions, dt, axis=0)
        joint_accelerations = np.gradient(joint_velocities, dt, axis=0)

        return {
            "time": time_vec,
            "positions": joint_positions,
            "velocities": joint_velocities,
            "accelerations": joint_accelerations,
            "cartesian_positions": cartesian_positions,
            "success_rate": float(np.mean(success_flags)),
            "method": "cartesian_straight_line"
        }

    # -------------------------------------------------------------
    # Performance & Smoothness Evaluation
    # -------------------------------------------------------------
    def compute_trajectory_metrics(self, trajectory: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate quantitative motion quality metrics:
        - Total duration (s)
        - Max joint velocity (rad/s)
        - Max joint acceleration (rad/s^2)
        - Joint jerk metric: integral(sum(jerk^2)) dt
        - End-effector Cartesian path length (m)
        """
        time = trajectory["time"]
        q_pos = trajectory["positions"]
        dt = float(time[1] - time[0]) if len(time) > 1 else 0.02

        # Numerical jerk = d(acc)/dt
        q_acc = trajectory["accelerations"]
        jerk = np.gradient(q_acc, dt, axis=0)
        jerk_cost = float(np.sum(jerk ** 2) * dt)

        # Compute end-effector Cartesian path
        cart_points = []
        for q in q_pos:
            T = self.fk.compute_fk(q)
            cart_points.append(T[0:3, 3])
        cart_points = np.array(cart_points)

        path_diffs = np.diff(cart_points, axis=0)
        cart_path_length = float(np.sum(np.linalg.norm(path_diffs, axis=1)))

        return {
            "duration_s": float(time[-1] - time[0]),
            "max_joint_velocity_rad_s": float(np.max(np.abs(trajectory["velocities"]))),
            "max_joint_acceleration_rad_s2": float(np.max(np.abs(q_acc))),
            "jerk_metric": jerk_cost,
            "cartesian_path_length_m": cart_path_length
        }


if __name__ == "__main__":
    planner = TrajectoryPlanner()

    q_start = np.array([0.0, -np.pi / 2.0, np.pi / 2.0, -np.pi / 2.0, -np.pi / 2.0, 0.0])
    q_end = np.array([0.5, -np.pi / 3.0, np.pi / 3.0, -np.pi / 4.0, -np.pi / 2.0, 0.5])

    print("=== Testing Trajectory Generation Strategies ===")

    # 1. Cubic Polynomial
    traj_cubic = planner.plan_cubic_joint_trajectory(q_start, q_end, duration=2.5)
    met_cubic = planner.compute_trajectory_metrics(traj_cubic)
    print("Cubic:", met_cubic)

    # 2. Quintic Polynomial
    traj_quintic = planner.plan_quintic_joint_trajectory(q_start, q_end, duration=2.5)
    met_quintic = planner.compute_trajectory_metrics(traj_quintic)
    print("Quintic:", met_quintic)

    # 3. Trapezoidal LSPB
    traj_trap = planner.plan_trapezoidal_joint_trajectory(q_start, q_end)
    met_trap = planner.compute_trajectory_metrics(traj_trap)
    print("Trapezoidal:", met_trap)
