from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time

from config import BASE, VICTIM
from core import RescueCore
from sensors import SensorSimulator, PublicDataSimulator


core = RescueCore(24, 16, set(), BASE, VICTIM)
sensors = SensorSimulator(VICTIM)
public = PublicDataSimulator()
lock = threading.Lock()


def snapshot():
    with lock:
        sensors.update(core.robot)
        return {
            "robot": {"x": core.robot[0], "y": core.robot[1]},
            "mode": core.mode,
            "found": core.found,
            "searching": core.searching,
            "sensors": sensors.snapshot(),
            "public": public.snapshot(),
            "log": core.log[:10],
        }


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json(snapshot())
            return
        self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/api/mode":
            self.send_json({"error": "not found"}, 404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
            mode = data.get("mode")
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "invalid json"}, 400)
            return

        with lock:
            if mode not in core.MODES:
                self.send_json({"error": "invalid mode", "modes": core.MODES}, 400)
                return
            core.set_mode(mode)

        self.send_json(snapshot())

    def log_message(self, *_):
        pass


def worker():
    while True:
        with lock:
            sensors.update(core.robot)
            if core.mode in ("RESCUE", "AUTONOMOUS") and sensors.person_visible and core.robot == VICTIM:
                core.report_found()
            core.step()
        time.sleep(0.5)


if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    print("API: http://127.0.0.1:8787")
    ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
