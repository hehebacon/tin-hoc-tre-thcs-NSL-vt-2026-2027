#pragma once
#include <Arduino.h>

enum class CompetitionPhase { IDLE, AUTONOMOUS, DRIVER_CONTROL, END_GAME, FINISHED };
enum class CompetitionState { IDLE, FOLLOW_LINE, RECOVERY_LINE_LOST, OBSTACLE_AVOIDANCE, PICK_TARGET, CLASSIFY_TARGET, PLACE_TARGET, END_GAME_HOME, EMERGENCY_STOP };
enum class RecoverySubState { BACKTRACK, SCAN_LEFT, SCAN_RIGHT, FAILED };

enum class DecisionGoal { NONE, RESCUE, PATROL, RETURN_HOME, DEMO, AUTONOMOUS_COURSE };

enum class DecisionAction {
    IDLE, SEARCH, APPROACH, RESCUE, RETURN_HOME, PATROL, DEMO,
    LINE_FOLLOW, PICKUP, CLASSIFY, PLACE, DRIVER, ENDGAME, FINISH, FAULT
};

struct DecisionInputs {
    bool sensorsHealthy;
    bool personDetected;
    bool thermalSignature;
    bool rescueComplete;
};

struct CompetitionInputs {
    bool sensorsHealthy = true;
    bool lineDetected = false;
    bool intersectionDetected = false;
    bool obstacleDetected = false;
    float obstacleDistance = 999.0f;
    bool targetDetected = false;
    bool targetPicked = false;
    bool targetClassified = false;
    bool targetPlaced = false;
    bool allAutonomousTasksDone = false;
    bool endGameReady = false;
    bool homeDetected = false;
};

struct DecisionOutput {
    DecisionGoal goal;
    DecisionAction action;
    bool missionActive;
};

class DecisionEngine {
public:
    void begin();
    bool setGoal(const String& goal);
    void clearGoal();
    void targetDetected();
    void rescueCompleted();

    void startAutonomous();
    void startDriverControl();
    void startEndGame();
    void finish();
    void setCompetitionInput(const CompetitionInputs& inputs);
    DecisionOutput updateCompetition();

    CompetitionPhase phase() const;
    String phaseName() const;
    DecisionOutput update(const DecisionInputs& inputs);

    DecisionGoal goal() const;
    DecisionAction action() const;
    String goalName() const;
    String actionName() const;

    CompetitionState competitionState() const { return competitionStateValue; }
    RecoverySubState recoveryState() const { return recoveryStateValue; }

private:
    DecisionGoal currentGoal = DecisionGoal::NONE;
    DecisionAction currentAction = DecisionAction::IDLE;
    CompetitionPhase currentPhase = CompetitionPhase::IDLE;
    CompetitionInputs competitionInputs{};
    CompetitionState competitionStateValue = CompetitionState::IDLE;
    RecoverySubState recoveryStateValue = RecoverySubState::BACKTRACK;
    unsigned long stateTimer = 0;
    bool targetLatched = false;
    bool rescueDone = false;

    void handleLineFollowing();
    void handleRecovery();
    void handleObstacle();
    static DecisionGoal parseGoal(const String& goal);
};