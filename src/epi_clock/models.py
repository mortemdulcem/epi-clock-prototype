from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNetCV
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

@dataclass
class TrainResult:
    model: ElasticNetCV
    r2: float
    mae: float
    y_true: np.ndarray
    y_pred: np.ndarray

def split_xy(
    df: pd.DataFrame, target: str, drop_cols: Tuple[str, ...] = ()
) -> tuple[pd.DataFrame, pd.Series]:
    X = df.drop(columns=[target, *drop_cols], errors="ignore")
    y = df[target]
    return X, y

def train_elastic_clock(
    df: pd.DataFrame,
    target: str,
    test_size: float = 0.2,
    random_state: int = 42,
    l1_ratio=(0.1, 0.5, 0.7, 0.9, 0.95, 1.0),
    alphas=None,
) -> TrainResult:
    X, y = split_xy(df, target=target)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    model = ElasticNetCV(
        l1_ratio=l1_ratio,
        alphas=alphas,
        cv=5,
        n_jobs=None,
        random_state=random_state,
        max_iter=10000,
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    return TrainResult(model=model, r2=r2, mae=mae, y_true=y_test.to_numpy(), y_pred=y_pred)

def report_metrics(tr: TrainResult) -> Dict[str, float]:
    return {"r2": float(tr.r2), "mae": float(tr.mae)}
