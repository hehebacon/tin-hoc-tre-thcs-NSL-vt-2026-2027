# Robot OS Protocol V1

All packets are newline-delimited JSON.

## Telemetry

    {"type":"telemetry","battery":96.2,"signal":98.0,"mode":"PATROL","state":"PATROLLING"}

## Command

    {"type":"command","command":"STOP"}

Supported commands:

- STOP
- RESUME
- RETURN_HOME

## Motion request

    {"type":"pose","leg":"FL","x":80,"y":45,"z":-90}

The ESP32 is responsible for validating limits and rejecting invalid targets.
