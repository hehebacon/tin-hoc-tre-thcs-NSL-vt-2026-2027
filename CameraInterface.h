#pragma once

struct CameraFrameInfo {
    bool valid;
    bool personDetected;
    float confidence;
};

class CameraInterface {
public:
    void begin();
    CameraFrameInfo observe() const;
};
