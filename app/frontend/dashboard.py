import os
import requests
import pandas as pd
import streamlit as st

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="LLMOps Evaluation Dashboard",
    page_icon="📊",
    layout="wide"
)

API_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:9999"
) + "/evaluations"

# --------------------------------------------------
# Dashboard Header
# --------------------------------------------------

st.title("📊 LLMOps Evaluation Monitoring")
st.caption("Monitor AI response quality using LLM-as-a-Judge.")

# --------------------------------------------------
# Fetch Evaluation History
# --------------------------------------------------

def fetch_evaluations():

    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to FastAPI. Please start the backend.")
        return None

    except requests.exceptions.Timeout:
        st.error("Request timed out while fetching evaluations.")
        return None

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch evaluations: {e}")
        return None


# --------------------------------------------------
# Refresh Button
# --------------------------------------------------

if st.button("🔄 Refresh Dashboard"):
    st.rerun()

# --------------------------------------------------
# Load Data
# --------------------------------------------------

evaluations = fetch_evaluations()

if evaluations is None:
    st.stop()

if not evaluations:

    st.info(
        "No evaluation records found. "
        "Enable LLM Judge in your AI application and submit some queries."
    )
    st.stop()

df = pd.DataFrame(evaluations)

# Convert timestamp into datetime
df["created_at"] = pd.to_datetime(
    df["created_at"],
    errors="coerce"
)

# --------------------------------------------------
# KPI Calculations
# --------------------------------------------------

total_evaluations = len(df)

average_score = df["overall_score"].mean()

highest_score = df["overall_score"].max()

low_score_count = (
    df["overall_score"] < 3
).sum()

# --------------------------------------------------
# KPI Dashboard
# --------------------------------------------------

st.subheader("Evaluation Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Evaluations",
    total_evaluations
)

col2.metric(
    "Average Score",
    f"{average_score:.2f} / 5"
)

col3.metric(
    "Highest Score",
    f"{highest_score:.2f} / 5"
)

col4.metric(
    "Low Score Responses",
    int(low_score_count)
)

st.divider()

# --------------------------------------------------
# Evaluation Metrics Chart
# --------------------------------------------------

st.subheader("Evaluation Score Breakdown")

metric_columns = [
    "relevance",
    "correctness",
    "completeness",
    "clarity"
]

metric_averages = df[metric_columns].mean()

st.bar_chart(
    metric_averages,
    y_label="Average Score",
    x_label="Evaluation Metric"
)

# --------------------------------------------------
# Overall Score Trend
# --------------------------------------------------

st.subheader("AI Response Quality Trend")

trend_df = df.dropna(subset=["created_at"]).copy()

if not trend_df.empty:

    trend_df["date"] = trend_df["created_at"].dt.date

    daily_scores = (
        trend_df.groupby("date")["overall_score"]
        .mean()
        .sort_index()
    )

    st.line_chart(
        daily_scores,
        y_label="Average Overall Score",
        x_label="Evaluation Date"
    )

else:
    st.info("No valid timestamps available for the trend chart.")

# --------------------------------------------------
# Evaluation History
# --------------------------------------------------

st.divider()

st.subheader("Evaluation History")

display_columns = [
    "id",
    "question",
    "overall_score",
    "relevance",
    "correctness",
    "completeness",
    "clarity",
    "created_at"
]

st.dataframe(
    df[display_columns],
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# Individual Evaluation Details
# --------------------------------------------------

st.subheader("Evaluation Details")

for _, record in df.iterrows():

    with st.expander(
        f"Evaluation #{record['id']} | Score: {record['overall_score']}/5"
    ):

        st.markdown("**Question**")
        st.write(record["question"])

        st.markdown("**AI Answer**")
        st.write(record["answer"])

        st.markdown("**Judge Feedback**")
        st.write(record["feedback"])

        detail_col1, detail_col2 = st.columns(2)

        detail_col1.write(
            f"Relevance: {record['relevance']}/5"
        )

        detail_col2.write(
            f"Correctness: {record['correctness']}/5"
        )

        detail_col1.write(
            f"Completeness: {record['completeness']}/5"
        )

        detail_col2.write(
            f"Clarity: {record['clarity']}/5"
        )

        st.caption(
            f"Created at: {record['created_at']}"
        )

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "LLMOps Evaluation Dashboard | "
    "Powered by FastAPI, SQLite, Streamlit and Groq"
)
