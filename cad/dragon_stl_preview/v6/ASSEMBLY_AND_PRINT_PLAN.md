# XZORT Dragon V6 — assembly and print plan

## Assembly hierarchy
1. BODY LOWER: battery bay, electronics mounting posts, four leg hardpoint pads, split-line screw holes.
2. BODY UPPER: removable armored lid, side scale plates, dorsal armor mounting pads.
3. HEAD MODULE: tapered skull, brow/horn features, cheek armor, front sensor aperture, rear mounting flange.
4. DORSAL ARMOR: one carrier with central and lateral spike rows; fastener locations along the carrier.
5. TAIL: five serviceable links; each link can be printed separately, then assembled as a tail module.
6. LEGS: coxa housing plus coxa/femur/tibia armor shells. Armor must not obstruct servo horns or joint travel.
7. ELECTRONICS TRAY: removable internal tray for controller, power distribution and sensors.

## Critical dimensions currently encoded
- Main body envelope: 180 x 90 x 60 mm nominal.
- Battery cavity target: 112 x 42 x 28 mm.
- Leg segment design parameters: coxa 40 mm, femur 75 mm, tibia 85 mm.
- Nominal M3 clearance: 3.2 mm.
- Bearing reference: 688ZZ, OD 16 / ID 8 / width 5 mm (press fit must be calibrated).

## Before calling V6 final
- [ ] Run `dragon_v6_build.py` in a build123d environment and ensure all exports succeed.
- [ ] Run mesh repair / watertightness / normals / non-manifold checks on every STL.
- [ ] Confirm the complete robot stays inside the 350 mm competition envelope; tail and leg sweep can exceed static body bounds.
- [ ] Measure actual DS3225 servo bodies, horns, screws, wiring bend radius and connector access.
- [ ] Validate all M3 screw paths, insert depths, head clearance, and upper/lower body alignment.
- [ ] Verify battery fits with insulation and retainer; verify electronics tray and cable routing.
- [ ] Run joint range/collision checks for all 12 servo axes.
- [ ] Print small tolerance coupons before committing to large parts.
- [ ] Assemble a low-cost prototype before printing the final cosmetic armor.

**Status:** design-source and preview package; not yet mechanically verified final release. Some visual meshes in this directory predate the parametric source. Re-export from `dragon_v6_build.py` before relying on them for fabrication.
