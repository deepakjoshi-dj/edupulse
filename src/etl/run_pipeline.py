"""End-to-end ETL: download → clean → load warehouse → train model.

Usage:
    python -m src.etl.run_pipeline
"""

from __future__ import annotations

import sys

from src.etl import build_warehouse, clean, download_data
from src.ml import train_dropout_model


def main() -> int:
    print("=" * 70)
    print("STEP 1/4  Download raw OULAD data")
    print("=" * 70)
    download_data.main()

    print("\n" + "=" * 70)
    print("STEP 2/4  Clean & preprocess")
    print("=" * 70)
    clean.main()

    print("\n" + "=" * 70)
    print("STEP 3/4  Build DuckDB warehouse")
    print("=" * 70)
    build_warehouse.main()

    print("\n" + "=" * 70)
    print("STEP 4/4  Train dropout-prediction model")
    print("=" * 70)
    train_dropout_model.main()

    print("\nAll pipeline steps complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
