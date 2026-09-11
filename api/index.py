import os, json
from http.server import BaseHTTPRequestHandler

# Try redis
has_redis = False
try:
    import redis
    r_url = os.environ.get('REDIS_URL') or os.environ.get('UPSTASH_REDIS_REST_URL')
    if r_url:
        has_redis = True
except:
    pass

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # If asking for /api/* -> return JSON status
                # ONLY handle /api and /api/index — let /api/chat, /api/state, /api/health go to their own files
        if self.path in ['/api', '/api/', '/api/index', '/api/index.py'] or self.path.startswith('/api/index?'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            data = {
                "status": "STEP 1 LIVE - api/index.py entrypoint FIXED 10/10",
                "health_url": "/api/health also works",
                "has_redis": has_redis,
                "path": self.path
            }
            self.wfile.write(json.dumps(data).encode())
            return
        
        # For ROOT / or /index.html -> serve theatre HTML
        try:
            # Find index.html at project root
            html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
            if not os.path.exists(html_path):
                html_path = 'index.html'
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(f"<h1>Phoenix Theatre Loading... {e}</h1>".encode())

    def do_POST(self):
        self.do_GET()
