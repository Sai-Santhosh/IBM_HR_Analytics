# Architecture

**Data flow**
1. Raw CSV → `hr_analytics.etl` → cleaned parquet
2. Clean parquet → `hr_analytics.db` → Postgres
   - `raw.hr_employee` (source of truth)
   - `analytics.*` marts for BI and dashboard
3. `hr_analytics.train` benchmarks models with SMOTE and saves best artifacts
4. Streamlit app reads from Postgres marts (fallback to parquet if DB isn’t running)

**Why Postgres**
- Simple local dev via Docker
- Warehouse-like modeling patterns (staging → marts)
- dbt compatibility for tests/docs
