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
          "status": "STEP 1 LIVE - api/index.py entrypoint FIXED 10/10",
          "health_url": "/api/health also works",
          "has_redis": bool(os.environ.get('REDIS_URL'))
        }
        self.wfile.write(json.dumps(data).encode())
        return
    
    def do_POST(self):
        self.do_GET()
