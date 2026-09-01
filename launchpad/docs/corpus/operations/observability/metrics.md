---
id: operations-observability-metrics
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-relay's metrics.rs installs the global metrics-rs recorder and a Prometheus HTTP exporter, records http_requests_total{code,caller,action} and http_request_latency_ms{code,caller,action} in a dedicated Axum middleware named track_metrics, and explicitly skips /_*, /health and /metrics paths in that middleware to avoid unbounded cardinality from scanner and probe traffic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs"
  - statement: "WebSocket connection-lifecycle series recorded in buzz-relay are buzz_ws_connections_total{community} (counter, on successful connect), buzz_ws_connections_active (gauge, incremented after the auth challenge succeeds and decremented on cleanup), buzz_ws_auth_timeouts_total, buzz_ws_backpressure_disconnects_total, buzz_ws_send_batch_size (histogram of batched outbound send sizes), and buzz_subscriptions_active (gauge, incremented/decremented as REQ subscriptions are added and removed)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "Auth and admission-control series in buzz-relay are buzz_auth_attempts_total{method}, buzz_auth_failures_total{reason} (reasons include nip42_invalid, allowlist_denied, not_relay_member, observed directly in handlers/auth.rs), buzz_admission_rejections_total{transport,reason} (transport is \"websocket\" in connection.rs and \"http\" in api/bridge.rs), buzz_count_fallback_rejections_total, buzz_gif_search_rejections_total{reason}, buzz_media_upload_rejections_total{reason}, and buzz_req_global_access_resolution_skips_total{kind}, whose kind label is the fixed string literal \"13534\" at its one call site rather than a variable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/gifs.rs"
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Event-ingestion and fan-out series in buzz-relay are buzz_events_received_total{kind} and buzz_community_events_received_total{community} (both incremented once per accepted event, the community-scoped series carrying no kind label by the source comment's own design), buzz_events_rejected_total{transport,reason} (reason is documented in a doc comment as a closed four-value set: \"auth\"/\"invalid\"/\"scope\"/\"error\"), buzz_events_stored_total{kind,author_type}, buzz_event_processing_seconds, buzz_fanout_recipients (histogram of recipient counts per delivery), buzz_multinode_fanout_total, buzz_multinode_fanout_lag_total, buzz_cache_invalidation_lag_total and buzz_conn_control_lag_total (each incremented by the lagged-message count when a tokio broadcast receiver falls behind), and buzz_post_commit_dispatch_scheduled_total / buzz_post_commit_dispatch_errors_total{stage}."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "Membership and access-cache series in buzz-relay are buzz_membership_cache_hits_total / buzz_membership_cache_misses_total, buzz_accessible_channels_cache_hits_total / buzz_accessible_channels_cache_misses_total, buzz_channel_roster_reconciliations_total / buzz_channel_roster_reconciliation_failures_total, and buzz_nip43_membership_reconciliations_total / buzz_nip43_membership_reconciliation_failures_total, plus buzz_nip43_membership_publications_total{result} and buzz_nip43_membership_publication_seconds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "Entity-creation series in buzz-relay are buzz_users_created_total{community}, buzz_channels_created_total{community,type}, and buzz_workflow_runs_total{trigger,community}, recorded at several independent call sites across command_executor.rs, ingest.rs, side_effects.rs, and moderation_notices.rs rather than one central location."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "The git/repository subsystem in buzz-relay records buzz_git_hydrations_total{outcome} and buzz_git_hydrate_seconds{outcome} with outcome drawn from a six-value closed match arm (success, missing, invalid_pointer, manifest_error, store_error, hydrate_error, resource_limit) visible directly at the call site, plus buzz_git_hydrate_bytes, buzz_git_hydrate_packs, buzz_git_upload_pack_stream_seconds, buzz_git_upload_pack_stream_bytes, buzz_git_upload_pack_timeouts_total, buzz_git_semaphore_rejections_total{operation}, buzz_git_pack_cache_lookups_total{result} (result: hit/coalesced/miss), buzz_git_pack_cache_bypasses_total, buzz_git_pack_cache_evictions_total, buzz_git_pack_cache_copy_fallbacks_total, buzz_git_pack_cache_populate_seconds{outcome}, buzz_git_pack_cache_population_wait_seconds, buzz_git_pack_cache_populations_active (gauge), buzz_git_pack_cache_bytes / buzz_git_pack_cache_entries (gauges), buzz_git_pack_compactions_total{outcome} and buzz_git_pack_compaction_seconds{outcome}, buzz_git_pack_compaction_packs_before / packs_after / bytes (histograms), and buzz_git_pack_compaction_required_failures_total."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/hydrate.rs"
      - "crates/buzz-relay/src/api/git/pack_cache.rs"
      - "crates/buzz-relay/src/api/git/cas_publish.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Media and audit series in buzz-relay are buzz_media_uploads_total{mime}, buzz_media_legacy_upload_route_total, buzz_audit_send_errors_total (recorded independently in both api/media.rs and state.rs), buzz_audit_log_errors_total, buzz_audit_log_seconds, and the startup config gauge buzz_audit_enabled."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "Push-delivery series on the relay side are buzz_push_match_jobs_total{result} (result: context_error/unmatched/matched/error), buzz_push_match_queue_seconds, buzz_push_wakes_total{result}, buzz_push_wake_enqueue_errors_total, buzz_push_wake_queue_seconds, buzz_push_gateway_requests_total, buzz_push_gateway_request_seconds, and buzz_push_deliveries_total{outcome}, plus the startup config gauge buzz_push_enabled recorded alongside buzz_audit_enabled in main.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "crates/buzz-push-gateway/src/metrics.rs is a second, independent metrics-rs/Prometheus installation for that binary, with its module doc stating every label value it emits is a compile-time &'static str drawn from a closed set and that no endpoint, device token, relay pubkey, or request id is ever used as a label; it records push_gateway_apns_send_attempts_total, push_gateway_apns_deliveries_total{outcome} (outcome: accepted/invalid_endpoint/retry/configuration_fault/permanent_request_fault, exhaustively matched), push_gateway_apns_delivery_seconds, push_gateway_admissions_total{result} (admitted/rejected/unavailable), push_gateway_delivery_errors_total{class}, push_gateway_reaper_failures_total, and push_gateway_readiness_failures_total{cause} (not_accepting/authority)."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/metrics.rs"
  - statement: "Database pool and pressure series are buzz_db_pool_size/idle/active/max and buzz_db_read_pool_size/idle/active/max (gauges polled periodically in main.rs), buzz_db_read_session_degraded (counter), buzz_db_pool_acquire_wait_seconds{pool_role} and buzz_db_pool_acquisitions_total{pool_role,outcome} where pool_role is a closed writer/reader enum, buzz_db_advisory_lock_wait_seconds{lock_type} and buzz_db_advisory_lock_acquisitions_total{lock_type,outcome} where lock_type is a closed five-value enum (Replacement, Membership, PushGate, Deletion, MigrationSchemaSafety) whose module doc states label values come only from these closed enums and callers must never derive a label from tenant data, buzz_db_transaction_duration_seconds{operation}, buzz_db_route_decision{path,decision,reason}, and buzz_db_operation_duration_seconds{operation,outcome} which is emitted by a proc-macro (datastore_span) rather than a hand-written call site."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-db/src/runtime/observability.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
      - "crates/buzz-datastore-tracing/src/lib.rs"
  - statement: "Replica-fence gauges buzz_db_replica_fence_lag_seconds, buzz_db_replica_fence_open, and buzz_db_replica_heartbeat_age_seconds, and Redis-pool gauges buzz_redis_pool_available/size/max/waiting, are polled periodically in buzz-relay's main.rs alongside the database pool gauges."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "buzz-relay's storage_sweep.rs records per-community gauges buzz_community_storage_bytes{community} and buzz_community_storage_objects{community}, fleet-wide buzz_total_storage_bytes{kind} / buzz_total_storage_objects{kind} (kind: physical/logical), buzz_storage_orphan_blob_bytes, buzz_storage_orphan_blobs, buzz_storage_orphan_sidecars, buzz_storage_multi_variant_shas, buzz_storage_multi_variant_bytes, buzz_storage_unknown_key_bytes, buzz_storage_unknown_key_objects, buzz_storage_unmapped_community_bytes, and process-local sweep-health gauges buzz_storage_sweep_ok, buzz_storage_sweep_failures, buzz_storage_sweep_duration_seconds, and buzz_storage_sweep_age_seconds; a source comment on buzz_storage_sweep_failures states it is deliberately a gauge rather than a _total counter because it is a process-local value that resets on leader failover, not a monotonic fleet total safe for PromQL rate()."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
  - statement: "buzz-relay's main.rs runs a periodic usage poller that emits buzz_communities_total, per-community gauges (buzz_community_users, buzz_community_git_repos, buzz_community_messages, buzz_community_subscriptions, buzz_community_ws_connections, buzz_community_users_online_pod, buzz_community_channels, buzz_community_active_channels, buzz_community_active_users, buzz_community_relay_members, buzz_community_workflows) each carrying a community label, and fleet-wide buzz_total_* counterparts (buzz_total_users{type}, buzz_total_channels{type}, buzz_total_messages, buzz_total_relay_members{role}, buzz_total_workflows{status}, buzz_total_git_repos, buzz_total_active_users{window,type}, buzz_total_active_channels{window}, buzz_total_users_online_pod, buzz_total_ws_connections, buzz_total_subscriptions), plus buzz_usage_poller_is_leader; source comments state the fleet-wide buzz_total_* gauges always emit while the per-community series are gated by an EmissionScope read from BUZZ_USAGE_METRICS_PER_COMMUNITY (\"all\"/\"off\", default \"all\") specifically because per-community series multiply a fixed-cost gauge set by every community on the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "buzz-relay-mesh's multi-node session-fence rejections are recorded as mesh_fence_rejections_total{reason} in buzz-relay's tunnel/directory.rs, and buzz-relay-mesh's own lib.rs documents the reason label as a closed four-value taxonomy (stale_generation, no_active_lease, owner_mismatch, future_generation) that every fence-visible rejection must use rather than a generic value, so live kill-9/partition/replay evidence stays unambiguous."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs"
      - "crates/buzz-relay-mesh/src/lib.rs"
  - statement: "This node's metric catalog was produced by running `grep -rn 'metrics::(counter|gauge|histogram)!' crates/ --include=\"*.rs\"` (plus a second pass for multi-line invocations whose metric-name string literal falls on the line after the macro call) against the recorded revision, and each name in the catalog below was cross-checked by opening the file(s) the grep reported; the catalog is a hand-authored, point-in-time enumeration rather than a generated/ artifact, so a reader who needs current numbers should re-run the same command rather than trust this table indefinitely."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs"
      - "crates/buzz-push-gateway/src/metrics.rs"
  - statement: "The relay's Helm chart names a distinct `metrics` Service port defaulting to 9102 (values.yaml service.metricsPort, wired into service.yaml alongside app and health ports), and ships an opt-in Prometheus Operator ServiceMonitor (serviceMonitor.enabled, default false) that scrapes that named port at a configurable interval (default 30s) and scrapeTimeout (default 10s)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/service.yaml"
      - "deploy/charts/buzz/templates/servicemonitor.yaml"
      - "deploy/charts/buzz/values.yaml"
  - statement: "The repository's dev-compose stack (deploy/compose/compose.dev.yml) runs a standalone prom/prometheus container mounting the repository-root prometheus.yml, whose only scrape_configs job (buzz-relay) targets host.docker.internal:9102 with a 5s scrape_interval, reachable because the relay itself runs on the host rather than inside the compose network in this dev topology."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.dev.yml"
      - "prometheus.yml"
  - statement: "layers-observability-metrics and layers-observability-prometheus are already-merged corpus nodes on origin/launchpad (confirmed against the batch's existing-node-ids inventory) that respectively describe what a metric is in Buzz conceptually and how the Prometheus exposition mechanism works; both explicitly decline to enumerate every metric name, and layers-observability-metrics's own Scope and omissions table names 'Exhaustive per-metric name/label catalogue' as a gap it did not attempt, which this node exists to fill."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/metrics.md"
      - "launchpad/docs/corpus/layers/observability/prometheus.md"
  - statement: "Issue #1212's dispatch brief for this batch names logs (#1211), traces (#1213), alerts (#1209) and dashboards (#1210) as sibling operations/observability reference nodes being authored concurrently in the same Feature #618 batch, and directs this node to name the boundary against them in prose without declaring relationships to them, since none is merged on origin/launchpad at this node's recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1212 task dispatch brief (corpus-batch-author, Feature #618 batch run)"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a Reference description, structured entries ordered to match the source's own order rather than alphabetically, an optional Commands-style section, an explicit boundary statement, relationships, and a scope-and-omissions section distinguishing what is out of scope from what was expected but unverified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: layers-observability-metrics
  - type: references
    target: layers-observability-prometheus
---

# Metrics: reference

This node catalogues the metrics Buzz's relay and push-gateway processes actually
emit at the recorded revision: every distinct `metrics::counter!` / `gauge!` /
`histogram!` call site found by grepping `crates/`, grouped by subsystem, with its
type and label set as read directly from source. It is the lookup table the
conceptual sibling node `layers-observability-metrics` names as a gap it
deliberately did not attempt, and it is linked from there via `references` below.
A reader wanting *why* metrics are shaped this way (the `EmissionScope`
cost-control rationale, the counter/gauge/histogram naming convention, per-surface
recorder installation) should start at that sibling node; this one is for finding
a specific series and its labels while operating the system.

## Metric catalog

Grouped by subsystem in roughly the order a reader would meet it operating the
relay, not alphabetically. `total`-suffixed names are monotonic counters unless
noted otherwise; every row was verified against the file(s) named in the
evidence ledger above for its group.

### HTTP framework (buzz-relay Axum middleware)

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `http_requests_total` | counter | `code`, `caller`, `action` | `action` is the matched route pattern, not the raw URI, specifically to bound cardinality against scanner traffic |
| `http_request_latency_ms` | histogram | `code`, `caller`, `action` | Millisecond buckets configured in `metrics.rs`'s `install()` |

### WebSocket connection lifecycle

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_ws_connections_total` | counter | `community` | Incremented once per established connection |
| `buzz_ws_connections_active` | gauge | none | Incremented after auth challenge send succeeds; decremented on cleanup |
| `buzz_ws_auth_timeouts_total` | counter | none | NIP-42 auth timeout closures |
| `buzz_ws_backpressure_disconnects_total` | counter | none | Recorded at two call sites (`connection.rs`, `state.rs`) for the same sustained-backpressure disconnect path |
| `buzz_ws_send_batch_size` | histogram | none | Size of a batched outbound send |
| `buzz_subscriptions_active` | gauge | none | Incremented/decremented as REQ subscriptions are added/removed |

### Auth and admission control

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_auth_attempts_total` | counter | `method` | Observed value `"nip42"` |
| `buzz_auth_failures_total` | counter | `reason` | Observed reasons include `nip42_invalid`, `allowlist_denied`, `not_relay_member` |
| `buzz_admission_rejections_total` | counter | `transport`, `reason` | `transport` is `"websocket"` (connection.rs) or `"http"` (api/bridge.rs); `reason` includes `quota`, `unavailable` |
| `buzz_count_fallback_rejections_total` | counter | none | COUNT filter rejected for requiring narrower constraints |
| `buzz_gif_search_rejections_total` | counter | `reason` | Observed value `"quota"` |
| `buzz_media_upload_rejections_total` | counter | `reason` | Observed values `rate_limit`, `concurrency` |
| `buzz_req_global_access_resolution_skips_total` | counter | `kind` | The one observed call site passes the fixed string `"13534"`, not a variable |

### Event ingestion and fan-out

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_events_received_total` | counter | `kind` | Fleet-wide, per Nostr event kind |
| `buzz_community_events_received_total` | counter | `community` | Deliberately carries no `kind` label per its own source comment, for per-community throughput graphs |
| `buzz_events_rejected_total` | counter | `transport`, `reason` | `reason` is a closed four-value set per its doc comment: `auth`/`invalid`/`scope`/`error` |
| `buzz_events_stored_total` | counter | `kind`, `author_type` | Events actually persisted |
| `buzz_event_processing_seconds` | histogram | none | End-to-end per-event processing latency |
| `buzz_fanout_recipients` | histogram | none | Recipient count per fan-out delivery; dedicated bucket set in `metrics.rs` |
| `buzz_multinode_fanout_total` | counter | none | Cross-node fan-out messages relayed |
| `buzz_multinode_fanout_lag_total` | counter | none | Incremented by the lagged-message count when the multi-node fan-out broadcast receiver falls behind |
| `buzz_cache_invalidation_lag_total` | counter | none | Same lag pattern, cache-invalidation broadcast channel |
| `buzz_conn_control_lag_total` | counter | none | Same lag pattern, connection-control broadcast channel |
| `buzz_post_commit_dispatch_scheduled_total` | counter | none | Post-commit dispatch tasks scheduled |
| `buzz_post_commit_dispatch_errors_total` | counter | `stage` | Observed value `"serialize"` |

### Membership, roster and access caches

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_membership_cache_hits_total` / `buzz_membership_cache_misses_total` | counter | none | Channel-membership in-process cache |
| `buzz_accessible_channels_cache_hits_total` / `buzz_accessible_channels_cache_misses_total` | counter | none | Accessible-channels in-process cache |
| `buzz_channel_roster_reconciliations_total` / `buzz_channel_roster_reconciliation_failures_total` | counter | none | Roster reconciliation background job |
| `buzz_nip43_membership_reconciliations_total` / `buzz_nip43_membership_reconciliation_failures_total` | counter | none | NIP-43 membership-list reconciliation |
| `buzz_nip43_membership_publications_total` | counter | `result` | Observed values `attempted`/`succeeded`/`failed` |
| `buzz_nip43_membership_publication_seconds` | histogram | none | Publication latency |

### Entity creation and workflows

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_users_created_total` | counter | `community` | Recorded at three independent call sites |
| `buzz_channels_created_total` | counter | `community`, `type` | Observed `type` includes `"dm"` and a computed channel-type string |
| `buzz_workflow_runs_total` | counter | `trigger`, `community` | `trigger` is the workflow trigger kind |

### Git and repository subsystem

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_git_hydrations_total` | counter | `outcome` | Seven-arm closed match: `success`, `missing`, `invalid_pointer`, `manifest_error`, `store_error`, `hydrate_error`, `resource_limit` |
| `buzz_git_hydrate_seconds` | histogram | `outcome` | Same outcome set, dedicated seconds buckets in `metrics.rs` |
| `buzz_git_hydrate_bytes` | histogram | none | Only recorded on the `success` path; dedicated byte buckets |
| `buzz_git_hydrate_packs` | histogram | none | Only recorded on the `success` path; dedicated pack-count buckets |
| `buzz_git_upload_pack_stream_seconds` | histogram | none | Dedicated seconds buckets |
| `buzz_git_upload_pack_stream_bytes` | histogram | none | Dedicated byte buckets |
| `buzz_git_upload_pack_timeouts_total` | counter | none | Stream timed out |
| `buzz_git_semaphore_rejections_total` | counter | `operation` | Git concurrency-semaphore rejection |
| `buzz_git_pack_cache_lookups_total` | counter | `result` | Observed values `hit`, `coalesced`, `miss` |
| `buzz_git_pack_cache_bypasses_total` | counter | none | Cache bypassed |
| `buzz_git_pack_cache_evictions_total` | counter | none | Entry evicted |
| `buzz_git_pack_cache_copy_fallbacks_total` | counter | none | Install fell back to a file copy |
| `buzz_git_pack_cache_populate_seconds` | histogram | `outcome` | Dedicated seconds buckets |
| `buzz_git_pack_cache_population_wait_seconds` | histogram | none | Wait for an in-flight population; dedicated buckets |
| `buzz_git_pack_cache_populations_active` | gauge | none | Concurrent in-flight populations |
| `buzz_git_pack_cache_bytes` / `buzz_git_pack_cache_entries` | gauge | none | Cache size and entry count |
| `buzz_git_pack_compactions_total` | counter | `outcome` | Dedicated to compaction results |
| `buzz_git_pack_compaction_seconds` | histogram | `outcome` | Dedicated seconds buckets |
| `buzz_git_pack_compaction_packs_before` / `packs_after` | histogram | none | Dedicated pack-count buckets |
| `buzz_git_pack_compaction_bytes` | histogram | none | Dedicated byte buckets |
| `buzz_git_pack_compaction_required_failures_total` | counter | none | A compaction the code required (not opportunistic) failed |

### Media and audit

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_media_uploads_total` | counter | `mime` | Successful upload, labeled by MIME type |
| `buzz_media_legacy_upload_route_total` | counter | none | Request hit the legacy upload route |
| `buzz_audit_send_errors_total` | counter | none | Recorded independently in `api/media.rs` and `state.rs` for the same audit-send-failure condition |
| `buzz_audit_log_errors_total` | counter | none | Audit log write failed |
| `buzz_audit_log_seconds` | histogram | none | Audit log write latency, recorded only on success |
| `buzz_audit_enabled` | gauge | none | 1/0, set once at startup from config |

### Push delivery — relay side

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_push_match_jobs_total` | counter | `result` | Observed values `context_error`, `unmatched`, `matched`, `error` |
| `buzz_push_match_queue_seconds` | histogram | none | Time a job waited in the match queue |
| `buzz_push_wakes_total` | counter | `result` | Push-wake dispatch outcome |
| `buzz_push_wake_enqueue_errors_total` | counter | none | Failed to enqueue a wake batch |
| `buzz_push_wake_queue_seconds` | histogram | none | Time a wake waited in queue |
| `buzz_push_gateway_requests_total` | counter | none | Request sent from the relay to the push gateway |
| `buzz_push_gateway_request_seconds` | histogram | none | Relay-to-gateway round-trip latency |
| `buzz_push_deliveries_total` | counter | `outcome` | Terminal delivery outcome |
| `buzz_push_enabled` | gauge | none | 1/0, set once at startup from config |

### Push gateway (separate `buzz-push-gateway` process)

The push gateway is a distinct binary with its own metrics-rs/Prometheus
installation — see *Scrape and exposition endpoints* below for why its `/metrics`
is not on a public port. Its module doc states every label value here is a
compile-time `&'static str` from a closed set, with no endpoint, device token,
relay pubkey, or request id ever used as a label.

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `push_gateway_apns_send_attempts_total` | counter | none | Entry into the concrete APNs HTTP send seam |
| `push_gateway_apns_deliveries_total` | counter | `outcome` | Exhaustive five-value enum: `accepted`, `invalid_endpoint`, `retry`, `configuration_fault`, `permanent_request_fault` |
| `push_gateway_apns_delivery_seconds` | histogram | none | Dedicated seconds buckets in the gateway's own `install()` |
| `push_gateway_admissions_total` | counter | `result` | `admitted`, `rejected`, `unavailable` |
| `push_gateway_delivery_errors_total` | counter | `class` | Fixed compile-time error-class strings, e.g. `invalid_grant`, `finish_failed` |
| `push_gateway_reaper_failures_total` | counter | none | Retention-reaper sweep failure |
| `push_gateway_readiness_failures_total` | counter | `cause` | `not_accepting`, `authority` |

### Database pool and pressure

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_db_pool_size` / `_idle` / `_active` / `_max` | gauge | none | Writer pool, polled periodically |
| `buzz_db_read_pool_size` / `_idle` / `_active` / `_max` | gauge | none | Read-replica pool, polled periodically |
| `buzz_db_read_session_degraded` | counter | none | A read session fell back to the writer |
| `buzz_db_pool_acquire_wait_seconds` | histogram | `pool_role` | `pool_role`: closed `writer`/`reader` enum |
| `buzz_db_pool_acquisitions_total` | counter | `pool_role`, `outcome` | Same closed `pool_role` enum |
| `buzz_db_advisory_lock_wait_seconds` | histogram | `lock_type` | `lock_type`: closed five-value enum — `Replacement`, `Membership`, `PushGate`, `Deletion`, `MigrationSchemaSafety` |
| `buzz_db_advisory_lock_acquisitions_total` | counter | `lock_type`, `outcome` | Same closed `lock_type` enum |
| `buzz_db_transaction_duration_seconds` | histogram | `operation` | Recorded in a `Drop` implementation |
| `buzz_db_operation_duration_seconds` | histogram | `operation`, `outcome` | Emitted by the `datastore_span` proc-macro, not a hand-written call site |
| `buzz_db_route_decision` | counter | `path`, `decision`, `reason` | Read/write routing decision |
| `buzz_db_replica_fence_lag_seconds` | gauge | none | Polled periodically |
| `buzz_db_replica_fence_open` | gauge | none | Polled periodically |
| `buzz_db_replica_heartbeat_age_seconds` | gauge | none | Polled periodically |

### Redis pool

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_redis_pool_available` / `_size` / `_max` / `_waiting` | gauge | none | Polled periodically in `main.rs` alongside the database pool gauges |

### Storage sweep

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_community_storage_bytes` / `_objects` | gauge | `community` | Per-community object-storage usage |
| `buzz_total_storage_bytes` / `_objects` | gauge | `kind` | `kind`: `physical`/`logical` |
| `buzz_storage_orphan_blob_bytes`, `_orphan_blobs`, `_orphan_sidecars` | gauge | none | Orphaned-object counts and bytes |
| `buzz_storage_multi_variant_shas` / `_bytes` | gauge | none | Blobs stored with more than one variant |
| `buzz_storage_unknown_key_bytes` / `_objects` | gauge | none | Objects under unrecognized storage keys |
| `buzz_storage_unmapped_community_bytes` | gauge | none | Bytes under a community mapping that no longer resolves |
| `buzz_storage_sweep_ok` | gauge | none | 1/0, last sweep succeeded |
| `buzz_storage_sweep_failures` | gauge | none | Deliberately a gauge, not a counter — a source comment states it is process-local and resets on leader failover, so it is not safe for PromQL `rate()` |
| `buzz_storage_sweep_duration_seconds` | gauge | none | Duration of the last sweep |
| `buzz_storage_sweep_age_seconds` | gauge | none | Time since the cached sweep snapshot completed |

### Fleet and per-community usage rollups

Emitted by a periodic poller in `main.rs`. Per-community series below are
suppressed fleet-wide when `BUZZ_USAGE_METRICS_PER_COMMUNITY=off`; the
`buzz_total_*` fleet gauges always emit regardless. See *Cardinality and
multi-tenancy* below and the sibling `layers-observability-metrics` node for the
full `EmissionScope` mechanism — this table states only the resulting series.

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `buzz_communities_total` | gauge | none | Fleet-wide community count |
| `buzz_community_users` | gauge | `community`, `type` | `type`: `human`/`agent` |
| `buzz_community_git_repos`, `_messages`, `_subscriptions`, `_ws_connections`, `_users_online_pod`, `_channels`, `_active_channels`, `_active_users`, `_relay_members`, `_workflows` | gauge | `community` (+ `type`/`window`/`role`/`status` where the fleet-wide counterpart also carries one) | Per-community rollups |
| `buzz_total_users` | gauge | `type` | `type`: `human`/`agent` |
| `buzz_total_channels` | gauge | `type` | Per channel type |
| `buzz_total_messages`, `_git_repos`, `_users_online_pod`, `_ws_connections`, `_subscriptions` | gauge | none | Fleet-wide totals |
| `buzz_total_relay_members` | gauge | `role` | Per relay-member role |
| `buzz_total_workflows` | gauge | `status` | Per workflow status |
| `buzz_total_active_users` | gauge | `window`, `type` | `type` includes `human`/`agent`/`unknown` |
| `buzz_total_active_channels` | gauge | `window` | Active-channel count for a time window |
| `buzz_usage_poller_is_leader` | gauge | none | 1/0, whether this pod runs the usage poller |

### Multi-node mesh

| Metric | Type | Labels | Notes |
|---|---|---|---|
| `mesh_fence_rejections_total` | counter | `reason` | Closed four-value taxonomy: `stale_generation`, `no_active_lease`, `owner_mismatch`, `future_generation` — every fence-visible rejection uses one of these rather than a generic value, by design, so live kill-9/partition/replay evidence stays unambiguous |

## Cardinality and multi-tenancy

Several series above carry a `community` label directly (`buzz_community_*`,
`buzz_ws_connections_total`, `buzz_users_created_total`,
`buzz_channels_created_total`, `buzz_workflow_runs_total`,
`buzz_community_storage_bytes`/`_objects`). Each such label value is one
independent Prometheus time series per community on the relay, so the per-community
usage rollups are the one series family in this catalog with a cost that scales
with tenant count rather than a fixed constant — which is exactly why they, alone
among the series above, are gated behind `BUZZ_USAGE_METRICS_PER_COMMUNITY`. Every
other multi-community-labeled series in this catalog (auth, admission, git, push,
storage-sweep-per-community) emits unconditionally regardless of tenant count. By
contrast, the push gateway's entire label surface and `buzz-db`'s pool/lock label
enums are closed, compile-time sets independent of tenant identity, per their own
module docs cited above — those series cannot grow with community count no matter
how many tenants the relay serves.

## Scrape and exposition endpoints

| Surface | Port / path | Mechanism | Notes |
|---|---|---|---|
| `buzz-relay` | `:9102` (default; `BUZZ_METRICS_PORT` overrides), `GET /metrics` | Embedded `PrometheusBuilder` HTTP listener, separate from the app router | Public port; the only surface in this catalog exposed outside the process |
| `buzz-push-gateway` | Rendered from the private health router (`:8081`), not a public port | `PrometheusBuilder::install_recorder()` with no HTTP listener of its own | Deliberately not public, per the module's own stated cardinality/exposure design |
| Kubernetes (Helm chart) | Service port named `metrics`, default `9102` (`values.yaml` `service.metricsPort`) | Opt-in `ServiceMonitor` (`serviceMonitor.enabled`, default `false`), scraping the named port at a configurable `interval` (default `30s`) and `scrapeTimeout` (default `10s`) | Scrapes `buzz-relay` only; the chart's `ServiceMonitor` template does not reference the push gateway |
| Local development | `prom/prometheus` container in `deploy/compose/compose.dev.yml`, mounting the repository-root `prometheus.yml` | Single `scrape_configs` job (`buzz-relay`) targeting `host.docker.internal:9102` at a `5s` interval | Assumes the relay runs on the host, not inside the compose network — the reason `host.docker.internal` is reachable at all in this topology |

## Boundary

This node is a **reference catalog**, not the conceptual explanation of what a
metric is or why Buzz's metrics are shaped the way they are — that is the
already-merged sibling `layers-observability-metrics`, and the exposition
mechanism's own internals (recorder installation order, bucket-boundary
configuration, idle-timeout policy) belong to the already-merged sibling
`layers-observability-prometheus`; both are linked below and neither is
restated here beyond what a table row needs. This node does not:

- Explain *why* a metric exists, what workflow it supports diagnosing, or how to
  read it in a dashboard or alert rule — that is dashboards (#1210) and alerts
  (#1209) territory, both in-flight sibling reference nodes in this same batch and
  not yet merged, so this node names them without linking them.
- Describe log lines or trace spans — logs (#1211) and traces (#1213) are separate
  sibling reference nodes in this same batch, also unmerged, also named without a
  relationships edge.
- Walk a reader through a diagnostic procedure step by step (e.g. "when the pool
  gauges look wrong, do X then Y") — that would be a how-to/procedure-shaped node,
  not this reference template.
- Claim to be a full API reference for the Prometheus exposition format itself
  (response headers, content negotiation) — `layers-observability-prometheus`
  is the closer fit for that if it is ever needed, and this node does not attempt
  it.

## Relationships

- `references` → `layers-observability-metrics` — the conceptual sibling this
  catalog exists to complete; that node names an "exhaustive per-metric
  name/label catalogue" as a gap it deliberately left open, and this node fills it.
- `references` → `layers-observability-prometheus` — the exposition-mechanism
  sibling this node's *Scrape and exposition endpoints* section draws its port,
  listener, and scrape-target facts from without repeating its internals.

No edge is declared toward logs (#1211), traces (#1213), alerts (#1209), or
dashboards (#1210): none is merged on `origin/launchpad` at this node's recorded
revision, and a `relationships[].target` naming an id no loaded node carries is a
hard validation error per `AGENTS.md`.

## Scope and omissions

**This node covers** every `metrics::counter!`/`gauge!`/`histogram!` call site
found by grepping `crates/` at the recorded revision, grouped by subsystem, with
each series' type, label set, and — where the source makes it visible — the
closed set of label values it can take; the multi-tenancy cardinality
consequence of the `community` label; and how each of `buzz-relay` and
`buzz-push-gateway` exposes its series for scraping, including the Kubernetes
`ServiceMonitor` and local dev-compose scrape configuration.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What a metric is conceptually, the counter/gauge/histogram naming convention, and why each surface installs its recorder the way it does | `layers-observability-metrics` (merged) |
| Prometheus exposition wire format and exporter internals (bucket configuration, idle-timeout policy, recorder install order) | `layers-observability-prometheus` (merged) |
| Structured logging | Logs reference node, #1211 (in-flight, unmerged at this revision) |
| Distributed tracing / spans | Traces reference node, #1213 (in-flight, unmerged at this revision) |
| Alerting rules and thresholds built on these series | Alerts reference node, #1209 (in-flight, unmerged at this revision) |
| Dashboards and how to read these series visually | Dashboards reference node, #1210 (in-flight, unmerged at this revision) |
| Health/liveness/readiness probe endpoints (a separate Kubernetes-probe surface, not Prometheus-scraped) | Not attempted here; out of this node's subject |

**Expected but not verified when this node was written:**

- **Whether every closed label enum documented above is genuinely exhaustive at
  every call site**, versus this node having found only the call sites its grep
  pattern matched. The grep covered both single-line and the one multi-line
  invocation shape actually present in this codebase; a differently-formatted
  call site (e.g. one broken across three or more lines in an unusual way) could
  in principle be missed. No independent tool (e.g. a Rust macro-expansion pass)
  was run to cross-check the grep's completeness.
- **Whether the local dev-compose Prometheus container is exercised regularly**
  as opposed to merely present in the repository — this node confirms the scrape
  target is configured correctly for the host-networked relay, not that anyone
  currently runs it day to day.
- **Whether the push gateway's `/metrics` endpoint on its private health router
  is reachable from outside the gateway's own pod/host in any deployed
  topology** — this node states what the code does (render from the private
  router, install no public listener) without tracing whether an operator-facing
  scrape path to it exists anywhere in the Helm chart or deployment tooling; a
  targeted grep of the chart found no `ServiceMonitor` or port reference naming
  the push gateway specifically.
