# Robot OS Protocol V1

All packets are newline-delimited JSON.

## Telemetry

    {"type":"telemetry","firmware":"0.3.0","safety_stop":false,"gait":"WALK","phase":0.25,"moving":true,"hardware":{...}}

The ESP32 safety state is authoritative.

## Command envelope

    {"type":"command","command":"STOP"}

## Safety / pose commands

Supported commands:

- STOP
- RESUME
- ENABLE
- CENTER
- STAND

## Gait command

    {"type":"command","command":"GAIT","mode":"WALK"}

Supported gait modes:

- WALK
- SLOW_WALK
- SEARCH
- RESCUE

The ESP32 validates the mode and safety state before starting motion.

## Foot target

    {"type":"pose","leg":"FL","x":80,"y":45,"z":-90}

The ESP32 is responsible for IK reachability, software limits, calibration and
physical servo output. Simulator reachability is not a hardware safety proof.
