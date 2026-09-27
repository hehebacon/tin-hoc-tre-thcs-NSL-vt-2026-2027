from dataclasses import dataclass


@dataclass
class LegTarget:
    x: float
    y: float
    z: float


class GaitPlanner:
    """Hardware-neutral gait planner.

    It produces foot targets only. A future ESP32 motion layer converts
    these targets to joint angles through the existing IK controller.
    """

    def __init__(self):
        self.phase = 0.0
        self.step_length = 30.0
        self.step_height = 25.0
        self.body_height = -90.0

    def update(self, moving=False, dt=0.05):
        if moving:
            self.phase = (self.phase + dt * 3.0) % 1.0

        phase = self.phase
        swing = phase < 0.5
        lift = self.step_height if swing else 0.0
        forward = (phase / 0.5) if swing else ((phase - 0.5) / 0.5)
        x = (forward * self.step_length) - (self.step_length / 2.0)

        if not moving:
            x = 0.0
            lift = 0.0

        return {
            "FL": LegTarget(+x, +45.0, self.body_height + lift),
            "FR": LegTarget(-x, -45.0, self.body_height + lift),
            "RL": LegTarget(-x, +45.0, self.body_height + lift),
            "RR": LegTarget(+x, -45.0, self.body_height + lift),
        }
