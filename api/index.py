from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def theatre():
    for p in ["index.html", "../index.html"]:
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    return "<h1>PHOENIX v3 THEATRE LIVE</h1><p>theatre loading...</p>"

@app.get("/api")
def api_root():
    return {"status": "api root LIVE - PHOENIX v3"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/state")
def state():
    return {"has_redis": False, "count": 0, "max": 100}

@app.get("/api/chat")
def get_chat():
    return {"messages": [], "status": "chat LIVE"}

@app.post("/api/chat")
async def post_chat(request: Request):
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
        content = data.get('content') or (body.decode()[:2000] if body else "hello")
    except:
        content = "hello"
    return {"messages": [
        {"role":"user","content":content},
        {"role":"oracle","content":f"🔮 Oracle: {content[:80]}"},
        {"role":"architect","content":f"🏗️ Architect: {content[:50]}"},
        {"role":"executor","content":f"⚡ Executor: {content[:60]}"}
    ]}
