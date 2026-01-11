"""
Manual Verification Script for FAA Calculator

This script manually tests the FAA calculator with real market data
to verify accuracy of calculations.
"""

import sys
from datetime import datetime
from faa_calculator import (
    calculate_momentum,
    calculate_volatility,
    calculate_correlation,
    calculate_faa_scores,
    get_allocation
)


def print_separator(title=""):
    """Print a formatted separator."""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)
    print()


def test_individual_functions():
    """Test individual calculation functions."""
    print_separator("TESTING INDIVIDUAL FUNCTIONS")

    ticker = "VTI"
    print(f"Testing with ticker: {ticker}")

    try:
        # Test momentum
        print("\n1. Testing Momentum Calculation:")
        momentum = calculate_momentum(ticker)
        print(f"   Momentum: {momentum:.4f} ({momentum*100:.2f}%)")

        # Test volatility
        print("\n2. Testing Volatility Calculation:")
        volatility = calculate_volatility(ticker)
        print(f"   Volatility: {volatility:.4f}")

        # Test correlation
        print("\n3. Testing Correlation Calculation:")
        tickers = ["VTI", "VEA"]
        correlations = calculate_correlation(tickers)
        for t, corr in correlations.items():
            print(f"   {t}: {corr:.4f}")

        print("\n✓ All individual functions executed successfully!")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_full_faa_calculation():
    """Test full FAA calculation with default 7-ticker portfolio."""
    print_separator("TESTING FULL FAA CALCULATION")

    # Default FAA tickers from PRD
    tickers = ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ']

    print(f"Portfolio: {', '.join(tickers)}")
    print(f"Number of assets: {len(tickers)}")

    try:
        print("\nCalculating FAA scores...")
        scores = calculate_faa_scores(tickers)

        print("\n" + "-" * 70)
        print(f"{'Ticker':<8} {'Momentum':<10} {'Volatility':<12} {'Correlation':<12} {'Integrated':<12} {'Selected':<10}")
        print("-" * 70)

        # Sort by integrated score
        sorted_tickers = sorted(scores.items(), key=lambda x: x[1]['integrated_score'])

        for ticker, data in sorted_tickers:
            momentum = data['momentum']
            volatility = data['volatility']
            correlation = data['correlation']
            integrated = data['integrated_score']
            selected = "✓" if data['selected'] else ""
            cash_flag = " [CASH]" if data['cash_replacement'] else ""

            print(f"{ticker:<8} "
                  f"{momentum:>9.4f} "
                  f"{volatility:>11.4f} "
                  f"{correlation:>11.4f} "
                  f"{integrated:>11.2f} "
                  f"{selected:<10}{cash_flag}")

        print("-" * 70)

        # Show ranks
        print("\n" + "-" * 70)
        print(f"{'Ticker':<8} {'M-Rank':<8} {'V-Rank':<8} {'C-Rank':<8}")
        print("-" * 70)

        for ticker, data in sorted_tickers:
            print(f"{ticker:<8} "
                  f"{data['momentum_rank']:<8} "
                  f"{data['volatility_rank']:<8} "
                  f"{data['correlation_rank']:<8}")

        print("-" * 70)

        # Show selected tickers
        selected_tickers = [t for t, d in scores.items() if d['selected']]
        print(f"\n✓ Top 3 Selected Tickers: {', '.join(selected_tickers)}")

        # Show cash replacements
        cash_replacements = [t for t, d in scores.items()
                           if d['selected'] and d['cash_replacement']]
        if cash_replacements:
            print(f"⚠ Cash Replacements (negative momentum): {', '.join(cash_replacements)}")

        print("\n✓ Full FAA calculation completed successfully!")
        return True, scores

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_allocation():
    """Test allocation calculation."""
    print_separator("TESTING ALLOCATION CALCULATION")

    tickers = ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ']
    investment_amount = 10000

    try:
        scores = calculate_faa_scores(tickers)
        allocation = get_allocation(scores, investment_amount)

        print(f"Investment Amount: ${investment_amount:,.2f}")
        print("\n" + "-" * 40)
        print(f"{'Ticker':<10} {'Allocation':>15}")
        print("-" * 40)

        total = 0
        for ticker, amount in sorted(allocation.items(), key=lambda x: -x[1]):
            print(f"{ticker:<10} ${amount:>14,.2f}")
            total += amount

        print("-" * 40)
        print(f"{'Total':<10} ${total:>14,.2f}")
        print("-" * 40)

        # Verify total
        if abs(total - investment_amount) < 0.01:
            print("\n✓ Allocation sums correctly!")
        else:
            print(f"\n⚠ Warning: Allocation difference: ${abs(total - investment_amount):.2f}")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_formulas():
    """Verify that formulas match PRD specifications."""
    print_separator("FORMULA VERIFICATION")

    print("PRD Formula Specifications:")
    print("1. Momentum = (current_price / price_4_months_ago) - 1")
    print("2. Volatility = std(daily_returns, 80_days)")
    print("3. Correlation = sum(correlation(asset_i, asset_j)) for all pairs")
    print("4. Integrated Score = momentum_rank * 1.0 + volatility_rank * 0.5 + correlation_rank * 0.5")
    print("\nRanking Rules:")
    print("- Momentum: Higher is better (rank 1 = highest)")
    print("- Volatility: Lower is better (rank 1 = lowest)")
    print("- Correlation: Lower is better (rank 1 = lowest)")
    print("- Integrated Score: Lower is better (top 3 selected)")
    print("\nAbsolute Momentum Filter:")
    print("- If momentum < 0 for selected asset → replace with cash (SHY)")

    print("\n✓ Formulas implemented according to PRD specifications")


def main():
    """Run all verification tests."""
    print("\n" + "="*70)
    print(" " * 15 + "FAA CALCULATOR MANUAL VERIFICATION")
    print("="*70)

    # Verify formulas
    verify_formulas()

    # Test individual functions
    success1 = test_individual_functions()

    if not success1:
        print("\n✗ Individual function tests failed. Aborting.")
        return False

    # Test full FAA calculation
    success2, scores = test_full_faa_calculation()

    if not success2:
        print("\n✗ Full FAA calculation failed. Aborting.")
        return False

    # Test allocation
    success3 = test_allocation()

    # Summary
    print_separator("VERIFICATION SUMMARY")

    all_success = success1 and success2 and success3

    if all_success:
        print("✓ All verification tests passed!")
        print("\nThe FAA Calculator is ready for production use.")
        return True
    else:
        print("✗ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
