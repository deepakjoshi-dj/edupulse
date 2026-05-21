"""Shared DuckDB connection helpers + cached queries for the dashboard."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "warehouse.duckdb"


def warehouse_exists() -> bool:
    return DB_PATH.exists()


@st.cache_resource(show_spinner=False)
def get_connection() -> duckdb.DuckDBPyConnection:
    if not warehouse_exists():
        raise FileNotFoundError(
            f"Warehouse not found at {DB_PATH}. "
            "Run `python -m src.etl.run_pipeline` first."
        )
    return duckdb.connect(str(DB_PATH), read_only=True)


@st.cache_data(ttl=3600, show_spinner=False)
def query(sql: str, params: tuple | None = None) -> pd.DataFrame:
    con = get_connection()
    if params:
        return con.execute(sql, params).df()
    return con.execute(sql).df()


@st.cache_data(ttl=3600, show_spinner=False)
def list_courses() -> pd.DataFrame:
    return query(
        """
        SELECT code_module, code_presentation, module_presentation_length
        FROM dim_course
        ORDER BY code_module, code_presentation
        """
    )


@st.cache_data(ttl=3600, show_spinner=False)
def warehouse_stats() -> dict:
    con = get_connection()
    rows = con.execute(
        """
        SELECT
            (SELECT COUNT(DISTINCT id_student) FROM dim_student)  AS students,
            (SELECT COUNT(*) FROM dim_course)                     AS course_presentations,
            (SELECT COUNT(*) FROM fact_enrollment)                AS enrollments,
            (SELECT SUM(sum_click)::BIGINT FROM fact_engagement)  AS total_clicks,
            (SELECT COUNT(*) FROM fact_assessment)                AS assessments_submitted
        """
    ).fetchone()
    return {
        "students": rows[0],
        "course_presentations": rows[1],
        "enrollments": rows[2],
        "total_clicks": rows[3],
        "assessments_submitted": rows[4],
    }
