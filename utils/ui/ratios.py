"""Financial ratios component"""

import math
from datetime import datetime

import streamlit as st

from utils.ratio_calculator import (
    calculate_5yr_average,
    format_ratio_value,
    get_industry_comparison,
    get_ratio_metrics,
)


def log_feedback(feedback_type: str, context: dict, sentiment: str = "neutral") -> None:
    """Track user feedback for AI improvements"""
    if "interaction_log" in st.session_state:
        st.session_state.interaction_log.append(
            {
                "timestamp": datetime.now(),
                "type": feedback_type,
                "context": context,
                "sentiment": sentiment,
            }
        )
    if "feedback_count" in st.session_state:
        st.session_state.feedback_count += 1


def render_ratios_section(
    ratios: dict,
    company_name: str,
    search_query: str,
    info: dict,
    income_stmt=None,
    balance_sheet=None,
) -> None:
    """
    Render financial ratios section with AI guide

    Args:
        ratios: Dictionary of calculated ratios
        company_name: Company name
        search_query: Search query string
        info: Stock info dictionary for comparison data
        income_stmt: Income statement DataFrame for 5yr averages
        balance_sheet: Balance sheet DataFrame for 5yr averages
    """
    st.markdown("### 📐 Key Financial Ratios")
    st.markdown("*Compare company performance to industry trends*")

    ratio_category = st.selectbox(
        "Select Ratio Category",
        ["Profitability", "Liquidity", "Efficiency", "Leverage", "Valuation"],
        key=f"ratio_category_{search_query}",
    )

    info_text, metrics_list = get_ratio_metrics(ratio_category)

    st.markdown(f"#### {ratio_category} Ratios")
    st.info(info_text)

    # Calculate comparison data with loading indicator
    with st.spinner("📊 Calculating industry benchmarks..."):
        five_yr_avg = calculate_5yr_average(info, income_stmt, balance_sheet)

    # Filter out metrics that have no data (N/A)
    available_metrics = [
        (ratio_key, ratio_display)
        for ratio_key, ratio_display in metrics_list
        if ratios.get(ratio_key) is not None
    ]

    if not available_metrics:
        st.warning(
            f"⚠️ No {ratio_category.lower()} ratio data currently available for {company_name}. "
            "This may be due to missing financial statement data or recent IPO."
        )
        return

    for ratio_key, ratio_display in available_metrics:
        value = ratios.get(ratio_key)
        formatted_value = format_ratio_value(value, ratio_key)

        # Get comparison values
        industry_avg = get_industry_comparison(info, ratio_key)
        yr5_avg = five_yr_avg.get(ratio_key)

        col_m1, col_m2, col_m3, col_m4 = st.columns([3, 2, 2, 1])
        with col_m1:
            st.metric(ratio_display, formatted_value)
        with col_m2:
            # Check for valid number (not None and not NaN)
            is_valid_industry = industry_avg is not None and not (
                isinstance(industry_avg, float) and math.isnan(industry_avg)
            )
            if is_valid_industry:
                ind_formatted = format_ratio_value(industry_avg, ratio_key)
                st.caption(f"vs Industry: {ind_formatted}")
            else:
                st.caption("vs Industry: Coming soon")
        with col_m3:
            # Check for valid number (not None and not NaN)
            is_valid_5yr = yr5_avg is not None and not (
                isinstance(yr5_avg, float) and math.isnan(yr5_avg)
            )
            if is_valid_5yr:
                avg_formatted = format_ratio_value(yr5_avg, ratio_key)
                st.caption(f"vs 5Y Avg: {avg_formatted}")
            else:
                st.caption("vs 5Y Avg: Coming soon")
        with col_m4:
            help_key = f"help_{ratio_key}_{search_query}"
            if st.button("❓", key=help_key, help="Ask guide about this"):
                st.session_state[f"guide_query_{ratio_key}"] = True

        if st.session_state.get(f"guide_query_{ratio_key}", False):
            _render_ratio_explanation(
                ratio_key, ratio_display, company_name, formatted_value, search_query
            )


def _render_ratio_explanation(
    ratio_key: str,
    ratio_display: str,
    company_name: str,
    formatted_value: str,
    search_query: str,
) -> None:
    """Render ratio explanation expander"""
    with st.expander(f"💡 Learn about {ratio_display}", expanded=True):
        st.markdown('<span class="ai-badge">AI Guide</span>', unsafe_allow_html=True)

        ratio_explanations = {
            "ROE": f"""
                **Return on Equity (ROE)** measures how efficiently
                {company_name} uses shareholder money to generate profit.

                **Calculation:** Net Income ÷ Shareholder Equity

                **{company_name}'s ROE:** {formatted_value}

                **What this means:**
                - ROE > 15%: Generally considered good
                - ROE < 10%: May indicate inefficiency
                - Compare to industry peers for context

                💡 *This is educational content.
                AI guide will provide deeper, contextual analysis.*
            """,
            "ROA": f"""
                **Return on Assets (ROA)** shows how profitable
                {company_name} is relative to its total assets.

                **Calculation:** Net Income ÷ Total Assets

                **{company_name}'s ROA:** {formatted_value}

                💡 *AI guide will provide sector-specific benchmarks.*
            """,
        }

        explanation = ratio_explanations.get(
            ratio_key,
            f"""
            **{ratio_display}** for {company_name}: {formatted_value}

            💡 *AI guide coming soon with detailed explanations!*
            """,
        )

        st.markdown(explanation)

        col_f1, col_f2, col_f3 = st.columns([1, 1, 3])
        with col_f1:
            if st.button("👍 Helpful", key=f"helpful_{ratio_key}_{search_query}"):
                log_feedback(
                    "guide_explanation",
                    {"ratio": ratio_key, "ticker": search_query},
                    "positive",
                )
                st.success("Thanks for the feedback!")
        with col_f2:
            if st.button("👎 Not helpful", key=f"not_helpful_{ratio_key}_{search_query}"):
                log_feedback(
                    "guide_explanation",
                    {"ratio": ratio_key, "ticker": search_query},
                    "negative",
                )
                st.info("We'll improve this explanation!")

        if st.button("✕ Close", key=f"close_{ratio_key}_{search_query}"):
            st.session_state[f"guide_query_{ratio_key}"] = False
            st.rerun()
