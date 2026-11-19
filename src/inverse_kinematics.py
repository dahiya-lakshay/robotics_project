"""
Inverse Kinematics Engine for 6-DOF Manipulator (Universal Robots UR5)
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from src.dh_parameters import UR5DHParameters
from src.forward_kinematics import ForwardKinematics


class InverseKinematics:
    """
    Dual-mode Inverse Kinematics solver for the 6-DOF UR5 robotic manipulator:
    1. Numerical Jacobian-based Damped Least Squares (DLS / Levenberg-Marquardt)
    2. Analytical Closed-Form Geometric Decoupling (Pieper's approach with up to 8 solutions)
    """

    def __init__(self, fk: Optional[ForwardKinematics] = None):
        self.fk = fk if fk is not None else ForwardKinematics()
        self.links = self.fk.links

        # UR5 Link dimensions
        self.d1 = UR5DHParameters.D1
        self.a2 = UR5DHParameters.A2
        self.a3 = UR5DHParameters.A3
        self.d4 = UR5DHParameters.D4
        self.d5 = UR5DHParameters.D5
        self.d6 = UR5DHParameters.D6

        # Joint limits
        self.joint_mins = np.array([l.joint_min for l in self.links])
        self.joint_maxs = np.array([l.joint_max for l in self.links])

        # Maximum reach from shoulder (approximate workspace sphere)
        self.max_reach = abs(self.a2) + abs(self.a3) + np.sqrt(self.d4**2 + self.d5**2 + self.d6**2)
        self.min_reach = 0.12  # Near-base singularity boundary

    def check_reachability(self, target_pos: np.ndarray) -> Tuple[bool, float, str]:
        """
        Verify whether Cartesian target position lies within kinematic workspace reach.
        """
        dist_from_base = float(np.linalg.norm(target_pos))
        if dist_from_base > self.max_reach:
            return False, dist_from_base, f"Target out of reach: distance {dist_from_base:.3f}m > max reach {self.max_reach:.3f}m"
        if dist_from_base < self.min_reach:
            return False, dist_from_base, f"Target too close to base singularity: distance {dist_from_base:.3f}m < min reach {self.min_reach:.3f}m"
        return True, dist_from_base, "Target within reachable workspace."

    @staticmethod
    def compute_pose_error(T_current: np.ndarray, T_target: np.ndarray) -> np.ndarray:
        """
        Compute 6D task-space pose error vector e = [e_pos; e_ori].
        Position error: e_pos = p_target - p_current
        Orientation error: e_ori computed via axis-angle representation of R_err = R_target * R_current^T
        """
        p_curr = T_current[0:3, 3]
        p_targ = T_target[0:3, 3]
        e_pos = p_targ - p_curr

        R_curr = T_current[0:3, 0:3]
        R_targ = T_target[0:3, 0:3]
        R_err = R_targ @ R_curr.T

        # Convert R_err to axis-angle vector
        trace = np.trace(R_err)
        cos_theta = np.clip((trace - 1.0) / 2.0, -1.0, 1.0)
        theta = np.arccos(cos_theta)

        if np.abs(theta) < 1e-6:
            e_ori = np.zeros(3)
        else:
            axis = np.array([
                R_err[2, 1] - R_err[1, 2],
                R_err[0, 2] - R_err[2, 0],
                R_err[1, 0] - R_err[0, 1]
            ]) / (2.0 * np.sin(theta))
            e_ori = axis * theta

        return np.concatenate([e_pos, e_ori])

    def solve_numerical_dls(
        self,
        T_target: np.ndarray,
        q_init: Optional[np.ndarray] = None,
        max_iterations: int = 150,
        tol_pos: float = 1e-4,   # 0.1 mm position accuracy
        tol_ori: float = 1e-3,   # ~0.05 deg orientation accuracy
        damping_factor: float = 0.05,
        step_limit: float = 0.2
    ) -> Dict[str, Any]:
        """
        Solve Inverse Kinematics using Damped Least Squares (DLS / Levenberg-Marquardt):
          Delta_q = J^T * (J * J^T + lambda^2 * I)^(-1) * error
        """
        reachable, dist, msg = self.check_reachability(T_target[0:3, 3])
        if not reachable:
            return {
                "success": False,
                "joint_angles": None,
                "iterations": 0,
                "error_pos": dist,
                "error_ori": np.pi,
                "message": msg
            }

        if q_init is None:
            # Default home configuration
            q = np.array([0.0, -np.pi / 2.0, np.pi / 2.0, -np.pi / 2.0, -np.pi / 2.0, 0.0])
        else:
            q = q_init.copy().astype(np.float64)

        for it in range(max_iterations):
            T_curr = self.fk.compute_fk(q)
            err = self.compute_pose_error(T_curr, T_target)

            err_pos_norm = float(np.linalg.norm(err[0:3]))
            err_ori_norm = float(np.linalg.norm(err[3:6]))

            if err_pos_norm < tol_pos and err_ori_norm < tol_ori:
                # Normalize joint angles into [-pi, pi]
                q_norm = (q + np.pi) % (2.0 * np.pi) - np.pi
                return {
                    "success": True,
                    "joint_angles": q_norm,
                    "iterations": it,
                    "error_pos": err_pos_norm,
                    "error_ori": err_ori_norm,
                    "message": f"DLS converged in {it} iterations."
                }

            J = self.fk.compute_geometric_jacobian(q)

            # Damped Least Squares formulation
            JJT = J @ J.T
            damped_matrix = JJT + (damping_factor ** 2) * np.eye(6)
            dq = J.T @ np.linalg.solve(damped_matrix, err)

            # Clamp joint step size to ensure stability near singularities
            dq_norm = np.linalg.norm(dq)
            if dq_norm > step_limit:
                dq = (dq / dq_norm) * step_limit

            q += dq

        # Max iterations reached
        T_curr = self.fk.compute_fk(q)
        err = self.compute_pose_error(T_curr, T_target)
        q_norm = (q + np.pi) % (2.0 * np.pi) - np.pi

        return {
            "success": False,
            "joint_angles": q_norm,
            "iterations": max_iterations,
            "error_pos": float(np.linalg.norm(err[0:3])),
            "error_ori": float(np.linalg.norm(err[3:6])),
            "message": f"DLS did not converge within {max_iterations} iterations."
        }

    def solve_analytical(self, T_target: np.ndarray) -> List[np.ndarray]:
        """
        Analytical closed-form Inverse Kinematics for UR5 (up to 8 valid solutions).
        Uses kinematic decoupling:
          Wrist center: p_05 = p_target - d6 * R_target * [0, 0, 1]^T
        """
        solutions = []

        R_06 = T_target[0:3, 0:3]
        p_06 = T_target[0:3, 3]

        # Step 1: Find wrist center position p_05
        # In D-H convention, frame 5 origin is at p_06 - d6 * z_06
        p_05 = p_06 - self.d6 * R_06[:, 2]

        # Step 2: Calculate theta_1 (shoulder pan)
        # There are 2 solutions for theta_1: left or right shoulder
        psi = np.arctan2(p_05[1], p_05[0])
        p_05_xy = np.sqrt(p_05[0]**2 + p_05[1]**2)

        if p_05_xy < abs(self.d4):
            # Target is inside shoulder singularity cylinder
            return solutions

        cos_gamma = self.d4 / p_05_xy
        cos_gamma = np.clip(cos_gamma, -1.0, 1.0)
        gamma = np.arccos(cos_gamma)

        theta1_candidates = [
            psi + gamma + np.pi / 2.0,
            psi - gamma + np.pi / 2.0
        ]

        for q1 in theta1_candidates:
            q1 = (q1 + np.pi) % (2 * np.pi) - np.pi

            # Step 3: Calculate theta_5 (wrist 2)
            # 2 solutions for theta_5 (wrist up/down)
            p_16z = p_06[0] * np.sin(q1) - p_06[1] * np.cos(q1)
            arg5 = (p_16z - self.d4) / self.d6
            if abs(arg5) > 1.0:
                continue
            arg5 = np.clip(arg5, -1.0, 1.0)
            theta5_candidates = [
                np.arccos(arg5),
                -np.arccos(arg5)
            ]

            for q5 in theta5_candidates:
                # Step 4: Calculate theta_6 (wrist 3)
                sin_q5 = np.sin(q5)
                if abs(sin_q5) < 1e-4:
                    # Wrist singularity: q5 = 0
                    q6 = 0.0
                else:
                    T_01 = self.links[0].transformation_matrix(q1)
                    R_01 = T_01[0:3, 0:3]
                    R_16 = R_01.T @ R_06
                    # Use row 1 (y-axis) of R_16
                    q6 = np.arctan2(-R_16[1, 2] / sin_q5, R_16[0, 2] / sin_q5)

                q6 = (q6 + np.pi) % (2 * np.pi) - np.pi

                # Step 5: Calculate theta_2, theta_3, theta_4 (planar 3-link arm)
                # Compute T_14 = T_01^-1 * T_06 * T_56^-1 * T_45^-1
                T_01 = self.links[0].transformation_matrix(q1)
                T_45 = self.links[4].transformation_matrix(q5)
                T_56 = self.links[5].transformation_matrix(q6)

                T_16 = np.linalg.inv(T_01) @ T_target
                T_14 = T_16 @ np.linalg.inv(T_45 @ T_56)

                p_13 = T_14[0:3, 3] - self.links[3].transformation_matrix(0.0)[0:3, 3]
                p_14 = T_14[0:3, 3]

                # Distance in link 2-3 plane
                p_14_x = p_14[0]
                p_14_y = p_14[1]
                p_14_norm_sq = p_14_x**2 + p_14_y**2

                cos_q3 = (p_14_norm_sq - self.a2**2 - self.a3**2) / (2.0 * self.a2 * self.a3)
                if abs(cos_q3) > 1.0:
                    continue
                cos_q3 = np.clip(cos_q3, -1.0, 1.0)

                # Two solutions for elbow (elbow up / elbow down)
                theta3_candidates = [
                    np.arccos(cos_q3),
                    -np.arccos(cos_q3)
                ]

                for q3 in theta3_candidates:
                    # Solve for theta_2
                    beta = np.arctan2(p_14_y, p_14_x)
                    cos_alpha = (p_14_norm_sq + self.a2**2 - self.a3**2) / (2.0 * self.a2 * np.sqrt(p_14_norm_sq))
                    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
                    alpha = np.arccos(cos_alpha)

                    if q3 > 0:
                        q2 = -(beta + alpha)
                    else:
                        q2 = -(beta - alpha)

                    q2 = (q2 + np.pi) % (2 * np.pi) - np.pi

                    # Solve for theta_4 (wrist 1)
                    # Orientation of link 4 relative to link 1
                    T_12 = self.links[1].transformation_matrix(q2)
                    T_23 = self.links[2].transformation_matrix(q3)
                    T_34 = np.linalg.inv(T_12 @ T_23) @ T_14

                    q4 = np.arctan2(T_34[1, 0], T_34[0, 0])
                    q4 = (q4 + np.pi) % (2 * np.pi) - np.pi

                    candidate_q = np.array([q1, q2, q3, q4, q5, q6], dtype=np.float64)

                    # Verify that this solution actually matches target pose
                    T_check = self.fk.compute_fk(candidate_q)
                    err = self.compute_pose_error(T_check, T_target)
                    if np.linalg.norm(err[0:3]) < 1e-2:  # 1 cm validation check
                        solutions.append(candidate_q)

        return solutions

    def select_best_configuration(
        self,
        candidate_solutions: List[np.ndarray],
        q_current: np.ndarray,
        weights: Optional[np.ndarray] = None
    ) -> Optional[np.ndarray]:
        """
        Select the configuration from candidate solutions that minimizes joint-space distance:
          cost = sum(weights * (q_candidate - q_current)^2)
        """
        if not candidate_solutions:
            return None

        if weights is None:
            # Heavily weight early joints (base, shoulder) to avoid large chassis repositioning
            weights = np.array([3.0, 2.5, 2.0, 1.0, 1.0, 0.5])

        best_q = None
        min_cost = float("inf")

        for q in candidate_solutions:
            # Compute shortest angular difference
            diff = (q - q_current + np.pi) % (2 * np.pi) - np.pi
            cost = float(np.sum(weights * (diff ** 2)))
            if cost < min_cost:
                min_cost = cost
                best_q = q

        return best_q

    def solve(
        self,
        T_target: np.ndarray,
        q_current: Optional[np.ndarray] = None,
        method: str = "hybrid"  # 'analytical', 'numerical', or 'hybrid'
    ) -> Dict[str, Any]:
        """
        Unified IK interface. 'hybrid' attempts analytical solution first; if no solution
        or singularity encountered, falls back seamlessly to Damped Least Squares.
        """
        if q_current is None:
            q_current = np.array([0.0, -np.pi / 2.0, np.pi / 2.0, -np.pi / 2.0, -np.pi / 2.0, 0.0])

        if method in ("analytical", "hybrid"):
            analytical_sols = self.solve_analytical(T_target)
            if analytical_sols:
                best_q = self.select_best_configuration(analytical_sols, q_current)
                T_res = self.fk.compute_fk(best_q)
                err = self.compute_pose_error(T_res, T_target)
                return {
                    "success": True,
                    "joint_angles": best_q,
                    "method": "analytical",
                    "num_solutions": len(analytical_sols),
                    "error_pos": float(np.linalg.norm(err[0:3])),
                    "error_ori": float(np.linalg.norm(err[3:6])),
                    "message": f"Analytical IK found {len(analytical_sols)} solutions; selected closest branch."
                }
            elif method == "analytical":
                return {
                    "success": False,
                    "joint_angles": None,
                    "method": "analytical",
                    "message": "Analytical IK found no valid configuration for target."
                }

        # Fallback or direct numerical DLS
        dls_result = self.solve_numerical_dls(T_target, q_init=q_current)
        dls_result["method"] = "numerical_dls"
        return dls_result


if __name__ == "__main__":
    fk = ForwardKinematics()
    ik = InverseKinematics(fk)

    # 1. Define known initial joint configuration
    q_known = np.array([0.2, -1.0, 1.2, -1.5, -1.2, 0.4])
    T_target = fk.compute_fk(q_known)
    pos_target = T_target[0:3, 3]

    print("=== Testing Inverse Kinematics Closure ===")
    print(f"Target Cartesian Position: {np.round(pos_target, 4)} m")

    # 2. Test Numerical DLS
    res_dls = ik.solve(T_target, q_current=np.zeros(6), method="numerical")
    print(f"\nDLS Result: Success={res_dls['success']} | Iterations={res_dls.get('iterations')} | Error={res_dls['error_pos']:.6e}m")
    if res_dls['success']:
        print("DLS Joint Angles [rad]:", np.round(res_dls['joint_angles'], 4))

    # 3. Test Hybrid Solver
    res_hybrid = ik.solve(T_target, q_current=np.zeros(6), method="hybrid")
    print(f"\nHybrid Result: Method={res_hybrid['method']} | Success={res_hybrid['success']} | Error={res_hybrid['error_pos']:.6e}m")
    if res_hybrid['success']:
        print("Hybrid Joint Angles [rad]:", np.round(res_hybrid['joint_angles'], 4))
