"""Overview page — platform-wide engagement and outcome KPIs."""

from __future__ import annotations

import streamlit as st

from src.utils import charts
from src.utils.db import query, warehouse_exists

st.set_page_config(page_title="Overview", page_icon="📈", layout="wide")

st.title("📈 Platform Overview")
st.caption("Aggregate engagement and outcome KPIs across all courses.")

if not warehouse_exists():
    st.error("Warehouse not built. Run `python -m src.etl.run_pipeline` first.")
    st.stop()

# ----------------------------------------------------------------------- KPIs
kpis = query(
    """
    SELECT
        COUNT(DISTINCT id_student)                                   AS students,
        SUM(CASE WHEN is_passed     THEN 1 ELSE 0 END)               AS passed,
        SUM(CASE WHEN is_withdrawn  THEN 1 ELSE 0 END)               AS withdrawn,
        SUM(CASE WHEN final_result = 'Distinction' THEN 1 ELSE 0 END) AS distinction,
        SUM(CASE WHEN final_result = 'Fail'        THEN 1 ELSE 0 END) AS failed,
        COUNT(*)                                                     AS enrollments
    FROM fact_enrollment
    """
).iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Unique students", f"{int(kpis['students']):,}")
c2.metric("Enrollments", f"{int(kpis['enrollments']):,}")
c3.metric("Pass rate", f"{kpis['passed'] / kpis['enrollments']:.1%}")
c4.metric("Withdrawal rate", f"{kpis['withdrawn'] / kpis['enrollments']:.1%}",
          delta=None, delta_color="inverse")
c5.metric("Distinctions", f"{int(kpis['distinction']):,}")

st.divider()

# ------------------------------------------------------------ Outcome split
col1, col2 = st.columns(2)

with col1:
    outcome = query(
        """
        SELECT final_result, COUNT(*) AS enrollments
        FROM fact_enrollment
        GROUP BY final_result
        ORDER BY enrollments DESC
        """
    )
    st.plotly_chart(
        charts.pie(outcome, names="final_result", values="enrollments",
                   title="Outcome distribution"),
        use_container_width=True,
    )

with col2:
    by_gender = query(
        """
        SELECT s.gender, e.final_result, COUNT(*) AS enrollments
        FROM fact_enrollment e
        JOIN dim_student s
          USING (id_student, code_module, code_presentation)
        GROUP BY s.gender, e.final_result
        ORDER BY s.gender, e.final_result
        """
    )
    st.plotly_chart(
        charts.grouped_bar(by_gender, x="gender", y="enrollments", color="final_result",
                           title="Outcomes by gender"),
        use_container_width=True,
    )

# ------------------------------------------------------------ Clicks over time
st.subheader("Daily VLE click activity")
clicks = query(
    """
    SELECT date, SUM(sum_click)::BIGINT AS total_clicks
    FROM fact_engagement
    WHERE date BETWEEN -30 AND 270
    GROUP BY date
    ORDER BY date
    """
)
st.plotly_chart(
    charts.line(clicks, x="date", y="total_clicks",
                title="Total VLE clicks by day from course start"),
    use_container_width=True,
)
st.caption(
    "Day 0 = course start. Negative days = pre-course onboarding activity. "
    "Look for sustained engagement plateaus and end-of-term spikes."
)

# ------------------------------------------------------------ Demographics
st.subheader("Learner demographics")
d1, d2 = st.columns(2)
with d1:
    age = query(
        """
        SELECT age_band, COUNT(*) AS students
        FROM (SELECT DISTINCT id_student, age_band FROM dim_student)
        GROUP BY age_band
        ORDER BY age_band
        """
    )
    st.plotly_chart(charts.bar(age, x="age_band", y="students", title="Age bands"),
                    use_container_width=True)
with d2:
    edu = query(
        """
        SELECT highest_education, COUNT(*) AS students
        FROM (SELECT DISTINCT id_student, highest_education FROM dim_student)
        GROUP BY highest_education
        ORDER BY students DESC
        """
    )
    st.plotly_chart(charts.bar(edu, x="highest_education", y="students",
                               title="Prior education"),
                    use_container_width=True)
