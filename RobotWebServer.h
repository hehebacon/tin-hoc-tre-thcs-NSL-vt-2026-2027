#pragma once
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include "RobotCore.h"
#include "MotionController.h"
#include "MotionSafety.h"
#include "RobotAI.h"
class RobotWebServer{
public:
 RobotWebServer(RobotCore& c,MotionController& m,MotionSafety& s);
 void begin(); void update(); String ip() const;
private:
 RobotCore& core; MotionController& motion; MotionSafety& safety; RobotAI ai; WebServer server;
 void root(); void status(); void chat(); void command(); void intent(RobotAIIntent i); static String page();
};