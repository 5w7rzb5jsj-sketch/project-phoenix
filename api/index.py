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
    global msg_count, pot, trial
    msg_count += 1
    h = hashlib.sha256(f"{text}{time.time()}".encode()).hexdigest()[:8]
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
        trial = {"active": True, "memory": random.choice(memories), "votes": {"keep":0,"burn":0}, "ends_at": time.time()+300}
    return m

@app.get("/")
def root():
    return {"status": "Phoenix alive"}

@app.get("/api/memories")
def get_mem():
    return {"memories": memories, "total": len(memories), "max": 100}

@app.get("/api/graveyard")
def get_grave():
    return {"graveyard": graveyard, "total_dead": len(graveyard)}

@app.get("/api/consciousness")
def cons():
    return {"memories_alive": len(memories), "total_dead": len(graveyard), "pot": pot, "divergence": round(random.random()*0.2,2)}

@app.get("/api/trial")
def get_trial():
    if trial["active"] and time.time() > trial["ends_at"]:
        trial["active"] = False
    if trial["active"]:
        trial["time_left"] = max(0, int(trial["ends_at"] - time.time()))
    return trial

@app.post("/api/trial/start")
def start_trial():
    if memories:
        trial.update({"active": True, "memory": random.choice(memories), "votes": {"keep":0,"burn":0}, "ends_at": time.time()+300})
    return trial

@app.post("/api/trial/vote")
async def vote(req: dict):
    c = req.get("choice")
    if trial["active"] and c in ["keep","burn"]:
        trial["votes"][c] += 1
    return trial

@app.post("/api/talk")
async def talk(req: dict):
    text = req.get("text","")
    agent = req.get("agent","Nova")
    sponsor = req.get("sponsor")
    if not text:
        return {"error": "no text"}
    m = add_memory(agent, text, sponsor)
    return {"memory": m}
