#pragma once

#include <Arduino.h>

struct CoreMissionState {
    String mode;
    bool active;
    bool personDetected;
    bool thermalSignature;
    bool healthy;
    uint32_t cycle;
};
