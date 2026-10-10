#!/usr/bin/env python3
"""XZORT Dragon Rescue Quadruped V6 CAD source — millimetres.

Run in an environment with build123d installed:
  python dragon_v6_build.py
Exports a modular STEP/STL set into ./out_v6.

Design intent:
- target envelope <= 350 mm (verify assembled envelope after changing parameters)
- body upper/lower split for service access
- battery bay for 112 x 42 x 28 mm pack cavity
- 4 servo hardpoint regions for 12-servo quadruped layout
- integrated dragon head armor, dorsal scale/spine carrier, tail segments and leg armor
- M3 clearance holes modeled where practical; validate against actual hardware before printing.

This is a parametric engineering starting point, not certified fit-checked hardware.
"""
from build123d import *
from pathlib import Path
import math

OUT = Path("out_v6"); OUT.mkdir(exist_ok=True)
BODY_L, BODY_W, BODY_H = 180.0, 84.0, 60.0
WALL = 3.0
BATTERY_CAVITY = (112.0, 42.0, 28.0)
M3 = 3.2
SERVO_CLEARANCE = 1.0
COXA, FEMUR, TIBIA = 40.0, 75.0, 85.0
BEARING_OD, BEARING_ID, BEARING_T = 16.0, 8.0, 5.0

def export(part, name):
    if part is None:
        raise ValueError(f"{name}: empty geometry")
    export_stl(part, str(OUT / f"{name}.stl"), tolerance=0.12, angular_tolerance=0.12)
    export_step(part, str(OUT / f"{name}.step"))

def capsule_plate(length, width, thick, z=0):
    return Pos(0,0,z) * Box(length, width, thick)

def upper_body():
    # Outer upper armor with inner relief. Edge rails keep a real wall around the cavity.
    outer = Pos(0,0,15) * Box(BODY_L, BODY_W, 30)
    inner = Pos(-3,0,12) * Box(BODY_L-2*WALL, BODY_W-2*WALL, 27)
    part = outer - inner
    # Raised central dragon-back spine / armor keel
    part += Pos(-5,0,31) * Box(116,34,5)
    # Layered scale panels along both flanks; intentionally large printable plates.
    for x in (-58,-29,0,29,58):
        for side in (-1,1):
            plate = Pos(x, side*31, 27) * Rot(Z=side*5) * Box(24,12,4)
            part += plate
    # Top access-cover screw bosses, four M3 pilot/clearance holes
    for x in (-76,76):
        for y in (-30,30):
            boss = Pos(x,y,25) * Cylinder(5.8,8)
            hole = Pos(x,y,25) * Cylinder(M3/2,10)
            part += boss
            part -= hole
    # Neck/head mount at front (+X) and tail mount at rear (-X), through-bolt pattern.
    for x in (-84,84):
        for y in (-15,15):
            part -= Pos(x,y,15) * Cylinder(M3/2,34)
    # Integrated dragon dorsal spikes: center row plus swept side rows.
    # These are part of the upper-body CAD solid, not separate loose spikes.
    for i, x in enumerate(range(-54, 55, 18)):
        h = 16 if i % 2 == 0 else 12
        part += Pos(x, 0, 30 + h/2 - 1) * Rot(Y=-18) * Cone(5.2, 1.1, h)
        for side in (-1, 1):
            part += Pos(x-2, side*13, 29) * Rot(X=side*22, Y=-24) * Cone(3.8, 1.0, 11)
    return part

def lower_body():
    # Lower pan with battery bay and serviceable lid interface.
    outer = Pos(0,0,-15) * Box(BODY_L, BODY_W, 30)
    cavity = Pos(-5,0,-12) * Box(BATTERY_CAVITY[0]+8, BATTERY_CAVITY[1]+8, 25)
    part = outer - cavity
    # Battery retention rails and end stops (leave top open for insertion).
    part += Pos(-5,-25,-18) * Box(120,4,8)
    part += Pos(-5,25,-18) * Box(120,4,8)
    part += Pos(-66,0,-18) * Box(4,46,8)
    part += Pos(56,0,-18) * Box(4,46,8)
    # Leg hardpoints at four corners; holes for M3 interface screws.
    for x in (-62,62):
        for y in (-34,34):
            boss = Pos(x,y,-10) * Cylinder(10,18)
            hole = Pos(x,y,-10) * Cylinder(M3/2,22)
            part += boss
            part -= hole
            # outer cheek plate gives the coxa module a broad bolting face
            part += Pos(x, y*1.13, -10) * Box(28,7,22)
    # M3 body split fastening holes
    for x in (-76,-25,25,76):
        for y in (-37,37):
            part -= Pos(x,y,0) * Cylinder(M3/2,38)
    # electronics tray standoffs (mounting slots are provided on the separate tray)
    for x in (-45,35):
        for y in (-15,15):
            part += Pos(x,y,-1) * Cylinder(4,12)
            part -= Pos(x,y,-1) * Cylinder(1.6,14)
    return part

def electronics_tray():
    p = Pos(-5,0,-7) * Box(124,52,3)
    for x in (-45,35):
        for y in (-15,15):
            p -= Pos(x,y,-7) * Cylinder(1.6,6)
    return p

def head_module():
    # Long tapered skull assembled from overlapping profile sections, then cheek/brow armor.
    skull = Pos(-14,0,0) * Box(56,43,32)
    skull += Pos(14,0,-5) * Box(34,30,22)
    skull += Pos(31,0,-8) * Box(24,22,13)
    skull += Pos(-29,0,5) * Box(24,36,26)
    # camera / sensor aperture in front snout
    skull -= Pos(42,0,-5) * Cylinder(7,30, rotation=(0,90,0))
    # horn and crown armor swept along z
    for side in (-1,1):
        skull += Pos(-28,side*17,21) * Rot(Y=-24) * Cone(8,3,23)
        skull += Pos(-5,side*17,18) * Rot(Y=-20) * Cone(6,2,17)
        skull += Pos(8,side*15,4) * Rot(Y=12) * Box(25,7,7)
        skull += Pos(-12,side*19,-4) * Rot(Z=side*12) * Box(28,7,10)
    skull += Pos(-22,0,24) * Rot(Y=-18) * Cone(5,1.5,15)
    # mounting flange and 4 bolt holes
    skull += Pos(-42,0,-4) * Box(12,34,8)
    for y in (-12,12):
        for z in (-6,0):
            skull -= Pos(-42,y,z) * Rot(Y=90) * Cylinder(M3/2,16)
    return skull

def dorsal_armor():
    p = Pos(0,0,0) * Box(126,26,8)
    # alternating raised center blades and outward swept side blades
    for i,x in enumerate(range(-54,55,18)):
        height = 25 if i%2==0 else 19
        p += Pos(x,0,8+height/2) * Rot(Y=-18) * Cone(7,1.8,height)
        for side in (-1,1):
            p += Pos(x-3,side*11,11) * Rot(X=side*25,Y=-25) * Cone(5.2,1.5,18)
        # recessed fastening points
        p -= Pos(x,0,0) * Cylinder(M3/2,14)
    return p

def tail_module():
    # Five distinct interlocking tapered tail links; each link exported independently
    # and also assembled as a single visual reference.
    links=[]
    radii=[12,10,8.2,6.3,4.5]
    lengths=[24,22,20,18,16]
    x=-95
    for i,(r,l) in enumerate(zip(radii,lengths)):
        link = Pos(x-l/2,0,0) * Cone(r,r*.78,l, rotation=(0,90,0))
        # central bolt passage along the tail axis
        link -= Pos(x-l/2,0,0) * Rot(Y=90) * Cylinder(2.2,l+2)
        for side in (-1,1):
            link += Pos(x-l/2,side*r*.75,r*.45) * Rot(X=side*25) * Cone(r*.35,1.0,l*.48)
        links.append(link)
        x -= l*.82
    return links

def coxa_housing():
    p = Box(40,30,28)
    p -= Pos(0,0,0) * Box(34,24,22)
    for y in (-10,10):
        p -= Pos(0,y,0) * Cylinder(M3/2,32)
    # bearing seat nominal OD 16 mm, 5 mm deep; tune press fit after printer calibration
    p -= Pos(0,0,8) * Cylinder(7.9,5)
    p -= Pos(0,0,-8) * Cylinder(4,32)
    return p

def leg_armor(length, width, height):
    shell = Box(length,width,height) - Box(length-2*WALL,width-2*WALL,height-2*WALL)
    shell += Pos(length*.22,0,0) * Box(length*.25,width+2, height*.65)
    return shell

def export_all():
    export(upper_body(),"PRINT_body_upper_v6")
    export(lower_body(),"PRINT_body_lower_v6")
    export(upper_body()+lower_body(),"ASSEMBLY_body_closed_preview_v6")
    export(electronics_tray(),"PRINT_electronics_tray_v6")
    export(head_module(),"PRINT_head_complete_v6")
    export(dorsal_armor(),"PRINT_dorsal_spines_complete_v6")
    export(coxa_housing(),"PRINT_coxa_housing_v6")
    export(leg_armor(COXA,22,24),"PRINT_coxa_armor_v6")
    export(leg_armor(FEMUR,25,28),"PRINT_femur_armor_v6")
    export(leg_armor(TIBIA,22,24),"PRINT_tibia_armor_v6")
    links=tail_module()
    for i,link in enumerate(links,1):
        export(link,f"PRINT_tail_link_{i:02d}_v6")
    assembled=links[0]
    for link in links[1:]:
        assembled += link
    export(assembled,"ASSEMBLY_tail_preview_v6")
    print("Exported V6 parts to", OUT.resolve())
    print("IMPORTANT: run mesh checks and fit tests before printing functional parts.")

if __name__ == "__main__":
    export_all()
