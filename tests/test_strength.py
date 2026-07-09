import pandas as pd
import pytest

from fx_utils.strength import pct_change_over_lookback


def _df(closes, complete=True):
    return pd.DataFrame(
        {
            "close": closes,
            "complete": [complete] * len(closes),
        }
    )


def test_pct_change_positive_move():
    df = _df([100.0, 101.0, 102.0, 103.0, 105.0])
    result = pct_change_over_lookback(df, lookback=4)
    assert result == pytest.approx((105.0 - 100.0) / 100.0 * 100.0)


def test_pct_change_negative_move():
    df = _df([100.0, 99.0, 98.0])
    result = pct_change_over_lookback(df, lookback=2)
    assert result == pytest.approx((98.0 - 100.0) / 100.0 * 100.0)


def test_pct_change_ignores_incomplete_candles():
    df = pd.DataFrame(
        {
            "close": [100.0, 101.0, 102.0, 999.0],
            "complete": [True, True, True, False],
        }
    )
    result = pct_change_over_lookback(df, lookback=2)
    assert result == pytest.approx((102.0 - 100.0) / 100.0 * 100.0)


def test_pct_change_raises_when_not_enough_history():
    df = _df([100.0, 101.0])
    with pytest.raises(ValueError):
        pct_change_over_lookback(df, lookback=5)
