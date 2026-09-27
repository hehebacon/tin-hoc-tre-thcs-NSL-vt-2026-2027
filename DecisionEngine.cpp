#include "DecisionEngine.h"

void DecisionEngine::begin(){ currentGoal=DecisionGoal::NONE; currentAction=DecisionAction::IDLE; currentPhase=CompetitionPhase::IDLE; competitionInputs=CompetitionInputs{}; targetLatched=false; rescueDone=false; }
bool DecisionEngine::setGoal(const String& goal){
    String v=goal; v.trim(); v.toUpperCase(); DecisionGoal n=parseGoal(v);
    if(n==DecisionGoal::NONE && v!="NONE") return false;
    currentGoal=n; targetLatched=false; rescueDone=false; currentAction=DecisionAction::IDLE;
    if(n==DecisionGoal::AUTONOMOUS_COURSE) startAutonomous(); else if(n==DecisionGoal::NONE) currentPhase=CompetitionPhase::IDLE;
    return true;
}
void DecisionEngine::clearGoal(){ currentGoal=DecisionGoal::NONE; currentAction=DecisionAction::IDLE; currentPhase=CompetitionPhase::IDLE; targetLatched=false; rescueDone=false; }
void DecisionEngine::targetDetected(){ targetLatched=true; }
void DecisionEngine::rescueCompleted(){ rescueDone=true; targetLatched=true; }
void DecisionEngine::startAutonomous(){ currentPhase=CompetitionPhase::AUTONOMOUS; currentGoal=DecisionGoal::AUTONOMOUS_COURSE; currentAction=DecisionAction::LINE_FOLLOW; }
void DecisionEngine::startDriverControl(){ currentPhase=CompetitionPhase::DRIVER_CONTROL; currentGoal=DecisionGoal::NONE; currentAction=DecisionAction::DRIVER; }
void DecisionEngine::startEndGame(){ currentPhase=CompetitionPhase::END_GAME; currentAction=DecisionAction::ENDGAME; }
void DecisionEngine::finish(){ currentPhase=CompetitionPhase::FINISHED; currentAction=DecisionAction::FINISH; }
void DecisionEngine::setCompetitionInput(const CompetitionInputs& i){ competitionInputs=i; }

DecisionOutput DecisionEngine::updateCompetition(){
    if(!competitionInputs.sensorsHealthy){ currentAction=DecisionAction::FAULT; return {currentGoal,currentAction,false}; }
    switch(currentPhase){
        case CompetitionPhase::AUTONOMOUS:
            if(competitionInputs.allAutonomousTasksDone && competitionInputs.endGameReady){ startEndGame(); break; }
            if(competitionInputs.targetDetected && !competitionInputs.targetPicked) currentAction=DecisionAction::PICKUP;
            else if(competitionInputs.targetPicked && !competitionInputs.targetClassified) currentAction=DecisionAction::CLASSIFY;
            else if(competitionInputs.targetClassified && !competitionInputs.targetPlaced) currentAction=DecisionAction::PLACE;
            else if(competitionInputs.targetPlaced) currentAction=DecisionAction::LINE_FOLLOW;
            else if(competitionInputs.obstacleDetected) currentAction=DecisionAction::APPROACH;
            else if(competitionInputs.lineDetected || competitionInputs.intersectionDetected) currentAction=DecisionAction::LINE_FOLLOW;
            else currentAction=DecisionAction::SEARCH;
            break;
        case CompetitionPhase::DRIVER_CONTROL: currentAction=DecisionAction::DRIVER; break;
        case CompetitionPhase::END_GAME: if(competitionInputs.homeDetected) finish(); else currentAction=DecisionAction::ENDGAME; break;
        case CompetitionPhase::FINISHED: currentAction=DecisionAction::FINISH; break;
        default: currentAction=DecisionAction::IDLE; break;
    }
    return {currentGoal,currentAction,currentPhase!=CompetitionPhase::IDLE && currentPhase!=CompetitionPhase::FINISHED && currentAction!=DecisionAction::FAULT};
}
CompetitionPhase DecisionEngine::phase() const{return currentPhase;}
String DecisionEngine::phaseName() const{
    switch(currentPhase){case CompetitionPhase::AUTONOMOUS:return "AUTONOMOUS";case CompetitionPhase::DRIVER_CONTROL:return "DRIVER_CONTROL";case CompetitionPhase::END_GAME:return "END_GAME";case CompetitionPhase::FINISHED:return "FINISHED";default:return "IDLE";}
}
DecisionOutput DecisionEngine::update(const DecisionInputs& i){
    if(!i.sensorsHealthy){currentAction=DecisionAction::FAULT;return {currentGoal,currentAction,false};}
    switch(currentGoal){
        case DecisionGoal::RESCUE: currentAction=(i.rescueComplete||rescueDone)?DecisionAction::RETURN_HOME:((i.personDetected||i.thermalSignature||targetLatched)?DecisionAction::RESCUE:DecisionAction::SEARCH); break;
        case DecisionGoal::PATROL: currentAction=DecisionAction::PATROL; break;
        case DecisionGoal::RETURN_HOME: currentAction=DecisionAction::RETURN_HOME; break;
        case DecisionGoal::DEMO: currentAction=DecisionAction::DEMO; break;
        case DecisionGoal::AUTONOMOUS_COURSE: return updateCompetition();
        default: currentAction=DecisionAction::IDLE; break;
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
    if(g=="RESCUE")return DecisionGoal::RESCUE;if(g=="PATROL")return DecisionGoal::PATROL;if(g=="RETURN_HOME")return DecisionGoal::RETURN_HOME;if(g=="DEMO")return DecisionGoal::DEMO;if(g=="AUTONOMOUS"||g=="AUTONOMOUS_COURSE")return DecisionGoal::AUTONOMOUS_COURSE;if(g=="NONE")return DecisionGoal::NONE;return DecisionGoal::NONE;
}
