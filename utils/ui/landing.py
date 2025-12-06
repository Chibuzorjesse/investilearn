"""Landing page component"""

import streamlit as st


def render_landing_page() -> None:
    """Render landing page content when no search is active"""
    st.markdown("---")

    if st.session_state.first_visit:
        st.success("👋 Welcome to InvestiLearn!")
        st.markdown(
            """
            This dashboard helps you learn fundamental investing by analyzing
            real company data. Let's get started with a quick tour:
            """
        )

        col_tour1, col_tour2, col_tour3 = st.columns(3)

        with col_tour1:
            st.info(
                """
                **1️⃣ Start Simple**

                Search for a company you know
                (like Apple, Microsoft, or Tesla)
                """
            )

        with col_tour2:
            st.info(
                """
                **2️⃣ Explore with AI**

                Click ❓ buttons to learn about
                any metric you don't understand
                """
            )

        with col_tour3:
            st.info(
                """
                **3️⃣ Give Feedback**

                Help improve the AI by rating
                explanations helpful or not
                """
            )

        if st.button("Got it! Let's explore 🚀"):
            st.session_state.first_visit = False
            st.rerun()

        st.markdown("---")

    st.info("👆 Enter a company name or ticker symbol above to begin your analysis")

    st.markdown("### 🎯 What is Fundamental Investing?")
    st.markdown(
        """
    Fundamental investing is a long-term investment strategy that focuses on analyzing a company's
    financial health, business model, and competitive advantages to identify high-quality companies
    worth holding for decades.

    **Key Principles:**
    - 📊 Analyze financial statements thoroughly
    - 📈 Focus on sustainable competitive advantages
    - ⏳ Think long-term (5-10+ years)
    - 💼 Invest in businesses you understand
    - 📉 Buy quality companies at reasonable prices
    """
    )

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
