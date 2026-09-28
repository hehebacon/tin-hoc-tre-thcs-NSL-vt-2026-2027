from build123d import *
from pathlib import Path
import math

OUT = Path("out")
OUT.mkdir(exist_ok=True)

# ============================================================
# XZORT RESCUE QUADRUPED — MECHANICAL DRAGON ARMOR CAD
# V8
# - 12-DOF quadruped skeleton
# - Separate dragon joint covers / armor shells
# - Layered body scales
# - Flat dragon fins / membranes
# - Detailed mechanical dragon head
# - Segmented articulated-style tail
# - Parts exported individually + visual full assembly
# ============================================================

# Coordinate convention:
#   X = front (+) / rear (-)
#   Y = left (+) / right (-)
#   Z = up (+)
# Leg names: FL, FR, RL, RR
# DOFs per leg: COXA, FEMUR, TIBIA


def rounded_box(x, y, z, r=6):
    s = Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    try:
        rr = max(0.1, min(r, x / 2 - 0.1, y / 2 - 0.1, z / 2 - 0.1))
        return fillet(s.edges(), rr)
    except Exception:
        return s


def rounded_plate(w, d, t, angle=0):
    s = rounded_box(w, d, t, min(t * 0.42, 6))
    return s.rotate(Axis.X, angle)


def cyl_x(r, h):
    return Cylinder(r, h, rotation=(0, 90, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN))


def make_xz_face(points):
    wire = Polyline([(x, 0, z) for x, z in points], close=True)
    return Face(wire)


def make_xy_face(points):
    wire = Polyline([(x, y, 0) for x, y in points], close=True)
    return Face(wire)


# ============================================================
# DRAGON BODY
# ============================================================

def body():
    s = rounded_box(300, 170, 82, 28)
    s = s.fuse(Sphere(78).translate((-72, 0, 5)))
    s = s.fuse(Sphere(70).translate((80, 0, 5)))
    s = s.fuse(Sphere(58).translate((0, 0, 18)))
    s = s.fuse(rounded_box(190, 92, 30, 14).translate((15, 0, 50)))
    return s


def body_belly_armor():
    # Thin armor panel under the chassis; intentionally separate from body.
    p = rounded_box(220, 118, 9, 4).translate((10, 0, -43))
    for x in range(-80, 111, 32):
        p = p.fuse(rounded_box(20, 92, 5, 2).translate((x, 0, -48)))
    return p


def dorsal_spikes():
    out = None
    for i in range(11):
        x = -120 + i * 24
        h = 16 + 14 * math.sin(i / 10 * math.pi)
        spike = Cone(11, 2.5, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        spike = spike.rotate(Axis.Y, 90).translate((x, 0, 64 + h * 0.20))
        out = spike if out is None else out.fuse(spike)
    return out


# ============================================================
# DETAILED MECHANICAL DRAGON HEAD
# ============================================================

def head_skull():
    s = Sphere(62)
    s = s.fuse(Sphere(40).translate((38, -38, -2)))
    s = s.fuse(Sphere(40).translate((38, 38, -2)))
    s = s.fuse(rounded_box(58, 84, 45, 15).translate((72, 0, -10)))
    s = s.fuse(Sphere(23).translate((106, 0, -3)))
    s = s.fuse(rounded_box(48, 72, 23, 9).translate((73, 0, -38)))

    # Eye sockets and nostrils are real recesses.
    for y in (-48, 48):
        s = s.cut(Sphere(18).translate((54, y, 18)))
    for y in (-12, 12):
        s = s.cut(Sphere(5).translate((116, y, -2)))
    return s


def head_brow_armor():
    out = None
    for y, ang in [(-40, -15), (40, 15)]:
        brow = rounded_box(46, 18, 12, 5).translate((45, y, 38))
        brow = brow.rotate(Axis.X, ang)
        out = brow if out is None else out.fuse(brow)
    return out


def head_cheek_armor():
    out = None
    for y in (-1, 1):
        cheek = rounded_plate(58, 34, 8, 16).translate((73, y * 48, -6))
        rear = rounded_plate(42, 26, 7, 24).translate((42, y * 58, 16))
        out = cheek.fuse(rear) if out is None else out.fuse(cheek).fuse(rear)
    return out


def head_horns():
    out = None
    for y, ang in [(-43, -18), (43, 18)]:
        horn = Cone(17, 5, 42, align=(Align.CENTER, Align.CENTER, Align.MIN))
        horn = horn.rotate(Axis.Y, ang).translate((7, y, 43))
        out = horn if out is None else out.fuse(horn)
    # smaller rear horns
    for y in (-31, 31):
        horn = Cone(9, 2.5, 26, align=(Align.CENTER, Align.CENTER, Align.MIN))
        horn = horn.rotate(Axis.Y, -10 if y < 0 else 10).translate((28, y, 55))
        out = out.fuse(horn)
    return out


def head_jaw():
    jaw = rounded_box(68, 70, 18, 7).translate((91, 0, -39))
    # mechanical teeth: small separate-looking teeth along both jaw edges
    for y in (-28, -14, 14, 28):
        tooth = Cone(5.5, 1.5, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
        tooth = tooth.translate((98, y, -52))
        jaw = jaw.fuse(tooth)
    return jaw


def head_sensor_mount():
    # Central flat face for camera/sensor module.
    mount = rounded_box(28, 40, 22, 5).translate((113, 0, 8))
    for y in (-12, 12):
        mount = mount.cut(Cylinder(2.5, 30).translate((113, y, -5)))
    return mount


def head():
    return (head_skull()
            .fuse(head_brow_armor())
            .fuse(head_cheek_armor())
            .fuse(head_horns())
            .fuse(head_jaw())
            .fuse(head_sensor_mount()))


# ============================================================
# NECK + DRAGON FRILL
# ============================================================

def neck():
    return cyl_x(42, 70).translate((-5, 0, 0))


def neck_armor_segments():
    out = None
    for i in range(5):
        x = -34 + i * 17
        ring = rounded_box(34 + i * 3, 96 + i * 3, 12, 4).translate((x, 0, 38 - i * 3))
        ring = ring.cut(rounded_box(23 + i * 2, 78 + i * 2, 18, 3).translate((x, 0, 38 - i * 3)))
        out = ring if out is None else out.fuse(ring)
    return out


def neck_frill():
    out = None
    levels = [
        (58, 30, 7, 30, 20),
        (68, 34, 7, 36, 9),
        (76, 38, 8, 40, -3),
        (68, 34, 7, 35, -18),
        (56, 29, 6, 27, -31),
    ]
    for i, (w, d, t, a, z) in enumerate(levels):
        x = -34 + i * 17
        p = rounded_plate(w, d, t, a).translate((x, 0, z))
        l = rounded_plate(w * .66, d * .58, t, a + 8).translate((x, -d * .62, z - 3))
        r = rounded_plate(w * .66, d * .58, t, a - 8).translate((x, d * .62, z - 3))
        out = p if out is None else out.fuse(p)
        out = out.fuse(l).fuse(r)
    return out


# ============================================================
# LAYERED DRAGON SCALES
# ============================================================

def scale_plate(w, d, t, angle=0):
    # Pointed shield-like scale, but still printable and thick enough.
    pts = [(-w / 2, -d / 2), (w / 2, -d / 2),
           (w / 2 + d * .20, 0), (w / 2, d / 2),
           (-w / 2, d / 2), (-w / 2 - d * .20, 0)]
    s = extrude(make_xy_face(pts), amount=t)
    return s.rotate(Axis.X, angle)


def body_scales():
    out = None
    for row in range(3):
        for i in range(9):
            x = -108 + i * 27 + (row % 2) * 13
            y = (row - 1) * 34
            w = 34 + 12 * math.sin(i / 8 * math.pi)
            sc = scale_plate(w, 28, 6, 18).translate((x, y, 61 + row * 4))
            out = sc if out is None else out.fuse(sc)
    return out


def shoulder_scales():
    out = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            for i in range(3):
                sc = scale_plate(34 - i * 4, 25 - i * 2, 6, 12)
                sc = sc.translate((sx * (104 - i * 7), sy * (82 + i * 5), 35 + i * 5))
                out = sc if out is None else out.fuse(sc)
    return out


# ============================================================
# FLAT DRAGON FINS / MEMBRANES
# ============================================================

def dragon_fin(points, thickness=4):
    return extrude(make_xz_face(points), amount=thickness, dir=(0, 1, 0))


def body_fins():
    # Flat fins on both sides of the body. They are deliberately planar.
    profile = [(-92, 10), (-40, 48), (12, 65), (62, 49),
               (108, 24), (78, 10), (32, 19), (-18, 16)]
    out = None
    for sy in (-1, 1):
        fin = dragon_fin(profile, 4).translate((0, sy * 78, 5))
        out = fin if out is None else out.fuse(fin)
    return out


def leg_fin():
    # One planar membrane module. Mounted on the outside of each leg.
    profile = [(0, 0), (34, 25), (80, 43), (126, 36),
               (154, 17), (132, 3), (88, 6), (46, 2)]
    return dragon_fin(profile, 4)


def leg_fin_edge():
    out = None
    for x, z, w, h, ang in [
        (34, 23, 28, 7, 18), (78, 40, 34, 7, 9),
        (120, 31, 32, 7, -5), (145, 16, 26, 6, -16)
    ]:
        p = rounded_plate(w, 7, h, ang).translate((x, -2, z))
        out = p if out is None else out.fuse(p)
    return out


# ============================================================
# 12-DOF LEG MECHANICS
# ============================================================

def joint_hub():
    j = cyl_x(30, 34)
    try:
        j = j.cut(cyl_x(7, 48).translate((-7, 0, 0)))
    except Exception:
        pass
    return j


def joint_armor_cover():
    # Outer cap around a joint. It is a visual/printable armor shell.
    shell = Sphere(37)
    shell = shell.cut(Sphere(29))
    # flatten the lower part slightly
    return shell


def coxa_link():
    L = 52
    core = rounded_box(L, 42, 34, 8).translate((L / 2, 0, 0))
    core = core.fuse(joint_hub())
    cap = joint_armor_cover().translate((0, 0, 0))
    return core.fuse(cap)


def femur_link():
    L = 150
    s = rounded_box(L, 42, 32, 9).translate((L / 2, 0, 0))
    s = s.fuse(joint_hub()).fuse(joint_hub().translate((L, 0, 0)))
    return s


def tibia_link():
    L = 165
    s = rounded_box(L, 38, 30, 8).translate((L / 2, 0, 0))
    s = s.fuse(joint_hub()).fuse(joint_hub().translate((L, 0, 0)))
    return s


def femur_armor():
    # Two triangular/shield layers around the structural link.
    upper = dragon_fin([(0, -16), (55, 22), (112, 19), (145, 0),
                        (112, -19), (55, -22)], 5)
    lower = dragon_fin([(10, -9), (52, 10), (112, 8), (135, 0),
                        (112, -8), (52, -10)], 4)
    return upper.fuse(lower)


def tibia_armor():
    upper = dragon_fin([(0, -14), (52, 19), (116, 15), (158, 0),
                        (116, -15), (52, -19)], 5)
    return upper


def foot_claw():
    base = rounded_box(58, 42, 12, 7).translate((10, 0, 0))
    for y in (-14, 0, 14):
        toe = rounded_box(38, 8, 9, 3).translate((42, y, -1))
        tip = Cone(5, 1.5, 16, align=(Align.CENTER, Align.CENTER, Align.MIN))
        tip = tip.rotate(Axis.Y, 90).translate((61, y, -1))
        base = base.fuse(toe).fuse(tip)
    return base


def shoulder():
    return Sphere(48).cut(Sphere(36).translate((8, 0, 10)))


def joint_cover_set():
    # Three visible armor caps: coxa / knee / ankle.
    out = None
    for x, z, scale in [(0, 0, 1.0), (150, 0, .92), (315, 0, .82)]:
        cap = joint_armor_cover().scale(scale).translate((x, 0, z))
        out = cap if out is None else out.fuse(cap)
    return out


# ============================================================
# ARTICULATED DRAGON TAIL
# ============================================================

def tail_segment(i):
    r = max(8, 31 - i * 3.0)
    length = max(24, 46 - i * 1.8)
    core = Cone(r, max(6, r * .72), length,
                rotation=(0, 90, 0),
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    armor = scale_plate(max(22, r * 1.8), max(15, r * 1.1), 5, 18)
    armor = armor.translate((length * .35, 0, r * .75))
    return core.fuse(armor)


def tail():
    parts = []
    x = 145
    z = 8
    for i in range(9):
        seg = tail_segment(i).translate((x, 0, z))
        parts.append(seg)
        x += max(24, 46 - i * 1.8) + 5
        z -= 2.2
    out = parts[0]
    for p in parts[1:]:
        out = out.fuse(p)
    return out


def tail_joint_covers():
    out = None
    x = 175
    z = 8
    for i in range(8):
        r = max(10, 22 - i * 1.6)
        cap = Sphere(r).cut(Sphere(max(5, r - 5))).translate((x, 0, z))
        out = cap if out is None else out.fuse(cap)
        x += max(24, 46 - i * 1.8) + 5
        z -= 2.2
    return out


def tail_spines():
    out = None
    x = 160
    z = 34
    for i in range(9):
        h = max(7, 19 - i * 1.4)
        spike = Cone(8, 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        spike = spike.translate((x, 0, z))
        out = spike if out is None else out.fuse(spike)
        x += max(24, 46 - i * 1.8) + 5
        z -= 2.2
    return out


# ============================================================
# SENSOR POD / TOP COVER
# ============================================================

def sensor_pod():
    p = rounded_box(58, 46, 30, 9)
    for y in (-14, 14):
        try:
            p = p.cut(Cylinder(3, 40).translate((0, y, -20)))
        except Exception:
            pass
    return p


def cover_rail():
    return rounded_box(210, 16, 12, 4).translate((0, 0, 42))


# ============================================================
# VISUAL ASSEMBLY
# ============================================================

def assembly():
    parts = [
        body(), body_belly_armor(), dorsal_spikes(),
        head().translate((-175, 0, 50)),
        neck().translate((-145, 0, 43)),
        neck_armor_segments().translate((-145, 0, 43)),
        neck_frill().translate((-145, 0, 43)),
        body_scales(), shoulder_scales(), body_fins(),
        tail(), tail_joint_covers(), tail_spines(),
        sensor_pod().translate((-10, 0, 86)), cover_rail(),
    ]

    # Four leg modules. sx selects front/rear; sy selects left/right.
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * 105
            y = sy * 82
            z = -8

            # DOF 1: coxa yaw module
            coxa = coxa_link().translate((x, y, z))
            coxa_cap = joint_armor_cover().translate((x, y, z))

            # DOF 2: femur pitch module
            femur = femur_link().translate((x + sx * 45, y, z - 2))
            femur_arm = femur_armor().translate((x + sx * 45, y + sy * 1, z - 2))
            knee_cap = joint_armor_cover().scale(.92).translate((x + sx * 195, y, z - 2))

            # DOF 3: tibia pitch module
            tibia = tibia_link().translate((x + sx * 195, y, z - 4))
            tibia_arm = tibia_armor().translate((x + sx * 195, y + sy * 1, z - 4))
            ankle_cap = joint_armor_cover().scale(.82).translate((x + sx * 360, y, z - 4))

            foot = foot_claw().translate((x + sx * 360, y, z - 32))

            # Flat dragon membrane on the outer side of each leg.
            fin = leg_fin().translate((x + sx * 40, y + sy * 22, z - 3))
            fin_edge = leg_fin_edge().translate((x + sx * 40, y + sy * 26, z - 3))

            parts += [coxa, coxa_cap, femur, femur_arm, knee_cap,
                      tibia, tibia_arm, ankle_cap, foot, fin, fin_edge]

    result = parts[0]
    for p in parts[1:]:
        result = result.fuse(p)
    return result


# ============================================================
# EXPORTS
# ============================================================


def export_part(name, part):
    try:
        export_stl(part, OUT / f"{name}.stl")
        print(f"[STL ] {name}")
    except Exception as e:
        print(f"[STL!] {name}: {e}")
    try:
        export_step(part, OUT / f"{name}.step")
        print(f"[STEP] {name}")
    except Exception as e:
        print(f"[STEP!] {name}: {e}")


if __name__ == "__main__":
    parts = {
        "body": body(),
        "body_belly_armor": body_belly_armor(),
        "dorsal_spikes": dorsal_spikes(),
        "head": head(),
        "head_skull": head_skull(),
        "head_horns": head_horns(),
        "head_jaw": head_jaw(),
        "head_cheek_armor": head_cheek_armor(),
        "head_sensor_mount": head_sensor_mount(),
        "neck": neck(),
        "neck_armor_segments": neck_armor_segments(),
        "neck_frill": neck_frill(),
        "body_scales": body_scales(),
        "shoulder_scales": shoulder_scales(),
        "body_fins": body_fins(),
        "coxa_link": coxa_link(),
        "femur_link": femur_link(),
        "femur_armor": femur_armor(),
        "tibia_link": tibia_link(),
        "tibia_armor": tibia_armor(),
        "joint_armor_cover": joint_armor_cover(),
        "joint_cover_set": joint_cover_set(),
        "leg_fin": leg_fin(),
        "leg_fin_edge": leg_fin_edge(),
        "foot_claw": foot_claw(),
        "tail": tail(),
        "tail_joint_covers": tail_joint_covers(),
        "tail_spines": tail_spines(),
        "sensor_pod": sensor_pod(),
        "cover_rail": cover_rail(),
    }

    for name, part in parts.items():
        export_part(name, part)

    print("[FULL] Building visual full-body dragon assembly...")
    full = assembly()
    export_part("dragon_spider_full", full)

    print("\n=== XZORT MECHANICAL DRAGON CAD V8 DONE ===")
    print("12-DOF skeleton + joint armor + scales + flat fins + dragon head + segmented tail")
    print("Output:", OUT.resolve())
