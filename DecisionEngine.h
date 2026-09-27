#pragma once
#include <Arduino.h>

enum class CompetitionPhase { IDLE, AUTONOMOUS, DRIVER_CONTROL, END_GAME, FINISHED };

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
    bool targetDetected = false;
    bool targetPicked = false;
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

private:
    DecisionGoal currentGoal = DecisionGoal::NONE;
    DecisionAction currentAction = DecisionAction::IDLE;
    CompetitionPhase currentPhase = CompetitionPhase::IDLE;
    CompetitionInputs competitionInputs{};
    bool targetLatched = false;
    bool rescueDone = false;
    static DecisionGoal parseGoal(const String& goal);
};
