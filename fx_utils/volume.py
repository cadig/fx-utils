"""Sums notional trade volume from ORDER_FILL transactions over a date range, converted
into the account's base currency, by walking the paginated OANDA transactions history
endpoint and pricing endpoint."""
from __future__ import annotations

import requests
from oandapyV20 import API
from oandapyV20.endpoints.pricing import PricingInfo
from oandapyV20.endpoints.transactions import TransactionList

API_HOSTS = {
    "practice": "https://api-fxpractice.oanda.com",
    "live": "https://api-fxtrade.oanda.com",
}


def _mid_price(client: API, account_id: str, instrument: str) -> float:
    request = PricingInfo(accountID=account_id, params={"instruments": instrument})
    response = client.request(request)
    price = response["prices"][0]
    bid = float(price["bids"][0]["price"])
    ask = float(price["asks"][0]["price"])
    return (bid + ask) / 2


def _conversion_rate(
    client: API, account_id: str, from_ccy: str, to_ccy: str, cache: dict[tuple[str, str], float]
) -> float:
    """1 unit of `from_ccy` expressed in `to_ccy`, using current spot pricing.

    Uses a direct instrument if OANDA lists one (in either orientation), otherwise
    bridges through USD. This is a live-rate approximation, not the historical rate
    at fill time.
    """
    if from_ccy == to_ccy:
        return 1.0
    if (from_ccy, to_ccy) in cache:
        return cache[(from_ccy, to_ccy)]

    try:
        rate = _mid_price(client, account_id, f"{from_ccy}_{to_ccy}")
    except Exception:
        try:
            rate = 1 / _mid_price(client, account_id, f"{to_ccy}_{from_ccy}")
        except Exception:
            if "USD" in (from_ccy, to_ccy):
                raise
            via_usd = _conversion_rate(client, account_id, from_ccy, "USD", cache)
            usd_to_target = _conversion_rate(client, account_id, "USD", to_ccy, cache)
            rate = via_usd * usd_to_target

    cache[(from_ccy, to_ccy)] = rate
    return rate


def notional_volume(
    client: API,
    token: str,
    environment: str,
    account_id: str,
    base_currency: str,
    start: str,
    end: str,
) -> float:
    """Returns total notional volume, converted into `base_currency`, summed across
    every ORDER_FILL transaction between `start` and `end` (RFC3339 timestamps).

    Each fill's notional (|units| * price) is in the instrument's quote currency;
    it's converted to `base_currency` using a current spot rate (bridged through USD
    if no direct pair exists), so conversion is approximate for fills whose quote
    currency has since moved against `base_currency`.
    """
    request = TransactionList(
        accountID=account_id, params={"from": start, "to": end, "type": "ORDER_FILL"}
    )
    response = client.request(request)

    headers = {"Authorization": f"Bearer {token}"}
    host = API_HOSTS[environment]
    rate_cache: dict[tuple[str, str], float] = {}
    total = 0.0
    for page_url in response.get("pages", []):
        url = page_url if page_url.startswith("http") else f"{host}{page_url}"
        page = requests.get(url, headers=headers, timeout=30)
        page.raise_for_status()
        for txn in page.json().get("transactions", []):
            if txn.get("type") != "ORDER_FILL":
                continue
            _, quote_ccy = txn["instrument"].split("_")
            notional_quote = abs(float(txn["units"])) * float(txn["price"])
            rate = _conversion_rate(client, account_id, quote_ccy, base_currency, rate_cache)
            total += notional_quote * rate
    return total
