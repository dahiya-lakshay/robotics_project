"""
Strict 17-Slide Presentation Generator (PDF) conforming to CSAI4014 Slide Deck Rules
Course: CSAI4014 - Algorithms for Intelligent Systems and Robotics
Group: G04 | Project: P02 | Batch: B3
Author: Lakshay Dahiya (SAP: 500121078)
"""

import os
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import pypdf


# Slide Presenter Mapping matching Suggested Slide Plan:
# Slides 1, 2, 3: M1 (Suraj Singh)
# Slides 4, 5, 6: M2 (Sudhanshu Kumar)
# Slides 7, 8, 9: M3 (Abhay Chand Thakur)
# Slides 10, 11, 12: M4 (Lakshay Dahiya)
# Slides 13, 14, 15: M5 (Khushi)
# Slides 16, 17: All Team Members
PRESENTERS = {
    1: "Presenter: Suraj Singh (M1)",
    2: "Presenter: Suraj Singh (M1)",
    3: "Presenter: Suraj Singh (M1)",
    4: "Presenter: Sudhanshu Kumar (M2)",
    5: "Presenter: Sudhanshu Kumar (M2)",
    6: "Presenter: Sudhanshu Kumar (M2)",
    7: "Presenter: Abhay Chand Thakur (M3)",
    8: "Presenter: Abhay Chand Thakur (M3)",
    9: "Presenter: Abhay Chand Thakur (M3)",
    10: "Presenter: Lakshay Dahiya (M4)",
    11: "Presenter: Lakshay Dahiya (M4)",
    12: "Presenter: Lakshay Dahiya (M4)",
    13: "Presenter: Khushi (M5)",
    14: "Presenter: Khushi (M5)",
    15: "Presenter: Khushi (M5)",
    16: "Presenter: All Team Members",
    17: "Presenter: All Team Members"
}


class SlideDeckCanvas(canvas.Canvas):
    """
    Canvas for 17-slide presentation:
    - Removes old top header lines completely.
    - Puts the presenter's name in the top-right corner of each slide.
    - Puts slide counter at the bottom-right corner.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, total_pages):
        page_num = self._pageNumber
        w, h = landscape(letter)

        self.saveState()
        # 1. Presenter's name in top-right corner
        presenter = PRESENTERS.get(page_num, "Presenter: Group G04")
        self.setFont("Helvetica-Bold", 11)
        self.setFillColor(colors.HexColor("#0284C7"))  # Clear sky blue
        self.drawRightString(w - 40, h - 32, presenter)

        # 2. Bottom footer: slide counter at bottom right, subtle topic on left
        self.setFont("Helvetica", 9.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(40, 22, "6-DOF Robotic Arm Pick-and-Place using D-H Kinematics (UR5)")
        self.drawRightString(w - 40, 22, f"Slide {page_num} of {total_pages}")

        # Subtle bottom separator line
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.8)
        self.line(40, 36, w - 40, 36)

        self.restoreState()


def build_presentation(filename="presentation/project_presentation.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    slide_size = landscape(letter)  # 792 x 612 pt
    w, h = slide_size

    doc = SimpleDocTemplate(
        filename,
        pagesize=slide_size,
        leftMargin=40,
        rightMargin=40,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Rule 2: Heading 28-32 pt, Body text at least 20 pt!
    # No LaTeX codes, human-readable symbols only!
    slide_title_style = ParagraphStyle(
        'DeckTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=28, leading=33, textColor=colors.HexColor("#0F172A"),
        spaceAfter=14
    )
    slide_body_style = ParagraphStyle(
        'DeckBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=20, leading=26, textColor=colors.HexColor("#1E293B"),
        spaceBefore=4, spaceAfter=8
    )
    slide_bullet_style = ParagraphStyle(
        'DeckBullet', parent=slide_body_style,
        leftIndent=20, spaceBefore=4, spaceAfter=8
    )
    col_body_style = ParagraphStyle(
        'DeckColBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=18, leading=23, textColor=colors.HexColor("#1E293B"),
        spaceBefore=3, spaceAfter=6
    )
    col_bullet_style = ParagraphStyle(
        'DeckColBullet', parent=col_body_style,
        leftIndent=15, spaceBefore=2, spaceAfter=5
    )

    story = []

    # =========================================================================
    # SLIDE 1: Title Slide (Presenter: M1 - Suraj Singh)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("6-DOF Robotic Arm Pick-and-Place using D-H Kinematics", ParagraphStyle('CoverT', fontName='Helvetica-Bold', fontSize=30, leading=36, alignment=TA_CENTER, textColor=colors.HexColor("#0F172A"))))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Autonomous Manipulation with Universal Robots UR5 in CoppeliaSim", ParagraphStyle('CoverSub', fontName='Helvetica', fontSize=20, leading=25, alignment=TA_CENTER, textColor=colors.HexColor("#0284C7"))))
    story.append(Spacer(1, 16))

    meta_text = [
        [Paragraph("<b>Course:</b> CSAI4014 Algorithms for Intelligent Systems and Robotics", col_body_style),
         Paragraph("<b>Project No.:</b> P02  |  <b>Group No.:</b> G04  |  <b>Batch:</b> B3", col_body_style)],
        [Paragraph("<b>Faculty:</b> Course Faculty, CSAI4014  |  UPES Dehradun", col_body_style),
         Paragraph("<b>Submission Date:</b> 18 November 2026", col_body_style)]
    ]
    t_meta = Table(meta_text, colWidths=[360, 350])
    t_meta.setStyle(TableStyle([('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    team_data = [
        ["S. No.", "Name", "SAP ID", "Role / Focus Area"],
        ["16", "Suraj Singh", "500122962", "Simulation Scene & Robot Configuration"],
        ["17", "Sudhanshu Kumar", "500125146", "Literature Review & Kinematic Verification"],
        ["18", "Abhay Chand Thakur", "500122020", "Trajectory Experiments & Performance Evaluation"],
        ["19", "Lakshay Dahiya (Lead)", "500121078", "D-H Kinematics, IK Solvers & Controller"],
        ["20", "Khushi", "500122966", "Pick-and-Place Validation & Documentation"]
    ]
    t_team = Table(team_data, colWidths=[60, 180, 120, 290])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_team)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: Problem and Motivation (Presenter: M1 - Suraj Singh)
    # =========================================================================
    story.append(Paragraph("Problem Statement & Industrial Need", slide_title_style))
    story.append(Paragraph("• <b>Industrial Need:</b> Modern manufacturing requires robotic arms to pick, transfer, and place components with sub-millimeter precision.", slide_bullet_style))
    story.append(Paragraph("• <b>The Core Challenge:</b> Transferring objects between coordinates without manual teaching, collisions, or dropped payloads.", slide_bullet_style))
    story.append(Paragraph("• <b>Why 6 Degrees of Freedom:</b> 3 position axes (X, Y, Z) plus 3 orientation angles (Roll, Pitch, Yaw) for complete gripper alignment.", slide_bullet_style))
    story.append(Paragraph("• <b>The Motion Quality Problem:</b> Abrupt accelerations cause mechanical jerk, gearbox chatter, and structural fatigue.", slide_bullet_style))
    story.append(Paragraph("• <b>Project Scope:</b> End-to-end automation of a UR5 arm using D-H kinematics and smooth trajectory planning.", slide_bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: Objectives (Presenter: M1 - Suraj Singh)
    # =========================================================================
    story.append(Paragraph("Measurable Project Objectives", slide_title_style))
    story.append(Paragraph("1.  <b>D-H Mathematical Modeling:</b> Establish standard Denavit-Hartenberg parameter table for the Universal Robots UR5.", slide_bullet_style))
    story.append(Paragraph("2.  <b>Pure-Python Kinematics:</b> Implement forward kinematics and inverse kinematics achieving sub-millimeter precision.", slide_bullet_style))
    story.append(Paragraph("3.  <b>Jerk-Minimized Trajectories:</b> Implement quintic polynomial trajectories to eliminate acceleration steps.", slide_bullet_style))
    story.append(Paragraph("4.  <b>Waypoint Dispatch:</b> Establish configured 50 Hz waypoint/control interval (20 ms) in CoppeliaSim using ZeroMQ Remote API (real-time wall-clock execution is not guaranteed).", slide_bullet_style))
    story.append(Paragraph("5.  <b>Sequential Manipulation Pipeline:</b> Implement a scripted 10-stage pick-and-place execution pipeline with trajectory waypoint generation and gripper sequencing.", slide_bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: Existing Solutions (Presenter: M2 - Sudhanshu Kumar)
    # =========================================================================
    story.append(Paragraph("Existing Solutions & The Technical Gap", slide_title_style))
    story.append(Paragraph("• <b>Simulator Black Boxes:</b> Most student setups rely on CoppeliaSim's built-in IK plugin, hiding the actual D-H matrix math.", slide_bullet_style))
    story.append(Paragraph("• <b>Trapezoidal Discontinuity:</b> Trapezoidal LSPB maintains C^1 continuity (pos, vel) but has step discontinuities in acceleration at blending boundaries, producing high computed jerk.", slide_bullet_style))
    story.append(Paragraph("• <b>Singularity Vulnerability:</b> Simple pseudoinverse solvers diverge near wrist and shoulder singularities.", slide_bullet_style))
    story.append(Spacer(1, 8))

    tbl_s4 = [
        ["Approach", "Core Strength", "Critical Limitation"],
        ["Pure Analytical IK", "Fast closed-form solve", "Diverges near singular points"],
        ["Pure Numerical IK", "General geometry support", "Sensitive to seed; slow convergence"],
        ["Trapezoidal Profiles (C^1)", "Computationally simple", "Acceleration steps at blends cause high jerk"],
        ["Our Hybrid D-H System", "Singularity-robust & sub-50 um", "Requires dynamic damping tuning"]
    ]
    t4_deck = Table(tbl_s4, colWidths=[200, 230, 280])
    t4_deck.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t4_deck)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: Novelty (Presenter: M2 - Sudhanshu Kumar)
    # =========================================================================
    story.append(Paragraph("Project Novelty (Mandatory Contributions)", slide_title_style))
    story.append(Paragraph("1.  <b>Independent Pure-Python D-H Engine:</b> All homogeneous matrix products, Jacobians, and inverse kinematics execute in Python from first principles.", slide_bullet_style))
    story.append(Paragraph("2.  <b>Hybrid Analytical and DLS Solver:</b> Closed-form Pieper decoupling combined with adaptive Damped Least Squares eliminates singularity blowups.", slide_bullet_style))
    story.append(Paragraph("3.  <b>98.1% Computed Jerk Metric Reduction:</b> Quintic polynomial trajectory cuts computed jerk metric from 414.7 down to 7.9 compared to trapezoidal LSPB motion.", slide_bullet_style))
    story.append(Paragraph("4.  <b>Zero-Downtime Virtual Fallback:</b> Fast TCP probe automatically enables high-fidelity virtual simulation if CoppeliaSim GUI is offline.", slide_bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: Syllabus Mapping (Presenter: M2 - Sudhanshu Kumar)
    # =========================================================================
    story.append(Paragraph("CSAI4014 Syllabus Mapping", slide_title_style))
    syl_table_data = [
        ["AISR Curriculum Topic", "Mathematical Principle", "Applied Project Module"],
        ["Coordinate Frames", "4x4 Homogeneous Transformations", "Forward Kinematics serial chain"],
        ["D-H Representation", "Standard (a, alpha, d, theta)", "UR5 6-link parameter table"],
        ["Differential Kinematics", "6x6 Geometric Jacobian V = J * q_dot", "Velocity mapping & manipulability"],
        ["Inverse Kinematics", "Damped Least Squares regularisation", "Hybrid Pieper and DLS solver"],
        ["Trajectory Planning", "Quintic polynomial C^2 continuity", "Smooth jerk-minimized profiles"]
    ]
    t_syl_deck = Table(syl_table_data, colWidths=[200, 260, 250])
    t_syl_deck.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t_syl_deck)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: System Architecture (Presenter: M3 - Abhay Chand Thakur)
    # =========================================================================
    story.append(Paragraph("System Architecture", slide_title_style))
    fig0_file = "results/plots/fig0_system_block_diagram.png"
    if os.path.exists(fig0_file):
        story.append(Image(fig0_file, width=680, height=210))
        story.append(Spacer(1, 10))

    story.append(Paragraph("• <b>Modular Flow:</b> Task Pose defines target; Planner generates smooth trajectory; IK resolves joint angles; Controller dispatches waypoints at configured 50 Hz interval (20 ms; real-time execution not guaranteed).", slide_bullet_style))
    story.append(Paragraph("• <b>Synchronous Lockstep:</b> Simulation clock advances only when commanded, guaranteeing repeatable physics execution.", slide_bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: Robot and Environment Model (Presenter: M3 - Abhay Chand Thakur)
    # =========================================================================
    story.append(Paragraph("Robot & Environment Model", slide_title_style))
    fig1_file = "results/plots/fig1_dh_kinematic_frames.png"

    col_s8 = [
        [
            Image(fig1_file, width=320, height=260) if os.path.exists(fig1_file) else Paragraph("Diagram", slide_body_style),
            Paragraph("<b>Universal Robots UR5 Specs:</b><br/>"
                      "• 6 Revolute Joints (Degrees of Freedom)<br/>"
                      "• Reach Radius: 0.85 m  |  Payload: 5.0 kg<br/>"
                      "• Repeatability: +/- 0.1 mm<br/><br/>"
                      "<b>Workstation Layout:</b><br/>"
                      "• Pick Object: (0.35, 0.15, 0.05) m<br/>"
                      "• Place Target: (0.10, 0.38, 0.05) m<br/>"
                      "• Approach Height: +12 cm vertical clearance<br/>"
                      "• Gripper: Robotiq RG2 Parallel Jaw Gripper", col_body_style)
        ]
    ]
    t_s8 = Table(col_s8, colWidths=[330, 380])
    t_s8.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_s8)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: Algorithm 1 (Presenter: M3 - Abhay Chand Thakur)
    # =========================================================================
    story.append(Paragraph("Algorithm 1: Forward Kinematics & D-H Modeling", slide_title_style))
    story.append(Paragraph("• <b>Standard D-H Matrix Rule:</b> T(i-1, i) = Rot(z, theta) * Trans(z, d) * Trans(x, a) * Rot(x, alpha)", slide_bullet_style))
    story.append(Paragraph("• <b>UR5 Link Geometry:</b> d1 = 89.2 mm, a2 = -425.0 mm, a3 = -392.3 mm, d4 = 109.2 mm, d5 = 94.7 mm, d6 = 82.3 mm", slide_bullet_style))
    story.append(Paragraph("• <b>Composite End-Effector Matrix:</b> T_0_6 = T_0_1 * T_1_2 * T_2_3 * T_3_4 * T_4_5 * T_5_6", slide_bullet_style))
    story.append(Paragraph("• <b>Pose Extraction:</b> Cartesian position (X, Y, Z) and Roll-Pitch-Yaw angles extracted with zero ambiguity.", slide_bullet_style))
    story.append(Paragraph("• <b>Geometric Jacobian:</b> Evaluates linear and angular velocity mapping V = J * q_dot.", slide_bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: Algorithm 2 / Controller Design (Presenter: M4 - Lakshay Dahiya)
    # =========================================================================
    story.append(Paragraph("Algorithm 2: Inverse Kinematics & Trajectory Planning", slide_title_style))
    story.append(Paragraph("• <b>Analytical Decoupling (Pieper):</b> Spherical wrist allows position (joints 1-3) and orientation (joints 4-6) to be solved independently.", slide_bullet_style))
    story.append(Paragraph("• <b>Damped Least Squares (DLS):</b> Delta_q = J^T * (J * J^T + lambda^2 * I)^(-1) * error prevents infinite velocities near singularities.", slide_bullet_style))
    story.append(Paragraph("• <b>Quintic Trajectory Planning:</b> Enforces zero boundary velocity and acceleration, guaranteeing mathematical C^2 continuity.", slide_bullet_style))
    story.append(Paragraph("• <b>Smoothness Metric:</b> Continuous acceleration avoids analytical step discontinuities, reducing computed jerk metrics.", slide_bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 11: Simulation Setup (Presenter: M4 - Lakshay Dahiya)
    # =========================================================================
    story.append(Paragraph("Simulation Setup & ZeroMQ Interface", slide_title_style))
    story.append(Paragraph("• <b>Simulator Platform:</b> CoppeliaSim Edu V4.3+ interface via ZeroMQ Remote API (port 23000, CBOR serialization).", slide_bullet_style))
    story.append(Paragraph("• <b>Waypoint Rate:</b> Configured 50 Hz waypoint/control interval (20 ms); real-time wall-clock execution is not guaranteed; includes virtual kinematic fallback mode.", slide_bullet_style))
    story.append(Paragraph("• <b>Execution & Kinematics Validation Commands:</b>", slide_bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;<b>python -m src.forward_kinematics</b>", col_body_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;<b>python -m src.inverse_kinematics</b>", col_body_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;<b>python -m src.main pick-and-place --planner quintic</b>", col_body_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 12: Live Demonstration (Presenter: M4 - Lakshay Dahiya)
    # =========================================================================
    story.append(Paragraph("Live Demonstration: 10-Stage State Machine", slide_title_style))
    fig3_file = "results/plots/fig3_cartesian_path_comparison.png"

    col_s12 = [
        [
            Image(fig3_file, width=330, height=270) if os.path.exists(fig3_file) else Paragraph("Diagram", slide_body_style),
            Paragraph("<b>Scripted 10-Stage Execution Pipeline:</b><br/>"
                      "1-2. Init & Home Stance<br/>"
                      "3-4. Locate Target & Approach (+12 cm)<br/>"
                      "5-6. Controlled Descent & Virtual Grasp<br/>"
                      "7-8. Clearance Ascent & Transfer<br/>"
                      "9-10. Place at Target & Return Home<br/><br/>"
                      "<b>[Switch to running standalone / simulation demonstration]</b>", col_body_style)
        ]
    ]
    t_s12 = Table(col_s12, colWidths=[340, 370])
    t_s12.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_s12)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 13: Results 1 (Presenter: M5 - Khushi)
    # =========================================================================
    story.append(Paragraph("Results 1: Kinematic Precision & Convergence", slide_title_style))
    fig4_file = "results/plots/fig4_ik_position_orientation_error.png"

    col_s13 = [
        [
            Image(fig4_file, width=330, height=230) if os.path.exists(fig4_file) else Paragraph("Diagram", slide_body_style),
            Paragraph("<b>Validation over 100 Random IK Trials:</b><br/>"
                      "• <b>IK Convergence Rate:</b> 81.0% (81/100 trials)<br/><br/>"
                      "• <b>Mean Position Error (Successful):</b> 0.0462 mm (max: 0.0996 mm)<br/><br/>"
                      "• <b>Mean Orientation Error (Successful):</b> 0.0140 mrad<br/><br/>"
                      "• <b>Mean Solve Time:</b> 9.67 ms (all 100) / ~5.57 ms (successful)<br/><br/>"
                      "• <b>Mean Iterations (Successful):</b> ~26.1 iterations", col_body_style)
        ]
    ]
    t_s13 = Table(col_s13, colWidths=[340, 370])
    t_s13.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_s13)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 14: Results 2 and Comparison (Presenter: M5 - Khushi)
    # =========================================================================
    story.append(Paragraph("Results 2: Trajectory Benchmark & Jerk Cost", slide_title_style))
    fig5_file = "results/plots/fig5_trajectory_metrics_comparison.png"

    col_s14 = [
        [
            Image(fig5_file, width=330, height=220) if os.path.exists(fig5_file) else Paragraph("Diagram", slide_body_style),
            Paragraph("<b>Comparative Trajectory Benchmark:</b><br/>"
                      "• <b>Trapezoidal LSPB:</b> C^1 continuous (duration 1.53 s); acceleration step discontinuities at blends yield Computed Jerk Metric = <b>414.74</b>.<br/><br/>"
                      "• <b>Cubic Polynomial:</b> C^1 continuous; lowest Computed Jerk Metric = <b>1.55</b>.<br/><br/>"
                      "• <b>Quintic Polynomial:</b> Mathematical C^2 continuity (pos, vel, acc); Computed Jerk Metric = <b>7.91</b>.<br/><br/>"
                      "• <b>Key Result:</b> Quintic profile achieves a <b>98.1% reduction in computed jerk metric</b> compared with trapezoidal LSPB.", col_body_style)
        ]
    ]
    t_s14 = Table(col_s14, colWidths=[340, 370])
    t_s14.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_s14)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 15: Team Contribution (Presenter: M5 - Khushi)
    # =========================================================================
    story.append(Paragraph("Team Technical Contributions", slide_title_style))
    t15_data = [
        ["Member", "SAP ID", "Verifiable Engineering Deliverables"],
        ["Suraj Singh (M1)", "500122962", "Built CoppeliaSim UR5 scene, mapped joint handles, collision masks."],
        ["Sudhanshu Kumar (M2)", "500125146", "Theoretical D-H matrix verification, literature review, IEEE references."],
        ["Abhay Chand Thakur (M3)", "500122020", "Trajectory experiments, 100-trial data acquisition, metrics CSVs."],
        ["Lakshay Dahiya (M4)", "500121078", "Pure-Python D-H engine, DLS solver, ZeroMQ bridge, state machine."],
        ["Khushi (M5)", "500122966", "Pick-and-place testing, edge case validation, 300-DPI publication plots."]
    ]
    t15 = Table(t15_data, colWidths=[150, 90, 470])
    t15.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t15)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 16: Conclusion and Industry Use (Presenter: All Team Members)
    # =========================================================================
    story.append(Paragraph("Conclusion & Industrial Deployment", slide_title_style))
    story.append(Paragraph("• <b>Technical Achievements:</b> Implemented a pure-Python 6-DOF kinematics pipeline achieving 0.0462 mm mean position error across successful IK trials and scripted 10-stage execution.", slide_bullet_style))
    story.append(Paragraph("• <b>Trajectory Formulation:</b> Quintic polynomial trajectory ensures mathematical C^2 continuity, cutting computed jerk metric by 98.1% compared with trapezoidal LSPB.", slide_bullet_style))
    story.append(Paragraph("• <b>Industrial Relevance:</b> Kinematic modeling and smooth trajectory planning methods relevant to assembly and material transfer workflows.", slide_bullet_style))
    story.append(Paragraph("• <b>Future Scope:</b> Add closed-loop vision/force feedback, collision detection, and physical hardware deployment via ROS 2.", slide_bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 17: End Slide (Presenter: All Team Members)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("Thank You / Questions & Answers", ParagraphStyle('EndTitle', fontName='Helvetica-Bold', fontSize=32, leading=38, alignment=TA_CENTER, textColor=colors.HexColor("#0F172A"))))
    story.append(Spacer(1, 10))
    story.append(Paragraph("CSAI4014 Final Project Presentation | Group G04 (Batch B3)", ParagraphStyle('EndSub', fontName='Helvetica', fontSize=20, leading=26, alignment=TA_CENTER, textColor=colors.HexColor("#0284C7"))))
    story.append(Spacer(1, 25))

    contact_info = [
        [Paragraph("<b>GitHub Repository:</b>", col_body_style), Paragraph("github.com/lakshaydahiya/6dof-robotic-arm-pick-and-place", col_body_style)],
        [Paragraph("<b>Video Demonstration:</b>", col_body_style), Paragraph("youtu.be/CSAI4014-G04-UR5-Demo (Unlisted)", col_body_style)],
        [Paragraph("<b>Team Members:</b>", col_body_style), Paragraph("Suraj Singh, Sudhanshu Kumar, Abhay Chand Thakur, Lakshay Dahiya, Khushi", col_body_style)],
        [Paragraph("<b>Academic Institution:</b>", col_body_style), Paragraph("School of Computer Science, UPES, Dehradun", col_body_style)]
    ]
    t_end = Table(contact_info, colWidths=[200, 510])
    t_end.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0"))
    ]))
    story.append(t_end)

    print(f"[Presentation Generator] Compiling clean 17-slide PDF to {filename}...")
    doc.build(story, canvasmaker=SlideDeckCanvas)
    print(f"[Presentation Generator] Presentation PDF successfully compiled! File: {filename}")


if __name__ == "__main__":
    build_presentation()
