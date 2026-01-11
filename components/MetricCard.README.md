# MetricCard Component

A responsive card component to display performance metrics (CAGR, MDD, Sharpe Ratio) with color-coded values.

## Features

- Responsive grid layout (1 column mobile, 3 columns desktop)
- Color-coded values (green for positive, red for negative)
- Loading skeleton states
- Consistent number formatting
- Built with shadcn/ui Card component

## Usage

```tsx
import { MetricCard } from "@/components/MetricCard";

function BacktestResults() {
  const metrics = {
    cagr: 0.125,    // 12.5%
    mdd: -0.152,    // -15.2%
    sharpe: 1.5,    // 1.50
  };

  return <MetricCard metrics={metrics} />;
}
```

## Props

```typescript
interface MetricCardProps {
  metrics: {
    cagr: number;      // Decimal format: 0.12 = 12%
    mdd: number;       // Decimal format: -0.15 = -15%
    sharpe: number;    // Ratio: 1.5
  };
  isLoading?: boolean; // Show skeleton loading state
}
```

## Metric Specifications

### CAGR (Compound Annual Growth Rate)
- **Format**: `+12.5%` (1 decimal place)
- **Color**: Green if positive, red if negative
- **Description**: "Compound Annual Growth Rate"

### MDD (Maximum Drawdown)
- **Format**: `-15.2%` (1 decimal place)
- **Color**: Always red
- **Description**: "Maximum Drawdown"

### Sharpe Ratio
- **Format**: `1.50` (2 decimal places)
- **Color**: Green if > 1, red otherwise
- **Description**: "Risk-Adjusted Return"

## Examples

### Normal State
```tsx
<MetricCard
  metrics={{
    cagr: 0.125,
    mdd: -0.152,
    sharpe: 1.5
  }}
/>
```

### Loading State
```tsx
<MetricCard
  metrics={{
    cagr: 0,
    mdd: 0,
    sharpe: 0
  }}
  isLoading={true}
/>
```

### Negative Performance
```tsx
<MetricCard
  metrics={{
    cagr: -0.035,  // -3.5%
    mdd: -0.25,    // -25.0%
    sharpe: 0.8    // 0.80
  }}
/>
```

## Responsive Behavior

- **Mobile (< 768px)**: Single column layout
- **Desktop (≥ 768px)**: Three column grid layout

## Dependencies

- `@/components/ui/card` (shadcn/ui)
- `@/lib/utils` (cn utility)
- React 18+

## File Location

`/Users/yunjihwan/Documents/project/faa-calculator/components/MetricCard.tsx`
