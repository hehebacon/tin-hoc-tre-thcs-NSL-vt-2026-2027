const API = "http://127.0.0.1:8787";

const map = document.querySelector("#map");
const connection = document.querySelector("#connection");
const modeLabel = document.querySelector("#mode");
const sensor = document.querySelector("#sensor");
const events = document.querySelector("#events");
const missionName = document.querySelector("#missionName");

const W=24,H=16,S=28;
const obstacles=new Set([
  "7,1","7,2","7,3","7,4","7,5",
  "12,5","13,5","14,5","15,5",
  "17,9","17,10","17,11","17,12",
  "4,10","5,10","6,10","7,10","8,10"
]);

for(let y=0;y<H;y++) for(let x=0;x<W;x++){
  const cell=document.createElement("div");
  cell.className="cell"+(obstacles.has(x+","+y)?" obstacle":"");
  cell.style.left=x*S+"px";
  cell.style.top=y*S+"px";
  map.appendChild(cell);
}

function marker(className,text,x,y){
  const el=document.createElement("div");
  el.className="marker "+className;
  el.textContent=text;
  el.style.left=x*S+"px";
  el.style.top=y*S+"px";
  map.appendChild(el);
  return el;
}

marker("base","B",2,2);
marker("victim","P",20,12);
const robot=marker("robot","R",2,2);

async function post(path,body={}){
  const response=await fetch(API+path,{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(body)
  });
  if(!response.ok) throw new Error("request failed");
  return response.json();
}

function setText(id,value){
  const el=document.querySelector("#"+id);
  if(el) el.textContent=value;
}

async function startMission(){
  try{
    await post("/api/mission/start",{name:missionName.value.trim()||"SEARCH ALPHA"});
  }catch(e){ setOffline(); }
}

async function stopMission(){
  try{ await post("/api/mission/stop"); }
  catch(e){ setOffline(); }
}

async function resetMission(){
  try{ await post("/api/mission/reset"); }
  catch(e){ setOffline(); }
}

async function setMode(mode){
  try{ await post("/api/mode",{mode}); }
  catch(e){ setOffline(); }
}

function setOffline(){
  connection.textContent="OFFLINE";
  connection.className="badge offline";
  modeLabel.textContent="OFFLINE";
}

function render(data){
  connection.textContent="ONLINE";
  connection.className="badge online";
  modeLabel.textContent=data.mode;

  robot.style.left=data.robot.x*S+"px";
  robot.style.top=data.robot.y*S+"px";

  setText("battery",data.telemetry.battery+"%");
  setText("signal",data.telemetry.signal+"%");
  setText("speed",data.telemetry.speed);
  setText("heading",data.telemetry.heading+"°");
  setText("pitch",data.telemetry.pitch+"°");
  setText("roll",data.telemetry.roll+"°");
  setText("gps",data.telemetry.gps.lat+", "+data.telemetry.gps.lon);
  setText("state",data.state);

  sensor.textContent=[
    "RGB CAMERA",
    "  PERSON       "+(data.camera.person_detected?"DETECTED":"NOT DETECTED"),
    "  CONFIDENCE   "+data.camera.confidence,
    "  DISTANCE     "+data.camera.distance+" m",
    "",
    "THERMAL",
    "  HOTSPOT      "+(data.thermal.hotspot_detected?"DETECTED":"NONE"),
    "  INTENSITY    "+data.thermal.intensity,
    "",
    "ENVIRONMENT",
    "  TEMP         "+data.sensors.temperature.toFixed(1)+" C",
    "  HUMIDITY     "+data.sensors.humidity.toFixed(1)+" %",
    "  PRESSURE     "+data.sensors.pressure.toFixed(1)+" hPa",
    "  ASSESSMENT   "+data.sensors.environment,
    "",
    "MISSION",
    "  ACTIVE       "+(data.mission.active?"YES":"NO"),
    "  NAME         "+data.mission.name,
    "  PERSON       "+(data.found?"FOUND":"SEARCHING")
  ].join("\n");

  events.textContent=data.mission.events.map(
    e=>e.timestamp+"  "+e.event
  ).join("\n");
}

async function refresh(){
  try{
    const response=await fetch(API+"/api/status",{cache:"no-store"});
    if(!response.ok) throw new Error("status failed");
    render(await response.json());
  }catch(e){
    setOffline();
  }
  setTimeout(refresh,500);
}

document.querySelector("#startMission").addEventListener("click",startMission);
document.querySelector("#stopMission").addEventListener("click",stopMission);
document.querySelector("#resetMission").addEventListener("click",resetMission);

document.querySelectorAll("[data-mode]").forEach(button=>{
  button.addEventListener("click",()=>setMode(button.dataset.mode));
});

refresh();
