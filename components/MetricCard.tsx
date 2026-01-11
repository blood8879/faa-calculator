"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  metrics: {
    cagr: number; // 0.12 = 12%
    mdd: number; // -0.15 = -15%
    sharpe: number; // 1.5
  };
  isLoading?: boolean;
}

interface MetricConfig {
  name: string;
  description: string;
  getValue: (metrics: MetricCardProps["metrics"]) => number;
  format: (value: number) => string;
  getColorClass: (value: number) => string;
}

const METRICS_CONFIG: MetricConfig[] = [
  {
    name: "연평균 성장률",
    description: "CAGR (Compound Annual Growth Rate)",
    getValue: (metrics) => metrics.cagr,
    format: (value) => `${value >= 0 ? "+" : ""}${(value * 100).toFixed(1)}%`,
    getColorClass: (value) => (value >= 0 ? "text-green-600" : "text-red-600"),
  },
  {
    name: "최대 낙폭",
    description: "MDD (Maximum Drawdown)",
    getValue: (metrics) => metrics.mdd,
    format: (value) => `${(value * 100).toFixed(1)}%`,
    getColorClass: () => "text-red-600", // Always red
  },
  {
    name: "샤프 지수",
    description: "위험 조정 수익률 (Sharpe Ratio)",
    getValue: (metrics) => metrics.sharpe,
    format: (value) => value.toFixed(2),
    getColorClass: (value) => (value > 1 ? "text-green-600" : "text-red-600"),
  },
];

function MetricCardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium">
          <div className="h-4 w-24 animate-pulse rounded bg-muted" />
        </CardTitle>
        <CardDescription>
          <div className="h-3 w-40 animate-pulse rounded bg-muted" />
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-10 w-28 animate-pulse rounded bg-muted" />
      </CardContent>
    </Card>
  );
}

function SingleMetricCard({
  config,
  metrics,
}: {
  config: MetricConfig;
  metrics: MetricCardProps["metrics"];
}) {
  const value = config.getValue(metrics);
  const formattedValue = config.format(value);
  const colorClass = config.getColorClass(value);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium">{config.name}</CardTitle>
        <CardDescription className="text-xs">
          {config.description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className={cn("text-3xl font-bold", colorClass)}>
          {formattedValue}
        </div>
      </CardContent>
    </Card>
  );
}

export function MetricCard({ metrics, isLoading = false }: MetricCardProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCardSkeleton />
        <MetricCardSkeleton />
        <MetricCardSkeleton />
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {METRICS_CONFIG.map((config) => (
        <SingleMetricCard
          key={config.name}
          config={config}
          metrics={metrics}
        />
      ))}
    </div>
  );
}
