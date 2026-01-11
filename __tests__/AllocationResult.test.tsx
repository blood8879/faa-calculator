/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AllocationResult } from '@/components/AllocationResult';
import * as localStorage from '@/lib/localStorage';

// Mock localStorage utilities
jest.mock('@/lib/localStorage', () => ({
  getAmount: jest.fn(),
  saveAmount: jest.fn(),
  getPortfolio: jest.fn(),
  savePortfolio: jest.fn(),
}));

describe('AllocationResult', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial Render', () => {
    it('should render investment amount input field', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i);
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('placeholder', '$10,000');
    });

    it('should show empty state when no amount is entered', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText(/enter an investment amount to see allocation/i)).toBeInTheDocument();
    });

    it('should load saved amount from localStorage on mount', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i) as HTMLInputElement;
      expect(input.value).toBe('$10,000.00');
    });

    it('should use default tickers when no portfolio is saved', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(null);

      render(<AllocationResult />);

      expect(screen.getByText(/3 tickers/i)).toBeInTheDocument();
    });

    it('should load saved portfolio from localStorage', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO', 'SHY']);

      render(<AllocationResult />);

      expect(screen.getByText(/4 tickers/i)).toBeInTheDocument();
    });
  });

  describe('Investment Amount Input', () => {
    it('should update input value when user types', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i) as HTMLInputElement;
      fireEvent.change(input, { target: { value: '5000' } });

      expect(input.value).toBe('5000');
    });

    it('should format currency on blur', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i) as HTMLInputElement;
      fireEvent.change(input, { target: { value: '5000' } });
      fireEvent.blur(input);

      expect(input.value).toBe('$5,000.00');
    });

    it('should remove formatting on focus', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i) as HTMLInputElement;
      fireEvent.focus(input);

      expect(input.value).toBe('10000');
    });

    it('should save amount to localStorage on blur', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);
      (localStorage.saveAmount as jest.Mock).mockReturnValue(true);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i);
      fireEvent.change(input, { target: { value: '5000' } });
      fireEvent.blur(input);

      expect(localStorage.saveAmount).toHaveBeenCalledWith(5000);
    });

    it('should handle currency symbols in input', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i) as HTMLInputElement;
      fireEvent.change(input, { target: { value: '$5,000.00' } });
      fireEvent.blur(input);

      expect(input.value).toBe('$5,000.00');
      expect(localStorage.saveAmount).toHaveBeenCalledWith(5000);
    });

    it('should handle invalid input gracefully', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i) as HTMLInputElement;
      fireEvent.change(input, { target: { value: 'abc' } });
      fireEvent.blur(input);

      expect(input.value).toBe('');
    });
  });

  describe('Allocation Calculation', () => {
    it('should display equal weight allocation for 3 tickers', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText('VTI')).toBeInTheDocument();
      expect(screen.getByText('VEA')).toBeInTheDocument();
      expect(screen.getByText('VWO')).toBeInTheDocument();

      // Each should have 33.33%
      const percentages = screen.getAllByText(/\(33\.33%\)/i);
      expect(percentages).toHaveLength(3);
    });

    it('should display correct dollar amounts', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      // Check if amounts are displayed (amounts should sum to $10,000)
      const amounts = screen.getAllByText(/\$3,333/);
      expect(amounts.length).toBeGreaterThan(0);
    });

    it('should ensure total equals investment amount', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      // Total should be displayed
      expect(screen.getByText('$10,000.00')).toBeInTheDocument();
    });

    it('should handle single ticker allocation', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(5000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI']);

      render(<AllocationResult />);

      expect(screen.getByText('VTI')).toBeInTheDocument();
      expect(screen.getByText(/\(100\.00%\)/i)).toBeInTheDocument();
      expect(screen.getByText('$5,000.00')).toBeInTheDocument();
    });

    it('should handle 7 tickers (FAA maximum)', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue([
        'VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'
      ]);

      render(<AllocationResult />);

      expect(screen.getByText(/7 tickers/i)).toBeInTheDocument();

      // Each should have ~14.29%
      const percentages = screen.getAllByText(/\(14\.29%\)/i);
      expect(percentages).toHaveLength(7);
    });

    it('should update allocation when amount changes', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      const { rerender } = render(<AllocationResult />);

      // Change amount
      const input = screen.getByLabelText(/investment amount/i);
      fireEvent.change(input, { target: { value: '15000' } });
      fireEvent.blur(input);

      // Wait for update
      waitFor(() => {
        expect(screen.getByText('$15,000.00')).toBeInTheDocument();
      });
    });
  });

  describe('Display and Formatting', () => {
    it('should format currency with thousand separators', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(100000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText('$100,000.00')).toBeInTheDocument();
    });

    it('should display ticker count', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA']);

      render(<AllocationResult />);

      expect(screen.getByText(/2 tickers/i)).toBeInTheDocument();
    });

    it('should display allocation heading', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText('Allocation')).toBeInTheDocument();
    });

    it('should display equal weight info message', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText(/equal weight distribution/i)).toBeInTheDocument();
    });

    it('should display numbered indicators for each ticker', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle zero amount', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(0);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText(/enter an investment amount to see allocation/i)).toBeInTheDocument();
    });

    it('should handle negative amount gracefully', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i);
      fireEvent.change(input, { target: { value: '-1000' } });
      fireEvent.blur(input);

      // Should clear invalid input
      expect((input as HTMLInputElement).value).toBe('');
    });

    it('should handle empty ticker array', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(10000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue([]);

      render(<AllocationResult />);

      expect(screen.getByText(/no tickers selected/i)).toBeInTheDocument();
    });

    it('should handle very large amounts', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(1000000);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText('$1,000,000.00')).toBeInTheDocument();
    });

    it('should handle decimal amounts', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount/i);
      fireEvent.change(input, { target: { value: '10000.50' } });
      fireEvent.blur(input);

      expect((input as HTMLInputElement).value).toBe('$10,000.50');
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria-label for input', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const input = screen.getByLabelText(/investment amount in usd/i);
      expect(input).toBeInTheDocument();
    });

    it('should have proper label association', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      const label = screen.getByText('Investment Amount');
      expect(label).toHaveAttribute('for', 'investment-amount');
    });

    it('should have descriptive helper text', () => {
      (localStorage.getAmount as jest.Mock).mockReturnValue(null);
      (localStorage.getPortfolio as jest.Mock).mockReturnValue(['VTI', 'VEA', 'VWO']);

      render(<AllocationResult />);

      expect(screen.getByText(/enter the total amount you want to invest in usd/i)).toBeInTheDocument();
    });
  });
});
