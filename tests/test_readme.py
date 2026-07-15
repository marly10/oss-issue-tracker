from pathlib import Path

from oss_issue_tracker.models import Issue, RepoReport, RunMetrics, ScoredIssue
from oss_issue_tracker.readme import update_readme


def make_report() -> RepoReport:
    issue = Issue(
        number=7,
        title="Do the thing",
        html_url="https://github.com/x/y/issues/7",
        labels=("good first issue",),
        comments=0,
        updated_at="2026-01-01T00:00:00Z",
    )
    report = RepoReport(upstream="x/y")
    report.scored_issues = [ScoredIssue(issue=issue, score=5)]
    return report


def make_metrics() -> RunMetrics:
    return RunMetrics(
        started_at="2026-01-01 00:00 UTC",
        duration_seconds=1.23,
        api_calls=10,
        rate_limit_remaining=4990,
        rate_limit_limit=5000,
    )


def test_update_readme_inserts_markers_when_absent(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n\nSome intro text.\n")

    update_readme(readme, [make_report()], max_per_repo=8, metrics=make_metrics())

    content = readme.read_text()
    assert "<!-- TRACKER:START -->" in content
    assert "<!-- TRACKER:END -->" in content
    assert "<!-- METRICS:START -->" in content
    assert "x/y" in content
    assert "#7" in content
    assert "Some intro text." in content  # existing content preserved


def test_update_readme_replaces_existing_block_not_duplicates(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text(
        "# Title\n\n<!-- TRACKER:START -->\n\nold content\n\n<!-- TRACKER:END -->\n"
    )

    update_readme(readme, [make_report()], max_per_repo=8, metrics=make_metrics())

    content = readme.read_text()
    assert content.count("<!-- TRACKER:START -->") == 1
    assert "old content" not in content
    assert "x/y" in content


def test_update_readme_is_idempotent_on_repeated_runs(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n")

    update_readme(readme, [make_report()], max_per_repo=8, metrics=make_metrics())
    first = readme.read_text()
    update_readme(readme, [make_report()], max_per_repo=8, metrics=make_metrics())
    second = readme.read_text()

    # Content should differ only in the timestamp line, structurally stable.
    assert first.count("<!-- TRACKER:START -->") == second.count("<!-- TRACKER:START -->") == 1


def test_update_readme_leaves_no_tmp_file_behind(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n")

    update_readme(readme, [make_report()], max_per_repo=8, metrics=make_metrics())

    assert not (tmp_path / "README.md.tmp").exists()


def test_update_readme_respects_max_per_repo_cap(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n")

    report = RepoReport(upstream="x/y")
    report.scored_issues = [
        ScoredIssue(
            issue=Issue(
                number=i,
                title=f"issue {i}",
                html_url=f"https://github.com/x/y/issues/{i}",
                labels=(),
                comments=0,
                updated_at="2026-01-01T00:00:00Z",
            ),
            score=5,
        )
        for i in range(20)
    ]

    update_readme(readme, [report], max_per_repo=3, metrics=make_metrics())
    content = readme.read_text()
    assert content.count("| ★★★★★ |") == 3
