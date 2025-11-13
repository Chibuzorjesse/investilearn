# Fundamental Investment Dashboard

A Streamlit-based dashboard for long-term fundamental investors to analyze company financials, key ratios, and relevant news.

[![CI/CD Pipeline](https://github.com/akhilkarra/investilearn/actions/workflows/ci.yml/badge.svg)](https://github.com/akhilkarra/investilearn/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Features

- 🔍 **Company Search**: Search for companies by name or ticker symbol
- 📊 **Financial Statements**: Visual Sankey diagrams for Income Statement, Cash Flow, and Balance Sheet
- 📐 **Key Ratios**: Compare company ratios against industry benchmarks and historical averages
- 📰 **News Feed**: Stay updated with relevant company news and developments
- 🎓 **Educational Tooltips**: Learn about fundamental investing concepts
- 🤖 **LLM Coaching** (Coming Soon): AI-powered investment guidance

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone git@github.com:akhilkarra/investilearn.git
cd investilearn

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On macOS/Linux
# or .venv\Scripts\activate on Windows

uv sync
```

### Installation with pip

```bash
git clone git@github.com:akhilkarra/investilearn.git
cd investilearn
pip install -r requirements.txt
```

### Running the Application

```bash
# With uv
uv run streamlit run dashboard.py

# Or if using traditional venv
streamlit run dashboard.py
```

Open your browser to `http://localhost:8501`

## Development Setup

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup instructions.

### Quick Development Setup

```bash
# Install with development dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run the app in development mode
uv run streamlit run dashboard.py
```

### Code Quality

```bash
# Lint and format
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy dashboard.py

# Run tests
uv run pytest
```

## Project Structure

```text
investilearn/
├── dashboard.py              # Main Streamlit application
├── utils/                    # Utility modules (stashed, coming soon)
│   ├── data_fetcher.py      # Financial data fetching
│   ├── ratio_calculator.py  # Ratio calculations
│   └── visualizations.py    # Plotting functions
├── tests/                    # Test suite
├── .github/workflows/        # CI/CD pipelines
├── pyproject.toml           # Project configuration
├── requirements.txt         # Legacy requirements file
└── README.md
```

## Roadmap

### ✅ Completed
- [x] Basic Streamlit UI with 3-column layout
- [x] Project structure and development environment
- [x] CI/CD pipeline with GitHub Actions
- [x] Pre-commit hooks for code quality
- [x] Documentation (README, CONTRIBUTING)

### 🚧 In Progress
- [ ] Integrate yfinance for real financial data
- [ ] Implement Sankey diagrams for financial statements
- [ ] Add financial ratio calculations and visualizations
- [ ] Integrate news feed (yfinance or NewsAPI)

### 📋 Planned
- [ ] LLM coaching feature (Together.ai/Groq API)
- [ ] ML recommender system for company suggestions
- [ ] Historical trend analysis
- [ ] Portfolio tracking
- [ ] Export functionality (PDF reports)
- [ ] Semantic search with BERT (reach goal)

## Usage

1. Enter a company name or ticker in the search bar (e.g., "AAPL", "Apple")
2. Use advanced filters to narrow your search (optional)
3. Review the three main sections:
   - **Left**: Financial statement flows (Sankey diagrams)
   - **Middle**: Key financial ratios with industry comparisons
   - **Right**: Latest news and updates
4. Explore additional resources and educational content

## Tech Stack

- **Streamlit**: Interactive web dashboard
- **yfinance**: Financial data from Yahoo Finance
- **Plotly**: Interactive data visualizations
- **Pandas**: Data manipulation and analysis
- **uv**: Fast, modern Python package management
- **Ruff**: Lightning-fast Python linter and formatter

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see LICENSE file for details.

---

**Built for long-term fundamental investors** 📈
