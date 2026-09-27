# Hardware V2 Integration

V1 is software-complete. V2 is the physical integration layer.

## Hardware chain

ESP32 -> PCA9685 -> 12 servos
       -> IMU
       -> environmental sensor
       -> network link

Optional companion computer:

camera -> Robot OS
thermal -> Robot OS

## Motion

The Python GaitPlanner produces logical foot targets.

The ESP32 Kinematics module converts:

    foot X/Y/Z
        -> coxa/femur/tibia
        -> calibrated servo angles

ServoManager is the hardware boundary.

## Safety requirements

Before powering a real mechanism:

- lift the robot clear of the ground for initial servo tests
- use conservative mechanical limits
- test one servo/channel at a time
- keep an accessible physical power cutoff
- never rely on software E-STOP as the only safety mechanism
- verify servo orientation and calibration before gait testing

The repository does not assume that simulated angles are safe mechanical angles.

## Firmware adapter status

The firmware now contains guarded adapters for PCA9685, IMU and environmental sensing. PCA9685 output remains disabled by default (`ENABLE_PCA9685 0`). Physical activation requires the matching library, verified wiring, servo calibration and conservative mechanical limits.

A firmware motion timeout and local E-STOP latch are also present so the network link is not the only safety layer.
