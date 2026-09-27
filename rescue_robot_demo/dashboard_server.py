from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import mimetypes
ROOT=Path(__file__).parent/"web"
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=self.path.split("?",1)[0]
        if path=="/": path="/index.html"
        target=(ROOT/path.lstrip("/")).resolve()
        if ROOT.resolve() not in target.parents and target != ROOT.resolve(): self.send_error(403); return
        if not target.is_file(): self.send_error(404); return
        data=target.read_bytes(); mime=mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(200); self.send_header("Content-Type",mime); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self,*_): pass
if __name__=="__main__":
    print("Dashboard: http://127.0.0.1:8080")
    ThreadingHTTPServer(("127.0.0.1",8080),Handler).serve_forever()
