#pragma once

#include <Arduino.h>

struct HardwareStatus {
    bool pca9685;
    bool imu;
    bool environmental;
    bool camera;
    bool thermal;
    bool network;
    bool motionSafety;
};

String hardwareStatusJson(const HardwareStatus& status);
