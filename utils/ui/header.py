"""Company header component"""

import streamlit as st


def render_company_header(info: dict, search_query: str) -> str:
    """
    Render the company header with key metrics

    Args:
        info: Stock information dictionary
        search_query: Search query string

    Returns:
        Company name (str)
    """
    company_name: str = info.get("longName", search_query)
    st.markdown("---")

    # Add CSS to enable text wrapping in metric labels and values
    st.markdown(
        """
        <style>
        /* Force text wrapping for all metric components */
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] *,
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] *,
        [data-testid="stMetricDelta"],
        [data-testid="stMetricDelta"] * {
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            text-overflow: clip !important;
            overflow: visible !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_header1, col_header2, col_header3, col_header4 = st.columns(4)

    with col_header1:
        st.metric("Company", company_name)

    with col_header2:
        price = info.get("currentPrice", info.get("regularMarketPrice", "N/A"))
        prev_close = info.get("previousClose", 0)
        try:
            if price != "N/A" and prev_close != 0:
                change = (price - prev_close) / prev_close * 100
            else:
                change = 0
        except (TypeError, ZeroDivisionError):
            change = 0
        st.metric("Price", f"${price:.2f}" if price != "N/A" else "N/A", f"{change:+.2f}%")

    with col_header3:
        market_cap = info.get("marketCap", 0)
        st.metric("Market Cap", f"${market_cap / 1e9:.2f}B" if market_cap else "N/A")

    with col_header4:
        sector = info.get("sector", "N/A")
        st.metric("Sector", sector)

    return company_name
