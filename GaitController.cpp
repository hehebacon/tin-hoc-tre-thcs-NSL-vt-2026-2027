#include "GaitController.h"

#include <math.h>

GaitController::GaitController()
    : phaseValue(0.0f),
      stepLength(0.0f),
      stepHeight(0.0f),
      bodyHeight(-90.0f),
      frequency(1.5f),
      active(false),
      modeName("IDLE")
{
}

void GaitController::reset()
{
    phaseValue = 0.0f;
    stepLength = 0.0f;
    stepHeight = 0.0f;
    frequency = 1.5f;
    active = false;
    modeName = "IDLE";
}

void GaitController::setMode(const String& mode)
{
    String normalized = mode;
    normalized.trim();
    normalized.toUpperCase();

    if (normalized == "WALK") {
        stepLength = 30.0f;
        stepHeight = 22.0f;
        frequency = 1.5f;
        active = true;
        modeName = "WALK";
    } else if (normalized == "SLOW_WALK") {
        stepLength = 20.0f;
        stepHeight = 16.0f;
        frequency = 1.0f;
        active = true;
        modeName = "SLOW_WALK";
    } else if (normalized == "SEARCH") {
        stepLength = 18.0f;
        stepHeight = 14.0f;
        frequency = 0.8f;
        active = true;
        modeName = "SEARCH";
    } else if (normalized == "RESCUE") {
        stepLength = 14.0f;
        stepHeight = 12.0f;
        frequency = 0.7f;
        active = true;
        modeName = "RESCUE";
    } else {
        reset();
    }
}

void GaitController::stop()
{
    active = false;
    stepLength = 0.0f;
    stepHeight = 0.0f;
    modeName = "IDLE";
}

void GaitController::update(float dt)
{
    if (!active)
        return;

    if (dt < 0.0f)
        dt = 0.0f;

    phaseValue += dt * frequency;

    while (phaseValue >= 1.0f)
        phaseValue -= 1.0f;
}

float GaitController::legY(GaitLeg leg) const
{
    return (leg == GAIT_FL || leg == GAIT_RL) ? 45.0f : -45.0f;
}

float GaitController::phaseOffset(GaitLeg leg) const
{
    return (leg == GAIT_FL || leg == GAIT_RR) ? 0.0f : 0.5f;
}

FootTarget GaitController::calculate(GaitLeg leg) const
{
    FootTarget result = {0.0f, legY(leg), bodyHeight, false};

    if (!active)
        return result;

    float local = phaseValue - phaseOffset(leg);
    while (local < 0.0f)
        local += 1.0f;
    while (local >= 1.0f)
        local -= 1.0f;

    if (local < 0.5f) {
        const float progress = local / 0.5f;
        result.x =
            -stepLength * 0.5f +
            progress * stepLength;

        result.z =
            bodyHeight +
            stepHeight * sinf(progress * PI);

        result.swing = true;
    } else {
        const float progress = (local - 0.5f) / 0.5f;
        result.x =
            stepLength * 0.5f -
            progress * stepLength;

        result.z = bodyHeight;
        result.swing = false;
    }

    return result;
}

FootTarget GaitController::target(GaitLeg leg) const
{
    return calculate(leg);
}

const char* GaitController::mode() const
{
    return modeName.c_str();
}

float GaitController::phase() const
{
    return phaseValue;
}

bool GaitController::moving() const
{
    return active;
}
