# XZORT Dragon V6 — modular print package (work in progress)

Branch: `feat/dragon-shell-35cm`

## V6 package files
- `PRINT_head_complete_v6.stl` — head armor + lower jaw combined into one STL import.
- `PRINT_body_upper_v6.stl` — upper body shell.
- `PRINT_body_lower_v6.stl` — lower body shell with preliminary internal rails and leg-hardpoint pads.
- `PRINT_body_complete_preview_v6.stl` — upper/lower body geometry packaged together for visual inspection only; do not print as one closed part.
- `PRINT_dorsal_spines_v6.stl` — dorsal spine armor in one STL import.
- `PRINT_tail_module_v6.stl` — tail visual module.
- `dragon_v6_parametric_reference.py` — starting parameter/reference architecture for the next editable CAD pass.

## Important status
The V6 CAD source has been refined: the body is narrower (180 x 84 x 60 mm) and dorsal center/side spikes are now modeled directly into the upper-body source. The STL previews have not yet been regenerated from this source, so this is **not a verified final print release**. The lower-shell battery bay now preserves a 3 mm floor and provides 27 mm depth; the specified 28 mm cavity/battery fit remains unconfirmed. Dorsal spikes are intended to come from the upper-body model only, avoiding a second overlapping spike carrier in the export set. The current meshes are generated concept geometry and may contain intersecting shells. Servo mounting holes, real servo envelopes, screw inserts, camera recesses, battery/electronics cavities, watertight Boolean unions, clearances, support orientation, and total assembly envelope have not been fully validated. Do not print functional/load-bearing parts before mesh repair and fit checks.

## Intended final module split
1. Head complete (single print file)
2. Body upper shell
3. Body lower shell / service-access side
4. Dorsal armor + spikes (single print file)
5. Tail module(s)
6. Four leg assemblies, split only where required for motion/servo installation
7. Internal electronics tray and fastener/hinge interfaces

The body upper and lower shells intentionally remain separate so electronics can be installed and serviced. This README does not claim the V6 assembly is mechanically complete.


## Automated validation
- `check_stl_meshes.py out_v6` checks every STL for watertightness, consistent winding and positive volume (requires `trimesh`).
- GitHub Actions workflow `Dragon V6 CAD QA` attempts a fresh Build123d export and runs the mesh checks on changes.
- A failed check is a blocker, not something to ignore. A passing mesh check still does not prove servo fit, battery fit, strength, collision-free movement, or a safe complete robot.
