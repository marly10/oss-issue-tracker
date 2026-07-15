"""Persists run metrics to metrics/history.jsonl (append-only, one JSON
object per run) and renders a trend chart from that history.

This exists because a tool that scrapes a rate-limited external API in a
scheduled job should be observable: how long did it take, how many API
calls did it burn, how close did it get to the rate limit, did anything
error. Same instinct as instrumenting a production pipeline, applied here.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .models import RunMetrics

logger = logging.getLogger(__name__)

MAX_HISTORY_POINTS_PLOTTED = 20


def append_metrics(metrics: RunMetrics, history_path: Path) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(metrics.to_dict()) + "\n")
    logger.info("Appended run metrics to %s", history_path)


def load_history(history_path: Path) -> list[dict]:
    if not history_path.exists():
        return []
    with open(history_path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_metrics_chart(history_path: Path, out_path: Path) -> bool:
    history = load_history(history_path)[-MAX_HISTORY_POINTS_PLOTTED:]
    if len(history) < 2:
        logger.info("Not enough history yet to plot a metrics trend.")
        return False

    runs = list(range(1, len(history) + 1))
    durations = [h["duration_seconds"] for h in history]
    api_calls = [h["api_calls"] for h in history]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5))

    ax1.plot(runs, durations, marker="o", color="#2b6cb0")
    ax1.set_title("Scrape duration per run (s)")
    ax1.set_xlabel("Run #")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    ax2.plot(runs, api_calls, marker="o", color="#805ad5")
    ax2.set_title("GitHub API calls per run")
    ax2.set_xlabel("Run #")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info("Metrics trend chart written to %s", out_path)
    return True
