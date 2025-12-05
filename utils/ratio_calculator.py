"""Financial ratio calculation utilities"""

import streamlit as st


def calculate_ratios(info, income_stmt=None, balance_sheet=None):
    """
    Calculate key financial ratios from stock info and financial statements

    Args:
        info: Stock info dictionary from yfinance
        income_stmt: Income statement DataFrame (optional)
        balance_sheet: Balance sheet DataFrame (optional)

    Returns:
        dict: Dictionary of calculated ratios
    """
    ratios = {}

    try:
        # Profitability ratios
        roe = info.get("returnOnEquity", None)
        ratios["ROE"] = roe * 100 if roe is not None else None

        roa = info.get("returnOnAssets", None)
        ratios["ROA"] = roa * 100 if roa is not None else None

        profit_margin = info.get("profitMargins", None)
        ratios["Net Profit Margin"] = profit_margin * 100 if profit_margin is not None else None

        gross_margin = info.get("grossMargins", None)
        ratios["Gross Profit Margin"] = gross_margin * 100 if gross_margin is not None else None

        # Liquidity ratios
        ratios["Current Ratio"] = info.get("currentRatio", None)
        ratios["Quick Ratio"] = info.get("quickRatio", None)

        # Leverage ratios
        ratios["Debt to Equity"] = info.get("debtToEquity", None)

        # Calculate Interest Coverage if income statement data available
        if income_stmt is not None and not income_stmt.empty:
            try:
                # Get most recent column (latest financial data)
                latest_data = income_stmt.iloc[:, 0]
                ebit = latest_data.get("EBIT", None)

                # Try multiple interest expense fields
                interest_expense = (
                    latest_data.get("Interest Expense", None)
                    or latest_data.get("Interest Expense Non Operating", None)
                    or latest_data.get("Net Non Operating Interest Income Expense", None)
                )

                if (
                    ebit is not None
                    and interest_expense is not None
                    and not (
                        isinstance(interest_expense, float) and interest_expense != interest_expense
                    )  # Check for NaN
                    and abs(interest_expense) > 0
                ):
                    ratios["Interest Coverage"] = ebit / abs(interest_expense)
                else:
                    ratios["Interest Coverage"] = None
            except (KeyError, IndexError, TypeError):
                ratios["Interest Coverage"] = None
        else:
            ratios["Interest Coverage"] = None

        # Calculate Debt Ratio if balance sheet data available
        if balance_sheet is not None and not balance_sheet.empty:
            try:
                latest_data = balance_sheet.iloc[:, 0]
                total_debt = latest_data.get("Total Debt", None)
                total_assets = latest_data.get("Total Assets", None)

                if total_debt is not None and total_assets is not None and total_assets != 0:
                    ratios["Debt Ratio"] = total_debt / total_assets
                else:
                    ratios["Debt Ratio"] = None
            except (KeyError, IndexError, TypeError):
                ratios["Debt Ratio"] = None
        else:
            ratios["Debt Ratio"] = None

        # Efficiency ratios
        # Asset Turnover = Revenue / Average Total Assets
        if (
            income_stmt is not None
            and not income_stmt.empty
            and balance_sheet is not None
            and not balance_sheet.empty
        ):
            try:
                revenue = income_stmt.iloc[:, 0].get("Total Revenue", None)
                current_assets = balance_sheet.iloc[:, 0].get("Total Assets", None)

                # Try to get previous period for average calculation
                if len(balance_sheet.columns) > 1:
                    prev_assets = balance_sheet.iloc[:, 1].get("Total Assets", None)
                    if current_assets is not None and prev_assets is not None:
                        avg_assets = (current_assets + prev_assets) / 2
                    else:
                        avg_assets = current_assets
                else:
                    avg_assets = current_assets

                if revenue is not None and avg_assets is not None and avg_assets != 0:
                    ratios["Asset Turnover"] = revenue / avg_assets
                else:
                    ratios["Asset Turnover"] = None
            except (KeyError, IndexError, TypeError):
                ratios["Asset Turnover"] = None
        else:
            ratios["Asset Turnover"] = None

        # Inventory Turnover = COGS / Average Inventory
        if (
            income_stmt is not None
            and not income_stmt.empty
            and balance_sheet is not None
            and not balance_sheet.empty
        ):
            try:
                cogs = income_stmt.iloc[:, 0].get("Cost Of Revenue", None)
                current_inventory = balance_sheet.iloc[:, 0].get("Inventory", None)

                # Try to get previous period for average calculation
                if len(balance_sheet.columns) > 1:
                    prev_inventory = balance_sheet.iloc[:, 1].get("Inventory", None)
                    if current_inventory is not None and prev_inventory is not None:
                        avg_inventory = (current_inventory + prev_inventory) / 2
                    else:
                        avg_inventory = current_inventory
                else:
                    avg_inventory = current_inventory

                if cogs is not None and avg_inventory is not None and avg_inventory != 0:
                    ratios["Inventory Turnover"] = cogs / avg_inventory
                else:
                    ratios["Inventory Turnover"] = None
            except (KeyError, IndexError, TypeError):
                ratios["Inventory Turnover"] = None
        else:
            ratios["Inventory Turnover"] = None

        # Days Sales Outstanding = (Accounts Receivable / Revenue) * 365
        if (
            income_stmt is not None
            and not income_stmt.empty
            and balance_sheet is not None
            and not balance_sheet.empty
        ):
            try:
                revenue = income_stmt.iloc[:, 0].get("Total Revenue", None)
                accounts_receivable = balance_sheet.iloc[:, 0].get("Accounts Receivable", None)

                if revenue is not None and accounts_receivable is not None and revenue != 0:
                    ratios["Days Sales Outstanding"] = (accounts_receivable / revenue) * 365
                else:
                    ratios["Days Sales Outstanding"] = None
            except (KeyError, IndexError, TypeError):
                ratios["Days Sales Outstanding"] = None
        else:
            ratios["Days Sales Outstanding"] = None

        # Valuation ratios
        ratios["P/E Ratio"] = info.get("trailingPE", None)
        ratios["P/B Ratio"] = info.get("priceToBook", None)
        ratios["PEG Ratio"] = info.get("pegRatio", None)
        ratios["Price to Sales"] = info.get("priceToSalesTrailing12Months", None)

    except Exception as e:
        st.warning(f"Error calculating some ratios: {str(e)}")

    return ratios


def get_ratio_metrics(ratio_category):
    """
    Get the list of metrics and descriptions for a ratio category

    Args:
        ratio_category: Category name (Profitability, Liquidity, etc.)

    Returns:
        tuple: (info_text, metrics_list)
    """
    ratio_configs = {
        "Profitability": {
            "info": "💡 **Profitability ratios** measure how efficiently a company generates profit",
            "metrics": [
                ("ROE", "ROE (Return on Equity)"),
                ("ROA", "ROA (Return on Assets)"),
                ("Net Profit Margin", "Net Profit Margin"),
                ("Gross Profit Margin", "Gross Profit Margin"),
            ],
        },
        "Liquidity": {
            "info": "💡 **Liquidity ratios** assess ability to meet short-term obligations",
            "metrics": [
                ("Current Ratio", "Current Ratio"),
                ("Quick Ratio", "Quick Ratio"),
            ],
        },
        "Efficiency": {
            "info": "💡 **Efficiency ratios** show how well assets are being used (calculations pending)",
            "metrics": [
                ("Asset Turnover", "Asset Turnover"),
                ("Inventory Turnover", "Inventory Turnover"),
                ("Days Sales Outstanding", "Days Sales Outstanding"),
            ],
        },
        "Leverage": {
            "info": "💡 **Leverage ratios** indicate financial risk from debt",
            "metrics": [
                ("Debt to Equity", "Debt-to-Equity"),
                ("Interest Coverage", "Interest Coverage"),
                ("Debt Ratio", "Debt Ratio"),
            ],
        },
        "Valuation": {
            "info": "💡 **Valuation ratios** help determine if stock is fairly priced",
            "metrics": [
                ("P/E Ratio", "P/E Ratio"),
                ("P/B Ratio", "P/B Ratio"),
                ("PEG Ratio", "PEG Ratio"),
                ("Price to Sales", "Price-to-Sales"),
            ],
        },
    }

    config = ratio_configs.get(ratio_category, ratio_configs["Profitability"])
    return config["info"], config["metrics"]


def calculate_5yr_average(info, income_stmts=None, balance_sheets=None):
    """
    Calculate 5-year average for key ratios from historical data

    Args:
        info: Stock info dictionary from yfinance
        income_stmts: Historical income statements DataFrame (optional)
        balance_sheets: Historical balance sheets DataFrame (optional)

    Returns:
        dict: Dictionary of 5-year average ratios
    """
    averages: dict[str, float | None] = {}

    # If we don't have historical data, return None for all
    if income_stmts is None or balance_sheets is None:
        ratio_keys = [
            "ROE",
            "ROA",
            "Net Profit Margin",
            "Gross Profit Margin",
            "Current Ratio",
            "Quick Ratio",
            "Asset Turnover",
            "Inventory Turnover",
            "Days Sales Outstanding",
            "Debt to Equity",
            "Interest Coverage",
            "Debt Ratio",
            "P/E Ratio",
            "P/B Ratio",
            "PEG Ratio",
            "Price to Sales",
        ]
        for key in ratio_keys:
            averages[key] = None
        return averages

    try:
        # Calculate ratios for each historical period
        historical_ratios = []
        num_periods = min(len(income_stmts.columns), len(balance_sheets.columns))

        for i in range(num_periods):
            period_ratios = {}
            income_data = income_stmts.iloc[:, i]
            balance_data = balance_sheets.iloc[:, i]

            # Profitability ratios
            net_income = income_data.get("Net Income", None)
            total_revenue = income_data.get("Total Revenue", None)
            gross_profit = income_data.get("Gross Profit", None)
            total_assets = balance_data.get("Total Assets", None)
            stockholder_equity = balance_data.get("Stockholders Equity", None)

            if (
                net_income is not None
                and stockholder_equity is not None
                and stockholder_equity != 0
            ):
                period_ratios["ROE"] = (net_income / stockholder_equity) * 100

            if net_income is not None and total_assets is not None and total_assets != 0:
                period_ratios["ROA"] = (net_income / total_assets) * 100

            if net_income is not None and total_revenue is not None and total_revenue != 0:
                period_ratios["Net Profit Margin"] = (net_income / total_revenue) * 100

            if gross_profit is not None and total_revenue is not None and total_revenue != 0:
                period_ratios["Gross Profit Margin"] = (gross_profit / total_revenue) * 100

            # Liquidity ratios
            current_assets = balance_data.get("Current Assets", None)
            current_liabilities = balance_data.get("Current Liabilities", None)

            if (
                current_assets is not None
                and current_liabilities is not None
                and current_liabilities != 0
            ):
                period_ratios["Current Ratio"] = current_assets / current_liabilities

            historical_ratios.append(period_ratios)

        # Calculate averages
        all_ratio_keys = [
            "ROE",
            "ROA",
            "Net Profit Margin",
            "Gross Profit Margin",
            "Current Ratio",
            "Quick Ratio",
        ]

        for key in all_ratio_keys:
            values = [r[key] for r in historical_ratios if key in r and r[key] is not None]
            if values:
                averages[key] = sum(values) / len(values)
            else:
                averages[key] = None

        # Ratios we can't easily calculate 5yr avg for (need more data)
        for key in [
            "Asset Turnover",
            "Inventory Turnover",
            "Days Sales Outstanding",
            "Debt to Equity",
            "Interest Coverage",
            "Debt Ratio",
            "P/E Ratio",
            "P/B Ratio",
            "PEG Ratio",
            "Price to Sales",
        ]:
            averages[key] = None

    except Exception:
        # If anything goes wrong, return None for all
        for key in all_ratio_keys:
            averages[key] = None

    return averages


def get_industry_comparison(info, ratio_name):
    """
    Get industry average for a ratio by analyzing peer companies

    Args:
        info: Stock info dictionary from yfinance
        ratio_name: Name of the ratio to compare

    Returns:
        float or None: Industry average value if available

    Note:
        This function filters peer companies by:
        1. Same industry/sector
        2. Similar market cap category (Large/Mid/Small)
        3. Calculates average ratios from ~5-10 peers

        This is a free alternative to paid APIs, with limitations:
        - Limited to major public companies (S&P 500 constituents)
        - Slower (requires multiple API calls)
        - Cached to avoid repeated API calls
    """
    import time

    import yfinance as yf

    # Get company details
    ticker = info.get("symbol")
    industry = info.get("industry")
    sector = info.get("sector")
    market_cap = info.get("marketCap")

    if not all([ticker, industry, market_cap]):
        return None

    # Determine market cap category
    if market_cap > 10e9:
        cap_category = "large"
    elif market_cap > 2e9:
        cap_category = "mid"
    else:
        cap_category = "small"

    # Get peer candidates
    peer_tickers = _get_peer_candidates(sector, cap_category)
    if not peer_tickers:
        return None

    # Calculate ratio for peers
    peer_values = []
    checked = 0
    max_checks = 15  # Check up to 15 companies to find ~5-10 valid peers

    for peer_ticker in peer_tickers:
        if checked >= max_checks:
            break
        if peer_ticker.upper() == ticker.upper():
            continue

        checked += 1

        try:
            peer = yf.Ticker(peer_ticker)
            peer_info = peer.info

            # Filter by exact industry match
            if peer_info.get("industry") != industry:
                continue

            # Filter by market cap category
            peer_cap = peer_info.get("marketCap")
            if not peer_cap:
                continue

            if cap_category == "large" and peer_cap <= 10e9:
                continue
            elif cap_category == "mid" and (peer_cap <= 2e9 or peer_cap > 10e9):
                continue
            elif cap_category == "small" and peer_cap >= 2e9:
                continue

            # Calculate the specific ratio for this peer
            peer_value = _calculate_peer_ratio(peer, ratio_name)
            if peer_value is not None:
                peer_values.append(peer_value)

            time.sleep(0.05)  # Small delay to avoid rate limiting

        except (KeyError, ValueError, TypeError, AttributeError):
            # Skip peers with missing/invalid data
            continue

    # Return average if we have at least 3 peers
    if len(peer_values) >= 3:
        return sum(peer_values) / len(peer_values)

    return None


def _calculate_peer_ratio(peer_ticker, ratio_name):
    """Calculate a specific ratio for a peer company"""
    try:
        income = peer_ticker.financials
        balance = peer_ticker.balance_sheet

        if income.empty or balance.empty:
            return None

        # Get most recent period
        net_income = income.iloc[:, 0].get("Net Income")
        revenue = income.iloc[:, 0].get("Total Revenue")
        equity = balance.iloc[:, 0].get("Stockholders Equity")
        total_assets = balance.iloc[:, 0].get("Total Assets")
        current_assets = balance.iloc[:, 0].get("Current Assets")
        current_liabilities = balance.iloc[:, 0].get("Current Liabilities")

        # Calculate based on ratio name
        if ratio_name == "Return on Equity (ROE)":
            if net_income is not None and equity is not None and equity != 0:
                return (net_income / equity) * 100

        elif ratio_name == "Return on Assets (ROA)":
            if net_income is not None and total_assets is not None and total_assets != 0:
                return (net_income / total_assets) * 100

        elif ratio_name == "Net Profit Margin":
            if net_income is not None and revenue is not None and revenue != 0:
                return (net_income / revenue) * 100

        elif ratio_name == "Gross Profit Margin":
            gross_profit = income.iloc[:, 0].get("Gross Profit")
            if gross_profit is not None and revenue is not None and revenue != 0:
                return (gross_profit / revenue) * 100

        elif ratio_name == "Current Ratio":
            if (
                current_assets is not None
                and current_liabilities is not None
                and current_liabilities != 0
            ):
                return current_assets / current_liabilities

        return None

    except (KeyError, ValueError, TypeError, AttributeError, IndexError):
        return None


def _get_peer_candidates(sector, _cap_category):
    """
    Get a list of potential peer company tickers based on sector

    Args:
        sector (str): Company sector
        cap_category (str): Market cap category (not used for initial filtering)

    Returns:
        list: List of ticker symbols to check as peers
    """
    # Major companies by sector (S&P 500 constituents)
    sector_tickers = {
        "Technology": [
            "AAPL",
            "MSFT",
            "GOOGL",
            "META",
            "NVDA",
            "ORCL",
            "CSCO",
            "ADBE",
            "CRM",
            "INTC",
            "AMD",
            "QCOM",
            "IBM",
            "NOW",
            "INTU",
            "AMAT",
            "TXN",
            "AVGO",
            "MU",
            "LRCX",
        ],
        "Healthcare": [
            "JNJ",
            "UNH",
            "PFE",
            "ABBV",
            "TMO",
            "MRK",
            "LLY",
            "ABT",
            "DHR",
            "BMY",
            "AMGN",
            "CVS",
            "GILD",
            "MDT",
            "CI",
            "ISRG",
            "ZTS",
            "SYK",
            "BSX",
            "VRTX",
        ],
        "Financial Services": [
            "JPM",
            "BAC",
            "WFC",
            "C",
            "GS",
            "MS",
            "BLK",
            "SCHW",
            "AXP",
            "CB",
            "PNC",
            "USB",
            "TFC",
            "COF",
            "BK",
            "STT",
            "AIG",
            "MMC",
            "ICE",
            "CME",
        ],
        "Consumer Cyclical": [
            "AMZN",
            "TSLA",
            "HD",
            "NKE",
            "MCD",
            "SBUX",
            "LOW",
            "TJX",
            "BKNG",
            "CMG",
            "MAR",
            "GM",
            "F",
            "ABNB",
            "ROST",
            "DG",
            "ORLY",
            "AZO",
            "YUM",
            "POOL",
        ],
        "Consumer Defensive": [
            "WMT",
            "PG",
            "KO",
            "PEP",
            "COST",
            "PM",
            "EL",
            "MDLZ",
            "CL",
            "KMB",
            "GIS",
            "HSY",
            "K",
            "CAG",
            "SJM",
            "MO",
            "STZ",
            "TAP",
            "KHC",
            "CPB",
        ],
        "Energy": [
            "XOM",
            "CVX",
            "COP",
            "EOG",
            "SLB",
            "MPC",
            "PSX",
            "VLO",
            "OXY",
            "HAL",
            "KMI",
            "WMB",
            "DVN",
            "HES",
            "BKR",
            "FANG",
            "PXD",
            "MRO",
            "APA",
            "CTRA",
        ],
        "Industrials": [
            "BA",
            "HON",
            "UNP",
            "UPS",
            "CAT",
            "RTX",
            "LMT",
            "GE",
            "MMM",
            "DE",
            "FDX",
            "NSC",
            "EMR",
            "ETN",
            "CSX",
            "WM",
            "ITW",
            "PH",
            "CARR",
            "PCAR",
        ],
        "Communication Services": [
            "GOOGL",
            "META",
            "DIS",
            "NFLX",
            "CMCSA",
            "VZ",
            "T",
            "TMUS",
            "CHTR",
            "EA",
            "TTWO",
            "PARA",
            "WBD",
            "FOXA",
            "OMC",
            "IPG",
            "MTCH",
            "PINS",
            "SNAP",
            "ROKU",
        ],
        "Real Estate": [
            "PLD",
            "AMT",
            "CCI",
            "EQIX",
            "PSA",
            "WELL",
            "DLR",
            "O",
            "SPG",
            "VICI",
            "AVB",
            "EQR",
            "SBAC",
            "VTR",
            "ARE",
            "INVH",
            "MAA",
            "KIM",
            "ESS",
            "UDR",
        ],
        "Utilities": [
            "NEE",
            "DUK",
            "SO",
            "D",
            "AEP",
            "EXC",
            "SRE",
            "XEL",
            "PCG",
            "ED",
            "EIX",
            "WEC",
            "AWK",
            "DTE",
            "PPL",
            "ES",
            "FE",
            "ETR",
            "AEE",
            "CMS",
        ],
        "Basic Materials": [
            "LIN",
            "APD",
            "SHW",
            "ECL",
            "DD",
            "NEM",
            "FCX",
            "NUE",
            "DOW",
            "PPG",
            "VMC",
            "MLM",
            "CTVA",
            "CF",
            "MOS",
            "ALB",
            "EMN",
            "CE",
            "FMC",
            "IFF",
        ],
    }

    return sector_tickers.get(sector, [])


def format_ratio_value(value, ratio_name):
    """
    Format a ratio value for display

    Args:
        value: The ratio value
        ratio_name: Name of the ratio

    Returns:
        str: Formatted string for display
    """
    if value is None:
        return "N/A"

    # Percentage ratios
    if any(term in ratio_name for term in ["ROE", "ROA", "Margin"]):
        return f"{value:.2f}%"

    # Days ratios
    if "Days" in ratio_name:
        return f"{value:.1f} days"

    # Turnover ratios
    if "Turnover" in ratio_name:
        return f"{value:.2f}x"

    # Regular ratios
    return f"{value:.2f}"
