"""Clean and preprocess OULAD raw CSVs into validated parquet files.

Cleaning steps:
- Standardise column names to snake_case
- Coerce types (numerics, categoricals)
- Handle missing values explicitly
- Filter clearly invalid rows
- Normalise categorical values (e.g. IMD bands)
- Persist as parquet (faster, smaller, typed) for the load step
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"


def _read(name: str) -> pd.DataFrame:
    # OULAD uses "?" as the missing-value marker in several tables
    # (notably vle.week_from/week_to and studentRegistration.date_unregistration).
    df = pd.read_csv(RAW / name, na_values=["?"])
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def clean_courses() -> pd.DataFrame:
    df = _read("courses.csv")
    df["module_presentation_length"] = df["module_presentation_length"].astype("int32")
    return df


def clean_student_info() -> pd.DataFrame:
    df = _read("studentInfo.csv")
    df["num_of_prev_attempts"] = df["num_of_prev_attempts"].fillna(0).astype("int16")
    df["studied_credits"] = df["studied_credits"].astype("int16")
    df["imd_band"] = df["imd_band"].fillna("Unknown").str.replace("-", "–").str.strip()
    df["age_band"] = df["age_band"].astype("category")
    df["gender"] = df["gender"].astype("category")
    df["region"] = df["region"].astype("category")
    df["highest_education"] = df["highest_education"].astype("category")
    df["disability"] = df["disability"].astype("category")
    df["final_result"] = df["final_result"].astype("category")
    # Drop true duplicates if any
    df = df.drop_duplicates(subset=["id_student", "code_module", "code_presentation"])
    return df


def clean_registration() -> pd.DataFrame:
    df = _read("studentRegistration.csv")
    df["date_registration"] = pd.to_numeric(df["date_registration"], errors="coerce")
    df["date_unregistration"] = pd.to_numeric(df["date_unregistration"], errors="coerce")
    return df


def clean_assessments() -> pd.DataFrame:
    df = _read("assessments.csv")
    df["weight"] = df["weight"].astype("float32")
    df["date"] = pd.to_numeric(df["date"], errors="coerce")
    df["assessment_type"] = df["assessment_type"].astype("category")
    return df


def clean_student_assessment() -> pd.DataFrame:
    df = _read("studentAssessment.csv")
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["is_banked"] = df["is_banked"].astype("int8")
    df = df.dropna(subset=["score"])
    df = df[(df["score"] >= 0) & (df["score"] <= 100)]
    return df


def clean_vle() -> pd.DataFrame:
    df = _read("vle.csv")
    df["activity_type"] = df["activity_type"].astype("category")
    # week_from / week_to are missing for most activities — use pandas
    # nullable Int so DuckDB receives NULL instead of NaN-cast-to-string.
    df["week_from"] = pd.to_numeric(df["week_from"], errors="coerce").astype("Int32")
    df["week_to"] = pd.to_numeric(df["week_to"], errors="coerce").astype("Int32")
    return df


def clean_student_vle() -> pd.DataFrame:
    df = _read("studentVle.csv")
    df["sum_click"] = df["sum_click"].astype("int32")
    df["date"] = df["date"].astype("int32")
    df = df[df["sum_click"] > 0]
    return df


CLEANERS = {
    "courses": clean_courses,
    "student_info": clean_student_info,
    "student_registration": clean_registration,
    "assessments": clean_assessments,
    "student_assessment": clean_student_assessment,
    "vle": clean_vle,
    "student_vle": clean_student_vle,
}


def main() -> int:
    PROC.mkdir(parents=True, exist_ok=True)
    for name, fn in CLEANERS.items():
        print(f"Cleaning {name} ...", flush=True)
        df = fn()
        out = PROC / f"{name}.parquet"
        df.to_parquet(out, index=False)
        print(f"  → {out.name}  rows={len(df):,}  cols={df.shape[1]}")
    print("Done. Cleaned tables saved to", PROC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
