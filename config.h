#pragma once

#define ROBOT_NAME "AI_QUADRUPED"
#define FIRMWARE_VERSION "0.4.0"

#define GEMINI_MODEL "gemini-3.6-flash"

#define SERVO_COUNT 12
#define LEG_COUNT 4

#define SERVO_MIN_ANGLE 0
#define SERVO_MAX_ANGLE 180

// Link lengths in millimeters.
#define COXA_LENGTH 45.0f
#define FEMUR_LENGTH 75.0f
#define TIBIA_LENGTH 105.0f

#define DEFAULT_SERVO_ANGLE 90

#define SERIAL_BAUD 115200

#define PCA9685_I2C_ADDRESS 0x40
#define PCA9685_PWM_FREQUENCY 50

// Motion loop target. The gait planner is deterministic and
// receives elapsed seconds from the firmware loop.
#define MOTION_UPDATE_MS 50
