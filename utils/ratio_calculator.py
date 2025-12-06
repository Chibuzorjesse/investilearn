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
    Get industry average for a ratio by analyzing peer companies using cached data

    Args:
        info: Stock info dictionary from yfinance
        ratio_name: Name of the ratio to compare

    Returns:
        float or None: Industry average value if available

    Note:
        This function uses an efficient cached approach:
        1. Fetches all peer data once and caches in memory
        2. Filters using pandas for instant results
        3. Only makes API calls on first use per session

        Filters peers by:
        - Same exact industry
        - Similar market cap category (Large/Mid/Small)
        - Valid financial data
    """

    # Get company details
    ticker = info.get("symbol")
    industry = info.get("industry")
    sector = info.get("sector")
    market_cap = info.get("marketCap")

    if not all([ticker, industry, market_cap]):
        return None

    # Get or build cached peer data
    peer_data = _get_cached_peer_data(sector)
    if peer_data is None or peer_data.empty:
        return None

    # Determine market cap category
    if market_cap > 10e9:
        cap_min, cap_max = 10e9, float("inf")
    elif market_cap > 2e9:
        cap_min, cap_max = 2e9, 10e9
    else:
        cap_min, cap_max = 0, 2e9

    # Filter peers using pandas (instant!)
    peers = peer_data[
        (peer_data["industry"] == industry)
        & (peer_data["marketCap"] >= cap_min)
        & (peer_data["marketCap"] < cap_max)
        & (peer_data["ticker"] != ticker.upper())
    ]

    # Need at least 3 peers for valid comparison
    if len(peers) < 3:
        return None

    # Get the ratio column based on ratio_name
    ratio_col = _map_ratio_name_to_column(ratio_name)
    if ratio_col not in peers.columns:
        return None

    # Calculate average, excluding NaN values
    peer_values = peers[ratio_col].dropna()
    if len(peer_values) >= 3:
        return peer_values.mean()

    return None


# Global cache for peer data (persists across function calls in same session)
_PEER_DATA_CACHE: dict = {}


def _get_cached_peer_data(sector):
    """
    Get or build cached DataFrame of peer company data for a sector

    Args:
        sector (str): Company sector

    Returns:
        pd.DataFrame: Cached peer data with columns:
            - ticker, industry, sector, marketCap
            - ROE, ROA, Net Profit Margin, Gross Profit Margin, Current Ratio
    """
    import time

    import pandas as pd
    import streamlit as st
    import yfinance as yf

    # Return cached data if available
    if sector in _PEER_DATA_CACHE:
        return _PEER_DATA_CACHE[sector]

    # Get tickers for this sector
    tickers = _get_peer_candidates(sector, None)
    if not tickers:
        return None

    # Show progress to user
    progress_text = f"Fetching {sector} sector data (one-time, ~10 sec)..."
    progress_bar = st.progress(0, text=progress_text)

    # Fetch data for all tickers in batch
    peer_records = []
    total = len(tickers)

    for idx, ticker in enumerate(tickers):
        try:
            # Update progress
            progress_bar.progress((idx + 1) / total, text=progress_text)

            stock = yf.Ticker(ticker)
            info = stock.info

            # Get basic company info
            record = {
                "ticker": ticker,
                "industry": info.get("industry"),
                "sector": info.get("sector"),
                "marketCap": info.get("marketCap"),
            }

            # Skip if missing critical data
            if not all([record["industry"], record["marketCap"]]):
                continue

            # Calculate ratios
            income = stock.financials
            balance = stock.balance_sheet

            if not income.empty and not balance.empty:
                # Get most recent period data
                net_income = income.iloc[:, 0].get("Net Income")
                revenue = income.iloc[:, 0].get("Total Revenue")
                gross_profit = income.iloc[:, 0].get("Gross Profit")
                equity = balance.iloc[:, 0].get("Stockholders Equity")
                total_assets = balance.iloc[:, 0].get("Total Assets")
                current_assets = balance.iloc[:, 0].get("Current Assets")
                current_liabilities = balance.iloc[:, 0].get("Current Liabilities")

                # Calculate ROE
                if net_income is not None and equity is not None and equity != 0:
                    record["ROE"] = (net_income / equity) * 100

                # Calculate ROA
                if net_income is not None and total_assets is not None and total_assets != 0:
                    record["ROA"] = (net_income / total_assets) * 100

                # Calculate Net Profit Margin
                if net_income is not None and revenue is not None and revenue != 0:
                    record["Net Profit Margin"] = (net_income / revenue) * 100

                # Calculate Gross Profit Margin
                if gross_profit is not None and revenue is not None and revenue != 0:
                    record["Gross Profit Margin"] = (gross_profit / revenue) * 100

                # Calculate Current Ratio
                if (
                    current_assets is not None
                    and current_liabilities is not None
                    and current_liabilities != 0
                ):
                    record["Current Ratio"] = current_assets / current_liabilities

            peer_records.append(record)
            time.sleep(0.1)  # Small delay between API calls

        except (KeyError, ValueError, TypeError, AttributeError, IndexError):
            # Skip tickers with errors
            continue

    # Create DataFrame
    df = pd.DataFrame(peer_records)

    # Cache the result
    _PEER_DATA_CACHE[sector] = df

    # Clear progress bar
    progress_bar.empty()

    return df


def _map_ratio_name_to_column(ratio_name):
    """Map display ratio name to DataFrame column name"""
    # Handle both the key and display names
    mapping = {
        "ROE": "ROE",
        "ROE (Return on Equity)": "ROE",
        "Return on Equity (ROE)": "ROE",
        "ROA": "ROA",
        "ROA (Return on Assets)": "ROA",
        "Return on Assets (ROA)": "ROA",
        "Net Profit Margin": "Net Profit Margin",
        "Gross Profit Margin": "Gross Profit Margin",
        "Current Ratio": "Current Ratio",
        "Quick Ratio": "Quick Ratio",
    }
    return mapping.get(ratio_name)


def _get_peer_candidates(sector, _cap_category):
    """
    Get a list of potential peer company tickers based on sector

    Args:
        sector (str): Company sector
        cap_category (str): Market cap category (not used for initial filtering)

    Returns:
        list: List of ticker symbols to check as peers
    """
    # Expanded ticker list (Russell 1000 major constituents by sector)
    sector_tickers = {
        "Technology": [
            # Mega cap tech
            "AAPL",
            "MSFT",
            "GOOGL",
            "GOOG",
            "META",
            "NVDA",
            "TSLA",
            # Software & Cloud
            "CRM",
            "ORCL",
            "ADBE",
            "NOW",
            "INTU",
            "WDAY",
            "PANW",
            "CRWD",
            "DDOG",
            "ZS",
            "SNOW",
            "MDB",
            "NET",
            "TEAM",
            "ZM",
            "DOCU",
            "OKTA",
            "VEEV",
            "ANSS",
            "CDNS",
            "SNPS",
            "FTNT",
            # Semiconductors
            "INTC",
            "AMD",
            "QCOM",
            "AVGO",
            "TXN",
            "AMAT",
            "MU",
            "LRCX",
            "ADI",
            "MCHP",
            "KLAC",
            "NXPI",
            "MRVL",
            "ON",
            "MPWR",
            "SWKS",
            # IT Services & Hardware
            "IBM",
            "CSCO",
            "SHOP",
            "SQ",
            "PYPL",
            "ACN",
            "ADSK",
            "HPQ",
            "DELL",
            "HPE",
            "NTAP",
            "WDC",
            "STX",
            "AKAM",
            "ANET",
            "FFIV",
            # E-commerce & Internet
            "AMZN",
            "BABA",
            "JD",
            "MELI",
            "EBAY",
            "ETSY",
            "W",
            "PINS",
            # Gaming & Entertainment Tech
            "EA",
            "TTWO",
            "RBLX",
            "U",
            "MTCH",
            "NFLX",
            "DIS",
            "ROKU",
        ],
        "Healthcare": [
            # Pharma (Large Cap)
            "JNJ",
            "UNH",
            "PFE",
            "ABBV",
            "MRK",
            "LLY",
            "BMY",
            "AMGN",
            "GILD",
            "REGN",
            "BIIB",
            "MRNA",
            "VRTX",
            "ILMN",
            "ALXN",
            "INCY",
            # Pharma (Mid Cap)
            "NBIX",
            "JAZZ",
            "UTHR",
            "EXEL",
            "BMRN",
            "SGEN",
            "HALO",
            # Medical Devices
            "TMO",
            "ABT",
            "DHR",
            "MDT",
            "ISRG",
            "SYK",
            "BSX",
            "EW",
            "ZBH",
            "BAX",
            "BDX",
            "HOLX",
            "ALGN",
            "DXCM",
            "IDXX",
            "IQV",
            "RMD",
            "PODD",
            "TDOC",
            "IRTC",
            "VEEV",
            # Health Insurance & Services
            "CVS",
            "CI",
            "HUM",
            "CNC",
            "ANTM",
            "MOH",
            "ELV",
            # Biotech
            "ZTS",
            "TECH",
            "ARWR",
            "CRSP",
            "NTLA",
            "EDIT",
            "BEAM",
            "BLUE",
            "FOLD",
            "RARE",
            "IONS",
            "SRPT",
            # Diagnostics & Research
            "A",
            "DGX",
            "LH",
            "QGEN",
            "MTD",
            "QDEL",
            "CDNA",
        ],
        "Financial Services": [
            # Banks (Large Cap)
            "JPM",
            "BAC",
            "WFC",
            "C",
            "USB",
            "PNC",
            "TFC",
            "COF",
            "BK",
            "STT",
            "FITB",
            "HBAN",
            "RF",
            "CFG",
            "KEY",
            # Investment Banks & Brokerages
            "GS",
            "MS",
            "SCHW",
            "BLK",
            "SPGI",
            "MCO",
            "MSCI",
            "ICE",
            "CME",
            "NDAQ",
            "MKTX",
            "IBKR",
            "VIRT",
            # Insurance
            "BRK.B",
            "AXP",
            "CB",
            "PGR",
            "TRV",
            "ALL",
            "AIG",
            "MET",
            "PRU",
            "AFL",
            "HIG",
            "CNA",
            "WRB",
            "RNR",
            "CINF",
            # Asset Management
            "MMC",
            "AON",
            "AJG",
            "WTW",
            "BEN",
            "IVZ",
            "TROW",
            "APAM",
            # REITs (Financial)
            "AMT",
            "PLD",
            "CCI",
            "EQIX",
            "PSA",
            "DLR",
            "SPG",
            "O",
            "WELL",
            "AVB",
            "EQR",
            "VTR",
            "ARE",
            "MAA",
            "UDR",
            "CPT",
            # Consumer Finance
            "V",
            "MA",
            "PYPL",
            "SQ",
            "AFRM",
            "UPST",
            "LC",
            "SOFI",
            # Fintech
            "FIS",
            "FISV",
            "COIN",
            "HOOD",
        ],
        "Consumer Cyclical": [
            # E-commerce & Retail
            "AMZN",
            "HD",
            "LOW",
            "TJX",
            "ROST",
            "BKNG",
            "EBAY",
            "ETSY",
            "W",
            "CHWY",
            "BBBY",
            "WSM",
            "RH",
            "ULTA",
            "AEO",
            "ANF",
            # Automotive
            "TSLA",
            "F",
            "GM",
            "RIVN",
            "LCID",
            "NIO",
            "LI",
            "XPEV",
            # Restaurants & Food Services
            "MCD",
            "SBUX",
            "YUM",
            "CMG",
            "QSR",
            "DPZ",
            "DNKN",
            "WEN",
            "DRI",
            "EAT",
            "TXRH",
            "BLMN",
            "CAKE",
            "PLAY",
            # Apparel & Footwear
            "NKE",
            "LULU",
            "DECK",
            "CROX",
            "SKX",
            "UAA",
            "VFC",
            "RL",
            "PVH",
            "HBI",
            "GIII",
            "TLRD",
            # Auto Parts & Services
            "ORLY",
            "AZO",
            "AAP",
            "GPC",
            "DKS",
            "BGFV",
            # Home Improvement & Furnishings
            "POOL",
            "BECN",
            "LOVE",
            "FBIN",
            # Consumer Discretionary Services
            "ABNB",
            "EXPE",
            "TRIP",
            "MAR",
            "HLT",
            "H",
            "WH",
            "IHG",
            "WYNN",
            "LVS",
            "MGM",
            "CZR",
            "PENN",
            "DKNG",
            "BALY",
            # Leisure & Entertainment
            "CCL",
            "RCL",
            "NCLH",
            "LYV",
            "MSG",
            "MSGS",
            # Retail (General)
            "TGT",
            "DG",
            "DLTR",
            "BBY",
            "M",
            "KSS",
            "JWN",
        ],
        "Consumer Defensive": [
            # Retail (Grocery & Discount)
            "WMT",
            "COST",
            "TGT",
            "KR",
            "SYY",
            "USFD",
            "PFGC",
            # Beverages
            "KO",
            "PEP",
            "MNST",
            "KDP",
            "CELH",
            "STZ",
            "TAP",
            "SAM",
            "BF.B",
            "DEO",
            # Food & Packaged Goods
            "PG",
            "MDLZ",
            "GIS",
            "HSY",
            "K",
            "CAG",
            "SJM",
            "CPB",
            "HRL",
            "MKC",
            "LW",
            "POST",
            "BGS",
            "LANC",
            "JJSF",
            # Tobacco
            "PM",
            "MO",
            "BTI",
            # Personal Care & Household
            "EL",
            "CL",
            "KMB",
            "CHD",
            "CLX",
            "EPC",
            "COTY",
            "ELF",
            # Consumer Staples Services
            "KHC",
            "CALM",
            "FLO",
            "INGR",
            "SENEA",
            "SMPL",
        ],
        "Energy": [
            # Oil & Gas (Integrated)
            "XOM",
            "CVX",
            "COP",
            "BP",
            "SHEL",
            "TTE",
            # Oil & Gas (E&P)
            "EOG",
            "OXY",
            "DVN",
            "HES",
            "FANG",
            "PXD",
            "MRO",
            "APA",
            "CTRA",
            "CLR",
            "PR",
            "MTDR",
            "AR",
            "CHRD",
            "MGY",
            "SM",
            # Oil & Gas (Services)
            "SLB",
            "HAL",
            "BKR",
            "FTI",
            "NOV",
            "HP",
            "WFRD",
            "NINE",
            "LBRT",
            "PUMP",
            "OII",
            # Oil & Gas (Refining)
            "MPC",
            "PSX",
            "VLO",
            "HFC",
            "DK",
            "CIVI",
            "PBF",
            # Oil & Gas (Midstream)
            "KMI",
            "WMB",
            "OKE",
            "EPD",
            "ET",
            "MPLX",
            "TRGP",
            "PAA",
            "AM",
            "LNG",
            "ENLC",
            "DTM",
            # Alternative Energy
            "NEE",
            "ENPH",
            "SEDG",
            "FSLR",
            "RUN",
            "NOVA",
            "PLUG",
            "BE",
        ],
        "Industrials": [
            # Aerospace & Defense
            "BA",
            "RTX",
            "LMT",
            "GD",
            "NOC",
            "HWM",
            "TXT",
            "LHX",
            "HII",
            "AJRD",
            "KTOS",
            "AVAV",
            "SPR",
            # Industrial Conglomerates
            "HON",
            "GE",
            "MMM",
            "EMR",
            "ITW",
            "ETN",
            "ROK",
            "AME",
            "DOV",
            "PH",
            "IR",
            # Machinery & Equipment
            "CAT",
            "DE",
            "PCAR",
            "CMI",
            "OSK",
            "WAB",
            "AGCO",
            "MTW",
            "TEX",
            "GNRC",
            "HUBB",
            "AOS",
            "RBC",
            "SNA",
            "TTC",
            # Transportation & Logistics
            "UNP",
            "UPS",
            "NSC",
            "FDX",
            "CSX",
            "JBHT",
            "ODFL",
            "KNX",
            "CHRW",
            "EXPD",
            "XPO",
            "R",
            "UBER",
            "LYFT",
            "DASH",
            "GXO",
            # Construction & Engineering
            "CARR",
            "JCI",
            "FLS",
            "J",
            "PWR",
            "BLDR",
            "MTZ",
            "WCC",
            "ACM",
            "STRL",
            "MAS",
            "OC",
            "VMC",
            "MLM",
            # Industrial Services
            "WM",
            "RSG",
            "WCN",
            "CVCO",
            "ROP",
            "ITT",
            "FAST",
            "WSO",
            "GWW",
            "WCC",
            "DCI",
            "MSM",
        ],
        "Communication Services": [
            # Internet & Media
            "GOOGL",
            "GOOG",
            "META",
            "NFLX",
            "DIS",
            "PARA",
            "WBD",
            "FOXA",
            "FOX",
            "SPOT",
            "RBLX",
            "MTCH",
            "PINS",
            "SNAP",
            "ROKU",
            "FUBO",
            "BMBL",
            "IAC",
            "LBRDA",
            "LBRDK",
            "SIRI",
            # Telecom
            "CMCSA",
            "VZ",
            "T",
            "TMUS",
            "CHTR",
            "LUMN",
            "SHEN",
            "FTR",
            "USM",
            "CABO",
            # Gaming & Entertainment
            "EA",
            "TTWO",
            "ATVI",
            "ZNGA",
            "U",
            "PLTK",
            # Advertising & Marketing
            "OMC",
            "IPG",
            "MGNI",
            "TTD",
            "APPS",
            "CRTO",
            "PUBM",
            "MAX",
            # Publishing & News
            "NYT",
            "NWSA",
            "NWS",
            "LEE",
            "GCI",
            "MCS",
        ],
        "Real Estate": [
            # REITs (Data Centers & Infrastructure)
            "AMT",
            "CCI",
            "EQIX",
            "DLR",
            "SBAC",
            "QTS",
            "CONE",
            "SAFE",
            # REITs (Industrial & Logistics)
            "PLD",
            "PSA",
            "CUBE",
            "EXR",
            "NSA",
            "LSI",
            "REXR",
            "FR",
            "STAG",
            "TRNO",
            "EGP",
            # REITs (Residential)
            "AVB",
            "EQR",
            "MAA",
            "UDR",
            "CPT",
            "ESS",
            "AIRC",
            "AIV",
            "BRT",
            "CSR",
            "IRT",
            "NXRT",
            # REITs (Retail)
            "SPG",
            "O",
            "REG",
            "KIM",
            "BRX",
            "WPC",
            "ADC",
            "GTY",
            "ROIC",
            "RPAI",
            "AKR",
            "SITE",
            "STOR",
            # REITs (Office)
            "BXP",
            "VNO",
            "SLG",
            "HPP",
            "DEI",
            "JBGS",
            "PGRE",
            "CUZ",
            # REITs (Healthcare)
            "WELL",
            "VTR",
            "PEAK",
            "OHI",
            "HR",
            "DOC",
            "LTC",
            "SBRA",
            # REITs (Specialty)
            "ARE",
            "INVH",
            "AMH",
            "SUI",
            "ELS",
            "VRE",
            "COLD",
            "IIPR",
            "VICI",
            # Real Estate Services
            "CBRE",
            "JLL",
            "CSGP",
            "Z",
            "RDFN",
            "OPEN",
            "COMP",
            "EXPI",
        ],
        "Utilities": [
            # Electric Utilities
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
            "DTE",
            "PPL",
            "ES",
            "FE",
            "ETR",
            "AEE",
            "CMS",
            "CNP",
            "EVRG",
            "LNT",
            "NI",
            "PNW",
            "AES",
            "VST",
            "ATO",
            "NRG",
            "OGE",
            # Gas Utilities
            "AWK",
            "ATO",
            "SJW",
            "YORW",
            "MSEX",
            "SJI",
            "NJR",
            "SR",
            # Water Utilities
            "AWK",
            "WTR",
            "CWT",
            "ARTNA",
            "SJW",
            "MSEX",
            # Multi-Utilities
            "DTE",
            "CMS",
            "NI",
            "MDU",
            "BKH",
            "AVA",
            "OTTR",
        ],
        "Basic Materials": [
            # Chemicals
            "LIN",
            "APD",
            "ECL",
            "DD",
            "DOW",
            "EMN",
            "CE",
            "FMC",
            "IFF",
            "ALB",
            "SEE",
            "PPG",
            "SHW",
            "RPM",
            "AXTA",
            "HUN",
            "OLN",
            "NEU",
            "CC",
            "ESI",
            "KWR",
            "CBT",
            "NGVT",
            # Metals & Mining
            "NEM",
            "FCX",
            "NUE",
            "STLD",
            "CLF",
            "X",
            "RS",
            "CMC",
            "MP",
            "IE",
            "CENX",
            "ZEUS",
            "ATI",
            "KALU",
            "WOR",
            # Construction Materials
            "VMC",
            "MLM",
            "SUM",
            "USCR",
            "USLM",
            "CRH",
            "MTX",
            # Agricultural Chemicals & Fertilizers
            "CTVA",
            "CF",
            "MOS",
            "NTR",
            "FMC",
            "SMG",
            "IPI",
            # Paper & Packaging
            "PKG",
            "IP",
            "WRK",
            "AMCR",
            "CCK",
            "BALL",
            "AVY",
            "GPK",
            "SON",
            "SEE",
            "SLVM",
            # Steel
            "NUE",
            "STLD",
            "CLF",
            "X",
            "RS",
            "CMC",
            "ZEUS",
            "TMST",
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
