"""ANSI-colored horizontal diverging bar chart for a signed score per category.

Bars grow outward from a shared center zero-axis, so categories with extreme scores
stretch toward the screen edges while near-zero scores cluster tightly around the
center - the bar length directly encodes the score's magnitude and sign.
"""
from __future__ import annotations

RESET = "\033[0m"


def diverging_bar_chart(
    scores: dict[str, float],
    colors: dict[str, str],
    width: int = 80,
    trends: dict[str, float] | None = None,
) -> str:
    """Render `scores` as a horizontal diverging bar chart, sorted strongest to weakest.

    `colors` maps each key to an ANSI color escape code. `trends`, if given, maps each
    key to its change since the previous render and adds a ▲/▼/‒ indicator.
    """
    if not scores:
        return ""

    label_width = max(len(k) for k in scores) + 1
    value_width = 9  # "+123.456"
    half_width = max(4, (width - label_width - value_width - 3) // 2)
    max_abs = max((abs(v) for v in scores.values()), default=0.0) or 1.0

    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    lines = []
    for currency, score in ordered:
        color = colors.get(currency, "")
        filled = min(half_width, round(abs(score) / max_abs * half_width))

        if score >= 0:
            neg_seg = " " * half_width
            pos_seg = f"{color}{'█' * filled}{RESET}" + " " * (half_width - filled)
        else:
            neg_seg = " " * (half_width - filled) + f"{color}{'█' * filled}{RESET}"
            pos_seg = " " * half_width

        arrow = ""
        if trends is not None:
            delta = trends.get(currency, 0.0)
            if delta > 1e-9:
                arrow = " \033[32m▲\033[0m"
            elif delta < -1e-9:
                arrow = " \033[31m▼\033[0m"
            else:
                arrow = " ‒"

        lines.append(
            f"{color}{currency:<{label_width}}{RESET}{neg_seg}│{pos_seg} "
            f"{score:+.3f}{arrow}"
        )

    axis_label = (
        f"{'':<{label_width}}{f'-{max_abs:.2f}':<{half_width}}0{f'+{max_abs:.2f}':>{half_width}}"
    )
    lines.append(axis_label)
    return "\n".join(lines)
