# Robot Protocol V1

The demo uses a small JSON telemetry/control protocol so the simulator can later be replaced by an ESP32 transport.

## Telemetry

```json
{
  "type": "telemetry",
  "robot": {"x": 2, "y": 2},
  "mode": "PATROL",
  "found": false,
  "sensors": {
    "temperature": 31.2,
    "humidity": 78.0,
    "pressure": 1007.0,
    "thermal": 0.0,
    "person_visible": false
  }
}
```

## Commands

- `{"type":"mode","mode":"PATROL"}`
- `{"type":"mode","mode":"RESCUE"}`
- `{"type":"mode","mode":"OSINT"}`
- `{"type":"mode","mode":"AUTONOMOUS"}`

Hardware transport is intentionally separated from robot logic.
