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

    def update(self, robot):
        distance = math.dist(robot, self.victim)
        self.person_visible = distance <= 5.0
        self.thermal = max(0.0, 1.0 - distance / 8.0) if distance <= 8.0 else 0.0
        self.temperature = max(15.0, min(45.0, self.temperature + random.uniform(-0.08, 0.08)))
        self.humidity = max(40.0, min(100.0, self.humidity + random.uniform(-0.5, 0.5)))
        self.pressure += random.uniform(-0.15, 0.15)

    def environment_assessment(self):
        if self.humidity > 82 and self.pressure < 1005:
            return "RAIN RISK ELEVATED"
        if self.humidity > 75:
            return "HUMID / MONITOR"
        return "STABLE"

    def snapshot(self):
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "thermal": self.thermal,
            "person_visible": self.person_visible,
            "environment": self.environment_assessment(),
        }


class PublicDataSimulator:
    def __init__(self):
        self.alert = "No public emergency alert in demo area"
        self.sources = ["Demo weather feed", "Demo public map", "Demo official alert feed"]

    def snapshot(self):
        return {"alert": self.alert, "sources": self.sources}
