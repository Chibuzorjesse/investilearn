"""Settings control panel component"""

import streamlit as st


@st.dialog("⚙️ Control Center", width="large")
def render_settings_panel() -> tuple[bool, str]:
    """
    Render settings control panel in a modal dialog

    Returns:
        Tuple of (ai_enabled, confidence_level)
    """
    st.markdown("### 🤖 AI Features")
    ai_enabled = st.checkbox(
        "Enable AI assistance",
        value=st.session_state.get("ai_enabled", True),
        help="Turn on AI-powered news curation and learning guide",
    )

    if ai_enabled:
        st.success("✓ AI features active")
        st.caption(
            "💡 Your interactions help improve recommendations. No personal data is collected."
        )
        st.info(
            "🔒 **Privacy First:** All AI models run locally on "
            "your device. No data is sent to external APIs."
        )

        # ML models toggle
        use_ml_ranking = st.checkbox(
            "Use advanced ML models",
            value=st.session_state.get("use_ml_ranking", True),
            help=(
                "Enable Hugging Face models for semantic similarity "
                "and sentiment analysis (requires transformers package)"
            ),
        )
        st.session_state.use_ml_ranking = use_ml_ranking

        if use_ml_ranking:
            st.caption("🧠 Using sentence embeddings & FinBERT sentiment analysis")
            st.caption("📍 Models run 100% locally - no external API calls")

        confidence_level = st.select_slider(
            "AI confidence threshold",
            options=["Show all", "Medium+", "High only"],
            value=st.session_state.get("confidence_level", "Show all"),
            help="Filter AI suggestions by confidence level",
        )

        if confidence_level != "Show all":
            st.caption(f"Only showing {confidence_level} confidence suggestions")
    else:
        st.info("AI features disabled. Showing raw data only.")
        confidence_level = "Show all"

    st.markdown("---")
    st.markdown("### Display Preferences")

    show_tooltips = st.checkbox(
        "Show educational tooltips",
        value=st.session_state.get("show_tooltips", True),
    )
    st.session_state.show_tooltips = show_tooltips

    currency = st.selectbox(
        "Currency",
        ["USD", "EUR", "GBP", "JPY"],
        index=0,
    )
    st.session_state.currency = currency

    beginner_mode = st.checkbox(
        "Beginner mode",
        value=st.session_state.get("beginner_mode", False),
        help="Simplified view with guided explanations",
    )
    st.session_state.beginner_mode = beginner_mode

    if beginner_mode:
        st.caption("🎓 Showing simplified metrics with learning hints")

    st.markdown("---")
    st.markdown("### 📚 Reference & Help")

    with st.expander("🔍 How AI Works Here"):
        st.caption(
            """
            **News Curation:**
            - Analyzes article relevance to your search
            - Balances sentiment and source diversity
            - Updates recommendations as you interact

            **Learning Guide:**
            - Trained on financial education materials
            - Provides context-specific explanations
            - Cites sources when available

            **What we DON'T do:**
            - Make investment recommendations
            - Predict stock prices
            - Guarantee accuracy of third-party data

            **Privacy:**
            - Interactions stored anonymously
            - No personal information collected
            - Data used only to improve experience
            """
        )

    with st.expander("📖 Quick Reference"):
        st.markdown(
            """
            **Financial Statements:**
            - Income Statement: Revenue & Profit
            - Cash Flow: Actual cash movement
            - Balance Sheet: Assets & Liabilities

            **Key Ratio Categories:**
            - Profitability: Earnings power
            - Liquidity: Short-term health
            - Efficiency: Asset utilization
            - Leverage: Debt levels
            - Valuation: Price vs value
            """
        )

    with st.expander("⚠️ Important Disclaimers"):
        st.caption(
            """
            **Investment Disclaimer:**
            This tool provides educational information only.
            It does not constitute investment advice, financial
            planning services, or securities recommendations.

            **Data Disclaimer:**
            Financial data is delayed 15-20 minutes and sourced
            from Yahoo Finance. AI-generated content may contain
            errors. Always verify with official SEC filings.

            **Liability:**
            Always conduct your own due diligence and consult
            with a licensed financial advisor before making any
            investment decisions.
            """
        )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.caption("Built for long-term fundamental investors 📈")
    with col2:
        st.caption("v1.0.0-beta | Powered by AI")

    # Store in session state for access by other components
    st.session_state.ai_enabled = ai_enabled
    st.session_state.confidence_level = confidence_level

    return ai_enabled, confidence_level
