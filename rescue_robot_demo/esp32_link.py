#!/usr/bin/env python3
"""Optional ESP32 telemetry link.

Simulation remains the default. This module only reads newline-delimited JSON
telemetry and never bypasses the ESP32 safety gate.
"""

import json
import threading
import time


class ESP32Link:
    def __init__(self, port=None, baud=115200):
        self.port = port
        self.baud = baud
        self.serial = None
        self.latest = {}
        self.running = False
        self.thread = None

    def connect(self):
        if not self.port:
            return False
        try:
            import serial
            self.serial = serial.Serial(self.port, self.baud, timeout=0.2)
        except Exception:
            self.serial = None
            return False

        self.running = True
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()
        return True

    def _reader(self):
        while self.running and self.serial:
            try:
                line = self.serial.readline().decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                packet = json.loads(line)
                if isinstance(packet, dict):
                    self.latest = packet
            except Exception:
                time.sleep(0.05)

    def snapshot(self):
        return dict(self.latest)

    def send(self, command):
        if not self.serial:
            return False
        packet = {"type": "command", "command": str(command).upper()}
        try:
            self.serial.write((json.dumps(packet) + "\n").encode("utf-8"))
            return True
        except Exception:
            return False

    def close(self):
        self.running = False
        if self.serial:
            try:
                self.serial.close()
            except Exception:
                pass
            self.serial = None
