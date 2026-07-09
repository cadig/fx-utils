"""Position inspection and management utilities for the OANDA v20 positions endpoint."""
from __future__ import annotations

from dataclasses import dataclass

from oandapyV20 import API
from oandapyV20.endpoints.positions import OpenPositions, PositionClose


@dataclass(frozen=True)
class OpenPosition:
    instrument: str
    long_units: float
    short_units: float

    @property
    def net_units(self) -> float:
        return self.long_units + self.short_units

    @property
    def is_long(self) -> bool:
        return self.long_units > 0

    @property
    def is_short(self) -> bool:
        return self.short_units < 0


def get_open_positions(client: API, account_id: str) -> list[OpenPosition]:
    request = OpenPositions(accountID=account_id)
    response = client.request(request)
    positions = []
    for p in response.get("positions", []):
        positions.append(
            OpenPosition(
                instrument=p["instrument"],
                long_units=float(p["long"]["units"]),
                short_units=float(p["short"]["units"]),
            )
        )
    return positions


def get_open_position(client: API, account_id: str, instrument: str) -> OpenPosition | None:
    for position in get_open_positions(client, account_id):
        if position.instrument == instrument:
            return position
    return None


def close_position(
    client: API,
    account_id: str,
    instrument: str,
    position: OpenPosition | None = None,
) -> dict:
    """Close all open units (long and/or short) for an instrument."""
    body = {}
    if position is None or position.is_long:
        body["longUnits"] = "ALL"
    if position is None or position.is_short:
        body["shortUnits"] = "ALL"

    request = PositionClose(accountID=account_id, instrument=instrument, data=body)
    return client.request(request)
