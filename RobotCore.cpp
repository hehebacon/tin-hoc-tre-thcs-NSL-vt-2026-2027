#include "RobotCore.h"
#include <math.h>

RobotCore::RobotCore(
    MotionController& motion,
    MotionSafety& safety,
    ImuInterface& imu,
    EnvironmentalSensors& environmental,
    CameraInterface& camera,
    ThermalInterface& thermal
)
    : motionController(motion),
      motionSafety(safety),
      imuInterface(imu),
      environmentalSensors(environmental),
      cameraInterface(camera),
      thermalInterface(thermal)
{
}

void RobotCore::begin()
{
    currentMode = RobotMode::IDLE;
    missionActive = false;
    personDetected = false;
    thermalSignature = false;
    sensorFault = false;
    coreFault = false;
    cycle = 0;
    motionController.stopGait();
}

void RobotCore::update(float dt)
{
    ++cycle;

    if (!motionSafety.allowed()) {
        motionController.stopGait();
        return;
    }

    evaluateSensors();

    if (coreFault) {
        enterFault();
        return;
    }

    handleMission();
    motionController.update(dt);
}

void RobotCore::evaluateSensors()
{
    const CameraFrameInfo cameraReading = cameraInterface.observe();
    const ThermalReading thermalReading = thermalInterface.read();
    const ImuReading imuReading = imuInterface.read();
    const EnvironmentalReading envReading = environmentalSensors.read();

    personDetected = personDetected || (cameraReading.valid && cameraReading.personDetected);
    thermalSignature = thermalSignature || (thermalReading.valid && thermalReading.personSignature);

    // Invalid sensor data is not a fault by itself: interfaces may be optional.
    // A real hardware driver should report an explicit valid reading once present.
    sensorFault = false;

    if (imuReading.valid) {
        if (isnan(imuReading.pitch) || isnan(imuReading.roll) || isnan(imuReading.yaw)) {
            sensorFault = true;
        }
    }

    if (envReading.valid) {
        if (isnan(envReading.temperature) ||
            isnan(envReading.humidity) ||
            isnan(envReading.pressure)) {
            sensorFault = true;
        }
    }

    if (cameraReading.valid && cameraReading.confidence < 0.0f) {
        sensorFault = true;
    }

    if (thermalReading.valid && thermalReading.hotspot < -100.0f) {
        sensorFault = true;
    }

    if (sensorFault) {
        coreFault = true;
    }
}

void RobotCore::handleMission()
{
    if (!missionActive) {
        motionController.stopGait();
        return;
    }

    switch (currentMode) {
        case RobotMode::PATROL:
            motionController.setGait("SLOW_WALK");
            break;

        case RobotMode::SEARCH:
            motionController.setGait("SEARCH");
            if (personDetected || thermalSignature) {
                currentMode = RobotMode::RESCUE;
            }
            break;

        case RobotMode::RESCUE:
            motionController.setGait("RESCUE");
            if (personDetected || thermalSignature) {
                personDetected = true;
            }
            break;

        case RobotMode::RETURN_HOME:
        case RobotMode::DELIVER:
        case RobotMode::RECHARGE:
            motionController.setGait("SLOW_WALK");
            break;

        case RobotMode::FOLLOW:
        case RobotMode::AVOID:
        case RobotMode::INSPECT:
            motionController.setGait("SEARCH");
            break;

        case RobotMode::EXPLORE:
        case RobotMode::DEMO:
            motionController.setGait("WALK");
            break;

        case RobotMode::CALIBRATION:
        case RobotMode::CLIMB:
        case RobotMode::IDLE:
        case RobotMode::FAULT:
        default:
            // CLIMB is intentionally a motion-capability placeholder until
            // a verified wall-climbing hardware driver is installed.
            motionController.stopGait();
            break;
    }
}

bool RobotCore::setMode(const String& mode)
{
    if (coreFault || !motionSafety.allowed()) {
        return false;
    }

    String normalized = mode;
    normalized.trim();
    normalized.toUpperCase();

    const RobotMode next = parseMode(normalized);
    if (next == RobotMode::IDLE && normalized != "IDLE") {
        return false;
    }

    currentMode = next;
    missionActive = next != RobotMode::IDLE;

    if (next == RobotMode::FAULT) {
        enterFault();
        return false;
    }

    applyMode();
    return true;
}

void RobotCore::applyMode()
{
    switch (currentMode) {
        case RobotMode::PATROL:
        case RobotMode::RETURN_HOME:
        case RobotMode::DELIVER:
        case RobotMode::RECHARGE:
            motionController.setGait("SLOW_WALK");
            break;
        case RobotMode::SEARCH:
        case RobotMode::FOLLOW:
        case RobotMode::AVOID:
        case RobotMode::INSPECT:
            motionController.setGait("SEARCH");
            break;
        case RobotMode::RESCUE:
            motionController.setGait("RESCUE");
            break;
        case RobotMode::EXPLORE:
        case RobotMode::DEMO:
            motionController.setGait("WALK");
            break;
        case RobotMode::CALIBRATION:
        case RobotMode::CLIMB:
        case RobotMode::IDLE:
        case RobotMode::FAULT:
        default:
            motionController.stopGait();
            break;
    }
}

void RobotCore::stop()
{
    missionActive = false;
    currentMode = RobotMode::IDLE;
    motionController.stopGait();
}

bool RobotCore::resume()
{
    if (coreFault || !motionSafety.allowed()) {
        return false;
    }

    if (currentMode == RobotMode::IDLE) {
        return true;
    }

    missionActive = true;
    applyMode();
    return true;
}

void RobotCore::resetMission()
{
    personDetected = false;
    thermalSignature = false;
    sensorFault = false;
    coreFault = false;
    missionActive = false;
    currentMode = RobotMode::IDLE;
    cycle = 0;
    motionController.stopGait();
}

bool RobotCore::reportPerson()
{
    if (coreFault || !missionActive) {
        return false;
    }

    personDetected = true;
    currentMode = RobotMode::RESCUE;
    missionActive = true;
    motionController.setGait("RESCUE");
    return true;
}

void RobotCore::returnHome()
{
    if (coreFault || !motionSafety.allowed()) {
        return;
    }

    currentMode = RobotMode::RETURN_HOME;
    missionActive = true;
    motionController.setGait("SLOW_WALK");
}

void RobotCore::enterFault()
{
    coreFault = true;
    missionActive = false;
    currentMode = RobotMode::FAULT;
    motionController.stopGait();
    motionSafety.emergencyStop();
}

RobotCoreStatus RobotCore::status() const
{
    return {
        currentMode,
        missionActive,
        personDetected,
        thermalSignature,
        !sensorFault,
        coreFault,
        cycle
    };
}

String RobotCore::modeName() const
{
    switch (currentMode) {
        case RobotMode::PATROL: return "PATROL";
        case RobotMode::SEARCH: return "SEARCH";
        case RobotMode::RESCUE: return "RESCUE";
        case RobotMode::RETURN_HOME: return "RETURN_HOME";
        case RobotMode::FOLLOW: return "FOLLOW";
        case RobotMode::AVOID: return "AVOID";
        case RobotMode::EXPLORE: return "EXPLORE";
        case RobotMode::INSPECT: return "INSPECT";
        case RobotMode::DELIVER: return "DELIVER";
        case RobotMode::RECHARGE: return "RECHARGE";
        case RobotMode::CALIBRATION: return "CALIBRATION";
        case RobotMode::DEMO: return "DEMO";
        case RobotMode::CLIMB: return "CLIMB";
        case RobotMode::FAULT: return "FAULT";
        case RobotMode::IDLE:
        default: return "IDLE";
    }
}

RobotMode RobotCore::parseMode(const String& mode)
{
    String value = mode;
    value.toUpperCase();

    if (value == "PATROL") return RobotMode::PATROL;
    if (value == "SEARCH") return RobotMode::SEARCH;
    if (value == "RESCUE") return RobotMode::RESCUE;
    if (value == "RETURN_HOME") return RobotMode::RETURN_HOME;
    if (value == "FOLLOW") return RobotMode::FOLLOW;
    if (value == "AVOID") return RobotMode::AVOID;
    if (value == "EXPLORE") return RobotMode::EXPLORE;
    if (value == "INSPECT") return RobotMode::INSPECT;
    if (value == "DELIVER") return RobotMode::DELIVER;
    if (value == "RECHARGE") return RobotMode::RECHARGE;
    if (value == "CALIBRATION") return RobotMode::CALIBRATION;
    if (value == "DEMO") return RobotMode::DEMO;
    if (value == "CLIMB") return RobotMode::CLIMB;
    if (value == "IDLE") return RobotMode::IDLE;

    return RobotMode::IDLE;
}
