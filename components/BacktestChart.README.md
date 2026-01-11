# BacktestChart Component

A responsive, accessible React component for visualizing FAA strategy backtest results with SPY benchmark comparison using Recharts.

## Installation

First, install the required dependency:

```bash
npm install recharts
# or
yarn add recharts
# or
pnpm add recharts
```

## Features

- **Dual-Line Chart**: Compare FAA strategy performance against SPY benchmark
- **Interactive Tooltip**: Displays date, portfolio values, and cumulative returns
- **Responsive Design**: Adapts to all viewport sizes
- **Summary Statistics**: Shows total returns and outperformance metrics
- **Loading State**: Built-in loading indicator
- **Accessible**: Follows WCAG accessibility guidelines
- **Theme Integration**: Consistent with shadcn/ui design system
- **Dark Mode Support**: Automatic color adaptation for dark mode

## Usage

### Basic Example

```tsx
import BacktestChart from '@/components/BacktestChart';

const backtestData = {
  equity_curve: [
    { date: "2019-01-01", value: 10000, return: 0.00 },
    { date: "2019-02-01", value: 10250, return: 0.025 },
    { date: "2019-03-01", value: 10500, return: 0.05 },
    // ... more data points
  ],
  spy_benchmark: [
    { date: "2019-01-01", value: 10000, return: 0.00 },
    { date: "2019-02-01", value: 10150, return: 0.015 },
    { date: "2019-03-01", value: 10300, return: 0.03 },
    // ... more data points
  ],
};

function MyPage() {
  return <BacktestChart data={backtestData} />;
}
```

### With Loading State

```tsx
function MyPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchBacktestData().then(result => {
      setData(result);
      setLoading(false);
    });
  }, []);

  return <BacktestChart data={data} isLoading={loading} />;
}
```

### API Integration

```tsx
'use client';

import { useState, useEffect } from 'react';
import BacktestChart, { BacktestData } from '@/components/BacktestChart';

export default function BacktestPage() {
  const [data, setData] = useState<BacktestData | null>(null);
  const [loading, setLoading] = useState(false);

  const runBacktest = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: ['SPY', 'TLT', 'VEA', 'VWO', 'DBC', 'BIL'],
          start_date: '2019-01-01',
          end_date: '2024-12-31',
        }),
      });

      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Backtest failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8">
      <button onClick={runBacktest}>Run Backtest</button>
      {data && <BacktestChart data={data} isLoading={loading} />}
    </div>
  );
}
```

## Props

### `BacktestChartProps`

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `data` | `BacktestData` | Yes | - | Backtest data containing equity curve and benchmark |
| `isLoading` | `boolean` | No | `false` | Shows loading state when true |

### `BacktestData`

```typescript
interface BacktestData {
  equity_curve: Array<{
    date: string;  // ISO date format "2019-01-01"
    value: number; // Portfolio value in dollars
    return: number; // Cumulative return as decimal (0.05 = 5%)
  }>;
  spy_benchmark: Array<{
    date: string;
    value: number;
    return: number;
  }>;
}
```

## Data Format

### Date Format
- **Input**: ISO date string `"2019-01-01"`
- **Display**: MM/YY format `"01/19"`

### Return Format
- **Input**: Decimal (0.05 for 5%)
- **Display**: Percentage with 2 decimal places ("+5.00%")

### Value Format
- **Input**: Raw dollar amount (10000)
- **Display**: Formatted currency ("$10,000.00")

## Customization

### Chart Colors

The component uses CSS custom properties for theming. You can customize colors in your `globals.css`:

```css
:root {
  --chart-1: 221.2 83.2% 53.3%; /* FAA strategy line color */
  --chart-2: 215.4 16.3% 46.9%; /* SPY benchmark line color */
}

.dark {
  --chart-1: 217.2 91.2% 59.8%; /* Dark mode FAA color */
  --chart-2: 215 20.2% 65.1%;   /* Dark mode SPY color */
}
```

### Chart Dimensions

Default height is 400px. To customize:

```tsx
// Edit the ResponsiveContainer height in BacktestChart.tsx
<ResponsiveContainer width="100%" height={500}>
```

## Components Structure

```
BacktestChart/
├── Chart Container (rounded border, card background)
│   ├── ResponsiveContainer
│   │   ├── LineChart
│   │   │   ├── CartesianGrid (3-3 dash pattern)
│   │   │   ├── XAxis (date in MM/YY format)
│   │   │   ├── YAxis (portfolio value)
│   │   │   ├── Tooltip (CustomTooltip)
│   │   │   ├── Legend
│   │   │   ├── Line (FAA Strategy)
│   │   │   └── Line (SPY Benchmark)
└── Summary Statistics (3-column grid)
    ├── FAA Total Return
    ├── SPY Total Return
    └── Outperformance
```

## Accessibility

- Semantic HTML structure
- ARIA labels for input elements
- Keyboard navigation support via Recharts
- High contrast colors for readability
- Responsive text sizes
- Screen reader friendly

## Performance Considerations

- Dots disabled on lines for better performance with large datasets
- Memoized tooltip rendering
- Efficient data transformation
- Responsive container handles resize efficiently

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires ES6+ support
- Responsive design works on all viewport sizes

## Troubleshooting

### Chart not displaying
- Ensure Recharts is installed: `npm install recharts`
- Check that data is in correct format
- Verify CSS variables are defined in globals.css

### Tooltip not showing
- Check that data points have all required fields
- Ensure CustomTooltip is receiving payload correctly

### Colors not matching theme
- Verify `--chart-1` and `--chart-2` are defined in CSS
- Check dark mode color variables are set

## Examples

See `BacktestChart.example.tsx` for more detailed usage examples.

## Dependencies

- `recharts`: ^2.x (peer dependency)
- `@/lib/utils`: For cn() utility
- shadcn/ui theme system

## License

Part of the FAA Calculator project.
