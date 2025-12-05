"""AI-powered news recommendation and curation utilities"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class NewsRecommender:
    """AI-powered news recommender with relevance scoring and ranking"""

    def __init__(self):
        """Initialize the news recommender"""
        self.relevance_weights = {
            "title_match": 0.3,
            "content_relevance": 0.25,
            "recency": 0.2,
            "source_credibility": 0.15,
            "sentiment_balance": 0.1,
        }

        # Trusted financial news sources
        self.credible_sources = {
            "Reuters": 0.95,
            "Bloomberg": 0.95,
            "Wall Street Journal": 0.95,
            "Financial Times": 0.95,
            "CNBC": 0.85,
            "MarketWatch": 0.85,
            "Seeking Alpha": 0.80,
            "The Motley Fool": 0.75,
            "Yahoo Finance": 0.75,
            "Benzinga": 0.70,
            "Barron's": 0.90,
            "Forbes": 0.80,
        }

    def rank_news(
        self,
        news_items: list[dict[str, Any]],
        ticker: str,
        company_name: str = "",
        user_context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Rank news items by relevance and quality

        Args:
            news_items: List of news dictionaries from yfinance
            ticker: Stock ticker symbol
            company_name: Full company name for better matching
            user_context: Optional user preferences and context

        Returns:
            List of news items with scores and explanations, sorted by relevance
        """
        if not news_items:
            return []

        scored_items = []

        for item in news_items:
            try:
                score, explanation = self._score_article(item, ticker, company_name, user_context)
                item["ai_score"] = score
                item["ai_explanation"] = explanation
                item["ai_confidence"] = self._calculate_confidence(score, item)
                scored_items.append(item)
            except Exception as e:
                logger.warning(f"Error scoring article: {e}")
                continue

        # Sort by score descending
        scored_items.sort(key=lambda x: x.get("ai_score", 0), reverse=True)

        return scored_items

    def _score_article(
        self,
        article: dict[str, Any],
        ticker: str,
        company_name: str,
        user_context: dict[str, Any] | None,
    ) -> tuple[float, dict[str, str]]:
        """
        Score a single article based on multiple factors

        Returns:
            tuple: (score, explanation_dict)
        """
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        publisher = article.get("publisher", "")
        published_time = article.get("providerPublishTime", 0)

        # Initialize scores
        scores = {}
        explanations = {}

        # 1. Title and content relevance
        ticker_lower = ticker.lower()
        company_lower = company_name.lower()
        # Extract first word of company name (e.g., "Apple" from "Apple Inc.")
        company_main = company_lower.split()[0] if company_lower else ""

        title_relevance: float = 0.0
        if (
            ticker_lower in title
            or company_lower in title
            or (company_main and company_main in title)
        ):
            title_relevance = 1.0
            explanations["title"] = f"Directly mentions {ticker}"
        elif (
            ticker_lower in summary
            or company_lower in summary
            or (company_main and company_main in summary)
        ):
            title_relevance = 0.7
            explanations["title"] = f"References {ticker} in summary"
        else:
            title_relevance = 0.3
            explanations["title"] = "General market news"

        scores["title_match"] = title_relevance

        # 2. Content relevance (keyword matching)
        content_score = self._calculate_content_relevance(title, summary, user_context)
        scores["content_relevance"] = content_score
        explanations["content"] = self._get_content_explanation(title, summary, user_context)

        # 3. Recency score
        recency_score = self._calculate_recency_score(published_time)
        scores["recency"] = recency_score
        explanations["recency"] = self._get_recency_explanation(published_time)

        # 4. Source credibility
        credibility_score = self._calculate_source_credibility(publisher)
        scores["source_credibility"] = credibility_score
        explanations["source"] = f"Source: {publisher} (credibility: {credibility_score:.0%})"

        # 5. Sentiment balance (avoid extreme bias)
        sentiment_score = self._calculate_sentiment_balance(title, summary)
        scores["sentiment_balance"] = sentiment_score
        explanations["sentiment"] = self._get_sentiment_explanation(sentiment_score)

        # Calculate weighted total
        total_score = sum(scores[key] * self.relevance_weights[key] for key in scores.keys())

        return total_score, explanations

    def _calculate_content_relevance(
        self, title: str, summary: str, user_context: dict[str, Any] | None
    ) -> float:
        """Calculate relevance based on content keywords"""
        text = f"{title} {summary}"

        # Financial statement keywords
        financial_keywords = [
            "earnings",
            "revenue",
            "profit",
            "loss",
            "quarter",
            "q1",
            "q2",
            "q3",
            "q4",
            "fiscal",
            "guidance",
            "outlook",
            "forecast",
        ]

        # Company development keywords
        development_keywords = [
            "product",
            "launch",
            "partnership",
            "acquisition",
            "merger",
            "expansion",
            "investment",
            "innovation",
            "contract",
            "deal",
        ]

        # Market/analysis keywords
        analysis_keywords = [
            "analysis",
            "upgrade",
            "downgrade",
            "target",
            "rating",
            "analyst",
            "valuation",
            "price",
        ]

        # Count matches
        financial_matches = sum(1 for kw in financial_keywords if kw in text)
        development_matches = sum(1 for kw in development_keywords if kw in text)
        analysis_matches = sum(1 for kw in analysis_keywords if kw in text)

        total_matches = financial_matches + development_matches + analysis_matches

        # Score based on matches (diminishing returns)
        if total_matches >= 5:
            return 1.0
        elif total_matches >= 3:
            return 0.8
        elif total_matches >= 1:
            return 0.6
        else:
            return 0.3

    def _get_content_explanation(
        self, title: str, summary: str, user_context: dict[str, Any] | None
    ) -> str:
        """Generate human-readable content explanation"""
        text = f"{title} {summary}"

        topics = []
        if any(kw in text for kw in ["earnings", "revenue", "profit", "quarter"]):
            topics.append("financial results")
        if any(kw in text for kw in ["product", "launch", "partnership", "acquisition"]):
            topics.append("business developments")
        if any(kw in text for kw in ["analyst", "upgrade", "downgrade", "rating"]):
            topics.append("analyst coverage")

        if topics:
            return f"Covers: {', '.join(topics)}"
        return "General company news"

    def _calculate_recency_score(self, published_time: int) -> float:
        """Calculate score based on article freshness"""
        if not published_time:
            return 0.3

        try:
            published_date = datetime.fromtimestamp(published_time)
            now = datetime.now()
            age_hours = (now - published_date).total_seconds() / 3600

            # Decay function: newer is better
            if age_hours < 6:
                return 1.0
            elif age_hours < 24:
                return 0.9
            elif age_hours < 72:  # 3 days
                return 0.7
            elif age_hours < 168:  # 1 week
                return 0.5
            elif age_hours < 720:  # 1 month
                return 0.3
            else:
                return 0.1
        except Exception:
            return 0.3

    def _get_recency_explanation(self, published_time: int) -> str:
        """Generate human-readable recency explanation"""
        if not published_time:
            return "Unknown publication date"

        try:
            published_date = datetime.fromtimestamp(published_time)
            now = datetime.now()
            age_hours = (now - published_date).total_seconds() / 3600

            if age_hours < 6:
                return "Published in last 6 hours"
            elif age_hours < 24:
                return "Published today"
            elif age_hours < 72:
                return "Published in last 3 days"
            elif age_hours < 168:
                return "Published this week"
            else:
                days = int(age_hours / 24)
                return f"Published {days} days ago"
        except Exception:
            return "Unknown publication date"

    def _calculate_source_credibility(self, publisher: str) -> float:
        """Calculate credibility score based on publisher"""
        # Check if publisher matches known credible sources
        for source, score in self.credible_sources.items():
            if source.lower() in publisher.lower():
                return score

        # Default for unknown sources
        return 0.5

    def _calculate_sentiment_balance(self, title: str, summary: str) -> float:
        """
        Calculate sentiment balance score
        Returns higher score for balanced/neutral content, lower for extreme sentiment
        """
        text = f"{title} {summary}".lower()

        # Positive sentiment words
        positive_words = [
            "soars",
            "surges",
            "jumps",
            "rallies",
            "gains",
            "record",
            "breakthrough",
            "success",
            "wins",
            "beats",
        ]

        # Negative sentiment words
        negative_words = [
            "plummets",
            "crashes",
            "tumbles",
            "slumps",
            "falls",
            "fails",
            "loses",
            "crisis",
            "warning",
            "misses",
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        total_sentiment = positive_count + negative_count

        if total_sentiment == 0:
            return 1.0  # Neutral is good

        # Balance score: closer to 0.5 = more balanced
        if total_sentiment > 0:
            balance = min(positive_count, negative_count) / total_sentiment
            return balance
        else:
            return 1.0

    def _get_sentiment_explanation(self, sentiment_score: float) -> str:
        """Generate human-readable sentiment explanation"""
        if sentiment_score >= 0.8:
            return "Balanced, objective tone"
        elif sentiment_score >= 0.5:
            return "Moderate sentiment bias"
        else:
            return "Strong sentiment (consider multiple sources)"

    def _calculate_confidence(self, score: float, article: dict[str, Any]) -> str:
        """
        Calculate confidence level for the recommendation

        Returns:
            str: 'high', 'medium', or 'low'
        """
        publisher = article.get("publisher", "")
        has_summary = bool(article.get("summary", ""))

        # High confidence: high score + credible source + has summary
        if score >= 0.7 and self._calculate_source_credibility(publisher) >= 0.8 and has_summary:
            return "high"
        # Low confidence: low score or unknown source
        elif score < 0.4 or self._calculate_source_credibility(publisher) < 0.5:
            return "low"
        else:
            return "medium"

    def filter_by_category(
        self, news_items: list[dict[str, Any]], category: str
    ) -> list[dict[str, Any]]:
        """
        Filter news items by category

        Args:
            news_items: List of news dictionaries
            category: Category name ('Earnings Reports', 'Press Releases', 'Market Analysis')

        Returns:
            Filtered list of news items
        """
        if category == "All News":
            return news_items

        filter_keywords = {
            "Earnings Reports": [
                "earnings",
                "results",
                "quarter",
                "q1",
                "q2",
                "q3",
                "q4",
                "fiscal",
                "revenue",
                "profit",
            ],
            "Press Releases": [
                "press release",
                "announces",
                "announcement",
                "unveils",
                "launches",
                "introduces",
            ],
            "Market Analysis": [
                "analysis",
                "market",
                "outlook",
                "forecast",
                "trend",
                "analyst",
                "upgrade",
                "downgrade",
                "target",
            ],
        }

        keywords = filter_keywords.get(category, [])
        if not keywords:
            return news_items

        filtered = []
        for item in news_items:
            title = item.get("title", "").lower()
            summary = item.get("summary", "").lower()
            text = f"{title} {summary}"

            if any(kw.lower() in text for kw in keywords):
                filtered.append(item)

        return filtered


def get_recommender() -> NewsRecommender:
    """Factory function to get a NewsRecommender instance"""
    return NewsRecommender()
