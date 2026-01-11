'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Check, X, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

// Default tickers as specified
const DEFAULT_TICKERS = ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'];

// Validation states
type ValidationState = 'empty' | 'validating' | 'valid' | 'invalid';

interface TickerData {
  value: string;
  state: ValidationState;
  name?: string;
  exchange?: string;
}

interface TickerInputProps {
  onValidationComplete?: (tickers: string[], allValid: boolean) => void;
}

export default function TickerInput({ onValidationComplete }: TickerInputProps) {
  const [tickers, setTickers] = useState<TickerData[]>(
    Array(7).fill(null).map(() => ({
      value: '',
      state: 'empty' as ValidationState,
    }))
  );

  // Debounce timers
  const debounceTimers = React.useRef<NodeJS.Timeout[]>([]);

  // Validate a single ticker
  const validateTicker = async (ticker: string, index: number) => {
    if (!ticker.trim()) {
      updateTickerState(index, { state: 'empty' });
      return;
    }

    // Set validating state
    updateTickerState(index, { state: 'validating' });

    try {
      const response = await fetch('/api/validate_ticker', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticker: ticker.toUpperCase().trim() }),
      });

      const data = await response.json();

      if (data.valid) {
        updateTickerState(index, {
          state: 'valid',
          name: data.name,
          exchange: data.exchange,
        });
      } else {
        updateTickerState(index, { state: 'invalid' });
      }
    } catch (error) {
      console.error('Validation error:', error);
      updateTickerState(index, { state: 'invalid' });
    }
  };

  // Update ticker state
  const updateTickerState = (index: number, updates: Partial<TickerData>) => {
    setTickers((prev) =>
      prev.map((ticker, i) =>
        i === index ? { ...ticker, ...updates } : ticker
      )
    );
  };

  // Handle input change with debounce
  const handleInputChange = (index: number, value: string) => {
    // Clear existing timer for this index
    if (debounceTimers.current[index]) {
      clearTimeout(debounceTimers.current[index]);
    }

    // Update value immediately
    updateTickerState(index, { value, state: value.trim() ? 'validating' : 'empty' });

    // Set debounce timer (300ms)
    if (value.trim()) {
      debounceTimers.current[index] = setTimeout(() => {
        validateTicker(value, index);
      }, 300);
    }
  };

  // Fill with default tickers
  const fillDefaults = () => {
    console.log('Fill defaults button clicked!');
    console.log('Default tickers:', DEFAULT_TICKERS);

    const defaultTickerData = DEFAULT_TICKERS.map((ticker) => ({
      value: ticker,
      state: 'validating' as ValidationState,
    }));

    setTickers(defaultTickerData);

    // Validate all defaults
    DEFAULT_TICKERS.forEach((ticker, index) => {
      setTimeout(() => validateTicker(ticker, index), 300);
    });
  };

  // Check if all tickers are valid
  const allValid = tickers.every((t) => t.state === 'valid');
  const validTickers = tickers
    .filter((t) => t.state === 'valid')
    .map((t) => t.value.toUpperCase().trim());

  // Notify parent component when validation state changes
  useEffect(() => {
    if (onValidationComplete) {
      onValidationComplete(validTickers, allValid);
    }
  }, [validTickers.length, allValid]);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      debounceTimers.current.forEach((timer) => {
        if (timer) clearTimeout(timer);
      });
    };
  }, []);

  // Get state indicator icon
  const getStateIndicator = (state: ValidationState) => {
    switch (state) {
      case 'validating':
        return <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />;
      case 'valid':
        return <Check className="h-4 w-4 text-success" />;
      case 'invalid':
        return <X className="h-4 w-4 text-destructive" />;
      default:
        return null;
    }
  };

  // Get border color based on state
  const getBorderColor = (state: ValidationState) => {
    switch (state) {
      case 'valid':
        return 'border-success focus-visible:ring-success';
      case 'invalid':
        return 'border-destructive focus-visible:ring-destructive';
      case 'validating':
        return 'border-muted-foreground/50';
      default:
        return '';
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Header with Fill Defaults button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">티커 입력</h2>
          <p className="text-sm text-muted-foreground mt-1">
            FAA 스코어를 계산하기 위해 7개의 티커 심볼을 입력하세요
          </p>
        </div>
        <Button
          onClick={fillDefaults}
          variant="outline"
          size="sm"
          className="shrink-0"
        >
          기본값 채우기
        </Button>
      </div>

      {/* Ticker inputs grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {tickers.map((ticker, index) => (
          <div key={index} className="space-y-2">
            <label
              htmlFor={`ticker-${index}`}
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              티커 {index + 1}
            </label>
            <div className="relative">
              <Input
                id={`ticker-${index}`}
                type="text"
                placeholder="e.g., VTI"
                value={ticker.value}
                onChange={(e) => handleInputChange(index, e.target.value)}
                className={cn(
                  'uppercase pr-10',
                  getBorderColor(ticker.state)
                )}
                maxLength={10}
                aria-label={`Ticker symbol ${index + 1}`}
                aria-invalid={ticker.state === 'invalid'}
                aria-describedby={
                  ticker.state === 'valid' && ticker.name
                    ? `ticker-${index}-name`
                    : undefined
                }
              />
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                {getStateIndicator(ticker.state)}
              </div>
            </div>
            {/* Display ticker name when valid */}
            {ticker.state === 'valid' && ticker.name && (
              <p
                id={`ticker-${index}-name`}
                className="text-xs text-muted-foreground line-clamp-1"
                title={ticker.name}
              >
                {ticker.name}
              </p>
            )}
            {/* Display error message when invalid */}
            {ticker.state === 'invalid' && (
              <p className="text-xs text-destructive">
                유효하지 않은 티커
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Validation summary */}
      <div className="flex items-center justify-between p-4 border rounded-lg bg-muted/50">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">
            유효한 티커: {validTickers.length} / 7
          </span>
        </div>
        {allValid && (
          <div className="flex items-center gap-2 text-success">
            <Check className="h-4 w-4" />
            <span className="text-sm font-medium">모든 티커 검증 완료</span>
          </div>
        )}
      </div>
    </div>
  );
}
