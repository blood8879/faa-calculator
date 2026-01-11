#!/usr/bin/env python3
"""
Python API Server for FAA Calculator
Runs all Python API endpoints on port 8000
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Import handlers
from validate_ticker import handler as ValidateTickerHandler
from score import handler as ScoreHandler
from backtest import handler as BacktestHandler

class APIRouter(BaseHTTPRequestHandler):
    """Routes requests to appropriate API handlers"""

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/validate_ticker':
            self._delegate_to_handler(ValidateTickerHandler)
        elif self.path == '/api/score':
            self._delegate_to_handler(ScoreHandler)
        elif self.path == '/api/backtest':
            self._delegate_to_handler(BacktestHandler)
        else:
            self.send_error(404, f"Endpoint not found: {self.path}")

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _delegate_to_handler(self, handler_class):
        """Delegate request to specific handler"""
        try:
            print(f"Delegating to {handler_class.__name__}")
            # Create temporary handler instance
            handler = object.__new__(handler_class)
            # Copy all attributes from current handler
            handler.request = self.request
            handler.client_address = self.client_address
            handler.server = self.server
            handler.rfile = self.rfile
            handler.wfile = self.wfile
            handler.headers = self.headers
            handler.command = self.command
            handler.path = self.path
            handler.request_version = self.request_version
            handler.requestline = self.requestline
            # Handle the request
            handler.do_POST()
            print(f"Handler {handler_class.__name__} completed")
        except Exception as e:
            print(f"Error delegating to handler: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Internal server error: {str(e)}")

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"{self.address_string()} - {format % args}")

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('localhost', port), APIRouter)

    print('='*60)
    print('🚀 FAA Calculator Python API Server')
    print('='*60)
    print(f'📍 Server running on http://localhost:{port}')
    print('')
    print('Available endpoints:')
    print(f'  POST http://localhost:{port}/api/validate_ticker')
    print(f'  POST http://localhost:{port}/api/score')
    print(f'  POST http://localhost:{port}/api/backtest')
    print('')
    print('Press Ctrl+C to stop')
    print('='*60)
    print('')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\n👋 Server stopped')
        sys.exit(0)
