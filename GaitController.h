#pragma once

#include <Arduino.h>

enum GaitLeg {
    GAIT_FL = 0,
    GAIT_FR = 1,
    GAIT_RL = 2,
    GAIT_RR = 3
};

struct FootTarget {
    float x;
    float y;
    float z;
    bool swing;
};

class GaitController {
public:
    GaitController();

    void reset();
    void setMode(const String& mode);
    void stop();

    void update(float dt);

    FootTarget target(GaitLeg leg) const;
    const char* mode() const;
    float phase() const;
    bool moving() const;

private:
    float phaseValue;
    float stepLength;
    float stepHeight;
    float bodyHeight;
    float frequency;
    bool active;
    String modeName;

    float legY(GaitLeg leg) const;
    float phaseOffset(GaitLeg leg) const;
    FootTarget calculate(GaitLeg leg) const;
};
