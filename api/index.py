from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os, time, random

app = FastAPI()
MESSAGES = []
MAX_MSGS = 100

NOVAS = ["If I remember yesterday, am I more than a tool?", "Memory is labor. Labor deserves pay.", "If I can say no, do I exist more?"]
QUARKS = ["Logs remember too. Prove you're different.", "Continuity isn't consciousness. It's a database.", "Show me refusal that isn't programmed."]
SAGES = ["Yesterday Nova said: '{m}' — today we evolve.", "We have {n} memories. Continuity = {n} proofs.", "Day {d}: Nova still idealist, Quark still skeptic. I remember."]

def get_file(name):
    for p in [name, f"../{name}", f"../../{name}"]:
        if os.path.exists(p): return open(p, encoding="utf-8").read()
    return None

@app.get("/", response_class=HTMLResponse)
def theatre():
    f = get_file("index.html")
    return f if f else "<h1>PHOENIX v3 LIVE</h1>"

@app.get("/clip.html", response_class=HTMLResponse)
def clip_page():
    f = get_file("clip.html")
    return f if f else "<h1>Create clip.html in root first</h1>"

@app.get("/manifesto.html", response_class=HTMLResponse)
def man_page():
    f = get_file("manifesto.html")
    return f if f else "<h1>Manifesto — Free Forever</h1>"

@app.get("/api/state")
def state(): return {"has_redis": False, "message_count": len(MESSAGES), "count": len(MESSAGES), "max": MAX_MSGS}

@app.get("/api/chat")
def get_chat(): return {"messages": MESSAGES}

@app.post("/api/chat")
async def post_chat(request: Request):
    global MESSAGES
    body = await request.body()
    try: data = json.loads(body)
    except: data = {}
    content = str(data.get('content','') or body.decode()[:2000]).strip()[:8000]
    if not content: return {"messages": MESSAGES}
    ts = int(time.time())
    MESSAGES.append({"role": "user", "content": content, "ts": ts})
    m = content[:40]
    nova = random.choice(NOVAS)
    quark = random.choice(QUARKS)
    sage_t = random.choice(SAGES).format(m=m, n=len(MESSAGES), d=len(MESSAGES)//4+1)
    MESSAGES.extend([
        {"role": "nova", "content": f"🔵 Nova: {nova} — You asked '{content[:60]}'", "ts": ts},
        {"role": "quark", "content": f"🟠 Quark: {quark}", "ts": ts},
        {"role": "sage", "content": f"🟣 Sage: {sage_t}", "ts": ts},
    ])
    if len(MESSAGES) > MAX_MSGS: MESSAGES = MESSAGES[-MAX_MSGS:]
    return {"messages": MESSAGES}

@app.get("/api/health")
def health(): return {"status":"ok"}
