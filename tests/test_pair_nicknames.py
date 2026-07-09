from fx_utils.pair_nicknames import pair_nickname


def test_known_pairs():
    assert pair_nickname("EUR_USD") == "euro"
    assert pair_nickname("USD_JPY") == "yen"
    assert pair_nickname("GBP_USD") == "cable"
    assert pair_nickname("NZD_USD") == "kiwi"
    assert pair_nickname("AUD_USD") == "aussie"
    assert pair_nickname("USD_CAD") == "cad"
    assert pair_nickname("USD_CHF") == "swiss"


def test_unknown_pair_falls_back_to_slash_form():
    assert pair_nickname("EUR_GBP") == "EUR/GBP"
