#include "ColorSensorInterface.h"
#include <math.h>
void ColorSensorInterface::begin() {}
RGBReading ColorSensorInterface::read() const { return {}; }
DetectedColor ColorSensorInterface::classify(const RGBReading& rgb, float& confidence) {
 confidence=0.0f; if(!rgb.valid) return DetectedColor::NONE;
 const float r=rgb.r,g=rgb.g,b=rgb.b,total=r+g+b; if(total<=0) return DetectedColor::UNKNOWN;
 const float rn=r/total,gn=g/total,bn=b/total,mx=fmax(rn,fmax(gn,bn)),mn=fmin(rn,fmin(gn,bn));
 if(mx-mn<0.08f){confidence=0.85f;return total<120?DetectedColor::BLACK:DetectedColor::WHITE;}
 if(rn>gn*1.35f&&rn>bn*1.35f){confidence=.90f;return DetectedColor::RED;}
 if(gn>rn*1.25f&&gn>bn*1.20f){confidence=.88f;return DetectedColor::GREEN;}
 if(bn>rn*1.25f&&bn>gn*1.20f){confidence=.88f;return DetectedColor::BLUE;}
 if(rn>bn*1.25f&&gn>bn*1.20f){confidence=.86f;return DetectedColor::YELLOW;}
 confidence=.35f; return DetectedColor::UNKNOWN;
}