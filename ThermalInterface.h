#pragma once

struct ThermalReading {
    float temperature;
    float hotspot;
    bool personSignature;
    bool valid;
};

class ThermalInterface {
public:
    void begin();
    ThermalReading read() const;
};
