#pragma once

struct EnvironmentalReading {
    float temperature;
    float humidity;
    float pressure;
    bool valid;
};

class EnvironmentalSensors {
public:
    void begin();
    EnvironmentalReading read() const;
};
