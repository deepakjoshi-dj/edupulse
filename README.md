# ⚡ EduPulse — Learning Analytics BI Dashboard

End-to-end Business Intelligence platform that measures the **pulse of student
engagement on online learning platforms** and helps administrators improve
content effectiveness and learner retention.

Built with **Streamlit + DuckDB + scikit-learn** on the real-world
[Open University Learning Analytics Dataset (OULAD)](https://analyse.kmi.open.ac.uk/open_dataset)
— 32,593 students, 22 course presentations, 10M+ click events.

---

## ✨ Features

| # | Feature | Where |
|---|---|---|
| 1 | Daily VLE click activity, outcome distribution, demographics | `pages/1_📈_Overview.py` |
| 2 | Course popularity, pass / withdrawal rates, outcome heatmaps | `pages/2_📚_Course_Analytics.py` |
| 3 | High & low engagement periods, content-type comparison | `pages/3_🔍_Engagement_Patterns.py` |
| 4 | ML dropout-risk scoring, top at-risk learners, CSV export | `pages/4_🎯_Dropout_Prediction.py` |
| 5 | Validated insights + recommendations for admins | `pages/5_📝_Insights.py` |

---

## 🏗️ Architecture

```
data/raw/*.csv          (OULAD download)
        │  src/etl/clean.py
        ▼
data/processed/*.parquet
        │  src/etl/build_warehouse.py  +  src/warehouse/schema.sql
        ▼
data/warehouse.duckdb   (star schema: dim_course / dim_student /
        │                dim_activity / dim_assessment + 3 facts + views)
        ├─► src/ml/train_dropout_model.py  →  models/dropout_model.joblib
        │
        ▼
Home.py + pages/*.py    (Streamlit dashboard)
```

**Star-schema dimensional model** (see [src/warehouse/schema.sql](src/warehouse/schema.sql)):

- **Facts:** `fact_engagement`, `fact_assessment`, `fact_enrollment`
- **Dimensions:** `dim_student`, `dim_course`, `dim_activity`, `dim_assessment`
- **Analytics views:** `v_engagement_daily`, `v_course_summary`, `v_student_features`

---

## 🚀 Quick start (local)

```bash
# 1. Clone / open the project, then create a venv
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full pipeline (download → clean → warehouse → train)
python -m src.etl.run_pipeline

# 4. Launch the dashboard
streamlit run Home.py
```

The first pipeline run takes ~3-5 minutes (OULAD download is ~100 MB).
Subsequent dashboard launches are instant — everything is cached.

---

## ☁️ Free deployment (Streamlit Community Cloud)

1. Push this project to a **public GitHub repo**.
2. Sign in at <https://share.streamlit.io/> with the GitHub account.
3. Click **New app** → pick the repo → set **Main file** to `Home.py`.
4. Click **Deploy**. The free tier gives you a public URL, always-on.

⚠️ The OULAD dataset (~100 MB) is too large to commit. On Streamlit Cloud
the pipeline downloads it on first boot — wait ~5 minutes after deploy
for the warehouse to build before the dashboard appears.

> Alternatives: Hugging Face Spaces (Streamlit SDK) and Render free web
> services also work — all use the same `requirements.txt`.

---

## 🎓 Milestone deliverables

This project maps directly to the 6 required milestones:

| Milestone | Artifact |
|---|---|
| Collect Data | [src/etl/download_data.py](src/etl/download_data.py) |
| Clean Data | [src/etl/clean.py](src/etl/clean.py) + `data/processed/*.parquet` |
| Design Data Warehouse | [src/warehouse/schema.sql](src/warehouse/schema.sql) |
| Implement ETL Workflows | [src/etl/build_warehouse.py](src/etl/build_warehouse.py) + [run_pipeline.py](src/etl/run_pipeline.py) |
| Develop Dashboards | [Home.py](Home.py) + [pages/](pages/) |
| Validate and Document | [pages/5_📝_Insights.py](pages/5_📝_Insights.py) + [docs/milestones/](docs/milestones/) |

Per-milestone write-ups (objectives, evidence, screenshots) live under
[docs/milestones/](docs/milestones/).

---

## 🤖 ML model — dropout prediction

- **Target:** student withdrew from the course (binary).
- **Features:** demographics (gender, region, IMD band, prior education, age,
  prior attempts, credits) + first-30-day engagement (clicks, active days,
  early assessment count and average score).
- **Algorithm:** scikit-learn `GradientBoostingClassifier` (200 trees, depth 3).
- **Eval:** stratified 80/20 split, ROC AUC + classification report.

Re-train with `python -m src.ml.train_dropout_model`.

---

## 📂 Project layout

```
Home.py                       # Streamlit entry
pages/                        # Multi-page dashboard
├── 1_📈_Overview.py
├── 2_📚_Course_Analytics.py
├── 3_🔍_Engagement_Patterns.py
├── 4_🎯_Dropout_Prediction.py
└── 5_📝_Insights.py
src/
├── etl/
│   ├── download_data.py      # downloads OULAD zip
│   ├── clean.py              # CSV → parquet, type/null fixes
│   ├── build_warehouse.py    # parquet → DuckDB star schema
│   └── run_pipeline.py       # one-shot orchestrator
├── warehouse/schema.sql      # dim/fact DDL + views
├── ml/train_dropout_model.py # GradientBoosting + joblib artifact
└── utils/                    # db helpers + chart builders
data/                         # raw + processed + warehouse (git-ignored)
models/                       # trained model artifact (git-ignored)
docs/milestones/              # milestone reports
requirements.txt
.streamlit/config.toml
```

---

## 📜 License

Code: MIT. Data: OULAD is © Open University, released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
