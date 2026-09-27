#pragma once

#include <Arduino.h>
#include "MotionController.h"
#include "MotionSafety.h"
#include "ImuInterface.h"
#include "EnvironmentalSensors.h"
#include "CameraInterface.h"
#include "ThermalInterface.h"
#include "DecisionEngine.h"
#include "HardwareStatus.h"
#include "Perception.h"

enum class RobotMode {
    IDLE,
    PATROL,
    SEARCH,
    RESCUE,
    RETURN_HOME,
    FOLLOW,
    AVOID,
    EXPLORE,
    INSPECT,
    DELIVER,
    RECHARGE,
    CALIBRATION,
    DEMO,
    CLIMB,
    FAULT
};

struct RobotCoreStatus {
    RobotMode mode;
    bool missionActive;
    bool personDetected;
    bool thermalSignature;
    bool sensorsReady;
    bool fault;
    uint32_t cycle;
    WorldState world;
};

class RobotCore {
public:
    RobotCore(
        MotionController& motion,
        MotionSafety& safety,
        ImuInterface& imu,
        EnvironmentalSensors& environmental,
        CameraInterface& camera,
        ThermalInterface& thermal
    );

    void begin();
    void update(float dt);

    bool setMode(const String& mode);
    void stop();
    bool resume();
    void resetMission();

    bool reportPerson();
    void returnHome();

    RobotCoreStatus status() const;
    String modeName() const;
    String goalName() const;
    String actionName() const;
    bool setGoal(const String& goal);
    void completeRescue();

    void startAutonomous();
    void startDriverControl();
    void startEndGame();
    void finishCompetition();
    void setCompetitionInput(const CompetitionInputs& inputs);
    void setPerceptionInput(const WorldState& world);
    const WorldState& worldState() const;
    String colorName() const;
    String phaseName() const;

private:
    MotionController& motionController;
    MotionSafety& motionSafety;
    ImuInterface& imuInterface;
    EnvironmentalSensors& environmentalSensors;
    CameraInterface& cameraInterface;
    ThermalInterface& thermalInterface;
    DecisionEngine decisionEngine;
    Perception perception;

    RobotMode currentMode = RobotMode::IDLE;
    bool missionActive = false;
    bool personDetected = false;
    bool thermalSignature = false;
    bool sensorFault = false;
    bool coreFault = false;
    uint32_t cycle = 0;

    void applyMode();
    void evaluateSensors();
    void handleMission();
    void enterFault();
    static RobotMode parseMode(const String& mode);
};
