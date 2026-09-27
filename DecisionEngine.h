#pragma once

#include <Arduino.h>

enum class CompetitionPhase { IDLE, AUTONOMOUS, DRIVER_CONTROL, END_GAME, FINISHED };\n\nenum class DecisionGoal {
    NONE,
    RESCUE,
    PATROL,
    RETURN_HOME,
    DEMO
};

enum class DecisionAction {
    IDLE,
    SEARCH,
    APPROACH,
    RESCUE,
    RETURN_HOME,
    PATROL,
    DEMO,
    FAULT
};

struct DecisionInputs {
    bool sensorsHealthy;
    bool personDetected;
    bool thermalSignature;
    bool rescueComplete;
};

struct CompetitionInputs { bool sensorsHealthy=true; bool lineDetected=false; bool intersectionDetected=false; bool obstacleDetected=false; bool targetDetected=false; bool targetPicked=false; bool targetPlaced=false; bool allAutonomousTasksDone=false; bool endGameReady=false; bool homeDetected=false; };\n\nstruct DecisionOutput {
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
    void rescueCompleted();\n    void startAutonomous();\n    void startDriverControl();\n    void startEndGame();\n    void finish();\n    void setCompetitionInput(const CompetitionInputs& inputs);\n    DecisionOutput updateCompetition();\n    CompetitionPhase phase() const;\n    String phaseName() const;

    DecisionOutput update(const DecisionInputs& inputs);

    DecisionGoal goal() const;
    DecisionAction action() const;
    String goalName() const;
    String actionName() const;

private:
    DecisionGoal currentGoal = DecisionGoal::NONE;
    DecisionAction currentAction = DecisionAction::IDLE;\n    CompetitionPhase currentPhase = CompetitionPhase::IDLE;\n    CompetitionInputs competitionInputs{};
    bool targetLatched = false;
    bool rescueDone = false;

    static DecisionGoal parseGoal(const String& goal);
};
