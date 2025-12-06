"""News section component with AI ranking"""

import logging
from datetime import datetime

import streamlit as st

from utils.data_fetcher import get_news
from utils.news_ai import get_recommender

# Set up logger
logger = logging.getLogger(__name__)


def _record_feedback(item: dict, feedback_type: str, note: str) -> None:
    """
    Record user feedback on AI recommendations

    Args:
        item: News item that received feedback
        feedback_type: Type of feedback (helpful, not_helpful, unclear)
        note: Description of the feedback
    """
    # Initialize feedback storage in session state
    if "news_feedback" not in st.session_state:
        st.session_state.news_feedback = []

    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "article_title": item.get("title", "Unknown"),
        "article_link": item.get("link", ""),
        "feedback_type": feedback_type,
        "note": note,
        "ai_score": item.get("ai_score", 0),
        "ai_confidence": item.get("ai_confidence", "unknown"),
    }

    st.session_state.news_feedback.append(feedback_entry)

    # Log feedback for monitoring
    logger.info(f"News feedback received: {feedback_type} for '{item.get('title', 'Unknown')}'")


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

    # Get ML preference from session state (default True)
    use_ml = st.session_state.get("use_ml_ranking", True)
    recommender = get_recommender(use_ml=use_ml)

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
            st.warning(
                "📰 No recent news available from data provider. "
                "Check the company's investor relations page or major financial news sites."
            )


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

    # Create scrollable container for news items
    st.markdown(
        """
        <style>
        .news-container {
            max-height: 600px;
            overflow-y: auto;
            padding-right: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Wrap all news items in a scrollable container
    news_html = '<div class="news-container">'
    st.markdown(news_html, unsafe_allow_html=True)

    for idx, item in enumerate(display_items, 1):
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

                    # Show ML model outputs directly if available
                    ml_details = item.get("ml_details", {})
                    use_ml = st.session_state.get("use_ml_ranking", True)

                    if use_ml and ml_details:
                        st.markdown("### 🧠 ML Model Outputs")

                        # Semantic Similarity Score
                        if "semantic_similarity" in ml_details:
                            sem = ml_details["semantic_similarity"]
                            st.markdown(
                                f"**📊 Semantic Similarity:** "
                                f"{sem['percentage']} ({sem['interpretation']})"
                            )
                            st.progress(sem["score"])

                        # Sentiment Analysis
                        if "sentiment" in ml_details:
                            sent = ml_details["sentiment"]
                            sentiment_emoji = {"positive": "📈", "negative": "📉", "neutral": "➖"}
                            emoji = sentiment_emoji.get(sent["label"], "❓")
                            st.markdown(
                                f"**{emoji} FinBERT Sentiment:** "
                                f"{sent['label'].title()} "
                                f"({sent['percentage']} confidence)"
                            )
                            st.progress(sent["confidence"])
                            st.caption(sent["interpretation"])

                        st.markdown("---")
                        st.markdown("### 📋 Scoring Breakdown")

                        # Score breakdown table
                        if "score_breakdown" in ml_details:
                            breakdown = ml_details["score_breakdown"]
                            for factor, details in breakdown.items():
                                factor_name = factor.replace("_", " ").title()
                                raw = details["raw_score"]
                                weight = details["weight"]
                                contribution = details["contribution"]
                                st.markdown(
                                    f"- **{factor_name}:** {raw:.1%} × "
                                    f"{weight:.0%} = {contribution:.1%}"
                                )

                        st.markdown("---")

                    st.markdown("**Other Factors:**")
                    for factor, explanation in ai_explanation.items():
                        st.markdown(f"- **{factor.title()}**: {explanation}")

                    st.markdown("---")
                    st.caption(f"Overall relevance: {ai_score:.0%} | Confidence: {ai_confidence}")

                    # Show confidence explanation
                    confidence_explanations = {
                        "high": (
                            "🟢 High confidence based on: strong relevance "
                            "score, credible source, complete article"
                        ),
                        "medium": ("🟡 Medium confidence - some factors may be uncertain"),
                        "low": ("🔴 Low confidence - limited information or weak signals"),
                    }
                    if use_ml and ml_details:
                        # Enhanced explanation with ML factors
                        ml_conf_factors = []
                        if "semantic_similarity" in ml_details:
                            sem_score = ml_details["semantic_similarity"]["score"]
                            if sem_score >= 0.7:
                                ml_conf_factors.append("strong semantic match")
                            elif sem_score >= 0.5:
                                ml_conf_factors.append("moderate semantic match")
                        if "sentiment" in ml_details:
                            sent_conf = ml_details["sentiment"]["confidence"]
                            if sent_conf >= 0.8:
                                ml_conf_factors.append("high sentiment confidence")

                        if ml_conf_factors:
                            st.caption(
                                f"{confidence_explanations.get(ai_confidence, '')} "
                                f"+ {', '.join(ml_conf_factors)}"
                            )
                        else:
                            st.caption(confidence_explanations.get(ai_confidence, ""))
                    else:
                        st.caption(confidence_explanations.get(ai_confidence, ""))

                    st.markdown("---")

                    if use_ml:
                        st.caption(
                            "🧠 ML models: Sentence embeddings (semantic) + FinBERT (sentiment)"
                        )
                    else:
                        st.caption(
                            "💡 AI considers: topic relevance, recency, "
                            "source credibility, and sentiment balance"
                        )

                    # Feedback buttons
                    st.markdown("**Was this explanation helpful?**")
                    feedback_cols = st.columns([1, 1, 1, 3])
                    feedback_key = f"news_feedback_{idx}"

                    with feedback_cols[0]:
                        if st.button("👍 Yes", key=f"{feedback_key}_yes"):
                            _record_feedback(item, "helpful", "User found explanation helpful")
                            st.success("Thanks!")

                    with feedback_cols[1]:
                        if st.button("👎 No", key=f"{feedback_key}_no"):
                            _record_feedback(
                                item, "not_helpful", "User found explanation unhelpful"
                            )
                            st.info("Thanks for the feedback!")

                    with feedback_cols[2]:
                        if st.button("🤔 Unclear", key=f"{feedback_key}_unclear"):
                            _record_feedback(item, "unclear", "User found explanation unclear")
                            st.info("We'll work on clarity!")
                else:
                    st.caption("Enable AI features in the sidebar to see detailed recommendations")

            st.markdown("---")

    # Close the scrollable container
    st.markdown("</div>", unsafe_allow_html=True)
