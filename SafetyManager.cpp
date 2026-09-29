#include "SafetyManager.h"
#include <math.h>

SafetyManager::SafetyManager()
    : enabled_(false), emergencyStop_(false) {}

void SafetyManager::reset()
{
    enabled_ = false;
    emergencyStop_ = false;
}

void SafetyManager::enable()
{
    if (!emergencyStop_)
        enabled_ = true;
}

void SafetyManager::disable()
{
    enabled_ = false;
}

void SafetyManager::emergencyStop()
{
    emergencyStop_ = true;
    enabled_ = false;
}

void SafetyManager::clearEmergencyStop()
{
    emergencyStop_ = false;
}

bool SafetyManager::canMove() const
{
    return enabled_ && !emergencyStop_;
}

bool SafetyManager::validateServoAngle(float angle) const
{
    return angle >= RobotConfig::SERVO_MIN_DEG &&
           angle <= RobotConfig::SERVO_MAX_DEG;
}

bool SafetyManager::validateFootTarget(float x, float y, float z) const
{
    const float radius = sqrtf(x * x + y * y);
    return radius >= RobotConfig::FOOT_MIN_RADIUS_MM &&
           radius <= RobotConfig::FOOT_MAX_RADIUS_MM &&
           z >= RobotConfig::FOOT_MIN_Z_MM &&
           z <= RobotConfig::FOOT_MAX_Z_MM;
}

bool SafetyManager::validateStep(float length, float height) const
{
    return length >= 0.0f &&
           height >= 0.0f &&
           length <= RobotConfig::MAX_STEP_LENGTH_MM &&
           height <= RobotConfig::MAX_STEP_HEIGHT_MM;
}

float SafetyManager::clampServoAngle(float angle) const
{
    if (angle < RobotConfig::SERVO_MIN_DEG)
        return RobotConfig::SERVO_MIN_DEG;
    if (angle > RobotConfig::SERVO_MAX_DEG)
        return RobotConfig::SERVO_MAX_DEG;
    return angle;
}

float SafetyManager::clampStepLength(float length) const
{
    if (length < 0.0f) return 0.0f;
    if (length > RobotConfig::MAX_STEP_LENGTH_MM)
        return RobotConfig::MAX_STEP_LENGTH_MM;
    return length;
}

float SafetyManager::clampStepHeight(float height) const
{
    if (height < 0.0f) return 0.0f;
    if (height > RobotConfig::MAX_STEP_HEIGHT_MM)
        return RobotConfig::MAX_STEP_HEIGHT_MM;
    return height;
}

bool SafetyManager::enabled() const { return enabled_; }
bool SafetyManager::emergency() const { return emergencyStop_; }
