"""Sidebar component"""

import streamlit as st


def render_sidebar() -> tuple[bool, str]:
    """
    Render sidebar with settings and AI controls

    Returns:
        Tuple of (ai_enabled, confidence_level)
    """
    with st.sidebar:
        st.markdown("## ⚙️ Settings")

        st.markdown("### 🤖 AI Features")
        ai_enabled = st.checkbox(
            "Enable AI assistance",
            value=True,
            help="Turn on AI-powered news curation and learning guide",
        )

        if ai_enabled:
            st.success("✓ AI features active")
            st.caption(
                "💡 Your interactions help improve recommendations. "
                "No personal data is collected."
            )

            # ML models toggle
            use_ml_ranking = st.checkbox(
                "Use advanced ML models",
                value=True,
                help=(
                    "Enable Hugging Face models for semantic similarity "
                    "and sentiment analysis (requires transformers package)"
                ),
            )
            st.session_state.use_ml_ranking = use_ml_ranking

            if use_ml_ranking:
                st.caption("🧠 Using sentence embeddings & FinBERT sentiment analysis")

            confidence_level = st.select_slider(
                "AI confidence threshold",
                options=["Show all", "Medium+", "High only"],
                value="Show all",
                help="Filter AI suggestions by confidence level",
            )

            if confidence_level != "Show all":
                st.caption(f"Only showing {confidence_level} confidence suggestions")
        else:
            st.info("AI features disabled. Showing raw data only.")
            confidence_level = "Show all"

        st.markdown("---")
        st.markdown("### Display Preferences")
        st.checkbox("Show educational tooltips", value=True)
        st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY"])

        beginner_mode = st.checkbox(
            "Beginner mode", value=False, help="Simplified view with guided explanations"
        )

        if beginner_mode:
            st.caption("🎓 Showing simplified metrics with learning hints")

        st.markdown("---")

        st.markdown(
            '### 🤖 AI Learning Guide <span class="ai-badge">Beta</span>',
            unsafe_allow_html=True,
        )

        if ai_enabled:
            st.markdown(
                """
                **How to use:**
                - Click ❓ next to any metric
                - Get instant explanations
                - Ask follow-up questions (coming soon)

                **Confidence Indicators:**
                - <span class="confidence-high">🟢 High</span>:
                  Well-established concepts
                - <span class="confidence-medium">🟡 Medium</span>:
                  Context-dependent
                - <span class="confidence-low">🔴 Low</span>:
                  Consult an expert
                """,
                unsafe_allow_html=True,
            )

            if "feedback_count" in st.session_state:
                st.caption(
                    f"📊 You've provided {st.session_state.feedback_count} "
                    "pieces of feedback. Thanks!"
                )
        else:
            st.info("Enable AI features above to use the guide")

        st.markdown("---")

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

        st.markdown("---")

        st.markdown("### 📖 Quick Reference")
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

        st.markdown("---")

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
        st.caption("Built for long-term fundamental investors 📈")
        st.caption("v1.0.0-beta | Powered by AI")

    # Store in session state for access by other components
    st.session_state.ai_enabled = ai_enabled
    st.session_state.confidence_level = confidence_level

    return ai_enabled, confidence_level
