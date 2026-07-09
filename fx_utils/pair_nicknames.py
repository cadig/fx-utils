"""Maps OANDA instrument names to their spoken nickname, for voice notifications."""
from __future__ import annotations

PAIR_NICKNAMES = {
    "EUR_USD": "euro",
    "USD_JPY": "yen",
    "GBP_USD": "cable",
    "NZD_USD": "kiwi",
    "AUD_USD": "aussie",
    "USD_CAD": "cad",
    "USD_CHF": "swiss",
}


def pair_nickname(instrument: str) -> str:
    """Spoken nickname for an instrument, e.g. "EUR_USD" -> "euro".

    Falls back to a slash-separated form (e.g. "EUR_GBP" -> "EUR/GBP") for pairs
    without a defined nickname.
    """
    return PAIR_NICKNAMES.get(instrument, instrument.replace("_", "/"))
