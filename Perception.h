#pragma once
#include <Arduino.h>

enum class DetectedColor { NONE, RED, GREEN, BLUE, YELLOW, BLACK, WHITE, UNKNOWN };
enum class LineState { LOST, LEFT, CENTER, RIGHT, INTERSECTION };

struct ColorObservation {
    DetectedColor color = DetectedColor::NONE;
    float confidence = 0.0f;
    bool valid = false;
};

// Compatibility wrapper: keeps .color/.confidence/.valid while behaving like DetectedColor.
struct TargetColorState {
    DetectedColor color = DetectedColor::NONE;
    float confidence = 0.0f;
    bool valid = false;
    operator DetectedColor() const { return color; }
};

struct WorldState {
    bool lineDetected = false;
    bool intersectionDetected = false;
    bool obstacleDetected = false;
    float obstacleDistance = 999.0f; // mm
    bool targetDetected = false;
    bool targetPicked = false;
    bool targetClassified = false;
    bool targetPlaced = false;
    TargetColorState targetColor{};
    float colorConfidence = 0.0f;
    bool homeDetected = false;
    bool endGameReady = false;
    bool allAutonomousTasksDone = false;
    bool sensorsHealthy = true;

    // Legacy aliases retained during the API migration.
    LineState line = LineState::LOST;
    float obstacleDistanceCm = 999.0f;
};

class PerceptionSystem {
public:
    virtual ~PerceptionSystem() = default;
    virtual void updateSensors() = 0;
    virtual WorldState getWorldState() = 0;
};

class Perception : public PerceptionSystem {
public:
    void begin();
    void update();
    void updateSensors() override { update(); }
    WorldState getWorldState() override { return world; }
    const WorldState& state() const;

    void setLine(bool detected, bool intersection = false);
    void setObstacle(bool detected, float distanceMm = 999.0f);
    void setTarget(bool detected);
    void setTargetPicked(bool value);
    void setTargetClassified(bool value);
    void setTargetPlaced(bool value);
    void setColor(DetectedColor color, float confidence, bool valid = true);
    void setHome(bool value);
    void setEndGameReady(bool value);
    void setAllTasksDone(bool value);
    void setHealthy(bool value);

    static const char* colorName(DetectedColor color);
    static const char* colorName(const TargetColorState& color) { return colorName(color.color); }
    static const char* lineName(LineState line);
    static LineState parseLine(const String& value);
    static DetectedColor parseColor(const String& value);

private:
    WorldState world{};
};
