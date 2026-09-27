# Wall Climb Mode

The robot now exposes a `CLIMB` mission mode in the mission state machine.

## Safety / capability boundary

`CLIMB` is currently a **capability placeholder**. Selecting the mode does not command the normal leg gait and therefore does not pretend that the current quadruped hardware can climb a wall.

Current behavior:

- Mission mode becomes `CLIMB`.
- Normal gait output is stopped.
- Simulator shows the mode as wall-climb standby.
- The mode can later be connected to a dedicated climbing controller after the physical mechanism, adhesion/traction sensing, fall detection, and limits have been validated.

This keeps the mission API ready without inventing hardware capabilities that have not been measured or installed.

## Command

Serial:

```
mission CLIMB
```

JSON:

```json
{"command":"MISSION","mode":"CLIMB"}
```

Return to normal operation with another supported mission mode or:

```
mission IDLE
```
