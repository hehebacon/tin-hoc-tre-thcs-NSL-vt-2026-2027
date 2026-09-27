from dataclasses import asdict, dataclass


@dataclass
class LegTarget:
    x: float
    y: float
    z: float
    phase: str


class GaitPlanner:
    """Hardware-neutral alternating diagonal gait.

    Produces foot targets only. ESP32 remains responsible for IK, joint
    limits, calibration and physical actuation.
    """

    LEG_PHASES = {"FL": 0.0, "RR": 0.0, "FR": 0.5, "RL": 0.5}

    def __init__(self):
        self.phase = 0.0
        self.step_length = 30.0
        self.step_height = 25.0
        self.body_height = -90.0
        self.foot_y = 45.0

    def _leg_target(self, leg, phase, moving):
        y = self.foot_y if leg in ("FL", "RL") else -self.foot_y
        if not moving:
            return LegTarget(0.0, y, self.body_height, "STANCE")

        local = (phase - self.LEG_PHASES[leg]) % 1.0
        if local < 0.5:
            progress = local / 0.5
            x = -self.step_length / 2.0 + progress * self.step_length
            z = self.body_height + self.step_height * (1.0 - abs(2.0 * progress - 1.0))
            phase_name = "SWING"
        else:
            progress = (local - 0.5) / 0.5
            x = self.step_length / 2.0 - progress * self.step_length
            z = self.body_height
            phase_name = "STANCE"

        return LegTarget(x, y, z, phase_name)

    def update(self, moving=False, dt=0.05):
        if moving:
            self.phase = (self.phase + dt * 1.5) % 1.0
        return {
            leg: self._leg_target(leg, self.phase, moving)
            for leg in ("FL", "FR", "RL", "RR")
        }

    def snapshot(self, moving=False, dt=0.05):
        return {leg: asdict(target) for leg, target in self.update(moving, dt).items()}
