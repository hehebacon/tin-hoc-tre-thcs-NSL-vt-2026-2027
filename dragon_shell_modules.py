#!/usr/bin/env python3
"""XZORT Rescue Dragon — replaceable exterior armor modules.
Units: mm. Build123d required. Visual shell modules are separate from the load-bearing
servo chassis so they can be printed, test-fitted, and revised without reprinting legs.
This is a visual/mechanical prototype, not a print-ready guarantee.
"""
from build123d import *
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out" / "DRAGON_MODULES"
OUT.mkdir(parents=True, exist_ok=True)
MAX_MM = 350.0

def soft_box(x, y, z, r=2):
    b = Box(x, y, z)
    try:
        return fillet(b.edges(), min(r, x/4, y/4, z/4))
    except Exception:
        return b

def ellipsoid(rx, ry, rz, at):
    return Sphere(1).scale((rx, ry, rz)).translate(at)

def beam(a, b, w, h, r=2):
    va, vb = Vector(a), Vector(b)
    d = vb-va
    ln = d.length
    s = soft_box(ln, w, h, r)
    axis = Vector(1,0,0).cross(d)
    if axis.length > 1e-8:
        s = s.rotate(Axis((0,0,0), axis), math.degrees(math.acos(max(-1,min(1,d.X/ln)))))
    elif d.X < 0:
        s = s.rotate(Axis.Z, 180)
    return s.translate(((va.X+vb.X)/2,(va.Y+vb.Y)/2,(va.Z+vb.Z)/2))

def plate(points, thickness=3):
    wire = Polyline([(x,0,z) for x,z in points], close=True)
    return extrude(Face(wire), amount=thickness, dir=(0,1,0))

def screw_tab(x, y, z, width=14, length=12, thickness=4, hole=3.4):
    tab = soft_box(width, length, thickness, 1.5).translate((x,y,z))
    cutter = Cylinder(hole/2, thickness+2).translate((x,y,z))
    return tab.cut(cutter)

def make_head_shell():
    p = []
    # Long angular dragon muzzle, brow, cheek armour and swept paired horns.
    p += [ellipsoid(22,18,17,(-116,0,28)),
          beam((-124,0,22),(-158,0,10),25,15,4),
          beam((-132,0,5),(-159,0,4),21,7,2),
          ellipsoid(10,12,6,(-155,0,2))]
    for side in (-1,1):
        # swept horns built as tapered overlapping sections
        pts=[(-108,side*13,42),(-103,side*16,54),(-107,side*18,66),(-117,side*19,77),(-128,side*19,82)]
        radii=[8,6.5,4.5,2.8]
        for i in range(len(pts)-1):
            p.append(beam(pts[i],pts[i+1],radii[i]*1.7,radii[i]*1.7,1.5))
        p += [ellipsoid(9,5,8,(-120,side*20,30)),
              beam((-133,side*18,39),(-111,side*22,42),6,5,1.5)]
        for i in range(3):
            p.append(plate([(-142+i*6,8),(-137+i*6,16),(-130+i*6,13),(-133+i*6,7)],3).translate((0,side*20,0)))
        # Sensor bezel is a separate ring so a blue lens can be fitted later.
        outer=ellipsoid(7.5,4.8,6.2,(-120,side*22,30))
        inner=ellipsoid(4.5,5.2,3.4,(-120,side*22,30))
        p.append(outer.cut(inner))
    p.append(beam((-150,0,17),(-167,0,12),7,6,1.5))
    return p

def make_dorsal_armor():
    p=[]
    # Saddle panels follow a smooth arched dorsal line. Each panel is a separate print.
    spine=[(-82,0,34),(-62,0,47),(-38,0,53),(-12,0,52),(15,0,44),(36,0,28),(48,0,8)]
    for i,(x,y,z) in enumerate(spine):
        t=i/(len(spine)-1)
        p.append(ellipsoid(17-3*t,27-4*t,9-2*t,(x,0,z)))
        w=23-4*t; h=15-3*t
        p.append(plate([(-w/2,0),(-w*.32,h*.62),(0,h),(w*.32,h*.62),(w/2,0),(0,-h*.12)],3.2)
                .rotate(Axis.X,90).translate((x,0,z+8)))
        if i<6:
            p.append(beam((x,0,z+7),(x-5,0,z+18-2*t),7-2*t,6-1.5*t,1.5))
    # Two rows of side scutes: white armor plates over the darker structural torso.
    for side in (-1,1):
        for i,(x,z) in enumerate([(-68,29),(-48,36),(-27,38),(-5,34),(17,25),(34,13)]):
            w=19 if i<3 else 16
            sc=plate([(-w/2,0),(-w*.25,9),(w*.25,8),(w/2,0),(0,-3)],3)
            p.append(sc.rotate(Axis.X,90).rotate(Axis.Y,side*12).translate((x,side*43,z)))
        # Shoulder cap around leg root with a visible circular pivot bezel.
        p.append(ellipsoid(20,10,17,(-43,side*48,0)))
        p.append(ellipsoid(12,4,12,(-43,side*56,0)).cut(ellipsoid(7,5,7,(-43,side*56,0))))
    return p

def make_tail_modules():
    p=[]
    path=[(54,0,-7),(72,0,-18),(82,0,-35),(78,0,-51),(64,0,-65),
          (45,0,-76),(23,0,-80),(2,0,-75),(-17,0,-61),(-31,0,-44),(-40,0,-28)]
    radii=[15,14,12.5,11,9.5,8.2,7,5.8,4.8,3.8]
    for i,(a,b) in enumerate(zip(path[:-1],path[1:])):
        r=radii[i]
        p.append(beam(a,b,r*1.55,r*1.35,min(3,r*.22)))
        p.append(ellipsoid(r*.78,r*.82,r*.78,b))
        # Overlapping dorsal cap; distinct pieces make the tail printable.
        p.append(plate([(-r,0),(-r*.55,r*.8),(0,r*1.15),(r*.55,r*.8),(r,0),(0,-r*.18)],2.6)
                   .rotate(Axis.X,90).translate(((a[0]+b[0])/2,0,(a[2]+b[2])/2+r*.55)))
    p += [ellipsoid(7.5,7,6,(-48,0,-20)),
          ellipsoid(3.8,4,3.8,(-53,0,-20))]
    return p

def make_leg_covers():
    out={}
    for name,sx,sy in (("FL",-1,-1),("FR",-1,1),("RL",1,-1),("RR",1,1)):
        # Lightweight segmented covers deliberately leave servo axis and screw access open.
        p=[]
        hip=(sx*50,sy*34,-7)
        knee=(sx*70,sy*74,-13)
        ankle=(sx*104,sy*92,-77)
        foot=(sx*131,sy*109,-177)
        p += [ellipsoid(16,13,17,hip),
              beam(hip,knee,25,22,3),
              ellipsoid(12,11,12,knee),
              beam(knee,ankle,22,19,2.5),
              ellipsoid(10,9,10,ankle),
              beam(ankle,foot,19,16,2),
              soft_box(30,24,9,3).translate((foot[0],foot[1],foot[2]-4))]
        for j in (-1,0,1):
            p.append(soft_box(12,5,4,1.5).translate((foot[0]+sx*7,foot[1]+j*6,foot[2]-8)))
        out[name+"_leg_cover"]=p
    return out

def export(name, parts):
    if not parts:
        raise RuntimeError("Empty module: "+name)
    obj=Compound(parts)
    bb=obj.bounding_box()
    dims=(bb.size.X,bb.size.Y,bb.size.Z)
    if max(dims)>MAX_MM:
        raise RuntimeError(f"{name} exceeds {MAX_MM} mm envelope: {dims}")
    export_stl(obj,str(OUT/(name+".stl")))
    return dims

def main():
    modules={
        "head_shell":make_head_shell(),
        "dorsal_armor":make_dorsal_armor(),
        "tail_shell":make_tail_modules(),
        **make_leg_covers(),
    }
    report=["XZORT RESCUE DRAGON — EXTERIOR MODULES","Units: mm",
            "Style target: white/black/blue plated mechanical dragon, no wings.",
            "These are visual shell modules; check mating faces and servo clearances against the chassis before printing."]
    for name,parts in modules.items():
        dims=export(name,parts)
        report.append(f"{name}.stl: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm; solids={len(parts)}")
    (OUT/"MODULE_MANIFEST.txt").write_text("\n".join(report)+"\n",encoding="utf-8")
    print("\n".join(report))

if __name__=="__main__":
    main()
