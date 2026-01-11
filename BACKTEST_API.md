# Backtest API Documentation

## Overview

The Backtest API endpoint (`/api/backtest`) simulates the FAA (Flexible Asset Allocation) strategy over a historical period, providing performance metrics and comparison with the SPY benchmark.

## Endpoint

```
POST /api/backtest
```

## Request Format

### Headers
```
Content-Type: application/json
```

### Body

```json
{
  "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
  "start_date": "2019-01-01"
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tickers` | Array of strings | Yes | List of ticker symbols for FAA universe |
| `start_date` | String | Yes | Start date in YYYY-MM-DD format |

### Validation Rules

- `tickers` must be a non-empty array of strings
- `start_date` must be in YYYY-MM-DD format
- `start_date` cannot be in the future
- All tickers must have sufficient historical data (at least 150 days before start_date)

## Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "equity_curve": [
    {
      "date": "2019-01-02",
      "value": 10000.0,
      "return": 0.0
    },
    {
      "date": "2019-01-03",
      "value": 10050.25,
      "return": 0.0050
    },
    ...
  ],
  "metrics": {
    "cagr": 0.12,
    "mdd": -0.15,
    "sharpe": 1.5
  },
  "spy_benchmark": [
    {
      "date": "2019-01-02",
      "value": 10000.0,
      "return": 0.0
    },
    ...
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | Indicates if the request was successful |
| `equity_curve` | Array | Daily portfolio values for FAA strategy |
| `equity_curve[].date` | String | Date in YYYY-MM-DD format |
| `equity_curve[].value` | Number | Portfolio value in USD |
| `equity_curve[].return` | Number | Cumulative return (decimal, e.g., 0.05 = 5%) |
| `metrics` | Object | Performance metrics |
| `metrics.cagr` | Number | Compound Annual Growth Rate (decimal) |
| `metrics.mdd` | Number | Maximum Drawdown (negative decimal) |
| `metrics.sharpe` | Number | Sharpe Ratio (annualized) |
| `spy_benchmark` | Array | Daily portfolio values for SPY buy-and-hold |

### Error Responses

#### 400 Bad Request
```json
{
  "success": false,
  "error": "Missing 'tickers' field in request"
}
```

Common 400 errors:
- Missing request body
- Missing `tickers` field
- Missing `start_date` field
- Invalid date format
- Start date in the future

#### 422 Unprocessable Entity
```json
{
  "success": false,
  "error": "Insufficient data for ticker: VTI"
}
```

Common 422 errors:
- Unable to download price data
- Insufficient historical data for backtest period
- Invalid ticker symbols

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error: ..."
}
```

## Implementation Details

### Strategy Simulation

1. **Data Download**: Downloads historical price data for all tickers and SPY benchmark
2. **Monthly Rebalancing**: Executes FAA strategy on the first trading day of each month
3. **Position Sizing**: Equal-weight allocation across top 3 selected assets
4. **Cash Replacement**: Assets with negative momentum are replaced with SHY
5. **Daily Tracking**: Portfolio value is tracked daily between rebalancing dates

### Performance Metrics

#### CAGR (Compound Annual Growth Rate)
```
CAGR = (Final Value / Initial Value) ^ (1 / Years) - 1
```

#### MDD (Maximum Drawdown)
```
MDD = max((Peak - Current) / Peak) for all dates
```
Returned as a negative value (e.g., -0.15 = -15% drawdown)

#### Sharpe Ratio
```
Sharpe = mean(daily_returns) / std(daily_returns) * sqrt(252)
```
Annualized using 252 trading days per year

### Performance Requirements

- **5-year backtest**: < 10 seconds
- **1-year backtest**: < 2 seconds

The implementation uses optimized batch data downloading and vectorized calculations to meet these requirements.

## Example Usage

### cURL

```bash
curl -X POST https://your-domain.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
    "start_date": "2019-01-01"
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('/api/backtest', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tickers: ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'],
    start_date: '2019-01-01'
  })
});

const data = await response.json();

if (data.success) {
  console.log('CAGR:', data.metrics.cagr);
  console.log('MDD:', data.metrics.mdd);
  console.log('Sharpe:', data.metrics.sharpe);
}
```

### Python

```python
import requests

response = requests.post(
    'https://your-domain.com/api/backtest',
    json={
        'tickers': ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'],
        'start_date': '2019-01-01'
    }
)

data = response.json()

if data['success']:
    print(f"CAGR: {data['metrics']['cagr']:.2%}")
    print(f"MDD: {data['metrics']['mdd']:.2%}")
    print(f"Sharpe: {data['metrics']['sharpe']:.2f}")
```

## Testing

Run the test suite:

```bash
# Unit and integration tests
python test_backtest.py

# Simple end-to-end tests
python test_backtest_simple.py
```

## Notes

- Initial portfolio value is fixed at $10,000 for all simulations
- All calculations use adjusted closing prices from Yahoo Finance
- Rebalancing occurs on the first trading day of each month
- The equity curve includes daily portfolio values (not just rebalancing dates)
- SPY benchmark uses simple buy-and-hold strategy with no rebalancing

## Related Documentation

- [FAA Calculator API](./api/faa_calculator.py) - Core FAA strategy implementation
- [Score API](./api/score.py) - Current FAA scores endpoint
- [PRD](./docs/PRD.md) - Product Requirements Document
