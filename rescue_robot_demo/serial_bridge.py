#!/usr/bin/env python3
"""Optional serial bridge between the Robot OS and an ESP32."""
import argparse
import json
import sys
import time

def run(port, baud):
    try:
        import serial
    except ImportError:
        print("Hardware bridge requires pyserial.", file=sys.stderr)
        print("Install with: python3 -m pip install pyserial", file=sys.stderr)
        return 2
    with serial.Serial(port, baud, timeout=0.2) as link:
        print(f"SERIAL BRIDGE: {port} @ {baud}")
        while True:
            line = link.readline().decode("utf-8", errors="replace").strip()
            if line:
                try:
                    print("ESP32 >", json.dumps(json.loads(line), separators=(",", ":")))
                except json.JSONDecodeError:
                    print("ESP32 >", line)
            time.sleep(0.02)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()
    raise SystemExit(run(args.port, args.baud))
