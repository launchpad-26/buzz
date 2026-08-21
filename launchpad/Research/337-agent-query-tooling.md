# Existing agent-facing query tooling for the Grafana stack

**Title:** Whether agent tooling for querying Grafana already exists, and what it can express
**Summary:** Yes, and it is first-party: `grafana/mcp-grafana`, maintained by Grafana Labs, actively developed with a commit on 2026-08-21. It covers Prometheus and Loki querying out of the box and has a `--disable-write` flag. Two gaps matter: there is no general Tempo/TraceQL query tool comparable to the Prometheus and Loki ones, only a narrow Sift `find_slow_requests`; and the two most diagnostically useful tools require Editor rather than Viewer, though per-datasource RBAC scopes offer a better third option whose availability on OSS Grafana is unconfirmed.
**Tags:** `observability` `agents` `mcp` `grafana` `tooling` `rbac`
**Reviewed:** 2026-08-22 · **Answers:** [#337](https://github.com/launchpad-26/buzz/issues/337)

---

## Finding

**Yes — and it is first-party. `grafana/mcp-grafana`, maintained by Grafana Labs**, an MCP server giving an AI assistant structured access to a Grafana instance.

**Maintenance is healthy:** last commit **2026-08-21**, release v1.1.0 on 2026-08-10, 3,379 stars, not archived.

**It has a `--disable-write` flag** disabling every mutation across dashboards, incidents, alerting, OnCall, annotations and snapshots. With [#336](https://github.com/launchpad-26/buzz/issues/336)'s Viewer-role service account, criterion 4's agent can be read-only at two independent layers.

**Two gaps matter.** There is **no general Tempo/TraceQL query tool** comparable to the Prometheus and Loki ones — only a narrow, opt-in, Editor-requiring Sift tool. And **the two most diagnostically useful tools require Editor, not Viewer**, which is in direct tension with least privilege.

---
## What it is and what it exposes

**Maintainer: Grafana Labs.** A Model Context Protocol server *"that provides AI assistants like Claude with structured access to Grafana instances and their surrounding observability ecosystem."*

**Enabled by default:**

| Area | Operations |
|---|---|
| **Prometheus** | PromQL queries, metric metadata, histogram percentiles |
| **Loki** | LogQL queries, log patterns, label discovery |
| Dashboards | Search, retrieve, create, update, patch, query panels |
| Alerting | Rules, routing, silences, contact points |
| Incidents | Create, update, search |
| Grafana OnCall | Schedules, shifts, alert groups, teams |
| Annotations | Create, update, retrieve with filters |
| Snapshots | List, create, delete, retrieve |
| Rendering | Panels and dashboards as PNG |
| Navigation | Deeplink generation |

**Disabled by default** (opt-in): InfluxDB, ClickHouse, CloudWatch, Elasticsearch/OpenSearch, Quickwit, Athena, Snowflake, Graphite, Agent Observability, Grafana Assistant, query examples, run-panel-queries, admin operations, Sift investigations, **Pyroscope profiling**.

### Credential and scoping

- **`GRAFANA_SERVICE_ACCOUNT_TOKEN`**, or username/password. Optional custom headers, org ID, and mTLS certificates.
- Supports fine-grained RBAC permissions and scopes; built-in roles work too, with **Editor recommended for broad access**.
- **`--disable-write`** disables all mutations across dashboards, incidents, alerting, OnCall, annotations, snapshots and experimental features.

Note the tension worth flagging: the project **recommends Editor** for broad access, while #336 establishes that **Viewer** is the read-only role. For an agent that only diagnoses, Viewer plus `--disable-write` is the conservative pairing, and it may cost some tool coverage. Nobody has tested which tools still work under Viewer.

### Distribution

`uvx` (recommended), Docker Hub (`grafana/mcp-grafana`), compiled binaries from GitHub releases, Go source, or a Helm chart. That is unusually good coverage — it can run wherever the cohort's agent runs.

### Stated limitations

- **Grafana 9.0+** required for full functionality; earlier versions lack the datasource API endpoints.
- **Large dashboards consume significant token context.** Mitigations exist — `get_dashboard_summary`, and `get_dashboard_property` with JSONPath.
- Image rendering needs a **separate Grafana Image Renderer service**.
- **Loki query cost guardrails are optional**, to prevent terabyte-scale unintended scans. Worth turning on: an agent writing its own LogQL is exactly the client that issues an accidentally unbounded query.
- InfluxDB tools infer SQL dialect from datasource config.

---

## The gap that matters

**Traces are not in the tool list I retrieved.** Prometheus and Loki each have named query tools. Tempo does not appear, in the default set or the opt-in set — the opt-in list covers other *datasources* (ClickHouse, Athena, Snowflake…) and Pyroscope profiling, but not tracing.

If that is accurate, then for criterion 3 — *"comparing what happened on that client against what happened on the others and on the relay at the same moment"* — **the agent could read logs and metrics through this server and would need something else for traces.** That is not fatal; the generic `run-panel-queries` tool is in the opt-in list and might reach a Tempo-backed panel, and the Grafana HTTP API is available directly regardless. But it is the difference between "configure an existing tool" and "configure it and write the trace path yourself".

**I am flagging this rather than asserting it.** It is an absence in a retrieved summary, and an absence is weaker evidence than a statement. See below.

---

## What this means for #289

1. **Criterion 4 is adopt, not build — for two of three signals.** A first-party, actively distributed MCP server covers logs and metrics query out of the box.
2. **Read-only is achievable at two layers**: `--disable-write` on the server, Viewer role on the token. Defence in depth for the credential #289 flags as a risk, and neither layer requires trusting the other.
3. **The trace gap should be checked before criterion 4 is scoped**, because criterion 3 is the acceptance test and it is a trace comparison. This is a ten-minute check against the tool list of a current release.
4. **Turn on Loki's query cost guardrails.** An agent composing its own LogQL against a laptop-hosted stack is precisely the scenario an unbounded scan ruins — and #331 measured that stack is running on one machine.
5. **Watch the context cost.** Large dashboards eating agent context is a stated limitation with named mitigations; worth knowing before an agent is pointed at a dashboard-heavy instance.
6. **Editor-versus-Viewer needs resolving.** The project recommends Editor; #336 establishes Viewer as read-only. Someone should determine which tools actually work under Viewer rather than taking the broader grant by default.

---

## Confidence and what is still unknown

**High confidence** on the project's existence, maintainer, credential model, `--disable-write` flag, distribution methods and stated limitations — all from its own README.

**The trace gap is the weakest claim here and the most consequential.** It rests on Tempo not appearing in a retrieved summary of the tool list. **An absence in a summary is not proof of an absence in the product.** I did not enumerate the tools from source or from a running instance, and the retrieval may simply have omitted it. Anyone acting on this should check the current release's tool list directly — and that check is worth doing before criterion 4 is scoped, precisely because criterion 3 depends on the answer.

**Not verified: I did not install or run it.** No MCP server was started, no tool invoked, no query issued through it. I did not check its maintenance status — commit recency, release cadence, open issue count — which [#324](https://github.com/launchpad-26/buzz/issues/324) demonstrated can be decisive between two superficially similar projects, and which would have been one API call. That is an omission rather than a limitation.

**Also not researched:** third-party alternatives, so I cannot say this is the best option, only that it is the first-party one and that it exists; whether it works against a self-hosted OSS Grafana as well as Grafana Cloud, where several listed tools (OnCall, Incidents, Sift, Grafana Assistant) are Cloud features that would presumably be inert; whether the cohort's own agent harness in `launchpad/agents/` can consume an MCP server at all, which is the practical integration question and entirely unexamined; and token-context cost in practice.

## Maintenance and the trace question, checked

```
pushed_at: 2026-08-21T20:44:04Z  archived: false  open_issues: 119  stars: 3379
last commit: 2026-08-21T11:03:11Z
latest release: v1.1.0 @ 2026-08-10T09:45:22Z
```

Actively maintained — it passes the same check that found #324's alternative receiver three years stale.

**On traces:** Tempo does appear in the README (51 code matches), but most mentions are the MCP server **emitting its own traces**, not querying yours:

```bash
# Send traces to a local Tempo instance
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
OTEL_EXPORTER_OTLP_INSECURE=true \
./mcp-grafana -t streamable-http
```

There is exactly one trace-**querying** tool, and it is narrow:

```
| `find_slow_requests` | Sift | Finds slow requests from the relevant tempo datasources. | Editor role |
```

A single Sift tool, in the disabled-by-default set, answering "what was slow" rather than criterion 3's "what differed for this member". For criterion 3 the agent would still need the Grafana HTTP API directly, or the opt-in `run-panel-queries` tool against a Tempo-backed panel.

## The permissions tension, and a better third option

The README's per-tool permissions column makes the problem concrete:

```
| `list_sift_investigations` | Sift | ...list of Sift investigations...           | Viewer role |
| `find_error_pattern_logs`  | Sift | Finds elevated error patterns in Loki logs. | Editor role |
| `find_slow_requests`       | Sift | Finds slow requests from tempo datasources. | Editor role |
```

**The two tools that would actually help diagnose the huddle fault — elevated error patterns in logs, and slow requests in traces — both require Editor.** A Viewer-only agent, which #336 recommends on least-privilege grounds, loses exactly those two.

A third option exists and is better than the binary. The same table shows fine-grained RBAC scopes per tool:

```
| `list_pyroscope_label_names` | Pyroscope | ... | `datasources:query` | `datasources:uid:pyroscope-uid` |
```

Tools can be granted by **action and datasource UID** rather than by broad role — query rights on named datasources and nothing else.

**Caveat, and it is the open question.** #336 recorded that fine-grained RBAC is a **Grafana Enterprise** feature. If so, this option is unavailable on the self-hosted OSS Grafana #289 implies, and the cohort is back to a binary with the two most useful tools on the wrong side of it. **Whether these scopes work on OSS Grafana is unconfirmed and is now the most important open question here.**

---

## Sources

- [grafana/mcp-grafana](https://github.com/grafana/mcp-grafana) — the project, its tools, credential model, `--disable-write`, distribution and limitations
- [Service accounts — Grafana documentation](https://grafana.com/docs/grafana/latest/administration/service-accounts/) — the token and role model it consumes, via [#336](https://github.com/launchpad-26/buzz/issues/336)
