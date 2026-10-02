#!/usr/bin/env python3
"""Two-way serial bridge for the Robot OS.

The bridge intentionally forwards only the small command set understood by
the ESP32 firmware. Physical motion still requires the firmware safety gate.
"""

import argparse
import json
import sys
import time
import select


ALLOWED_COMMANDS = {
    "STOP", "RESUME", "ENABLE", "CENTER", "STAND", "RESCUE_DONE",
    "GAIT WALK", "GAIT SLOW_WALK", "GAIT SEARCH", "GAIT RESCUE",
    "MISSION PATROL", "MISSION SEARCH", "MISSION RESCUE", "MISSION RETURN_HOME",
    "GOAL PATROL", "GOAL RESCUE", "GOAL RETURN_HOME",
}


def run(port, baud):
    try:
        import serial
    except ImportError:
        print("Install pyserial first: python3 -m pip install pyserial", file=sys.stderr)
        return 2

    with serial.Serial(port, baud, timeout=0.2) as link:
        print(f"BRIDGE ONLINE: {port} @ {baud}")
        while True:
            line = link.readline().decode("utf-8", errors="replace").strip()
            if line:
                try:
                    packet = json.loads(line)
                    print("ESP32 >", json.dumps(packet, separators=(",", ":")))
                except json.JSONDecodeError:
                    print("ESP32 >", line)

            command = None
            # This loop is receive-first by design. Commands can be injected
            # later through the optional stdin mode without changing protocol.
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if ready:
                raw = sys.stdin.readline().strip().upper()
                if raw in ALLOWED_COMMANDS:
                    parts = raw.split()
                    if parts[0] == "GAIT":
                        packet = {"type": "command", "command": "GAIT", "mode": parts[1]}
                    elif parts[0] == "MISSION":
                        packet = {"type": "command", "command": "MISSION", "mode": parts[1]}
                    elif parts[0] == "GOAL":
                        packet = {"type": "command", "command": "GOAL", "goal": parts[1]}
                    else:
                        packet = {"type": "command", "command": raw}
                    link.write((json.dumps(packet) + "\n").encode())
                    print("PC ->", packet)

            time.sleep(0.02)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()
    raise SystemExit(run(args.port, args.baud))
