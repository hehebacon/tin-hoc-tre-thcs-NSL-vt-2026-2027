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


## Current firmware architecture (v0.4.0)

The firmware now contains:
- hardware-independent quadruped core, kinematics, gait and servo calibration
- deterministic offline competition DecisionEngine
- Perception / WorldState abstraction for line, obstacle, target and color
- color and line sensor adapter interfaces
- local Vietnamese/English offline command AI
- ESP32 Wi-Fi AP + optional STA Internet connection
- optional Gemini online assistant with offline fallback
- web dashboard and telemetry
- safety layer remains authoritative over motion

Online AI is optional. Competition autonomy must not depend on Internet access.

Real-hardware status: the software interfaces are ready for integration, but sensor drivers, pickup/place hardware, field calibration and repeated real-robot testing are still required before claiming competition-ready hardware performance.
