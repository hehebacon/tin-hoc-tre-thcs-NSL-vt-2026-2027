#include "EnvironmentalSensors.h"

void EnvironmentalSensors::begin()
{
}

EnvironmentalReading EnvironmentalSensors::read() const
{
    return {0.0f, 0.0f, 0.0f, false};
}
