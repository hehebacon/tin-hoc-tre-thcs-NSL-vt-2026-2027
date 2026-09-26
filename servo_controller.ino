#include <Arduino.h>

#include "ServoCalibration.h"
#include "config.h"
#include "ServoManager.h"
#include "Kinematics.h"

// ============================================================
// AI QUADRUPED ROBOT - MAIN FIRMWARE
// ============================================================

enum LegID {
    FL = 0,
    FR = 1,
    RL = 2,
    RR = 3
};

const char* LEG_NAMES[LEG_COUNT] = {
    "FL", "FR", "RL", "RR"
};

const uint8_t SERVO_MAP[LEG_COUNT][3] = {
    {0, 1, 2},
    {3, 4, 5},
    {6, 7, 8},
    {9, 10, 11}
};

struct LegState {
    float coxa;
    float femur;
    float tibia;
};

LegState legs[LEG_COUNT];

ServoCalibrator calibrator;
ServoManager servoManager;

Kinematics ik(
    45.0f,
    75.0f,
    105.0f
);

String serialBuffer;

// ============================================================
// HELPERS
// ============================================================

int parseLegName(String name)
{
    name.trim();
    name.toUpperCase();

    if (name == "FL") return FL;
    if (name == "FR") return FR;
    if (name == "RL") return RL;
    if (name == "RR") return RR;

    return -1;
}

void setServoCalibrated(int channel, int rawAngle)
{
    int calibratedAngle = calibrator.apply(channel, rawAngle);

    Serial.printf(
        "[SERVO] CH%02d raw=%d calibrated=%d\n",
        channel,
        rawAngle,
        calibratedAngle
    );

    servoManager.setAngle(channel, calibratedAngle);
}

void setLeg(int leg, int coxa, int femur, int tibia)
{
    if (leg < 0 || leg >= LEG_COUNT) {
        Serial.println("[LEG] Invalid leg");
        return;
    }

    legs[leg].coxa = coxa;
    legs[leg].femur = femur;
    legs[leg].tibia = tibia;

    setServoCalibrated(SERVO_MAP[leg][0], coxa);
    setServoCalibrated(SERVO_MAP[leg][1], femur);
    setServoCalibrated(SERVO_MAP[leg][2], tibia);

    Serial.printf(
        "[LEG] %s -> raw C:%d F:%d T:%d\n",
        LEG_NAMES[leg],
        coxa,
        femur,
        tibia
    );
}

void setLegIK(int leg, float x, float y, float z)
{
    if (leg < 0 || leg >= LEG_COUNT) {
        Serial.println("[IK] Invalid leg");
        return;
    }

    JointAngles result = ik.solve(x, y, z);

    if (!result.valid) {
        Serial.printf(
            "[IK] %s position unreachable\n",
            LEG_NAMES[leg]
        );
        return;
    }

    Serial.printf(
        "[IK] %s -> C:%.2f F:%.2f T:%.2f\n",
        LEG_NAMES[leg],
        result.coxa,
        result.femur,
        result.tibia
    );

    setLeg(
        leg,
        (int)result.coxa,
        (int)result.femur,
        (int)result.tibia
    );
}

// ============================================================
// HELP
// ============================================================

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
    Serial.println("  enable");
    Serial.println("  disable");
    Serial.println("  debug");

    Serial.println();
    Serial.println("SERVO");
    Serial.println("  servo <channel> <angle>");
    Serial.println("  leg <FL|FR|RL|RR> <coxa> <femur> <tibia>");

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
    Serial.println("EXAMPLES");
    Serial.println("  servo 0 90");
    Serial.println("  leg FL 90 90 90");
    Serial.println("  ik 80 0 -100");
    Serial.println("  ikleg FL 80 0 -100");
    Serial.println("  cal");
    Serial.println("  caloffset 0 5");
    Serial.println("  calinvert 1 1");
    Serial.println("  callimit 2 10 170");

    Serial.println("================================================");
    Serial.println();
}

// ============================================================
// STATUS / DEBUG
// ============================================================

void printRobotStatus()
{
    Serial.println();
    Serial.println("============== ROBOT STATUS ==============");
    Serial.printf("Robot    : %s\n", ROBOT_NAME);
    Serial.printf("Firmware : %s\n", FIRMWARE_VERSION);
    Serial.println("Mode     : SIMULATION");
    Serial.println("PCA9685  : NOT CONNECTED");
    Serial.println("Servos   : NOT CONNECTED");
    Serial.println();

    for (int i = 0; i < LEG_COUNT; i++) {
        Serial.printf(
            "%s | C:%6.2f F:%6.2f T:%6.2f\n",
            LEG_NAMES[i],
            legs[i].coxa,
            legs[i].femur,
            legs[i].tibia
        );
    }

    Serial.println("==========================================");
    servoManager.status();
}

void debugModules()
{
    Serial.println();
    Serial.println("========== MODULE DEBUG ==========");

    Serial.printf("[OK] config.h              | Robot=%s\n", ROBOT_NAME);
    Serial.printf("[OK] ServoManager          | channels=%d\n", SERVO_COUNT);
    Serial.println("[OK] ServoCalibration");
    Serial.println("[OK] Kinematics");
    Serial.println("[OK] Main firmware");

    Serial.println();
    Serial.println("[INFO] Hardware:");
    Serial.println("       PCA9685 : OFFLINE");
    Serial.println("       Servos  : OFFLINE");
    Serial.println("       Camera  : OFFLINE");
    Serial.println("       Voice   : OFFLINE");

    Serial.println("==================================");
    Serial.println();
}

void testIK(float x, float y, float z)
{
    JointAngles result = ik.solve(x, y, z);

    Serial.println();
    Serial.println("=============== IK RESULT ===============");
    Serial.printf("Input X : %.2f mm\n", x);
    Serial.printf("Input Y : %.2f mm\n", y);
    Serial.printf("Input Z : %.2f mm\n", z);
    Serial.println();

    if (result.valid) {
        Serial.printf("Coxa    : %.2f deg\n", result.coxa);
        Serial.printf("Femur   : %.2f deg\n", result.femur);
        Serial.printf("Tibia   : %.2f deg\n", result.tibia);
        Serial.println("Status  : VALID");
    } else {
        Serial.println("Status  : UNREACHABLE");
    }

    Serial.println("==========================================");
    Serial.println();
}

// ============================================================
// COMMAND PROCESSOR
// ============================================================

void processCommand(String command)
{
    command.trim();

    if (command.length() == 0)
        return;

    Serial.printf("[CMD] %s\n", command.c_str());

    if (command == "help") {
        printHelp();
        return;
    }

    if (command == "debug") {
        debugModules();
        return;
    }

    if (command == "status") {
        printRobotStatus();
        return;
    }

    if (command == "cal") {
        calibrator.printAll();
        return;
    }

    if (command.startsWith("cal ")) {
        int channel;

        if (sscanf(command.c_str(), "cal %d", &channel) == 1) {
            calibrator.print(channel);
        } else {
            Serial.println("[ERROR] cal <channel>");
        }

        return;
    }

    if (command.startsWith("caloffset ")) {
        int channel;
        int offset;

        if (
            sscanf(
                command.c_str(),
                "caloffset %d %d",
                &channel,
                &offset
            ) == 2
        ) {
            calibrator.setOffset(channel, offset);
            calibrator.print(channel);
        } else {
            Serial.println(
                "[ERROR] caloffset <channel> <offset>"
            );
        }

        return;
    }

    if (command.startsWith("calinvert ")) {
        int channel;
        int invert;

        if (
            sscanf(
                command.c_str(),
                "calinvert %d %d",
                &channel,
                &invert
            ) == 2
        ) {
            calibrator.setInvert(channel, invert != 0);
            calibrator.print(channel);
        } else {
            Serial.println(
                "[ERROR] calinvert <channel> <0|1>"
            );
        }

        return;
    }

    if (command.startsWith("callimit ")) {
        int channel;
        int minAngle;
        int maxAngle;

        if (
            sscanf(
                command.c_str(),
                "callimit %d %d %d",
                &channel,
                &minAngle,
                &maxAngle
            ) == 3
        ) {
            calibrator.setLimits(
                channel,
                minAngle,
                maxAngle
            );
            calibrator.print(channel);
        } else {
            Serial.println(
                "[ERROR] callimit <channel> <min> <max>"
            );
        }

        return;
    }

    if (command == "center") {
        for (int i = 0; i < SERVO_COUNT; i++) {
            setServoCalibrated(i, 90);
        }

        for (int i = 0; i < LEG_COUNT; i++) {
            legs[i] = {90.0f, 90.0f, 90.0f};
        }

        return;
    }

    if (command == "enable") {
        servoManager.enableAll();
        return;
    }

    if (command == "disable") {
        servoManager.disableAll();
        return;
    }

    if (command.startsWith("servo ")) {
        int channel;
        int angle;

        if (
            sscanf(
                command.c_str(),
                "servo %d %d",
                &channel,
                &angle
            ) == 2
        ) {
            setServoCalibrated(channel, angle);
        } else {
            Serial.println(
                "[ERROR] servo <channel> <angle>"
            );
        }

        return;
    }

    if (command.startsWith("leg ")) {
        char name[4];
        int coxa;
        int femur;
        int tibia;

        if (
            sscanf(
                command.c_str(),
                "leg %3s %d %d %d",
                name,
                &coxa,
                &femur,
                &tibia
            ) == 4
        ) {
            int leg = parseLegName(String(name));

            setLeg(
                leg,
                coxa,
                femur,
                tibia
            );
        } else {
            Serial.println(
                "[ERROR] leg <FL|FR|RL|RR> <C> <F> <T>"
            );
        }

        return;
    }

    if (command.startsWith("ik ")) {
        float x;
        float y;
        float z;

        if (
            sscanf(
                command.c_str(),
                "ik %f %f %f",
                &x,
                &y,
                &z
            ) == 3
        ) {
            testIK(x, y, z);
        } else {
            Serial.println(
                "[ERROR] ik <x> <y> <z>"
            );
        }

        return;
    }

    if (command.startsWith("ikleg ")) {
        char name[4];
        float x;
        float y;
        float z;

        if (
            sscanf(
                command.c_str(),
                "ikleg %3s %f %f %f",
                name,
                &x,
                &y,
                &z
            ) == 4
        ) {
            int leg = parseLegName(String(name));

            setLegIK(
                leg,
                x,
                y,
                z
            );
        } else {
            Serial.println(
                "[ERROR] ikleg <FL|FR|RL|RR> <x> <y> <z>"
            );
        }

        return;
    }

    Serial.println("[ERROR] Unknown command.");
    Serial.println("Type 'help' for available commands.");
}

// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(115200);

    delay(500);

    Serial.println();
    Serial.println("================================================");
    Serial.println("             AI QUADRUPED ROBOT");
    Serial.println("================================================");

    Serial.printf("Firmware : %s\n", FIRMWARE_VERSION);
    Serial.printf("Target   : %s\n", ROBOT_NAME);
    Serial.println();

    Serial.println("[BOOT] Starting firmware...");

    calibrator.begin();
    servoManager.begin();

    for (int i = 0; i < LEG_COUNT; i++) {
        legs[i] = {
            90.0f,
            90.0f,
            90.0f
        };
    }

    debugModules();

    Serial.println("[BOOT] Simulation mode ACTIVE");
    Serial.println("[BOOT] Firmware READY");
    Serial.println("[BOOT] Type 'help' for commands");
    Serial.println();
}

void loop()
{
    while (Serial.available()) {
        char c = Serial.read();

        if (c == '\n' || c == '\r') {
            if (serialBuffer.length() > 0) {
                processCommand(serialBuffer);
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
