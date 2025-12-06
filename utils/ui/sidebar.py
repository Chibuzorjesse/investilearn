"""Sidebar component"""

import streamlit as st


def render_sidebar(company_context: dict | None = None) -> tuple[bool, str]:
    """
    Render simplified sidebar

    Args:
        company_context: Optional context about current company being viewed

    Returns:
        Tuple of (ai_enabled, confidence_level) from session state
    """
    with st.sidebar:
        st.markdown("## 💡 Quick Tips")

        st.info(
            """
            **Getting Started:**
            - Search for any company above
            - Click ❓ buttons to learn about metrics
            - Click 💬 button to ask the coach

            **Confidence Levels:**
            - 🟢 High: Well-established
            - 🟡 Medium: Context-dependent
            - 🔴 Low: Consult an expert
            """
        )

        if "feedback_count" in st.session_state and st.session_state.feedback_count > 0:
            st.success(f"📊 Thanks for {st.session_state.feedback_count} pieces of feedback!")

    # Return from session state
    ai_enabled = st.session_state.get("ai_enabled", True)
    confidence_level = st.session_state.get("confidence_level", "Show all")
    return ai_enabled, confidence_level
