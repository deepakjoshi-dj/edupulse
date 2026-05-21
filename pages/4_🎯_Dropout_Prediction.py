"""Dropout Prediction — ML model flagging at-risk students from first-30-day activity."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from src.utils import charts
from src.utils.db import query, warehouse_exists

st.set_page_config(page_title="Dropout Prediction", page_icon="🎯", layout="wide")
st.title("🎯 Dropout Prediction")
st.caption(
    "Gradient Boosting classifier predicting whether a student will withdraw, "
    "using demographics + engagement signals from the first 30 days of the course."
)

if not warehouse_exists():
    st.error("Warehouse not built. Run `python -m src.etl.run_pipeline` first.")
    st.stop()

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "dropout_model.joblib"
if not MODEL_PATH.exists():
    st.error(
        "Model artifact not found. Run `python -m src.ml.train_dropout_model` "
        "(or `python -m src.etl.run_pipeline`) to train it."
    )
    st.stop()


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH)


artifact = load_model()
pipe = artifact["pipeline"]
metrics = artifact["metrics"]
top_importances = artifact["feature_importance_top"]
numeric_features = artifact["numeric_features"]
categorical_features = artifact["categorical_features"]

# -------------------------------------------------------------------- Metrics
st.subheader("Model performance (held-out test set)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Accuracy", f"{metrics['accuracy']:.3f}")
m2.metric("ROC AUC", f"{metrics['roc_auc']:.3f}")
m3.metric("Test rows", f"{metrics['test_size']:,}")
m4.metric("Baseline dropout rate", f"{metrics['dropout_rate']:.1%}")

st.caption(
    "ROC AUC of 1.0 = perfect, 0.5 = random. Accuracy alone is misleading for "
    "imbalanced classes — judge by AUC."
)

# -------------------------------------------------------------------- Importance
st.subheader("What drives the prediction?")
if top_importances:
    imp_df = pd.DataFrame(top_importances).sort_values("importance")
    st.plotly_chart(
        charts.bar(imp_df, x="importance", y="feature",
                   title="Top feature importances",
                   orientation="h"),
        use_container_width=True,
    )

st.divider()

# -------------------------------------------------------------------- Live scoring
st.subheader("Score current learners")
st.markdown(
    "Pick a course presentation. The model scores all enrolled students using "
    "first-30-day data, ranks them by predicted withdrawal probability, and "
    "lets you export the at-risk list."
)

courses = query(
    """
    SELECT DISTINCT code_module, code_presentation
    FROM v_student_features
    ORDER BY code_module, code_presentation
    """
)
courses["label"] = courses["code_module"] + " / " + courses["code_presentation"]
choice = st.selectbox("Course presentation", courses["label"].tolist())
sel = courses[courses["label"] == choice].iloc[0]

risk_threshold = st.slider("At-risk probability threshold", 0.10, 0.90, 0.50, 0.05)

cohort = query(
    """
    SELECT *
    FROM v_student_features
    WHERE code_module = ? AND code_presentation = ?
    """,
    (sel["code_module"], sel["code_presentation"]),
)

if cohort.empty:
    st.warning("No students found for this course presentation.")
    st.stop()

features = cohort[numeric_features + categorical_features]
proba = pipe.predict_proba(features)[:, 1]
cohort = cohort.assign(
    dropout_probability=proba,
    risk_flag=(proba >= risk_threshold),
)

at_risk = cohort[cohort["risk_flag"]]
c1, c2, c3 = st.columns(3)
c1.metric("Cohort size", f"{len(cohort):,}")
c2.metric("Flagged at risk", f"{len(at_risk):,}",
          delta=f"{len(at_risk) / len(cohort):.1%} of cohort")
c3.metric("Actual withdrawal in this cohort",
          f"{cohort['is_withdrawn'].sum():,}",
          delta=f"{cohort['is_withdrawn'].mean():.1%}")

# Top-N at-risk leaderboard
st.markdown("**Top 20 highest-risk students in this cohort**")
display = (
    cohort.nlargest(20, "dropout_probability")[
        ["id_student", "dropout_probability", "total_clicks", "active_days",
         "avg_assessment_score", "assessments_submitted", "final_result"]
    ]
    .rename(columns={
        "dropout_probability": "Risk %",
        "total_clicks": "Clicks (30d)",
        "active_days": "Active days (30d)",
        "avg_assessment_score": "Avg score (30d)",
        "assessments_submitted": "Assessments (30d)",
        "final_result": "Actual outcome",
    })
)
display["Risk %"] = (display["Risk %"] * 100).round(1)
st.dataframe(display, hide_index=True, use_container_width=True)

# Download
csv = (
    cohort.sort_values("dropout_probability", ascending=False)
    .loc[:, ["id_student", "code_module", "code_presentation",
             "dropout_probability", "risk_flag", "final_result"]]
    .to_csv(index=False)
    .encode("utf-8")
)
st.download_button(
    "Download full risk-scored cohort (CSV)",
    csv,
    file_name=f"at_risk_{sel['code_module']}_{sel['code_presentation']}.csv",
    mime="text/csv",
)
