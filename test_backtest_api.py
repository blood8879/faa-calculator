"""
Integration test for the backtest API endpoint.

This script simulates HTTP requests to test the API handler.
"""

import json
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import Mock
from api.backtest import handler


def create_mock_request(data):
    """Create a mock HTTP request with the given data."""
    request = Mock()
    request.headers = {
        'Content-Length': str(len(json.dumps(data).encode()))
    }

    body_bytes = json.dumps(data).encode('utf-8')
    request.rfile = BytesIO(body_bytes)

    return request


def create_mock_response():
    """Create a mock HTTP response object."""
    response = Mock()
    response._response_code = None
    response._headers = {}
    response._body = BytesIO()

    def send_response(code):
        response._response_code = code

    def send_header(key, value):
        response._headers[key] = value

    def end_headers():
        pass

    def write(data):
        response._body.write(data)

    response.send_response = send_response
    response.send_header = send_header
    response.end_headers = end_headers
    response.wfile = response._body

    return response


def test_valid_backtest_request():
    """Test a valid backtest request."""
    print("=" * 60)
    print("TEST: Valid Backtest Request")
    print("=" * 60)

    # Create request data
    request_data = {
        "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
        "start_date": "2024-01-01"
    }

    # Create handler instance
    h = handler(create_mock_request(request_data), ('127.0.0.1', 8000), None)
    response = create_mock_response()

    # Monkey patch the handler with our mock response
    h.send_response = response.send_response
    h.send_header = response.send_header
    h.end_headers = response.end_headers
    h.wfile = response.wfile

    # Call the POST handler
    h.do_POST()

    # Check response
    response_body = response._body.getvalue().decode('utf-8')
    response_json = json.loads(response_body)

    print(f"\nResponse Code: {response._response_code}")
    print(f"Success: {response_json.get('success')}")

    if response_json.get('success'):
        print(f"Equity Curve Points: {len(response_json.get('equity_curve', []))}")
        print(f"SPY Benchmark Points: {len(response_json.get('spy_benchmark', []))}")

        metrics = response_json.get('metrics', {})
        print(f"\nMetrics:")
        print(f"  CAGR: {metrics.get('cagr')}")
        print(f"  MDD: {metrics.get('mdd')}")
        print(f"  Sharpe: {metrics.get('sharpe')}")

        # Verify structure
        assert 'equity_curve' in response_json
        assert 'metrics' in response_json
        assert 'spy_benchmark' in response_json
        assert len(response_json['equity_curve']) > 0
        assert len(response_json['spy_benchmark']) > 0

        print("\n✓ Test PASSED")
        return True
    else:
        print(f"\n✗ Test FAILED: {response_json.get('error')}")
        return False


def test_missing_tickers():
    """Test request with missing tickers field."""
    print("\n" + "=" * 60)
    print("TEST: Missing Tickers Field")
    print("=" * 60)

    request_data = {
        "start_date": "2024-01-01"
    }

    h = handler(create_mock_request(request_data), ('127.0.0.1', 8000), None)
    response = create_mock_response()

    h.send_response = response.send_response
    h.send_header = response.send_header
    h.end_headers = response.end_headers
    h.wfile = response.wfile

    h.do_POST()

    response_body = response._body.getvalue().decode('utf-8')
    response_json = json.loads(response_body)

    print(f"\nResponse Code: {response._response_code}")
    print(f"Success: {response_json.get('success')}")
    print(f"Error: {response_json.get('error')}")

    assert response._response_code == 400
    assert response_json['success'] == False
    assert 'tickers' in response_json['error'].lower()

    print("\n✓ Test PASSED")
    return True


def test_missing_start_date():
    """Test request with missing start_date field."""
    print("\n" + "=" * 60)
    print("TEST: Missing Start Date Field")
    print("=" * 60)

    request_data = {
        "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    }

    h = handler(create_mock_request(request_data), ('127.0.0.1', 8000), None)
    response = create_mock_response()

    h.send_response = response.send_response
    h.send_header = response.send_header
    h.end_headers = response.end_headers
    h.wfile = response.wfile

    h.do_POST()

    response_body = response._body.getvalue().decode('utf-8')
    response_json = json.loads(response_body)

    print(f"\nResponse Code: {response._response_code}")
    print(f"Success: {response_json.get('success')}")
    print(f"Error: {response_json.get('error')}")

    assert response._response_code == 400
    assert response_json['success'] == False
    assert 'start_date' in response_json['error'].lower()

    print("\n✓ Test PASSED")
    return True


def test_invalid_date_format():
    """Test request with invalid date format."""
    print("\n" + "=" * 60)
    print("TEST: Invalid Date Format")
    print("=" * 60)

    request_data = {
        "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
        "start_date": "01/01/2024"  # Wrong format
    }

    h = handler(create_mock_request(request_data), ('127.0.0.1', 8000), None)
    response = create_mock_response()

    h.send_response = response.send_response
    h.send_header = response.send_header
    h.end_headers = response.end_headers
    h.wfile = response.wfile

    h.do_POST()

    response_body = response._body.getvalue().decode('utf-8')
    response_json = json.loads(response_body)

    print(f"\nResponse Code: {response._response_code}")
    print(f"Success: {response_json.get('success')}")
    print(f"Error: {response_json.get('error')}")

    assert response._response_code == 400
    assert response_json['success'] == False

    print("\n✓ Test PASSED")
    return True


def test_cors_headers():
    """Test that CORS headers are set correctly."""
    print("\n" + "=" * 60)
    print("TEST: CORS Headers")
    print("=" * 60)

    request_data = {
        "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
        "start_date": "2024-01-01"
    }

    h = handler(create_mock_request(request_data), ('127.0.0.1', 8000), None)
    response = create_mock_response()

    h.send_response = response.send_response
    h.send_header = response.send_header
    h.end_headers = response.end_headers
    h.wfile = response.wfile

    h.do_POST()

    print(f"\nCORS Header: {response._headers.get('Access-Control-Allow-Origin')}")

    assert 'Access-Control-Allow-Origin' in response._headers
    assert response._headers['Access-Control-Allow-Origin'] == '*'

    print("\n✓ Test PASSED")
    return True


def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("BACKTEST API INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        test_valid_backtest_request,
        test_missing_tickers,
        test_missing_start_date,
        test_invalid_date_format,
        test_cors_headers,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")

    if all(results):
        print("\n✓ ALL TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED")

    return all(results)


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
