"""Loads and validates trailing-stop watcher definitions from config/watchers.yaml, and
builds the corresponding `trailing_ema_close.py` subprocess command for each one.

Every watcher must state its own account, instrument, ema_period, granularity, direction,
and interval explicitly - matching trailing_ema_close.py's own no-defaults requirement,
just defined once in config instead of retyped on the command line each time.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from fx_utils.config import REPO_ROOT

WATCHER_SCRIPT = REPO_ROOT / "scripts" / "trailing_ema_close.py"

REQUIRED_FIELDS = ["account", "instrument", "ema_period", "granularity", "direction", "interval"]


def load_watchers(config_path: Path) -> list[dict]:
    if not config_path.exists():
        raise FileNotFoundError(
            f"Missing {config_path}. Copy config/watchers.example.yaml to "
            f"{config_path.name} and define your watchers."
        )
    with config_path.open() as f:
        raw = yaml.safe_load(f) or {}

    watchers = raw.get("watchers", [])
    if not watchers:
        raise ValueError(f"No watchers defined in {config_path}")

    for i, watcher in enumerate(watchers):
        missing = [field for field in REQUIRED_FIELDS if field not in watcher]
        if missing:
            raise ValueError(f"watchers[{i}] is missing required field(s): {missing}")

    return watchers


def build_command(watcher: dict) -> list[str]:
    cmd = [
        sys.executable,
        "-u",  # unbuffered stdout/stderr so the launcher's live-tailed output isn't delayed
        str(WATCHER_SCRIPT),
        "--account", str(watcher["account"]),
        "--instrument", str(watcher["instrument"]),
        "--ema-period", str(watcher["ema_period"]),
        "--granularity", str(watcher["granularity"]),
        "--direction", str(watcher["direction"]),
        "--interval", str(watcher["interval"]),
    ]
    if watcher.get("dry_run"):
        cmd.append("--dry-run")
    return cmd


def watcher_label(watcher: dict, used_labels: set[str]) -> str:
    """A short, unique display label for a watcher, e.g. "EUR_USD/long"."""
    base = f"{watcher['instrument']}/{watcher['direction']}"
    label = base
    suffix = 2
    while label in used_labels:
        label = f"{base}#{suffix}"
        suffix += 1
    return label
