from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


@dataclass
class FeatureArtifacts:
    label_encoders: dict[str, LabelEncoder]
    scaler: StandardScaler
    feature_columns: list[str]


def encode_categoricals_label(df: pd.DataFrame, exclude_cols: set[str] | None = None) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    """
    Matches the notebook approach: label-encode every object column.
    Note: this is suitable for tree models; for linear models, consider OneHotEncoding.
    """
    exclude_cols = exclude_cols or set()
    df = df.copy()

    encoders: dict[str, LabelEncoder] = {}
    cat_cols = [c for c in df.select_dtypes(include=["object"]).columns if c not in exclude_cols]

    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    return df, encoders


def standard_scale_train_test(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[object, object, StandardScaler]:
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, scaler
