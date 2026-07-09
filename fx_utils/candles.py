"""Candlestick retrieval utilities backed by the OANDA v20 instruments/candles endpoint."""
from __future__ import annotations

import pandas as pd
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles


def get_candles(
    client: API,
    instrument: str,
    granularity: str = "M1",
    count: int = 100,
    price: str = "M",
) -> pd.DataFrame:
    """Fetch recent candlesticks and return them as a DataFrame.

    Columns: time (tz-aware UTC), open, high, low, close, volume, complete.
    Rows are in ascending time order, matching the API response.
    """
    params = {"granularity": granularity, "count": count, "price": price}
    request = InstrumentsCandles(instrument=instrument, params=params)
    response = client.request(request)

    price_key = {"M": "mid", "B": "bid", "A": "ask"}[price]
    rows = []
    for candle in response["candles"]:
        ohlc = candle[price_key]
        rows.append(
            {
                "time": pd.Timestamp(candle["time"]),
                "open": float(ohlc["o"]),
                "high": float(ohlc["h"]),
                "low": float(ohlc["l"]),
                "close": float(ohlc["c"]),
                "volume": int(candle["volume"]),
                "complete": bool(candle["complete"]),
            }
        )
    return pd.DataFrame(rows)


def last_closed_candle(df: pd.DataFrame) -> pd.Series:
    """Return the most recent fully closed (complete=True) candle."""
    closed = df[df["complete"]]
    if closed.empty:
        raise ValueError("No completed candles in the given DataFrame")
    return closed.iloc[-1]
