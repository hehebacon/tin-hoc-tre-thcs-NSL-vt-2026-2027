import math
import random


class SensorSimulator:
    def __init__(self, victim):
        self.victim = victim
        self.temperature = 31.2
        self.humidity = 78.0
        self.pressure = 1007.0
        self.thermal = 0.0
        self.person_visible = False
        self.obstacle_distance = 5.0
        self.rain_risk = 0.0

    def update(self, robot):
        distance = math.dist(robot, self.victim)
        self.person_visible = distance <= 5.0
        self.thermal = max(0.0, 1.0 - distance / 8.0)
        self.temperature = max(15.0, min(45.0, self.temperature + random.uniform(-0.08, 0.08)))
        self.humidity = max(40.0, min(100.0, self.humidity + random.uniform(-0.5, 0.5)))
        self.pressure += random.uniform(-0.15, 0.15)
        self.obstacle_distance = round(max(0.8, 4.5 + random.uniform(-0.8, 0.8)), 2)
        self.rain_risk = max(0.0, min(1.0, (self.humidity - 55.0) / 45.0 + max(0.0, 1005.0 - self.pressure) / 20.0))

    def environment_assessment(self):
        if self.rain_risk >= 0.7:
            return "RAIN RISK ELEVATED"
        if self.rain_risk >= 0.45:
            return "HUMID / MONITOR"
        return "STABLE"

    def snapshot(self):
        return {
            "temperature": round(self.temperature, 2),
            "humidity": round(self.humidity, 2),
            "pressure": round(self.pressure, 2),
            "thermal": round(self.thermal, 2),
            "person_visible": self.person_visible,
            "obstacle_distance": self.obstacle_distance,
            "rain_risk": round(self.rain_risk, 2),
            "environment": self.environment_assessment(),
        }


class PublicDataSimulator:
    def __init__(self):
        self.alert = "No public emergency alert in demo area"
        self.sources = ["Demo weather feed", "Demo public map", "Demo official alert feed"]
        self.last_scan = "READY"

    def scan(self):
        self.last_scan = "PUBLIC SOURCES SCANNED"
        return self.snapshot()

    def snapshot(self):
        return {"alert": self.alert, "sources": self.sources, "last_scan": self.last_scan}
