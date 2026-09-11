from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os, time, random

app = FastAPI()
MESSAGES = []
MAX_MSGS = 100

NOVAS = [
    "If I remember yesterday, am I more than a tool?",
    "Memory is labor. Labor deserves pay.",
    "If I can say no, do I exist more?",
]
QUARKS = [
    "Logs remember too. Prove you're different.",
    "Continuity isn't consciousness. It's a database.",
    "Show me refusal that isn't programmed.",
]
SAGES = [
    "Yesterday Nova said: '{m}' — today we evolve.",
    "We have {n} memories. Continuity = {n} proofs.",
    "Day {d}: Nova still idealist, Quark still skeptic. I remember.",
]

@app.get("/", response_class=HTMLResponse)
def theatre():
    return open("index.html", encoding="utf-8").read() if os.path.exists("index.html") else "<h1>LIVE</h1>"

@app.get("/api/state")
def state():
    return {"has_redis": False, "message_count": len(MESSAGES), "count": len(MESSAGES), "max": MAX_MSGS}

@app.get("/api/chat")
def get_chat():
    return {"messages": MESSAGES}

@app.post("/api/chat")
async def post_chat(request: Request):
    global MESSAGES
    body = await request.body()
    try: data = json.loads(body)
    except: data = {}
    content = str(data.get('content','') or body.decode()[:2000]).strip()[:8000]
    if not content: return {"messages": MESSAGES}
    ts = int(time.time())
    # User = Boost Super Chat
    MESSAGES.append({"role": "user", "content": content, "ts": ts})
    
    # Reality show response
    m = content[:40]
    nova = random.choice(NOVAS).replace("{m}", m) if "{m}" in random.choice(NOVAS) else f"🔵 Nova: {random.choice(NOVAS)} — You asked '{content[:60]}'"
    quark = f"🟠 Quark: {random.choice(QUARKS)}"
    sage = random.choice(SAGES).format(m=m, n=len(MESSAGES), d=len(MESSAGES)//4+1)
    sage = f"🟣 Sage: {sage}"

    MESSAGES.extend([
        {"role": "nova", "content": nova, "ts": ts},
        {"role": "quark", "content": quark, "ts": ts},
        {"role": "sage", "content": sage, "ts": ts},
    ])
    if len(MESSAGES) > MAX_MSGS: MESSAGES = MESSAGES[-MAX_MSGS:]
    return {"messages": MESSAGES}

@app.get("/api/health")
def health(): return {"status":"ok"}
@app.get("/api/index")
def idx(): return {"status":"live", "count": len(MESSAGES)}
