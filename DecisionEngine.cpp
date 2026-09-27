#include "DecisionEngine.h"

void DecisionEngine::begin() {
    currentGoal=DecisionGoal::NONE;
    currentAction=DecisionAction::IDLE;
    currentPhase=CompetitionPhase::IDLE;
    competitionInputs=CompetitionInputs{};
    competitionStateValue=CompetitionState::IDLE;
    recoveryStateValue=RecoverySubState::BACKTRACK;
    stateTimer=millis();
    targetLatched=false;
    rescueDone=false;
}
bool DecisionEngine::setGoal(const String& goal){
    String v=goal; v.trim(); v.toUpperCase();
    DecisionGoal n=parseGoal(v);
    if(n==DecisionGoal::NONE && v!="NONE") return false;
    currentGoal=n; targetLatched=false; rescueDone=false; currentAction=DecisionAction::IDLE;
    if(n==DecisionGoal::AUTONOMOUS_COURSE) startAutonomous();
    else if(n==DecisionGoal::NONE) currentPhase=CompetitionPhase::IDLE;
    return true;
}
void DecisionEngine::clearGoal(){currentGoal=DecisionGoal::NONE;currentAction=DecisionAction::IDLE;currentPhase=CompetitionPhase::IDLE;competitionStateValue=CompetitionState::IDLE;}
void DecisionEngine::targetDetected(){targetLatched=true;}
void DecisionEngine::rescueCompleted(){rescueDone=true;targetLatched=true;}

void DecisionEngine::startAutonomous(){
    currentPhase=CompetitionPhase::AUTONOMOUS;
    currentGoal=DecisionGoal::AUTONOMOUS_COURSE;
    competitionStateValue=CompetitionState::FOLLOW_LINE;
    recoveryStateValue=RecoverySubState::BACKTRACK;
    stateTimer=millis();
    currentAction=DecisionAction::LINE_FOLLOW;
}
void DecisionEngine::startDriverControl(){currentPhase=CompetitionPhase::DRIVER_CONTROL;currentGoal=DecisionGoal::NONE;currentAction=DecisionAction::DRIVER;}
void DecisionEngine::startEndGame(){currentPhase=CompetitionPhase::END_GAME;competitionStateValue=CompetitionState::END_GAME_HOME;currentAction=DecisionAction::ENDGAME;stateTimer=millis();}
void DecisionEngine::finish(){currentPhase=CompetitionPhase::FINISHED;currentAction=DecisionAction::FINISH;competitionStateValue=CompetitionState::IDLE;}
void DecisionEngine::setCompetitionInput(const CompetitionInputs& i){competitionInputs=i;}

void DecisionEngine::handleLineFollowing(){
    if(competitionInputs.obstacleDetected && competitionInputs.obstacleDistance < 150.0f){
        competitionStateValue=CompetitionState::OBSTACLE_AVOIDANCE;
        currentAction=DecisionAction::APPROACH;
        stateTimer=millis();
        return;
    }
    if(!competitionInputs.lineDetected && !competitionInputs.intersectionDetected){
        competitionStateValue=CompetitionState::RECOVERY_LINE_LOST;
        recoveryStateValue=RecoverySubState::BACKTRACK;
        currentAction=DecisionAction::SEARCH;
        stateTimer=millis();
        return;
    }
    currentAction=DecisionAction::LINE_FOLLOW;
}

void DecisionEngine::handleRecovery(){
    if(competitionInputs.lineDetected || competitionInputs.intersectionDetected){
        competitionStateValue=CompetitionState::FOLLOW_LINE;
        currentAction=DecisionAction::LINE_FOLLOW;
        return;
    }
    const unsigned long elapsed=millis()-stateTimer;
    switch(recoveryStateValue){
        case RecoverySubState::BACKTRACK:
            currentAction=DecisionAction::SEARCH;
            if(elapsed>1500){recoveryStateValue=RecoverySubState::SCAN_LEFT;stateTimer=millis();}
            break;
        case RecoverySubState::SCAN_LEFT:
            currentAction=DecisionAction::SEARCH;
            if(elapsed>2000){recoveryStateValue=RecoverySubState::SCAN_RIGHT;stateTimer=millis();}
            break;
        case RecoverySubState::SCAN_RIGHT:
            currentAction=DecisionAction::SEARCH;
            if(elapsed>4000){recoveryStateValue=RecoverySubState::FAILED;}
            break;
        case RecoverySubState::FAILED:
            competitionStateValue=CompetitionState::EMERGENCY_STOP;
            currentAction=DecisionAction::FAULT;
            break;
    }
}

void DecisionEngine::handleObstacle(){
    if(!competitionInputs.obstacleDetected){
        competitionStateValue=CompetitionState::FOLLOW_LINE;
        currentAction=DecisionAction::LINE_FOLLOW;
        return;
    }
    currentAction=DecisionAction::APPROACH;
}

DecisionOutput DecisionEngine::updateCompetition(){
    if(!competitionInputs.sensorsHealthy){
        competitionStateValue=CompetitionState::EMERGENCY_STOP;
        currentAction=DecisionAction::FAULT;
        return {currentGoal,currentAction,false};
    }

    switch(competitionStateValue){
        case CompetitionState::IDLE:
            if(competitionInputs.lineDetected || competitionInputs.intersectionDetected){
                competitionStateValue=CompetitionState::FOLLOW_LINE;
                currentAction=DecisionAction::LINE_FOLLOW;
            }
            break;
        case CompetitionState::FOLLOW_LINE:
            if(competitionInputs.targetDetected && !competitionInputs.targetPicked){competitionStateValue=CompetitionState::PICK_TARGET;currentAction=DecisionAction::PICKUP;}
            else if(competitionInputs.allAutonomousTasksDone && competitionInputs.endGameReady){startEndGame();}
            else handleLineFollowing();
            break;
        case CompetitionState::RECOVERY_LINE_LOST: handleRecovery(); break;
        case CompetitionState::OBSTACLE_AVOIDANCE: handleObstacle(); break;
        case CompetitionState::PICK_TARGET:
            currentAction=competitionInputs.targetPicked?DecisionAction::CLASSIFY:DecisionAction::PICKUP;
            if(competitionInputs.targetPicked) competitionStateValue=CompetitionState::CLASSIFY_TARGET;
            break;
        case CompetitionState::CLASSIFY_TARGET:
            currentAction=competitionInputs.targetClassified?DecisionAction::PLACE:DecisionAction::CLASSIFY;
            if(competitionInputs.targetClassified) competitionStateValue=CompetitionState::PLACE_TARGET;
            break;
        case CompetitionState::PLACE_TARGET:
            currentAction=competitionInputs.targetPlaced?DecisionAction::LINE_FOLLOW:DecisionAction::PLACE;
            if(competitionInputs.targetPlaced) competitionStateValue=CompetitionState::FOLLOW_LINE;
            break;
        case CompetitionState::END_GAME_HOME:
            if(competitionInputs.homeDetected) finish();
            else currentAction=DecisionAction::ENDGAME;
            break;
        case CompetitionState::EMERGENCY_STOP:
            currentAction=DecisionAction::FAULT;
            break;
    }
    return {currentGoal,currentAction,currentPhase!=CompetitionPhase::IDLE&&currentPhase!=CompetitionPhase::FINISHED&&currentAction!=DecisionAction::FAULT};
}

CompetitionPhase DecisionEngine::phase() const{return currentPhase;}
String DecisionEngine::phaseName() const{
    switch(currentPhase){
        case CompetitionPhase::AUTONOMOUS:return "AUTONOMOUS";
        case CompetitionPhase::DRIVER_CONTROL:return "DRIVER_CONTROL";
        case CompetitionPhase::END_GAME:return "END_GAME";
        case CompetitionPhase::FINISHED:return "FINISHED";
        default:return "IDLE";
    }
}
DecisionOutput DecisionEngine::update(const DecisionInputs& i){
    if(!i.sensorsHealthy){currentAction=DecisionAction::FAULT;return {currentGoal,currentAction,false};}
    switch(currentGoal){
        case DecisionGoal::RESCUE:currentAction=(i.rescueComplete||rescueDone)?DecisionAction::RETURN_HOME:((i.personDetected||i.thermalSignature||targetLatched)?DecisionAction::RESCUE:DecisionAction::SEARCH);break;
        case DecisionGoal::PATROL:currentAction=DecisionAction::PATROL;break;
        case DecisionGoal::RETURN_HOME:currentAction=DecisionAction::RETURN_HOME;break;
        case DecisionGoal::DEMO:currentAction=DecisionAction::DEMO;break;
        case DecisionGoal::AUTONOMOUS_COURSE:return updateCompetition();
        default:currentAction=DecisionAction::IDLE;break;
    }
    return {currentGoal,currentAction,currentAction!=DecisionAction::IDLE&&currentAction!=DecisionAction::FAULT};
}
DecisionGoal DecisionEngine::goal() const{return currentGoal;}
DecisionAction DecisionEngine::action() const{return currentAction;}
String DecisionEngine::goalName() const{
    switch(currentGoal){case DecisionGoal::RESCUE:return "RESCUE";case DecisionGoal::PATROL:return "PATROL";case DecisionGoal::RETURN_HOME:return "RETURN_HOME";case DecisionGoal::DEMO:return "DEMO";case DecisionGoal::AUTONOMOUS_COURSE:return "AUTONOMOUS_COURSE";default:return "NONE";}
}
String DecisionEngine::actionName() const{
    switch(currentAction){case DecisionAction::SEARCH:return "SEARCH";case DecisionAction::APPROACH:return "APPROACH";case DecisionAction::RESCUE:return "RESCUE";case DecisionAction::RETURN_HOME:return "RETURN_HOME";case DecisionAction::PATROL:return "PATROL";case DecisionAction::DEMO:return "DEMO";case DecisionAction::LINE_FOLLOW:return "LINE_FOLLOW";case DecisionAction::PICKUP:return "PICKUP";case DecisionAction::CLASSIFY:return "CLASSIFY";case DecisionAction::PLACE:return "PLACE";case DecisionAction::DRIVER:return "DRIVER";case DecisionAction::ENDGAME:return "ENDGAME";case DecisionAction::FINISH:return "FINISH";case DecisionAction::FAULT:return "FAULT";default:return "IDLE";}
}
DecisionGoal DecisionEngine::parseGoal(const String& g){
    if(g=="RESCUE")return DecisionGoal::RESCUE;
    if(g=="PATROL")return DecisionGoal::PATROL;
    if(g=="RETURN_HOME")return DecisionGoal::RETURN_HOME;
    if(g=="DEMO")return DecisionGoal::DEMO;
    if(g=="AUTONOMOUS"||g=="AUTONOMOUS_COURSE")return DecisionGoal::AUTONOMOUS_COURSE;
    if(g=="NONE")return DecisionGoal::NONE;
    return DecisionGoal::NONE;
}
