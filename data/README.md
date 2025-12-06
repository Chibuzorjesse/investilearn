# Data Cache Directory

This directory contains pre-computed financial data to avoid API rate limits.

## Files

- `sector_tickers.csv` - List of all tickers organized by sector
- `sector_data/` - Pre-computed peer comparison data for each sector
  - `Technology.parquet` - Technology sector companies with financial metrics
  - `Healthcare.parquet` - Healthcare sector companies with financial metrics
  - etc.

## Data Refresh

Run the data refresh worker to update cached data:

```bash
uv run python scripts/refresh_data.py
```

This should be run:
- Daily for active trading hours data
- Weekly for fundamental data updates
- Can be automated via cron job or scheduled task

## Data Schema

Each sector parquet file contains:
- ticker: Stock symbol
- company_name: Full company name
- sector: Sector classification
- market_cap: Market capitalization
- pe_ratio: Price-to-earnings ratio
- pb_ratio: Price-to-book ratio
- debt_to_equity: Debt-to-equity ratio
- current_ratio: Current ratio
- roe: Return on equity
- revenue_growth: Revenue growth rate
- profit_margin: Profit margin
- last_updated: Timestamp of data collection
