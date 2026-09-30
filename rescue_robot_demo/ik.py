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
    """Simulator IK aligned with the 35 cm ESP32 motion model.

    Geometry:
      coxa = 35 mm
      femur = 65 mm
      tibia = 85 mm

    Returned joint angles use the same 0..180 logical servo space as the
    firmware. Mechanical offsets/inversion remain the responsibility of
    ServoCalibration on the ESP32.
    """

    COXA = 35.0
    FEMUR = 65.0
    TIBIA = 85.0

    COXA_MIN = 15.0
    COXA_MAX = 165.0
    FEMUR_MIN = 15.0
    FEMUR_MAX = 165.0
    TIBIA_MIN = 10.0
    TIBIA_MAX = 170.0

    def solve(self, x, y, z):
        x = float(x)
        y = float(y)
        z = float(z)

        coxa = 90.0 + math.degrees(math.atan2(y, x))
        horizontal = math.hypot(x, y) - self.COXA
        distance = math.hypot(horizontal, z)

        min_reach = abs(self.FEMUR - self.TIBIA) + 0.5
        max_reach = self.FEMUR + self.TIBIA - 0.5

        if distance <= 1e-6 or distance < min_reach or distance > max_reach:
            return JointAngles(round(coxa, 3), 90.0, 90.0, False, "OUT_OF_REACH")

        cos_knee = (
            self.FEMUR * self.FEMUR
            + self.TIBIA * self.TIBIA
            - distance * distance
        ) / (2.0 * self.FEMUR * self.TIBIA)
        cos_knee = max(-1.0, min(1.0, cos_knee))
        knee_internal = math.acos(cos_knee)

        femur_geometry = math.atan2(z, horizontal) + math.atan2(
            self.TIBIA * math.sin(knee_internal),
            self.FEMUR + self.TIBIA * math.cos(knee_internal),
        )

        femur = 90.0 + math.degrees(femur_geometry)
        tibia = 180.0 - math.degrees(knee_internal)

        valid = (
            self.COXA_MIN <= coxa <= self.COXA_MAX
            and self.FEMUR_MIN <= femur <= self.FEMUR_MAX
            and self.TIBIA_MIN <= tibia <= self.TIBIA_MAX
        )

        if not valid:
            return JointAngles(round(coxa, 3), round(femur, 3), round(tibia, 3), False, "JOINT_LIMIT")

        return JointAngles(round(coxa, 3), round(femur, 3), round(tibia, 3), True, "OK")

    def solve_all(self, targets):
        return {leg: self.solve(t.x, t.y, t.z) for leg, t in targets.items()}
