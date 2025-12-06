"""
InvestiLearn - Fundamental Investment Dashboard

Main entry point for the Streamlit dashboard application.
Orchestrates UI components and data flow.
"""

import streamlit as st

from utils.cache_warmer import get_cache_stats, warm_sector_caches
from utils.data_fetcher import get_financial_statements, get_stock_info
from utils.ratio_calculator import calculate_ratios
from utils.ui import (
    render_company_header,
    render_financial_statements,
    render_landing_page,
    render_news_section,
    render_ratios_section,
)
from utils.ui.coach_panel import render_coach_panel
from utils.ui.landing import render_additional_resources

# Page configuration
st.set_page_config(
    page_title="Fundamental Investment Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",  # Keep sidebar open for buttons
)

# Custom CSS for AI badges
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

/* Add padding to account for fixed header */
.main .block-container {
    padding-top: 5rem !important;
}

/* Hide the phantom buttons */
button[kind="primary"]:has-text("Coach (hidden)"),
button:has-text("Settings (hidden)"),
div.stButton:has(button[kind="primary"]) ~ div.stButton,
.stButton button:contains("hidden") {
    display: none !important;
}

/* Target the container with hidden buttons */
[data-testid="column"]:has(button[kind="primary"]) {
    display: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# App title
st.title("📊 InvestiLearn")

# Sidebar with controls and quick actions
with st.sidebar:
    # AI Controls - All checkboxes for consistency
    st.markdown("### 🤖 AI Assistant")

    master_ai = st.checkbox(
        "**Enable All AI Features**",
        value=st.session_state.get("ai_enabled", True),
        key="ai_enabled",
        help="Master switch for all AI-powered features",
    )

    if master_ai:
        # Sub-options indented/grouped
        st.markdown("**AI Capabilities:**")

        llm_coach = st.checkbox(
            "🤖 LLM Coach",
            value=True,
            help="Enable AI-powered investment coach for explanations and insights",
            disabled=not master_ai,
            key="llm_coach",
        )

        # Ask the Coach - adaptive button (only when LLM Coach enabled)
        if llm_coach:
            coach_button_text = "💬 Ask the Coach"
            current_company = st.session_state.get("current_company")
            if current_company:
                coach_button_text = f"💬 Ask about {current_company}"

            if st.button(coach_button_text, use_container_width=True, type="primary"):
                st.session_state.open_coach = True

        use_ml = st.checkbox(
            "🧠 News ML Models",
            value=st.session_state.get("use_ml_ranking", True),
            key="use_ml_ranking",
            help="Use machine learning for news ranking and sentiment analysis",
            disabled=not master_ai,
        )

        if use_ml:
            st.caption("📍 Models run 100% locally")
    else:
        st.caption("❌ AI features disabled")

    st.markdown("---")

    # Information & Learning Section
    st.markdown("### 📚 Information & Learning")

    if st.button("👋 Getting Started Guide", use_container_width=True):
        st.session_state.show_getting_started = True
        st.rerun()

    if st.button("🤖 How AI Assists You", use_container_width=True):
        st.session_state.show_ai_info = True
        st.rerun()

    if st.button("💎 What is Fundamental Investing?", use_container_width=True):
        st.session_state.show_fundamentals = True
        st.rerun()

    if st.button("📖 Additional Resources", use_container_width=True):
        st.session_state.show_resources = True
        st.rerun()

    if st.button("💡 Quick Tips", use_container_width=True):
        st.session_state.show_tips = True
        st.rerun()

    st.markdown("---")

    # Collapsed confidence info
    with st.expander("✨ Confidence Levels", expanded=False):
        st.caption("🟢 High: Well-established")
        st.caption("🟡 Medium: Context-dependent")
        st.caption("🔴 Low: Consult an expert")

    if "feedback_count" in st.session_state and st.session_state.feedback_count > 0:
        st.markdown("---")
        st.success(f"📊 {st.session_state.feedback_count} feedback given!")


# Dialog functions
@st.dialog("👋 Getting Started with InvestiLearn", width="large")
def show_getting_started_dialog() -> None:
    """Display getting started guide in a dialog."""
    st.markdown(
        """
        Welcome to **InvestiLearn** - your interactive platform for learning
        fundamental investing by analyzing real company data!

        ### 🎯 Quick Start Guide

        **1️⃣ Start Simple**

        Search for a company you know (like Apple, Microsoft, or Tesla) using
        the search bar on the main page.

        **2️⃣ Explore with AI**

        Click ❓ buttons next to any metric you don't understand. Our AI Coach
        will explain it in simple terms.

        **3️⃣ Ask Questions**

        Use the "Ask the Coach" button to get personalized explanations about
        investing concepts or specific companies.

        **4️⃣ Give Feedback**

        Help improve the AI by rating explanations as helpful or not. Your
        feedback makes the system better!

        ### 🎨 Navigation

        - **Main Page:** Search companies and view their data
        - **Left Sidebar:** Access AI features, learning resources, and info
        - **Tabs:** Explore financial statements, ratios, and news

        ### 🚀 Ready to Begin?

        Close this dialog and search for your first company!
        """
    )


@st.dialog("🤖 How AI Assists You", width="large")
def show_ai_info_dialog() -> None:
    """Display AI capabilities and limitations in a dialog."""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            ### What AI Does

            **🎯 Smart News Ranking**

            AI scores articles based on:
            - Relevance to the company and sector
            - Source credibility and reputation
            - Recency and timeliness
            - Content quality and depth

            **🔍 Transparent Recommendations**

            Click any article to see exactly why it was ranked the way it was.
            No black boxes - you see the scoring factors.

            **💬 Interactive Learning**

            Click ❓ next to any financial metric for instant, context-aware
            explanations tailored to your learning level.

            **🎓 Educational Coach**

            Ask the AI Coach questions about:
            - Investing concepts and terminology
            - How to interpret financial metrics
            - Company-specific analysis
            - General market principles
            """
        )

    with col2:
        st.info(
            """
            ### AI Doesn't:

            ❌ Make investment decisions

            ❌ Predict stock prices

            ❌ Provide financial advice

            ❌ Replace professional advisors

            ---

            **Always verify with official sources and consult professionals.**
            """
        )

    st.markdown("---")
    st.markdown(
        """
        ### 🎚️ Confidence Levels

        Every AI response includes a confidence indicator:

        - **🟢 High:** Well-established financial concepts and clear data
        - **🟡 Medium:** Context-dependent or requires interpretation
        - **🔴 Low:** Complex topics - consult additional sources

        You can filter AI insights by confidence level in the sidebar.
        """
    )


# Show "What is Fundamental Investing" dialog if triggered
if st.session_state.get("show_getting_started"):
    st.session_state.show_getting_started = False
    show_getting_started_dialog()

if st.session_state.get("show_ai_info"):
    st.session_state.show_ai_info = False
    show_ai_info_dialog()

if st.session_state.get("show_fundamentals"):
    st.session_state.show_fundamentals = False

    @st.dialog("💎 What is Fundamental Investing?", width="large")
    def show_fundamentals_dialog():
        st.markdown("""
        ### The Philosophy

        Fundamental investing is a **long-term investment strategy** that focuses on
        analyzing a company's financial health, business model, and competitive advantages
        to identify high-quality companies worth holding for decades.

        ### 📋 Key Principles

        **📊 Analyze Financial Statements Thoroughly**
        - Study income statements, balance sheets, and cash flow
        - Look for consistent revenue and profit growth
        - Understand where money comes from and goes

        **🏢 Focus on Sustainable Competitive Advantages**
        - Does the company have a "moat"?
        - Brand strength, network effects, economies of scale
        - Barriers to entry that protect market position

        **⏰ Think Long-Term (5-10+ Years)**
        - Ignore short-term market noise
        - Focus on business fundamentals, not stock prices
        - Patience is key to compound growth

        **🎯 Invest in Businesses You Understand**
        - "Circle of competence" - stay within what you know
        - If you can't explain the business, don't invest
        - Understand the industry and competitive landscape

        **💰 Buy Quality Companies at Reasonable Prices**
        - Look for undervalued opportunities
        - Use metrics like P/E, P/B, ROE to assess value
        - Remember: Price is what you pay, value is what you get
        """)

        st.markdown("---")

        st.info(
            "💡 **This dashboard helps you apply these principles** by providing financial data, metrics, and AI-powered insights for any public company!"
        )

        if st.button("Close", type="primary", use_container_width=True):
            st.rerun()

    show_fundamentals_dialog()

# Show learning resources modal if triggered
if st.session_state.get("show_resources"):
    st.session_state.show_resources = False

    @st.dialog("📚 Additional Learning Resources", width="large")
    def show_resources_dialog():
        st.markdown("### 📖 Recommended Resources")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **📚 Books & Letters:**
            - [Warren Buffett's Letters](https://berkshirehathaway.com/letters/letters.html)
            - The Intelligent Investor (Benjamin Graham)
            - Common Stocks and Uncommon Profits (Philip Fisher)
            """)

        with col2:
            st.markdown("""
            **🌐 Online Resources:**
            - [SEC EDGAR Database](https://www.sec.gov/edgar)
            - [Investopedia](https://www.investopedia.com)
            - [FRED Economic Data](https://fred.stlouisfed.org)
            """)

        st.markdown("---")

        st.info(
            "💡 **Pro Tip:** Always verify information from multiple sources and consult with a financial advisor for personalized advice!"
        )

        if st.button("Close", type="primary", use_container_width=True):
            st.rerun()

    show_resources_dialog()


@st.dialog("💡 Quick Tips for Using InvestiLearn", width="large")
def show_tips_dialog() -> None:
    """Display quick tips in a dialog."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 🚀 Getting Started

            **Search:**
            - Enter company name or ticker
            - Try: Apple, MSFT, TSLA
            - Works with most US stocks

            **Learn:**
            - Click ❓ for metric explanations
            - Use Coach for deeper questions
            - All explanations are context-aware
            """
        )

    with col2:
        st.markdown(
            """
            ### 🎯 Understanding Results

            **Confidence Levels:**
            - 🟢 High: Trust this info
            - 🟡 Medium: Context matters
            - 🔴 Low: Verify elsewhere

            **Tabs:**
            - 📊 Statements: Raw financials
            - 📈 Ratios: Key metrics
            - 📰 News: AI-ranked articles
            """
        )

    with col3:
        st.markdown(
            """
            ### ⚙️ AI Features

            **Settings:**
            - Toggle AI on/off in sidebar
            - Adjust confidence filters
            - All models run locally

            **Coach:**
            - General investing questions
            - Company-specific analysis
            - Always includes confidence
            """
        )

    st.markdown("---")
    st.info(
        """
        **💡 Pro Tip:** Start with companies you know well. It's easier to learn
        financial analysis when you already understand the business model!
        """
    )


# Show tips dialog if triggered
if st.session_state.get("show_tips"):
    st.session_state.show_tips = False
    show_tips_dialog()


# Initialize session state for AI interactions (HAX Guideline G15)
if "feedback_count" not in st.session_state:
    st.session_state.feedback_count = 0
if "interaction_log" not in st.session_state:
    st.session_state.interaction_log = []
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

# Precompute caches on first app load (simulates server startup)
if "caches_warmed" not in st.session_state:
    warm_sector_caches()
    st.session_state.caches_warmed = True
    cache_stats = get_cache_stats()
    st.toast(
        f"✅ Loaded {cache_stats['total_companies']} companies "
        f"across {cache_stats['sectors_cached']} sectors!"
    )

# Preload ML models if enabled
if "models_loaded" not in st.session_state:
    from utils.model_loader import preload_models_with_ui

    preload_models_with_ui()
    st.session_state.models_loaded = True

# Search bar
st.markdown("---")
search_query = st.text_input(
    "🔍 Search for a company or ticker symbol",
    placeholder="e.g., Apple, AAPL, Microsoft, etc.",
    help="Enter a company name or stock ticker to begin your analysis",
)

# Simple welcome message when no search
if not search_query:
    st.markdown(
        """
        ### 👋 Welcome to InvestiLearn!

        Learn fundamental investing by analyzing real company data with AI.

        **Get started:**
        1. Search for a company above (e.g., Apple, MSFT, Tesla)
        2. Explore financial data, ratios, and news
        3. Click ❓ buttons or ask the Coach for explanations

        💡 *New here? Check the "Getting Started Guide" in the sidebar!*
        """
    )

# Check if coach button was clicked from sidebar
if st.session_state.get("open_coach"):
    # Clear the flag
    del st.session_state.open_coach

    # Sidebar button NEVER uses auto_prompt - always opens blank
    # This allows users to ask their own questions
    stored_context = st.session_state.get("company_context")

    if stored_context:
        # Use stored context (company was previously loaded)
        render_coach_panel(stored_context, None)
    else:
        # No company context available - general questions
        render_coach_panel(None, None)

# If no search query, stop here
if not search_query:
    st.stop()  # Stop rendering the rest of the page

# Main content area
if search_query:
    # Store current company in session state for sidebar button
    st.session_state.current_company = search_query

    # Fetch stock data
    with st.spinner(f"Fetching data for {search_query}..."):
        info = get_stock_info(search_query)

    if info:
        # Display company header
        company_name = render_company_header(info, search_query)

        # Get financial data
        income_stmt, balance_sheet, cash_flow = get_financial_statements(search_query)
        ratios = calculate_ratios(info, income_stmt, balance_sheet)

        # Build comprehensive company context for coach
        company_context = {
            "company_name": company_name,
            "ticker": search_query,
            "sector": info.get("sector", "Unknown"),
            "market_cap": info.get("marketCap", "N/A"),
            "current_price": info.get("currentPrice", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "forward_pe": info.get("forwardPE", "N/A"),
            "pb_ratio": info.get("priceToBook", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "avg_volume": info.get("averageVolume", "N/A"),
            "beta": info.get("beta", "N/A"),
            "ratios": ratios,  # Include all calculated ratios
            "income_statement": income_stmt,  # Financial statements
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow,
        }

        # Store company context for sidebar button
        st.session_state.company_context = company_context

        # Check if coach button was clicked or metric help was triggered
        if st.session_state.get("open_coach") or "ask_coach_metric" in st.session_state:
            # Clear the flag
            st.session_state.pop("open_coach", None)

            # Check for metric-specific question
            if "ask_coach_metric" in st.session_state:
                metric_info = st.session_state.ask_coach_metric
                enhanced_context = {
                    **company_context,
                    "metric_name": metric_info["name"],
                    "metric_value": metric_info["value"],
                }
                if metric_info.get("industry_avg"):
                    enhanced_context["industry_avg"] = metric_info["industry_avg"]

                # Create auto prompt for the metric
                auto_prompt = (
                    f"Explain the {metric_info['name']} ratio for "
                    f"{metric_info['company']}. Their current value is "
                    f"{metric_info['value']}"
                )
                if metric_info.get("industry_avg"):
                    auto_prompt += f" vs industry average of {metric_info['industry_avg']}"
                auto_prompt += (
                    ". What does this tell me about the company's financial "
                    "health and what should I consider for fundamental investing?"
                )

                st.session_state.pop("ask_coach_metric", None)
                render_coach_panel(enhanced_context, auto_prompt)
            else:
                # Check if there's news article context
                context_to_use = company_context
                if "news_article_context" in st.session_state:
                    context_to_use = {**company_context, **st.session_state.news_article_context}
                    st.session_state.pop("news_article_context", None)

                # When clicking "Ask Coach" button, provide full context
                auto_prompt = st.session_state.get("coach_auto_prompt")
                render_coach_panel(context_to_use, auto_prompt)

        # Floating coach button (removed - now in header)

        st.markdown("---")

        # Tab-based navigation for better mobile experience
        st.info(
            "💡 **Navigate the sections below** to explore financial statements, "
            "key ratios, and AI-curated news"
        )

        tab1, tab2, tab3 = st.tabs(
            ["📊 Financial Statements", "📈 Key Ratios", "📰 News & Updates"]
        )

        with tab1:
            render_financial_statements(income_stmt, balance_sheet, cash_flow)

        with tab2:
            render_ratios_section(
                ratios, company_name, search_query, info, income_stmt, balance_sheet
            )

        with tab3:
            render_news_section(search_query, company_name)

        # Additional resources below the tabs
        ticker_symbol = info.get("symbol", search_query)
        render_additional_resources(ticker=ticker_symbol, cik=ticker_symbol)

        # Ask the Coach button for company-specific questions
        st.markdown("---")
        col_coach1, col_coach2, col_coach3 = st.columns([1, 2, 1])
        with col_coach2:
            if st.button(
                f"💬 Ask the Coach about {company_name}",
                use_container_width=True,
                type="primary",
                key="company_coach_button",
            ):
                st.session_state.open_coach = True
                st.rerun()

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
