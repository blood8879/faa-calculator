"""
Unit tests for FAA Calculator Module

Test coverage:
- Momentum calculation accuracy
- Volatility calculation accuracy
- Correlation calculation accuracy
- FAA score ranking logic
- Integrated score formula
- Top 3 selection
- Absolute momentum filter
- Allocation calculation
- Error handling and edge cases
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from api.faa_calculator import (
    calculate_momentum,
    calculate_volatility,
    calculate_correlation,
    calculate_faa_scores,
    get_selected_tickers,
    get_allocation
)


class TestMomentumCalculation(unittest.TestCase):
    """Test momentum calculation function."""

    @patch('api.faa_calculator.yf.download')
    def test_positive_momentum(self, mock_download):
        """Test momentum calculation with price increase."""
        # Create mock data: price goes from 100 to 120 over 80 days
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')
        prices = np.linspace(100, 120, 80)
        mock_data = pd.DataFrame({
            'Close': prices
        }, index=dates)
        mock_download.return_value = mock_data

        momentum = calculate_momentum('VTI')

        # Expected: (120 / 100) - 1 = 0.20 (20% gain)
        self.assertAlmostEqual(momentum, 0.20, places=2)
        mock_download.assert_called_once()

    @patch('api.faa_calculator.yf.download')
    def test_negative_momentum(self, mock_download):
        """Test momentum calculation with price decrease."""
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')
        prices = np.linspace(100, 80, 80)
        mock_data = pd.DataFrame({
            'Close': prices
        }, index=dates)
        mock_download.return_value = mock_data

        momentum = calculate_momentum('VTI')

        # Expected: (80 / 100) - 1 = -0.20 (20% loss)
        self.assertAlmostEqual(momentum, -0.20, places=2)

    @patch('api.faa_calculator.yf.download')
    def test_zero_momentum(self, mock_download):
        """Test momentum calculation with no price change."""
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')
        prices = np.full(80, 100)
        mock_data = pd.DataFrame({
            'Close': prices
        }, index=dates)
        mock_download.return_value = mock_data

        momentum = calculate_momentum('VTI')

        # Expected: (100 / 100) - 1 = 0.0
        self.assertAlmostEqual(momentum, 0.0, places=2)

    @patch('api.faa_calculator.yf.download')
    def test_insufficient_data(self, mock_download):
        """Test error handling with insufficient data."""
        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        prices = np.linspace(100, 120, 50)
        mock_data = pd.DataFrame({
            'Close': prices
        }, index=dates)
        mock_download.return_value = mock_data

        with self.assertRaises(ValueError) as context:
            calculate_momentum('VTI')

        self.assertIn("Insufficient data", str(context.exception))

    @patch('api.faa_calculator.yf.download')
    def test_no_data(self, mock_download):
        """Test error handling with no data."""
        mock_download.return_value = pd.DataFrame()

        with self.assertRaises(ValueError) as context:
            calculate_momentum('INVALID')

        self.assertIn("No data available", str(context.exception))


class TestVolatilityCalculation(unittest.TestCase):
    """Test volatility calculation function."""

    @patch('api.faa_calculator.yf.download')
    def test_volatility_calculation(self, mock_download):
        """Test volatility calculation with known data."""
        # Create data with controlled volatility
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 80)
        prices = 100 * (1 + returns).cumprod()

        mock_data = pd.DataFrame({
            'Close': prices
        }, index=dates)
        mock_download.return_value = mock_data

        volatility = calculate_volatility('VTI')

        # Volatility should be a positive number
        self.assertGreater(volatility, 0)
        self.assertLess(volatility, 1)  # Should be reasonable range

    @patch('api.faa_calculator.yf.download')
    def test_zero_volatility(self, mock_download):
        """Test volatility with constant prices."""
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')
        prices = np.full(80, 100)
        mock_data = pd.DataFrame({
            'Close': prices
        }, index=dates)
        mock_download.return_value = mock_data

        volatility = calculate_volatility('VTI')

        # Constant prices should give zero volatility
        self.assertAlmostEqual(volatility, 0.0, places=6)

    @patch('api.faa_calculator.yf.download')
    def test_high_volatility(self, mock_download):
        """Test volatility with highly volatile prices."""
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')
        # Create alternating high/low prices
        prices = [100 if i % 2 == 0 else 90 for i in range(80)]
        mock_data = pd.DataFrame({
            'Close': prices
        }, index=dates)
        mock_download.return_value = mock_data

        volatility = calculate_volatility('VTI')

        # Should have high volatility
        self.assertGreater(volatility, 0.05)

    @patch('api.faa_calculator.yf.download')
    def test_volatility_insufficient_data(self, mock_download):
        """Test error handling with insufficient data."""
        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        prices = np.linspace(100, 120, 50)
        mock_data = pd.DataFrame({
            'Close': prices
        }, index=dates)
        mock_download.return_value = mock_data

        with self.assertRaises(ValueError):
            calculate_volatility('VTI')


class TestCorrelationCalculation(unittest.TestCase):
    """Test correlation calculation function."""

    @patch('api.faa_calculator.yf.download')
    def test_perfect_correlation(self, mock_download):
        """Test correlation with perfectly correlated assets."""
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')
        prices1 = np.linspace(100, 120, 80)
        prices2 = np.linspace(50, 60, 80)

        mock_data = pd.DataFrame({
            ('Close', 'VTI'): prices1,
            ('Close', 'VEA'): prices2
        }, index=dates)
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        mock_download.return_value = mock_data

        correlations = calculate_correlation(['VTI', 'VEA'])

        # Perfect positive correlation should give sum close to 1.0
        self.assertAlmostEqual(correlations['VTI'], 1.0, places=1)
        self.assertAlmostEqual(correlations['VEA'], 1.0, places=1)

    @patch('api.faa_calculator.yf.download')
    def test_negative_correlation(self, mock_download):
        """Test correlation with negatively correlated assets."""
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')

        # Create prices with actual negative correlation in returns
        # Use sine waves that are out of phase
        np.random.seed(42)
        t = np.linspace(0, 4*np.pi, 80)
        prices1 = 100 * (1 + 0.1 * np.sin(t))
        prices2 = 100 * (1 + 0.1 * np.sin(t + np.pi))  # 180 degrees out of phase

        mock_data = pd.DataFrame({
            ('Close', 'VTI'): prices1,
            ('Close', 'VEA'): prices2
        }, index=dates)
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        mock_download.return_value = mock_data

        correlations = calculate_correlation(['VTI', 'VEA'])

        # With sine waves 180 degrees out of phase, correlation should be negative
        self.assertLess(correlations['VTI'], 0)
        self.assertLess(correlations['VEA'], 0)

    @patch('api.faa_calculator.yf.download')
    def test_multiple_tickers(self, mock_download):
        """Test correlation with multiple tickers."""
        dates = pd.date_range(end=datetime.now(), periods=80, freq='D')
        np.random.seed(42)

        # Create correlated returns
        base_returns = np.random.normal(0.001, 0.02, 80)
        prices = {}
        for ticker in ['VTI', 'VEA', 'VWO']:
            noise = np.random.normal(0, 0.01, 80)
            returns = base_returns + noise
            prices[('Close', ticker)] = 100 * (1 + returns).cumprod()

        mock_data = pd.DataFrame(prices, index=dates)
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        mock_download.return_value = mock_data

        correlations = calculate_correlation(['VTI', 'VEA', 'VWO'])

        # Each should have correlation sum > 0 (positively correlated)
        self.assertGreater(correlations['VTI'], 0)
        self.assertGreater(correlations['VEA'], 0)
        self.assertGreater(correlations['VWO'], 0)

    def test_insufficient_tickers(self):
        """Test error with insufficient tickers."""
        with self.assertRaises(ValueError) as context:
            calculate_correlation(['VTI'])

        self.assertIn("at least 2 tickers", str(context.exception))

    def test_empty_tickers(self):
        """Test error with empty tickers list."""
        with self.assertRaises(ValueError):
            calculate_correlation([])


class TestFAAScoresCalculation(unittest.TestCase):
    """Test complete FAA score calculation."""

    @patch('api.faa_calculator.calculate_correlation')
    @patch('api.faa_calculator.calculate_volatility')
    @patch('api.faa_calculator.calculate_momentum')
    def test_ranking_logic(self, mock_momentum, mock_volatility, mock_correlation):
        """Test that ranking logic works correctly."""
        tickers = ['A', 'B', 'C']

        # Mock momentum: A=0.15, B=0.10, C=0.05 -> Ranks: A=1, B=2, C=3
        mock_momentum.side_effect = [0.15, 0.10, 0.05]

        # Mock volatility: A=0.02, B=0.01, C=0.03 -> Ranks: B=1, A=2, C=3
        mock_volatility.side_effect = [0.02, 0.01, 0.03]

        # Mock correlation: A=2.0, B=1.5, C=1.0 -> Ranks: C=1, B=2, A=3
        mock_correlation.return_value = {'A': 2.0, 'B': 1.5, 'C': 1.0}

        scores = calculate_faa_scores(tickers)

        # Verify momentum ranks
        self.assertEqual(scores['A']['momentum_rank'], 1)
        self.assertEqual(scores['B']['momentum_rank'], 2)
        self.assertEqual(scores['C']['momentum_rank'], 3)

        # Verify volatility ranks
        self.assertEqual(scores['B']['volatility_rank'], 1)
        self.assertEqual(scores['A']['volatility_rank'], 2)
        self.assertEqual(scores['C']['volatility_rank'], 3)

        # Verify correlation ranks
        self.assertEqual(scores['C']['correlation_rank'], 1)
        self.assertEqual(scores['B']['correlation_rank'], 2)
        self.assertEqual(scores['A']['correlation_rank'], 3)

    @patch('api.faa_calculator.calculate_correlation')
    @patch('api.faa_calculator.calculate_volatility')
    @patch('api.faa_calculator.calculate_momentum')
    def test_integrated_score_formula(self, mock_momentum, mock_volatility, mock_correlation):
        """Test integrated score formula: M_rank * 1.0 + V_rank * 0.5 + C_rank * 0.5"""
        tickers = ['A', 'B', 'C']

        mock_momentum.side_effect = [0.15, 0.10, 0.05]  # Ranks: 1, 2, 3
        mock_volatility.side_effect = [0.02, 0.01, 0.03]  # Ranks: 2, 1, 3
        mock_correlation.return_value = {'A': 2.0, 'B': 1.5, 'C': 1.0}  # Ranks: 3, 2, 1

        scores = calculate_faa_scores(tickers)

        # A: 1*1.0 + 2*0.5 + 3*0.5 = 1.0 + 1.0 + 1.5 = 3.5
        self.assertAlmostEqual(scores['A']['integrated_score'], 3.5, places=2)

        # B: 2*1.0 + 1*0.5 + 2*0.5 = 2.0 + 0.5 + 1.0 = 3.5
        self.assertAlmostEqual(scores['B']['integrated_score'], 3.5, places=2)

        # C: 3*1.0 + 3*0.5 + 1*0.5 = 3.0 + 1.5 + 0.5 = 5.0
        self.assertAlmostEqual(scores['C']['integrated_score'], 5.0, places=2)

    @patch('api.faa_calculator.calculate_correlation')
    @patch('api.faa_calculator.calculate_volatility')
    @patch('api.faa_calculator.calculate_momentum')
    def test_top_3_selection(self, mock_momentum, mock_volatility, mock_correlation):
        """Test that top 3 tickers by integrated score are selected."""
        tickers = ['A', 'B', 'C', 'D', 'E']

        # Create scores that will result in clear ranking
        mock_momentum.side_effect = [0.20, 0.15, 0.10, 0.05, 0.02]
        mock_volatility.side_effect = [0.01, 0.02, 0.03, 0.04, 0.05]
        mock_correlation.return_value = {
            'A': 1.0, 'B': 1.5, 'C': 2.0, 'D': 2.5, 'E': 3.0
        }

        scores = calculate_faa_scores(tickers)

        # Count selected
        selected_count = sum(1 for data in scores.values() if data['selected'])
        self.assertEqual(selected_count, 3)

        # Get selected tickers
        selected = [t for t, d in scores.items() if d['selected']]
        self.assertEqual(len(selected), 3)

    @patch('api.faa_calculator.calculate_correlation')
    @patch('api.faa_calculator.calculate_volatility')
    @patch('api.faa_calculator.calculate_momentum')
    def test_absolute_momentum_filter(self, mock_momentum, mock_volatility, mock_correlation):
        """Test that negative momentum triggers cash replacement flag."""
        tickers = ['A', 'B', 'C']

        # A has negative momentum
        mock_momentum.side_effect = [-0.05, 0.10, 0.15]
        mock_volatility.side_effect = [0.01, 0.02, 0.03]
        mock_correlation.return_value = {'A': 1.0, 'B': 1.5, 'C': 2.0}

        scores = calculate_faa_scores(tickers)

        # Check if A is selected and has cash_replacement flag
        if scores['A']['selected']:
            self.assertTrue(scores['A']['cash_replacement'])

        # B and C should not have cash replacement (positive momentum)
        if scores['B']['selected']:
            self.assertFalse(scores['B']['cash_replacement'])
        if scores['C']['selected']:
            self.assertFalse(scores['C']['cash_replacement'])

    def test_empty_tickers(self):
        """Test error with empty tickers."""
        with self.assertRaises(ValueError) as context:
            calculate_faa_scores([])

        self.assertIn("cannot be empty", str(context.exception))

    def test_insufficient_tickers(self):
        """Test error with less than 3 tickers."""
        with self.assertRaises(ValueError) as context:
            calculate_faa_scores(['A', 'B'])

        self.assertIn("at least 3 tickers", str(context.exception))


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions."""

    def test_get_selected_tickers(self):
        """Test extraction of selected tickers."""
        faa_scores = {
            'A': {'selected': True},
            'B': {'selected': False},
            'C': {'selected': True},
            'D': {'selected': True}
        }

        selected = get_selected_tickers(faa_scores)

        self.assertEqual(len(selected), 3)
        self.assertIn('A', selected)
        self.assertIn('C', selected)
        self.assertIn('D', selected)
        self.assertNotIn('B', selected)

    def test_get_allocation_equal_weight(self):
        """Test equal weight allocation."""
        faa_scores = {
            'A': {'selected': True, 'cash_replacement': False},
            'B': {'selected': True, 'cash_replacement': False},
            'C': {'selected': True, 'cash_replacement': False},
            'D': {'selected': False, 'cash_replacement': False}
        }

        allocation = get_allocation(faa_scores, 10000)

        # Each should get 1/3 of total
        self.assertAlmostEqual(allocation['A'], 3333.33, places=2)
        self.assertAlmostEqual(allocation['B'], 3333.33, places=2)
        self.assertAlmostEqual(allocation['C'], 3333.33, places=2)
        self.assertEqual(len(allocation), 3)

    def test_get_allocation_with_cash_replacement(self):
        """Test allocation with cash replacement."""
        faa_scores = {
            'A': {'selected': True, 'cash_replacement': True},  # Replace with cash
            'B': {'selected': True, 'cash_replacement': False},
            'C': {'selected': True, 'cash_replacement': False},
            'D': {'selected': False, 'cash_replacement': False}
        }

        allocation = get_allocation(faa_scores, 9000, cash_ticker='SHY')

        # A should be replaced with SHY
        self.assertNotIn('A', allocation)
        self.assertIn('SHY', allocation)
        self.assertAlmostEqual(allocation['SHY'], 3000.00, places=2)
        self.assertAlmostEqual(allocation['B'], 3000.00, places=2)
        self.assertAlmostEqual(allocation['C'], 3000.00, places=2)

    def test_get_allocation_multiple_cash_replacements(self):
        """Test allocation with multiple cash replacements."""
        faa_scores = {
            'A': {'selected': True, 'cash_replacement': True},
            'B': {'selected': True, 'cash_replacement': True},
            'C': {'selected': True, 'cash_replacement': False}
        }

        allocation = get_allocation(faa_scores, 9000, cash_ticker='SHY')

        # A and B should both be replaced with SHY (combined)
        self.assertAlmostEqual(allocation['SHY'], 6000.00, places=2)
        self.assertAlmostEqual(allocation['C'], 3000.00, places=2)
        self.assertEqual(len(allocation), 2)

    def test_get_allocation_invalid_amount(self):
        """Test error with invalid investment amount."""
        faa_scores = {
            'A': {'selected': True, 'cash_replacement': False}
        }

        with self.assertRaises(ValueError) as context:
            get_allocation(faa_scores, -1000)

        self.assertIn("must be positive", str(context.exception))

    def test_get_allocation_no_selection(self):
        """Test error with no selected tickers."""
        faa_scores = {
            'A': {'selected': False, 'cash_replacement': False},
            'B': {'selected': False, 'cash_replacement': False}
        }

        with self.assertRaises(ValueError) as context:
            get_allocation(faa_scores, 10000)

        self.assertIn("No tickers selected", str(context.exception))


class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world integration scenarios."""

    @patch('api.faa_calculator.calculate_correlation')
    @patch('api.faa_calculator.calculate_volatility')
    @patch('api.faa_calculator.calculate_momentum')
    def test_full_faa_workflow(self, mock_momentum, mock_volatility, mock_correlation):
        """Test complete FAA workflow from calculation to allocation."""
        tickers = ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ']

        # Mock data for 7 tickers
        mock_momentum.side_effect = [0.15, 0.12, 0.08, 0.02, 0.03, -0.05, 0.10]
        mock_volatility.side_effect = [0.15, 0.18, 0.22, 0.05, 0.08, 0.25, 0.20]
        mock_correlation.return_value = {
            'VTI': 3.5, 'VEA': 3.8, 'VWO': 4.0, 'SHY': 1.0,
            'BND': 1.5, 'GSG': 2.0, 'VNQ': 3.0
        }

        # Calculate scores
        scores = calculate_faa_scores(tickers)

        # Verify structure
        for ticker in tickers:
            self.assertIn('momentum', scores[ticker])
            self.assertIn('volatility', scores[ticker])
            self.assertIn('correlation', scores[ticker])
            self.assertIn('momentum_rank', scores[ticker])
            self.assertIn('volatility_rank', scores[ticker])
            self.assertIn('correlation_rank', scores[ticker])
            self.assertIn('integrated_score', scores[ticker])
            self.assertIn('selected', scores[ticker])
            self.assertIn('cash_replacement', scores[ticker])

        # Get allocation
        allocation = get_allocation(scores, 10000)

        # Verify allocation sums to investment amount (with rounding)
        total = sum(allocation.values())
        self.assertAlmostEqual(total, 10000, places=0)

    @patch('api.faa_calculator.calculate_correlation')
    @patch('api.faa_calculator.calculate_volatility')
    @patch('api.faa_calculator.calculate_momentum')
    def test_bear_market_scenario(self, mock_momentum, mock_volatility, mock_correlation):
        """Test FAA behavior in bear market (all negative momentum)."""
        tickers = ['A', 'B', 'C', 'D', 'E']

        # All negative momentum
        mock_momentum.side_effect = [-0.10, -0.15, -0.05, -0.20, -0.08]
        mock_volatility.side_effect = [0.15, 0.18, 0.12, 0.20, 0.14]
        mock_correlation.return_value = {
            'A': 2.0, 'B': 2.5, 'C': 1.8, 'D': 3.0, 'E': 2.2
        }

        scores = calculate_faa_scores(tickers)

        # All selected tickers should have cash_replacement flag
        selected = [t for t, d in scores.items() if d['selected']]
        for ticker in selected:
            self.assertTrue(scores[ticker]['cash_replacement'])

        # Allocation should all go to cash
        allocation = get_allocation(scores, 10000, cash_ticker='SHY')
        self.assertEqual(len(allocation), 1)
        self.assertIn('SHY', allocation)
        self.assertAlmostEqual(allocation['SHY'], 10000, places=0)


if __name__ == '__main__':
    unittest.main()
