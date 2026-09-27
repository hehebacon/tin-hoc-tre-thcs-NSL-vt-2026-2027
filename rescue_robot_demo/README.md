# Rescue Robot Simulator V3

This directory contains the hardware-neutral rescue robot simulator and the
ESP32 motion boundary.

## What is included

- deterministic 50 ms simulator loop
- A* navigation with terrain cost
- alternating-diagonal quadruped gait
- gait movesets: IDLE, WALK, SLOW_WALK, SEARCH, RESCUE
- foot-target -> hardware-aligned IK -> joint-angle telemetry
- live leg moveset/phase visualization and joint-angle display
- ESP32 MotionController gait execution
- calibration remains between IK and servo output
- E-STOP / resume path
- telemetry and serial command protocol
- unit tests for navigation, gait and safety

## Motion architecture

Simulator:

    mission/path
        -> GaitPlanner
        -> FootTarget
        -> QuadrupedIK (45/75/105 mm)
        -> joint angles

ESP32:

    GaitController
        -> FootTarget
        -> MotionController
        -> Kinematics
        -> ServoCalibration
        -> ServoManager
        -> PCA9685

The simulator is not a replacement for mechanical calibration. Before real
servo power-up, verify every leg's direction, limits, neutral angle and physical
clearance at low speed.

## Run

    ./run.sh

## Test

    python3 -m unittest discover -s . -p 'test_*.py'

## Serial gait commands

    gait WALK
    gait SLOW_WALK
    gait SEARCH
    gait RESCUE
    stop
    resume

JSON command example:

    {"command":"GAIT","mode":"WALK"}

## Safety

Never treat simulator reachability as proof that a physical pose is safe.
Mechanical limits, power/current limits and calibration must be verified on the
real robot.


## Simulator validation status

The simulator now exposes the same nominal leg geometry documented for the
physical robot:

- Coxa: 45 mm
- Femur: 75 mm
- Tibia: 105 mm

The Python IK layer is used for reachability and telemetry only. The ESP32
Kinematics module remains authoritative for physical servo output and limits.

The UI shows each leg's gait phase plus C/F/T joint angles while the robot
moves. This makes gait changes visible before hardware power-up.
