import re

from fx_utils.terminal_viz import diverging_bar_chart

ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def test_sorted_strongest_to_weakest():
    scores = {"EUR": -1.0, "USD": 2.0, "GBP": 0.5}
    colors = {"EUR": "", "USD": "", "GBP": ""}
    out = strip_ansi(diverging_bar_chart(scores, colors, width=60))
    lines = out.splitlines()
    order = [line.split()[0] for line in lines[:-1]]
    assert order == ["USD", "GBP", "EUR"]


def test_extreme_scores_produce_longer_bars_than_middling_scores():
    scores = {"USD": 5.0, "EUR": 0.1, "JPY": -5.0}
    colors = {"USD": "", "EUR": "", "JPY": ""}
    out = strip_ansi(diverging_bar_chart(scores, colors, width=60))
    lines = {line.split()[0]: line for line in out.splitlines()[:-1]}
    usd_bar_len = lines["USD"].count("█")
    eur_bar_len = lines["EUR"].count("█")
    jpy_bar_len = lines["JPY"].count("█")
    assert usd_bar_len > eur_bar_len
    assert jpy_bar_len > eur_bar_len


def test_empty_scores_returns_empty_string():
    assert diverging_bar_chart({}, {}) == ""


def test_zero_score_has_no_bar():
    scores = {"EUR": 0.0, "USD": 3.0}
    colors = {"EUR": "", "USD": ""}
    out = strip_ansi(diverging_bar_chart(scores, colors, width=60))
    lines = {line.split()[0]: line for line in out.splitlines()[:-1]}
    assert lines["EUR"].count("█") == 0
