# Milestone 4 — Implement ETL Workflows

## Objective
Implement the Extract / Transform / Load pipeline that takes raw OULAD CSVs
and produces a queryable warehouse + a trained model artifact.

## Pipeline stages

```
                 download_data.py      clean.py         build_warehouse.py   train_dropout_model.py
                 ┌───────────────┐   ┌──────────┐    ┌──────────────────┐  ┌────────────────────┐
   OULAD URL ──▶ │ raw/*.csv     │──▶│ parquet  │──▶ │ DuckDB warehouse │─▶│ dropout_model.joblib│
                 └───────────────┘   └──────────┘    └──────────────────┘  └────────────────────┘
```

## Orchestrator
[`src/etl/run_pipeline.py`](../../src/etl/run_pipeline.py) runs the four
stages end-to-end:

```bash
python -m src.etl.run_pipeline
```

Output (truncated):
```
STEP 1/4  Download raw OULAD data
STEP 2/4  Clean & preprocess
STEP 3/4  Build DuckDB warehouse
STEP 4/4  Train dropout-prediction model
```

## Design notes
- **Idempotency:** the downloader is a no-op if the files already exist.
  `build_warehouse.py` deletes any prior warehouse file before reloading,
  so the result is deterministic.
- **Caching:** Streamlit caches DuckDB connections (`@st.cache_resource`)
  and query results (`@st.cache_data` with TTL) so the dashboard stays snappy.
- **Read-only at runtime:** the dashboard opens the warehouse in `read_only=True`
  mode — query latency improves and there's no risk of dashboard sessions
  corrupting the file.
- **No row-by-row inserts:** parquet → DuckDB loads use `INSERT INTO … SELECT
  FROM read_parquet(…)`, the fastest path available.
