# Fundamental Investment Dashboard

A Streamlit-based dashboard for long-term fundamental investors to analyze company financials, key ratios, and relevant news.

## Features

- 🔍 **Company Search**: Search for companies by name or ticker symbol
- 📊 **Financial Statements**: Visual Sankey diagrams for Income Statement, Cash Flow, and Balance Sheet (UI placeholders ready)
- 📐 **Key Ratios**: Compare company ratios against industry benchmarks and historical averages
- 📰 **News Feed**: Stay updated with relevant company news and developments
- 🎓 **Educational Tooltips**: Learn about fundamental investing concepts

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run dashboard.py
```

3. Open your browser to `http://localhost:8501`

## Project Structure

```
app/
├── dashboard.py          # Main Streamlit application
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Next Steps

- [ ] Integrate financial data API (e.g., Alpha Vantage, Yahoo Finance, Financial Modeling Prep)
- [ ] Implement Sankey diagrams for financial statements using Plotly
- [ ] Add ratio calculation and visualization logic
- [ ] Integrate news API (e.g., News API, Financial News API)
- [ ] Build ML recommender system for company suggestions
- [ ] Add data caching for performance optimization

## Usage

1. Enter a company name or ticker in the search bar
2. Use advanced filters to narrow your search (optional)
3. Review the three main sections:
   - Left: Financial statement flows
   - Middle: Key financial ratios
   - Right: Latest news and updates
4. Explore additional resources and educational content

## Built With

- **Streamlit**: Interactive web dashboard
- **Plotly**: Data visualizations
- **Pandas**: Data manipulation
- **Python**: Core programming language

---
*Built for long-term fundamental investors 📈*
