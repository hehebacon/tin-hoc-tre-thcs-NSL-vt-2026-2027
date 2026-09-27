import os
import math
from build123d import *

# ============================================================
# RESCUE QUADRUPED — FDM PRINT V4
# DRAGON-BACK / DRAGON-TAIL BODY DESIGN
#
# V4 adds:
#   - sculpted central body
#   - dragon-style rear tail
#   - separate printable tail modules
#   - head with drilled eye openings
#   - cleaner tapered leg links with structural ribs
#   - complete body/leg master assembly
#
# IMPORTANT:
# This is a printable prototype. Measure the real servo,
# horn, screw and electronics before final production.
# ============================================================

OUT = "output_cad"
PRINT_OUT = os.path.join(OUT, "print_ready")
CAD_OUT = os.path.join(OUT, "cad_master")
os.makedirs(PRINT_OUT, exist_ok=True)
os.makedirs(CAD_OUT, exist_ok=True)

P = {
    "robot_height": 800.0,

    # Prototype servo envelope.
    "servo_w": 20.0,
    "servo_l": 40.0,
    "servo_h": 40.0,

    # Leg geometry.
    "thigh_length": 180.0,
    "shin_length": 200.0,

    # FDM.
    "wall": 5.0,
    "clearance": 0.35,
    "m3_hole": 3.4,
    "m3_insert": 4.3,
    "pivot_hole": 4.2,

    # Foot.
    "foot_diameter": 30.0,
    "foot_thickness": 5.0,

    # Body.
    "body_length": 250.0,
    "body_width": 145.0,
    "body_height": 72.0,
    "body_wall": 5.0,

    # Dragon head.
    "head_length": 72.0,
    "head_width": 82.0,
    "head_height": 55.0,
    "eye_hole": 8.0,

    # Tail.
    "tail_modules": 6,
    "tail_base_radius": 18.0,
    "tail_tip_radius": 5.0,
    "tail_module_length": 38.0,

    # STL quality.
    "stl_tolerance": 0.05,
    "stl_angular_tolerance": 0.1,
}

W = P["servo_w"]
L = P["servo_l"]
H = P["servo_h"]
WALL = P["wall"]
CLR = P["clearance"]
M3_R = P["m3_hole"] / 2
PIVOT_R = P["pivot_hole"] / 2


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
# HIP — smoother dragon/mechanical housing
# ============================================================
def hip_bracket():
    outer_w = W + 2 * WALL
    outer_l = L + 2 * WALL
    outer_h = H + WALL

    with BuildPart() as p:
        Box(
            outer_w, outer_l, outer_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                W + 2 * CLR,
                L + 2 * CLR,
                H + 0.8,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

            with Locations(Pos(0, -(L / 2 + WALL / 2), H * 0.62)):
                Box(
                    W * 0.60,
                    WALL + 2.0,
                    H * 0.55,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

        # Rounded shoulder ears.
        ear_x = outer_w / 2 + WALL * 1.2
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(ear_x, 0, 0), Pos(-ear_x, 0, 0)):
                Cylinder(
                    radius=10.0,
                    height=WALL,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(ear_x, 0, WALL / 2),
                Pos(-ear_x, 0, WALL / 2),
            ):
                Cylinder(radius=M3_R, height=WALL + 2)

    p.part.label = "DRAGON_HIP_BRACKET_PRINT"
    return p.part


# ============================================================
# THIGH — tapered dragon scale silhouette + ribs
# ============================================================
def thigh_link():
    length = P["thigh_length"]
    beam_w = 30.0
    beam_h = 18.0

    with BuildPart() as p:
        Box(
            beam_w,
            length,
            beam_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Rounded joint bosses.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, 0, 0), Pos(0, length, 0)):
                Cylinder(
                    radius=18.0,
                    height=beam_h,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        # Narrow top relief for weight saving.
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                14.0,
                max(50.0, length - 50.0),
                beam_h * 0.50,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Raised longitudinal dragon ribs.
        rib_y = [length * 0.25, length * 0.50, length * 0.75]
        with BuildPart(mode=Mode.ADD):
            for y in rib_y:
                with Locations(Pos(0, y, beam_h)):
                    Box(
                        38.0,
                        5.0,
                        3.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )

        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(0, 0, beam_h / 2),
                Pos(0, length, beam_h / 2),
            ):
                Cylinder(radius=PIVOT_R, height=beam_h + 3)

    p.part.label = "DRAGON_THIGH_LINK_PRINT"
    return p.part


# ============================================================
# SHIN — tapered mechanical dragon leg
# ============================================================
def knee_shin():
    length = P["shin_length"]

    with BuildPart() as p:
        Cone(
            bottom_radius=11.0,
            top_radius=17.0,
            height=length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Structural side ribs.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, 0, length * 0.35)):
                Box(
                    5.0, 34.0, length * 0.45,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        # Knee housing.
        with Locations(Pos(0, 0, length - 28)):
            Box(
                W + 2 * WALL + 2 * CLR,
                38.0,
                38.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, 0, length - 8)):
                Cylinder(
                    radius=PIVOT_R,
                    height=45,
                    rotation=(0, 90, 0),
                )

        with Locations(Pos(0, 0, -P["foot_thickness"])):
            Cylinder(
                radius=P["foot_diameter"] / 2,
                height=P["foot_thickness"],
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    p.part.label = "DRAGON_KNEE_SHIN_PRINT"
    return p.part


# ============================================================
# BODY — central armored dragon torso
#
# Coordinate convention:
#   X = left/right
#   Y = front/back
#   Z = up
#   Front = -Y
#   Tail = +Y
# ============================================================
def body_shell():
    bl = P["body_length"]
    bw = P["body_width"]
    bh = P["body_height"]

    with BuildPart() as p:
        # Main low-profile torso.
        Box(
            bw, bl, bh,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Rounded armor shoulders/front and rear.
        with BuildPart(mode=Mode.ADD):
            with Locations(
                Pos(0, -bl * 0.43, bh * 0.45),
                Pos(0, bl * 0.43, bh * 0.45),
            ):
                Sphere(radius=bw * 0.43)

        # Electronics cavity from the underside.
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                bw - 2 * P["body_wall"],
                bl - 42.0,
                bh * 0.55,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Four servo mounting towers.
        tower_x = bw * 0.34
        tower_y = bl * 0.28
        with BuildPart(mode=Mode.ADD):
            for x in (-tower_x, tower_x):
                for y in (-tower_y, tower_y):
                    with Locations(Pos(x, y, bh)):
                        Cylinder(
                            radius=13.0,
                            height=10.0,
                            align=(Align.CENTER, Align.CENTER, Align.MIN),
                        )

        # M3 holes through mounting towers.
        with BuildPart(mode=Mode.SUBTRACT):
            for x in (-tower_x, tower_x):
                for y in (-tower_y, tower_y):
                    with Locations(Pos(x, y, bh + 5)):
                        Cylinder(radius=M3_R, height=14.0)

        # Dragon spine armor — repeated low fins.
        fin_count = 5
        for i in range(fin_count):
            y = -bl * 0.30 + i * (bl * 0.15)
            fin_h = 9.0 if i in (0, fin_count - 1) else 13.0
            with BuildPart(mode=Mode.ADD):
                with Locations(Pos(0, y, bh)):
                    Cone(
                        bottom_radius=14.0,
                        top_radius=3.0,
                        height=fin_h,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )

    p.part.label = "DRAGON_BODY_SHELL_PRINT"
    return p.part


# ============================================================
# HEAD — compact dragon head with two drilled eye holes
# ============================================================
def dragon_head():
    with BuildPart() as p:
        # Main head block + snout.
        Box(
            P["head_width"],
            P["head_length"],
            P["head_height"],
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, -P["head_length"] * 0.48, 8)):
                Box(
                    P["head_width"] * 0.72,
                    30.0,
                    P["head_height"] * 0.62,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        # Eye sockets: actual through-holes, suitable for LED/camera
        # inserts or simply leaving as open printed holes.
        eye_x = P["head_width"] * 0.31
        eye_y = -P["head_length"] * 0.20
        eye_z = P["head_height"] * 0.67

        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(-eye_x, eye_y, eye_z),
                Pos(eye_x, eye_y, eye_z),
            ):
                Cylinder(
                    radius=P["eye_hole"] / 2,
                    height=30.0,
                    rotation=(1, 0, 0),
                )

        # Small nostril holes.
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(
                Pos(-10.0, -P["head_length"] * 0.49, 26.0),
                Pos(10.0, -P["head_length"] * 0.49, 26.0),
            ):
                Cylinder(
                    radius=2.5,
                    height=12.0,
                    rotation=(1, 0, 0),
                )

        # Brow horns/fins.
        with BuildPart(mode=Mode.ADD):
            with Locations(
                Pos(-eye_x, 0, P["head_height"]),
                Pos(eye_x, 0, P["head_height"]),
            ):
                Cone(
                    bottom_radius=7.0,
                    top_radius=1.5,
                    height=18.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    p.part.label = "DRAGON_HEAD_EYE_HOLES_PRINT"
    return p.part


# ============================================================
# TAIL MODULE — dragon-like articulated rear tail
#
# Each module is printed separately and can be assembled as:
# BODY -> TAIL 01 -> 02 -> 03 -> 04 -> 05 -> TIP
# The modules progressively taper and curve upward.
# ============================================================
def dragon_tail_module(index):
    count = P["tail_modules"]
    t = index / max(1, count - 1)

    radius = (
        P["tail_base_radius"] * (1.0 - t)
        + P["tail_tip_radius"] * t
    )
    length = P["tail_module_length"]

    # Gentle upward curve toward the tail tip.
    angle_deg = -12.0 + index * 7.0

    with BuildPart() as p:
        Cone(
            bottom_radius=radius,
            top_radius=max(3.0, radius - 4.0),
            height=length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Connector collar at base.
        with Locations(Pos(0, 0, 0)):
            Cylinder(
                radius=radius + 3.0,
                height=6.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Central M4-ish assembly bore.
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=2.2,
                height=length + 3.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Dragon spine spike.
        with Locations(Pos(0, length * 0.52, radius * 0.55)):
            Cone(
                bottom_radius=max(3.0, radius * 0.38),
                top_radius=0.8,
                height=12.0 + 7.0 * (1.0 - t),
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    part = p.part
    part.label = f"DRAGON_TAIL_MODULE_{index + 1:02d}"

    # Rotate each module to create the curved silhouette.
    return part.rotate(Axis.X, angle_deg)


def dragon_tail_tip():
    with BuildPart() as p:
        Cone(
            bottom_radius=7.0,
            top_radius=0.5,
            height=42.0,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        with Locations(Pos(0, 17.0, 7.0)):
            Cone(
                bottom_radius=5.0,
                top_radius=0.2,
                height=22.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    p.part.label = "DRAGON_TAIL_TIP_PRINT"
    return p.part


# ============================================================
# BUILD / EXPORT
# ============================================================
print("[PRINT V4] Generating dragon-style FDM modules...")

hip = hip_bracket()
thigh = thigh_link()
shin = knee_shin()
body = body_shell()
head = dragon_head()

tail_parts = []
for i in range(P["tail_modules"]):
    part = dragon_tail_module(i)
    tail_parts.append(part)
    export_print(part, f"RescueQuadruped_Dragon_Tail_{i + 1:02d}_PRINT")
    export_master(part, f"RescueQuadruped_Dragon_Tail_{i + 1:02d}_MASTER")

tail_tip = dragon_tail_tip()
export_print(tail_tip, "RescueQuadruped_Dragon_Tail_Tip_PRINT")
export_master(tail_tip, "RescueQuadruped_Dragon_Tail_Tip_MASTER")

export_print(hip, "RescueQuadruped_Dragon_Hip_Bracket_PRINT")
export_print(thigh, "RescueQuadruped_Dragon_Thigh_Link_PRINT")
export_print(shin, "RescueQuadruped_Dragon_Knee_Shin_PRINT")
export_print(body, "RescueQuadruped_Dragon_Body_PRINT")
export_print(head, "RescueQuadruped_Dragon_Head_EyeHoles_PRINT")

export_master(hip, "RescueQuadruped_Dragon_Hip_Bracket_MASTER")
export_master(thigh, "RescueQuadruped_Dragon_Thigh_Link_MASTER")
export_master(shin, "RescueQuadruped_Dragon_Knee_Shin_MASTER")
export_master(body, "RescueQuadruped_Dragon_Body_MASTER")
export_master(head, "RescueQuadruped_Dragon_Head_EyeHoles_MASTER")


# ============================================================
# FULL LEG + BODY MASTER
# ============================================================
assembly_children = [
    body,
    head.moved(Location(Pos(0, -P["body_length"] * 0.55, 42))),
]

# Tail is intentionally separate modules but shown in one master assembly.
tail_y = P["body_length"] * 0.48
for i, part in enumerate(tail_parts):
    assembly_children.append(
        part.moved(Location(Pos(0, tail_y + i * P["tail_module_length"], 35)))
    )

assembly_children.append(
    tail_tip.moved(
        Location(
            Pos(
                0,
                tail_y + len(tail_parts) * P["tail_module_length"],
                42,
            )
        )
    )
)

# Four leg brackets are mirrored by placement.
for x in (-P["body_width"] * 0.40, P["body_width"] * 0.40):
    for y in (-P["body_length"] * 0.30, P["body_length"] * 0.30):
        assembly_children.append(
            hip.moved(Location(Pos(x, y, -P["servo_h"] * 0.70)))
        )

assembly = Compound(
    label="RESCUE_QUADRUPED_DRAGON_BODY_ASSEMBLY_MASTER",
    children=assembly_children,
)
export_master(assembly, "RescueQuadruped_Dragon_Full_Body_ASSEMBLY")


# ============================================================
# PRINT SPEC
# ============================================================
with open(os.path.join(OUT, "PRINT_SPEC.txt"), "w", encoding="utf-8") as f:
    f.write("RESCUE QUADRUPED — FDM PRINT V4 / DRAGON BODY\n")
    f.write("=" * 62 + "\n\n")

    f.write("DESIGN\n")
    f.write("- Dragon-style central body with armored spine\n")
    f.write("- Rear articulated tapering dragon tail\n")
    f.write("- Separate tail modules for easier printing/replacement\n")
    f.write("- Dragon head with drilled eye openings\n")
    f.write("- Tapered leg links with structural ribs\n\n")

    f.write("MODEL\n")
    f.write(f"Nominal robot height: {P['robot_height']} mm\n")
    f.write(f"Body: {P['body_width']} x {P['body_length']} x {P['body_height']} mm\n")
    f.write(f"Thigh: {P['thigh_length']} mm\n")
    f.write(f"Shin: {P['shin_length']} mm\n")
    f.write(f"Tail modules: {P['tail_modules']} + tip\n")
    f.write(f"Eye hole diameter: {P['eye_hole']} mm\n\n")

    f.write("PRINT FILES\n")
    f.write("- Dragon body\n")
    f.write("- Dragon head with eye holes\n")
    f.write("- Dragon hip brackets\n")
    f.write("- Dragon thigh links\n")
    f.write("- Dragon knee/shin links\n")
    f.write("- Tail modules 01-06\n")
    f.write("- Tail tip\n\n")

    f.write("FDM STARTING PROFILE\n")
    f.write("- Layer height: 0.20 mm\n")
    f.write("- Walls: 4+\n")
    f.write("- Infill: 30-50% for structural prototypes\n")
    f.write("- PETG or another mechanically suitable material\n")
    f.write("- Print one body/leg/tail test before full production\n")
    f.write("- Verify real servo and fastener dimensions before final print\n")

print("[PRINT V4] DONE")
print("[PRINT V4] STL: output_cad/print_ready/")
print("[PRINT V4] STEP: output_cad/cad_master/")
print("[PRINT V4] SPEC: output_cad/PRINT_SPEC.txt")
