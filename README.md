# oss-issue-tracker

Dynamic contribution radar: scans every repo I've forked, resolves each one's upstream, pulls its open issues, and scores them by how approachable they are — so I can decide what to work on next without manually digging through issue trackers.

Refreshed automatically every Monday by [`.github/workflows/weekly-scrape.yml`](.github/workflows/weekly-scrape.yml). Trigger it manually anytime from the Actions tab.

## How scoring works

Each issue gets a 1-5 star approachability score, computed in [`scripts/update_tracker.py`](scripts/update_tracker.py):

- `good first issue` / `beginner-friendly` label → +3
- `help wanted` / `up-for-grabs` label → +2
- `bug` or `enhancement` label → +1
- Zero comments (nobody's claimed or debated it) → +1
- More than 10 comments (likely contested or stale) → -1

Repos with no labeled beginner-friendly issues fall back to showing their most recently updated open issues, so quiet repos don't just disappear from the table.

## Tracked issues

<!-- TRACKER:START -->

_Last updated: 2026-07-15 18:41 UTC_

_Tracking **11** upstream repos, **343** relevant open issues._

### [GoogleCloudPlatform/bigquery-utils](https://github.com/GoogleCloudPlatform/bigquery-utils)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★☆☆ | [#459](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/459) Add Script for On Demand vs. Reservation Analysis | enhancement | 0 | 2024-10-01 |
| ★★☆☆☆ | [#518](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/518) bqutil resources are inaccessible via Workload Identity Federation | — | 0 | 2025-12-23 |
| ★★☆☆☆ | [#484](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/484) Add unit testing for colab notebooks | — | 0 | 2025-03-19 |
| ★★☆☆☆ | [#465](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/465) Fix CI/CD pipeline to prevent multiple builds from clobbering cloud storage folders | enhancement | 1 | 2025-01-06 |
| ★★☆☆☆ | [#453](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/453) Unable to find module in theta_sketch.mjs for theta_sketch_int64 | bug | 2 | 2024-12-16 |
| ★★☆☆☆ | [#379](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/379) Missing Datasource for Hourly Utilization Heatmap section | bug | 1 | 2024-10-03 |
| ★★☆☆☆ | [#422](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/422) Add a queries_grouped_by_session.sql script to the optimization/ scripts | enhancement | 1 | 2024-09-18 |
| ★☆☆☆☆ | [#544](https://github.com/GoogleCloudPlatform/bigquery-utils/issues/544) theta_sketch_* UDFs hang until query timeout on estimation-mode sketches (started ~mid-June 2026, europe-west1) | — | 2 | 2026-06-25 |

### [ansible-collections/community.general](https://github.com/ansible-collections/community.general)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#11331](https://github.com/ansible-collections/community.general/issues/11331) btrfs mountpoint scan does not account for symlinks | bug, module, has_pr, plugins | 6 | 2026-07-12 |
| ★★☆☆☆ | [#12388](https://github.com/ansible-collections/community.general/issues/12388) consul_kv: deprecate and remove get_value | bug, module, plugins | 2 | 2026-07-12 |
| ★★☆☆☆ | [#8980](https://github.com/ansible-collections/community.general/issues/8980) incus conn plugin: Intermittent Issues with Temporary Directory Creation and Connection Drops | bug | 8 | 2026-07-11 |
| ★★☆☆☆ | [#11246](https://github.com/ansible-collections/community.general/issues/11246) Cobbler Dynamic Inventory Source incorrectly upgrades connection to SSL | bug, inventory, plugins | 3 | 2026-07-10 |
| ★★☆☆☆ | [#12374](https://github.com/ansible-collections/community.general/issues/12374) community.general.office_365_connector_card - Connector cards are deprecated, and errors on `202 Accepted` from PowerAutomate | bug, module, plugins | 3 | 2026-07-04 |
| ★★☆☆☆ | [#12375](https://github.com/ansible-collections/community.general/issues/12375) snap: module fails with `list index out of range` exception if cannot find snap | bug, module, traceback, plugins | 2 | 2026-07-03 |
| ★☆☆☆☆ | [#11482](https://github.com/ansible-collections/community.general/issues/11482) Releasing, Versioning and Deprecation (2/N) | admin | 12 | 2026-07-13 |
| ★☆☆☆☆ | [#12029](https://github.com/ansible-collections/community.general/issues/12029) Deprecate xml module's `print_match`, `count`, and `content` options | feature, module, has_pr, plugins | 3 | 2026-07-13 |

### [ansible/ansible](https://github.com/ansible/ansible)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#87251](https://github.com/ansible/ansible/issues/87251) get_url fails with SSL [ASN1: NOT_ENOUGH_DATA] on current UBI9 | module, needs_triage, bug, affects_2.20 | 3 | 2026-07-15 |
| ★★☆☆☆ | [#87178](https://github.com/ansible/ansible/issues/87178) Regresssion: "'item' is undefined" if using delegate_to with with_items | needs_info, bug, affects_2.21 | 5 | 2026-07-14 |
| ★★☆☆☆ | [#85503](https://github.com/ansible/ansible/issues/85503) chmod: invalid mode: ‘A+user:myuser:rx:allow’ when using become_user and acl package is not installed on the node | bug, verified, affects_2.18 | 5 | 2026-07-14 |
| ★★☆☆☆ | [#87228](https://github.com/ansible/ansible/issues/87228) powershell exec_wrapper fails when multiple powershell.exe entries are found in PATH | needs_triage, bug, affects_2.21 | 1 | 2026-07-10 |
| ★☆☆☆☆ | [#87252](https://github.com/ansible/ansible/issues/87252) configuration file for ansible-galaxy | needs_triage, feature | 4 | 2026-07-15 |
| ★☆☆☆☆ | [#87197](https://github.com/ansible/ansible/issues/87197) dnf module should expose clean_requirements_on_remove independently from autoremove | module, has_pr, feature | 1 | 2026-07-14 |
| ★☆☆☆☆ | [#87161](https://github.com/ansible/ansible/issues/87161) `ansible.builtin.meta: refresh_inventory` What does exactly get refreshed? | module, has_pr, docs, affects_2.21 | 2 | 2026-07-14 |
| ★☆☆☆☆ | [#87236](https://github.com/ansible/ansible/issues/87236) Support mTLS client certificates per Galaxy server | needs_triage, has_pr, feature | 1 | 2026-07-13 |

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
| ★★★★☆ | [#110](https://github.com/grafana/google-bigquery-datasource/issues/110) Documentation: Add more verbose documentation for macros support | documentation, type/feature-request, help wanted | 0 | 2022-04-21 |

### [grafana/grafana-ansible-collection](https://github.com/grafana/grafana-ansible-collection)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★★ | [#268](https://github.com/grafana/grafana-ansible-collection/issues/268) Add Workflow to Upload collection verion to Ansible Galaxy | good first issue, help wanted | 0 | 2024-09-13 |

### [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★☆☆ | [#114369](https://github.com/kubernetes/kubernetes/issues/114369) NetworkPolicy tests for blocking north/south traffic | priority/backlog, sig/network, help wanted, good first issue, triage/accepted, area/network-policy | 38 | 2026-07-15 |
| ★★★☆☆ | [#138149](https://github.com/kubernetes/kubernetes/issues/138149) Migrate DRA components to support granular authorization on status updates | sig/network, sig/node, sig/auth, help wanted, good first issue, triage/accepted, wg/device-management | 71 | 2026-07-14 |
| ★★★☆☆ | [#126379](https://github.com/kubernetes/kubernetes/issues/126379) add and use alternative APIs which support contextual logging | area/logging, kind/feature, help wanted, sig/instrumentation, good first issue, triage/accepted, wg/structured-logging | 38 | 2026-06-30 |
| ★★★☆☆ | [#135058](https://github.com/kubernetes/kubernetes/issues/135058) DRA: measure and track performance of "experimental" allocator | kind/feature, help wanted, good first issue, needs-triage, wg/device-management | 20 | 2026-06-17 |
| ★★★☆☆ | [#115782](https://github.com/kubernetes/kubernetes/issues/115782) Write the stress test for gRPC, http, and tcp probes | priority/backlog, kind/cleanup, sig/node, help wanted, good first issue, needs-triage | 39 | 2026-06-16 |
| ★★★☆☆ | [#139328](https://github.com/kubernetes/kubernetes/issues/139328) Investigate nftables startup performance at scale | sig/network, area/kube-proxy, help wanted, triage/accepted | 6 | 2026-06-04 |
| ★★★☆☆ | [#138679](https://github.com/kubernetes/kubernetes/issues/138679) [Flaking Test] TestEventSeries failing in pull-kubernetes-integration with timed out waiting for Event Series | kind/flake, help wanted, sig/instrumentation, triage/accepted | 6 | 2026-05-29 |
| ★★★☆☆ | [#109717](https://github.com/kubernetes/kubernetes/issues/109717) tracker: improve the kubelet test coverage | sig/node, help wanted, good first issue, needs-triage | 49 | 2026-05-26 |

### [nightscout/cgm-remote-monitor](https://github.com/nightscout/cgm-remote-monitor)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★★ | [#7766](https://github.com/nightscout/cgm-remote-monitor/issues/7766) Add base_uri variable (for proxy) | enhancement, help wanted, feature/deployment-setup, feature request | 0 | 2025-05-22 |
| ★★★★★ | [#6676](https://github.com/nightscout/cgm-remote-monitor/issues/6676) Horizontal Scrolling with mouse wheel (holding Shift key) | good-first-issue | 0 | 2025-05-16 |
| ★★★★☆ | [#8048](https://github.com/nightscout/cgm-remote-monitor/issues/8048) Clock whit seconds | feature request, good-first-issue | 1 | 2026-06-30 |
| ★★★★☆ | [#8192](https://github.com/nightscout/cgm-remote-monitor/issues/8192) List items are not scrollable when viewing Food Editor on mobile. | good-first-issue | 1 | 2026-06-17 |
| ★★★★☆ | [#7441](https://github.com/nightscout/cgm-remote-monitor/issues/7441) Link to step-by-step guide for updating does not work anymore | docs, good-first-issue | 2 | 2026-05-21 |
| ★★★★☆ | [#7540](https://github.com/nightscout/cgm-remote-monitor/issues/7540) BASE_URL and sub-directories. | good-first-issue | 6 | 2025-07-22 |
| ★★★★☆ | [#7377](https://github.com/nightscout/cgm-remote-monitor/issues/7377) Clock views don't show when token auth is used | clock, good-first-issue | 1 | 2025-05-22 |
| ★★★☆☆ | [#5742](https://github.com/nightscout/cgm-remote-monitor/issues/5742) Custom WebHook Support | help wanted, feature request | 2 | 2026-06-15 |

### [observIQ/bindplane-otel-collector](https://github.com/observIQ/bindplane-otel-collector)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★☆☆☆ | [#2542](https://github.com/observIQ/bindplane-otel-collector/issues/2542) Add TCP Check receiver | — | 0 | 2025-08-23 |
| ★☆☆☆☆ | [#2296](https://github.com/observIQ/bindplane-otel-collector/issues/2296) install_unix.sh breaks with status code 2 in non-interactive environments | — | 4 | 2026-03-04 |

### [open-telemetry/opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★★ | [#48419](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/48419) [connector/signaltometrics] Change default `error_mode` to `ignore` | enhancement, help wanted, good first issue, connector/signaltometrics | 5 | 2026-05-30 |
| ★★★★★ | [#38092](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/38092) [CI/CD\| run no race tests in CIs too | enhancement, good first issue, ci-cd, never stale | 9 | 2026-05-21 |
| ★★★★★ | [#48420](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/48420) [processor/tailsampling] Change default `error_mode` to `ignore` | enhancement, help wanted, good first issue, processor/tailsampling | 3 | 2026-05-19 |
| ★★★★★ | [#39333](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/39333) Add system.cpu.socket.id and system.cpu.core.id attributes | enhancement, good first issue, Stale, processor/resourcedetection, never stale | 9 | 2026-01-20 |
| ★★★★☆ | [#43918](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/43918) [aws/k8s] TestGetShutdown is failing on Windows after upgrading k8s library to 1.34 | bug, help wanted, good first issue, internal/aws | 12 | 2026-07-15 |
| ★★★★☆ | [#48186](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/48186) Deprecate and remove kafkatopicsobserver | good first issue, extension/observer/kafkatopicsobserver | 10 | 2026-07-09 |
| ★★★★☆ | [#22095](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/22095) Migrate to latest semconv version and ensure we regularly update going forward | enhancement, good first issue, priority:p2, never stale, component-stability-phase-1 | 24 | 2026-07-04 |
| ★★★★☆ | [#19172](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/19172) Add Warning header to all necessary components | documentation, help wanted, good first issue, priority:p3, never stale, Contribfest | 10 | 2026-07-02 |

### [prometheus/prometheus](https://github.com/prometheus/prometheus)

| Score | Issue | Labels | Comments | Updated |
|---|---|---|---|---|
| ★★★★☆ | [#14342](https://github.com/prometheus/prometheus/issues/14342) [Remote Write 2.x] Arrow Proto Message Experiment & Benchmark | help wanted, priority/Pmaybe, component/remote storage, not-as-easy-as-it-looks, kind/optimization | 0 | 2024-06-25 |
| ★★★★☆ | [#1220](https://github.com/prometheus/prometheus/issues/1220) Preview alerts in expression browser | help wanted, kind/enhancement, component/ui, priority/P3 | 0 | 2024-02-13 |
| ★★★☆☆ | [#14763](https://github.com/prometheus/prometheus/issues/14763) Start Timestamp: Opt-in ST auto-generation globally/per scrape job. | help wanted, kind/feature | 3 | 2026-07-14 |
| ★★★☆☆ | [#14057](https://github.com/prometheus/prometheus/issues/14057) Add relabeling action that drops sample if any label matches pattern | help wanted, component/config, priority/P3, kind/feature | 4 | 2026-07-08 |
| ★★★☆☆ | [#16176](https://github.com/prometheus/prometheus/issues/16176) TestDBReadOnly_Querier_NoAlteration is flaky on Windows | help wanted, component/tests | 5 | 2026-07-08 |
| ★★★☆☆ | [#16513](https://github.com/prometheus/prometheus/issues/16513) Idea: store scrape cache as a trie instead of a map. | help wanted, kind/enhancement, component/scraping | 10 | 2026-07-08 |
| ★★★☆☆ | [#10953](https://github.com/prometheus/prometheus/issues/10953) Configuring PromQL query statistics | help wanted, kind/enhancement, priority/P3, component/api | 8 | 2026-07-07 |
| ★★★☆☆ | [#18387](https://github.com/prometheus/prometheus/issues/18387) Support periodic DNS re-resolution for FQDN targets discovered via Consul SD | help wanted, kind/bug | 8 | 2026-06-28 |


<!-- TRACKER:END -->
