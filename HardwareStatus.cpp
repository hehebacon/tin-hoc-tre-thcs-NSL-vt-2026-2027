#include "HardwareStatus.h"

String hardwareStatusJson(const HardwareStatus& status)
{
    String out = "{";
    out += "\"pca9685\":" + String(status.pca9685 ? "true" : "false");
    out += ",\"imu\":" + String(status.imu ? "true" : "false");
    out += ",\"environmental\":" + String(status.environmental ? "true" : "false");
    out += ",\"camera\":" + String(status.camera ? "true" : "false");
    out += ",\"thermal\":" + String(status.thermal ? "true" : "false");
    out += ",\"network\":" + String(status.network ? "true" : "false");
    out += ",\"motion_safety\":" + String(status.motionSafety ? "true" : "false");
    out += "}";
    return out;
}
