---
id: capabilities-activity-activity-feed
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844 on branch launchpad."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "query_activity finds recent stream messages (KIND_STREAM_MESSAGE=9, KIND_STREAM_MESSAGE_V2=40002), forum posts (KIND_FORUM_POST=45001), and agent job events (KIND_JOB_REQUEST=43001, KIND_JOB_PROGRESS=43003, KIND_JOB_RESULT=43004), scoped to community-global events plus channels the caller can access, ordered newest-first (build_activity_query and query_activity in crates/buzz-db/src/store/feed.rs)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:253-275"
      - "crates/buzz-db/src/store/feed.rs:283-291"
      - "crates/buzz-core/src/kind.rs:479"
      - "crates/buzz-core/src/kind.rs:481"
      - "crates/buzz-core/src/kind.rs:518"
      - "crates/buzz-core/src/kind.rs:522"
      - "crates/buzz-core/src/kind.rs:524"
      - "crates/buzz-core/src/kind.rs:550"
  - statement: "The module doc comment on feed.rs states the activity category is one of three feed categories (mentions, needs-action, activity) aggregated for the Home Feed feature, and that workflow execution kinds (46001-46012) are intentionally excluded from the activity query 'to avoid noise'."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:1-23"
      - "crates/buzz-db/src/store/feed.rs:277-281"
  - statement: "Feed channel visibility is enforced by push_visible_channel_filter: an empty accessible-channel list means 'community-global events only' (channel_id IS NULL), never 'all channels', and a non-empty list matches global events OR events in one of the caller's accessible channels."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:56-73"
  - statement: "Every feed query, including query_activity, enforces a hard cap of FEED_MAX_LIMIT=100 rows regardless of the limit value the caller requests (build_activity_query calls limit.min(FEED_MAX_LIMIT))."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:25-29"
      - "crates/buzz-db/src/store/feed.rs:259"
  - statement: "query_feed_activity_routed is a replica-routed wrapper around query_activity: it attempts the read against a routed replica connection when RoutePredicate::Bounded permits it, and re-runs the same query against the writer pool if the replica read errors."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:483-525"
  - statement: "An integration test named routed_reads_are_confined_to_the_requested_community exercises query_feed_activity_routed against a writer/replica pair with two communities, asserting the routed activity read returns only the requesting community's replica-only row and never a sibling community's row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/tests.rs:1558"
      - "crates/buzz-db/src/runtime/tests.rs:1747-1751"
  - statement: "The relay's HTTP/WebSocket query bridge recognizes a non-standard 'feed_types' array field on an incoming filter via extract_feed_types; when present and non-empty, the bridge dispatches per requested type instead of running the filter as a plain Nostr query, and an 'activity' entry in feed_types routes to state.db.query_feed_activity_routed with the filter's since/limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:332-343"
      - "crates/buzz-relay/src/api/bridge.rs:1155-1225"
  - statement: "An 'agent_activity' value in feed_types is canonicalized to 'activity' before dispatch, so both values route to the same query_feed_activity_routed call and are deduplicated together (seen_types / seen id sets) within one request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1172-1187"
  - statement: "buzz-cli's feed get subcommand (FeedCmd::Get) accepts a comma-separated --types flag validated against exactly four values: mentions, needs_action, activity, agent_activity; only when --types is supplied does the outgoing filter carry a feed_types key at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:977-991"
      - "crates/buzz-cli/src/commands/feed.rs:6"
      - "crates/buzz-cli/src/commands/feed.rs:49-60"
  - statement: "Plain 'buzz feed get' with no --types flag never sets a feed_types key on its query filter, so extract_feed_types returns None on the relay side and that request is handled as an ordinary NIP-01 filter query (a bare #p-tag match on the caller's own pubkey) rather than reaching query_activity/query_feed_activity_routed at all — the activity-specific query path is reached only when --types includes 'activity' or 'agent_activity'."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/feed.rs:36-62"
      - "crates/buzz-relay/src/api/bridge.rs:332-343"
  - statement: "The desktop app's HomeFeed type carries a dedicated activity: FeedItem[] array (distinct from mentions/needsAction/agentActivity), and FeedItemCategory includes \"activity\" as one of its four values, populated from the relay's activity-category feed items."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/types.ts:206-230"
  - statement: "The desktop Home inbox labels an item whose category is \"activity\" with the display text \"Activity\" (categoryLabelFor), distinct from \"Mention\", \"Needs Action\", and \"Agent update\" (agent_activity)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/home/lib/inbox.ts:197-205"
  - statement: "The desktop Pulse feature (desktop/src/features/pulse/**, e.g. PulseScreen.tsx, AgentActivityCard.tsx) is a separate, independently routed screen from the Home Feed's activity category, and is issue #702's subject, not this node's."
    entry_class: FACT
    evidence:
      - "desktop/src/features/pulse/ui/PulseScreen.tsx"
      - "desktop/src/app/routes/pulse.tsx"
  - statement: "crates/buzz-cli/TESTING.md documents a live-testing runbook entry for the activity feed capability ('6.10 Feed': buzz feed get | jq . and buzz feed get --limit 5 | jq ., expecting complete signed Nostr events sorted newest-first), and a corresponding manual-verification checklist row ('43 | feed get')."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/TESTING.md:426-433"
      - "crates/buzz-cli/TESTING.md:608"
  - statement: "The activity feed capability is shipped: query_activity/query_feed_activity_routed, the CLI feed get --types activity path, the relay bridge dispatch, and the desktop Home Feed's activity category are all present in currently-merged source and exercised by an automated integration test, not merely designed."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/feed.rs:283-330"
      - "crates/buzz-relay/src/api/bridge.rs:1213-1223"
      - "crates/buzz-db/src/runtime/tests.rs:1558"
      - "desktop/src/shared/api/types.ts:225-230"
    confidence: 0.9
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-cli
---

# Activity feed: capability

Buzz gives every member (human or agent) a running feed of recent activity across
the channels they can access — stream messages, forum posts, and agent job
progress/result events — surfaced through the Home Feed's "Activity" category so a
user does not have to visit every channel individually to see what has been
happening. It is one of four categories the Home Feed aggregates (mentions, needs
action, activity, and agent-specific activity), and is fetched via `buzz feed get
--types activity` on the CLI or the corresponding `feed_types` extension on a relay
query, then rendered in the desktop app's Home inbox labelled "Activity".

## Maturity

**Shipped.** The query implementation (`query_activity`, `build_activity_query`,
`crates/buzz-db/src/store/feed.rs:253-291`), its replica-routed wrapper
(`query_feed_activity_routed`, `feed.rs:483-525`), the relay bridge dispatch
(`extract_feed_types` plus its `"activity"` arm, `crates/buzz-relay/src/api/bridge.rs:332-343,1155-1225`),
the CLI surface (`FeedCmd::Get --types`, `crates/buzz-cli/src/lib.rs:977-991`,
`crates/buzz-cli/src/commands/feed.rs`), and the desktop consumer
(`HomeFeed.activity` / `FeedItemCategory: "activity"`,
`desktop/src/shared/api/types.ts:206-230`, labelled "Activity" in
`desktop/src/features/home/lib/inbox.ts:197-205`) are all present in currently
merged source. An integration test
(`routed_reads_are_confined_to_the_requested_community`,
`crates/buzz-db/src/runtime/tests.rs:1558-1751`) exercises
`query_feed_activity_routed` directly, and `crates/buzz-cli/TESTING.md`'s "6.10
Feed" section documents the live-testing runbook for `buzz feed get`.

## Boundary

This node does not describe:
- **How the capability is built** — the relay, Postgres, and CLI containers that
  implement it are the architecture family's territory; see the `references`
  relationships below (`architecture-containers-relay`,
  `architecture-containers-cli`).
- **The interface(s) the capability is exposed through** — the exact CLI flag
  grammar and relay query-bridge extension field are cited above as evidence, not
  re-described here as their own interface contract; no `interfaces-events`
  template has landed yet for this batch to reference.
- **The step-by-step flow through this capability** — no flow node exists yet for
  this batch to reference; this node states that the capability exists and what it
  covers, not the sequence a caller walks through to use it.
- **Mentions and needs-action**, the other two feed categories `query_mentions` and
  `query_needs_action` implement in the same file. Those are separate capability
  nodes (issues #700 `mentions-feed` and #701 `needs-action`), not folded into this
  one, per the corpus rule that one node is one independently maintainable idea.
- **Pulse**, the desktop app's separate community-wide activity/notes screen
  (`desktop/src/features/pulse/**`, issue #702). Pulse is a distinct, independently
  routed screen from the Home Feed's activity category, even though both surface
  "recent activity" in casual language.
- **How the running system is operated** (deployment, monitoring, incident
  response) — the `operations` corpus surface's territory, not this node's.

A subtlety worth stating precisely because it is easy to miss: plain `buzz feed get`
with no `--types` flag never reaches `query_activity` at all. `cmd_get_feed` only
adds a `feed_types` key to its outgoing filter when `--types` is supplied
(`crates/buzz-cli/src/commands/feed.rs:36-62`); without it, the relay bridge's
`extract_feed_types` returns `None` and the request falls through to an ordinary
NIP-01 filter query (a bare `#p`-tag match on the caller's own pubkey) rather than
the activity-specific query path. Reaching this capability requires `--types`
including `activity` or `agent_activity` (the latter is canonicalized to `activity`
server-side, `crates/buzz-relay/src/api/bridge.rs:1176`).

## Relationships

- references: `architecture-containers-relay` — the relay container hosts the
  bridge dispatch (`extract_feed_types`) and the Postgres-backed feed queries this
  capability runs.
- references: `architecture-containers-cli` — `buzz-cli` is the agent-facing
  interface through which this capability is invoked (`feed get --types activity`).

## Scope and omissions

**This node covers** the activity feed's capability statement, its current shipped
maturity with citations, its explicit boundary against mentions/needs-action/pulse/
operations/architecture/interface/flow, and the CLI-default nuance that plain `feed
get` does not reach this query path.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Mentions feed category | issue #700 (`capabilities/activity/mentions-feed.md`) |
| Needs-action feed category | issue #701 (`capabilities/activity/needs-action.md`) |
| Pulse (desktop community activity screen) | issue #702 (`capabilities/activity/pulse.md`) |
| How the relay/CLI containers are built | `architecture-containers-relay`, `architecture-containers-cli` |
| The CLI flag grammar and relay query-bridge field as their own interface contract | a future `interfaces-events` node (no template landed in this batch) |
| The step-by-step flow through this capability | a future flow node (no template landed in this batch) |

**Expected but not verified when this node was written:**
- **No live invocation of `buzz feed get --types activity` was run against a
  running relay** during authoring — maturity is established from source and an
  automated integration test, not a fresh manual run of
  `crates/buzz-cli/TESTING.md`'s "6.10 Feed" checklist item (row 43, unchecked in
  that file at this revision).
- **The desktop Home Feed's `since`/pagination behavior and how often the Tauri
  bridge polls or re-fetches the activity category** were not traced past the type
  definitions and the labelling function cited above.
- **`architecture-containers-relay` and `architecture-containers-cli` are both
  `status: draft`** in the corpus at this revision — their own content has not
  been human-reviewed to `active`, so this node's `references` edges point at
  still-draft neighbors, not settled ones.
