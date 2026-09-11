from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api")
@app.get("/api/index")
def api_root():
    return {"status": "api root LIVE"}

@app.get("/api/health")
def health():
    return {"status": "ok", "theatre": "LIVE"}

@app.get("/api/state")
def state():
    return {"has_redis": False, "count": 0, "max": 100}

@app.api_route("/api/chat", methods=["GET", "POST", "OPTIONS"])
async def chat(request: Request):
    if request.method == "GET":
        return {"messages": [], "status": "chat LIVE 10/10"}
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
        content = str(data.get('content',''))[:5000] or body.decode()[:5000] if body else "hello"
    except:
        content = "hello"
    return {"messages": [
        {"role":"user","content":content},
        {"role":"oracle","content":f"🔮 Oracle sees: '{content[:80]}'"},
        {"role":"architect","content":f"🏗️ Architect: plan for '{content[:50]}'"},
        {"role":"executor","content":f"⚡ Executor builds: '{content[:60]}'"}
    ]}
