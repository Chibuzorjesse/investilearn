"""
InvestiLearn - Fundamental Investment Dashboard

Main entry point for the Streamlit dashboard application.
Orchestrates UI components and data flow.
"""

import streamlit as st

from utils.data_fetcher import get_financial_statements, get_stock_info
from utils.ratio_calculator import calculate_ratios
from utils.ui import (
    render_company_header,
    render_financial_statements,
    render_landing_page,
    render_news_section,
    render_ratios_section,
    render_sidebar,
)
from utils.ui.landing import render_additional_resources

# Page configuration
st.set_page_config(page_title="Fundamental Investment Dashboard", page_icon="📈", layout="wide")

# Custom CSS for AI badges and styling
st.markdown(
    """
<style>
.ai-badge {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
    margin-left: 8px;
}
.confidence-high { color: #10b981; font-weight: 600; }
.confidence-medium { color: #f59e0b; font-weight: 600; }
.confidence-low { color: #ef4444; font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state for AI interactions (HAX Guideline G15)
if "feedback_count" not in st.session_state:
    st.session_state.feedback_count = 0
if "interaction_log" not in st.session_state:
    st.session_state.interaction_log = []
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

# Render sidebar (sets ai_enabled and confidence_level in session state)
render_sidebar()

# Main header
st.title("📊 Fundamental Investment Dashboard")
st.markdown(
    """
Welcome to your long-term investment research tool. Search for companies to analyze their
financial health, key ratios, and stay updated with relevant news.
"""
)

# AI Features disclosure (HAX Guideline G1)
st.info(
    """
🤖 **AI-Powered Features:**
- **Smart News Curation:** AI ranks articles by relevance, recency, and credibility
- **Interactive Learning Guide:** Click ❓ buttons to learn about any metric
- **Full Transparency:** See exactly why each recommendation is made

⚠️ **Important:** This tool provides educational information only. Not investment advice.
Always conduct your own due diligence and consult with a licensed financial advisor.
"""
)

# Search bar
st.markdown("---")
search_query = st.text_input(
    "🔍 Search for a company or ticker symbol",
    placeholder="e.g., Apple, AAPL, Microsoft, etc.",
    help="Enter a company name or stock ticker to begin your analysis",
)

# Filter options
with st.expander("🎯 Advanced Filters (Optional)"):
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        st.selectbox(
            "Industry",
            [
                "All Industries",
                "Technology",
                "Healthcare",
                "Finance",
                "Consumer Goods",
                "Energy",
                "Industrials",
                "Real Estate",
                "Utilities",
            ],
        )

    with col_filter2:
        st.selectbox(
            "Market Cap",
            ["All Sizes", "Large Cap (>$10B)", "Mid Cap ($2B-$10B)", "Small Cap (<$2B)"],
        )

    with col_filter3:
        st.checkbox("Prioritize ESG/Low Carbon Emissions")

# Main content area
if search_query:
    # Fetch stock data
    with st.spinner(f"Fetching data for {search_query}..."):
        info = get_stock_info(search_query)

    if info:
        # Display company header
        company_name = render_company_header(info, search_query)

        # Get financial data
        income_stmt, balance_sheet, cash_flow = get_financial_statements(search_query)
        ratios = calculate_ratios(info, income_stmt, balance_sheet)

        st.markdown("---")

        # Three column layout
        col1, col2, col3 = st.columns([1, 1, 1])

        # Left: Financial Statements
        with col1:
            render_financial_statements(income_stmt, balance_sheet, cash_flow)

        # Middle: Key Ratios
        with col2:
            render_ratios_section(ratios, company_name, search_query)

        # Right: News & Updates
        with col3:
            render_news_section(search_query, company_name)

        # Additional resources below the main columns
        render_additional_resources()

    else:
        # If no stock found, show error message
        st.error(
            f"Could not find data for '{search_query}'. "
            "Please check the ticker symbol and try again."
        )
        st.info("💡 Tip: Try using the stock ticker symbol (e.g., 'AAPL' for Apple Inc.)")

else:
    # Show landing page when no search is active
    render_landing_page()
