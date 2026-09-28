from build123d import *
from pathlib import Path
import math

OUT = Path("out")
OUT.mkdir(exist_ok=True)

# ============================================================
# XZORT RESCUE QUADRUPED — CHIBI MECHANICAL DRAGON CAD
# V7: rounded body + dragon wing membranes on all four legs
# ============================================================

def rounded_box(x, y, z, r=6):
    s = Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    try:
        return fillet(s.edges(), min(r, x/2-0.1, y/2-0.1, z/2-0.1))
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

# ---------- rounded dragon body ----------
def body():
    # Main silhouette is intentionally soft/organic instead of a box.
    s = rounded_box(300, 170, 82, 30)
    s = s.fuse(Sphere(78).translate((-72, 0, 5)))
    s = s.fuse(Sphere(70).translate((80, 0, 5)))
    s = s.fuse(Sphere(58).translate((0, 0, 18)))
    # raised dorsal shell
    s = s.fuse(rounded_box(190, 92, 30, 14).translate((15, 0, 50)))
    return s

# ---------- chibi angry dragon head ----------
def head():
    s = Sphere(62)
    s = s.fuse(Sphere(40).translate((38, -38, -2)))
    s = s.fuse(Sphere(40).translate((38, 38, -2)))
    s = s.fuse(rounded_box(58, 84, 45, 15).translate((72, 0, -10)))
    s = s.fuse(Sphere(23).translate((106, 0, -3)))
    s = s.fuse(rounded_box(48, 72, 23, 9).translate((73, 0, -38)))

    # angry brow forms
    for y, ang in [(-40, -15), (40, 15)]:
        brow = rounded_box(43, 18, 12, 5).translate((45, y, 38))
        brow = brow.rotate(Axis.X, ang)
        s = s.fuse(brow)

    # eye sockets
    for y in (-48, 48):
        s = s.cut(Sphere(18).translate((54, y, 18)))

    # nostrils
    for y in (-12, 12):
        s = s.cut(Sphere(5).translate((116, y, -2)))

    # small swept horns
    for y, ang in [(-43, -18), (43, 18)]:
        h = Cone(17, 5, 42, align=(Align.CENTER, Align.CENTER, Align.MIN))
        s = s.fuse(h.translate((7, y, 43)).rotate(Axis.Y, ang))
    return s

# ---------- neck ----------
def neck():
    return cyl_x(42, 70).translate((-5, 0, 0))

# ---------- layered dragon neck frill ----------
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

# ---------- chunky overlapping body armor scales ----------
def body_scales():
    out = None
    for i in range(9):
        x = -108 + i * 27
        w = 42 + 18 * math.sin(i / 8 * math.pi)
        p = rounded_plate(w, 32, 7, 18).translate((x, 0, 62 + i * 1.5))
        l = rounded_plate(w * .72, 27, 6, 12).translate((x, -71, 37))
        r = rounded_plate(w * .72, 27, 6, 12).translate((x, 71, 37))
        out = p if out is None else out.fuse(p)
        out = out.fuse(l).fuse(r)
    return out

# ---------- segmented tail ----------
def tail():
    out = None
    for i in range(9):
        r1 = max(9, 34 - i * 3.2)
        r2 = max(7, 27 - i * 2.8)
        seg = Cone(r1, r2, 45, rotation=(0, 90, 0),
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
        x = 145 + i * 38
        seg = seg.translate((x, 0, 8 - i * 1.5))
        out = seg if out is None else out.fuse(seg)
    return out

def tail_scales():
    out = None
    for i in range(9):
        x = 150 + i * 38
        w = max(20, 56 - i * 4)
        p = rounded_plate(w, 25, 6, 23).translate((x + 5, 0, 27 - i * 2))
        l = rounded_plate(w * .60, 18, 5, 14).translate((x, -21, 13 - i))
        r = rounded_plate(w * .60, 18, 5, 14).translate((x, 21, 13 - i))
        out = p if out is None else out.fuse(p)
        out = out.fuse(l).fuse(r)
    return out

# ---------- mechanical joints / leg links ----------
def joint():
    j = cyl_x(30, 34)
    try:
        j = j.cut(cyl_x(6, 44).translate((-5, 0, 0)))
    except Exception:
        pass
    return j

def upper_leg():
    L = 150
    s = cyl_x(18, L)
    s = s.fuse(joint()).fuse(joint().translate((L, 0, 0)))
    s = s.fuse(rounded_box(90, 44, 32, 11).translate((75, 0, 0)))
    return s

def lower_leg():
    L = 165
    s = cyl_x(15, L)
    s = s.fuse(joint()).fuse(joint().translate((L, 0, 0)))
    s = s.fuse(rounded_box(88, 40, 30, 10).translate((82, 0, 0)))
    s = s.fuse(Sphere(25).translate((82, 0, 4)))
    return s

def foot():
    s = rounded_box(72, 48, 16, 11)
    for y in (-14, 14):
        try:
            s = s.cut(Cylinder(2, 30).translate((7, y, -15)))
        except Exception:
            pass
    return s

# ---------- DRAGON WING MEMBRANE ----------
# This is a broad, smooth web — NOT spikes, cones, claws, or teeth.
# The membrane follows the outside of each leg like a small dragon wing.
def leg_membrane():
    upper = [
        (28, 10), (62, 34), (108, 46), (150, 38),
        (174, 20), (154, 2), (112, -2), (70, 2), (38, 0)
    ]
    lower = [
        (132, 8), (174, 30), (218, 34), (262, 18),
        (304, -8), (286, -27), (244, -20), (204, -5),
        (158, -3), (138, 0)
    ]

    # Thin extruded XZ webs, softened with a slight overlap.
    a = extrude(make_xz_face(upper), amount=5, dir=(0, 1, 0))
    b = extrude(make_xz_face(lower), amount=5, dir=(0, 1, 0))

    # Rounded attachment pads keep the membrane mechanically integrated.
    pad1 = Sphere(22).translate((38, 0, 8))
    pad2 = Sphere(20).translate((150, 0, 3))
    pad3 = Sphere(18).translate((286, 0, -8))
    return a.fuse(b).fuse(pad1).fuse(pad2).fuse(pad3)

# Smaller scalloped membrane edge pieces give a dragon-wing silhouette.
def membrane_edge():
    out = None
    for x, z, w, h, ang in [
        (64, 32, 32, 8, 18),
        (108, 42, 38, 8, 10),
        (151, 28, 34, 8, -8),
        (195, 22, 34, 8, -8),
        (239, 8, 34, 8, -15),
        (280, -12, 28, 7, -22),
    ]:
        p = rounded_plate(w, 8, h, ang).translate((x, -2, z))
        out = p if out is None else out.fuse(p)
    return out

# ---------- accessories ----------
def shoulder():
    return Sphere(48).cut(Sphere(36).translate((8, 0, 10)))

def sensor_pod():
    p = rounded_box(58, 46, 30, 9)
    for y in (-14, 14):
        try:
            p = p.cut(Cylinder(3, 40).translate((0, y, -20)))
        except Exception:
            pass
    return p

def cover_rail():
    rail = rounded_box(210, 16, 12, 4).translate((0, 0, 42))
    for x in range(-90, 91, 30):
        try:
            rail = rail.cut(Cylinder(1.7, 25).translate((x, 0, 42)))
        except Exception:
            pass
    return rail

def foot_claw():
    base = rounded_box(58, 42, 10, 7).translate((10, 0, 0))
    for y in (-13, 0, 13):
        toe = rounded_box(38, 8, 9, 3).translate((42, y, 0))
        base = base.fuse(toe)
    return base

# ---------- assembly ----------
def assembly():
    b = body()
    h = head().translate((-175, 0, 50))
    n = neck().translate((-145, 0, 43))
    nf = neck_frill().translate((-145, 0, 43))
    bs = body_scales()
    t = tail()
    ts = tail_scales()
    rail = cover_rail()
    sensor = sensor_pod().translate((-10, 0, 86))

    parts = [b, h, n, nf, bs, t, ts, rail, sensor]

    # Four mirrored mechanical dragon legs.
    for sx in (-1, 1):
        for sy in (-1, 1):
            y = sy * 78
            x = sx * 105

            sh = shoulder().translate((x, y, 10))
            up = upper_leg().translate((x, y, -5))
            lo = lower_leg().translate((x + sx * 145, y, -5))
            ft = foot().translate((x + sx * 300, y, -25))

            # Put the broad membrane on the OUTSIDE of each leg.
            # No sharp spikes: it is a continuous dragon-wing web.
            web = leg_membrane().translate((x, y + sy * 16, -5))
            edge = membrane_edge().translate((x, y + sy * 21, -5))

            parts += [sh, up, lo, ft, web, edge]

    result = parts[0]
    for p in parts[1:]:
        result = result.fuse(p)
    return result

# ---------- exports ----------
if __name__ == "__main__":
    parts = {
        "body": body(),
        "head": head(),
        "neck": neck(),
        "neck_frill": neck_frill(),
        "body_scales": body_scales(),
        "tail": tail(),
        "tail_scales": tail_scales(),
        "upper_leg": upper_leg(),
        "lower_leg": lower_leg(),
        "leg_membrane": leg_membrane(),
        "membrane_edge": membrane_edge(),
        "foot": foot(),
        "shoulder": shoulder(),
        "sensor_pod": sensor_pod(),
        "cover_rail": cover_rail(),
        "foot_claw": foot_claw(),
    }

    for name, part in parts.items():
        try:
            export_stl(part, OUT / f"{name}.stl")
        except Exception as e:
            print("[STL]", name, e)
        try:
            export_step(part, OUT / f"{name}.step")
        except Exception as e:
            print("[STEP]", name, e)

    full = assembly()
    print("Full body assembly: rounded dragon body + frill + scales + tail + 4 membrane legs")
    try:
        export_stl(full, OUT / "dragon_spider_full.stl")
    except Exception as e:
        print("[FULL STL]", e)
    try:
        export_step(full, OUT / "dragon_spider_full.step")
    except Exception as e:
        print("[FULL STEP]", e)

    print("\n=== XZORT DRAGON CAD V7 DONE ===")
    print("Output:", OUT.resolve())
