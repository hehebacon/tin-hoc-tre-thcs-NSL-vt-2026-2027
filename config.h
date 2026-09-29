#pragma once

#include "RobotConfig.h"

#define ROBOT_NAME "XZORT_RESCUE_QUADRUPED_35CM"
#define FIRMWARE_VERSION "0.5.0"

#define GEMINI_MODEL "gemini-3.8-flash"

#define SERVO_COUNT RobotConfig::SERVO_COUNT
#define LEG_COUNT RobotConfig::LEG_COUNT

#define SERVO_MIN_ANGLE static_cast<int>(RobotConfig::SERVO_MIN_DEG)
#define SERVO_MAX_ANGLE static_cast<int>(RobotConfig::SERVO_MAX_DEG)

// Compatibility aliases. New modules should prefer RobotConfig::*.
#define COXA_LENGTH RobotConfig::COXA_MM
#define FEMUR_LENGTH RobotConfig::FEMUR_MM
#define TIBIA_LENGTH RobotConfig::TIBIA_MM

#define DEFAULT_SERVO_ANGLE static_cast<int>(RobotConfig::DEFAULT_SERVO_DEG)

#define SERIAL_BAUD 115200

#define PCA9685_I2C_ADDRESS 0x40
#define PCA9685_PWM_FREQUENCY 50

#define MOTION_UPDATE_MS RobotConfig::CONTROL_PERIOD_MS

// Keep the API key empty in the public repository. Configure it locally.
#define GEMINI_API_KEY ""
