"""Thin GitHub REST API client with retry/backoff on transient failures and
rate-limit tracking fed into RunMetrics (see metrics.py)."""

from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import Issue, RunMetrics

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"

# Retries on connection errors and 5xx/429 responses. GitHub's primary rate
# limit (403 with a specific message) is handled separately in `_get`,
# since it needs a longer, header-driven backoff than exponential retry.
_RETRY = Retry(
    total=4,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)


class GitHubClient:
    def __init__(self, token: str, metrics: RunMetrics):
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        adapter = HTTPAdapter(max_retries=_RETRY)
        self._session.mount("https://", adapter)
        self._metrics = metrics

    def _get(self, url: str, params: dict | None = None) -> requests.Response:
        resp = self._session.get(url, params=params)
        self._metrics.api_calls += 1

        remaining = resp.headers.get("X-RateLimit-Remaining")
        limit = resp.headers.get("X-RateLimit-Limit")
        if remaining is not None:
            self._metrics.rate_limit_remaining = int(remaining)
        if limit is not None:
            self._metrics.rate_limit_limit = int(limit)

        if resp.status_code == 403 and remaining == "0":
            msg = "GitHub primary rate limit exhausted mid-run"
            logger.error(msg)
            self._metrics.errors.append(msg)
            resp.raise_for_status()

        resp.raise_for_status()
        return resp

    def _paginated_get(self, url: str, params: dict | None = None) -> list[dict]:
        params = dict(params or {})
        params.setdefault("per_page", 100)
        results: list[dict] = []
        next_url: str | None = url
        while next_url:
            resp = self._get(next_url, params)
            results.extend(resp.json())
            next_url = resp.links.get("next", {}).get("url")
            params = None  # 'next' URL already carries the full query string
        return results

    def get_forks(self, username: str) -> list[dict]:
        repos = self._paginated_get(
            f"{GITHUB_API}/users/{username}/repos", {"type": "owner"}
        )
        return [r for r in repos if r.get("fork")]

    def get_parent(self, fork_full_name: str) -> str | None:
        resp = self._get(f"{GITHUB_API}/repos/{fork_full_name}")
        parent = resp.json().get("parent")
        return parent["full_name"] if parent else None

    def get_open_issues(self, repo_full_name: str) -> list[Issue]:
        raw = self._paginated_get(
            f"{GITHUB_API}/repos/{repo_full_name}/issues",
            {"state": "open", "sort": "updated", "direction": "desc"},
        )
        # The issues endpoint also returns pull requests; exclude those.
        return [Issue.from_api(i) for i in raw if "pull_request" not in i]
