#pragma once

#include <Arduino.h>
#include "MotionController.h"
#include "MotionSafety.h"
#include "ImuInterface.h"
#include "EnvironmentalSensors.h"
#include "CameraInterface.h"
#include "ThermalInterface.h"
#include "HardwareStatus.h"

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

private:
    MotionController& motionController;
    MotionSafety& motionSafety;
    ImuInterface& imuInterface;
    EnvironmentalSensors& environmentalSensors;
    CameraInterface& cameraInterface;
    ThermalInterface& thermalInterface;

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
