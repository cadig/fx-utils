# fx-utils

Interactive CLI utilities for trading against the OANDA v20 REST API, built on
[`oandapyV20`](https://github.com/hootnot/oanda-api-v20).

## Setup

```bash
conda env create -f environment.yml
conda activate fx-utils
pip install -e .
```

## Credentials (never committed)

Two files under `config/` hold secrets and are gitignored:

1. `config/credentials.env` — your OANDA Personal Access Token:

   ```bash
   cp config/credentials.example.env config/credentials.env
   ```

   Edit it:

   ```
   OANDA_TOKEN=your-real-pat
   OANDA_ENVIRONMENT=practice   # or "live"
   ```

2. `config/accounts.yaml` — the sub-account id(s) you want to target:

   ```bash
   cp config/accounts.example.yaml config/accounts.yaml
   ```

   Edit it:

   ```yaml
   accounts:
     - id: "101-001-00000000-001"
       alias: main
   default_alias: main
   ```

3. `config/watchers.yaml` — optional, only needed for
   [launching multiple trailing stops at once](#trailing-ema-close-listener):

   ```bash
   cp config/watchers.example.yaml config/watchers.yaml
   ```

`config/credentials.env`, `config/accounts.yaml`, and `config/watchers.yaml` are all in
`.gitignore` — they will never be pushed to GitHub. Only the `*.example.*` versions are
tracked.

## Layout

```
fx_utils/            reusable library
  config.py          loads credentials.env + accounts.yaml
  client.py          builds an oandapyV20 API client
  candles.py         candlestick fetch + last-closed-candle helper
  indicators.py      EMA and other indicator calculations
  positions.py       open-position lookup and close-position calls
  pairs.py           generates the 28 major-currency pairs, resolves each to its
                      actual OANDA instrument name + base/quote orientation
  strength.py        per-pair % change + per-currency cumulative strength scoring
  notify.py          local notification helpers (macOS `say` text-to-speech)
  pair_nicknames.py  instrument -> spoken nickname mapping (euro, cable, yen, ...)
  currency_colors.py fixed ANSI color per major currency
  terminal_viz.py    ANSI horizontal diverging bar chart renderer
  watchers.py         loads/validates config/watchers.yaml, builds subprocess commands
  launcher.py         runs multiple labeled subprocesses concurrently, prefixed output
  cli.py             `fx-utils` general-purpose interactive CLI

scripts/
  trailing_ema_close.py     specific utility: closes a position if the last closed
                             candle crosses its EMA against the given direction
  launch_trailing_stops.py  launches multiple trailing_ema_close.py watchers at once,
                             configured via config/watchers.yaml
  currency_strength_meter.py   specific utility: live terminal chart of cumulative
                                strength (% change, 20x M1 lookback) for all 8 majors

tests/                unit tests for the reusable library (no network calls)
```

## Running

General CLI (ad-hoc checks, reusable across future utilities):

```bash
fx-utils accounts
fx-utils positions --account main
fx-utils candles --instrument EUR_USD --granularity M1 --count 20
```

Trailing EMA close listener. Every flag is required, no defaults — instrument, EMA period,
granularity, direction, and poll interval must all be stated explicitly:

```bash
python scripts/trailing_ema_close.py \
    --account main --instrument EUR_USD --ema-period 26 --granularity M1 \
    --direction long --interval 60
```

Flags:

- `--instrument` — OANDA instrument, e.g. `EUR_USD`, `USD_JPY`
- `--ema-period` — EMA length, e.g. `26`
- `--granularity` — candle granularity, e.g. `M1`, `M5`, `H1`
- `--direction` — `long` or `short`. Determines both which open position is targeted
  (long units vs. short units) and the exit condition: `long` closes when the last closed
  candle's close drops below the EMA, `short` closes when it rises above it.
- `--interval` — poll interval in seconds
- `--dry-run` — log the close decision but never actually send the close order
- `--once` — run a single check and exit (good for testing / cron instead of a long-lived loop)

On an actual close (not `--dry-run`), it speaks "Closed {nickname} trade" via macOS `say`
(`fx_utils/pair_nicknames.py`): euro (EUR_USD), yen (USD_JPY), cable (GBP_USD),
kiwi (NZD_USD), aussie (AUD_USD), cad (USD_CAD), swiss (USD_CHF). Other pairs fall back to
a spoken "EUR/GBP"-style form.

Recommended first run against practice with `--dry-run --once` to confirm credentials and
account access before letting it run live and unattended.

### Launching several trailing stops at once

Hand-typing that whole command per trade gets tedious. Define each trailing stop once in
`config/watchers.yaml` (copy from `config/watchers.example.yaml`) and launch them all
together as subprocesses:

```yaml
watchers:
  - account: main
    instrument: EUR_USD
    ema_period: 26
    granularity: M1
    direction: long
    interval: 60
    dry_run: false

  - account: main
    instrument: USD_JPY
    ema_period: 20
    granularity: M5
    direction: short
    interval: 60
    dry_run: true
```

```bash
python scripts/launch_trailing_stops.py
python scripts/launch_trailing_stops.py --config config/watchers.yaml   # explicit path
```

Every watcher runs as its own `trailing_ema_close.py` subprocess (same no-defaults
validation applies — a watcher missing a required field fails fast at startup, before
anything launches). Output from every watcher is interleaved in one terminal, each line
prefixed with its label (e.g. `[EUR_USD/long]`). Ctrl+C stops the launcher and terminates
every watcher subprocess together.

Currency strength meter (scans all 28 major pairs, redraws a live terminal chart every 60s):

```bash
python scripts/currency_strength_meter.py --account main
```

Useful flags:

- `--interval 60` — poll interval in seconds
- `--once` — run a single scan, print each currency's current score, and exit (no chart)

Each currency's score is the sum of signed % price changes (20-period M1 lookback) across
the 7 pairs it appears in, so e.g. a strong USD_JPY move adds to both USD's and JPY's scores
in the correct direction. Rendered each update as a color-coded horizontal diverging bar
chart (`fx_utils/terminal_viz.py`), sorted strongest to weakest: bars grow outward from a
center zero-axis, so extreme currencies stretch toward the screen edges while middling ones
cluster near the center. Each currency has a fixed color (`fx_utils/currency_colors.py`), and
a ▲/▼/‒ arrow shows the move since the previous update. Ctrl+C to stop.

## Tests

```bash
pytest
```
