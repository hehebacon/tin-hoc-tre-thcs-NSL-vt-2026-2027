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
lock = threading.Lock()
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
                if mode not in core.MODES:
                    self.send_json({"error": "invalid mode", "modes": core.MODES}, 400)
                    return
                core.set_mode(mode)
                mission.add("MODE_CHANGED", {"mode": mode})

            elif path == "/api/mission/start":
                mission.start(data.get("name", "SEARCH & RESCUE"))
                core.set_mode("RESCUE")

            elif path == "/api/mission/stop":
                mission.stop()
                core.set_mode("PATROL")

            elif path == "/api/mission/reset":
                core.reset()
                mission.active = False
                mission.add("MISSION_RESET")

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
            if core.mode in ("RESCUE", "AUTONOMOUS") and sensors.person_visible and core.robot == VICTIM:
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
