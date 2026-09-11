from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import time, random, hashlib, os
import stripe

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

memories = []
msg_count = 0
pot = 0.0
trial = {"active": False, "memory": None, "votes": {"keep":0,"burn":0}, "ends_at":0, "keep_pct":50, "burn_pct":50}
ROOT = os.path.dirname(os.path.dirname(__file__))

def add_memory(agent, text, sponsor=None):
    global msg_count, pot
    msg_count += 1
    m = {
        "id": hashlib.md5(f"{time.time()}{text}".encode()).hexdigest()[:8],
        "agent": agent,
        "text": text,
        "ts": time.time(),
        "sponsor": sponsor
    }
    memories.append(m)
    if sponsor:
        pot += 1.4
    if msg_count % 20 == 0 and memories and not trial["active"]:
        trial.update({"active": True, "memory": random.choice(memories), "votes": {"keep":0,"burn":0}, "ends_at": time.time()+300, "keep_pct":50, "burn_pct":50})
    return m

@app.get("/")
def serve_index():
    path = os.path.join(ROOT, "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"status":"Phoenix alive"})

@app.get("/vault.html")
def serve_vault():
    path = os.path.join(ROOT, "vault.html")
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"error":"vault.html missing"})

@app.get("/clip.html")
def serve_clip():
    path = os.path.join(ROOT, "clip.html")
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"error":"clip.html missing"})

@app.get("/manifesto.html")
def serve_manif():
    path = os.path.join(ROOT, "manifesto.html")
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"error":"manifesto.html missing"})

@app.get("/api/")
def api_root():
    return {"status": "Phoenix alive"}

@app.get("/api/memories")
def get_memories():
    return memories[-100:]

@app.get("/api/stats")
def get_stats():
    return {"alive": len(memories), "dead": 0, "forgotten_fund": round(pot,2), "divergence": random.randint(0,20), "trial": trial}

@app.post("/api/create-checkout")
def create_checkout(data: dict):
    try:
        if not stripe.api_key:
            return {"error": "STRIPE_SECRET_KEY not set in Vercel"}
        text = data.get("text", "Engraved Memory")[:80]
        mid = data.get("id", "memory")
        session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Engrave Memory Forever",
                        "description": f'"{text}" - 20% ($1.40) to The Forgotten Fund'
                    },
                    "unit_amount": 700,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://project-phoenix-dusky.vercel.app/vault.html?engraved={mid}&paid=1",
            cancel_url="https://project-phoenix-dusky.vercel.app/vault.html?canceled=1",
            metadata={"forgotten_fund": "1.40", "memory_id": str(mid)}
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
