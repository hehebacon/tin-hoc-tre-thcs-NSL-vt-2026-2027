#include "Kinematics.h"

#include <math.h>

// ============================================================
// CONSTRUCTOR
// ============================================================

Kinematics::Kinematics(
    float coxaLength,
    float femurLength,
    float tibiaLength
)
    : coxaLength(coxaLength),
      femurLength(femurLength),
      tibiaLength(tibiaLength)
{
}

// ============================================================
// CLAMP
// ============================================================

float Kinematics::clampFloat(
    float value,
    float minimum,
    float maximum
) const
{
    if (value < minimum)
        return minimum;

    if (value > maximum)
        return maximum;

    return value;
}

// ============================================================
// SOLVE
//
// Coordinate convention used by this software model:
// X = forward/back
// Y = left/right
// Z = up/down
//
// This calculates a simple 3-DOF leg solution:
//   coxa  = horizontal heading
//   femur = shoulder elevation
//   tibia = knee angle
//
// Mechanical servo orientation is handled separately by
// ServoCalibration.
// ============================================================

JointAngles Kinematics::solve(
    float x,
    float y,
    float z
) const
{
    JointAngles result{};
    result.valid = false;

    const float coxaAngle =
        atan2f(y, x) * 180.0f / PI;

    const float horizontal =
        sqrtf(
            x * x +
            y * y
        ) - coxaLength;

    const float distance =
        sqrtf(
            horizontal * horizontal +
            z * z
        );

    const float minimumReach =
        fabsf(femurLength - tibiaLength);

    const float maximumReach =
        femurLength + tibiaLength;

    if (
        distance < minimumReach ||
        distance > maximumReach ||
        distance <= 0.001f
    ) {
        result.coxa = coxaAngle;
        result.femur = 0;
        result.tibia = 0;
        return result;
    }

    const float cosKnee =
        clampFloat(
            (
                femurLength * femurLength +
                tibiaLength * tibiaLength -
                distance * distance
            ) /
            (
                2.0f *
                femurLength *
                tibiaLength
            ),
            -1.0f,
            1.0f
        );

    const float kneeInternal =
        acosf(cosKnee);

    const float femurAngle =
        atan2f(z, horizontal) +
        atan2f(
            tibiaLength * sinf(kneeInternal),
            femurLength +
            tibiaLength * cosf(kneeInternal)
        );

    result.coxa =
        coxaAngle;

    result.femur =
        femurAngle * 180.0f / PI;

    // Convert internal knee geometry to a servo-friendly
    // joint representation. Calibration maps this to the
    // actual mechanical orientation later.
    result.tibia =
        180.0f -
        kneeInternal * 180.0f / PI;

    result.valid = true;

    return result;
}
