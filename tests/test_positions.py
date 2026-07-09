from fx_utils.positions import OpenPosition


def test_long_position_flags():
    p = OpenPosition(instrument="EUR_USD", long_units=1000.0, short_units=0.0)
    assert p.is_long
    assert not p.is_short
    assert p.net_units == 1000.0


def test_short_position_flags():
    p = OpenPosition(instrument="EUR_USD", long_units=0.0, short_units=-500.0)
    assert not p.is_long
    assert p.is_short
    assert p.net_units == -500.0


def test_flat_position_flags():
    p = OpenPosition(instrument="EUR_USD", long_units=0.0, short_units=0.0)
    assert not p.is_long
    assert not p.is_short
    assert p.net_units == 0.0
