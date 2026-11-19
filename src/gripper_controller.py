"""
Gripper Controller for 6-DOF Manipulator End-Effector
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import time
from typing import Optional
from src.robot_connection import CoppeliaSimBridge


class GripperController:
    """
    Controls robot end-effector gripping mechanism (Robotiq RG2 parallel jaw / Vacuum gripper).
    """

    def __init__(self, bridge: CoppeliaSimBridge, actuation_delay_s: float = 0.5):
        self.bridge = bridge
        self.actuation_delay_s = actuation_delay_s
        self.is_holding_object = False

    def close(self, delay: Optional[float] = None) -> bool:
        """
        Close gripper fingers or activate suction cup to grasp object.
        """
        wait_time = delay if delay is not None else self.actuation_delay_s
        self.bridge.set_gripper_state(True)
        # Advance simulation to allow physics contact
        for _ in range(int(wait_time / 0.05)):
            self.bridge.step_simulation()
            time.sleep(0.01)

        self.is_holding_object = True
        return True

    def open(self, delay: Optional[float] = None) -> bool:
        """
        Open gripper fingers or release suction cup to detach object.
        """
        wait_time = delay if delay is not None else self.actuation_delay_s
        self.bridge.set_gripper_state(False)
        for _ in range(int(wait_time / 0.05)):
            self.bridge.step_simulation()
            time.sleep(0.01)

        self.is_holding_object = False
        return True

    def status(self) -> bool:
        """
        Returns True if gripper is actively grasping.
        """
        return self.bridge.get_gripper_state()
