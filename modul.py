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
 ln=P["thigh_length"]; bw=34.; bh=22.; part=Box(bw,ln,bh,align=(Align.CENTER,Align.CENTER,Align.MIN))
 for y in (0,ln): part=part.fuse(Cylinder(19,bw,rotation=(0,90,0)).translate((0,y,bh/2)))
 part=part.fuse(Cone(13,4,8,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,ln*.5,bh)))
 for y in (ln*.25,ln*.5,ln*.75): part=part.fuse(Box(40,6,3.5,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,y,bh)))
 for y in (0,ln): part=part.cut(Cylinder(PIVOT_R,bw+8,rotation=(0,90,0)).translate((0,y,bh/2)))
 for y in (12,ln-12): part=part.cut(Cylinder(P["fastener_head"]/2,P["fastener_depth"]).translate((0,y,bh-1.4)))
 return part

def knee_shin():
 ln=P["shin_length"]; part=Cone(12,19,ln,align=(Align.CENTER,Align.CENTER,Align.MIN))
 part=part.fuse(Box(5,30,ln*.55,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,0,ln*.2)))
 part=part.fuse(Cylinder(22,28,align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,0,ln-25)))
 part=part.cut(Cylinder(PIVOT_R,48,rotation=(0,90,0)).translate((0,0,ln-11)))
 return part.fuse(Cylinder(P["foot_diameter"]/2,P["foot_thickness"],align=(Align.CENTER,Align.CENTER,Align.MIN)).translate((0,0,-P["foot_thickness"])))

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
 print("[PRINT V6] Generating stable dragon modules...")
 parts=[("RescueQuadruped_Dragon_Hip_Bracket_PRINT",hip_bracket()),("RescueQuadruped_Dragon_Thigh_Link_PRINT",thigh_link()),("RescueQuadruped_Dragon_Knee_Shin_PRINT",knee_shin()),("RescueQuadruped_Dragon_Body_PRINT",body_shell()),("RescueQuadruped_Dragon_Head_EyeHoles_PRINT",dragon_head())]
 for name,part in parts: export_print(part,name); export_master(part,name.replace("_PRINT","_MASTER"))
 for i in range(P["tail_modules"]):
  part=dragon_tail_module(i); export_print(part,f"RescueQuadruped_Dragon_Tail_{i+1:02d}_PRINT"); export_master(part,f"RescueQuadruped_Dragon_Tail_{i+1:02d}_MASTER")
 tip=dragon_tail_tip(); export_print(tip,"RescueQuadruped_Dragon_Tail_Tip_PRINT"); export_master(tip,"RescueQuadruped_Dragon_Tail_Tip_MASTER")
 print("[PRINT V6] DONE")
