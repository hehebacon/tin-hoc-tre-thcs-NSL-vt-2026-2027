#include "ImuInterface.h"

void ImuInterface::begin()
{
}

ImuReading ImuInterface::read() const
{
    return {0.0f, 0.0f, 0.0f, false};
}
