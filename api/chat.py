import os, json
from http.server import BaseHTTPRequestHandler

# Redis setup with fallback
r = None
has_redis = False
try:
    import redis
    url = os.environ.get('REDIS_URL')
    if url:
        r = redis.from_url(url, decode_responses=True)
        r.ping()
        has_redis = True
except:
    r = None

MEMORY = []  # fallback if no redis
MAX_MSGS = 100
MAX_CHARS = 8000

def get_msgs():
    if has_redis and r:
        try:
            data = r.get('phoenix_messages')
            if data:
                return json.loads(data)
        except:
            pass
    return MEMORY

def save_msgs(msgs):
    # Bounded: trim to 100 msgs, 8000 chars per msg
    trimmed = []
    for m in msgs[-MAX_MSGS:]:
        c = m.get('content','')[:MAX_CHARS]
        trimmed.append({'role': m.get('role','user'), 'content': c})
    if has_redis and r:
        try:
            r.set('phoenix_messages', json.dumps(trimmed))
        except:
            pass
    global MEMORY
    MEMORY = trimmed
    return trimmed

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        msgs = get_msgs()
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(json.dumps({"messages": msgs, "has_redis": has_redis, "count": len(msgs)}).encode())

    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(length).decode() if length else '{}'
        try:
            data = json.loads(body)
            content = data.get('content','')[:MAX_CHARS]
        except:
            content = body[:MAX_CHARS]

        msgs = get_msgs()
        msgs.append({"role": "user", "content": content})

        # THEATRE ORCHESTRATION — 3 AIs talk
        # Step 4: Mock orchestration (Step 5 will add real LLM if you add GROQ key)
        oracle = f"🔮 Oracle sees: '{content[:60]}' — Timeline shows intent to build. Risk: low. Opportunity: high. Recommends breaking into 3 steps."
        architect = f"🏗️ Architect plans: Step1: Validate '{content[:40]}' with bounded memory. Step2: Store in Redis ({len(msgs)} msgs). Step3: Execute with anti-crash (100/{MAX_CHARS})."
        executor = f"⚡ Executor builds: Executed '{content[:50]}' — Saved to {'Redis 10/10' if has_redis else 'memory'} — Bounded memory active — {len(msgs)+3}/{MAX_MSGS} msgs used — Free forever, never crashes."

        msgs.append({"role": "oracle", "content": oracle})
        msgs.append({"role": "architect", "content": architect})
        msgs.append({"role": "executor", "content": executor})

        final = save_msgs(msgs)

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(json.dumps({"messages": final, "has_redis": has_redis}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
