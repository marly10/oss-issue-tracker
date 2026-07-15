"""Typed data models. Kept dependency-free (dataclasses only) so the rest
of the codebase never passes raw dicts around."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Issue:
    """A single open GitHub issue (pull requests are filtered out upstream)."""

    number: int
    title: str
    html_url: str
    labels: tuple[str, ...]
    comments: int
    updated_at: str  # ISO 8601, kept as str; only ever sliced for display

    @classmethod
    def from_api(cls, data: dict) -> Issue:
        return cls(
            number=data["number"],
            title=data["title"],
            html_url=data["html_url"],
            labels=tuple(lbl["name"] for lbl in data.get("labels", [])),
            comments=data.get("comments", 0),
            updated_at=data.get("updated_at", ""),
        )

    @property
    def label_set(self) -> frozenset[str]:
        return frozenset(lbl.lower() for lbl in self.labels)


@dataclass
class ScoredIssue:
    issue: Issue
    score: int  # 1-5, see scoring.py for the documented formula

    @property
    def stars(self) -> str:
        return "★" * self.score + "☆" * (5 - self.score)


@dataclass
class RepoReport:
    """All tracked issues for one upstream repo, plus how many were found
    before any display truncation — used for both the table and the chart."""

    upstream: str
    scored_issues: list[ScoredIssue] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.scored_issues)

    def top(self, n: int) -> list[ScoredIssue]:
        return sorted(self.scored_issues, key=lambda si: si.score, reverse=True)[:n]

    def score_counts(self) -> dict[int, int]:
        counts = {s: 0 for s in range(1, 6)}
        for si in self.scored_issues:
            counts[si.score] += 1
        return counts


@dataclass
class RunMetrics:
    """Observability metrics for a single tracker run — the Tier 3 piece."""

    started_at: str
    duration_seconds: float = 0.0
    forks_found: int = 0
    forks_excluded: int = 0
    repos_tracked: int = 0
    issues_tracked: int = 0
    api_calls: int = 0
    rate_limit_remaining: int | None = None
    rate_limit_limit: int | None = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "duration_seconds": round(self.duration_seconds, 2),
            "forks_found": self.forks_found,
            "forks_excluded": self.forks_excluded,
            "repos_tracked": self.repos_tracked,
            "issues_tracked": self.issues_tracked,
            "api_calls": self.api_calls,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_limit": self.rate_limit_limit,
            "errors": self.errors,
        }
