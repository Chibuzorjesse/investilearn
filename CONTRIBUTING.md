# Contributing to InvestiLearn

Thank you for your interest in contributing to InvestiLearn! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Git

### Setting Up Your Development Environment

1. **Clone the repository**
   ```bash
   git clone git@github.com:akhilkarra/investilearn.git
   cd investilearn
   ```

2. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create and activate virtual environment with uv**
   ```bash
   uv venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

4. **Install dependencies**
   ```bash
   uv sync --all-extras
   ```

5. **Install pre-commit hooks**
   ```bash
   uv run pre-commit install
   ```

## Development Workflow

### Running the Application

```bash
uv run streamlit run dashboard.py
```

The app will be available at `http://localhost:8501`

### Code Quality

We use several tools to maintain code quality:

- **Ruff**: Fast Python linter and formatter
- **mypy**: Static type checking
- **pre-commit**: Automated checks before commits

#### Manual Checks

```bash
# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy dashboard.py

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_data_fetcher.py
```

## Project Structure

```
investilearn/
├── dashboard.py           # Main Streamlit application
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── data_fetcher.py   # Data fetching functions
│   ├── ratio_calculator.py # Financial ratio calculations
│   └── visualizations.py # Plotting functions
├── tests/                 # Test files
├── docs/                  # Documentation
├── .github/               # GitHub Actions workflows
├── pyproject.toml        # Project configuration
├── requirements.txt      # Legacy requirements (deprecated, use pyproject.toml)
└── README.md
```

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all functions and classes

### Docstring Format

```python
def calculate_ratio(numerator: float, denominator: float) -> float:
    """
    Calculate a financial ratio.

    Args:
        numerator: The top number in the ratio
        denominator: The bottom number in the ratio

    Returns:
        The calculated ratio value

    Raises:
        ZeroDivisionError: If denominator is zero
    """
    if denominator == 0:
        raise ZeroDivisionError("Denominator cannot be zero")
    return numerator / denominator
```

### Commit Messages

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add Sankey diagram for income statement

- Implement income statement flow visualization
- Add data processing for Sankey diagram
- Update tests for new functionality
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   uv run pre-commit run --all-files
   uv run pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of changes
   - Link any related issues
   - Ensure CI/CD checks pass

## Adding Dependencies

To add a new dependency:

```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

This will automatically update `pyproject.toml` and the lockfile.

## Reporting Issues

When reporting issues, please include:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant error messages or logs

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what is best for the community

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase
- Documentation improvements

Thank you for contributing! 🚀
