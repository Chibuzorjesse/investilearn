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
        st.info("💡 **Income Statement** shows how revenue flows through expenses to profit")
        if income_stmt is not None:
            fig = create_sankey_diagram(income_stmt, "income")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No income statement data available")

    with tab2:
        st.info("💡 **Cash Flow** tracks actual cash in and out of the business")
        if cash_flow is not None:
            fig = create_sankey_diagram(cash_flow, "cashflow")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No cash flow data available")

    with tab3:
        st.info("💡 **Balance Sheet** shows what the company owns vs owes")
        if balance_sheet is not None:
            fig = create_sankey_diagram(balance_sheet, "balance")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No balance sheet data available")
