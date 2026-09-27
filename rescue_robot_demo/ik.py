import math
from dataclasses import dataclass


@dataclass(frozen=True)
class JointAngles:
    coxa: float
    femur: float
    tibia: float
    reachable: bool
    reason: str = "OK"


class QuadrupedIK:
    """Hardware-aligned 3-DOF leg IK model.

    Geometry matches AI_CONTEXT.md:
      coxa = 45 mm
      femur = 75 mm
      tibia = 105 mm

    This is a simulator/reachability model. It does not replace the ESP32
    Kinematics implementation or physical servo calibration.
    """

    COXA = 45.0
    FEMUR = 75.0
    TIBIA = 105.0

    def solve(self, x, y, z):
        x = float(x)
        y = float(y)
        z = float(z)

        coxa = math.degrees(math.atan2(y, x))

        horizontal = math.hypot(x, y) - self.COXA
        distance = math.hypot(horizontal, z)

        min_reach = abs(self.FEMUR - self.TIBIA)
        max_reach = self.FEMUR + self.TIBIA

        if distance < min_reach or distance > max_reach:
            return JointAngles(coxa, 0.0, 0.0, False, "OUT_OF_REACH")

        cos_knee = (
            distance * distance
            - self.FEMUR * self.FEMUR
            - self.TIBIA * self.TIBIA
        ) / (2.0 * self.FEMUR * self.TIBIA)
        cos_knee = max(-1.0, min(1.0, cos_knee))

        knee = math.degrees(math.acos(cos_knee))

        alpha = math.atan2(z, horizontal)
        beta = math.acos(
            max(
                -1.0,
                min(
                    1.0,
                    (
                        self.FEMUR * self.FEMUR
                        + distance * distance
                        - self.TIBIA * self.TIBIA
                    )
                    / (2.0 * self.FEMUR * distance),
                ),
            )
        )

        femur = math.degrees(alpha + beta)

        return JointAngles(
            round(coxa, 3),
            round(femur, 3),
            round(knee, 3),
            True,
            "OK",
        )

    def solve_all(self, targets):
        return {leg: self.solve(t.x, t.y, t.z) for leg, t in targets.items()}
