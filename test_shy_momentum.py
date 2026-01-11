#!/usr/bin/env python3
"""
Test script to verify SHY momentum calculation
"""

import sys
sys.path.append('./api')

from faa_calculator import calculate_momentum, calculate_volatility
from datetime import datetime

print("=" * 60)
print("SHY (단기 미국 국채) 모멘텀 테스트")
print("=" * 60)

# Calculate SHY momentum
try:
    shy_momentum = calculate_momentum('SHY')
    print(f"\n✓ SHY 모멘텀: {shy_momentum:.6f} ({shy_momentum*100:.2f}%)")

    if shy_momentum < 0:
        print("  → 음수 모멘텀 (하락)")
    else:
        print("  → 양수 모멘텀 (상승)")

    # Calculate SHY volatility for context
    shy_volatility = calculate_volatility('SHY')
    print(f"✓ SHY 변동성: {shy_volatility:.6f} ({shy_volatility*100:.2f}%)")

except Exception as e:
    print(f"\n✗ 에러 발생: {str(e)}")

print("\n" + "=" * 60)
print("다른 현금성 자산 비교")
print("=" * 60)

# Test other cash-like assets
cash_tickers = ['SHY', 'BIL', 'VGSH', 'AGG']

for ticker in cash_tickers:
    try:
        momentum = calculate_momentum(ticker)
        status = "📉 음수" if momentum < 0 else "📈 양수"
        print(f"{ticker:6s}: {momentum:+.6f} ({momentum*100:+.2f}%) {status}")
    except Exception as e:
        print(f"{ticker:6s}: 데이터 없음 ({str(e)})")

print("\n" + "=" * 60)
