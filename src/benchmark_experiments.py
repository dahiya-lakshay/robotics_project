"""
Empirical Benchmarking and Experimental Evaluation Engine
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend for artifact and plot generation
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from src.dh_parameters import UR5DHParameters
from src.forward_kinematics import ForwardKinematics
from src.inverse_kinematics import InverseKinematics
from src.trajectory_planner import TrajectoryPlanner
from src.pick_and_place import PickAndPlaceStateMachine


class BenchmarkExperiments:
    """
    Executes empirical experiments, gathers quantitative measurements,
    and produces CSV data tables and high-resolution figures.
    """

    def __init__(self, output_dir: str = "results", plots_dir: str = "results/plots"):
        self.output_dir = output_dir
        self.plots_dir = plots_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.plots_dir, exist_ok=True)

        self.fk = ForwardKinematics()
        self.ik = InverseKinematics(self.fk)
        self.planner = TrajectoryPlanner(self.fk, self.ik)

    # =========================================================================
    # EXPERIMENT 1: FK & IK Precision and Convergence across 100 Random Poses
    # =========================================================================
    def run_kinematics_precision_benchmark(self, num_trials: int = 100) -> pd.DataFrame:
        """
        Samples 100 reachable configurations, computes FK, solves IK via Numerical DLS,
        and logs precision, orientation error, solve time, and convergence iterations.
        """
        print(f"\n[Experiment 1] Running Kinematics Precision Benchmark ({num_trials} trials)...")
        np.random.seed(42)  # For reproducible academic verification

        records = []
        for i in range(num_trials):
            # Sample random non-singular joint configuration in operating envelope
            q_truth = np.array([
                np.random.uniform(-2.5, 2.5),
                np.random.uniform(-2.2, -0.5),
                np.random.uniform(0.3, 2.4),
                np.random.uniform(-2.5, 0.0),
                np.random.uniform(-2.5, 2.5),
                np.random.uniform(-2.5, 2.5)
            ])

            # Forward Kinematics ground truth
            T_target = self.fk.compute_fk(q_truth)
            pos_target = T_target[0:3, 3]

            # Solve IK using DLS starting from standard neutral posture
            q_seed = np.array([0.0, -np.pi / 2.0, np.pi / 2.0, -np.pi / 2.0, -np.pi / 2.0, 0.0])
            start_t = time.perf_counter()
            ik_res = self.ik.solve_numerical_dls(T_target, q_init=q_seed)
            solve_time_ms = (time.perf_counter() - start_t) * 1000.0

            if ik_res["success"]:
                q_sol = ik_res["joint_angles"]
                T_actual = self.fk.compute_fk(q_sol)
                pos_actual = T_actual[0:3, 3]

                # Position error in millimeters
                pos_error_mm = float(np.linalg.norm(pos_target - pos_actual) * 1000.0)

                # Orientation error in milliradians
                R_err = T_target[0:3, 0:3] @ T_actual[0:3, 0:3].T
                trace = np.clip((np.trace(R_err) - 1.0) / 2.0, -1.0, 1.0)
                ori_error_mrad = float(np.arccos(trace) * 1000.0)

                records.append({
                    "trial_id": i + 1,
                    "target_x_m": pos_target[0],
                    "target_y_m": pos_target[1],
                    "target_z_m": pos_target[2],
                    "success": 1,
                    "iterations": ik_res["iterations"],
                    "solve_time_ms": solve_time_ms,
                    "pos_error_mm": pos_error_mm,
                    "ori_error_mrad": ori_error_mrad,
                    "manipulability": self.fk.compute_manipulability(q_sol)
                })
            else:
                records.append({
                    "trial_id": i + 1,
                    "target_x_m": pos_target[0],
                    "target_y_m": pos_target[1],
                    "target_z_m": pos_target[2],
                    "success": 0,
                    "iterations": ik_res["iterations"],
                    "solve_time_ms": solve_time_ms,
                    "pos_error_mm": np.nan,
                    "ori_error_mrad": np.nan,
                    "manipulability": np.nan
                })

        df = pd.DataFrame(records)
        csv_path = os.path.join(self.output_dir, "metrics.csv")
        df.to_csv(csv_path, index=False)
        print(f"[Experiment 1] Completed. Results saved to {csv_path}")
        print(f"  -> Success Rate: {df['success'].mean() * 100:.1f}%")
        print(f"  -> Mean Position Error: {df['pos_error_mm'].mean():.4e} mm")
        print(f"  -> Mean Orientation Error: {df['ori_error_mrad'].mean():.4e} mrad")
        print(f"  -> Mean Solve Time: {df['solve_time_ms'].mean():.2f} ms")
        return df

    # =========================================================================
    # EXPERIMENT 2: Trajectory Planning Strategy Comparison
    # =========================================================================
    def run_trajectory_comparison_benchmark(self) -> pd.DataFrame:
        """
        Executes a standardized motion transfer between pick approach stance and
        place approach stance across three distinct mathematical planners:
          1. Joint-Space Cubic Polynomial (C1 continuous)
          2. Joint-Space Quintic Polynomial (C2 continuous / zero boundary jerk)
          3. Joint-Space Trapezoidal Velocity Profile (LSPB)
          4. Cartesian-Space Linear Interpolation with SLERP
        """
        print("\n[Experiment 2] Running Trajectory Planning Strategy Comparison...")

        # Representative pick-to-place transfer configurations
        q_start = np.array([-0.8, -1.2, 1.4, -1.8, -1.5, 0.3])
        q_end = np.array([0.6, -1.0, 1.1, -1.7, -1.5, -0.4])
        fixed_duration = 3.0  # seconds

        # 1. Cubic
        traj_cubic = self.planner.plan_cubic_joint_trajectory(q_start, q_end, duration=fixed_duration)
        met_cubic = self.planner.compute_trajectory_metrics(traj_cubic)

        # 2. Quintic
        traj_quintic = self.planner.plan_quintic_joint_trajectory(q_start, q_end, duration=fixed_duration)
        met_quintic = self.planner.compute_trajectory_metrics(traj_quintic)

        # 3. Trapezoidal LSPB
        traj_trap = self.planner.plan_trapezoidal_joint_trajectory(q_start, q_end)
        met_trap = self.planner.compute_trajectory_metrics(traj_trap)

        # 4. Cartesian Straight Line
        T_start = self.fk.compute_fk(q_start)
        T_end = self.fk.compute_fk(q_end)
        traj_cart = self.planner.plan_cartesian_straight_line(T_start, T_end, duration=fixed_duration, q_seed=q_start)
        met_cart = self.planner.compute_trajectory_metrics(traj_cart)

        comparison_data = [
            {
                "Method": "Joint Cubic Polynomial",
                "Continuity": "C^1 (Position, Velocity)",
                "Duration (s)": met_cubic["duration_s"],
                "Max Velocity (rad/s)": met_cubic["max_joint_velocity_rad_s"],
                "Max Acceleration (rad/s^2)": met_cubic["max_joint_acceleration_rad_s2"],
                "Jerk Metric (cost)": met_cubic["jerk_metric"],
                "Cartesian Path Length (m)": met_cubic["cartesian_path_length_m"],
                "Computational Complexity": "O(N) Analytical"
            },
            {
                "Method": "Joint Quintic Polynomial",
                "Continuity": "C^2 (Position, Velocity, Acceleration)",
                "Duration (s)": met_quintic["duration_s"],
                "Max Velocity (rad/s)": met_quintic["max_joint_velocity_rad_s"],
                "Max Acceleration (rad/s^2)": met_quintic["max_joint_acceleration_rad_s2"],
                "Jerk Metric (cost)": met_quintic["jerk_metric"],
                "Cartesian Path Length (m)": met_quintic["cartesian_path_length_m"],
                "Computational Complexity": "O(N) Analytical"
            },
            {
                "Method": "Joint Trapezoidal (LSPB)",
                "Continuity": "C^0 (Acceleration has discontinuities)",
                "Duration (s)": met_trap["duration_s"],
                "Max Velocity (rad/s)": met_trap["max_joint_velocity_rad_s"],
                "Max Acceleration (rad/s^2)": met_trap["max_joint_acceleration_rad_s2"],
                "Jerk Metric (cost)": met_trap["jerk_metric"],
                "Cartesian Path Length (m)": met_trap["cartesian_path_length_m"],
                "Computational Complexity": "O(N) Piecewise"
            },
            {
                "Method": "Cartesian Straight-Line (SLERP)",
                "Continuity": "Task-space Linear C^1",
                "Duration (s)": met_cart["duration_s"],
                "Max Velocity (rad/s)": met_cart["max_joint_velocity_rad_s"],
                "Max Acceleration (rad/s^2)": met_cart["max_joint_acceleration_rad_s2"],
                "Jerk Metric (cost)": met_cart["jerk_metric"],
                "Cartesian Path Length (m)": met_cart["cartesian_path_length_m"],
                "Computational Complexity": "O(N * IK_iter) Iterative"
            }
        ]

        df_comp = pd.DataFrame(comparison_data)
        csv_path = os.path.join(self.output_dir, "comparison.csv")
        df_comp.to_csv(csv_path, index=False)
        print(f"[Experiment 2] Completed. Results saved to {csv_path}")

        # Store trajectories for plotting
        self.trajectories = {
            "cubic": traj_cubic,
            "quintic": traj_quintic,
            "trapezoidal": traj_trap,
            "cartesian": traj_cart
        }
        return df_comp

    # =========================================================================
    # EXPERIMENT 3: Plot Generation for Academic Report & Presentation
    # =========================================================================
    def generate_publication_figures(self, df_metrics: pd.DataFrame, df_comp: pd.DataFrame):
        """
        Creates publication-quality 300-DPI Matplotlib figures.
        """
        print("\n[Visuals] Rendering publication-quality engineering plots...")

        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

        # -------------------------------------------------------------
        # Figure 1: 3D Robot Kinematic Link Frame Diagram
        # -------------------------------------------------------------
        fig = plt.figure(figsize=(9, 7), dpi=300)
        ax = fig.add_subplot(111, projection='3d')

        q_pose = np.array([0.4, -0.9, 1.3, -1.6, -1.5, 0.4])
        T_cum = self.fk.get_cumulative_transformations(q_pose)

        origins = np.array([T[0:3, 3] for T in T_cum])
        ax.plot(origins[:, 0], origins[:, 1], origins[:, 2], 'o-', color='#1f77b4', linewidth=4, markersize=8, label="UR5 Link Structure")

        # Draw coordinate frame triad at each joint
        axis_len = 0.08
        for i, T in enumerate(T_cum):
            p = T[0:3, 3]
            R = T[0:3, 0:3]
            ax.quiver(p[0], p[1], p[2], R[0, 0]*axis_len, R[1, 0]*axis_len, R[2, 0]*axis_len, color='red', alpha=0.8, arrow_length_ratio=0.2)
            ax.quiver(p[0], p[1], p[2], R[0, 1]*axis_len, R[1, 1]*axis_len, R[2, 1]*axis_len, color='green', alpha=0.8, arrow_length_ratio=0.2)
            ax.quiver(p[0], p[1], p[2], R[0, 2]*axis_len, R[1, 2]*axis_len, R[2, 2]*axis_len, color='blue', alpha=0.8, arrow_length_ratio=0.2)
            ax.text(p[0], p[1], p[2] + 0.02, f"F_{i}", fontsize=9, fontweight='bold')

        ax.set_title("Universal Robots UR5 6-DOF Kinematic Frame Assignment (Standard D-H)", fontsize=12, pad=15)
        ax.set_xlabel("X (meters)")
        ax.set_ylabel("Y (meters)")
        ax.set_zlabel("Z (meters)")
        ax.set_xlim([-0.8, 0.8])
        ax.set_ylim([-0.8, 0.8])
        ax.set_zlim([-0.2, 1.0])
        ax.legend(loc='upper right')
        plt.tight_layout()
        f1_path = os.path.join(self.plots_dir, "fig1_dh_kinematic_frames.png")
        plt.savefig(f1_path, dpi=300)
        plt.close()
        print(f"  -> Generated: {f1_path}")

        # -------------------------------------------------------------
        # Figure 2: Trajectory Profiles (Position, Velocity, Acceleration vs Time)
        # -------------------------------------------------------------
        fig, axes = plt.subplots(3, 1, figsize=(10, 8), dpi=300, sharex=True)

        t_quintic = self.trajectories["quintic"]["time"]
        q_quintic = self.trajectories["quintic"]["positions"]
        v_quintic = self.trajectories["quintic"]["velocities"]
        a_quintic = self.trajectories["quintic"]["accelerations"]

        for j in range(6):
            axes[0].plot(t_quintic, q_quintic[:, j], label=f"Joint {j+1}")
            axes[1].plot(t_quintic, v_quintic[:, j], label=f"Joint {j+1}")
            axes[2].plot(t_quintic, a_quintic[:, j], label=f"Joint {j+1}")

        axes[0].set_ylabel("Joint Position (rad)", fontweight='bold')
        axes[0].set_title("Quintic Polynomial Trajectory Profiles across all 6 Revolute Joints", fontsize=12, pad=10)
        axes[0].grid(True, linestyle='--', alpha=0.6)
        axes[0].legend(loc='upper right', ncol=6, fontsize=8)

        axes[1].set_ylabel("Joint Velocity (rad/s)", fontweight='bold')
        axes[1].grid(True, linestyle='--', alpha=0.6)

        axes[2].set_ylabel("Joint Acceleration (rad/s²)", fontweight='bold')
        axes[2].set_xlabel("Time (seconds)", fontweight='bold')
        axes[2].grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        f2_path = os.path.join(self.plots_dir, "fig2_trajectory_joint_profiles.png")
        plt.savefig(f2_path, dpi=300)
        plt.close()
        print(f"  -> Generated: {f2_path}")

        # -------------------------------------------------------------
        # Figure 3: 3D Cartesian Task-Space Pick-and-Place Path
        # -------------------------------------------------------------
        fig = plt.figure(figsize=(9, 7), dpi=300)
        ax = fig.add_subplot(111, projection='3d')

        # Simulate pick-and-place end-effector path
        sm = PickAndPlaceStateMachine(trajectory_method="quintic")
        pick_pt = np.array([0.35, 0.15, 0.05])
        place_pt = np.array([0.10, 0.38, 0.05])
        pre_pick = pick_pt + np.array([0.0, 0.0, 0.12])
        pre_place = place_pt + np.array([0.0, 0.0, 0.12])

        path_pts = np.vstack([
            np.array([0.0, -0.487, 0.432]),  # Home
            pre_pick,
            pick_pt,
            pre_pick,
            pre_place,
            place_pt,
            pre_place,
            np.array([0.0, -0.487, 0.432])   # Return Home
        ])

        ax.plot(path_pts[:, 0], path_pts[:, 1], path_pts[:, 2], 'o--', color='#e377c2', linewidth=2, markersize=6, label="Pick-and-Place Waypoint Path")
        ax.scatter([pick_pt[0]], [pick_pt[1]], [pick_pt[2]], color='green', s=120, marker='^', label="Pick Target [0.35, 0.15, 0.05]")
        ax.scatter([place_pt[0]], [place_pt[1]], [place_pt[2]], color='red', s=120, marker='v', label="Place Target [0.10, 0.38, 0.05]")

        ax.set_title("3D Cartesian Task-Space Pick-and-Place Trajectory Sequence", fontsize=12, pad=15)
        ax.set_xlabel("X (meters)")
        ax.set_ylabel("Y (meters)")
        ax.set_zlabel("Z (meters)")
        ax.legend(loc='upper right')
        plt.tight_layout()
        f3_path = os.path.join(self.plots_dir, "fig3_cartesian_path_comparison.png")
        plt.savefig(f3_path, dpi=300)
        plt.close()
        print(f"  -> Generated: {f3_path}")

        # -------------------------------------------------------------
        # Figure 4: Kinematics Precision & Convergence Distributions
        # -------------------------------------------------------------
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

        # Subplot A: Positioning Error Distribution (in micrometers)
        pos_err_um = df_metrics["pos_error_mm"].dropna() * 1000.0  # convert to micrometers
        axes[0].hist(pos_err_um, bins=25, color='#2ca02c', edgecolor='black', alpha=0.8)
        axes[0].set_title("End-Effector Positioning Accuracy (100 Poses)", fontsize=11, fontweight='bold')
        axes[0].set_xlabel("Positioning Error (μm)")
        axes[0].set_ylabel("Frequency (Trial Count)")
        axes[0].grid(True, linestyle='--', alpha=0.6)

        # Subplot B: DLS Convergence Iterations
        axes[1].hist(df_metrics["iterations"].dropna(), bins=15, color='#ff7f0e', edgecolor='black', alpha=0.8)
        axes[1].set_title("DLS Inverse Kinematics Convergence Iterations", fontsize=11, fontweight='bold')
        axes[1].set_xlabel("Iterations to Convergence (< 0.1 mm tolerance)")
        axes[1].set_ylabel("Frequency (Trial Count)")
        axes[1].grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        f4_path = os.path.join(self.plots_dir, "fig4_ik_position_orientation_error.png")
        plt.savefig(f4_path, dpi=300)
        plt.close()
        print(f"  -> Generated: {f4_path}")

        # -------------------------------------------------------------
        # Figure 5: Trajectory Performance Metric Comparison
        # -------------------------------------------------------------
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

        methods = ["Cubic", "Quintic", "Trapezoidal (LSPB)"]
        vels = [
            df_comp.loc[df_comp["Method"] == "Joint Cubic Polynomial", "Max Velocity (rad/s)"].values[0],
            df_comp.loc[df_comp["Method"] == "Joint Quintic Polynomial", "Max Velocity (rad/s)"].values[0],
            df_comp.loc[df_comp["Method"] == "Joint Trapezoidal (LSPB)", "Max Velocity (rad/s)"].values[0]
        ]
        jerks = [
            df_comp.loc[df_comp["Method"] == "Joint Cubic Polynomial", "Jerk Metric (cost)"].values[0],
            df_comp.loc[df_comp["Method"] == "Joint Quintic Polynomial", "Jerk Metric (cost)"].values[0],
            df_comp.loc[df_comp["Method"] == "Joint Trapezoidal (LSPB)", "Jerk Metric (cost)"].values[0]
        ]

        # Bar chart 1: Peak Velocity
        axes[0].bar(methods, vels, color=['#1f77b4', '#2ca02c', '#d62728'], edgecolor='black', alpha=0.85)
        axes[0].set_title("Peak Joint Velocity Comparison", fontsize=11, fontweight='bold')
        axes[0].set_ylabel("Peak Velocity (rad/s)")
        axes[0].grid(True, linestyle='--', alpha=0.6)

        # Bar chart 2: Jerk Cost (log scale)
        axes[1].bar(methods, jerks, color=['#1f77b4', '#2ca02c', '#d62728'], edgecolor='black', alpha=0.85)
        axes[1].set_yscale('log')
        axes[1].set_title("Motion Smoothness / Jerk Metric Cost (Log Scale)", fontsize=11, fontweight='bold')
        axes[1].set_ylabel("Integral Jerk Metric ∫||dddq||² dt")
        axes[1].grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        f5_path = os.path.join(self.plots_dir, "fig5_trajectory_metrics_comparison.png")
        plt.savefig(f5_path, dpi=300)
        plt.close()
        print(f"  -> Generated: {f5_path}")


if __name__ == "__main__":
    benchmark = BenchmarkExperiments()
    df_metrics = benchmark.run_kinematics_precision_benchmark(num_trials=100)
    df_comp = benchmark.run_trajectory_comparison_benchmark()
    benchmark.generate_publication_figures(df_metrics, df_comp)
    print("\n[Benchmark] All experiments, data logs, and figures generated successfully!")
