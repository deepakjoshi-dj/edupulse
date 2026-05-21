-- Star-schema data warehouse for learning analytics
-- Database: DuckDB (file-based, embedded, OLAP columnar)
--
-- Grain choices:
--   fact_engagement      : 1 row per (student, course presentation, day)  -- daily VLE clicks
--   fact_assessment      : 1 row per (student, assessment) submission
--   fact_enrollment      : 1 row per (student, course presentation)       -- registration outcome
--
-- Dimensions are conformed across facts where possible.

DROP VIEW  IF EXISTS v_engagement_daily;
DROP VIEW  IF EXISTS v_course_summary;
DROP VIEW  IF EXISTS v_student_features;
DROP TABLE IF EXISTS fact_engagement;
DROP TABLE IF EXISTS fact_assessment;
DROP TABLE IF EXISTS fact_enrollment;
DROP TABLE IF EXISTS dim_student;
DROP TABLE IF EXISTS dim_course;
DROP TABLE IF EXISTS dim_activity;
DROP TABLE IF EXISTS dim_assessment;

---------------------------------------------------------------------------
-- Dimensions
---------------------------------------------------------------------------

CREATE TABLE dim_course (
    code_module                 VARCHAR  NOT NULL,
    code_presentation           VARCHAR  NOT NULL,
    module_presentation_length  INTEGER,
    PRIMARY KEY (code_module, code_presentation)
);

CREATE TABLE dim_student (
    id_student          INTEGER  NOT NULL,
    code_module         VARCHAR  NOT NULL,
    code_presentation   VARCHAR  NOT NULL,
    gender              VARCHAR,
    region              VARCHAR,
    highest_education   VARCHAR,
    imd_band            VARCHAR,
    age_band            VARCHAR,
    disability          VARCHAR,
    num_of_prev_attempts INTEGER,
    studied_credits     INTEGER,
    PRIMARY KEY (id_student, code_module, code_presentation)
);

CREATE TABLE dim_activity (
    id_site            INTEGER  NOT NULL,
    code_module        VARCHAR  NOT NULL,
    code_presentation  VARCHAR  NOT NULL,
    activity_type      VARCHAR,
    week_from          INTEGER,
    week_to            INTEGER,
    PRIMARY KEY (id_site)
);

CREATE TABLE dim_assessment (
    id_assessment      INTEGER  NOT NULL,
    code_module        VARCHAR  NOT NULL,
    code_presentation  VARCHAR  NOT NULL,
    assessment_type    VARCHAR,
    date               INTEGER,
    weight             DOUBLE,
    PRIMARY KEY (id_assessment)
);

---------------------------------------------------------------------------
-- Facts
---------------------------------------------------------------------------

-- Daily VLE click activity per student/course/activity
CREATE TABLE fact_engagement (
    id_student         INTEGER  NOT NULL,
    code_module        VARCHAR  NOT NULL,
    code_presentation  VARCHAR  NOT NULL,
    id_site            INTEGER  NOT NULL,
    date               INTEGER  NOT NULL,    -- days from course start (can be negative)
    sum_click          INTEGER  NOT NULL
);

CREATE TABLE fact_assessment (
    id_student         INTEGER  NOT NULL,
    id_assessment      INTEGER  NOT NULL,
    code_module        VARCHAR  NOT NULL,
    code_presentation  VARCHAR  NOT NULL,
    date_submitted     INTEGER,
    is_banked          TINYINT,
    score              DOUBLE
);

CREATE TABLE fact_enrollment (
    id_student            INTEGER  NOT NULL,
    code_module           VARCHAR  NOT NULL,
    code_presentation     VARCHAR  NOT NULL,
    date_registration     INTEGER,
    date_unregistration   INTEGER,
    final_result          VARCHAR,           -- Pass / Fail / Withdrawn / Distinction
    is_withdrawn          BOOLEAN,
    is_passed             BOOLEAN
);

---------------------------------------------------------------------------
-- Analytics views (consumed by the dashboard)
---------------------------------------------------------------------------

CREATE VIEW v_engagement_daily AS
SELECT
    code_module,
    code_presentation,
    date,
    COUNT(DISTINCT id_student)    AS active_students,
    SUM(sum_click)::BIGINT        AS total_clicks,
    AVG(sum_click)                AS avg_clicks_per_event
FROM fact_engagement
GROUP BY code_module, code_presentation, date;

CREATE VIEW v_course_summary AS
SELECT
    e.code_module,
    e.code_presentation,
    COUNT(*)                                                       AS enrollments,
    SUM(CASE WHEN e.is_passed     THEN 1 ELSE 0 END)               AS pass_count,
    SUM(CASE WHEN e.is_withdrawn  THEN 1 ELSE 0 END)               AS withdrawal_count,
    SUM(CASE WHEN e.final_result = 'Distinction' THEN 1 ELSE 0 END) AS distinction_count,
    ROUND(100.0 * SUM(CASE WHEN e.is_withdrawn THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS withdrawal_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN e.is_passed    THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS pass_rate_pct
FROM fact_enrollment e
GROUP BY e.code_module, e.code_presentation;

-- Per-student feature view used by ML + dashboard drilldowns
CREATE VIEW v_student_features AS
SELECT
    s.id_student,
    s.code_module,
    s.code_presentation,
    s.gender,
    s.region,
    s.highest_education,
    s.imd_band,
    s.age_band,
    s.disability,
    s.num_of_prev_attempts,
    s.studied_credits,
    e.final_result,
    e.is_withdrawn,
    e.is_passed,
    e.date_registration,
    COALESCE(SUM(fe.sum_click), 0)                AS total_clicks,
    COUNT(DISTINCT fe.date)                       AS active_days,
    COALESCE(AVG(fa.score), 0)                    AS avg_assessment_score,
    COUNT(fa.id_assessment)                       AS assessments_submitted
FROM dim_student s
JOIN fact_enrollment e
       ON  s.id_student        = e.id_student
       AND s.code_module       = e.code_module
       AND s.code_presentation = e.code_presentation
LEFT JOIN fact_engagement fe
       ON  s.id_student        = fe.id_student
       AND s.code_module       = fe.code_module
       AND s.code_presentation = fe.code_presentation
       AND fe.date <= 30           -- features computed from first 30 days only
LEFT JOIN fact_assessment fa
       ON  s.id_student        = fa.id_student
       AND s.code_module       = fa.code_module
       AND s.code_presentation = fa.code_presentation
       AND COALESCE(fa.date_submitted, 9999) <= 30
GROUP BY
    s.id_student, s.code_module, s.code_presentation,
    s.gender, s.region, s.highest_education, s.imd_band, s.age_band, s.disability,
    s.num_of_prev_attempts, s.studied_credits,
    e.final_result, e.is_withdrawn, e.is_passed, e.date_registration;
