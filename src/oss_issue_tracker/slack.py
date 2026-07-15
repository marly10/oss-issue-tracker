"""Posts a run summary to Slack via an incoming webhook.

The webhook URL is a bearer-token-equivalent secret: read ONLY from the
SLACK_WEBHOOK_URL environment variable by the caller, never hardcoded,
never logged. This module never prints the URL itself.
"""

from __future__ import annotations

import logging

import requests

from .models import RepoReport, RunMetrics

logger = logging.getLogger(__name__)

TOP_PICKS_LIMIT = 5
MIN_STARS_FOR_HIGHLIGHT = 4


def build_message(repo_url: str, reports: list[RepoReport], metrics: RunMetrics) -> str:
    total_issues = sum(r.total for r in reports)
    lines = [
        f"*OSS Issue Tracker weekly update* — tracking *{len(reports)}* repos, "
        f"*{total_issues}* open issues. ({metrics.duration_seconds:.1f}s, "
        f"{metrics.api_calls} API calls)"
    ]

    best = []
    for report in reports:
        for scored in report.scored_issues:
            if scored.score >= MIN_STARS_FOR_HIGHLIGHT:
                best.append(scored)
    best.sort(key=lambda si: si.score, reverse=True)
    best = best[:TOP_PICKS_LIMIT]

    if best:
        lines.append("\nTop picks this week:")
        for scored in best:
            issue = scored.issue
            lines.append(f"• {scored.stars} <{issue.html_url}|#{issue.number} {issue.title}>")

    if metrics.errors:
        lines.append(f"\n⚠️ {len(metrics.errors)} error(s) this run — check the Actions log.")

    lines.append(f"\n<{repo_url}|View full tracker>")
    return "\n".join(lines)


def send_notification(webhook_url: str, message: str) -> None:
    resp = requests.post(
        webhook_url, json={"text": message}, headers={"Content-Type": "application/json"}
    )
    resp.raise_for_status()
    logger.info("Slack notification sent (status %s).", resp.status_code)
