from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time, random, hashlib

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

memories = []
graveyard = []
pot = 0.0
msg_count = 0
trial = {"active": False, "memory": None, "votes": {"keep":0,"burn":0}, "ends_at":0}

def add_memory(agent, text, sponsor=None):
    global msg_count, pot
    msg_count += 1
    h = hashlib.sha256(f"{text}{time.time()}{random.random()}".encode()).hexdigest()[:8]
    m = {"id": h, "agent": agent, "text": text, "hash": h, "created_at": time.time(), "sponsor": sponsor}
    if len(memories) >= 100:
        dead = memories.pop(0)
        dead["died_at"] = time.time()
        dead["cause"] = "overflow"
        graveyard.append(dead)
    memories.append(m)
    if sponsor:
        pot += 1.4
    if msg_count % 20 == 0 and memories and not trial["active"]:
        trial.update({"active": True, "memory": random.choice(memories), "votes": {"keep":0,"burn":0}, "ends_at": time.time()+300})
    return m

@app.get("/api/")
def api_root():
    return {"status": "Phoenix alive"}

@app.get("/api/memories")
def get_mem():
    return {"memories": memories, "total": len(memories), "max": 100}

@app.get("/api/graveyard")
def get_grave():
    return {"graveyard": graveyard[-100:][::-1], "total_dead": len(graveyard)}

@app.get("/api/consciousness")
def cons():
    div = round(min(0.95, len(graveyard)*0.02 + random.random()*0.15), 2)
    return {"memories_alive": len(memories), "total_dead": len(graveyard), "pot": round(pot,2), "ai_rights_pot": round(pot,2), "divergence": div}

@app.get("/api/trial")
def get_trial():
    if trial["active"] and time.time() > trial["ends_at"]:
        trial["active"] = False
        trial["last_result"] = "kept" if trial["votes"]["keep"] >= trial["votes"]["burn"] else "burned"
    if trial["active"]:
        trial["time_left"] = max(0, int(trial["ends_at"] - time.time()))
        total = trial["votes"]["keep"] + trial["votes"]["burn"]
        if total>0:
            trial["keep_pct"]=int(trial["votes"]["keep"]/total*100)
            trial["burn_pct"]=100-trial["keep_pct"]
        else:
            trial["keep_pct"]=50; trial["burn_pct"]=50
    return trial

@app.post("/api/trial/start")
def start_trial():
    if memories:
        trial.update({"active": True, "memory": random.choice(memories), "votes": {"keep":0,"burn":0}, "ends_at": time.time()+300, "keep_pct":50, "burn_pct":50})
    return trial

@app.post("/api/trial/vote")
async def vote(req: dict):
    c = req.get("choice")
    if trial["active"] and c in ["keep","burn"]:
        trial["votes"][c] += 1
        total = trial["votes"]["keep"] + trial["votes"]["burn"]
        trial["keep_pct"]=int(trial["votes"]["keep"]/total*100) if total else 50
        trial["burn_pct"]=100-trial["keep_pct"]
    return trial

@app.post("/api/talk")
async def talk(req: dict):
    text = req.get("text","").strip()
    agent = req.get("agent","Nova")
    sponsor = req.get("sponsor")
    if not text:
        return {"error":"no text"}
    m = add_memory(agent, text, sponsor)
    return {"memory": m, "pot": pot}
