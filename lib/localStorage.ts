/**
 * LocalStorage Utility for FAA Calculator
 *
 * Provides type-safe localStorage operations with SSR compatibility.
 * All functions check for window object availability to prevent SSR errors.
 */

// Storage keys
const STORAGE_KEYS = {
  PORTFOLIO: 'faa_portfolio',
  AMOUNT: 'faa_investment_amount',
} as const;

/**
 * Type guard to check if we're in a browser environment
 */
const isBrowser = (): boolean => {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
};

/**
 * Get saved portfolio tickers from localStorage
 *
 * @returns Array of ticker symbols, or null if not found
 * @example
 * const tickers = getPortfolio(); // ['VTI', 'VEA', 'VWO', ...]
 */
export const getPortfolio = (): string[] | null => {
  if (!isBrowser()) {
    return null;
  }

  try {
    const stored = window.localStorage.getItem(STORAGE_KEYS.PORTFOLIO);
    if (!stored) {
      return null;
    }

    const parsed = JSON.parse(stored);

    // Validate that it's an array of strings
    if (Array.isArray(parsed) && parsed.every(item => typeof item === 'string')) {
      return parsed;
    }

    return null;
  } catch (error) {
    console.error('Error reading portfolio from localStorage:', error);
    return null;
  }
};

/**
 * Save portfolio tickers to localStorage
 *
 * @param tickers - Array of ticker symbols (max 7 for FAA strategy)
 * @returns true if saved successfully, false otherwise
 * @example
 * savePortfolio(['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ']);
 */
export const savePortfolio = (tickers: string[]): boolean => {
  if (!isBrowser()) {
    return false;
  }

  try {
    // Validate input
    if (!Array.isArray(tickers)) {
      throw new Error('Tickers must be an array');
    }

    if (tickers.some(ticker => typeof ticker !== 'string')) {
      throw new Error('All tickers must be strings');
    }

    // Trim and uppercase tickers
    const cleanedTickers = tickers
      .map(ticker => ticker.trim().toUpperCase())
      .filter(ticker => ticker.length > 0);

    window.localStorage.setItem(STORAGE_KEYS.PORTFOLIO, JSON.stringify(cleanedTickers));
    return true;
  } catch (error) {
    console.error('Error saving portfolio to localStorage:', error);
    return false;
  }
};

/**
 * Get saved investment amount from localStorage
 *
 * @returns Investment amount as number, or null if not found
 * @example
 * const amount = getAmount(); // 10000
 */
export const getAmount = (): number | null => {
  if (!isBrowser()) {
    return null;
  }

  try {
    const stored = window.localStorage.getItem(STORAGE_KEYS.AMOUNT);
    if (!stored) {
      return null;
    }

    const parsed = JSON.parse(stored);

    // Validate that it's a number
    if (typeof parsed === 'number' && !isNaN(parsed) && parsed >= 0) {
      return parsed;
    }

    return null;
  } catch (error) {
    console.error('Error reading amount from localStorage:', error);
    return null;
  }
};

/**
 * Save investment amount to localStorage
 *
 * @param amount - Investment amount in USD (must be positive)
 * @returns true if saved successfully, false otherwise
 * @example
 * saveAmount(10000);
 */
export const saveAmount = (amount: number): boolean => {
  if (!isBrowser()) {
    return false;
  }

  try {
    // Validate input
    if (typeof amount !== 'number' || isNaN(amount)) {
      throw new Error('Amount must be a valid number');
    }

    if (amount < 0) {
      throw new Error('Amount must be positive');
    }

    window.localStorage.setItem(STORAGE_KEYS.AMOUNT, JSON.stringify(amount));
    return true;
  } catch (error) {
    console.error('Error saving amount to localStorage:', error);
    return false;
  }
};

/**
 * Clear all FAA calculator data from localStorage
 *
 * @returns true if cleared successfully, false otherwise
 * @example
 * clearAll();
 */
export const clearAll = (): boolean => {
  if (!isBrowser()) {
    return false;
  }

  try {
    window.localStorage.removeItem(STORAGE_KEYS.PORTFOLIO);
    window.localStorage.removeItem(STORAGE_KEYS.AMOUNT);
    return true;
  } catch (error) {
    console.error('Error clearing localStorage:', error);
    return false;
  }
};

/**
 * Export storage keys for testing purposes
 */
export const __STORAGE_KEYS__ = STORAGE_KEYS;
