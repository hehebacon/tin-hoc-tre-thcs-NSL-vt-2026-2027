#pragma once

#include <Arduino.h>

// ============================================================
// INVERSE KINEMATICS
// ============================================================

struct JointAngles {
    float coxa;
    float femur;
    float tibia;
    bool valid;
};

class Kinematics {
public:
    Kinematics(
        float coxaLength,
        float femurLength,
        float tibiaLength
    );

    JointAngles solve(
        float x,
        float y,
        float z
    ) const;

private:
    float coxaLength;
    float femurLength;
    float tibiaLength;

    float clampFloat(
        float value,
        float minimum,
        float maximum
    ) const;
};
