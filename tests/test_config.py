from pathlib import Path

from oss_issue_tracker.config import load_config

TOML_CONTENT = """
[github]
username = "octocat"

[scoring]
good_first_issue_labels = ["good first issue", "Beginner-Friendly"]
help_wanted_labels = ["help wanted"]
well_scoped_labels = ["bug"]

[display]
max_issues_per_repo_table = 5
"""


def test_load_config_parses_username(tmp_path: Path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(TOML_CONTENT)

    config = load_config(config_path)

    assert config.username == "octocat"
    assert config.max_issues_per_repo_table == 5


def test_load_config_lowercases_labels(tmp_path: Path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(TOML_CONTENT)

    config = load_config(config_path)

    assert "beginner-friendly" in config.scoring.good_first_issue_labels
    assert "bug" in config.scoring.well_scoped_labels


def test_load_config_defaults_display_when_missing(tmp_path: Path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('[github]\nusername = "someone"\n')

    config = load_config(config_path)

    assert config.max_issues_per_repo_table == 8  # documented default
