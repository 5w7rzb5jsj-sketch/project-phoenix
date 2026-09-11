   from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        data = {
          "status": "STEP 1 LIVE - foundation 10/10 FIXED",
          "has_redis": bool(os.environ.get('REDIS_URL')),
          "message": "If you see this, Step 1 is 10/10"
        }
        self.wfile.write(json.dumps(data).encode())
        return
