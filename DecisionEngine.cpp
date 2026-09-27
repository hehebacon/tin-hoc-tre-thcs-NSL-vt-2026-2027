#include "DecisionEngine.h"

void DecisionEngine::begin()
{
    currentGoal = DecisionGoal::NONE;
    currentAction = DecisionAction::IDLE;
    targetLatched = false;
    rescueDone = false;
}

bool DecisionEngine::setGoal(const String& goal)
{
    String value = goal;
    value.trim();
    value.toUpperCase();

    const DecisionGoal next = parseGoal(value);
    if (next == DecisionGoal::NONE && value != "NONE") {
        return false;
    }

    currentGoal = next;
    targetLatched = false;
    rescueDone = false;
    currentAction = DecisionAction::IDLE;
    return true;
}

void DecisionEngine::clearGoal()
{
    currentGoal = DecisionGoal::NONE;
    currentAction = DecisionAction::IDLE;
    targetLatched = false;
    rescueDone = false;
}

void DecisionEngine::targetDetected()
{
    targetLatched = true;
}

void DecisionEngine::rescueCompleted()
{
    rescueDone = true;
    targetLatched = true;
}

DecisionOutput DecisionEngine::update(const DecisionInputs& inputs)
{
    if (!inputs.sensorsHealthy) {
        currentAction = DecisionAction::FAULT;
        return {currentGoal, currentAction, false};
    }

    switch (currentGoal) {
        case DecisionGoal::RESCUE:
            if (inputs.rescueComplete || rescueDone) {
                currentAction = DecisionAction::RETURN_HOME;
            } else if (inputs.personDetected || inputs.thermalSignature || targetLatched) {
                targetLatched = true;
                currentAction = DecisionAction::RESCUE;
            } else {
                currentAction = DecisionAction::SEARCH;
            }
            break;

        case DecisionGoal::PATROL:
            currentAction = DecisionAction::PATROL;
            break;

        case DecisionGoal::RETURN_HOME:
            currentAction = DecisionAction::RETURN_HOME;
            break;

        case DecisionGoal::DEMO:
            currentAction = DecisionAction::DEMO;
            break;

        case DecisionGoal::NONE:
        default:
            currentAction = DecisionAction::IDLE;
            break;
    }

    return {
        currentGoal,
        currentAction,
        currentAction != DecisionAction::IDLE &&
        currentAction != DecisionAction::FAULT
    };
}

DecisionGoal DecisionEngine::goal() const
{
    return currentGoal;
}

DecisionAction DecisionEngine::action() const
{
    return currentAction;
}

String DecisionEngine::goalName() const
{
    switch (currentGoal) {
        case DecisionGoal::RESCUE: return "RESCUE";
        case DecisionGoal::PATROL: return "PATROL";
        case DecisionGoal::RETURN_HOME: return "RETURN_HOME";
        case DecisionGoal::DEMO: return "DEMO";
        case DecisionGoal::NONE:
        default: return "NONE";
    }
}

String DecisionEngine::actionName() const
{
    switch (currentAction) {
        case DecisionAction::SEARCH: return "SEARCH";
        case DecisionAction::APPROACH: return "APPROACH";
        case DecisionAction::RESCUE: return "RESCUE";
        case DecisionAction::RETURN_HOME: return "RETURN_HOME";
        case DecisionAction::PATROL: return "PATROL";
        case DecisionAction::DEMO: return "DEMO";
        case DecisionAction::FAULT: return "FAULT";
        case DecisionAction::IDLE:
        default: return "IDLE";
    }
}

DecisionGoal DecisionEngine::parseGoal(const String& goal)
{
    if (goal == "RESCUE") return DecisionGoal::RESCUE;
    if (goal == "PATROL") return DecisionGoal::PATROL;
    if (goal == "RETURN_HOME") return DecisionGoal::RETURN_HOME;
    if (goal == "DEMO") return DecisionGoal::DEMO;
    if (goal == "NONE") return DecisionGoal::NONE;
    return DecisionGoal::NONE;
}
