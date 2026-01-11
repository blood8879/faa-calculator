#!/usr/bin/env python3
"""
Test new momentum calculation (average of 1m, 3m, 6m, 12m)
"""

import sys
sys.path.append('./api')

from faa_calculator import calculate_momentum

print("=" * 80)
print("새로운 모멘텀 계산 테스트 (1개월, 3개월, 6개월, 12개월 평균)")
print("=" * 80)

# Test tickers from the screenshot
test_tickers = ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'PDBC', 'VNQ']

print("\n티커별 모멘텀:")
print("-" * 80)
print(f"{'티커':^10s} | {'모멘텀':^12s} | {'모멘텀(%)':^12s} | {'상태':^10s}")
print("-" * 80)

for ticker in test_tickers:
    try:
        momentum = calculate_momentum(ticker)
        status = "📉 음수" if momentum < 0 else "📈 양수"
        print(f"{ticker:^10s} | {momentum:>12.6f} | {momentum*100:>11.2f}% | {status:^10s}")
    except Exception as e:
        print(f"{ticker:^10s} | {'에러':^12s} | {str(e)[:30]:^12s} | {'':^10s}")

print("-" * 80)

print("\n" + "=" * 80)
print("참고: jasan-calc.netlify.app 결과와 비교")
print("=" * 80)
print("VTI:  5.4%")
print("VEA:  7.4%")
print("VWO:  3.4%")
print("SHY: -0.2%  ← 음수 확인!")
print("BND: -0.5%  ← 음수 확인!")
print("VNQ: -4.0%  ← 음수 확인!")
print("=" * 80)
