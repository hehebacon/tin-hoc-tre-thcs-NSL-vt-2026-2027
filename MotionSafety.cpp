#include "MotionSafety.h"

void MotionSafety::begin()
{
    stopped = false;
    lastMotionMs = millis();
}

void MotionSafety::emergencyStop()
{
    stopped = true;
}

void MotionSafety::resume()
{
    stopped = false;
    lastMotionMs = millis();
}

bool MotionSafety::allowed() const
{
    return !stopped && !timedOut();
}

bool MotionSafety::timedOut() const
{
    return (millis() - lastMotionMs) > MOTION_TIMEOUT_MS;
}

void MotionSafety::noteMotionCommand()
{
    lastMotionMs = millis();
}
