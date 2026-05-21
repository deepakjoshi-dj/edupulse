"""Download the Open University Learning Analytics Dataset (OULAD).

Sources (tried in order):
  1. UCI Machine Learning Repository mirror (stable, https)
  2. Open University KMI portal (original)

The dataset is anonymised and released under CC BY 4.0.
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

import requests

OULAD_URLS = [
    "https://archive.ics.uci.edu/static/public/349/open+university+learning+analytics+dataset.zip",
    "https://analyse.kmi.open.ac.uk/open-dataset/download",
]

EXPECTED_FILES = {
    "studentInfo.csv",
    "studentRegistration.csv",
    "studentAssessment.csv",
    "studentVle.csv",
    "vle.csv",
    "assessments.csv",
    "courses.csv",
}

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
ZIP_PATH = RAW_DIR / "anonymisedData.zip"


def already_downloaded() -> bool:
    return all((RAW_DIR / name).exists() for name in EXPECTED_FILES)


def _try_download(url: str) -> bool:
    print(f"Trying {url} ...")
    try:
        with requests.get(url, stream=True, timeout=180,
                          headers={"User-Agent": "oulad-bi-dashboard/1.0"}) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with ZIP_PATH.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 16):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded * 100 / total
                        print(f"  {downloaded / 1e6:6.1f} / {total / 1e6:6.1f} MB "
                              f"({pct:5.1f}%)", end="\r")
            print()
        return True
    except requests.HTTPError as e:
        print(f"  failed: {e}")
        return False
    except requests.RequestException as e:
        print(f"  network error: {e}")
        return False


def download_zip() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for url in OULAD_URLS:
        if _try_download(url):
            print(f"Saved zip to {ZIP_PATH}")
            return
    raise RuntimeError(
        "Could not download OULAD from any known source. "
        "Check your internet connection or manually place the dataset CSVs "
        f"into {RAW_DIR}/ (see EXPECTED_FILES)."
    )


def extract_zip() -> None:
    print(f"Extracting {ZIP_PATH} ...")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extractall(RAW_DIR)

    # Some mirrors wrap the CSVs in a nested folder. Flatten if needed.
    for name in EXPECTED_FILES:
        target = RAW_DIR / name
        if target.exists():
            continue
        found = next(RAW_DIR.rglob(name), None)
        if found and found != target:
            print(f"  flattening {found.relative_to(RAW_DIR)} → {name}")
            shutil.move(str(found), str(target))

    # Clean up any now-empty subdirectories
    for sub in [p for p in RAW_DIR.iterdir() if p.is_dir()]:
        try:
            sub.rmdir()
        except OSError:
            pass

    print(f"Extracted to {RAW_DIR}")


def verify() -> None:
    missing = [name for name in EXPECTED_FILES if not (RAW_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"Missing expected files after extract: {missing}")
    print("All expected OULAD files present:")
    for name in sorted(EXPECTED_FILES):
        size_mb = (RAW_DIR / name).stat().st_size / 1e6
        print(f"  {name:30s} {size_mb:8.2f} MB")


def main() -> int:
    if already_downloaded():
        print("OULAD already present in data/raw/. Skipping download.")
        return 0
    download_zip()
    extract_zip()
    verify()
    return 0


if __name__ == "__main__":
    sys.exit(main())
