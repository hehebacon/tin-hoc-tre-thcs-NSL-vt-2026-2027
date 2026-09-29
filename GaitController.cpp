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
    : phaseValue(0),
      stepLengthValue(RobotConfig::DEFAULT_STEP_LENGTH_MM),
      stepHeightValue(RobotConfig::DEFAULT_STEP_HEIGHT_MM),
      frequencyValue(RobotConfig::DEFAULT_GAIT_FREQUENCY_HZ),
      targetStepLength(RobotConfig::DEFAULT_STEP_LENGTH_MM),
      targetStepHeight(RobotConfig::DEFAULT_STEP_HEIGHT_MM),
      targetFrequency(RobotConfig::DEFAULT_GAIT_FREQUENCY_HZ),
      bodyHeight(RobotConfig::DEFAULT_BODY_Z_MM),
      speedValue(0),
      targetSpeed(0),
      active(false),
      modeName("IDLE") {}

void GaitController::reset() {
    phaseValue = 0;
    stepLengthValue = targetStepLength = RobotConfig::DEFAULT_STEP_LENGTH_MM;
    stepHeightValue = targetStepHeight = RobotConfig::DEFAULT_STEP_HEIGHT_MM;
    frequencyValue = targetFrequency = RobotConfig::DEFAULT_GAIT_FREQUENCY_HZ;
    speedValue = targetSpeed = 0;
    active = false;
    modeName = "IDLE";
}

void GaitController::configure(float stepLength, float stepHeight, float frequency) {
    targetStepLength = fminf(stepLength, RobotConfig::MAX_STEP_LENGTH_MM);
    targetStepHeight = fminf(stepHeight, RobotConfig::MAX_STEP_HEIGHT_MM);
    targetFrequency = frequency;
    targetSpeed = 1.0f;
    active = true;
}

void GaitController::setMode(const String& mode) {
    String m = mode;
    m.trim();
    m.toUpperCase();

    if (m == "STABLE" || m == "STABLE_WALK") {
        configure(24, 18, 1.10f);
        modeName = "STABLE_WALK";
    } else if (m == "WALK" || m == "CRUISE") {
        configure(32, 20, 1.55f);
        modeName = (m == "CRUISE" ? "CRUISE" : "WALK");
    } else if (m == "FAST" || m == "FAST_WALK") {
        configure(42, 24, 1.90f);
        modeName = "FAST";
    } else if (m == "SLOW_WALK") {
        configure(20, 16, 0.95f);
        modeName = "SLOW_WALK";
    } else if (m == "SEARCH") {
        configure(18, 14, 0.80f);
        modeName = "SEARCH";
    } else if (m == "RESCUE") {
        configure(14, 12, 0.70f);
        modeName = "RESCUE";
    } else {
        reset();
    }
}

void GaitController::stop() {
    targetSpeed = 0;
    active = false;
    modeName = "IDLE";
}

void GaitController::update(float dt) {
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
        speedValue = 0;
        return;
    }

    phaseValue += dt * frequencyValue * speedValue;
    while (phaseValue >= 1.0f)
        phaseValue -= 1.0f;
}

float GaitController::legY(GaitLeg leg) const {
    constexpr float HALF_BODY_WIDTH = RobotConfig::BODY_WIDTH_MM * 0.5f;
    return (leg == GAIT_FL || leg == GAIT_RL)
        ? HALF_BODY_WIDTH
        : -HALF_BODY_WIDTH;
}

float GaitController::phaseOffset(GaitLeg leg) const {
    // Diagonal tripod groups: FL+RR / FR+RL.
    return (leg == GAIT_FL || leg == GAIT_RR) ? 0.0f : 0.5f;
}

FootTarget GaitController::calculate(GaitLeg leg) const {
    const float y = legY(leg);
    const float centerX = 0.0f;
    const float phase = phaseValue - phaseOffset(leg);
    const bool mirrored = (leg == GAIT_FR || leg == GAIT_RL);

    TrajectoryPoint p = FootTrajectory::tripod(
        phase,
        centerX,
        y,
        bodyHeight,
        stepLengthValue * speedValue,
        stepHeightValue * speedValue,
        mirrored
    );

    FootTarget result;
    result.x = p.x;
    result.y = p.y;
    result.z = p.z;
    result.swing = p.swing;
    return result;
}

FootTarget GaitController::target(GaitLeg leg) const { return calculate(leg); }
const char* GaitController::mode() const { return modeName.c_str(); }
float GaitController::phase() const { return phaseValue; }
bool GaitController::moving() const { return speedValue > 0.001f; }
float GaitController::speedScale() const { return speedValue; }
float GaitController::stepLength() const { return stepLengthValue; }
float GaitController::stepHeight() const { return stepHeightValue; }
float GaitController::frequency() const { return frequencyValue; }
