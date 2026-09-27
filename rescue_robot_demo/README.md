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


## V2 implementation status

The V2 stack now contains:

- hardware-neutral ESP32 interfaces for PCA9685, IMU, environmental sensing, camera, thermal and network transport
- local firmware E-STOP and motion timeout gate
- conservative firmware IK target envelope
- newline-delimited JSON telemetry/command protocol
- optional Python ESP32 telemetry link
- optional PC serial bridge
- simulation-first gait and mission stack
- dashboard/API safety controls

### Hardware activation status

Physical outputs remain disabled by default. The PCA9685 adapter uses `ENABLE_PCA9685 0`.

Do not treat simulated coordinates or joint angles as mechanically safe. Before enabling physical servos, verify the exact servo model, supply, wiring, mechanical travel, calibration and an accessible physical power cutoff.

See `../WIRING_PLAN.md` and `HARDWARE_V2.md` for the staged bring-up process.
