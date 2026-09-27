class SafetyManager:
    """Software safety gate for simulation and future hardware adapters."""

    def __init__(self):
        self.estop = False
        self.max_speed = 1.0
        self.min_battery = 15.0

    def stop(self, reason="operator"):
        self.estop = True
        return {"ok": True, "state": "STOPPED", "reason": reason}

    def resume(self):
        self.estop = False
        return {"ok": True, "state": "READY"}

    def allow_motion(self, battery):
        if self.estop:
            return False, "EMERGENCY_STOP"
        if battery < self.min_battery:
            return False, "LOW_BATTERY"
        return True, "OK"

    def snapshot(self):
        return {
            "estop": self.estop,
            "max_speed": self.max_speed,
            "min_battery": self.min_battery,
        }
