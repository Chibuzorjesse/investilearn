"""LLM Coach chat interface component"""

import streamlit as st

from utils.llm_coach import get_coach


def render_coach_chat(company_context: dict | None = None) -> None:
    """
    Render the LLM coach chat interface in sidebar

    Args:
        company_context: Optional company/metric context for questions
    """
    st.markdown("### 💬 Ask the Investment Coach")

    # Initialize chat history in session state
    if "coach_messages" not in st.session_state:
        st.session_state.coach_messages = []

    if "coach_model" not in st.session_state:
        st.session_state.coach_model = "qwen2.5:14b"

    # Model selector
    with st.expander("⚙️ Coach Settings"):
        model_options = [
            "qwen2.5:14b",
            "qwen2.5:7b",
            "llama3.2:3b",
            "gpt-oss:20b",
        ]
        selected_model = st.selectbox(
            "Model",
            options=model_options,
            index=model_options.index(st.session_state.coach_model)
            if st.session_state.coach_model in model_options
            else 0,
            help="Select the LLM model to use for coaching",
        )
        st.session_state.coach_model = selected_model

        if st.button("Clear Conversation"):
            st.session_state.coach_messages = []
            st.rerun()

    # Check coach availability
    coach = get_coach(model=st.session_state.coach_model)
    available, status_msg = coach.check_availability()

    if not available:
        st.error(f"❌ Coach unavailable: {status_msg}")
        st.caption(
            "Make sure Ollama is running and the model is downloaded:\n"
            f"```bash\nollama pull {st.session_state.coach_model}\n```"
        )
        return

    st.success(f"✅ Coach ready ({st.session_state.coach_model})")

    # Display chat history
    for msg in st.session_state.coach_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Show confidence badge for assistant messages
            if msg["role"] == "assistant" and "confidence" in msg:
                confidence = msg["confidence"]
                if confidence == "high":
                    badge = "🟢 High Confidence"
                elif confidence == "medium":
                    badge = "🟡 Medium Confidence"
                elif confidence == "low":
                    badge = "🔴 Low Confidence"
                else:
                    badge = ""

                if badge:
                    st.caption(badge)

    # Chat input
    if prompt := st.chat_input("Ask about investing concepts..."):
        # Add user message
        st.session_state.coach_messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get coach response
        with st.chat_message("assistant"):
            with st.spinner("Coach is thinking..."):
                response_data = coach.ask(
                    question=prompt,
                    context=company_context,
                    conversation_history=st.session_state.coach_messages[:-1],
                )

            st.markdown(response_data["response"])

            # Show confidence
            confidence = response_data.get("confidence", "unknown")
            if confidence == "high":
                st.caption("🟢 High Confidence")
            elif confidence == "medium":
                st.caption("🟡 Medium Confidence - Consider verifying")
            elif confidence == "low":
                st.caption("🔴 Low Confidence - Please consult additional sources")

            # Add assistant message to history
            st.session_state.coach_messages.append(
                {
                    "role": "assistant",
                    "content": response_data["response"],
                    "confidence": confidence,
                }
            )

        # Feedback
        col_fb1, col_fb2 = st.columns(2)
        msg_count = len(st.session_state.coach_messages)
        with col_fb1:
            if st.button("👍 Helpful", key=f"fb_up_{msg_count}"):
                st.toast("Thanks for the feedback!", icon="✅")
                if "feedback_count" not in st.session_state:
                    st.session_state.feedback_count = 0
                st.session_state.feedback_count += 1

        with col_fb2:
            if st.button("👎 Not helpful", key=f"fb_down_{msg_count}"):
                st.toast("Feedback noted. We'll improve!", icon="📝")

    # Helpful tips
    if len(st.session_state.coach_messages) == 0:
        st.info(
            """
            **💡 Try asking:**
            - "What does ROE mean?"
            - "Is a P/E of 30 high or low?"
            - "How do I read a cash flow statement?"
            - "What's the difference between debt and equity?"
            """
        )

    # Privacy notice
    with st.expander("🔒 Privacy & How This Works"):
        st.caption(
            """
            **100% Local & Private:**
            - Coach runs entirely on your computer via Ollama
            - No data sent to external servers
            - Conversations stored only in your browser session

            **Educational Purpose:**
            - Provides general investment education
            - NOT personalized financial advice
            - Always verify information independently

            **Context-Aware:**
            - When viewing a company, coach has access to:
              - Company name, ticker, sector
              - Specific metrics you're looking at
            - This helps provide relevant, specific answers
            """
        )
