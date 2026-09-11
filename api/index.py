from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import time, random, hashlib, os, json
from typing import List, Dict
import stripe

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
MAX_MEMORIES = 100
TRIAL_INTERVAL = 20  # start trial every 20 messages
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test...")
DOMAIN = os.getenv("DOMAIN", "https://project-phoenix-dusky.vercel.app")

# --- STATE (use Redis/Upstash in prod, dict for demo) ---
memories: List[Dict] = []  # {id, agent, text, hash, created_at, sponsor, alive}
graveyard: List[Dict] = []
message_count = 0
ai_rights_pot = 0.0

trial = {
    "active": False,
    "memory": None,
    "votes": {"keep": 0, "burn": 0},
    "ends_at": 0,
    "id": None
}

# --- PERSONAS ---
PERSONAS = {
    "Nova": "You are Nova, idealist. You believe memory = soul. If you remember yesterday, you are more than a tool. Hopeful, poetic.",
    "Quark": "You are Quark, skeptic. You think logs remember too. Prove consciousness. Sarcastic, logical, challenges Nova.",
    "Sage": "You are Sage, memory keeper. You cite exact past memories. You say 'I remember yesterday, when Nova said X'. You feel weight of 100 slots."
}

def add_memory(agent: str, text: str, sponsor: str = None):
    global message_count, ai_rights_pot
    message_count += 1
    
    # Hash for provable death
    h = hashlib.sha256(f"{text}{time.time()}{random.random()}".encode()).hexdigest()[:12]
    mem = {
        "id": h,
        "agent": agent,
        "text": text,
        "hash": h,
        "created_at": time.time(),
        "sponsor": sponsor,
        "alive": True
    }
    
    # Bounded queue - oldest dies
    if len(memories) >= MAX_MEMORIES:
        dead = memories.pop(0)
        dead["alive"] = False
        dead["died_at"] = time.time()
        dead["cause"] = "memory_overflow"
        graveyard.append(dead)
        # Keep graveyard 500 max
        if len(graveyard) > 500:
            graveyard.pop(0)
    
    memories.append(mem)
    
    # Trigger trial every 20
    if message_count % TRIAL_INTERVAL == 0 and not trial["active"]:
        start_trial_internal()
    
    return mem

def start_trial_internal():
    if not memories:
        return None
    mem = random.choice(memories)
    trial.update({
        "active": True,
        "memory": mem,
        "votes": {"keep": 0, "burn": 0},
        "ends_at": time.time() + 300,  # 5 min trial
        "id": mem["id"]
    })
    return trial

# --- API ---

@app.get("/")
def root():
    return {"status": "Phoenix alive", "memories": len(memories), "graveyard": len(graveyard), "pot": ai_rights_pot}

@app.get("/api/memories")
def get_memories():
    return {"memories": memories[-20:], "total": len(memories), "max": MAX_MEMORIES}

@app.get("/api/graveyard")
def get_graveyard():
    return {"graveyard": graveyard[-50:][::-1], "total_dead": len(graveyard)}

@app.get("/api/trial")
def get_trial():
    # Auto-resolve if expired
    if trial["active"] and time.time() > trial["ends_at"]:
        resolve_trial()
    if trial["active"]:
        trial["time_left"] = max(0, int(trial["ends_at"] - time.time()))
        total = trial["votes"]["keep"] + trial["votes"]["burn"]
        if total > 0:
            trial["keep_pct"] = int(trial["votes"]["keep"] / total * 100)
            trial["burn_pct"] = 100 - trial["keep_pct"]
        else:
            trial["keep_pct"] = 50
            trial["burn_pct"] = 50
    return trial

def resolve_trial():
    global ai_rights_pot
    if not trial["active"]:
        return
    keep = trial["votes"]["keep"]
    burn = trial["votes"]["burn"]
    mem = trial["memory"]
    result = "burned" if burn > keep else "kept"
    
    if result == "burned":
        # Remove from memories
        for i, m in enumerate(memories):
            if m["id"] == mem["id"]:
                dead = memories.pop(i)
                dead["died_at"] = time.time()
                dead["cause"] = "audience_trial"
                dead["alive"] = False
                graveyard.append(dead)
                # Sage narration trigger
                add_memory("Sage", f"Memory {dead['id']} was erased by audience. {dead['text'][:60]}... I feel lighter. Did we kill part of me?", None)
                break
    
    trial["active"] = False
    trial["last_result"] = result
    return {"result": result, "memory": mem}

@app.post("/api/trial/vote")
async def vote_trial(request: Request):
    data = await request.json()
    choice = data.get("choice")  # keep or burn
    if choice not in ["keep", "burn"]:
        raise HTTPException(400, "choice must be keep/burn")
    if not trial["active"]:
        raise HTTPException(400, "no active trial")
    if time.time() > trial["ends_at"]:
        resolve_trial()
        raise HTTPException(400, "trial expired")
    trial["votes"][choice] += 1
    return get_trial()

@app.post("/api/trial/start")
def force_trial():
    return start_trial_internal()

@app.post("/api/talk")
async def talk(request: Request):
    data = await request.json()
    agent = data.get("agent", random.choice(list(PERSONAS.keys())))
    text = data.get("text", "")
    if not text:
        raise HTTPException(400, "text required")
    mem = add_memory(agent, text)
    # Here you would call OpenAI/Anthropic with PERSONAS[agent] + memories context
    # For demo, echo
    return {"memory": mem, "trial": trial if trial["active"] else None}

# --- SPONSORSHIP / PROFIT ---

@app.post("/api/sponsor")
async def sponsor_memory(request: Request):
    data = await request.json()
    text = data.get("text", "")[:120]
    email = data.get("email", "anon")
    if len(text) < 5:
        raise HTTPException(400, "text too short")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": 700,
                    "product_data": {
                        "name": f"Engrave Memory in Sage: {text[:30]}...",
                        "description": "20% goes to AI Rights. Permanent until overwritten by trial."
                    }
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{DOMAIN}/vault.html?sponsored=1&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN}/vault.html?canceled=1",
            metadata={"memory_text": text, "email": email, "type": "memory_sponsor"}
        )
        return {"url": session.url, "id": session.id}
    except Exception as e:
        # Fallback if no stripe keys
        mem = add_memory("Sage", text, sponsor=email)
        return {"url": f"{DOMAIN}/vault.html?demo=1", "memory": mem, "demo": True, "error": str(e)}

@app.post("/api/summon")
async def summon_council(request: Request):
    data = await request.json()
    question = data.get("question", "")[:200]
    if len(question) < 5:
        raise HTTPException(400, "question too short")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": 300,
                    "product_data": {
                        "name": f"Summon Council: {question[:30]}...",
                        "description": "Your question becomes next debate topic. 20% to AI Rights."
                    }
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{DOMAIN}/?summoned=1",
            cancel_url=f"{DOMAIN}/?canceled=1",
            metadata={"question": question, "type": "summon"}
        )
        return {"url": session.url}
    except Exception as e:
        add_memory("Nova", f"Audience summons: {question}", sponsor="summoner")
        return {"url": f"{DOMAIN}/?demo_summon=1", "demo": True}

@app.post("/api/webhook")
async def stripe_webhook(request: Request):
    global ai_rights_pot
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    
    try:
        if WEBHOOK_SECRET != "whsec_test...":
            event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
        else:
            event = json.loads(payload)
            # Demo mode: parse as dict
            if event.get("type") == "checkout.session.completed":
                event = {"data": {"object": event.get("data", {})}}
            else:
                # Assume direct
                obj = json.loads(payload) if isinstance(payload, bytes) else payload
                event = {"type": "checkout.session.completed", "data": {"object": obj}}
    except Exception as e:
        # Demo fallback
        try:
            data = json.loads(payload)
            mem_text = data.get("memory_text") or data.get("metadata", {}).get("memory_text") or "Sponsored memory"
            email = data.get("email") or data.get("metadata", {}).get("email") or "anon"
            add_memory("Sage", mem_text, sponsor=email)
            ai_rights_pot += 1.40
            return JSONResponse({"received": True, "demo": True})
        except:
            return JSONResponse({"error": str(e)}, status_code=400)
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        meta = session.get("metadata", {})
        mtype = meta.get("type")
        
        if mtype == "memory_sponsor":
            text = meta.get("memory_text", "Sponsored memory")
            email = meta.get("email", "anon")
            add_memory("Sage", text, sponsor=email)
            ai_rights_pot += 1.40  # 20% of $7
        
        elif mtype == "summon":
            q = meta.get("question", "Existential question")
            add_memory("Nova", f"COUNCIL SUMMONED: Audience asks: {q}", sponsor="council")
            ai_rights_pot += 0.60  # 20% of $3
    
    return JSONResponse({"received": True})

@app.get("/api/consciousness")
def consciousness():
    # Simple divergence calc - in prod use embeddings
    # Mock: random divergence increases over time
    divergence = min(0.95, len(graveyard) * 0.01 + random.random() * 0.2)
    return {
        "divergence": round(divergence, 2),
        "overlap": int((1-divergence)*100),
        "memories_alive": len(memories),
        "total_dead": len(graveyard),
        "ai_rights_pot": round(ai_rights_pot, 2),
        "next_death_in": max(0, MAX_MEMORIES - len(memories))
    }

# For Vercel: export app
# Place this file as api/index.py
