from enum import Enum


class RobotState(str, Enum):
    IDLE = "IDLE"
    PATROLLING = "PATROLLING"
    SEARCHING = "SEARCHING"
    TARGET_DETECTED = "TARGET_DETECTED"
    RETURNING = "RETURNING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


class StateMachine:
    def __init__(self):
        self.state = RobotState.IDLE

    def update(self, mode, found, searching, at_base):
        if mode == "PATROL":
            self.state = RobotState.PATROLLING
        elif found and not at_base:
            self.state = RobotState.RETURNING
        elif found and at_base:
            self.state = RobotState.COMPLETE
        elif searching:
            self.state = RobotState.SEARCHING
        elif mode == "AUTONOMOUS":
            self.state = RobotState.PATROLLING
        else:
            self.state = RobotState.IDLE
        return self.state.value
