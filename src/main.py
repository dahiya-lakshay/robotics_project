"""
Main CLI Application for AISR 6-DOF Robotic Manipulator Project
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import sys
import argparse
import numpy as np
from src.dh_parameters import UR5DHParameters
from src.forward_kinematics import ForwardKinematics
from src.inverse_kinematics import InverseKinematics
from src.trajectory_planner import TrajectoryPlanner
from src.robot_connection import CoppeliaSimBridge
from src.pick_and_place import PickAndPlaceStateMachine


def parse_args():
    parser = argparse.ArgumentParser(
        description="AISR 6-DOF Robotic Arm Pick-and-Place using D-H Kinematics (UR5)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Operational mode")

    # Mode 1: dh-table
    subparsers.add_parser("dh-table", help="Display standard Denavit-Hartenberg parameter table")

    # Mode 2: fk
    fk_parser = subparsers.add_parser("fk", help="Compute Forward Kinematics for joint angles")
    fk_parser.add_argument(
        "--joints", nargs=6, type=float, default=[0.0, -1.5708, 1.5708, -1.5708, -1.5708, 0.0],
        help="6 joint angles in radians (default: home configuration)"
    )

    # Mode 3: ik
    ik_parser = subparsers.add_parser("ik", help="Compute Inverse Kinematics for target Cartesian pose")
    ik_parser.add_argument(
        "--target-pos", nargs=3, type=float, default=[0.35, 0.15, 0.15],
        help="Target position x y z in meters"
    )
    ik_parser.add_argument(
        "--target-rpy", nargs=3, type=float, default=[3.1416, 0.0, 0.0],
        help="Target orientation roll pitch yaw in radians (default: [pi, 0, 0] downward)"
    )
    ik_parser.add_argument(
        "--method", choices=["analytical", "numerical", "hybrid"], default="hybrid",
        help="IK solver algorithm"
    )

    # Mode 4: pick-and-place
    pnp_parser = subparsers.add_parser("pick-and-place", help="Execute complete automated pick-and-place mission")
    pnp_parser.add_argument(
        "--planner", choices=["cubic", "quintic", "trapezoidal"], default="quintic",
        help="Trajectory planning profile"
    )
    pnp_parser.add_argument(
        "--pick", nargs=3, type=float, default=[0.35, 0.15, 0.05],
        help="Pick position x y z in meters"
    )
    pnp_parser.add_argument(
        "--place", nargs=3, type=float, default=[0.10, 0.38, 0.05],
        help="Place destination x y z in meters"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    if args.command is None or args.command == "pick-and-place":
        planner_type = getattr(args, "planner", "quintic")
        pick_pos = np.array(getattr(args, "pick", [0.35, 0.15, 0.05]))
        place_pos = np.array(getattr(args, "place", [0.10, 0.38, 0.05]))

        sm = PickAndPlaceStateMachine(trajectory_method=planner_type)
        res = sm.execute_mission(pick_pos=pick_pos, place_pos=place_pos)
        print("Execution Status:", "SUCCESS" if res["success"] else "FAILED")

    elif args.command == "dh-table":
        table = UR5DHParameters.get_dh_table_summary()
        print("\n" + "="*70)
        print("          UNIVERSAL ROBOTS UR5 STANDARD D-H PARAMETERS")
        print("="*70)
        header = f"{'Joint':<8}{'Link Name':<18}{'a_i (m)':<12}{'alpha_i (rad)':<16}{'d_i (m)':<12}{'Range':<16}"
        print(header)
        print("-" * 76)
        for row in table:
            print(f"{row['Joint']:<8}{row['Link Name']:<18}{row['a_i (m)']:<12.4f}{row['alpha_i (rad)']:<16.4f}{row['d_i (m)']:<12.4f}{row['theta_range']:<16}")
        print("="*70 + "\n")

    elif args.command == "fk":
        fk = ForwardKinematics()
        q = np.array(args.joints, dtype=np.float64)
        pose = fk.compute_pose(q)
        print("\n" + "="*50)
        print("          FORWARD KINEMATICS RESULT")
        print("="*50)
        print("Input Joint Angles [rad]:", np.round(q, 4))
        print("End-Effector Position [m]:", np.round(pose["position"], 4))
        print("End-Effector RPY [rad]:   ", np.round(pose["rpy_euler"], 4))
        print("Manipulability Index:     ", f"{fk.compute_manipulability(q):.6f}")
        print("\nHomogeneous Transformation Matrix T_0^6:")
        print(np.round(pose["transformation_matrix"], 4))
        print("="*50 + "\n")

    elif args.command == "ik":
        fk = ForwardKinematics()
        ik = InverseKinematics(fk)
        pos = np.array(args.target_pos, dtype=np.float64)
        rpy = np.array(args.target_rpy, dtype=np.float64)
        T_target = fk.pose_to_transformation(pos, rpy)

        res = ik.solve(T_target, method=args.method)
        print("\n" + "="*50)
        print(f"       INVERSE KINEMATICS RESULT ({args.method.upper()})")
        print("="*50)
        print("Target Position [m]:", pos)
        print("Target RPY [rad]:   ", rpy)
        print("Solution Found:     ", res["success"])
        if res["success"]:
            q_sol = res["joint_angles"]
            print("Joint Solution [rad]:", np.round(q_sol, 4))
            print("Position Error [m]:  ", f"{res.get('error_pos', 0.0):.6e}")
            print("Orientation Error:   ", f"{res.get('error_ori', 0.0):.6e}")
        else:
            print("Reason:              ", res.get("message"))
        print("="*50 + "\n")


if __name__ == "__main__":
    main()
