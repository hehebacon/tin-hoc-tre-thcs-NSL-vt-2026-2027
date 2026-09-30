#pragma once

#include <Arduino.h>
#include "RobotConfig.h"
#include "FootTrajectory.h"

class MotionSet {
public:
    enum class Pose : uint8_t {
        STAND,
        SIT,
        CROUCH,
        READY,
        RECOVERY
    };

    enum class Action : uint8_t {
        NONE,
        WALK_FORWARD,
        WALK_BACKWARD,
        TURN_LEFT,
        TURN_RIGHT,
        SEARCH,
        RESCUE
    };

    MotionSet();

    void reset();
    void setPose(Pose pose);
    void setAction(Action action);
    void stop();
    void update(float dt);

    Pose pose() const;
    Action action() const;
    bool active() const;
    float transition() const;

    static const char* poseName(Pose pose);
    static const char* actionName(Action action);

private:
    Pose currentPose_;
    Pose targetPose_;
    Action action_;
    float transition_;
    bool active_;

    float poseHeight(Pose pose) const;
};
