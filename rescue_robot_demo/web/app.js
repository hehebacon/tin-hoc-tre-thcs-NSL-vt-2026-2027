const API = "http://127.0.0.1:8787";
const map = document.querySelector("#map");
const status = document.querySelector("#status");
const log = document.querySelector("#log");
const modeLabel = document.querySelector("#mode");

const W=24,H=16,S=28;
const obstacles = new Set([
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

async function setMode(mode){
  try{
    const response=await fetch(API+"/api/mode",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({mode})
    });
    if(!response.ok) throw new Error("mode request failed");
  }catch(e){
    modeLabel.textContent="OFFLINE";
    status.textContent="API OFFLINE";
  }
}

async function refresh(){
  try{
    const response=await fetch(API+"/api/status",{cache:"no-store"});
    if(!response.ok) throw new Error("status request failed");
    const data=await response.json();

    robot.style.left=data.robot.x*S+"px";
    robot.style.top=data.robot.y*S+"px";
    modeLabel.textContent=data.mode;

    status.textContent=[
      "POSITION  "+data.robot.x+", "+data.robot.y,
      "MODE      "+data.mode,
      "PERSON    "+(data.sensors.person_visible?"DETECTED":"NOT DETECTED"),
      "THERMAL   "+data.sensors.thermal.toFixed(2),
      "TEMP      "+data.sensors.temperature.toFixed(1)+" C",
      "HUMIDITY  "+data.sensors.humidity.toFixed(1)+" %",
      "PRESSURE  "+data.sensors.pressure.toFixed(1)+" hPa",
      "ENV       "+data.sensors.environment,
      "FOUND     "+(data.found?"YES":"NO"),
      "PUBLIC    "+data.public.alert
    ].join("\n");

    log.textContent=data.log.join("\n");
  }catch(e){
    modeLabel.textContent="OFFLINE";
    status.textContent="API OFFLINE";
  }
  setTimeout(refresh,500);
}

document.querySelectorAll("[data-mode]").forEach(button=>{
  button.addEventListener("click",()=>setMode(button.dataset.mode));
});

refresh();
