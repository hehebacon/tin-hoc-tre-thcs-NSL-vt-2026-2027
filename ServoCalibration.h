#pragma once

#include <Arduino.h>
#include "config.h"

// ============================================================
// PER-SERVO CALIBRATION
// ============================================================

struct ServoCalibration {
    int offset;
    bool invert;
    int minAngle;
    int maxAngle;
};

class ServoCalibrator {
public:
    void begin();

    int apply(
        int channel,
        int angle
    );

    void setOffset(
        int channel,
        int offset
    );

    void setInvert(
        int channel,
        bool invert
    );

    void setLimits(
        int channel,
        int minimum,
        int maximum
    );

    void print(int channel) const;
    void printAll() const;

private:
    ServoCalibration data[SERVO_COUNT];

    bool validChannel(int channel) const;

    int clamp(
        int value,
        int minimum,
        int maximum
    ) const;
};
