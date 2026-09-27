#include <Arduino.h>

#include "config.h"
#include "MotionController.h"
#include "PCA9685ServoDriver.h"
#include "ImuInterface.h"
#include "EnvironmentalSensors.h"
#include "CameraInterface.h"
#include "ThermalInterface.h"
#include "MotionSafety.h"
#include "HardwareStatus.h"
#include "RobotCore.h"

MotionController motionController;
PCA9685ServoDriver pca9685;
ImuInterface imu;
EnvironmentalSensors environmental;
CameraInterface camera;
ThermalInterface thermal;
MotionSafety motionSafety;
RobotCore robotCore(motionController, motionSafety, imu, environmental, camera, thermal);

String serialBuffer;
bool safetyStopLatched = false;
unsigned long lastTelemetryMs = 0;
unsigned long lastMotionMs = 0;

String jsonValue(const String& json, const String& key)
{
    const String needle = String(""") + key + "":"";
    int start = json.indexOf(needle);
    if (start < 0) return "";
    start += needle.length();
    int end = json.indexOf(""", start);
    if (end < 0) return "";
    return json.substring(start, end);
}

void processJsonPacket(const String& packet)
{
    String command = jsonValue(packet, "command");
    command.toUpperCase();

    if (command == "STOP") {
        safetyStopLatched = true;
        motionSafety.emergencyStop();
        motionController.disable();
        Serial.println("{"type":"ack","command":"STOP","ok":true}");
        return;
    }

    if (command == "RESUME") {
        motionSafety.resume();
        safetyStopLatched = false;
        motionController.enable();
        Serial.println("{"type":"ack","command":"RESUME","ok":true}");
        return;
    }

    if (command == "ENABLE") {
        if (safetyStopLatched || !motionSafety.allowed()) {
            Serial.println("{"type":"error","error":"SAFETY_BLOCK"}");
            return;
        }
        motionController.enable();
        motionSafety.noteMotionCommand();
        Serial.println("{"type":"ack","command":"ENABLE"}");
        return;
    }

    if (command == "CENTER") {
        if (safetyStopLatched || !motionSafety.allowed()) {
            Serial.println("{"type":"ack","command":"CENTER","ok":false,"error":"E_STOP"}");
            return;
        }
        motionController.center();
        Serial.println("{"type":"ack","command":"CENTER","ok":true}");
        return;
    }

    if (command == "STAND") {
        if (safetyStopLatched || !motionSafety.allowed()) {
            Serial.println("{"type":"ack","command":"STAND","ok":false,"error":"E_STOP"}");
            return;
        }
        motionController.stand();
        Serial.println("{"type":"ack","command":"STAND","ok":true}");
        return;
    }

    if (command == "MISSION") {
        String mode = jsonValue(packet, "mode");
        if (robotCore.setMode(mode)) {
            Serial.printf(
                "{\"type\":\"ack\",\"command\":\"MISSION\",\"ok\":true,\"mode\":\"%s\"}\\n",
                robotCore.modeName().c_str()
            );
        } else {
            Serial.println("{\"type\":\"ack\",\"command\":\"MISSION\",\"ok\":false}");
        }
        return;
    }

    if (command == "GAIT") {
        String mode = jsonValue(packet, "mode");
        mode.toUpperCase();

        if (safetyStopLatched || !motionSafety.allowed()) {
            Serial.println("{"type":"ack","command":"GAIT","ok":false,"error":"E_STOP"}");
            return;
        }

        if (
            mode != "WALK" &&
            mode != "SLOW_WALK" &&
            mode != "SEARCH" &&
            mode != "RESCUE"
        ) {
            Serial.println("{"type":"ack","command":"GAIT","ok":false,"error":"BAD_MODE"}");
            return;
        }

        motionController.setGait(mode);
        motionSafety.noteMotionCommand();
        Serial.printf(
            "{"type":"ack","command":"GAIT","ok":true,"mode":"%s"}\n",
            mode.c_str()
        );
        return;
    }

    Serial.println("{"type":"error","error":"UNKNOWN_COMMAND"}");
}

void emitTelemetry()
{
    if (millis() - lastTelemetryMs < 1000)
        return;

    lastTelemetryMs = millis();

    HardwareStatus status = {
        pca9685.available(), false, false, false, false, false,
        motionSafety.allowed()
    };

    Serial.printf(
        "{"type":"telemetry","firmware":"%s","safety_stop":%s,"gait":"%s","phase":%.3f,"moving":%s,"hardware":%s}\n",
        FIRMWARE_VERSION,
        safetyStopLatched ? "true" : "false",
        motionController.gait().mode(),
        motionController.gait().phase(),
        motionController.gait().moving() ? "true" : "false",
        hardwareStatusJson(status).c_str()
    );

    const RobotCoreStatus core = robotCore.status();
    Serial.printf(
        "{\"type\":\"core\",\"mode\":\"%s\",\"active\":%s,\"person\":%s,\"thermal\":%s,\"healthy\":%s,\"cycle\":%lu}\n",
        robotCore.modeName().c_str(),
        core.missionActive ? "true" : "false",
        core.personDetected ? "true" : "false",
        core.thermalSignature ? "true" : "false",
        !core.fault ? "true" : "false",
        static_cast<unsigned long>(core.cycle)
    );
}

void printHelp()
{
    Serial.println();
    Serial.println("================================================");
    Serial.println("             AI QUADRUPED ROBOT");
    Serial.println("================================================");
    Serial.println("SYSTEM");
    Serial.println("  help | status | center | stand | enable | disable | debug");
    Serial.println();
    Serial.println("SERVO");
    Serial.println("  servo <channel> <angle>");
    Serial.println("  leg <FL|FR|RL|RR> <C> <F> <T>");
    Serial.println();
    Serial.println("CALIBRATION");
    Serial.println("  cal | cal <channel>");
    Serial.println("  caloffset <channel> <offset>");
    Serial.println("  calinvert <channel> <0|1>");
    Serial.println("  callimit <channel> <min> <max>");
    Serial.println();
    Serial.println("KINEMATICS");
    Serial.println("  ik <x> <y> <z>");
    Serial.println("  ikleg <FL|FR|RL|RR> <x> <y> <z>");
    Serial.println("  pose <FL|FR|RL|RR> <x> <y> <z>");
    Serial.println();
    Serial.println("GAIT");
    Serial.println("  gait <WALK|SLOW_WALK|SEARCH|RESCUE>");
    Serial.println("  mission <IDLE|PATROL|SEARCH|RESCUE|RETURN_HOME>");
    Serial.println("  found | home | mission_status | reset_mission");
    Serial.println("================================================");
    Serial.println();
}

void processCommand(String command)
{
    command.trim();

    if (command.startsWith("{")) {
        processJsonPacket(command);
        return;
    }

    if (command.length() == 0)
        return;

    Serial.printf("[CMD] %s\n", command.c_str());

    if (command == "help") {
        printHelp();
        return;
    }

    if (command == "status") {
        motionController.status();
        return;
    }

    if (command == "mission_status") {
        const RobotCoreStatus state = robotCore.status();
        Serial.printf(
            "[CORE] mode=%s active=%s person=%s thermal=%s healthy=%s cycle=%lu\\n",
            robotCore.modeName().c_str(),
            state.missionActive ? "true" : "false",
            state.personDetected ? "true" : "false",
            state.thermalSignature ? "true" : "false",
            !state.fault ? "true" : "false",
            static_cast<unsigned long>(state.cycle)
        );
        return;
    }

    if (command == "reset_mission") {
        robotCore.resetMission();
        Serial.println("[CORE] mission reset");
        return;
    }

    if (command == "found") {
        if (robotCore.reportPerson())
            Serial.println("[CORE] person detected -> RESCUE");
        else
            Serial.println("[CORE] person report rejected");
        return;
    }

    if (command == "home") {
        robotCore.returnHome();
        Serial.println("[CORE] RETURN_HOME requested");
        return;
    }

    if (command.startsWith("mission ")) {
        String mode = command.substring(8);
        mode.trim();
        if (robotCore.setMode(mode)) {
            Serial.printf("[CORE] mode -> %s\\n", robotCore.modeName().c_str());
        } else {
            Serial.println("[CORE] mission mode rejected");
        }
        return;
    }

    if (command == "debug") {
        motionController.debug();
        return;
    }

    if (command == "center") {
        if (safetyStopLatched || !motionSafety.allowed()) {
            Serial.println("[SAFETY] E-STOP active");
            return;
        }
        motionController.center();
        motionSafety.noteMotionCommand();
        return;
    }

    if (command == "stand") {
        if (safetyStopLatched || !motionSafety.allowed()) {
            Serial.println("[SAFETY] E-STOP active");
            return;
        }
        motionController.stand();
        motionSafety.noteMotionCommand();
        return;
    }

    if (command == "enable") {
        if (safetyStopLatched || !motionSafety.allowed()) {
            Serial.println("[SAFETY] enable blocked");
            return;
        }
        motionController.enable();
        motionSafety.noteMotionCommand();
        return;
    }

    if (command == "disable") {
        motionController.disable();
        return;
    }

    if (command == "stop") {
        safetyStopLatched = true;
        motionSafety.emergencyStop();
        motionController.disable();
        Serial.println("[SAFETY] E-STOP");
        return;
    }

    if (command == "resume") {
        motionSafety.resume();
        safetyStopLatched = false;
        motionController.enable();
        Serial.println("[SAFETY] RESUMED");
        return;
    }

    int channel, angle, offset, invert, minAngle, maxAngle;

    if (command == "cal") {
        motionController.printCalibration();
        return;
    }

    if (sscanf(command.c_str(), "cal %d", &channel) == 1) {
        motionController.printCalibration(channel);
        return;
    }

    if (sscanf(command.c_str(), "caloffset %d %d", &channel, &offset) == 2) {
        motionController.setCalibrationOffset(channel, offset);
        return;
    }

    if (sscanf(command.c_str(), "calinvert %d %d", &channel, &invert) == 2) {
        motionController.setCalibrationInvert(channel, invert != 0);
        return;
    }

    if (sscanf(command.c_str(), "callimit %d %d %d", &channel, &minAngle, &maxAngle) == 3) {
        motionController.setCalibrationLimits(channel, minAngle, maxAngle);
        return;
    }

    if (sscanf(command.c_str(), "servo %d %d", &channel, &angle) == 2) {
        if (safetyStopLatched) {
            Serial.println("[SAFETY] E-STOP active");
            return;
        }
        motionController.setServo(channel, angle);
        return;
    }

    char name[4];
    int coxa, femur, tibia;

    if (sscanf(command.c_str(), "leg %3s %d %d %d", name, &coxa, &femur, &tibia) == 4) {
        motionController.setLeg(String(name), coxa, femur, tibia);
        return;
    }

    float x, y, z;

    if (sscanf(command.c_str(), "ik %f %f %f", &x, &y, &z) == 3) {
        motionController.testIK(x, y, z);
        return;
    }

    if (sscanf(command.c_str(), "ikleg %3s %f %f %f", name, &x, &y, &z) == 4) {
        motionController.setLegIK(String(name), x, y, z);
        return;
    }

    if (sscanf(command.c_str(), "pose %3s %f %f %f", name, &x, &y, &z) == 4) {
        motionController.setFootTarget(String(name), x, y, z);
        return;
    }

    char gaitMode[16];

    if (sscanf(command.c_str(), "gait %15s", gaitMode) == 1) {
        if (safetyStopLatched || !motionSafety.allowed()) {
            Serial.println("[SAFETY] gait blocked");
            return;
        }

        motionController.setGait(String(gaitMode));
        motionSafety.noteMotionCommand();
        return;
    }

    Serial.println("[ERROR] Unknown command. Type 'help'.");
}

void setup()
{
    Serial.begin(SERIAL_BAUD);
    delay(500);

    Serial.println();
    Serial.println("================================================");
    Serial.println("             AI QUADRUPED ROBOT");
    Serial.println("================================================");
    Serial.printf("Firmware : %s\n", FIRMWARE_VERSION);
    Serial.printf("Target   : %s\n", ROBOT_NAME);
    Serial.println();

    motionController.begin();
    pca9685.begin();
    imu.begin();
    environmental.begin();
    camera.begin();
    thermal.begin();
    motionSafety.begin();
    robotCore.begin();

    lastMotionMs = millis();

    Serial.println("[BOOT] Firmware READY");
    Serial.println("[BOOT] Type 'help' for commands");
    Serial.println();
}

void loop()
{
    emitTelemetry();

    if (motionSafety.timedOut() && !safetyStopLatched) {
        safetyStopLatched = true;
        motionSafety.emergencyStop();
        motionController.disable();
        robotCore.stop();
        Serial.println("{\"type\":\"safety\",\"event\":\"MOTION_TIMEOUT\"}");
    }

    const unsigned long now = millis();

    if (
        now - lastMotionMs >= MOTION_UPDATE_MS &&
        !safetyStopLatched &&
        motionSafety.allowed()
    ) {
        const float dt =
            static_cast<float>(now - lastMotionMs) / 1000.0f;

        lastMotionMs = now;
        robotCore.update(dt);
    }

    while (Serial.available()) {
        const char c = static_cast<char>(Serial.read());

        if (c == '
' || c == '') {
            if (serialBuffer.length() > 0) {
                processCommand(serialBuffer);
                serialBuffer = "";
            }
        } else {
            serialBuffer += c;

            if (serialBuffer.length() > 128) {
                serialBuffer = "";
                Serial.println("[ERROR] Command too long");
            }
        }
    }
}
