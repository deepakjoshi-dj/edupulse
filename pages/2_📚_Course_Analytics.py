"""Course Analytics — popularity, pass rates, withdrawal patterns by course."""

from __future__ import annotations

import streamlit as st

from src.utils import charts
from src.utils.db import list_courses, query, warehouse_exists

st.set_page_config(page_title="Course Analytics", page_icon="📚", layout="wide")
st.title("📚 Course Analytics")
st.caption("Compare popularity, pass/withdrawal rates, and outcomes across courses.")

if not warehouse_exists():
    st.error("Warehouse not built. Run `python -m src.etl.run_pipeline` first.")
    st.stop()

courses_df = list_courses()
modules = ["All"] + sorted(courses_df["code_module"].unique().tolist())
chosen_module = st.sidebar.selectbox("Module", modules, index=0)

st.sidebar.markdown("---")
st.sidebar.caption(
    "**About module codes:** OULAD anonymises modules as letters (AAA, BBB, …) "
    "and presentations as year+season (e.g. 2014J = Oct 2014, 2014B = Feb 2014)."
)

module_filter_sql = ""
if chosen_module != "All":
    module_filter_sql = f"WHERE code_module = '{chosen_module}'"

# ------------------------------------------------- Popularity (enrollments)
st.subheader("Course popularity")
popularity = query(
    f"""
    SELECT
        code_module || ' / ' || code_presentation AS course,
        code_module, code_presentation, enrollments,
        pass_rate_pct, withdrawal_rate_pct
    FROM v_course_summary
    {module_filter_sql}
    ORDER BY enrollments DESC
    LIMIT 30
    """
)
st.plotly_chart(
    charts.bar(popularity, x="course", y="enrollments",
               title="Enrollments by course presentation"),
    use_container_width=True,
)

# ------------------------------------------------- Pass vs withdrawal
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(
        charts.bar(popularity.head(15), x="course", y="pass_rate_pct",
                   title="Pass rate (%) — top 15 by enrollment"),
        use_container_width=True,
    )
with c2:
    st.plotly_chart(
        charts.bar(popularity.head(15), x="course", y="withdrawal_rate_pct",
                   title="Withdrawal rate (%) — top 15 by enrollment"),
        use_container_width=True,
    )

# ------------------------------------------------- Outcome heatmap
st.subheader("Outcomes across course presentations")
heat = query(
    f"""
    SELECT
        code_module,
        code_presentation,
        ROUND(100.0 * SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_pct
    FROM fact_enrollment
    {module_filter_sql}
    GROUP BY code_module, code_presentation
    ORDER BY code_module, code_presentation
    """
)
if not heat.empty:
    st.plotly_chart(
        charts.heatmap(heat, x="code_presentation", y="code_module", z="pass_pct",
                       title="Pass rate (%) by module × presentation"),
        use_container_width=True,
    )

# ------------------------------------------------- Detailed table
st.subheader("Course summary table")
st.dataframe(
    popularity.rename(columns={
        "code_module": "Module",
        "code_presentation": "Presentation",
        "enrollments": "Enrollments",
        "pass_rate_pct": "Pass %",
        "withdrawal_rate_pct": "Withdrawal %",
    }).drop(columns=["course"]),
    use_container_width=True,
    hide_index=True,
)
