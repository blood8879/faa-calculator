/**
 * Type definitions for FAA Calculator
 */

/**
 * Ticker validation state
 */
export type TickerState = 'empty' | 'validating' | 'valid' | 'invalid';

/**
 * Ticker validation result from API
 */
export interface TickerValidation {
  valid: boolean;
  name?: string;
  exchange?: string;
}

/**
 * Individual ticker's FAA score data
 */
export interface FAAScore {
  momentum: number;
  momentum_rank: number;
  volatility: number;
  volatility_rank: number;
  correlation: number;
  correlation_rank: number;
  integrated_score: number;
  selected: boolean;
  cash_replacement: boolean;
}

/**
 * Complete FAA scores response from API
 */
export interface FAAScoresData {
  [ticker: string]: FAAScore;
}

/**
 * Allocation result from API
 */
export interface AllocationData {
  [ticker: string]: number;
}

/**
 * Score API response
 */
export interface ScoreAPIResponse {
  success: boolean;
  scores?: FAAScoresData;
  allocation?: AllocationData;
  timestamp?: string;
  error?: string;
}

/**
 * Ticker input state
 */
export interface TickerInputState {
  value: string;
  state: TickerState;
  name?: string;
  exchange?: string;
}
