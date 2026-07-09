"""Live terminal currency strength meter.

Every minute, scans all 28 unique pairs across the 8 major currencies
(EUR, CAD, AUD, NZD, JPY, GBP, CHF, USD), computes each pair's % price change over a
20-period M1 lookback, and aggregates a cumulative strength score per currency (each
currency appears in 7 of the 28 pairs). Renders the scores as a color-coded horizontal
diverging bar chart: strongest/weakest currencies stretch toward the screen edges,
middling currencies cluster near the zero-axis in the center.

Usage:
    python scripts/currency_strength_meter.py
    python scripts/currency_strength_meter.py --interval 60
"""
from __future__ import annotations

import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fx_utils.client import make_client
from fx_utils.config import load_settings
from fx_utils.currency_colors import CURRENCY_COLORS
from fx_utils.pairs import resolve_pairs
from fx_utils.strength import compute_currency_scores
from fx_utils.terminal_viz import diverging_bar_chart

GRANULARITY = "M1"
LOOKBACK = 20
CLEAR_SCREEN = "\033[2J\033[H"


def log(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    click.echo(f"[{ts}] {message}", err=True)


def render(scores: dict[str, float], trends: dict[str, float] | None) -> None:
    width = shutil.get_terminal_size(fallback=(80, 24)).columns
    click.echo(CLEAR_SCREEN, nl=False)
    click.echo(f"Currency Strength ({LOOKBACK}x{GRANULARITY} lookback, % change)")
    click.echo(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    click.echo()
    click.echo(diverging_bar_chart(scores, CURRENCY_COLORS, width=width, trends=trends))


@click.command()
@click.option("--account", "alias", default=None, help="Account alias from accounts.yaml")
@click.option("--interval", default=60, help="Poll interval in seconds")
@click.option("--once", is_flag=True, help="Run a single scan, print scores, and exit")
def main(alias, interval, once):
    settings = load_settings()
    client = make_client(settings)
    account = settings.account_for(alias)

    log("Resolving instrument names for all 28 major-currency pairs...")
    pairs = resolve_pairs(client, account.id)
    log(f"Resolved {len(pairs)} pairs: {[p.instrument for p in pairs]}")

    prev_scores: dict[str, float] | None = None

    while True:
        try:
            scores = compute_currency_scores(client, pairs, granularity=GRANULARITY, lookback=LOOKBACK)
            trends = None
            if prev_scores is not None:
                trends = {c: scores[c] - prev_scores[c] for c in scores}

            if once:
                for currency, score in sorted(scores.items(), key=lambda kv: kv[1], reverse=True):
                    click.echo(f"{currency}: {score:+.3f}")
                return

            render(scores, trends)
            prev_scores = scores
        except Exception as exc:  # keep the meter alive across transient API/network errors
            log(f"ERROR during scan: {exc!r}")

        time.sleep(interval)


if __name__ == "__main__":
    main()
