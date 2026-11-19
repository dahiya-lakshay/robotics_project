"""
Forward Kinematics and Jacobian Engine for 6-DOF Manipulator (Universal Robots UR5)
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from src.dh_parameters import UR5DHParameters, DHLink


class ForwardKinematics:
    """
    Computes forward kinematics, intermediate link frames, and geometric Jacobian
    for the 6-DOF UR5 robotic arm using standard Denavit-Hartenberg parameters.
    """

    def __init__(self, links: Optional[List[DHLink]] = None):
        if links is None:
            self.links = UR5DHParameters.get_links()
        else:
            self.links = links
        assert len(self.links) == 6, "Manipulator must possess exactly 6 links/joints."

    def get_individual_transformations(self, joint_angles: np.ndarray) -> List[np.ndarray]:
        """
        Compute individual transformation matrices T_{i-1}^i for each joint.
        """
        assert len(joint_angles) == 6, f"Expected 6 joint angles, got {len(joint_angles)}"
        transforms = []
        for i, link in enumerate(self.links):
            T_i = link.transformation_matrix(float(joint_angles[i]))
            transforms.append(T_i)
        return transforms

    def get_cumulative_transformations(self, joint_angles: np.ndarray) -> List[np.ndarray]:
        """
        Compute cumulative transformations T_0^i for each link i in {0, 1, ..., 6}.
        Returns list of 7 matrices: [T_0^0, T_0^1, T_0^2, T_0^3, T_0^4, T_0^5, T_0^6].
        """
        individual_T = self.get_individual_transformations(joint_angles)
        T_cum = [np.eye(4, dtype=np.float64)]

        curr_T = np.eye(4, dtype=np.float64)
        for T_step in individual_T:
            curr_T = curr_T @ T_step
            T_cum.append(curr_T.copy())

        return T_cum

    def compute_fk(self, joint_angles: np.ndarray) -> np.ndarray:
        """
        Compute overall homogeneous transformation matrix T_0^6 from base to end-effector.
        """
        T_cum = self.get_cumulative_transformations(joint_angles)
        return T_cum[-1]

    @staticmethod
    def extract_position(T: np.ndarray) -> np.ndarray:
        """
        Extract 3D Cartesian position vector [x, y, z] from a 4x4 transformation matrix.
        """
        return T[0:3, 3].copy()

    @staticmethod
    def extract_rotation(T: np.ndarray) -> np.ndarray:
        """
        Extract 3x3 orthonormal rotation matrix R from a 4x4 transformation matrix.
        """
        return T[0:3, 0:3].copy()

    @staticmethod
    def rotation_matrix_to_rpy(R: np.ndarray) -> np.ndarray:
        """
        Convert 3x3 rotation matrix to Roll-Pitch-Yaw (RPY) angles [roll, pitch, yaw]
        using standard Z-Y-X Euler convention:
          R = R_z(yaw) * R_y(pitch) * R_x(roll)
        """
        sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
        singular = sy < 1e-6

        if not singular:
            roll = np.arctan2(R[2, 1], R[2, 2])
            pitch = np.arctan2(-R[2, 0], sy)
            yaw = np.arctan2(R[1, 0], R[0, 0])
        else:
            # Gimbal lock singularity
            roll = np.arctan2(-R[1, 2], R[1, 1])
            pitch = np.arctan2(-R[2, 0], sy)
            yaw = 0.0

        return np.array([roll, pitch, yaw], dtype=np.float64)

    @staticmethod
    def rpy_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
        """
        Convert Roll-Pitch-Yaw angles to 3x3 rotation matrix using Z-Y-X convention.
        """
        cr, sr = np.cos(roll), np.sin(roll)
        cp, sp = np.cos(pitch), np.sin(pitch)
        cy, sy = np.cos(yaw), np.sin(yaw)

        Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
        Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
        Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])

        return Rz @ Ry @ Rx

    @staticmethod
    def pose_to_transformation(position: np.ndarray, rpy: np.ndarray) -> np.ndarray:
        """
        Construct 4x4 homogeneous transformation matrix from [x, y, z] and [roll, pitch, yaw].
        """
        R = ForwardKinematics.rpy_to_rotation_matrix(rpy[0], rpy[1], rpy[2])
        T = np.eye(4, dtype=np.float64)
        T[0:3, 0:3] = R
        T[0:3, 3] = position
        return T

    def compute_pose(self, joint_angles: np.ndarray) -> Dict[str, Any]:
        """
        Returns full pose dictionary containing T, position vector, rotation matrix, and RPY angles.
        """
        T = self.compute_fk(joint_angles)
        pos = self.extract_position(T)
        R = self.extract_rotation(T)
        rpy = self.rotation_matrix_to_rpy(R)

        return {
            "transformation_matrix": T,
            "position": pos,
            "rotation_matrix": R,
            "rpy_euler": rpy,
            "x": float(pos[0]),
            "y": float(pos[1]),
            "z": float(pos[2]),
            "roll": float(rpy[0]),
            "pitch": float(rpy[1]),
            "yaw": float(rpy[2])
        }

    def compute_geometric_jacobian(self, joint_angles: np.ndarray) -> np.ndarray:
        """
        Compute 6x6 Geometric Jacobian matrix J(q) relating joint velocities to end-effector velocities:
          V = [v_linear; omega_angular] = J(q) * q_dot

        For revolute joints:
          J_{v, i} = z_{i-1} x (p_e - p_{i-1})
          J_{\\omega, i} = z_{i-1}
        where z_{i-1} is unit axis of joint i, p_{i-1} is origin of frame i-1, and p_e is end-effector origin.
        """
        T_cum = self.get_cumulative_transformations(joint_angles)
        p_e = T_cum[6][0:3, 3]

        J = np.zeros((6, 6), dtype=np.float64)

        for i in range(6):
            T_prev = T_cum[i]
            z_prev = T_prev[0:3, 2]  # z-axis of frame i-1 in base coordinates
            p_prev = T_prev[0:3, 3]  # origin of frame i-1 in base coordinates

            # Linear velocity Jacobian component
            J_v = np.cross(z_prev, (p_e - p_prev))
            # Angular velocity Jacobian component
            J_w = z_prev

            J[0:3, i] = J_v
            J[3:6, i] = J_w

        return J

    def compute_manipulability(self, joint_angles: np.ndarray) -> float:
        """
        Compute Yoshikawa Manipulability Measure:
          w = sqrt(det(J(q) * J(q)^T))
        Indicates distance from kinematic singularities (w -> 0 near singularity).
        """
        J = self.compute_geometric_jacobian(joint_angles)
        JJT = J @ J.T
        det = np.linalg.det(JJT)
        return float(np.sqrt(max(0.0, det)))


if __name__ == "__main__":
    fk = ForwardKinematics()

    # Test configuration 1: All zero angles
    q_zero = np.zeros(6)
    pose_zero = fk.compute_pose(q_zero)
    print("=== Zero Configuration Pose ===")
    print("Position [m]:", np.round(pose_zero["position"], 4))
    print("RPY [rad]:", np.round(pose_zero["rpy_euler"], 4))
    print("Manipulability:", fk.compute_manipulability(q_zero))

    # Test configuration 2: Standard "Upright" configuration [0, -pi/2, 0, -pi/2, 0, 0]
    q_upright = np.array([0.0, -np.pi / 2.0, 0.0, -np.pi / 2.0, 0.0, 0.0])
    pose_upright = fk.compute_pose(q_upright)
    print("\n=== Upright Configuration Pose ===")
    print("Position [m]:", np.round(pose_upright["position"], 4))
    print("RPY [rad]:", np.round(pose_upright["rpy_euler"], 4))
    print("Manipulability:", fk.compute_manipulability(q_upright))
