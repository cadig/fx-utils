"""Reusable technical indicator calculations over candlestick DataFrames."""
from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def with_ema(df: pd.DataFrame, period: int, column: str = "close") -> pd.DataFrame:
    """Return a copy of df with an `ema_{period}` column added."""
    out = df.copy()
    out[f"ema_{period}"] = ema(out[column], period)
    return out
