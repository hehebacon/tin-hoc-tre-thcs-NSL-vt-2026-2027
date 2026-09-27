class BodyStabilizer:
    """Simulation-side IMU compensation model; physical tuning belongs on ESP32."""
    def __init__(self):
        self.max_compensation = 8.0

    def update(self, pitch, roll):
        return {
            "pitch_correction": round(max(-self.max_compensation, min(self.max_compensation, -pitch * 0.35)), 2),
            "roll_correction": round(max(-self.max_compensation, min(self.max_compensation, -roll * 0.35)), 2),
            "active": abs(pitch) > 2.0 or abs(roll) > 2.0,
        }

    def snapshot(self, pitch, roll):
        return self.update(pitch, roll)
