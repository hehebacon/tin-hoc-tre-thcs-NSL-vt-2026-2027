import math


class CameraSimulator:
    def __init__(self, victim):
        self.victim = victim

    def observe(self, robot):
        distance = math.dist(robot, self.victim)
        confidence = max(0.0, min(1.0, 1.0 - distance / 8.0))
        return {
            "person_detected": distance <= 5.0,
            "confidence": round(confidence, 2),
            "distance": round(distance, 2),
            "source": "SIMULATED_RGB_CAMERA",
        }
