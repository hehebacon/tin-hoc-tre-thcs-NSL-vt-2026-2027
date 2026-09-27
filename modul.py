"""RESCUE QUADRUPED — DRAGON V6
Stable FDM CAD primitives and import-safe module.
"""

import os
from build123d import *

OUT="output_cad"
PRINT_OUT=os.path.join(OUT,"print_ready")
CAD_OUT=os.path.join(OUT,"cad_master")
os.makedirs(PRINT_OUT,exist_ok=True); os.makedirs(CAD_OUT,exist_ok=True)

P={
 "robot_height":800.0,"design_version":"V6_DRAGON_FULL_BODY_STABLE",
 "servo_w":20.0,"servo_l":40.0,"servo_h":40.0,
 "thigh_length":180.0,"shin_length":200.0,
 "wall":5.0,"clearance":0.35,"m3_hole":3.4,"pivot_hole":4.2,
 "fastener_head":6.2,"fastener_depth":3.2,"armor_t":4.0,
 "foot_diameter":30.0,"foot_thickness":5.0,
 "body_length":250.0,"body_width":145.0,"body_height":72.0,"body_wall":5.0,
 "head_length":72.0,"head_width":82.0,"head_height":55.0,"eye_hole":8.0,
 "tail_modules":6,"tail_base_radius":18.0,"tail_tip_radius":5.0,
 "tail_module_length":38.0,"stl_tolerance":0.05,"stl_angular_tolerance":0.1,
}
W,L,H=P["servo_w"],P["servo_l"],P["servo_h"]; WALL=P["wall"]; CLR=P["clearance"]
M3_R=P["m3_hole"]/2; PIVOT_R=P["pivot_hole"]/2

def export_print(part,name):
 export_stl(part,os.path.join(PRINT_OUT,name+".stl"),tolerance=P["stl_tolerance"],angular_tolerance=P["stl_angular_tolerance"],ascii_format=False)
def export_master(part,name): export_step(part,os.path.join(CAD_OUT,name+".step"))

def hip_bracket():
    """OCC-stable servo hip housing.

    Uses only robust overlapping solids and through-holes. Counterbores are
    intentionally deferred to the final manufacturing CAD pass because they
    can create Null TopoDS_Shape on some build123d/OCC combinations.
    """
    ow = W + 2 * WALL + 4
    ol = L + 2 * WALL + 4
    oh = H + WALL

    outer = Box(ow, ol, oh, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cavity = Box(
        W + 2 * CLR, L + 2 * CLR, H + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    ).translate((0, 0, -0.5))
    part = outer.cut(cavity)

    # Reinforcement pads overlap the housing.
    pad_x = ow / 2 - 8
    for x in (-pad_x, pad_x):
        part = part.fuse(
            Cylinder(
                12, 8,
                align=(Align.CENTER, Align.CENTER, Align.MIN)
            ).translate((x, -ol * 0.15, oh * 0.25))
        )

    # Two full-depth M3 mounting holes.
    for x in (-ow * 0.30, ow * 0.30):
        hole = Cylinder(
            M3_R, oh + 2,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        ).translate((x, ol * 0.18, -0.5))
        part = part.cut(hole)

    # Pivot boss overlaps the front wall.
    boss = Cylinder(
        16, 12,
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    ).translate((-6, 0, oh * 0.5))
    part = part.fuse(boss)

    pivot = Cylinder(
        PIVOT_R, 24,
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    ).translate((-12, 0, oh * 0.5))

    return part.cut(pivot)

def thigh_link():
    """Angular spider-style upper leg.

    The silhouette uses straight rectangular arms and a hard 90-degree
    offset instead of a round rod. Servo/pivot bores remain mechanical.
    """
    ln = P["thigh_length"]
    bw = 30.0
    bh = 24.0
    arm = 24.0
    joint_r = 18.0

    part = Box(
        bw, ln * 0.72, bh,
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # Square rear shoulder / pivot block.
    part = part.fuse(
        Box(bw + 10, 34, bh + 4,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((0, -17, -2))
    )

    # Main straight section.
    part = part.fuse(
        Box(bw, ln * 0.42, bh,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((0, ln * 0.58, 0))
    )

    # Hard 90-degree spider bend.
    part = part.fuse(
        Box(bw, arm, bh + 10,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((0, ln * 0.68, 0))
    )
    part = part.fuse(
        Box(bw + 18, arm, bh,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((0, ln * 0.82, 5))
    )

    # End joint housing.
    part = part.fuse(
        Cylinder(joint_r, bw + 8,
                 rotation=(0, 90, 0),
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, ln, bh / 2))
    )

    # Light structural ribs for FDM strength.
    for y in (ln * 0.18, ln * 0.42, ln * 0.66):
        part = part.fuse(
            Box(bw + 8, 5, 4,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((0, y, bh))
        )

    # Pivot holes at both ends.
    for y in (0, ln):
        part = part.cut(
            Cylinder(
                PIVOT_R, bw + 12,
                rotation=(0, 90, 0),
                align=(Align.CENTER, Align.CENTER, Align.MIN)
            ).translate((0, y, bh / 2))
        )

    return part


def knee_shin():
    """Angular lower leg with the characteristic compact spider bend."""
    ln = P["shin_length"]
    bw = 28.0
    bh = 22.0
    joint_r = 18.0

    # Upper vertical-ish section.
    part = Box(
        bw, ln * 0.48, bh,
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # 90-degree knee offset.
    part = part.fuse(
        Box(bw + 12, 30, bh + 8,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, ln * 0.42, 0))
    )
    part = part.fuse(
        Box(bw, ln * 0.50, bh,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, ln * 0.50, 0))
    )

    # Lower foot section is deliberately offset for the spider silhouette.
    part = part.fuse(
        Box(bw + 14, 34, bh,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, ln * 0.80, 0))
    )

    # Knee/end joint bosses.
    for y in (0, ln):
        part = part.fuse(
            Cylinder(
                joint_r, bw + 8,
                rotation=(0, 90, 0),
                align=(Align.CENTER, Align.CENTER, Align.MIN)
            ).translate((0, y, bh / 2))
        )

    # Pivot bores.
    for y in (0, ln):
        part = part.cut(
            Cylinder(
                PIVOT_R, bw + 12,
                rotation=(0, 90, 0),
                align=(Align.CENTER, Align.CENTER, Align.MIN)
            ).translate((0, y, bh / 2))
        )

    # Flat rescue foot.
    foot = Box(
        42, 52, P["foot_thickness"],
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    ).translate((0, ln * 0.91, -P["foot_thickness"]))
    foot = foot.fuse(
        Cylinder(
            P["foot_diameter"] / 2,
            P["foot_thickness"],
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        ).translate((0, ln * 0.91, -P["foot_thickness"]))
    )

    return part.fuse(foot)


def shoulder_armor():
    """Stylized shoulder shell that hides the servo housing."""
    w = W + 24
    d = 48
    h = 18
    part = Box(w, d, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = part.fuse(
        Cone(w * 0.48, w * 0.34, 12,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, 0, h))
    )
    # Mechanical side fins.
    for x in (-w * 0.42, w * 0.42):
        part = part.fuse(
            Box(7, 30, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((x, 0, 4))
        )
    # M3 service holes.
    for x in (-w * 0.30, w * 0.30):
        part = part.cut(
            Cylinder(M3_R, h + 4,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((x, 0, -1))
        )
    return part


def thigh_armor():
    """Slim upper-leg armor with a raised mechanical spine."""
    ln = P["thigh_length"]
    w = 38
    t = 5
    part = Box(w, ln * 0.78, t,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Tapered-looking nose and rear cap.
    part = part.fuse(
        Cone(w * 0.55, w * 0.38, 10,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, ln * 0.78, 0))
    )
    part = part.fuse(
        Box(10, ln * 0.62, 12,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, ln * 0.08, t))
    )
    # Two angular side rails.
    for x in (-w * 0.38, w * 0.38):
        part = part.fuse(
            Box(5, ln * 0.52, 8,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((x, ln * 0.18, t))
        )
    return part


def shin_armor():
    """Lower-leg armor plate with compact spider/mecha geometry."""
    ln = P["shin_length"]
    w = 34
    t = 5
    part = Box(w, ln * 0.64, t,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = part.fuse(
        Box(w + 10, 34, 9,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, ln * 0.44, t))
    )
    part = part.fuse(
        Box(w * 0.72, 40, 8,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, ln * 0.72, t))
    )
    return part


def foot_claw():
    """Wide rescue foot with three simple traction claws."""
    base = Box(48, 58, 7,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    base = base.fuse(
        Cylinder(18, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, 20, 0))
    )
    for x in (-15, 0, 15):
        base = base.fuse(
            Cone(6, 1.8, 26,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
            .rotate(Axis.X, -18)
            .translate((x, 43, 2))
        )
    # Grip ribs.
    for y in (8, 22, 36):
        base = base.fuse(
            Box(34, 4, 3,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((0, y, 7))
        )
    return base


def body_side_armor():
    """Layered side armor for a finished rescue-mecha silhouette."""
    bw = P["body_width"]
    bl = P["body_length"]
    h = P["body_height"]
    plate = Box(8, bl * 0.56, h * 0.48,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = plate.fuse(
        Box(14, bl * 0.26, h * 0.34,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, -bl * 0.13, h * 0.38))
    )
    # Raised armor ribs.
    for y in (-bl * 0.18, 0, bl * 0.18):
        plate = plate.fuse(
            Box(12, 6, h * 0.30,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((0, y, h * 0.16))
        )
    return plate


def head_crest():
    """Dragon/mecha dorsal crest for the head."""
    crest = Box(10, 42, 8,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    for y, z, r in ((-15, 8, 9), (0, 13, 7), (15, 17, 5)):
        crest = crest.fuse(
            Cone(r, 1.2, 18,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((0, y, z))
        )
    return crest


def neck_ring():
    """Armored neck collar between head and body."""
    outer = Cylinder(30, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inner = Cylinder(19, 12, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((0, 0, -1))
    ring = outer.cut(inner)
    for a in (0, 90, 180, 270):
        x = 24 if a in (0, 180) else 0
        y = 24 if a in (90, 270) else 0
        ring = ring.fuse(
            Cylinder(6, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((x, y, 2))
        )
    return ring


def sensor_pod():
    """Front sensor/camera pod placeholder for future perception hardware."""
    pod = Box(34, 28, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pod = pod.fuse(
        Cone(18, 10, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
        .translate((0, -4, 20))
    )
    for x in (-9, 9):
        pod = pod.cut(
            Cylinder(4.2, 12,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            .translate((x, -1, 14))
        )
    return pod


def rescue_beacon():
    """Small roof beacon / status-light housing."""
    base = Cylinder(13, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    dome = Sphere(10).translate((0, 0, 5))
    return base.fuse(dome)


def tail_armor_segment():
    """Decorative armored collar that can be repeated along the tail."""
    outer = Cylinder(24, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inner = Cylinder(15, 10, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((0, 0, -1))
    ring = outer.cut(inner)
    for a in (0, 90, 180, 270):
        ring = ring.fuse(
            Box(7, 18, 5,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            .rotate(Axis.Z, a)
            .translate((0, 0, 2))
        )
    return ring


def cable_clip():
    """Tiny snap-on cable guide for servo wiring."""
    outer = Box(14, 12, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    slot = Box(8, 8, 6, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((0, 0, 3))
    return outer.cut(slot)


def accessory_kit():
    """Complete visual accessory set for the finished robot."""
    return Compound(children=[
        shoulder_armor(),
        thigh_armor(),
        shin_armor(),
        foot_claw(),
        body_side_armor(),
        head_crest(),
        neck_ring(),
        sensor_pod(),
        rescue_beacon(),
        tail_armor_segment(),
        cable_clip(),
    ])



def body_shell():
 bl,bw,bh=P["body_length"],P["body_width"],P["body_height"]; part=Box(bw,bl,bh,align=(Align.CENTER,Align.CENTER,Align.MIN))
 for y in (-bl*.42,bl*.40): part=part.fuse(Sphere(bw*.42).translate((0,y,bh*.48)))
 part=part.cut(Box(bw-2*P["body_wall"],bl-46,bh*.48,align=(Align.CENTER,Align.CENTER,Align.MIN)))
 for x in (-bw*.36,bw*.36): part=part.fuse(Sphere(22).translate((x,-bl*.30,bh)))
 part=part.fuse(Box(34,bl*.64,P["armor_t"]+8,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,-bl*.05,bh)))
 for y,z in ((-bl*.30,bh+7),(-bl*.10,bh+9),(bl*.10,bh+9),(bl*.30,bh+7)): part=part.fuse(Cone(13,2.5,13,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,y,z)))
 tx,ty=bw*.34,bl*.28
 for x in (-tx,tx):
  for y in (-ty,ty):
   part=part.fuse(Cylinder(14,10,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((x,y,bh-2)))
   part=part.cut(Cylinder(M3_R,15).translate((x,y,bh-1)))
   part=part.cut(Cylinder(P["fastener_head"]/2,P["fastener_depth"]+.5).translate((x,y,bh-3)))
 socket=Cylinder(22,24,rotation=(90,0,0)).translate((0,bl*.52,bh*.42))
 bore=Cylinder(12,34,rotation=(90,0,0)).translate((0,bl*.52,bh*.42))
 return part.fuse(socket).cut(bore)

def dragon_head():
 hw,hl,hh=P["head_width"],P["head_length"],P["head_height"]; part=Box(hw,hl,hh,align=(Align.CENTER,Align.CENTER,Align.MIN))
 part=part.fuse(Cone(hw*.43,hw*.30,30,rotation=(90,0,0),align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,-hl*.48,8)))
 ex,ey,ez=hw*.31,-hl*.18,hh*.68
 for x in (-ex,ex):
  part=part.cut(Cylinder(7,10,rotation=(1,0,0)).translate((x,ey,ez)))
  part=part.cut(Cylinder(P["eye_hole"]/2,26,rotation=(1,0,0)).translate((x,ey+3,ez)))
 for x in (-10,10): part=part.cut(Cylinder(2.5,12,rotation=(1,0,0)).translate((x,-hl*.49,25)))
 for x in (-ex,ex): part=part.fuse(Cone(8,1,22,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((x,-4,hh)))
 return part.fuse(Box(hw*.58,28,8,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,-hl*.42,5)))

def dragon_tail_module(index):
 count=P["tail_modules"]; t=index/max(1,count-1); r1=P["tail_base_radius"]*(1-t)+P["tail_tip_radius"]*t; r2=max(3,r1-4.5); ln=P["tail_module_length"]
 part=Cone(r1,r2,ln,align=(Align.CENTER,Align.CENTER,Align.MIN))
 part=part.fuse(Cylinder(r1+3,7,align=(Align.CENTER,Align.CENTER,Align.MIN)))
 part=part.fuse(Cylinder(r2+2.5,7,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,0,ln-7)))
 part=part.cut(Cylinder(max(5,r1*.52),11,align=(Align.CENTER,Align.CENTER,Align.MIN)))
 part=part.cut(Cylinder(2.2,(r1+8)*2,rotation=(0,90,0)).translate((0,0,5)))
 part=part.fuse(Cone(max(3,r1*.4),.8,14+6*(1-t),align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,ln*.52,r1*.55)))
 return part.rotate(Axis.X,-10+index*6)

def dragon_tail_tip():
 return Cone(7,.5,42,align=(Align.CENTER,Align.CENTER,Align.MIN)).fuse(Cone(5,.2,22,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,17,7)))

if __name__=="__main__":
 print("[PRINT V7] Generating full dragon-mecha modules + accessory kit...")
 parts=[("RescueQuadruped_Dragon_Hip_Bracket_PRINT",hip_bracket()),("RescueQuadruped_Dragon_Thigh_Link_PRINT",thigh_link()),("RescueQuadruped_Dragon_Knee_Shin_PRINT",knee_shin()),("RescueQuadruped_Dragon_Body_PRINT",body_shell()),("RescueQuadruped_Dragon_Head_EyeHoles_PRINT",dragon_head())]
 for name,part in parts: export_print(part,name); export_master(part,name.replace("_PRINT","_MASTER"))
 for i in range(P["tail_modules"]):
  part=dragon_tail_module(i); export_print(part,f"RescueQuadruped_Dragon_Tail_{i+1:02d}_PRINT"); export_master(part,f"RescueQuadruped_Dragon_Tail_{i+1:02d}_MASTER")
 tip=dragon_tail_tip(); export_print(tip,"RescueQuadruped_Dragon_Tail_Tip_PRINT"); export_master(tip,"RescueQuadruped_Dragon_Tail_Tip_MASTER")
 accessories=[
  ("Shoulder_Armor",shoulder_armor()),
  ("Thigh_Armor",thigh_armor()),
  ("Shin_Armor",shin_armor()),
  ("Foot_Claw",foot_claw()),
  ("Body_Side_Armor",body_side_armor()),
  ("Head_Crest",head_crest()),
  ("Neck_Ring",neck_ring()),
  ("Sensor_Pod",sensor_pod()),
  ("Rescue_Beacon",rescue_beacon()),
  ("Tail_Armor_Segment",tail_armor_segment()),
  ("Cable_Clip",cable_clip()),
 ]
 for name,part in accessories:
  export_print(part,f"RescueQuadruped_Dragon_{name}_PRINT")
  export_master(part,f"RescueQuadruped_Dragon_{name}_MASTER")
 export_print(accessory_kit(),"RescueQuadruped_Dragon_Accessory_Kit_PRINT")
 export_master(accessory_kit(),"RescueQuadruped_Dragon_Accessory_Kit_MASTER")
 print("[PRINT V7] DONE")
