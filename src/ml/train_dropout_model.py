"""Train a dropout / at-risk prediction model.

Target: did the student withdraw from the course (binary classification).
Features: demographics + first-30-day engagement (clicks, active days, early scores).

Outputs models/dropout_model.joblib and prints validation metrics.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "warehouse.duckdb"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "dropout_model.joblib"

CATEGORICAL = [
    "gender", "region", "highest_education",
    "imd_band", "age_band", "disability",
]
NUMERIC = [
    "num_of_prev_attempts", "studied_credits",
    "total_clicks", "active_days",
    "avg_assessment_score", "assessments_submitted",
]
TARGET = "is_withdrawn"


def load_features() -> pd.DataFrame:
    if not DB.exists():
        raise SystemExit("Warehouse not built — run src/etl/build_warehouse.py first.")
    con = duckdb.connect(str(DB), read_only=True)
    # ORDER BY makes the row order deterministic across runs (DuckDB makes no
    # guarantees on view scan order otherwise). Without this, the train/test
    # split produced by random_state=42 can drift between training and any
    # later re-evaluation that re-reads the view.
    df = con.execute(
        "SELECT * FROM v_student_features "
        "ORDER BY id_student, code_module, code_presentation"
    ).df()
    con.close()
    return df


def build_pipeline() -> Pipeline:
    numeric_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocess = ColumnTransformer([
        ("num", numeric_pipe, NUMERIC),
        ("cat", categorical_pipe, CATEGORICAL),
    ])
    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.08,
        random_state=42,
    )
    return Pipeline([("prep", preprocess), ("clf", clf)])


def main() -> int:
    df = load_features()
    print(f"Loaded {len(df):,} student-course rows")

    y = df[TARGET].astype(int)
    X = df[NUMERIC + CATEGORICAL].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42,
    )
    print(f"Train: {len(X_train):,}  |  Test: {len(X_test):,}")
    print(f"Dropout rate (train): {y_train.mean():.3f}")

    pipe = build_pipeline()
    print("\nTraining GradientBoostingClassifier ...")
    pipe.fit(X_train, y_train)

    pred = pipe.predict(X_test)
    proba = pipe.predict_proba(X_test)[:, 1]

    print("\n========= Test set metrics =========")
    print(f"Accuracy : {accuracy_score(y_test, pred):.4f}")
    print(f"ROC AUC  : {roc_auc_score(y_test, proba):.4f}")
    print("\nClassification report:")
    print(classification_report(y_test, pred, target_names=["Retained", "Withdrawn"]))
    print("Confusion matrix [[TN FP][FN TP]]:")
    print(confusion_matrix(y_test, pred))

    # Persist
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "pipeline": pipe,
        "numeric_features": NUMERIC,
        "categorical_features": CATEGORICAL,
        "target": TARGET,
        "metrics": {
            "accuracy": float(accuracy_score(y_test, pred)),
            "roc_auc": float(roc_auc_score(y_test, proba)),
            "test_size": int(len(X_test)),
            "train_size": int(len(X_train)),
            "dropout_rate": float(y_train.mean()),
        },
        "feature_importance_top": _top_importances(pipe, NUMERIC, CATEGORICAL),
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"\nSaved model → {MODEL_PATH}")
    return 0


def _top_importances(pipe: Pipeline, numeric: list[str], categorical: list[str]) -> list[dict]:
    """Surface the top feature importances for the dashboard explainer."""
    try:
        ohe = pipe.named_steps["prep"].named_transformers_["cat"].named_steps["ohe"]
        cat_names = list(ohe.get_feature_names_out(categorical))
        feature_names = numeric + cat_names
        importances = pipe.named_steps["clf"].feature_importances_
        ranked = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        return [{"feature": name, "importance": float(score)} for name, score in ranked[:15]]
    except Exception:
        return []


if __name__ == "__main__":
    sys.exit(main())
