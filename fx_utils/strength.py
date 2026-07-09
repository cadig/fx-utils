"""Currency strength scoring: per-pair % change over a lookback window, aggregated per
currency across every pair it appears in."""
from __future__ import annotations

import pandas as pd
from oandapyV20 import API

from fx_utils.candles import get_candles
from fx_utils.pairs import MAJORS, ResolvedPair


def pct_change_over_lookback(df: pd.DataFrame, lookback: int) -> float:
    """% change from the close `lookback` closed candles ago to the latest closed candle."""
    closed = df[df["complete"]]
    if len(closed) <= lookback:
        raise ValueError(
            f"Need more than {lookback} completed candles to compute pct change, "
            f"got {len(closed)}"
        )
    latest = closed.iloc[-1]["close"]
    reference = closed.iloc[-1 - lookback]["close"]
    return (latest - reference) / reference * 100.0


def pair_strength(client: API, pair: ResolvedPair, granularity: str, lookback: int) -> float:
    """Signed % change for `pair.instrument`, oriented so positive means currency_a
    strengthened against currency_b."""
    df = get_candles(client, pair.instrument, granularity=granularity, count=lookback + 5)
    change = pct_change_over_lookback(df, lookback)
    return change * pair.sign


def compute_currency_scores(
    client: API,
    pairs: list[ResolvedPair],
    granularity: str = "M1",
    lookback: int = 20,
) -> dict[str, float]:
    """Cumulative strength score per currency: sum of signed pct changes across every
    pair containing that currency."""
    scores = {currency: 0.0 for currency in MAJORS}
    for pair in pairs:
        change = pair_strength(client, pair, granularity, lookback)
        scores[pair.currency_a] += change
        scores[pair.currency_b] -= change
    return scores
