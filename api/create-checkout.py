from http.server import BaseHTTPRequestHandler
import json, os, stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))).decode())
        session = stripe.checkout.sessions.create(
            payment_method_types=['card'],
            line_items=[{'price_data':{'currency':'usd','product_data':{'name':data.get('text','Memory')},'unit_amount':700},'quantity':1}],
            mode='payment',
            success_url=f"https://project-phoenix-dusky.vercel.app/vault.html?paid=1&text={data.get('text','')}",
            cancel_url="https://project-phoenix-dusky.vercel.app/vault.html"
        )
        self.wfile.write(json.dumps({"url":session.url}).encode())
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
