from http.server import BaseHTTPRequestHandler
import json
from typing import Dict, Any
from datetime import datetime

# Import FAA calculator functions
try:
    from .faa_calculator import calculate_faa_scores, get_allocation
except ImportError:
    from faa_calculator import calculate_faa_scores, get_allocation


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
            tickers = data.get('tickers', [])
            if not tickers:
                self._send_error(400, "Missing 'tickers' field in request")
                return

            if not isinstance(tickers, list):
                self._send_error(400, "'tickers' must be an array")
                return

            if len(tickers) != 7:
                self._send_error(400, "Exactly 7 tickers are required")
                return

            # Clean and validate tickers
            tickers = [str(t).strip().upper() for t in tickers]
            if any(not t for t in tickers):
                self._send_error(400, "All tickers must be non-empty strings")
                return

            # Calculate FAA scores
            faa_scores = calculate_faa_scores(tickers)

            # Get investment amount if provided
            investment_amount = data.get('amount')
            allocation = None

            if investment_amount is not None:
                try:
                    investment_amount = float(investment_amount)
                    if investment_amount > 0:
                        allocation = get_allocation(faa_scores, investment_amount)
                except (ValueError, TypeError):
                    # If amount is invalid, just don't include allocation
                    pass

            # Prepare response
            result = {
                "success": True,
                "scores": faa_scores,
                "allocation": allocation,
                "timestamp": datetime.now().isoformat()
            }

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON in request body")
        except ValueError as e:
            # FAA calculation errors
            self._send_error(422, str(e))
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_error(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {"success": False, "error": message}
        self.wfile.write(json.dumps(error_response).encode())
