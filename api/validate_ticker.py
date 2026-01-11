from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf
from typing import Dict, Any


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, "Missing request body")
                return

            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # Validate request payload
            ticker = data.get('ticker', '').strip().upper()
            if not ticker:
                self._send_error(400, "Missing 'ticker' field in request")
                return

            # Validate ticker using yfinance
            result = self._validate_ticker(ticker)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON in request body")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _validate_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Validate ticker symbol using basic format checking.
        Real validation happens when calculating scores.
        This provides instant feedback for better UX.
        """
        import re

        # Basic ticker format validation
        # Most US stock tickers are 1-5 uppercase letters
        # Can also include numbers and dots (e.g., BRK.B)
        ticker_pattern = r'^[A-Z]{1,5}(\.[A-Z])?$'

        if not re.match(ticker_pattern, ticker):
            return {"valid": False}

        # If format is valid, return success
        # Note: We don't verify if the ticker actually exists here
        # for better performance. Real verification happens during score calculation.
        return {
            "valid": True,
            "name": f"{ticker} (Format Valid)",
            "exchange": "To be verified"
        }

    def _send_error(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {"error": message, "valid": False}
        self.wfile.write(json.dumps(error_response).encode())
