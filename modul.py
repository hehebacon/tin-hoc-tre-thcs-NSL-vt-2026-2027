from build123d import *
from pathlib import Path
import math

OUT = Path("out")
OUT.mkdir(exist_ok=True)

# ============================================================
# XZORT RESCUE BEAST — 80 cm / 12 DOF / NO WINGS
#
# Design hierarchy:
#   SERVO/JOINING SKELETON -> BEAST BODY -> DRAGON SCALE ARMOR
#
# Main target proportions:
#   body: 500 L x 200 W x ~500 H overall envelope
#   head: large, ~2/3 body visual mass
#   4 legs x 3 servo DOF = 12 servos
#   1 = outer/lower segment + shield
#   2 = middle segment
#   3 = body-mounted/root segment
#
# PRINT_* = intended physical modules
# REF_*   = assembly/reference only, never print
# ============================================================

def fillet_safe(s, r):
    try:
        return fillet(s.edges(), r)
    except Exception:
        return s

def box(x, y, z, r=0):
    s = Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return fillet_safe(s, r) if r else s

def cyl_x(r, l):
    return Cylinder(r, l, rotation=(0, 90, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

def cyl_z(r, l):
    return Cylinder(r, l, align=(Align.CENTER, Align.CENTER, Align.MIN))

def scale_plate(w=42, h=32, t=5):
    pts = [(-w/2,0), (-w*.28,h*.68), (0,h), (w*.28,h*.68),
           (w/2,0), (0,-h*.18)]
    wire = Polyline([(x,0,z) for x,z in pts], close=True)
    return extrude(Face(wire), amount=t, dir=(0,1,0))

def triangular_beam(length, width, height):
    pts = [(0,0), (length*.18,height), (length*.50,height*.72),
           (length,0), (length*.50,-height*.72), (length*.18,-height)]
    wire = Polyline([(x,-width/2,z) for x,z in pts], close=True)
    return extrude(Face(wire), amount=width, dir=(0,1,0))

# ------------------------------------------------------------
# BODY — organic / large / hollow, NOT a simple box
# ------------------------------------------------------------

def body_shell():
    # Three overlapping rounded masses create an organic beast torso.
    core = box(330, 200, 150, 58)
    shoulder = box(185, 188, 175, 55).translate((-112,0,8))
    rear = box(175, 178, 165, 52).translate((105,0,4))
    outer = core.fuse(shoulder).fuse(rear)

    # Large internal cavity: leave thick outer armor.
    cavity = box(278, 142, 112, 42).translate((12,0,-10))
    shell = outer.cut(cavity)

    # Open underside access, but retain side structure.
    access = box(250, 128, 35, 28).translate((15,0,-70))
    shell = shell.cut(access)

    # Four structural root pods for the body-mounted servo (#3).
    for x in (-112, 108):
        for y in (-91, 91):
            pod = cyl_z(31, 42).translate((x,y,-52))
            bore = cyl_z(18, 50).translate((x,y,-56))
            shell = shell.fuse(pod.cut(bore))

    return shell

def body_lower_cover():
    cover = box(255, 132, 9, 12).translate((12,0,-75))
    for x in (-105,105):
        for y in (-52,52):
            cover = cover.cut(cyl_z(4,18).translate((x,y,-82)))
    return cover

# ------------------------------------------------------------
# ELECTRONICS BAY
# ------------------------------------------------------------

def electronics_tray():
    tray = box(252, 126, 8, 10).translate((12,0,-42))
    for x,y in [(-96,-42),(-32,-42),(32,-42),(96,-42),
                (-96,42),(-32,42),(32,42),(96,42)]:
        tray = tray.cut(cyl_z(3,18).translate((x,y,-51)))
    return tray

def electronics_rail():
    rail = box(225, 12, 18, 4).translate((12,0,-30))
    return rail.cut(box(190,7,12,2).translate((12,0,-30)))

def electronics_standoffs():
    out=[]
    for i,(x,y) in enumerate([(-105,-48),(-35,-48),(35,-48),(105,-48),
                               (-105,48),(-35,48),(35,48),(105,48)]):
        s = cyl_z(8,22).translate((x+12,y,-29))
        s = s.cut(cyl_z(3,28).translate((x+12,y,-33)))
        out.append((f"electronics_standoff_{i+1:02d}",s))
    return out

# ------------------------------------------------------------
# TOP SCREEN — recessed, protected by armor
# ------------------------------------------------------------

def screen_frame():
    outer = box(126,82,12,10).translate((30,0,88))
    opening = box(102,58,18,7).translate((30,0,88))
    frame = outer.cut(opening)
    for x in (-23,83):
        for y in (-34,34):
            frame = frame.fuse(cyl_z(8,12).translate((x,y,82)).cut(
                cyl_z(3,18).translate((x,y,79))))
    return frame

def screen_mount():
    return box(106,62,5,6).translate((30,0,77))

def screen_hood():
    # Raised rear hood protects the display without becoming a wing.
    hood = box(116,16,28,6).translate((35,37,91))
    return hood.cut(box(96,9,20,3).translate((35,37,91)))

# ------------------------------------------------------------
# DRAGON SCALES — layered armor, no fins/wings
# ------------------------------------------------------------

def body_scale_set():
    parts=[]
    n=0
    # Dense overlapping scale rows on top and side armor.
    for row in range(5):
        z=48 + row*22
        for i in range(13):
            x=-150+i*25
            offset=12 if row%2 else 0
            s=scale_plate(40,28,5).translate((x+offset,0,z))
            parts.append((f"body_scale_{n:03d}",s))
            n+=1

    # Side scale armor panels.
    for side in (-1,1):
        for row in range(4):
            for i in range(9):
                x=-125+i*30
                z=-8+row*27
                s=scale_plate(36,25,5).rotate(Axis.X,90)
                s=s.translate((x,side*99,z))
                parts.append((f"side_scale_{n:03d}",s))
                n+=1
    return parts

def dorsal_scales():
    parts=[]
    for i in range(11):
        x=-150+i*30
        h=18+10*math.sin(i/10*math.pi)
        s=Cone(15,3,h,align=(Align.CENTER,Align.CENTER,Align.MIN))
        parts.append((f"dorsal_scale_{i+1:02d}",s.translate((x,0,112))))
    return parts

# ------------------------------------------------------------
# HEAD — large beast/dragon head, no wings
# ------------------------------------------------------------

def dragon_head():
    # Large head mass: deliberately NOT a tiny dragon head attached to a spider.
    cranium=box(150,132,132,42).translate((-210,0,92))
    cheek=box(108,145,95,30).translate((-250,0,58))
    muzzle=box(125,102,65,24).translate((-315,0,58))
    jaw=box(105,94,25,10).translate((-320,0,20))
    head=cranium.fuse(cheek).fuse(muzzle).fuse(jaw)

    # Deep eye sockets.
    for y in (-52,52):
        socket=Sphere(22).translate((-248,y,108))
        head=head.cut(socket)

    # Brow armor.
    for y in (-54,54):
        brow=scale_plate(62,38,7).rotate(Axis.X,90)
        head=head.fuse(brow.translate((-250,y,103)))

    # Horns: backward/upward, not wings.
    for y in (-47,47):
        horn=Cone(22,5,68,align=(Align.CENTER,Align.CENTER,Align.MIN))
        horn=horn.rotate(Axis.Y, -18 if y<0 else 18)
        head=head.fuse(horn.translate((-192,y,145)))

    # Cheek scale plates.
    for y in (-70,70):
        for i in range(3):
            s=scale_plate(48,35,6).rotate(Axis.X,90)
            head=head.fuse(s.translate((-235+i*22,y,58+i*10)))

    # Mouth/nose armor.
    for y in (-31,31):
        head=head.fuse(box(38,14,16,4).translate((-360,y,62)))

    # Four small lower teeth.
    for y in (-30,-10,10,30):
        tooth=Cone(7,2,19,align=(Align.CENTER,Align.CENTER,Align.MIN))
        head=head.fuse(tooth.translate((-353,y,8)))
    return head

# ------------------------------------------------------------
# HEAD WEAPON / SENSOR MOUNT
# ------------------------------------------------------------

def head_weapon_mount():
    base=box(52,48,24,8).translate((-374,0,72))
    barrel=cyl_x(11,82).translate((-400,-11,72))
    shroud=box(72,34,34,10).translate((-365,0,72))
    return base.fuse(barrel).fuse(shroud)

# ------------------------------------------------------------
# NECK — 3 armor rings, no wings
# ------------------------------------------------------------

def neck_module():
    parts=[]
    for i,x in enumerate([-132,-105,-78]):
        r=42-i*3
        core=cyl_x(r,30).translate((x,0,65))
        armor=cyl_x(r+8,34).translate((x,0,65))
        parts.append((f"neck_ring_{i+1}",core.fuse(armor)))
    return parts

# ------------------------------------------------------------
# LEGS — 4 legs x 3 DOF = 12 servos
#
# Segment 3 = body/root
# Segment 2 = middle
# Segment 1 = outer/lower, WITH SHIELD
# ------------------------------------------------------------

SERVO_R=18
SERVO_W=36

def servo_housing():
    body=box(48,44,42,10)
    motor=cyl_x(SERVO_R,SERVO_W).translate((-18,0,0))
    shaft=cyl_x(7,50).translate((-24,0,0))
    return body.fuse(motor).fuse(shaft)

def joint_shield():
    # Shield wraps around the outer/lower segment.
    outer=box(92,58,72,18)
    inner=box(66,48,48,13)
    shield=outer.cut(inner)
    ridge=box(74,12,58,5).translate((0,27,0))
    return shield.fuse(ridge)

def leg_segment_3():
    # Root segment, directly attached to body.
    beam=triangular_beam(92,42,24)
    servo=servo_housing().translate((0,0,0))
    return beam.fuse(servo)

def leg_segment_2():
    L=118
    beam=triangular_beam(L,38,25)
    # Nested triangular relief.
    relief=triangular_beam(L*.62,24,14).translate((25,0,0))
    return beam.cut(relief)

def leg_segment_1():
    L=112
    beam=triangular_beam(L,36,23)
    shield=joint_shield().translate((52,0,0))
    return beam.fuse(shield)

def leg_foot():
    foot=box(72,48,20,9)
    for y in (-15,0,15):
        toe=box(42,9,13,4).translate((28,y,-4))
        tip=Cone(6,2,18,rotation=(0,90,0),
                 align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((47,y,-4))
        foot=foot.fuse(toe).fuse(tip)
    return foot

LEG_POS={
    "FL":(-112,-92,-45),
    "FR":(-112,92,-45),
    "RL":(108,-92,-45),
    "RR":(108,92,-45)
}

def make_leg(name,x,y,z):
    side=-1 if y<0 else 1
    out=[]
    # Servo #3: hidden in the body/root armor.
    out.append((f"{name}_SERVO_3",servo_housing().translate((x,y,z))))
    out.append((f"{name}_SEGMENT_3",leg_segment_3().translate((x,y,z))))

    # Segment 2.
    p2=(x+92,y+side*15,z-32)
    out.append((f"{name}_SERVO_2",servo_housing().translate(p2)))
    out.append((f"{name}_SEGMENT_2",leg_segment_2().translate(p2)))

    # Segment 1 + shield.
    p1=(x+210,y+side*22,z-75)
    out.append((f"{name}_SERVO_1",servo_housing().translate(p1)))
    out.append((f"{name}_SEGMENT_1_SHIELD",leg_segment_1().translate(p1)))

    out.append((f"{name}_FOOT",leg_foot().translate(
        (p1[0]+112,p1[1],p1[2]-28))))
    return out

# ------------------------------------------------------------
# TAIL — segmented, tapered, articulated-looking
# ------------------------------------------------------------

def tail_segment(i):
    length=max(34,58-i*3)
    r=max(8,23-i*1.4)
    core=cyl_x(r,length)
    armor=cyl_x(r+6,length+6)
    cap=Sphere(r+6).translate((length,0,0))
    scale=scale_plate(max(24,r*1.8),max(18,r*1.25),5).translate(
        (length*.45,0,r+4))
    return core.fuse(armor).fuse(cap).fuse(scale)

def dragon_tail():
    out=[]
    x=250
    z=20
    for i in range(10):
        yaw=-5*i
        seg=tail_segment(i).rotate(Axis.Y,yaw)
        seg=seg.translate((x,0,z))
        out.append((f"tail_segment_{i+1:02d}",seg))
        x += max(34,58-i*3)
        z += 7
    return out

# ------------------------------------------------------------
# REFERENCE ASSEMBLY
# ------------------------------------------------------------

def all_components():
    c=[
        ("body_shell",body_shell()),
        ("body_lower_cover",body_lower_cover()),
        ("electronics_tray",electronics_tray()),
        ("electronics_rail",electronics_rail()),
        ("screen_frame",screen_frame()),
        ("screen_mount",screen_mount()),
        ("screen_hood",screen_hood()),
        ("dragon_head",dragon_head()),
        ("head_weapon_mount",head_weapon_mount()),
    ]
    c += body_scale_set()
    c += dorsal_scales()
    c += neck_module()
    c += electronics_standoffs()
    c += dragon_tail()
    for name,pos in LEG_POS.items():
        c += make_leg(name,*pos)
    return c

def printable_components():
    # Every physical module is separate. No wing/fin parts exist.
    return all_components()

def export_pair(prefix,name,shape):
    export_stl(shape,str(OUT/f"{prefix}_{name}.stl"))
    export_step(shape,str(OUT/f"{prefix}_{name}.step"))
    print(f"[OK] {prefix}_{name}")

def fuse_all(parts):
    result=None
    for _,s in parts:
        result=s if result is None else result.fuse(s)
    return result

def manifest(parts):
    lines=[
        "XZORT RESCUE BEAST — PRINT MANIFEST",
        "="*68,
        "",
        "PRINT_* = intended physical print module",
        "REF_*   = visual assembly only / DO NOT PRINT",
        "",
        "DESIGN LOCKS:",
        "  4 legs / 12 servos total / 3 servos per leg",
        "  Leg segment 3 = body-mounted root",
        "  Leg segment 2 = middle",
        "  Leg segment 1 = outer/lower + SHIELD",
        "  Dragon scales cover body/head/legs/tail",
        "  NO WINGS / NO WING FIN PARTS",
        "  Large internal electronics bay + removable tray",
        "  Recessed top screen mount",
        "  Large beast-like head + front weapon mount",
        "  Segmented tapered tail",
        "",
        "MODULES:",
    ]
    for n,_ in parts:
        lines.append(f"  PRINT_{n}.stl / PRINT_{n}.step")
    lines += [
        "",
        "REFERENCE:",
        "  REF_full_assembly.stl / REF_full_assembly.step",
        "",
        "Before fabrication, verify the actual servo, battery, PCB,",
        "screen and fastener dimensions against the hardware.",
    ]
    (OUT/"PRINT_MANIFEST.txt").write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    print("="*72)
    print("XZORT RESCUE BEAST — 80cm / 12 DOF / NO WINGS")
    print("DRAGON SCALE ARMOR + LARGE BEAST HEAD + MODULAR LEGS")
    print("="*72)

    parts=printable_components()
    print(f"[INFO] Printable modules: {len(parts)}")

    for name,shape in parts:
        export_pair("PRINT",name,shape)

    assembly=fuse_all(parts)
    export_pair("REF","full_assembly",assembly)
    manifest(parts)

    print(f"[DONE] Output: {OUT.resolve()}")
    print("[DONE] PRINT_* = print")
    print("[DONE] REF_*   = reference only")
