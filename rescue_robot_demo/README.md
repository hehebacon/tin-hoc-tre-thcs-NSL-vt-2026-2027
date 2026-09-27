# Rescue Robot V1

Tin Hoc Tre THCS NSL Vung Tau 2026-2027 quadruped rescue-robot software platform.

## V1 capabilities

- 2D mission map with A* obstacle-aware navigation
- PATROL / SEARCH & RESCUE / PUBLIC DATA / AUTONOMOUS modes
- Mission start, stop, reset and event history
- Emergency stop, resume and return-home commands
- RGB camera and thermal sensing simulation
- Temperature, humidity and pressure telemetry
- Battery, signal, speed, heading, pitch, roll and GPS simulation
- Web command center with realtime polling
- Hardware adapter boundary for ESP32 integration
- Optional serial bridge for future physical robot
- Public/authorized-data boundary for OSINT-style functions

## Run

    cd rescue_robot_demo
    ./run_demo.sh

Open the dashboard at http://127.0.0.1:8080.

## Tests

    python3 -m unittest discover -p 'test_*.py'

## Hardware phase

V1 is deliberately hardware-independent. The physical phase replaces simulated providers with ESP32, servo/PCA9685, IMU, environmental, RGB and thermal drivers while preserving the Robot OS API contract.

See V1_ARCHITECTURE.md and ESP32_BRIDGE.md.
