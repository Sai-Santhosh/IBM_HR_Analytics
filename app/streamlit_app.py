from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

from hr_analytics.settings import Settings

st.set_page_config(page_title="IBM HR Attrition Analytics", layout="wide")

s = Settings()

@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    # Prefer analytics mart if Postgres is running; fallback to local parquet.
    try:
        url = f"postgresql+psycopg2://{s.pg_user}:{s.pg_password}@{s.pg_host}:{s.pg_port}/{s.pg_db}"
        engine = create_engine(url, pool_pre_ping=True)
        with engine.begin() as conn:
            df = pd.read_sql(text(f"SELECT * FROM {s.pg_schema_analytics}.fct_employee_attrition"), conn)
        return df
    except Exception:
        return pd.read_parquet(s.processed_path)

df = load_data()

st.title("IBM HR Attrition Analytics")
st.caption("Self-serve drilldowns + KPI cuts over a curated HR mart (Postgres) with reproducible ETL and model benchmarking.")

# Filters
with st.sidebar:
    st.header("Filters")
    dept = st.multiselect("Department", sorted(df["Department"].astype(str).unique()))
    role = st.multiselect("JobRole", sorted(df["JobRole"].astype(str).unique()))
    overtime = st.multiselect("OverTime", sorted(df["OverTime"].astype(str).unique()))

f = df.copy()
if dept:
    f = f[f["Department"].astype(str).isin(dept)]
if role:
    f = f[f["JobRole"].astype(str).isin(role)]
if overtime:
    f = f[f["OverTime"].astype(str).isin(overtime)]

# Normalize attrition flag for plots
attr = f["Attrition"].astype(str).str.lower().isin(["yes","1","true"]).astype(int)
f = f.assign(attrition_flag=attr)

c1, c2, c3 = st.columns(3)
c1.metric("Employees", f"{len(f):,}")
c2.metric("Attrition rate", f"{f['attrition_flag'].mean()*100:.1f}%")
c3.metric("Avg monthly income", f"${f['MonthlyIncome'].mean():,.0f}")

tab1, tab2, tab3 = st.tabs(["Drivers", "Segments", "Table"])

with tab1:
    colA, colB = st.columns(2)
    with colA:
        fig = px.bar(
            f.groupby("OverTime", dropna=False)["attrition_flag"].mean().reset_index(),
            x="OverTime", y="attrition_flag", title="Attrition rate by Overtime", labels={"attrition_flag": "attrition_rate"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        fig = px.bar(
            f.groupby("Department", dropna=False)["attrition_flag"].mean().reset_index().sort_values("attrition_flag", ascending=False),
            x="Department", y="attrition_flag", title="Attrition rate by Department", labels={"attrition_flag": "attrition_rate"}
        )
        st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        f, x="Age", y="MonthlyIncome", color="Attrition",
        hover_data=["JobRole","Department","OverTime"],
        title="Age vs Monthly Income (colored by Attrition)"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.box(
        f, x="JobRole", y="MonthlyIncome", color="Attrition",
        title="Monthly Income distribution by Job Role"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.dataframe(f, use_container_width=True, height=450)
