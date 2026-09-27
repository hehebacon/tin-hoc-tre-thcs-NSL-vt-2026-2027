#pragma once

#include <Arduino.h>
#include "HardwareConfig.h"

class PCA9685ServoDriver {
public:
    bool begin();
    bool available() const;
    void setAngle(uint8_t channel, int angle);
    void disableAll();

private:
    bool ready = false;
};
