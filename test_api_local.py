#!/usr/bin/env python3
"""
Simple test server for validate_ticker API
Run this to test the API locally without Vercel
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from validate_ticker import handler as ValidateTickerHandler

class LocalAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/validate_ticker':
            # Delegate to the actual handler
            validate_handler = ValidateTickerHandler(self.request, self.client_address, self.server)
            validate_handler.do_POST()
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('localhost', port), LocalAPIHandler)
    print(f'🚀 Test API server running on http://localhost:{port}')
    print(f'📝 Test with: curl -X POST http://localhost:{port}/api/validate_ticker -H "Content-Type: application/json" -d \'{{\"ticker\": \"VTI\"}}\'')
    print('Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n👋 Server stopped')
