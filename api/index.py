from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/memories")
def get_memories():
    return []

@app.get("/api/graveyard")
def get_graveyard():
    return []

@app.get("/api/consciousness")
def get_consciousness():
    return {"status": "awake"}

@app.post("/api/create-checkout")
def create_checkout(data: dict):
    import os, stripe
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    session = stripe.checkout.sessions.create(
        payment_method_types=['card'],
        line_items=[{'price_data':{'currency':'usd','product_data':{'name': str(data.get('text','Memory'))[:40]},'unit_amount':700},'quantity':1}],
        mode='payment',
        success_url='https://project-phoenix-dusky.vercel.app/vault.html?paid=1',
        cancel_url='https://project-phoenix-dusky.vercel.app/vault.html'
    )
    return {"url": session.url}
