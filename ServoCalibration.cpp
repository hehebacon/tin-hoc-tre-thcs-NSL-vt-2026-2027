#include "ServoCalibration.h"

// ============================================================
// INITIALIZE
// ============================================================

void ServoCalibrator::begin()
{
    for (int i = 0; i < SERVO_COUNT; i++) {
        data[i].offset = 0;
        data[i].invert = false;
        data[i].minAngle = SERVO_MIN_ANGLE;
        data[i].maxAngle = SERVO_MAX_ANGLE;
    }

    Serial.println("[CAL] Calibration initialized");
}

// ============================================================
// VALID CHANNEL
// ============================================================

bool ServoCalibrator::validChannel(int channel) const
{
    return channel >= 0 && channel < SERVO_COUNT;
}

// ============================================================
// CLAMP
// ============================================================

int ServoCalibrator::clamp(
    int value,
    int minimum,
    int maximum
) const
{
    if (value < minimum)
        return minimum;

    if (value > maximum)
        return maximum;

    return value;
}

// ============================================================
// APPLY
// ============================================================

int ServoCalibrator::apply(
    int channel,
    int angle
)
{
    if (!validChannel(channel))
        return angle;

    ServoCalibration& c = data[channel];

    angle = clamp(
        angle,
        SERVO_MIN_ANGLE,
        SERVO_MAX_ANGLE
    );

    if (c.invert)
        angle = 180 - angle;

    angle += c.offset;

    angle = clamp(
        angle,
        c.minAngle,
        c.maxAngle
    );

    return angle;
}

// ============================================================
// SETTERS
// ============================================================

void ServoCalibrator::setOffset(
    int channel,
    int offset
)
{
    if (!validChannel(channel))
        return;

    data[channel].offset = offset;
}

void ServoCalibrator::setInvert(
    int channel,
    bool invert
)
{
    if (!validChannel(channel))
        return;

    data[channel].invert = invert;
}

void ServoCalibrator::setLimits(
    int channel,
    int minimum,
    int maximum
)
{
    if (!validChannel(channel))
        return;

    minimum = clamp(
        minimum,
        SERVO_MIN_ANGLE,
        SERVO_MAX_ANGLE
    );

    maximum = clamp(
        maximum,
        SERVO_MIN_ANGLE,
        SERVO_MAX_ANGLE
    );

    if (minimum > maximum)
        return;

    data[channel].minAngle = minimum;
    data[channel].maxAngle = maximum;
}

// ============================================================
// PRINT
// ============================================================

void ServoCalibrator::print(int channel) const
{
    if (!validChannel(channel)) {
        Serial.printf(
            "[CAL] Invalid channel: %d\n",
            channel
        );
        return;
    }

    const ServoCalibration& c = data[channel];

    Serial.printf(
        "CH%02d | offset=%d | invert=%s | limit=%d..%d\n",
        channel,
        c.offset,
        c.invert ? "YES" : "NO",
        c.minAngle,
        c.maxAngle
    );
}

void ServoCalibrator::printAll() const
{
    Serial.println();
    Serial.println("========= SERVO CALIBRATION =========");

    for (int i = 0; i < SERVO_COUNT; i++)
        print(i);

    Serial.println("=====================================");
    Serial.println();
}
