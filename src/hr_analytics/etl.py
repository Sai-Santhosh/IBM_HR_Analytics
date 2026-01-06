from __future__ import annotations

import argparse
import pathlib

import pandas as pd

from hr_analytics.settings import Settings
from hr_analytics.validation import DROP_COLS, validate_hr_dataframe


def load_raw_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def clean_hr(df: pd.DataFrame) -> pd.DataFrame:
    # Drop constant / identifier columns (matches notebook)
    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    # Normalize common whitespace issues
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype(str).str.strip()

    # Replace obvious "nan" strings back to NaN
    df = df.replace({"nan": pd.NA, "NaN": pd.NA, "None": pd.NA})

    return df


def main() -> None:
    s = Settings()
    ap = argparse.ArgumentParser(description="ETL: load + clean IBM HR attrition dataset")
    ap.add_argument("--input", default=s.raw_csv_path, help="Path to raw CSV")
    ap.add_argument("--out", default=s.processed_path, help="Path to write cleaned parquet")
    args = ap.parse_args()

    df = load_raw_csv(args.input)
    df = clean_hr(df)

    vr = validate_hr_dataframe(df)
    if not vr.ok:
        raise SystemExit("Data validation failed:\n- " + "\n- ".join(vr.errors))

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    print(f"Wrote cleaned dataset → {out_path} (rows={len(df)}, cols={df.shape[1]})")


if __name__ == "__main__":
    main()
