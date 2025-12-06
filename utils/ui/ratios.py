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


def _get_performance_indicator(ratio_key, value, industry_avg, yr5_avg):
    """
    Determine performance indicator (emoji, color, tooltip) for a ratio

    Returns:
        dict: {"emoji": str, "color": str, "tooltip": str}
    """
    # Default neutral
    result = {"emoji": "●", "color": "#666", "tooltip": "Ratio value"}

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return result

    # Higher is better ratios
    higher_is_better = {
        "ROE",
        "ROA",
        "Net Profit Margin",
        "Gross Profit Margin",
        "Current Ratio",
        "Quick Ratio",
        "Asset Turnover",
        "Inventory Turnover",
        "Interest Coverage",
    }

    # Lower is better ratios
    lower_is_better = {"Days Sales Outstanding", "Debt to Equity", "Debt Ratio"}

    # Valuation ratios (context dependent, lower often better)
    valuation_ratios = {"P/E Ratio", "P/B Ratio", "PEG Ratio", "Price to Sales"}

    # Compare with industry if available
    has_industry = industry_avg is not None and not (
        isinstance(industry_avg, float) and math.isnan(industry_avg)
    )

    if ratio_key in higher_is_better and has_industry:
        if value > industry_avg * 1.1:  # 10% better than industry
            result = {
                "emoji": "●",
                "color": "#10b981",
                "tooltip": f"Strong: {value:.2f} vs industry {industry_avg:.2f}",
            }
        elif value > industry_avg * 0.9:  # Within 10%
            result = {
                "emoji": "●",
                "color": "#f59e0b",
                "tooltip": f"On par: {value:.2f} vs industry {industry_avg:.2f}",
            }
        else:
            result = {
                "emoji": "●",
                "color": "#ef4444",
                "tooltip": f"Below: {value:.2f} vs industry {industry_avg:.2f}",
            }
    elif ratio_key in lower_is_better and has_industry:
        if value < industry_avg * 0.9:  # 10% better (lower)
            result = {
                "emoji": "●",
                "color": "#10b981",
                "tooltip": f"Strong: {value:.2f} vs industry {industry_avg:.2f}",
            }
        elif value < industry_avg * 1.1:  # Within 10%
            result = {
                "emoji": "●",
                "color": "#f59e0b",
                "tooltip": f"On par: {value:.2f} vs industry {industry_avg:.2f}",
            }
        else:
            result = {
                "emoji": "●",
                "color": "#ef4444",
                "tooltip": f"Above: {value:.2f} vs industry {industry_avg:.2f}",
            }
    elif ratio_key in valuation_ratios and has_industry:
        # For valuation, lower is generally better
        if value < industry_avg * 0.9:
            result = {
                "emoji": "●",
                "color": "#10b981",
                "tooltip": f"Undervalued: {value:.2f} vs industry {industry_avg:.2f}",
            }
        elif value < industry_avg * 1.1:
            result = {
                "emoji": "●",
                "color": "#f59e0b",
                "tooltip": f"Fair value: {value:.2f} vs industry {industry_avg:.2f}",
            }
        else:
            result = {
                "emoji": "●",
                "color": "#ef4444",
                "tooltip": f"Overvalued: {value:.2f} vs industry {industry_avg:.2f}",
            }

    return result


def _get_contextual_explanation(ratio_key, value, industry_avg, yr5_avg, performance_indicator):
    """Generate contextual explanation for ratio performance"""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None

    color = performance_indicator["color"]

    # Build explanation based on available comparisons
    parts = []

    # Check if we have industry data
    has_industry = industry_avg is not None and not (
        isinstance(industry_avg, float) and math.isnan(industry_avg)
    )

    # Check if we have 5Y data
    has_5yr = yr5_avg is not None and not (isinstance(yr5_avg, float) and math.isnan(yr5_avg))

    # Common baseline benchmarks for specific ratios
    baseline_benchmarks = {
        "Current Ratio": (2.0, "healthy"),
        "Quick Ratio": (1.0, "healthy"),
        "Debt to Equity": (1.0, "moderate"),
        "Debt Ratio": (0.5, "moderate"),
        "Interest Coverage": (3.0, "safe"),
        "ROE": (15.0, "good"),
        "ROA": (5.0, "good"),
        "Net Profit Margin": (10.0, "good"),
    }

    # Check against baseline if applicable
    if ratio_key in baseline_benchmarks:
        baseline, label = baseline_benchmarks[ratio_key]
        if ratio_key in ["Debt to Equity", "Debt Ratio"]:
            # Lower is better for debt ratios
            if value < baseline:
                parts.append(f"● Below {label} level ({baseline:.1f}) - Low debt risk")
            elif value < baseline * 1.5:
                parts.append(f"● Near {label} level ({baseline:.1f}) - Acceptable debt")
            else:
                parts.append(f"● Above {label} level ({baseline:.1f}) - High leverage")
        else:
            # Higher is better for most ratios
            if value > baseline:
                parts.append(f"● Above {label} level ({baseline:.1f}) - Strong position")
            elif value > baseline * 0.7:
                parts.append(f"● Near {label} level ({baseline:.1f}) - Acceptable")
            else:
                parts.append(f"● Below {label} level ({baseline:.1f}) - Needs attention")

    # Industry comparison
    if has_industry:
        ind_formatted = format_ratio_value(industry_avg, ratio_key)

        # For valuation ratios, the interpretation is reversed
        is_valuation = ratio_key in {"P/E Ratio", "P/B Ratio", "PEG Ratio", "Price to Sales"}

        if color == "#10b981":  # Green
            if is_valuation:
                parts.append(f"● Below industry average ({ind_formatted}) - Undervalued")
            else:
                parts.append(f"● Outperforming industry average ({ind_formatted})")
        elif color == "#f59e0b":  # Yellow
            if is_valuation:
                parts.append(f"● Near industry average ({ind_formatted}) - Fair value")
            else:
                parts.append(f"● Matching industry average ({ind_formatted})")
        else:  # Red
            if is_valuation:
                parts.append(f"● Above industry average ({ind_formatted}) - Overvalued")
            else:
                parts.append(f"● Below industry average ({ind_formatted})")

    # 5-year trend
    if has_5yr:
        yr5_formatted = format_ratio_value(yr5_avg, ratio_key)
        diff_pct = ((value - yr5_avg) / yr5_avg * 100) if yr5_avg != 0 else 0
        if abs(diff_pct) < 5:
            parts.append(f"● Stable vs 5Y average ({yr5_formatted})")
        elif diff_pct > 10:
            parts.append(f"● Up {diff_pct:.0f}% vs 5Y average ({yr5_formatted}) - Improving")
        elif diff_pct > 0:
            parts.append(f"● Up {diff_pct:.0f}% vs 5Y average ({yr5_formatted})")
        elif diff_pct < -10:
            parts.append(f"● Down {abs(diff_pct):.0f}% vs 5Y average ({yr5_formatted}) - Declining")
        else:
            parts.append(f"● Down {abs(diff_pct):.0f}% vs 5Y average ({yr5_formatted})")

    if parts:
        return "<br>".join(parts)

    return None


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

    # Check if this is valuation category (no 5Y avg)
    valuation_ratios = {"P/E Ratio", "P/B Ratio", "PEG Ratio", "Price to Sales"}

    for ratio_key, ratio_display in available_metrics:
        value = ratios.get(ratio_key)
        formatted_value = format_ratio_value(value, ratio_key)

        # Get comparison values
        industry_avg = get_industry_comparison(info, ratio_key)
        yr5_avg = five_yr_avg.get(ratio_key)

        # Determine if this ratio is good (for coloring)
        performance_indicator = _get_performance_indicator(ratio_key, value, industry_avg, yr5_avg)

        # Display with larger fonts and colors
        is_valuation = ratio_key in valuation_ratios

        st.markdown(f"**{ratio_display}**")

        col4 = None  # Initialize for type checker
        if is_valuation:
            # For valuation: only show value and industry comparison
            col1, col2, col3 = st.columns([2, 2, 1])
        else:
            # For others: show value, industry, and 5Y avg
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        with col1:
            # Main value with performance indicator
            emoji = performance_indicator["emoji"]
            color = performance_indicator["color"]
            tooltip = performance_indicator["tooltip"]

            st.markdown(
                f'<h2 style="margin:0; color:{color};" title="{tooltip}">'
                f"{emoji} {formatted_value}</h2>",
                unsafe_allow_html=True,
            )

        with col2:
            # Industry comparison
            is_valid_industry = industry_avg is not None and not (
                isinstance(industry_avg, float) and math.isnan(industry_avg)
            )
            if is_valid_industry:
                ind_formatted = format_ratio_value(industry_avg, ratio_key)
                st.markdown(
                    f'<p style="font-size:1.2em; margin:0;">vs Industry: <b>{ind_formatted}</b></p>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("vs Industry: Coming soon")

        with col3:
            if not is_valuation:
                # 5Y average (only for non-valuation ratios)
                is_valid_5yr = yr5_avg is not None and not (
                    isinstance(yr5_avg, float) and math.isnan(yr5_avg)
                )
                if is_valid_5yr:
                    avg_formatted = format_ratio_value(yr5_avg, ratio_key)
                    st.markdown(
                        f'<p style="font-size:1.2em; margin:0;">vs 5Y Avg: <b>{avg_formatted}</b></p>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("vs 5Y Avg: Coming soon")
            else:
                # Help button for valuation ratios
                help_key = f"help_{ratio_key}_{search_query}"
                if st.button("❓", key=help_key, help="Learn more"):
                    st.session_state[f"guide_query_{ratio_key}"] = True

        if not is_valuation:
            # col4 is guaranteed to be defined when is_valuation is False
            assert col4 is not None  # nosec B101
            with col4:
                # Help button for non-valuation ratios
                help_key = f"help_{ratio_key}_{search_query}"
                if st.button("❓", key=help_key, help="Learn more"):
                    st.session_state[f"guide_query_{ratio_key}"] = True

        # Add contextual explanation
        explanation = _get_contextual_explanation(
            ratio_key, value, industry_avg, yr5_avg, performance_indicator
        )
        if explanation:
            st.markdown(
                f'<div style="font-size:0.9em; color:#888; line-height:1.6;">{explanation}</div>',
                unsafe_allow_html=True,
            )
            st.caption("💡 Want to learn more? Click ❓ above")

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
