from __future__ import annotations

import argparse
import json
import pathlib

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

try:
    from xgboost import XGBClassifier  # optional
except Exception:  # pragma: no cover
    XGBClassifier = None  # type: ignore

from hr_analytics.features import encode_categoricals_label, standard_scale_train_test
from hr_analytics.settings import Settings


def train_and_eval(df: pd.DataFrame, random_state: int = 2023) -> dict:
    # Encode label
    df2, encoders = encode_categoricals_label(df)

    # Target
    y = df2["Attrition"]
    X = df2.drop(columns=["Attrition"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    # Scale (matches notebook flow)
    X_train_scaled, X_test_scaled, scaler = standard_scale_train_test(X_train, X_test)

    # Balance train set via SMOTE
    sm = SMOTE(random_state=42)
    X_train_bal, y_train_bal = sm.fit_resample(X_train_scaled, y_train)

    # Model zoo (matches notebook output set)
    models = [
        ("LogisticRegression", LogisticRegression(max_iter=2000, random_state=42)),
        ("KNN", KNeighborsClassifier(n_neighbors=5)),
        ("SVM", SVC(kernel="rbf", C=1.0, gamma="scale", random_state=42)),
        ("GaussianNB", GaussianNB()),
        ("DecisionTree", DecisionTreeClassifier(max_depth=5, random_state=42)),
        ("RandomForest", RandomForestClassifier(n_estimators=100, max_depth=None, random_state=42)),
        ("GradientBoosting", GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, max_depth=3, random_state=42)),
    ]
    if XGBClassifier is not None:
        models.append(("XGBoost", XGBClassifier(
            n_estimators=150, learning_rate=0.1, max_depth=3,
            subsample=0.8, colsample_bytree=0.8,
            random_state=42, use_label_encoder=False, eval_metric="logloss"
        )))

    results = []
    fitted = {}

    for name, model in models:
        model.fit(X_train_bal, y_train_bal)
        pred_tr = model.predict(X_train_bal)
        pred_te = model.predict(X_test_scaled)

        acc_tr = float(accuracy_score(y_train_bal, pred_tr))
        acc_te = float(accuracy_score(y_test, pred_te))

        results.append({"model": name, "train_accuracy": acc_tr, "test_accuracy": acc_te})
        fitted[name] = model

    results_sorted = sorted(results, key=lambda r: r["test_accuracy"], reverse=True)
    best = results_sorted[0]
    best_name = best["model"]

    artifacts = {
        "encoders": encoders,
        "scaler": scaler,
        "best_model": fitted[best_name],
        "feature_columns": list(X.columns),
    }

    return {
        "split": {
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "smote_before": {"majority": int((y_train==0).sum()), "minority": int((y_train==1).sum())},
            "smote_after": {"majority": int((y_train_bal==0).sum()), "minority": int((y_train_bal==1).sum())},
            "random_state": random_state,
        },
        "results": results_sorted,
        "best": best,
        "artifacts": artifacts,
    }


def main() -> None:
    s = Settings()
    ap = argparse.ArgumentParser(description="Train and benchmark models for IBM HR attrition")
    ap.add_argument("--data", default=s.processed_path, help="Cleaned parquet path (output of ETL)")
    ap.add_argument("--outdir", default=s.model_dir, help="Directory to write model artifacts")
    ap.add_argument("--metrics", default="reports/metrics.json", help="Path to write metrics JSON")
    ap.add_argument("--random-state", type=int, default=s.random_state)
    args = ap.parse_args()

    df = pd.read_parquet(args.data)
    out = train_and_eval(df, random_state=args.random_state)

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Persist artifacts
    joblib.dump(out["artifacts"]["best_model"], outdir / "model.joblib")
    joblib.dump(out["artifacts"]["scaler"], outdir / "scaler.joblib")
    joblib.dump(out["artifacts"]["encoders"], outdir / "encoders.joblib")
    joblib.dump(out["artifacts"]["feature_columns"], outdir / "feature_columns.joblib")

    # Persist metrics
    metrics_path = pathlib.Path(args.metrics)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({
            "best": out["best"],
            "results": out["results"],
            "split": out["split"],
        }, f, indent=2)

    print(f"Best model: {out['best']['model']} (test_accuracy={out['best']['test_accuracy']:.4f})")
    print(f"Saved artifacts → {outdir}")
    print(f"Saved metrics   → {metrics_path}")


if __name__ == "__main__":
    main()
