#pragma once

struct ImuReading {
    float pitch;
    float roll;
    float yaw;
    bool valid;
};

class ImuInterface {
public:
    void begin();
    ImuReading read() const;
};
