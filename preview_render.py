"""
RESCUE QUADRUPED — DRAGON V4
One-file preview generator.

Run:
    source .venv/bin/activate
    python preview_render.py

Outputs:
    output_cad/preview/RescueQuadruped_Dragon_FULL_PREVIEW.stl
    output_cad/preview/RescueQuadruped_Dragon_FULL_PREVIEW.step

This is a visual/master assembly preview, not a final manufacturing assembly.
Verify servo dimensions, joint axes, fasteners and clearances before printing.
"""

import os
from build123d import *
from modul import (
    P,
    body_shell,
    dragon_head,
    dragon_tail_module,
    dragon_tail_tip,
    hip_bracket,
    thigh_link,
    knee_shin,
)

PREVIEW_OUT = os.path.join("output_cad", "preview")
os.makedirs(PREVIEW_OUT, exist_ok=True)


def leg_assembly(x, y, mirror_x=False, mirror_y=False):
    hip = hip_bracket()
    thigh = thigh_link()
    shin = knee_shin()

    # Visual placement only: hip -> thigh -> knee/shin.
    sx = -1 if mirror_x else 1
    sy = -1 if mirror_y else 1

    hip_part = hip.moved(Location(Pos(x, y, 55), (0, 0, 0)))
    thigh_part = thigh.moved(
        Location(
            Pos(x + sx * 18, y + sy * 20, -95),
            (0, sx * 12, sy * 4),
        )
    )
    shin_part = shin.moved(
        Location(
            Pos(x + sx * 25, y + sy * 105, -270),
            (0, sx * 7, sy * 8),
        )
    )

    return [hip_part, thigh_part, shin_part]


def build_full_preview():
    children = []

    # Main armored body.
    body = body_shell()
    children.append(body)

    # Head at the front.
    head = dragon_head()
    children.append(
        head.moved(
            Location(
                Pos(0, -P["body_length"] * 0.56, 40),
                (0, 0, 0),
            )
        )
    )

    # Six-piece curved tail + tip.
    tail_y = P["body_length"] * 0.46
    for i in range(P["tail_modules"]):
        tail = dragon_tail_module(i)
        children.append(
            tail.moved(
                Location(
                    Pos(0, tail_y + i * P["tail_module_length"], 34 + i * 5),
                    (0, 0, 0),
                )
            )
        )

    tip = dragon_tail_tip()
    children.append(
        tip.moved(
            Location(
                Pos(
                    0,
                    tail_y + P["tail_modules"] * P["tail_module_length"],
                    68,
                ),
                (0, 0, 0),
            )
        )
    )

    # Four complete legs.
    x = P["body_width"] * 0.40
    y = P["body_length"] * 0.30

    for px, py, mx, my in [
        (-x, -y, True, False),   # FL
        ( x, -y, False, False),  # FR
        (-x,  y, True, True),    # RL
        ( x,  y, False, True),   # RR
    ]:
        children.extend(leg_assembly(px, py, mx, my))

    return Compound(
        label="RESCUE_QUADRUPED_DRAGON_V4_FULL_PREVIEW",
        children=children,
    )


print("[PREVIEW] Building complete dragon quadruped...")
assembly = build_full_preview()

stl_path = os.path.join(
    PREVIEW_OUT, "RescueQuadruped_Dragon_FULL_PREVIEW.stl"
)
step_path = os.path.join(
    PREVIEW_OUT, "RescueQuadruped_Dragon_FULL_PREVIEW.step"
)

export_stl(
    assembly,
    stl_path,
    tolerance=P["stl_tolerance"],
    angular_tolerance=P["stl_angular_tolerance"],
    ascii_format=False,
)
export_step(assembly, step_path)

with open(
    os.path.join(PREVIEW_OUT, "README_PREVIEW.txt"),
    "w",
    encoding="utf-8",
) as f:
    f.write("RESCUE QUADRUPED — DRAGON V4 FULL PREVIEW\n")
    f.write("=" * 58 + "\n")
    f.write("Contains: body + head + eye holes + 6 tail modules + tip + 4 complete legs.\n")
    f.write("STL = quick visual/slicer preview.\n")
    f.write("STEP = CAD/master inspection.\n")
    f.write("This assembly is for visual layout; verify real hardware dimensions before production.\n")

print("[PREVIEW] DONE")
print("[PREVIEW] STL :", stl_path)
print("[PREVIEW] STEP:", step_path)
