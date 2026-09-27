import os
import math
from build123d import *

# ============================================================
# RESCUE QUADRUPED — FDM PRINT V5
# FULL DRAGON SHELL / HIDDEN-FASTENER MECHANICAL DESIGN
#
# V5 focus:
#   - continuous dragon silhouette from head -> torso -> tail
#   - layered armor instead of box-like exposed mechanics
#   - recessed/counterbored fasteners and service-side mounting
#   - articulated tail with real connector sockets
#   - leg shells/bosses shaped as dragon limbs
#   - printable parts remain separate for maintenance
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
    "design_version": "V5_DRAGON_SHELL_HIDDEN_FASTENER",

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
    "fastener_head": 6.2,
    "fastener_depth": 3.2,
    "armor_t": 4.0,

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
    """Dragon shoulder/hip housing with recessed service-side fasteners."""
    outer_w = W + 2 * WALL + 4
    outer_l = L + 2 * WALL + 4
    outer_h = H + WALL

    with BuildPart() as p:
        Box(outer_w, outer_l, outer_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Servo cavity: the servo is captured inside the shell.
        with BuildPart(mode=Mode.SUBTRACT):
            Box(W + 2 * CLR, L + 2 * CLR, H + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Dragon shoulder armor, integrated into the housing.
        with BuildPart(mode=Mode.ADD):
            with Locations(
                Pos(-outer_w * 0.50, -outer_l * 0.15, outer_h * 0.55),
                Pos( outer_w * 0.50, -outer_l * 0.15, outer_h * 0.55),
            ):
                Sphere(radius=12.0)

        # Recessed mounting channels. Fastener heads sit below the skin.
        for x in (-outer_w * 0.30, outer_w * 0.30):
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations(Pos(x, outer_l * 0.18, outer_h - 2.0)):
                    Cylinder(radius=M3_R, height=outer_h + 4)
                with Locations(Pos(x, outer_l * 0.18, outer_h - P["fastener_depth"] / 2)):
                    Cylinder(radius=P["fastener_head"] / 2,
                             height=P["fastener_depth"] + 0.4)

        # Hidden-side pivot boss; screw access is from the inner face.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, 0, outer_h * 0.50)):
                Cylinder(radius=16.0, height=outer_w * 0.70,
                         rotation=(0, 90, 0))

        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, 0, outer_h * 0.50)):
                Cylinder(radius=PIVOT_R, height=outer_w + 6,
                         rotation=(0, 90, 0))

    p.part.label = "DRAGON_HIP_HIDDEN_FASTENER_PRINT"
    return p.part

def thigh_link():
    """Armored thigh beam with recessed fastener pockets."""
    length = P["thigh_length"]
    beam_w = 34.0
    beam_h = 22.0

    with BuildPart() as p:
        # Tapered-looking structural core.
        Box(beam_w, length, beam_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Large joint bosses blend into the beam.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, 0, beam_h / 2), Pos(0, length, beam_h / 2)):
                Cylinder(radius=19.0, height=beam_h,
                         rotation=(0, 90, 0))

        # Dragon armor spine on the outer face.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, length * 0.50, beam_h)):
                Cone(bottom_radius=13.0, top_radius=4.0, height=8.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Three recessed armor ribs.
        for y in (length * 0.25, length * 0.50, length * 0.75):
            with BuildPart(mode=Mode.ADD):
                with Locations(Pos(0, y, beam_h)):
                    Box(40.0, 6.0, 3.5,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Pivot holes run through the joint bosses.
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, 0, beam_h / 2), Pos(0, length, beam_h / 2)):
                Cylinder(radius=PIVOT_R, height=beam_w + 8,
                         rotation=(0, 90, 0))

        # Counterbores keep screw heads flush instead of sticking outside.
        with BuildPart(mode=Mode.SUBTRACT):
            for y in (12.0, length - 12.0):
                with Locations(Pos(0, y, beam_h - 1.4)):
                    Cylinder(radius=P["fastener_head"] / 2,
                             height=P["fastener_depth"])

    p.part.label = "DRAGON_ARMORED_THIGH_PRINT"
    return p.part

def knee_shin():
    """Tapered dragon shin with enclosed foot/pivot geometry."""
    length = P["shin_length"]

    with BuildPart() as p:
        Cone(bottom_radius=12.0, top_radius=19.0, height=length,
             align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Outer armor blade follows the leg instead of looking like a box.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, 0, length * 0.20)):
                Box(5.0, 30.0, length * 0.55,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Knee collar.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, 0, length - 25.0)):
                Cylinder(radius=22.0, height=28.0,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Cross pivot is mechanically enclosed.
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, 0, length - 11.0)):
                Cylinder(radius=PIVOT_R, height=48.0,
                         rotation=(0, 90, 0))

        # Foot pad.
        with Locations(Pos(0, 0, -P["foot_thickness"])):
            Cylinder(radius=P["foot_diameter"] / 2,
                     height=P["foot_thickness"],
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    p.part.label = "DRAGON_ARMORED_SHIN_PRINT"
    return p.part

def body_shell():
    """Main dragon torso: curved silhouette, armor plates, hidden service fasteners."""
    bl = P["body_length"]
    bw = P["body_width"]
    bh = P["body_height"]

    with BuildPart() as p:
        # Core torso.
        Box(bw, bl, bh, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Rounded front/rear shoulders make the body read as one creature.
        with BuildPart(mode=Mode.ADD):
            with Locations(
                Pos(0, -bl * 0.42, bh * 0.48),
                Pos(0,  bl * 0.40, bh * 0.48),
            ):
                Sphere(radius=bw * 0.42)

        # Underside electronics/service cavity.
        with BuildPart(mode=Mode.SUBTRACT):
            Box(bw - 2 * P["body_wall"], bl - 46.0, bh * 0.48,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Continuous dragon shoulder armor.
        for x in (-bw * 0.36, bw * 0.36):
            with BuildPart(mode=Mode.ADD):
                with Locations(Pos(x, -bl * 0.30, bh)):
                    Sphere(radius=22.0)

        # Top armor spine: large central ridge + smaller scales.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, -bl * 0.05, bh)):
                Box(34.0, bl * 0.64, P["armor_t"] + 8.0),
            with Locations(
                Pos(0, -bl * 0.30, bh + 7),
                Pos(0, -bl * 0.10, bh + 9),
                Pos(0,  bl * 0.10, bh + 9),
                Pos(0,  bl * 0.30, bh + 7),
            ):
                Cone(bottom_radius=13.0, top_radius=2.5, height=13.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Four internal servo towers. Mounting screws enter from the service side.
        tower_x = bw * 0.34
        tower_y = bl * 0.28
        with BuildPart(mode=Mode.ADD):
            for x in (-tower_x, tower_x):
                for y in (-tower_y, tower_y):
                    with Locations(Pos(x, y, bh - 2)):
                        Cylinder(radius=14.0, height=10.0,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Through bores with recessed screw heads. No proud screw heads on the skin.
        with BuildPart(mode=Mode.SUBTRACT):
            for x in (-tower_x, tower_x):
                for y in (-tower_y, tower_y):
                    with Locations(Pos(x, y, bh - 1)):
                        Cylinder(radius=M3_R, height=15.0)
                    with Locations(Pos(x, y, bh - 3.0)):
                        Cylinder(radius=P["fastener_head"] / 2,
                                 height=P["fastener_depth"] + 0.5)

        # Rear tail socket is integrated into the body.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, bl * 0.52, bh * 0.42)):
                Cylinder(radius=22.0, height=24.0,
                         rotation=(90, 0, 0))

        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, bl * 0.52, bh * 0.42)):
                Cylinder(radius=12.0, height=34.0,
                         rotation=(90, 0, 0))

    p.part.label = "DRAGON_FULL_ARMOR_BODY_PRINT"
    return p.part

def dragon_head():
    """More creature-like head with recessed eyes, nostrils and brow armor."""
    with BuildPart() as p:
        # Main skull and tapered snout.
        Box(P["head_width"], P["head_length"], P["head_height"],
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, -P["head_length"] * 0.48, 8)):
                Cone(bottom_radius=P["head_width"] * 0.43,
                     top_radius=P["head_width"] * 0.30,
                     height=30.0,
                     rotation=(90, 0, 0),
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

        eye_x = P["head_width"] * 0.31
        eye_y = -P["head_length"] * 0.18
        eye_z = P["head_height"] * 0.68

        # Eye pockets are recessed: LED/camera lens sits inside the head.
        with BuildPart(mode=Mode.SUBTRACT):
            for x in (-eye_x, eye_x):
                with Locations(Pos(x, eye_y, eye_z)):
                    Cylinder(radius=7.0, height=10.0, rotation=(1, 0, 0))
                    with Locations(Pos(0, 3.0, 0)):
                        Cylinder(radius=P["eye_hole"] / 2, height=26.0,
                                 rotation=(1, 0, 0))

        # Small nostrils.
        with BuildPart(mode=Mode.SUBTRACT):
            for x in (-10.0, 10.0):
                with Locations(Pos(x, -P["head_length"] * 0.49, 25.0)):
                    Cylinder(radius=2.5, height=12.0, rotation=(1, 0, 0))

        # Brow armor and horns.
        with BuildPart(mode=Mode.ADD):
            for x in (-eye_x, eye_x):
                with Locations(Pos(x, -4.0, P["head_height"])):
                    Cone(bottom_radius=8.0, top_radius=1.0, height=22.0,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Lower jaw plate.
        with BuildPart(mode=Mode.ADD):
            with Locations(Pos(0, -P["head_length"] * 0.42, 5.0)):
                Box(P["head_width"] * 0.58, 28.0, 8.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

    p.part.label = "DRAGON_HEAD_RECESSED_EYES_PRINT"
    return p.part

def dragon_tail_module(index):
    """Articulated tail segment with socket + hidden cross-pin."""
    count = P["tail_modules"]
    t = index / max(1, count - 1)
    r1 = P["tail_base_radius"] * (1.0 - t) + P["tail_tip_radius"] * t
    r2 = max(3.0, r1 - 4.5)
    length = P["tail_module_length"]

    with BuildPart() as p:
        # Rounded/tapered segment.
        Cone(bottom_radius=r1, top_radius=r2, height=length,
             align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Base collar and forward socket.
        with BuildPart(mode=Mode.ADD):
            Cylinder(radius=r1 + 3.0, height=7.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations(Pos(0, 0, length - 7.0)):
                Cylinder(radius=r2 + 2.5, height=7.0,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Female axial socket at the base, male-style reduced nose at the tip.
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(radius=max(5.0, r1 * 0.52), height=11.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Hidden cross-pin bore, kept inside the collar silhouette.
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, 0, 5.0)):
                Cylinder(radius=2.2, height=(r1 + 8.0) * 2,
                         rotation=(0, 90, 0))

        # Dorsal scale/spike.
        with Locations(Pos(0, length * 0.52, r1 * 0.55)):
            Cone(bottom_radius=max(3.0, r1 * 0.40), top_radius=0.8,
                 height=14.0 + 6.0 * (1.0 - t),
                 align=(Align.CENTER, Align.CENTER, Align.MIN))

    part = p.part
    part.label = f"DRAGON_TAIL_ARMORED_{index + 1:02d}"
    return part.rotate(Axis.X, -10.0 + index * 6.0)

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
print("[PRINT V5] Generating full dragon shell + hidden-fastener FDM modules...")

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
    f.write("RESCUE QUADRUPED — FDM PRINT V5 / FULL DRAGON SHELL\n")
    f.write("=" * 62 + "\n\n")

    f.write("DESIGN\n")
    f.write("- Continuous dragon silhouette with armored torso\n")
    f.write("- Recessed/counterbored fasteners; service-side access\n")
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

print("[PRINT V5] DONE")
print("[PRINT V5] STL: output_cad/print_ready/")
print("[PRINT V5] STEP: output_cad/cad_master/")
print("[PRINT V5] SPEC: output_cad/PRINT_SPEC.txt")
