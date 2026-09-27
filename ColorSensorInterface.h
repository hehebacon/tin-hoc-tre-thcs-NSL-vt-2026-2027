#pragma once
#include "Perception.h"
struct RGBReading { uint16_t r=0; uint16_t g=0; uint16_t b=0; bool valid=false; };
class ColorSensorInterface {
public:
 void begin();
 RGBReading read() const;
 static DetectedColor classify(const RGBReading& rgb, float& confidence);
};