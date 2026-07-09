"""Fixed ANSI color assignment per major currency, so a currency is always the same
color across every render and every script that uses it."""
from __future__ import annotations

CURRENCY_COLORS = {
    "EUR": "\033[36m",  # cyan
    "USD": "\033[31m",  # red
    "GBP": "\033[35m",  # magenta
    "JPY": "\033[33m",  # yellow
    "AUD": "\033[32m",  # green
    "NZD": "\033[34m",  # blue
    "CAD": "\033[96m",  # bright cyan
    "CHF": "\033[97m",  # bright white
}
