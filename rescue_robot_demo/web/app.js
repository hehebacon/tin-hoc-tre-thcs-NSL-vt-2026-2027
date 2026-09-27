const API="http://127.0.0.1:8787";
const map=document.querySelector("#map"),connection=document.querySelector("#connection");
const modeLabel=document.querySelector("#mode"),sensor=document.querySelector("#sensor"),events=document.querySelector("#events");
const missionName=document.querySelector("#missionName"),moveset=document.querySelector("#moveset");
const W=24,H=16,S=28;
const obstacles=new Set(["7,1","7,2","7,3","7,4","7,5","12,5","13,5","14,5","15,5","17,9","17,10","17,11","17,12","4,10","5,10","6,10","7,10","8,10"]);
for(let y=0;y<H;y++)for(let x=0;x<W;x++){const e=document.createElement("div");e.className="cell"+(obstacles.has(x+","+y)?" obstacle":"");e.style.left=x*S+"px";e.style.top=y*S+"px";map.appendChild(e)}
function marker(c,t,x,y){const e=document.createElement("div");e.className="marker "+c;e.textContent=t;e.style.left=x*S+"px";e.style.top=y*S+"px";map.appendChild(e);return e}
marker("base","B",2,2);marker("victim","P",20,12);const robot=marker("robot","R",2,2);
const pathLayer=document.createElement("div");pathLayer.className="path-layer";map.appendChild(pathLayer);
async function post(path,body={}){const r=await fetch(API+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});if(!r.ok)throw Error("request failed");return r.json()}
function setText(id,v){const e=document.querySelector("#"+id);if(e)e.textContent=v}
function offline(){connection.textContent="OFFLINE";connection.className="badge offline";modeLabel.textContent="OFFLINE"}
async function command(c){try{await post("/api/command",{command:c})}catch(e){offline()}}
async function start(){try{await post("/api/mission/start",{name:missionName.value.trim()||"SEARCH ALPHA"})}catch(e){offline()}}
async function stop(){try{await post("/api/mission/stop")}catch(e){offline()}}
async function reset(){try{await post("/api/mission/reset")}catch(e){offline()}}
async function mode(m){try{await post("/api/mode",{mode:m})}catch(e){offline()}}
function render(d){
 connection.textContent="ONLINE";connection.className="badge online";modeLabel.textContent=d.mode;
 robot.style.left=d.robot.x*S+"px";robot.style.top=d.robot.y*S+"px";
 robot.classList.toggle("moving",d.path.length>0);robot.classList.toggle("found",d.found);
 pathLayer.innerHTML="";(d.path||[]).forEach(p=>{const e=document.createElement("div");e.className="path-dot";e.style.left=p[0]*S+10+"px";e.style.top=p[1]*S+10+"px";pathLayer.appendChild(e)});
 setText("battery",d.telemetry.battery+"%");setText("signal",d.telemetry.signal+"%");setText("speed",d.telemetry.speed);
 setText("heading",d.telemetry.heading+"°");setText("pitch",d.telemetry.pitch+"°");setText("roll",d.telemetry.roll+"°");
 setText("gps",d.telemetry.gps.lat+", "+d.telemetry.gps.lon);setText("state",d.state);setText("slope",d.terrain.slope_deg+"°");
 setText("terrain",d.terrain.type);setText("fusion",d.perception.person_confirmed?"PERSON CONFIRMED":"SCANNING");
 if(moveset)moveset.innerHTML=["FL","FR","RL","RR"].map(function(leg){const g=d.gait[leg];return '<div class="leg-card '+g.phase.toLowerCase()+'"><b>'+leg+'</b><span>'+g.phase+'</span><i></i></div>'}).join("");
 sensor.textContent=[
 "ROBOT STATE","  "+d.state,"  E-STOP       "+(d.emergency_stop?"ACTIVE":"CLEAR"),"",
 "DECISION","  "+d.decision,"  TASK         "+d.task.current+" ("+d.task.index+"/"+d.task.total+")","",
 "PERCEPTION FUSION","  RGB          "+(d.perception.rgb.person_detected?"DETECTED":"NO"),
 "  THERMAL      "+(d.perception.thermal.hotspot_detected?"DETECTED":"NO"),"  CONFIDENCE   "+d.perception.confidence,
 "  DECISION     "+(d.perception.person_confirmed?"PERSON CONFIRMED":"SEARCHING"),"",
 "ENVIRONMENT","  TEMP         "+d.sensors.temperature.toFixed(1)+" C","  HUMIDITY     "+d.sensors.humidity.toFixed(1)+" %",
 "  PRESSURE     "+d.sensors.pressure.toFixed(1)+" hPa","  RAIN RISK    "+Math.round(d.sensors.rain_risk*100)+" %",
 "  ASSESSMENT   "+d.sensors.environment,"","TERRAIN","  TYPE         "+d.terrain.type,"  SLOPE        "+d.terrain.slope_deg+" deg",
 "  PATH         "+d.path.length+" cells","","STABILIZATION","  PITCH CORR   "+d.stabilization.pitch_correction+"°",
 "  ROLL CORR    "+d.stabilization.roll_correction+"°","  ACTIVE       "+(d.stabilization.active?"YES":"NO"),"",
 "MISSION","  ACTIVE       "+(d.mission.active?"YES":"NO"),"  PERSON       "+(d.found?"FOUND":"SEARCHING")
 ].join("\n");
 events.textContent=d.mission.events.map(function(e){return e.timestamp+"  "+e.event}).join("\n");
}
async function refresh(){try{const r=await fetch(API+"/api/status",{cache:"no-store"});if(!r.ok)throw Error();render(await r.json())}catch(e){offline()}setTimeout(refresh,500)}
document.querySelector("#startMission").onclick=start;document.querySelector("#stopMission").onclick=stop;
document.querySelector("#returnHome").onclick=function(){command("RETURN_HOME")};document.querySelector("#resumeRobot").onclick=function(){command("RESUME")};
document.querySelector("#resetMission").onclick=reset;document.querySelectorAll("[data-mode]").forEach(function(b){b.onclick=function(){mode(b.dataset.mode)}});refresh();
