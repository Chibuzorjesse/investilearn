"""News section component with AI ranking"""

from datetime import datetime

import streamlit as st

from utils.data_fetcher import get_news
from utils.news_ai import get_recommender


def render_news_section(search_query: str, company_name: str) -> None:
    """
    Render news section with AI-powered ranking

    Args:
        search_query: Ticker symbol
        company_name: Full company name
    """
    st.markdown(
        '### 📰 Relevant News & Updates <span class="ai-badge">AI Powered</span>',
        unsafe_allow_html=True,
    )
    st.markdown("*AI-curated news based on relevance and quality*")

    news_items = get_news(search_query, max_items=20)
    recommender = get_recommender()

    news_filter = st.radio(
        "News Type",
        ["All News", "Earnings Reports", "Press Releases", "Market Analysis"],
        horizontal=True,
    )

    # AI-rank the news
    if news_items:
        ranked_news = recommender.rank_news(
            news_items,
            search_query,
            company_name,
            user_context=None,
        )

        if news_filter != "All News":
            filtered_news_items = recommender.filter_by_category(ranked_news, news_filter)
        else:
            filtered_news_items = ranked_news
    else:
        filtered_news_items = []

    st.markdown("#### Top Stories")

    if filtered_news_items:
        display_items = _filter_by_confidence(filtered_news_items)
        _render_news_items(display_items)
    else:
        if news_filter != "All News":
            st.info(f"No {news_filter.lower()} found for this ticker")
        else:
            st.info("No recent news available for this ticker")


def _filter_by_confidence(news_items: list) -> list:
    """Filter news items by confidence level"""
    if st.session_state.get("ai_enabled", True):
        confidence_filter = st.session_state.get("confidence_level", "Show all")

        if confidence_filter == "Medium+":
            return [item for item in news_items if item.get("ai_confidence") in ["high", "medium"]]
        elif confidence_filter == "High only":
            return [item for item in news_items if item.get("ai_confidence") == "high"]

    return news_items


def _render_news_items(display_items: list) -> None:
    """Render news items with AI rankings"""
    if st.session_state.get("ai_enabled", True):
        st.success(f"🤖 AI ranked {len(display_items)} articles by relevance")
    else:
        st.caption("📊 Showing chronological news (AI disabled)")

    for idx, item in enumerate(display_items[:5], 1):
        with st.container():
            title = item.get("title", "No title available")
            publisher = item.get("publisher", "Unknown source")
            link = item.get("link", "#")
            published_time = item.get("providerPublishTime", 0)

            ai_score = item.get("ai_score", 0)
            ai_confidence = item.get("ai_confidence", "medium")
            ai_explanation = item.get("ai_explanation", {})

            if published_time:
                date_str = datetime.fromtimestamp(published_time).strftime("%B %d, %Y")
            else:
                date_str = "Recent"

            confidence_badges = {
                "high": "🟢",
                "medium": "🟡",
                "low": "🔴",
            }
            badge = confidence_badges.get(ai_confidence, "⚪")

            st.markdown(f"**{badge} #{idx}: {title}**")
            st.caption(f"{publisher} • {date_str}")

            if st.session_state.get("ai_enabled", True):
                st.caption(f"Relevance Score: {ai_score:.0%} | Confidence: {ai_confidence.title()}")

            st.markdown(f"[Read more →]({link})")

            with st.expander("🔍 Why is this recommended?", expanded=False):
                if st.session_state.get("ai_enabled", True):
                    st.markdown("**AI Explanation:**")
                    for factor, explanation in ai_explanation.items():
                        st.markdown(f"- **{factor.title()}**: {explanation}")
                    st.markdown("---")
                    st.caption(f"Overall relevance: {ai_score:.0%} | Confidence: {ai_confidence}")
                    st.caption(
                        "💡 AI considers: topic relevance, recency, "
                        "source credibility, and sentiment balance"
                    )
                else:
                    st.caption("Enable AI features in the sidebar to see detailed recommendations")

            st.markdown("---")
