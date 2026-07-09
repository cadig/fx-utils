"""Thin factory around oandapyV20's API client, built from fx_utils.config.Settings."""
from __future__ import annotations

from oandapyV20 import API

from fx_utils.config import Settings


def make_client(settings: Settings) -> API:
    return API(access_token=settings.token, environment=settings.environment)
