import pandas as pd
from hr_analytics.train import train_and_eval

def test_train_and_eval_smoke():
    # tiny synthetic dataset just to ensure code runs
    df = pd.DataFrame({
        "Attrition": ["Yes","No","No","Yes","No","No","Yes","No","No","No"],
        "Age": [22,35,29,41,30,27,38,33,26,45],
        "Department": ["Sales","R&D","Sales","R&D","Sales","HR","R&D","Sales","HR","R&D"],
        "JobRole": ["Sales Exec","Scientist","Sales Exec","Scientist","Sales Exec","HR","Scientist","Sales Exec","HR","Scientist"],
        "MonthlyIncome": [4000,9000,5000,12000,5500,6000,11000,5200,6100,12500],
        "OverTime": ["Yes","No","No","Yes","No","No","Yes","No","No","Yes"],
        "TotalWorkingYears": [1,10,5,15,6,4,12,7,3,20],
        # add a few extra numeric cols to mimic real data
        "DistanceFromHome": [2,10,5,15,7,3,9,6,4,12],
        "JobSatisfaction": [3,4,2,2,3,3,1,4,2,1],
    })
    # Convert Attrition to 0/1 by simple mapping to align with notebook expectations after encoding
    # The training code label-encodes this column; for stability in this test we pre-map to 0/1.
    df["Attrition"] = df["Attrition"].map({"No":0,"Yes":1})
    out = train_and_eval(df, random_state=42)
    assert "best" in out
    assert len(out["results"]) >= 5
