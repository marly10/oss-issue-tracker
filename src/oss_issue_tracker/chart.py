"""Renders the stacked bar chart: open issues per repo, colored by score."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display available on CI runners
import matplotlib.pyplot as plt

from .models import RepoReport

logger = logging.getLogger(__name__)

SCORE_COLORS = {
    1: "#d73a49",  # red    - low approachability
    2: "#e8862c",  # orange
    3: "#dbab09",  # yellow
    4: "#8fc93a",  # light green
    5: "#28a745",  # green  - most approachable
}


def build_chart(reports: list[RepoReport], path: Path) -> bool:
    """Horizontal stacked bar chart, one bar per repo with tracked issues,
    sorted by total volume descending. Returns False (no-op) if nothing to
    plot, so callers can skip embedding a stale/empty image."""
    reports = [r for r in reports if r.total > 0]
    if not reports:
        logger.info("No issues to chart; skipping chart generation.")
        return False

    reports.sort(key=lambda r: r.total, reverse=True)

    fig_height = max(3, 0.45 * len(reports) + 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    left = [0] * len(reports)
    repo_names = [r.upstream for r in reports]
    for s in range(1, 6):
        counts = [r.score_counts()[s] for r in reports]
        ax.barh(
            repo_names,
            counts,
            left=left,
            color=SCORE_COLORS[s],
            label=f"{'★' * s}{'☆' * (5 - s)} ({s})",
            edgecolor="white",
            linewidth=0.5,
        )
        left = [total + c for total, c in zip(left, counts, strict=True)]

    ax.set_xlabel("Open issues tracked")
    ax.set_title("Open-source issues to work on, by repo and approachability score")
    ax.invert_yaxis()
    ax.legend(title="Score", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    os.makedirs(path.parent, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info("Chart written to %s", path)
    return True
