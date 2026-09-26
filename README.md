# AI Quadruped Robot - Servo Controller

Current firmware stage:

- ESP32 target
- 4 legs / 12 logical servo channels
- Inverse kinematics module
- Per-servo calibration
- Servo manager
- Serial command/debug interface
- Hardware-independent simulation stage

## Folder

```text
servo_controller/
├── servo_controller.ino
├── config.h
├── Kinematics.h
├── Kinematics.cpp
├── ServoCalibration.h
├── ServoCalibration.cpp
├── ServoManager.h
├── ServoManager.cpp
└── README.md
```

## Arduino IDE

Open:

```text
servo_controller.ino
```

Select the ESP32 board already being used by the project and press Verify.

No PCA9685 library is required yet because the current ServoManager is a software/simulation layer.

## Serial

Baud:

```text
115200
```

Commands:

```text
help
debug
status
center
enable
disable

servo 0 90
leg FL 90 90 90

cal
cal 0
caloffset 0 5
calinvert 1 1
callimit 2 10 170

ik 80 0 -100
ikleg FL 80 0 -100
```

## Important

Do not connect or power real servos yet.

The next hardware stage is:

```text
ServoManager
    ↓
PCA9685
    ↓
12 servos
```

That stage will require correct power wiring and current handling.
