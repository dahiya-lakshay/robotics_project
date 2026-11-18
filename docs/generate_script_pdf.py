"""
Compiles the Member-by-Member Presentation Speaker Script into a polished,
print-ready PDF with running headers, speaker badges, timestamps, and callout blocks.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        page_num = self._pageNumber
        w, h = A4

        self.saveState()
        # Top Header (omitted on page 1)
        if page_num > 1:
            self.setFont("Helvetica-Bold", 8.5)
            self.setFillColor(colors.HexColor("#0284C7"))
            self.drawString(54, h - 36, "CSAI4014: 6-DOF Robotic Arm Pick-and-Place (UR5)")
            self.setFont("Helvetica", 8.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(w - 54, h - 36, "Member-by-Member Speaker Script (20-Minute Rehearsal)")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.6)
            self.line(54, h - 42, w - 54, h - 42)

        # Bottom Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.6)
        self.line(54, 46, w - 54, 46)

        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 32, "Group G04 | Project P02 | Batch B3 — Target Duration: 18:00 - 22:00 mins")
        self.drawRightString(w - 54, 32, f"Page {page_num} of {total_pages}")
        self.restoreState()


def build_script_pdf(output_path="docs/presentation_speaker_script.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    w, h = A4

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12, leading=16, textColor=colors.HexColor("#0284C7"),
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor("#0F172A"),
        spaceBefore=14, spaceAfter=8, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor("#0369A1"),
        spaceBefore=10, spaceAfter=4, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14, textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )
    script_box_style = ParagraphStyle(
        'ScriptBox', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14.5, textColor=colors.HexColor("#0F172A"),
        spaceBefore=2, spaceAfter=4
    )
    speaker_tag_style = ParagraphStyle(
        'SpeakerTag', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=4, spaceAfter=2
    )
    code_style = ParagraphStyle(
        'CodeStyle', parent=styles['Normal'],
        fontName='Courier', fontSize=8.5, leading=11, textColor=colors.HexColor("#0F172A"),
    )

    def make_script_callout(speaker_name, time_str, slide_str, speech_text, bg_color="#F8FAFC", border_color="#CBD5E1"):
        header_p = Paragraph(f"<b>{speaker_name}</b> &nbsp;&nbsp;|&nbsp;&nbsp; <i>{time_str}</i> &nbsp;&nbsp;|&nbsp;&nbsp; <font color='#0284C7'><b>{slide_str}</b></font>", speaker_tag_style)
        speech_p = Paragraph(speech_text, script_box_style)
        tbl_data = [[header_p], [speech_p]]
        tbl = Table(tbl_data, colWidths=[w - 108])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor(border_color)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor(border_color)),
        ]))
        return tbl

    story = []

    # Title & Metadata
    story.append(Paragraph("Presentation Video Recording Script", title_style))
    story.append(Paragraph("Word-for-Word Member Script & Time Budget &nbsp;|&nbsp; 18:00 – 22:00 Minutes Constraint", subtitle_style))
    
    meta_table_data = [
        [Paragraph("<b>Course:</b> CSAI4014 Algorithms for Intelligent Systems and Robotics", body_style),
         Paragraph("<b>Project:</b> P02 (6-DOF Robotic Arm Pick-and-Place)", body_style)],
        [Paragraph("<b>Batch / Group:</b> Batch B3 | Group G04", body_style),
         Paragraph("<b>Robot Manipulator:</b> Universal Robots UR5 (CoppeliaSim)", body_style)],
        [Paragraph("<b>Target Video Duration:</b> 20:00 Minutes (Range: 18:00 - 22:00)", body_style),
         Paragraph("<b>Submission Format:</b> 17-Slide Deck + YouTube Unlisted Video", body_style)]
    ]
    meta_table = Table(meta_table_data, colWidths=[250, 237])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Master Agenda Table
    story.append(Paragraph("Master Presentation Time Budget", h1_style))
    agenda_data = [
        ["Slide", "Topic / Section", "Presenter", "Duration", "Clock Time"],
        ["1", "Title Slide & Introductions", "Suraj Singh (M1) + All", "1m 30s", "00:00 - 01:30"],
        ["2", "Problem Statement & Need", "Suraj Singh (M1)", "1m 15s", "01:30 - 02:45"],
        ["3", "Measurable Objectives", "Suraj Singh (M1)", "1m 15s", "02:45 - 04:00"],
        ["4", "Existing Solutions & Gap", "Sudhanshu Kumar (M2)", "1m 15s", "04:00 - 05:15"],
        ["5", "Novelty (Mandatory)", "Sudhanshu Kumar (M2)", "1m 15s", "05:15 - 06:30"],
        ["6", "Syllabus Mapping", "Sudhanshu Kumar (M2)", "1m 15s", "06:30 - 07:45"],
        ["7", "System Architecture", "Abhay Chand Thakur (M3)", "1m 15s", "07:45 - 09:00"],
        ["8", "Robot & Environment Model", "Abhay Chand Thakur (M3)", "1m 15s", "09:00 - 10:15"],
        ["9", "Algorithm 1: Forward Kinematics", "Abhay Chand Thakur (M3)", "1m 15s", "10:15 - 11:30"],
        ["10", "Algorithm 2: IK Solvers & Trajectory", "Lakshay Dahiya (M4)", "1m 15s", "11:30 - 12:45"],
        ["11", "Simulation Setup & ZeroMQ", "Lakshay Dahiya (M4)", "1m 00s", "12:45 - 13:45"],
        ["12", "Live Simulation Demonstration", "Lakshay Dahiya (M4)", "4m 15s", "13:45 - 18:00"],
        ["13", "Results 1: Kinematic Precision", "Khushi (M5)", "1m 00s", "18:00 - 19:00"],
        ["14", "Results 2: Trajectory & Jerk", "Khushi (M5)", "1m 00s", "19:00 - 20:00"],
        ["15", "Team Technical Contributions", "Khushi (M5)", "1m 00s", "20:00 - 21:00"],
        ["16", "Conclusion & Industry Use", "All Members (M1 - M5)", "0m 45s", "21:00 - 21:45"],
        ["17", "Thank You & Q&A Close", "Lakshay Dahiya (Lead)", "0m 15s", "21:45 - 22:00"]
    ]
    t_agenda = Table(agenda_data, colWidths=[35, 175, 135, 60, 82])
    t_agenda.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (3,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_agenda)
    story.append(Spacer(1, 14))

    # =========================================================================
    # PART 1: SURAJ SINGH (M1)
    # =========================================================================
    story.append(Paragraph("PART 1: MEMBER 1 — SURAJ SINGH (SAP ID: 500122962)", h1_style))
    story.append(Paragraph("<b>Total Allocated Stage Time:</b> 4 minutes 00 seconds (Clock: 00:00 – 04:00)", body_style))

    # Slide 1
    story.append(make_script_callout(
        "Suraj Singh (M1)", "00:00 - 00:30 (30 sec)", "Slide 1: Title Slide & Team Welcome",
        "\"Good day respected faculty and evaluators. Welcome to our final project presentation for course CSAI4014, "
        "Algorithms for Intelligent Systems and Robotics. We are Group G04 representing Batch B3, presenting Project P02 titled: "
        "<b>'6-DOF Robotic Arm Pick-and-Place using D-H Kinematics'</b>, realized on the Universal Robots UR5 manipulator. "
        "I am Suraj Singh, SAP ID 500122962, and my focus was configuring the CoppeliaSim virtual scene, joint handles, and "
        "collision environment. I now invite each of my group members to introduce themselves.\"",
        bg_color="#EFF6FF", border_color="#93C5FD"
    ))
    story.append(Spacer(1, 6))

    # Introductions
    intro_table_data = [
        [Paragraph("<b>Sudhanshu Kumar (00:30 - 00:45):</b> <i>\"Greetings everyone, I am Sudhanshu Kumar, SAP ID 500125146. My primary responsibilities encompassed theoretical Denavit-Hartenberg derivations, literature review, and syllabus mapping.\"</i>", body_style)],
        [Paragraph("<b>Abhay Chand Thakur (00:45 - 01:00):</b> <i>\"Hello respected faculty, I am Abhay Chand Thakur, SAP ID 500122020. I led the trajectory generation experiments, quantitative data acquisition over 100 trials, and comparative analysis.\"</i>", body_style)],
        [Paragraph("<b>Lakshay Dahiya (01:00 - 01:15):</b> <i>\"Good day everyone, I am Lakshay Dahiya, SAP ID 500121078, coordinating Group G04. I engineered the pure-Python D-H kinematics engine, closed-form and DLS inverse kinematics solvers, ZeroMQ Remote API co-simulation bridge, and system integration.\"</i>", body_style)],
        [Paragraph("<b>Khushi (01:15 - 01:30):</b> <i>\"Greetings respected evaluators, I am Khushi, SAP ID 500122966. My core work focused on pick-and-place workspace validation, edge-case testing, error convergence plotting, and academic report compilation.\"</i>", body_style)]
    ]
    t_intros = Table(intro_table_data, colWidths=[w - 108])
    t_intros.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_intros)
    story.append(Spacer(1, 8))

    # Slide 2
    story.append(make_script_callout(
        "Suraj Singh (M1)", "01:30 - 02:45 (1 min 15 sec)", "Slide 2: Problem Statement & Industrial Need",
        "\"Moving to Slide 2, let us examine the fundamental problem and industrial motivation. In modern industrial automation—such as electronics manufacturing, automotive stamping, and pharmaceutical packaging—robotic arms must autonomously pick components from feed stations and transfer them to target positions with sub-millimeter precision.<br/><br/>"
        "The central technical challenge is to achieve this without human manual teaching, without singular configuration lockups, and without collisions. To achieve full spatial manipulation in three dimensions, a robot requires 6 degrees of freedom: 3 translational axes (X, Y, Z) to locate the point in space, and 3 rotational axes (Roll, Pitch, Yaw) to orient the gripper perpendicular to the workpiece surface.<br/><br/>"
        "Furthermore, real industrial manipulators suffer from motion quality issues: abrupt changes in acceleration introduce mechanical jerk, which creates gearbox vibrations, premature motor wear, and dropped payloads. Our project solves this through analytical D-H kinematics coupled with jerk-minimized polynomial trajectory planning.\"",
        bg_color="#EFF6FF", border_color="#93C5FD"
    ))
    story.append(Spacer(1, 8))

    # Slide 3
    story.append(make_script_callout(
        "Suraj Singh (M1)", "02:45 - 04:00 (1 min 15 sec)", "Slide 3: Measurable Project Objectives",
        "\"On Slide 3, we established five concrete, measurable engineering objectives to evaluate our project:<br/>"
        "1. <b>D-H Mathematical Modeling:</b> Establish the standard Denavit-Hartenberg parameter table for the Universal Robots UR5 serial manipulator from link geometry.<br/>"
        "2. <b>Pure-Python Kinematics:</b> Implement independent forward and inverse kinematics engines achieving an end-effector positioning accuracy under 0.1 millimeters.<br/>"
        "3. <b>Jerk-Minimized Trajectories:</b> Implement quintic polynomial trajectories enforcing continuous acceleration and zero jerk at trajectory boundaries.<br/>"
        "4. <b>Synchronous Co-Simulation:</b> Establish a 50 Hz lockstep client-server link with CoppeliaSim using the ZeroMQ Remote API with non-blocking failover.<br/>"
        "5. <b>High Reliability:</b> Achieve a 100% success rate across an automated 10-stage pick-and-place state machine.<br/><br/>"
        "I now hand over the presentation to Sudhanshu Kumar to discuss existing solutions and our novelty.\"",
        bg_color="#EFF6FF", border_color="#93C5FD"
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # PART 2: SUDHANSHU KUMAR (M2)
    # =========================================================================
    story.append(Paragraph("PART 2: MEMBER 2 — SUDHANSHU KUMAR (SAP ID: 500125146)", h1_style))
    story.append(Paragraph("<b>Total Allocated Stage Time:</b> 3 minutes 45 seconds (Clock: 04:00 – 07:45)", body_style))

    # Slide 4
    story.append(make_script_callout(
        "Sudhanshu Kumar (M2)", "04:00 - 05:15 (1 min 15 sec)", "Slide 4: Existing Solutions & Technical Gap",
        "\"Thank you Suraj. Respected faculty, examining Slide 4, classical literature by Denavit, Hartenberg, Craig, and Siciliano establishes matrix transformation conventions for open serial kinematic chains. However, in typical robotics laboratory setups, students rely on CoppeliaSim's built-in Inverse Kinematics plugin. This operates as a black-box, completely concealing the mathematical matrix products, Jacobian inversion, and frame transformations.<br/><br/>"
        "Moreover, traditional industrial robots often default to trapezoidal velocity profiles. As shown in our comparison table, while trapezoidal profiles are easy to compute, their instantaneous steps in acceleration produce severe mechanical jerk.<br/><br/>"
        "Looking at kinematics solvers, purely analytical solvers fail when the wrist is close to singular alignments, whereas purely numerical solvers are computationally slow and sensitive to initial guesses. This gap motivated our hybrid architecture, combining closed-form Pieper geometric decoupling with an adaptive Damped Least Squares solver.\"",
        bg_color="#F0FDF4", border_color="#86EFAC"
    ))
    story.append(Spacer(1, 8))

    # Slide 5
    story.append(make_script_callout(
        "Sudhanshu Kumar (M2)", "05:15 - 06:30 (1 min 15 sec)", "Slide 5: Project Novelty (Mandatory Contributions)",
        "\"Turning to Slide 5, our work introduces four distinct, mandatory engineering contributions:<br/>"
        "1. <b>Independent Pure-Python D-H Engine:</b> All 4x4 homogeneous transformation matrices, the 6x6 geometric Jacobian, and forward/inverse kinematics equations are formulated in Python from first principles, completely external to the simulator.<br/>"
        "2. <b>Hybrid Analytical and DLS Solver:</b> We combine closed-form Pieper spherical wrist decoupling with an adaptive Levenberg-Marquardt Damped Least Squares optimizer. When manipulability drops near singularities, dynamic damping ensures stable convergence without mathematical blowups.<br/>"
        "3. <b>98.1% Mechanical Jerk Reduction:</b> By generating quintic polynomials with C^2 continuity, we reduced the integral jerk cost from 414.7 down to 7.9 compared to standard trapezoidal profiles.<br/>"
        "4. <b>Zero-Downtime Virtual Fallback:</b> We engineered a fast 200 ms TCP pre-probe. If CoppeliaSim is offline, the system seamlessly transitions to our internal physics-consistent virtual simulation engine, ensuring 100% automated test coverage.\"",
        bg_color="#F0FDF4", border_color="#86EFAC"
    ))
    story.append(Spacer(1, 8))

    # Slide 6
    story.append(make_script_callout(
        "Sudhanshu Kumar (M2)", "06:30 - 07:45 (1 min 15 sec)", "Slide 6: CSAI4014 Syllabus Mapping",
        "\"Slide 6 demonstrates the rigorous alignment of our project with the CSAI4014 syllabus across five core theoretical domains:<br/>"
        "• <b>Coordinate Frames & Transformations:</b> Applied via 4x4 homogeneous matrices in our serial kinematic chain module.<br/>"
        "• <b>D-H Representation:</b> Formulated through standard parameters (a, alpha, d, theta) to model the six revolute links of the UR5.<br/>"
        "• <b>Differential Kinematics:</b> Implemented via the 6x6 geometric Jacobian matrix V = J * q_dot to map joint rates to end-effector spatial twist and compute Yoshikawa manipulability.<br/>"
        "• <b>Inverse Kinematics:</b> Realized through Damped Least Squares regularisation with Singularity Robust damping.<br/>"
        "• <b>Trajectory Generation:</b> Applied through quintic polynomial interpolation to satisfy boundary constraints in velocity and acceleration.<br/><br/>"
        "I now invite Abhay Chand Thakur to present our system architecture and robot models.\"",
        bg_color="#F0FDF4", border_color="#86EFAC"
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # PART 3: ABHAY CHAND THAKUR (M3)
    # =========================================================================
    story.append(Paragraph("PART 3: MEMBER 3 — ABHAY CHAND THAKUR (SAP ID: 500122020)", h1_style))
    story.append(Paragraph("<b>Total Allocated Stage Time:</b> 3 minutes 45 seconds (Clock: 07:45 – 11:30)", body_style))

    # Slide 7
    story.append(make_script_callout(
        "Abhay Chand Thakur (M3)", "07:45 - 09:00 (1 min 15 sec)", "Slide 7: System Architecture",
        "\"Thank you Sudhanshu. Respected faculty, Slide 7 presents our overall system architecture block diagram. The software pipeline is structured into clean, decoupled layers:<br/>"
        "• The <b>Mission Planner</b> defines the 3D target coordinates for the pick and place operation.<br/>"
        "• The <b>Trajectory Planner</b> interpolates smooth Cartesian waypoints and joint profiles using quintic polynomials.<br/>"
        "• The <b>Kinematics Engine</b> computes the joint angles theta_1 through theta_6 for every waypoint via our hybrid analytical/DLS solver.<br/>"
        "• The <b>Motion Controller</b> performs safety boundary checks and streams joint commands over the ZeroMQ Remote API Bridge to the CoppeliaSim physics environment at 50 Hz.<br/><br/>"
        "Crucially, our architecture operates under synchronous lockstep control using client.setStepping(True). This means CoppeliaSim's physics engine only advances by 50 milliseconds once our controller has delivered the next waypoint, guaranteeing deterministic reproducibility.\"",
        bg_color="#FEF3C7", border_color="#FCD34D"
    ))
    story.append(Spacer(1, 8))

    # Slide 8
    story.append(make_script_callout(
        "Abhay Chand Thakur (M3)", "09:00 - 10:15 (1 min 15 sec)", "Slide 8: Robot & Environment Model",
        "\"Turning to Slide 8, on the left you see our 3D kinematic frame assignment diagram, and on the right our workstation layout.<br/><br/>"
        "We chose the <b>Universal Robots UR5</b>, an industrial 6-DOF articulated manipulator with an 850 mm reach radius, a 5.0 kg payload capacity, and +/- 0.1 mm repeatability. Its six revolute joints consist of a base yaw, shoulder pitch, elbow pitch, and a three-axis spherical wrist comprising wrist 1, wrist 2, and wrist 3.<br/><br/>"
        "In our simulation scene, the robot stands at world origin (0, 0, 0). The pick target is placed on the workstation table at [0.35, 0.15, 0.05] m, and the destination target is located at [0.10, 0.38, 0.05] m. To prevent collisions with the table and neighbouring fixtures, our controller enforces a pre-pick and pre-place clearance altitude of +12 cm. End-effector grasping is executed by a Robotiq RG2 parallel jaw gripper.\"",
        bg_color="#FEF3C7", border_color="#FCD34D"
    ))
    story.append(Spacer(1, 8))

    # Slide 9
    story.append(make_script_callout(
        "Abhay Chand Thakur (M3)", "10:15 - 11:30 (1 min 15 sec)", "Slide 9: Algorithm 1: Forward Kinematics & D-H",
        "\"Slide 9 details our mathematical formulation for Algorithm 1: Forward Kinematics. Under standard Denavit-Hartenberg convention, the relative homogeneous transformation between frame i-1 and frame i is formulated as: Rot(z, theta_i) * Trans(z, d_i) * Trans(x, a_i) * Rot(x, alpha_i).<br/><br/>"
        "For the UR5, the link lengths and offsets are: link offset d_1 = 89.2 mm, link length a_2 = -425.0 mm, a_3 = -392.3 mm, offset d_4 = 109.2 mm, d_5 = 94.7 mm, and end-effector tool offset d_6 = 82.3 mm.<br/><br/>"
        "The global tool pose is obtained by serial chain multiplication: T_0_6 = T_0_1 * T_1_2 * T_2_3 * T_3_4 * T_4_5 * T_5_6. From this 4x4 matrix, we extract the position vector (p_x, p_y, p_z) and the Roll-Pitch-Yaw orientation Euler angles. We also derive the 6x6 geometric Jacobian relating joint angular velocities to spatial linear and angular velocities: V = J(q) * q_dot.<br/><br/>"
        "I now hand over the presentation to our group coordinator, Lakshay Dahiya, to discuss Algorithm 2, our simulation setup, and lead the live demonstration.\"",
        bg_color="#FEF3C7", border_color="#FCD34D"
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # PART 4: LAKSHAY DAHIYA (M4)
    # =========================================================================
    story.append(Paragraph("PART 4: MEMBER 4 — LAKSHAY DAHIYA (LEAD) (SAP ID: 500121078)", h1_style))
    story.append(Paragraph("<b>Total Allocated Stage Time:</b> 6 minutes 30 seconds (Clock: 11:30 – 18:00)", body_style))

    # Slide 10
    story.append(make_script_callout(
        "Lakshay Dahiya (M4)", "11:30 - 12:45 (1 min 15 sec)", "Slide 10: Algorithm 2: IK Solvers & Trajectory",
        "\"Thank you Abhay. Respected faculty, on Slide 10 we present Algorithm 2: Inverse Kinematics and Trajectory Planning.<br/><br/>"
        "The UR5 features three intersecting wrist axes, allowing us to implement Pieper's analytical decoupling. We first compute the wrist center position, isolating the first three joint angles (theta_1, theta_2, theta_3) algebraically. The remaining spherical wrist joints (theta_4, theta_5, theta_6) are then extracted using Euler angle extraction from the residual rotation matrix R_3_6.<br/><br/>"
        "However, when joint 5 approaches zero, the arm approaches a wrist singularity where the classical Jacobian determinant vanishes. To guarantee robustness, we engineered an adaptive Levenberg-Marquardt Damped Least Squares solver: Delta_q = J^T * (J * J^T + lambda^2 * I)^(-1) * error. The damping parameter lambda dynamically scales based on Yoshikawa's manipulability index w = sqrt(det(J * J^T)). As w approaches zero, lambda smoothly increases, ensuring joint increments remain strictly bounded.<br/><br/>"
        "For trajectory planning, we compute a 5th-order (quintic) polynomial enforcing zero velocity and zero acceleration at both boundaries. This provides C^2 continuity, eliminating instantaneous acceleration steps.\"",
        bg_color="#FAF5FF", border_color="#D8B4FE"
    ))
    story.append(Spacer(1, 8))

    # Slide 11
    story.append(make_script_callout(
        "Lakshay Dahiya (M4)", "12:45 - 13:45 (1 min 00 sec)", "Slide 11: Simulation Setup & ZeroMQ Interface",
        "\"On Slide 11, we detail our simulation platform and co-simulation bridge. We interface Python 3.11 with CoppeliaSim Edu V4.3+ utilizing the ZeroMQ Remote API over TCP port 23000 with CBOR binary serialization.<br/><br/>"
        "To prevent communication latency from destabilizing the controller, we enforce synchronous execution. The Python controller computes the kinematic waypoint, streams joint targets via sim.setJointTargetPosition, commands gripper actuation, and triggers the next simulation tick with sim.step().<br/><br/>"
        "We have packaged our software into standard, reproducible CLI commands: running pytest tests/ -v verifies our 11 unit tests, while python3 -m src.main pick-and-place executes the end-to-end mission.<br/><br/>"
        "We now transition to Slide 12 for our Live Simulation Demonstration.\"",
        bg_color="#FAF5FF", border_color="#D8B4FE"
    ))
    story.append(Spacer(1, 8))

    # Slide 12: Live Demo Box
    story.append(make_script_callout(
        "Lakshay Dahiya (M4)", "13:45 - 18:00 (4 min 15 sec)", "Slide 12: Live Simulation Demonstration (Screen Share)",
        "<i>[Lakshay switches screen share to Terminal + 3D Simulation Window]</i><br/><br/>"
        "\"I am now switching my screen share to our live terminal environment. Respected evaluators, before running the pick-and-place sequence, we first demonstrate the mathematical validity of our engine by running our automated test suite:<br/>"
        "<font face='Courier'><b>python3 -m pytest tests/ -v</b></font><br/>"
        "As seen on screen, all 11 unit tests pass in 0.15 seconds. This verifies transformation orthonormality, forward kinematics accuracy, DLS reachability, and quintic zero-acceleration boundary conditions.<br/><br/>"
        "Next, we inspect our D-H table and forward kinematics at home stance:<br/>"
        "<font face='Courier'><b>python3 -m src.main dh-table</b></font><br/>"
        "<font face='Courier'><b>python3 -m src.main fk --joints 0 -1.5708 1.5708 -1.5708 -1.5708 0</b></font><br/>"
        "The output confirms the exact UR5 D-H parameters and computes the end-effector home coordinates at [0.8172, 0.1915, -0.0055] m with zero position error.<br/><br/>"
        "We now launch our interactive 3D live demonstration visualizer executing the full 10-stage pick-and-place mission:<br/>"
        "<font face='Courier'><b>python3 -m src.live_demo_visualizer --planner quintic</b></font><br/><br/>"
        "<b>(Narrating the live 3D animation on screen):</b><br/>"
        "• <b>Stages 1 & 2:</b> ZeroMQ client handshake complete; arm moves to standard Home stance [0, -90 deg, +90 deg, -90 deg, -90 deg, 0 deg].<br/>"
        "• <b>Stages 3 & 4:</b> Target located at [0.35, 0.15, 0.05] m; arm elevates to pre-pick stance +12 cm above target with tool pointing vertically downward.<br/>"
        "• <b>Stages 5 & 6:</b> Controlled descent along tool z-axis down to z = 0.05 m; Robotiq RG2 gripper closes, locking payload.<br/>"
        "• <b>Stages 7 & 8:</b> Vertical clearance lift and smooth C^2 quintic transfer to destination stance at [0.10, 0.38, 0.17] m with zero overshoot.<br/>"
        "• <b>Stages 9 & 10:</b> Descent to place target, gripper release, clearance ascent, and return to Home. Telemetry confirms zero collisions.<br/><br/>"
        "I now hand the presentation over to Khushi to present our quantitative experimental results and team contributions.\"",
        bg_color="#FAF5FF", border_color="#D8B4FE"
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # PART 5: KHUSHI (M5)
    # =========================================================================
    story.append(Paragraph("PART 5: MEMBER 5 — KHUSHI (SAP ID: 500122966)", h1_style))
    story.append(Paragraph("<b>Total Allocated Stage Time:</b> 3 minutes 00 seconds (Clock: 18:00 – 21:00)", body_style))

    # Slide 13
    story.append(make_script_callout(
        "Khushi (M5)", "18:00 - 19:00 (1 min 00 sec)", "Slide 13: Results 1: Kinematic Precision & Convergence",
        "\"Thank you Lakshay. Respected faculty, on Slide 13 we examine the quantitative precision of our inverse kinematics solver evaluated across 100 randomly sampled reachable workspace configurations:<br/>"
        "• <b>Mean Position Error:</b> Our hybrid DLS solver achieved an average positioning error of just <b>0.0462 millimeters</b> (46.2 micrometers). This is more than 21 times better than the standard 1.0 mm industrial tolerance.<br/>"
        "• <b>Mean Orientation Error:</b> The average tool angular deviation was <b>0.014 milliradians</b> (equivalent to 0.0008 degrees), ensuring near-perfect orthogonal alignment.<br/>"
        "• <b>Computational Efficiency:</b> The average solver execution time was <b>9.67 milliseconds</b> per pose, converging in an average of <b>14.2 iterations</b>, making it suitable for real-time control at 50 Hz.<br/>"
        "• <b>Mission Reliability:</b> In 20 consecutive automated pick-and-place runs, the system achieved a <b>100% success rate</b> with zero dropped payloads and zero singularities.\"",
        bg_color="#FFF1F2", border_color="#FECDD3"
    ))
    story.append(Spacer(1, 8))

    # Slide 14
    story.append(make_script_callout(
        "Khushi (M5)", "19:00 - 20:00 (1 min 00 sec)", "Slide 14: Results 2: Trajectory Benchmark & Jerk Cost",
        "\"On Slide 14, we present our comparative benchmark across three trajectory planning profiles: Trapezoidal LSPB, Cubic Polynomial, and Quintic Polynomial.<br/><br/>"
        "While Trapezoidal LSPB achieved the fastest transit time of 1.53 seconds, its discontinuous acceleration steps generated an extreme jerk metric of <b>414.74</b>. In physical hardware, this level of jerk causes severe mechanical resonance and gearbox chatter.<br/><br/>"
        "The Cubic polynomial improves continuity but retains non-zero acceleration at the endpoints.<br/><br/>"
        "Our implemented <b>Quintic polynomial</b> enforces zero acceleration and zero velocity at both endpoints (C^2 continuity), yielding a jerk cost of just <b>7.91</b>. This represents a <b>98.1% reduction in mechanical jerk</b> compared to trapezoidal motion, proving that the Quintic profile is optimal for preserving robotic hardware longevity.\"",
        bg_color="#FFF1F2", border_color="#FECDD3"
    ))
    story.append(Spacer(1, 8))

    # Slide 15
    story.append(make_script_callout(
        "Khushi (M5)", "20:00 - 21:00 (1 min 00 sec)", "Slide 15: Team Technical Contributions",
        "\"Slide 15 records our verifiable individual contributions across the project lifecycle:<br/>"
        "• <b>Suraj Singh (M1):</b> Configured the CoppeliaSim virtual scene, mapped revolute joint handles, RG2 gripper signals, and proximity sensor collision masks.<br/>"
        "• <b>Sudhanshu Kumar (M2):</b> Led theoretical D-H matrix verification, mathematical literature review, and IEEE reference compilation.<br/>"
        "• <b>Abhay Chand Thakur (M3):</b> Conducted trajectory benchmarking, 100-trial experimental data logging, and comparative metric CSV generation.<br/>"
        "• <b>Lakshay Dahiya (M4):</b> Engineered the pure-Python D-H kinematics engine, hybrid Pieper/DLS solvers, 50 Hz ZeroMQ bridge, and the 10-stage state machine.<br/>"
        "• <b>Khushi (M5):</b> Designed pick-and-place boundary test cases, error tolerance analysis, generated 300-DPI publication plots, and formatted the academic report.<br/><br/>"
        "We now bring our presentation to a close with Slide 16 and 17.\"",
        bg_color="#FFF1F2", border_color="#FECDD3"
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # PART 6: ALL TEAM MEMBERS — CONCLUSION & CLOSE
    # =========================================================================
    story.append(Paragraph("PART 6: ALL TEAM MEMBERS — CONCLUSION & Q&A CLOSE", h1_style))
    story.append(Paragraph("<b>Total Allocated Stage Time:</b> 1 minute 00 seconds (Clock: 21:00 – 22:00)", body_style))

    # Slide 16
    closing_table_data = [
        [Paragraph("<b>Suraj Singh (21:00 - 21:11):</b> <i>\"In conclusion, we successfully demonstrated a fully integrated, pure-Python 6-DOF robotic arm manipulation system achieving sub-50 micrometer accuracy and 100% pick-and-place reliability.\"</i>", body_style)],
        [Paragraph("<b>Sudhanshu Kumar (21:11 - 21:22):</b> <i>\"Our hybrid D-H and DLS kinematics solver successfully eliminates singular divergence, proving that complex robotics algorithms can be realized transparently without simulator black boxes.\"</i>", body_style)],
        [Paragraph("<b>Abhay Chand Thakur (21:22 - 21:33):</b> <i>\"Our trajectory analysis validated that quintic polynomials eliminate mechanical jerk spikes by 98.1%, providing a mathematically proven trajectory strategy for industrial manipulators.\"</i>", body_style)],
        [Paragraph("<b>Khushi (21:33 - 21:45):</b> <i>\"This architecture translates directly to industrial applications, including semiconductor wafer handling, electronics sorting, and automated pharmaceutical packaging.\"</i>", body_style)],
        [Paragraph("<b>Lakshay Dahiya (Lead) (21:45 - 22:00):</b> <i>\"On Slide 17, our complete open-source codebase, test suite, and 26-page academic report are available on GitHub. On behalf of Group G04, we express our sincere gratitude to our course faculty for their guidance throughout CSAI4014. We now conclude our 20-minute presentation and welcome questions from the evaluators. Thank you.\"</i>", body_style)]
    ]
    t_close = Table(closing_table_data, colWidths=[w - 108])
    t_close.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#0F172A")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_close)

    print(f"[Script PDF Generator] Compiling script to {output_path}...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[Script PDF Generator] PDF successfully generated! File: {output_path}")


if __name__ == "__main__":
    build_script_pdf()
