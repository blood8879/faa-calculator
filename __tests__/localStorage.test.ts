/**
 * Unit tests for localStorage utility
 *
 * Tests SSR safety, type validation, and CRUD operations
 */

import {
  getPortfolio,
  savePortfolio,
  getAmount,
  saveAmount,
  clearAll,
  __STORAGE_KEYS__,
} from '../lib/localStorage';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

describe('localStorage utility', () => {
  describe('SSR Safety', () => {
    it('should return null when window is undefined (SSR)', () => {
      // Simulate SSR environment
      const originalWindow = global.window;
      // @ts-ignore
      delete global.window;

      expect(getPortfolio()).toBeNull();
      expect(getAmount()).toBeNull();

      // Restore window
      global.window = originalWindow;
    });

    it('should return false when window is undefined (SSR) for save operations', () => {
      const originalWindow = global.window;
      // @ts-ignore
      delete global.window;

      expect(savePortfolio(['VTI'])).toBe(false);
      expect(saveAmount(10000)).toBe(false);
      expect(clearAll()).toBe(false);

      global.window = originalWindow;
    });
  });

  describe('Portfolio operations', () => {
    beforeEach(() => {
      // Setup mock localStorage
      Object.defineProperty(window, 'localStorage', {
        value: localStorageMock,
        writable: true,
      });
      localStorageMock.clear();
    });

    it('should save and retrieve portfolio tickers', () => {
      const tickers = ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'];

      const saveResult = savePortfolio(tickers);
      expect(saveResult).toBe(true);

      const retrieved = getPortfolio();
      expect(retrieved).toEqual(tickers);
    });

    it('should return null when portfolio is not saved', () => {
      const retrieved = getPortfolio();
      expect(retrieved).toBeNull();
    });

    it('should trim and uppercase ticker symbols', () => {
      const tickers = ['  vti  ', 'vea', 'VWO '];

      savePortfolio(tickers);

      const retrieved = getPortfolio();
      expect(retrieved).toEqual(['VTI', 'VEA', 'VWO']);
    });

    it('should filter out empty strings after trimming', () => {
      const tickers = ['VTI', '  ', 'VEA', ''];

      savePortfolio(tickers);

      const retrieved = getPortfolio();
      expect(retrieved).toEqual(['VTI', 'VEA']);
    });

    it('should reject non-array input', () => {
      // @ts-ignore - intentionally testing invalid input
      const result = savePortfolio('VTI');
      expect(result).toBe(false);
    });

    it('should reject array with non-string elements', () => {
      // @ts-ignore - intentionally testing invalid input
      const result = savePortfolio(['VTI', 123, 'VEA']);
      expect(result).toBe(false);
    });

    it('should handle corrupted localStorage data gracefully', () => {
      localStorageMock.setItem(__STORAGE_KEYS__.PORTFOLIO, 'invalid json');

      const retrieved = getPortfolio();
      expect(retrieved).toBeNull();
    });

    it('should handle invalid data type in localStorage', () => {
      localStorageMock.setItem(__STORAGE_KEYS__.PORTFOLIO, JSON.stringify('not an array'));

      const retrieved = getPortfolio();
      expect(retrieved).toBeNull();
    });
  });

  describe('Amount operations', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'localStorage', {
        value: localStorageMock,
        writable: true,
      });
      localStorageMock.clear();
    });

    it('should save and retrieve investment amount', () => {
      const amount = 10000;

      const saveResult = saveAmount(amount);
      expect(saveResult).toBe(true);

      const retrieved = getAmount();
      expect(retrieved).toBe(amount);
    });

    it('should return null when amount is not saved', () => {
      const retrieved = getAmount();
      expect(retrieved).toBeNull();
    });

    it('should save decimal amounts correctly', () => {
      const amount = 10000.50;

      saveAmount(amount);

      const retrieved = getAmount();
      expect(retrieved).toBe(amount);
    });

    it('should save zero amount', () => {
      const amount = 0;

      saveAmount(amount);

      const retrieved = getAmount();
      expect(retrieved).toBe(0);
    });

    it('should reject negative amounts', () => {
      const result = saveAmount(-1000);
      expect(result).toBe(false);
    });

    it('should reject NaN', () => {
      const result = saveAmount(NaN);
      expect(result).toBe(false);
    });

    it('should reject non-number input', () => {
      // @ts-ignore - intentionally testing invalid input
      const result = saveAmount('10000');
      expect(result).toBe(false);
    });

    it('should handle corrupted localStorage data gracefully', () => {
      localStorageMock.setItem(__STORAGE_KEYS__.AMOUNT, 'invalid json');

      const retrieved = getAmount();
      expect(retrieved).toBeNull();
    });

    it('should handle invalid data type in localStorage', () => {
      localStorageMock.setItem(__STORAGE_KEYS__.AMOUNT, JSON.stringify('not a number'));

      const retrieved = getAmount();
      expect(retrieved).toBeNull();
    });
  });

  describe('clearAll operation', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'localStorage', {
        value: localStorageMock,
        writable: true,
      });
      localStorageMock.clear();
    });

    it('should clear all saved data', () => {
      // Save portfolio and amount
      savePortfolio(['VTI', 'VEA', 'VWO']);
      saveAmount(10000);

      // Verify they are saved
      expect(getPortfolio()).not.toBeNull();
      expect(getAmount()).not.toBeNull();

      // Clear all
      const result = clearAll();
      expect(result).toBe(true);

      // Verify they are cleared
      expect(getPortfolio()).toBeNull();
      expect(getAmount()).toBeNull();
    });

    it('should succeed even when no data exists', () => {
      const result = clearAll();
      expect(result).toBe(true);
    });

    it('should only clear FAA calculator data, not other localStorage items', () => {
      // Save some non-FAA data
      localStorageMock.setItem('other_app_data', 'some value');

      // Save FAA data
      savePortfolio(['VTI']);
      saveAmount(5000);

      // Clear FAA data
      clearAll();

      // Verify FAA data is cleared but other data remains
      expect(getPortfolio()).toBeNull();
      expect(getAmount()).toBeNull();
      expect(localStorageMock.getItem('other_app_data')).toBe('some value');
    });
  });

  describe('Integration scenarios', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'localStorage', {
        value: localStorageMock,
        writable: true,
      });
      localStorageMock.clear();
    });

    it('should handle complete user workflow', () => {
      // User saves portfolio
      const tickers = ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'];
      expect(savePortfolio(tickers)).toBe(true);

      // User saves investment amount
      expect(saveAmount(10000)).toBe(true);

      // User retrieves data (page refresh)
      expect(getPortfolio()).toEqual(tickers);
      expect(getAmount()).toBe(10000);

      // User updates portfolio
      const newTickers = ['SPY', 'AGG', 'GLD'];
      expect(savePortfolio(newTickers)).toBe(true);
      expect(getPortfolio()).toEqual(newTickers);

      // User clears all data
      expect(clearAll()).toBe(true);
      expect(getPortfolio()).toBeNull();
      expect(getAmount()).toBeNull();
    });

    it('should allow independent updates of portfolio and amount', () => {
      // Save portfolio
      savePortfolio(['VTI', 'VEA']);
      saveAmount(5000);

      // Update only amount
      saveAmount(15000);

      // Portfolio should remain unchanged
      expect(getPortfolio()).toEqual(['VTI', 'VEA']);
      expect(getAmount()).toBe(15000);

      // Update only portfolio
      savePortfolio(['SPY']);

      // Amount should remain unchanged
      expect(getPortfolio()).toEqual(['SPY']);
      expect(getAmount()).toBe(15000);
    });
  });

  describe('Edge cases', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'localStorage', {
        value: localStorageMock,
        writable: true,
      });
      localStorageMock.clear();
    });

    it('should handle very large ticker arrays', () => {
      const largeTickers = Array(100).fill('VTI');

      const result = savePortfolio(largeTickers);
      expect(result).toBe(true);

      const retrieved = getPortfolio();
      expect(retrieved?.length).toBe(100);
    });

    it('should handle very large investment amounts', () => {
      const largeAmount = 999999999999;

      saveAmount(largeAmount);

      const retrieved = getAmount();
      expect(retrieved).toBe(largeAmount);
    });

    it('should handle Infinity as invalid amount', () => {
      const result = saveAmount(Infinity);
      expect(result).toBe(false);
    });

    it('should handle empty ticker array', () => {
      savePortfolio([]);

      const retrieved = getPortfolio();
      expect(retrieved).toEqual([]);
    });
  });
});
