#pragma once

#include <Arduino.h>

class NetworkInterface {
public:
    void begin();
    bool connected() const;
    void sendTelemetry(const String& json);
    bool sendCommand(const String& json);

private:
    bool online = false;
};
