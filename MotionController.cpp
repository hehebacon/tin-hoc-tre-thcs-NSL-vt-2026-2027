#include "MotionController.h"
#include "EnvironmentalSensors.h"
#include "ImuInterface.h"

static EnvironmentalSensors environment;
static ImuInterface imu;

const uint8_t MotionController::SERVO_MAP[LEG_COUNT][3] = {
    {0, 1, 2},
    {3, 4, 5},
    {6, 7, 8},
    {9, 10, 11}
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

    if (radial < 35.0f || radial > 180.0f)
        return false;

    if (z > -45.0f || z < -150.0f)
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
        x, y, z
    );
}

bool MotionController::setLegIK(
    LegID leg,
    float x,
    float y,
    float z
)
{
    return setFootTarget(leg, x, y, z);
}

bool MotionController::setLegIK(
    const String& name,
    float x,
    float y,
    float z
)
{
    return setFootTarget(name, x, y, z);
}

void MotionController::testIK(float x, float y, float z) const
{
    JointAngles result;

    Serial.println();
    Serial.println("=============== IK RESULT ===============");
    Serial.printf("Input X : %.2f mm\n", x);
    Serial.printf("Input Y : %.2f mm\n", y);
    Serial.printf("Input Z : %.2f mm\n", z);

    if (solveIK(x, y, z, result)) {
        Serial.printf("Coxa    : %.2f deg\n", result.coxa);
        Serial.printf("Femur   : %.2f deg\n", result.femur);
        Serial.printf("Tibia   : %.2f deg\n", result.tibia);
        Serial.println("Status  : VALID");
    } else {
        Serial.println("Status  : UNREACHABLE");
    }

    Serial.println("==========================================");
    Serial.println();
}

void MotionController::jump()
{
    if (jumpActive) {
        Serial.println("[JUMP] Already active");
        return;
    }

    gaitController.stop();
    jumpActive = true;
    jumpPhase = JumpPhase::CROUCH;
    jumpPhaseStartedMs = millis();

    Serial.println("[JUMP] START");
    applyJumpPose(-90.0f);
}

bool MotionController::jumping() const
{
    return jumpActive;
}

void MotionController::applyJumpPose(float z)
{
    for (int i = 0; i < LEG_COUNT; ++i) {
        const float y = (i == FL || i == RL) ? 45.0f : -45.0f;
        if (!setFootTarget(static_cast<LegID>(i), 0.0f, y, z)) {
            Serial.printf("[JUMP] IK REJECT %s Z=%.1f\\n", LEG_NAMES[i], z);
            finishJump();
            return;
        }
    }
}

void MotionController::updateJump()
{
    const unsigned long elapsed = millis() - jumpPhaseStartedMs;

    switch (jumpPhase) {
        case JumpPhase::CROUCH:
            if (elapsed >= 220) {
                jumpPhase = JumpPhase::LOAD;
                jumpPhaseStartedMs = millis();
                applyJumpPose(-112.0f);
                Serial.println("[JUMP] LOAD");
            }
            break;

        case JumpPhase::LOAD:
            if (elapsed >= 160) {
                jumpPhase = JumpPhase::PUSH;
                jumpPhaseStartedMs = millis();
                applyJumpPose(-70.0f);
                Serial.println("[JUMP] PUSH");
            }
            break;

        case JumpPhase::PUSH:
            if (elapsed >= 140) {
                jumpPhase = JumpPhase::FLIGHT;
                jumpPhaseStartedMs = millis();
                applyJumpPose(-70.0f);
                Serial.println("[JUMP] FLIGHT");
            }
            break;

        case JumpPhase::FLIGHT:
            if (elapsed >= 280) {
                jumpPhase = JumpPhase::TUCK;
                jumpPhaseStartedMs = millis();
                applyJumpPose(-76.0f);
                Serial.println("[JUMP] TUCK");
            }
            break;

        case JumpPhase::TUCK:
            if (elapsed >= 120) {
                jumpPhase = JumpPhase::LAND;
                jumpPhaseStartedMs = millis();
                applyJumpPose(-78.0f);
                Serial.println("[JUMP] LAND");
            }
            break;

        case JumpPhase::LAND:
            if (elapsed >= 120) {
                jumpPhase = JumpPhase::ABSORB;
                jumpPhaseStartedMs = millis();
                applyJumpPose(-98.0f);
                Serial.println("[JUMP] ABSORB");
            }
            break;

        case JumpPhase::ABSORB:
            if (elapsed >= 180) {
                jumpPhase = JumpPhase::RECOVER;
                jumpPhaseStartedMs = millis();
                applyJumpPose(-100.0f);
                Serial.println("[JUMP] RECOVER");
            }
            break;

        case JumpPhase::RECOVER:
            if (elapsed >= 220) {
                finishJump();
            }
            break;

        case JumpPhase::IDLE:
        default:
            finishJump();
            break;
    }
}

void MotionController::finishJump()
{
    jumpActive = false;
    jumpPhase = JumpPhase::IDLE;
    jumpPhaseStartedMs = 0;
    stand();
    Serial.println("[JUMP] COMPLETE");
}

void MotionController::setGait(const String& mode)
{
    gaitController.setMode(mode);
    Serial.printf("[GAIT] Mode -> %s\n", gaitController.mode());
}

void MotionController::stopGait()
{
    gaitController.stop();
    Serial.println("[GAIT] Stopped");
}

const GaitController& MotionController::gait() const
{
    return gaitController;
}

void MotionController::center()
{
    stopGait();
    servoManager.centerAll();
    resetLegStates();
    Serial.println("[MOTION] Neutral pose applied");
}

void MotionController::stand()
{
    stopGait();

    for (int i = 0; i < LEG_COUNT; ++i)
        setLeg(static_cast<LegID>(i), 90, 90, 90);

    Serial.println("[MOTION] Stand pose applied");
}

void MotionController::enable()
{
    servoManager.enableAll();
}

void MotionController::disable()
{
    stopGait();
    servoManager.disableAll();
}

void MotionController::status() const
{
    Serial.println();
    Serial.println("============== ROBOT STATUS ==============");
    Serial.printf("Robot    : %s\n", ROBOT_NAME);
    Serial.printf("Firmware : %s\n", FIRMWARE_VERSION);
    Serial.printf("Gait     : %s\n", gaitController.mode());
    Serial.printf("Phase    : %.3f\n", gaitController.phase());
    Serial.printf("Moving   : %s\n", gaitController.moving() ? "YES" : "NO");
    Serial.println();

    for (int i = 0; i < LEG_COUNT; ++i) {
        Serial.printf(
            "%s | C:%6.2f F:%6.2f T:%6.2f\n",
            LEG_NAMES[i],
            legs[i].coxa,
            legs[i].femur,
            legs[i].tibia
        );
    }

    Serial.println("==========================================");
    servoManager.status();
}

void MotionController::debug() const
{
    Serial.println();
    Serial.println("========== MODULE DEBUG ==========");
    Serial.printf("[OK] config.h              | Robot=%s\n", ROBOT_NAME);
    Serial.printf("[OK] ServoManager          | channels=%d\n", SERVO_COUNT);
    Serial.println("[OK] ServoCalibration");
    Serial.println("[OK] Kinematics");
    Serial.println("[OK] GaitController");
    Serial.println("[OK] MotionController");
    Serial.println("[OK] Main firmware");
    Serial.println();
    Serial.println("[INFO] Hardware:");
    Serial.println("       PCA9685 : guarded hardware adapter");
    Serial.println("       Servos  : OFFLINE");
    Serial.println("       Camera  : OFFLINE");
    Serial.println("       Voice   : OFFLINE");
    Serial.println("==================================");
    Serial.println();
}

void MotionController::printCalibration() const
{
    calibrator.printAll();
}

void MotionController::printCalibration(int channel) const
{
    calibrator.print(channel);
}

void MotionController::setCalibrationOffset(int channel, int offset)
{
    calibrator.setOffset(channel, offset);
    calibrator.print(channel);
}

void MotionController::setCalibrationInvert(int channel, bool invert)
{
    calibrator.setInvert(channel, invert);
    calibrator.print(channel);
}

void MotionController::setCalibrationLimits(
    int channel,
    int minimum,
    int maximum
)
{
    calibrator.setLimits(channel, minimum, maximum);
    calibrator.print(channel);
}

const LegState& MotionController::getLegState(LegID leg) const
{
    static const LegState invalid = {0.0f, 0.0f, 0.0f};

    if (leg < 0 || leg >= LEG_COUNT)
        return invalid;

    return legs[leg];
}
