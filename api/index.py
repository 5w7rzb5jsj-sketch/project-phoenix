import os, json
from http.server import BaseHTTPRequestHandler

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
        # Only handle root theatre and /api/index
        if self.path.startswith('/api/'):
            # Let Vercel route to other api files - return 404 so chat.py can handle /api/chat
            if self.path not in ['/api', '/api/', '/api/index', '/api/index.py'] and not self.path.startswith('/api/index?'):
                self.send_response(404)
                self.send_header('Content-type','application/json')
                self.send_header('Access-Control-Allow-Origin','*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not handled by index, should go to specific API file", "path": self.path}).encode())
                return
            # Handle /api index
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "STEP 1 LIVE - FIXED 10/10",
                "has_redis": has_redis,
                "path": self.path
            }).encode())
            return
        
        # Serve theatre for / and /index.html
        try:
            base = os.path.dirname(os.path.dirname(__file__))
            p1 = os.path.join(base, 'index.html')
            p2 = 'index.html'
            html_path = p1 if os.path.exists(p1) else p2
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(f"<h1>Error {e}</h1>".encode())

    def do_POST(self):
        self.do_GET()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
