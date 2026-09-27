#include "Perception.h"

void Perception::begin() { world = WorldState{}; }
void Perception::update() {}

const WorldState& Perception::state() const { return world; }

void Perception::setLine(LineState value) { world.line = value; }
void Perception::setObstacle(bool detected, float distanceCm) {
    world.obstacleDetected = detected;
    world.obstacleDistanceCm = distanceCm;
}
void Perception::setTarget(bool detected) { world.targetDetected = detected; }
void Perception::setTargetPicked(bool value) { world.targetPicked = value; }
void Perception::setTargetClassified(bool value) { world.targetClassified = value; }
void Perception::setTargetPlaced(bool value) { world.targetPlaced = value; }
void Perception::setColor(DetectedColor color, float confidence, bool valid) {
    world.targetColor = {color, confidence, valid};
}
void Perception::setHome(bool value) { world.homeDetected = value; }
void Perception::setEndGameReady(bool value) { world.endGameReady = value; }
void Perception::setAllTasksDone(bool value) { world.allAutonomousTasksDone = value; }
void Perception::setHealthy(bool value) { world.sensorsHealthy = value; }

const char* Perception::colorName(DetectedColor c) {
    switch(c) {
        case DetectedColor::RED: return "RED";
        case DetectedColor::GREEN: return "GREEN";
        case DetectedColor::BLUE: return "BLUE";
        case DetectedColor::YELLOW: return "YELLOW";
        case DetectedColor::BLACK: return "BLACK";
        case DetectedColor::WHITE: return "WHITE";
        case DetectedColor::UNKNOWN: return "UNKNOWN";
        default: return "NONE";
    }
}
const char* Perception::lineName(LineState l) {
    switch(l) {
        case LineState::LEFT: return "LEFT";
        case LineState::CENTER: return "CENTER";
        case LineState::RIGHT: return "RIGHT";
        case LineState::INTERSECTION: return "INTERSECTION";
        default: return "LOST";
    }
}
DetectedColor Perception::parseColor(const String& raw) {
    String v=raw; v.trim(); v.toUpperCase();
    if(v=="RED") return DetectedColor::RED;
    if(v=="GREEN") return DetectedColor::GREEN;
    if(v=="BLUE") return DetectedColor::BLUE;
    if(v=="YELLOW") return DetectedColor::YELLOW;
    if(v=="BLACK") return DetectedColor::BLACK;
    if(v=="WHITE") return DetectedColor::WHITE;
    if(v=="UNKNOWN") return DetectedColor::UNKNOWN;
    return DetectedColor::NONE;
}
LineState Perception::parseLine(const String& raw) {
    String v=raw; v.trim(); v.toUpperCase();
    if(v=="LEFT") return LineState::LEFT;
    if(v=="CENTER" || v=="CENTRE") return LineState::CENTER;
    if(v=="RIGHT") return LineState::RIGHT;
    if(v=="INTERSECTION" || v=="CROSS") return LineState::INTERSECTION;
    return LineState::LOST;
}