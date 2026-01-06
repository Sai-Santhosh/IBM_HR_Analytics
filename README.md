# IBM HR Attrition Analytics (Analytics Engineering + ML Baseline)

A production-style, end-to-end **attrition analytics workflow** built on the classic IBM HR dataset (**1,470 rows, 35 columns**).
This repo focuses on what an Analytics / Data Analytics Engineer would ship: **ETL + data-quality**, **curated marts in Postgres**,
**reproducible model benchmarking**, and a **self-serve dashboard** for drilldowns.

- SMOTE balancing: minority class **190 → 986** (train split)
- Best baseline model: **GradientBoosting**, test accuracy **0.8673**

---

## What’s inside

### 1) ETL + Data Quality
- Loads the raw CSV, drops constant/identifier columns (`EmployeeCount`, `StandardHours`, `Over18`, `EmployeeNumber`)
- Normalizes string columns, enforces basic validation (required fields, sane ranges)
- Writes a clean parquet for repeatable downstream runs

### 2) Curated Analytics Tables (Postgres)
- Loads the clean dataset into `raw.hr_employee`
- Publishes BI-ready marts into `analytics.*`:
  - `analytics.fct_employee_attrition` (employee-level fact table)
  - `analytics.kpi_attrition_by_role` (role/department rollups)
- Includes reusable SQL cuts in `/sql` for quick stakeholder-ready views

### 3) Model Benchmarking (8+ baselines)
Benchmarks a small model zoo (LogReg, KNN, SVM, Naive Bayes, Decision Tree, RandomForest, GradientBoosting, optional XGBoost) using:
- Standard scaling (matches the original notebook flow)
- SMOTE to address imbalance
- Single command to produce `reports/metrics.json` + persisted artifacts (`joblib`)

### 4) Self-Serve Dashboard (Streamlit)
A lightweight UI over the curated marts:
- Filter by Department / JobRole / OverTime
- Attrition rate and income distributions
- Scatter + boxplots for fast driver exploration

### 5) dbt project (Postgres)
A small dbt project is included to demonstrate:
- staging → marts pattern
- tests + docs scaffolding

---

## Repo layout

```
app/                   # Streamlit UI
src/hr_analytics/       # ETL, validation, training, DB loader
dbt/                   # dbt models (staging → marts)
sql/                   # reusable SQL cuts
notebooks/             # original notebook
docs/assets/figures/    # extracted notebook figures
docker/                # Dockerfile + docker-compose (Postgres + app)
```

---

## Dataset

This repo expects the IBM HR CSV at:

`data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv`

You can download it from Kaggle:
- https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

(Recommended: don’t commit the full dataset to GitHub.)

---

## Quickstart (local)

### 0) Install
```bash
make install
```

Or manually:

```bash
pip install -r requirements.txt
pip install -e .
```

### 1) ETL: CSV → cleaned parquet
```bash
make etl
# writes data/processed/hr_clean.parquet
```

### 2) Start Postgres + dashboard (Docker)
```bash
make db-up
# Postgres: localhost:5432
# Dashboard: http://localhost:8501
```

### 3) Load curated tables into Postgres
In a second terminal:
```bash
make seed-db
```

### 4) Train + benchmark models
```bash
make train
# artifacts/model/* and reports/metrics.json
```

---

## Figures (from your notebook)

Notebook outputs are extracted and committed under `docs/assets/figures/`, including:
- `attrition_pie.png`
- `correlation_heatmap.png`
- `attrition_by_department.png`
- `attrition_by_overtime.png`
- `rf_feature_importance.png`
- `model_accuracy_comparison.png`
- confusion matrices (e.g., `cm_gradient_boosting.png`)

---

## Deployment notes (AWS ECS Fargate)

This repo includes a Dockerfile and compose setup that maps cleanly to:
- Build & push image to **ECR**
- Run the Streamlit app on **ECS Fargate** behind an **ALB**
- Use CloudWatch logs for app observability

See: `docs/aws_deployment.md`

---

## Reproducibility & Engineering Practices

- Deterministic train/test split (`HR_RANDOM_STATE`, default 2023)
- Metrics and artifacts persisted in `reports/` + `artifacts/`
- CI: lint + tests via GitHub Actions

---
