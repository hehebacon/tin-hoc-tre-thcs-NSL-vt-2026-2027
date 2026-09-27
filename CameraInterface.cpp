#include "CameraInterface.h"

void CameraInterface::begin()
{
}

CameraFrameInfo CameraInterface::observe() const
{
    return {false, false, 0.0f};
}
