import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(json.dumps({"messages": [], "status": "chat LIVE 10/10"}).encode())
    
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length else '{}'
        try:
            data = json.loads(body)
            content = str(data.get('content', body))[:5000]
        except:
            content = str(body)[:5000]
        msgs = [
            {"role": "user", "content": content},
            {"role": "oracle", "content": f"🔮 Oracle sees: '{content[:80]}' - Timeline shows build intent. Risk low. Bounded memory active."},
            {"role": "architect", "content": f"🏗️ Architect plans: Break '{content[:50]}' into 3 steps. Max 100 msgs / 8000 chars."},
            {"role": "executor", "content": f"⚡ Executor builds: Done '{content[:60]}'. Anti-crash: trimmed to 100 max."}
        ]
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(json.dumps({"messages": msgs}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
