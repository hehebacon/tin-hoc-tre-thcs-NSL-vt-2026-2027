#!/usr/bin/env python3
"""XZORT Rescue Dragon — exterior module CAD v2.
Build123d / millimetres. Separate printable shell groups for fit-checking.
WARNING: prototype geometry only; run in the project environment and verify fit before printing.
"""
from build123d import *
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out" / "DRAGON_MODULES"
PRINT = OUT / "PRINT"
REF = OUT / "REF"
PRINT.mkdir(parents=True, exist_ok=True)
REF.mkdir(parents=True, exist_ok=True)
MAX_MM = 350.0

def soft_box(x, y, z, r=2):
    b = Box(x, y, z)
    try:
        return fillet(b.edges(), min(r, x/4, y/4, z/4))
    except Exception:
        return b

def ellipsoid(rx, ry, rz, at):
    # Non-uniform scale creates an ellipsoid from a unit sphere in build123d/OCC.
    return Sphere(1).scale((rx, ry, rz)).translate(at)

def beam(a, b, w, h, r=2):
    va, vb = Vector(a), Vector(b)
    d = vb - va
    ln = d.length
    if ln < 0.01:
        raise ValueError("beam endpoints must differ")
    shape = soft_box(ln, w, h, r)
    axis = Vector(1, 0, 0).cross(d)
    if axis.length > 1e-8:
        dot = max(-1.0, min(1.0, d.X / ln))
        shape = shape.rotate(Axis((0, 0, 0), axis), math.degrees(math.acos(dot)))
    elif d.X < 0:
        shape = shape.rotate(Axis.Z, 180)
    return shape.translate(((va.X+vb.X)/2, (va.Y+vb.Y)/2, (va.Z+vb.Z)/2))

def plate(points, thickness=3):
    wire = Polyline([(x, 0, z) for x, z in points], close=True)
    return extrude(Face(wire), amount=thickness, dir=(0, 1, 0))

def ring_bezel(center, outer, inner, depth, axis="y"):
    x,y,z=center
    rot=(90,0,0) if axis=="y" else (0,90,0)
    a=Cylinder(outer, depth, rotation=rot).translate((x,y,z))
    b=Cylinder(inner, depth+1, rotation=rot).translate((x,y,z))
    return a.cut(b)

def make_head():
    p=[
      ellipsoid(22,18,17,(-116,0,28)),
      beam((-124,0,22),(-158,0,10),25,15,4),
      beam((-132,0,5),(-159,0,4),21,7,2),
      ellipsoid(10,12,6,(-155,0,2)),
      beam((-150,0,17),(-167,0,12),7,6,1.5),
    ]
    for side in (-1,1):
        pts=[(-108,side*13,42),(-103,side*16,54),(-107,side*18,66),(-117,side*19,77),(-128,side*19,82)]
        widths=[13,10,7,4]
        for i in range(len(pts)-1):
            p.append(beam(pts[i],pts[i+1],widths[i],widths[i],1.5))
        p += [
          ellipsoid(10,7,8,(-132,side*20,15)),
          beam((-134,side*19,38),(-111,side*22,42),7,6,1.5),
          ring_bezel((-120,side*22,30),7.5,4.2,5,"y")
        ]
        for i in range(3):
            x=-140+i*7
            p.append(plate([(x,5),(x+4,14),(x+11,12),(x+8,5)],3).translate((0,side*21,0)))
    # A lower jaw gap gives the muzzle a readable dragon silhouette.
    return p

def make_back_shell():
    p=[]
    # Independent saddle scales; not fused to the chassis, so shell thickness can be adjusted.
    spine=[(-82,0,34),(-62,0,47),(-38,0,53),(-12,0,52),(15,0,44),(36,0,28),(48,0,8)]
    for i,(x,y,z) in enumerate(spine):
        t=i/(len(spine)-1)
        p.append(ellipsoid(17-3*t,25-4*t,8-1.5*t,(x,0,z)))
        w=23-4*t; h=15-3*t
        p.append(plate([(-w/2,0),(-w*.32,h*.62),(0,h),(w*.32,h*.62),(w/2,0),(0,-h*.12)],3.2)
                .rotate(Axis.X,90).translate((x,0,z+8)))
        if i < 6:
            p.append(beam((x,0,z+7),(x-5,0,z+18-2*t),7-2*t,6-1.5*t,1.5))
    for side in (-1,1):
        for i,(x,z) in enumerate([(-68,29),(-48,36),(-27,38),(-5,34),(17,25),(34,13)]):
            w=19 if i<3 else 16
            sc=plate([(-w/2,0),(-w*.25,9),(w*.25,8),(w/2,0),(0,-3)],3)
            p.append(sc.rotate(Axis.X,90).rotate(Axis.Y,side*12).translate((x,side*43,z)))
        # Open circular rings leave pivot access visible around the leg roots.
        p.append(ellipsoid(18,8,15,(-43,side*46,0)))
        p.append(ring_bezel((-43,side*54,0),12,7,4,"y"))
    # four low-profile mounting ears; M3 holes are intentionally clearance-sized.
    for x in (-55,55):
        for y in (-38,38):
            p.append(soft_box(14,10,4,1.2).translate((x,y,4)))
            p.append(Cylinder(1.7,6).translate((x,y,4)).cut(soft_box(0.1,0.1,0.1,.01))) if False else None
    return p

def make_tail():
    p=[]
    path=[(54,0,-7),(72,0,-18),(82,0,-35),(78,0,-51),(64,0,-65),
          (45,0,-76),(23,0,-80),(2,0,-75),(-17,0,-61),(-31,0,-44),(-40,0,-28)]
    radii=[15,14,12.5,11,9.5,8.2,7,5.8,4.8,3.8]
    for i,(a,b) in enumerate(zip(path[:-1],path[1:])):
        r=radii[i]
        p.append(beam(a,b,r*1.55,r*1.35,min(3,r*.22)))
        p.append(ellipsoid(r*.78,r*.82,r*.78,b))
        p.append(plate([(-r,0),(-r*.55,r*.8),(0,r*1.15),(r*.55,r*.8),(r,0),(0,-r*.18)],2.6)
                   .rotate(Axis.X,90).translate(((a[0]+b[0])/2,0,(a[2]+b[2])/2+r*.55)))
    # End cap is placed at the actual end of the final tail link to prevent a detached tip.
    p += [ellipsoid(7.5,7,6,(-44,0,-24)),
          ellipsoid(3.8,4,3.8,(-48,0,-24))]
    return p

def make_leg_covers():
    out={}
    for name,sx,sy in (("FL",-1,-1),("FR",-1,1),("RL",1,-1),("RR",1,1)):
        hip=(sx*50,sy*34,-7)
        knee=(sx*70,sy*74,-13)
        ankle=(sx*104,sy*92,-77)
        foot=(sx*131,sy*109,-177)
        p=[
          ellipsoid(16,13,17,hip),
          beam(hip,knee,25,22,3),
          ellipsoid(12,11,12,knee),
          beam(knee,ankle,22,19,2.5),
          ellipsoid(10,9,10,ankle),
          beam(ankle,foot,19,16,2),
          soft_box(30,24,9,3).translate((foot[0],foot[1],foot[2]-4))
        ]
        for j in (-1,0,1):
            p.append(soft_box(12,5,4,1.5).translate((foot[0]+sx*7,foot[1]+j*6,foot[2]-8)))
        out[name+"_leg_cover"]=p
    return out

def export_group(name, parts):
    obj=Compound(parts)
    bb=obj.bounding_box()
    dims=(float(bb.size.X),float(bb.size.Y),float(bb.size.Z))
    if max(dims)>MAX_MM:
        raise RuntimeError(f"{name} exceeds {MAX_MM} mm: {dims}")
    export_stl(obj,str(PRINT/(name+".stl")))
    return obj,dims

def main():
    modules={
      "head_shell":make_head(),
      "back_armor":make_back_shell(),
      "tail_shell":make_tail(),
      **make_leg_covers()
    }
    assembly=[]
    lines=["XZORT RESCUE DRAGON — MODULAR EXTERIOR V2","Units: mm",
      "Appearance target: white/black/blue dragon armor; no wings; 4 legs / 12 servo robot.",
      "IMPORTANT: visual shells are prototypes. Fit to the actual chassis and verify motion before printing."]
    for name,parts in modules.items():
        obj,dims=export_group(name,parts)
        assembly.append(obj)
        lines.append(f"{name}.stl | {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm | {len(parts)} solids")
    all_obj=Compound([s for group in assembly for s in group.solids()])
    bb=all_obj.bounding_box()
    dims=(float(bb.size.X),float(bb.size.Y),float(bb.size.Z))
    lines.append(f"Exterior overall bounding box: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm")
    lines.append("Fit-check items: servo-axis clearance, M3 fasteners, cable path, print orientation, minimum wall thickness.")
    export_step(all_obj,str(REF/"dragon_exterior_assembly.step"))
    (OUT/"MODULE_MANIFEST.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))

if __name__=="__main__":
    main()
