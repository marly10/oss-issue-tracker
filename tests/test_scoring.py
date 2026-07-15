from oss_issue_tracker.config import ScoringConfig
from oss_issue_tracker.models import Issue
from oss_issue_tracker.scoring import is_relevant, score_issue

SCORING = ScoringConfig(
    good_first_issue_labels=frozenset({"good first issue", "beginner-friendly"}),
    help_wanted_labels=frozenset({"help wanted", "up-for-grabs"}),
    well_scoped_labels=frozenset({"bug", "enhancement"}),
)


def make_issue(labels=(), comments=0) -> Issue:
    return Issue(
        number=1,
        title="test issue",
        html_url="https://github.com/x/y/issues/1",
        labels=tuple(labels),
        comments=comments,
        updated_at="2026-01-01T00:00:00Z",
    )


def test_baseline_score_is_minimum():
    issue = make_issue(labels=(), comments=3)
    assert score_issue(issue, SCORING) == 1


def test_good_first_issue_label_scores_high():
    issue = make_issue(labels=("good first issue",), comments=3)
    # +3 for label, no comment bonus/penalty (3 comments) -> 1 + 3 = 4
    assert score_issue(issue, SCORING) == 4


def test_good_first_issue_plus_zero_comments_hits_max():
    issue = make_issue(labels=("good first issue",), comments=0)
    # 1 + 3 (label) + 1 (zero comments) = 5
    assert score_issue(issue, SCORING) == 5


def test_help_wanted_scores_lower_than_good_first_issue():
    good_first = make_issue(labels=("good first issue",), comments=5)
    help_wanted = make_issue(labels=("help wanted",), comments=5)
    assert score_issue(good_first, SCORING) > score_issue(help_wanted, SCORING)


def test_good_first_issue_and_help_wanted_together_does_not_double_count():
    # elif in the implementation: only the higher-value label should apply
    both = make_issue(labels=("good first issue", "help wanted"), comments=5)
    only_good_first = make_issue(labels=("good first issue",), comments=5)
    assert score_issue(both, SCORING) == score_issue(only_good_first, SCORING)


def test_bug_label_adds_one():
    plain = make_issue(labels=(), comments=3)
    bug = make_issue(labels=("bug",), comments=3)
    assert score_issue(bug, SCORING) == score_issue(plain, SCORING) + 1


def test_many_comments_penalizes_score():
    quiet = make_issue(labels=("good first issue",), comments=3)
    noisy = make_issue(labels=("good first issue",), comments=50)
    assert score_issue(noisy, SCORING) == score_issue(quiet, SCORING) - 1


def test_score_never_exceeds_five():
    issue = make_issue(labels=("good first issue", "bug"), comments=0)
    assert score_issue(issue, SCORING) == 5


def test_score_never_below_one():
    issue = make_issue(labels=(), comments=100)
    assert score_issue(issue, SCORING) == 1


def test_score_is_case_insensitive_on_labels():
    issue = make_issue(labels=("Good First Issue",), comments=0)
    assert score_issue(issue, SCORING) == 5


def test_is_relevant_true_for_labeled_issue():
    issue = make_issue(labels=("help wanted",))
    assert is_relevant(issue, SCORING) is True


def test_is_relevant_false_for_unlabeled_issue():
    issue = make_issue(labels=("bug",))
    assert is_relevant(issue, SCORING) is False
