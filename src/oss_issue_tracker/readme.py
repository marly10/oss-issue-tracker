"""Renders the tracked-issues markdown block and writes it into README.md
between marker comments. Writes atomically (temp file + rename) so a crash
mid-write can never leave a corrupted README committed."""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path

from .models import RepoReport, RunMetrics

logger = logging.getLogger(__name__)

TRACKER_START = "<!-- TRACKER:START -->"
TRACKER_END = "<!-- TRACKER:END -->"
METRICS_START = "<!-- METRICS:START -->"
METRICS_END = "<!-- METRICS:END -->"


def render_table(
    reports: list[RepoReport], max_per_repo: int, chart_relpath: str | None
) -> str:
    lines: list[str] = []
    total_issues = sum(r.total for r in reports)
    lines.append(
        f"_Tracking **{len(reports)}** upstream repos, "
        f"**{total_issues}** relevant open issues._\n"
    )

    if chart_relpath:
        lines.append(f"![Open issues by repo and score]({chart_relpath})\n")

    for report in sorted(reports, key=lambda r: r.upstream):
        if report.total == 0:
            continue
        lines.append(f"### [{report.upstream}](https://github.com/{report.upstream})\n")
        lines.append("| Score | Issue | Labels | Comments | Updated |")
        lines.append("|---|---|---|---|---|")
        for scored in report.top(max_per_repo):
            issue = scored.issue
            title = issue.title.replace("|", "\\|")
            link = f"[#{issue.number}]({issue.html_url})"
            labels = ", ".join(issue.labels) or "—"
            updated = issue.updated_at[:10]
            lines.append(
                f"| {scored.stars} | {link} {title} | {labels} | "
                f"{issue.comments} | {updated} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_metrics_block(metrics: RunMetrics, chart_relpath: str | None) -> str:
    lines = [
        f"_Last run: {metrics.started_at}, took **{metrics.duration_seconds:.1f}s**, "
        f"**{metrics.api_calls}** GitHub API calls, "
        f"**{metrics.rate_limit_remaining}/{metrics.rate_limit_limit}** rate limit remaining._"
    ]
    if metrics.errors:
        lines.append(f"\n⚠️ {len(metrics.errors)} error(s) this run: " + "; ".join(metrics.errors))
    if chart_relpath:
        lines.append(f"\n![Scrape metrics trend]({chart_relpath})")
    return "\n".join(lines)


def _replace_block(content: str, start: str, end: str, body: str) -> str:
    block = f"{start}\n\n{body}\n\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(content):
        return pattern.sub(lambda _: block, content)
    return content.rstrip() + "\n\n" + block + "\n"


def update_readme(
    readme_path: Path,
    reports: list[RepoReport],
    max_per_repo: int,
    metrics: RunMetrics,
    chart_relpath: str | None = None,
    metrics_chart_relpath: str | None = None,
) -> None:
    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    table_body = f"_Last updated: {timestamp}_\n\n" + render_table(
        reports, max_per_repo, chart_relpath
    )
    content = _replace_block(content, TRACKER_START, TRACKER_END, table_body)

    metrics_body = render_metrics_block(metrics, metrics_chart_relpath)
    content = _replace_block(content, METRICS_START, METRICS_END, metrics_body)

    # Atomic write: write to a temp file in the same directory, then rename.
    # A crash mid-write leaves the temp file, never a truncated README.md.
    tmp_path = readme_path.with_suffix(".md.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp_path, readme_path)
    logger.info("README.md updated atomically.")
