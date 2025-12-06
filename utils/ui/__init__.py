"""UI components for the dashboard"""

from utils.ui.financial_statements import render_financial_statements
from utils.ui.header import render_company_header
from utils.ui.landing import render_landing_page
from utils.ui.news import render_news_section
from utils.ui.ratios import render_ratios_section
from utils.ui.sidebar import render_sidebar

__all__ = [
    "render_company_header",
    "render_financial_statements",
    "render_ratios_section",
    "render_news_section",
    "render_sidebar",
    "render_landing_page",
]
