'use client';

import React, { useState } from 'react';
import TickerInput from '@/components/TickerInput';
import ScoreTable, { ScoreData } from '@/components/ScoreTable';
import AllocationResult from '@/components/AllocationResult';
import UserGuide from '@/components/UserGuide';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const [validTickers, setValidTickers] = useState<string[]>([]);
  const [allValid, setAllValid] = useState(false);
  const [scores, setScores] = useState<ScoreData[]>([]);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasCalculated, setHasCalculated] = useState(false);

  const handleValidationComplete = (tickers: string[], valid: boolean) => {
    setValidTickers(tickers);
    setAllValid(valid);
  };

  const calculateScores = async () => {
    if (!allValid || validTickers.length !== 7) {
      return;
    }

    setIsCalculating(true);
    setError(null);

    try {
      const response = await fetch('/api/score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tickers: validTickers }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to calculate scores');
      }

      // Transform API response to ScoreData format
      const scoresData: ScoreData[] = Object.entries(data.scores).map(
        ([ticker, scoreInfo]: [string, any]) => ({
          ticker,
          current_price: scoreInfo.current_price,
          momentum: scoreInfo.momentum,
          volatility: scoreInfo.volatility,
          correlation: scoreInfo.correlation,
          momentum_rank: scoreInfo.momentum_rank,
          volatility_rank: scoreInfo.volatility_rank,
          correlation_rank: scoreInfo.correlation_rank,
          total_score: scoreInfo.integrated_score,
          selected: scoreInfo.selected,
          cash_proxy: scoreInfo.cash_replacement,
          hold_cash: scoreInfo.hold_cash || false,
        })
      );

      setScores(scoresData);
      setHasCalculated(true);
    } catch (err) {
      console.error('Score calculation error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <div className="container py-8">
      {/* User Guide Button */}
      <UserGuide />

      <div className="flex flex-col space-y-8">
        {/* Header */}
        <div className="flex flex-col space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">FAA 계산기</h1>
          <p className="text-muted-foreground">
            FAA 전략을 사용하여 최적의 포트폴리오 배분을 계산합니다
          </p>
        </div>

        {/* Step 1: Ticker Input */}
        <TickerInput onValidationComplete={handleValidationComplete} />

        {/* Calculate Button */}
        {allValid && (
          <div className="flex items-center justify-center">
            <Button
              onClick={calculateScores}
              disabled={isCalculating}
              size="lg"
              className="min-w-[200px]"
            >
              {isCalculating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  계산 중...
                </>
              ) : (
                'FAA 스코어 계산'
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

        {/* Step 2: Score Table */}
        {hasCalculated && scores.length > 0 && (
          <ScoreTable scores={scores} isLoading={isCalculating} />
        )}

        {/* Step 3: Allocation Result */}
        {hasCalculated && scores.length > 0 && (
          <AllocationResult scores={scores} />
        )}
      </div>
    </div>
  );
}
