#include "GaitController.h"
#include "RobotConfig.h"
#include "FootTrajectory.h"
#include <math.h>

namespace {
constexpr float RAMP_RATE = 2.5f;
constexpr float PARAM_RATE = 4.0f;
constexpr float MIN_DT = 0.001f;
constexpr float MAX_DT = 0.10f;
}

GaitController::GaitController()
    : phaseValue(0.0f),
      stepLengthValue(RobotConfig::DEFAULT_STEP_LENGTH_MM),
      stepHeightValue(RobotConfig::DEFAULT_STEP_HEIGHT_MM),
      frequencyValue(RobotConfig::DEFAULT_GAIT_FREQUENCY_HZ),
      targetStepLength(RobotConfig::DEFAULT_STEP_LENGTH_MM),
      targetStepHeight(RobotConfig::DEFAULT_STEP_HEIGHT_MM),
      targetFrequency(RobotConfig::DEFAULT_GAIT_FREQUENCY_HZ),
      bodyHeight(RobotConfig::DEFAULT_BODY_Z_MM),
      speedValue(0.0f),
      targetSpeed(0.0f),
      active(false),
      modeName("IDLE") {}

void GaitController::reset()
{
    phaseValue = 0.0f;
    stepLengthValue = targetStepLength = RobotConfig::DEFAULT_STEP_LENGTH_MM;
    stepHeightValue = targetStepHeight = RobotConfig::DEFAULT_STEP_HEIGHT_MM;
    frequencyValue = targetFrequency = RobotConfig::DEFAULT_GAIT_FREQUENCY_HZ;
    bodyHeight = RobotConfig::DEFAULT_BODY_Z_MM;
    speedValue = targetSpeed = 0.0f;
    active = false;
    modeName = "IDLE";
}

void GaitController::configure(float stepLength, float stepHeight, float frequency)
{
    targetStepLength = fmaxf(0.0f, fminf(stepLength, RobotConfig::MAX_STEP_LENGTH_MM));
    targetStepHeight = fmaxf(0.0f, fminf(stepHeight, RobotConfig::MAX_STEP_HEIGHT_MM));
    targetFrequency = fmaxf(0.1f, fminf(frequency, RobotConfig::MAX_GAIT_FREQUENCY_HZ));
    targetSpeed = RobotConfig::MAX_COMMAND_SPEED_SCALE;
    active = true;
}

void GaitController::setMode(const String& mode)
{
    String m = mode;
    m.trim();
    m.toUpperCase();

    if (m == "STABLE" || m == "STABLE_WALK") {
        configure(24.0f, 16.0f, 1.00f);
        modeName = "STABLE_WALK";
    } else if (m == "WALK" || m == "CRUISE") {
        configure(30.0f, 18.0f, 1.35f);
        modeName = (m == "CRUISE" ? "CRUISE" : "WALK");
    } else if (m == "FAST" || m == "FAST_WALK") {
        configure(38.0f, 22.0f, 1.80f);
        modeName = "FAST";
    } else if (m == "SLOW_WALK") {
        configure(18.0f, 14.0f, 0.80f);
        modeName = "SLOW_WALK";
    } else if (m == "SEARCH") {
        configure(16.0f, 12.0f, 0.70f);
        modeName = "SEARCH";
    } else if (m == "RESCUE") {
        configure(14.0f, 11.0f, 0.60f);
        modeName = "RESCUE";
    } else {
        reset();
    }
}

void GaitController::stop()
{
    targetSpeed = 0.0f;
    active = false;
    modeName = "IDLE";
}

void GaitController::update(float dt)
{
    dt = fmaxf(MIN_DT, fminf(dt, MAX_DT));
    const float blend = fminf(1.0f, dt * PARAM_RATE);

    stepLengthValue += (targetStepLength - stepLengthValue) * blend;
    stepHeightValue += (targetStepHeight - stepHeightValue) * blend;
    frequencyValue += (targetFrequency - frequencyValue) * blend;

    const float ramp = RAMP_RATE * dt;
    if (speedValue < targetSpeed)
        speedValue = fminf(targetSpeed, speedValue + ramp);
    else
        speedValue = fmaxf(targetSpeed, speedValue - ramp);

    if (speedValue <= 0.001f) {
        speedValue = 0.0f;
        return;
    }

    phaseValue += dt * frequencyValue * speedValue;
    while (phaseValue >= 1.0f) phaseValue -= 1.0f;
    while (phaseValue < 0.0f) phaseValue += 1.0f;
}

float GaitController::legY(GaitLeg leg) const
{
    const float halfWidth = RobotConfig::BODY_WIDTH_MM * 0.5f;
    return (leg == GAIT_FL || leg == GAIT_RL) ? halfWidth : -halfWidth;
}

float GaitController::phaseOffset(GaitLeg leg) const
{
    // True diagonal tripod: FL+RR / FR+RL.
    return (leg == GAIT_FL || leg == GAIT_RR) ? 0.0f : 0.5f;
}

FootTarget GaitController::calculate(GaitLeg leg) const
{
    const float halfLength = RobotConfig::BODY_LENGTH_MM * 0.5f;
    const float centerX = (leg == GAIT_FL || leg == GAIT_FR) ? halfLength : -halfLength;
    const float phase = phaseValue - phaseOffset(leg);

    // phaseOffset already creates the diagonal gait; do not apply a second mirror offset.
    const TrajectoryPoint p = FootTrajectory::tripod(
        phase,
        centerX,
        legY(leg),
        bodyHeight,
        stepLengthValue * speedValue,
        stepHeightValue * speedValue,
        false
    );

    return {p.x, p.y, p.z, p.swing};
}

FootTarget GaitController::target(GaitLeg leg) const { return calculate(leg); }
const char* GaitController::mode() const { return modeName.c_str(); }
float GaitController::phase() const { return phaseValue; }
bool GaitController::moving() const { return speedValue > 0.001f; }
float GaitController::speedScale() const { return speedValue; }
float GaitController::stepLength() const { return stepLengthValue; }
float GaitController::stepHeight() const { return stepHeightValue; }
float GaitController::frequency() const { return frequencyValue; }
