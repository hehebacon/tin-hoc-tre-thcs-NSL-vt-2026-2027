#pragma once
#include <Arduino.h>
enum class RobotAIIntent { NONE, STOP, RESUME, AUTONOMOUS, DRIVER, END_GAME, STATUS, STAND, CENTER, PATROL, RETURN_HOME, RESCUE, DEMO };
struct RobotAIResult { RobotAIIntent intent=RobotAIIntent::NONE; String reply; };
class RobotAI {
public: void begin(); RobotAIResult think(const String& text) const; String name() const;
private: static bool has(const String& text,const char* needle);
};