from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os, time

app = FastAPI()

# BOUNDED MEMORY — Free Forever
MESSAGES = []
MAX_MSGS = 100
MAX_CHARS = 8000

@app.get("/", response_class=HTMLResponse)
def theatre():
    for p in ["index.html", "../index.html"]:
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    return "<h1>PHOENIX v3 THEATRE LIVE</h1>"

@app.get("/api")
def api_root():
    return {"status": "api root LIVE - PHOENIX v3", "messages": len(MESSAGES)}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/state")
def state():
    total_chars = sum(len(m.get('content','')) for m in MESSAGES)
    return {"has_redis": False, "count": len(MESSAGES), "message_count": len(MESSAGES), "chars": total_chars, "max": MAX_MSGS}

@app.get("/api/index")
def api_index():
    return {"status": "index LIVE", "count": len(MESSAGES)}

@app.get("/api/chat")
def get_chat():
    return {"messages": MESSAGES[-MAX_MSGS:], "status": "chat LIVE 10/10"}

@app.post("/api/chat")
async def post_chat(request: Request):
    global MESSAGES
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
        content = str(data.get('content','')).strip() or (body.decode()[:2000] if body else "").strip()
    except:
        content = "hello"
    if not content:
        content = "hello"
    
    # Trim input
    content = content[:MAX_CHARS]

    # Add user + 3 AIs (bounded)
    now = int(time.time())
    new_msgs = [
        {"role": "user", "content": content, "ts": now},
        {"role": "oracle", "content": f"🔮 Oracle sees: '{content[:80]}' → timeline analyzed, pattern detected.", "ts": now},
        {"role": "architect", "content": f"🏗️ Architect plans: Break '{content[:50]}' into 3 steps → bounded execution.", "ts": now},
        {"role": "executor", "content": f"⚡ Executor builds: '{content[:60]}' → executed, memory bounded to {MAX_MSGS}.", "ts": now},
    ]
    
    MESSAGES.extend(new_msgs)
    # Anti-crash bound
    if len(MESSAGES) > MAX_MSGS:
        MESSAGES = MESSAGES[-MAX_MSGS:]
    
    return {"messages": MESSAGES[-MAX_MSGS:], "status": "sent"}
