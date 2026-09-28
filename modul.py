from build123d import *
from pathlib import Path
import math

OUT = Path("out")
OUT.mkdir(exist_ok=True)

# ============================================================
# XZORT RESCUE DRAGON-SPIDER — 80cm / 12 DOF
# DESIGN REVISION: DRAGON BODY FIRST
#
# HARD LOCKS
#   - no wings / no canards / no fin-wings
#   - black mechanical dragon-beast silhouette
#   - round, swollen "mythical beast belly" body
#   - large dragon head, short/small muzzle
#   - eyes are camera housings, but visually remain dragon eyes
#   - 4 legs x 3 DOF = 12 servos
#   - practical spider-robot style leg shields
#   - articulated dragon tail, tapered toward the tip
#   - layered scales follow the surfaces
#   - real internal electronics bay + top display mount
#
# PRINT_* = physical module
# REF_*   = assembly/reference only
# ============================================================

def safe_fillet(shape, radius):
    try:
        return fillet(shape.edges(), radius)
    except Exception:
        return shape

def rounded_box(x, y, z, r=0):
    s = Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return safe_fillet(s, r) if r else s

def cyl_x(radius, length):
    return Cylinder(radius, length, rotation=(0, 90, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

def cyl_y(radius, length):
    return Cylinder(radius, length, rotation=(90, 0, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

def cyl_z(radius, length):
    return Cylinder(radius, length,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

def dome_x(radius, length):
    # Rounded mechanical collar.
    return cyl_x(radius, length).fuse(Sphere(radius).translate((length, 0, 0)))

def scale_plate(width=38, height=30, thickness=5):
    pts = [
        (-width/2, 0),
        (-width*0.30, height*0.68),
        (0, height),
        (width*0.30, height*0.68),
        (width/2, 0),
        (0, -height*0.18),
    ]
    wire = Polyline([(x, 0, z) for x, z in pts], close=True)
    return extrude(Face(wire), amount=thickness, dir=(0, 1, 0))

def dragon_scale(width, height, thickness=5):
    s = scale_plate(width, height, thickness)
    # Slight central ridge makes the scale read as a real layered plate.
    ridge = rounded_box(width*0.18, thickness*1.2, height*0.55, 2)
    return s.fuse(ridge.translate((0, thickness*0.45, height*0.18)))

def tapered_beam(length, width, height):
    # Closed elongated organic/mechanical link.
    pts = [
        (0, 0),
        (length*0.15, height),
        (length*0.72, height*0.72),
        (length, height*0.30),
        (length, -height*0.30),
        (length*0.72, -height*0.72),
        (length*0.15, -height),
    ]
    wire = Polyline([(x, -width/2, z) for x, z in pts], close=True)
    return extrude(Face(wire), amount=width, dir=(0, 1, 0))

# ------------------------------------------------------------
# BODY — swollen mythical-beast belly
# ------------------------------------------------------------

def body_core():
    # Broad central belly with rounded shoulder and rear masses.
    belly = rounded_box(310, 194, 170, 68)
    shoulder = rounded_box(185, 184, 182, 62).translate((-105, 0, 8))
    rear = rounded_box(190, 178, 172, 58).translate((108, 0, 2))

    # Lower belly is deliberately curved/voluminous rather than chassis-like.
    lower = Sphere(118).scale((1.55, 1.02, 0.78)).translate((18, 0, -38))
    upper = Sphere(112).scale((1.55, 1.00, 0.70)).translate((10, 0, 42))

    return belly.fuse(shoulder).fuse(rear).fuse(lower).fuse(upper)

def body_shell():
    outer = body_core()

    # Large internal cavity for ESP32/PCA9685/IMU/power/battery/wiring.
    cavity = rounded_box(255, 130, 112, 40).translate((18, 0, -5))
    cavity = cavity.fuse(Sphere(74).scale((1.7, 1.0, 0.72)).translate((25, 0, -42)))
    shell = outer.cut(cavity)

    # Underside service opening.
    access = rounded_box(225, 118, 28, 18).translate((22, 0, -92))
    shell = shell.cut(access)

    # Structural servo root bosses. These are part of the creature body.
    for x in (-112, 108):
        for y in (-88, 88):
            boss = cyl_z(31, 45).translate((x, y, -76))
            bore = cyl_z(18, 54).translate((x, y, -80))
            shell = shell.fuse(boss.cut(bore))

    # Tail root socket.
    tail_socket = cyl_x(32, 38).translate((152, 0, 10))
    shell = shell.fuse(tail_socket)

    return shell

def body_lower_cover():
    cover = rounded_box(235, 126, 9, 12).translate((20, 0, -101))
    for x in (-92, -30, 32, 94):
        for y in (-46, 46):
            cover = cover.cut(cyl_z(3.5, 16).translate((x, y, -108)))
    return cover

# ------------------------------------------------------------
# ELECTRONICS BAY
# ------------------------------------------------------------

def electronics_tray():
    tray = rounded_box(246, 120, 8, 10).translate((20, 0, -55))
    for x in (-95, -32, 32, 95):
        for y in (-45, 45):
            tray = tray.cut(cyl_z(3, 18).translate((x, y, -64)))
    return tray

def electronics_rail():
    left = rounded_box(218, 10, 18, 3).translate((20, -51, -43))
    right = rounded_box(218, 10, 18, 3).translate((20, 51, -43))
    return left.fuse(right)

def electronics_standoffs():
    out = []
    n = 1
    for x in (-95, -32, 32, 95):
        for y in (-45, 45):
            s = cyl_z(7.5, 20).translate((x+20, y, -44))
            s = s.cut(cyl_z(3, 25).translate((x+20, y, -47)))
            out.append((f"electronics_standoff_{n:02d}", s))
            n += 1
    return out

# ------------------------------------------------------------
# TOP DISPLAY — integrated into the back, not a wing
# ------------------------------------------------------------

def screen_mount():
    base = rounded_box(122, 82, 10, 12).translate((25, 0, 112))
    opening = rounded_box(100, 60, 18, 8).translate((25, 0, 116))
    frame = base.cut(opening)
    for x in (-18, 68):
        for y in (-31, 31):
            frame = frame.fuse(
                cyl_z(7, 14).translate((x, y, 108)).cut(
                    cyl_z(2.8, 18).translate((x, y, 106))
                )
            )
    return frame

def screen_rear_guard():
    # Small raised guard around the display; explicitly not a wing/fin.
    guard = rounded_box(112, 10, 24, 4).translate((25, 37, 121))
    return guard

# ------------------------------------------------------------
# DRAGON SCALES — surface-following layered armor
# ------------------------------------------------------------

def body_scales():
    parts = []
    n = 0

    # Centerline dorsal scales.
    for i in range(11):
        x = -150 + i*30
        z = 100 + 9*math.sin(i/10*math.pi)
        s = dragon_scale(42, 34, 5).rotate(Axis.X, 90)
        s = s.translate((x, -3, z))
        parts.append((f"body_dorsal_scale_{n:03d}", s))
        n += 1

    # Side rows: overlapping plates follow the belly sides.
    for side in (-1, 1):
        for row in range(4):
            z = -35 + row*34
            for i in range(10):
                x = -135 + i*29 + (12 if row % 2 else 0)
                s = dragon_scale(38, 28, 5).rotate(Axis.X, 90)
                s = s.translate((x, side*(94 + 3*row), z))
                parts.append((f"body_side_scale_{n:03d}", s))
                n += 1

    # Rear/top overlap gives the body a dragon hide rather than a flat chassis.
    for row in range(2):
        for i in range(8):
            x = 8 + i*25
            y = -72 + row*42
            s = dragon_scale(34, 26, 4).rotate(Axis.X, 70)
            s = s.translate((x, y, 82))
            parts.append((f"body_rear_scale_{n:03d}", s))
            n += 1

    return parts

# ------------------------------------------------------------
# HEAD — large dragon face, wide cheeks, short muzzle
# ------------------------------------------------------------

def camera_eye_housing(side):
    y = 1 if side > 0 else -1

    # Recessed spherical camera eye with dragon-like brow around it.
    socket = Sphere(27).scale((1.05, 1.0, 0.78)).translate((-246, y*54, 122))
    socket_shell = Sphere(34).scale((1.05, 1.0, 0.84)).translate((-246, y*54, 122))
    eye = socket_shell.cut(socket)

    brow = rounded_box(68, 18, 25, 8).translate((-254, y*61, 142))
    cheek = dragon_scale(54, 36, 6).rotate(Axis.X, 90)
    cheek = cheek.translate((-247, y*68, 99))

    return eye.fuse(brow).fuse(cheek)

def dragon_head():
    # Large cranium and wide face.
    cranium = rounded_box(154, 140, 142, 45).translate((-202, 0, 102))
    face = rounded_box(126, 150, 108, 34).translate((-252, 0, 74))

    # Short, slightly protruding muzzle.
    muzzle = rounded_box(112, 104, 64, 24).translate((-315, 0, 65))
    nose = rounded_box(74, 92, 42, 18).translate((-356, 0, 68))

    # Lower jaw gives a dragon profile without making the snout long.
    jaw = rounded_box(102, 100, 27, 11).translate((-320, 0, 27))

    head = cranium.fuse(face).fuse(muzzle).fuse(nose).fuse(jaw)

    # Camera eyes remain visually integrated into the dragon face.
    head = head.fuse(camera_eye_housing(-1)).fuse(camera_eye_housing(1))

    # Brow/forehead plates.
    for y in (-1, 1):
        brow = dragon_scale(66, 42, 7).rotate(Axis.X, 90)
        head = head.fuse(brow.translate((-232, y*70, 119)))

    # Horns swept backward.
    for y in (-1, 1):
        horn_base = cyl_z(18, 28).translate((-190, y*48, 164))
        horn_tip = Cone(18, 3, 62, align=(Align.CENTER, Align.CENTER, Align.MIN))
        horn_tip = horn_tip.rotate(Axis.Y, -20)
        horn_tip = horn_tip.translate((-184, y*48, 182))
        head = head.fuse(horn_base).fuse(horn_tip)

    # Layered cheek scales.
    for y in (-1, 1):
        for i in range(3):
            s = dragon_scale(48-i*5, 34-i*4, 5)
            s = s.rotate(Axis.X, 90).translate((-236+i*18, y*(75+i*3), 68+i*12))
            head = head.fuse(s)

    # Small nose plates.
    for y in (-1, 1):
        p = rounded_box(30, 12, 16, 4).translate((-385, y*31, 71))
        head = head.fuse(p)

    # Mouth line is a separate mechanical jaw interface.
    mouth = rounded_box(72, 8, 8, 3).translate((-350, 0, 45))
    head = head.fuse(mouth)

    # Small lower teeth/serration, kept purely decorative.
    for y in (-26, -9, 9, 26):
        tooth = Cone(5.5, 1.5, 15, align=(Align.CENTER, Align.CENTER, Align.MIN))
        head = head.fuse(tooth.translate((-351, y, 30)))

    return head

# Safe non-functional sensor/tool mounting bay only.
def head_sensor_mount():
    base = rounded_box(54, 46, 22, 8).translate((-390, 0, 91))
    ring = cyl_x(20, 18).translate((-415, 0, 91))
    return base.fuse(ring)

# ------------------------------------------------------------
# NECK — articulated-looking dragon neck
# ------------------------------------------------------------

def neck_module():
    parts = []
    for i, x in enumerate((-138, -111, -84)):
        r = 42 - i*4
        core = cyl_x(r, 25).translate((x, 0, 72))
        collar = cyl_x(r+7, 30).translate((x, 0, 72))
        scale = dragon_scale(46-i*3, 34-i*2, 5).rotate(Axis.X, 90)
        scale = scale.translate((x+8, 0, 104))
        parts.append((f"neck_ring_{i+1:02d}", core.fuse(collar).fuse(scale)))
    return parts

# ------------------------------------------------------------
# LEGS — practical spider-robot armor around real joints
# ------------------------------------------------------------

SERVO_R = 18
SERVO_W = 36

def servo_housing():
    shell = rounded_box(52, 46, 44, 10)
    motor = cyl_x(SERVO_R, SERVO_W).translate((-18, 0, 0))
    shaft = cyl_x(7, 52).translate((-25, 0, 0))
    cap = cyl_x(23, 8).translate((18, 0, 0))
    return shell.fuse(motor).fuse(shaft).fuse(cap)

def spider_joint_shield():
    # Practical closed shell, not fantasy armor.
    outer = rounded_box(92, 62, 76, 18)
    inner = rounded_box(66, 48, 50, 13)
    shell = outer.cut(inner)

    top_ridge = rounded_box(70, 12, 58, 5).translate((0, 29, 0))
    side_ridge = rounded_box(12, 52, 58, 5).translate((0, -28, 0))
    return shell.fuse(top_ridge).fuse(side_ridge)

def leg_segment_3():
    beam = tapered_beam(92, 44, 25)
    armor = rounded_box(82, 50, 54, 15).translate((38, 0, 0))
    window = rounded_box(52, 36, 30, 10).translate((42, 0, 0))
    return beam.fuse(armor.cut(window))

def leg_segment_2():
    L = 120
    beam = tapered_beam(L, 40, 26)
    relief = tapered_beam(76, 24, 14).translate((23, 0, 0))
    return beam.cut(relief)

def leg_segment_1():
    L = 112
    beam = tapered_beam(L, 38, 24)
    shield = spider_joint_shield().translate((52, 0, 0))
    return beam.fuse(shield)

def leg_foot():
    foot = rounded_box(76, 52, 22, 10)
    for y in (-16, 0, 16):
        toe = rounded_box(44, 10, 13, 4).translate((28, y, -5))
        foot = foot.fuse(toe)
    return foot

LEG_POS = {
    "FL": (-112, -88, -72),
    "FR": (-112,  88, -72),
    "RL": (108, -88, -72),
    "RR": (108,  88, -72),
}

def make_leg(name, x, y, z):
    side = -1 if y < 0 else 1
    out = []

    # DOF 3: body/root joint.
    out.append((f"{name}_SERVO_3", servo_housing().translate((x, y, z))))
    out.append((f"{name}_SEGMENT_3", leg_segment_3().translate((x, y, z))))

    # DOF 2: middle joint.
    p2 = (x+88, y+side*14, z-32)
    out.append((f"{name}_SERVO_2", servo_housing().translate(p2)))
    out.append((f"{name}_SEGMENT_2", leg_segment_2().translate(p2)))

    # DOF 1: outer/lower joint + mandatory shield.
    p1 = (x+205, y+side*22, z-72)
    out.append((f"{name}_SERVO_1", servo_housing().translate(p1)))
    out.append((f"{name}_SEGMENT_1_SHIELD", leg_segment_1().translate(p1)))

    foot_pos = (p1[0]+112, p1[1], p1[2]-30)
    out.append((f"{name}_FOOT", leg_foot().translate(foot_pos)))

    return out

# ------------------------------------------------------------
# TAIL — segmented dragon tail, inspired by articulated 3D dragon
# ------------------------------------------------------------

def tail_segment(index):
    length = max(30, 60 - index*3.2)
    radius = max(7, 24 - index*1.45)

    core = cyl_x(radius, length)
    armor = cyl_x(radius+5.5, length+4)
    collar_a = cyl_x(radius+8, 10)
    collar_b = cyl_x(radius+7, 10).translate((length-6, 0, 0))

    # Overlapping top scale gives each segment a dragon-hide appearance.
    scale = dragon_scale(max(24, radius*1.9),
                         max(18, radius*1.35), 4.5)
    scale = scale.translate((length*0.42, 0, radius+5))

    cap = Sphere(radius+5).translate((length, 0, 0))
    return core.fuse(armor).fuse(collar_a).fuse(collar_b).fuse(scale).fuse(cap)

def dragon_tail():
    out = []
    x = 170
    z = 12

    for i in range(12):
        seg = tail_segment(i)

        # Gentle compound curve, with articulation gaps preserved visually.
        yaw = -4.5*i
        pitch = 2.0 + i*0.55
        seg = seg.rotate(Axis.Y, yaw).rotate(Axis.Z, pitch)
        seg = seg.translate((x, 0, z))

        out.append((f"tail_segment_{i+1:02d}", seg))

        x += max(30, 60-i*3.2)
        z += 4 + i*0.65

    return out

# ------------------------------------------------------------
# ASSEMBLY / EXPORT
# ------------------------------------------------------------

def all_components():
    parts = [
        ("body_shell", body_shell()),
        ("body_lower_cover", body_lower_cover()),
        ("electronics_tray", electronics_tray()),
        ("electronics_rail", electronics_rail()),
        ("screen_mount", screen_mount()),
        ("screen_rear_guard", screen_rear_guard()),
        ("dragon_head", dragon_head()),
        ("head_sensor_mount", head_sensor_mount()),
    ]

    parts += body_scales()
    parts += neck_module()
    parts += electronics_standoffs()
    parts += dragon_tail()

    for name, pos in LEG_POS.items():
        parts += make_leg(name, *pos)

    return parts

def export_pair(prefix, name, shape):
    export_stl(shape, str(OUT/f"{prefix}_{name}.stl"))
    export_step(shape, str(OUT/f"{prefix}_{name}.step"))
    print(f"[OK] {prefix}_{name}")

def fuse_all(parts):
    result = None
    for _, shape in parts:
        result = shape if result is None else result.fuse(shape)
    return result

def manifest(parts):
    lines = [
        "XZORT RESCUE DRAGON-SPIDER — PRINT MANIFEST",
        "="*72,
        "",
        "DESIGN LOCKS",
        "  Dragon-beast body is the primary visual form",
        "  Round/swollen mythical-beast belly",
        "  Large dragon head / wide face / short muzzle",
        "  Camera eyes integrated into dragon eye sockets",
        "  4 legs x 3 DOF = 12 servos",
        "  Segment 3 = body/root",
        "  Segment 2 = middle",
        "  Segment 1 = outer/lower + spider-style shield",
        "  Articulated tapered dragon tail",
        "  Layered surface-following scales",
        "  Real electronics bay + removable tray",
        "  Top screen mount integrated into back",
        "  NO WINGS / NO CANARDS / NO FIN-WINGS",
        "",
        "SAFETY DESIGN NOTE",
        "  Head front mount is a non-functional sensor/tool bay.",
        "  No weapon mechanism is included in this CAD.",
        "",
        "PRINT_* = intended physical module",
        "REF_*   = assembly/reference only",
        "",
        "MODULES:",
    ]

    for name, _ in parts:
        lines.append(f"  PRINT_{name}.stl / PRINT_{name}.step")

    lines += [
        "",
        "REFERENCE:",
        "  REF_full_assembly.stl / REF_full_assembly.step",
        "",
        "Hardware dimensions still require final verification",
        "against the actual servo, battery, PCB, camera and screen.",
    ]

    (OUT/"PRINT_MANIFEST.txt").write_text(
        "\n".join(lines), encoding="utf-8"
    )

if __name__ == "__main__":
    print("="*76)
    print("XZORT RESCUE DRAGON-SPIDER — 80cm / 12 DOF")
    print("DRAGON BODY FIRST / NO WINGS / MODULAR PRINT")
    print("="*76)

    parts = all_components()
    print(f"[INFO] Printable modules: {len(parts)}")

    for name, shape in parts:
        export_pair("PRINT", name, shape)

    assembly = fuse_all(parts)
    export_pair("REF", "full_assembly", assembly)
    manifest(parts)

    print(f"[DONE] Output: {OUT.resolve()}")
    print("[DONE] PRINT_* = physical modules")
    print("[DONE] REF_*   = reference only")
