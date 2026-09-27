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
    : kinematics(
        COXA_LENGTH,
        FEMUR_LENGTH,
        TIBIA_LENGTH
    )
{
    resetLegStates();
}

void MotionController::begin()
{
    calibrator.begin();
    servoManager.begin();
    environment.begin();
    imu.begin();
    resetLegStates();

    Serial.println("[MOTION] Controller initialized");
    Serial.println("[MOTION] Hardware adapter initialized");
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

    if (normalized == "FL")
        return FL;

    if (normalized == "FR")
        return FR;

    if (normalized == "RL")
        return RL;

    if (normalized == "RR")
        return RR;

    return -1;
}

void MotionController::setServo(
    int channel,
    int rawAngle
)
{
    if (!servoManager.validChannel(channel)) {
        Serial.printf(
            "[MOTION] Invalid servo channel: %d\n",
            channel
        );
        return;
    }

    const int calibratedAngle =
        calibrator.apply(channel, rawAngle);

    servoManager.setAngle(
        channel,
        calibratedAngle
    );

    Serial.printf(
        "[MOTION] CH%02d raw=%d calibrated=%d\n",
        channel,
        rawAngle,
        calibratedAngle
    );
}

bool MotionController::setLeg(
    LegID leg,
    int coxa,
    int femur,
    int tibia
)
{
    if (leg < 0 || leg >= LEG_COUNT) {
        Serial.println("[MOTION] Invalid leg");
        return false;
    }

    legs[leg] = {
        static_cast<float>(coxa),
        static_cast<float>(femur),
        static_cast<float>(tibia)
    };

    setServo(
        SERVO_MAP[leg][0],
        coxa
    );

    setServo(
        SERVO_MAP[leg][1],
        femur
    );

    setServo(
        SERVO_MAP[leg][2],
        tibia
    );

    Serial.printf(
        "[MOTION] %s -> C:%d F:%d T:%d\n",
        LEG_NAMES[leg],
        coxa,
        femur,
        tibia
    );

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

    if (leg < 0) {
        Serial.printf(
            "[MOTION] Invalid leg: %s\n",
            name.c_str()
        );

        return false;
    }

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
    result = kinematics.solve(
        x,
        y,
        z
    );

    return result.valid;
}

bool MotionController::setLegIK(
    LegID leg,
    float x,
    float y,
    float z
)
{
    if (leg < 0 || leg >= LEG_COUNT) {
        Serial.println("[IK] Invalid leg");
        return false;
    }

    JointAngles result;

    if (!solveIK(
            x,
            y,
            z,
            result
        )) {

        Serial.printf(
            "[IK] %s unreachable: "
            "X=%.2f Y=%.2f Z=%.2f\n",
            LEG_NAMES[leg],
            x,
            y,
            z
        );

        return false;
    }

    Serial.printf(
        "[IK] %s -> C:%.2f F:%.2f T:%.2f\n",
        LEG_NAMES[leg],
        result.coxa,
        result.femur,
        result.tibia
    );

    return setLeg(
        leg,
        static_cast<int>(
            lroundf(result.coxa)
        ),
        static_cast<int>(
            lroundf(result.femur)
        ),
        static_cast<int>(
            lroundf(result.tibia)
        )
    );
}

bool MotionController::setLegIK(
    const String& name,
    float x,
    float y,
    float z
)
{
    const int leg = parseLeg(name);

    if (leg < 0) {
        Serial.printf(
            "[IK] Invalid leg: %s\n",
            name.c_str()
        );

        return false;
    }

    return setLegIK(
        static_cast<LegID>(leg),
        x,
        y,
        z
    );
}

void MotionController::testIK(
    float x,
    float y,
    float z
) const
{
    JointAngles result;

    Serial.println();
    Serial.println(
        "=============== IK RESULT ==============="
    );

    Serial.printf(
        "Input X : %.2f mm\n",
        x
    );

    Serial.printf(
        "Input Y : %.2f mm\n",
        y
    );

    Serial.printf(
        "Input Z : %.2f mm\n",
        z
    );

    if (solveIK(
            x,
            y,
            z,
            result
        )) {

        Serial.printf(
            "Coxa    : %.2f deg\n",
            result.coxa
        );

        Serial.printf(
            "Femur   : %.2f deg\n",
            result.femur
        );

        Serial.printf(
            "Tibia   : %.2f deg\n",
            result.tibia
        );

        Serial.println(
            "Status  : VALID"
        );

    } else {

        Serial.println(
            "Status  : UNREACHABLE"
        );
    }

    Serial.println(
        "=========================================="
    );

    Serial.println();
}

void MotionController::center()
{
    servoManager.centerAll();

    resetLegStates();

    Serial.println(
        "[MOTION] Neutral pose applied"
    );
}

void MotionController::stand()
{
    for (int i = 0; i < LEG_COUNT; ++i) {
        setLeg(
            static_cast<LegID>(i),
            90,
            90,
            90
        );
    }

    Serial.println(
        "[MOTION] Stand pose applied"
    );
}

void MotionController::enable()
{
    servoManager.enableAll();
}

void MotionController::disable()
{
    servoManager.disableAll();
}

void MotionController::status() const
{
    Serial.println();
    Serial.println(
        "============== ROBOT STATUS =============="
    );

    Serial.printf(
        "Robot    : %s\n",
        ROBOT_NAME
    );

    Serial.printf(
        "Firmware : %s\n",
        FIRMWARE_VERSION
    );

    Serial.println(
        "Mode     : SIMULATION"
    );

    Serial.println(
        "PCA9685  : NOT CONNECTED"
    );

    Serial.println(
        "Servos   : NOT CONNECTED"
    );

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

    Serial.println(
        "=========================================="
    );

    servoManager.status();
}

void MotionController::debug() const
{
    Serial.println();
    Serial.println(
        "========== MODULE DEBUG =========="
    );

    Serial.printf(
        "[OK] config.h              | Robot=%s\n",
        ROBOT_NAME
    );

    Serial.printf(
        "[OK] ServoManager          | channels=%d\n",
        SERVO_COUNT
    );

    Serial.println(
        "[OK] ServoCalibration"
    );

    Serial.println(
        "[OK] Kinematics"
    );

    Serial.println(
        "[OK] MotionController"
    );

    Serial.println(
        "[OK] Main firmware"
    );

    Serial.println();

    Serial.println(
        "[INFO] Hardware:"
    );

    Serial.println(
        "       PCA9685 : guarded hardware adapter"
    );

    Serial.println(
        "       Servos  : OFFLINE"
    );

    Serial.println(
        "       Camera  : OFFLINE"
    );

    Serial.println(
        "       Voice   : OFFLINE"
    );

    Serial.println(
        "=================================="
    );

    Serial.println();
}

void MotionController::printCalibration() const
{
    calibrator.printAll();
}

void MotionController::printCalibration(
    int channel
) const
{
    calibrator.print(channel);
}

void MotionController::setCalibrationOffset(
    int channel,
    int offset
)
{
    calibrator.setOffset(
        channel,
        offset
    );

    calibrator.print(channel);
}

void MotionController::setCalibrationInvert(
    int channel,
    bool invert
)
{
    calibrator.setInvert(
        channel,
        invert
    );

    calibrator.print(channel);
}

void MotionController::setCalibrationLimits(
    int channel,
    int minimum,
    int maximum
)
{
    calibrator.setLimits(
        channel,
        minimum,
        maximum
    );

    calibrator.print(channel);
}

const LegState&
MotionController::getLegState(
    LegID leg
) const
{
    static const LegState invalid = {
        0.0f,
        0.0f,
        0.0f
    };

    if (leg < 0 || leg >= LEG_COUNT)
        return invalid;

    return legs[leg];
}