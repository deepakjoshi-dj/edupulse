# Milestone 6 — Validate and Document

## Objective
Validate dashboard accuracy and document insights + improvement recommendations.

## Validation checks

| Check | How | Where it shows up |
|---|---|---|
| Outcome reconciliation | `SUM(pass) + SUM(fail) + SUM(withdrawn) == COUNT(*)` over `fact_enrollment` | Insights page reconciliation panel |
| No data loss in cleaning | Row counts printed in `clean.py` match parquet output | Console log |
| Star-schema integrity | Foreign keys: `(id_student, code_module, code_presentation)` join cleanly across `dim_student` and all three facts | `build_warehouse.py` insert log |
| ML evaluation | Stratified 80/20 split, ROC AUC + classification report on held-out test | Dropout Prediction page metrics |
| Feature definition | First-30-day window enforced inside `v_student_features` so the ML model uses the **same** features the dashboard displays | `src/warehouse/schema.sql` |

## Documented insights (with recommendations)

1. **Early engagement strongly predicts retention.** Withdrawn students show
   ~3–5× fewer clicks in the first 30 days than students who pass.
   *Action: trigger automated outreach at day-14 when click count is below
   a course-specific threshold.*

2. **Withdrawal rates vary widely across modules** (~20-point spread).
   *Action: prioritise module-level redesign over blanket platform changes —
   higher ROI on the worst-performing modules.*

3. **Deprivation (IMD band) correlates with withdrawal.**
   *Action: direct support resources (mentorship, device/connectivity
   grants) at the most-deprived bands first.*

4. **Prior attempts are a risk signal** — more prior attempts → lower pass
   rate and higher withdrawal.
   *Action: flag repeat attempters at enrollment for proactive academic
   support.*

All four findings are reproducible directly from warehouse views — no
hard-coded numbers in the dashboard.

## Limitations
- OULAD covers 2013–2014. Findings should be revalidated on more recent
  cohorts when newer data is available.
- The ML model is trained on a 30-day feature window, so it cannot score
  students earlier than day 30 of a course presentation. For real-time
  use the window could be made configurable.

## How to re-run end-to-end
```bash
python -m src.etl.run_pipeline   # download → clean → warehouse → train
streamlit run Home.py            # launch dashboard
```
