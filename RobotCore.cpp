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
    decisionEngine.begin();
    perception.begin();
}

void RobotCore::update(float dt)
{
    ++cycle;

    if (!motionSafety.allowed()) {
        motionController.stopGait();
        return;
    }

    perception.update();
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
    const WorldState& world = perception.state();
    CompetitionInputs competition{};
    competition.sensorsHealthy = world.sensorsHealthy;
    competition.lineDetected = world.line != LineState::LOST;
    competition.intersectionDetected = world.line == LineState::INTERSECTION;
    competition.obstacleDetected = world.obstacleDetected;
    competition.targetDetected = world.targetDetected;
    competition.targetPicked = world.targetPicked;
    competition.targetClassified = world.targetClassified;
    competition.targetPlaced = world.targetPlaced;
    competition.allAutonomousTasksDone = world.allAutonomousTasksDone;
    competition.endGameReady = world.endGameReady;
    competition.homeDetected = world.homeDetected;
    decisionEngine.setCompetitionInput(competition);

    const DecisionInputs inputs = {
        !sensorFault && !coreFault,
        personDetected,
        thermalSignature,
        decisionEngine.action() == DecisionAction::RETURN_HOME && decisionEngine.goal() == DecisionGoal::RESCUE
    };

    const DecisionOutput decision = decisionEngine.update(inputs);

    if (!missionActive) {
        motionController.stopGait();
        return;
    }

    switch (decision.action) {
        case DecisionAction::SEARCH:
            currentMode = RobotMode::SEARCH;
            motionController.setGait("SEARCH");
            break;

        case DecisionAction::APPROACH:
            currentMode = RobotMode::RESCUE;
            motionController.setGait("SLOW_WALK");
            break;

        case DecisionAction::RESCUE:
            currentMode = RobotMode::RESCUE;
            motionController.setGait("RESCUE");
            break;

        case DecisionAction::RETURN_HOME:
            currentMode = RobotMode::RETURN_HOME;
            motionController.setGait("SLOW_WALK");
            break;

        case DecisionAction::PATROL:
            currentMode = RobotMode::PATROL;
            motionController.setGait("SLOW_WALK");
            break;

        case DecisionAction::DEMO:
            currentMode = RobotMode::DEMO;
            motionController.setGait("WALK");
            break;

        case DecisionAction::LINE_FOLLOW:
            currentMode = RobotMode::FOLLOW;
            motionController.setGait("SLOW_WALK");
            break;

        case DecisionAction::PICKUP:
        case DecisionAction::CLASSIFY:
        case DecisionAction::PLACE:
            currentMode = RobotMode::DELIVER;
            motionController.stopGait();
            break;

        case DecisionAction::DRIVER:
            currentMode = RobotMode::IDLE;
            motionController.stopGait();
            break;

        case DecisionAction::ENDGAME:
            currentMode = RobotMode::CLIMB;
            motionController.stopGait();
            break;

        case DecisionAction::FINISH:
            currentMode = RobotMode::IDLE;
            missionActive = false;
            motionController.stopGait();
            break;

        case DecisionAction::FAULT:
            enterFault();
            break;

        case DecisionAction::IDLE:
        default:
            currentMode = RobotMode::IDLE;
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

    if (next == RobotMode::IDLE) {
        stop();
        return true;
    }

    if (next == RobotMode::PATROL) {
        return setGoal("PATROL");
    }

    if (next == RobotMode::SEARCH) {
        if (!setGoal("RESCUE")) {
            return false;
        }
        currentMode = RobotMode::SEARCH;
        return true;
    }

    if (next == RobotMode::RESCUE) {
        if (!setGoal("RESCUE")) {
            return false;
        }
        decisionEngine.targetDetected();
        currentMode = RobotMode::RESCUE;
        handleMission();
        return true;
    }

    if (next == RobotMode::RETURN_HOME) {
        return setGoal("RETURN_HOME");
    }

    if (next == RobotMode::DEMO) {
        return setGoal("DEMO");
    }

    // Legacy modes remain available for diagnostics. They are not presented
    // as autonomous capabilities unless their physical/sensor stack exists.
    currentMode = next;
    missionActive = true;
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

bool RobotCore::setGoal(const String& goal)
{
    if (coreFault || !motionSafety.allowed()) {
        return false;
    }

    if (!decisionEngine.setGoal(goal)) {
        return false;
    }

    missionActive = decisionEngine.goal() != DecisionGoal::NONE;

    if (!missionActive) {
        currentMode = RobotMode::IDLE;
        motionController.stopGait();
        return true;
    }

    // Let the decision engine choose the first action instead of forcing
    // a pre-scripted gait.
    handleMission();
    return true;
}

void RobotCore::startAutonomous()
{
    if (coreFault || !motionSafety.allowed()) return;
    decisionEngine.startAutonomous();
    missionActive = true;
    handleMission();
}

void RobotCore::startDriverControl()
{
    if (coreFault || !motionSafety.allowed()) return;
    decisionEngine.startDriverControl();
    missionActive = true;
    currentMode = RobotMode::IDLE;
    motionController.stopGait();
}

void RobotCore::startEndGame()
{
    if (coreFault || !motionSafety.allowed()) return;
    decisionEngine.startEndGame();
    missionActive = true;
    handleMission();
}

void RobotCore::finishCompetition()
{
    decisionEngine.finish();
    missionActive = false;
    motionController.stopGait();
    currentMode = RobotMode::IDLE;
}

void RobotCore::setCompetitionInput(const CompetitionInputs& inputs)
{
    WorldState world = perception.state();
    world.sensorsHealthy = inputs.sensorsHealthy;
    world.line = inputs.intersectionDetected ? LineState::INTERSECTION :
                 (inputs.lineDetected ? LineState::CENTER : LineState::LOST);
    world.obstacleDetected = inputs.obstacleDetected;
    world.targetDetected = inputs.targetDetected;
    world.targetPicked = inputs.targetPicked;
    world.targetPlaced = inputs.targetPlaced;
    world.allAutonomousTasksDone = inputs.allAutonomousTasksDone;
    world.endGameReady = inputs.endGameReady;
    world.homeDetected = inputs.homeDetected;
    setPerceptionInput(world);

    if (decisionEngine.phase() != CompetitionPhase::IDLE) {
        missionActive = true;
    }
}

void RobotCore::setPerceptionInput(const WorldState& world)\n{\n    perception.setHealthy(world.sensorsHealthy);\n    perception.setLine(world.line);\n    perception.setObstacle(world.obstacleDetected, world.obstacleDistanceCm);\n    perception.setTarget(world.targetDetected);\n    perception.setTargetPicked(world.targetPicked);\n    perception.setTargetPlaced(world.targetPlaced);\n    perception.setColor(world.targetColor.color, world.targetColor.confidence, world.targetColor.valid);\n    perception.setHome(world.homeDetected);\n    perception.setEndGameReady(world.endGameReady);\n    perception.setAllTasksDone(world.allAutonomousTasksDone);\n}\n\nconst WorldState& RobotCore::worldState() const\n{\n    return perception.state();\n}\n\nString RobotCore::colorName() const\n{\n    return String(Perception::colorName(perception.state().targetColor.color));\n}\n\nString RobotCore::phaseName() const
{
    return decisionEngine.phaseName();
}

void RobotCore::completeRescue()
{
    if (!missionActive) {
        return;
    }

    decisionEngine.rescueCompleted();
    handleMission();
}

void RobotCore::stop()
{
    missionActive = false;
    currentMode = RobotMode::IDLE;
    decisionEngine.clearGoal();
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
    decisionEngine.clearGoal();
    motionController.stopGait();
}

bool RobotCore::reportPerson()
{
    if (coreFault || !missionActive) {
        return false;
    }

    personDetected = true;
    decisionEngine.targetDetected();
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

    if (decisionEngine.setGoal("RETURN_HOME")) {
        missionActive = true;
        currentMode = RobotMode::RETURN_HOME;
        handleMission();
    }
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

String RobotCore::goalName() const
{
    return decisionEngine.goalName();
}

String RobotCore::actionName() const
{
    return decisionEngine.actionName();
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
