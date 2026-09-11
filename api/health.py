   from http.server import BaseHTTPRequestHandler
   import json, os
   class handler(BaseHTTPRequestHandler):
       def do_GET(self):
           self.send_response(200)
           self.send_header('Content-type','application/json')
           self.end_headers()
           self.wfile.write(json.dumps({
             "status": "STEP 1 LIVE - foundation 10/10",
             "has_redis": bool(os.environ.get('REDIS_URL')),
             "next": "Add REDIS_URL in Vercel, then we add chat"
           }).encode())
