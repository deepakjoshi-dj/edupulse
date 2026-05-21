"""Build the DuckDB warehouse from cleaned parquet tables.

Reads cleaned parquet from data/processed/ and loads the star schema defined
in src/warehouse/schema.sql, then computes derived columns (e.g. is_withdrawn).
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
DB = ROOT / "data" / "warehouse.duckdb"
SCHEMA = ROOT / "src" / "warehouse" / "schema.sql"


def main() -> int:
    if not PROC.exists():
        raise SystemExit("data/processed/ missing — run src/etl/clean.py first.")
    if DB.exists():
        DB.unlink()
        wal = DB.with_suffix(DB.suffix + ".wal")
        if wal.exists():
            wal.unlink()

    con = duckdb.connect(str(DB))
    print(f"Connected to {DB}")

    print(f"Applying schema {SCHEMA.name} ...")
    con.execute(SCHEMA.read_text())

    # Dimensions — always list columns explicitly so the load is robust to
    # CSV column ordering differences between OULAD source files.
    print("Loading dim_course ...")
    con.execute(f"""
        INSERT INTO dim_course (code_module, code_presentation, module_presentation_length)
        SELECT code_module, code_presentation, module_presentation_length
        FROM read_parquet('{PROC / 'courses.parquet'}')
    """)

    print("Loading dim_student ...")
    con.execute(f"""
        INSERT INTO dim_student (
            id_student, code_module, code_presentation,
            gender, region, highest_education, imd_band, age_band, disability,
            num_of_prev_attempts, studied_credits
        )
        SELECT
            id_student, code_module, code_presentation,
            gender, region, highest_education, imd_band, age_band, disability,
            num_of_prev_attempts, studied_credits
        FROM read_parquet('{PROC / 'student_info.parquet'}')
    """)

    print("Loading dim_activity ...")
    con.execute(f"""
        INSERT INTO dim_activity (
            id_site, code_module, code_presentation,
            activity_type, week_from, week_to
        )
        SELECT id_site, code_module, code_presentation,
               activity_type, week_from, week_to
        FROM read_parquet('{PROC / 'vle.parquet'}')
    """)

    print("Loading dim_assessment ...")
    con.execute(f"""
        INSERT INTO dim_assessment (
            id_assessment, code_module, code_presentation,
            assessment_type, date, weight
        )
        SELECT id_assessment, code_module, code_presentation,
               assessment_type, date, weight
        FROM read_parquet('{PROC / 'assessments.parquet'}')
    """)

    # Facts
    print("Loading fact_engagement ...")
    con.execute(f"""
        INSERT INTO fact_engagement (
            id_student, code_module, code_presentation, id_site, date, sum_click
        )
        SELECT id_student, code_module, code_presentation, id_site, date, sum_click
        FROM read_parquet('{PROC / 'student_vle.parquet'}')
    """)

    print("Loading fact_assessment ...")
    con.execute(f"""
        INSERT INTO fact_assessment (
            id_student, id_assessment, code_module, code_presentation,
            date_submitted, is_banked, score
        )
        SELECT
            sa.id_student, sa.id_assessment,
            a.code_module, a.code_presentation,
            sa.date_submitted, sa.is_banked, sa.score
        FROM read_parquet('{PROC / 'student_assessment.parquet'}') sa
        JOIN read_parquet('{PROC / 'assessments.parquet'}') a USING (id_assessment)
    """)

    print("Loading fact_enrollment ...")
    con.execute(f"""
        INSERT INTO fact_enrollment (
            id_student, code_module, code_presentation,
            date_registration, date_unregistration,
            final_result, is_withdrawn, is_passed
        )
        SELECT
            si.id_student,
            si.code_module,
            si.code_presentation,
            sr.date_registration,
            sr.date_unregistration,
            si.final_result,
            si.final_result = 'Withdrawn' AS is_withdrawn,
            si.final_result IN ('Pass', 'Distinction') AS is_passed
        FROM read_parquet('{PROC / 'student_info.parquet'}') si
        LEFT JOIN read_parquet('{PROC / 'student_registration.parquet'}') sr
          USING (id_student, code_module, code_presentation)
    """)

    # Report row counts for validation
    print("\nWarehouse row counts:")
    for tbl in [
        "dim_course", "dim_student", "dim_activity", "dim_assessment",
        "fact_enrollment", "fact_assessment", "fact_engagement",
    ]:
        n = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl:20s} {n:>12,}")

    # Force checkpoint so the file is fully flushed
    con.execute("CHECKPOINT")
    con.close()
    print(f"\nWarehouse ready: {DB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
