"""Approachability scoring. Pure function, no I/O — this is what the test
suite exercises directly rather than mocking the GitHub API."""

from __future__ import annotations

from .config import ScoringConfig
from .models import Issue

MIN_SCORE = 1
MAX_SCORE = 5


def score_issue(issue: Issue, scoring: ScoringConfig) -> int:
    """
    1-5 approachability score:
      +3  labeled good-first-issue / beginner-friendly
      +2  labeled help-wanted / up-for-grabs / contributions-welcome
      +1  labeled bug or enhancement (well-scoped work, not vague)
      +1  zero comments (nobody's claimed or debated it yet)
      -1  more than 10 comments (likely contested, unclear, or stale debate)
    Clamped to [1, 5].
    """
    labels = issue.label_set
    score = MIN_SCORE

    if labels & scoring.good_first_issue_labels:
        score += 3
    elif labels & scoring.help_wanted_labels:
        score += 2

    if labels & scoring.well_scoped_labels:
        score += 1

    if issue.comments == 0:
        score += 1
    elif issue.comments > 10:
        score -= 1

    return max(MIN_SCORE, min(MAX_SCORE, score))


def is_relevant(issue: Issue, scoring: ScoringConfig) -> bool:
    """Whether an issue carries any beginner-signaling label at all."""
    return bool(
        issue.label_set & (scoring.good_first_issue_labels | scoring.help_wanted_labels)
    )
