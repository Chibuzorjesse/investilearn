"""Utility modules for InvestiLearn dashboard"""

from .data_fetcher import get_financial_statements, get_news, get_stock_info
from .llm_coach import InvestmentCoach, get_coach
from .news_ai import NewsRecommender, get_recommender
from .ratio_calculator import (
    calculate_ratios,
    format_ratio_value,
    get_ratio_metrics,
)
from .visualizations import create_sankey_diagram

__all__ = [
    "get_stock_info",
    "get_financial_statements",
    "get_news",
    "calculate_ratios",
    "get_ratio_metrics",
    "format_ratio_value",
    "create_sankey_diagram",
    "NewsRecommender",
    "get_recommender",
    "InvestmentCoach",
    "get_coach",
]
