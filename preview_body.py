"""
RESCUE QUADRUPED — DRAGON V5
FULL BODY PREVIEW

Run:
    source .venv/bin/activate
    python preview_body.py

Creates one complete visual assembly:
    body + head + tail + 4 articulated legs

Outputs:
    output_cad/preview/RescueQuadruped_Dragon_V5_FULL_BODY.stl
    output_cad/preview/RescueQuadruped_Dragon_V5_FULL_BODY.step

This is a visual/master assembly. It is NOT the final mechanical
joint alignment; verify real servo dimensions before printing.
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

OUT = os.path.join("output_cad", "preview")
os.makedirs(OUT, exist_ok=True)


def make_leg(x, y, sx, sy):
    hip = hip_bracket()
    thigh = thigh_link()
    shin = knee_shin()

    # Visual pose: all mechanical parts remain separate solids.
    return [
        hip.moved(Location(Pos(x, y, 52))),
        thigh.moved(Location(Pos(x + sx * 18, y + sy * 22, -92),
                             (0, sx * 10, sy * 5))),
        shin.moved(Location(Pos(x + sx * 25, y + sy * 105, -265),
                            (0, sx * 6, sy * 8))),
    ]


def build_full_body():
    parts = []

    # Dragon torso.
    parts.append(body_shell())

    # Head / neck transition.
    parts.append(
        dragon_head().moved(
            Location(Pos(0, -P["body_length"] * 0.56, 40))
        )
    )

    # Articulated tail, progressively rising.
    tail_start = P["body_length"] * 0.48
    for i in range(P["tail_modules"]):
        parts.append(
            dragon_tail_module(i).moved(
                Location(
                    Pos(0, tail_start + i * P["tail_module_length"],
                        34 + i * 6)
                )
            )
        )

    parts.append(
        dragon_tail_tip().moved(
            Location(
                Pos(0,
                    tail_start + P["tail_modules"] * P["tail_module_length"],
                    75)
            )
        )
    )

    # Four legs around the armored torso.
    x = P["body_width"] * 0.40
    y = P["body_length"] * 0.30

    parts.extend(make_leg(-x, -y, -1, -1))  # front-left
    parts.extend(make_leg( x, -y,  1, -1))  # front-right
    parts.extend(make_leg(-x,  y, -1,  1))  # rear-left
    parts.extend(make_leg( x,  y,  1,  1))  # rear-right

    return Compound(
        label="RESCUE_QUADRUPED_DRAGON_V5_FULL_BODY",
        children=parts,
    )


print("[FULL BODY PREVIEW] Building V5 dragon quadruped...")
assembly = build_full_body()

stl = os.path.join(OUT, "RescueQuadruped_Dragon_V5_FULL_BODY.stl")
step = os.path.join(OUT, "RescueQuadruped_Dragon_V5_FULL_BODY.step")

export_stl(
    assembly,
    stl,
    tolerance=P["stl_tolerance"],
    angular_tolerance=P["stl_angular_tolerance"],
    ascii_format=False,
)
export_step(assembly, step)

with open(os.path.join(OUT, "README_FULL_BODY.txt"), "w", encoding="utf-8") as f:
    f.write("RESCUE QUADRUPED — DRAGON V5 FULL BODY PREVIEW\n")
    f.write("=" * 62 + "\n")
    f.write("Complete visual assembly: head + armored body + tail + four legs.\n")
    f.write("Fasteners are represented by recessed/counterbored mounting geometry in the individual parts.\n")
    f.write("STL: visual/slicer preview.\n")
    f.write("STEP: CAD/master inspection.\n")
    f.write("This is a visual layout, not a final manufacturing assembly.\n")

print("[FULL BODY PREVIEW] DONE")
print("[FULL BODY PREVIEW] STL :", stl)
print("[FULL BODY PREVIEW] STEP:", step)
