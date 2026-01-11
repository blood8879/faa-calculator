from http.server import BaseHTTPRequestHandler
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np

# Import FAA calculator functions
try:
    from .faa_calculator import calculate_faa_scores
except ImportError:
    from faa_calculator import calculate_faa_scores


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, "Missing request body")
                return

            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # Validate request payload
            tickers = data.get('tickers', [])
            if not tickers:
                self._send_error(400, "Missing 'tickers' field in request")
                return

            if not isinstance(tickers, list):
                self._send_error(400, "'tickers' must be an array")
                return

            # Clean and validate tickers
            tickers = [str(t).strip().upper() for t in tickers]
            if any(not t for t in tickers):
                self._send_error(400, "All tickers must be non-empty strings")
                return

            # Validate and parse start_date
            start_date_str = data.get('start_date')
            if not start_date_str:
                self._send_error(400, "Missing 'start_date' field in request")
                return

            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                self._send_error(400, "Invalid date format. Use YYYY-MM-DD")
                return

            # Ensure start date is not in the future
            if start_date > datetime.now():
                self._send_error(400, "Start date cannot be in the future")
                return

            # Run backtest
            result = run_backtest(tickers, start_date)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON in request body")
        except ValueError as e:
            self._send_error(422, str(e))
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_error(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {"success": False, "error": message}
        self.wfile.write(json.dumps(error_response).encode())


def run_backtest(tickers: List[str], start_date: datetime) -> Dict[str, Any]:
    """
    Run backtest simulation for FAA strategy.

    Args:
        tickers: List of ticker symbols for FAA universe
        start_date: Start date for backtest

    Returns:
        Dictionary containing equity curve, metrics, and SPY benchmark
    """
    # Initial portfolio value
    initial_value = 10000.0

    # Download historical data for all tickers plus SPY benchmark
    end_date = datetime.now()

    # Add buffer to start date to ensure we have enough data for first rebalancing
    # (need 150 days before first rebalancing for momentum/volatility calculations)
    data_start_date = start_date - timedelta(days=180)

    # Download data for FAA tickers
    all_tickers = tickers + ['SPY']
    price_data = yf.download(all_tickers, start=data_start_date, end=end_date, progress=False)

    if price_data.empty:
        raise ValueError("Unable to download price data for specified tickers")

    # Extract closing prices
    if len(all_tickers) == 1:
        close_prices = pd.DataFrame({all_tickers[0]: price_data['Close']})
    else:
        close_prices = price_data['Close']

    # Ensure all tickers have data
    for ticker in all_tickers:
        if ticker not in close_prices.columns:
            raise ValueError(f"No data available for ticker: {ticker}")

    # Generate monthly rebalancing dates (first trading day of each month)
    rebalancing_dates = generate_monthly_dates(close_prices, start_date)

    if not rebalancing_dates:
        raise ValueError("Insufficient data for backtest period")

    # Run FAA strategy backtest
    equity_curve = simulate_faa_strategy(
        tickers=tickers,
        close_prices=close_prices,
        rebalancing_dates=rebalancing_dates,
        initial_value=initial_value
    )

    # Run SPY benchmark backtest
    spy_benchmark = simulate_buy_and_hold(
        ticker='SPY',
        close_prices=close_prices,
        start_date=rebalancing_dates[0],
        initial_value=initial_value
    )

    # Calculate performance metrics
    metrics = calculate_metrics(equity_curve)

    # Format response
    result = {
        "success": True,
        "equity_curve": equity_curve,
        "metrics": metrics,
        "spy_benchmark": spy_benchmark
    }

    return result


def generate_monthly_dates(price_data: pd.DataFrame, start_date: datetime) -> List[datetime]:
    """
    Generate list of rebalancing dates (first trading day of each month).

    Args:
        price_data: DataFrame with price data (index is dates)
        start_date: Start date for backtest

    Returns:
        List of datetime objects representing rebalancing dates
    """
    dates = []
    price_index = price_data.index

    # Filter to dates on or after start_date
    valid_dates = price_index[price_index >= pd.Timestamp(start_date)]

    if len(valid_dates) == 0:
        return []

    current_month = None

    for date in valid_dates:
        date_month = (date.year, date.month)

        # First trading day of new month
        if current_month is None or date_month != current_month:
            dates.append(date.to_pydatetime())
            current_month = date_month

    return dates


def simulate_faa_strategy(
    tickers: List[str],
    close_prices: pd.DataFrame,
    rebalancing_dates: List[datetime],
    initial_value: float
) -> List[Dict[str, Any]]:
    """
    Simulate FAA strategy with monthly rebalancing.

    Args:
        tickers: List of ticker symbols
        close_prices: DataFrame with historical prices
        rebalancing_dates: List of rebalancing dates
        initial_value: Initial portfolio value

    Returns:
        List of equity curve points with date, value, and return
    """
    equity_curve = []
    portfolio_value = initial_value
    holdings = {}  # ticker -> number of shares

    for i, rebal_date in enumerate(rebalancing_dates):
        # Calculate FAA scores for this rebalancing date using pre-downloaded data
        try:
            faa_scores = calculate_faa_scores_from_data(
                tickers, close_prices, rebal_date
            )
        except Exception as e:
            # Skip this rebalancing if calculation fails (likely insufficient data)
            continue

        # Get selected tickers (top 3 by integrated score)
        selected = [
            ticker for ticker, data in faa_scores.items()
            if data.get('selected', False)
        ]

        # Apply cash replacement for negative momentum
        final_allocation = {}
        cash_positions = 0  # Count of positions holding actual cash

        for ticker in selected:
            if faa_scores[ticker].get('hold_cash', False):
                # Hold actual cash (0% return) - count it but don't allocate to any ticker
                cash_positions += 1
            elif faa_scores[ticker].get('cash_replacement', False):
                # Replace with SHY (cash proxy)
                if 'SHY' in final_allocation:
                    final_allocation['SHY'] += 1
                else:
                    final_allocation['SHY'] = 1
            else:
                final_allocation[ticker] = final_allocation.get(ticker, 0) + 1

        # Equal weight allocation
        allocation_per_position = portfolio_value / len(selected)

        # Rebalance portfolio
        new_holdings = {}
        cash_value = 0  # Track actual cash holdings

        # Allocate to investable positions
        for ticker, count in final_allocation.items():
            if ticker in close_prices.columns:
                price = close_prices.loc[rebal_date, ticker]
                shares = (allocation_per_position * count) / price
                new_holdings[ticker] = shares

        # Add cash positions (0% return)
        if cash_positions > 0:
            cash_value = allocation_per_position * cash_positions

        holdings = new_holdings

        # Record equity curve point
        return_pct = 0 if i == 0 else (portfolio_value / initial_value - 1)
        equity_curve.append({
            "date": rebal_date.strftime('%Y-%m-%d'),
            "value": round(float(portfolio_value), 2),
            "return": round(float(return_pct), 4)
        })

        # Update portfolio value daily until next rebalancing
        next_rebal_idx = i + 1
        if next_rebal_idx < len(rebalancing_dates):
            next_rebal_date = rebalancing_dates[next_rebal_idx]

            # Get daily dates between rebalancings
            rebal_timestamp = pd.Timestamp(rebal_date)
            next_rebal_timestamp = pd.Timestamp(next_rebal_date)

            daily_dates = close_prices.index[
                (close_prices.index > rebal_timestamp) &
                (close_prices.index < next_rebal_timestamp)
            ]

            for daily_date in daily_dates:
                # Calculate portfolio value based on current holdings
                daily_value = cash_value  # Start with cash holdings (0% return)
                for ticker, shares in holdings.items():
                    if ticker in close_prices.columns:
                        price = close_prices.loc[daily_date, ticker]
                        daily_value += shares * price

                portfolio_value = daily_value
                return_pct = (portfolio_value / initial_value - 1)

                equity_curve.append({
                    "date": daily_date.strftime('%Y-%m-%d'),
                    "value": round(float(portfolio_value), 2),
                    "return": round(float(return_pct), 4)
                })

    # Final portfolio value
    if len(rebalancing_dates) > 0:
        last_date = close_prices.index[-1]
        final_value = cash_value  # Include cash holdings

        for ticker, shares in holdings.items():
            if ticker in close_prices.columns:
                price = close_prices.loc[last_date, ticker]
                final_value += shares * price

        portfolio_value = final_value
        return_pct = (portfolio_value / initial_value - 1)

        # Only add if not already the last date
        if not equity_curve or equity_curve[-1]['date'] != last_date.strftime('%Y-%m-%d'):
            equity_curve.append({
                "date": last_date.strftime('%Y-%m-%d'),
                "value": round(float(portfolio_value), 2),
                "return": round(float(return_pct), 4)
            })

    return equity_curve


def calculate_faa_scores_from_data(
    tickers: List[str],
    close_prices: pd.DataFrame,
    end_date: datetime,
    cash_ticker: str = "SHY"
) -> Dict[str, dict]:
    """
    Calculate FAA scores using pre-downloaded price data.

    This is an optimized version that doesn't re-download data for each calculation.

    Args:
        tickers: List of ticker symbols
        close_prices: DataFrame with historical prices (already downloaded)
        end_date: End date for calculation
        cash_ticker: Ticker to use for cash proxy (default: SHY)

    Returns:
        Dictionary with FAA scores (same format as calculate_faa_scores)
    """
    if not tickers or len(tickers) < 3:
        raise ValueError("Need at least 3 tickers for FAA calculation")

    results = {}
    end_timestamp = pd.Timestamp(end_date)

    # Get data up to end_date
    historical_data = close_prices[close_prices.index <= end_timestamp]

    if len(historical_data) < 80:
        raise ValueError("Insufficient historical data for FAA calculation")

    # Calculate momentum and volatility for each ticker
    for ticker in tickers:
        if ticker not in close_prices.columns:
            raise ValueError(f"No data for ticker: {ticker}")

        prices = historical_data[ticker].dropna()

        if len(prices) < 80:
            raise ValueError(f"Insufficient data for {ticker}")

        # Get last 80 days of prices
        recent_prices = prices.iloc[-80:]

        # Momentum: (current / 4_months_ago) - 1
        current_price = float(recent_prices.iloc[-1])
        price_4m_ago = float(recent_prices.iloc[0])  # First of last 80 days
        momentum = (current_price / price_4m_ago) - 1

        # Volatility: std of daily returns over 80 days
        daily_returns = recent_prices.pct_change().dropna()
        volatility = daily_returns.std()

        results[ticker] = {
            "momentum": float(momentum),
            "current_price": float(current_price),
            "volatility": float(volatility)
        }

    # Calculate correlations
    # Get last 80 days for all tickers
    recent_data = historical_data.iloc[-80:][tickers]
    returns = recent_data.pct_change().dropna()
    corr_matrix = returns.corr()

    for ticker in tickers:
        # Sum of correlations with all other tickers (excluding self)
        correlation_sum = corr_matrix[ticker].sum() - 1.0
        results[ticker]["correlation"] = float(correlation_sum)

    # Rank metrics
    # Momentum: Higher is better (rank 1 = highest)
    momentum_sorted = sorted(results.items(), key=lambda x: x[1]["momentum"], reverse=True)
    for rank, (ticker, _) in enumerate(momentum_sorted, 1):
        results[ticker]["momentum_rank"] = rank

    # Volatility: Lower is better (rank 1 = lowest)
    volatility_sorted = sorted(results.items(), key=lambda x: x[1]["volatility"])
    for rank, (ticker, _) in enumerate(volatility_sorted, 1):
        results[ticker]["volatility_rank"] = rank

    # Correlation: Lower is better (rank 1 = lowest)
    correlation_sorted = sorted(results.items(), key=lambda x: x[1]["correlation"])
    for rank, (ticker, _) in enumerate(correlation_sorted, 1):
        results[ticker]["correlation_rank"] = rank

    # Calculate integrated score
    for ticker in results:
        integrated_score = (
            results[ticker]["momentum_rank"] * 1.0 +
            results[ticker]["volatility_rank"] * 0.5 +
            results[ticker]["correlation_rank"] * 0.5
        )
        results[ticker]["integrated_score"] = integrated_score

    # Select top 3 by integrated score (lower is better)
    integrated_sorted = sorted(results.items(), key=lambda x: x[1]["integrated_score"])
    top_3_tickers = [ticker for ticker, _ in integrated_sorted[:3]]

    # Mark selected assets and apply absolute momentum filter
    for ticker in results:
        results[ticker]["selected"] = ticker in top_3_tickers
        results[ticker]["cash_replacement"] = False
        results[ticker]["hold_cash"] = False

    # Step 5: Apply absolute momentum filter
    # If any selected asset has negative momentum, replace with cash proxy (SHY)
    has_cash_replacement = False
    for ticker in top_3_tickers:
        if results[ticker]["momentum"] < 0:
            results[ticker]["cash_replacement"] = True
            has_cash_replacement = True

    # Step 6: Check cash proxy (SHY) momentum
    # If we're replacing any asset with SHY, check if SHY itself has negative momentum
    if has_cash_replacement and cash_ticker in close_prices.columns:
        try:
            # Calculate SHY momentum from data
            shy_prices = historical_data[cash_ticker].dropna()

            if len(shy_prices) >= 80:
                recent_shy_prices = shy_prices.iloc[-80:]
                current_shy_price = recent_shy_prices.iloc[-1]
                shy_price_4m_ago = recent_shy_prices.iloc[0]
                shy_momentum = (current_shy_price / shy_price_4m_ago) - 1

                # If SHY also has negative momentum, hold actual cash (0% return)
                if shy_momentum < 0:
                    for ticker in top_3_tickers:
                        if results[ticker]["cash_replacement"]:
                            results[ticker]["hold_cash"] = True
        except Exception as e:
            # If we can't calculate SHY momentum, log and continue
            print(f"Warning: Could not calculate {cash_ticker} momentum: {str(e)}")

    return results


def simulate_buy_and_hold(
    ticker: str,
    close_prices: pd.DataFrame,
    start_date: datetime,
    initial_value: float
) -> List[Dict[str, Any]]:
    """
    Simulate buy-and-hold strategy for benchmark (SPY).

    Args:
        ticker: Ticker symbol (e.g., 'SPY')
        close_prices: DataFrame with historical prices
        start_date: Start date for backtest
        initial_value: Initial investment amount

    Returns:
        List of equity curve points with date, value, and return
    """
    equity_curve = []

    # Filter data to start date onwards
    start_timestamp = pd.Timestamp(start_date)
    benchmark_data = close_prices[close_prices.index >= start_timestamp][ticker]

    if benchmark_data.empty:
        return []

    # Initial price and shares
    initial_price = benchmark_data.iloc[0]
    shares = initial_value / initial_price

    # Calculate daily values
    for date, price in benchmark_data.items():
        value = shares * price
        return_pct = (value / initial_value - 1)

        equity_curve.append({
            "date": date.strftime('%Y-%m-%d'),
            "value": round(float(value), 2),
            "return": round(float(return_pct), 4)
        })

    return equity_curve


def calculate_metrics(equity_curve: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate performance metrics for equity curve.

    Args:
        equity_curve: List of equity curve points

    Returns:
        Dictionary with CAGR, MDD, and Sharpe ratio
    """
    if not equity_curve or len(equity_curve) < 2:
        return {
            "cagr": 0.0,
            "mdd": 0.0,
            "sharpe": 0.0
        }

    # Extract values and dates
    values = [point['value'] for point in equity_curve]
    dates = [datetime.strptime(point['date'], '%Y-%m-%d') for point in equity_curve]

    # Calculate CAGR
    initial_value = values[0]
    final_value = values[-1]
    years = (dates[-1] - dates[0]).days / 365.25

    if years > 0 and initial_value > 0:
        cagr = (final_value / initial_value) ** (1 / years) - 1
    else:
        cagr = 0.0

    # Calculate Maximum Drawdown (MDD)
    peak = values[0]
    max_drawdown = 0.0

    for value in values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    mdd = -max_drawdown  # Negative to indicate loss

    # Calculate Sharpe Ratio
    # Calculate daily returns
    returns = []
    for i in range(1, len(values)):
        daily_return = (values[i] - values[i-1]) / values[i-1]
        returns.append(daily_return)

    if returns:
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return > 0:
            # Annualize: sqrt(252) for daily returns
            sharpe = (mean_return / std_return) * np.sqrt(252)
        else:
            sharpe = 0.0
    else:
        sharpe = 0.0

    return {
        "cagr": round(cagr, 4),
        "mdd": round(mdd, 4),
        "sharpe": round(sharpe, 4)
    }
