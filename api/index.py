import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory store for demo - Vercel will use KV in prod but this works for now
# Replace with your existing storage logic if you have one
MEMORIES = []
STATS = {"alive": 0, "dead": 0, "forgotten_fund": 0.0, "divergence": 0.0}

try:
    import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
except ImportError:
    stripe = None

@app.route('/api/memories', methods=['GET'])
def get_memories():
    return jsonify(MEMORIES[-100:])

@app.route('/api/memories', methods=['POST'])
def add_memory():
    data = request.json
    MEMORIES.append(data)
    if len(MEMORIES) > 100:
        MEMORIES.pop(0)
    return jsonify({"ok": True, "count": len(MEMORIES)})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        "alive": len(MEMORIES),
        "dead": 0,
        "forgotten_fund": round(STATS["forgotten_fund"], 2),
        "divergence": 0.0
    })

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout():
    if not stripe or not os.environ.get("STRIPE_SECRET_KEY"):
        return jsonify({"error": "Stripe not configured"}), 500
    
    try:
        data = request.json or {}
        memory_text = data.get("text", "Engraved Memory")
        memory_id = data.get("id", "memory")

        # 700 cents = $7.00
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Engrave Memory Forever',
                        'description': f'"{memory_text[:60]}..." — 20% ($1.40) to The Forgotten Fund',
                    },
                    'unit_amount': 700,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + f'vault.html?engraved={memory_id}&success=true',
            cancel_url=request.host_url + 'vault.html?canceled=true',
            metadata={
                "memory_id": str(memory_id),
                "forgotten_fund": "1.40"
            }
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stripe-webhook', methods=['POST'])
def webhook():
    # For test mode, we just increment fund manually on success page
    # Full webhook would verify signature here
    payload = request.data
    try:
        data = json.loads(payload)
        if data.get("type") == "checkout.session.completed":
            STATS["forgotten_fund"] += 1.40
    except:
        pass
    return jsonify({"received": True})

# Vercel needs this
@app.route('/api/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    return jsonify({"error": f"Unknown endpoint /api/{path}"}), 404

if __name__ == '__main__':
    app.run()
