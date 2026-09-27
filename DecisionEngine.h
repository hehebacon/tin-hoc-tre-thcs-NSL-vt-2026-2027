#pragma once

#include <Arduino.h>

enum class DecisionGoal {
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

    DecisionOutput update(const DecisionInputs& inputs);

    DecisionGoal goal() const;
    DecisionAction action() const;
    String goalName() const;
    String actionName() const;

private:
    DecisionGoal currentGoal = DecisionGoal::NONE;
    DecisionAction currentAction = DecisionAction::IDLE;
    bool targetLatched = false;
    bool rescueDone = false;

    static DecisionGoal parseGoal(const String& goal);
};
