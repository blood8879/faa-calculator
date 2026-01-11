#!/usr/bin/env python3
"""Simple test server to debug API issues"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print(f"Received POST request to {self.path}")

        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        print(f"Request body: {body}")

        # Send response
        response = {"status": "ok", "message": "Test successful"}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
        print("Response sent")

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), SimpleHandler)
    print('Test server running on http://localhost:8000')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped')
