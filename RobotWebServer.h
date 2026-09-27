#pragma once
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include "RobotCore.h"
#include "MotionController.h"
#include "MotionSafety.h"
#include "RobotAI.h"
#include "OnlineAIClient.h"

class RobotWebServer {
public:
    RobotWebServer(RobotCore& c, MotionController& m, MotionSafety& s);
    void begin();
    void update();
    String ip() const;
    bool internetReady() const;

private:
    RobotCore& core;
    MotionController& motion;
    MotionSafety& safety;
    RobotAI offlineAI;
    OnlineAIClient onlineAI;
    WebServer server;

    void root();
    void status();
    void chat();
    void command();
    void intent(RobotAIIntent i);
    static String jsonEscape(const String& value);
    static String page();
};