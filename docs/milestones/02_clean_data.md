# Milestone 2 — Clean Data

## Objective
Clean and preprocess engagement data — handle missing values, standardise
formats, coerce types, and persist a validated intermediate.

## Cleaning rules applied
| Table | Rule |
|---|---|
| `studentInfo` | Lower-case columns; coerce numerics; drop true duplicates on (id_student, module, presentation); fill missing `imd_band` with "Unknown"; cast categoricals. |
| `studentRegistration` | Coerce `date_registration` and `date_unregistration` to numeric. |
| `assessments` | Cast `weight` and `date` to numeric; cast `assessment_type` as categorical. |
| `studentAssessment` | Drop rows with missing score; clip to [0, 100]. |
| `vle` | Cast `activity_type` as categorical. |
| `studentVle` | Cast `sum_click`/`date` to int32; drop rows with `sum_click <= 0` (irrelevant noise). |
| `courses` | Cast `module_presentation_length` to int. |

## Output format
Each cleaned table is persisted as **parquet** under `data/processed/`. Parquet
gives us columnar storage, typed schema preservation, and significantly faster
loads than CSV.

## Implementation
[`src/etl/clean.py`](../../src/etl/clean.py).

```bash
python -m src.etl.clean
```

## Validation
The script prints row counts and shape per table after cleaning. The
dashboard's **Insights** page additionally reconciles outcome counts vs. total
enrollments to confirm no rows were dropped during the warehouse load.
