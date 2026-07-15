# Contributing

There's a certain irony in a tool built to help people contribute to open source not having a clean contributor path itself, so here's the actual process.

## Setup

```bash
git clone https://github.com/<you>/oss-issue-tracker.git
cd oss-issue-tracker
python3.11 -m venv .venv   # 3.11+ required (uses stdlib tomllib)
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running locally

```bash
GH_TOKEN=$(gh auth token) oss-tracker --no-slack
```

`GH_TOKEN` needs no special scopes beyond default read access to public repos. `--no-slack` skips the notification step, which is what you want while developing.

## Before opening a PR

```bash
ruff check .      # lint
pytest -v         # tests
```

Both run in CI on every PR (`.github/workflows/ci.yml`), across Python 3.11 and 3.12 — a PR won't merge if either fails, so it's faster to catch it locally first.

## What's a good PR here

- **Scoring changes**: `score_issue()` in `src/oss_issue_tracker/scoring.py` is a pure function with a documented formula in its docstring — if you change the formula, update the docstring and the tests in `tests/test_scoring.py` in the same PR.
- **New notification backends**: `slack.py` is intentionally small and self-contained (`build_message` / `send_notification`). A Discord or email backend should follow the same shape — build the message as pure data, then a thin send function — rather than growing `cli.py`'s orchestration logic.
- **Config changes**: new config fields go in `config.toml` (with a sensible default in `config.py`'s loader) rather than as new environment variables, so the project stays fork-and-edit friendly for people who aren't setting up CI secrets.

## Reporting a bug

Open an issue with the log output from the failing run (Actions logs are public on this repo) and which repo/fork triggered it, if relevant.
