from oss_issue_tracker.models import Issue, RepoReport, ScoredIssue


def make_issue(number=1, comments=0) -> Issue:
    return Issue(
        number=number,
        title=f"issue {number}",
        html_url=f"https://github.com/x/y/issues/{number}",
        labels=(),
        comments=comments,
        updated_at="2026-01-01T00:00:00Z",
    )


def test_issue_from_api_filters_and_maps_fields():
    data = {
        "number": 42,
        "title": "Fix the thing",
        "html_url": "https://github.com/x/y/issues/42",
        "labels": [{"name": "bug"}, {"name": "help wanted"}],
        "comments": 3,
        "updated_at": "2026-05-01T12:00:00Z",
    }
    issue = Issue.from_api(data)
    assert issue.number == 42
    assert issue.labels == ("bug", "help wanted")
    assert issue.label_set == frozenset({"bug", "help wanted"})


def test_scored_issue_stars_render_correctly():
    scored = ScoredIssue(issue=make_issue(), score=3)
    assert scored.stars == "★★★☆☆"


def test_repo_report_top_n_sorts_by_score_descending():
    report = RepoReport(upstream="x/y")
    report.scored_issues = [
        ScoredIssue(issue=make_issue(1), score=2),
        ScoredIssue(issue=make_issue(2), score=5),
        ScoredIssue(issue=make_issue(3), score=3),
    ]
    top = report.top(2)
    assert [si.issue.number for si in top] == [2, 3]


def test_repo_report_score_counts_buckets_correctly():
    report = RepoReport(upstream="x/y")
    report.scored_issues = [
        ScoredIssue(issue=make_issue(1), score=5),
        ScoredIssue(issue=make_issue(2), score=5),
        ScoredIssue(issue=make_issue(3), score=1),
    ]
    counts = report.score_counts()
    assert counts[5] == 2
    assert counts[1] == 1
    assert counts[2] == 0


def test_repo_report_total_matches_issue_count():
    report = RepoReport(upstream="x/y")
    report.scored_issues = [ScoredIssue(issue=make_issue(i), score=1) for i in range(4)]
    assert report.total == 4
