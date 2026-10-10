#!/usr/bin/env python3
"""Generate a sharper, faceted XZORT dragon quadruped concept STL set.
Requires: pip install trimesh numpy
Units: mm. VISUAL CONCEPT ONLY; not mechanically validated or print-ready.
"""
from pathlib import Path
import numpy as np
import trimesh

OUT = Path(__file__).resolve().parent / "v3"
OUT.mkdir(parents=True, exist_ok=True)

def ellipsoid(center, radii, subdivisions=2):
    m = trimesh.creation.icosphere(subdivisions=subdivisions, radius=1)
    m.vertices *= np.asarray(radii, dtype=float)
    m.apply_translation(center)
    return m

def box(center, extents):
    m = trimesh.creation.box(extents=extents)
    m.apply_translation(center)
    return m

def beam(a, b, radius, sections=8):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b-a
    m = trimesh.creation.cylinder(radius=radius, height=np.linalg.norm(d), sections=sections)
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1], d))
    m.apply_translation((a+b)/2)
    return m

def cone_between(base, tip, radius, sections=8):
    a, b = np.asarray(base,float), np.asarray(tip,float)
    d=b-a
    m=trimesh.creation.cone(radius=radius, height=np.linalg.norm(d), sections=sections)
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1], d))
    m.apply_translation((a+b)/2)
    return m

def merge(parts):
    m=trimesh.util.concatenate(parts)
    m.remove_unreferenced_vertices()
    return m

# X forward is negative, Y sides, Z up. The body is kept inside ~350 mm.
head = [
    ellipsoid((-94,0,59),(31,24,20),2),
    ellipsoid((-117,0,49),(24,15,10),1),
    # angular brow/cheek armor plates
    box((-99,-20,61),(26,7,10)), box((-99,20,61),(26,7,10)),
    box((-119,-9,53),(19,5,6)), box((-119,9,53),(19,5,6)),
    cone_between((-87,-15,73),(-75,-21,94),6),
    cone_between((-87,15,73),(-75,21,94),6),
    # camera/sensor bezel pair
    trimesh.creation.annulus(r_min=5.5,r_max=8,height=3,sections=12),
    trimesh.creation.annulus(r_min=5.5,r_max=8,height=3,sections=12),
]
head[-2].apply_translation((-101,-16,66))
head[-1].apply_translation((-101,16,66))

back = [
    ellipsoid((-4,0,59),(70,36,19),2),
    # layered angular shoulder and rear plates
    box((-35,0,76),(40,61,8)),
    box((2,0,78),(44,64,8)),
    box((34,0,72),(24,53,8)),
]
for x,h,w in [(-39,16,9),(-18,20,10),(4,18,9),(25,14,8)]:
    back.append(cone_between((x,0,80),(x+5,0,80+h),w))
# side armor ribs
for x in [-31,-7,17]:
    for side in [-1,1]:
        back.append(beam((x,side*28,60),(x+9,side*33,48),4,6))

tail = [
    ellipsoid((64,0,57),(18,16,13),1),
    ellipsoid((82,0,50),(17,13,11),1),
    ellipsoid((99,3,41),(15,11,9),1),
    ellipsoid((114,7,31),(13,9,7),1),
    ellipsoid((127,11,22),(10,7,6),1),
]
for a,b,r in [
    ((78,0,58),(88,0,69),4),
    ((96,3,49),(106,4,59),3.5),
    ((112,7,38),(121,8,47),3),
]:
    tail.append(cone_between(a,b,r))

legs=[]
for x,y in [(-43,-26),(-43,26),(39,-26),(39,26)]:
    # segmented limb shells with beveled-looking armor blocks
    hip=(x,y*0.78,48)
    knee=(x+(-7 if x<0 else 7),y*1.25,28)
    ankle=(x+(-12 if x<0 else 12),y*1.43,10)
    legs += [
        ellipsoid(hip,(11,11,11),1),
        beam(hip,knee,8,8),
        beam(knee,ankle,6.5,8),
        box(((hip[0]+knee[0])/2,y*0.98,38),(19,15,10)),
        box(((knee[0]+ankle[0])/2,y*1.34,18),(15,12,8)),
        ellipsoid(ankle,(11,9,4),1),
    ]

body=[ellipsoid((-2,0,53),(72,34,18),2), box((0,0,66),(88,54,10))]
parts={
    "head_shell_v3.stl":merge(head),
    "back_armor_v3.stl":merge(back),
    "tail_shell_v3.stl":merge(tail),
    "leg_covers_v3.stl":merge(legs),
    "assembly_preview_v3.stl":merge(body+head+back+tail+legs),
}
for name, mesh in parts.items():
    mesh.export(OUT/name)
    print(f"{name}: {len(mesh.faces)} triangles; bounds={np.round(mesh.bounds,1).tolist()}")
print(f"Exported to: {OUT}")
print("WARNING: concept geometry only. Check dimensions, watertightness, wall thickness, servo fit and collisions before printing.")
