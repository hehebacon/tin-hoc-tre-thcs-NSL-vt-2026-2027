#include "ServoManager.h"
#include "PCA9685ServoDriver.h"

static PCA9685ServoDriver hardwareDriver;

// ============================================================
// BEGIN
// ============================================================

void ServoManager::begin()
{
    for (int i = 0; i < SERVO_COUNT; i++) {
        angles[i] = DEFAULT_SERVO_ANGLE;
        enabled[i] = true;
    }

    hardwareDriver.begin();
    Serial.printf("[SERVO] Manager initialized | PCA9685=%s\n", hardwareDriver.available() ? "ONLINE" : "OFFLINE");
}

// ============================================================
// VALID CHANNEL
// ============================================================

bool ServoManager::validChannel(int channel) const
{
    return channel >= 0 && channel < SERVO_COUNT;
}

// ============================================================
// CLAMP
// ============================================================

int ServoManager::clampAngle(int angle) const
{
    if (angle < SERVO_MIN_ANGLE)
        return SERVO_MIN_ANGLE;

    if (angle > SERVO_MAX_ANGLE)
        return SERVO_MAX_ANGLE;

    return angle;
}

// ============================================================
// SET ANGLE
// ============================================================

void ServoManager::setAngle(
    int channel,
    int angle
)
{
    if (!validChannel(channel)) {
        Serial.printf(
            "[SERVO] Invalid channel: %d\n",
            channel
        );
        return;
    }

    angle = clampAngle(angle);
    angles[channel] = angle;

    if (enabled[channel])
        hardwareDriver.setAngle(static_cast<uint8_t>(channel), angle);

    Serial.printf(
        "[SERVO] CH%02d -> %d deg\n",
        channel,
        angle
    );
}

// ============================================================
// GET ANGLE
// ============================================================

int ServoManager::getAngle(int channel) const
{
    if (!validChannel(channel))
        return -1;

    return angles[channel];
}

// ============================================================
// CENTER
// ============================================================

void ServoManager::centerAll()
{
    Serial.println("[SERVO] Centering all servos");

    for (int i = 0; i < SERVO_COUNT; i++)
        setAngle(i, DEFAULT_SERVO_ANGLE);
}

// ============================================================
// ENABLE / DISABLE
// ============================================================

void ServoManager::enableAll()
{
    for (int i = 0; i < SERVO_COUNT; i++)
        enabled[i] = true;

    Serial.println("[SERVO] All servos enabled");
}

void ServoManager::disableAll()
{
    for (int i = 0; i < SERVO_COUNT; i++)
        enabled[i] = false;

    hardwareDriver.disableAll();
    Serial.println("[SERVO] All servos disabled");
}

// ============================================================
// STATUS
// ============================================================

void ServoManager::status() const
{
    Serial.println();
    Serial.println("========== SERVO STATUS ==========");

    for (int i = 0; i < SERVO_COUNT; i++) {
        Serial.printf(
            "CH%02d | %3d deg | %s\n",
            i,
            angles[i],
            enabled[i] ? "ENABLED" : "DISABLED"
        );
    }

    Serial.println("==================================");
    Serial.println();
}
