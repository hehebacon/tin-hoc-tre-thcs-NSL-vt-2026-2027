# BOM — XZORT Rescue Quadruped / Bảng B

**Revision:** 2026-10-27  
**Purchase ceiling:** 1,000,000 VND for new purchases  
**Status:** staged/provisional; not a claim that a complete 12-DOF robot can be purchased from zero within the cap.

## Important decision before ordering

This BOM is for a **lightweight SpiderBot-style 12-DOF quadruped**, not the current oversized dragon-lizard CAD. MG90S is only the initial servo reference for adapting lightweight geometry. Its typical published stall torque is around 1.8–2.2 kgf·cm depending on voltage/model; clones vary, so it is **not approved for the current large body** without a joint-load calculation. Sources: [TowerPro MG90S specification](https://towerpro.com.tw/product/mg90s-3/) and [Vietnam MG90S reference](https://mlab.com.vn/dong-co-servo-mg90s).

Do not order 12 servos yet. First buy/test one compatible unit, measure its case and mounting holes, and validate a single leg. The exact Huna Robo board and competition rules are still unknown.

## A. Inventory first — target spend 0 VND

Check school/team stock and record exact model/quantity:

- [ ] Huna Robo controller: exact board name/revision, MCU, I/O voltage, supported SDK, I²C availability
- [ ] Any ESP32 board already available (only if external boards are allowed)
- [ ] Existing servos and included horns/screws
- [ ] PCA9685 16-channel servo driver, if already available
- [ ] Battery / regulated DC supply
- [ ] 3D printer access and filament
- [ ] M2/M3 screws, nuts, spacers, wire, connectors, switch and fuse
- [ ] Multimeter and suitable tools available at school

## B. Phase 1 — one-leg proof of concept

Buy only missing items after the board/rules are confirmed. The quantities below test one 3-DOF leg; they do **not** complete the robot.

| Item | Qty | Priority | Budget guidance / acceptance criteria |
|---|---:|---|---|
| MG90S 180° positional metal-gear servo | 3 | Required for 3-DOF test | Buy one first if possible; verify actual dimensions, horns, voltage and torque from the seller/datasheet. Reference allocation: up to 255,000 VND for 3 only if each is ≤85,000 VND. |
| Controller board | 0 if provided; otherwise TBD | Blocking | Do not buy until exact Huna Robo model and competition rules are confirmed. ESP32 firmware is not automatically compatible with Huna Robo. |
| PCA9685 16-channel PWM driver | 0 if already available; otherwise quote first | Conditional | Needed only if the selected controller/software path uses an external PWM driver. Check logic voltage and I²C compatibility first. |
| Dedicated regulated servo supply | 1 | Required | 4.8–6 V only if confirmed for the chosen servo; current rating must be calculated from the exact servo's stall current and how many can stall simultaneously. Never power servos from a 3.3 V MCU regulator. |
| Inline fuse + holder | 1 set | Required | Select fuse/wire rating after supply and servo current are known. |
| Physical power switch / disconnect | 1 | Required | Must interrupt servo power and be reachable during tests. |
| Suitable wire, connectors, common-ground leads | 1 set | Required | Wire gauge and connector current rating must match the calculated load; keep servo power separate from the controller rail. |
| M2/M3 screws, nuts, washers/spacers | 1 small set | Required | Final sizes depend on measured servo tabs and printed parts. |
| Filament / test print | As needed | Required | Prefer school printer/material stock; do not print final body parts before the servo fit check. |
| Contingency and shipping | — | Required reserve | Keep at least 100,000 VND unspent until local quotes are confirmed. |

### Phase 1 spending rule

Use the 1,000,000 VND ceiling as a hard total including shipping. The previous budget envelope reserved about 250,000 VND for power/protection/wiring and about 250,000 VND for frame/fasteners/test prints, with at least 100,000 VND contingency. These are **planning caps, not current vendor quotes**. If the controller or PWM driver must be purchased, recalculate before ordering. If all required items do not fit, pause and request school stock/sponsorship instead of removing the fuse or power cutoff.

## C. Phase 2 — complete 12-DOF robot (not approved for purchase yet)

| Item | Qty for full robot | Buy gate |
|---|---:|---|
| Same exact servo model | 12 total (including the 3 tested) | Only after the 3-DOF leg passes load, heat, range-of-motion and repeatability checks. If using the lightweight MG90S geometry, confirm it can support the measured robot mass and lever arms. |
| PCA9685 16-channel driver | 1 if required by chosen controller path | Confirm controller, I²C logic voltage and driver current/power routing. |
| Controller | 1 | Exact board and competition rules confirmed first. |
| Servo power system | 1 system | Sized from actual servo stall-current data, wiring, fuse and battery/supply requirements. Not sized by guesswork. |
| Frame / brackets / fasteners | 1 set | CAD must match measured servos and board; inspect fit before final print. |
| Battery, charger and power conversion | As required | Only after voltage/current budget and competition rules are known. |
| Optional sensors | As required by the actual task | Defer until stable standing and repeatable gait work. No display, thermal camera or decorative shell in the first build. |

**Cost reality:** a full 12-servo robot, controller, safe power system and frame is not confirmed feasible under 1,000,000 VND from zero. Treat borrowed/school-supplied parts as essential to this cap. Do not label the project competition-ready until it passes real-hardware testing.

## D. Do not buy yet

- [ ] 12 servos in one order
- [ ] A guessed Huna Robo board / replacement controller
- [ ] Battery or regulator before the voltage/current budget is calculated
- [ ] Final custom tray or body before measuring the real PCB/servo
- [ ] Sensors, camera, display, decorative shell or nonessential upgrades
- [ ] Any part whose compatibility is inferred only from a product name

## E. Pre-purchase checklist

- [ ] Exact controller model and contest rules confirmed
- [ ] One servo physically measured; mounting interface recorded
- [ ] Servo type confirmed as positional (not continuous rotation)
- [ ] Voltage and stall-current data verified for the exact seller/model
- [ ] Driver and controller logic levels / I²C compatibility confirmed
- [ ] Separate servo power rail, common ground, fuse and physical cutoff planned
- [ ] Local quote includes shipping and total stays ≤1,000,000 VND
- [ ] CAD mount and test leg updated to measured dimensions
- [ ] Adult/teacher reviews the power wiring before first powered test
