# AI CONTEXT — RESCUE QUADRUPED ROBOT

> Read this file before modifying the project. It is the persistent context for AI assistants working on this robotics project.

## 1. Project

This is a real student-built quadruped rescue robot for the Vietnamese Tin học trẻ competition.

- Competition: Tin học trẻ, THCS Ngô Sĩ Liên — Vũng Tàu, 2026–2027, Bảng B
- Repository: hehebacon/tin-hoc-tre-thcs-NSL-vt-2026-2027
- Goal: build a practical search-and-rescue quadruped prototype, not just a visual simulator.

Core concept:

PERCEIVE → UNDERSTAND → MOVE → SEARCH → DETECT → RESPOND → RESCUE

## 2. Robot

Physical architecture:

- 4 legs
- 3 DOF per leg
- 12 servos total
- ESP32 controller
- PCA9685 16-channel PWM driver

Legs:

- FL = Front Left
- FR = Front Right
- RL = Rear Left
- RR = Rear Right

Each leg:

Coxa → Femur → Tibia → Foot

Target servo: MG996R or mechanically/electrically compatible equivalent.

## 3. Servo mapping

Do not change casually:

FL: 0=Coxa, 1=Femur, 2=Tibia
FR: 3=Coxa, 4=Femur, 5=Tibia
RL: 6=Coxa, 7=Femur, 8=Tibia
RR: 9=Coxa, 10=Femur, 11=Tibia

## 4. IK geometry

Current geometry:

- Coxa: 45 mm
- Femur: 75 mm
- Tibia: 105 mm

These values must remain consistent across firmware, simulator, calibration, and CAD unless a deliberate redesign is requested.

## 5. Software architecture

Sensors
↓
RobotCore
↓
MotionSafety
↓
MotionController
↓
GaitController
↓
Inverse Kinematics
↓
Servo Calibration
↓
PCA9685
↓
12 Servos

RobotCore is the high-level mission/state layer. It should not directly control raw servo PWM.

MotionSafety has priority over mission logic. Never bypass E-STOP, safety limits, or fault handling.

MotionController converts foot targets into joint angles, calibration values, servo mapping, and PCA9685 commands.

## 6. Mission modes

Current modes:

IDLE
PATROL
SEARCH
RESCUE
FOLLOW
AVOID
EXPLORE
INSPECT
DELIVER
RECHARGE
RETURN_HOME
CALIBRATION
DEMO
CLIMB
FAULT

High-level intent:

- IDLE: stop
- PATROL: slow walking
- SEARCH: search gait
- RESCUE: rescue gait
- RETURN_HOME: return movement
- FOLLOW/AVOID/INSPECT: movement/search-style behavior
- EXPLORE/DEMO: walking/demo behavior
- CALIBRATION: stop and calibrate
- FAULT: stop
- CLIMB: placeholder only

These are software states. A mode does not prove the corresponding physical capability exists.

## 7. Gait

Current gait concepts:

- IDLE
- WALK
- SLOW_WALK
- SEARCH
- RESCUE

The gait uses alternating diagonal patterns such as FL+RR versus FR+RL.

Priorities:

1. Stability
2. Smooth movement
3. Predictable foot placement
4. Low servo shock
5. Repeatability

## 8. Sensors

Planned/target sensors include:

- IMU, potentially MPU6050
- Distance sensors
- Environmental sensor
- ESP32 camera
- Thermal sensor

Important distinction:

A software interface or placeholder does not mean hardware is installed.

Camera ≠ completed AI vision.
Thermal sensor ≠ automatic human detection.
Simulator pathfinding ≠ physical autonomous navigation.

## 9. Search/rescue flow

Conceptual mission:

PATROL → SEARCH → TARGET DETECTED → RESCUE → RETURN_HOME

Person/target detection may come from camera, thermal sensing, or other validated sensors.

Detection may be latched until mission reset so a short detection is not immediately lost.

## 10. Simulator

Simulator directory:

rescue_robot_demo/

Important files:

- core.py
- gait.py
- main.py
- test_core.py
- esp32_link.py
- PROTOCOL_V1.md
- ESP32_BRIDGE.md
- README.md
- VERSION

The simulator models mission state, gait, rescue flow, safety, terrain/path planning, and ESP32 communication.

Always distinguish:
- IMPLEMENTED
- SIMULATED
- PLANNED
- HARDWARE DEPENDENT
- PLACEHOLDER

Never present simulated functionality as physically verified.

## 11. Path planning

The simulator includes A*-style pathfinding with terrain costs.

This is simulation functionality. Real autonomous navigation requires physical sensing, localization, perception, obstacle detection, and control.

## 12. CLIMB

CLIMB is currently a software placeholder.

The physical robot does NOT currently have a verified wall-climbing mechanism.

Do not invent or claim wall climbing capability.

Any future climbing system requires an actual mechanical mechanism and dedicated control/safety design.

## 13. Power

12 high-current servos must not be powered directly from the ESP32.

Expected architecture:

Battery
├── dedicated servo power rail → 12 servos/PCA9685 V+
└── regulated logic power → ESP32

Use a correctly sized power system and appropriate common grounding/protection. Do not underspec the power system merely to save cost.

## 14. Mechanical/CAD rules

The robot should be compact, rigid, modular, repairable, and realistically manufacturable.

CAD should provide mounting/access for:

- ESP32
- PCA9685
- battery
- power converter/BEC
- camera
- sensors
- wiring

Battery and heavy electronics should stay near the body center to maintain a stable center of gravity.

Priorities:

1. Mechanical stability
2. Feasibility
3. Servo compatibility
4. Center of gravity
5. Ground clearance
6. Cable management
7. Electronics access
8. Sensor visibility
9. Weight
10. Appearance

## 15. AI rules

When assisting this project:

1. Treat it as a real physical engineering project.
2. Do not invent hardware or claim unverified capabilities.
3. Explicitly label simulation-only, planned, placeholder, and hardware-dependent features.
4. Preserve the existing architecture unless a redesign is explicitly requested.
5. Check dependent files when changing shared interfaces, servo mapping, IK dimensions, commands, or telemetry.
6. Never bypass MotionSafety or E-STOP.
7. Prefer practical, testable, modular solutions over unnecessary complexity.
8. Do not add advanced frameworks or hardware simply to make the project sound impressive.
9. Do not claim firmware compilation/tests succeeded unless they were actually run.
10. When making substantial source changes, provide complete replacement files when practical.

## 16. Development workflow

For code changes:

1. Inspect the current repository/source first.
2. Identify all affected files.
3. Implement the complete change.
4. Validate what can actually be validated.
5. Update related documentation/tests.
6. Commit the change to GitHub.
7. Report the commit and exactly what was changed.
8. Clearly state anything that could not be verified.

## 17. Current priority

Do not try to implement everything at once.

Priority:

Stable standing
→ Reliable walking
→ Turning
→ Sensor integration
→ Search
→ Target detection
→ Rescue behavior
→ Autonomous navigation
→ Advanced capabilities

A reliable physical robot is more valuable than a large collection of unfinished features.

## 18. Future expansion

Potential future modules include:

- Computer vision
- Thermal perception
- Obstacle avoidance
- Localization
- SLAM
- Autonomous navigation
- Mapping
- Terrain-adaptive gait
- Remote control
- Mission planning
- AI assistance
- Advanced climbing

These are future directions unless the repository shows otherwise.

## 19. Short identity

This is a 12-DOF ESP32/PCA9685 quadruped rescue robot with modular mission control, gait, inverse kinematics, calibration, safety, and sensor layers. It is being developed as a real Tin học trẻ competition prototype. Keep simulation separate from physical capability, never invent hardware, never bypass safety, and prefer practical complete-file changes.



## Latest extension status

v0.4.0 adds Perception, WorldState, color/line sensor adapters, Gemini OnlineAIClient, AP+STA Wi-Fi, and a web dashboard that reports perception and online AI status. No credentials are committed.