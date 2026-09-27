#pragma once
#include "Perception.h"
struct LineReading { LineState state=LineState::LOST; float confidence=0.0f; bool valid=false; };
class LineSensorInterface { public: void begin(); LineReading read() const; };