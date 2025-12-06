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

    # Confidence filter for AI-ranked news
    if use_ml:
        st.markdown("**AI Confidence Filter:**")
        news_confidence = st.select_slider(
            "Show articles with confidence level:",
            options=["Any (show all)", "Medium or higher", "High only"],
            value="Medium or higher",
            help="Filter news recommendations based on AI confidence",
            key="news_confidence_filter",
        )
        # Map to internal values
        news_confidence_map = {
            "Any (show all)": "low",
            "Medium or higher": "medium",
            "High only": "high",
        }
        st.session_state.news_confidence_level = news_confidence_map[news_confidence]

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
    if st.session_state.get("use_ml_ranking", True):
        confidence_filter = st.session_state.get("news_confidence_level", "low")
        confidence_levels = {"low": 0, "medium": 1, "high": 2}
        threshold_level = confidence_levels.get(confidence_filter, 0)

        filtered = []
        for item in news_items:
            item_confidence = item.get("ai_confidence", "low")
            item_level = confidence_levels.get(item_confidence, 0)
            if item_level >= threshold_level:
                filtered.append(item)
        return filtered

    return news_items


def _render_news_items(display_items: list) -> None:
    """Render news items with AI rankings"""
    if st.session_state.get("ai_enabled", True):
        use_ml = st.session_state.get("use_ml_ranking", True)
        if use_ml:
            st.success(f"🤖 AI ranked {len(display_items)} articles by relevance using ML models")
        else:
            st.info(
                f"📊 Ranked {len(display_items)} articles using rule-based scoring (keyword matching, source credibility, recency)"
            )
    else:
        st.info(
            f"📊 Ranked {len(display_items)} articles using rule-based scoring\n\n"
            "Even with AI features off, news is still ranked by:\n"
            "- Keyword relevance to company\n"
            "- Source credibility\n"
            "- Recency and freshness"
        )

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
                col_score, col_coach_btn = st.columns([3, 1])
                with col_score:
                    st.caption(
                        f"Relevance Score: {ai_score:.0%} | Confidence: {ai_confidence.title()}"
                    )
                with col_coach_btn:
                    ai_enabled = st.session_state.get("ai_enabled", True)
                    llm_coach_enabled = st.session_state.get("llm_coach", True)
                    if st.button(
                        "💬 Ask Coach",
                        key=f"coach_news_{idx}",
                        use_container_width=True,
                        disabled=not (ai_enabled and llm_coach_enabled),
                    ):
                        # Store article context separately for the coach
                        st.session_state.news_article_context = {
                            "article_title": title,
                            "article_publisher": publisher,
                            "article_url": link,
                            "article_date": date_str,
                            "article_summary": item.get("summary", ""),
                        }

                        # Create clean auto prompt (article details passed via context)
                        st.session_state.coach_auto_prompt = (
                            "Explain what this news article means for fundamental "
                            "investing and what I should consider when analyzing "
                            "this information."
                        )
                        st.session_state.open_coach = True
                        st.rerun()

            st.markdown(f"[Read more →]({link})")

            with st.expander("🔍 Why is this recommended?", expanded=False):
                ml_details = item.get("ml_details", {})
                use_ml = st.session_state.get("use_ml_ranking", True)
                ai_enabled = st.session_state.get("ai_enabled", True)

                # Show score breakdown when AI is OFF or News ML is OFF
                if not ai_enabled or not use_ml:
                    if "score_breakdown" in ml_details:
                        # Show detailed score breakdown
                        breakdown = ml_details["score_breakdown"]
                        total = 0
                        st.markdown("**📊 Score Breakdown - How this was ranked:**")
                        st.markdown("")
                        for factor, details in breakdown.items():
                            factor_name = factor.replace("_", " ").title()
                            raw = details["raw_score"]
                            weight = details["weight"]
                            contribution = details["contribution"]
                            total += contribution
                            st.markdown(
                                f"- **{factor_name}:** {raw:.1%} × "
                                f"{weight:.0%} weight = **{contribution:.1%}** contribution"
                            )
                        st.markdown(f"\n**Final Score: {total:.1%}**")
                        if not ai_enabled:
                            st.caption(
                                "📐 Using rule-based scoring (keywords, source credibility, recency)"
                            )
                        else:
                            st.caption("📐 Using rule-based scoring (ML models disabled for news)")
                    else:
                        st.info("Score breakdown not available for this article")

                elif ai_enabled and use_ml:
                    # Show AI/ML outputs when AI features are enabled
                    st.markdown("**AI Explanation:**")

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
