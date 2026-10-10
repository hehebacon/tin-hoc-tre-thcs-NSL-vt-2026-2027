#!/usr/bin/env python3
"""XZORT Rescue Dragon quadruped CAD v2 — dimensions in mm.

Reference styling: dragon-1.png (horned head, layered scales, wings, segmented tail).
Mechanical geometry remains a four-legged, 12-servo rescue robot. No global scaling:
servo envelopes and link lengths stay at their authored dimensions.
"""
from build123d import *
from pathlib import Path
import math
import shutil

ROOT = Path(__file__).resolve().parent
OUT = Path(__import__("os").environ.get("XZORT_OUT", ROOT / "out"))
MAX_MM = 350.0
SERVO_X, SERVO_Y, SERVO_Z = 41.0, 21.0, 41.0  # DS3225 envelope + small CAD allowance

if OUT.exists():
    for p in OUT.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".stl", ".step", ".stp"}:
            p.unlink()
else:
    OUT.mkdir(parents=True, exist_ok=True)
(OUT / "PRINT").mkdir(parents=True, exist_ok=True)
(OUT / "REF").mkdir(parents=True, exist_ok=True)

def rb(x, y, z, r=2):
    s = Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    if r <= 0:
        return s
    try:
        return fillet(s.edges(), min(r, x/4, y/4, z/4))
    except Exception:
        return s

def ball(r, sx=1, sy=1, sz=1):
    return Sphere(r).scale((sx, sy, sz))

def beam_between(a, b, width, height, radius=2):
    va, vb = Vector(a), Vector(b)
    d = vb - va
    length = d.length
    if length <= 0.1:
        raise ValueError("Beam endpoints must be distinct")
    shape = rb(length, width, height, radius)
    axis = Vector(1, 0, 0).cross(d)
    if axis.length > 1e-8:
        dot = max(-1.0, min(1.0, d.X / length))
        shape = shape.rotate(Axis((0, 0, 0), axis), math.degrees(math.acos(dot)))
    elif d.X < 0:
        shape = shape.rotate(Axis.Z, 180)
    return shape.translate(((va.X+vb.X)/2, (va.Y+vb.Y)/2, (va.Z+vb.Z)/2))

def scale_plate(width, height, thickness=3):
    pts = [(-width/2, 0), (-width*.28, height*.7), (0, height),
           (width*.28, height*.7), (width/2, 0), (0, -height*.16)]
    wire = Polyline([(x, 0, z) for x, z in pts], close=True)
    return extrude(Face(wire), amount=thickness, dir=(0, 1, 0))

def make_body():
    shell = rb(180, 90, 60, 14)
    cavity = rb(118, 54, 34, 8).translate((5, 0, -2))
    shell = shell.cut(cavity)
    # Removable lower panel and mounting bosses.
    panel = rb(132, 62, 5, 3).translate((0, 0, -29))
    for x in (-52, -18, 18, 52):
        for y in (-23, 23):
            panel = panel.cut(Cylinder(1.7, 8, align=(Align.CENTER, Align.CENTER, Align.CENTER)).translate((x, y, -29)))
    # Dorsal scale plates, kept separate as grouped printable detail.
    scales = []
    for i, x in enumerate(range(-58, 63, 20)):
        plate = scale_plate(22, 18, 3).rotate(Axis.X, 90).translate((x, 0, 31))
        scales.append(plate)
    # Side armor rows
    for side in (-1, 1):
        for row in range(2):
            for i, x in enumerate(range(-55, 56, 22)):
                plate = scale_plate(21, 15, 3).rotate(Axis.X, 90)
                scales.append(plate.translate((x, side*(45+row*2), -10+row*20)))
    return shell, panel, scales

def make_head():
    parts = []
    skull = rb(68, 62, 48, 16).translate((-105, 0, 27))
    muzzle = rb(48, 44, 25, 9).translate((-145, 0, 13))
    jaw = rb(48, 42, 8, 3).translate((-143, 0, -3))
    parts += [skull, muzzle, jaw]
    # Eye sockets and raised eye housings (camera windows are 16 mm openings).
    for side in (-1, 1):
        socket = ball(12, 1.0, 0.78, 0.85).translate((-116, side*27, 35))
        rim = ball(15, 1.0, 0.82, 0.9).translate((-116, side*27, 35))
        parts.append(rim.cut(socket))
        parts.append(rb(29, 12, 9, 3).translate((-119, side*28, 47)))
        horn = Cone(9, 2.2, 29, align=(Align.CENTER, Align.CENTER, Align.MIN))
        horn = horn.rotate(Axis.Y, -18).translate((-99, side*22, 50))
        parts.append(horn)
        # Cheek scales
        for i in range(3):
            parts.append(scale_plate(20-i*3, 13-i*2, 3).rotate(Axis.X, 90).translate((-128+i*8, side*(30+i), 18+i*7)))
    # Nose bridge and nostril rims
    parts.append(rb(18, 35, 13, 5).translate((-164, 0, 17)))
    for side in (-1, 1):
        parts.append(ball(3, 1, 1, .7).translate((-171, side*10, 20)))
    return parts

def make_neck():
    parts = []
    for i, x in enumerate((-87, -76, -65)):
        ring = Cylinder(22-i*2, 10, rotation=(0,90,0),
                        align=(Align.CENTER, Align.CENTER, Align.CENTER)).translate((x,0,12))
        collar = Cylinder(27-i*2, 3, rotation=(0,90,0),
                          align=(Align.CENTER, Align.CENTER, Align.CENTER)).translate((x,0,12))
        parts.append(ring.fuse(collar))
    return parts

def make_wing(side):
    # Decorative dragon-like folded wing, thin and removable; stays inside 350 mm envelope.
    pts = [
        (0, side*38, 22), (0, side*110, 67), (0, side*91, 79),
        (0, side*73, 61), (0, side*58, 73), (0, side*45, 42),
        (0, side*38, 22)
    ]
    membrane = extrude(Face(Polyline(pts)), amount=3.2, dir=(1,0,0)).translate((-18,0,0))
    shoulder = ball(13, 1.2, 1.0, .8).translate((-15, side*42, 28))
    return Compound([membrane, shoulder])

def make_tail():
    parts = []
    lengths = [16, 14, 12, 10, 8, 7, 6, 5]
    radii = [14, 12, 10, 8.5, 7, 5.8, 4.8, 3.8]
    x = 82
    z = -1
    for i, (length, radius) in enumerate(zip(lengths, radii)):
        seg = Cylinder(radius, length, rotation=(0,90,0),
                       align=(Align.CENTER, Align.CENTER, Align.CENTER))
        seg = seg.fuse(Cylinder(radius+3, 3, rotation=(0,90,0),
                                align=(Align.CENTER, Align.CENTER, Align.CENTER)).translate((length*.25,0,0)))
        seg = seg.translate((x+length/2, 0, z+i*1.3))
        parts.append(seg)
        # Small dorsal ridge per tail segment.
        ridge = Cone(radius*.65, 1.2, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
        parts.append(ridge.translate((x+length*.55, 0, z+radius+i*1.3)))
        x += length
    parts.append(ball(5).translate((x+2, 0, z+10)))
    return parts

def make_legs():
    groups = {name: [] for name in ("FL_leg", "FR_leg", "RL_leg", "RR_leg")}
    for name, sx, sy in (("FL",-1,-1), ("FR",-1,1), ("RL",1,-1), ("RR",1,1)):
        hip = (sx*50, sy*34, -7)
        # 40 mm coxa, 75 mm femur, 85 mm tibia. These are physical lengths,
        # not scaled decorative approximations.
        coxa = (hip[0]+sx*18, hip[1]+sy*35.72, -9)
        femur = (coxa[0]+sx*35, coxa[1]+sy*18, coxa[2]-64.3)
        foot_joint = (femur[0]+sx*22, femur[1]+sy*14, femur[2]-80.8)
        # Servo housings at all three axes; actual mounting details are separate follow-up work.
        for p in (hip, coxa, femur):
            groups[name].append(rb(SERVO_X, SERVO_Y, SERVO_Z, 3).translate(p))
            groups[name].append(Cylinder(6, 4, rotation=(0,90,0),
                align=(Align.CENTER, Align.CENTER, Align.CENTER)).translate((p[0], p[1], p[2]+SERVO_Z/2)))
        groups[name].append(beam_between(hip, coxa, 28, 24, 3))
        groups[name].append(beam_between(coxa, femur, 25, 22, 3))
        groups[name].append(beam_between(femur, foot_joint, 22, 18, 3))
        foot = rb(36, 26, 10, 4).translate((foot_joint[0]+sx*3, foot_joint[1]+sy*2, foot_joint[2]-5))
        for j in (-1,0,1):
            foot = foot.fuse(rb(17, 5, 5, 2).translate((foot_joint[0]+sx*12, foot_joint[1]+sy*2+j*6, foot_joint[2]-8)))
        groups[name].append(foot)
    return groups

def bounds(shapes):
    boxes = [s.bounding_box() for s in shapes]
    return (
        min(float(b.min.X) for b in boxes), max(float(b.max.X) for b in boxes),
        min(float(b.min.Y) for b in boxes), max(float(b.max.Y) for b in boxes),
        min(float(b.min.Z) for b in boxes), max(float(b.max.Z) for b in boxes),
    )

def export_group(name, shapes):
    if not shapes:
        raise RuntimeError(f"Empty CAD group: {name}")
    obj = Compound(shapes)
    export_stl(obj, str(OUT / "PRINT" / f"{name}.stl"))
    return obj

def main():
    body, panel, scales = make_body()
    head = make_head()
    neck = make_neck()
    tail = make_tail()
    legs = make_legs()
    wings = [make_wing(-1), make_wing(1)]
    groups = {
        "body": [body] + scales,
        "head": head + neck,
        "electronics": [panel, rb(112,48,4,2).translate((4,0,14))], # removable tray + board plate
        "wings": wings,
        "tail": tail,
        **legs,
    }
    # Export per-group printable STL and a single reference STEP assembly.
    objects = {name: export_group(name, shapes) for name, shapes in groups.items()}
    all_shapes = [shape for shapes in groups.values() for shape in shapes]
    envelope = bounds(all_shapes)
    size = (envelope[1]-envelope[0], envelope[3]-envelope[2], envelope[5]-envelope[4])
    if max(size) > MAX_MM + 0.05:
        raise RuntimeError(f"Envelope guard failed: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm (limit {MAX_MM:.1f})")
    export_step(Compound(all_shapes), str(OUT / "REF" / "full_assembly.step"))
    manifest = [
        "XZORT RESCUE DRAGON QUADRUPED v2",
        "Reference style: dragon-1.png — horns, raised eyes, layered scales, folded wings, segmented tail",
        "Mechanical layout: four legs / 12 servo housings",
        "No global scaling. DS3225 envelope remains 41 x 21 x 41 mm.",
        "Link centerline targets: coxa 40 mm, femur 75 mm, tibia 85 mm.",
        f"Bounding box: X={size[0]:.2f}, Y={size[1]:.2f}, Z={size[2]:.2f} mm",
        f"Hard envelope limit: {MAX_MM:.1f} mm",
        "NOTE: STEP/STL are design prototypes. Validate servo horn geometry, fasteners, wire routing, clearances and physical gait before printing the full set.",
        "Printable groups: " + ", ".join(groups.keys()),
    ]
    (OUT / "PRINT_MANIFEST.txt").write_text("\n".join(manifest)+"\n", encoding="utf-8")
    print("[CAD] Groups:", ", ".join(groups.keys()))
    print("[CAD] Envelope: %.2f x %.2f x %.2f mm" % size)
    print("[CAD] Exported out/REF/full_assembly.step and grouped out/PRINT/*.stl")

if __name__ == "__main__":
    main()
