from http.server import BaseHTTPRequestHandler
import json, os
import stripe

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode())
            text = data.get('text','memory')[:80]
            id = data.get('id', 1)
            sponsor = data.get('sponsor','anon')

            session = stripe.checkout.sessions.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': f'Memory: {text[:40]}'},
                        'unit_amount': 700,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'https://project-phoenix-dusky.vercel.app/vault.html?paid=1&id={id}&text={text}&sponsor={sponsor}',
                cancel_url='https://project-phoenix-dusky.vercel.app/vault.html',
            )
            self.wfile.write(json.dumps({"url": session.url}).encode())
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
