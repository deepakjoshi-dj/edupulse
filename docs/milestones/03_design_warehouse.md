# Milestone 3 — Design Data Warehouse

## Objective
Design a data warehouse optimised for learning-analytics queries.

## Why DuckDB
- File-based (no server to deploy / manage)
- Columnar OLAP engine — fast aggregations for BI workloads
- Reads parquet directly
- Free and embedded in the Streamlit app

## Star schema

```
                       ┌────────────────┐
                       │  dim_course    │
                       │  (module,      │
                       │   presentation)│
                       └────────────────┘
                              ▲
                              │
   ┌─────────────┐   ┌────────┴────────┐   ┌─────────────────┐
   │ dim_student │◀──┤ fact_enrollment │──▶│  dim_assessment │
   └─────────────┘   └─────────────────┘   └─────────────────┘
          ▲                  ▲                     ▲
          │                  │                     │
          │       ┌──────────┴───────┐             │
          └───────┤ fact_engagement  │             │
                  │ (daily clicks)   │             │
                  └──────────────────┘             │
                            ▲                      │
                            │                      │
                  ┌─────────┴────────┐             │
                  │   dim_activity   │   ┌─────────┴────────┐
                  └──────────────────┘   │ fact_assessment  │
                                          └──────────────────┘
```

### Facts
| Fact | Grain |
|---|---|
| `fact_engagement` | 1 row per (student, course, activity, day) — daily VLE clicks |
| `fact_assessment` | 1 row per assessment submission |
| `fact_enrollment` | 1 row per (student, course presentation) — outcome record |

### Dimensions
| Dim | Key attributes |
|---|---|
| `dim_student` | gender, region, IMD band, age band, education, disability, prior attempts, credits |
| `dim_course` | module, presentation, length (days) |
| `dim_activity` | activity_type, week range — what the VLE click was on |
| `dim_assessment` | type, weight, date due |

### Analytical views
| View | Purpose |
|---|---|
| `v_engagement_daily` | Time-series clicks & active students per day |
| `v_course_summary` | Enrollments / pass / withdrawal counts and rates per course |
| `v_student_features` | Per-student feature row consumed by ML model **and** dashboard drilldowns |

## Implementation
[`src/warehouse/schema.sql`](../../src/warehouse/schema.sql)
