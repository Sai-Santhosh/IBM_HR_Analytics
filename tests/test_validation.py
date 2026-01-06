import pandas as pd
from hr_analytics.validation import validate_hr_dataframe

def test_validate_ok_minimal():
    df = pd.DataFrame({
        "Attrition": ["Yes", "No"],
        "Age": [25, 33],
        "Department": ["Sales", "Research & Development"],
        "JobRole": ["Sales Executive", "Research Scientist"],
        "MonthlyIncome": [5000, 8000],
        "OverTime": ["Yes", "No"],
        "TotalWorkingYears": [3, 8],
    })
    vr = validate_hr_dataframe(df)
    assert vr.ok

def test_validate_missing_cols():
    df = pd.DataFrame({"Attrition": ["Yes"]})
    vr = validate_hr_dataframe(df)
    assert not vr.ok
