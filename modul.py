import os
from build123d import *

# ============================================================
# RESCUE QUADRUPED — PRINTABLE LEG CAD V2
# Parametric mechanical model for FDM prototyping.
# All dimensions are millimeters.
#
# IMPORTANT:
# - Verify the actual servo body, horn, screws and inserts before printing.
# - These are prototype dimensions, not a certified load-bearing design.
# - Change values in DESIGN below instead of editing geometry functions.
# ============================================================

os.makedirs("output_cad", exist_ok=True)

# ============================================================
# DESIGN PARAMETERS
# ============================================================
DESIGN = {
    # Robot / leg
    "robot_nominal_height": 800.0,
    "thigh_length": 180.0,
    "shin_length": 200.0,

    # Servo envelope — replace with measured dimensions of the actual servo
    "servo_width": 20.0,
    "servo_length": 40.0,
    "servo_height": 40.0,

    # FDM / mechanical
    "wall": 5.0,
    "clearance": 0.35,
    "m3_hole_d": 3.4,
    "m3_insert_d": 4.3,
    "pivot_d": 4.2,
    "horn_d": 20.0,
    "foot_d": 24.0,

    # Manufacturing
    "stl_tolerance": 0.05,
    "stl_angular_tolerance": 0.1,
}

S = DESIGN
SERVO_W = S["servo_width"]
SERVO_L = S["servo_length"]
SERVO_H = S["servo_height"]
WALL = S["wall"]
CLR = S["clearance"]
M3_R = S["m3_hole_d"] / 2
INSERT_R = S["m3_insert_d"] / 2
PIVOT_R = S["pivot_d"] / 2
HORN_R = S["horn_d"] / 2
FOOT_R = S["foot_d"] / 2


# ============================================================
# HELPERS
# ============================================================
def export_part(part, name):
    export_step(part, f"output_cad/{name}.step")
    export_stl(
        part,
        f"output_cad/{name}.stl",
        tolerance=S["stl_tolerance"],
        angular_tolerance=S["stl_angular_tolerance"],
        ascii_format=False,
    )


# ============================================================
# PART 1 — HIP BRACKET
# Compact servo cradle with mounting ears and cable opening.
# ============================================================
def design_hip_bracket():
    outer_w = SERVO_W + 2 * WALL
    outer_l = SERVO_L + 2 * WALL
    outer_h = SERVO_H + WALL

    with BuildPart() as p:
        Box(
            outer_w,
            outer_l,
            outer_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Servo cavity
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                SERVO_W + 2 * CLR,
                SERVO_L + 2 * CLR,
                SERVO_H + WALL,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

            # Rear cable/service opening
            Box(
                SERVO_W * 0.65,
                WALL + 4.0,
                SERVO_H * 0.55,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Strong mounting ears
        ear_x = (SERVO_W + 2 * WALL) / 2 + WALL * 1.5
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(ear_x, 0, 0), Pos(-ear_x, 0, 0)):
                Box(
                    WALL * 2.0,
                    18.0,
                    WALL,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        # M3 mounting holes
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(ear_x, 0, WALL / 2),
                Pos(-ear_x, 0, WALL / 2),
            ):
                Cylinder(radius=M3_R, height=WALL + 2.0)

    p.part.label = "RESCUE_QUADRUPED_HIP_BRACKET"
    return p.part


# ============================================================
# PART 2 — THIGH LINK
# Lightweight boxed beam with rounded/pivot ends.
# ============================================================
def design_thigh_link():
    length = S["thigh_length"]
    beam_w = 28.0
    beam_h = 18.0
    end_r = 18.0

    with BuildPart() as p:
        # Main structural beam
        Box(
            beam_w,
            length,
            beam_h,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )

        # Rounded reinforcement ends
        with Locations(
            Pos(0, -length / 2, 0),
            Pos(0, length / 2, 0),
        ):
            Cylinder(
                radius=end_r,
                height=beam_h,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )

        # Weight-relief pocket through the central section
        pocket_w = 14.0
        pocket_l = max(40.0, length - 55.0)
        pocket_h = beam_h * 0.55

        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                pocket_w,
                pocket_l,
                pocket_h,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )

        # Pivot holes at both ends
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(0, -length / 2, 0),
                Pos(0, length / 2, 0),
            ):
                Cylinder(
                    radius=PIVOT_R,
                    height=beam_h + 4.0,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

    p.part.label = "RESCUE_QUADRUPED_THIGH_LINK"
    return p.part


# ============================================================
# PART 3 — KNEE / SHIN LINK
# Tapered structural link with reinforced joint and foot end.
# ============================================================
def design_knee_shin():
    length = S["shin_length"]
    top_r = 17.0
    bottom_r = 11.0

    with BuildPart() as p:
        # Tapered structural body
        Cone(
            bottom_radius=bottom_r,
            top_radius=top_r,
            height=length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Reinforced knee block
        with Locations(Pos(0, 0, length - 18.0)):
            Box(
                SERVO_W + 2 * WALL + 2 * CLR,
                36.0,
                36.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Knee pivot bore
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, 0, length - 1.0)):
                Cylinder(
                    radius=PIVOT_R,
                    height=40.0,
                    rotation=(0, 90, 0),
                )

        # Flat mounting foot at ground end
        with Locations(Pos(0, 0, -2.0)):
            Cylinder(
                radius=FOOT_R,
                height=4.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    p.part.label = "RESCUE_QUADRUPED_KNEE_SHIN"
    return p.part


# ============================================================
# GENERATE + EXPORT
# ============================================================
print("[CAD V2] Building parametric rescue-quadruped leg...")

hip = design_hip_bracket()
thigh = design_thigh_link()
knee = design_knee_shin()

export_part(hip, "RescueQuadruped_Part1_Hip_Bracket")
export_part(thigh, "RescueQuadruped_Part2_Thigh_Link")
export_part(knee, "RescueQuadruped_Part3_Knee_Shin")

# Assembly preview only — not a physical fit validation.
assembly = Compound(
    label="RESCUE_QUADRUPED_FULL_LEG_ASSEMBLY",
    children=[
        hip.moved(Location(Pos(0, -95, 25), (0, 90, 0))),
        thigh.moved(Location(Pos(0, 0, 0), (0, 0, 0))),
        knee.moved(Location(Pos(0, 90, -S["shin_length"]), (0, 35, 0))),
    ],
)

export_step(assembly, "output_cad/RescueQuadruped_Full_Leg_Assembly.step")

# Human-readable design specification
with open("output_cad/RescueQuadruped_Print_Spec.txt", "w", encoding="utf-8") as f:
    f.write("RESCUE QUADRUPED — LEG CAD V2\n")
    f.write("=" * 48 + "\n")
    for key, value in DESIGN.items():
        f.write(f"{key}: {value} mm\n" if isinstance(value, (int, float)) else f"{key}: {value}\n")
    f.write("\nFILES\n")
    f.write("- Hip bracket: STEP + STL\n")
    f.write("- Thigh link: STEP + STL\n")
    f.write("- Knee/shin: STEP + STL\n")
    f.write("- Full leg assembly: STEP\n")

print("[CAD V2] Export complete.")
print("[CAD V2] Check output_cad/ before printing.")
