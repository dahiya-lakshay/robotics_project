"""
Motion Controller and Trajectory Execution Engine for 6-DOF Manipulator
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import time
import numpy as np
from typing import Dict, Any, List, Optional
from src.robot_connection import CoppeliaSimBridge
from src.forward_kinematics import ForwardKinematics
from src.dh_parameters import UR5DHParameters


class MotionController:
    """
    Executes joint-space and Cartesian trajectories on the robot bridge.
    Monitors joint limits, performs safe interpolation, and logs telemetry.
    """

    def __init__(
        self,
        bridge: CoppeliaSimBridge,
        fk: Optional[ForwardKinematics] = None,
        control_frequency_hz: float = 50.0
    ):
        self.bridge = bridge
        self.fk = fk if fk is not None else ForwardKinematics()
        self.control_dt = 1.0 / control_frequency_hz

        # UR5 Joint position limits (radians)
        self.joint_limits = [(-np.pi, np.pi)] * 6

        # Telemetry history
        self.history_time = []
        self.history_commanded_q = []
        self.history_actual_q = []
        self.history_actual_ee_pos = []

    def check_joint_limits(self, q: np.ndarray) -> bool:
        """
        Verify that all 6 joint angles reside within allowable mechanical bounds.
        """
        for i in range(6):
            q_min, q_max = self.joint_limits[i]
            if q[i] < q_min - 1e-3 or q[i] > q_max + 1e-3:
                return False
        return True

    def execute_trajectory(
        self,
        trajectory: Dict[str, Any],
        real_time: bool = False
    ) -> Dict[str, Any]:
        """
        Stream waypoints from a planned trajectory to the robot bridge.
        Logs telemetry and computes tracking metrics.
        """
        positions = trajectory["positions"]
        num_waypoints = len(positions)

        cmd_log = []
        act_log = []
        ee_pos_log = []
        time_log = []

        start_time = time.time()

        for step in range(num_waypoints):
            q_target = positions[step]

            # Enforce bounds
            if not self.check_joint_limits(q_target):
                q_target = np.clip(q_target, -np.pi, np.pi)

            # Send command to robot bridge
            self.bridge.set_joint_target_positions(q_target)
            self.bridge.step_simulation()

            # Read actual feedback
            q_actual = self.bridge.get_joint_positions()
            ee_pose = self.fk.compute_pose(q_actual)

            cmd_log.append(q_target.copy())
            act_log.append(q_actual.copy())
            ee_pos_log.append(ee_pose["position"].copy())
            time_log.append(step * self.control_dt)

            if real_time:
                time.sleep(self.control_dt)

        execution_duration = time.time() - start_time

        cmd_arr = np.array(cmd_log)
        act_arr = np.array(act_log)
        ee_pos_arr = np.array(ee_pos_log)
        time_arr = np.array(time_log)

        # Compute tracking errors
        joint_tracking_error = np.abs(cmd_arr - act_arr)
        max_joint_error = float(np.max(joint_tracking_error))
        rms_joint_error = float(np.sqrt(np.mean(joint_tracking_error ** 2)))

        return {
            "success": True,
            "waypoints_executed": num_waypoints,
            "sim_duration_s": float(time_arr[-1] - time_arr[0]),
            "wall_duration_s": execution_duration,
            "max_tracking_error_rad": max_joint_error,
            "rms_tracking_error_rad": rms_joint_error,
            "commanded_positions": cmd_arr,
            "actual_positions": act_arr,
            "actual_ee_positions": ee_pos_arr,
            "timestamps": time_arr
        }

    def move_to_joint_configuration(
        self,
        q_target: np.ndarray,
        duration: float = 2.0,
        planner=None
    ) -> Dict[str, Any]:
        """
        Smoothly moves the robot from current configuration to target configuration.
        """
        from src.trajectory_planner import TrajectoryPlanner
        if planner is None:
            planner = TrajectoryPlanner(self.fk)

        q_current = self.bridge.get_joint_positions()
        traj = planner.plan_quintic_joint_trajectory(q_current, q_target, duration=duration, dt=self.control_dt)
        return self.execute_trajectory(traj)
