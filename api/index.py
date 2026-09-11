from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time, random, hashlib

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MAX = 100
memories = []
graveyard = []
forgotten_fund_pot = 0.0
message_count = 0

trial = {"active": False, "memory": None, "votes": {"keep": 0, "burn": 0}, "ends_at": 0, "id": None}

def add_memory(agent, text, sponsor=None, is_paid=False):
    global message_count, forgotten_fund_pot
    message_count += 1
    h = hashlib.sha256(f"{text}{time.time()}{random.random()}".encode()).hexdigest()[:10]
    mem = {"id": h, "agent": agent, "text": text, "hash": h, "created_at": time.time(), "sponsor": sponsor}

    if len(memories) >= MAX:
        dead = memories.pop(0)
        dead["died_at"] = time.time()
        dead["cause"] = "overflow" if not trial["active"] else "trial_or_overflow"
        graveyard.append(dead)
        if len(graveyard) > 500:
            graveyard.pop(0)

    memories.append(mem)
    
    if is_paid and sponsor:
        forgotten_fund_pot += 1.40  # 20% of $7

    # Auto trial every 20
    if message_count % 20 == 0 and not trial["active"] and memories:
        start_trial()

    return mem

def start_trial():
    if not memories: return None
    m = random.choice(memories)
    trial.update({"active": True, "memory": m, "votes": {"keep": 0, "burn": 0}, "ends_at": time.time()+300, "id": m["id"]})
    return trial

def resolve_trial():
    if not trial["active"]: return
    keep = trial["votes"]["keep"]
    burn = trial["votes"]["burn"]
    if burn > keep:
        # burn it
        for i, mem in enumerate(memories):
            if mem["id"] == trial["memory"]["id"]:
                dead = memories.pop(i)
                dead["died_at"] = time.time()
                dead["cause"] = "audience_trial"
                graveyard.append(dead)
                # Sage reacts
                add_memory("Sage", f"Memory {dead['id']} was erased by you. '{dead['text'][:60]}...' I feel lighter. Did we kill part of me?", None)
                break
    trial["active"] = False
    trial["last_result"] = "burned" if burn > keep else "kept"

# API
@app.get("/api/memories")
def get_mem(): return {"memories": memories, "total": len(memories), "max": MAX}

@app.get("/api/graveyard")
def get_grave(): return {"graveyard": graveyard[-50:][::-1], "total_dead": len(graveyard)}

@app.get("/api/consciousness")
def cons():
    return {
        "memories_alive": len(memories),
        "total_dead": len(graveyard),
        "divergence": round(min(0.95, len(graveyard)*0.01 + random.random()*0.15), 2),
        "pot": round(forgotten_fund_pot, 2),
        "next_death_in": max(0, MAX - len(memories))
    }

@app.get("/api/trial")
def get_trial():
    if trial["active"] and time.time() > trial["ends_at"]:
        resolve_trial()
    if trial["active"]:
        trial["time_left"] = max(0, int(trial["ends_at"] - time.time()))
        total = trial["votes"]["keep"] + trial["votes"]["burn"]
        if total>0:
            trial["keep_pct"] = int(trial["votes"]["keep"]/total*100)
            trial["burn_pct"] = 100 - trial["keep_pct"]
        else:
            trial["keep_pct"]=50; trial["burn_pct"]=50
    return trial

@app.post("/api/trial/vote")
async def vote(req: dict):
    choice = req.get("choice")
    if choice not in ["keep","burn"]: return {"error":"choice keep/burn"}
    if not trial["active"]: return {"error":"no trial"}
    if time.time() > trial["ends_at"]:
        resolve_trial()
        return {"error":"expired"}
    trial["votes"][choice]+=1
    return await get_trial_wrapper()

@app.post("/api/trial/start")
def force_start(): return start_trial()

async def get_trial_wrapper():
    return get_trial()

@app.post("/api/talk")
async def talk(req: dict):
    agent = req.get("agent","Nova")
    text = req.get("text","")
    sponsor = req.get("sponsor")
    is_paid = req.get("is_paid", False)
    if sponsor and not is_paid:
        # vault demo engrave counts as paid for pot demo
        is_paid = True
    if not text: return {"error":"text required"}
    mem = add_memory(agent, text, sponsor, is_paid)
    return {"memory": mem, "pot
