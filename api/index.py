from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def theatre():
    for p in ["index.html", "../index.html"]:
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    return "<h1>PHOENIX v3 THEATRE LIVE</h1>"

@app.get("/api")
def api_root():
    return {"status": "api root LIVE - PHOENIX v3"}

@app.get("/api/health")
def health():
    return {"status": "ok", "theatre": "LIVE"}

@app.get("/api/state")
def state():
    return {"has_redis": False, "count": 0, "max": 100}

@app.get("/api/chat")
def get_chat():
    return {"messages": [], "status": "chat LIVE 10/10"}

@app.post("/api/chat")
async def post_chat(request: Request):
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
        content = data.get('content') or (body.decode()[:2000] if body else "hello")
    except:
        content = "hello"
    if not content:
        content = "hello"
    return {"messages": [
        {"role": "user", "content": content},
        {"role": "oracle", "content": f"🔮 Oracle sees: '{content[:80]}'"},
        {"role": "architect", "content": f"🏗️ Architect: plan for '{content[:50]}'"},
        {"role": "executor", "content": f"⚡ Executor builds: '{content[:60]}'"}
    ]}
