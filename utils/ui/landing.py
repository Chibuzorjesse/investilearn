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


def render_additional_resources() -> None:
    """Render additional resources section"""
    st.markdown("---")
    st.markdown("### 📚 Additional Resources")

    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        st.markdown("#### 📄 SEC Filings")
        st.markdown("- 10-K Annual Report")
        st.markdown("- 10-Q Quarterly Report")
        st.markdown("- 8-K Current Report")
        st.markdown("- Proxy Statements")

    with col_res2:
        st.markdown("#### 📊 Historical Performance")
        st.markdown("- 5-Year Stock Chart")
        st.markdown("- Dividend History")
        st.markdown("- Earnings History")
        st.markdown("- Share Buyback Activity")

    with col_res3:
        st.markdown("#### 🎓 Learn More")
        st.markdown("- What is Fundamental Analysis?")
        st.markdown("- Understanding Financial Ratios")
        st.markdown("- Long-term Investment Strategies")
        st.markdown("- Reading Financial Statements")
