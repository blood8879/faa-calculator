// Example usage of MetricCard component
// This file is for documentation purposes only

import { MetricCard } from "./MetricCard";

export function MetricCardExample() {
  // Example 1: Positive performance
  const positiveMetrics = {
    cagr: 0.125, // +12.5%
    mdd: -0.152, // -15.2%
    sharpe: 1.5, // 1.50
  };

  // Example 2: Negative performance
  const negativeMetrics = {
    cagr: -0.035, // -3.5%
    mdd: -0.25, // -25.0%
    sharpe: 0.8, // 0.80
  };

  // Example 3: Loading state
  return (
    <div className="space-y-8">
      <div>
        <h2 className="mb-4 text-xl font-semibold">Positive Performance</h2>
        <MetricCard metrics={positiveMetrics} />
      </div>

      <div>
        <h2 className="mb-4 text-xl font-semibold">Negative Performance</h2>
        <MetricCard metrics={negativeMetrics} />
      </div>

      <div>
        <h2 className="mb-4 text-xl font-semibold">Loading State</h2>
        <MetricCard
          metrics={positiveMetrics}
          isLoading={true}
        />
      </div>
    </div>
  );
}
