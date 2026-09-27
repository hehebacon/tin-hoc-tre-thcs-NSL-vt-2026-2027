#include "PCA9685ServoDriver.h"

#if ENABLE_PCA9685
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
static Adafruit_PWMServoDriver pca(PCA9685_I2C_ADDRESS);
#endif

bool PCA9685ServoDriver::begin()
{
#if ENABLE_PCA9685
    pca.begin();
    pca.setPWMFreq(PCA9685_PWM_FREQUENCY);
    ready = true;
#else
    ready = false;
#endif
    return ready;
}

bool PCA9685ServoDriver::available() const
{
    return ready;
}

void PCA9685ServoDriver::setAngle(uint8_t channel, int angle)
{
#if ENABLE_PCA9685
    if (!ready || channel >= 16) return;

    angle = constrain(angle, 0, 180);
    const int pulse = map(angle, 0, 180, SERVO_PULSE_MIN, SERVO_PULSE_MAX);
    pca.setPWM(channel, 0, pulse);
#else
    (void)channel;
    (void)angle;
#endif
}

void PCA9685ServoDriver::disableAll()
{
#if ENABLE_PCA9685
    if (!ready) return;
    for (uint8_t i = 0; i < 16; ++i)
        pca.setPWM(i, 0, 0);
#endif
}
