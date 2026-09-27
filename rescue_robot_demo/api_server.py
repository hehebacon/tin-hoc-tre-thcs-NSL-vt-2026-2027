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

core = RescueCore(MAP_W, MAP_H, OBSTACLES, BASE, VICTIM)
sensors = SensorSimulator(VICTIM)
camera = CameraSimulator(VICTIM)
thermal = ThermalSimulator(VICTIM)
telemetry = TelemetrySimulator(BASE)
state_machine = StateMachine()
mission = MissionManager()
lock = threading.RLock()
previous_robot = core.robot


def snapshot():
    with lock:
        state = state_machine.update(
            core.mode, core.found, core.searching, core.robot == BASE
        )
        return {
            "robot": {"x": core.robot[0], "y": core.robot[1]},
            "mode": core.mode,
            "state": state,
            "emergency_stop": core.emergency_stop,
            "found": core.found,
            "searching": core.searching,
            "mission": {
                "active": mission.active,
                "name": mission.name,
                "events": mission.export()[:10],
            },
            "sensors": sensors.snapshot(),
            "camera": camera.observe(core.robot),
            "thermal": thermal.observe(core.robot),
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
            if path == "/api/mode":
                mode = data.get("mode")
                if not core.set_mode(mode):
                    self.send_json({"error": "invalid mode", "modes": core.MODES}, 400)
                    return
                mission.add("MODE_CHANGED", {"mode": mode})

            elif path == "/api/mission/start":
                mission.start(data.get("name", "SEARCH & RESCUE"))
                core.set_mode("RESCUE")

            elif path == "/api/mission/stop":
                mission.stop()
                core.stop()

            elif path == "/api/mission/reset":
                core.reset()
                mission.active = False
                mission.add("MISSION_RESET")

            elif path == "/api/command":
                command = str(data.get("command", "")).upper()
                if command == "STOP":
                    core.stop()
                    mission.add("EMERGENCY_STOP")
                elif command == "RESUME":
                    core.resume()
                    mission.add("MOTION_RESUMED")
                elif command == "RETURN_HOME":
                    core.return_home()
                    mission.add("RETURN_HOME")
                else:
                    self.send_json({
                        "error": "invalid command",
                        "commands": ["STOP", "RESUME", "RETURN_HOME"]
                    }, 400)
                    return

            else:
                self.send_json({"error": "not found"}, 404)
                return

        self.send_json(snapshot())

    def log_message(self, *_):
        pass


def worker():
    global previous_robot
    while True:
        with lock:
            sensors.update(core.robot)

            detected_now = (
                core.mode in ("RESCUE", "AUTONOMOUS")
                and sensors.person_visible
                and core.robot == VICTIM
                and not core.found
            )
            if detected_now:
                core.report_found()
                mission.add("PERSON_DETECTED", {"position": list(VICTIM)})

            core.step()
            telemetry.update(core.robot, previous_robot)
            previous_robot = core.robot

            if core.found and core.robot == BASE and mission.active:
                mission.add("MISSION_COMPLETE")
                mission.active = False

        time.sleep(0.5)


if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    print("API: http://127.0.0.1:8787")
    ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
