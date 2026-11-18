"""
D-H Parameters Specification for 6-DOF Robotic Manipulator (Universal Robots UR5)
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class DHLink:
    """
    Representation of a single robotic link using standard Denavit-Hartenberg parameters.
    Standard D-H Convention Transformation:
      T(i-1, i) = Rot(z, theta_i) * Trans(z, d_i) * Trans(x, a_i) * Rot(x, alpha_i)
    """
    joint_idx: int
    name: str
    a: float          # Link length (meters)
    alpha: float      # Link twist (radians)
    d: float          # Link offset (meters)
    theta_offset: float  # Constant angle offset (radians)
    joint_min: float  # Lower joint limit (radians)
    joint_max: float  # Upper joint limit (radians)

    def transformation_matrix(self, theta_var: float) -> np.ndarray:
        """
        Compute the 4x4 homogeneous transformation matrix T_{i-1}^i for given variable joint angle.
        """
        theta = theta_var + self.theta_offset
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(self.alpha)
        sa = np.sin(self.alpha)

        # Standard Denavit-Hartenberg transformation matrix
        T = np.array([
            [ct, -st * ca,  st * sa, self.a * ct],
            [st,  ct * ca, -ct * sa, self.a * st],
            [0.0,      sa,       ca,     self.d],
            [0.0,     0.0,      0.0,        1.0]
        ], dtype=np.float64)

        return T


class UR5DHParameters:
    """
    Physical link dimensions and standard D-H parameter definitions for the UR5 manipulator.
    Dimensions verified against Universal Robots kinematic specifications:
      d1 = 0.089159 m (Base to shoulder)
      a2 = -0.42500 m (Upper arm length)
      a3 = -0.39225 m (Forearm length)
      d4 = 0.10915 m  (Wrist 1 offset)
      d5 = 0.09465 m  (Wrist 2 offset)
      d6 = 0.08230 m  (Wrist 3 / Flange offset)
    """
    # Link lengths (meters)
    D1: float = 0.089159
    A2: float = -0.42500
    A3: float = -0.39225
    D4: float = 0.10915
    D5: float = 0.09465
    D6: float = 0.08230

    @classmethod
    def get_links(cls) -> List[DHLink]:
        """
        Returns the ordered list of 6 DHLinks defining the UR5 arm.
        Convention: Standard Denavit-Hartenberg (D-H).
        """
        # Joint limits typically [-2*pi, 2*pi], restricted to [-pi, pi] for conservative workspace control
        joint_limit = np.pi

        return [
            # Link 1: Base to Shoulder
            DHLink(
                joint_idx=1,
                name="Base-Shoulder",
                a=0.0,
                alpha=np.pi / 2.0,
                d=cls.D1,
                theta_offset=0.0,
                joint_min=-joint_limit,
                joint_max=joint_limit
            ),
            # Link 2: Shoulder to Elbow
            DHLink(
                joint_idx=2,
                name="Shoulder-Elbow",
                a=cls.A2,
                alpha=0.0,
                d=0.0,
                theta_offset=0.0,
                joint_min=-joint_limit,
                joint_max=joint_limit
            ),
            # Link 3: Elbow to Wrist 1
            DHLink(
                joint_idx=3,
                name="Elbow-Wrist1",
                a=cls.A3,
                alpha=0.0,
                d=0.0,
                theta_offset=0.0,
                joint_min=-joint_limit,
                joint_max=joint_limit
            ),
            # Link 4: Wrist 1 to Wrist 2
            DHLink(
                joint_idx=4,
                name="Wrist1-Wrist2",
                a=0.0,
                alpha=np.pi / 2.0,
                d=cls.D4,
                theta_offset=0.0,
                joint_min=-joint_limit,
                joint_max=joint_limit
            ),
            # Link 5: Wrist 2 to Wrist 3
            DHLink(
                joint_idx=5,
                name="Wrist2-Wrist3",
                a=0.0,
                alpha=-np.pi / 2.0,
                d=cls.D5,
                theta_offset=0.0,
                joint_min=-joint_limit,
                joint_max=joint_limit
            ),
            # Link 6: Wrist 3 to Flange / End-Effector
            DHLink(
                joint_idx=6,
                name="Wrist3-Flange",
                a=0.0,
                alpha=0.0,
                d=cls.D6,
                theta_offset=0.0,
                joint_min=-joint_limit,
                joint_max=joint_limit
            )
        ]

    @classmethod
    def get_dh_table_summary(cls) -> List[Dict[str, Any]]:
        """
        Returns tabular summary of standard D-H parameters for documentation and reports.
        """
        links = cls.get_links()
        summary = []
        for l in links:
            summary.append({
                "Joint": l.joint_idx,
                "Link Name": l.name,
                "a_i (m)": l.a,
                "alpha_i (rad)": l.alpha,
                "d_i (m)": l.d,
                "theta_offset (rad)": l.theta_offset,
                "theta_range": f"[{l.joint_min:.2f}, {l.joint_max:.2f}]"
            })
        return summary


if __name__ == "__main__":
    import pprint
    print("=== Universal Robots UR5 D-H Parameter Table ===")
    table = UR5DHParameters.get_dh_table_summary()
    pprint.pprint(table)
