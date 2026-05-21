"""Learning Analytics BI Dashboard — landing page.

Entry point for the Streamlit multi-page app. The pages/ directory contains
the individual dashboard sections, which Streamlit auto-discovers.
"""

from __future__ import annotations

import streamlit as st

from src.utils.db import warehouse_exists, warehouse_stats

st.set_page_config(
    page_title="EduPulse — Learning Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ EduPulse")
st.subheader("BI Dashboard for Online Learning Engagement Analytics")
st.caption(
    "End-to-end Business Intelligence platform — measures the pulse of student "
    "engagement, surfaces course outcomes, and predicts dropout risk."
)

if not warehouse_exists():
    st.warning(
        "**Warehouse not built yet.** The dashboard needs the OULAD dataset "
        "downloaded, cleaned, loaded into DuckDB, and the dropout model "
        "trained — about 3-5 minutes total on first run."
    )

    st.markdown("**Option A — locally:** open a terminal in the project root and run:")
    st.code("python -m src.etl.run_pipeline", language="bash")

    st.markdown("**Option B — right here (Streamlit Cloud or local):** click below.")
    if st.button("🚀 Build warehouse now", type="primary"):
        from src.etl import build_warehouse, clean, download_data
        from src.ml import train_dropout_model

        progress = st.progress(0.0)
        status = st.empty()
        for i, (label, fn) in enumerate(
            [
                ("Downloading OULAD dataset (~100 MB)", download_data.main),
                ("Cleaning & preprocessing", clean.main),
                ("Building DuckDB warehouse", build_warehouse.main),
                ("Training dropout-prediction model", train_dropout_model.main),
            ],
            start=1,
        ):
            status.info(f"Step {i}/4 — {label} …")
            fn()
            progress.progress(i / 4)
        status.success("Pipeline complete. Reloading dashboard …")
        st.rerun()
    st.stop()

stats = warehouse_stats()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Students", f"{stats['students']:,}")
c2.metric("Course presentations", f"{stats['course_presentations']:,}")
c3.metric("Enrollments", f"{stats['enrollments']:,}")
c4.metric("VLE clicks", f"{stats['total_clicks']:,}")
c5.metric("Assessments submitted", f"{stats['assessments_submitted']:,}")

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("What's in this dashboard")
    st.markdown(
        """
        - **📈 Overview** – platform-wide engagement and outcome KPIs
        - **📚 Course Analytics** – popularity, pass/withdrawal patterns by course
        - **🔍 Engagement Patterns** – when learners are most/least active
        - **🎯 Dropout Prediction** – ML model flagging at-risk students
        - **📝 Insights & Recommendations** – validated findings for administrators
        """
    )

    st.subheader("Project pipeline")
    st.markdown(
        """
        | Stage | Tool | Output |
        |---|---|---|
        | Collect | `requests` | `data/raw/*.csv` (OULAD dataset) |
        | Clean | `pandas` | `data/processed/*.parquet` |
        | Warehouse | `DuckDB` star-schema | `data/warehouse.duckdb` |
        | ETL | Python pipeline | facts + dims loaded |
        | ML | `scikit-learn` Gradient Boosting | `models/dropout_model.joblib` |
        | Dashboard | Streamlit + Plotly | this app |
        """
    )

with right:
    st.subheader("Data source")
    st.markdown(
        """
        **Open University Learning Analytics Dataset (OULAD)** — real anonymised
        data from 7 courses, 22 module presentations, **32,593 students**,
        10M+ click interactions.

        Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
        Source: [analyse.kmi.open.ac.uk/open_dataset](https://analyse.kmi.open.ac.uk/open_dataset)
        """
    )

    st.subheader("How to use")
    st.markdown(
        "Use the **sidebar** to navigate between pages. Most pages have "
        "filters (course, demographics) at the top that drive the charts below."
    )

st.divider()
st.caption(
    "**EduPulse** • Streamlit + DuckDB + scikit-learn • "
    "Open source, deployable for free on Streamlit Community Cloud."
)
