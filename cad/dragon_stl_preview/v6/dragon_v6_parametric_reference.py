"""
XZORT Dragon Rescue Quadruped V6 modular CAD generator (Build123d).
Reference envelope: 350 mm target. Units: mm.
Module export policy:
- PRINT_head_complete_v6.stl = head armor + lower jaw + horns/spikes as one imported model
- PRINT_body_upper_v6.stl and PRINT_body_lower_v6.stl = two body shells; keep internal cavity accessible
- PRINT_body_complete_preview_v6.stl = combined preview only (overlapping upper/lower shells; NOT intended as one print)
- PRINT_dorsal_spines_v6.stl = spine base + all spikes as one imported model
- PRINT_tail_module_v6.stl = segmented tail preview
IMPORTANT: This script documents the intended editable CAD architecture. Current STL previews are early meshes;
verify watertightness, internal cavity, fastener holes, servo fit, support strategy and 350 mm envelope before printing.
"""
from build123d import *

# Parametric design envelope / interfaces (mm)
BODY_L, BODY_W, BODY_H = 180, 90, 60
COXA, FEMUR, TIBIA = 40, 75, 85
BATTERY = (112, 42, 28)
SERVO_CLEARANCE = 1.0
BEARING_OD, BEARING_ID, BEARING_T = 16, 8, 5
M3_CLEARANCE = 3.2
BODY_SPLIT_Z = 0

def body_shell(upper=True):
    # Parametric starting point for next CAD validation pass. Shells intentionally separate.
    z = 12 if upper else -12
    outer = Pos(0,0,z) * Box(BODY_L, BODY_W, 22)
    cavity = Pos(-5,0,z) * Box(124, 50, 16)
    shell = outer - cavity
    # Four reinforced leg hardpoints: each needs drilling/fit review against actual servo horns.
    for x in (-62,62):
        for y in (-35,35):
            boss = Pos(x,y,z) * Cylinder(8, 12)
            shell = shell + boss
    return shell

def head_module():
    # Import/trace the visual sculpt as a separate detailed module in the final CAD pass.
    # The current STL is the form-study source; mounting interface still requires dimensioned redesign.
    return Pos(0,0,0) * Box(100,48,45)

def dorsal_module():
    # Spine carrier and alternating spikes are separated from the load-bearing body.
    base = Box(116,24,10)
    for x in range(-48,49,12):
        base += Pos(x,0,16) * Rot(Y=-18) * Box(12,8,28)
    return base

if __name__ == "__main__":
    print("V6 design parameters loaded. Export/repair and mechanical fit validation still required.")
