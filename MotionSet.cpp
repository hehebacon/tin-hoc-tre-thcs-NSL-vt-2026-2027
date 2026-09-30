#include "MotionSet.h"
#include <math.h>

namespace {
constexpr float TRANSITION_RATE = 3.0f;
}

MotionSet::MotionSet()
    : currentPose_(Pose::STAND),
      targetPose_(Pose::STAND),
      action_(Action::NONE),
      transition_(1.0f),
      active_(false) {}

void MotionSet::reset() {
    currentPose_ = Pose::STAND;
    targetPose_ = Pose::STAND;
    action_ = Action::NONE;
    transition_ = 1.0f;
    active_ = false;
}

void MotionSet::setPose(Pose pose) {
    if (pose == targetPose_ && transition_ >= 1.0f)
        return;

    targetPose_ = pose;
    transition_ = 0.0f;
    active_ = true;
}

void MotionSet::setAction(Action action) {
    action_ = action;
    if (action != Action::NONE)
        active_ = true;
}

void MotionSet::stop() {
    action_ = Action::NONE;
    active_ = false;
    targetPose_ = currentPose_;
    transition_ = 1.0f;
}

void MotionSet::update(float dt) {
    dt = fmaxf(0.0f, fminf(dt, 0.10f));

    if (currentPose_ != targetPose_) {
        transition_ += dt * TRANSITION_RATE;
        if (transition_ >= 1.0f) {
            transition_ = 1.0f;
            currentPose_ = targetPose_;
        }
    }

    active_ = (currentPose_ != targetPose_) || (action_ != Action::NONE);
}

MotionSet::Pose MotionSet::pose() const {
    return currentPose_;
}

MotionSet::Action MotionSet::action() const {
    return action_;
}

bool MotionSet::active() const {
    return active_;
}

float MotionSet::transition() const {
    return transition_;
}

float MotionSet::poseHeight(Pose pose) const {
    switch (pose) {
        case Pose::STAND:    return RobotConfig::DEFAULT_BODY_Z_MM;
        case Pose::READY:    return RobotConfig::DEFAULT_BODY_Z_MM + 5.0f;
        case Pose::CROUCH:   return RobotConfig::DEFAULT_BODY_Z_MM + 25.0f;
        case Pose::SIT:      return RobotConfig::DEFAULT_BODY_Z_MM + 35.0f;
        case Pose::RECOVERY: return RobotConfig::DEFAULT_BODY_Z_MM + 10.0f;
    }
    return RobotConfig::DEFAULT_BODY_Z_MM;
}

const char* MotionSet::poseName(Pose pose) {
    switch (pose) {
        case Pose::STAND: return "STAND";
        case Pose::SIT: return "SIT";
        case Pose::CROUCH: return "CROUCH";
        case Pose::READY: return "READY";
        case Pose::RECOVERY: return "RECOVERY";
    }
    return "UNKNOWN";
}

const char* MotionSet::actionName(Action action) {
    switch (action) {
        case Action::NONE: return "NONE";
        case Action::WALK_FORWARD: return "WALK_FORWARD";
        case Action::WALK_BACKWARD: return "WALK_BACKWARD";
        case Action::TURN_LEFT: return "TURN_LEFT";
        case Action::TURN_RIGHT: return "TURN_RIGHT";
        case Action::SEARCH: return "SEARCH";
        case Action::RESCUE: return "RESCUE";
    }
    return "UNKNOWN";
}
