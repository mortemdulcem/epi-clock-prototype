from __future__ import annotations
import numpy as np
import pandas as pd

def drop_missing(df: pd.DataFrame, thresh: float = 0.2) -> pd.DataFrame:
    miss = df.isna().mean()
    keep_cols = miss[miss <= thresh].index.tolist()
    return df[keep_cols].copy()

def zscore(
    df: pd.DataFrame, cols: list[str] | None = None, clip: float | None = None
) -> pd.DataFrame:
    X = df.copy()
    if cols is None:
        cols = X.select_dtypes(include=[np.number]).columns.tolist()
    mu = X[cols].mean()
    sd = X[cols].std(ddof=0).replace(0, np.nan)
    X[cols] = (X[cols] - mu) / sd
    if clip is not None:
        X[cols] = X[cols].clip(lower=-clip, upper=clip)
    return X
