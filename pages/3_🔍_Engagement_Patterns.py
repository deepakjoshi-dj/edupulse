"""Engagement Patterns — high/low engagement periods, category comparison."""

from __future__ import annotations

import streamlit as st

from src.utils import charts
from src.utils.db import list_courses, query, warehouse_exists

st.set_page_config(page_title="Engagement Patterns", page_icon="🔍", layout="wide")
st.title("🔍 Engagement Patterns")
st.caption("When are learners most and least active? How does activity vary by content type?")

if not warehouse_exists():
    st.error("Warehouse not built. Run `python -m src.etl.run_pipeline` first.")
    st.stop()

# ------------------------------------------------- Filters
courses_df = list_courses()
modules = ["All"] + sorted(courses_df["code_module"].unique().tolist())
chosen_module = st.sidebar.selectbox("Module", modules, index=0)
week_window = st.sidebar.slider("Time window (days from course start)",
                                min_value=-30, max_value=270, value=(0, 200))

module_filter = "" if chosen_module == "All" else f"AND code_module = '{chosen_module}'"

# ------------------------------------------------- Engagement timeline (peak/trough)
st.subheader("Engagement timeline — peaks and troughs")
timeline = query(
    f"""
    SELECT
        date,
        SUM(sum_click)::BIGINT      AS total_clicks,
        COUNT(DISTINCT id_student)  AS active_students
    FROM fact_engagement
    WHERE date BETWEEN {week_window[0]} AND {week_window[1]}
    {module_filter}
    GROUP BY date
    ORDER BY date
    """
)

if not timeline.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            charts.line(timeline, x="date", y="total_clicks",
                        title="Total clicks per day"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            charts.line(timeline, x="date", y="active_students",
                        title="Active distinct students per day"),
            use_container_width=True,
        )

    peak = timeline.nlargest(5, "total_clicks")[["date", "total_clicks", "active_students"]]
    trough = timeline.nsmallest(5, "total_clicks")[["date", "total_clicks", "active_students"]]
    p_col, t_col = st.columns(2)
    with p_col:
        st.markdown("**Top 5 highest-engagement days**")
        st.dataframe(peak, hide_index=True, use_container_width=True)
    with t_col:
        st.markdown("**Top 5 lowest-engagement days** (within window)")
        st.dataframe(trough, hide_index=True, use_container_width=True)

# ------------------------------------------------- Activity-type comparison
st.subheader("Engagement by content type")
activity_mix = query(
    f"""
    SELECT
        a.activity_type,
        SUM(fe.sum_click)::BIGINT      AS clicks,
        COUNT(DISTINCT fe.id_student)  AS distinct_students
    FROM fact_engagement fe
    JOIN dim_activity a USING (id_site)
    WHERE fe.date BETWEEN {week_window[0]} AND {week_window[1]}
    {module_filter}
    GROUP BY a.activity_type
    ORDER BY clicks DESC
    """
)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(
        charts.bar(activity_mix, x="activity_type", y="clicks",
                   title="Total clicks by content type"),
        use_container_width=True,
    )
with c2:
    st.plotly_chart(
        charts.bar(activity_mix, x="activity_type", y="distinct_students",
                   title="Distinct students reached by content type"),
        use_container_width=True,
    )

# ------------------------------------------------- Engagement vs outcome
st.subheader("Engagement vs. course outcome")
engagement_by_result = query(
    f"""
    SELECT
        e.final_result,
        AVG(per_student.total_clicks)  AS avg_total_clicks,
        AVG(per_student.active_days)   AS avg_active_days
    FROM fact_enrollment e
    JOIN (
        SELECT id_student, code_module, code_presentation,
               SUM(sum_click) AS total_clicks,
               COUNT(DISTINCT date) AS active_days
        FROM fact_engagement
        WHERE date BETWEEN {week_window[0]} AND {week_window[1]}
        {module_filter}
        GROUP BY id_student, code_module, code_presentation
    ) per_student
      USING (id_student, code_module, code_presentation)
    GROUP BY e.final_result
    ORDER BY avg_total_clicks DESC
    """
)
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(
        charts.bar(engagement_by_result, x="final_result", y="avg_total_clicks",
                   title="Avg total clicks (per student) by outcome"),
        use_container_width=True,
    )
with c2:
    st.plotly_chart(
        charts.bar(engagement_by_result, x="final_result", y="avg_active_days",
                   title="Avg active days per student by outcome"),
        use_container_width=True,
    )

st.info(
    "**Interpretation:** Students who eventually pass or earn distinction typically "
    "show higher and more consistent click activity in the first weeks. Use this on "
    "the Dropout Prediction page to flag at-risk learners early."
)
