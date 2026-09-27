#pragma once

// Hardware is OFF by default. Enable only after the physical wiring,
// library and limits have been verified.
#define ENABLE_PCA9685 0

#define PCA9685_I2C_ADDRESS 0x40
#define PCA9685_PWM_FREQUENCY 50

// Conservative pulse range for a typical hobby servo.
// Final values must be calibrated for the actual servo model.
#define SERVO_PULSE_MIN 110
#define SERVO_PULSE_MAX 510

#define MOTION_TIMEOUT_MS 1500
