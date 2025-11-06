from __future__ import annotations

import numpy as np
import pandas as pd


def drop_missing(df: pd.DataFrame, thresh: float = 0.2) -> pd.DataFrame:
    """
    Kolon bazında eksik oranı thresh'i aşan sütunları at.
    thresh=0.2 => %20'den fazla eksik varsa sütun düşer.
    """
    miss = df.isna().mean()
    keep_cols = miss[miss <= thresh].index.tolist()
    return df[keep_cols].copy()


def zscore(
    df: pd.DataFrame, cols: list[str] | None = None, clip: float | None = None
) -> pd.DataFrame:
    """
    Z-puan standardizasyonu uygular. clip belirtilirse +/- clip ile sınırlar.
    """
    X = df.copy()
    if cols is None:
        cols = X.select_dtypes(include=[np.number]).columns.tolist()

    mu = X[cols].mean()
    sd = X[cols].std(ddof=0).replace(0, np.nan)
    X[cols] = (X[cols] - mu) / sd

    if clip is not None:
        X[cols] = X[cols].clip(lower=-clip, upper=clip)

    return X
