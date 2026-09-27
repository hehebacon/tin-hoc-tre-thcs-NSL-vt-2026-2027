#include "Perception.h"

void Perception::begin() { world = WorldState{}; }
void Perception::update() {}
const WorldState& Perception::state() const { return world; }

void Perception::setLine(bool detected, bool intersection) {
    world.lineDetected = detected;
    world.intersectionDetected = intersection;
    world.line = intersection ? LineState::INTERSECTION : (detected ? LineState::CENTER : LineState::LOST);
}

void Perception::setObstacle(bool detected, float distanceMm) {
    world.obstacleDetected = detected;
    world.obstacleDistance = distanceMm;
    world.obstacleDistanceCm = distanceMm / 10.0f;
}

void Perception::setTarget(bool detected) { world.targetDetected = detected; }
void Perception::setTargetPicked(bool value) { world.targetPicked = value; }
void Perception::setTargetClassified(bool value) { world.targetClassified = value; }
void Perception::setTargetPlaced(bool value) { world.targetPlaced = value; }

void Perception::setColor(DetectedColor color, float confidence, bool valid) {
    world.targetColor = color;
    world.colorConfidence = confidence;
    world.targetColorObservation.color = color;
    world.targetColorObservation.confidence = confidence;
    world.targetColorObservation.valid = valid;
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

const char* Perception::lineName(LineState line) {
    switch(line) {
        case LineState::LEFT: return "LEFT";
        case LineState::CENTER: return "CENTER";
        case LineState::RIGHT: return "RIGHT";
        case LineState::INTERSECTION: return "INTERSECTION";
        default: return "LOST";
    }
}

LineState Perception::parseLine(const String& raw) {
    String v=raw; v.trim(); v.toUpperCase();
    if(v=="LEFT") return LineState::LEFT;
    if(v=="CENTER" || v=="DETECTED") return LineState::CENTER;
    if(v=="RIGHT") return LineState::RIGHT;
    if(v=="INTERSECTION" || v=="CROSS") return LineState::INTERSECTION;
    return LineState::LOST;
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
