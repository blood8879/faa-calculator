#!/usr/bin/env python3
"""
Detailed momentum breakdown to understand the calculation
"""

import yfinance as yf
from datetime import datetime, timedelta

ticker = "SHY"
end_date = datetime.now()
start_date = end_date - timedelta(days=430)

print("=" * 80)
print(f"SHY 모멘텀 상세 분석 (현재 시점: {end_date.strftime('%Y-%m-%d')})")
print("=" * 80)

data = yf.download(ticker, start=start_date, end=end_date, progress=False)
prices = data['Close']

print(f"\n다운로드된 데이터: {len(prices)}일")
print(f"시작: {prices.index[0].strftime('%Y-%m-%d')}")
print(f"종료: {prices.index[-1].strftime('%Y-%m-%d')}")

current_price = float(prices.iloc[-1])

print(f"\n현재 가격: ${current_price:.4f}")
print("\n기간별 수익률:")
print("-" * 80)

periods = [
    ("1개월", 21),
    ("3개월", 63),
    ("6개월", 126),
    ("12개월", 252),
]

returns = []
for label, days in periods:
    if len(prices) >= days:
        past_price = float(prices.iloc[-days])
        past_date = prices.index[-days].strftime('%Y-%m-%d')
        ret = (current_price / past_price) - 1
        returns.append(ret)

        print(f"{label:8s} ({past_date}): ${past_price:7.4f} → ${current_price:7.4f} = {ret:+.6f} ({ret*100:+.2f}%)")

avg_momentum = sum(returns) / len(returns) if returns else 0
print("-" * 80)
print(f"평균 모멘텀: {avg_momentum:.6f} ({avg_momentum*100:.2f}%)")

print("\n" + "=" * 80)
print("최근 12개월 가격 추이 (SHY)")
print("=" * 80)

# Show monthly prices
for months_ago in range(12, 0, -1):
    days_back = months_ago * 21
    if days_back <= len(prices):
        price = float(prices.iloc[-days_back])
        date = prices.index[-days_back].strftime('%Y-%m-%d')
        change = (current_price / price - 1) * 100
        print(f"{months_ago:2d}개월 전 ({date}): ${price:.4f} ({change:+.2f}%)")

print(f" 0개월 전 ({prices.index[-1].strftime('%Y-%m-%d')}): ${current_price:.4f} (0.00%)")

print("\n" + "=" * 80)
