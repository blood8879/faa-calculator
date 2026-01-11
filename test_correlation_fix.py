#!/usr/bin/env python3
"""Test script to verify correlation calculation fix."""

import requests
import json

# Test with the same tickers from the screenshot
test_tickers = ["VNQ", "GSG", "VWO", "BND", "VTI", "VEA", "SHY"]

print("🧪 Testing correlation calculation fix...")
print(f"Tickers: {', '.join(test_tickers)}\n")

try:
    # Call the API
    response = requests.post(
        "http://localhost:8000/api/score",
        json={"tickers": test_tickers},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()

        print("✅ API Response successful!\n")
        print("Ticker | Correlation | Rank")
        print("-" * 40)

        # Sort by ticker for consistent display
        for ticker in test_tickers:
            if ticker in data['scores']:
                score = data['scores'][ticker]
                corr = score.get('correlation', 'N/A')
                rank = score.get('correlation_rank', 'N/A')
                print(f"{ticker:6} | {corr:11.4f} | {rank:4}")

        print("\n📊 Validation:")
        all_valid = True
        for ticker, score in data['scores'].items():
            corr = score.get('correlation', -1)
            if not (0 <= corr <= 1):
                print(f"❌ {ticker}: correlation = {corr} (OUT OF RANGE!)")
                all_valid = False

        if all_valid:
            print("✅ All correlations are within valid range [0, 1]")

    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Test failed: {e}")
