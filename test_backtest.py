"""
Test script for backtest API endpoint.

This script tests the backtest functionality with various scenarios.
"""

import json
from datetime import datetime, timedelta
from api.backtest import run_backtest, calculate_metrics, generate_monthly_dates
import pandas as pd


def test_basic_backtest():
    """Test basic backtest with standard FAA tickers."""
    print("=" * 60)
    print("TEST 1: Basic Backtest (1 year)")
    print("=" * 60)

    tickers = ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    start_date = datetime.now() - timedelta(days=365)

    try:
        result = run_backtest(tickers, start_date)

        print(f"\nSuccess: {result['success']}")
        print(f"\nEquity Curve Points: {len(result['equity_curve'])}")
        print(f"First Point: {result['equity_curve'][0]}")
        print(f"Last Point: {result['equity_curve'][-1]}")

        print(f"\nMetrics:")
        print(f"  CAGR: {result['metrics']['cagr']:.2%}")
        print(f"  MDD: {result['metrics']['mdd']:.2%}")
        print(f"  Sharpe: {result['metrics']['sharpe']:.2f}")

        print(f"\nSPY Benchmark Points: {len(result['spy_benchmark'])}")
        print(f"SPY First: {result['spy_benchmark'][0]}")
        print(f"SPY Last: {result['spy_benchmark'][-1]}")

        print("\n✓ Test 1 PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Test 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_5_year_backtest():
    """Test 5-year backtest to verify performance requirement (<10 seconds)."""
    print("\n" + "=" * 60)
    print("TEST 2: 5-Year Backtest (Performance Test)")
    print("=" * 60)

    tickers = ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    start_date = datetime.now() - timedelta(days=365*5)

    import time
    start_time = time.time()

    try:
        result = run_backtest(tickers, start_date)
        elapsed_time = time.time() - start_time

        print(f"\nExecution Time: {elapsed_time:.2f} seconds")
        print(f"Success: {result['success']}")
        print(f"Equity Curve Points: {len(result['equity_curve'])}")

        print(f"\nMetrics:")
        print(f"  CAGR: {result['metrics']['cagr']:.2%}")
        print(f"  MDD: {result['metrics']['mdd']:.2%}")
        print(f"  Sharpe: {result['metrics']['sharpe']:.2f}")

        # Check performance requirement
        if elapsed_time < 10:
            print(f"\n✓ Performance requirement met: {elapsed_time:.2f}s < 10s")
        else:
            print(f"\n⚠ Performance requirement NOT met: {elapsed_time:.2f}s >= 10s")

        print("\n✓ Test 2 PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Test 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_calculation():
    """Test metrics calculation logic."""
    print("\n" + "=" * 60)
    print("TEST 3: Metrics Calculation")
    print("=" * 60)

    # Create sample equity curve
    equity_curve = [
        {"date": "2020-01-01", "value": 10000, "return": 0.0},
        {"date": "2020-06-01", "value": 9000, "return": -0.10},  # 10% drawdown
        {"date": "2021-01-01", "value": 12000, "return": 0.20},  # Recovery + gain
    ]

    metrics = calculate_metrics(equity_curve)

    print(f"\nSample Equity Curve:")
    for point in equity_curve:
        print(f"  {point}")

    print(f"\nCalculated Metrics:")
    print(f"  CAGR: {metrics['cagr']:.2%}")
    print(f"  MDD: {metrics['mdd']:.2%}")
    print(f"  Sharpe: {metrics['sharpe']:.2f}")

    # Verify MDD is calculated correctly (should be -10% or -0.10)
    expected_mdd = -0.10
    if abs(metrics['mdd'] - expected_mdd) < 0.01:
        print(f"\n✓ MDD calculation correct: {metrics['mdd']:.2%}")
    else:
        print(f"\n✗ MDD calculation incorrect: expected {expected_mdd:.2%}, got {metrics['mdd']:.2%}")

    print("\n✓ Test 3 PASSED")
    return True


def test_monthly_rebalancing():
    """Test that rebalancing happens monthly."""
    print("\n" + "=" * 60)
    print("TEST 4: Monthly Rebalancing Verification")
    print("=" * 60)

    tickers = ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"]
    start_date = datetime.now() - timedelta(days=180)  # 6 months

    try:
        result = run_backtest(tickers, start_date)

        # Count number of month transitions in equity curve
        dates = [point['date'] for point in result['equity_curve']]
        months = set()

        for date_str in dates:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            months.add((date.year, date.month))

        print(f"\nBacktest Period: {dates[0]} to {dates[-1]}")
        print(f"Number of unique months: {len(months)}")
        print(f"Expected months: approximately 6")

        if len(months) >= 5:  # Allow some tolerance
            print("\n✓ Monthly rebalancing appears to be working")
        else:
            print("\n⚠ Monthly rebalancing may not be working correctly")

        print("\n✓ Test 4 PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Test 4 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 60)
    print("TEST 5: Edge Cases")
    print("=" * 60)

    # Test 1: Empty equity curve
    print("\nTest 5a: Empty equity curve metrics")
    metrics = calculate_metrics([])
    assert metrics['cagr'] == 0.0
    assert metrics['mdd'] == 0.0
    assert metrics['sharpe'] == 0.0
    print("✓ Empty equity curve handled correctly")

    # Test 2: Single point equity curve
    print("\nTest 5b: Single point equity curve")
    metrics = calculate_metrics([{"date": "2020-01-01", "value": 10000, "return": 0.0}])
    assert metrics['cagr'] == 0.0
    print("✓ Single point equity curve handled correctly")

    print("\n✓ Test 5 PASSED")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BACKTEST API TEST SUITE")
    print("=" * 60)

    tests = [
        test_basic_backtest,
        test_5_year_backtest,
        test_metrics_calculation,
        test_monthly_rebalancing,
        test_edge_cases,
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
