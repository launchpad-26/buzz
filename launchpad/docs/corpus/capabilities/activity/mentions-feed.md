---
id: capabilities-activity-mentions-feed
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
  - statement: "VISION.md states: \"The Home Feed is the personalized entry point — @mentions, items needing action, channel activity, agent updates. Fan-out-on-read, assembled at query time. Agents read the same feed via MCP.\", naming mentions as one of the Home Feed's constituent categories and stating that both humans and agents read the same feed."
    entry_class: FACT
    evidence:
      - "VISION.md:133"
  - statement: "buzz-cli's feed command accepts a `--types` filter whose valid values are `mentions`, `needs_action`, `activity`, and `agent_activity`, and sends the requested list to the relay as a `feed_types` field on the query filter, rejecting any value outside that set with a usage error."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/feed.rs:6"
      - "crates/buzz-cli/src/commands/feed.rs:29-64"
  - statement: "The relay's HTTP query bridge (`crates/buzz-relay/src/api/bridge.rs`) recognizes the `feed_types` extension field (`extract_feed_types`), treats `agent_activity` as a canonical alias for `activity`, and for the `mentions` value dispatches to `Db::query_feed_mentions_routed`, capped per-request at `BRIDGE_FEED_MAX_LIMIT` and filtered again in-process for channel accessibility, cross-community leakage, and `reader_authorized_for_event` before any event is returned."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:332-341"
      - "crates/buzz-relay/src/api/bridge.rs:1155-1246"
  - statement: "buzz-db's mentions feed query (`crate::feed::build_mentions_query`, exposed as `Db::query_feed_mentions`/`Db::query_feed_mentions_routed`) is an `INNER JOIN` of `events` against an `event_mentions` table on `(community_id, event_id)`, filtered to a fixed kind allowlist (stream messages, text notes, forum posts/comments, and git PR/issue/status kinds), scoped to the caller's community and accessible channels (or community-global rows when the channel is `NULL`), and ordered by `event_created_at DESC`; a hard `FEED_MAX_LIMIT` of 100 rows is enforced regardless of the caller-supplied limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:1-50"
      - "crates/buzz-db/src/store/feed.rs:86-119"
      - "crates/buzz-db/src/store/feed.rs:309-329"
  - statement: "The `event_mentions` table that the mentions feed query joins against is populated by `insert_mentions`/`insert_mentions_in_transaction` on every event insert, per buzz-db's own module documentation and the function's presence in `runtime/mod.rs`."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:16-20"
      - "crates/buzz-db/src/runtime/mod.rs:21-36"
  - statement: "The mentions feed query is covered by dedicated tests: `crates/buzz-db/src/store/feed.rs`'s own `mod tests` (26 `#[test]`/`#[tokio::test]` functions from that module, including `query_mentions_is_scoped_across_communities`), and a cross-community/replica-routing separation test in `crates/buzz-db/src/runtime/tests.rs` that calls `db.query_feed_mentions_routed(...)` directly and asserts it returns only the caller's own community's replica-visible rows."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:539"
      - "crates/buzz-db/src/store/feed.rs:611"
      - "crates/buzz-db/src/runtime/tests.rs:1725-1735"
  - statement: "The relay bridge's `extract_feed_types` parser (rejecting non-array, mixed-type, empty, and absent `feed_types` values) is covered by its own unit tests (`extract_feed_types_valid`, `extract_feed_types_empty_array`, `extract_feed_types_mixed_types`, `extract_feed_types_absent`, `extract_feed_types_non_array`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:3559-3592"
  - statement: "The desktop app implements a second, independently-coded mentions path that does not go through the relay bridge's `feed_types` extension: the Tauri command `get_feed` (`desktop/src-tauri/src/commands/messages.rs`) builds its own `#p`-tagged relay filter over a fixed kind list (including stream messages, text notes, forum kinds, and git PR/issue/status kinds) directly against the relay, tags each result `FeedItemCategory::Mention`, and returns it under a `mentions` array; this is surfaced to the frontend as `HomeFeedResponse.feed.mentions` (`desktop/src/shared/api/tauri.ts`)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/messages.rs:49-145"
      - "desktop/src/shared/api/tauri.ts:58-83"
  - statement: "The desktop Home inbox exposes a user-facing \"Mentions\" filter option (value `mention`) alongside All/Projects/Threads/Needs action/Agents/Reminders/Drafts in its filter dropdown, and `matchesInboxFilter` matches an inbox item against that filter by checking whether the item's `categories` array includes `\"mention\"` (with `mention` also folded into the broader \"All\" view's own inclusion test)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/home/ui/InboxFilterMenu.tsx:14-24"
      - "desktop/src/features/home/lib/inboxViewHelpers.ts:41-76"
      - "desktop/src/features/home/lib/inboxViewHelpers.ts:78-100"
  - statement: "The desktop inbox's mentions-filter matching logic (`matchesInboxFilter`, `matchesInboxAllView`) has dedicated test coverage asserting that an item categorized `mentions` matches the `mentions` filter, that an item categorized only `activity` does not, and that an item with no categories does not match `mentions`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/home/lib/inboxViewHelpers.test.mjs:72"
      - "desktop/src/features/home/lib/inboxViewHelpers.test.mjs:156-166"
  - statement: "`launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`) is merged on `origin/launchpad` and states that a node built from it \"may declare `implements` toward this template node itself ... once this node is merged, if the author wants the generated `implemented-by` edge\", and `relationships.schema.json` defines `implements`' directionality as \"source is the concrete realization of target (e.g. a template instance of a standard)\"."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/capability.md:326-329"
      - "launchpad/docs/corpus/schema/relationships.schema.json:35-39"
  - statement: "At the recorded revision, no corpus node merged on `origin/launchpad` documents a Buzz architecture container, interface, or flow scoped specifically to the feed or mentions subsystem (the merged `architecture/containers`, `architecture/context`, `architecture/deployment`, `architecture/flows`, and `architecture/principles` nodes all cover other subsystems), so no `references` edge from this node to such a node currently resolves."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no architecture/interface/flow node named or scoped to feed/mentions, checked against the recorded revision's corpus tree"
  - statement: "The desktop `get_feed` mentions path and the CLI/relay-bridge `feed_types=[\"mentions\"]` path were not reconciled or deduplicated by this task; whether they are expected to converge, or are deliberately independent for latency/architecture reasons, was not established by any source read while drafting this node."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/feed.rs:1-20"
      - "desktop/src-tauri/src/commands/messages.rs:49-119"
    confidence: 0.6
relationships:
  - type: implements
    target: corpus-template-capability
---

# Mentions feed: capability

The mentions feed lets a human or agent user see, in one place, every event
across their accessible channels that names them directly — a message,
forum post, git pull request/issue, or git status change carrying their
pubkey in a `p` tag. It is one of the constituent categories of Buzz's Home
Feed, alongside items needing action, general channel activity, and agent
activity (VISION.md:133). A user does not have to have been present in a
channel at the moment of the mention, or to poll every channel individually,
to find out someone named them.

## Maturity

**Shipped.** The mentions feed is implemented and exposed through two
independent, currently-shipped paths:

- **`buzz-cli`** exposes `buzz feed get --types mentions`, which the relay's
  HTTP query bridge resolves to `Db::query_feed_mentions_routed` — a joined,
  indexed query against the `event_mentions` table, itself populated on every
  event insert.
- **The desktop app** exposes a "Mentions" filter in its Home inbox
  (`InboxFilterMenu.tsx`), backed by its own Tauri `get_feed` command, which
  queries the relay directly with a `#p`-tagged filter rather than going
  through the bridge's `feed_types` extension.

Both paths are covered by passing tests (see the evidence ledger above), and
neither is gated behind a feature flag or marked experimental in its own
source. See *Scope and omissions* for the fact that these two paths are
separately implemented and were not checked against each other for behavioral
parity by this node.

## Boundary

This node does not describe:

- **How the mentions feed is built** — the `event_mentions` table's schema
  and indexing strategy, the relay's routing/replica logic, or the desktop
  Tauri IPC boundary. Those are architecture-container subject matter; no
  corpus node currently documents them (see *Relationships* below).
- **The interface(s) the capability is exposed through** — `buzz-cli`'s
  `feed get --types mentions` subcommand and the relay's `POST /query`
  `feed_types` extension are interface-shaped surfaces in their own right;
  no interface node yet documents either.
- **The step-by-step flow through this capability** — how a single mention
  travels from message composition (`@name` extraction, `p`-tag creation:
  `crates/buzz-sdk/src/mentions.rs`) through insertion, indexing, and feed
  read. That is flow-shaped subject matter, not covered here.
- **How the mentions feed is operated** — monitoring query latency, capacity
  planning for `event_mentions`, or incident response. That is operations
  subject matter.

## Relationships

- implements: `corpus-template-capability` — this node is drafted from, and
  follows the required-sections skeleton of, the capability template.
- No `references` edge is declared. At the recorded revision, no corpus node
  merged on `origin/launchpad` documents a Buzz architecture container,
  interface, or flow scoped to the feed/mentions subsystem specifically, so
  no such target currently resolves (checked against
  `origin/launchpad`'s own corpus tree, not this node's worktree, per
  `AGENTS.md`'s guidance on the two branches diverging).

## Scope and omissions

**This node covers** what the mentions feed capability is, who it serves,
its current shipped maturity across both its CLI/relay-bridge and desktop
implementations, and the explicit boundary against how it is built, exposed,
walked step-by-step, and operated.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the mentions feed is built (event_mentions schema, relay routing, Tauri IPC) | a future architecture-container node (none merged yet) |
| The CLI/HTTP interface surface (`feed get --types mentions`, `feed_types` bridge extension) | a future interface node (none merged yet) |
| The step-by-step flow from `@mention` composition to feed read | a future flow node (none merged yet) |
| How the mentions feed is operated (monitoring, capacity, incidents) | the `operations` corpus surface |
| `@name`/NIP-27 mention extraction and `p`-tag construction (`crates/buzz-sdk/src/mentions.rs`) | a separate, independently-maintainable message-composition concept — out of scope for this task |
| Whether the desktop `get_feed` mentions path and the CLI/relay-bridge `feed_types=["mentions"]` path are intended to converge, or are deliberately independent | not established by any source read for this node (see the `INFERENCE` entry in the evidence ledger) |

**Expected but not verified when this node was written:**

- **No live end-to-end test was run.** All coverage cited above is unit-level
  (Rust `#[test]`/`#[tokio::test]` and desktop `.test.mjs`); this node does
  not claim to have exercised `buzz feed get --types mentions` or the desktop
  Home inbox's Mentions filter against a running relay.
- **Behavioral parity between the two mentions implementations was not
  checked.** Whether the desktop `get_feed` path and the CLI/bridge
  `query_feed_mentions_routed` path return the same events for the same
  user under the same conditions (e.g. identical kind allowlists, identical
  channel-accessibility rules) was not verified — their kind lists were read
  independently and are not byte-identical on inspection, but a full
  behavioral diff was not performed.
