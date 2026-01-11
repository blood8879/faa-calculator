#!/usr/bin/env python3
"""
Test script for validate_ticker API endpoint.

Tests:
1. Valid tickers (VTI, SPY, QQQ) - should return valid: true + name + exchange
2. Invalid ticker (INVALID123) - should return valid: false
3. Response time < 2 seconds
4. Error handling for network issues
"""

import sys
import time
import json
from io import BytesIO
from unittest.mock import Mock, patch
sys.path.insert(0, '/Users/yunjihwan/Documents/project/faa-calculator/api')

from validate_ticker import handler


class MockRequest:
    """Mock HTTP request for testing"""

    def __init__(self, body_data):
        self.body = json.dumps(body_data).encode('utf-8')
        self.headers = {'Content-Length': str(len(self.body))}
        self.response_status = None
        self.response_headers = {}
        self.response_body = BytesIO()

    def send_response(self, status):
        self.response_status = status

    def send_header(self, key, value):
        self.response_headers[key] = value

    def end_headers(self):
        pass

    def read(self, length):
        return self.body

    def get_response(self):
        return {
            'status': self.response_status,
            'headers': self.response_headers,
            'body': json.loads(self.response_body.getvalue().decode('utf-8'))
        }


def test_ticker(ticker_symbol, expected_valid=True):
    """Test a single ticker symbol"""
    print(f"\nTesting ticker: {ticker_symbol}")
    print("-" * 50)

    # Create mock handler
    mock_handler = handler(Mock(), ('127.0.0.1', 8000), Mock())

    # Create request
    request_data = {"ticker": ticker_symbol}

    # Mock the request/response
    mock_handler.rfile = BytesIO(json.dumps(request_data).encode('utf-8'))
    mock_handler.wfile = BytesIO()
    mock_handler.headers = {'Content-Length': str(len(json.dumps(request_data)))}

    # Track response
    mock_handler.response_status = None
    mock_handler.response_headers = {}

    def mock_send_response(status):
        mock_handler.response_status = status

    def mock_send_header(key, value):
        mock_handler.response_headers[key] = value

    def mock_end_headers():
        pass

    mock_handler.send_response = mock_send_response
    mock_handler.send_header = mock_send_header
    mock_handler.end_headers = mock_end_headers

    # Measure response time
    start_time = time.time()
    mock_handler.do_POST()
    elapsed_time = time.time() - start_time

    # Get response
    response_body = mock_handler.wfile.getvalue().decode('utf-8')
    response_data = json.loads(response_body)

    # Print results
    print(f"Response Status: {mock_handler.response_status}")
    print(f"Response Time: {elapsed_time:.3f} seconds")
    print(f"Response Body: {json.dumps(response_data, indent=2)}")

    # Validate response
    assert mock_handler.response_status == 200, f"Expected 200, got {mock_handler.response_status}"
    assert elapsed_time < 2.0, f"Response time {elapsed_time:.3f}s exceeded 2 seconds"

    if expected_valid:
        assert response_data.get('valid') == True, "Expected valid: true"
        assert 'name' in response_data, "Expected 'name' field in response"
        assert 'exchange' in response_data, "Expected 'exchange' field in response"
        print(f"✓ Valid ticker: {response_data['name']} ({response_data['exchange']})")
    else:
        assert response_data.get('valid') == False, "Expected valid: false"
        print(f"✓ Invalid ticker correctly identified")

    print(f"✓ Response time check passed ({elapsed_time:.3f}s < 2s)")

    return True


def test_error_handling():
    """Test error handling for malformed requests"""
    print("\n\nTesting Error Handling")
    print("=" * 50)

    # Test 1: Missing ticker field
    print("\nTest: Missing ticker field")
    mock_handler = handler(Mock(), ('127.0.0.1', 8000), Mock())
    mock_handler.rfile = BytesIO(json.dumps({}).encode('utf-8'))
    mock_handler.wfile = BytesIO()
    mock_handler.headers = {'Content-Length': str(len(json.dumps({})))}
    mock_handler.response_status = None

    def mock_send_response(status):
        mock_handler.response_status = status

    mock_handler.send_response = mock_send_response
    mock_handler.send_header = lambda k, v: None
    mock_handler.end_headers = lambda: None

    mock_handler.do_POST()
    assert mock_handler.response_status == 400, "Expected 400 for missing ticker"
    print("✓ Missing ticker field handled correctly (400)")

    # Test 2: Invalid JSON
    print("\nTest: Invalid JSON")
    mock_handler = handler(Mock(), ('127.0.0.1', 8000), Mock())
    mock_handler.rfile = BytesIO(b"invalid json{{{")
    mock_handler.wfile = BytesIO()
    mock_handler.headers = {'Content-Length': '15'}
    mock_handler.response_status = None
    mock_handler.send_response = mock_send_response
    mock_handler.send_header = lambda k, v: None
    mock_handler.end_headers = lambda: None

    mock_handler.do_POST()
    assert mock_handler.response_status == 400, "Expected 400 for invalid JSON"
    print("✓ Invalid JSON handled correctly (400)")


def main():
    """Run all tests"""
    print("=" * 50)
    print("Ticker Validation API Tests")
    print("=" * 50)

    try:
        # Test valid tickers
        test_ticker("VTI", expected_valid=True)
        test_ticker("SPY", expected_valid=True)
        test_ticker("QQQ", expected_valid=True)

        # Test invalid ticker
        test_ticker("INVALID123", expected_valid=False)

        # Test error handling
        test_error_handling()

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
