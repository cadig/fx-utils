"""Generates the set of unique currency pairs from a currency basket and resolves each
to its actual tradable OANDA instrument name + orientation (since OANDA lists only one
direction per pair, e.g. "EUR_USD" but never "USD_EUR")."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from oandapyV20 import API
from oandapyV20.endpoints.accounts import AccountInstruments

MAJORS = ["EUR", "CAD", "AUD", "NZD", "JPY", "GBP", "CHF", "USD"]


@dataclass(frozen=True)
class ResolvedPair:
    currency_a: str
    currency_b: str
    instrument: str
    # +1 if instrument is "{currency_a}_{currency_b}" (a is base), -1 if reversed.
    sign: int


def unique_currency_pairs(currencies: list[str] = MAJORS) -> list[tuple[str, str]]:
    """All C(n,2) unordered pairs, e.g. 28 pairs for 8 currencies."""
    return list(combinations(currencies, 2))


def fetch_available_instruments(client: API, account_id: str) -> set[str]:
    request = AccountInstruments(accountID=account_id)
    response = client.request(request)
    return {i["name"] for i in response["instruments"]}


def resolve_pairs(
    client: API, account_id: str, currencies: list[str] = MAJORS
) -> list[ResolvedPair]:
    """Resolve each unique currency pair to the instrument name actually listed by OANDA.

    Raises ValueError listing any pairs that couldn't be resolved in either direction,
    so misconfiguration is caught at startup rather than silently dropped.
    """
    available = fetch_available_instruments(client, account_id)
    resolved = []
    missing = []
    for a, b in unique_currency_pairs(currencies):
        forward = f"{a}_{b}"
        reverse = f"{b}_{a}"
        if forward in available:
            resolved.append(ResolvedPair(a, b, forward, sign=1))
        elif reverse in available:
            resolved.append(ResolvedPair(a, b, reverse, sign=-1))
        else:
            missing.append((a, b))

    if missing:
        raise ValueError(f"Could not resolve instruments for pairs: {missing}")
    return resolved
