import pytest

from fx_utils.watchers import build_command, load_watchers, watcher_label


def test_load_watchers_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_watchers(tmp_path / "does_not_exist.yaml")


def test_load_watchers_empty_raises(tmp_path):
    config = tmp_path / "watchers.yaml"
    config.write_text("watchers: []\n")
    with pytest.raises(ValueError):
        load_watchers(config)


def test_load_watchers_missing_required_field_raises(tmp_path):
    config = tmp_path / "watchers.yaml"
    config.write_text(
        "watchers:\n"
        "  - account: main\n"
        "    instrument: EUR_USD\n"
        "    ema_period: 26\n"
        "    granularity: M1\n"
        "    direction: long\n"
        # interval intentionally omitted
    )
    with pytest.raises(ValueError, match="interval"):
        load_watchers(config)


def test_load_watchers_valid_config(tmp_path):
    config = tmp_path / "watchers.yaml"
    config.write_text(
        "watchers:\n"
        "  - account: main\n"
        "    instrument: EUR_USD\n"
        "    ema_period: 26\n"
        "    granularity: M1\n"
        "    direction: long\n"
        "    interval: 60\n"
    )
    watchers = load_watchers(config)
    assert len(watchers) == 1
    assert watchers[0]["instrument"] == "EUR_USD"


def test_build_command_includes_all_required_flags():
    watcher = {
        "account": "main",
        "instrument": "EUR_USD",
        "ema_period": 26,
        "granularity": "M1",
        "direction": "long",
        "interval": 60,
    }
    cmd = build_command(watcher)
    assert "--account" in cmd and "main" in cmd
    assert "--instrument" in cmd and "EUR_USD" in cmd
    assert "--ema-period" in cmd and "26" in cmd
    assert "--granularity" in cmd and "M1" in cmd
    assert "--direction" in cmd and "long" in cmd
    assert "--interval" in cmd and "60" in cmd
    assert "--dry-run" not in cmd


def test_build_command_adds_dry_run_flag_when_set():
    watcher = {
        "account": "main",
        "instrument": "EUR_USD",
        "ema_period": 26,
        "granularity": "M1",
        "direction": "long",
        "interval": 60,
        "dry_run": True,
    }
    cmd = build_command(watcher)
    assert "--dry-run" in cmd


def test_watcher_label_deduplicates():
    watcher = {"instrument": "EUR_USD", "direction": "long"}
    used = set()
    first = watcher_label(watcher, used)
    used.add(first)
    second = watcher_label(watcher, used)
    assert first == "EUR_USD/long"
    assert second != first
