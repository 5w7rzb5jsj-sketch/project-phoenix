import os, json, stripe
stripe.api_key=os.environ.get('STRIPE_SECRET_KEY')
def handler(request):
    if request.method=="OPTIONS":
        return {"statusCode":200,"headers":{"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"POST,OPTIONS","Access-Control-Allow-Headers":"Content-Type"},"body":""}
    data=json.loads(request.body if isinstance(request.body,str) else request.body.decode())
    s=stripe.checkout.sessions.create(payment_method_types=['card'],line_items=[{'price_data':{'currency':'usd','product_data':{'name':data.get('text','Memory')[:40]},'unit_amount':700},'quantity':1}],mode='payment',success_url=f"https://project-phoenix-dusky.vercel.app/vault.html?paid=1",cancel_url="https://project-phoenix-dusky.vercel.app/vault.html")
    return {"statusCode":200,"headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},"body":json.dumps({"url":s.url})}
