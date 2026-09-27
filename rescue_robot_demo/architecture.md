# Rescue Robot Architecture

## Mission
A modular quadruped platform for search-and-rescue, environmental awareness, telemetry and authorized/public-data-assisted operations.

## Runtime layers
1. Firmware / motion: ESP32, servo controller, inverse kinematics and calibration.
2. Sensor layer: RGB camera, thermal sensor, IMU and environmental sensors.
3. Robot core: state, safety, motion requests and telemetry.
4. Decision layer: patrol, rescue, autonomous navigation and public/authorized data analysis.
5. Network layer: REST/WebSocket gateway.
6. Operator UI: live map, camera/thermal view, telemetry, mode control and logs.

## Design rule
Simulation providers must expose the same logical data shape as future hardware providers. This keeps the demo useful after hardware integration.

## OSINT boundary
The OSINT mode is designed around public or explicitly authorized information sources for emergency-response context. It is not a private-person tracking system.
