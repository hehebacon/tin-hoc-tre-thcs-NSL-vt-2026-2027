#include "FootTrajectory.h"

namespace {
constexpr float HALF_PI = 1.57079632679f;
}

float FootTrajectory::smoothStep5(float t)
{
    if (t < 0.0f) t = 0.0f;
    if (t > 1.0f) t = 1.0f;
    return t * t * t * (t * (t * 6.0f - 15.0f) + 10.0f);
}

float FootTrajectory::swingHeight(float t)
{
    if (t < 0.0f) t = 0.0f;
    if (t > 1.0f) t = 1.0f;
    // Zero velocity at lift-off and touchdown.
    return sinf(t * 3.14159265359f);
}

TrajectoryPoint FootTrajectory::tripod(
    float phase,
    float centerX,
    float centerY,
    float groundZ,
    float stepLength,
    float stepHeight,
    bool mirrored
)
{
    while (phase < 0.0f) phase += 1.0f;
    while (phase >= 1.0f) phase -= 1.0f;

    if (mirrored)
        phase += 0.5f;
    if (phase >= 1.0f)
        phase -= 1.0f;

    TrajectoryPoint p;
    p.x = centerX;
    p.y = centerY;
    p.z = groundZ;

    if (phase < 0.5f) {
        // Swing: use quintic easing for a softer start/end.
        const float t = phase * 2.0f;
        const float e = smoothStep5(t);
        p.x = centerX - stepLength * 0.5f + e * stepLength;
        p.z = groundZ + swingHeight(t) * stepHeight;
        p.swing = true;
    } else {
        // Stance: move the foot backward relative to the body.
        const float t = (phase - 0.5f) * 2.0f;
        const float e = smoothStep5(t);
        p.x = centerX + stepLength * 0.5f - e * stepLength;
        p.swing = false;
    }

    return p;
}
