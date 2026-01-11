# Quick Start: Backtest API

## Overview
The backtest API simulates the FAA strategy over a historical period and returns performance metrics.

## Basic Usage

### 1. Simple Request (1 year backtest)

```bash
curl -X POST http://localhost:3000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
    "start_date": "2023-01-01"
  }'
```

### 2. JavaScript/TypeScript (Next.js)

```typescript
const runBacktest = async () => {
  const response = await fetch('/api/backtest', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tickers: ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'],
      start_date: '2023-01-01'
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('Performance Metrics:');
    console.log(`CAGR: ${(data.metrics.cagr * 100).toFixed(2)}%`);
    console.log(`Max Drawdown: ${(data.metrics.mdd * 100).toFixed(2)}%`);
    console.log(`Sharpe Ratio: ${data.metrics.sharpe.toFixed(2)}`);

    // Access equity curve
    data.equity_curve.forEach(point => {
      console.log(`${point.date}: $${point.value} (${(point.return * 100).toFixed(2)}%)`);
    });
  }
};
```

### 3. Python

```python
import requests
from datetime import datetime, timedelta

# Calculate start date (1 year ago)
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

response = requests.post(
    'http://localhost:3000/api/backtest',
    json={
        'tickers': ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'],
        'start_date': start_date
    }
)

data = response.json()

if data['success']:
    print(f"CAGR: {data['metrics']['cagr']:.2%}")
    print(f"Max Drawdown: {data['metrics']['mdd']:.2%}")
    print(f"Sharpe Ratio: {data['metrics']['sharpe']:.2f}")
    print(f"Total return: {data['equity_curve'][-1]['return']:.2%}")
```

## Response Structure

```json
{
  "success": true,
  "equity_curve": [
    {"date": "2023-01-03", "value": 10000.0, "return": 0.0},
    {"date": "2023-01-04", "value": 10025.5, "return": 0.0026},
    ...
  ],
  "metrics": {
    "cagr": 0.1234,      // 12.34% annualized return
    "mdd": -0.0856,      // -8.56% maximum drawdown
    "sharpe": 1.45       // Sharpe ratio
  },
  "spy_benchmark": [
    {"date": "2023-01-03", "value": 10000.0, "return": 0.0},
    ...
  ]
}
```

## Common Use Cases

### Compare Strategy vs Benchmark

```javascript
const comparePerformance = (data) => {
  const faaReturn = data.equity_curve[data.equity_curve.length - 1].return;
  const spyReturn = data.spy_benchmark[data.spy_benchmark.length - 1].return;

  const outperformance = faaReturn - spyReturn;

  console.log(`FAA Strategy: ${(faaReturn * 100).toFixed(2)}%`);
  console.log(`SPY Benchmark: ${(spyReturn * 100).toFixed(2)}%`);
  console.log(`Outperformance: ${(outperformance * 100).toFixed(2)}%`);
};
```

### Plot Equity Curve

```javascript
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';

const EquityCurveChart = ({ data }) => {
  const chartData = data.equity_curve.map((point, index) => ({
    date: point.date,
    FAA: point.value,
    SPY: data.spy_benchmark[index]?.value || 0
  }));

  return (
    <LineChart width={800} height={400} data={chartData}>
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="FAA" stroke="#8884d8" />
      <Line type="monotone" dataKey="SPY" stroke="#82ca9d" />
    </LineChart>
  );
};
```

### Calculate Additional Metrics

```javascript
const calculateAdditionalMetrics = (equityCurve) => {
  const returns = equityCurve.map(point => point.return);

  // Total return
  const totalReturn = returns[returns.length - 1];

  // Volatility (annualized)
  const dailyReturns = [];
  for (let i = 1; i < equityCurve.length; i++) {
    const dailyReturn = (equityCurve[i].value - equityCurve[i-1].value) / equityCurve[i-1].value;
    dailyReturns.push(dailyReturn);
  }

  const mean = dailyReturns.reduce((a, b) => a + b, 0) / dailyReturns.length;
  const variance = dailyReturns.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / dailyReturns.length;
  const volatility = Math.sqrt(variance) * Math.sqrt(252); // Annualized

  return {
    totalReturn,
    volatility,
  };
};
```

## Testing Locally

### 1. Run Tests

```bash
# Comprehensive test suite
python test_backtest.py

# Simple end-to-end tests
python test_backtest_simple.py
```

### 2. Start Development Server

```bash
npm run dev
```

### 3. Test API Endpoint

```bash
curl -X POST http://localhost:3000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
    "start_date": "2023-01-01"
  }' | jq
```

## Performance Tips

- **Shorter periods** (1-2 years) run faster (~0.5 seconds)
- **Longer periods** (5 years) still fast (~0.7 seconds)
- All data is downloaded once at the start for efficiency
- Results are not cached (each request runs fresh calculation)

## Error Handling

```javascript
const handleBacktestRequest = async () => {
  try {
    const response = await fetch('/api/backtest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tickers: ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'],
        start_date: '2023-01-01'
      })
    });

    const data = await response.json();

    if (!data.success) {
      console.error('Backtest failed:', data.error);
      return;
    }

    // Process results...
  } catch (error) {
    console.error('Network error:', error);
  }
};
```

## Next Steps

- See [BACKTEST_API.md](./BACKTEST_API.md) for complete API documentation
- See [TASK-013-SUMMARY.md](./TASK-013-SUMMARY.md) for implementation details
- Check [test_backtest.py](./test_backtest.py) for usage examples
