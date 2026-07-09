"""General-purpose interactive CLI entry point (`fx-utils`) for ad-hoc account/position/candle checks."""
from __future__ import annotations

import click

from fx_utils.client import make_client
from fx_utils.config import load_settings
from fx_utils import candles as candles_mod
from fx_utils import positions as positions_mod


@click.group()
def main():
    """fx-utils: interactive OANDA v20 CLI utilities."""


@main.command()
def accounts():
    """List configured account aliases and ids."""
    settings = load_settings()
    for account in settings.accounts:
        marker = " (default)" if account.alias == settings.default_alias else ""
        click.echo(f"{account.alias}{marker}: {account.id}")


@main.command()
@click.option("--account", "alias", default=None, help="Account alias from accounts.yaml")
def positions(alias):
    """List open positions for an account."""
    settings = load_settings()
    client = make_client(settings)
    account = settings.account_for(alias)
    open_positions = positions_mod.get_open_positions(client, account.id)
    if not open_positions:
        click.echo(f"No open positions for {account.alias} ({account.id})")
        return
    for p in open_positions:
        click.echo(f"{p.instrument}: net_units={p.net_units} long={p.long_units} short={p.short_units}")


@main.command()
@click.option("--account", "alias", default=None, help="Account alias from accounts.yaml")
@click.option("--instrument", required=True, help="e.g. EUR_USD")
@click.option("--granularity", default="M1", help="e.g. M1, M5, H1")
@click.option("--count", default=20, help="Number of candles to fetch")
def candles(alias, instrument, granularity, count):
    """Show recent candlesticks for an instrument."""
    settings = load_settings()
    client = make_client(settings)
    settings.account_for(alias)  # validates alias even though candles are account-agnostic
    df = candles_mod.get_candles(client, instrument, granularity=granularity, count=count)
    click.echo(df.to_string(index=False))


if __name__ == "__main__":
    main()
