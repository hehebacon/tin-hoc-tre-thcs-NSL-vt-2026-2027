# Rescue Robot Simulator V3

This directory contains the hardware-neutral rescue robot simulator and the
ESP32 motion boundary.

## What is included

- deterministic 50 ms simulator loop
- A* navigation with terrain cost
- alternating-diagonal quadruped gait
- gait movesets: IDLE, WALK, SLOW_WALK, SEARCH, RESCUE
- foot-target -> IK -> joint-angle pipeline
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
        -> IK model
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
