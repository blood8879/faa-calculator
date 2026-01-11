#!/usr/bin/env python3
"""
Integration test for validate_ticker API endpoint.
Tests the full HTTP request/response cycle.
"""

import sys
import json
import time
from io import BytesIO
from unittest.mock import MagicMock

sys.path.insert(0, '/Users/yunjihwan/Documents/project/faa-calculator/api')

from validate_ticker import handler


def create_mock_handler():
    """Create a mock handler with necessary components"""
    # Create a mock socket and connection
    mock_request = MagicMock()
    mock_request.makefile = MagicMock()

    # Create handler instance without calling __init__
    h = handler.__new__(handler)

    # Mock the necessary attributes
    h.rfile = BytesIO()
    h.wfile = BytesIO()
    h.headers = {}
    h.response_status = None
    h.response_headers = {}

    # Mock response methods
    def mock_send_response(status):
        h.response_status = status

    def mock_send_header(key, value):
        h.response_headers[key] = value

    def mock_end_headers():
        pass

    h.send_response = mock_send_response
    h.send_header = mock_send_header
    h.end_headers = mock_end_headers

    return h


def test_post_request(ticker, expected_valid=True):
    """Test a POST request to the validate_ticker endpoint"""
    print(f"\nTesting POST /api/validate-ticker with ticker: {ticker}")
    print("-" * 60)

    # Create handler
    h = create_mock_handler()

    # Create request body
    request_data = {"ticker": ticker}
    request_body = json.dumps(request_data).encode('utf-8')

    # Set up request
    h.rfile = BytesIO(request_body)
    h.headers = {'Content-Length': str(len(request_body))}

    # Make request
    start_time = time.time()
    h.do_POST()
    elapsed_time = time.time() - start_time

    # Parse response
    response_body = h.wfile.getvalue().decode('utf-8')
    response_data = json.loads(response_body)

    # Print results
    print(f"Request: POST /api/validate-ticker")
    print(f"Body: {request_data}")
    print(f"Status: {h.response_status}")
    print(f"Response Time: {elapsed_time:.3f}s")
    print(f"Response: {json.dumps(response_data, indent=2)}")

    # Assertions
    assert h.response_status == 200, f"Expected 200, got {h.response_status}"
    assert 'Access-Control-Allow-Origin' in h.response_headers, "Missing CORS header"

    if expected_valid:
        assert response_data['valid'] == True, "Expected valid: true"
        assert 'name' in response_data, "Missing 'name' field"
        assert 'exchange' in response_data, "Missing 'exchange' field"
        print(f"✓ Valid response: {response_data['name']} on {response_data['exchange']}")
    else:
        assert response_data['valid'] == False, "Expected valid: false"
        print(f"✓ Correctly identified as invalid")

    assert elapsed_time < 2.0, f"Response time {elapsed_time:.3f}s exceeded 2 seconds"
    print(f"✓ Response time within limit")


def test_error_cases():
    """Test error handling"""
    print("\n\nTesting Error Cases")
    print("=" * 60)

    # Test 1: Missing ticker field
    print("\nTest: Missing ticker field")
    print("-" * 60)
    h = create_mock_handler()
    request_body = json.dumps({}).encode('utf-8')
    h.rfile = BytesIO(request_body)
    h.headers = {'Content-Length': str(len(request_body))}
    h.do_POST()

    assert h.response_status == 400, "Expected 400 for missing ticker"
    print(f"✓ Returns 400 Bad Request")

    # Test 2: Invalid JSON
    print("\nTest: Invalid JSON")
    print("-" * 60)
    h = create_mock_handler()
    request_body = b"not valid json{{{"
    h.rfile = BytesIO(request_body)
    h.headers = {'Content-Length': str(len(request_body))}
    h.do_POST()

    assert h.response_status == 400, "Expected 400 for invalid JSON"
    print(f"✓ Returns 400 Bad Request")

    # Test 3: Empty body
    print("\nTest: Empty request body")
    print("-" * 60)
    h = create_mock_handler()
    h.rfile = BytesIO(b"")
    h.headers = {'Content-Length': '0'}
    h.do_POST()

    assert h.response_status == 400, "Expected 400 for empty body"
    print(f"✓ Returns 400 Bad Request")


def test_cors():
    """Test CORS headers"""
    print("\n\nTesting CORS Support")
    print("=" * 60)

    print("\nTest: OPTIONS request (CORS preflight)")
    print("-" * 60)
    h = create_mock_handler()
    h.do_OPTIONS()

    assert h.response_status == 200, "Expected 200 for OPTIONS"
    assert 'Access-Control-Allow-Origin' in h.response_headers, "Missing CORS header"
    assert 'Access-Control-Allow-Methods' in h.response_headers, "Missing CORS methods header"
    print(f"✓ CORS headers present")
    print(f"  Allow-Origin: {h.response_headers.get('Access-Control-Allow-Origin')}")
    print(f"  Allow-Methods: {h.response_headers.get('Access-Control-Allow-Methods')}")


def main():
    """Run all integration tests"""
    print("=" * 60)
    print("Ticker Validation API - Integration Tests")
    print("=" * 60)

    try:
        # Test valid tickers
        test_post_request("VTI", expected_valid=True)
        test_post_request("SPY", expected_valid=True)
        test_post_request("QQQ", expected_valid=True)

        # Test invalid ticker
        test_post_request("INVALID123", expected_valid=False)

        # Test error handling
        test_error_cases()

        # Test CORS
        test_cors()

        print("\n" + "=" * 60)
        print("ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)

        print("\n\nAPI Contract Verification:")
        print("-" * 60)
        print("Endpoint: POST /api/validate-ticker")
        print("\nValid Request:")
        print('  {"ticker": "VTI"}')
        print("Valid Response:")
        print('  {"valid": true, "name": "...", "exchange": "..."}')
        print("\nInvalid Request:")
        print('  {"ticker": "INVALID123"}')
        print("Invalid Response:")
        print('  {"valid": false}')
        print("\n✓ All acceptance criteria met")
        print("✓ Response time < 2 seconds")
        print("✓ Proper error handling")
        print("✓ CORS support enabled")

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
