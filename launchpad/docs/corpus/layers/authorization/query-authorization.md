---
id: layers-authorization-query-authorization
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The WebSocket REQ handler (`handle_req`) requires an authenticated connection and, if the connection carries any scopes, requires `Scope::MessagesRead` among them; an unauthenticated or insufficiently-scoped REQ is closed before any query executes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:51-480"
  - statement: "`handle_req` resolves the caller's accessible channel set via `AppState::get_accessible_channel_ids_cached`, which serves a per-(community, pubkey) cache and falls back to `Database::get_accessible_channel_ids` on a cache miss."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:51-480"
      - "crates/buzz-relay/src/state.rs:1232-1249"
  - statement: "For each explicitly requested channel (`#h` tag) not already in the cached accessible set, `handle_req` confirms membership directly against the database (`Database::is_member`) rather than trusting a stale cache negative, and a verified positive repairs the in-memory accessible-channels vector for the rest of the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:51-480"
  - statement: "If a REQ names one or more explicit channels and none of them survive authorization, `handle_req` sends a CLOSED with reason `restricted: not a channel member` rather than registering a subscription that could never produce output."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:51-480"
  - statement: "For a global (non-channel-scoped) REQ, `handle_req` runs three filter-level gates in this order before the NIP-50 search branch and before subscription registration: `p_gated_filters_authorized`, `engram_filters_authorized`, and `author_only_filters_authorized`, each closing the subscription with a `restricted:` reason on failure. The comment at this call site states this ordering exists specifically so a search filter cannot be used to harvest indexed-but-globally-stored sensitive events, since search hits skip the per-filter post-check the historical-delivery branch applies."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:51-480"
  - statement: "`p_gated_filters_authorized` treats a filter with no `kinds` field as able to match any P_GATED_KINDS value (`filter.kinds.as_ref().is_none_or(...)` defaults to true), so an omitted `kinds` is authorized only when the filter's `#p` tag is present and equals exactly the authenticated reader's own pubkey; a REQ or COUNT with no `kinds` and no matching `#p` is rejected by this gate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1182-1216"
  - statement: "`P_GATED_KINDS` is kind:24200 (agent observer frame), kind:44100/44101 (member-added/member-removed notification), kind:1059 (gift wrap), kind:30622 (DM visibility), and kind:44200 (agent turn metric); these are kinds whose stored events are readable only by a subscriber whose pubkey appears in the event's `#p` tag, enforced at the filter layer by `p_gated_filters_authorized` rather than only at the result level."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:159-169"
      - "crates/buzz-core/src/kind.rs:60"
      - "crates/buzz-core/src/kind.rs:449"
      - "crates/buzz-core/src/kind.rs:469"
      - "crates/buzz-core/src/kind.rs:532-536"
      - "crates/buzz-core/src/kind.rs:545"
  - statement: "`AUTHOR_ONLY_KINDS` (event reminder, push lease, private managed agent) are kinds whose stored events must be readable only by their own author; `author_only_filters_authorized` enforces this at the filter layer when a filter's `kinds` targets exclusively author-only kinds, requiring `authors` to equal exactly the authenticated reader."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:129-133"
      - "crates/buzz-relay/src/handlers/req.rs:1395-1414"
  - statement: "`engram_filters_authorized` enforces that a filter able to match kind:30174 (NIP-AE agent engram, an agent's encrypted memory record) is authorized only when the filter's `authors` is exactly the reader, or its `#p` tag is exactly the reader — mirroring the same self-or-addressed-to-self pattern as the p-gate and author-only gate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1239-1269"
      - "crates/buzz-core/src/kind.rs:94"
  - statement: "After a historical query executes, `handle_req` applies two further per-event checks before an event is sent to the subscriber: (1) if the stored event carries a `channel_id`, it must be present in the caller's accessible-channels set, and (2) `event_visible_to_reader` must return true for the event and the reader's pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:51-480"
  - statement: "`event_visible_to_reader` composes three checks: the event must not be an author-only event the reader does not own (`is_author_only_event`), must not be an unshared-gated event the reader cannot see (`is_unshared_gated_event`), and must pass `buzz_core::filter::reader_authorized_for_event` (the general `#p`/result-gate check covering kinds like DM visibility and agent turn metric)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1368-1380"
  - statement: "The WebSocket COUNT handler (`handle_count`) enforces the identical gate sequence as `handle_req` — auth required, `p_gated_filters_authorized`, `engram_filters_authorized`, `author_only_filters_authorized`, cached-accessible-channels resolution with the same DB-confirmed fallback for explicitly requested channels, and token-channel-scope narrowing — with its own inline comments stating this is 'same enforcement as WS REQ handler' at each corresponding step."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:18-317"
  - statement: "`handle_count` additionally reasons about which filters are safe for the fast SQL `count_events()` pushdown (`filter_fully_pushable`) versus which require a bounded fallback query plus per-event post-filtering (`needs_author_only_filtering`, `needs_shared_gate_filtering`, `needs_result_gated_filtering`), so that a gated kind's count is never computed by a SQL path that skips the per-event authorization check that `event_visible_to_reader`-equivalent logic performs in the fallback branch."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:18-317"
  - statement: "The HTTP bridge endpoints `POST /query` and `POST /count` (`query_events`, `count_events` in `crates/buzz-relay/src/api/bridge.rs`) each first bind the request to a community from the request's `Host` header via `crate::tenant::bind_community`, failing closed with a generic 404 on an unmapped host, then authenticate the caller via NIP-98 (`verify_bridge_auth`) before any query executes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:887-949"
      - "crates/buzz-relay/src/api/bridge.rs:1375-1434"
  - statement: "`query_events`'s underlying `query_events_authed` helper (starting line 954) and `count_events`'s underlying `count_events_authed` helper (starting line 1439) each run the identical p-gate and author-only-gate checks as the WebSocket REQ/COUNT path, with the bridge.rs source comments at each site explicitly stating 'same as WS REQ handler' (in `query_events_authed`) and 'same as WS REQ and /query' (in `count_events_authed`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:954-1005"
      - "crates/buzz-relay/src/api/bridge.rs:1439-1482"
  - statement: "`buzz-auth`'s `ChannelAccessChecker` trait and its `check_read_access`/`check_write_access` functions (`crates/buzz-auth/src/access.rs`, re-exported from `crates/buzz-auth/src/lib.rs`) have no call sites anywhere in the workspace outside their own unit tests in `access.rs` itself, confirmed by a direct `grep -rn check_read_access crates/` across every crate in the repository."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs:31-57"
      - "crates/buzz-auth/src/access.rs:72-85"
      - "crates/buzz-auth/src/lib.rs:33"
  - statement: "The actual read-path authorization mechanism is not `buzz-auth`'s `ChannelAccessChecker` trait but a separate implementation living directly in `buzz-relay` (`AppState::get_accessible_channel_ids_cached` plus `Database::is_member`) and `buzz-core` (the gated-kind constant lists and filter-level authorization functions in `req.rs`), so the trait's non-use on the read path is the same category of finding the sibling event-authorization node reports for the write/ingest path, not a contradiction of it."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/access.rs:31-57"
      - "crates/buzz-relay/src/handlers/req.rs:51-480"
      - "crates/buzz-relay/src/state.rs:1232-1249"
    confidence: 0.85
  - statement: "Buzz's CLAUDE.md states as a project-wide gotcha that 'Relay queries must specify kinds — omitting kinds triggers the p-gate (403)', which is the same behavior this node traces to `p_gated_filters_authorized`'s `is_none_or` default rather than a separately implemented top-level kinds requirement."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "CLAUDE.md (repo root), Common Gotchas #2"
  - statement: "Issue #1039's own Definition of Done requires exactly one hand-authored canonical document, schema-valid front matter with typed relationships where appropriate, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links to related concepts/implementation/verification without duplicating them, a check against the recorded provenance revision, a clean validator run, a one-sentence definition before deeper explanation, stated boundaries/non-goals, and examples that clarify rather than introduce a second concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1039 definition of done"
  - statement: "At the recorded revision, `origin/launchpad`'s `launchpad/docs/corpus` tree contains no `layers/` directory and no node whose subject is authorization, so no `relationships` target exists yet for this node to declare against; sibling tasks #1035 (event-authorization) and #1033 (channel-roles) are open, unmerged, and authored in parallel with no ordering guarantee against this node."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/**, standards/**; no layers/ directory present"
---

# Query authorization

**Query authorization is the set of checks Buzz's relay applies to a read
request — a WebSocket `REQ`, a WebSocket `COUNT`, or their HTTP equivalents
`POST /query` and `POST /count` — that decide which stored events, if any,
the requester is allowed to see.** It answers a narrower question than
"is this caller allowed to talk to the relay at all": given an authenticated
caller and a NIP-01 filter, which events in that filter's match set does the
relay actually return, or count, for that specific caller?

## Definition

Query authorization runs in three layers, applied in order, on every REQ,
COUNT, `/query`, and `/count` request:

1. **Connection-level gates.** The caller must be authenticated
   (`AuthState::Authenticated`), and if the connection carries any scopes at
   all, `Scope::MessagesRead` must be among them. This runs first and closes
   the request immediately on failure — no query is ever built for an
   unauthenticated or insufficiently-scoped caller.

2. **Filter-level gates.** Before any database query executes, every filter
   is checked against three sensitive-kind rules — the *p-gate*
   (`p_gated_filters_authorized`), the *engram gate*
   (`engram_filters_authorized`), and the *author-only gate*
   (`author_only_filters_authorized`) — plus channel-membership resolution
   (accessible-channels cache, confirmed against the database for any
   explicitly requested channel not already in the cached set). A filter
   that fails any of these never reaches the database.

3. **Result-level gates.** Each row returned by a query is checked again
   before it is sent to the caller: its `channel_id`, if any, must be in the
   caller's accessible-channels set, and `event_visible_to_reader` must
   return true — a second check that exists because a filter can be
   authorized in the abstract ("this filter's `#p` matches you") while an
   individual matched event still needs its own visibility rule applied
   (for example, an author-only event reached via a kindless `ids` lookup).

The WebSocket `REQ`/`COUNT` handlers and the HTTP `/query`/`/count` bridge
endpoints implement this same three-layer shape independently, not through
one shared authorization function — see *Boundary* below.

## Use cases

- **Explaining a 403 or a `restricted:` CLOSED reason.** A caller whose REQ
  or `/query` request is rejected with `restricted: p-gated events require
  #p matching your pubkey`, `restricted: not a channel member`, or a similar
  message hit one of the gates named above. Knowing the layer a rejection
  came from (connection, filter, or result) narrows where to look.
- **Understanding why omitting `kinds` can trigger the p-gate.** A filter
  with no `kinds` field is treated by `p_gated_filters_authorized` as able
  to match any gated kind, so it is authorized only if `#p` already pins the
  request to the caller's own pubkey. This is the mechanism behind the
  project-wide guidance that relay queries should specify `kinds` explicitly
  (see the `TEAM_KNOWLEDGE` evidence entry above).
- **Auditing whether a new gated kind is actually enforced on the read
  path**, and not just on ingest — this node's evidence traces the specific
  functions and constant lists (`P_GATED_KINDS`, `AUTHOR_ONLY_KINDS`,
  `KIND_AGENT_ENGRAM`) an author adding a new sensitive kind needs to touch.

## Boundary: what this node does not cover

**Not channel/community read-access assignment.** *Who* is a member of a
channel — invites, roles, community-level membership — is decided
elsewhere (channel-roles authorization, sibling issue #1033's node once it
exists). This node covers only how a query *consults* that existing
membership state (`get_accessible_channel_ids_cached`, `is_member`), not how
membership is granted or revoked.

**Not event ingestion/write authorization.** Whether a caller may *publish*
an event of a given kind, to a given channel, is a separate enforcement path
(`crates/buzz-relay/src/handlers/ingest.rs`, `required_scope_for_kind`,
`requires_h_channel_scope`) covered by sibling issue #1035's
event-authorization node. The two paths share some of the same gated-kind
*data* (`buzz-core::kind`'s constant lists) but not the same enforcement
code.

**Not `buzz-auth`'s `ChannelAccessChecker` trait.** `buzz-auth` defines a
`ChannelAccessChecker` trait and `check_read_access`/`check_write_access`
functions that look, by name, like the natural place to find this
enforcement. They are not: as the evidence ledger above records, neither has
any call site anywhere in the workspace outside their own unit tests. The
real read-path enforcement lives directly in `buzz-relay` and `buzz-core`,
described in *Definition* above. This is stated plainly here rather than
silently — a reader who goes looking for query authorization in
`buzz-auth` first, by name, will find a well-tested trait that the relay
does not actually call.

**Not NIP-42 WebSocket authentication itself** — establishing *who* the
authenticated pubkey is, before any filter is evaluated, is a separate,
earlier concern (authentication-layer territory, related to issue #1028).

**Not git smart-HTTP or Blossom media read access** — those are separate
HTTP surfaces (`crates/buzz-relay/src/api/git/`, `crates/buzz-relay/src/api/media.rs`)
with their own authorization logic, not the NIP-01 filter path this node
describes.

## Example: a query with no matching gate never touches the database

A REQ filter like `{"authors": ["<some-channel-member>"], "kinds": [40001]}`
(an ordinary channel message kind) matches none of `P_GATED_KINDS`,
`AUTHOR_ONLY_KINDS`, or `KIND_AGENT_ENGRAM`, so all three filter-level gates
short-circuit to "not applicable" for it, and the only enforcement that
applies is channel-membership resolution and the per-event checks in
*Definition*, step 3. This is the common case — the gates in step 2 exist
specifically for the small set of sensitive kinds named in the evidence
ledger, not for every filter that reaches the relay.

## Scope and omissions

**This node covers** the authorization checks Buzz's relay applies to
read/query requests — WebSocket `REQ`/`COUNT` and HTTP `POST /query`/`POST
/count` — across their connection-level, filter-level, and result-level
gates, and states plainly that `buzz-auth`'s `ChannelAccessChecker` trait is
not part of that enforcement today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Channel/community membership assignment (who becomes a member and how) | #1033 (channel-roles authorization), not yet merged |
| Event ingestion/write authorization | #1035 (event-authorization), not yet merged |
| NIP-42 WebSocket authentication (establishing the authenticated pubkey) | Related to #1028, not this node's subject |
| Git smart-HTTP and Blossom media read authorization | Separate HTTP surfaces, not filed against this node |
| Whether `buzz-auth`'s unused `ChannelAccessChecker` trait should be wired up, removed, or is intentionally reserved | Not established here — reported as a verified fact, not resolved |

**Expected but not verified when this node was written:**

- Whether the read-path enforcement in `req.rs`/`count.rs`/`bridge.rs` and
  the write-path enforcement `buzz-auth`'s unused trait was apparently
  intended to serve were ever the same code path historically (e.g. before
  a refactor) was not investigated — this node reports the current state
  only, via `git blame`/history was not run.
- `AUTHOR_ONLY_KINDS`'s three members (event reminder, push lease, private
  managed agent) are named descriptively above without restating their
  numeric kind values (`P_GATED_KINDS`'s values are verified and cited
  directly in the evidence ledger; `AUTHOR_ONLY_KINDS`'s are not), since
  that list's own doc comment warns it may grow past a small linear set — a
  reader who needs the current integers should read
  `crates/buzz-core/src/kind.rs` directly rather than trust a copy here,
  which would drift silently if the list changes.
- No relationship to #1033 or #1035 is declared because neither is merged
  at authoring time (see the `FACT` evidence entry above, checked directly
  against `origin/launchpad` rather than assumed) — a future edit to add
  `references` edges once both merge is expected but not made here.
