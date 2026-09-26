#pragma once

#include <Arduino.h>
#include "config.h"

// ============================================================
// SERVO MANAGER
//
// Current stage: simulation / serial debug.
// PCA9685 output is deliberately isolated here so hardware
// can be added later without changing IK or calibration.
// ============================================================

class ServoManager {
public:
    void begin();

    bool validChannel(int channel) const;

    void setAngle(
        int channel,
        int angle
    );

    int getAngle(int channel) const;

    void centerAll();

    void enableAll();
    void disableAll();

    void status() const;

private:
    int angles[SERVO_COUNT];
    bool enabled[SERVO_COUNT];

    int clampAngle(int angle) const;
};
