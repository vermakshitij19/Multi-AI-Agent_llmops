
import os
import requests
import streamlit as st

from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:9999")

st.set_page_config(
    page_title="Multi AI Agent",
    layout="centered"
)

st.title("Multi AI Agent")

# --------------------------------------------------
# Initialize Session State
# --------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_error" not in st.session_state:
    st.session_state.last_error = None

# --------------------------------------------------
# AI Agent Configuration
# --------------------------------------------------

system_prompt = st.text_area(
    "Define your AI Agent:",
    height=70,
    placeholder="Example: You are a helpful DevOps engineer.",
    key="system_prompt"
)

selected_model = st.selectbox(
    "Select your AI model:",
    options=settings.ALLOWED_MODEL_NAMES,
    key="model_selector"
)

# --------------------------------------------------
# Agent Options
# --------------------------------------------------

allow_web_search = st.checkbox(
    "Allow web search",
    value=False,
    key="allow_web_search"
)

evaluate_response_enabled = st.checkbox(
    "Evaluate AI response using LLM Judge",
    value=True,
    key="evaluate_response"
)

# --------------------------------------------------
# User Query
# --------------------------------------------------

user_query = st.text_area(
    "Enter your query:",
    height=150,
    placeholder="Ask your AI Agent a question...",
    key="user_query"
)

# --------------------------------------------------
# Submit Query
# --------------------------------------------------

if st.button("Ask Agent", type="primary"):

    if not user_query.strip():
        st.warning("Please enter your query first.")

    else:

        payload = {
            "model_name": selected_model,
            "system_prompt": system_prompt,
            "messages": [user_query.strip()],
            "allow_search": allow_web_search,
            "evaluate_response": evaluate_response_enabled
        }

        st.session_state.last_error = None

        logger.info(
            "Sending chat request. Evaluation enabled: %s",
            evaluate_response_enabled
        )

        try:

            with st.spinner("AI Agent is processing your request..."):

                response = requests.post(
                    f"{API_URL}/chat",
                    json=payload,
                    timeout=120
                )

                response.raise_for_status()

                result = response.json()

            # Save response in session state

            chat_entry = {
                "question": user_query.strip(),
                "response": result.get("response", ""),
                "evaluation": result.get("evaluation"),
                "evaluation_enabled": evaluate_response_enabled,
                "model": selected_model
            }

            st.session_state.chat_history.append(chat_entry)

        except requests.exceptions.ConnectionError:

            logger.exception("Backend connection failed")

            st.session_state.last_error = (
                "Cannot connect to FastAPI backend."
            )

        except requests.exceptions.Timeout:

            logger.exception("Backend request timed out")

            st.session_state.last_error = (
                "The request timed out. Please try again."
            )

        except requests.exceptions.HTTPError as error:

            logger.exception("Backend returned HTTP error")

            st.session_state.last_error = (
                f"Backend HTTP error: "
                f"{error.response.status_code} - "
                f"{error.response.text}"
            )

        except requests.exceptions.RequestException as error:

            logger.exception("Request failed")

            st.session_state.last_error = str(error)

        except (KeyError, TypeError, ValueError) as error:

            logger.exception("Unexpected API response")

            st.session_state.last_error = (
                f"Unexpected response format: {error}"
            )

# --------------------------------------------------
# Display Errors
# --------------------------------------------------

if st.session_state.last_error:
    st.error(st.session_state.last_error)

# --------------------------------------------------
# Display Conversation History
# --------------------------------------------------

if st.session_state.chat_history:

    st.divider()
    st.header("Conversation History")

    for index, chat in enumerate(st.session_state.chat_history):

        with st.container(border=True):

            st.caption(
                f"Question {index + 1} | Model: {chat['model']}"
            )

            st.markdown("**You:**")
            st.write(chat["question"])

            st.markdown("**AI Agent Response:**")
            st.markdown(chat["response"])

            evaluation = chat["evaluation"]

            if evaluation is not None:

                st.subheader("LLM Judge Evaluation")

                col1, col2 = st.columns(2)

                col1.metric(
                    "Overall Score",
                    f"{evaluation['overall_score']}/5"
                )

                col2.metric(
                    "Evaluation Status",
                    "Completed"
                )

                with st.expander("View evaluation details"):
                    st.json(evaluation)

            elif chat["evaluation_enabled"]:

                st.warning(
                    "Evaluation was enabled, but no evaluation was returned."
                )

            else:

                st.info(
                    "LLM Judge evaluation was disabled for this request."
                )

    if st.button("Clear Conversation History"):

        st.session_state.chat_history = []
        st.session_state.last_error = None
        st.rerun()
