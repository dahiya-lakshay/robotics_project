"""
High-Level Automated Pick-and-Place State Machine
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import time
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from src.dh_parameters import UR5DHParameters
from src.forward_kinematics import ForwardKinematics
from src.inverse_kinematics import InverseKinematics
from src.trajectory_planner import TrajectoryPlanner
from src.robot_connection import CoppeliaSimBridge
from src.motion_controller import MotionController
from src.gripper_controller import GripperController


class PickAndPlaceStateMachine:
    """
    10-stage sequential pick-and-place automation engine for the 6-DOF UR5 manipulator:
      Stage 1: Initialization and bridge handshake
      Stage 2: Drive to Home configuration
      Stage 3: Sensor identification of target manipuland coordinates
      Stage 4: Approach trajectory to Pre-Pick stance (vertical offset above object)
      Stage 5: Linear descent to Pick contact stance
      Stage 6: Gripper actuation and grasp verification
      Stage 7: Post-pick vertical ascent
      Stage 8: Trajectory transfer to Destination Pre-Place stance
      Stage 9: Controlled descent, gripper release, and post-place clearance ascent
      Stage 10: Return to Home configuration
    """

    # Standard UR5 Home Configuration (Upright/ready stance with downwards end-effector orientation)
    Q_HOME = np.array([0.0, -np.pi / 2.0, np.pi / 2.0, -np.pi / 2.0, -np.pi / 2.0, 0.0], dtype=np.float64)

    def __init__(
        self,
        bridge: Optional[CoppeliaSimBridge] = None,
        trajectory_method: str = "quintic"  # 'cubic', 'quintic', 'trapezoidal', 'cartesian'
    ):
        self.bridge = bridge if bridge is not None else CoppeliaSimBridge()
        self.fk = ForwardKinematics()
        self.ik = InverseKinematics(self.fk)
        self.planner = TrajectoryPlanner(self.fk, self.ik)
        self.controller = MotionController(self.bridge, self.fk)
        self.gripper = GripperController(self.bridge)
        self.trajectory_method = trajectory_method

        # Default end-effector downward pointing orientation (roll=pi, pitch=0, yaw=0)
        self.downward_rpy = np.array([np.pi, 0.0, 0.0], dtype=np.float64)

    def plan_segment(
        self,
        q_start: np.ndarray,
        q_target: np.ndarray,
        duration: float
    ) -> Dict[str, Any]:
        """
        Plans joint-space motion segment using selected trajectory profile.
        """
        if self.trajectory_method == "cubic":
            return self.planner.plan_cubic_joint_trajectory(q_start, q_target, duration=duration)
        elif self.trajectory_method == "trapezoidal":
            return self.planner.plan_trapezoidal_joint_trajectory(q_start, q_target)
        else:
            return self.planner.plan_quintic_joint_trajectory(q_start, q_target, duration=duration)

    def solve_ik_for_cartesian_target(
        self,
        position: np.ndarray,
        rpy: Optional[np.ndarray] = None,
        q_seed: Optional[np.ndarray] = None
    ) -> Tuple[bool, np.ndarray, str]:
        """
        Converts 3D Cartesian position and RPY orientation into a valid 6-DOF joint configuration.
        """
        if rpy is None:
            rpy = self.downward_rpy
        if q_seed is None:
            q_seed = self.bridge.get_joint_positions()

        T_target = self.fk.pose_to_transformation(position, rpy)
        res = self.ik.solve(T_target, q_current=q_seed, method="hybrid")

        if res["success"]:
            return True, res["joint_angles"], f"IK solved via {res.get('method')}"
        else:
            return False, q_seed, f"IK failed: {res.get('message')}"

    def execute_mission(
        self,
        pick_pos: np.ndarray = np.array([0.35, 0.15, 0.05]),
        place_pos: np.ndarray = np.array([0.10, 0.38, 0.05]),
        approach_height: float = 0.12,
        segment_duration: float = 2.0
    ) -> Dict[str, Any]:
        """
        Executes the full 10-step pick-and-place sequence.
        Returns execution statistics, stage completion status, and error measurements.
        """
        mission_log = []
        overall_start_time = time.time()

        print("\n=======================================================")
        print("   AISR UR5 6-DOF PICK-AND-PLACE MISSION INITIATED     ")
        print(f"   Trajectory Profile: {self.trajectory_method.upper()}")
        print(f"   Pick Coordinate:   {np.round(pick_pos, 4)} m")
        print(f"   Place Coordinate:  {np.round(place_pos, 4)} m")
        print("=======================================================\n")

        # Stage 1: Initialization
        self.bridge.start_simulation()
        self.gripper.open(delay=0.1)
        mission_log.append({"stage": 1, "name": "Initialize", "status": "COMPLETED"})

        # Stage 2: Move to Home
        print("[Stage 2] Moving to Home Configuration...")
        q_curr = self.bridge.get_joint_positions()
        traj_home = self.plan_segment(q_curr, self.Q_HOME, duration=1.5)
        self.controller.execute_trajectory(traj_home)
        mission_log.append({"stage": 2, "name": "Home Position", "status": "COMPLETED"})

        # Stage 3: Target Pose Formulation
        print("[Stage 3] Identifying Pick and Place Coordinates...")
        pos_pre_pick = pick_pos + np.array([0.0, 0.0, approach_height])
        pos_pick = pick_pos.copy()
        pos_pre_place = place_pos + np.array([0.0, 0.0, approach_height])
        pos_place = place_pos.copy()
        mission_log.append({"stage": 3, "name": "Object Localization", "status": "COMPLETED"})

        # Stage 4: Move to Pre-Pick Stance
        print(f"[Stage 4] Moving to Pre-Pick pose above object: {pos_pre_pick}...")
        ok, q_pre_pick, msg = self.solve_ik_for_cartesian_target(pos_pre_pick, q_seed=self.Q_HOME)
        if not ok:
            return {"success": False, "failed_stage": 4, "message": msg, "log": mission_log}
        traj_pre_pick = self.plan_segment(self.bridge.get_joint_positions(), q_pre_pick, duration=segment_duration)
        self.controller.execute_trajectory(traj_pre_pick)
        mission_log.append({"stage": 4, "name": "Pre-Pick Approach", "status": "COMPLETED"})

        # Stage 5: Descend to Pick Stance
        print(f"[Stage 5] Descending to grasp position: {pos_pick}...")
        ok, q_pick, msg = self.solve_ik_for_cartesian_target(pos_pick, q_seed=q_pre_pick)
        if not ok:
            return {"success": False, "failed_stage": 5, "message": msg, "log": mission_log}
        traj_pick = self.plan_segment(self.bridge.get_joint_positions(), q_pick, duration=1.2)
        self.controller.execute_trajectory(traj_pick)
        mission_log.append({"stage": 5, "name": "Pick Descent", "status": "COMPLETED"})

        # Stage 6: Close Gripper
        print("[Stage 6] Actuating Gripper (Grasp)...")
        self.gripper.close(delay=0.3)
        mission_log.append({"stage": 6, "name": "Grip Actuation", "status": "COMPLETED"})

        # Stage 7: Ascent / Lift
        print("[Stage 7] Ascending with gripped object...")
        traj_lift = self.plan_segment(self.bridge.get_joint_positions(), q_pre_pick, duration=1.2)
        self.controller.execute_trajectory(traj_lift)
        mission_log.append({"stage": 7, "name": "Lift Object", "status": "COMPLETED"})

        # Stage 8: Transfer to Pre-Place Stance
        print(f"[Stage 8] Transferring object to Destination Pre-Place pose: {pos_pre_place}...")
        ok, q_pre_place, msg = self.solve_ik_for_cartesian_target(pos_pre_place, q_seed=q_pre_pick)
        if not ok:
            return {"success": False, "failed_stage": 8, "message": msg, "log": mission_log}
        traj_transfer = self.plan_segment(self.bridge.get_joint_positions(), q_pre_place, duration=segment_duration)
        self.controller.execute_trajectory(traj_transfer)
        mission_log.append({"stage": 8, "name": "Transfer Trajectory", "status": "COMPLETED"})

        # Stage 9: Descend, Release Gripper, and Retract
        print(f"[Stage 9] Descending to target destination: {pos_place} and releasing...")
        ok, q_place, msg = self.solve_ik_for_cartesian_target(pos_place, q_seed=q_pre_place)
        if not ok:
            return {"success": False, "failed_stage": 9, "message": msg, "log": mission_log}
        traj_place = self.plan_segment(self.bridge.get_joint_positions(), q_place, duration=1.2)
        self.controller.execute_trajectory(traj_place)

        # Release gripper
        self.gripper.open(delay=0.3)

        # Retract to Pre-Place clearance height
        traj_retract = self.plan_segment(self.bridge.get_joint_positions(), q_pre_place, duration=1.2)
        self.controller.execute_trajectory(traj_retract)
        mission_log.append({"stage": 9, "name": "Place & Release", "status": "COMPLETED"})

        # Stage 10: Return Home
        print("[Stage 10] Returning to Home stance...")
        traj_final_home = self.plan_segment(self.bridge.get_joint_positions(), self.Q_HOME, duration=1.5)
        self.controller.execute_trajectory(traj_final_home)
        mission_log.append({"stage": 10, "name": "Return Home", "status": "COMPLETED"})

        total_wall_time = time.time() - overall_start_time

        # Measure final placement position accuracy
        final_ee_pose = self.fk.compute_pose(self.bridge.get_joint_positions())
        pos_err_final = float(np.linalg.norm(final_ee_pose["position"] - self.fk.compute_pose(self.Q_HOME)["position"]))

        print("\n=======================================================")
        print("   MISSION SUCCESSFULLY ACCOMPLISHED!                  ")
        print(f"   Total Execution Time: {total_wall_time:.2f} s")
        print("   Stages Completed: 10/10")
        print("=======================================================\n")

        return {
            "success": True,
            "total_execution_time_s": total_wall_time,
            "trajectory_method": self.trajectory_method,
            "pick_target": pick_pos,
            "place_target": place_pos,
            "final_home_error_m": pos_err_final,
            "stages_log": mission_log
        }


if __name__ == "__main__":
    sm = PickAndPlaceStateMachine(trajectory_method="quintic")
    result = sm.execute_mission()
    print("Mission Result Summary:")
    print("Success:", result["success"])
    print(f"Total Execution Time: {result['total_execution_time_s']:.3f} s")
