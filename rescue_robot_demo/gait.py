from dataclasses import asdict, dataclass
from math import sin, pi


@dataclass
class LegTarget:
    x: float
    y: float
    z: float
    phase: str


class GaitPlanner:
    """Deterministic hardware-neutral alternating-diagonal gait.

    The planner only produces foot targets. IK, joint limits, calibration and
    physical servo output stay on the ESP32 side.
    """

    LEGS = ("FL", "FR", "RL", "RR")
    LEG_PHASES = {"FL": 0.0, "RR": 0.0, "FR": 0.5, "RL": 0.5}

    def __init__(self):
        self.phase = 0.0
        self.step_length = 30.0
        self.step_height = 22.0
        self.body_height = -90.0
        self.foot_y = {"FL": 45.0, "RL": 45.0, "FR": -45.0, "RR": -45.0}
        self.frequency = 1.5
        self.moving = False
        self.move_name = "IDLE"

    def set_moveset(self, name):
        name = str(name).upper()
        presets = {
            "IDLE": (0.0, 0.0),
            "WALK": (30.0, 22.0),
            "SLOW_WALK": (20.0, 16.0),
            "SEARCH": (18.0, 14.0),
            "RESCUE": (14.0, 12.0),
        }
        if name not in presets:
            return False
        self.move_name = name
        self.step_length, self.step_height = presets[name]
        self.moving = name != "IDLE"
        if name == "SLOW_WALK":
            self.frequency = 1.0
        elif name == "SEARCH":
            self.frequency = 0.8
        elif name == "RESCUE":
            self.frequency = 0.7
        else:
            self.frequency = 1.5
        return True

    def reset(self):
        self.phase = 0.0
        self.set_moveset("IDLE")

    def _leg_target(self, leg):
        y = self.foot_y[leg]
        if not self.moving:
            return LegTarget(0.0, y, self.body_height, "STANCE")

        local = (self.phase - self.LEG_PHASES[leg]) % 1.0

        if local < 0.5:
            progress = local / 0.5
            x = -self.step_length / 2.0 + progress * self.step_length
            lift = sin(progress * pi)
            z = self.body_height + self.step_height * lift
            phase_name = "SWING"
        else:
            progress = (local - 0.5) / 0.5
            x = self.step_length / 2.0 - progress * self.step_length
            z = self.body_height
            phase_name = "STANCE"

        return LegTarget(round(x, 3), y, round(z, 3), phase_name)

    def update(self, dt=0.05, moving=None):
        if moving is not None:
            self.moving = bool(moving)

        if self.moving:
            self.phase = (self.phase + max(0.0, float(dt)) * self.frequency) % 1.0

        return {leg: self._leg_target(leg) for leg in self.LEGS}

    def snapshot(self, dt=0.05, moving=None):
        return {
            leg: asdict(target)
            for leg, target in self.update(dt, moving).items()
        }
