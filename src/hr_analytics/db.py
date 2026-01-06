from __future__ import annotations

import argparse
import pathlib

import pandas as pd
from sqlalchemy import create_engine, text

from hr_analytics.settings import Settings


def make_engine(s: Settings):
    url = f"postgresql+psycopg2://{s.pg_user}:{s.pg_password}@{s.pg_host}:{s.pg_port}/{s.pg_db}"
    return create_engine(url, pool_pre_ping=True)


def ensure_schemas(engine, raw_schema: str, analytics_schema: str) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {raw_schema};"))
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {analytics_schema};"))


def load_raw_to_postgres(df: pd.DataFrame, engine, raw_schema: str, table: str = "hr_employee") -> None:
    df.to_sql(table, engine, schema=raw_schema, if_exists="replace", index=False, method="multi", chunksize=2000)


def publish_curated_tables(df: pd.DataFrame, engine, analytics_schema: str) -> None:
    """Publish BI-ready cuts / views as physical tables for speed and reproducibility."""
    # Example curated tables (extend as needed)
    # 1) A clean employee fact table
    fact_cols = [c for c in df.columns if c not in ["EmployeeCount", "StandardHours", "Over18", "EmployeeNumber"]]
    df_fact = df[fact_cols].copy()
    df_fact.to_sql("fct_employee_attrition", engine, schema=analytics_schema, if_exists="replace", index=False, method="multi", chunksize=2000)

    # 2) Simple KPI rollups
    kpi = (
        df_fact.assign(attrition_flag=lambda d: (d["Attrition"].astype(str).str.lower().isin(["yes", "1"])).astype(int))
            .groupby(["Department", "JobRole"], dropna=False)
            .agg(employees=("attrition_flag", "size"), attrition_rate=("attrition_flag", "mean"), avg_income=("MonthlyIncome", "mean"))
            .reset_index()
    )
    kpi.to_sql("kpi_attrition_by_role", engine, schema=analytics_schema, if_exists="replace", index=False, method="multi", chunksize=2000)


def main() -> None:
    s = Settings()
    ap = argparse.ArgumentParser(description="Load cleaned HR dataset into Postgres and publish curated tables.")
    ap.add_argument("--data", default=s.processed_path, help="Cleaned parquet path (output of ETL)")
    ap.add_argument("--raw-schema", default=s.pg_schema_raw)
    ap.add_argument("--analytics-schema", default=s.pg_schema_analytics)
    args = ap.parse_args()

    df = pd.read_parquet(args.data)
    engine = make_engine(s)
    ensure_schemas(engine, args.raw_schema, args.analytics_schema)

    load_raw_to_postgres(df, engine, raw_schema=args.raw_schema)
    publish_curated_tables(df, engine, analytics_schema=args.analytics_schema)

    print(f"Loaded raw table → {args.raw_schema}.hr_employee")
    print(f"Published marts → {args.analytics_schema}.fct_employee_attrition, {args.analytics_schema}.kpi_attrition_by_role")


if __name__ == "__main__":
    main()
