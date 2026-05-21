# Milestone 5 — Develop Dashboards

## Objective
Build interactive dashboards that visualise engagement trends, course
popularity, dropout patterns, high/low engagement periods, and category
comparisons.

## Pages

| Page | Charts | Tasks it answers |
|---|---|---|
| **📈 Overview** | KPI strip, outcome pie, outcomes by gender, daily clicks line, age + education bars | "Develop dashboards showing user engagement trends" |
| **📚 Course Analytics** | Enrollment bar (top 30), pass/withdrawal rate bars, pass-rate heatmap, summary table | "Analyze course popularity and dropout patterns"; "Compare engagement across course categories" |
| **🔍 Engagement Patterns** | Click & active-student timelines, peak/trough tables, activity-type bars, engagement-by-outcome | "Identify high and low engagement periods" |
| **🎯 Dropout Prediction** | Model metric cards, feature-importance bar, live cohort scorer, top-20 risk leaderboard, CSV export | ML insight layer + interactive reporting |
| **📝 Insights** | 4 validated findings with recommendations, reconciliation panel | "Document insights and improvement recommendations"; "Validate dashboard accuracy" |

## Interactivity
- **Sidebar filters** on every page (module, time window) drive the SQL queries
  underneath. All filters apply server-side via DuckDB, so even with 10M+
  click events the responses stay sub-second.
- **CSV export** of at-risk students on the Dropout Prediction page lets
  admins act on the model output outside the dashboard.

## Implementation
- [`Home.py`](../../Home.py) — landing page
- [`pages/`](../../pages/) — one file per page (Streamlit native multi-page
  pattern; auto-discovered)
- [`src/utils/charts.py`](../../src/utils/charts.py) — shared Plotly builders
  for visual consistency
- [`src/utils/db.py`](../../src/utils/db.py) — cached DuckDB connection +
  query helpers
