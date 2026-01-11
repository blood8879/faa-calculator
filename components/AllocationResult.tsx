'use client';

import React, { useState, useEffect } from 'react';
import { getAmount, saveAmount, getPortfolio } from '@/lib/localStorage';
import { cn } from '@/lib/utils';

export interface ScoreData {
  ticker: string;
  current_price: number;
  momentum: number;
  volatility: number;
  correlation: number;
  momentum_rank: number;
  volatility_rank: number;
  correlation_rank: number;
  total_score: number;
  selected: boolean;
  cash_proxy: boolean;
  hold_cash: boolean;
}

interface AllocationResultProps {
  scores: ScoreData[];
}

/**
 * AllocationResult Component
 *
 * Displays investment allocation results based on selected tickers.
 * Features:
 * - Investment amount input with USD formatting
 * - Equal weight distribution across selected tickers
 * - Per-ticker allocation display with $ amount and percentage
 * - LocalStorage integration for saving/loading investment amount
 * - Responsive design
 *
 * @example
 * <AllocationResult scores={scores} />
 */
export function AllocationResult({ scores }: AllocationResultProps) {
  const [investmentAmount, setInvestmentAmount] = useState<string>('');
  const [inputValue, setInputValue] = useState<string>('');

  // Get selected tickers from scores and categorize them
  const selectedScores = scores.filter(score => score.selected);

  // Build allocation map considering cash replacement
  const getAllocationTickers = () => {
    const tickers: string[] = [];

    for (const score of selectedScores) {
      if (score.hold_cash) {
        // Hold actual cash (0% return)
        tickers.push('CASH');
      } else if (score.cash_proxy) {
        // Replace with SHY
        tickers.push('SHY');
      } else {
        // Normal asset
        tickers.push(score.ticker);
      }
    }

    return tickers;
  };

  const allocationTickers = getAllocationTickers();

  // Load saved amount on mount
  useEffect(() => {
    const savedAmount = getAmount();
    if (savedAmount !== null) {
      setInvestmentAmount(savedAmount.toString());
      setInputValue(formatCurrency(savedAmount));
    }
  }, []);

  /**
   * Format number as USD currency
   * @param value - Number to format
   * @returns Formatted string (e.g., "$10,000.00")
   */
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  /**
   * Parse currency string to number
   * @param value - Currency string (e.g., "$10,000.00" or "10000")
   * @returns Parsed number
   */
  const parseCurrency = (value: string): number => {
    // Remove all non-numeric characters except decimal point
    const cleaned = value.replace(/[^0-9.]/g, '');
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
  };

  /**
   * Calculate allocation for each ticker
   * Uses equal weight distribution and consolidates duplicate tickers (e.g., multiple SHY or CASH)
   * @param amount - Total investment amount
   * @param tickers - Array of ticker symbols (may contain duplicates)
   * @returns Array of allocation objects
   */
  const calculateAllocation = (
    amount: number,
    tickers: string[]
  ): Array<{ ticker: string; amount: number; percentage: number }> => {
    if (tickers.length === 0 || amount <= 0) {
      return [];
    }

    const equalWeight = 100 / tickers.length;
    const amountPerTicker = amount / tickers.length;

    // Consolidate duplicate tickers
    const tickerMap = new Map<string, { count: number; amount: number }>();

    for (const ticker of tickers) {
      const existing = tickerMap.get(ticker);
      if (existing) {
        existing.count += 1;
        existing.amount += amountPerTicker;
      } else {
        tickerMap.set(ticker, { count: 1, amount: amountPerTicker });
      }
    }

    // Convert to array format
    const allocations = Array.from(tickerMap.entries()).map(([ticker, data]) => ({
      ticker,
      amount: data.amount,
      percentage: equalWeight * data.count,
    }));

    return allocations;
  };

  /**
   * Handle input change with currency formatting
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const numericValue = parseCurrency(value);

    setInputValue(value);
    setInvestmentAmount(numericValue.toString());
  };

  /**
   * Handle input blur - format and save to localStorage
   */
  const handleInputBlur = () => {
    const numericValue = parseCurrency(inputValue);

    if (numericValue > 0) {
      setInputValue(formatCurrency(numericValue));
      saveAmount(numericValue);
    } else {
      setInputValue('');
      setInvestmentAmount('');
    }
  };

  /**
   * Handle input focus - remove formatting for easier editing
   */
  const handleInputFocus = () => {
    const numericValue = parseCurrency(inputValue);
    if (numericValue > 0) {
      setInputValue(numericValue.toString());
    }
  };

  // Calculate allocations
  const amount = parseFloat(investmentAmount) || 0;
  const allocations = calculateAllocation(amount, allocationTickers);

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Investment Amount Input */}
      <div className="space-y-2">
        <label
          htmlFor="investment-amount"
          className="text-sm font-medium text-foreground"
        >
          투자 금액
        </label>
        <div className="relative">
          <input
            id="investment-amount"
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onBlur={handleInputBlur}
            onFocus={handleInputFocus}
            placeholder="$10,000"
            className={cn(
              "w-full px-4 py-3 text-lg font-semibold",
              "border border-border rounded-md",
              "bg-background text-foreground",
              "placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
              "transition-colors duration-200"
            )}
            aria-label="Investment amount in USD"
          />
        </div>
        <p className="text-xs text-muted-foreground">
          투자하고자 하는 총 금액을 USD로 입력하세요
        </p>
      </div>

      {/* Allocation Results */}
      {amount > 0 && allocationTickers.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-foreground">
              자산 배분
            </h3>
            <span className="text-sm text-muted-foreground">
              {selectedScores.length}개 포지션 ({allocations.length}개 자산)
            </span>
          </div>

          {/* Allocation List */}
          <div className="space-y-3">
            {allocations.map((allocation, index) => (
              <div
                key={allocation.ticker}
                className={cn(
                  "flex items-center justify-between p-4 rounded-lg",
                  "bg-secondary/50 border border-border",
                  "transition-all duration-200 hover:bg-secondary/80"
                )}
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary text-sm font-semibold">
                    {index + 1}
                  </div>
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-semibold text-foreground">
                        {allocation.ticker}
                      </span>
                      {allocation.ticker === 'CASH' && (
                        <span className="text-xs px-2 py-0.5 rounded bg-destructive/10 text-destructive font-medium">
                          현금보유
                        </span>
                      )}
                      {allocation.ticker === 'SHY' && (
                        <span className="text-xs px-2 py-0.5 rounded bg-secondary text-secondary-foreground font-medium">
                          현금대용
                        </span>
                      )}
                    </div>
                    {allocation.ticker !== 'CASH' && (() => {
                      // Find the price info for this allocation
                      let tickerScore;

                      if (allocation.ticker === 'SHY') {
                        // For SHY, look in all scores (not just selected)
                        tickerScore = scores.find(s => s.ticker === 'SHY');
                      } else {
                        // For other tickers, find from selected scores
                        tickerScore = selectedScores.find(s =>
                          !s.cash_proxy && !s.hold_cash && s.ticker === allocation.ticker
                        );
                      }

                      if (!tickerScore) return null;

                      const shares = allocation.amount / tickerScore.current_price;
                      return (
                        <div className="flex flex-col gap-0.5">
                          <span className="text-xs text-muted-foreground">
                            현재가: ${tickerScore.current_price.toFixed(2)}
                          </span>
                          <span className="text-xs font-medium text-primary">
                            {shares.toFixed(4)} 주
                          </span>
                        </div>
                      );
                    })()}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-lg font-bold text-foreground">
                    {formatCurrency(allocation.amount)}
                  </span>
                  <span className="text-sm font-medium text-muted-foreground min-w-[4rem] text-right">
                    ({allocation.percentage.toFixed(2)}%)
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Total Summary */}
          <div className="pt-4 border-t border-border">
            <div className="flex items-center justify-between p-4 bg-primary/5 rounded-lg">
              <span className="text-sm font-semibold text-foreground">
                총 투자금액
              </span>
              <span className="text-xl font-bold text-primary">
                {formatCurrency(amount)}
              </span>
            </div>
          </div>

          {/* Info Message */}
          <div className="p-3 bg-muted/50 rounded-md space-y-1">
            <p className="text-xs text-muted-foreground text-center">
              균등 배분: 포지션당 {formatCurrency(amount / selectedScores.length)}
            </p>
            {allocationTickers.includes('CASH') && (
              <p className="text-xs text-destructive text-center font-medium">
                ⚠️ 현금보유: SHY도 마이너스 모멘텀이므로 일부 자금을 현금으로 보유합니다
              </p>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {amount <= 0 && (
        <div className="text-center py-8">
          <p className="text-sm text-muted-foreground">
            투자 금액을 입력하면 자산 배분을 확인할 수 있습니다
          </p>
        </div>
      )}

      {/* No Tickers State */}
      {allocationTickers.length === 0 && amount > 0 && (
        <div className="text-center py-8">
          <p className="text-sm text-muted-foreground">
            선택된 티커가 없습니다. 티커를 선택하면 자산 배분을 확인할 수 있습니다.
          </p>
        </div>
      )}
    </div>
  );
}

export default AllocationResult;
