from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


# Columns commonly dropped in the IBM HR dataset (not predictive / constant)
DROP_COLS = ["EmployeeCount", "StandardHours", "Over18", "EmployeeNumber"]

# Minimal required fields for our pipeline
REQUIRED_COLS = [
    "Attrition",
    "Age",
    "Department",
    "JobRole",
    "MonthlyIncome",
    "OverTime",
    "TotalWorkingYears",
]


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]


def validate_hr_dataframe(df: pd.DataFrame, required_cols: Iterable[str] = REQUIRED_COLS) -> ValidationResult:
    errors: list[str] = []

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")

    if "Attrition" in df.columns:
        # Accept common variants: Yes/No or 1/0 (after encoding)
        s = df["Attrition"].dropna()
        if s.dtype == object:
            bad = sorted(set(s.unique()) - {"Yes", "No"})
            if bad:
                errors.append(f"Unexpected Attrition values: {bad} (expected Yes/No)")
        else:
            bad = sorted(set(s.unique()) - {0, 1})
            if bad:
                errors.append(f"Unexpected Attrition values: {bad} (expected 0/1)")

    # Basic sanity checks
    if "Age" in df.columns:
        if (df["Age"].dropna() <= 0).any():
            errors.append("Age has non-positive values.")
    if "MonthlyIncome" in df.columns:
        if (df["MonthlyIncome"].dropna() < 0).any():
            errors.append("MonthlyIncome has negative values.")

    return ValidationResult(ok=(len(errors) == 0), errors=errors)
