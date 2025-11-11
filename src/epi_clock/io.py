from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

import pandas as pd


def read_table(
    path: str | Path,
    fmt: Optional[Literal["csv", "tsv", "parquet", "feather"]] = None,
    **kwargs,
) -> pd.DataFrame:
    p = Path(path)
    ext = fmt or p.suffix.lower().lstrip(".")
    if ext in ("csv",):
        return pd.read_csv(p, **kwargs)
    if ext in ("tsv",):
        return pd.read_csv(p, sep="\t", **kwargs)
    if ext in ("parquet",):
        return pd.read_parquet(p, **kwargs)
    if ext in ("feather", "ft"):
        return pd.read_feather(p, **kwargs)
    raise ValueError(f"Bilinmeyen/unsupported format: {ext} (path={p})")


def write_table(
    df: pd.DataFrame,
    path: str | Path,
    fmt: Optional[Literal["csv", "tsv", "parquet", "feather"]] = None,
    index: bool = False,
    **kwargs,
) -> None:
    p = Path(path)
    ext = fmt or p.suffix.lower().lstrip(".")
    p.parent.mkdir(parents=True, exist_ok=True)
    if ext in ("csv",):
        df.to_csv(p, index=index, **kwargs)
        return
    if ext in ("tsv",):
        df.to_csv(p, sep="\t", index=index, **kwargs)
        return
    if ext in ("parquet",):
        df.to_parquet(p, index=index, **kwargs)
        return
    if ext in ("feather", "ft"):
        df.to_feather(p, **kwargs)
        return
    raise ValueError(f"Bilinmeyen/unsupported format: {ext} (path={p})")
