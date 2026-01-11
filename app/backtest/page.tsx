'use client';

import React, { useState } from 'react';
import TickerInput from '@/components/TickerInput';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import BacktestChart from '@/components/BacktestChart';
import { MetricCard } from '@/components/MetricCard';
import { Loader2 } from 'lucide-react';

interface BacktestData {
  equity_curve: Array<{
    date: string;
    value: number;
    return: number;
  }>;
  spy_benchmark: Array<{
    date: string;
    value: number;
    return: number;
  }>;
  metrics: {
    cagr: number;
    mdd: number;
    sharpe: number;
  };
}

export default function BacktestPage() {
  const [startDate, setStartDate] = useState('2019-01-01');
  const [validTickers, setValidTickers] = useState<string[]>([]);
  const [allValid, setAllValid] = useState(false);
  const [backtestData, setBacktestData] = useState<BacktestData | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleValidationComplete = (tickers: string[], valid: boolean) => {
    setValidTickers(tickers);
    setAllValid(valid);
  };

  const runBacktest = async () => {
    if (!allValid || validTickers.length !== 7) {
      return;
    }

    setIsRunning(true);
    setError(null);

    try {
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tickers: validTickers,
          start_date: startDate,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Backtest failed');
      }

      setBacktestData({
        equity_curve: data.equity_curve,
        spy_benchmark: data.spy_benchmark,
        metrics: data.metrics,
      });
    } catch (err) {
      console.error('Backtest error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="container py-8">
      <div className="flex flex-col space-y-8">
        {/* Header */}
        <div className="flex flex-col space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">백테스트</h1>
          <p className="text-muted-foreground">
            과거 데이터로 FAA 전략을 테스트하고 SPY 벤치마크와 비교합니다
          </p>
        </div>

        {/* Ticker Input */}
        <TickerInput onValidationComplete={handleValidationComplete} />

        {/* Controls */}
        {allValid && (
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1 space-y-2">
              <label htmlFor="start-date" className="text-sm font-medium">
                시작 날짜
              </label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="max-w-xs"
              />
            </div>
            <Button
              onClick={runBacktest}
              disabled={isRunning || !startDate}
              size="lg"
              className="min-w-[200px]"
            >
              {isRunning ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  백테스트 실행 중...
                </>
              ) : (
                '백테스트 실행'
              )}
            </Button>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="rounded-lg border border-destructive bg-destructive/10 p-4">
            <p className="text-sm text-destructive font-medium">오류: {error}</p>
          </div>
        )}

        {/* Results */}
        {backtestData && (
          <>
            {/* Metrics */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold tracking-tight">성과 지표</h2>
              <MetricCard metrics={backtestData.metrics} isLoading={isRunning} />
            </div>

            {/* Chart */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold tracking-tight">자산 곡선</h2>
              <BacktestChart
                data={{
                  equity_curve: backtestData.equity_curve,
                  spy_benchmark: backtestData.spy_benchmark,
                }}
                isLoading={isRunning}
              />
            </div>
          </>
        )}

        {/* Empty State */}
        {!backtestData && !isRunning && allValid && (
          <div className="text-center py-12 rounded-lg border border-dashed">
            <p className="text-muted-foreground">
              시작 날짜를 선택하고 &quot;백테스트 실행&quot;을 클릭하세요
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
