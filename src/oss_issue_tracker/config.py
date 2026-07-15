"""Loads config.toml. Uses stdlib tomllib (Python 3.11+) — no extra
dependency needed just to parse config."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.toml"


@dataclass
class ScoringConfig:
    good_first_issue_labels: frozenset[str]
    help_wanted_labels: frozenset[str]
    well_scoped_labels: frozenset[str]


@dataclass
class Config:
    username: str
    scoring: ScoringConfig
    max_issues_per_repo_table: int


def load_config(path: Path | None = None) -> Config:
    path = path or DEFAULT_CONFIG_PATH
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    scoring_raw = raw.get("scoring", {})
    scoring = ScoringConfig(
        good_first_issue_labels=frozenset(
            s.lower() for s in scoring_raw.get("good_first_issue_labels", [])
        ),
        help_wanted_labels=frozenset(
            s.lower() for s in scoring_raw.get("help_wanted_labels", [])
        ),
        well_scoped_labels=frozenset(
            s.lower() for s in scoring_raw.get("well_scoped_labels", [])
        ),
    )

    return Config(
        username=raw["github"]["username"],
        scoring=scoring,
        max_issues_per_repo_table=raw.get("display", {}).get(
            "max_issues_per_repo_table", 8
        ),
    )
