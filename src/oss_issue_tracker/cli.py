"""Entry point: `oss-tracker` (see pyproject.toml [project.scripts]).

Design note on logging vs. metrics: runtime logs here stay human-readable
text, because their only consumer is someone reading the Actions log by
eye. The actual observability artifact is metrics/history.jsonl — one
structured JSON object per run, written specifically so it could be
ingested by a real log/metrics pipeline later without changing the format.
That split (ephemeral human logs vs. durable structured records) is
deliberate, not an oversight.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from .chart import build_chart
from .config import load_config
from .github_client import GitHubClient
from .metrics import append_metrics, build_metrics_chart
from .models import RepoReport, RunMetrics, ScoredIssue
from .readme import update_readme
from .scoring import is_relevant, score_issue
from .slack import build_message, send_notification

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("oss_issue_tracker")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_excluded(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        return {
            line.strip() for line in f if line.strip() and not line.strip().startswith("#")
        }


def run(args: argparse.Namespace) -> int:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.error("GH_TOKEN or GITHUB_TOKEN must be set")
        return 1

    started_at = datetime.now(UTC)
    metrics = RunMetrics(started_at=started_at.strftime("%Y-%m-%d %H:%M UTC"))
    t0 = time.monotonic()

    config = load_config(Path(args.config) if args.config else None)
    client = GitHubClient(token, metrics)
    excluded = load_excluded(REPO_ROOT / "excluded_repos.txt")

    logger.info("Fetching forks for %s...", config.username)
    forks = client.get_forks(config.username)
    metrics.forks_found = len(forks)
    metrics.forks_excluded = sum(1 for f in forks if f["full_name"] in excluded)
    logger.info(
        "Found %d forks (%d excluded by excluded_repos.txt)",
        len(forks),
        metrics.forks_excluded,
    )

    reports: list[RepoReport] = []
    for fork in forks:
        fork_name = fork["full_name"]
        if fork_name in excluded:
            logger.info("  %s -> skipped (excluded)", fork_name)
            continue

        try:
            parent = client.get_parent(fork_name)
        except Exception as exc:  # noqa: BLE001 - one bad fork shouldn't kill the run
            msg = f"Failed to resolve parent for {fork_name}: {exc}"
            logger.warning(msg)
            metrics.errors.append(msg)
            continue

        if not parent:
            continue
        logger.info("  %s -> upstream %s", fork_name, parent)

        try:
            issues = client.get_open_issues(parent)
        except Exception as exc:  # noqa: BLE001
            msg = f"Failed to fetch issues for {parent}: {exc}"
            logger.warning(msg)
            metrics.errors.append(msg)
            continue

        relevant = [i for i in issues if is_relevant(i, config.scoring)]
        # Fall back to the most-recently-updated open issues if nothing is
        # beginner-labeled, so quiet repos don't just vanish from the report.
        chosen = relevant if relevant else issues[: config.max_issues_per_repo_table]

        report = RepoReport(upstream=parent)
        report.scored_issues = [
            ScoredIssue(issue=i, score=score_issue(i, config.scoring)) for i in chosen
        ]
        reports.append(report)

    metrics.repos_tracked = len([r for r in reports if r.total > 0])
    metrics.issues_tracked = sum(r.total for r in reports)

    chart_path = REPO_ROOT / "assets" / "issues_by_repo.png"
    chart_generated = build_chart(reports, chart_path)

    metrics_history_path = REPO_ROOT / "metrics" / "history.jsonl"
    metrics_chart_path = REPO_ROOT / "assets" / "metrics_trend.png"

    metrics.duration_seconds = time.monotonic() - t0
    append_metrics(metrics, metrics_history_path)
    metrics_chart_generated = build_metrics_chart(metrics_history_path, metrics_chart_path)

    update_readme(
        REPO_ROOT / "README.md",
        reports,
        config.max_issues_per_repo_table,
        metrics,
        chart_relpath="assets/issues_by_repo.png" if chart_generated else None,
        metrics_chart_relpath="assets/metrics_trend.png" if metrics_chart_generated else None,
    )

    logger.info(
        "Run complete: %d repos, %d issues, %.1fs, %d API calls, %s/%s rate limit remaining",
        metrics.repos_tracked,
        metrics.issues_tracked,
        metrics.duration_seconds,
        metrics.api_calls,
        metrics.rate_limit_remaining,
        metrics.rate_limit_limit,
    )

    if not args.no_slack:
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        if webhook_url:
            default_repo = f"{config.username}/oss-issue-tracker"
            repo_url = f"https://github.com/{os.environ.get('GH_REPO', default_repo)}"
            message = build_message(repo_url, reports, metrics)
            try:
                send_notification(webhook_url, message)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Slack notification failed: %s", exc)
        else:
            logger.info("SLACK_WEBHOOK_URL not set; skipping Slack notification.")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan GitHub forks for approachable open issues.")
    parser.add_argument("--config", help="Path to config.toml (default: repo root)")
    parser.add_argument(
        "--no-slack", action="store_true", help="Skip Slack notification even if configured"
    )
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
