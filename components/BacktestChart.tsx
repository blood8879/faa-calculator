'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { cn } from '@/lib/utils';

/**
 * Backtest data structure
 */
export interface BacktestData {
  equity_curve: Array<{
    date: string;  // "2019-01-01"
    value: number; // 10500
    return: number; // 0.05
  }>;
  spy_benchmark: Array<{
    date: string;
    value: number;
    return: number;
  }>;
}

/**
 * BacktestChart component props
 */
interface BacktestChartProps {
  data: BacktestData;
  isLoading?: boolean;
}

/**
 * Custom tooltip for displaying detailed information
 */
interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    dataKey: string;
    payload: {
      date: string;
      faaValue: number;
      spyValue: number;
      faaReturn: number;
      spyReturn: number;
    };
  }>;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4 space-y-2">
      <p className="font-semibold text-sm text-foreground mb-2">{data.date}</p>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[hsl(var(--chart-1))]" />
            <span className="text-xs font-medium text-muted-foreground">FAA 전략</span>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-foreground">
              ${data.faaValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
            <p className={cn(
              "text-xs font-semibold",
              data.faaReturn >= 0 ? "text-green-600" : "text-red-600"
            )}>
              {data.faaReturn >= 0 ? '+' : ''}{(data.faaReturn * 100).toFixed(2)}%
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[hsl(var(--chart-2))]" />
            <span className="text-xs font-medium text-muted-foreground">SPY 벤치마크</span>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-foreground">
              ${data.spyValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
            <p className={cn(
              "text-xs font-semibold",
              data.spyReturn >= 0 ? "text-green-600" : "text-red-600"
            )}>
              {data.spyReturn >= 0 ? '+' : ''}{(data.spyReturn * 100).toFixed(2)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Format date for X-axis display (MM/YY)
 */
const formatXAxisDate = (dateString: string): string => {
  const date = new Date(dateString);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = String(date.getFullYear()).slice(-2);
  return `${month}/${year}`;
};

/**
 * Format Y-axis value (Portfolio Value)
 */
const formatYAxisValue = (value: number): string => {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`;
  }
  return `$${value}`;
};

/**
 * BacktestChart Component
 *
 * Displays cumulative return comparison between FAA strategy and SPY benchmark.
 *
 * Features:
 * - Dual-line chart comparing FAA strategy vs SPY benchmark
 * - Interactive tooltip showing date, portfolio values, and returns
 * - Responsive design
 * - Consistent styling with shadcn/ui theme
 * - Loading state
 *
 * @example
 * ```tsx
 * <BacktestChart
 *   data={{
 *     equity_curve: [...],
 *     spy_benchmark: [...]
 *   }}
 *   isLoading={false}
 * />
 * ```
 */
export default function BacktestChart({ data, isLoading = false }: BacktestChartProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold tracking-tight">백테스트 결과</h2>
        </div>
        <div className="rounded-lg border p-8 flex items-center justify-center min-h-[400px]">
          <p className="text-muted-foreground">백테스트 데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  // Validate data
  if (!data || !data.equity_curve || !data.spy_benchmark ||
      data.equity_curve.length === 0 || data.spy_benchmark.length === 0) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold tracking-tight">백테스트 결과</h2>
        </div>
        <div className="rounded-lg border p-8 flex items-center justify-center min-h-[400px]">
          <p className="text-muted-foreground">백테스트 데이터가 없습니다</p>
        </div>
      </div>
    );
  }

  // Merge data for chart (align by date)
  const chartData = data.equity_curve.map((faaPoint, index) => {
    const spyPoint = data.spy_benchmark[index] || data.spy_benchmark[data.spy_benchmark.length - 1];

    return {
      date: formatXAxisDate(faaPoint.date),
      faaValue: faaPoint.value,
      spyValue: spyPoint.value,
      faaReturn: faaPoint.return,
      spyReturn: spyPoint.return,
    };
  });

  // Calculate summary statistics
  const finalFaaReturn = data.equity_curve[data.equity_curve.length - 1]?.return || 0;
  const finalSpyReturn = data.spy_benchmark[data.spy_benchmark.length - 1]?.return || 0;
  const outperformance = finalFaaReturn - finalSpyReturn;

  return (
    <div className="w-full space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">백테스트 결과</h2>
          <p className="text-sm text-muted-foreground mt-1">
            누적 수익률 비교: FAA 전략 vs SPY 벤치마크
          </p>
        </div>
      </div>

      {/* Chart Container */}
      <div className="rounded-lg border overflow-hidden bg-card">
        <div className="p-6">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                className="stroke-muted"
                opacity={0.3}
              />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
                tickLine={{ stroke: 'hsl(var(--border))' }}
                axisLine={{ stroke: 'hsl(var(--border))' }}
              />
              <YAxis
                tickFormatter={formatYAxisValue}
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
                tickLine={{ stroke: 'hsl(var(--border))' }}
                axisLine={{ stroke: 'hsl(var(--border))' }}
                label={{
                  value: '포트폴리오 가치',
                  angle: -90,
                  position: 'insideLeft',
                  className: 'text-muted-foreground text-sm'
                }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              <Line
                type="monotone"
                dataKey="faaValue"
                stroke="hsl(var(--chart-1))"
                strokeWidth={2}
                dot={false}
                name="FAA 전략"
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="spyValue"
                stroke="hsl(var(--chart-2))"
                strokeWidth={2}
                dot={false}
                name="SPY 벤치마크"
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-lg border p-4 bg-card">
          <p className="text-xs text-muted-foreground mb-1">FAA 총 수익률</p>
          <p className={cn(
            "text-2xl font-bold",
            finalFaaReturn >= 0 ? "text-green-600" : "text-red-600"
          )}>
            {finalFaaReturn >= 0 ? '+' : ''}{(finalFaaReturn * 100).toFixed(2)}%
          </p>
        </div>

        <div className="rounded-lg border p-4 bg-card">
          <p className="text-xs text-muted-foreground mb-1">SPY 총 수익률</p>
          <p className={cn(
            "text-2xl font-bold",
            finalSpyReturn >= 0 ? "text-green-600" : "text-red-600"
          )}>
            {finalSpyReturn >= 0 ? '+' : ''}{(finalSpyReturn * 100).toFixed(2)}%
          </p>
        </div>

        <div className="rounded-lg border p-4 bg-card">
          <p className="text-xs text-muted-foreground mb-1">초과 수익</p>
          <p className={cn(
            "text-2xl font-bold",
            outperformance >= 0 ? "text-green-600" : "text-red-600"
          )}>
            {outperformance >= 0 ? '+' : ''}{(outperformance * 100).toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  );
}
