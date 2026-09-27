import math
import random


class TelemetrySimulator:
    def __init__(self, base=(2, 2)):
        self.battery = 96.0
        self.signal = 98.0
        self.heading = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.speed = 0.0
        self.gps = {"lat": 10.411, "lon": 107.136}
        self.base = base

    def update(self, robot, previous):
        dx = robot[0] - previous[0]
        dy = robot[1] - previous[1]
        moved = math.hypot(dx, dy)

        if moved:
            self.speed = min(1.0, moved * 2.0)
            self.heading = (math.degrees(math.atan2(dy, dx)) + 360) % 360
            self.battery = max(0.0, self.battery - 0.015)
        else:
            self.speed = max(0.0, self.speed * 0.7)

        self.signal = max(60.0, min(100.0, self.signal + random.uniform(-1.0, 1.0)))
        self.pitch = max(-20.0, min(20.0, self.pitch + random.uniform(-1.2, 1.2)))
        self.roll = max(-20.0, min(20.0, self.roll + random.uniform(-1.2, 1.2)))

        self.gps["lat"] += dx * 0.00001
        self.gps["lon"] += dy * 0.00001

    def snapshot(self):
        return {
            "battery": round(self.battery, 1),
            "signal": round(self.signal, 1),
            "heading": round(self.heading, 1),
            "pitch": round(self.pitch, 1),
            "roll": round(self.roll, 1),
            "speed": round(self.speed, 2),
            "gps": {
                "lat": round(self.gps["lat"], 6),
                "lon": round(self.gps["lon"], 6),
            },
        }
