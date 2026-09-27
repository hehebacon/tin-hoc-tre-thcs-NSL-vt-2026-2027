#include "RobotWebServer.h"
#include "config.h"
#include "WIFI_CONFIG.h"

static const char* AP_SSID = "XZORT-RESCUE";
static const char* AP_PASS = "robot1234";

RobotWebServer::RobotWebServer(RobotCore& c, MotionController& m, MotionSafety& s)
    : core(c), motion(m), safety(s), server(80) {}

void RobotWebServer::begin() {
    offlineAI.begin();
    onlineAI.begin();

    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP(AP_SSID, AP_PASS);

    if (strlen(ROBOT_WIFI_SSID) > 0) {
        WiFi.begin(ROBOT_WIFI_SSID, ROBOT_WIFI_PASSWORD);
    }

    server.on("/", HTTP_GET, [this]() { root(); });
    server.on("/api/status", HTTP_GET, [this]() { status(); });
    server.on("/api/chat", HTTP_GET, [this]() { chat(); });
    server.on("/api/command", HTTP_GET, [this]() { command(); });
    server.begin();
}

void RobotWebServer::update() {
    server.handleClient();
}

String RobotWebServer::ip() const {
    if (WiFi.status() == WL_CONNECTED) return WiFi.localIP().toString();
    return WiFi.softAPIP().toString();
}

bool RobotWebServer::internetReady() const {
    return WiFi.status() == WL_CONNECTED;
}

String RobotWebServer::jsonEscape(const String& value) {
    String out;
    for (size_t i = 0; i < value.length(); ++i) {
        const char c = value[i];
        if (c == '"') out += "\\\"";
        else if (c == '\\') out += "\\\\";
        else if (c == '\n') out += "\\n";
        else if (c == '\r') out += "\\r";
        else out += c;
    }
    return out;
}

void RobotWebServer::root() {
    server.send(200, "text/html; charset=utf-8", page());
}

void RobotWebServer::status() {
    const RobotCoreStatus s = core.status();
    const WorldState& w = core.worldState();

    String j = "{";
    j += "\"robot\":\"" + String(ROBOT_NAME) + "\",";
    j += "\"firmware\":\"" + String(FIRMWARE_VERSION) + "\",";
    j += "\"wifi_mode\":\"AP+STA\",";
    j += "\"internet\":" + String(internetReady() ? "true" : "false") + ",";
    j += "\"online_ai_configured\":" + String(onlineAI.configured() ? "true" : "false") + ",";
    j += "\"phase\":\"" + core.phaseName() + "\",";
    j += "\"goal\":\"" + core.goalName() + "\",";
    j += "\"action\":\"" + core.actionName() + "\",";
    j += "\"mode\":\"" + core.modeName() + "\",";
    j += "\"color\":\"" + core.colorName() + "\",";
    j += "\"color_confidence\":" + String(w.targetColor.confidence, 2) + ",";
    j += "\"line\":\"" + String(Perception::lineName(w.line)) + "\",";
    j += "\"target\":" + String(w.targetDetected ? "true" : "false") + ",";
    j += "\"obstacle\":" + String(w.obstacleDetected ? "true" : "false") + ",";
    j += "\"active\":" + String(s.missionActive ? "true" : "false") + ",";
    j += "\"fault\":" + String(s.fault ? "true" : "false");
    j += "}";
    server.send(200, "application/json", j);
}

void RobotWebServer::chat() {
    const String q = server.arg("q");
    const RobotAIResult local = offlineAI.think(q);

    if (local.intent != RobotAIIntent::NONE) {
        intent(local.intent);
        String reply = jsonEscape(local.reply);
        server.send(200, "application/json",
                    "{\"source\":\"offline\",\"reply\":\"" + reply +
                    "\",\"phase\":\"" + core.phaseName() +
                    "\",\"action\":\"" + core.actionName() + "\"}");
        return;
    }

    String prompt =
        "You are the online assistant for an ESP32 rescue quadruped robot. "
        "Do not issue direct servo commands. Give safe, concise diagnostic or planning advice. "
        "Current robot state: phase=" + core.phaseName() +
        ", mode=" + core.modeName() +
        ", goal=" + core.goalName() +
        ", action=" + core.actionName() +
        ", color=" + core.colorName() +
        ", line=" + String(Perception::lineName(core.worldState().line)) +
        ". User request: " + q;

    const OnlineAIResult remote = onlineAI.ask(prompt);
    String reply = jsonEscape(remote.text);
    String source = remote.ok ? "gemini" : "offline-fallback";

    if (!remote.ok && reply.length() == 0) {
        reply = "Online AI unavailable. Robot remains on offline safety logic.";
    }

    server.send(200, "application/json",
                "{\"source\":\"" + source + "\",\"reply\":\"" + reply +
                "\",\"phase\":\"" + core.phaseName() +
                "\",\"action\":\"" + core.actionName() + "\"}");
}

void RobotWebServer::command() {
    String c = server.arg("cmd");
    c.toUpperCase();
    bool ok = true;

    if (c == "AUTONOMOUS") core.startAutonomous();
    else if (c == "DRIVER") core.startDriverControl();
    else if (c == "ENDGAME") core.startEndGame();
    else if (c == "STOP") {
        core.stop();
        safety.emergencyStop();
        motion.disable();
    } else if (c == "RESUME") {
        safety.resume();
        motion.enable();
        ok = core.resume();
    } else if (c == "STAND") {
        motion.stand();
    } else if (c == "CENTER") {
        motion.center();
    } else if (c == "FINISH") {
        core.finishCompetition();
    } else ok = false;

    server.send(200, "application/json",
                String("{\"ok\":") + (ok ? "true" : "false") + "}");
}

void RobotWebServer::intent(RobotAIIntent i) {
    switch (i) {
        case RobotAIIntent::STOP:
            core.stop(); safety.emergencyStop(); motion.disable(); break;
        case RobotAIIntent::RESUME:
            safety.resume(); motion.enable(); core.resume(); break;
        case RobotAIIntent::AUTONOMOUS: core.startAutonomous(); break;
        case RobotAIIntent::DRIVER: core.startDriverControl(); break;
        case RobotAIIntent::END_GAME: core.startEndGame(); break;
        case RobotAIIntent::RETURN_HOME: core.returnHome(); break;
        case RobotAIIntent::RESCUE: core.setGoal("RESCUE"); break;
        case RobotAIIntent::PATROL: core.setGoal("PATROL"); break;
        case RobotAIIntent::STAND: motion.stand(); break;
        case RobotAIIntent::CENTER: motion.center(); break;
        case RobotAIIntent::DEMO: core.setGoal("DEMO"); break;
        default: break;
    }
}

String RobotWebServer::page() {
    return R"HTML(
<!doctype html><html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XZORT Rescue Quadruped AI</title>
<style>
body{font-family:system-ui;background:#080d14;color:#eef;margin:0}
main{max-width:1000px;margin:auto;padding:20px}.c{background:#111b27;border:1px solid #26384d;border-radius:16px;padding:16px;margin:12px 0}
.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:9px}
button,input{padding:11px;border-radius:10px;border:1px solid #40536a;background:#101824;color:#fff}
input{width:62%}pre{white-space:pre-wrap}.ok{font-weight:700}
</style></head><body><main>
<h1>XZORT Rescue Quadruped</h1>
<p>Offline AI + Gemini Online AI + Perception</p>
<div class="c"><b>Robot status</b><pre id="s">loading...</pre></div>
<div class="c"><div class="g">
<button onclick="cmd('AUTONOMOUS')">AUTONOMOUS</button>
<button onclick="cmd('DRIVER')">DRIVER</button>
<button onclick="cmd('ENDGAME')">END GAME</button>
<button onclick="cmd('FINISH')">FINISH</button>
<button onclick="cmd('STAND')">STAND</button>
<button onclick="cmd('CENTER')">CENTER</button>
<button onclick="cmd('STOP')">STOP</button>
<button onclick="cmd('RESUME')">RESUME</button>
</div></div>
<div class="c"><b>AI chat</b><br><br>
<input id="q" placeholder="Ví dụ: robot đang làm gì?">
<button onclick="chat()">Gửi</button><pre id="r"></pre></div>
<script>
async function refresh(){try{let x=await fetch('/api/status');s.textContent=JSON.stringify(await x.json(),null,2)}catch(e){s.textContent='WEB OFFLINE'}}
async function cmd(x){await fetch('/api/command?cmd='+encodeURIComponent(x));refresh()}
async function chat(){let x=await fetch('/api/chat?q='+encodeURIComponent(q.value));let j=await x.json();r.textContent='['+j.source+'] '+j.reply;refresh()}
setInterval(refresh,1000);refresh();
</script></main></body></html>)HTML";
}
