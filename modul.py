from build123d import *
from pathlib import Path
import math

OUT = Path("out")
OUT.mkdir(exist_ok=True)

# ============================================================
# XZORT RESCUE QUADRUPED — 80 cm TOY-LIKE MECHANICAL DRAGON
# PRINT-READY MODULAR CAD
#
# Output convention:
#   PRINT_*.stl / PRINT_*.step = parts intended for 3D printing
#   REF_*.stl  / REF_*.step  = assembly/reference only, do NOT print
#   PRINT_MANIFEST.txt        = complete print/reference list
#
# The body is intentionally rounded/bulged and hollow, with:
#   - large internal electronics bay
#   - removable electronics tray
#   - top display cavity + bezel
#   - cable channels / mounting bosses
#   - separate dragon armor scales
#   - separate joint covers
#   - separate sharp triangular leg armor
#   - segmented articulated-looking dragon tail
# ============================================================

def safe_fillet(shape, radius):
    try:
        return fillet(shape.edges(), radius)
    except Exception:
        return shape

def rounded_box(x, y, z, r=6):
    r = max(0.5, min(r, x/2-0.2, y/2-0.2, z/2-0.2))
    return safe_fillet(Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.CENTER)), r)

def cyl_x(radius, length):
    return Cylinder(radius, length, rotation=(0, 90, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

def cyl_z(radius, length):
    return Cylinder(radius, length, align=(Align.CENTER, Align.CENTER, Align.MIN))

def dragon_scale(width=32, height=24, thickness=5):
    p = [(-width*.5, 0), (-width*.24, height*.72), (0, height),
         (width*.24, height*.72), (width*.5, 0), (0, -height*.22)]
    wire = Polyline([(x, 0, z) for x, z in p], close=True)
    return extrude(Face(wire), amount=thickness, dir=(0, 1, 0))

def flat_fin(points, thickness=4):
    wire = Polyline([(x, 0, z) for x, z in points], close=True)
    return extrude(Face(wire), amount=thickness, dir=(0, 1, 0))

def triangular_link(length, width, height):
    p = [(0,0), (length*.25,height), (length*.72,height*.72),
         (length,0), (length*.72,-height*.72), (length*.25,-height)]
    wire = Polyline([(x, -width/2, z) for x,z in p], close=True)
    return extrude(Face(wire), amount=width, dir=(0,1,0))

def joint_core(radius=22, width=30):
    s = cyl_x(radius, width)
    try:
        s = s.cut(cyl_x(7, width+10).translate((-5,0,0)))
    except Exception:
        pass
    return s

def joint_armor_cover(radius=29, width=36):
    # Decorative outer cap; the central bore is retained.
    outer = cyl_x(radius, width)
    try:
        shell = outer.cut(cyl_x(radius-7, width+8))
    except Exception:
        shell = outer
    crown = rounded_box(width*.75, radius*1.30, 8, 3).translate(
        (width*.10, 0, radius*.68))
    shell = shell.fuse(crown)
    return shell

def leg_link_armor(length, width, height):
    shell = triangular_link(length, width, height)
    # Recess makes the "two triangles nested together" look.
    try:
        recess = rounded_box(length*.56, width*.58, height*.46, 5).translate(
            (length*.50, 0, 0))
        shell = shell.cut(recess)
    except Exception:
        pass
    spine = rounded_box(length*.68, width*.16, height*.13, 2).translate(
        (length*.50, 0, height*.45))
    shell = shell.fuse(spine)
    for i in range(3):
        x = length*(.20 + i*.28)
        shell = shell.fuse(
            dragon_scale(width*.60, height*.50, 3).translate((x, width*.52, 0))
        )
    return shell

# ------------------------------------------------------------
# BODY: large, rounded, toy-like and HOLLOW
# ------------------------------------------------------------

def body_shell():
    # Bulged outer body. Bigger than the previous boxy version.
    outer = rounded_box(330, 205, 92, 34)

    # Large underside-open electronics cavity.
    inner = rounded_box(292, 165, 70, 28).translate((0, 0, -16))
    shell = outer.cut(inner)

    # Front/head transition makes the silhouette less like a plain box.
    nose_bulge = rounded_box(115, 170, 55, 25).translate((-128, 0, 15))
    shell = shell.fuse(nose_bulge.cut(
        rounded_box(92, 138, 43, 20).translate((-128, 0, 15))
    ))

    # Rear battery hump.
    rear_hump = rounded_box(125, 155, 42, 20).translate((105, 0, 38))
    shell = shell.fuse(rear_hump)

    # Four thick motor/leg mounting bosses.
    for x in (-108, 108):
        for y in (-82, 82):
            boss = cyl_z(25, 25).translate((x, y, -4))
            bore = cyl_z(9, 32).translate((x, y, -7))
            shell = shell.fuse(boss.cut(bore))

    return shell

def body_bottom_guard():
    # Removable lower guard; keeps the electronics bay accessible.
    plate = rounded_box(292, 165, 8, 14).translate((0,0,-48))
    for x in (-105, 105):
        for y in (-58, 58):
            plate = plate.cut(cyl_z(8, 18).translate((x,y,-56)))
    return plate

def electronics_tray():
    # Separate printable tray sitting inside the hollow body.
    tray = rounded_box(255, 132, 8, 10).translate((0,0,-30))
    # Controller / power / PCA mounting holes.
    for x,y in [(-82,-40),(-82,40),(0,-40),(0,40),(82,-40),(82,40)]:
        tray = tray.cut(cyl_z(3, 16).translate((x,y,-38)))
    # Cable pass-through slots.
    for x in (-112,112):
        tray = tray.cut(rounded_box(20, 12, 16, 4).translate((x,0,-30)))
    return tray

def electronics_standoffs():
    parts=[]
    for i,(x,y) in enumerate([(-105,-58),(-105,58),(105,-58),(105,58),
                               (-35,-58),(35,-58)]):
        p = cyl_z(8, 22).translate((x,y,-20))
        p = p.cut(cyl_z(3, 30).translate((x,y,-24)))
        parts.append((f"body_standoff_{i:02d}", p))
    return parts

# ------------------------------------------------------------
# TOP DISPLAY BAY
# ------------------------------------------------------------

def display_bezel():
    # Large top opening sized as a generic modular display bay.
    outer = rounded_box(122, 76, 10, 12).translate((25, 0, 51))
    opening = rounded_box(100, 54, 16, 8).translate((25, 0, 51))
    frame = outer.cut(opening)

    # Four screw ears around the screen.
    for x in (25-57, 25+57):
        for y in (-38, 38):
            ear = cyl_z(9, 10).translate((x,y,51))
            ear = ear.cut(cyl_z(3, 16).translate((x,y,48)))
            frame = frame.fuse(ear)
    return frame

def display_mount_plate():
    plate = rounded_box(126, 80, 6, 10).translate((25,0,43))
    opening = rounded_box(100,54,12,8).translate((25,0,43))
    plate = plate.cut(opening)
    return plate

def display_cable_tunnel():
    # Small printed channel below the display for ribbon/power cables.
    return rounded_box(78, 18, 12, 5).translate((25,0,34)).cut(
        rounded_box(66, 10, 14, 3).translate((25,0,34))
    )

# ------------------------------------------------------------
# DRAGON BODY ARMOR
# ------------------------------------------------------------

def body_scales():
    parts=[]
    idx=0
    for row in range(3):
        for i in range(11):
            x=-132+i*26.4
            y=-86 + row*43
            z=40 + (1-abs(i-5)/5)*5 - row*2
            s=dragon_scale(38-row*3, 28-row*2, 5).translate((x,y,z))
            parts.append((f"body_scale_{idx:02d}",s))
            idx+=1
    return parts

def dorsal_spines():
    result=None
    for i in range(9):
        x=-112+i*28
        h=25+10*math.sin(i/8*math.pi)
        s=Cone(13,2,h,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((x,0,48))
        result=s if result is None else result.fuse(s)
    return result

# ------------------------------------------------------------
# DRAGON HEAD
# ------------------------------------------------------------

def dragon_head():
    head = rounded_box(112, 100, 78, 24).translate((-178,0,54))
    brow = rounded_box(78, 86, 48, 16).translate((-215,0,82))
    snout = rounded_box(92, 78, 46, 15).translate((-250,0,42))
    jaw = rounded_box(80, 72, 18, 7).translate((-252,0,8))
    head = head.fuse(brow).fuse(snout).fuse(jaw)

    # Eye recesses.
    for y in (-39,39):
        head = head.cut(Sphere(17).translate((-211,y,77)))

    # Cheek armor plates.
    for y in (-53,53):
        head = head.fuse(dragon_scale(54,42,6).translate((-218,y,42)))

    # Horns.
    for y,d in [(-38,-1),(38,1)]:
        horn=Cone(19,4,62,align=(Align.CENTER,Align.CENTER,Align.MIN))
        horn=horn.rotate(Axis.Y,-d*18).translate((-190,y,96))
        head=head.fuse(horn)

    # Nose armor + teeth.
    for y in (-23,23):
        head=head.fuse(rounded_box(28,12,17,4).translate((-289,y,40)))
    for y in (-25,-9,9,25):
        tooth=Cone(6,1,17,align=(Align.CENTER,Align.CENTER,Align.MIN))
        head=head.fuse(tooth.translate((-283,y,0)))

    return head

# ------------------------------------------------------------
# LEGS — separate printable modules, 12 DOF skeleton
# ------------------------------------------------------------

def coxa_module():
    core = joint_core(24,34)
    arm = rounded_box(54,44,36,8).translate((26,0,0))
    shaft = cyl_z(8,48).translate((0,0,-24))
    return core.fuse(arm).fuse(shaft)

def coxa_armor():
    return joint_armor_cover(31,40).fuse(
        dragon_scale(56,44,5).translate((16,0,24))
    )

def femur_module():
    L=125
    return triangular_link(L,34,20).fuse(
        joint_core(20,32)
    ).fuse(joint_core(20,32).translate((L,0,0)))

def femur_armor():
    L=125
    armor=leg_link_armor(L,40,25)
    fin=flat_fin([(12,20),(42,46),(78,33),(110,18),(125,0),
                  (88,7),(48,13)],4)
    return armor.fuse(fin)

def tibia_module():
    L=145
    return triangular_link(L,30,18).fuse(
        joint_core(19,30)
    ).fuse(joint_core(17,28).translate((L,0,0)))

def tibia_armor():
    L=145
    armor=leg_link_armor(L,36,22)
    fin=flat_fin([(10,15),(42,36),(78,28),(112,17),(145,0),
                  (110,4),(65,9)],4)
    return armor.fuse(fin)

def dragon_claw():
    base=rounded_box(52,42,12,5)
    for y in (-14,0,14):
        claw=rounded_box(38,8,9,3).translate((30,y,-2))
        tip=Cone(7,2,22,rotation=(0,90,0),
                 align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((48,y,-2))
        base=base.fuse(claw).fuse(tip)
    return base

LEG_POSITIONS={
    "FL":(-105,-96,-12), "FR":(-105,96,-12),
    "RL":(105,-96,-12),  "RR":(105,96,-12)
}

def make_leg(name,x,y,z,side):
    parts=[]
    parts.append((f"{name}_coxa", coxa_module().rotate(
        Axis.Z,-18 if side>0 else 18).translate((x,y,z))))
    parts.append((f"{name}_coxa_armor", coxa_armor().translate((x,y,z))))

    fy=y+side*38
    femur_origin=(x,fy,z)
    parts.append((f"{name}_femur",femur_module().translate(femur_origin)))
    parts.append((f"{name}_femur_armor",femur_armor().translate(femur_origin)))

    knee_x=x+125
    knee_z=z-12
    tibia_origin=(knee_x,fy,knee_z)
    parts.append((f"{name}_tibia",tibia_module().translate(tibia_origin)))
    parts.append((f"{name}_tibia_armor",tibia_armor().translate(tibia_origin)))

    parts.append((f"{name}_foot",dragon_claw().translate(
        (knee_x+145,fy,knee_z-15))))
    return parts

# ------------------------------------------------------------
# NECK / TAIL / FINS
# ------------------------------------------------------------

def neck_assembly():
    result=None
    for i,x in enumerate((-145,-128,-111)):
        r=35-i*3
        core=cyl_x(r,28).translate((x,0,50))
        armor=joint_armor_cover(r+7,34).translate((x,0,50))
        p=core.fuse(armor)
        result=p if result is None else result.fuse(p)
    return result

def body_fins():
    pts=[(-112,45),(-88,92),(-50,62),(-10,86),(28,54),(66,75),
         (112,42),(58,31),(-25,34)]
    return flat_fin(pts,4), flat_fin(pts,4)

def tail_segment(index):
    length=max(28,54-index*4)
    radius=max(7,22-index*1.5)
    core=cyl_x(radius,length)
    cover=joint_armor_cover(radius+5,length+4)
    spine=Cone(radius*.8,2,20+max(0,10-index),
               align=(Align.CENTER,Align.CENTER,Align.MIN)).translate(
                   (length*.5,0,radius))
    return core.fuse(cover).fuse(spine)

def dragon_tail():
    # Each segment is exported separately so the physical tail can articulate.
    parts=[]
    x=150
    for i in range(9):
        seg=tail_segment(i).rotate(Axis.Y,-i*5).translate(
            (x,0,15-i*3))
        parts.append((f"tail_segment_{i+1:02d}",seg))
        x += max(28,54-i*4)
    return parts

# ------------------------------------------------------------
# REFERENCE-ONLY ASSEMBLY
# ------------------------------------------------------------

def reference_assembly():
    comps=[]
    comps.append(("body_shell",body_shell()))
    comps.append(("body_bottom_guard",body_bottom_guard()))
    comps.append(("electronics_tray",electronics_tray()))
    comps.append(("display_bezel",display_bezel()))
    comps.append(("display_mount_plate",display_mount_plate()))
    comps.append(("display_cable_tunnel",display_cable_tunnel()))
    comps += body_scales()
    comps.append(("dorsal_spines",dorsal_spines()))
    comps.append(("dragon_head",dragon_head()))
    comps.append(("neck_armor",neck_assembly()))
    left,right=body_fins()
    comps.append(("dragon_fin_left",left.translate((0,-74,0))))
    comps.append(("dragon_fin_right",right.translate((0,70,0))))
    for n,p in dragon_tail():
        comps.append((n,p))
    for name,(x,y,z) in LEG_POSITIONS.items():
        comps += make_leg(name,x,y,z,-1 if y<0 else 1)
    return comps

def printable_components():
    comps=[
        ("body_shell",body_shell()),
        ("body_bottom_guard",body_bottom_guard()),
        ("electronics_tray",electronics_tray()),
        ("display_bezel",display_bezel()),
        ("display_mount_plate",display_mount_plate()),
        ("display_cable_tunnel",display_cable_tunnel()),
    ]
    for name,shape in body_scales():
        comps.append((name,shape))
    comps.append(("dorsal_spines",dorsal_spines()))
    comps.append(("dragon_head",dragon_head()))
    comps.append(("neck_armor",neck_assembly()))
    left,right=body_fins()
    comps += [
        ("dragon_fin_left",left.translate((0,-74,0))),
        ("dragon_fin_right",right.translate((0,70,0))),
    ]
    for name,shape in dragon_tail():
        comps.append((name,shape))
    for name,(x,y,z) in LEG_POSITIONS.items():
        comps += make_leg(name,x,y,z,-1 if y<0 else 1)
    comps += electronics_standoffs()
    return comps

def export_pair(prefix,name,shape):
    export_stl(shape,str(OUT/f"{prefix}_{name}.stl"))
    export_step(shape,str(OUT/f"{prefix}_{name}.step"))
    print(f"[OK] {prefix}_{name}")

def fuse_all(components):
    result=None
    for _,shape in components:
        result=shape if result is None else result.fuse(shape)
    return result

def write_manifest(printable, reference):
    lines=[
        "XZORT RESCUE QUADRUPED — CAD OUTPUT MANIFEST",
        "="*64,
        "",
        "PRINT_*  = PRINT THIS PART",
        "REF_*    = REFERENCE ONLY — DO NOT PRINT",
        "",
        "PRINTED MODULES:",
    ]
    for name,_ in printable:
        lines.append(f"  PRINT_{name}.stl / PRINT_{name}.step")
    lines += [
        "",
        "REFERENCE:",
        "  REF_full_assembly.stl / REF_full_assembly.step",
        "  REF_full_assembly is a visual assembly preview only.",
        "",
        "BODY:",
        "  Large rounded hollow shell.",
        "  Internal electronics bay is intentionally spacious.",
        "  Top display bay accepts a generic screen/module.",
        "  Electronics tray is removable.",
        "",
        "IMPORTANT:",
        "  STL = normally used for slicing/printing.",
        "  STEP = CAD/editing/reference format.",
        "  REF files are not intended to be printed.",
        "  Check real servo/screen dimensions before final fabrication.",
    ]
    (OUT/"PRINT_MANIFEST.txt").write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    print("="*68)
    print("XZORT RESCUE QUADRUPED — 80cm MECHANICAL DRAGON")
    print("ROUND / HOLLOW BODY + DISPLAY BAY + MODULAR PRINT PARTS")
    print("="*68)

    printable=printable_components()
    print(f"[INFO] Printable modules: {len(printable)}")

    for name,shape in printable:
        export_pair("PRINT",name,shape)

    # Reference assembly is deliberately separate from printable files.
    reference=reference_assembly()
    preview=fuse_all(reference)
    export_pair("REF","full_assembly",preview)

    write_manifest(printable,reference)

    print()
    print("[DONE] All CAD output is in:")
    print(f"       {OUT.resolve()}")
    print("[DONE] PRINT_* = print")
    print("[DONE] REF_*   = do not print")
