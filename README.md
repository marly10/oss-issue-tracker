# oss-issue-tracker

[![CI](https://github.com/marly10/oss-issue-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/marly10/oss-issue-tracker/actions/workflows/ci.yml)
[![Weekly Issue Scrape](https://github.com/marly10/oss-issue-tracker/actions/workflows/weekly-scrape.yml/badge.svg)](https://github.com/marly10/oss-issue-tracker/actions/workflows/weekly-scrape.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)

Dynamic contribution radar: scans every repo I've forked, resolves each one's real upstream, pulls its open issues, and scores them by how approachable they are — so I can decide what to work on next without manually digging through issue trackers. Refreshed every Monday by GitHub Actions, with a Slack summary and a chart, not just a wall of markdown.

## Why I built this

I wanted to start contributing to open source in the projects I actually use at work (OpenTelemetry/Bindplane, Grafana's BigQuery datasource, the GCP Terraform provider), but the actual bottleneck wasn't motivation — it was that "go look for a good issue" is a task I'd always defer indefinitely because it required opening ten tabs and skimming label lists. This tool turns that into a five-minute Monday-morning read: one Slack message, one chart, done.

It's also, deliberately, not just a personal script. Anyone can fork this repo, change one line in `config.toml`, and get the same weekly radar pointed at their own GitHub account.

## How it works

```
your forks (GitHub API)
      │
      ▼
resolve each fork's real upstream repo
      │
      ▼
pull open issues from the upstream (retries + rate-limit tracking)
      │
      ▼
score each issue 1-5★ (scoring.py — pure function, unit tested)
      │
      ├──► chart.py    → assets/issues_by_repo.png (stacked bar, by score)
      ├──► metrics.py  → metrics/history.jsonl (structured run telemetry)
      ├──► readme.py   → README.md (atomic write — never a half-written file)
      └──► slack.py    → weekly summary + top picks
```

Every box above is a separate, independently tested module under `src/oss_issue_tracker/` — see [`cli.py`](src/oss_issue_tracker/cli.py) for the orchestration.

## Using this for your own account

1. Fork this repo.
2. Edit `config.toml` — change `username` under `[github]` to yours.
3. Edit `excluded_repos.txt` to skip any forks that aren't real contribution targets (course projects, toy repos, etc).
4. Add a `SLACK_WEBHOOK_URL` repo secret if you want Slack notifications (Settings → Secrets and variables → Actions). Skip this and it just won't notify — everything else still works.
5. The weekly workflow runs automatically. Trigger it manually anytime from the Actions tab if you don't want to wait for Monday.

No code changes needed for a basic fork — that's the point.

## How scoring works

Each issue gets a 1-5★ approachability score, computed in [`scoring.py`](src/oss_issue_tracker/scoring.py) (formula is documented in the function's own docstring, and every branch of it is covered by [`tests/test_scoring.py`](tests/test_scoring.py)):

- `good first issue` / `beginner-friendly` label → +3
- `help wanted` / `up-for-grabs` label → +2
- `bug` or `enhancement` label → +1
- Zero comments (nobody's claimed or debated it) → +1
- More than 10 comments (likely contested or stale) → -1

Repos with no labeled beginner-friendly issues fall back to showing their most recently updated open issues, so quiet repos don't just disappear from the table. Label sets are configurable per-fork in `config.toml`, not hardcoded.

## Engineering notes

A few decisions worth explaining rather than leaving implicit:

- **`tomllib` over a YAML/config dependency.** Config parsing needed exactly one feature (typed key-value config), and Python 3.11+ ships that in the standard library. Pulling in PyYAML for this would be a dependency for a problem already solved.
- **Atomic README writes.** `readme.py` writes to a temp file and `os.replace()`s it into place. If the process dies mid-write (OOM-killed runner, network blip during a later step), the committed README is never left truncated — worst case, the update simply didn't happen this week.
- **Retries live in the HTTP adapter, not sprinkled through business logic.** `github_client.py` configures `urllib3`'s `Retry` once, at the session level, so `chart.py`/`readme.py`/`scoring.py` never need to know the network is unreliable. GitHub's primary rate limit (a 403 with `X-RateLimit-Remaining: 0`) is handled as a distinct case from generic 5xx/429s, since it needs a different response than "retry with backoff" — the run should stop and report it, not hammer an exhausted quota.
- **Structured metrics, human-readable logs — deliberately not the same thing.** Console output during a run is plain text, because its only consumer is a person reading the Actions log. `metrics/history.jsonl` is one structured JSON object per run instead, specifically so it could be ingested by a real metrics pipeline later without a format change. Conflating "what a human wants to read right now" with "what a machine should be able to query later" is a common source of bad logging; this repo keeps them separate on purpose.
- **`excluded_repos.txt` instead of auto-filtering "real" OSS repos.** I could try to heuristically guess which forks are course assignments vs. real contribution targets, but that's a judgment call that belongs to whoever's running the tool, not a heuristic. A plain-text opt-out file keeps that decision explicit and easy to audit.

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor workflow — including, fittingly, guidance on what makes a good PR to a tool about making good PRs.

## Tracked issues

<!-- TRACKER:START -->

_Last updated: 2026-11-26 20:27 UTC_

_Tracking **18** upstream repos, **378** relevant open issues._

![Open issues by repo and score](assets/issues_by_repo.png)

### [GoogleCloudPlatform/bigquery-utils](https://github.com/GoogleCloudPlatform/bigquery-utils)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★☆☆ | [#459](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/459) Add Script for On Demand vs. Reservation Analysis | enhancement | 0 | 2024-10-01 |
| ★★★☆☆ | [#5](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/5) Feature Request: Authorized View Generator / Refresher script | enhancement | 0 | 2024-05-29 |
| ★★☆☆☆ | [#518](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/518) bqutil resources are inaccessible via Workload Identity Federation | — | 0 | 2025-12-23 |
| ★★☆☆☆ | [#484](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/484) Add unit testing for colab notebooks | — | 0 | 2025-03-19 |
| ★★☆☆☆ | [#465](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/465) Fix CI/CD pipeline to prevent multiple builds from clobbering cloud storage folders | enhancement | 1 | 2025-01-06 |
| ★★☆☆☆ | [#453](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/453) Unable to find module in theta_sketch.mjs for theta_sketch_int64 | bug | 2 | 2024-12-16 |
| ★★☆☆☆ | [#379](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/379) Missing Datasource for Hourly Utilization Heatmap section | bug | 1 | 2024-10-03 |
| ★★☆☆☆ | [#422](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/422) Add a queries_grouped_by_session.sql script to the optimization/ scripts | enhancement | 1 | 2024-09-18 |

### [GoogleCloudPlatform/opentelemetry-operations-go](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#912](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go/issues/912) Dependency Dashboard | priority: p3, dependencies | 0 | 2026-11-25 |
| ★★☆☆☆ | [#1038](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go/issues/1038) Disabling the normalizer breaks unknown metrics | bug, priority: p2 | 1 | 2026-11-03 |
| ★★☆☆☆ | [#1039](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go/issues/1039) Cloud Trace does not display error span status description | bug, priority: p3, Blocked | 4 | 2025-06-02 |
| ★★☆☆☆ | [#733](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go/issues/733) Remove HTTP method from span name | enhancement, priority: p2 | 5 | 2024-01-31 |
| ★★☆☆☆ | [#707](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go/issues/707) Add metrics for export RPCs | enhancement, priority: p2 | 4 | 2023-08-15 |
| ★☆☆☆☆ | [#1068](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go/issues/1068) Duplicate label key encountered service_name on trace metrics | — | 22 | 2025-09-29 |
| ★☆☆☆☆ | [#1017](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go/issues/1017) Client metrics for cross-project GCS traffic | — | 6 | 2025-02-19 |
| ★☆☆☆☆ | [#443](https://github.com/GoogleCloudPlatform/opentelemetry-operations-go/issues/443) Exporter time series errors do not include metric names | enhancement, priority: p2 | 13 | 2023-08-14 |

### [GoogleCloudPlatform/opentelemetry-operations-python](https://github.com/GoogleCloudPlatform/opentelemetry-operations-python)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★★ | [#357](https://github.com/GoogleCloudPlatform/opentelemetry-operations-python/issues/357) Unsupported metric data type ExponentialHistogram in opentelemetry-exporter-gcp-monitoring | enhancement, good first issue, priority: p2, enhancement accepted | 2 | 2025-06-23 |

### [ansible-collections/community.general](https://github.com/ansible-collections/community.general)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#13367](https://github.com/ansible-collections/community.general/issues/13367) ipa_user: krbpasswordexpiration reports a change on every run | bug, module, plugins | 2 | 2026-11-26 |
| ★★☆☆☆ | [#13360](https://github.com/ansible-collections/community.general/issues/13360) svc module always reports `changed=true` when service no longer exists | bug, module, plugins | 2 | 2026-11-25 |
| ★★☆☆☆ | [#3826](https://github.com/ansible-collections/community.general/issues/3826) idrac_redfish_command HTTP Error 400 submitting configuration job | bug, module, has_pr, needs_info, plugins, remote_management | 8 | 2026-11-22 |
| ★★☆☆☆ | [#13315](https://github.com/ansible-collections/community.general/issues/13315) Module java_cert does not behave correctly when removing a key from a keystore | bug, module, needs_info, plugins | 4 | 2026-11-22 |
| ★☆☆☆☆ | [#13350](https://github.com/ansible-collections/community.general/issues/13350) osx_defaults: nested dict values are written as strings; arrays of dicts fail | feature, module, plugins | 2 | 2026-11-24 |
| ★☆☆☆☆ | [#13347](https://github.com/ansible-collections/community.general/issues/13347) Set a User-Agent for XenAPI requests from xenserver modules | feature, needs_info, needs_template | 4 | 2026-11-24 |
| ★☆☆☆☆ | [#2601](https://github.com/ansible-collections/community.general/issues/2601) Add systemd_escape algorithm as Jinja2 filter | feature, waiting_on_contributor, needs_triage | 12 | 2026-11-24 |
| ★☆☆☆☆ | [#12180](https://github.com/ansible-collections/community.general/issues/12180) bitwarden-lookup : speed up thing by using `bw serve` | feature, lookup, plugins | 7 | 2026-11-22 |

### [ansible/ansible](https://github.com/ansible/ansible)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#87952](https://github.com/ansible/ansible/issues/87952) ansible-playbook -M / --module-path succeeds at runtime but fails under --syntax-check | bug, has_pr, affects_2.20 | 3 | 2026-11-24 |
| ★★☆☆☆ | [#87951](https://github.com/ansible/ansible/issues/87951) ansible-playbook --start-at-task prints [ERROR]: No matching task found but exits 0 | bug, has_pr, affects_2.20 | 4 | 2026-11-24 |
| ★★☆☆☆ | [#87894](https://github.com/ansible/ansible/issues/87894) `environment` values end up in the target's sudo log with `become` | bug | 3 | 2026-11-23 |
| ★★☆☆☆ | [#76221](https://github.com/ansible/ansible/issues/76221) git module changes .git/config despite check_mode when combined with --diff | module, bug, P3, affects_2.11, affects_2.13 | 2 | 2026-11-23 |
| ★☆☆☆☆ | [#87973](https://github.com/ansible/ansible/issues/87973) Provide ability to disable secrets redaction globally, per-task, or for a single ansible run [feature] | feature | 3 | 2026-11-26 |
| ★☆☆☆☆ | [#87978](https://github.com/ansible/ansible/issues/87978) Set SYSLOG_IDENTIFIER when logging to journal | needs_triage, feature | 1 | 2026-11-25 |
| ★☆☆☆☆ | [#86881](https://github.com/ansible/ansible/issues/86881) 2.19 variable performance regression | bug, affects_2.18, affects_2.19 | 18 | 2026-11-25 |
| ★☆☆☆☆ | [#87961](https://github.com/ansible/ansible/issues/87961) get_url does not support ca_path | module, feature | 1 | 2026-11-24 |

### [aws-observability/aws-otel-collector](https://github.com/aws-observability/aws-otel-collector)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#3245](https://github.com/aws-observability/aws-otel-collector/issues/3245) Add AWS Application Signals (awsapplicationsignals) processor to ADOT Collector | — | 0 | 2026-10-26 |
| ★★☆☆☆ | [#3241](https://github.com/aws-observability/aws-otel-collector/issues/3241) Rebuild release artifacts with patched Go for eMudhra CA distrust (CVE-2026-111943) | — | 0 | 2026-10-23 |
| ★★☆☆☆ | [#3239](https://github.com/aws-observability/aws-otel-collector/issues/3239) Add prometheusremotewritereceiver to ADOT Collector | — | 0 | 2026-10-22 |
| ★★☆☆☆ | [#3240](https://github.com/aws-observability/aws-otel-collector/issues/3240) Update method for verifying deb signatures | — | 0 | 2026-10-22 |
| ★★☆☆☆ | [#3234](https://github.com/aws-observability/aws-otel-collector/issues/3234) Bump golang.org/x/crypto and google.golang.org/grpc for CVE-2026-56854, CVE-2026-84304 and CVE-2026-84445 | — | 0 | 2026-09-25 |
| ★☆☆☆☆ | [#3162](https://github.com/aws-observability/aws-otel-collector/issues/3162) AWS exporters fail to refresh externally-rotated credentials (e.g., SSM hybrid-activated on-prem instances) | stale | 7 | 2026-11-22 |
| ★☆☆☆☆ | [#2462](https://github.com/aws-observability/aws-otel-collector/issues/2462) ECS FireLens compatibiltiy: Make it a drop in replacement for aws for fluent bit | logs | 40 | 2026-10-04 |
| ★☆☆☆☆ | [#1166](https://github.com/aws-observability/aws-otel-collector/issues/1166) spanmetricsprocessor for ADOT | feature-request, ADOT collector, processor | 9 | 2026-03-03 |

### [collabnix/dockerlabs](https://github.com/collabnix/dockerlabs)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#544](https://github.com/collabnix/dockerlabs/issues/544) A New Modern Look for Docker Labs | — | 0 | 2026-03-25 |
| ★★☆☆☆ | [#452](https://github.com/collabnix/dockerlabs/issues/452) Define journey for Azure, AWS and Google Cloud Engineers | — | 0 | 2022-08-02 |
| ★★☆☆☆ | [#413](https://github.com/collabnix/dockerlabs/issues/413) A weird IP in this HA K8S deployment doc   10.10.40.10   ? | — | 0 | 2022-01-23 |
| ★☆☆☆☆ | [#549](https://github.com/collabnix/dockerlabs/issues/549) PWD lab plaform deprecated | — | 2 | 2026-03-25 |
| ★☆☆☆☆ | [#536](https://github.com/collabnix/dockerlabs/issues/536) docs: Capabilities page - Images can store file-based capabilities | — | 2 | 2024-01-09 |
| ★☆☆☆☆ | [#508](https://github.com/collabnix/dockerlabs/issues/508) [docker] Upgrade labs for cross-platform compatibility | — | 3 | 2023-09-30 |
| ★☆☆☆☆ | [#456](https://github.com/collabnix/dockerlabs/issues/456) Improve Sample Apps section - Add a showcase page | — | 2 | 2023-08-24 |
| ★☆☆☆☆ | [#293](https://github.com/collabnix/dockerlabs/issues/293) Etcd config mistake | — | 2 | 2022-12-02 |

### [grafana/google-bigquery-datasource](https://github.com/grafana/google-bigquery-datasource)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#414](https://github.com/grafana/google-bigquery-datasource/issues/414) Dependency Dashboard | — | 0 | 2026-11-26 |
| ★★☆☆☆ | [#575](https://github.com/grafana/google-bigquery-datasource/issues/575) [bigquery] Re-enable e2e health check test on cloud | — | 0 | 2026-10-02 |
| ★★☆☆☆ | [#552](https://github.com/grafana/google-bigquery-datasource/issues/552) Incorrect interpolation of single quote for multi-value variable | — | 0 | 2026-08-04 |
| ★★☆☆☆ | [#548](https://github.com/grafana/google-bigquery-datasource/issues/548) Ensure BigQuery is React 19 compatible | — | 0 | 2026-07-24 |
| ★★☆☆☆ | [#533](https://github.com/grafana/google-bigquery-datasource/issues/533) Feature: GCE for Alerting | — | 0 | 2026-06-28 |
| ★★☆☆☆ | [#522](https://github.com/grafana/google-bigquery-datasource/issues/522) Grafana 13.0.2 BigQuery Query Variable definition Field Always Cleared | — | 0 | 2026-06-10 |
| ★☆☆☆☆ | [#322](https://github.com/grafana/google-bigquery-datasource/issues/322) Streaming JSON parser for Big Query | stale | 3 | 2026-11-07 |
| ★☆☆☆☆ | [#502](https://github.com/grafana/google-bigquery-datasource/issues/502) NUMERIC / BIGNUMERIC values lose precision (converted via float64) | — | 2 | 2026-07-04 |

### [grafana/grafana-ansible-collection](https://github.com/grafana/grafana-ansible-collection)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★★ | [#268](https://github.com/grafana/grafana-ansible-collection/issues/268) Add Workflow to Upload collection verion to Ansible Galaxy | good first issue, help wanted | 0 | 2024-09-13 |

### [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★☆ | [#144333](https://github.com/kubernetes/kubernetes/issues/144333) retry.OnErrorWithContext / retry.RetryOnConflictWithContext | sig/api-machinery, help wanted, good first issue, needs-triage | 6 | 2026-11-22 |
| ★★★☆☆ | [#141200](https://github.com/kubernetes/kubernetes/issues/141200) [Flaking Test] [sig-node] [Feature:GPUDevicePlugin] Sanity test using nvidia-smi [Provider:aws,gce] should run nvidia-smi and cuda-demo-suite [Serial] | sig/node, kind/flake, help wanted, priority/important-longterm, triage/accepted | 10 | 2026-11-24 |
| ★★★☆☆ | [#144431](https://github.com/kubernetes/kubernetes/issues/144431) DRA Node Allocatable Resources: hugepages e2e cases never run in CI | area/test, sig/node, help wanted, priority/important-longterm, kind/failing-test, triage/accepted, wg/device-management | 5 | 2026-11-23 |
| ★★★☆☆ | [#138149](https://github.com/kubernetes/kubernetes/issues/138149) Migrate DRA components to support granular authorization on status updates | sig/network, sig/node, sig/auth, help wanted, good first issue, triage/accepted, wg/device-management | 99 | 2026-11-18 |
| ★★★☆☆ | [#144300](https://github.com/kubernetes/kubernetes/issues/144300) [Flaking Test] LocalStorageCapacityIsolationEviction: clean-exit emptyDir container exits 137, expected 0 | sig/node, kind/flake, help wanted, priority/important-longterm, triage/accepted | 5 | 2026-11-18 |
| ★★★☆☆ | [#144302](https://github.com/kubernetes/kubernetes/issues/144302) [Flaking Test] PodResources metrics: List() gets connection refused on the kubelet socket | sig/node, kind/flake, help wanted, priority/important-longterm, triage/accepted | 5 | 2026-11-18 |
| ★★★☆☆ | [#118172](https://github.com/kubernetes/kubernetes/issues/118172) kubelet parameter(eviction-max-pod-grace-period ), not work as expected like officical comment. | kind/bug, priority/backlog, kind/documentation, sig/node, help wanted, priority/important-longterm, good first issue, triage/accepted | 48 | 2026-11-10 |
| ★★★☆☆ | [#120677](https://github.com/kubernetes/kubernetes/issues/120677) Test Audit policy using original (non-impersonated) user for filtering | sig/auth, help wanted, triage/accepted | 8 | 2026-11-01 |

### [langfuse/langfuse](https://github.com/langfuse/langfuse)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★☆☆ | [#20921](https://github.com/langfuse/langfuse/issues/20921) bug: chart category labels split surrogate pairs when truncated | bug, feat-dashboard | 0 | 2026-11-26 |
| ★★★☆☆ | [#21013](https://github.com/langfuse/langfuse/issues/21013) ClickHouse migration 0050 fails on ClickHouse 26.6: "Cannot materialize column `session_id` because it doesn't have default expression" | bug, feat-scores, self-hosting | 0 | 2026-11-26 |
| ★★★☆☆ | [#21005](https://github.com/langfuse/langfuse/issues/21005) bug: ingestion drops metadata values false, 0, and empty string | bug, feat-metadata, feat-ingestion | 0 | 2026-11-26 |
| ★★★☆☆ | [#20947](https://github.com/langfuse/langfuse/issues/20947) bug(sdk-js): ChatPromptClient.compile() renders placeholder messages as mustache, deleting {{...}} text or throwing | bug, feat-prompt-management | 0 | 2026-11-26 |
| ★★★☆☆ | [#20923](https://github.com/langfuse/langfuse/issues/20923) bug: Genkit Gemini spans lose visible output tokens because thoughtsTokens is subtracted from outputTokens | bug, feat-llm-cost-tracking, integration-otel, feat-otel | 0 | 2026-11-26 |
| ★★☆☆☆ | [#19365](https://github.com/langfuse/langfuse/issues/19365) Dataset duplication name counter fails to increment properly for dataset names with underscores | bug, feat-datasets, stale | 1 | 2026-11-26 |
| ★★☆☆☆ | [#19369](https://github.com/langfuse/langfuse/issues/19369) bug: Graph view freezes the browser for seconds on traces with nested spans (quadratic step adjustment in buildStepData) | bug, single-trace-ui, stale, front-end-performance, graph | 1 | 2026-11-26 |
| ★☆☆☆☆ | [#16077](https://github.com/langfuse/langfuse/issues/16077) bug: v4 unified Tracing table cannot display trace total cost — root SPAN rows show $0.00 | bug, tables, feat-llm-cost-tracking, feat-tracing | 25 | 2026-11-26 |

### [nightscout/cgm-remote-monitor](https://github.com/nightscout/cgm-remote-monitor)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★☆ | [#6676](https://github.com/nightscout/cgm-remote-monitor/issues/6676) Horizontal Scrolling with mouse wheel (holding Shift key) | good-first-issue | 2 | 2026-11-23 |
| ★★★★☆ | [#7540](https://github.com/nightscout/cgm-remote-monitor/issues/7540) BASE_URL and sub-directories. | good-first-issue | 6 | 2025-07-22 |
| ★★★☆☆ | [#5742](https://github.com/nightscout/cgm-remote-monitor/issues/5742) Custom WebHook Support | help wanted, feature request | 2 | 2026-06-15 |
| ★★★☆☆ | [#6028](https://github.com/nightscout/cgm-remote-monitor/issues/6028) Loopalyzer report has missing Active insulin rendering for some days | help wanted | 4 | 2020-10-14 |

### [observIQ/bindplane-otel-collector](https://github.com/observIQ/bindplane-otel-collector)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#3823](https://github.com/observIQ/bindplane-otel-collector/issues/3823) Mirror from DBDOT: deps: update ghcr.io/open-telemetry/opentelemetry-collector-contrib/telemetrygen docker tag to v0.165.1 (#142) | dbdot-mirror-issue | 0 | 2026-11-24 |
| ★★☆☆☆ | [#3822](https://github.com/observIQ/bindplane-otel-collector/issues/3822) Mirror from DBDOT: chore(tests): Add load tests (#150) | dbdot-mirror-issue | 0 | 2026-11-23 |
| ★★☆☆☆ | [#3821](https://github.com/observIQ/bindplane-otel-collector/issues/3821) Mirror from DBDOT: deps: update ubuntu:26.04 docker digest to d66b366 (#152) | dbdot-mirror-issue | 0 | 2026-11-23 |
| ★★☆☆☆ | [#3820](https://github.com/observIQ/bindplane-otel-collector/issues/3820) Mirror from DBDOT: deps: update github-actions deps (#153) | dbdot-mirror-issue | 0 | 2026-11-23 |
| ★★☆☆☆ | [#3817](https://github.com/observIQ/bindplane-otel-collector/issues/3817) Mirror from DBDOT: feat: Add Exabeam exporter (BP-1307) (#149) | dbdot-mirror-issue | 0 | 2026-11-20 |
| ★★☆☆☆ | [#3814](https://github.com/observIQ/bindplane-otel-collector/issues/3814) Mirror from DBDOT: chore: v1.4.0 release prep (#148) | dbdot-mirror-issue | 0 | 2026-11-19 |
| ★☆☆☆☆ | [#3825](https://github.com/observIQ/bindplane-otel-collector/issues/3825) Mirror from DBDOT: deps: update dependency goreleaser/goreleaser-pro to v2.20.3 (#156) | dbdot-mirror-issue | 1 | 2026-11-24 |
| ★☆☆☆☆ | [#3824](https://github.com/observIQ/bindplane-otel-collector/issues/3824) Mirror from DBDOT: chore: track all tool versions in GHA with renovate (#155) | dbdot-mirror-issue | 2 | 2026-11-24 |

### [open-telemetry/opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★★ | [#52946](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/52946) [pkg/ottl] Comparing two values of the same uncomparable type panics and crashes the collector | bug, good first issue, priority:p0, pkg/ottl | 6 | 2026-11-19 |
| ★★★★☆ | [#48079](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/48079) [pkg/pdatatest] New MTS-focused metric assertion framework | enhancement, help wanted, never stale, pkg/pdatatest | 2 | 2026-11-25 |
| ★★★★☆ | [#39333](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/39333) Add system.cpu.socket.id and system.cpu.core.id attributes | enhancement, good first issue, receiver/hostmetrics, never stale | 19 | 2026-11-23 |
| ★★★★☆ | [#51982](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/51982) [receiver/k8sevents] watch stalls forever without logging: RetryWatcher retries every second and the observer never re-lists | bug, help wanted, receiver/k8sevents, internal/k8sinventory | 7 | 2026-11-20 |
| ★★★★☆ | [#52039](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/52039) [internal/kafka] Deprecate `AWS_MSK_IAM_OAUTHBEARER` | good first issue, extension/sigv4auth, internal/kafka | 10 | 2026-11-20 |
| ★★★★☆ | [#53398](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/53398) [receiver/solace] Unmaintained component | help wanted, unmaintained | 0 | 2026-11-20 |
| ★★★★☆ | [#53397](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/53397) [receiver/namedpipe] Unmaintained component | help wanted, unmaintained | 0 | 2026-11-20 |
| ★★★★☆ | [#53396](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/53396) [exporter/logzio] Unmaintained component | help wanted, unmaintained | 0 | 2026-11-20 |

### [prometheus/prometheus](https://github.com/prometheus/prometheus)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★☆ | [#1220](https://github.com/prometheus/prometheus/issues/1220) Preview alerts in expression browser | help wanted, kind/enhancement, component/ui, priority/P3 | 0 | 2024-02-13 |
| ★★★☆☆ | [#8798](https://github.com/prometheus/prometheus/issues/8798) Add exemplar support to rules (recording, alerts) | help wanted, component/rules, kind/feature | 7 | 2026-11-23 |
| ★★★☆☆ | [#14349](https://github.com/prometheus/prometheus/issues/14349) [agent] metrics reported by prometheus in agent mode break meta monitoring | help wanted, kind/bug, component/agent | 4 | 2026-11-21 |
| ★★★☆☆ | [#11852](https://github.com/prometheus/prometheus/issues/11852) Prometheus agent mode hashmod sharding issue | help wanted, kind/bug, priority/Pmaybe, component/agent | 4 | 2026-11-20 |
| ★★★☆☆ | [#14342](https://github.com/prometheus/prometheus/issues/14342) [Remote Write 2.x] Arrow Proto Message Experiment & Benchmark | help wanted, priority/Pmaybe, component/remote storage, not-as-easy-as-it-looks, kind/optimization | 2 | 2026-11-18 |
| ★★★☆☆ | [#14926](https://github.com/prometheus/prometheus/issues/14926) feat: Avoid decay of our micro-benchmarks; test them on CI | help wanted, priority/P2, component/tests, area/ci-cd | 7 | 2026-11-17 |
| ★★★☆☆ | [#12896](https://github.com/prometheus/prometheus/issues/12896) Turn one source label into multiple target labels | help wanted, kind/enhancement, component/service discovery, priority/P3 | 5 | 2026-11-11 |
| ★★★☆☆ | [#14823](https://github.com/prometheus/prometheus/issues/14823) ST: Optimize CPU/memory use for OM1.0 Text CT/ST parsing (`st-storage` and `created-timestamp-zero-ingestion` features) | help wanted, component/scraping | 6 | 2026-11-06 |

### [splunk/ansible-role-for-splunk](https://github.com/splunk/ansible-role-for-splunk)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★★ | [#102](https://github.com/splunk/ansible-role-for-splunk/issues/102) Enhancement: Add support to perform rolling upgrades for shc and idx | enhancement, help wanted | 0 | 2021-09-15 |

### [splunk/splunk-sdk-python](https://github.com/splunk/splunk-sdk-python)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#860](https://github.com/splunk/splunk-sdk-python/issues/860) Documentation suggestion: make TLS verification explicit in SDK connection examples | — | 0 | 2026-11-18 |
| ★★☆☆☆ | [#704](https://github.com/splunk/splunk-sdk-python/issues/704) Unverified SSL context | — | 0 | 2026-09-04 |
| ★★☆☆☆ | [#840](https://github.com/splunk/splunk-sdk-python/issues/840) mcp 2.x compatibility for splunklib.ai | — | 0 | 2026-09-03 |
| ★★☆☆☆ | [#828](https://github.com/splunk/splunk-sdk-python/issues/828) Search Result Export with SSL off doesn't work | — | 0 | 2026-08-18 |
| ★★☆☆☆ | [#785](https://github.com/splunk/splunk-sdk-python/issues/785) Splunk core -> python3.13 | — | 0 | 2026-05-13 |
| ★★☆☆☆ | [#687](https://github.com/splunk/splunk-sdk-python/issues/687) Custom command have high CPU load / RAM usage | bug, Custom Search Commands | 1 | 2026-03-20 |
| ★★☆☆☆ | [#617](https://github.com/splunk/splunk-sdk-python/issues/617) Question - High performing and high scale KVstore content retrieval with the Splunk Python SDK | bug, KV Store | 2 | 2025-11-13 |
| ★☆☆☆☆ | [#831](https://github.com/splunk/splunk-sdk-python/issues/831) `SPLUNK_HOME` absolute-path check in `splunklib.ai.tools` fails on Windows | — | 1 | 2026-08-19 |

### [traceloop/openllmetry](https://github.com/traceloop/openllmetry)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★☆ | [#417](https://github.com/traceloop/openllmetry/issues/417) 🐛 Bug Report: disabled tests for GCP / VertexAI | good first issue, help wanted, testing | 9 | 2026-11-12 |
| ★★★★☆ | [#2303](https://github.com/traceloop/openllmetry/issues/2303) 🚀 Feature: Support for Azure AI Search | enhancement, good first issue, help wanted | 16 | 2026-05-18 |
| ★★★★☆ | [#2283](https://github.com/traceloop/openllmetry/issues/2283) 🚀 Feature: Add instruments support for httpx | enhancement, good first issue | 11 | 2025-11-06 |
| ★★★☆☆ | [#4069](https://github.com/traceloop/openllmetry/issues/4069) 🚀 Feature: Suggestion: Add beginner-friendly example for LLM tracing | good first issue | 16 | 2026-11-03 |
| ★★★☆☆ | [#1618](https://github.com/traceloop/openllmetry/issues/1618) 🚀 Feature: Support new Pinecone APIs | good first issue, help wanted | 13 | 2026-10-28 |
| ★★★☆☆ | [#2803](https://github.com/traceloop/openllmetry/issues/2803) 🚀 Feature: Install less packages | good first issue, help wanted | 20 | 2026-10-14 |
| ★★★☆☆ | [#3492](https://github.com/traceloop/openllmetry/issues/3492) 🐛 Bug Report: `opentelemetry-instrumentation-qdrant` is incompatible with `qdrant-client` version `1.16.1` | good first issue, help wanted | 13 | 2026-09-13 |
| ★★★☆☆ | [#785](https://github.com/traceloop/openllmetry/issues/785) 🚀 Feature: Support runpod.ai | help wanted, new instrumentation | 4 | 2026-08-19 |


<!-- TRACKER:END -->

## Run metrics

<!-- METRICS:START -->

_Last run: 2026-11-26 20:25 UTC, took **114.1s**, **125** GitHub API calls, **4875/5000** rate limit remaining._

![Scrape metrics trend](assets/metrics_trend.png)

<!-- METRICS:END -->

## License

[MIT](LICENSE)
