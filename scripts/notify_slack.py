#!/usr/bin/env python3
"""
Posts a short summary of the latest tracker run to Slack via an incoming
webhook. The webhook URL is a bearer-token-equivalent secret: it is read
ONLY from the SLACK_WEBHOOK_URL environment variable, never hardcoded,
never logged, and never written to any file in this repo.
"""

import json
import os
import re
import sys

import requests

REPO = os.environ.get("GH_REPO", "marly10/oss-issue-tracker")
WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

if not WEBHOOK_URL:
    print("ERROR: SLACK_WEBHOOK_URL env var not set", file=sys.stderr)
    sys.exit(1)


def extract_summary(readme_text):
    match = re.search(r"Tracking \*\*(\d+)\*\* upstream repos, \*\*(\d+)\*\* relevant open issues", readme_text)
    repos, issues = (match.group(1), match.group(2)) if match else ("?", "?")

    # Pull every markdown table row, keep the ones with a 5-star or 4-star score.
    rows = re.findall(r"\| (★+☆*) \| \[#(\d+)\]\((https://[^\)]+)\) ([^\|]+) \|", readme_text)
    best = [r for r in rows if r[0].count("★") >= 4][:5]
    return repos, issues, best


def build_message(repos, issues, best):
    lines = [f"*OSS Issue Tracker weekly update* — tracking *{repos}* repos, *{issues}* open issues."]
    if best:
        lines.append("\nTop picks this week:")
        for stars, number, url, title in best:
            lines.append(f"• {stars} <{url}|#{number} {title.strip()}>")
    lines.append(f"\n<https://github.com/{REPO}|View full tracker>")
    return "\n".join(lines)


def main():
    with open("README.md", encoding="utf-8") as f:
        readme_text = f.read()

    repos, issues, best = extract_summary(readme_text)
    text = build_message(repos, issues, best)

    resp = requests.post(WEBHOOK_URL, data=json.dumps({"text": text}), headers={"Content-Type": "application/json"})
    resp.raise_for_status()
    print(f"Slack notification sent (status {resp.status_code}).")


if __name__ == "__main__":
    main()
