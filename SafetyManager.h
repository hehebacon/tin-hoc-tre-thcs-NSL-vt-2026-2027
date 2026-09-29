#pragma once

#include "RobotConfig.h"

class SafetyManager {
public:
    SafetyManager();

    void reset();
    void enable();
    void disable();
    void emergencyStop();
    void clearEmergencyStop();

    bool canMove() const;

    bool validateServoAngle(float angle) const;
    bool validateFootTarget(float x, float y, float z) const;
    bool validateStep(float length, float height) const;

    float clampServoAngle(float angle) const;
    float clampStepLength(float length) const;
    float clampStepHeight(float height) const;

    bool enabled() const;
    bool emergency() const;

private:
    bool enabled_;
    bool emergencyStop_;
};
