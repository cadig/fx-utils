import pandas as pd

from fx_utils.indicators import ema, with_ema


def test_ema_matches_pandas_ewm():
    series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    result = ema(series, period=3)
    expected = series.ewm(span=3, adjust=False).mean()
    pd.testing.assert_series_equal(result, expected)


def test_with_ema_adds_expected_column():
    df = pd.DataFrame({"close": [1.0, 2.0, 3.0]})
    out = with_ema(df, period=2)
    assert "ema_2" in out.columns
    assert "close" in df.columns  # original untouched
    assert len(out) == len(df)
