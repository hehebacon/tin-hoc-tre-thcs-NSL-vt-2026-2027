import math


class ThermalSimulator:
    def __init__(self, victim):
        self.victim = victim

    def observe(self, robot):
        distance = math.dist(robot, self.victim)
        intensity = max(0.0, min(1.0, 1.0 - distance / 8.0))
        return {
            "hotspot_detected": intensity >= 0.45,
            "intensity": round(intensity, 2),
            "distance": round(distance, 2),
            "source": "SIMULATED_THERMAL_SENSOR",
        }
