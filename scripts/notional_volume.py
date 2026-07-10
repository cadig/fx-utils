"""Sums total notional trading volume for an account over a date range, by summing
|units| * fill price across every ORDER_FILL transaction in the range.

Usage:
    python scripts/notional_volume.py --account main --start 2026-06-01
    python scripts/notional_volume.py --account main --start 2026-06-01 --end 2026-07-31
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fx_utils.client import make_client
from fx_utils.config import load_settings
from fx_utils.volume import notional_volume


def to_rfc3339(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat()


@click.command()
@click.option("--account", "alias", required=True, help="Account alias from accounts.yaml")
@click.option("--start", required=True, help="Start date, YYYY-MM-DD")
@click.option("--end", default=None, help="End date, YYYY-MM-DD (defaults to now)")
def main(alias, start, end):
    settings = load_settings()
    client = make_client(settings)
    account = settings.account_for(alias)

    start_rfc3339 = to_rfc3339(start)
    end_rfc3339 = to_rfc3339(end) if end else datetime.now(timezone.utc).isoformat()

    total = notional_volume(
        client,
        settings.token,
        settings.environment,
        account.id,
        account.base_currency,
        start_rfc3339,
        end_rfc3339,
    )

    click.echo(f"Account: {account.alias} ({account.id})")
    click.echo(f"Period: {start_rfc3339} to {end_rfc3339}")
    click.echo(f"Total notional volume: {total:,.2f} {account.base_currency}")


if __name__ == "__main__":
    main()
