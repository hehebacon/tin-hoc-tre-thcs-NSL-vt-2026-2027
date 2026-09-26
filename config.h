#pragma once

// ============================================================
// ROBOT CONFIGURATION
// ============================================================

#define ROBOT_NAME "AI_QUADRUPED"
#define FIRMWARE_VERSION "0.2.0"

#define SERVO_COUNT 12
#define LEG_COUNT 4

// Logical servo limits.
// These are software limits; final mechanical limits must be
// calibrated carefully before powering real servos.
#define SERVO_MIN_ANGLE 0
#define SERVO_MAX_ANGLE 180

// IK link lengths in millimeters.
#define COXA_LENGTH 45.0f
#define FEMUR_LENGTH 75.0f
#define TIBIA_LENGTH 105.0f

// Default neutral pose.
#define DEFAULT_SERVO_ANGLE 90

// Serial debug.
#define SERIAL_BAUD 115200

// PCA9685 settings reserved for hardware integration.
#define PCA9685_I2C_ADDRESS 0x40
#define PCA9685_PWM_FREQUENCY 50
