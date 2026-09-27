class SafetyManager:
    """Software safety gate for simulation and future hardware commands."""

    MAX_SPEED = 1.0

    def validate_mode(self, mode, allowed_modes):
        return mode in allowed_modes

    def validate_target(self, target):
        return (
            isinstance(target, (tuple, list))
            and len(target) == 2
            and all(isinstance(v, int) for v in target)
        )

    def motion_allowed(self, emergency_stop=False):
        return not emergency_stop
