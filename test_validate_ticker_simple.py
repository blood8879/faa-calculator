#!/usr/bin/env python3
"""
Simple test script for validate_ticker validation logic.

Tests:
1. Valid tickers (VTI, SPY, QQQ) - should return valid: true + name + exchange
2. Invalid ticker (INVALID123) - should return valid: false
3. Response time < 2 seconds
"""

import sys
import time
sys.path.insert(0, '/Users/yunjihwan/Documents/project/faa-calculator/api')

from validate_ticker import handler


def test_validation_function():
    """Test the _validate_ticker function directly"""

    # Create a handler instance just to access the validation method
    class MockHandler:
        pass

    # Copy the validation method
    h = handler.__new__(handler)

    print("=" * 50)
    print("Ticker Validation Logic Tests")
    print("=" * 50)

    # Test 1: Valid ticker VTI
    print("\nTest 1: Valid ticker VTI")
    print("-" * 50)
    start_time = time.time()
    result = h._validate_ticker("VTI")
    elapsed_time = time.time() - start_time

    print(f"Response Time: {elapsed_time:.3f} seconds")
    print(f"Result: {result}")

    assert result.get('valid') == True, "Expected valid: true"
    assert 'name' in result, "Expected 'name' field in response"
    assert 'exchange' in result, "Expected 'exchange' field in response"
    assert elapsed_time < 2.0, f"Response time {elapsed_time:.3f}s exceeded 2 seconds"
    print(f"✓ Valid ticker: {result['name']} ({result['exchange']})")
    print(f"✓ Response time check passed ({elapsed_time:.3f}s < 2s)")

    # Test 2: Valid ticker SPY
    print("\nTest 2: Valid ticker SPY")
    print("-" * 50)
    start_time = time.time()
    result = h._validate_ticker("SPY")
    elapsed_time = time.time() - start_time

    print(f"Response Time: {elapsed_time:.3f} seconds")
    print(f"Result: {result}")

    assert result.get('valid') == True, "Expected valid: true"
    assert 'name' in result, "Expected 'name' field in response"
    assert 'exchange' in result, "Expected 'exchange' field in response"
    assert elapsed_time < 2.0, f"Response time {elapsed_time:.3f}s exceeded 2 seconds"
    print(f"✓ Valid ticker: {result['name']} ({result['exchange']})")
    print(f"✓ Response time check passed ({elapsed_time:.3f}s < 2s)")

    # Test 3: Valid ticker QQQ
    print("\nTest 3: Valid ticker QQQ")
    print("-" * 50)
    start_time = time.time()
    result = h._validate_ticker("QQQ")
    elapsed_time = time.time() - start_time

    print(f"Response Time: {elapsed_time:.3f} seconds")
    print(f"Result: {result}")

    assert result.get('valid') == True, "Expected valid: true"
    assert 'name' in result, "Expected 'name' field in response"
    assert 'exchange' in result, "Expected 'exchange' field in response"
    assert elapsed_time < 2.0, f"Response time {elapsed_time:.3f}s exceeded 2 seconds"
    print(f"✓ Valid ticker: {result['name']} ({result['exchange']})")
    print(f"✓ Response time check passed ({elapsed_time:.3f}s < 2s)")

    # Test 4: Invalid ticker
    print("\nTest 4: Invalid ticker INVALID123")
    print("-" * 50)
    start_time = time.time()
    result = h._validate_ticker("INVALID123")
    elapsed_time = time.time() - start_time

    print(f"Response Time: {elapsed_time:.3f} seconds")
    print(f"Result: {result}")

    assert result.get('valid') == False, "Expected valid: false"
    assert elapsed_time < 2.0, f"Response time {elapsed_time:.3f}s exceeded 2 seconds"
    print(f"✓ Invalid ticker correctly identified")
    print(f"✓ Response time check passed ({elapsed_time:.3f}s < 2s)")

    # Test 5: Empty string
    print("\nTest 5: Empty ticker")
    print("-" * 50)
    result = h._validate_ticker("")
    print(f"Result: {result}")
    assert result.get('valid') == False, "Expected valid: false for empty ticker"
    print(f"✓ Empty ticker correctly identified as invalid")

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
    print("\nAcceptance Criteria Met:")
    print("✓ Valid ticker (VTI, SPY, QQQ) returns valid: true + name + exchange")
    print("✓ Invalid ticker (INVALID123) returns valid: false")
    print("✓ Response time < 2 seconds for all requests")
    print("✓ Proper error handling (returns valid: false on errors)")


if __name__ == "__main__":
    try:
        test_validation_function()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
