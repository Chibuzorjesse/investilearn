"""Tests for news_ai module"""

from datetime import datetime, timedelta

import pytest

from utils.news_ai import NewsRecommender, get_recommender


@pytest.fixture
def sample_news_items():
    """Sample news items for testing"""
    now = datetime.now()
    return [
        {
            "title": "Apple Reports Record Q4 Earnings Beat Expectations",
            "summary": "Apple Inc. reported quarterly revenue of $90B, beating analyst estimates",
            "publisher": "Reuters",
            "link": "https://example.com/news1",
            "providerPublishTime": int(now.timestamp()),
        },
        {
            "title": "Tech Stocks Rally on Market Optimism",
            "summary": "Broader market trends show positive momentum across tech sector",
            "publisher": "Yahoo Finance",
            "link": "https://example.com/news2",
            "providerPublishTime": int((now - timedelta(days=2)).timestamp()),
        },
        {
            "title": "Apple Announces New Product Launch Event",
            "summary": "Company unveils plans for major product announcements next month",
            "publisher": "Bloomberg",
            "link": "https://example.com/news3",
            "providerPublishTime": int((now - timedelta(hours=6)).timestamp()),
        },
        {
            "title": "Analyst Upgrades Apple Stock to Buy",
            "summary": "Major investment firm raises price target citing strong fundamentals",
            "publisher": "MarketWatch",
            "link": "https://example.com/news4",
            "providerPublishTime": int((now - timedelta(days=7)).timestamp()),
        },
        {
            "title": "General Market News About Technology",
            "summary": "Broad discussion of technology trends without specific company focus",
            "publisher": "Unknown Blog",
            "link": "https://example.com/news5",
            "providerPublishTime": int((now - timedelta(days=30)).timestamp()),
        },
    ]


class TestNewsRecommender:
    """Test suite for NewsRecommender class"""

    def test_init(self):
        """Test NewsRecommender initialization"""
        recommender = NewsRecommender()
        assert recommender is not None
        assert len(recommender.relevance_weights) == 5
        assert len(recommender.credible_sources) > 0

    def test_get_recommender_factory(self):
        """Test factory function"""
        recommender = get_recommender()
        assert isinstance(recommender, NewsRecommender)

    def test_rank_news_empty_list(self):
        """Test ranking with empty news list"""
        recommender = NewsRecommender()
        result = recommender.rank_news([], "AAPL", "Apple Inc.")
        assert result == []

    def test_rank_news_basic(self, sample_news_items):
        """Test basic news ranking"""
        recommender = NewsRecommender()
        ranked = recommender.rank_news(sample_news_items, "AAPL", "Apple Inc.")

        assert len(ranked) == len(sample_news_items)
        assert all("ai_score" in item for item in ranked)
        assert all("ai_explanation" in item for item in ranked)
        assert all("ai_confidence" in item for item in ranked)

    def test_rank_news_sorting(self, sample_news_items):
        """Test that news is sorted by score descending"""
        recommender = NewsRecommender()
        ranked = recommender.rank_news(sample_news_items, "AAPL", "Apple Inc.")

        # Check that scores are in descending order
        scores = [item["ai_score"] for item in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_rank_news_relevance(self, sample_news_items):
        """Test that Apple-specific news ranks higher"""
        recommender = NewsRecommender()
        ranked = recommender.rank_news(sample_news_items, "AAPL", "Apple Inc.")

        # First item should be Apple-specific (not general market news)
        top_item = ranked[0]
        assert "apple" in top_item["title"].lower()

        # Last item should be less relevant (general tech news or old news)
        last_item = ranked[-1]
        # Should have lower score than top item
        assert last_item["ai_score"] < top_item["ai_score"]

    def test_score_article_title_match(self):
        """Test scoring when ticker/company is in title"""
        recommender = NewsRecommender()
        article = {
            "title": "Apple Reports Earnings",
            "summary": "Financial results announced",
            "publisher": "Reuters",
            "providerPublishTime": int(datetime.now().timestamp()),
        }

        score, explanation = recommender._score_article(article, "AAPL", "Apple Inc.", None)

        assert score > 0.5  # Should have high score
        assert "title" in explanation
        # Check that it detected the match (either direct mention or in summary)
        assert "Directly mentions" in explanation["title"] or "References" in explanation["title"]

    def test_calculate_content_relevance(self):
        """Test content relevance calculation"""
        recommender = NewsRecommender()

        # High relevance: earnings report
        score1 = recommender._calculate_content_relevance(
            "quarterly earnings report shows revenue growth",
            "company posted profit beating analyst estimates",
            None,
        )
        assert score1 >= 0.6  # Should be high

        # Low relevance: generic news
        score2 = recommender._calculate_content_relevance(
            "general market update", "stock market moves higher today", None
        )
        assert score2 <= score1  # Should be lower

    def test_calculate_recency_score(self):
        """Test recency scoring"""
        recommender = NewsRecommender()
        now = datetime.now()

        # Very recent (1 hour ago)
        recent_time = int((now - timedelta(hours=1)).timestamp())
        score_recent = recommender._calculate_recency_score(recent_time)
        assert score_recent >= 0.9  # Should be very high

        # Old news (1 month ago)
        old_time = int((now - timedelta(days=30)).timestamp())
        score_old = recommender._calculate_recency_score(old_time)
        assert score_old < score_recent  # Should be much lower

        # Invalid timestamp
        score_invalid = recommender._calculate_recency_score(0)
        assert score_invalid == 0.3  # Default score

    def test_calculate_source_credibility(self):
        """Test source credibility scoring"""
        recommender = NewsRecommender()

        # Known credible source
        score_reuters = recommender._calculate_source_credibility("Reuters")
        assert score_reuters >= 0.9

        score_bloomberg = recommender._calculate_source_credibility("Bloomberg")
        assert score_bloomberg >= 0.9

        # Unknown source
        score_unknown = recommender._calculate_source_credibility("Random Blog")
        assert score_unknown == 0.5  # Default

    def test_calculate_sentiment_balance(self):
        """Test sentiment balance calculation"""
        recommender = NewsRecommender()

        # Neutral content
        score_neutral = recommender._calculate_sentiment_balance(
            "Company reports quarterly results", "Financial data released"
        )
        assert score_neutral >= 0.8  # Should be high for neutral

        # Extreme positive
        score_positive = recommender._calculate_sentiment_balance(
            "Stock soars and surges to record highs",
            "Company wins breakthrough success",
        )
        assert score_positive < score_neutral  # Should be lower due to extreme sentiment

        # Mixed sentiment
        score_mixed = recommender._calculate_sentiment_balance(
            "Stock gains despite some concerns", "Positive results but challenges remain"
        )
        # Mixed should be between neutral and extreme
        assert score_mixed >= score_positive

    def test_calculate_confidence(self):
        """Test confidence calculation"""
        recommender = NewsRecommender()

        # High confidence: high score + credible source + has summary
        article_high = {
            "publisher": "Reuters",
            "summary": "Detailed summary of the news article",
        }
        confidence_high = recommender._calculate_confidence(0.8, article_high)
        assert confidence_high == "high"

        # Low confidence: low score
        article_low = {"publisher": "Unknown", "summary": ""}
        confidence_low = recommender._calculate_confidence(0.3, article_low)
        assert confidence_low == "low"

        # Medium confidence
        article_medium = {"publisher": "MarketWatch", "summary": "Some summary"}
        confidence_medium = recommender._calculate_confidence(0.6, article_medium)
        assert confidence_medium == "medium"

    def test_filter_by_category_all_news(self, sample_news_items):
        """Test filtering with 'All News' category"""
        recommender = NewsRecommender()
        filtered = recommender.filter_by_category(sample_news_items, "All News")
        assert len(filtered) == len(sample_news_items)

    def test_filter_by_category_earnings(self, sample_news_items):
        """Test filtering for earnings reports"""
        recommender = NewsRecommender()
        filtered = recommender.filter_by_category(sample_news_items, "Earnings Reports")

        # Should include the earnings article
        assert len(filtered) >= 1
        assert any("earnings" in item["title"].lower() for item in filtered)

    def test_filter_by_category_press_releases(self, sample_news_items):
        """Test filtering for press releases"""
        recommender = NewsRecommender()
        filtered = recommender.filter_by_category(sample_news_items, "Press Releases")

        # Should include the product launch announcement
        assert any(
            "announces" in item["title"].lower() or "announces" in item.get("summary", "").lower()
            for item in filtered
        )

    def test_filter_by_category_market_analysis(self, sample_news_items):
        """Test filtering for market analysis"""
        recommender = NewsRecommender()
        filtered = recommender.filter_by_category(sample_news_items, "Market Analysis")

        # Should include analyst upgrade
        assert any(
            "analyst" in item["title"].lower() or "analyst" in item.get("summary", "").lower()
            for item in filtered
        )

    def test_filter_by_invalid_category(self, sample_news_items):
        """Test filtering with invalid category"""
        recommender = NewsRecommender()
        filtered = recommender.filter_by_category(sample_news_items, "Invalid Category")
        # Should return all items (no filtering)
        assert len(filtered) == len(sample_news_items)

    def test_get_recency_explanation(self):
        """Test recency explanation generation"""
        recommender = NewsRecommender()
        now = datetime.now()

        # Recent
        time_recent = int((now - timedelta(hours=2)).timestamp())
        explanation = recommender._get_recency_explanation(time_recent)
        assert "6 hours" in explanation or "today" in explanation

        # This week
        time_week = int((now - timedelta(days=5)).timestamp())
        explanation_week = recommender._get_recency_explanation(time_week)
        assert "week" in explanation_week or "days" in explanation_week

        # Invalid
        explanation_invalid = recommender._get_recency_explanation(0)
        assert "Unknown" in explanation_invalid

    def test_get_content_explanation(self):
        """Test content explanation generation"""
        recommender = NewsRecommender()

        # Financial results
        explanation1 = recommender._get_content_explanation(
            "earnings report shows strong revenue", "quarterly profit increased", None
        )
        assert "financial" in explanation1.lower()

        # Business development
        explanation2 = recommender._get_content_explanation(
            "company launches new product", "partnership announced", None
        )
        assert "business" in explanation2.lower() or "development" in explanation2.lower()

        # Generic
        explanation3 = recommender._get_content_explanation(
            "stock market update", "general news", None
        )
        assert "general" in explanation3.lower()

    def test_get_sentiment_explanation(self):
        """Test sentiment explanation generation"""
        recommender = NewsRecommender()

        explanation_balanced = recommender._get_sentiment_explanation(0.9)
        assert (
            "balanced" in explanation_balanced.lower()
            or "objective" in explanation_balanced.lower()
        )

        explanation_bias = recommender._get_sentiment_explanation(0.3)
        assert "sentiment" in explanation_bias.lower()

    def test_ranking_preserves_original_data(self, sample_news_items):
        """Test that ranking doesn't lose original article data"""
        recommender = NewsRecommender()
        ranked = recommender.rank_news(sample_news_items.copy(), "AAPL", "Apple Inc.")

        for item in ranked:
            # Check that original fields are preserved
            assert "title" in item
            assert "publisher" in item
            assert "link" in item

            # Check that new fields are added
            assert "ai_score" in item
            assert "ai_explanation" in item
            assert "ai_confidence" in item

    def test_ranking_with_missing_fields(self):
        """Test ranking with incomplete article data"""
        recommender = NewsRecommender()
        incomplete_articles = [
            {
                "title": "Test Article",
                # Missing summary, publisher, publishedTime
            },
            {
                "summary": "Just a summary"  # Missing title
            },
        ]

        # Should not crash, but may filter out invalid items
        ranked = recommender.rank_news(incomplete_articles, "AAPL", "Apple Inc.")
        # Should handle gracefully
        assert isinstance(ranked, list)
