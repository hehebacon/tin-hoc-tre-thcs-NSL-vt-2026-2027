#pragma once

#include <stdint.h>

// Single source of truth for the 35 cm competition robot.
namespace RobotConfig {

constexpr float MAX_LENGTH_MM = 350.0f;
constexpr float MAX_WIDTH_MM  = 350.0f;
constexpr float MAX_HEIGHT_MM = 350.0f;

constexpr float BODY_LENGTH_MM = 150.0f;
constexpr float BODY_WIDTH_MM  = 105.0f;
constexpr float BODY_HEIGHT_MM = 45.0f;

constexpr float COXA_MM  = 35.0f;
constexpr float FEMUR_MM = 65.0f;
constexpr float TIBIA_MM = 85.0f;

constexpr uint8_t LEG_COUNT = 4;
constexpr uint8_t DOF_PER_LEG = 3;
constexpr uint8_t SERVO_COUNT = LEG_COUNT * DOF_PER_LEG;

constexpr float SERVO_MIN_DEG = 0.0f;
constexpr float SERVO_MAX_DEG = 180.0f;
constexpr float DEFAULT_SERVO_DEG = 90.0f;

// Logical joint limits. Mechanical calibration can narrow these further.
constexpr float COXA_MIN_DEG  = 15.0f;
constexpr float COXA_MAX_DEG  = 165.0f;
constexpr float FEMUR_MIN_DEG = 15.0f;
constexpr float FEMUR_MAX_DEG = 165.0f;
constexpr float TIBIA_MIN_DEG = 10.0f;
constexpr float TIBIA_MAX_DEG = 170.0f;

// Conservative workspace for the 35 cm frame.
constexpr float FOOT_MIN_RADIUS_MM = 30.0f;
constexpr float FOOT_MAX_RADIUS_MM = 135.0f;
constexpr float FOOT_MIN_Z_MM = -125.0f;
constexpr float FOOT_MAX_Z_MM = -45.0f;

constexpr float DEFAULT_BODY_Z_MM = -90.0f;
constexpr float DEFAULT_STEP_LENGTH_MM = 24.0f;
constexpr float DEFAULT_STEP_HEIGHT_MM = 18.0f;
constexpr float DEFAULT_GAIT_FREQUENCY_HZ = 1.10f;

constexpr float MAX_STEP_LENGTH_MM = 45.0f;
constexpr float MAX_STEP_HEIGHT_MM = 28.0f;
constexpr float MAX_GAIT_FREQUENCY_HZ = 2.0f;

constexpr float MAX_COMMAND_SPEED_SCALE = 1.0f;
constexpr float MIN_SAFE_BATTERY_PERCENT = 15.0f;

constexpr uint32_t CONTROL_PERIOD_MS = 20;
constexpr uint32_t TELEMETRY_PERIOD_MS = 100;

constexpr uint8_t SERVO_FL_COXA = 0;
constexpr uint8_t SERVO_FL_FEMUR = 1;
constexpr uint8_t SERVO_FL_TIBIA = 2;
constexpr uint8_t SERVO_FR_COXA = 3;
constexpr uint8_t SERVO_FR_FEMUR = 4;
constexpr uint8_t SERVO_FR_TIBIA = 5;
constexpr uint8_t SERVO_RL_COXA = 6;
constexpr uint8_t SERVO_RL_FEMUR = 7;
constexpr uint8_t SERVO_RL_TIBIA = 8;
constexpr uint8_t SERVO_RR_COXA = 9;
constexpr uint8_t SERVO_RR_FEMUR = 10;
constexpr uint8_t SERVO_RR_TIBIA = 11;

} // namespace RobotConfig
