import os
from build123d import *

# ============================================================
# RESCUE QUADRUPED — FDM PRINT V3
# Physical-print oriented parametric leg parts.
#
# Output:
#   output_cad/print_ready/*.stl
#   output_cad/cad_master/*.step
#   output_cad/PRINT_SPEC.txt
#
# IMPORTANT:
# These are printable prototypes. Confirm the real servo,
# horn, screw and joint dimensions before final production.
# ============================================================

OUT = "output_cad"
PRINT_OUT = os.path.join(OUT, "print_ready")
CAD_OUT = os.path.join(OUT, "cad_master")
os.makedirs(PRINT_OUT, exist_ok=True)
os.makedirs(CAD_OUT, exist_ok=True)

# ============================================================
# MASTER PARAMETERS — mm
# ============================================================
P = {
    "robot_height": 800.0,

    # Prototype servo envelope. Replace with measured servo.
    "servo_w": 20.0,
    "servo_l": 40.0,
    "servo_h": 40.0,

    # Leg geometry
    "thigh_length": 180.0,
    "shin_length": 200.0,

    # FDM
    "wall": 5.0,
    "clearance": 0.35,
    "min_feature": 2.4,
    "m3_hole": 3.4,
    "m3_insert": 4.3,
    "pivot_hole": 4.2,

    # Foot
    "foot_diameter": 30.0,
    "foot_thickness": 5.0,

    # STL quality
    "stl_tolerance": 0.05,
    "stl_angular_tolerance": 0.1,
}

W = P["servo_w"]
L = P["servo_l"]
H = P["servo_h"]
WALL = P["wall"]
CLR = P["clearance"]
M3_R = P["m3_hole"] / 2
INSERT_R = P["m3_insert"] / 2
PIVOT_R = P["pivot_hole"] / 2


# ============================================================
# EXPORT HELPERS
# ============================================================
def export_print(part, name):
    export_stl(
        part,
        os.path.join(PRINT_OUT, name + ".stl"),
        tolerance=P["stl_tolerance"],
        angular_tolerance=P["stl_angular_tolerance"],
        ascii_format=False,
    )


def export_master(part, name):
    export_step(part, os.path.join(CAD_OUT, name + ".step"))


# ============================================================
# PART 1 — HIP BRACKET
# PRINT ORIENTATION:
#   Large flat base sits directly on build plate.
#   Servo cavity opens upward.
# ============================================================
def hip_bracket():
    outer_w = W + 2 * WALL
    outer_l = L + 2 * WALL
    outer_h = H + WALL

    with BuildPart() as p:
        # Solid shell
        Box(
            outer_w,
            outer_l,
            outer_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Servo pocket: leaves a real bottom for printing
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                W + 2 * CLR,
                L + 2 * CLR,
                H + 0.8,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

            # Cable opening on one side
            with Locations(Pos(0, -(L / 2 + WALL / 2), H * 0.62)):
                Box(
                    W * 0.60,
                    WALL + 2.0,
                    H * 0.55,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

        # Mounting ears
        ear_x = outer_w / 2 + WALL * 1.4
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(ear_x, 0, 0), Pos(-ear_x, 0, 0)):
                Box(
                    WALL * 2.2,
                    20.0,
                    WALL,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        # M3 through holes in ears
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(ear_x, 0, WALL / 2),
                Pos(-ear_x, 0, WALL / 2),
            ):
                Cylinder(radius=M3_R, height=WALL + 2)

        # Optional servo-side insert holes
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(0, (L + WALL) / 2, H - 7),
                Pos(0, -(L + WALL) / 2, H - 7),
            ):
                Cylinder(
                    radius=INSERT_R,
                    height=12,
                    rotation=(90, 0, 0),
                )

    p.part.label = "PRINT_HIP_BRACKET"
    return p.part


# ============================================================
# PART 2 — THIGH LINK
# PRINT ORIENTATION:
#   Broad face is the build-plate face.
#   Structural beam has rounded ends and relief pocket.
# ============================================================
def thigh_link():
    length = P["thigh_length"]
    beam_w = 30.0
    beam_h = 18.0
    end_r = 18.0

    with BuildPart() as p:
        Box(
            beam_w,
            length,
            beam_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Reinforced round ends
        with BuildPart(mode=Mode.ADD):
            with Locations(
                Pos(0, 0, 0),
                Pos(0, length, 0),
            ):
                Cylinder(
                    radius=end_r,
                    height=beam_h,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        # Central weight-relief pocket, open from top.
        # Bottom remains solid for FDM printing.
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                14.0,
                max(50.0, length - 45.0),
                beam_h * 0.55,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Pivot holes
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(0, 0, beam_h / 2),
                Pos(0, length, beam_h / 2),
            ):
                Cylinder(
                    radius=PIVOT_R,
                    height=beam_h + 3,
                )

    p.part.label = "PRINT_THIGH_LINK"
    return p.part


# ============================================================
# PART 3 — KNEE / SHIN
# PRINT ORIENTATION:
#   Shin stands vertically in CAD but export is automatically
#   translated so its flat foot face is at Z=0.
# ============================================================
def knee_shin():
    length = P["shin_length"]

    with BuildPart() as p:
        # Main tapered leg, bottom at Z=0.
        Cone(
            bottom_radius=11.0,
            top_radius=17.0,
            height=length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Reinforced knee housing
        with Locations(Pos(0, 0, length - 28)):
            Box(
                W + 2 * WALL + 2 * CLR,
                38.0,
                38.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Knee pivot bore through housing
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, 0, length - 8)):
                Cylinder(
                    radius=PIVOT_R,
                    height=45,
                    rotation=(0, 90, 0),
                )

        # Flat circular foot pad
        with Locations(Pos(0, 0, -P["foot_thickness"])):
            Cylinder(
                radius=P["foot_diameter"] / 2,
                height=P["foot_thickness"],
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    p.part.label = "PRINT_KNEE_SHIN"
    return p.part


# ============================================================
# BUILD
# ============================================================
print("[PRINT V3] Generating FDM-printable parts...")

hip = hip_bracket()
thigh = thigh_link()
shin = knee_shin()

export_print(hip, "RescueQuadruped_Hip_Bracket_PRINT")
export_print(thigh, "RescueQuadruped_Thigh_Link_PRINT")
export_print(shin, "RescueQuadruped_Knee_Shin_PRINT")

export_master(hip, "RescueQuadruped_Hip_Bracket_MASTER")
export_master(thigh, "RescueQuadruped_Thigh_Link_MASTER")
export_master(shin, "RescueQuadruped_Knee_Shin_MASTER")


# ============================================================
# ASSEMBLY MASTER — NOT FOR DIRECT PRINTING
# ============================================================
assembly = Compound(
    label="RESCUE_QUADRUPED_LEG_ASSEMBLY_MASTER",
    children=[
        hip.moved(Location(Pos(0, -100, 25), (0, 90, 0))),
        thigh.moved(Location(Pos(0, 0, 0), (0, 0, 0))),
        shin.moved(Location(Pos(0, 100, -P["shin_length"]), (0, 35, 0))),
    ],
)
export_master(assembly, "RescueQuadruped_Full_Leg_ASSEMBLY")


# ============================================================
# PRINT SPECIFICATION
# ============================================================
with open(os.path.join(OUT, "PRINT_SPEC.txt"), "w", encoding="utf-8") as f:
    f.write("RESCUE QUADRUPED — FDM PRINT V3\n")
    f.write("=" * 58 + "\n\n")

    f.write("MODEL\n")
    f.write(f"Nominal robot height: {P['robot_height']} mm\n")
    f.write(f"Thigh length: {P['thigh_length']} mm\n")
    f.write(f"Shin length: {P['shin_length']} mm\n\n")

    f.write("SERVO PROTOTYPE ENVELOPE\n")
    f.write(f"Width: {W} mm\n")
    f.write(f"Length: {L} mm\n")
    f.write(f"Height: {H} mm\n\n")

    f.write("FDM FIT\n")
    f.write(f"Wall thickness: {WALL} mm\n")
    f.write(f"General clearance: {CLR} mm\n")
    f.write(f"M3 through hole: {P['m3_hole']} mm\n")
    f.write(f"M3 insert pocket: {P['m3_insert']} mm\n")
    f.write(f"Pivot hole: {P['pivot_hole']} mm\n\n")

    f.write("PRINT FILES — USE THESE FOR SLICER\n")
    f.write("1. RescueQuadruped_Hip_Bracket_PRINT.stl\n")
    f.write("2. RescueQuadruped_Thigh_Link_PRINT.stl\n")
    f.write("3. RescueQuadruped_Knee_Shin_PRINT.stl\n\n")

    f.write("MASTER CAD FILES — DO NOT USE AS SLICER INPUT\n")
    f.write("STEP files are provided for CAD editing/assembly.\n\n")

    f.write("SUGGESTED FIRST PROTOTYPE\n")
    f.write("- Layer height: 0.20 mm\n")
    f.write("- Walls: 4 or more\n")
    f.write("- Infill: 30-50%\n")
    f.write("- Material: PETG or another mechanically suitable FDM material\n")
    f.write("- Print one test part before printing all 4 legs.\n")
    f.write("- Re-measure servo and hardware before final production.\n")

print("[PRINT V3] DONE")
print("[PRINT V3] STL files: output_cad/print_ready/")
print("[PRINT V3] STEP masters: output_cad/cad_master/")
print("[PRINT V3] Specification: output_cad/PRINT_SPEC.txt")
