"""AI-powered news recommendation and curation utilities"""

import logging
from datetime import datetime
from typing import Any

try:
    import numpy as np

    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    np = None
    logging.warning(
        "Hugging Face models not available. "
        "Install with: pip install transformers sentence-transformers torch"
    )

logger = logging.getLogger(__name__)


class NewsRecommender:
    """AI-powered news recommender with relevance scoring and ranking"""

    def __init__(self, use_ml: bool = True):
        """Initialize the news recommender

        Args:
            use_ml: Use ML models if available (default True)
        """
        self.use_ml = use_ml and HF_AVAILABLE

        # Try to get pre-loaded models from cache
        self.embedding_model = None
        self.sentiment_analyzer = None

        if self.use_ml:
            try:
                # Import model loader
                from utils.model_loader import (
                    get_embedding_model,
                    get_sentiment_model,
                )

                # Try to get cached models first
                self.embedding_model = get_embedding_model()
                self.sentiment_analyzer = get_sentiment_model()

                # If models exist, we're good
                if self.embedding_model and self.sentiment_analyzer:
                    logger.info("Using pre-loaded ML models from cache")
                else:
                    logger.info("ML models not in cache, will load on demand")

            except Exception as e:
                logger.warning("Failed to access ML models: %s", str(e))
                self.use_ml = False

        # When ML is enabled, prioritize ML signals heavily
        self.relevance_weights = {
            "title_match": 0.15 if self.use_ml else 0.3,
            "content_relevance": 0.15 if self.use_ml else 0.25,
            # Increased for better relevance
            "semantic_similarity": 0.35 if self.use_ml else 0.0,
            # Increased to prioritize sentiment
            "ml_sentiment": 0.20 if self.use_ml else 0.0,
            "recency": 0.10 if self.use_ml else 0.2,
            "source_credibility": 0.05 if self.use_ml else 0.15,
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
                score, explanation, ml_details = self._score_article(
                    item, ticker, company_name, user_context
                )
                item["ai_score"] = score
                item["ai_explanation"] = explanation
                # Store raw ML scores for display
                item["ml_details"] = ml_details
                # Calculate confidence using all scores and ML details
                item["ai_confidence"] = self._calculate_confidence(score, item, ml_details)
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
    ) -> tuple[float, dict[str, str], dict[str, Any]]:
        """
        Score a single article based on multiple factors

        Returns:
            tuple: (score, explanation_dict, ml_details_dict)
        """
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        publisher = article.get("publisher", "")
        published_time = article.get("providerPublishTime", 0)

        # Initialize scores and ML details
        scores = {}
        explanations = {}
        ml_details = {}  # Store raw ML model outputs

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

        # 3. ML-based semantic similarity (if available)
        if self.use_ml:
            semantic_score = self._calculate_semantic_similarity(
                ticker, company_name, title, summary
            )
            scores["semantic_similarity"] = semantic_score
            explanations["semantic"] = self._get_semantic_explanation(semantic_score)
            ml_details["semantic_similarity"] = {
                "score": semantic_score,
                "percentage": f"{semantic_score:.1%}",
                "interpretation": self._get_semantic_explanation(semantic_score),
            }

        # 4. ML-based sentiment analysis (if available)
        if self.use_ml:
            (
                ml_sentiment_score,
                sentiment_label,
                sentiment_confidence,
            ) = self._calculate_ml_sentiment(title, summary)
            scores["ml_sentiment"] = ml_sentiment_score
            explanations["ml_sentiment"] = self._get_ml_sentiment_explanation(ml_sentiment_score)
            ml_details["sentiment"] = {
                "label": sentiment_label,
                "confidence": sentiment_confidence,
                "percentage": f"{sentiment_confidence:.1%}",
                "score": ml_sentiment_score,
                "interpretation": self._get_ml_sentiment_explanation(ml_sentiment_score),
            }

        # 5. Recency score
        recency_score = self._calculate_recency_score(published_time)
        scores["recency"] = recency_score
        explanations["recency"] = self._get_recency_explanation(published_time)

        # 6. Source credibility
        credibility_score = self._calculate_source_credibility(publisher)
        scores["source_credibility"] = credibility_score
        explanations["source"] = f"Source: {publisher} (credibility: {credibility_score:.0%})"

        # Calculate weighted total
        total_score = sum(
            scores[key] * self.relevance_weights.get(key, 0.0) for key in scores.keys()
        )

        # Add score breakdown to ml_details
        if self.use_ml:
            ml_details["score_breakdown"] = {
                factor: {
                    "raw_score": scores.get(factor, 0),
                    "weight": self.relevance_weights.get(factor, 0),
                    "contribution": (scores.get(factor, 0) * self.relevance_weights.get(factor, 0)),
                }
                for factor in self.relevance_weights.keys()
                if factor in scores
            }

        return total_score, explanations, ml_details

    def _calculate_semantic_similarity(
        self, ticker: str, company_name: str, title: str, summary: str
    ) -> float:
        """
        Calculate semantic similarity using sentence embeddings

        Returns similarity score between company context and article
        """
        if not self.use_ml or self.embedding_model is None:
            return 0.5

        try:
            # Create company context
            company_context = f"{company_name} {ticker} stock investment financial analysis"
            article_text = f"{title} {summary}"

            # Get embeddings
            embeddings = self.embedding_model.encode([company_context, article_text])

            # Calculate cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )

            # Normalize to 0-1 range (cosine similarity is -1 to 1)
            normalized_score = (similarity + 1) / 2

            return float(normalized_score)
        except Exception as e:
            logger.warning("Semantic similarity calculation failed: %s", str(e))
            return 0.5

    def _get_semantic_explanation(self, score: float) -> str:
        """Generate explanation for semantic similarity score"""
        if score >= 0.7:
            return "Strong semantic relevance to company"
        elif score >= 0.5:
            return "Moderate semantic relevance"
        else:
            return "Low semantic relevance (general market news)"

    def _calculate_ml_sentiment(self, title: str, summary: str) -> tuple[float, str, float]:
        """
        Use FinBERT to analyze financial sentiment

        Returns: (score, label, confidence)
        """
        if not self.use_ml or self.sentiment_analyzer is None:
            return 0.5, "neutral", 0.0

        try:
            text = f"{title}. {summary}"[:512]  # Truncate to model limit

            result = self.sentiment_analyzer(text)[0]
            label = result["label"].lower()
            confidence = result["score"]

            # Map sentiment to score
            if label == "positive":
                # Positive news gets higher score
                score = 0.5 + (confidence * 0.5)
            elif label == "negative":
                # Negative news still valuable but lower score
                score = 0.5 - (confidence * 0.3)
            else:  # neutral
                # Neutral is middle ground
                score = 0.5 + (confidence * 0.2)

            return score, label, confidence
        except Exception as e:
            logger.warning("ML sentiment analysis failed: %s", str(e))
            return 0.5, "neutral", 0.0

    def _get_ml_sentiment_explanation(self, score: float) -> str:
        """Generate explanation for ML sentiment score"""
        if score >= 0.75:
            return "Positive financial sentiment (AI)"
        elif score >= 0.55:
            return "Neutral to positive sentiment (AI)"
        elif score >= 0.35:
            return "Neutral to negative sentiment (AI)"
        else:
            return "Negative financial sentiment (AI)"

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

    def _calculate_confidence(
        self, score: float, article: dict[str, Any], ml_details: dict[str, Any]
    ) -> str:
        """
        Calculate confidence level for the recommendation based on all scoring factors

        Considers:
        - Overall score
        - Source credibility
        - Article completeness (has summary)
        - ML model confidence (semantic similarity & sentiment confidence)
        - Score consistency across factors

        Returns:
            str: 'high', 'medium', or 'low'
        """
        publisher = article.get("publisher", "")
        has_summary = bool(article.get("summary", ""))
        source_credibility = self._calculate_source_credibility(publisher)

        # Start with base confidence from overall score
        confidence_score = 0.0

        # 1. Overall score contribution (40%)
        if score >= 0.7:
            confidence_score += 0.4
        elif score >= 0.5:
            confidence_score += 0.25
        else:
            confidence_score += 0.1

        # 2. Source credibility contribution (20%)
        confidence_score += source_credibility * 0.2

        # 3. Content completeness (10%)
        if has_summary:
            confidence_score += 0.1

        # 4. ML model confidence (30% if available)
        if ml_details and self.use_ml:
            ml_confidence = 0.0

            # Semantic similarity confidence
            if "semantic_similarity" in ml_details:
                semantic_score = ml_details["semantic_similarity"]["score"]
                if semantic_score >= 0.7:
                    ml_confidence += 0.15
                elif semantic_score >= 0.5:
                    ml_confidence += 0.10
                else:
                    ml_confidence += 0.05

            # Sentiment analysis confidence
            if "sentiment" in ml_details:
                sentiment_conf = ml_details["sentiment"]["confidence"]
                # High model confidence = high recommendation confidence
                ml_confidence += sentiment_conf * 0.15

            confidence_score += ml_confidence
        else:
            # If no ML, redistribute that 30% to other factors
            # Boost overall score weight
            if score >= 0.7:
                confidence_score += 0.2
            elif score >= 0.5:
                confidence_score += 0.1

        # 5. Score consistency check (bonus/penalty)
        # If we have ML details, check if scores agree
        if ml_details and "score_breakdown" in ml_details:
            breakdown = ml_details["score_breakdown"]
            raw_scores = [
                details["raw_score"] for details in breakdown.values() if details["raw_score"] > 0
            ]

            if len(raw_scores) >= 3:
                # Calculate variance - low variance = more consistent = higher confidence
                avg_score = sum(raw_scores) / len(raw_scores)
                variance = sum((s - avg_score) ** 2 for s in raw_scores) / len(raw_scores)

                # Low variance (< 0.05) = consistent scores = bonus
                if variance < 0.05:
                    confidence_score += 0.1
                # High variance (> 0.15) = inconsistent = penalty
                elif variance > 0.15:
                    confidence_score -= 0.1

        # Clamp to [0, 1]
        confidence_score = max(0.0, min(1.0, confidence_score))

        # Map to categories
        if confidence_score >= 0.7:
            return "high"
        elif confidence_score >= 0.4:
            return "medium"
        else:
            return "low"

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


def get_recommender(use_ml: bool = True) -> NewsRecommender:
    """
    Factory function to get a NewsRecommender instance

    Args:
        use_ml: Enable ML-powered scoring (default True if models available)

    Returns:
        NewsRecommender instance
    """
    return NewsRecommender(use_ml=use_ml)
