#include <Arduino.h>

#include "config.h"
#include "MotionController.h"

MotionController motionController;

String serialBuffer;
bool safetyStopLatched = false;
unsigned long lastTelemetryMs = 0;

String jsonValue(const String& json, const String& key)
{
    const String needle = String("\"") + key + "\":\"";
    int start = json.indexOf(needle);
    if (start < 0) return "";
    start += needle.length();
    int end = json.indexOf("\"", start);
    if (end < 0) return "";
    return json.substring(start, end);
}

void processJsonPacket(const String& packet)
{
    String command = jsonValue(packet, "command");
    command.toUpperCase();

    if (command == "STOP") {
        safetyStopLatched = true;
        motionController.disable();
        Serial.println("{\"type\":\"ack\",\"command\":\"STOP\",\"ok\":true}");
        return;
    }

    if (command == "RESUME") {
        safetyStopLatched = false;
        motionController.enable();
        Serial.println("{\"type\":\"ack\",\"command\":\"RESUME\",\"ok\":true}");
        return;
    }

    if (command == "CENTER") {
        if (safetyStopLatched) {
            Serial.println("{\"type\":\"ack\",\"command\":\"CENTER\",\"ok\":false,\"error\":\"E_STOP\"}");
            return;
        }
        motionController.center();
        Serial.println("{\"type\":\"ack\",\"command\":\"CENTER\",\"ok\":true}");
        return;
    }

    if (command == "STAND") {
        if (safetyStopLatched) {
            Serial.println("{\"type\":\"ack\",\"command\":\"STAND\",\"ok\":false,\"error\":\"E_STOP\"}");
            return;
        }
        motionController.stand();
        Serial.println("{\"type\":\"ack\",\"command\":\"STAND\",\"ok\":true}");
        return;
    }

    Serial.println("{\"type\":\"error\",\"error\":\"UNKNOWN_COMMAND\"}");
}

void emitTelemetry()
{
    if (millis() - lastTelemetryMs < 1000)
        return;

    lastTelemetryMs = millis();
    Serial.printf(
        "{\"type\":\"telemetry\",\"firmware\":\"%s\",\"safety_stop\":%s,\"hardware_mode\":\"SIMULATION\"}\n",
        FIRMWARE_VERSION,
        safetyStopLatched ? "true" : "false"
    );
}

void printHelp()
{
    Serial.println();
    Serial.println("================================================");
    Serial.println("             AI QUADRUPED ROBOT");
    Serial.println("================================================");

    Serial.println("SYSTEM");
    Serial.println("  help");
    Serial.println("  status");
    Serial.println("  center");
    Serial.println("  stand");
    Serial.println("  enable");
    Serial.println("  disable");
    Serial.println("  debug");

    Serial.println();
    Serial.println("SERVO");
    Serial.println("  servo <channel> <angle>");
    Serial.println("  leg <FL|FR|RL|RR> <C> <F> <T>");

    Serial.println();
    Serial.println("CALIBRATION");
    Serial.println("  cal");
    Serial.println("  cal <channel>");
    Serial.println("  caloffset <channel> <offset>");
    Serial.println("  calinvert <channel> <0|1>");
    Serial.println("  callimit <channel> <min> <max>");

    Serial.println();
    Serial.println("KINEMATICS");
    Serial.println("  ik <x> <y> <z>");
    Serial.println("  ikleg <FL|FR|RL|RR> <x> <y> <z>");

    Serial.println();
    Serial.println("MOTION");
    Serial.println("  pose <FL|FR|RL|RR> <x> <y> <z>");
    Serial.println("  stand");

    Serial.println();
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

    Serial.printf(
        "[CMD] %s\n",
        command.c_str()
    );

    if (command == "help") {
        printHelp();
        return;
    }

    if (command == "status") {
        motionController.status();
        return;
    }

    if (command == "debug") {
        motionController.debug();
        return;
    }

    if (command == "center") {
        motionController.center();
        return;
    }

    if (command == "stand") {
        motionController.stand();
        return;
    }

    if (command == "enable") {
        motionController.enable();
        return;
    }

    if (command == "disable") {
        motionController.disable();
        return;
    }

    if (command == "cal") {
        motionController.printCalibration();
        return;
    }

    int channel;
    int angle;
    int offset;
    int invert;
    int minAngle;
    int maxAngle;

    if (sscanf(
            command.c_str(),
            "cal %d",
            &channel
        ) == 1) {

        motionController.printCalibration(
            channel
        );

        return;
    }

    if (sscanf(
            command.c_str(),
            "caloffset %d %d",
            &channel,
            &offset
        ) == 2) {

        motionController.setCalibrationOffset(
            channel,
            offset
        );

        return;
    }

    if (sscanf(
            command.c_str(),
            "calinvert %d %d",
            &channel,
            &invert
        ) == 2) {

        motionController.setCalibrationInvert(
            channel,
            invert != 0
        );

        return;
    }

    if (sscanf(
            command.c_str(),
            "callimit %d %d %d",
            &channel,
            &minAngle,
            &maxAngle
        ) == 3) {

        motionController.setCalibrationLimits(
            channel,
            minAngle,
            maxAngle
        );

        return;
    }

    if (sscanf(
            command.c_str(),
            "servo %d %d",
            &channel,
            &angle
        ) == 2) {

        motionController.setServo(
            channel,
            angle
        );

        return;
    }

    char name[4];

    int coxa;
    int femur;
    int tibia;

    if (sscanf(
            command.c_str(),
            "leg %3s %d %d %d",
            name,
            &coxa,
            &femur,
            &tibia
        ) == 4) {

        motionController.setLeg(
            String(name),
            coxa,
            femur,
            tibia
        );

        return;
    }

    float x;
    float y;
    float z;

    if (sscanf(
            command.c_str(),
            "ik %f %f %f",
            &x,
            &y,
            &z
        ) == 3) {

        motionController.testIK(
            x,
            y,
            z
        );

        return;
    }

    if (sscanf(
            command.c_str(),
            "ikleg %3s %f %f %f",
            name,
            &x,
            &y,
            &z
        ) == 4) {

        motionController.setLegIK(
            String(name),
            x,
            y,
            z
        );

        return;
    }

    if (sscanf(
            command.c_str(),
            "pose %3s %f %f %f",
            name,
            &x,
            &y,
            &z
        ) == 4) {

        motionController.setLegIK(
            String(name),
            x,
            y,
            z
        );

        return;
    }

    Serial.println(
        "[ERROR] Unknown command."
    );

    Serial.println(
        "Type 'help' for commands."
    );
}

void setup()
{
    Serial.begin(
        SERIAL_BAUD
    );

    delay(500);

    Serial.println();
    Serial.println(
        "================================================"
    );

    Serial.println(
        "             AI QUADRUPED ROBOT"
    );

    Serial.println(
        "================================================"
    );

    Serial.printf(
        "Firmware : %s\n",
        FIRMWARE_VERSION
    );

    Serial.printf(
        "Target   : %s\n",
        ROBOT_NAME
    );

    Serial.println();

    motionController.begin();

    Serial.println(
        "[BOOT] Firmware READY"
    );

    Serial.println(
        "[BOOT] Type 'help' for commands"
    );

    Serial.println();
}

void loop()
{
    emitTelemetry();

    while (Serial.available()) {

        const char c =
            static_cast<char>(
                Serial.read()
            );

        if (c == '\n' || c == '\r') {

            if (serialBuffer.length() > 0) {

                processCommand(
                    serialBuffer
                );

                serialBuffer = "";
            }

        } else {

            serialBuffer += c;

            if (serialBuffer.length() > 128) {

                serialBuffer = "";

                Serial.println(
                    "[ERROR] Command too long"
                );
            }
        }
    }
}