#!/usr/bin/env python3
"""
Scans the configured GitHub user's forks, resolves each fork's upstream repo,
pulls open issues from those upstreams, scores them by approachability, and
writes a markdown table into README.md between the TRACKER markers.
"""

import os
import re
import sys
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")  # no display available on Actions runners
import matplotlib.pyplot as plt
import requests

GITHUB_API = "https://api.github.com"
USERNAME = os.environ.get("GH_USERNAME", "marly10")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    print("ERROR: GH_TOKEN or GITHUB_TOKEN must be set", file=sys.stderr)
    sys.exit(1)

SESSION = requests.Session()
SESSION.headers.update(
    {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
)

# Issues carrying these labels are the ones worth surfacing at all.
# Repos with huge issue trackers (prometheus, kubernetes, etc.) would otherwise
# flood the table with thousands of unrelated issues.
RELEVANT_LABELS = {
    "good first issue",
    "good-first-issue",
    "help wanted",
    "help-wanted",
    "beginner-friendly",
    "contributions welcome",
    "up-for-grabs",
    "easy",
}

MAX_ISSUES_PER_REPO = 8
EXCLUDE_FILE = os.path.join(os.path.dirname(__file__), "..", "excluded_repos.txt")


def load_excluded():
    if not os.path.exists(EXCLUDE_FILE):
        return set()
    with open(EXCLUDE_FILE, encoding="utf-8") as f:
        return {
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        }


def paginated_get(url, params=None):
    params = dict(params or {})
    params.setdefault("per_page", 100)
    results = []
    while url:
        resp = SESSION.get(url, params=params)
        resp.raise_for_status()
        results.extend(resp.json())
        url = resp.links.get("next", {}).get("url")
        params = None  # 'next' url already carries the query string
    return results


def get_forks(username):
    repos = paginated_get(f"{GITHUB_API}/users/{username}/repos", {"type": "owner"})
    return [r for r in repos if r.get("fork")]


def get_parent(fork_full_name):
    resp = SESSION.get(f"{GITHUB_API}/repos/{fork_full_name}")
    resp.raise_for_status()
    data = resp.json()
    parent = data.get("parent")
    return parent["full_name"] if parent else None


def get_open_issues(repo_full_name):
    issues = paginated_get(
        f"{GITHUB_API}/repos/{repo_full_name}/issues",
        {"state": "open", "sort": "updated", "direction": "desc"},
    )
    # The issues endpoint also returns pull requests; exclude those.
    return [i for i in issues if "pull_request" not in i]


def score_issue(issue):
    """
    1-5 approachability score. Documented, not a black box:
      +3  labeled good-first-issue / beginner-friendly
      +2  labeled help-wanted / up-for-grabs / contributions-welcome
      +1  labeled bug or enhancement (well-scoped work, not vague)
      +1  zero comments (nobody's claimed or debated it yet)
      -1  more than 10 comments (likely contested, unclear, or stale debate)
    Clamped to [1, 5].
    """
    labels = {lbl["name"].lower() for lbl in issue.get("labels", [])}
    score = 1

    if labels & {"good first issue", "good-first-issue", "beginner-friendly", "easy"}:
        score += 3
    elif labels & {"help wanted", "help-wanted", "up-for-grabs", "contributions welcome"}:
        score += 2

    if labels & {"bug", "enhancement"}:
        score += 1

    comments = issue.get("comments", 0)
    if comments == 0:
        score += 1
    elif comments > 10:
        score -= 1

    return max(1, min(5, score))


def stars(score):
    return "★" * score + "☆" * (5 - score)


def build_table(repo_issues, chart_generated):
    lines = []
    total_issues = sum(len(v) for v in repo_issues.values())
    lines.append(f"_Tracking **{len(repo_issues)}** upstream repos, **{total_issues}** relevant open issues._\n")

    if chart_generated:
        lines.append("![Open issues by repo and score](assets/issues_by_repo.png)\n")

    for upstream, issues in sorted(repo_issues.items()):
        if not issues:
            continue
        lines.append(f"### [{upstream}](https://github.com/{upstream})\n")
        lines.append("| Score | Issue | Labels | Comments | Updated |")
        lines.append("|---|---|---|---|---|")
        ranked = sorted(issues, key=score_issue, reverse=True)[:MAX_ISSUES_PER_REPO]
        for issue in ranked:
            score = score_issue(issue)
            title = issue["title"].replace("|", "\\|")
            link = f"[#{issue['number']}]({issue['html_url']})"
            labels = ", ".join(lbl["name"] for lbl in issue.get("labels", [])) or "—"
            comments = issue.get("comments", 0)
            updated = issue["updated_at"][:10]
            lines.append(f"| {stars(score)} | {link} {title} | {labels} | {comments} | {updated} |")
        lines.append("")
    return "\n".join(lines)


SCORE_COLORS = {
    1: "#d73a49",  # red   - low approachability
    2: "#e8862c",  # orange
    3: "#dbab09",  # yellow
    4: "#8fc93a",  # light green
    5: "#28a745",  # green - most approachable
}


def build_chart(repo_issues, path="assets/issues_by_repo.png"):
    """
    Horizontal stacked bar chart: one bar per tracked repo, segments colored
    by approachability score (red=hard/unclear -> green=easiest entry point).
    Uses the FULL relevant/fallback issue set per repo (not the 8-row cap
    applied to the table), so the chart reflects true volume of opportunity.
    """
    repos = [r for r, issues in repo_issues.items() if issues]
    if not repos:
        return False

    # Sort repos by total tracked issue count, descending, so the busiest
    # opportunity shows at the top of the chart.
    repos.sort(key=lambda r: len(repo_issues[r]), reverse=True)

    counts_by_score = {s: [] for s in range(1, 6)}
    for repo in repos:
        scores = [score_issue(i) for i in repo_issues[repo]]
        for s in range(1, 6):
            counts_by_score[s].append(scores.count(s))

    fig_height = max(3, 0.45 * len(repos) + 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    left = [0] * len(repos)
    for s in range(1, 6):
        ax.barh(
            repos,
            counts_by_score[s],
            left=left,
            color=SCORE_COLORS[s],
            label=f"{stars(s)} ({s})",
            edgecolor="white",
            linewidth=0.5,
        )
        left = [l + c for l, c in zip(left, counts_by_score[s])]

    ax.set_xlabel("Open issues tracked")
    ax.set_title("Open-source issues to work on, by repo and approachability score")
    ax.invert_yaxis()  # highest-volume repo at top
    ax.legend(title="Score", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return True


def update_readme(table_md, path="README.md"):
    start_marker = "<!-- TRACKER:START -->"
    end_marker = "<!-- TRACKER:END -->"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    block = f"{start_marker}\n\n_Last updated: {timestamp}_\n\n{table_md}\n\n{end_marker}"
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)

    if pattern.search(content):
        content = pattern.sub(block, content)
    else:
        content = content.rstrip() + "\n\n" + block + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    excluded = load_excluded()
    print(f"Fetching forks for {USERNAME}...")
    forks = get_forks(USERNAME)
    print(f"Found {len(forks)} forks ({len(excluded)} excluded by excluded_repos.txt)")

    repo_issues = {}
    for fork in forks:
        fork_name = fork["full_name"]
        if fork_name in excluded:
            print(f"  {fork_name} -> skipped (excluded)")
            continue
        parent = get_parent(fork_name)
        if not parent:
            continue
        print(f"  {fork_name} -> upstream {parent}")
        issues = get_open_issues(parent)
        relevant = [
            i for i in issues
            if {lbl["name"].lower() for lbl in i.get("labels", [])} & RELEVANT_LABELS
        ]
        # Fall back to the most-recently-updated open issues if the repo
        # doesn't label anything as beginner-friendly, so small/quiet repos
        # still show up instead of disappearing from the table.
        repo_issues[parent] = relevant if relevant else issues[:MAX_ISSUES_PER_REPO]

    chart_generated = build_chart(repo_issues)
    print(f"Chart generated: {chart_generated}")

    table_md = build_table(repo_issues, chart_generated)
    update_readme(table_md)
    print("README.md updated.")


if __name__ == "__main__":
    main()
