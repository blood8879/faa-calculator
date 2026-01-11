#!/usr/bin/env python3
"""
Verify momentum calculation logic
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

print("=" * 80)
print("모멘텀 계산 로직 검증")
print("=" * 80)

ticker = "SHY"
end_date = datetime.now()
start_date = end_date - timedelta(days=150)

# Download data
data = yf.download(ticker, start=start_date, end=end_date, progress=False)
prices = data['Close']

print(f"\n✓ 다운로드된 데이터: {len(prices)}일")
print(f"  시작일: {prices.index[0].strftime('%Y-%m-%d')}")
print(f"  종료일: {prices.index[-1].strftime('%Y-%m-%d')}")

# Current logic
if len(prices) >= 80:
    current_price = float(prices.iloc[-1])
    price_4m_ago = float(prices.iloc[-80])

    momentum = (current_price / price_4m_ago) - 1

    print(f"\n현재 로직:")
    print(f"  80일 전 가격 ({prices.index[-80].strftime('%Y-%m-%d')}): ${price_4m_ago:.4f}")
    print(f"  현재 가격 ({prices.index[-1].strftime('%Y-%m-%d')}): ${current_price:.4f}")
    print(f"  모멘텀: {momentum:.6f} ({momentum*100:.2f}%)")

    # Calculate actual trading days difference
    days_diff = (prices.index[-1] - prices.index[-80]).days
    print(f"  실제 일수 차이: {days_diff}일 (약 {days_diff/30.5:.1f}개월)")

print("\n" + "=" * 80)
print("다양한 기간별 모멘텀 비교")
print("=" * 80)

periods = {
    "1개월 (20일)": 20,
    "2개월 (40일)": 40,
    "3개월 (60일)": 60,
    "4개월 (80일)": 80,
    "5개월 (100일)": 100,
    "6개월 (120일)": 120,
}

for label, days in periods.items():
    if len(prices) >= days:
        past_price = float(prices.iloc[-days])
        current_price = float(prices.iloc[-1])
        momentum = (current_price / past_price) - 1

        past_date = prices.index[-days].strftime('%Y-%m-%d')
        print(f"{label:20s}: {momentum:+.6f} ({momentum*100:+.2f}%) [{past_date} → 현재]")

print("\n" + "=" * 80)
print("최근 12개월 월별 모멘텀 추이 (SHY)")
print("=" * 80)

# Get 1 year of data
end_date = datetime.now()
start_date = end_date - timedelta(days=400)
data_1y = yf.download(ticker, start=start_date, end=end_date, progress=False)
prices_1y = data_1y['Close']

# Calculate monthly momentum
for months_ago in range(12, 0, -1):
    if len(prices_1y) >= months_ago * 21:  # Approximate 21 trading days per month
        days_back = months_ago * 21
        if days_back <= len(prices_1y):
            past_price = float(prices_1y.iloc[-days_back])
            current_price = float(prices_1y.iloc[-1])
            momentum = (current_price / past_price) - 1

            past_date = prices_1y.index[-days_back].strftime('%Y-%m-%d')
            symbol = "📉" if momentum < 0 else "📈"
            print(f"{months_ago:2d}개월 전부터: {momentum:+.6f} ({momentum*100:+.2f}%) {symbol}")

print("\n" + "=" * 80)
