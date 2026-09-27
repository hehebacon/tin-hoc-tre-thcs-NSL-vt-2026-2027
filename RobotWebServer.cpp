#include "RobotWebServer.h"
#include "config.h"
static const char* SSID="XZORT-RESCUE";
static const char* PASS="robot1234";
RobotWebServer::RobotWebServer(RobotCore& c,MotionController& m,MotionSafety& s):core(c),motion(m),safety(s),server(80){}
void RobotWebServer::begin(){
 ai.begin(); WiFi.mode(WIFI_AP); WiFi.softAP(SSID,PASS);
 server.on("/",HTTP_GET,[this](){root();});
 server.on("/api/status",HTTP_GET,[this](){status();});
 server.on("/api/chat",HTTP_GET,[this](){chat();});
 server.on("/api/command",HTTP_GET,[this](){command();});
 server.begin();
}
void RobotWebServer::update(){server.handleClient();}
String RobotWebServer::ip() const{return WiFi.softAPIP().toString();}
void RobotWebServer::root(){server.send(200,"text/html; charset=utf-8",page());}
void RobotWebServer::status(){
 RobotCoreStatus s=core.status();
 String j="{"robot":""+String(ROBOT_NAME)+"","firmware":""+String(FIRMWARE_VERSION)+"","phase":""+core.phaseName()+"","goal":""+core.goalName()+"","action":""+core.actionName()+"","mode":""+core.modeName()+"","active":"+(String)(s.missionActive?"true":"false")+","fault":"+(String)(s.fault?"true":"false")+"}";
 server.send(200,"application/json",j);
}
void RobotWebServer::chat(){
 RobotAIResult r=ai.think(server.arg("q")); if(r.intent!=RobotAIIntent::NONE) intent(r.intent);
 String x=r.reply; x.replace("\\","\\\\"); x.replace(""","\\"");
 server.send(200,"application/json","{"reply":""+x+"","phase":""+core.phaseName()+"","action":""+core.actionName()+""}");
}
void RobotWebServer::command(){
 String c=server.arg("cmd"); c.toUpperCase(); bool ok=true;
 if(c=="AUTONOMOUS")core.startAutonomous();
 else if(c=="DRIVER")core.startDriverControl();
 else if(c=="ENDGAME")core.startEndGame();
 else if(c=="STOP"){core.stop();safety.emergencyStop();motion.disable();}
 else if(c=="RESUME"){safety.resume();motion.enable();ok=core.resume();}
 else if(c=="STAND")motion.stand();
 else if(c=="CENTER")motion.center();
 else ok=false;
 server.send(200,"application/json",String("{"ok":")+(ok?"true":"false")+"}");
}
void RobotWebServer::intent(RobotAIIntent i){
 switch(i){
  case RobotAIIntent::STOP: core.stop(); safety.emergencyStop(); motion.disable(); break;
  case RobotAIIntent::RESUME: safety.resume(); motion.enable(); core.resume(); break;
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
String RobotWebServer::page(){return R"HTML(
<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XZORT Rescue AI</title><style>
body{font-family:system-ui;background:#080d14;color:#eef;margin:0}main{max-width:900px;margin:auto;padding:24px}.c{background:#111b27;border:1px solid #26384d;border-radius:16px;padding:18px;margin:12px 0}.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}button,input{padding:11px;border-radius:10px;border:1px solid #40536a;background:#101824;color:#fff}input{width:65%}pre{white-space:pre-wrap}</style>
<main><h1>XZORT Rescue Quadruped</h1><p>Offline AI + Wi-Fi control</p><div class=c><b>Status</b><pre id=s>...</pre></div>
<div class=c><div class=g><button onclick="c('AUTONOMOUS')">AUTONOMOUS</button><button onclick="c('DRIVER')">DRIVER</button><button onclick="c('ENDGAME')">END GAME</button><button onclick="c('STAND')">STAND</button><button onclick="c('CENTER')">CENTER</button><button onclick="c('STOP')">STOP</button><button onclick="c('RESUME')">RESUME</button></div></div>
<div class=c><b>Chat AI</b><br><br><input id=q placeholder="Ví dụ: tự hành"><button onclick="chat()">Gửi</button><pre id=r></pre></div>
<script>
async function refresh(){let x=await fetch('/api/status');document.getElementById('s').textContent=JSON.stringify(await x.json(),null,2)}
async function c(x){await fetch('/api/command?cmd='+encodeURIComponent(x));refresh()}
async function chat(){let x=await fetch('/api/chat?q='+encodeURIComponent(q.value));let j=await x.json();r.textContent=j.reply;refresh()}
setInterval(refresh,1000);refresh();
</script></main>)HTML";}
