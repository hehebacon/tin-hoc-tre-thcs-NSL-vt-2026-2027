#pragma once
#include <Arduino.h>

enum class DetectedColor {
    NONE,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    BLACK,
    WHITE,
    UNKNOWN
};

enum class LineState {
    LOST,
    LEFT,
    CENTER,
    RIGHT,
    INTERSECTION
};

struct ColorObservation {
    DetectedColor color = DetectedColor::NONE;
    float confidence = 0.0f;
    bool valid = false;
};

struct WorldState {
    bool sensorsHealthy = true;
    LineState line = LineState::LOST;
    bool obstacleDetected = false;
    float obstacleDistanceCm = -1.0f;
    bool targetDetected = false;
    bool targetPicked = false;
    bool targetPlaced = false;
    ColorObservation targetColor{};
    bool homeDetected = false;
    bool endGameReady = false;
    bool allAutonomousTasksDone = false;
};

class Perception {
public:
    void begin();
    void update();
    const WorldState& state() const;

    void setLine(LineState value);
    void setObstacle(bool detected, float distanceCm = -1.0f);
    void setTarget(bool detected);
    void setTargetPicked(bool value);
    void setTargetPlaced(bool value);
    void setColor(DetectedColor color, float confidence, bool valid = true);
    void setHome(bool value);
    void setEndGameReady(bool value);
    void setAllTasksDone(bool value);
    void setHealthy(bool value);

    static const char* colorName(DetectedColor color);
    static const char* lineName(LineState line);
    static DetectedColor parseColor(const String& value);
    static LineState parseLine(const String& value);

private:
    WorldState world{};
};