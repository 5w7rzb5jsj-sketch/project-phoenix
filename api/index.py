import os, json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            if self.path in ['/api', '/api/', '/api/index', '/api/index.py'] or self.path.startswith('/api/index?'):
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.send_header('Access-Control-Allow-Origin','*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "STEP 1 LIVE - api/index.py FIXED"}).encode())
                return
            self.send_response(404)
            self.send_header('Content-type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "use specific file", "path": self.path}).encode())
            return
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html'), 'r', encoding='utf-8') as f:
                html = f.read()
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        except:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(b"<h1>PHOENIX</h1>")

    def do_POST(self): self.do_GET()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
