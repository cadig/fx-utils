"""Launches multiple trailing_ema_close.py watchers concurrently as subprocesses, one per
entry in a watchers YAML config - configure every trailing stop once instead of hand-typing
several long CLI invocations each time you want to run them together.

Usage:
    python scripts/launch_trailing_stops.py
    python scripts/launch_trailing_stops.py --config config/watchers.yaml
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fx_utils.config import REPO_ROOT
from fx_utils.launcher import run_labeled_processes
from fx_utils.watchers import build_command, load_watchers, watcher_label

DEFAULT_CONFIG = REPO_ROOT / "config" / "watchers.yaml"


@click.command()
@click.option(
    "--config",
    "config_path",
    default=str(DEFAULT_CONFIG),
    type=click.Path(path_type=Path),
    help="Path to the watchers YAML config",
)
def main(config_path: Path):
    watchers = load_watchers(config_path)

    commands: dict[str, list[str]] = {}
    for watcher in watchers:
        label = watcher_label(watcher, used_labels=set(commands))
        commands[label] = build_command(watcher)

    click.echo(f"Launching {len(commands)} trailing stop watcher(s): {list(commands)}")
    exit_code = run_labeled_processes(commands)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
