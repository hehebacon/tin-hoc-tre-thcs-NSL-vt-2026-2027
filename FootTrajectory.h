#pragma once

#include <math.h>

struct TrajectoryPoint {
    float x = 0.0f;
    float y = 0.0f;
    float z = 0.0f;
    bool swing = false;
};

class FootTrajectory {
public:
    // Smooth swing/stance trajectory using quintic easing.
    // phase is normalized to [0, 1).
    static TrajectoryPoint tripod(
        float phase,
        float centerX,
        float centerY,
        float groundZ,
        float stepLength,
        float stepHeight,
        bool mirrored = false
    );

    static float smoothStep5(float t);
    static float swingHeight(float t);
};
