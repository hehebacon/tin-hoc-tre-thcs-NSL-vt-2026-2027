#include "MotionSafety.h"

void MotionSafety::begin()
{
    stopped = false;
    lastMotionMs = millis();
    motionActive = false;
}

void MotionSafety::clearMotion()
{
    motionActive = false;
}

void MotionSafety::emergencyStop()
{
    stopped = true;
}

void MotionSafety::resume()
{
    stopped = false;
    lastMotionMs = millis();
    motionActive = false;
}

bool MotionSafety::allowed() const
{
    return !stopped && !timedOut();
}

bool MotionSafety::timedOut() const
{
    if (!motionActive) return false;
    return (millis() - lastMotionMs) > MOTION_TIMEOUT_MS;
}

void MotionSafety::noteMotionCommand()
{
    lastMotionMs = millis();
    motionActive = false;
}
