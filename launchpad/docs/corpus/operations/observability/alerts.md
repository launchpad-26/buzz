---
id: operations-observability-alerts
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The only PrometheusRule resource defined anywhere in this repository is deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml, which declares five alerts in one rule group named buzz-push-gateway: PushGatewayConfigurationFault, PushGatewayAdmissionUnavailable, PushGatewayReadinessAuthorityFailing, PushGatewayReaperFailing and PushGatewayHighApnsRetryRate."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml"
  - statement: "PushGatewayConfigurationFault (prometheusrule.yaml:16-26) fires on any rate of push_gateway_apns_deliveries_total{outcome=\"configuration_fault\"} sustained for 10m, at severity critical; PushGatewayAdmissionUnavailable (prometheusrule.yaml:28-38) fires on any rate of push_gateway_admissions_total{result=\"unavailable\"} sustained for 5m, at severity critical."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml:16-26"
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml:28-38"
  - statement: "PushGatewayReadinessAuthorityFailing (prometheusrule.yaml:41-51) fires on any rate of push_gateway_readiness_failures_total{cause=\"authority\"} sustained for 5m, at severity warning; PushGatewayReaperFailing (prometheusrule.yaml:56-66) fires when push_gateway_reaper_failures_total increases by 2 or more within a 30m window, sustained for 5m, at severity warning; PushGatewayHighApnsRetryRate (prometheusrule.yaml:71-88) fires when the retryable fraction of push_gateway_apns_deliveries_total over a 10m window exceeds a configurable threshold (prometheusRule.apnsRetryRatioThreshold, default 0.25) while at least prometheusRule.apnsRetryMinSamples (default 20) attempts occurred, sustained for 15m, at severity warning."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml:41-51"
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml:56-66"
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml:71-88"
      - "deploy/charts/buzz-push-gateway/values.yaml"
  - statement: "deploy/charts/buzz-push-gateway/values.yaml sets prometheusRule.enabled to false by default, and deploy/charts/buzz-push-gateway/values-production.yaml, the chart's production values overlay, does not set prometheusRule anywhere, so the one alert set this repository defines stays disabled even under the production overlay unless an operator overrides it at install time."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/values.yaml"
      - "deploy/charts/buzz-push-gateway/values-production.yaml"
  - statement: "deploy/charts/buzz-push-gateway/tests/render.sh asserts, at line 67, that a default chart render (prometheusRule.enabled left at its default) contains no PodMonitor or PrometheusRule resource at all; at line 137, after rendering with --set prometheusRule.enabled=true (set at line 121) and --set podMonitor.enabled=true, it asserts the rendered PrometheusRule's spec.groups is not empty; and at lines 180-182, after --set prometheusRule.enabled=true, it asserts that --set prometheusRule.apnsRetryRatioThreshold=2 (a value outside the 0..1 fraction the alert expression assumes) fails Helm's schema validation rather than rendering."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/tests/render.sh:67"
      - "deploy/charts/buzz-push-gateway/tests/render.sh:121"
      - "deploy/charts/buzz-push-gateway/tests/render.sh:137"
      - "deploy/charts/buzz-push-gateway/tests/render.sh:180-182"
  - statement: "docs/push-gateway-deployment.md documents the same five alerts in prose, as a table naming each alert's firing condition, severity and the operator action expected in response, and states directly that alerting rules ship as an opt-in prometheus-operator PrometheusRule (prometheusRule.enabled=true)."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md:79-87"
  - statement: "The main relay Helm chart, deploy/charts/buzz, ships an opt-in Prometheus Operator ServiceMonitor (templates/servicemonitor.yaml, ServiceMonitor.enabled defaulting to false in values.yaml) that scrapes the relay's /metrics endpoint, but its values.yaml defines no prometheusRule key or PrometheusRule template of any kind -- unlike the sibling buzz-push-gateway chart, the relay chart ships no alert-rule surface at all, opt-in or otherwise."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/servicemonitor.yaml"
      - "deploy/charts/buzz/values.yaml"
  - statement: "buzz-relay's health-only listener serves liveness_handler, which unconditionally returns 200 OK with no dependency check, and readiness_handler, which under a 2-second timeout concurrently checks a Postgres ping, a Redis pool checkout and the deletion-serving catalog's validity, returning 200 {\"status\": \"ready\"} only if all three pass and 503 with a per-check JSON breakdown (or {\"status\": \"shutting_down\"}) otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:401-449"
  - statement: "readiness_handler's body (crates/buzz-relay/src/router.rs:410-449) contains no call into the metrics-rs facade (no counter!, gauge! or histogram! of any kind), so a readiness failure at the relay is visible only in the HTTP response body and in whatever a Kubernetes probe does with it -- unlike buzz-push-gateway, whose readiness check calls record_readiness_failure(cause), incrementing the push_gateway_readiness_failures_total counter with a cause label, which is the exact series PushGatewayReadinessAuthorityFailing (prometheusrule.yaml:41-51) alerts on."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:410-449"
      - "crates/buzz-push-gateway/src/metrics.rs:107-120"
  - statement: "ADR-0007-dependency-update-path.md and ADR-0008-security-audit-privilege.md both use the word \"alert\" to mean a GitHub-native security signal -- Dependabot dependency alerts (ADR-0007) and secret-scanning alerts (ADR-0008) -- a namespace those two decisions govern and that is unrelated to Prometheus/Alertmanager-shaped system alerting; ADR-0007 records that Dependabot's alerts feature specifically was, at that decision's time, admin-gated and left disabled, with the gap assigned to a separate issue rather than resolved by that ADR."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0007-dependency-update-path.md"
      - "launchpad/decisions/ADR-0008-security-audit-privilege.md"
  - statement: "No accepted decision record under launchpad/decisions/ was found addressing Prometheus/Alertmanager-shaped system alerting policy -- which alerts should exist, what severities mean, who is paged -- for buzz-relay or buzz-push-gateway; the alert set this node documents exists only as chart-authored PrometheusRule content and prose in docs/push-gateway-deployment.md, with no governing ADR located for either."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0007-dependency-update-path.md"
      - "launchpad/decisions/ADR-0008-security-audit-privilege.md"
      - "grep_repo(pattern='alert', scope='launchpad/decisions/') -> 3 files matched (ADR-0007, ADR-0008, ADR-0012), none concerning Prometheus/Alertmanager system alerting"
    confidence: 0.75
  - statement: "launchpad/Research/324-alert-to-issue-prior-art.md surveys off-the-shelf receivers (pfnet-research/alertmanager-to-github, m-lab/alertmanager-github-receiver) and a GitHub-Actions-workflow alternative for turning a fired alert into a GitHub issue, and launchpad/Research/325-alert-duplicate-suppression.md researches Alertmanager/Grafana anti-flap controls (pending period, keep_firing_for, group_by) -- both dated 2026-08-22 and framed as prior-art research for a pipeline not yet built in this repository, not as a description of anything currently running."
    entry_class: FACT
    evidence:
      - "launchpad/Research/324-alert-to-issue-prior-art.md"
      - "launchpad/Research/325-alert-duplicate-suppression.md"
  - statement: "layers-observability-prometheus, layers-observability-health-checks and layers-observability-metrics are present in the origin/launchpad corpus tree at the recorded revision and each cover, respectively, the Prometheus exposition mechanism, the relay's health/liveness/readiness probe surface, and (per its own scope) the catalog of Buzz-specific metric series -- the three mechanisms this node's alert-worthy-signals table draws on without restating their content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/prometheus.md"
      - "launchpad/docs/corpus/layers/observability/health-checks.md"
  - statement: "Issue #1209's dispatch brief for this Feature (#618) requires that where this repository ships no alert definitions for a given surface, the document state that plainly, cite the searches that establish it, and document the real signals an operator would have to build alerts from instead of importing a generic SRE alerting playbook."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1209 dispatch brief for Feature #618"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a reference-description paragraph, structured entries ordered to match the source's own order, an optional Commands table, an explicit boundary statement, relationships per its own guidance, and a scope-and-omissions section separating what is not covered from what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: layers-observability-prometheus
  - type: references
    target: layers-observability-health-checks
  - type: references
    target: layers-observability-metrics
---

# Alerting: reference

This node catalogues every alert-firing rule this repository actually defines,
and, where none exists for a surface, the signal an operator would have to
build one from instead. It is linked from an operator standing up or running
a Buzz relay or push-gateway deployment who needs to know what will page them
today, as distinct from what merely *could* be measured. Read it alongside
`layers-observability-prometheus` (how metrics reach a scrapeable endpoint at
all), `layers-observability-health-checks` (the probe surface several of the
signals below come from) and `layers-observability-metrics` (the fuller
metric catalog); this node does not restate any of the three.

**The central finding, stated first because it is the point of this
document:** `buzz-relay` itself defines zero alert rules. The only
`PrometheusRule` anywhere in this repository belongs to `buzz-push-gateway`,
a separate, optional service, and even that one rule set ships disabled by
default and stays disabled under the chart's own production values overlay
unless an operator explicitly turns it on.

## Alert rules that exist

The five alerts below are the entire alert-rule surface of this repository.
All five live in one `PrometheusRule` resource,
`deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml`, rendered
only when `prometheusRule.enabled=true` is set at install time. Ordered as
they appear in that file.

| Alert | Fires when | `for` | Severity | Operator action |
|---|---|---|---|---|
| `PushGatewayConfigurationFault` | any rate of `push_gateway_apns_deliveries_total{outcome="configuration_fault"}` | 10m | critical | The APNs certificate, topic or environment is misconfigured. No endpoints are being invalidated; deliveries are simply failing. Check the APNs certificate identity and topic. |
| `PushGatewayAdmissionUnavailable` | any rate of `push_gateway_admissions_total{result="unavailable"}` | 5m | critical | The PostgreSQL authority store is unreachable or failing at the admission seam. Check DB connectivity and the pod's Postgres-egress `NetworkPolicy`. |
| `PushGatewayReadinessAuthorityFailing` | any rate of `push_gateway_readiness_failures_total{cause="authority"}` | 5m | warning | Readiness is failing on the authority check; replicas will be pulled from the Service. Fix DB health before capacity drops below the `PodDisruptionBudget`. |
| `PushGatewayReaperFailing` | `push_gateway_reaper_failures_total` increases by 2+ within a 30m window (the reaper runs every 5m) | 5m | warning | Expired reservations are not being swept, growing the bounded-until-expiry window. Check DB write availability. |
| `PushGatewayHighApnsRetryRate` | retryable fraction of `push_gateway_apns_deliveries_total` over 10m exceeds `prometheusRule.apnsRetryRatioThreshold` (default `0.25`), gated by `prometheusRule.apnsRetryMinSamples` (default `20`) attempts | 15m | warning | APNs is throttling or degrading (429/500/503 outcomes). Deliveries are delayed, not lost. |

`docs/push-gateway-deployment.md` documents the identical table in prose
alongside the metrics it is built from; this table is the structured form of
that same source, cross-checked directly against the chart template rather
than copied from the prose.

**This rule set is opt-in twice over.** `prometheusRule.enabled` defaults to
`false` in the chart's `values.yaml`, and the chart's production values
overlay, `values-production.yaml`, does not set it either -- so an operator
rendering the chart with the checked-in production values still gets no
alert rules unless they add `--set prometheusRule.enabled=true` themselves.
The chart's own render tests hold both directions of this: a default render
carries no `PodMonitor` or `PrometheusRule` at all, and a render with
`prometheusRule.enabled=true` set must produce a `PrometheusRule` whose
`spec.groups` is non-empty. A malformed override is also tested: setting
`apnsRetryRatioThreshold` to `2` -- outside the `0..1` fraction the alert
expression assumes -- fails chart schema validation rather than rendering a
rule that could never usefully fire.

## Signals that exist with no alert rule

Nothing below is wired to a `PrometheusRule`, an Alertmanager route, or any
other paging mechanism found in this repository. These are the raw material
an operator building relay-level alerting would start from.

| Signal | Where it lives | What it would need to become an alert |
|---|---|---|
| `/_liveness` (relay, unconditional 200 OK) | Health-only listener, `crates/buzz-relay/src/router.rs:405-407` | A scrape or synthetic probe outside this repository; the handler itself performs no check and records no metric on failure. |
| `/_readiness` (relay; checks Postgres, Redis, deletion-serving catalog under a 2s timeout) | Health-only listener, `crates/buzz-relay/src/router.rs:410-449` | The handler records no metric on failure at all -- no counter, gauge or histogram call appears in its body. An alert would need either a metric added at this call site or an external prober scraping the HTTP status directly; today the failure is visible only in the JSON response body and to whatever already polls it (a Kubernetes probe). |
| The relay's Prometheus metric catalog (`http_requests_total`, `http_request_latency_ms`, and the `buzz_*` series `layers-observability-metrics` catalogues) | Scraped via the relay's `ServiceMonitor` (`deploy/charts/buzz/templates/servicemonitor.yaml`, opt-in) | A `PrometheusRule` resource -- none exists in this chart. Every series is already exposed and scrapeable; nothing thresholds any of them. |
| The relay's `ServiceMonitor` itself | `deploy/charts/buzz/values.yaml` (`serviceMonitor.enabled`, default `false`) | Enabling the `ServiceMonitor` is a precondition for any Prometheus-based alert on relay metrics, and it is off by default -- an operator who has not turned it on has no relay series to alert on regardless of any rule that might exist. |

Contrast this against `PushGatewayReadinessAuthorityFailing` above: the
push-gateway's readiness check calls `record_readiness_failure(cause)`,
incrementing a labelled counter, and that counter is exactly what the
existing alert thresholds. The relay's readiness check has no equivalent
counter, so the same *kind* of alert cannot be written for the relay without
first adding the metric the push-gateway already has.

## Commands

| Command | What it does |
|---|---|
| `helm template push deploy/charts/buzz-push-gateway --set prometheusRule.enabled=true` | Renders the `PrometheusRule` above (and only it -- `podMonitor` and `networkPolicy.monitoring` are separate flags gating scrape access, not alert rendering). |
| `helm template push deploy/charts/buzz-push-gateway --set prometheusRule.enabled=true --set prometheusRule.apnsRetryRatioThreshold=0.4 --set prometheusRule.apnsRetryMinSamples=50` | Overrides the two configurable thresholds on `PushGatewayHighApnsRetryRate`; every other alert's thresholds are fixed in the template. |
| `kubectl get prometheusrule -n <namespace>` | Lists any installed `PrometheusRule` objects in a live cluster -- the only way to confirm whether the opt-in rule set above was actually installed, as distinct from merely being renderable. |

## Boundary

This node does not describe:

- **Why these five thresholds and severities were chosen**, or the general
  design of Prometheus/Alertmanager alerting -- that is explanation, not
  reference, and no concept/explanation node for it exists yet to link.
- **How to install, upgrade, or operate the push-gateway or relay chart**
  step by step -- that is a how-to/procedure concern; `docs/push-gateway-deployment.md`
  already carries that content and it is not restated here.
- **An API Reference for a monitoring vendor's own alerting API** (Alertmanager's,
  Grafana's, or PagerDuty's) -- this node stays inside what this repository
  ships, not a third party's full surface.
- **Metrics, logs, traces, or dashboards as their own subjects.** Those are
  sibling reference nodes for this same Feature, being authored alongside
  this one (`document operations/observability/metrics`,
  `operations/observability/logs`, `operations/observability/traces`,
  `operations/observability/dashboards`). None of them exist in this corpus
  yet, so none is linked here by path or by `relationships` edge; this node
  names them only to draw its own boundary; it says nothing about their
  content, and confirming their eventual node ids is out of scope for this
  document.
- **Whether any Alertmanager, Grafana, or paging receiver is actually
  configured** for wherever this fork's images are deployed. This repository
  carries only the chart-authored `PrometheusRule` template; whether a real
  cluster routes its alerts anywhere is not answerable from this repository
  alone -- see *Scope and omissions*.
- **GitHub-native "alerts"** -- Dependabot dependency alerts and
  secret-scanning alerts are a different namespace entirely, governed by
  `ADR-0007-dependency-update-path.md` and
  `ADR-0008-security-audit-privilege.md` respectively. This node is scoped to
  Prometheus/Alertmanager-shaped system alerting only.

## Relationships

- `references` -> `layers-observability-prometheus`: the exposition mechanism
  (the embedded HTTP listener, the `GET /metrics` endpoint) that any
  Prometheus-based alert, existing or hypothetical, depends on for its data.
- `references` -> `layers-observability-health-checks`: the probe surface
  (`/_liveness`, `/_readiness`) named in the *Signals that exist with no
  alert rule* table above.
- `references` -> `layers-observability-metrics`: the fuller catalog of
  named metric series this node's tables draw single examples from without
  reproducing the catalog itself.

All three are `references` edges -- supporting context, no ownership or
currency dependency implied -- and all three were confirmed present in
`origin/launchpad`'s corpus tree before this front matter was finalized (via
the batch's own `existing-node-ids.txt` snapshot, per this task's dispatch
instructions, rather than this worktree's local tree). No edge is declared
to any `operations/observability/*` sibling: none of them exist as ids on
`origin/launchpad` at the recorded revision, and declaring one would be a
hard validation error the moment this node reached the merge branch ahead of
whichever sibling introduces it.

## Scope and omissions

**This node covers** every alert-firing rule (`PrometheusRule`) defined
anywhere in this repository, the exact conditions and actions each one
encodes, how firmly opt-in the one rule set that exists actually is, and,
for the surfaces that have no alert rule at all (chiefly the relay), the
concrete signals -- probes and metrics -- an operator would have to start
from to build one.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Prometheus exposition mechanism itself (the embedded listener, `GET /metrics`) | `layers-observability-prometheus` |
| The relay's health/liveness/readiness probe surface in full depth | `layers-observability-health-checks` |
| The catalog of named metric series and what each measures | `layers-observability-metrics` |
| The metrics reference for this same operations Feature | `document operations/observability/metrics`, #1212, unmerged at the recorded revision |
| The logs reference for this same operations Feature | `document operations/observability/logs`, #1211, unmerged at the recorded revision |
| The traces reference for this same operations Feature | `document operations/observability/traces`, #1213, unmerged at the recorded revision |
| The dashboards reference for this same operations Feature | `document operations/observability/dashboards`, #1210, unmerged at the recorded revision |
| GitHub-native Dependabot/secret-scanning alerting | `ADR-0007-dependency-update-path.md`, `ADR-0008-security-audit-privilege.md` |
| Whether any Alertmanager/Grafana/paging receiver is configured for a live deployment of this fork | Not established by this repository; see below |
| An alert-fires-a-GitHub-issue pipeline | `launchpad/Research/324-alert-to-issue-prior-art.md`, `325-alert-duplicate-suppression.md` -- research toward a pipeline not yet built |

**Expected but not verified when this node was written:**

- **Whether the push-gateway's `PrometheusRule` has ever actually fired in a
  running deployment.** This repository's render tests confirm the rule
  renders and that its `spec.groups` is non-empty when enabled; nothing in
  this repository shows the rule installed in a live cluster or evaluated by
  a running Prometheus/Alertmanager, and no such evidence was located.
- **Whether any Alertmanager route, receiver, or paging integration exists
  outside this repository** for wherever this fork's `buzz-relay` or
  `buzz-push-gateway` images are actually deployed. A `PrometheusRule`
  resource only defines *what* would fire; *who gets told* is Alertmanager
  configuration this repository does not carry, and its existence or absence
  in any operated cluster could not be checked from here.
- **Whether `#1212`'s eventual metrics reference will name every relay
  series a future alert rule could threshold on.** This node cites only the
  handful of series relevant to its own tables, not the full catalog.
