"""
FAA (Flexible Asset Allocation) Calculator Module

This module implements the core FAA strategy calculations including:
- Momentum calculation (4-month return)
- Volatility calculation (80-day standard deviation)
- Correlation calculation (sum of pairwise correlations)
- Integrated score ranking and asset selection

References:
    PRD: /docs/PRD.md
    Strategy: Keller & Keuning's Flexible Asset Allocation
"""

from typing import List, Dict, Tuple, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_momentum(ticker: str, end_date: Optional[datetime] = None) -> Tuple[float, float]:
    """
    Calculate momentum score for a given ticker.

    Formula: (current_price / price_4_months_ago) - 1

    Args:
        ticker: Stock ticker symbol (e.g., "VTI")
        end_date: End date for calculation (defaults to today)

    Returns:
        Tuple of (momentum score, current price)
        - Momentum score as a decimal (e.g., 0.15 for 15% gain)
        - Current price as a float

    Raises:
        ValueError: If ticker data cannot be retrieved or insufficient data
    """
    if end_date is None:
        end_date = datetime.now()

    # Download 5 months of data to ensure we have 4 months of trading days
    start_date = end_date - timedelta(days=150)

    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if data.empty:
            raise ValueError(f"No data available for ticker: {ticker}")

        if len(data) < 80:
            raise ValueError(f"Insufficient data for {ticker}: need 80 days, got {len(data)}")

        # Get closing prices
        prices = data['Close']

        # Current price (most recent)
        current_price = float(prices.iloc[-1])

        # Price 4 months ago (approximately 80 trading days)
        # Use index -80 to ensure we have exactly 4 months of data
        price_4_months_ago = float(prices.iloc[-80])

        # Calculate momentum
        momentum = (current_price / price_4_months_ago) - 1

        return float(momentum), float(current_price)

    except Exception as e:
        raise ValueError(f"Error calculating momentum for {ticker}: {str(e)}")


def calculate_volatility(ticker: str, end_date: Optional[datetime] = None) -> float:
    """
    Calculate volatility score for a given ticker.

    Formula: std(daily_returns, 80_days)

    Args:
        ticker: Stock ticker symbol
        end_date: End date for calculation (defaults to today)

    Returns:
        Volatility (standard deviation of daily returns)

    Raises:
        ValueError: If ticker data cannot be retrieved or insufficient data
    """
    if end_date is None:
        end_date = datetime.now()

    # Download 5 months of data to get 80 trading days
    start_date = end_date - timedelta(days=150)

    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if data.empty:
            raise ValueError(f"No data available for ticker: {ticker}")

        if len(data) < 80:
            raise ValueError(f"Insufficient data for {ticker}: need 80 days, got {len(data)}")

        # Get closing prices for last 80 days
        prices = data['Close'].iloc[-80:]

        # Calculate daily returns
        daily_returns = prices.pct_change().dropna()

        # Calculate standard deviation
        volatility = daily_returns.std()

        return float(volatility)

    except Exception as e:
        raise ValueError(f"Error calculating volatility for {ticker}: {str(e)}")


def calculate_correlation(tickers: List[str], end_date: Optional[datetime] = None) -> Dict[str, float]:
    """
    Calculate correlation scores for each ticker against all others.

    Formula: For each asset, mean of absolute correlation coefficients with all other assets

    Args:
        tickers: List of ticker symbols (should be 7 for FAA strategy)
        end_date: End date for calculation (defaults to today)

    Returns:
        Dictionary mapping ticker to its correlation score (0 to 1)
        Higher values indicate stronger correlation with other assets

    Raises:
        ValueError: If tickers list is invalid or data cannot be retrieved
    """
    if not tickers or len(tickers) < 2:
        raise ValueError("Need at least 2 tickers to calculate correlation")

    if end_date is None:
        end_date = datetime.now()

    # Download 5 months of data
    start_date = end_date - timedelta(days=150)

    try:
        # Download data for all tickers
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)

        if data.empty:
            raise ValueError("No data available for the provided tickers")

        # Handle both single and multiple ticker cases
        if len(tickers) == 1:
            prices = data['Close']
        else:
            prices = data['Close']

        # Get last 80 days
        prices = prices.iloc[-80:]

        # Calculate daily returns for all tickers
        returns = prices.pct_change().dropna()

        # Calculate correlation matrix
        corr_matrix = returns.corr()

        # Calculate mean absolute correlation for each ticker (excluding self-correlation)
        correlation_scores = {}
        for ticker in tickers:
            # Calculate mean of absolute correlations with all others
            if ticker in corr_matrix.columns:
                # Get all correlations for this ticker
                correlations = corr_matrix[ticker]
                # Calculate mean of absolute values, excluding self-correlation
                abs_correlations = correlations.abs()
                # Sum of absolute correlations minus 1.0 (self), divided by count minus 1
                mean_abs_corr = (abs_correlations.sum() - 1.0) / (len(tickers) - 1)
                correlation_scores[ticker] = float(mean_abs_corr)
            else:
                raise ValueError(f"Missing data for ticker: {ticker}")

        return correlation_scores

    except Exception as e:
        raise ValueError(f"Error calculating correlations: {str(e)}")


def calculate_faa_scores(
    tickers: List[str],
    end_date: Optional[datetime] = None,
    cash_ticker: str = "SHY"
) -> Dict[str, dict]:
    """
    Calculate complete FAA scores for a portfolio of tickers.

    This function:
    1. Calculates momentum, volatility, and correlation for all tickers
    2. Ranks each metric (1=best, 7=worst for 7 assets)
    3. Computes integrated score: momentum_rank * 1.0 + volatility_rank * 0.5 + correlation_rank * 0.5
    4. Selects top 3 assets by integrated score (lower is better)
    5. Applies absolute momentum filter (replaces negative momentum with cash)
    6. If cash proxy (SHY) also has negative momentum, holds actual cash (0% return)

    Args:
        tickers: List of ticker symbols (typically 7 for FAA)
        end_date: End date for calculation (defaults to today)
        cash_ticker: Ticker to use for cash proxy (default: SHY)

    Returns:
        Dictionary with structure:
        {
            "ticker": {
                "momentum": float,
                "current_price": float,
                "momentum_rank": int,
                "volatility": float,
                "volatility_rank": int,
                "correlation": float,
                "correlation_rank": int,
                "integrated_score": float,
                "selected": bool,
                "cash_replacement": bool,  # True if negative momentum
                "hold_cash": bool  # True if SHY also has negative momentum
            },
            ...
        }

    Raises:
        ValueError: If invalid input or data retrieval fails
    """
    if not tickers:
        raise ValueError("Tickers list cannot be empty")

    if len(tickers) < 3:
        raise ValueError("Need at least 3 tickers for FAA calculation")

    if end_date is None:
        end_date = datetime.now()

    try:
        # Step 1: Calculate all metrics
        results = {}

        # Calculate momentum and volatility for each ticker
        for ticker in tickers:
            momentum, current_price = calculate_momentum(ticker, end_date)
            volatility = calculate_volatility(ticker, end_date)

            results[ticker] = {
                "momentum": momentum,
                "current_price": current_price,
                "volatility": volatility,
            }

        # Calculate correlations for all tickers
        correlations = calculate_correlation(tickers, end_date)
        for ticker in tickers:
            results[ticker]["correlation"] = correlations[ticker]

        # Step 2: Rank each metric
        # Momentum: Higher is better, so rank descending (highest = rank 1)
        momentum_sorted = sorted(results.items(), key=lambda x: x[1]["momentum"], reverse=True)
        for rank, (ticker, _) in enumerate(momentum_sorted, 1):
            results[ticker]["momentum_rank"] = rank

        # Volatility: Lower is better, so rank ascending (lowest = rank 1)
        volatility_sorted = sorted(results.items(), key=lambda x: x[1]["volatility"])
        for rank, (ticker, _) in enumerate(volatility_sorted, 1):
            results[ticker]["volatility_rank"] = rank

        # Correlation: Lower is better, so rank ascending (lowest = rank 1)
        correlation_sorted = sorted(results.items(), key=lambda x: x[1]["correlation"])
        for rank, (ticker, _) in enumerate(correlation_sorted, 1):
            results[ticker]["correlation_rank"] = rank

        # Step 3: Calculate integrated score
        for ticker in results:
            momentum_rank = results[ticker]["momentum_rank"]
            volatility_rank = results[ticker]["volatility_rank"]
            correlation_rank = results[ticker]["correlation_rank"]

            integrated_score = (
                momentum_rank * 1.0 +
                volatility_rank * 0.5 +
                correlation_rank * 0.5
            )

            results[ticker]["integrated_score"] = integrated_score

        # Step 4: Select top 3 by integrated score (lower is better)
        integrated_sorted = sorted(results.items(), key=lambda x: x[1]["integrated_score"])
        top_3_tickers = [ticker for ticker, _ in integrated_sorted[:3]]

        # Mark selected assets
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
        if has_cash_replacement:
            try:
                shy_momentum, _ = calculate_momentum(cash_ticker, end_date)

                # If SHY also has negative momentum, hold actual cash (0% return)
                if shy_momentum < 0:
                    for ticker in top_3_tickers:
                        if results[ticker]["cash_replacement"]:
                            results[ticker]["hold_cash"] = True
            except Exception as e:
                # If we can't get SHY data, log warning but continue
                # This allows the strategy to work even if SHY data is unavailable
                print(f"Warning: Could not retrieve {cash_ticker} momentum: {str(e)}")

        return results

    except Exception as e:
        raise ValueError(f"Error calculating FAA scores: {str(e)}")


def get_selected_tickers(faa_scores: Dict[str, dict]) -> List[str]:
    """
    Extract list of selected tickers from FAA scores.

    Args:
        faa_scores: Output from calculate_faa_scores()

    Returns:
        List of selected ticker symbols
    """
    return [ticker for ticker, data in faa_scores.items() if data["selected"]]


def get_allocation(
    faa_scores: Dict[str, dict],
    investment_amount: float,
    cash_ticker: str = "SHY"
) -> Dict[str, float]:
    """
    Calculate equal-weight allocation for selected tickers.

    Args:
        faa_scores: Output from calculate_faa_scores()
        investment_amount: Total amount to invest (in USD)
        cash_ticker: Ticker to use for cash replacement (default: SHY)

    Returns:
        Dictionary mapping ticker to dollar allocation

    Example:
        >>> allocation = get_allocation(scores, 10000)
        >>> {"VTI": 3333.33, "VEA": 3333.33, "SHY": 3333.33}
    """
    if investment_amount <= 0:
        raise ValueError("Investment amount must be positive")

    selected = get_selected_tickers(faa_scores)

    if not selected:
        raise ValueError("No tickers selected in FAA scores")

    # Equal weight allocation
    allocation_per_ticker = investment_amount / len(selected)

    allocation = {}
    for ticker in selected:
        # Check if this ticker should be replaced with cash
        if faa_scores[ticker]["hold_cash"]:
            # Hold actual cash (0% return) - represented as "CASH"
            if "CASH" in allocation:
                allocation["CASH"] += allocation_per_ticker
            else:
                allocation["CASH"] = allocation_per_ticker
        elif faa_scores[ticker]["cash_replacement"]:
            # Allocate to cash ticker (SHY) instead
            if cash_ticker in allocation:
                allocation[cash_ticker] += allocation_per_ticker
            else:
                allocation[cash_ticker] = allocation_per_ticker
        else:
            allocation[ticker] = allocation_per_ticker

    # Round to 2 decimal places
    allocation = {k: round(v, 2) for k, v in allocation.items()}

    return allocation
