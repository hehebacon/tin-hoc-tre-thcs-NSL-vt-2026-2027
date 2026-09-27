# XZORT Rescue Quadruped — Hardware, Assembly & Troubleshooting

> Project: Tin học trẻ THCS Ngô Sĩ Liên — Vũng Tàu 2026–2027
>
> Robot: 4-legged quadruped, 12 logical servo channels, ESP32-based controller.
>
> This document is the practical guide for moving from simulator/firmware to a real prototype.

## 1. Architecture

    XZORT RESCUE QUADRUPED
             |
           ESP32
     RobotState / Motion
     Kinematics / Sensors
             |
          I2C/PWM
             |
          PCA9685
             |
      12 servo channels
             |
       4 legs x 3 DOF

Power:

    Servo supply -> fuse/switch -> servo power rail -> servos
    ESP32 supply -> regulated 5V/USB path
    Common GND -> ESP32 + PCA9685 + servo supply

IMPORTANT: never use the ESP32 as the power source for 12 physical servos. Select the servo supply from the actual servo voltage and current specifications.

## 2. Hardware purchase checklist

### Controller

- [ ] ESP32 development board x1
- [ ] USB data cable x1
- [ ] PCA9685 16-channel PWM board x1
- [ ] Spare wires/connectors
- [ ] Terminal blocks as needed

### Actuation

- [ ] 12 compatible servos
- [ ] 2–4 spare servos
- [ ] Servo horns
- [ ] Servo brackets
- [ ] Mechanical linkages
- [ ] M3/M4 hardware as required by the mechanical design

Do not buy/install all 12 servos before proving one complete leg.

Recommended order:

    1 complete leg
        -> 1 servo per joint
        -> 3-DOF leg
        -> 4-leg mechanical test
        -> full 12-servo build

### Power

- [ ] Servo-rated DC supply/battery
- [ ] DC-DC regulator if required
- [ ] Main power switch
- [ ] Fuse or suitable over-current protection
- [ ] Power distribution block
- [ ] Correct-gauge wiring
- [ ] Separate regulated ESP32 supply if required
- [ ] Multimeter

### Sensors

- [ ] IMU
- [ ] Distance sensors
- [ ] Optional camera
- [ ] Optional environmental/thermal sensor
- [ ] Buzzer/status LED
- [ ] Emergency-stop input

The simulator should provide software equivalents before hardware sensor integration.

### Mechanical

- [ ] Main chassis
- [ ] 4 leg assemblies
- [ ] Electronics mounting plate
- [ ] Battery mount
- [ ] Cable-management points
- [ ] Protective covers
- [ ] Rubber feet/contact pads

## 3. Assembly sequence

### Phase A — electronics bench test

    ESP32
      |
    PCA9685
      |
    ONE servo

Verify I2C, PWM, enable/disable, center position and conservative movement limits.

### Phase B — one joint

Test one servo at a time.

Verify:

- direction
- center
- limits
- no mechanical collision
- no abnormal noise or heating

### Phase C — one complete leg

    Hip
      |
    Thigh
      |
    Knee

Run the kinematics module and compare requested coordinates with actual movement.

### Phase D — four legs

    FL = Front Left
    FR = Front Right
    RL = Rear Left
    RR = Rear Right

Verify all 12 logical channels.

### Phase E — calibration

Calibrate before walking.

### Phase F — movesets

Test:

    stand
    sit
    center
    lift_leg
    place_leg
    step_forward
    step_backward
    turn_left
    turn_right

### Phase G — rescue behavior

Only after locomotion is stable:

    sensor input
        -> RobotState
        -> RescueController
        -> MotionController
        -> servo output

## 4. Module integration

Recommended dependency direction:

    main
     |
     +-- RobotState
     |
     +-- SensorManager
     |
     +-- RescueController
     |
     +-- MotionController
            |
            +-- Kinematics
            |
            +-- ServoManager
                   |
                   +-- PCA9685 / hardware driver

### RobotState

Stores current state such as:

    enabled
    emergencyStop
    batteryVoltage
    bodyX/bodyY/bodyZ
    sensorWarning
    rescueMode

Keep shared state here instead of scattering global variables.

### Kinematics

Input:

    target X/Y/Z

Output:

    joint angles

Kinematics should not contain PWM or I2C code.

### ServoManager

Responsible for:

- logical servo IDs
- angle limits
- inversion
- offsets
- simulation output
- hardware output
- enable/disable

### MotionController

Responsible for:

- standing
- stepping
- turning
- leg movement
- interpolation
- movesets

It calls Kinematics and ServoManager instead of directly manipulating PCA9685 channels.

### SensorManager

Responsible for reading sensors, validating readings and updating RobotState.

A bad sensor reading must not directly command a servo.

### RescueController

High-level behavior:

    IDLE
      -> PATROL
      -> TARGET_DETECTED
      -> APPROACH
      -> STOP_NEAR_TARGET
      -> REPORT / ASSIST

Start with deterministic, testable behavior. AI can be added later.

## 5. Servo channel map

Keep one fixed logical mapping.

| ID | Leg | Joint |
|---:|---|---|
| 0 | FL | Hip |
| 1 | FL | Thigh |
| 2 | FL | Knee |
| 3 | FR | Hip |
| 4 | FR | Thigh |
| 5 | FR | Knee |
| 6 | RL | Hip |
| 7 | RL | Thigh |
| 8 | RL | Knee |
| 9 | RR | Hip |
| 10 | RR | Thigh |
| 11 | RR | Knee |

Initially map logical ID N to PCA9685 channel N.

If physical wiring differs, change the mapping/configuration rather than rewriting MotionController.

## 6. Calibration

Start with the robot lifted off the ground.

Record for every servo:

    servo ID
    center
    offset
    invert
    minimum
    maximum

Example configuration concept:

    center = 90
    offset = 0
    invert = false
    minAngle = 20
    maxAngle = 160

These are examples only. Use the actual mechanical limits of the installed servo/joint.

Procedure:

1. Move every servo to a conservative center.
2. Test one joint at a time.
3. Check left/right symmetry.
4. Save calibration in project configuration.
5. Only then test standing.

## 7. Simulator and hardware

Use one MotionController for both environments.

    MotionController
          |
      ServoManager
          |
       +--+----------------+
       |                   |
    Simulator           Hardware
     backend             backend
                           |
                        PCA9685

Do not duplicate the walking algorithm for simulator and hardware.

## 8. Software installation

Arduino IDE:

1. Install Arduino IDE.
2. Install the ESP32 board package.
3. Open servo_controller/servo_controller.ino.
4. Select the exact ESP32 board.
5. Select the correct serial port.
6. Compile before connecting real servos.
7. Upload firmware.
8. Open Serial Monitor at 115200 baud.

Initial commands:

    help
    status
    debug
    center

## 9. Adding a module

Workflow:

    1. Define responsibility
    2. Create .h
    3. Create .cpp
    4. Add dependencies through constructors
    5. Add initialization
    6. Add update/tick method
    7. Add debug/status output
    8. Test in simulator
    9. Test one hardware component
    10. Integrate into full robot

Example interface:

    class NewSensor {
    public:
        bool begin();
        void update();
        bool healthy() const;
    };

Keep new modules small and single-purpose.

## 10. Troubleshooting

### ESP32 does not upload

Check:

- correct board
- correct serial port
- USB data cable
- board driver
- boot mode requirements
- whether another program owns the serial port

For upload debugging, disconnect external servo power first.

### PCA9685 is not detected

Check:

- SDA
- SCL
- GND
- VCC
- I2C address
- loose wires

Run an I2C scanner before changing servo code.

### Servo does not move

Check in this order:

    1. servo power
    2. common GND
    3. signal wire
    4. PCA9685 channel
    5. PWM frequency
    6. channel mapping
    7. angle limits
    8. calibration

### Servo moves in the wrong direction

Use the calibration inversion setting instead of rewriting the motion algorithm.

### Servo is offset

Use the per-servo offset instead of modifying the kinematics equations.

### One leg is mirrored

Check:

- left/right inversion
- mechanical mounting orientation
- logical channel mapping
- calibration offset

### Robot shakes

Possible causes:

- aggressive interpolation
- incorrect calibration
- loose mechanical joints
- inadequate servo power
- excessive mechanical load
- control-loop timing

Test one servo, then one leg, then four legs.

### ESP32 resets when servos move

Treat this as a power problem first.

Check:

    servo supply
    voltage sag
    current capability
    ground connection
    wiring
    regulator

Do not try to hide repeated brownouts with random software delays.

### Robot walks backward

Check:

- forward-direction convention
- coordinate system
- joint inversion
- gait phase order
- left/right mapping

### Robot falls

Debug in this order:

    calibration
      -> standing pose
      -> mechanical balance
      -> one-leg motion
      -> gait timing
      -> step height
      -> step length

Do not start autonomous gait testing before the static standing pose is stable.

## 11. Standard bug report

When something breaks, record:

    firmware version / commit
    board
    module
    exact command
    Serial Monitor output
    servo/channel ID
    expected behavior
    actual behavior
    simulator result
    hardware power state

Template:

    ## Bug

    Module:
    Commit:
    Hardware:
    Command:

    Expected:
    Actual:

    Serial output:

    Steps to reproduce:
    1.
    2.
    3.

## 12. Integration gates

    GATE 1  Code compiles
       |
    GATE 2  Simulator passes
       |
    GATE 3  ESP32 boots
       |
    GATE 4  PCA9685 communicates
       |
    GATE 5  One servo works
       |
    GATE 6  One joint calibrated
       |
    GATE 7  One complete leg works
       |
    GATE 8  Four legs stand
       |
    GATE 9  Basic gait works
       |
    GATE 10 Sensors work
       |
    GATE 11 Rescue behavior works
       |
    GATE 12 Full demo build

Never jump directly from simulator to full-power 12-servo testing.

## 13. Recommended documentation

Keep these files updated:

    README.md
    HARDWARE_BUILD_AND_TROUBLESHOOTING.md
    CALIBRATION.md
    TROUBLESHOOTING.md
    ARCHITECTURE.md
    CHANGELOG.md

## 14. Pre-demo checklist

### Hardware

- [ ] All 12 servos respond
- [ ] Calibration saved
- [ ] No cable can enter a moving joint
- [ ] Power connections secured
- [ ] Emergency stop / power switch tested
- [ ] Battery/supply checked

### Software

- [ ] Clean build
- [ ] Simulator test passed
- [ ] Servo mapping verified
- [ ] Standing pose verified
- [ ] Movesets verified
- [ ] Sensor simulation verified
- [ ] Rescue mode verified
- [ ] Serial debug available

### Demo flow

    BOOT
      -> SELF CHECK
      -> STAND
      -> MOVE
      -> SENSOR EVENT
      -> RESCUE BEHAVIOR
      -> REPORT STATUS

## 15. Golden debugging rule

Fix the smallest layer that is actually broken.

    Power
      -> Wiring
      -> Hardware driver
      -> ServoManager
      -> Calibration
      -> Kinematics
      -> MotionController
      -> Sensor/Rescue logic
      -> Demo

Do not rewrite the whole project because one servo channel is inverted.
