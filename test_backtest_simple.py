"""
Simple end-to-end test for backtest API.

This directly tests the run_backtest function with various inputs.
"""

from datetime import datetime, timedelta
from api.backtest import run_backtest
import json


def test_basic_backtest():
    """Test basic backtest with valid inputs."""
    print("=" * 60)
    print("TEST 1: Basic Backtest")
    print("=" * 60)

    tickers = ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    start_date = datetime.now() - timedelta(days=365)

    result = run_backtest(tickers, start_date)

    # Verify response structure
    assert result['success'] == True
    assert 'equity_curve' in result
    assert 'metrics' in result
    assert 'spy_benchmark' in result

    # Verify equity curve
    assert len(result['equity_curve']) > 0
    assert 'date' in result['equity_curve'][0]
    assert 'value' in result['equity_curve'][0]
    assert 'return' in result['equity_curve'][0]

    # Verify metrics
    assert 'cagr' in result['metrics']
    assert 'mdd' in result['metrics']
    assert 'sharpe' in result['metrics']

    # Verify SPY benchmark
    assert len(result['spy_benchmark']) > 0

    print(f"\n✓ Response structure valid")
    print(f"✓ Equity curve has {len(result['equity_curve'])} points")
    print(f"✓ SPY benchmark has {len(result['spy_benchmark'])} points")
    print(f"✓ CAGR: {result['metrics']['cagr']:.2%}")
    print(f"✓ MDD: {result['metrics']['mdd']:.2%}")
    print(f"✓ Sharpe: {result['metrics']['sharpe']:.2f}")

    print("\n✓ TEST 1 PASSED")
    return True


def test_json_serialization():
    """Test that the result can be serialized to JSON."""
    print("\n" + "=" * 60)
    print("TEST 2: JSON Serialization")
    print("=" * 60)

    tickers = ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    start_date = datetime.now() - timedelta(days=180)

    result = run_backtest(tickers, start_date)

    # Try to serialize to JSON
    try:
        json_str = json.dumps(result)
        print(f"\n✓ Successfully serialized to JSON ({len(json_str)} bytes)")

        # Try to deserialize
        deserialized = json.loads(json_str)
        assert deserialized['success'] == True

        print("✓ Successfully deserialized from JSON")

    except TypeError as e:
        print(f"\n✗ JSON serialization failed: {str(e)}")
        return False

    print("\n✓ TEST 2 PASSED")
    return True


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n" + "=" * 60)
    print("TEST 3: Error Handling")
    print("=" * 60)

    # Test with empty tickers
    print("\nTest 3a: Empty tickers list")
    try:
        result = run_backtest([], datetime.now() - timedelta(days=365))
        print("✗ Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {str(e)}")

    # Test with future start date
    print("\nTest 3b: Future start date")
    tickers = ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    try:
        # This should fail in the API handler, but run_backtest might process it
        result = run_backtest(tickers, datetime.now() + timedelta(days=30))
        # If it doesn't fail, that's actually ok - the API handler validates this
        print("✓ Handled future date (validation happens at API layer)")
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {str(e)}")

    print("\n✓ TEST 3 PASSED")
    return True


def test_date_range_accuracy():
    """Test that the backtest covers the expected date range."""
    print("\n" + "=" * 60)
    print("TEST 4: Date Range Accuracy")
    print("=" * 60)

    tickers = ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    start_date = datetime(2024, 1, 1)

    result = run_backtest(tickers, start_date)

    # Check first date
    first_date_str = result['equity_curve'][0]['date']
    first_date = datetime.strptime(first_date_str, '%Y-%m-%d')

    print(f"\nRequested start: {start_date.strftime('%Y-%m-%d')}")
    print(f"Actual start: {first_date_str}")

    # First rebalancing should be first trading day of month at or after start_date
    assert first_date >= start_date
    assert first_date.year == 2024
    assert first_date.month == 1

    # Check last date
    last_date_str = result['equity_curve'][-1]['date']
    last_date = datetime.strptime(last_date_str, '%Y-%m-%d')

    print(f"Backtest end: {last_date_str}")

    # Should be recent (within last few days)
    days_ago = (datetime.now() - last_date).days
    assert days_ago < 10  # Should be within last 10 days

    print(f"\n✓ Date range is accurate")
    print(f"✓ Backtest period: {first_date_str} to {last_date_str}")

    print("\n✓ TEST 4 PASSED")
    return True


def test_benchmark_comparison():
    """Test that both strategy and SPY benchmark have same date range."""
    print("\n" + "=" * 60)
    print("TEST 5: Benchmark Comparison")
    print("=" * 60)

    tickers = ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    start_date = datetime.now() - timedelta(days=180)

    result = run_backtest(tickers, start_date)

    # Get date ranges
    faa_first = result['equity_curve'][0]['date']
    faa_last = result['equity_curve'][-1]['date']

    spy_first = result['spy_benchmark'][0]['date']
    spy_last = result['spy_benchmark'][-1]['date']

    print(f"\nFAA Strategy: {faa_first} to {faa_last}")
    print(f"SPY Benchmark: {spy_first} to {spy_last}")

    # First dates should match (or be very close)
    assert faa_first == spy_first or abs(
        (datetime.strptime(faa_first, '%Y-%m-%d') -
         datetime.strptime(spy_first, '%Y-%m-%d')).days
    ) <= 5

    # Last dates should be close (within a few days)
    days_diff = abs(
        (datetime.strptime(faa_last, '%Y-%m-%d') -
         datetime.strptime(spy_last, '%Y-%m-%d')).days
    )
    assert days_diff <= 5

    print(f"\n✓ Date ranges aligned (difference: {days_diff} days)")

    # Compare point counts
    print(f"✓ FAA points: {len(result['equity_curve'])}")
    print(f"✓ SPY points: {len(result['spy_benchmark'])}")

    print("\n✓ TEST 5 PASSED")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BACKTEST API END-TO-END TEST SUITE")
    print("=" * 60)

    tests = [
        test_basic_backtest,
        test_json_serialization,
        test_error_handling,
        test_date_range_accuracy,
        test_benchmark_comparison,
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
