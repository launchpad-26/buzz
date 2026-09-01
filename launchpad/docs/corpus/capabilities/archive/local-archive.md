---
id: capabilities-archive-local-archive
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "The desktop Settings UI exposes a panel with the literal value \"local-archive\" and label \"Local archive\", rendered by `LocalArchiveSettingsCard`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/SettingsPanels.tsx:222-225"
      - "desktop/src/features/settings/ui/SettingsPanels.tsx:855-856"
  - statement: "The Rust archive module's own doc comment describes it as \"Local-save archive — Tauri commands for archiving relay messages to a per-identity SQLite database in the Buzz nest,\" with two access-proof paths depending on event kind: persistent scopes (channel_h, referenced_e, owner_p+44200) verified by re-querying the relay, and the ephemeral owner_p kind-24200 observer-frame scope verified only by local fail-closed validation because the relay never stores those events."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/archive/mod.rs:1-18"
  - statement: "The local archive's SQLite store holds three tables -- archived_events (one raw event row per identity/relay/event_id), archived_event_scopes (many-to-many scope membership per raw event), and save_subscriptions (which scopes the user has subscribed to save) -- with raw event rows garbage-collected once their last scope row is deleted."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/archive/store.rs:1-9"
  - statement: "Retention is a single global setting: observer frames (kind 24200) are kept for a configurable rolling window (default 30 days, bounded to at most ~100 years), while NIP-AM agent-turn-metric events (kind 44200) and every other archived kind are kept indefinitely with no retention/prune machinery."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/archive/retention.rs:1-32"
  - statement: "The Tauri command surface registered in the desktop app's invoke_handler includes archive_events, create_save_subscription, merge_save_subscription_kinds, remove_save_subscription_kind, list_save_subscriptions, delete_save_subscription, read_archived_events, read_archived_observer_events_for_channel, index_observer_channel_id, read_unindexed_observer_rows, get_agent_usage_series, get_observer_retention_days, set_observer_retention_days, archive_size_stats, and the archive-sync lifecycle commands announce_archive_sync_epoch/start_archive_sync/stop_archive_sync."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:836-852"
  - statement: "An independently-authored coverage inventory (launchpad/docs/Observability/current-state/coverage.md, row D04) names this same subsystem \"Local archive, migrations, and saved subscriptions\" -- SQLite/archive initialization, event/observer/usage persistence, save subscriptions, and legacy storage migration -- rooted at desktop/src-tauri/src/archive/, migration.rs, and the legacy_storage/observer_archive/agent_metric_archive commands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/coverage.md:90"
  - statement: "The frontend TypeScript wrapper (tauriArchive.ts) exposes typed callers for the save-subscription CRUD, batch archiving, paginated archived-event reads (scoped and channel-scoped observer reads), the NIP-AM agent-usage-series query, and an epoch/lease-ordered lifecycle (announceArchiveSyncEpoch, startArchiveSync, stopArchiveSync) that hands the live per-scope relay subscription to a backend-owned sync task rather than the renderer."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/tauriArchive.ts:216-361"
  - statement: "The backend archive-sync task (sync.rs) opens one live relay subscription per saved archive configuration and forwards matched events to the archive pipeline in debounced batches, replacing an earlier renderer-side archiveSyncManager so that matched events no longer cross the IPC boundary twice; the task is not self-starting and requires the renderer's observer-reconciliation step to seed the ephemeral kind-24200 subscription before it opens, because frames arriving before the listener opens are permanently lost."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/archive/sync.rs:1-18"
  - statement: "Desktop end-to-end specs exercise this capability's user-facing behavior directly: observer-archive-policy.spec.ts asserts the observer-archive toggle defaults to enabled and checked for a fresh identity, that toggling OFF/ON removes/recreates the underlying save subscription, that an explicit opt-out persists across reload, and that archive sync only starts after reconciliation seeds the subscription; local-archive-screenshots.spec.ts captures the subscriptions list, the add-scope flow, the kind checklist, and the observer-archive toggle section."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/observer-archive-policy.spec.ts"
      - "desktop/tests/e2e/local-archive-screenshots.spec.ts"
  - statement: "CHANGELOG.md records multiple merged, shipped features and fixes against this capability across a long history -- e.g. \"feat(archive): add agent turn-metric (kind 44200) local archive\" (#1555), \"feat(archive): add observer-frame retention schema and gated DB adapter\" (#5719), and \"fix(local-archive): default both archive settings to enabled\" (#4750) -- establishing this as a shipped, actively maintained capability rather than a designed-but-unbuilt one."
    entry_class: FACT
    evidence:
      - "CHANGELOG.md:60"
      - "CHANGELOG.md:521"
      - "CHANGELOG.md:1270"
  - statement: "No dedicated architecture, interface, or flow corpus node yet exists for the archive subsystem specifically; the closest merged architecture node, architecture-containers-desktop, documents the desktop container generally (Tauri/React/Rust boundary, relay/IPC interfaces, identity and media-proxy security implications) and does not itself describe the archive subsystem's schema, retention policy, or sync task -- so this capability node references it as the realizing container without treating it as a substitute for an archive-specific architecture node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "Root VISION_PROJECTS.md's own Status capability table has no row naming local archive, offline storage, or message retention, so this node's maturity claim rests on code, CHANGELOG history, and e2e coverage rather than a VISION status marker."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-259"
---

# Local archive: capability

Buzz's desktop app can keep a **local, per-identity copy of relay data** on
the user's own machine, independent of what the relay currently holds or
returns live: channel and DM messages the user has chosen to save, the
user's own AI agents' ephemeral observer frames and turn-metric telemetry,
and the save-subscription configuration that drives all of it. A human
owner turns this on or off, and chooses what to save, from the desktop
app's "Local archive" Settings panel; an agent or the desktop UI itself
reads back through the same local store for paginated history and usage
reporting, without needing the relay to still hold or return that data.

## Maturity

**Shipped.** This is not a designed-but-unbuilt capability: it has a
complete, wired backend (SQLite schema, retention policy, batch archiving,
paginated reads, an epoch/lease-ordered sync-task lifecycle), a complete
frontend (a dedicated Settings panel, typed API wrappers, preference
persistence), and end-to-end test coverage of its user-facing toggle and
reconciliation behavior. CHANGELOG.md records a long history of merged
features and fixes against it, from the original kind-44200 turn-metric
archive (#1555) through retention-schema work (#5719) and default-enablement
fixes (#4750), and root VISION_PROJECTS.md's own capability Status table
(which does track other capabilities as Ships today / in progress /
Designed) has no separate row for it at all -- its maturity is established
directly from code, tests and shipped history rather than from a VISION
status marker.

## Boundary

This node does not describe:
- **How the capability is built.** The SQLite schema, the retention
  index/prune design, the sync task's epoch/lease ordering, and the
  fail-closed access-proof paths for persistent versus ephemeral scopes are
  implementation detail owned by an archive-specific architecture node, not
  yet drafted. `architecture-containers-desktop` documents the desktop
  container this capability lives inside, at a level that does not reach
  the archive subsystem's own internals.
- **The interface(s) this capability is exposed through.** The Tauri command
  surface (`archive_events`, `read_archived_events`, the sync lifecycle
  commands, and the rest) and the Settings-panel UI it backs are a boundary
  contract, owned by an interface node once one is drafted for it.
- **The step-by-step flow through it.** How a single save-subscription
  toggle, a batch archive call, or a sync-task start/stop actually plays out
  turn by turn is flow-node territory, not yet drafted for this capability.
- **How the capability is operated.** Nothing here covers monitoring, disk
  pressure, or incident response for the local archive database in the
  field -- that is the `operations` corpus surface's territory, not this
  node's.
- **The relay-side data model or retention of the events this capability
  copies.** This node describes the desktop-local copy only; what the relay
  itself stores, returns, or expires is out of scope here.

## Relationships

- references: architecture-containers-desktop

## Scope and omissions

**This node covers** what the local archive capability lets a user and
their agents do (save relay data locally, configure what is saved, read it
back, and bound how long ephemeral observer frames are kept), and its
current shipped maturity, grounded in code, the Tauri command registration,
CHANGELOG history, and e2e test coverage.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The archive subsystem's own architecture (schema, sync-task design, access-proof paths) | An archive-specific architecture node, not yet drafted |
| The Tauri command / Settings-panel boundary contract | An interface node, not yet drafted |
| The step-by-step flow through a save/read/sync interaction | A flow node, not yet drafted |
| How the running archive database is operated in the field | The `operations` corpus surface |
| The relay's own data model and retention for the events this capability copies | Out of scope for this node |

**Expected but not verified when this node was written:**
- **The Phase-2 prune worker referenced by `retention.rs`'s own comments**
  ("The prune worker itself lands in Phase 2") was not located or read; this
  node describes the retention *setting* (get/set accessors, the seeded
  default, the bound) as implemented, but does not claim the scheduled prune
  job itself is wired up, since that file explicitly defers it.
- **The desktop mobile/web clients' equivalent (or lack of one).** This node
  was checked only against the desktop app; whether mobile or web have any
  comparable local-archive behavior was not investigated.
- **CHANGELOG.md's cited entries were read for their one-line summaries
  only**, not by opening each linked PR's full diff -- the shipped-history
  claim rests on the changelog text and the current code present at the
  recorded revision, not on a PR-by-PR diff review.
