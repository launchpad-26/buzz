---
id: operations-observability-dashboards
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "launchpad/docs/Observability/current-state/coverage.md's explicit-exclusions table carries a row 'X05 | Operations platform | Collection, storage, querying, dashboards, alerts, retention, and deployment | Infrastructure after product export surfaces | Separate buzz-infrastructure repository and deployed systems | buzz-infrastructure#113 | ... | Excluded | PRD #289 routes infrastructure collection/storage/dashboards/alerts/retention/deployment to #113', and repeats the same routing sentence verbatim in its closing paragraph."
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/coverage.md"
  - statement: "launchpad/docs/Observability/current-state/overview.md states that 'External collection, storage, querying, dashboards, and operational deployment begin after the product export boundaries and are not treated as product instrumentation', and launchpad/docs/Observability/current-state/relay.md states, for the relay specifically, that 'Collection, storage, querying, dashboards, and deployment are likewise outside the relay runtime unless they affect whether a relay-produced signal crosses its export boundary.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/overview.md"
      - "launchpad/docs/Observability/current-state/relay.md"
  - statement: "No file under deploy/charts/buzz/, deploy/charts/buzz-push-gateway/, or the repository's compose files (docker-compose.yml, docker-compose.harness.yml, deploy/compose/compose.dev.yml, deploy/compose/compose.yml, deploy/compose/compose.caddy.yml) mentions Grafana or a dashboard resource; the only monitoring-adjacent Helm templates present are a ServiceMonitor for the relay and a PodMonitor plus a PrometheusRule for buzz-push-gateway, none of which define a dashboard."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/servicemonitor.yaml"
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz-push-gateway/templates/podmonitor.yaml"
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml"
      - "deploy/charts/buzz-push-gateway/values.yaml"
      - "deploy/compose/compose.dev.yml"
  - statement: "A repository-wide search for a Grafana dashboard export (files matching *dashboard*.json, and directories named *grafana*) found none, and a repository-wide search for the words 'grafana' or 'dashboard' across YAML, JSON, and Markdown files found no hit outside documentation, research notes, and the moderation/feedback admin surface described below."
    entry_class: INFERENCE
    evidence:
      - "grep_and_find(patterns=['grafana', 'dashboard'], scopes=['**/*.yml','**/*.yaml','**/*.json','**/*.md'], and find(name='*dashboard*.json')) -> no Grafana dashboard JSON found; textual hits confined to documentation/research/admin-dashboard sources cited in this node"
    confidence: 0.85
  - statement: "deploy/charts/buzz/values.yaml sets serviceMonitor.enabled to false by default (interval 30s, scrapeTimeout 10s), and the relay's opt-in ServiceMonitor template selects the chart's own Service by its selector labels and scrapes the port named 'metrics'."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/templates/servicemonitor.yaml"
  - statement: "deploy/charts/buzz-push-gateway/values.yaml sets podMonitor.enabled to false by default (interval 30s, scrapeTimeout 10s), and the PodMonitor template scrapes only the push-gateway's private 'health' port at path /metrics, never the public Service."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/values.yaml"
      - "deploy/charts/buzz-push-gateway/templates/podmonitor.yaml"
  - statement: "The repository's dev-compose stack (deploy/compose/compose.dev.yml) runs a standalone prom/prometheus:latest container named buzz-prometheus, mounting the root prometheus.yml scrape config; no Grafana or other dashboarding container is defined alongside it."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.dev.yml"
  - statement: "docs/admin/README.md, titled 'Deployment moderation dashboard', states that 'Buzz can expose a private, deployment-wide moderation dashboard from the existing relay process. It shows open moderation reports and recent product feedback', activated by setting BUZZ_ADMIN_HOST plus BUZZ_ADMIN_WEB_DIR and an authentication mode (nip98 or disabled)."
    entry_class: FACT
    evidence:
      - "docs/admin/README.md"
  - statement: "The Justfile's admin recipe is commented '# Build and run the private admin dashboard', builds admin-web, sets BUZZ_ADMIN_HOST/BUZZ_ADMIN_WEB_DIR/BUZZ_ADMIN_AUTH defaults for local use, and echoes 'Admin dashboard: http://<host>/reports' before running the relay; admin-seed is commented '# Seed deterministic reports and product feedback for local admin dashboard review'; admin-check is commented '# Run focused relay and browser checks for the admin dashboard' and runs relay unit tests plus admin-web's own checks and e2e suite."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "crates/buzz-relay/src/api/admin/mod.rs's module doc names the surface 'Private deployment moderation API', mounts only under /api/admin/v1 when the relay's admin config is present, and registers read routes for /probe, /reports, /reports/{id}, /feedback, /feedback/{id}, plus mutation routes to resolve/reopen/cancel a report, update feedback status, and staffing routes (GET/PUT/DELETE /operators) -- no route in this router serves a metric, a log, a trace, or a chart."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs"
  - statement: "crates/buzz-relay/src/api/admin/auth.rs implements two access modes for this admin API -- AdminAuth::Disabled (reads pass, mutations 403 via require_mutation_principal) and AdminAuth::Nip98 (every request must carry a NIP-98-signed event, resolved to an AdminPrincipal with role Operator or Moderator via resolve_admin_principal) -- and authorize() additionally requires the request's Host header to match the configured admin host (is_admin_host) and, when present, an Origin header matching that same host, before any principal is granted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs"
  - statement: "crates/buzz-relay/src/router.rs mounts the admin API only when state.config.admin.is_some(), serves the admin-web static bundle only on requests whose Host matches the configured admin host (is_admin_host), and applies a restrictive Content-Security-Policy (ADMIN_CSP: \"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'\") to every response served on that host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "admin-web/src/App.tsx renders exactly four views -- titled 'Open reports', 'Report detail', 'Feedback', and 'Feedback detail' -- consistent with docs/admin/README.md's own route list (/reports, /reports/:id, /feedback, /feedback/:id) and consistent with the relay's admin router; none of the four views renders a metric, a time-series chart, or a log/trace viewer."
    entry_class: FACT
    evidence:
      - "admin-web/src/App.tsx"
      - "docs/admin/README.md"
  - statement: "docs/admin/README.md states that access additionally requires a private ingress ('A private ingress limits access to the operator VPN or approved source IPs'), that in nip98 mode a NIP-07 browser extension signs every request with the resolved principal's Nostr key, and that in disabled mode 'the entire moderation and feedback dataset is exposed' if the admin API is reachable by untrusted clients, so operators are told to prefer nip98 mode and to treat network-layer isolation as the sole control only when it is genuinely present."
    entry_class: FACT
    evidence:
      - "docs/admin/README.md"
  - statement: "launchpad/docs/corpus/capabilities/moderation/operator-dashboard.md documents a different, already-shipped dashboard: a per-community owner/admin panel inside the desktop app's Settings surface (ModerationQueueCard), reached over the /moderation/* endpoints and NIP-29 community roles, distinct from the deployment-wide, NIP-98-or-network-authenticated /api/admin/v1 console this node describes -- that node's own Maturity section states the platform-side escalation inbox 'is a separate build' from the shipped community panel, and this node's admin-dashboard evidence above is that separate, already-shipped surface."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/capabilities/moderation/operator-dashboard.md"
  - statement: "launchpad/docs/corpus/layers/observability/prometheus.md documents the relay's Prometheus exposition mechanism (the embedded HTTP listener on port 9102 serving GET /metrics) as the substrate a metrics dashboard would scrape, and explicitly scopes itself to that exposition mechanism only, not to any dashboard or the catalog of series it exposes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/prometheus.md"
  - statement: "A separate, already-merged corpus node (architecture-context-relay-operator) defines 'the relay operator' as the role responsible for provisioning, deploying and administering the running buzz-relay process and its stateful dependencies -- the audience this node's Commands and Configuration sections are written for."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/relay-operator.md"
  - statement: "launchpad/Research/327-grafana-stack-components.md, a reviewed research note answering issue #327, finds that a self-hosted Grafana stack (Prometheus, Loki, Tempo, Grafana itself for query/dashboards/alerting, plus an OTel collector) is the minimum component set that would satisfy the observability platform this PRD is planning, and observes that 'the relay exposes Prometheus metrics on :9102, so a Prometheus scrape needs no translation layer' -- confirming this is planning research toward a future, separately-hosted platform, not a description of anything currently deployed in this repository."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#327, recorded in launchpad/Research/327-grafana-stack-components.md"
  - statement: "buzz-infrastructure#113 is the tracking issue PRD #289 names for the operations-platform work (collection, storage, querying, dashboards, alerts, retention, deployment) excluded from this repository's product-observability scope; it lives in a separate repository this task did not open, so its current state and any dashboard work already done there is not established by this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issue #289, and the X05 row of launchpad/docs/Observability/current-state/coverage.md that cites it"
  - statement: "The three relationship targets this node declares resolve on origin/launchpad at the revision this node records: launchpad/docs/corpus/layers/observability/prometheus.md declares id layers-observability-prometheus, launchpad/docs/corpus/capabilities/moderation/operator-dashboard.md declares id capabilities-moderation-operator-dashboard, and launchpad/docs/corpus/architecture/context/relay-operator.md declares id architecture-context-relay-operator; a dispatch-time listing of every id resolving on origin/launchpad contains no operations/observability/* id and no capabilities-type node for the deployment-wide admin dashboard this node describes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/prometheus.md"
      - "launchpad/docs/corpus/capabilities/moderation/operator-dashboard.md"
      - "launchpad/docs/corpus/architecture/context/relay-operator.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to open with a Reference description, follow with structured entries (a table, ordered to match the material's own order rather than alphabetically), optionally add a Commands table for CLI-shaped content, state an explicit Boundary against the concept/explanation and how-to/procedure templates, declare Relationships, and close with Scope and omissions naming both what is excluded and what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: layers-observability-prometheus
  - type: references
    target: capabilities-moderation-operator-dashboard
  - type: references
    target: architecture-context-relay-operator
---

# Dashboards: reference

This node catalogues what this repository ships that a reader might call a
"dashboard" in an operations or observability context: the surfaces that exist,
the one surface actually named a dashboard, and the boundary that keeps the two
from being confused. It is linked from an operator standing up a relay who is
looking for a metrics/observability dashboard and needs to know, quickly, that
none ships here and where the substrate for one lives instead.

**The central fact this node exists to record:** this repository defines no
observability dashboard. No Grafana dashboard JSON, no dashboard-provisioning
directory, and no chart/panel definition of any kind is present anywhere in this
checkout. That is a deliberate, documented scope boundary (see *Structured
entries* below), not an oversight this node is reporting as a gap to fill.

## Structured entries

Ordered from the surface closest to "a dashboard" to the surface furthest from
it -- not alphabetically, per the reference template's convention.

| Surface | What it is | Is it a dashboard? |
|---|---|---|
| Private admin console (`admin-web/` + `crates/buzz-relay/src/api/admin/`, mounted at `/api/admin/v1`) | A deployment-wide, `BUZZ_ADMIN_HOST`-gated web console with four views (`Open reports`, `Report detail`, `Feedback`, `Feedback detail`) for triaging moderation reports and product feedback. `docs/admin/README.md` and the `Justfile`'s `admin`/`admin-seed`/`admin-check` recipes call it "the (private) admin dashboard." | **This is the one thing this repository actually calls a "dashboard."** It is a moderation/feedback console, not an observability dashboard -- no route in `crates/buzz-relay/src/api/admin/mod.rs` serves a metric, log, trace, or chart. See *Boundary*. |
| Community moderation panel (desktop Settings -> Moderation) | A per-community owner/admin panel documented by the already-merged `capabilities-moderation-operator-dashboard` node, reached over `/moderation/*` and community roles rather than `/api/admin/v1` and deployment-wide roles. | No -- a different, already-documented capability. See *Boundary*. |
| Relay Prometheus exposition (`GET /metrics`, default port 9102) | The embedded HTTP listener `PrometheusBuilder` binds inside `buzz-relay`, serving Prometheus text-format output for every metric recorded through the `metrics`-rs facade. Documented in full by `layers-observability-prometheus`. | No -- this is raw, unvisualized metric data. It is the substrate a dashboard would query, not a dashboard. |
| Helm `ServiceMonitor` (`deploy/charts/buzz/templates/servicemonitor.yaml`) | Opt-in (`serviceMonitor.enabled`, default `false`) Prometheus Operator resource that tells a cluster's Prometheus to scrape the relay's `metrics`-named Service port on a 30s interval. | No -- this wires scraping, it defines no query, panel, or visualization. |
| Helm `PodMonitor` + `PrometheusRule` (`deploy/charts/buzz-push-gateway/templates/{podmonitor,prometheusrule}.yaml`) | Opt-in (`podMonitor.enabled`, `prometheusRule.enabled`, both default `false`) equivalents for `buzz-push-gateway`: pod-level scrape config plus alerting-rule definitions. | No -- scrape wiring and alert rules, not a dashboard. Alerting itself is out of this node's scope (see *Boundary*). |
| Dev-compose Prometheus container (`deploy/compose/compose.dev.yml`, service `prometheus`) | A standalone `prom/prometheus:latest` container for local development, scraping the host-run relay via `host.docker.internal:9102`. | No -- Prometheus's own web UI is not a dashboard in the Grafana-panel sense, and no Grafana container is defined alongside it in this stack. |
| `buzz-infrastructure` repository (tracked at `buzz-infrastructure#113`) | The separate repository `PRD #289` names as the home for "collection, storage, querying, dashboards, alerts, retention, and deployment" once product signals cross this repository's export boundary. | **This is where a dashboard, if one is built, would be defined.** Not this repository, and this node cannot see that repository's current state. |

## Configuration

The one dashboard this repository ships is activated entirely through relay
environment configuration -- there is no separate deployment step beyond
configuring and serving it from the same relay process:

| Variable | Purpose | Default |
|---|---|---|
| `BUZZ_ADMIN_HOST` | Hostname that activates the admin dashboard and admin API when the relay's `Host` header matches it. Unset means the surface does not exist for any request. | unset (disabled) |
| `BUZZ_ADMIN_WEB_DIR` | Filesystem directory the relay serves the built `admin-web` SPA bundle from, on the admin host only. | unset |
| `BUZZ_ADMIN_AUTH` | Access mode: `nip98` (every request signed with a NIP-98 event, resolved to an Operator/Moderator principal) or `disabled` (reads pass unauthenticated; mutations still 403; relies entirely on network-layer isolation). Any other non-empty value is a startup error. | `nip98` when `BUZZ_ADMIN_HOST` is set and `BUZZ_ADMIN_AUTH` is unset |
| `RELAY_OPERATOR_PUBKEYS` | Comma-separated hex pubkeys granted the `Operator` role under `nip98` mode. | empty |
| `RELAY_OWNER_PUBKEY` | Implicit `Operator` fallback grant, active only while `RELAY_OPERATOR_PUBKEYS` is empty. | unset |

## Commands

| Command | Description | Argument | Example |
|---|---|---|---|
| `just admin` | Builds the `admin-web` bundle and runs the relay with `BUZZ_ADMIN_HOST`/`BUZZ_ADMIN_WEB_DIR` defaulted for local use (`BUZZ_ADMIN_AUTH` defaults to `disabled` locally). | none (reads `.env`) | `just admin` -> serves the dashboard at `http://admin.localhost:3000/reports` |
| `just admin-seed` | Seeds deterministic moderation reports and product-feedback fixtures, including real image/diagnostic attachments uploaded to local MinIO, so the dashboard has content to review. | none | run once before `just admin` |
| `just admin-check` | Runs the relay's admin-API unit tests (`cargo test -p buzz-relay api::admin`, `router::tests`) plus `admin-web`'s own checks and Playwright e2e suite. | none | `just admin-check` |

## Boundary

This node does not describe:

- **The metrics catalog, structured logging, distributed tracing, or alerting
  rules that a future dashboard would visualize or act on.** Those are separate,
  in-progress reference nodes under this same `operations/observability/`
  surface (tracked as issues #1212, #1211, #1213, and #1209 respectively, none
  merged at the time this node was written), and this node declares no
  relationship to any of them -- see *Scope and omissions*.
- **How the relay exposes the raw metrics a dashboard would query.** That
  mechanism -- the embedded Prometheus HTTP listener, its startup sequence, and
  its histogram-bucket configuration -- is `layers-observability-prometheus`'s
  subject; this node references it rather than restating it.
- **The community-level moderation dashboard's internal behavior** (report
  triage logic, enforcement actions, audit-log detail). That capability is fully
  documented by `capabilities-moderation-operator-dashboard`; this node only
  draws the boundary between it and the deployment-wide admin console described
  above.
- **The full `/api/admin/v1` HTTP contract** (every request/response shape,
  every error code). `docs/admin/README.md` is the authoritative route list;
  this node cites it rather than duplicating it, and no interface-family corpus
  node exists yet to hold that contract formally.
- **A procedure for standing up a Grafana-based observability stack.** No such
  stack exists in this repository. `launchpad/Research/327-grafana-stack-components.md`
  is a research note about what a future stack in `buzz-infrastructure` would
  need; it is not instruction for building one here, and this node does not
  convert research into a procedure the repository does not otherwise support.
- **Whether or when `buzz-infrastructure#113` will define an actual dashboard.**
  That is a separate repository this node did not open.

## Relationships

- `references`: `layers-observability-prometheus` -- the exposition mechanism
  that is the metrics substrate any future dashboard would query; this node
  names it as the nearest existing thing to "what a dashboard reads from" in
  this repository, without restating its content.
- `references`: `capabilities-moderation-operator-dashboard` -- the other,
  already-documented dashboard-shaped capability in this repository (the
  community-level moderation panel), cited for the boundary distinction drawn
  above: two different surfaces share the word "dashboard" and must not be
  conflated.
- `references`: `architecture-context-relay-operator` -- the role this node's
  *Configuration* and *Commands* sections are written for: the person
  responsible for provisioning and administering the running `buzz-relay`
  process, as distinct from a community owner/admin.

## Scope and omissions

**This node covers** every surface in this repository that could be called an
operational or observability "dashboard": the one surface actually named a
dashboard (the private, deployment-wide moderation/feedback admin console), the
surfaces that would feed a metrics dashboard if one existed (Prometheus
exposition, opt-in `ServiceMonitor`/`PodMonitor`, the dev-compose Prometheus
container), the community-level moderation panel that is a different capability
sharing the same word, the environment configuration and `just` commands that
operate the one shipped dashboard, and the explicit, documented boundary that
routes dashboard-as-code to a separate repository.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The metrics catalog -- what each Prometheus series measures | issue #1212 (`operations/observability/metrics.md`), unmerged at the time this node was written |
| Structured logging as an operational concern | issue #1211 (`operations/observability/logs.md`), unmerged |
| Distributed tracing as an operational concern | issue #1213 (`operations/observability/traces.md`), unmerged |
| Alerting rules and thresholds | issue #1209 (`operations/observability/alerts.md`), unmerged; note `buzz-push-gateway`'s `PrometheusRule` template exists today but is out of this node's scope |
| The Prometheus exposition mechanism's internals | `layers-observability-prometheus` (merged) |
| The community-level moderation dashboard's own behavior | `capabilities-moderation-operator-dashboard` (merged) |
| The full `/api/admin/v1` request/response contract | `docs/admin/README.md`; no interface-family corpus node yet |
| Whether the deployment-wide admin console (`admin-web` + `crates/buzz-relay/src/api/admin/`) deserves its own `capabilities`-type corpus node, parallel to the community-level one | Not decided here -- flagged as a candidate second concept for a future task |
| Collection, storage, querying, dashboards, alerts, retention, and deployment beyond this repository's product-export boundary | `buzz-infrastructure#113`, per PRD #289 / exclusion row X05 |

**Expected but not verified when this node was written:**

- **Whether the mobile app has any dashboard-like operational surface.**
  `mobile/lib` was not searched while drafting this node; PRD #289 excludes
  mobile from the current-state observability documentation this node draws on,
  but that exclusion is about product-observability scope, not proof that no
  mobile-side operational surface exists.
- **Whether the repository-wide search for a Grafana dashboard export is
  exhaustive.** The search covered common file-naming and content patterns
  (`*dashboard*.json`, the words "grafana"/"dashboard" across YAML/JSON/Markdown);
  it cannot rule out a differently-named or non-textual artifact, which is why
  that specific claim is classified `INFERENCE` rather than `FACT` above.
- **The current state of `buzz-infrastructure#113`.** That issue and repository
  were not opened while writing this node; whether any dashboard work has
  already started there is unknown from inside this repository.
- **Whether `admin-web`'s CSP and origin checks have been independently
  re-verified against a live deployment.** This node's claims about `ADMIN_CSP`
  and `is_admin_host` are grounded in reading `crates/buzz-relay/src/router.rs`
  and `crates/buzz-relay/src/api/admin/auth.rs` directly, not in exercising a
  running relay against them.
