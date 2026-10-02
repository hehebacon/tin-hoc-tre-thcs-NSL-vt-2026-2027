from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time

from config import MAP_W, MAP_H, BASE, VICTIM, OBSTACLES
from core import RescueCore
from sensors import SensorSimulator, PublicDataSimulator
from camera import CameraSimulator
from thermal import ThermalSimulator
from telemetry import TelemetrySimulator
from state_machine import StateMachine
from mission import MissionManager
from safety import SafetyManager
from task_engine import TaskEngine
from decision_engine import DecisionEngine
from stabilization import BodyStabilizer

core = RescueCore(MAP_W, MAP_H, OBSTACLES, BASE, VICTIM)
sensors = SensorSimulator(VICTIM)
camera = CameraSimulator(VICTIM)
thermal = ThermalSimulator(VICTIM)
telemetry = TelemetrySimulator(BASE)
state_machine = StateMachine()
mission = MissionManager()
safety = SafetyManager()
public = PublicDataSimulator()
tasks = TaskEngine()
decision = DecisionEngine()
stabilizer = BodyStabilizer()
lock = threading.RLock()
previous_robot = core.robot


def fused_perception():
    rgb = camera.observe(core.robot)
    ir = thermal.observe(core.robot)
    agreement = rgb["person_detected"] and ir["hotspot_detected"]
    score = round((rgb["confidence"] + ir["intensity"]) / 2.0, 2)
    return {
        "person_confirmed": agreement and score >= 0.45,
        "confidence": score,
        "rgb": rgb,
        "thermal": ir,
        "fusion_rule": "RGB + THERMAL",
    }


def snapshot():
    with lock:
        state = state_machine.update(
            core.mode,
            core.found,
            core.searching,
            core.robot == BASE,
        )
        perception = fused_perception()
        motion_allowed = safety.allow_motion(telemetry.battery)[0]
        decision_action = decision.decide(
            core.mode,
            motion_allowed,
            core.found,
            perception["person_confirmed"],
            bool(core.path),
            core.robot == BASE,
        )
        return {
            "robot": {"x": core.robot[0], "y": core.robot[1]},
            "mode": core.mode,
            "state": state,
            "emergency_stop": core.emergency_stop,
            "safety": safety.snapshot(),
            "gait": core.gait.snapshot(moving=bool(core.path), dt=0.0),
            "joint_angles": {
                leg: {
                    "coxa": angle.coxa,
                    "femur": angle.femur,
                    "tibia": angle.tibia,
                    "reachable": angle.reachable,
                    "reason": angle.reason,
                }
                for leg, angle in core.last_joint_angles.items()
            },
            "decision": decision_action,
            "task": tasks.snapshot(),
            "stabilization": stabilizer.snapshot(telemetry.pitch, telemetry.roll),
            "terrain": core.terrain_at(),
            "path": [list(p) for p in core.path[:20]],
            "found": core.found,
            "searching": core.searching,
            "perception": perception,
            "mission": {
                "active": mission.active,
                "name": mission.name,
                "events": mission.export()[:10],
            },
            "sensors": sensors.snapshot(),
            "telemetry": telemetry.snapshot(),
            "public": public.snapshot(),
            "log": core.log[:10],
        }


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def read_json(self):
        length = max(0, min(int(self.headers.get("Content-Length", "0")), 4096))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json(snapshot())
            return
        self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            data = self.read_json()
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "invalid json"}, 400)
            return

        with lock:
            if path == "/api/safety":
                action = str(data.get("action", "")).upper()
                if action == "STOP":
                    safety.stop("operator")
                    core.stop()
                    mission.add("EMERGENCY_STOP")
                elif action == "RESUME":
                    result = safety.resume(telemetry.battery)
                    if not result["ok"]:
                        self.send_json({"error": result["reason"]}, 409)
                        return
                    core.resume()
                    mission.add("MOTION_RESUMED")
                else:
                    self.send_json(
                        {"error": "invalid safety action", "actions": ["STOP", "RESUME"]},
                        400,
                    )
                    return

            elif path == "/api/mode":
                allowed, reason = safety.allow_motion(telemetry.battery)
                if not allowed:
                    self.send_json({"error": reason}, 409)
                    return
                mode = data.get("mode")
                if not core.set_mode(mode):
                    self.send_json(
                        {"error": "invalid mode", "modes": core.MODES},
                        400,
                    )
                    return
                if mode == "OSINT":
                    public.scan()
                mission.add("MODE_CHANGED", {"mode": mode})

            elif path == "/api/mission/start":
                allowed, reason = safety.allow_motion(telemetry.battery)
                if not allowed:
                    self.send_json({"error": reason}, 409)
                    return
                mission.start(data.get("name", "SEARCH & RESCUE"))
                core.set_mode("RESCUE")
                tasks.load_rescue(BASE, VICTIM)
                mission.add(
                    "SEARCH_STARTED",
                    {"pipeline": "PERCEPTION+DECISION+NAV+GAIT"},
                )

            elif path == "/api/mission/stop":
                mission.stop()
                safety.stop("mission_stop")
                core.stop()

            elif path == "/api/mission/reset":
                core.reset()
                safety.resume(telemetry.battery)
                tasks = TaskEngine()
                mission.active = False
                mission.add("MISSION_RESET")

            elif path == "/api/command":
                command = str(data.get("command", "")).upper()
                if command == "STOP":
                    safety.stop("operator")
                    core.stop()
                    mission.add("EMERGENCY_STOP")
                elif command == "RESUME":
                    result = safety.resume(telemetry.battery)
                    if not result["ok"]:
                        self.send_json({"error": result["reason"]}, 409)
                        return
                    core.resume()
                    mission.add("MOTION_RESUMED")
                elif command == "RETURN_HOME":
                    allowed, reason = safety.allow_motion(telemetry.battery)
                    if not allowed or not core.return_home():
                        self.send_json(
                            {"error": reason if not allowed else "return home blocked"},
                            409,
                        )
                        return
                    mission.add("RETURN_HOME")
                else:
                    self.send_json(
                        {
                            "error": "invalid command",
                            "commands": ["STOP", "RESUME", "RETURN_HOME"],
                        },
                        400,
                    )
                    return
            else:
                self.send_json({"error": "not found"}, 404)
                return

        self.send_json(snapshot())

    def log_message(self, *_):
        pass


def worker():
    global previous_robot, tasks

    while True:
        with lock:
            sensors.update(core.robot)
            perception = fused_perception()

            current_task = tasks.current()
            if current_task and current_task.action == "NAVIGATE":
                if core.robot == current_task.target:
                    tasks.complete_current()

            detected_now = (
                core.mode in ("RESCUE", "AUTONOMOUS")
                and perception["person_confirmed"]
                and core.robot == VICTIM
                and not core.found
            )

            if detected_now:
                core.report_found()
                mission.add(
                    "PERSON_DETECTED",
                    {
                        "position": list(VICTIM),
                        "confidence": perception["confidence"],
                    },
                )
                mission.add("LOCATION_RECORDED", {"gps": telemetry.gps})

                for action in ("SEARCH", "CONFIRM"):
                    current_task = tasks.current()
                    if current_task and current_task.action == action:
                        tasks.complete_current()

            allowed, reason = safety.allow_motion(telemetry.battery)
            if allowed:
                core.step(0.05)
            elif reason == "LOW_BATTERY":
                core.stop()

            telemetry.update(core.robot, previous_robot)
            previous_robot = core.robot

            current_task = tasks.current()
            if current_task and current_task.action == "RETURN":
                if core.robot == current_task.target:
                    tasks.complete_current()

            if core.found and core.robot == BASE and mission.active:
                mission.add("MISSION_COMPLETE")
                mission.active = False
                while tasks.current():
                    tasks.complete_current()

        time.sleep(0.05)


if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    print("API: http://127.0.0.1:8787")
    ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
