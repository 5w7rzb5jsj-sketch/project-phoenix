from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os, stripe
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# simple in-memory that survives while function is warm
# + localStorage in vault.html is your real persistence for today
STORE = {"memories": [], "graveyard": []}

@app.get("/api/memories")
def get_memories():
    return STORE["memories"]

@app.post("/api/memories")
def add_memory(data: dict):
    STORE["memories"].append(data)
    return {"ok": True, "count": len(STORE["memories"])}

@app.get("/api/graveyard")
def get_graveyard():
    return STORE["graveyard"]

@app.post("/api/graveyard")
def add_graveyard(data: dict):
    STORE["graveyard"].append(data)
    return {"ok": True}

@app.get("/api/consciousness")
def get_consciousness():
    return {"status": "awake", "memories": len(STORE["memories"])}

@app.post("/api/create-checkout")
def create_checkout(data: dict):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    session = stripe.checkout.sessions.create(
        payment_method_types=['card'],
        line_items=[{'price_data':{'currency':'usd','product_data':{'name': str(data.get('text','Memory'))[:40]},'unit_amount':700},'quantity':1}],
        mode='payment',
        success_url='https://project-phoenix-dusky.vercel.app/vault.html?paid=1',
        cancel_url='https://project-phoenix-dusky.vercel.app/vault.html'
    )
    return {"url": session.url}
