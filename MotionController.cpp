#include "MotionController.h"
#include "EnvironmentalSensors.h"
#include "ImuInterface.h"
#include "RobotConfig.h"

static EnvironmentalSensors environment;
static ImuInterface imu;

const uint8_t MotionController::SERVO_MAP[LEG_COUNT][3] = {
    {RobotConfig::SERVO_FL_COXA, RobotConfig::SERVO_FL_FEMUR, RobotConfig::SERVO_FL_TIBIA},
    {RobotConfig::SERVO_FR_COXA, RobotConfig::SERVO_FR_FEMUR, RobotConfig::SERVO_FR_TIBIA},
    {RobotConfig::SERVO_RL_COXA, RobotConfig::SERVO_RL_FEMUR, RobotConfig::SERVO_RL_TIBIA},
    {RobotConfig::SERVO_RR_COXA, RobotConfig::SERVO_RR_FEMUR, RobotConfig::SERVO_RR_TIBIA}
};

const char* const MotionController::LEG_NAMES[LEG_COUNT] = {
    "FL", "FR", "RL", "RR"
};

MotionController::MotionController()
    : kinematics(COXA_LENGTH, FEMUR_LENGTH, TIBIA_LENGTH),
      jumpPhase(JumpPhase::IDLE),
      jumpPhaseStartedMs(0),
      jumpActive(false)
{
    resetLegStates();
}

void MotionController::begin()
{
    calibrator.begin();
    servoManager.begin();
    environment.begin();
    imu.begin();
    gaitController.reset();
    resetLegStates();
    jumpPhase = JumpPhase::IDLE;
    jumpActive = false;

    Serial.println("[MOTION] Controller initialized");
    Serial.println("[MOTION] 35cm configuration loaded");
    Serial.println("[MOTION] Hardware adapter initialized");
}

void MotionController::update(float dt)
{
    if (jumpActive) {
        updateJump();
        return;
    }

    if (!gaitController.moving())
        return;

    gaitController.update(dt);

    for (int i = 0; i < LEG_COUNT; ++i) {
        const FootTarget target =
            gaitController.target(static_cast<GaitLeg>(i));

        setFootTarget(
            static_cast<LegID>(i),
            target.x,
            target.y,
            target.z
        );
    }
}

void MotionController::resetLegStates()
{
    for (int i = 0; i < LEG_COUNT; ++i) {
        legs[i] = {
            static_cast<float>(DEFAULT_SERVO_ANGLE),
            static_cast<float>(DEFAULT_SERVO_ANGLE),
            static_cast<float>(DEFAULT_SERVO_ANGLE)
        };
    }
}

int MotionController::parseLeg(const String& name) const
{
    String normalized = name;
    normalized.trim();
    normalized.toUpperCase();

    if (normalized == "FL") return FL;
    if (normalized == "FR") return FR;
    if (normalized == "RL") return RL;
    if (normalized == "RR") return RR;

    return -1;
}

void MotionController::setServo(int channel, int rawAngle)
{
    if (!servoManager.validChannel(channel)) {
        Serial.printf("[MOTION] Invalid servo channel: %d\n", channel);
        return;
    }

    const int calibratedAngle = calibrator.apply(channel, rawAngle);
    servoManager.setAngle(channel, calibratedAngle);

    Serial.printf(
        "[MOTION] CH%02d raw=%d calibrated=%d\n",
        channel, rawAngle, calibratedAngle
    );
}

bool MotionController::setLeg(
    LegID leg,
    int coxa,
    int femur,
    int tibia
)
{
    if (leg < 0 || leg >= LEG_COUNT)
        return false;

    legs[leg] = {
        static_cast<float>(coxa),
        static_cast<float>(femur),
        static_cast<float>(tibia)
    };

    setServo(SERVO_MAP[leg][0], coxa);
    setServo(SERVO_MAP[leg][1], femur);
    setServo(SERVO_MAP[leg][2], tibia);

    return true;
}

bool MotionController::setLeg(
    const String& name,
    int coxa,
    int femur,
    int tibia
)
{
    const int leg = parseLeg(name);
    if (leg < 0)
        return false;

    return setLeg(
        static_cast<LegID>(leg),
        coxa,
        femur,
        tibia
    );
}

bool MotionController::solveIK(
    float x,
    float y,
    float z,
    JointAngles& result
) const
{
    result = kinematics.solve(x, y, z);
    return result.valid;
}

bool MotionController::validateFootTarget(
    float x,
    float y,
    float z
) const
{
    const float radial = sqrtf(x * x + y * y);

    if (radial < RobotConfig::FOOT_MIN_RADIUS_MM ||
        radial > RobotConfig::FOOT_MAX_RADIUS_MM)
        return false;

    if (z > RobotConfig::FOOT_MAX_Z_MM ||
        z < RobotConfig::FOOT_MIN_Z_MM)
        return false;

    return true;
}

bool MotionController::setFootTarget(
    LegID leg,
    float x,
    float y,
    float z
)
{
    if (leg < 0 || leg >= LEG_COUNT)
        return false;

    if (!validateFootTarget(x, y, z)) {
        Serial.printf(
            "[MOTION] Target rejected %s X=%.1f Y=%.1f Z=%.1f\n",
            LEG_NAMES[leg], x, y, z
        );
        return false;
    }

    JointAngles result;

    if (!solveIK(x, y, z, result)) {
        Serial.printf(
            "[IK] %s unreachable X=%.1f Y=%.1f Z=%.1f\n",
            LEG_NAMES[leg], x, y, z
        );
        return false;
    }

    return setLeg(
        leg,
        static_cast<int>(lroundf(result.coxa)),
        static_cast<int>(lroundf(result.femur)),
        static_cast<int>(lroundf(result.tibia))
    );
}

bool MotionController::setFootTarget(
    const String& name,
    float x,
    float y,
    float z
)
{
    const int leg = parseLeg(name);
    if (leg < 0)
        return false;

    return setFootTarget(
        static_cast<LegID>(leg),
        x,
        y,
        z
    );
}
