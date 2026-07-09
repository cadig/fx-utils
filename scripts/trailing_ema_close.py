"""Polls an OANDA account every N seconds; if a position is open for the given instrument
and direction, and the last closed candle closes across the EMA against that direction
(long: closes below EMA; short: closes above EMA), closes the position.

Instrument, EMA period, granularity, and direction are all required - there are no
defaults, so every run states exactly what it's trading.

Usage:
    python scripts/trailing_ema_close.py --account main \\
        --instrument EUR_USD --ema-period 26 --granularity M1 --direction long
    python scripts/trailing_ema_close.py --account main \\
        --instrument USD_JPY --ema-period 20 --granularity M5 --direction short --dry-run
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fx_utils.client import make_client
from fx_utils.config import load_settings
from fx_utils.candles import get_candles, last_closed_candle
from fx_utils.indicators import with_ema
from fx_utils.notify import speak
from fx_utils.pair_nicknames import pair_nickname
from fx_utils.positions import get_open_position, close_position


def log(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    click.echo(f"[{ts}] {message}")


def check_once(
    client,
    account_id: str,
    instrument: str,
    ema_period: int,
    granularity: str,
    direction: str,
    dry_run: bool,
) -> bool:
    """Returns True if this check actually closed the position (never True for dry runs)."""
    position = get_open_position(client, account_id, instrument)
    if position is None:
        log(f"No open {instrument} position. Skipping.")
        return False

    position_matches = position.is_long if direction == "long" else position.is_short
    if not position_matches:
        log(
            f"Open {instrument} position does not match expected direction "
            f"'{direction}' (long_units={position.long_units} "
            f"short_units={position.short_units}). Skipping."
        )
        return False

    # EMA needs warm-up history; fetch more than the period to let it stabilize.
    df = get_candles(client, instrument, granularity=granularity, count=ema_period * 3)
    df = with_ema(df, ema_period)
    last = last_closed_candle(df)
    ema_col = f"ema_{ema_period}"

    log(
        f"Open {instrument} {direction} position (net_units={position.net_units}). "
        f"Last closed candle close={last['close']:.5f} ema{ema_period}={last[ema_col]:.5f} "
        f"time={last['time']}"
    )

    if direction == "long":
        should_close = last["close"] < last[ema_col]
        reason = f"close below EMA{ema_period}"
    else:
        should_close = last["close"] > last[ema_col]
        reason = f"close above EMA{ema_period}"

    if should_close:
        if dry_run:
            log(f"DRY RUN: would close position ({reason}).")
            return False
        log(f"{reason} -> closing position.")
        result = close_position(client, account_id, instrument, position=position)
        log(f"Close response: {result}")
        speak(f"Closed {pair_nickname(instrument)} trade")
        return True

    log(f"No {reason} yet. Holding position.")
    return False


@click.command()
@click.option("--account", "alias", required=True, help="Account alias from accounts.yaml")
@click.option("--instrument", required=True, help="OANDA instrument, e.g. EUR_USD")
@click.option("--ema-period", required=True, type=int, help="EMA period, e.g. 26")
@click.option("--granularity", required=True, help="Candle granularity, e.g. M1, M5, H1")
@click.option(
    "--direction",
    required=True,
    type=click.Choice(["long", "short"]),
    help="Direction of the position being trailed",
)
@click.option("--interval", required=True, type=int, help="Poll interval in seconds")
@click.option("--dry-run", is_flag=True, help="Log the decision but never actually close")
@click.option("--once", is_flag=True, help="Run a single check and exit, no polling loop")
def main(alias, instrument, ema_period, granularity, direction, interval, dry_run, once):
    settings = load_settings()
    client = make_client(settings)
    account = settings.account_for(alias)

    log(
        f"Starting trailing EMA close listener: account={account.alias} ({account.id}) "
        f"instrument={instrument} direction={direction} granularity={granularity} "
        f"ema_period={ema_period} interval={interval}s dry_run={dry_run}"
    )

    if once:
        check_once(client, account.id, instrument, ema_period, granularity, direction, dry_run)
        return

    while True:
        try:
            closed = check_once(
                client, account.id, instrument, ema_period, granularity, direction, dry_run
            )
            if closed:
                log("Position closed - exiting, nothing left to watch.")
                return
        except Exception as exc:  # keep the poller alive across transient API/network errors
            log(f"ERROR during check: {exc!r}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
