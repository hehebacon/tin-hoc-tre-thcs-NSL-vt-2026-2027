# Rescue Robot Demo V1

Offline simulator for the Tin Hoc Tre THCS robot project.

## Features
- 2D rescue map
- PATROL, RESCUE, OSINT and AUTONOMOUS modes
- A* path planning
- Simulated camera/person detection
- Simulated thermal sensing
- Temperature, humidity and pressure telemetry
- Public/authorized data feed simulation
- Live status and event log
- No external Python packages required

## Run
```bash
cd rescue_robot_demo
python3 main.py
```

The simulator is hardware-independent. Real camera, thermal, IMU, environmental and network drivers can later replace simulator providers without changing the decision layer.
