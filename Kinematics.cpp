#include "Kinematics.h"
#include "RobotConfig.h"
#include <math.h>

namespace {
constexpr float RAD_TO_DEG = 57.2957795131f;
}

Kinematics::Kinematics(float coxaLength, float femurLength, float tibiaLength)
    : coxaLength(coxaLength),
      femurLength(femurLength),
      tibiaLength(tibiaLength) {}

float Kinematics::clampFloat(float value, float minimum, float maximum) const
{
    if (value < minimum) return minimum;
    if (value > maximum) return maximum;
    return value;
}

JointAngles Kinematics::solve(float x, float y, float z) const
{
    JointAngles result{90.0f, 90.0f, 90.0f, false};

    // Coxa is represented as a servo angle around a 90 degree neutral.
    const float heading = atan2f(y, x) * RAD_TO_DEG;
    const float coxa = 90.0f + heading;

    const float radial = sqrtf(x * x + y * y);
    const float horizontal = radial - coxaLength;
    const float distance = sqrtf(horizontal * horizontal + z * z);

    const float minimumReach = fabsf(femurLength - tibiaLength) + 0.5f;
    const float maximumReach = femurLength + tibiaLength - 0.5f;

    if (distance < minimumReach || distance > maximumReach || distance <= 0.001f)
        return result;

    const float cosKnee = clampFloat(
        (femurLength * femurLength + tibiaLength * tibiaLength - distance * distance) /
        (2.0f * femurLength * tibiaLength),
        -1.0f, 1.0f
    );

    const float kneeInternal = acosf(cosKnee);

    const float femurGeometry =
        atan2f(z, horizontal) +
        atan2f(
            tibiaLength * sinf(kneeInternal),
            femurLength + tibiaLength * cosf(kneeInternal)
        );

    // Convert mathematical joint angles to 0..180 logical servo space.
    const float femur = 90.0f + femurGeometry * RAD_TO_DEG;
    const float tibia = 180.0f - kneeInternal * RAD_TO_DEG;

    result.coxa = clampFloat(coxa, RobotConfig::COXA_MIN_DEG, RobotConfig::COXA_MAX_DEG);
    result.femur = clampFloat(femur, RobotConfig::FEMUR_MIN_DEG, RobotConfig::FEMUR_MAX_DEG);
    result.tibia = clampFloat(tibia, RobotConfig::TIBIA_MIN_DEG, RobotConfig::TIBIA_MAX_DEG);

    // Clamping is only acceptable when the requested solution is already
    // inside the physical joint envelope; otherwise reject it.
    const bool withinLimits =
        coxa >= RobotConfig::COXA_MIN_DEG && coxa <= RobotConfig::COXA_MAX_DEG &&
        femur >= RobotConfig::FEMUR_MIN_DEG && femur <= RobotConfig::FEMUR_MAX_DEG &&
        tibia >= RobotConfig::TIBIA_MIN_DEG && tibia <= RobotConfig::TIBIA_MAX_DEG;

    result.valid = withinLimits;
    return result;
}
