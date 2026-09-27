#include "ThermalInterface.h"

void ThermalInterface::begin()
{
}

ThermalReading ThermalInterface::read() const
{
    return {0.0f, 0.0f, false, false};
}
