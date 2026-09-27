"""RESCUE QUADRUPED — DRAGON V6 FULL BODY PREVIEW"""
import os
from build123d import *
from modul import P,body_shell,dragon_head,dragon_tail_module,dragon_tail_tip,hip_bracket,thigh_link,knee_shin

OUT=os.path.join("output_cad","preview"); os.makedirs(OUT,exist_ok=True)

def make_leg(x,y,sx,sy):
 return [
  hip_bracket().moved(Location(Pos(x,y,52))),
  thigh_link().moved(Location(Pos(x+sx*18,y+sy*22,-92),(0,sx*10,sy*5))),
  knee_shin().moved(Location(Pos(x+sx*25,y+sy*105,-265),(0,sx*6,sy*8))),
 ]

def build_full_body():
 parts=[body_shell(),dragon_head().moved(Location(Pos(0,-P["body_length"]*.56,40)))]
 tail_start=P["body_length"]*.48
 for i in range(P["tail_modules"]):
  parts.append(dragon_tail_module(i).moved(Location(Pos(0,tail_start+i*P["tail_module_length"],34+i*6))))
 parts.append(dragon_tail_tip().moved(Location(Pos(0,tail_start+P["tail_modules"]*P["tail_module_length"],75))))
 x=P["body_width"]*.40; y=P["body_length"]*.30
 parts += make_leg(-x,-y,-1,-1)+make_leg(x,-y,1,-1)+make_leg(-x,y,-1,1)+make_leg(x,y,1,1)
 return Compound(label="RESCUE_QUADRUPED_DRAGON_V6_FULL_BODY",children=parts)

if __name__=="__main__":
 print("[FULL BODY V6] Building dragon quadruped...")
 assembly=build_full_body()
 stl=os.path.join(OUT,"RescueQuadruped_Dragon_V6_FULL_BODY.stl")
 step=os.path.join(OUT,"RescueQuadruped_Dragon_V6_FULL_BODY.step")
 export_stl(assembly,stl,tolerance=P["stl_tolerance"],angular_tolerance=P["stl_angular_tolerance"],ascii_format=False)
 export_step(assembly,step)
 with open(os.path.join(OUT,"README_FULL_BODY.txt"),"w",encoding="utf-8") as f:
  f.write("RESCUE QUADRUPED — DRAGON V6 FULL BODY PREVIEW\n"+"="*62+"\n")
  f.write("Complete visual assembly: dragon head + armored body + 4 articulated legs + 6 tail modules + tip.\n")
  f.write("This is a visual/master layout; verify real servo dimensions before manufacturing.\n")
 print("[FULL BODY V6] DONE")
