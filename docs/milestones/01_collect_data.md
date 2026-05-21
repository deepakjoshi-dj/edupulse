# Milestone 1 — Collect Data

## Objective
Collect platform-usage datasets describing login frequency, course completion,
and engagement on an online learning platform.

## What we did
Selected the **Open University Learning Analytics Dataset (OULAD)** —
real anonymised data from the Open University's virtual learning environment.

| Property | Value |
|---|---|
| Source | <https://analyse.kmi.open.ac.uk/open_dataset> |
| License | CC BY 4.0 |
| Students | 32,593 |
| Courses (modules) | 7 |
| Presentations | 22 |
| Click interactions | ~10 million |
| Time span | 2013–2014 |

## Files collected
| File | Description |
|---|---|
| `studentInfo.csv` | Demographics + final result (Pass / Fail / Withdrawn / Distinction) |
| `studentRegistration.csv` | Registration & unregistration dates |
| `studentAssessment.csv` | Assessment scores per student |
| `studentVle.csv` | Daily VLE click activity per student (~10M rows) |
| `vle.csv` | VLE activity metadata (type, week range) |
| `assessments.csv` | Assessment metadata (type, weight, date) |
| `courses.csv` | Module/presentation length |

## Implementation
[`src/etl/download_data.py`](../../src/etl/download_data.py) — downloads the
zipped dataset, verifies file completeness, extracts into `data/raw/`.

```bash
python -m src.etl.download_data
```

## Reproducibility
The downloader is idempotent — re-running detects the already-downloaded files
and skips. The dataset URL and licence are documented inside the script.
