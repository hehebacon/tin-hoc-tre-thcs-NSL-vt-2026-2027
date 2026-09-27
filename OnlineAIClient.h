#pragma once
#include <Arduino.h>

struct OnlineAIResult {
    bool ok = false;
    String text;
    int httpCode = 0;
};

class OnlineAIClient {
public:
    void begin();
    OnlineAIResult ask(const String& prompt) const;
    bool configured() const;
    bool online() const;
    const String& lastError() const;
    const char* provider() const { return "Gemini"; }

private:
    mutable bool lastOnline = false;
    mutable String error;
};