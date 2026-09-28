#pragma once

#include <Arduino.h>

enum GaitLeg { GAIT_FL=0, GAIT_FR=1, GAIT_RL=2, GAIT_RR=3 };

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
    float speedScale() const;
    float stepLength() const;
    float stepHeight() const;
    float frequency() const;
private:
    float phaseValue, stepLengthValue, stepHeightValue, frequencyValue;
    float targetStepLength, targetStepHeight, targetFrequency;
    float bodyHeight, speedValue, targetSpeed;
    bool active;
    String modeName;
    float legY(GaitLeg leg) const;
    float phaseOffset(GaitLeg leg) const;
    FootTarget calculate(GaitLeg leg) const;
    void configure(float stepLength, float stepHeight, float frequency);
};