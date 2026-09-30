#include "MotionController.h"
#include "EnvironmentalSensors.h"
#include "ImuInterface.h"
#include "MotionSet.h"
#include "SafetyManager.h"
#include <math.h>

static EnvironmentalSensors environment;
static ImuInterface imu;
static MotionSet motionSet;
static SafetyManager safetyManager;

const uint8_t MotionController::SERVO_MAP[LEG_COUNT][3] = {
    {RobotConfig::SERVO_FL_COXA, RobotConfig::SERVO_FL_FEMUR, RobotConfig::SERVO_FL_TIBIA},
    {RobotConfig::SERVO_FR_COXA, RobotConfig::SERVO_FR_FEMUR, RobotConfig::SERVO_FR_TIBIA},
    {RobotConfig::SERVO_RL_COXA, RobotConfig::SERVO_RL_FEMUR, RobotConfig::SERVO_RL_TIBIA},
    {RobotConfig::SERVO_RR_COXA, RobotConfig::SERVO_RR_FEMUR, RobotConfig::SERVO_RR_TIBIA}
};

const char* const MotionController::LEG_NAMES[LEG_COUNT] = {"FL", "FR", "RL", "RR"};

MotionController::MotionController()
    : kinematics(RobotConfig::COXA_MM, RobotConfig::FEMUR_MM, RobotConfig::TIBIA_MM),
      jumpPhase(JumpPhase::IDLE), jumpPhaseStartedMs(0), jumpActive(false) {
    resetLegStates();
}

void MotionController::begin() {
    calibrator.begin();
    servoManager.begin();
    environment.begin();
    imu.begin();
    gaitController.reset();
    motionSet.reset();
    safetyManager.reset();
    resetLegStates();
    jumpPhase = JumpPhase::IDLE;
    jumpActive = false;
    Serial.println("[MOTION] 35cm motion stack initialized");
}

void MotionController::update(float dt) {
    motionSet.update(dt);
    if (!safetyManager.canMove()) return;

    if (jumpActive) {
        updateJump();
        return;
    }

    if (!gaitController.moving()) return;
    gaitController.update(dt);

    for (uint8_t i = 0; i < LEG_COUNT; ++i) {
        const FootTarget target = gaitController.target(static_cast<GaitLeg>(i));
        setFootTarget(static_cast<LegID>(i), target.x, target.y, target.z);
    }
}

void MotionController::resetLegStates() {
    for (uint8_t i = 0; i < LEG_COUNT; ++i)
        legs[i] = {RobotConfig::DEFAULT_SERVO_DEG, RobotConfig::DEFAULT_SERVO_DEG, RobotConfig::DEFAULT_SERVO_DEG};
}

int MotionController::parseLeg(const String& name) const {
    String n = name;
    n.trim();
    n.toUpperCase();
    if (n == "FL") return FL;
    if (n == "FR") return FR;
    if (n == "RL") return RL;
    if (n == "RR") return RR;
    return -1;
}

void MotionController::setServo(int channel, int rawAngle) {
    if (!servoManager.validChannel(channel) || !safetyManager.canMove()) return;
    if (!safetyManager.validateServoAngle(rawAngle)) return;

    const int calibrated = calibrator.apply(channel, rawAngle);
    if (!safetyManager.validateServoAngle(calibrated)) return;
    servoManager.setAngle(channel, calibrated);
}

bool MotionController::setLeg(LegID leg, int coxa, int femur, int tibia) {
    if (leg < FL || leg > RR || !safetyManager.canMove()) return false;
    if (!safetyManager.validateServoAngle(coxa) ||
        !safetyManager.validateServoAngle(femur) ||
        !safetyManager.validateServoAngle(tibia)) return false;

    legs[leg] = {static_cast<float>(coxa), static_cast<float>(femur), static_cast<float>(tibia)};
    setServo(SERVO_MAP[leg][0], coxa);
    setServo(SERVO_MAP[leg][1], femur);
    setServo(SERVO_MAP[leg][2], tibia);
    return true;
}

bool MotionController::setLeg(const String& name, int coxa, int femur, int tibia) {
    const int leg = parseLeg(name);
    return leg >= 0 && setLeg(static_cast<LegID>(leg), coxa, femur, tibia);
}

bool MotionController::solveIK(float x, float y, float z, JointAngles& result) const {
    result = kinematics.solve(x, y, z);
    return result.valid;
}

bool MotionController::validateFootTarget(float x, float y, float z) const {
    return safetyManager.validateFootTarget(x, y, z);
}

bool MotionController::setFootTarget(LegID leg, float x, float y, float z) {
    if (leg < FL || leg > RR || !safetyManager.canMove()) return false;
    if (!validateFootTarget(x, y, z)) return false;

    JointAngles result;
    if (!solveIK(x, y, z, result)) return false;

    return setLeg(leg,
        static_cast<int>(lroundf(result.coxa)),
        static_cast<int>(lroundf(result.femur)),
        static_cast<int>(lroundf(result.tibia)));
}

bool MotionController::setFootTarget(const String& name, float x, float y, float z) {
    const int leg = parseLeg(name);
    return leg >= 0 && setFootTarget(static_cast<LegID>(leg), x, y, z);
}

bool MotionController::setLegIK(LegID leg, float x, float y, float z) {
    return setFootTarget(leg, x, y, z);
}

bool MotionController::setLegIK(const String& name, float x, float y, float z) {
    return setFootTarget(name, x, y, z);
}

void MotionController::testIK(float x, float y, float z) const {
    JointAngles a;
    if (!solveIK(x, y, z, a)) {
        Serial.printf("[IK] INVALID target %.1f %.1f %.1f\n", x, y, z);
        return;
    }
    Serial.printf("[IK] %.1f %.1f %.1f -> C=%.1f F=%.1f T=%.1f\n", x, y, z, a.coxa, a.femur, a.tibia);
}

void MotionController::setGait(const String& mode) {
    gaitController.setMode(mode);
    motionSet.setAction(MotionSet::Action::WALK_FORWARD);
}

void MotionController::stopGait() {
    gaitController.stop();
    motionSet.stop();
}

const GaitController& MotionController::gait() const { return gaitController; }
bool MotionController::jumping() const { return jumpActive; }

void MotionController::center() {
    if (!safetyManager.canMove()) return;
    for (uint8_t i = 0; i < LEG_COUNT; ++i)
        setLeg(static_cast<LegID>(i), 90, 90, 90);
}

void MotionController::stand() {
    motionSet.setPose(MotionSet::Pose::STAND);
    if (!safetyManager.canMove()) return;

    const float x = RobotConfig::BODY_LENGTH_MM * 0.5f;
    const float y = RobotConfig::BODY_WIDTH_MM * 0.5f;
    for (uint8_t i = 0; i < LEG_COUNT; ++i) {
        const float sx = (i == FL || i == FR) ? x : -x;
        const float sy = (i == FL || i == RL) ? y : -y;
        setFootTarget(static_cast<LegID>(i), sx, sy, RobotConfig::DEFAULT_BODY_Z_MM);
    }
}

void MotionController::enable() {
    safetyManager.enable();
    servoManager.enableAll();
}

void MotionController::disable() {
    gaitController.stop();
    motionSet.stop();
    safetyManager.disable();
    servoManager.disableAll();
}

void MotionController::jump() {
    if (!safetyManager.canMove() || jumpActive) return;
    jumpActive = true;
    jumpPhase = JumpPhase::CROUCH;
    jumpPhaseStartedMs = millis();
}

float MotionController::jumpPhaseProgress(unsigned long elapsed, unsigned long duration) const {
    if (duration == 0) return 1.0f;
    return fminf(1.0f, static_cast<float>(elapsed) / static_cast<float>(duration));
}

void MotionController::applyJumpPose(float z) {
    const float x = RobotConfig::BODY_LENGTH_MM * 0.5f;
    const float y = RobotConfig::BODY_WIDTH_MM * 0.5f;
    for (uint8_t i = 0; i < LEG_COUNT; ++i) {
        const float sx = (i == FL || i == FR) ? x : -x;
        const float sy = (i == FL || i == RL) ? y : -y;
        setFootTarget(static_cast<LegID>(i), sx, sy, z);
    }
}

void MotionController::updateJump() {
    const unsigned long elapsed = millis() - jumpPhaseStartedMs;
    unsigned long duration = 160;
    float z = RobotConfig::DEFAULT_BODY_Z_MM;

    switch (jumpPhase) {
        case JumpPhase::CROUCH: duration = 180; z = -70.0f; break;
        case JumpPhase::LOAD: duration = 100; z = -78.0f; break;
        case JumpPhase::PUSH: duration = 120; z = -105.0f; break;
        case JumpPhase::FLIGHT: duration = 180; z = -115.0f; break;
        case JumpPhase::TUCK: duration = 100; z = -105.0f; break;
        case JumpPhase::LAND: duration = 140; z = -82.0f; break;
        case JumpPhase::ABSORB: duration = 120; z = -78.0f; break;
        case JumpPhase::RECOVER: duration = 180; z = RobotConfig::DEFAULT_BODY_Z_MM; break;
        default: finishJump(); return;
    }

    applyJumpPose(z);
    if (elapsed < duration) return;

    switch (jumpPhase) {
        case JumpPhase::CROUCH: jumpPhase = JumpPhase::LOAD; break;
        case JumpPhase::LOAD: jumpPhase = JumpPhase::PUSH; break;
        case JumpPhase::PUSH: jumpPhase = JumpPhase::FLIGHT; break;
        case JumpPhase::FLIGHT: jumpPhase = JumpPhase::TUCK; break;
        case JumpPhase::TUCK: jumpPhase = JumpPhase::LAND; break;
        case JumpPhase::LAND: jumpPhase = JumpPhase::ABSORB; break;
        case JumpPhase::ABSORB: jumpPhase = JumpPhase::RECOVER; break;
        case JumpPhase::RECOVER: finishJump(); return;
        default: finishJump(); return;
    }
    jumpPhaseStartedMs = millis();
}

void MotionController::finishJump() {
    jumpActive = false;
    jumpPhase = JumpPhase::IDLE;
    stand();
}

void MotionController::status() const {
    Serial.printf("[MOTION] safety=%s estop=%s gait=%s phase=%.3f step=%.1f/%.1f\n",
        safetyManager.enabled() ? "ON" : "OFF",
        safetyManager.emergency() ? "YES" : "NO",
        gaitController.mode(), gaitController.phase(), gaitController.stepLength(), gaitController.stepHeight());
}

void MotionController::debug() const {
    status();
    for (uint8_t i = 0; i < LEG_COUNT; ++i)
        Serial.printf("[%s] C=%.1f F=%.1f T=%.1f\n", LEG_NAMES[i], legs[i].coxa, legs[i].femur, legs[i].tibia);
}

void MotionController::printCalibration() const { calibrator.printAll(); }
void MotionController::printCalibration(int channel) const { calibrator.print(channel); }
void MotionController::setCalibrationOffset(int channel, int offset) { calibrator.setOffset(channel, offset); }
void MotionController::setCalibrationInvert(int channel, bool invert) { calibrator.setInvert(channel, invert); }
void MotionController::setCalibrationLimits(int channel, int minimum, int maximum) { calibrator.setLimits(channel, minimum, maximum); }

const LegState& MotionController::getLegState(LegID leg) const {
    static const LegState invalid{};
    if (leg < FL || leg > RR) return invalid;
    return legs[leg];
}
