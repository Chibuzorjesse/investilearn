"""Landing page component"""

import streamlit as st


def render_landing_page() -> None:
    """Render landing page content when no search is active"""
    st.markdown("---")

    st.info("👆 Enter a company name or ticker symbol above to begin your analysis")

    st.markdown("### 🔍 How to Use This Dashboard")
    col_help1, col_help2, col_help3 = st.columns(3)

    with col_help1:
        st.markdown("**1️⃣ Search**")
        st.markdown("Enter a company name or ticker to analyze")

    with col_help2:
        st.markdown("**2️⃣ Analyze**")
        st.markdown("Review financial statements, ratios, and news")

    with col_help3:
        st.markdown("**3️⃣ Decide**")
        st.markdown("Make informed long-term investment decisions")


def render_additional_resources(ticker: str | None = None, cik: str | None = None) -> None:
    """
    Render additional resources section with links

    Args:
        ticker: Stock ticker symbol (optional)
        cik: SEC CIK number (optional)
    """
    st.markdown("---")
    st.markdown("### 📚 Additional Resources")

    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        st.markdown("#### 📄 SEC Filings")
        if ticker and cik:
            # SEC EDGAR links
            edgar_base = "https://www.sec.gov/cgi-bin/browse-edgar"
            st.markdown(
                f"- [10-K Annual Report]({edgar_base}?action=getcompany&CIK={cik}&type=10-K)"
            )
            st.markdown(
                f"- [10-Q Quarterly Report]({edgar_base}?action=getcompany&CIK={cik}&type=10-Q)"
            )
            st.markdown(
                f"- [8-K Current Report]({edgar_base}?action=getcompany&CIK={cik}&type=8-K)"
            )
            st.markdown(
                f"- [Proxy Statements]({edgar_base}?action=getcompany&CIK={cik}&type=DEF+14A)"
            )
            st.markdown(f"- [All Filings]({edgar_base}?action=getcompany&CIK={cik}&owner=exclude)")
        else:
            st.caption("Search for a company to see SEC filing links")

    with col_res2:
        st.markdown("#### 📊 Historical Performance")
        if ticker:
            # Yahoo Finance links
            yf_base = f"https://finance.yahoo.com/quote/{ticker}"
            st.markdown(f"- [Stock Chart]({yf_base}/chart)")
            st.markdown(f"- [Historical Data]({yf_base}/history)")
            st.markdown(f"- [Financials]({yf_base}/financials)")
            st.markdown(f"- [Analysis]({yf_base}/analysis)")
        else:
            st.caption("Search for a company to see performance links")

    with col_res3:
        st.markdown("#### 🎓 Learn More")
        st.markdown(
            "- [What is Fundamental Analysis?]"
            "(https://www.investopedia.com/terms/f/"
            "fundamentalanalysis.asp)"
        )
        st.markdown(
            "- [Understanding Financial Ratios]"
            "(https://www.investopedia.com/financial-ratios-4689817)"
        )
        st.markdown(
            "- [Long-term Investing](https://www.investopedia.com/terms/l/longterminvestments.asp)"
        )
        st.markdown(
            "- [Reading Financial Statements]"
            "(https://www.sec.gov/oiea/investor-alerts-and-bulletins/"
            "how-read-financial-statement)"
        )
