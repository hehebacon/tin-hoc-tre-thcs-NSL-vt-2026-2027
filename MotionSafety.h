#pragma once

#include <Arduino.h>
#include "HardwareConfig.h"

class MotionSafety {
public:
    void begin();
    void emergencyStop();
    void resume();
    bool allowed() const;
    bool timedOut() const;
    void noteMotionCommand();
    void clearMotion();

private:
    bool stopped = false;
    unsigned long lastMotionMs = 0;
    bool motionActive = false;
};
