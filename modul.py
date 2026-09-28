from build123d import *
from pathlib import Path
import math

OUT = Path("out")
OUT.mkdir(exist_ok=True)

# ============================================================
# XZORT RESCUE QUADRUPED — MECHANICAL DRAGON ARMOR — 12 DOF
# Independent dragon armor modules for printable STL/STEP.
# ============================================================

def safe_fillet(shape, radius):
    try:
        return fillet(shape.edges(), radius)
    except Exception:
        return shape

def rounded_box(x, y, z, r=4):
    s = Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return safe_fillet(s, min(r, x/2-0.2, y/2-0.2, z/2-0.2))

def cylinder_x(radius, length):
    return Cylinder(radius, length, rotation=(0, 90, 0),
                   align=(Align.CENTER, Align.CENTER, Align.MIN))

def cylinder_z(radius, length):
    return Cylinder(radius, length, align=(Align.CENTER, Align.CENTER, Align.MIN))

def flat_fin(points, thickness=4):
    wire = Polyline([(x, 0, z) for x, z in points], close=True)
    return extrude(Face(wire), amount=thickness, dir=(0, 1, 0))

def dragon_scale(width=32, height=24, thickness=5):
    p = [(-width*.5,0),(-width*.25,height*.72),(0,height),
         (width*.25,height*.72),(width*.5,0),(0,-height*.22)]
    wire = Polyline([(x,0,z) for x,z in p], close=True)
    return extrude(Face(wire), amount=thickness, dir=(0,1,0))

def joint_core(radius=22, width=30):
    s = cylinder_x(radius, width)
    try:
        s = s.cut(cylinder_x(7, width+10).translate((-5,0,0)))
    except Exception:
        pass
    return s

def joint_armor_cover(radius=29, width=36):
    outer = cylinder_x(radius, width)
    try:
        shell = outer.cut(cylinder_x(radius-7, width+8))
    except Exception:
        shell = outer
    ridge = rounded_box(width*.72, radius*1.35, 8, 3).translate(
        (width*.12, 0, radius*.72))
    shell = shell.fuse(ridge)
    for y in (-radius*.62, radius*.62):
        shell = shell.fuse(dragon_scale(width*.55, radius*.62, 4).translate(
            (0,y,radius*.15)))
    return shell

def triangular_link(length, width, height):
    outer = [(0,0),(length*.30,height),(length*.72,height*.78),
             (length,0),(length*.72,-height*.78),(length*.30,-height)]
    wire = Polyline([(x,-width/2,z) for x,z in outer], close=True)
    return extrude(Face(wire), amount=width, dir=(0,1,0))

def leg_link_armor(length, width, height):
    shell = triangular_link(length,width,height)
    try:
        recess = rounded_box(length*.56,width*.60,height*.48,4).translate(
            (length*.50,0,0))
        shell = shell.cut(recess)
    except Exception:
        pass
    spine = rounded_box(length*.65,width*.18,height*.12,2).translate(
        (length*.50,0,height*.45))
    shell = shell.fuse(spine)
    for i in range(3):
        x = length*(.22+i*.27)
        shell = shell.fuse(dragon_scale(width*.65,height*.55,3).translate(
            (x,width*.52,0)))
    return shell

def coxa_module():
    core = joint_core(24,34)
    arm = rounded_box(52,42,34,8).translate((26,0,0))
    shaft = cylinder_z(8,48).translate((0,0,-24))
    return core.fuse(arm).fuse(shaft)

def coxa_armor():
    cover = joint_armor_cover(31,40)
    shoulder = dragon_scale(54,42,5).translate((15,0,24))
    return cover.fuse(shoulder)

def femur_module():
    L=125
    return (triangular_link(L,34,20)
            .fuse(joint_core(20,32))
            .fuse(joint_core(20,32).translate((L,0,0))))

def femur_armor():
    L=125
    armor = leg_link_armor(L,40,25)
    fin = flat_fin([(15,20),(45,44),(78,31),(110,18),(125,0),
                    (90,7),(50,12)],4)
    return armor.fuse(fin)

def tibia_module():
    L=145
    return (triangular_link(L,30,18)
            .fuse(joint_core(19,30))
            .fuse(joint_core(17,28).translate((L,0,0))))

def tibia_armor():
    L=145
    armor = leg_link_armor(L,36,22)
    fin = flat_fin([(10,15),(42,35),(78,28),(112,17),(145,0),
                    (110,4),(65,9)],4)
    return armor.fuse(fin)

def dragon_claw():
    base = rounded_box(52,42,12,5)
    for y in (-14,0,14):
        claw = rounded_box(38,8,9,3).translate((30,y,-2))
        tip = Cone(7,2,22,rotation=(0,90,0),
                   align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((48,y,-2))
        base = base.fuse(claw).fuse(tip)
    return base

def chassis():
    return (rounded_box(300,170,72,24)
            .fuse(rounded_box(250,130,36,15).translate((15,0,-42)))
            .fuse(rounded_box(220,115,28,12).translate((-10,0,48))))

def body_dragon_scales():
    result=[]
    for row in range(3):
        for i in range(9):
            x=-105+i*27
            result.append(dragon_scale(34-row*3,25-row*2,5).translate(
                (x,(row-1)*52,39-row*13)))
    return result

def dorsal_spines():
    result=None
    for i in range(9):
        x=-110+i*28
        h=25+10*math.sin(i/8*math.pi)
        s=Cone(13,2,h,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((x,0,42))
        result=s if result is None else result.fuse(s)
    return result

def dragon_head():
    head=(rounded_box(105,95,72,22).translate((-175,0,42))
          .fuse(rounded_box(70,82,45,15).translate((-215,0,72)))
          .fuse(rounded_box(78,72,42,14).translate((-245,0,30)))
          .fuse(rounded_box(70,68,18,7).translate((-250,0,7)))
          .fuse(rounded_box(65,62,16,7).translate((-246,0,-8))))
    for y in (-35,35):
        head=head.cut(Sphere(15).translate((-210,y,66)))
        head=head.fuse(Sphere(7).translate((-213,y,66)))
    for y in (-52,52):
        head=head.fuse(dragon_scale(48,38,6).translate((-208,y,36)))
    for y,d in [(-36,-1),(36,1)]:
        horn=Cone(18,4,58,align=(Align.CENTER,Align.CENTER,Align.MIN))
        horn=horn.rotate(Axis.Y,-d*18).translate((-192,y,85))
        head=head.fuse(horn)
    for y in (-20,20):
        head=head.fuse(rounded_box(28,12,16,4).translate((-285,y,38)))
    for y in (-23,-8,8,23):
        head=head.fuse(Cone(6,1,15,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate(
            (-278,y,3)))
    return head

def neck_assembly():
    result=None
    for i,x in enumerate((-145,-128,-111)):
        r=35-i*3
        core=cylinder_x(r,28).translate((x,0,42))
        armor=joint_armor_cover(r+7,34).translate((x,0,42))
        part=core.fuse(armor)
        result=part if result is None else result.fuse(part)
    return result

def body_fins():
    pts=[(-105,40),(-80,85),(-45,57),(-10,78),(25,48),(60,68),
         (105,38),(55,30),(-20,32)]
    return flat_fin(pts,4), flat_fin(pts,4)

def tail_segment(index):
    length=max(26,52-index*4)
    radius=max(7,22-index*1.5)
    core=cylinder_x(radius,length)
    cover=joint_armor_cover(radius+5,length+4)
    spine=Cone(radius*.8,2,20+max(0,10-index),
               align=(Align.CENTER,Align.CENTER,Align.MIN)).translate(
               (length*.5,0,radius))
    return core.fuse(cover).fuse(spine)

def dragon_tail():
    result=None
    x=145
    for i in range(8):
        seg=tail_segment(i).rotate(Axis.Y,-i*4).translate((x,0,18-i*3))
        result=seg if result is None else result.fuse(seg)
        x+=max(26,52-i*4)
    return result

LEG_POSITIONS={"FL":(-100,-82,-15),"FR":(-100,82,-15),
               "RL":(100,-82,-15),"RR":(100,82,-15)}

def make_leg(name,x,y,z,side):
    parts=[]
    coxa=coxa_module().rotate(Axis.Z,-18 if side>0 else 18).translate((x,y,z))
    parts.append((f"{name}_coxa",coxa))
    parts.append((f"{name}_coxa_armor",coxa_armor().translate((x,y,z))))

    fy=y+side*40
    femur_origin=(x,fy,z)
    parts.append((f"{name}_femur",femur_module().translate(femur_origin)))
    parts.append((f"{name}_femur_armor",femur_armor().translate(femur_origin)))

    knee_x=x+125
    knee_z=z-12
    tibia_origin=(knee_x,fy,knee_z)
    parts.append((f"{name}_tibia",tibia_module().translate(tibia_origin)))
    parts.append((f"{name}_tibia_armor",tibia_armor().translate(tibia_origin)))

    foot=dragon_claw().translate((knee_x+145,fy,knee_z-15))
    parts.append((f"{name}_foot",foot))
    return parts

def assembly():
    components=[("body",chassis())]
    for i,s in enumerate(body_dragon_scales()):
        components.append((f"body_scale_{i:02d}",s))
    components += [("dorsal_spines",dorsal_spines()),
                   ("dragon_head",dragon_head()),
                   ("neck_armor",neck_assembly())]
    left,right=body_fins()
    components += [("dragon_fin_left",left.translate((0,-72,0))),
                   ("dragon_fin_right",right.translate((0,68,0))),
                   ("dragon_tail",dragon_tail())]
    for name,(x,y,z) in LEG_POSITIONS.items():
        components.extend(make_leg(name,x,y,z,-1 if y<0 else 1))
    return components

def export_component(name,shape):
    export_stl(shape,str(OUT/f"{name}.stl"))
    export_step(shape,str(OUT/f"{name}.step"))
    print(f"[OK] {name}")

def build_preview(components):
    preview=None
    for _,shape in components:
        preview=shape if preview is None else preview.fuse(shape)
    return preview

if __name__=="__main__":
    print("="*64)
    print("XZORT RESCUE QUADRUPED — MECHANICAL DRAGON ARMOR")
    print("12 DOF / MODULAR STL + STEP")
    print("="*64)
    components=assembly()
    print(f"[INFO] Components: {len(components)}")
    for name,shape in components:
        export_component(name,shape)
    print("[INFO] Building full preview...")
    preview=build_preview(components)
    export_stl(preview,str(OUT/"dragon_spider_full.stl"))
    export_step(preview,str(OUT/"dragon_spider_full.step"))
    print(f"[DONE] Output: {OUT.resolve()}")
