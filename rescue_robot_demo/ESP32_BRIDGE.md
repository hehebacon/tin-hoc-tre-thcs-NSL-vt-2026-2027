# ESP32 Bridge

V1 keeps the transport boundary separate from the Robot OS.

## Serial packet format

ESP32 -> PC:

    {"type":"telemetry","battery":94.2,"mode":"PATROL","state":"PATROLLING"}

PC -> ESP32:

    {"type":"command","command":"STOP"}

Supported safety commands:
- STOP
- RESUME
- RETURN_HOME

The Python bridge is optional. The simulator and dashboard work without an ESP32.

## Hardware integration order

1. ESP32 motion firmware
2. Serial/USB transport
3. Servo/PCA9685 output
4. IMU
5. Environmental sensor
6. RGB camera
7. Thermal sensor
8. Real network transport
