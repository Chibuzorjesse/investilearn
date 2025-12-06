# InvestiLearn - AI-Powered Fundamental Investment Education Platform

An interactive educational dashboard that teaches fundamental investing principles through real company data analysis, powered by local AI models and machine learning.

[![CI/CD Pipeline](https://github.com/akhilkarra/investilearn/actions/workflows/ci.yml/badge.svg)](https://github.com/akhilkarra/investilearn/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## 🎯 Project Overview

**InvestiLearn** is a comprehensive educational platform designed to teach fundamental investing concepts through hands-on analysis of real financial data. The application combines traditional financial analysis tools with cutting-edge AI assistance to create an interactive learning environment.

### Key Differentiators

- 🧠 **Local AI Models**: All AI processing runs locally - no external API calls, complete privacy
- 🎓 **Education-First**: Designed for learning, not investment advice
- 🔍 **Transparent AI**: Every AI decision includes explanations and confidence levels
- 📊 **Real Data**: Live financial data from Yahoo Finance
- 💬 **Interactive Coach**: Context-aware LLM guidance using Ollama

## ✨ Features

### Core Analytics
- 🔍 **Company Search**: Intelligent search for companies by name or ticker symbol
- 📊 **Financial Statements**: Interactive Sankey flow diagrams showing money movement
  - Income Statement visualization
  - Cash Flow analysis
  - Balance Sheet structure
- 📐 **Financial Ratios**: 20+ key metrics with industry comparisons
  - Profitability ratios (ROE, ROA, margins)
  - Liquidity ratios (Current, Quick)
  - Efficiency ratios (Asset turnover, inventory)
  - Leverage ratios (Debt/Equity, Interest coverage)
  - Valuation ratios (P/E, P/B, PEG)

### AI-Powered Learning
- 💬 **LLM Investment Coach**: Interactive Q&A powered by Ollama (qwen2.5:14b)
  - Context-aware explanations of metrics and concepts
  - Company-specific analysis with full financial context
  - Confidence-based filtering (High/Medium/Low)
  - Streaming responses with interrupt capability
  - Article-specific news analysis
- 📰 **AI News Ranking**: Machine learning-powered news curation
  - Semantic similarity using sentence-transformers
  - Financial sentiment analysis with FinBERT
  - Source credibility scoring
  - Recency and relevance weighting
  - Transparent scoring breakdowns
- 🎯 **Smart Recommendations**: Context-aware suggestions throughout the UI
  - Metric-specific help buttons
  - Statement-level guidance
  - Article interpretation assistance

### Educational Tools
- 📚 **Interactive Learning Guides**:
  - Getting Started tutorial
  - Fundamental investing principles
  - How AI assists you
  - Quick tips and best practices
- 💡 **Contextual Explanations**: Click ❓ anywhere for instant learning
- 🎨 **Confidence Indicators**: Visual cues for AI reliability (🟢🟡🔴)
- 📖 **Additional Resources**: Curated external learning materials

## 🚀 Quick Start

### Prerequisites

- **Python 3.10 or higher**
- **[uv](https://github.com/astral-sh/uv)** (recommended) or pip
- **[Ollama](https://ollama.ai)** for LLM Coach feature

### Step 1: Install Dependencies

#### Option A: Using uv (Recommended)

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

# Install all dependencies
uv sync
```

#### Option B: Using pip

```bash
git clone git@github.com:akhilkarra/investilearn.git
cd investilearn
pip install -r requirements.txt
```

### Step 2: Install Ollama and Download LLM Model

The LLM Coach feature requires Ollama with the qwen2.5:14b model:

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# For macOS, you can also use Homebrew
brew install ollama

# Start Ollama service
ollama serve

# In a new terminal, download the model (one-time setup, ~9GB)
ollama pull qwen2.5:14b
```

**Note**: The model download is ~9GB and may take several minutes depending on your connection.

### Step 3: Install ML Models (Optional)

For enhanced news ranking with semantic similarity and sentiment analysis:

```bash
# First run will automatically download models:
# - sentence-transformers/all-MiniLM-L6-v2 (~80MB)
# - ProsusAI/finbert (~440MB)

# You can disable ML models in the UI if you prefer rule-based ranking
```

### Step 4: Run the Application

```bash
# Make sure Ollama is running in the background
# (run 'ollama serve' in a separate terminal if needed)

# Start the dashboard
uv run streamlit run dashboard.py

# Or if using traditional venv
streamlit run dashboard.py
```

Open your browser to `http://localhost:8501` (should open automatically)

### Troubleshooting

**Ollama Connection Issues:**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

**Model Not Found:**

```bash
# List installed models
ollama list

# If qwen2.5:14b is missing
ollama pull qwen2.5:14b
```

**ML Models Disabled:**
- You can still use the app with ML features turned off
- Toggle "🧠 News ML Models" in the sidebar to disable/enable

## 📁 Project Structure

```text
investilearn/
├── dashboard.py                      # Main Streamlit application entry point
├── utils/                            # Core utility modules
│   ├── __init__.py                  # Package initialization
│   ├── cache_warmer.py              # Sector-based data caching system
│   ├── data_fetcher.py              # Yahoo Finance API integration
│   ├── llm_coach.py                 # Ollama LLM wrapper for coaching
│   ├── model_loader.py              # ML model initialization and caching
│   ├── news_ai.py                   # News ranking with ML/rule-based scoring
│   ├── ratio_calculator.py          # Financial ratio computations
│   ├── visualizations.py            # Plotly Sankey diagram generation
│   └── ui/                          # UI component modules
│       ├── __init__.py
│       ├── coach_panel.py           # LLM coach modal dialog
│       ├── financial_statements.py  # Statement visualizations
│       ├── header.py                # Company header component
│       ├── landing.py               # Landing page and resources
│       ├── news.py                  # News section with AI ranking
│       ├── ratios.py                # Ratio analysis and comparisons
│       ├── settings.py              # Settings panel (legacy)
│       └── sidebar.py               # Sidebar with quick tips
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_data_fetcher.py        # Data fetching tests
│   ├── test_llm_coach.py           # LLM coach tests
│   ├── test_news_ai.py             # News AI tests
│   └── test_ratio_calculator.py    # Ratio calculation tests
├── .github/workflows/               # CI/CD pipelines
│   └── ci.yml                      # GitHub Actions workflow
├── pyproject.toml                   # Project configuration and dependencies
├── requirements.txt                 # Frozen dependencies for pip
├── README.md                        # This file
├── CONTRIBUTING.md                  # Development guidelines
└── LICENSE                          # MIT License
```

## 🛠️ Tech Stack

### Core Framework & UI

- **[Streamlit 1.39+](https://streamlit.io)**: Interactive web dashboard framework
  - Custom CSS for AI badges and styling
  - Modal dialog system for coach and settings
  - Session state management for UI flow
  - Responsive layout with columns and tabs

### Data & Finance

- **[yfinance](https://github.com/ranaroussi/yfinance)**: Yahoo Finance API wrapper
  - Real-time and historical stock data
  - Financial statements (Income, Balance, Cash Flow)
  - Company info and sector classifications
  - News article feeds
- **[Pandas 2.2+](https://pandas.pydata.org)**: Data manipulation and analysis
  - Financial statement processing
  - Ratio calculations
  - Time-series analysis
- **[Plotly 5.24+](https://plotly.com/python/)**: Interactive visualizations
  - Custom Sankey diagrams for financial flows
  - Responsive charts with hover details

### AI & Machine Learning

- **[Ollama](https://ollama.ai)** + **qwen2.5:14b**: Local LLM for investment coaching
  - 100% local inference, no external API calls
  - Streaming responses with interrupt capability
  - Context-aware explanations
  - Confidence estimation
- **[sentence-transformers](https://www.sbert.net)**: Semantic similarity
  - Model: `all-MiniLM-L6-v2`
  - Used for news article relevance scoring
  - Embedding-based company-article matching
- **[transformers](https://huggingface.co/transformers)** + **FinBERT**: Financial sentiment analysis
  - Model: `ProsusAI/finbert`
  - Domain-specific sentiment for financial text
  - News article sentiment scoring

### Development Tools

- **[uv](https://github.com/astral-sh/uv)**: Ultra-fast Python package manager
  - Dependency resolution and management
  - Virtual environment creation
  - Lock file generation
- **[Ruff](https://github.com/astral-sh/ruff)**: Lightning-fast linting and formatting
  - Replaces flake8, isort, black
  - Auto-fixing capabilities
  - ~10-100x faster than alternatives
- **[mypy](http://mypy-lang.org)**: Static type checking
  - Type hints validation
  - Improved code reliability
- **[pytest](https://pytest.org)**: Testing framework
  - Unit tests for core functionality
  - Mocking for external dependencies
- **[pre-commit](https://pre-commit.com)**: Git hooks for code quality
  - Automatic linting on commit
  - Format checking

### Code Attribution & Open Source Usage

This project was built from scratch with the following open-source libraries:

**No base template or starter code was used.** All application logic, UI components, and AI integration were developed specifically for this project.

#### External Libraries Used (via pip/uv)

1. **Data & Visualization Libraries** (Standard usage, no modifications):
   - `streamlit` - Web framework (official API usage)
   - `yfinance` - Financial data fetching (official API usage)
   - `pandas` - Data manipulation (standard library usage)
   - `plotly` - Charting library (standard API usage)

2. **AI/ML Libraries** (Standard usage, no modifications):
   - `ollama` - LLM client library (official Python SDK)
   - `transformers` - Hugging Face model interface (standard API)
   - `sentence-transformers` - Sentence embeddings (standard API)
   - `torch` - PyTorch backend for ML models (dependency)

3. **Development Tools** (Standard usage):
   - `pytest`, `mypy`, `ruff`, `pre-commit` - Standard development tools

#### Custom Code Developed (100% Original)

All code in `dashboard.py` and `utils/` directory is original work, including:

- **LLM Coach System** (`utils/llm_coach.py`): Custom wrapper around Ollama with:
  - Context building from financial data
  - Confidence estimation algorithm
  - Streaming response handling
  - Educational prompt engineering

- **News AI Ranking** (`utils/news_ai.py`): Original ML-powered ranking system:
  - Hybrid scoring (ML + rule-based)
  - Semantic similarity implementation
  - Multi-factor weighting algorithm
  - Transparent score breakdown

- **Financial Analysis** (`utils/ratio_calculator.py`, `utils/data_fetcher.py`):
  - Custom ratio calculations beyond yfinance defaults
  - 5-year historical averaging
  - Industry comparison logic
  - Data cleaning and validation

- **UI Components** (`utils/ui/*.py`): Complete custom UI system:
  - Modal dialog implementation
  - Coach panel with confidence filtering
  - News section with AI explanations
  - Ratio visualizations with context
  - Interactive Sankey diagrams for statements

- **Caching System** (`utils/cache_warmer.py`): Custom sector-based caching:
  - S&P 500 company pre-loading
  - Intelligent cache warming
  - Performance optimization

**Lines of Code**: ~4,500 lines of original Python code (excluding tests and documentation)

**AI Usage Transparency**: GitHub Copilot was used as a coding assistant during development, primarily for:

- Boilerplate code generation
- Documentation string formatting
- Test case scaffolding
- Type hint suggestions

All core algorithms, architecture decisions, and business logic were human-designed and implemented.

## 🗺️ Roadmap

### ✅ Phase 1: Foundation (Completed)

- [x] Project structure and development environment
- [x] CI/CD pipeline with GitHub Actions
- [x] Pre-commit hooks for code quality
- [x] Documentation (README, CONTRIBUTING)
- [x] Basic Streamlit UI framework

### ✅ Phase 2: Core Analytics (Completed)

- [x] Yahoo Finance integration for real-time data
- [x] Financial statement Sankey diagrams
- [x] 20+ financial ratio calculations
- [x] Industry benchmark comparisons
- [x] 5-year historical trend analysis
- [x] Company search and data caching

### ✅ Phase 3: AI Features (Completed)

- [x] **LLM Coach Integration** - Ollama-powered investment guidance
- [x] **ML News Ranking** - Semantic similarity and sentiment analysis
- [x] **Confidence Filtering** - Transparent AI reliability indicators
- [x] **Context-Aware Help** - Metric and statement-specific coaching
- [x] **Interactive Dialogs** - Modal system for coach and settings

### ✅ Phase 4: Polish & UX (Completed)

- [x] Educational landing page and guides
- [x] Responsive UI with improved accessibility
- [x] Comprehensive error handling
- [x] Session state management optimization
- [x] All linting errors resolved (644+ fixes)

### 🎯 Future Enhancements (Optional)

- [ ] Portfolio tracking and comparison
- [ ] Historical performance backtesting
- [ ] Export functionality (PDF reports)
- [ ] Multi-company side-by-side comparison
- [ ] Custom ratio calculator
- [ ] Screener for finding companies by criteria

## 💻 Usage Guide

### First Time Setup

1. **Start Ollama** (required for LLM Coach):

   ```bash
   ollama serve
   ```

2. **Launch the Dashboard**:

   ```bash
   uv run streamlit run dashboard.py
   ```

3. **Navigate to** `http://localhost:8501`

### Using the Dashboard

1. **Search for a Company**:
   - Enter ticker (e.g., "AAPL") or company name (e.g., "Apple")
   - Press Enter to load company data

2. **Explore Financial Data**:
   - **Financial Statements Tab**: View interactive Sankey diagrams
   - **Ratios Tab**: Compare metrics against industry averages
   - **News Tab**: See AI-ranked relevant articles

3. **Ask the Coach**:
   - Click 💬 button next to any metric for explanations
   - Use sidebar "Ask the Coach" for general questions
   - Filter responses by confidence level

4. **Configure AI Settings**:
   - Toggle AI features on/off in sidebar
   - Enable/disable ML models for news ranking
   - Adjust confidence thresholds

### Tips for Best Experience

- **Start with familiar companies** - Easier to learn when you know the business
- **Check confidence levels** - Use 🟢 High confidence for learning fundamentals
- **Explore ratios** - Click ❓ to understand what each metric means
- **Compare with industry** - Look for companies that outperform peers
- **Read AI explanations** - Understand WHY articles are ranked as they are

## 🧪 Development Setup

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

### Quick Development Setup

```bash
# Install with development dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run the app in development mode
uv run streamlit run dashboard.py
```

### Code Quality Tools

```bash
# Lint and auto-fix issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Type checking
uv run mypy dashboard.py utils/

# Run tests with coverage
uv run pytest --cov=utils --cov-report=html

# Run pre-commit checks manually
uv run pre-commit run --all-files
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_llm_coach.py

# Run with verbose output
uv run pytest -v

# Generate coverage report
uv run pytest --cov=utils --cov-report=term-missing
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow code style**: Run `ruff format` before committing
3. **Add tests**: Maintain >80% code coverage
4. **Update docs**: Keep README and docstrings current
5. **Submit a PR**: Include description of changes

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This is an educational tool, not investment advice.**

- No investment recommendations
- No price predictions
- No guarantee of data accuracy
- Always verify with official SEC filings
- Consult licensed financial advisors for personal advice

All financial data is delayed 15-20 minutes and sourced from Yahoo Finance API.

## 🙏 Acknowledgments

- **[Yahoo Finance](https://finance.yahoo.com)** for financial data API
- **[Ollama](https://ollama.ai)** for local LLM infrastructure
- **[Qwen Team](https://qwenlm.github.io)** for the qwen2.5 model
- **[Hugging Face](https://huggingface.co)** for transformer models
- **[Streamlit](https://streamlit.io)** for the amazing web framework

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/akhilkarra/investilearn/issues)
- **Discussions**: [GitHub Discussions](https://github.com/akhilkarra/investilearn/discussions)
- **Author**: Akhil Karra ([@akhilkarra](https://github.com/akhilkarra))

---

**Built for long-term fundamental investors** 📈

**Learn by doing. Invest with confidence.**
