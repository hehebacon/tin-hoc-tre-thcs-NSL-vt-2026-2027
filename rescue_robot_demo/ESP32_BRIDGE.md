# ESP32 Bridge

The Python Robot OS talks to the ESP32 through a newline-delimited JSON
boundary. The ESP32 is the authoritative safety boundary for physical motion.

## PC -> ESP32

Safety:

    {"type":"command","command":"STOP"}
    {"type":"command","command":"RESUME"}

Pose:

    {"type":"pose","leg":"FL","x":80,"y":45,"z":-90}

Gait:

    {"type":"command","command":"GAIT","mode":"WALK"}

Supported gait modes:

- WALK
- SLOW_WALK
- SEARCH
- RESCUE

## ESP32 -> PC

Telemetry contains firmware, E-STOP state, gait mode, gait phase, movement
state and hardware status.

The Python side must treat an active E-STOP or safety timeout as authoritative
and must never assume that a simulator command means the physical robot moved.

## Hardware integration order

1. ESP32 motion firmware
2. Serial/USB transport
3. Servo/PCA9685 output
4. IMU
5. Environmental sensor
6. RGB camera
7. Thermal sensor
8. Real network transport
