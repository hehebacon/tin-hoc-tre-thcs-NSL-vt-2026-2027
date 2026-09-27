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
