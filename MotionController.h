#pragma once

#include <Arduino.h>
#include "config.h"
#include "Kinematics.h"
#include "ServoCalibration.h"
#include "ServoManager.h"
#include "GaitController.h"

enum LegID {
    FL = 0,
    FR = 1,
    RL = 2,
    RR = 3
};

struct LegState {
    float coxa;
    float femur;
    float tibia;
};

class MotionController {
public:
    MotionController();

    void begin();
    void update(float dt = 0.05f);

    void setServo(int channel, int rawAngle);

    bool setLeg(LegID leg, int coxa, int femur, int tibia);
    bool setLeg(const String& name, int coxa, int femur, int tibia);

    bool setLegIK(LegID leg, float x, float y, float z);
    bool setLegIK(const String& name, float x, float y, float z);

    bool setFootTarget(LegID leg, float x, float y, float z);
    bool setFootTarget(const String& name, float x, float y, float z);

    bool solveIK(float x, float y, float z, JointAngles& result) const;
    void testIK(float x, float y, float z) const;
    bool validateFootTarget(float x, float y, float z) const;

    void setGait(const String& mode);
    void stopGait();
    void jump();
    bool jumping() const;
    const GaitController& gait() const;

    void center();
    void stand();
    void enable();
    void disable();

    void status() const;
    void debug() const;

    void printCalibration() const;
    void printCalibration(int channel) const;

    void setCalibrationOffset(int channel, int offset);
    void setCalibrationInvert(int channel, bool invert);
    void setCalibrationLimits(
        int channel,
        int minimum,
        int maximum
    );

    const LegState& getLegState(LegID leg) const;

private:
    ServoCalibrator calibrator;
    ServoManager servoManager;
    Kinematics kinematics;
    GaitController gaitController;

    enum class JumpPhase { IDLE, CROUCH, LOAD, PUSH, FLIGHT, TUCK, LAND, ABSORB, RECOVER };
    JumpPhase jumpPhase;
    unsigned long jumpPhaseStartedMs;
    bool jumpActive;

    void updateJump();
    void applyJumpPose(float z);
    void finishJump();

    LegState legs[LEG_COUNT];

    static const uint8_t SERVO_MAP[LEG_COUNT][3];
    static const char* const LEG_NAMES[LEG_COUNT];

    int parseLeg(const String& name) const;
    void resetLegStates();
};
