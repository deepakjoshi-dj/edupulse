"""Generate diagram PNGs for the report (Chapters 3 and 4).

Saves images under assets/figures/. Each figure function is independent and
can be regenerated without affecting others.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "assets" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------- style

BLUE = "#4F8BF9"
LIGHT_BLUE = "#DCE7FA"
GREY = "#E5E7EB"
DARK = "#1F2937"
WARM = "#FBE7B0"
GREEN = "#C6E5CF"


def _save(fig, name: str) -> Path:
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {path.relative_to(path.parents[2])}")
    return path


def _box(ax, xy, w, h, label, color=LIGHT_BLUE, edge=DARK, fontsize=10, bold=False):
    box = FancyBboxPatch(
        xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=1.3, edgecolor=edge, facecolor=color,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + w / 2, xy[1] + h / 2, label,
        ha="center", va="center", fontsize=fontsize,
        fontweight="bold" if bold else "normal", color=DARK,
    )


def _arrow(ax, start, end, style="->", color=DARK, lw=1.3, curve=0.0,
           linestyle="-"):
    arrow = FancyArrowPatch(
        start, end, arrowstyle=style,
        mutation_scale=14, linewidth=lw, color=color,
        connectionstyle=f"arc3,rad={curve}",
        linestyle=linestyle,
    )
    ax.add_patch(arrow)


# ============================ Figure 3.1: System Architecture =====================

def figure_3_1_architecture() -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis("off")

    # Title bar
    ax.text(6, 7.6, "EduPulse — High-Level System Architecture",
            ha="center", fontsize=14, fontweight="bold", color=DARK)

    # Layer 1 — Data Source
    ax.text(0.3, 6.8, "1.  Data Source Layer", fontsize=11, fontweight="bold", color=BLUE)
    _box(ax, (0.5, 5.4), 11, 1.1,
         "Open University Learning Analytics Dataset (OULAD)  •  CC BY 4.0  •  32,593 students  •  7 modules  •  10M+ click events",
         color=WARM, fontsize=10)

    # Layer 2 — ETL
    ax.text(0.3, 4.9, "2.  ETL Pipeline (Python)", fontsize=11, fontweight="bold", color=BLUE)
    _box(ax, (0.5, 3.8), 2.5, 0.9, "Downloader\n(requests + zipfile)", color=LIGHT_BLUE)
    _box(ax, (3.3, 3.8), 2.5, 0.9, "Cleaner\n(pandas)", color=LIGHT_BLUE)
    _box(ax, (6.1, 3.8), 2.5, 0.9, "Loader\n(DuckDB COPY)", color=LIGHT_BLUE)
    _box(ax, (8.9, 3.8), 2.6, 0.9, "Trainer\n(scikit-learn)", color=LIGHT_BLUE)
    _arrow(ax, (3.0, 4.25), (3.3, 4.25))
    _arrow(ax, (5.8, 4.25), (6.1, 4.25))
    _arrow(ax, (8.6, 4.25), (8.9, 4.25))

    # Layer 3 — Warehouse + Model
    ax.text(0.3, 3.3, "3.  Storage Layer", fontsize=11, fontweight="bold", color=BLUE)
    _box(ax, (0.5, 2.0), 7.4, 1.1,
         "DuckDB Warehouse  (star schema)\nfact_engagement  •  fact_assessment  •  fact_enrollment\n+ dim_student / dim_course / dim_activity / dim_assessment",
         color=GREEN, fontsize=9)
    _box(ax, (8.2, 2.0), 3.3, 1.1, "Trained Model\ndropout_model.joblib", color=GREEN, fontsize=10)

    # Layer 4 — Presentation
    ax.text(0.3, 1.5, "4.  Presentation Layer", fontsize=11, fontweight="bold", color=BLUE)
    _box(ax, (0.5, 0.3), 11, 0.9,
         "Streamlit Multi-page Dashboard  —  Home  •  Overview  •  Course Analytics  •  Engagement Patterns  •  Dropout Prediction  •  Insights",
         color=LIGHT_BLUE, fontsize=10)

    # Connectors between layers
    _arrow(ax, (6, 5.4), (6, 4.7))    # Source → ETL
    _arrow(ax, (4.0, 3.8), (4.0, 3.1))  # ETL → Warehouse
    _arrow(ax, (10.2, 3.8), (9.85, 3.1))  # ETL Trainer → Model
    _arrow(ax, (4.0, 2.0), (4.0, 1.2))   # Warehouse → Dashboard
    _arrow(ax, (9.85, 2.0), (8, 1.2))    # Model → Dashboard

    _save(fig, "figure_3_1_architecture.png")


# ============================ Figure 3.2: DFD Level 0 =====================

def figure_3_2_dfd_level_0() -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis("off")
    ax.text(6, 5.5, "Figure 3.2 — DFD Level 0  (Context Diagram)",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    # External entities (rectangles) — moved further apart so labels don't collide
    _box(ax, (0.3, 2.4), 2.0, 1.2, "OULAD\nData Source",
         color=WARM, fontsize=11, bold=True)
    _box(ax, (9.7, 2.4), 2.0, 1.2, "Course\nAdministrator",
         color=WARM, fontsize=11, bold=True)

    # Central process — number-prefixed label on one line, body below
    proc = FancyBboxPatch(
        (4.4, 2.1), 3.2, 1.8, boxstyle="round,pad=0.05,rounding_size=0.4",
        linewidth=1.5, edgecolor=DARK, facecolor=LIGHT_BLUE,
    )
    ax.add_patch(proc)
    ax.text(6.0, 3.4, "0",
            ha="center", fontsize=12, fontweight="bold", color=DARK)
    ax.text(6.0, 2.7, "EduPulse\nBI Platform",
            ha="center", fontsize=12, fontweight="bold", color=DARK)

    # Inbound flow from OULAD
    _arrow(ax, (2.3, 3.0), (4.4, 3.0))
    ax.text(3.35, 3.15, "Raw OULAD CSVs", ha="center", fontsize=10, color=DARK)

    # Outbound flows to Admin — pulled clear of the box edges
    _arrow(ax, (7.6, 3.5), (9.7, 3.5))
    ax.text(8.65, 3.65, "KPIs  •  Charts", ha="center", fontsize=10, color=DARK)

    _arrow(ax, (7.6, 2.7), (9.7, 2.7))
    ax.text(8.65, 2.85, "Risk-scored cohort CSV",
            ha="center", fontsize=10, color=DARK)

    # Inbound flow from Admin (curve down)
    _arrow(ax, (9.7, 2.0), (7.6, 2.4), curve=0.15)
    ax.text(8.65, 1.85, "Module / threshold filters",
            ha="center", fontsize=10, color=DARK)

    _save(fig, "figure_3_2_dfd_level_0.png")


# ============================ Figure 3.3: DFD Level 1 =====================

def figure_3_3_dfd_level_1() -> None:
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9); ax.axis("off")
    ax.text(7, 8.6, "Figure 3.3 — DFD Level 1  (Decomposed View)",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    # External entity — OULAD (top-left)
    _box(ax, (0.3, 6.7), 1.7, 0.9, "OULAD", color=WARM, fontsize=11, bold=True)

    # Row 1: ETL processes — labels split into two lines, well-spaced
    proc_y = 6.5; proc_h = 1.2
    proc_positions = [
        (2.6, "1.0  Extract"),
        (5.4, "2.0  Clean &\n        Transform"),
        (8.2, "3.0  Load to\n        Warehouse"),
        (11.0, "4.0  Train ML\n        Model"),
    ]
    for x, label in proc_positions:
        _box(ax, (x, proc_y), 2.4, proc_h, label,
             color=LIGHT_BLUE, fontsize=10)

    # Horizontal flow chain
    _arrow(ax, (2.0, 7.1), (2.6, 7.1))
    _arrow(ax, (5.0, 7.1), (5.4, 7.1))
    _arrow(ax, (7.8, 7.1), (8.2, 7.1))
    _arrow(ax, (10.6, 7.1), (11.0, 7.1))

    # Row 2: Data stores — open-ended rectangles (DFD convention)
    store_y = 4.6; store_h = 0.7
    stores = [
        (2.6, 2.4, "D1:  data/raw  (CSVs)"),
        (5.4, 2.4, "D2:  data/processed  (parquet)"),
        (8.2, 2.4, "D3:  warehouse.duckdb"),
        (11.0, 2.4, "D4:  dropout_model.joblib"),
    ]
    for x, w, lbl in stores:
        # open-ended store: top + bottom lines only, with left-edge mini-tab
        ax.plot([x, x + w], [store_y + store_h, store_y + store_h], color=DARK, lw=1.3)
        ax.plot([x, x + w], [store_y, store_y], color=DARK, lw=1.3)
        ax.plot([x, x], [store_y, store_y + store_h], color=DARK, lw=1.3)
        ax.text(x + w / 2, store_y + store_h / 2, lbl,
                ha="center", va="center", fontsize=10, color=DARK)

    # Process → Store (vertical)
    for x in [3.8, 6.6, 9.4, 12.2]:
        _arrow(ax, (x, 6.5), (x, 5.3))

    # Row 3: Dashboard + Score processes
    dash_y = 2.7; dash_h = 1.2
    _box(ax, (4.8, dash_y), 2.6, dash_h, "5.0  Serve\n        Dashboard",
         color=LIGHT_BLUE, fontsize=10)
    _box(ax, (8.4, dash_y), 2.6, dash_h, "6.0  Score\n        Cohort",
         color=LIGHT_BLUE, fontsize=10)

    # Stores → Dashboard / Score (vertical)
    _arrow(ax, (6.6, 4.6), (6.1, 3.9))         # D2 → 5.0
    _arrow(ax, (9.4, 4.6), (9.4, 3.9))         # D3 → 6.0
    _arrow(ax, (12.2, 4.6), (10.4, 3.9))       # D4 → 6.0  (curving)

    # External entity — Administrator (bottom-left)
    _box(ax, (0.3, 1.1), 2.0, 0.9, "Course\nAdministrator",
         color=WARM, fontsize=10, bold=True)

    # Admin ↔ Dashboard
    _arrow(ax, (2.3, 1.9), (4.8, 2.95))
    ax.text(3.0, 2.55, "filters / clicks", fontsize=9, color=DARK)
    _arrow(ax, (4.8, 3.25), (2.3, 1.7), curve=-0.15)
    ax.text(3.0, 2.05, "KPIs / charts", fontsize=9, color=DARK)

    # 5.0 → 6.0 (request scoring)
    _arrow(ax, (7.4, 3.3), (8.4, 3.3))
    ax.text(7.9, 3.45, "scoring request", fontsize=9, color=DARK)

    # 6.0 → Admin (risk CSV)
    _arrow(ax, (8.4, 2.95), (2.3, 1.5), curve=-0.20)
    ax.text(5.3, 1.6, "risk-scored CSV", fontsize=9, color=DARK)

    _save(fig, "figure_3_3_dfd_level_1.png")


# ============================ Figure 3.4: Use Case Diagram =====================

def figure_3_4_use_case() -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 11); ax.set_ylim(0, 7); ax.axis("off")
    ax.text(5.5, 6.6, "Figure 3.4 — Use Case Diagram",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    # System boundary
    ax.add_patch(mpatches.Rectangle((2.8, 0.6), 6.0, 5.4,
                                       linewidth=1.3, edgecolor=DARK,
                                       facecolor="#FAFBFD"))
    ax.text(5.8, 6.05, "EduPulse System", fontsize=11, fontweight="bold",
            color=DARK, ha="center")

    # Stick-figure actors
    def stickman(x, y, label):
        # head
        ax.add_patch(plt.Circle((x, y + 0.55), 0.15, edgecolor=DARK, facecolor="white", linewidth=1.3))
        # body & arms & legs
        ax.plot([x, x], [y + 0.40, y - 0.10], color=DARK, lw=1.3)
        ax.plot([x - 0.30, x + 0.30], [y + 0.20, y + 0.20], color=DARK, lw=1.3)
        ax.plot([x, x - 0.20], [y - 0.10, y - 0.45], color=DARK, lw=1.3)
        ax.plot([x, x + 0.20], [y - 0.10, y - 0.45], color=DARK, lw=1.3)
        ax.text(x, y - 0.65, label, ha="center", fontsize=10, fontweight="bold", color=DARK)

    stickman(1.4, 4.5, "Course\nAdministrator")
    stickman(9.7, 4.5, "ETL\nPipeline\n<<system>>")

    # Use cases (ellipses)
    cases = [
        (4.5, 5.3, "View Overview KPIs"),
        (4.5, 4.5, "Browse Course Analytics"),
        (4.5, 3.7, "Explore Engagement\nPatterns"),
        (4.5, 2.9, "Score Cohort\n(Predict Dropouts)"),
        (4.5, 2.1, "Export At-Risk\nStudents (CSV)"),
        (4.5, 1.3, "Review Insights &\nRecommendations"),
        (7.4, 5.3, "Download OULAD"),
        (7.4, 4.5, "Clean Data"),
        (7.4, 3.7, "Build Warehouse"),
        (7.4, 2.9, "Train Model"),
    ]
    for x, y, label in cases:
        ax.add_patch(mpatches.Ellipse((x, y), 2.4, 0.7,
                                        linewidth=1.2, edgecolor=DARK,
                                        facecolor=LIGHT_BLUE))
        ax.text(x, y, label, ha="center", va="center", fontsize=9, color=DARK)
        # connect actors
        if x == 4.5:
            ax.plot([1.4 + 0.30, x - 1.2], [4.5, y], color=DARK, lw=0.8)
        else:
            ax.plot([9.7 - 0.30, x + 1.2], [4.5, y], color=DARK, lw=0.8)

    _save(fig, "figure_3_4_use_case.png")


# ============================ Figure 4.1: Class Diagram =====================

def figure_4_1_class_diagram() -> None:
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9); ax.axis("off")
    ax.text(7, 8.6, "Figure 4.1 — Class Diagram  (Python modules as UML classes)",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    def umlclass(x, y, w, h, name, attrs, ops, color=LIGHT_BLUE):
        ax.add_patch(mpatches.Rectangle((x, y), w, h, linewidth=1.3,
                                          edgecolor=DARK, facecolor=color))
        # name compartment
        name_h = 0.5
        ax.add_patch(mpatches.Rectangle((x, y + h - name_h), w, name_h,
                                          linewidth=1.3, edgecolor=DARK,
                                          facecolor="#BFD3F7"))
        ax.text(x + w / 2, y + h - name_h / 2, name,
                ha="center", va="center", fontweight="bold", fontsize=10)
        # attributes
        attr_h = 0.32 * len(attrs)
        for i, a in enumerate(attrs):
            ax.text(x + 0.1, y + h - name_h - 0.25 - i * 0.30, "− " + a,
                    fontsize=8.5, color=DARK, va="center")
        # separator
        sep_y = y + h - name_h - attr_h - 0.10
        ax.plot([x, x + w], [sep_y, sep_y], color=DARK, lw=1.0)
        # operations
        for i, op in enumerate(ops):
            ax.text(x + 0.1, sep_y - 0.25 - i * 0.30, "+ " + op,
                    fontsize=8.5, color=DARK, va="center")

    # Layout: 3 columns × 2 rows
    umlclass(0.3, 5.6, 4.0, 2.6, "Downloader",
             ["OULAD_URLS : list[str]", "RAW_DIR : Path", "ZIP_PATH : Path"],
             ["already_downloaded() : bool",
              "download_zip() : None",
              "extract_zip() : None",
              "main() : int"])
    umlclass(4.8, 5.6, 4.4, 2.6, "Cleaner",
             ["RAW : Path", "PROC : Path", "CLEANERS : dict[str, fn]"],
             ["_read(name) : DataFrame",
              "_write_parquet(df, path) : None",
              "clean_student_info() : DataFrame",
              "clean_student_vle() : DataFrame",
              "main() : int"])
    umlclass(9.7, 5.6, 4.0, 2.6, "WarehouseBuilder",
             ["PROC : Path", "DB : Path", "SCHEMA : Path"],
             ["main() : int  (executes schema.sql,",
              "  loads dims + facts via COPY)"])

    umlclass(0.3, 2.7, 4.0, 2.6, "DropoutModelTrainer",
             ["NUMERIC : list[str]", "CATEGORICAL : list[str]",
              "TARGET : 'is_withdrawn'"],
             ["load_features() : DataFrame",
              "build_pipeline() : Pipeline",
              "main() : int"])
    umlclass(4.8, 2.7, 4.4, 2.6, "DashboardApp",
             ["pages : list[Page]", "warehouse : DuckDB"],
             ["render_overview() : None",
              "render_course_analytics() : None",
              "render_engagement_patterns() : None",
              "render_dropout_prediction() : None",
              "render_insights() : None"])
    umlclass(9.7, 2.7, 4.0, 2.6, "WarehouseAccess",
             ["DB_PATH : Path", "connection : DuckDBConn"],
             ["query(sql) : DataFrame",
              "list_courses() : DataFrame",
              "warehouse_stats() : dict"])

    # relationships (simple lines with arrows)
    _arrow(ax, (4.3, 6.9), (4.8, 6.9))    # Downloader → Cleaner
    ax.text(4.55, 7.05, "feeds", ha="center", fontsize=8, color=DARK)
    _arrow(ax, (9.2, 6.9), (9.7, 6.9))    # Cleaner → WarehouseBuilder
    ax.text(9.45, 7.05, "feeds", ha="center", fontsize=8, color=DARK)
    _arrow(ax, (11.7, 5.6), (11.7, 5.3))  # WarehouseBuilder → WarehouseAccess (read)
    ax.text(11.7, 5.45, "reads from", ha="center", fontsize=8, color=DARK)
    _arrow(ax, (2.3, 5.6), (2.3, 5.3))    # Downloader → Trainer (uses warehouse)
    _arrow(ax, (9.7, 4.0), (9.2, 4.0))    # Access → Dashboard
    ax.text(9.45, 4.15, "queried by", ha="center", fontsize=8, color=DARK)
    _arrow(ax, (4.3, 4.0), (4.8, 4.0))    # Trainer → Dashboard
    ax.text(4.55, 4.15, "loaded by", ha="center", fontsize=8, color=DARK)

    _save(fig, "figure_4_1_class_diagram.png")


# ============================ Figure 4.2: Sequence Diagram =====================

def figure_4_2_sequence_diagram() -> None:
    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_xlim(0, 13); ax.set_ylim(0, 9); ax.axis("off")
    ax.text(6.5, 8.6, "Figure 4.2 — Sequence Diagram  (Dropout-Prediction Flow)",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    actors = [
        (1.2, "Administrator"),
        (3.6, "Streamlit\nDashboard"),
        (6.2, "WarehouseAccess\n(DuckDB)"),
        (9.0, "v_student_features\n(view)"),
        (11.6, "Dropout Model\n(joblib)"),
    ]
    for x, name in actors:
        # header box
        ax.add_patch(mpatches.Rectangle((x - 0.9, 7.5), 1.8, 0.6,
                                          linewidth=1.3, edgecolor=DARK,
                                          facecolor=LIGHT_BLUE))
        ax.text(x, 7.8, name, ha="center", va="center", fontsize=9,
                fontweight="bold", color=DARK)
        # lifeline (dashed)
        ax.plot([x, x], [7.5, 0.6], color=DARK, lw=0.8, linestyle="--")

    # messages (top-down)
    messages = [
        (1.2, 3.6, 7.0, "1. select course presentation",      True),
        (3.6, 6.2, 6.5, "2. cohort = query(SELECT * FROM v_student_features WHERE …)", True),
        (6.2, 9.0, 6.0, "3. SQL execute",                     True),
        (9.0, 6.2, 5.5, "4. cohort rows",                     False),
        (6.2, 3.6, 5.0, "5. DataFrame",                       False),
        (3.6, 11.6, 4.5, "6. model.predict_proba(features)",   True),
        (11.6, 3.6, 4.0, "7. probabilities[N]",                False),
        (3.6, 3.6, 3.5, "8. attach risk-flag at threshold",   True),
        (3.6, 1.2, 3.0, "9. render top-N table",              False),
        (1.2, 3.6, 2.5, "10. click Download CSV",             True),
        (3.6, 1.2, 2.0, "11. risk-scored CSV",                False),
    ]
    for from_x, to_x, y, label, request in messages:
        linestyle = "-" if request else "--"
        _arrow(ax, (from_x, y), (to_x, y), style="->",
               lw=1.0, linestyle=linestyle)
        midx = (from_x + to_x) / 2
        # offset label up
        ax.text(midx, y + 0.15, label, ha="center", fontsize=8.5, color=DARK)

    _save(fig, "figure_4_2_sequence_diagram.png")


# ============================ Figure 4.3: Activity Diagram =====================

def figure_4_3_activity_diagram() -> None:
    fig, ax = plt.subplots(figsize=(8, 12))
    ax.set_xlim(0, 8); ax.set_ylim(0, 14); ax.axis("off")
    ax.text(4, 13.5, "Figure 4.3 — Activity Diagram  (ETL Pipeline)",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    # start (filled circle)
    ax.add_patch(plt.Circle((4, 12.8), 0.18, color=DARK))
    _arrow(ax, (4, 12.6), (4, 12.0))

    # actions (rounded rectangles)
    def action(y, label, color=LIGHT_BLUE):
        _box(ax, (2.4, y - 0.35), 3.2, 0.7, label, color=color, fontsize=10)
        return y

    # decision (diamond)
    def decision(y, label):
        # diamond as polygon
        diamond = mpatches.Polygon(
            [(4, y + 0.55), (4.9, y), (4, y - 0.55), (3.1, y)],
            linewidth=1.3, edgecolor=DARK, facecolor=WARM,
        )
        ax.add_patch(diamond)
        ax.text(4, y, label, ha="center", va="center", fontsize=9,
                fontweight="bold", color=DARK)

    # Layout (top to bottom)
    decision(11.5, "Files\nalready\npresent?")
    ax.text(5.3, 11.5, "[yes]", fontsize=9, color=DARK)
    ax.text(2.7, 11.5, "[no]", fontsize=9, color=DARK)

    action(10.4, "Download OULAD ZIP")
    _arrow(ax, (4, 11.0), (4, 10.75))
    action(9.3, "Extract & flatten archive")
    _arrow(ax, (4, 10.05), (4, 9.65))
    action(8.2, "Clean: type coerce / null-fill / dedupe")
    _arrow(ax, (4, 8.95), (4, 8.55))
    action(7.1, "Write parquet via DuckDB")
    _arrow(ax, (4, 7.85), (4, 7.45))
    action(6.0, "Drop & recreate warehouse")
    _arrow(ax, (4, 6.75), (4, 6.35))
    action(4.9, "INSERT dims + facts")
    _arrow(ax, (4, 5.65), (4, 5.25))
    action(3.8, "Build v_student_features view")
    _arrow(ax, (4, 4.55), (4, 4.15))
    action(2.7, "Train GradientBoosting model")
    _arrow(ax, (4, 3.45), (4, 3.05))
    action(1.6, "Persist dropout_model.joblib", color=GREEN)
    _arrow(ax, (4, 2.30), (4, 1.95))

    # end (filled circle with ring)
    ax.add_patch(plt.Circle((4, 0.8), 0.22, edgecolor=DARK, facecolor="white", linewidth=1.3))
    ax.add_patch(plt.Circle((4, 0.8), 0.10, color=DARK))
    _arrow(ax, (4, 1.30), (4, 1.05))

    # [yes] branch: skip Download + Extract, jump directly to Clean
    # (The [no] path is just the default downward flow from the diamond
    # through Download → Extract → Clean, no extra arrows needed.)
    ax.plot([4.9, 6.5], [11.5, 11.5], color=DARK, lw=1.0)
    ax.plot([6.5, 6.5], [11.5, 8.55], color=DARK, lw=1.0)
    _arrow(ax, (6.5, 8.55), (5.6, 8.55))

    _save(fig, "figure_4_3_activity_diagram.png")


# ============================ Figure 4.4: ER Diagram =====================

def figure_4_4_er_diagram() -> None:
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9); ax.axis("off")
    ax.text(7, 8.6, "Figure 4.4 — Entity–Relationship Diagram",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    def entity(x, y, w, h, name, attrs, color=LIGHT_BLUE):
        # name box
        ax.add_patch(mpatches.Rectangle((x, y), w, 0.5, linewidth=1.3,
                                          edgecolor=DARK, facecolor="#BFD3F7"))
        ax.text(x + w / 2, y + 0.25, name, ha="center", va="center",
                fontweight="bold", fontsize=10)
        # attributes box
        ah = 0.28 * len(attrs)
        ax.add_patch(mpatches.Rectangle((x, y - ah), w, ah, linewidth=1.3,
                                          edgecolor=DARK, facecolor=color))
        for i, a in enumerate(attrs):
            prefix = "PK " if "(PK)" in a else "FK " if "(FK)" in a else "      "
            display = a.replace(" (PK)", "").replace(" (FK)", "")
            ax.text(x + 0.1, y - 0.18 - i * 0.28, prefix + display,
                    fontsize=8.5, color=DARK, va="center", fontfamily="monospace")

    # Student entity (top-left)
    entity(0.3, 7.5, 3.5, 1.2, "STUDENT",
           ["id_student (PK)", "gender", "region", "age_band",
            "highest_education", "imd_band", "disability"])
    # Course entity (top-right)
    entity(10.0, 7.5, 3.5, 1.2, "COURSE",
           ["code_module (PK)", "code_presentation (PK)",
            "module_presentation_length"])

    # Activity entity (mid-left)
    entity(0.3, 3.5, 3.5, 1.2, "ACTIVITY",
           ["id_site (PK)", "code_module (FK)", "code_presentation (FK)",
            "activity_type", "week_from", "week_to"])
    # Assessment entity (mid-right)
    entity(10.0, 3.5, 3.5, 1.2, "ASSESSMENT",
           ["id_assessment (PK)", "code_module (FK)", "code_presentation (FK)",
            "assessment_type", "date", "weight"])

    # Central relationship (Enrollment / Engagement / AssessmentSubmission)
    entity(5.0, 5.5, 4.0, 1.4, "ENROLLMENT",
           ["id_student (FK)", "code_module (FK)",
            "code_presentation (FK)", "date_registration",
            "date_unregistration", "final_result"])

    entity(5.0, 1.5, 4.0, 1.4, "ENGAGEMENT_EVENT",
           ["id_student (FK)", "code_module (FK)",
            "code_presentation (FK)", "id_site (FK)",
            "date", "sum_click"])

    # Relationships with clean cardinality labels (1..N style)
    def rel(x1, y1, x2, y2, left_card, right_card):
        ax.plot([x1, x2], [y1, y2], color=DARK, lw=1.0)
        # place labels at 20% and 80% along the line
        ax.text(x1 + 0.18 * (x2 - x1), y1 + 0.18 * (y2 - y1) + 0.15,
                left_card, fontsize=10, fontweight="bold", color=BLUE,
                ha="center", bbox=dict(boxstyle="round,pad=0.2",
                                       facecolor="white", edgecolor="none"))
        ax.text(x1 + 0.82 * (x2 - x1), y1 + 0.82 * (y2 - y1) + 0.15,
                right_card, fontsize=10, fontweight="bold", color=BLUE,
                ha="center", bbox=dict(boxstyle="round,pad=0.2",
                                       facecolor="white", edgecolor="none"))

    # STUDENT (1) ── enrolls in ── (N) COURSE  (via ENROLLMENT)
    rel(3.8, 7.0, 5.0, 6.5, "1", "N")
    rel(9.0, 6.5, 10.0, 7.0, "N", "1")
    # ENROLLMENT has demographic / outcome attributes shown in its own box

    # STUDENT (1) ── generates ── (N) ENGAGEMENT_EVENT
    rel(3.8, 7.4, 5.0, 2.5, "1", "N")
    # COURSE (1) ── has ── (N) ACTIVITY
    rel(10.0, 7.5, 3.8, 4.0, "1", "N")
    # COURSE (1) ── has ── (N) ASSESSMENT
    rel(11.5, 7.5, 11.5, 4.7, "1", "N")
    # ACTIVITY (1) ── recorded in ── (N) ENGAGEMENT_EVENT
    rel(3.8, 3.5, 5.0, 2.2, "1", "N")

    _save(fig, "figure_4_4_er_diagram.png")


# ============================ Figure 4.5: Star Schema =====================

def figure_4_5_star_schema() -> None:
    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_xlim(0, 13); ax.set_ylim(0, 9); ax.axis("off")
    ax.text(6.5, 8.6, "Figure 4.5 — Warehouse Star Schema",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    def table(x, y, w, h, name, cols, color=LIGHT_BLUE):
        ax.add_patch(mpatches.Rectangle((x, y), w, 0.5, linewidth=1.3,
                                          edgecolor=DARK, facecolor="#BFD3F7"))
        ax.text(x + w / 2, y + 0.25, name, ha="center", va="center",
                fontweight="bold", fontsize=10)
        ch = 0.27 * len(cols)
        ax.add_patch(mpatches.Rectangle((x, y - ch), w, ch, linewidth=1.3,
                                          edgecolor=DARK, facecolor=color))
        for i, c in enumerate(cols):
            ax.text(x + 0.1, y - 0.16 - i * 0.27, c, fontsize=8.5,
                    fontfamily="monospace", va="center")

    # Centre fact tables - stack 3 facts vertically
    table(5.0, 6.7, 4.0, 0.9, "fact_engagement",
          ["id_student  FK", "code_module/pres  FK",
           "id_site  FK", "date", "sum_click"], color=GREEN)
    table(5.0, 4.3, 4.0, 0.9, "fact_assessment",
          ["id_student  FK", "id_assessment  FK",
           "code_module/pres  FK", "date_submitted",
           "score"], color=GREEN)
    table(5.0, 1.9, 4.0, 0.9, "fact_enrollment",
          ["id_student  FK", "code_module/pres  FK",
           "date_registration", "date_unregistration",
           "final_result", "is_withdrawn", "is_passed"], color=GREEN)

    # Dim tables — corners
    table(0.5, 6.7, 3.5, 0.9, "dim_student",
          ["id_student  PK", "gender", "region", "age_band",
           "highest_education", "imd_band", "disability"])
    table(10.0, 6.7, 2.7, 0.9, "dim_activity",
          ["id_site  PK", "activity_type",
           "week_from", "week_to"])
    table(0.5, 1.9, 3.5, 0.9, "dim_course",
          ["code_module  PK", "code_presentation  PK",
           "module_presentation_length"])
    table(10.0, 1.9, 2.7, 0.9, "dim_assessment",
          ["id_assessment  PK", "assessment_type",
           "date", "weight"])

    # Edges from each dim to relevant facts
    def edge(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color=DARK, lw=1.0)

    # dim_student → all 3 facts
    edge(4.0, 6.4, 5.0, 6.5); edge(4.0, 6.4, 5.0, 4.1); edge(4.0, 6.4, 5.0, 1.7)
    # dim_course → all 3 facts
    edge(4.0, 1.7, 5.0, 1.7); edge(4.0, 1.7, 5.0, 4.1); edge(4.0, 1.7, 5.0, 6.5)
    # dim_activity → fact_engagement
    edge(10.0, 6.4, 9.0, 6.5)
    # dim_assessment → fact_assessment
    edge(10.0, 1.7, 9.0, 4.1)

    _save(fig, "figure_4_5_star_schema.png")


# ============================ Figure 4.6 / 4.7 / 4.8: Wireframes =====================

def _wireframe(title, sidebar_items, header, content_rows, out_name, fig_num):
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 8); ax.axis("off")
    ax.text(6.5, 7.6, f"Figure {fig_num} — UI Wireframe: {title}",
            ha="center", fontsize=13, fontweight="bold", color=DARK)

    # Browser chrome
    ax.add_patch(mpatches.Rectangle((0.5, 0.5), 12, 6.6,
                                       linewidth=1.5, edgecolor=DARK,
                                       facecolor="white"))
    ax.add_patch(mpatches.Rectangle((0.5, 6.5), 12, 0.6,
                                       linewidth=1.5, edgecolor=DARK,
                                       facecolor=GREY))
    for i, dot in enumerate(["#E25B47", "#E5A02C", "#5BC25C"]):
        ax.add_patch(plt.Circle((0.85 + i * 0.3, 6.8), 0.1, color=dot))
    ax.text(2.0, 6.8, "edupulse.streamlit.app  /  " + title,
            fontsize=10, va="center", color=DARK)

    # Sidebar
    ax.add_patch(mpatches.Rectangle((0.7, 0.7), 2.3, 5.7,
                                       linewidth=1.0, edgecolor=DARK,
                                       facecolor=LIGHT_BLUE))
    ax.text(1.85, 6.15, "EduPulse ⚡", ha="center",
            fontsize=11, fontweight="bold", color=DARK)
    for i, item in enumerate(sidebar_items):
        bold = "←" in item
        ax.text(0.85, 5.5 - i * 0.4, item, fontsize=9.5,
                fontweight="bold" if bold else "normal", color=DARK)

    # Header strip
    ax.add_patch(mpatches.Rectangle((3.2, 5.8), 9.1, 0.6,
                                       linewidth=1.0, edgecolor=DARK,
                                       facecolor=WARM))
    ax.text(3.4, 6.1, header, fontsize=11, fontweight="bold", color=DARK,
            va="center")

    # Content rows (5 KPIs / chart blocks)
    y0 = 5.4
    for row in content_rows:
        ax.add_patch(mpatches.Rectangle((row["x"], row["y"]), row["w"], row["h"],
                                           linewidth=1.0, edgecolor=DARK,
                                           facecolor=row.get("color", GREY)))
        ax.text(row["x"] + row["w"] / 2, row["y"] + row["h"] / 2,
                row["label"], ha="center", va="center",
                fontsize=row.get("fs", 9), color=DARK)

    _save(fig, out_name)


def figure_4_6_wf_home() -> None:
    _wireframe(
        title="Home / Overview",
        sidebar_items=["Home  ←", "Overview", "Course Analytics",
                       "Engagement Patterns", "Dropout Prediction", "Insights"],
        header="⚡ EduPulse — BI Dashboard",
        content_rows=[
            # 5 KPI cards
            {"x": 3.3, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Students\n32,593"},
            {"x": 5.1, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Enrollments\n32,593"},
            {"x": 6.9, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Pass rate\n47%"},
            {"x": 8.7, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Withdrawal\n31%"},
            {"x": 10.5, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Clicks\n10.6M"},
            # "what's in this dashboard" block
            {"x": 3.3, "y": 2.4, "w": 5.4, "h": 2.0, "label": "What's in this dashboard\n(5 bullets)",
             "color": LIGHT_BLUE},
            {"x": 8.9, "y": 2.4, "w": 3.3, "h": 2.0, "label": "Data source: OULAD\nCC BY 4.0", "color": LIGHT_BLUE},
            # Pipeline table
            {"x": 3.3, "y": 0.9, "w": 8.9, "h": 1.2, "label": "Pipeline Stage Table",
             "color": GREEN},
        ],
        out_name="figure_4_6_wf_home.png",
        fig_num="4.6",
    )


def figure_4_7_wf_overview() -> None:
    _wireframe(
        title="Overview Page",
        sidebar_items=["Home", "Overview  ←", "Course Analytics",
                       "Engagement Patterns", "Dropout Prediction", "Insights"],
        header="📈 Platform Overview",
        content_rows=[
            {"x": 3.3, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Students"},
            {"x": 5.1, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Enrollments"},
            {"x": 6.9, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Pass %"},
            {"x": 8.7, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Withdraw %"},
            {"x": 10.5, "y": 4.7, "w": 1.7, "h": 0.9, "label": "Distinctions"},
            {"x": 3.3, "y": 2.7, "w": 4.3, "h": 1.8, "label": "Outcome\nPie Chart", "color": LIGHT_BLUE},
            {"x": 7.9, "y": 2.7, "w": 4.3, "h": 1.8, "label": "Outcomes by Gender\n(Grouped Bar)", "color": LIGHT_BLUE},
            {"x": 3.3, "y": 0.9, "w": 8.9, "h": 1.5, "label": "Daily VLE Click Timeline (Line Chart)",
             "color": GREEN},
        ],
        out_name="figure_4_7_wf_overview.png",
        fig_num="4.7",
    )


# ============================ Figure 7.1: Query Latency ================

def figure_7_1_query_latency() -> None:
    """Measure real DuckDB query latency for the main dashboard queries."""
    import time
    import duckdb

    db = OUT.parents[1] / "data" / "warehouse.duckdb"
    con = duckdb.connect(str(db), read_only=True)

    queries = {
        "v_course_summary\n(per-course KPIs)": "SELECT * FROM v_course_summary",
        "Outcome distribution\n(fact_enrollment)":
            "SELECT final_result, COUNT(*) FROM fact_enrollment "
            "GROUP BY final_result",
        "Daily click timeline\n(fact_engagement, 300 days)":
            "SELECT date, SUM(sum_click) FROM fact_engagement "
            "WHERE date BETWEEN -30 AND 270 GROUP BY date ORDER BY date",
        "Activity-type mix\n(JOIN fact × dim)":
            "SELECT a.activity_type, SUM(fe.sum_click) "
            "FROM fact_engagement fe JOIN dim_activity a USING (id_site) "
            "GROUP BY a.activity_type",
        "Cohort feature scan\n(v_student_features)":
            "SELECT * FROM v_student_features "
            "WHERE code_module='AAA' AND code_presentation='2014J'",
    }

    # warm-up + 3 runs each
    timings = {}
    for label, sql in queries.items():
        con.execute(sql).fetchall()                  # warm-up
        samples = []
        for _ in range(3):
            t0 = time.perf_counter()
            con.execute(sql).fetchall()
            samples.append((time.perf_counter() - t0) * 1000)
        timings[label] = min(samples)               # best of 3 (ms)

    con.close()

    labels = list(timings.keys())
    values = [timings[k] for k in labels]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    bars = ax.barh(labels, values, color=BLUE, edgecolor=DARK, linewidth=0.8)
    ax.set_xlabel("Query latency  (milliseconds, best of 3 runs)", fontsize=11)
    ax.set_title("Figure 7.1 — DuckDB query latency for principal dashboard queries",
                 fontsize=13, fontweight="bold", color=DARK, pad=14)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)
    for b, v in zip(bars, values):
        ax.text(v + max(values) * 0.01, b.get_y() + b.get_height() / 2,
                f"{v:.1f} ms", va="center", fontsize=10, color=DARK)
    _save(fig, "figure_7_1_query_latency.png")


# ============================ Figures 6.1 / 6.2: Model evaluation ================

def _load_test_predictions():
    """Re-create the same stratified split used in training and return y_true, y_pred, y_proba."""
    import duckdb
    import joblib
    from sklearn.model_selection import train_test_split

    db = OUT.parents[1] / "data" / "warehouse.duckdb"
    model_path = OUT.parents[1] / "models" / "dropout_model.joblib"
    artifact = joblib.load(model_path)
    pipe = artifact["pipeline"]
    NUMERIC = artifact["numeric_features"]
    CATEGORICAL = artifact["categorical_features"]

    con = duckdb.connect(str(db), read_only=True)
    # ORDER BY is required: DuckDB doesn't guarantee row order on a view scan,
    # and the training run consumed rows in whatever order the warehouse first
    # returned. Locking the order here keeps the train/test split identical to
    # the one used at training time, so the figure's AUC matches the artifact.
    df = con.execute(
        "SELECT * FROM v_student_features "
        "ORDER BY id_student, code_module, code_presentation"
    ).df()
    con.close()
    y = df["is_withdrawn"].astype(int)
    X = df[NUMERIC + CATEGORICAL].copy()
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42,
    )
    proba = pipe.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    return y_test.values, pred, proba, artifact["metrics"]


def figure_6_1_confusion_matrix() -> None:
    import numpy as np
    from sklearn.metrics import confusion_matrix

    y_true, y_pred, _, _ = _load_test_predictions()
    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    im = ax.imshow(cm, cmap="Blues", aspect="auto")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Retained", "Withdrawn"], fontsize=11)
    ax.set_yticklabels(["Retained", "Withdrawn"], fontsize=11)
    ax.set_xlabel("Predicted label", fontsize=11)
    ax.set_ylabel("True label", fontsize=11)
    ax.set_title("Figure 6.1 — Confusion Matrix  (test set, threshold = 0.5)",
                 fontsize=12, fontweight="bold", color=DARK, pad=14)

    # annotate counts + percent
    total = cm.sum()
    for i in range(2):
        for j in range(2):
            c = cm[i, j]
            txt_color = "white" if c > cm.max() * 0.5 else DARK
            ax.text(j, i, f"{c:,}\n({c/total*100:.1f}%)",
                    ha="center", va="center", fontsize=13,
                    fontweight="bold", color=txt_color)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    _save(fig, "figure_6_1_confusion_matrix.png")


def figure_6_2_roc_curve() -> None:
    from sklearn.metrics import roc_curve, auc

    y_true, _, y_proba, metrics = _load_test_predictions()
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.plot(fpr, tpr, color=BLUE, lw=2.2,
            label=f"GBM (AUC = {roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], color="grey", lw=1.0, linestyle="--",
            label="Random classifier (AUC = 0.500)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.set_xlabel("False positive rate", fontsize=11)
    ax.set_ylabel("True positive rate", fontsize=11)
    ax.set_title("Figure 6.2 — ROC Curve  (held-out test set)",
                 fontsize=12, fontweight="bold", color=DARK, pad=14)
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(alpha=0.3)
    _save(fig, "figure_6_2_roc_curve.png")


def figure_4_8_wf_dropout() -> None:
    _wireframe(
        title="Dropout Prediction Page",
        sidebar_items=["Home", "Overview", "Course Analytics",
                       "Engagement Patterns", "Dropout Prediction  ←", "Insights",
                       "", "Module: AAA / 2014J", "Risk threshold: 0.50"],
        header="🎯 Dropout Prediction",
        content_rows=[
            {"x": 3.3, "y": 4.7, "w": 2.2, "h": 0.9, "label": "Accuracy\n0.803"},
            {"x": 5.7, "y": 4.7, "w": 2.2, "h": 0.9, "label": "ROC AUC\n0.810"},
            {"x": 8.1, "y": 4.7, "w": 2.0, "h": 0.9, "label": "Cohort\n2,041"},
            {"x": 10.3, "y": 4.7, "w": 1.9, "h": 0.9, "label": "At-risk\n658"},
            {"x": 3.3, "y": 2.6, "w": 8.9, "h": 1.9, "label": "Feature Importance Bar Chart",
             "color": LIGHT_BLUE},
            {"x": 3.3, "y": 0.9, "w": 6.5, "h": 1.5, "label": "Top-20 At-Risk Students Table",
             "color": GREEN},
            {"x": 10.0, "y": 0.9, "w": 2.2, "h": 1.5, "label": "Download\nCSV button", "color": WARM},
        ],
        out_name="figure_4_8_wf_dropout.png",
        fig_num="4.8",
    )


# ----------------------------------------------------------------- run

if __name__ == "__main__":
    figure_3_1_architecture()
    figure_3_2_dfd_level_0()
    figure_3_3_dfd_level_1()
    figure_3_4_use_case()
    print("Chapter-3 figures generated.")
    figure_4_1_class_diagram()
    figure_4_2_sequence_diagram()
    figure_4_3_activity_diagram()
    figure_4_4_er_diagram()
    figure_4_5_star_schema()
    figure_4_6_wf_home()
    figure_4_7_wf_overview()
    figure_4_8_wf_dropout()
    print("Chapter-4 figures generated.")
    figure_6_1_confusion_matrix()
    figure_6_2_roc_curve()
    print("Chapter-6 figures generated.")
    figure_7_1_query_latency()
    print("Chapter-7 figures generated.")
