"""Load-balancer endpoint entrypoint.

Runs sglang directly on PORT (inbound traffic hits it natively, no queue
handler) plus a sidecar health server on PORT_HEALTH implementing RunPod's
required /ping contract: 200 = healthy, 204 = still initializing.

Start command for LB endpoints: python3 lb.py
"""

import os
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from engine import SGlangEngine


class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] != "/ping":
            self.send_response(404)
            self.end_headers()
            return
        port = os.getenv("PORT", "80")
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/health", timeout=2
            ) as resp:
                healthy = resp.status == 200
        except Exception:
            healthy = False
        self.send_response(200 if healthy else 204)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    health_port = int(os.getenv("PORT_HEALTH", "8001"))
    health_server = ThreadingHTTPServer(("0.0.0.0", health_port), PingHandler)
    threading.Thread(target=health_server.serve_forever, daemon=True).start()
    print(f"Health server listening on :{health_port}/ping")

    engine = SGlangEngine()
    engine.start_server()
    raise SystemExit(engine.process.wait())


if __name__ == "__main__":
    main()
