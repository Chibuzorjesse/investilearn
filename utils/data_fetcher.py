"""Data fetching utilities using yfinance"""

import streamlit as st
import yfinance as yf


@st.cache_resource(ttl=3600)  # Cache for 1 hour
def _get_stock_object(ticker):
    """
    Create and cache a yfinance Ticker object

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

    Returns:
        yf.Ticker object or None on error
    """
    try:
        return yf.Ticker(ticker)
    except Exception as e:
        st.error(f"Error creating ticker object for {ticker}: {str(e)}")
        return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_info(ticker):
    """
    Fetch stock information using yfinance

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

    Returns:
        dict: Stock info dictionary or None on error
    """
    try:
        stock = _get_stock_object(ticker)
        if stock is None:
            return None

        info = stock.info

        # Validate that we got meaningful data
        if not info or "symbol" not in info:
            st.error(f"No data found for ticker: {ticker}")
            return None

        return info
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return None


@st.cache_data(ttl=3600)
def get_financial_statements(ticker):
    """
    Fetch financial statements for a given ticker

    Args:
        ticker: Stock ticker symbol

    Returns:
        tuple: (income_statement, balance_sheet, cash_flow) DataFrames
               or (None, None, None) on error
    """
    try:
        stock = _get_stock_object(ticker)
        if stock is None:
            return None, None, None

        # Fetch annual financial statements
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow

        return income_stmt, balance_sheet, cash_flow
    except Exception as e:
        st.error(f"Error fetching financial statements: {str(e)}")
        return None, None, None


@st.cache_data(ttl=3600)
def get_news(ticker, max_items=10):
    """
    Fetch recent news for a given ticker

    Args:
        ticker: Stock ticker symbol
        max_items: Maximum number of news items to return

    Returns:
        list: List of news dictionaries with normalized structure
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news

        if not news:
            return []

        # Normalize the news structure from yfinance
        normalized_news = []
        for item in news[:max_items]:
            # yfinance returns nested structure: item['content'] has the actual data
            content = item.get("content", item)  # Fallback to item if no content key

            # Extract and normalize fields
            normalized = {
                "title": content.get("title", "No title available"),
                "summary": content.get("summary") or content.get("description", ""),
                "link": (
                    content.get("clickThroughUrl", {}).get("url")
                    or content.get("canonicalUrl", {}).get("url")
                    or content.get("link", "#")
                ),
                "publisher": (
                    content.get("provider", {}).get("displayName")
                    or content.get("publisher", "Unknown source")
                ),
                "providerPublishTime": None,  # Will parse pubDate
            }

            # Parse pubDate to timestamp
            pub_date = content.get("pubDate") or content.get("providerPublishTime")
            if pub_date:
                if isinstance(pub_date, str):
                    # Parse ISO format datetime
                    try:
                        from datetime import datetime

                        dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                        normalized["providerPublishTime"] = int(dt.timestamp())
                    except (ValueError, AttributeError):
                        # Invalid date format, keep as None
                        pass
                elif isinstance(pub_date, int | float):
                    normalized["providerPublishTime"] = int(pub_date)

            normalized_news.append(normalized)

        return normalized_news

    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []


@st.cache_data(ttl=3600)
def get_historical_data(ticker, period="1y"):
    """
    Fetch historical price data

    Args:
        ticker: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        DataFrame: Historical price data or None on error
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return None
