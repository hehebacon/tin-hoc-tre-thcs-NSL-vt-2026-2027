#include "NetworkInterface.h"

void NetworkInterface::begin()
{
    // Transport is intentionally hardware-neutral for now.
    online = false;
}

bool NetworkInterface::connected() const
{
    return online;
}

void NetworkInterface::sendTelemetry(const String& json)
{
    if (!online) return;
    (void)json;
}

bool NetworkInterface::sendCommand(const String& json)
{
    if (!online) return false;
    (void)json;
    return true;
}
