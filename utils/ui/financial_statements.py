"""Financial statements component with Sankey diagrams"""

import streamlit as st

from utils.visualizations import create_sankey_diagram


def render_financial_statements(income_stmt, balance_sheet, cash_flow) -> None:
    """
    Render financial statements section with Sankey diagrams

    Args:
        income_stmt: Income statement DataFrame
        balance_sheet: Balance sheet DataFrame
        cash_flow: Cash flow DataFrame
    """
    st.markdown("### 📊 Financial Statements")
    st.markdown("*Sankey flow diagrams showing money movement*")

    tab1, tab2, tab3 = st.tabs(["Income Statement", "Cash Flow", "Balance Sheet"])

    with tab1:
        col_info, col_coach = st.columns([4, 1])
        with col_info:
            st.info("💡 **Income Statement** shows how revenue flows through expenses to profit")
        with col_coach:
            ai_enabled = st.session_state.get("ai_enabled", True)
            llm_coach_enabled = st.session_state.get("llm_coach", True)
            if st.button(
                "💬 Ask Coach",
                key="coach_income_stmt",
                use_container_width=True,
                disabled=not (ai_enabled and llm_coach_enabled),
            ):
                st.session_state.coach_auto_prompt = "Explain what an Income Statement is, what it shows, and how I should interpret it for fundamental investing. What key metrics should I look for?"
                st.session_state.open_coach = True
                st.rerun()

        if income_stmt is not None:
            fig = create_sankey_diagram(income_stmt, "income")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No income statement data available")

    with tab2:
        col_info, col_coach = st.columns([4, 1])
        with col_info:
            st.info("💡 **Cash Flow** tracks actual cash in and out of the business")
        with col_coach:
            ai_enabled = st.session_state.get("ai_enabled", True)
            llm_coach_enabled = st.session_state.get("llm_coach", True)
            if st.button(
                "💬 Ask Coach",
                key="coach_cash_flow",
                use_container_width=True,
                disabled=not (ai_enabled and llm_coach_enabled),
            ):
                st.session_state.coach_auto_prompt = "Explain what a Cash Flow Statement is, what it shows, and why it's important for fundamental investing. What should I look for in the operating, investing, and financing activities?"
                st.session_state.open_coach = True
                st.rerun()

        if cash_flow is not None:
            fig = create_sankey_diagram(cash_flow, "cashflow")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No cash flow data available")

    with tab3:
        col_info, col_coach = st.columns([4, 1])
        with col_info:
            st.info("💡 **Balance Sheet** shows what the company owns vs owes")
        with col_coach:
            ai_enabled = st.session_state.get("ai_enabled", True)
            llm_coach_enabled = st.session_state.get("llm_coach", True)
            if st.button(
                "💬 Ask Coach",
                key="coach_balance_sheet",
                use_container_width=True,
                disabled=not (ai_enabled and llm_coach_enabled),
            ):
                st.session_state.coach_auto_prompt = "Explain what a Balance Sheet is, what it shows, and how to interpret assets, liabilities, and equity for fundamental investing. What key ratios are derived from it?"
                st.session_state.open_coach = True
                st.rerun()

        if balance_sheet is not None:
            fig = create_sankey_diagram(balance_sheet, "balance")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No balance sheet data available")
