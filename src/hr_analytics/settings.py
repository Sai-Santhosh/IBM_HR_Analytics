from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    # Data paths
    raw_csv_path: str = os.getenv("HR_RAW_CSV", "data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv")
    processed_path: str = os.getenv("HR_PROCESSED_PATH", "data/processed/hr_clean.parquet")
    model_dir: str = os.getenv("HR_MODEL_DIR", "artifacts/model")
    report_dir: str = os.getenv("HR_REPORT_DIR", "reports")

    # Database (optional; used by ETL + dashboard)
    pg_host: str = os.getenv("PGHOST", "localhost")
    pg_port: int = int(os.getenv("PGPORT", "5432"))
    pg_db: str = os.getenv("PGDATABASE", "hr_analytics")
    pg_user: str = os.getenv("PGUSER", "postgres")
    pg_password: str = os.getenv("PGPASSWORD", "postgres")
    pg_schema_raw: str = os.getenv("PGSCHEMA_RAW", "raw")
    pg_schema_analytics: str = os.getenv("PGSCHEMA_ANALYTICS", "analytics")

    # Reproducibility
    random_state: int = int(os.getenv("HR_RANDOM_STATE", "2023"))
