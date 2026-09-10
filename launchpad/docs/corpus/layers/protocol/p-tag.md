---
id: layers-protocol-p-tag
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "P_GATED_KINDS in kind.rs is a six-member slice -- KIND_AGENT_OBSERVER_FRAME (24200), KIND_MEMBER_ADDED_NOTIFICATION (44100), KIND_MEMBER_REMOVED_NOTIFICATION (44101), KIND_GIFT_WRAP (1059), KIND_DM_VISIBILITY (30622) and KIND_AGENT_TURN_METRIC (44200) -- and its doc comment describes them as kinds whose stored events have `#p`-bound read access, readable only by subscribers whose pubkey appears in the event's `#p` tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "That same doc comment states that for the stored (non-ephemeral) kinds in the set the storage layer additionally writes a NULL `search_tsv` so the event is unsearchable through NIP-50 full-text search, while ephemeral kinds such as KIND_AGENT_OBSERVER_FRAME are included for filter-layer enforcement only because they are never stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "p_gated_filters_authorized decides whether a filter can match a p-gated kind with `filter.kinds.as_ref().is_none_or(...)`, so a filter carrying no `kinds` clause at all is treated as capable of matching a p-gated kind rather than being waved through."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Once a filter is judged capable of matching a p-gated kind, p_gated_filters_authorized authorizes it only if either a non-empty `ids` clause is present (the ids exemption) or the filter's `#p` values are non-empty and every one of them equals the authenticated reader's hex pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The `ids` exemption is withdrawn -- so the `#p`-owner check must hold regardless -- for filters that explicitly name KIND_DM_VISIBILITY or KIND_AGENT_TURN_METRIC, because (per the function's own comments) kind 30622 is relay-signed so its id is not author-bound and its content is plaintext hide choices, and kind 44200's cleartext envelope leaks turn-activity metadata; a kindless `ids` lookup is deliberately unaffected by that withdrawal."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A REQ whose filters fail this gate is closed with the message \"restricted: p-gated events require #p matching your pubkey\", and the gate runs before the NIP-50 search branch and only for global (channel_id = None) subscriptions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The same p_gated_filters_authorized function is reused by the COUNT handler and by the HTTP bridge (which rejects with HTTP 403 and the wording \"restricted: p-gated kinds require #p tag matching your pubkey\" rather than the REQ handler's close message), so the `p` tag's authorization role is not specific to the WebSocket REQ path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "kind.rs declares four separate gate slices -- AUTHOR_ONLY_KINDS, RESULT_GATED_KINDS, P_GATED_KINDS and SHARED_GATED_KINDS -- and RESULT_GATED_KINDS is exactly [KIND_DM_VISIBILITY, KIND_AGENT_TURN_METRIC], a two-member subset of P_GATED_KINDS."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's per-constant doc comments state what the `p` tag names for four of the six p-gated kinds: KIND_GIFT_WRAP is the \"outer envelope for private DMs -- hides sender, content, timestamp\", KIND_AGENT_OBSERVER_FRAME is \"owner-scoped encrypted agent observer telemetry and control frame\" in the ephemeral 20000-29999 range that is never stored, and KIND_MEMBER_ADDED_NOTIFICATION and KIND_MEMBER_REMOVED_NOTIFICATION are both relay-signed and \"stored globally (channel_id = None) with p-tag = target, h-tag = channel UUID\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-core's reader_authorized_for_event is a second, result-level `#p` check applied per delivered event for KIND_DM_VISIBILITY and KIND_AGENT_TURN_METRIC, returning true for every other kind, and its doc comment states it exists so that a query bypassing the filter-level gate (for example a kindless `ids:[...]` lookup of a known event id) still cannot read another user's private event."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "filter_to_query_params pushes a `#p` constraint into SQL only when the filter's `#p` carries exactly one value; for two or more values it leaves `p_tag_hex` as None, and the surrounding comment gives gift-wrap and membership-notification queries as the motivating case where other recipients' events would otherwise push the caller's events past the LIMIT before post-filtering."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "filter_fully_pushable returns false for a `#p` with more than one value, and its doc comment lists multi-`#p` alongside `#t`, `#a`, `search` and `#d` on non-NIP-33 kinds as constraints that require post-filtering and cannot use the fast COUNT path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The historical-delivery loop applies buzz_core::filter::filters_match to each returned row after the database query, and filter_match_one matches a generic tag by comparing the filter's value byte-exactly against the event's tag content."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-core/src/filter.rs"
  - statement: "A multi-value `#p` REQ therefore has its per-filter LIMIT applied by SQL to rows that carry no `#p` restriction at all, and the `#p` match is re-applied in Rust only afterwards, so a caller's matching events can be pushed out of the result window by other recipients' events -- exactly the failure the single-value pushdown was added to avoid."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-core/src/filter.rs"
    confidence: 0.85
  - statement: "The COUNT handler handles the same non-pushable case differently from REQ: it fetches a bounded candidate set (COUNT_FALLBACK_CANDIDATE_LIMIT of 5,000 rows plus one), post-filters in Rust, and closes the subscription with \"restricted: count filter requires narrower constraints\" rather than returning a truncated count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "insert_mentions_in_transaction extracts every tag whose first element is \"p\" and which has at least two elements, rejects any value that is not exactly 64 ASCII hex characters (logging it as a malformed p-tag), lowercases the survivors, and inserts them into event_mentions with ON CONFLICT DO NOTHING in chunks of 5,000 rows to stay under Postgres's 65,535 bind-parameter cap -- the function's own comment gives relay-signed kind:39002 rosters, which carry one p-tag per channel member, as the case that can exceed a single statement's row budget."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "event_mentions is primary-keyed (community_id, pubkey_hex, event_id), so the table holds at most one row per distinct mentioned pubkey per event rather than one row per literal `p` tag; a repeated `p` tag collapses under the ON CONFLICT DO NOTHING clause."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "The single-value `#p` SQL pushdown is served by an INNER JOIN of events against event_mentions on the community tuple (e.community_id = m.community_id AND e.id = m.event_id) with m.pubkey_hex compared against the lowercased filter value."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "Buzz's own NIP-AM requires an agent turn metric event to carry exactly one `p` tag (the owner) and exactly one `agent` tag, and states that only a party whose authenticated pubkey equals the `#p` tag value may receive the event."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AM.md"
  - statement: "Buzz's own NIP-DV states that a kind:30622 snapshot carries exactly one `p` tag whose value equals the `d` value, names the `p` tag as \"the read-authorization key\", and says the two tags are deliberately redundant because `d` addresses the replaceable event while `p` authorizes the reader."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-DV.md"
  - statement: "No upstream numbered Nostr NIP specification text is present in this repository -- docs/nips/ holds only Buzz's own two-letter custom NIPs -- so any claim about what upstream NIP-01 or NIP-17 requires cannot be a FACT on a repository path here."
    entry_class: FACT
    evidence:
      - "list_dir_count(path='docs/nips/', pattern='^NIP-[0-9]+\\.md$') -> 0 matching files; only two-letter Buzz NIPs (NIP-AA, NIP-AM, NIP-DV, NIP-RS, ...) are present"
  - statement: "The all-values-must-match rule is covered live by test_membership_notification_multi_p_rejected in buzz-test-client's e2e_relay suite, an #[ignore]-gated test that subscribes to kinds 44100/44101 with a `#p` containing both the authenticated pubkey and a second party's, and asserts the relay answers CLOSED; test_nip17_gift_wrap_requires_p_filter in e2e_nostr_interop covers the missing-`#p` case for kind:1059."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "No unit or integration test function for filter_fully_pushable exists in the crates tree at the recorded revision; every occurrence of the name is either its definition or a call site."
    entry_class: FACT
    evidence:
      - "grep_r('filter_fully_pushable', path='crates/') -> 5 matches: 1 definition in buzz-relay/src/handlers/req.rs, 2 call sites in buzz-relay/src/api/bridge.rs, 2 call sites in buzz-relay/src/handlers/count.rs; no test function"
  - statement: "Issue #1162 requires that this node define the term in one sentence before deeper explanation, state boundaries and what the concept must not be confused with, link to related concepts, implementation and verification without duplicating their canonical content, and use examples only to clarify the concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1162 definition of done"
relationships:
  - type: references
    target: capabilities-messaging-mention
  - type: references
    target: capabilities-activity-mentions-feed
  - type: references
    target: capabilities-messaging-direct-message
  - type: references
    target: capabilities-messaging-gift-wrap
  - type: references
    target: layers-data-postgres-events-table
  - type: references
    target: architecture-flows-historical-query
  - type: references
    target: implementation-crates-buzz-core
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: verification-contracts-nostr
---

# The `p` tag

**A `p` tag is a Nostr event tag whose first element is the literal string `p` and whose
second element is a hex-encoded public key, naming a person or agent the event is
*about* — and in Buzz it is simultaneously a reference, a delivery address, and, for six
event kinds, the key the relay's read-authorization gate checks.**

(Buzz's mention indexer accepts only values of exactly 64 ASCII hex characters and
lowercases them before storing; a `p` tag whose value fails that check is logged and
skipped rather than rejecting the event. So 64-char lowercase hex is what Buzz *indexes*,
not a shape this node claims the tag is constrained to at the protocol level.)

That third role is what makes this tag unlike its siblings. An `e` tag points at an event
and an `h` tag scopes a message to a channel; neither decides whether you are permitted to
read anything. A `p` tag does. For the kinds listed in `P_GATED_KINDS`, the value in the
`p` tag *is* the access-control decision, and the relay will close a subscription that
asks for those kinds without proving the reader owns that pubkey.

## The three roles, and why they are one tag

**As a reference.** A `p` tag says "this event concerns this pubkey." Nothing in the tag
itself distinguishes an @-mention from a DM recipient from an event owner; the *kind*
supplies that meaning. This is why the same two-element shape can carry a channel
member roster (one `p` per member on a relay-signed kind:39002) and a private per-viewer
snapshot (exactly one `p`, the owner) without any change to the tag format.

**As a delivery address.** Every `p` tag on every inserted event is projected into the
`event_mentions` table, which is what makes "show me everything addressed to me" an
indexed lookup rather than a scan of the `tags` JSONB column. The projection is
lossy on purpose: values that are not exactly 64 ASCII hex characters are logged and
dropped, survivors are lowercased, and the table's primary key
(`community_id`, `pubkey_hex`, `event_id`) collapses a repeated `p` tag to one row. So the
honest statement is *one row per distinct valid mentioned pubkey per event*, not one row
per literal tag.

The table's own schema, indexes and rebuildability are
`layers-data-postgres-events-table`'s subject, not this node's.

**As an authorization key.** Six kinds carry `#p`-bound read access:

| Kind | Constant | What the `p` tag names |
|---|---|---|
| 1059 | `KIND_GIFT_WRAP` | the party the outer envelope is addressed to (`kind.rs`: "outer envelope for private DMs") |
| 24200 | `KIND_AGENT_OBSERVER_FRAME` | the owner of the observer frame (`kind.rs`: "owner-scoped encrypted agent observer telemetry"; ephemeral, never stored) |
| 30622 | `KIND_DM_VISIBILITY` | the viewer whose hide-state this snapshot is (NIP-DV) |
| 44100 | `KIND_MEMBER_ADDED_NOTIFICATION` | the target pubkey added to the channel (`kind.rs`: "p-tag = target") |
| 44101 | `KIND_MEMBER_REMOVED_NOTIFICATION` | the target pubkey removed from the channel (`kind.rs`: "p-tag = target") |
| 44200 | `KIND_AGENT_TURN_METRIC` | the owner the metric is encrypted to (NIP-AM) |

This table exists to make the *set* legible, not to catalogue the kinds. Each kind's own
semantics belong to its kind node or its owning capability node.

## How the gate decides

`p_gated_filters_authorized` evaluates every filter in a REQ and requires **all** of them
to pass. Per filter, in order:

1. **Can this filter match a p-gated kind?** The check is
   `filter.kinds.as_ref().is_none_or(...)`. The `is_none_or` is the load-bearing part: a
   filter with **no `kinds` clause at all** is treated as *possibly* matching a p-gated
   kind, and falls through to the checks below. A wildcard is not a free pass. If the
   filter names kinds and none of them is p-gated, it is authorized immediately.
2. **Does it name a specific event?** A non-empty `ids` clause authorizes the filter —
   "knowing the id implies authorization." But this exemption is **withdrawn** when the
   filter *explicitly names* `KIND_DM_VISIBILITY` or `KIND_AGENT_TURN_METRIC`. Kind 30622
   is relay-signed, so its id is not author-bound and could be guessed or replayed by a
   party who never had read access; kind 44200's cleartext envelope leaks turn-activity
   metadata. A *kindless* `ids` lookup keeps the exemption at this layer — deliberately —
   and is closed instead at the result level (below).
3. **Otherwise, prove ownership.** The filter's `#p` values must be non-empty and **every
   one** of them must equal the authenticated reader's hex pubkey. A filter asking for
   your pubkey *and* someone else's fails.

A filter that reaches the end without passing closes the subscription with
`restricted: p-gated events require #p matching your pubkey`. The gate runs before the
NIP-50 search branch, so an authenticated member cannot launder a p-gated kind through a
`search` filter, and it applies only to global (non-channel-scoped) subscriptions. The
same function backs the COUNT handler and the HTTP bridge — the bridge rejecting with a
403 and its own wording rather than a close frame — so this is a property of the `p` tag
in Buzz, not of one transport.

**The second layer.** `reader_authorized_for_event` in `buzz-core` re-checks the `#p`
owner per delivered event, for kinds 30622 and 44200 only, returning `true` for every
other kind. That is what closes the kindless-`ids` path step 2 leaves open. The two layers
answer different questions — *may you ask this?* and *may you have this row?* — and the
step-2 exemption is only safe because the second layer exists.

The end-to-end shape of a historical query, including where these gates sit relative to
channel-access resolution, is `architecture-flows-historical-query`'s subject.

**How this is verified.** Step 3's "every one of them" is not just a code reading:
`test_membership_notification_multi_p_rejected` subscribes to kinds 44100/44101 with a
`#p` carrying the authenticated pubkey *and* a second party's, and asserts the relay
answers `CLOSED` — a filter that includes your own key alongside someone else's is
rejected, not silently narrowed. `test_nip17_gift_wrap_requires_p_filter` covers the
missing-`#p` case for kind:1059. Both are `#[ignore]`-gated and need a live relay; the
wider Nostr contract they belong to is `verification-contracts-nostr`'s subject.

## The query-side asymmetry: single-valued `#p` is privileged

A `#p` constraint is pushed down into SQL **only when it carries exactly one value**.
`filter_to_query_params` reads the filter's `#p` set and populates `p_tag_hex` if and only
if `values.len() == 1`; two or more values leave it `None`. The single-value case becomes
an `INNER JOIN` against `event_mentions` on the community tuple, matching on the
`pubkey_hex` column that table is indexed on.

For two or more values there is no SQL `#p` constraint at all. The per-filter `LIMIT` is
then applied by Postgres to rows that have **not** been narrowed by `#p`, and the `#p`
match is re-applied in Rust afterwards by `filters_match`. The consequence is the one the
pushdown was introduced to prevent, reappearing whenever a client sends more than one
value: other recipients' events consume the result window before the caller's own events
are reached. The code's own comment names gift-wrap and membership-notification queries as
the motivating case.

`filter_fully_pushable` encodes the same rule for COUNT, listing multi-`#p` alongside
`#t`, `#a`, `search` and `#d`-on-non-NIP-33 as non-pushable. COUNT then diverges from REQ:
rather than silently truncating, it fetches a bounded 5,001-row candidate set,
post-filters, and closes with `restricted: count filter requires narrower constraints` if
the budget is exceeded — because a count that is quietly wrong is worse than no count.

**The practical reading**: query one `#p` value per filter. Two filters each naming one
pubkey are OR-ed with per-filter limits; one filter naming two pubkeys is not.

## What this must not be confused with

- **A `p` tag is not an @-mention.** The mention is a *product* feature — resolving
  `@name` against membership, agents and teams, capping and deduplicating, overriding mute
  state. That resolution pipeline and its guarantees are
  `capabilities-messaging-mention`'s. The `p` tag is what it emits.
- **A `p` tag is not the mentions feed.** The feed's query, kind allowlist and limits are
  `capabilities-activity-mentions-feed`'s.
- **A `p` tag is not a statement about encrypted content.** For a gift wrap (kind:1059,
  which `kind.rs` describes as the "outer envelope for private DMs — hides sender,
  content, timestamp") the `p` tag is what the relay routes and gates on; what the sealed
  payload actually contains is opaque to the relay, and the relationship between the
  envelope's `p` tag and the inner message is
  `capabilities-messaging-gift-wrap`'s and `capabilities-messaging-direct-message`'s
  subject, not this node's.
- **`#p` (the filter key) is not `p` (the event tag).** The relay compares one against the
  other, but they are authored by different parties at different times: the event's tag by
  the signer, the filter's `#p` by the reader. The gate's whole job is deciding whether
  the reader may assert the value the signer wrote.
- **A `p` tag is not a channel scope.** Channel membership is carried by `h`; a `p` tag
  neither grants nor implies channel access, and the p-gate runs only on global
  subscriptions precisely because channel-scoped ones can never reach globally-stored
  p-gated events.
- **"p-gated" is not "author-only" and not "result-gated."** `P_GATED_KINDS`,
  `AUTHOR_ONLY_KINDS`, `SHARED_GATED_KINDS` and `RESULT_GATED_KINDS` are four separate
  slices in `kind.rs` with four separate gate functions; `RESULT_GATED_KINDS` is a
  two-member subset of `P_GATED_KINDS`, which is why kinds 30622 and 44200 appear under
  both mechanisms.

## Why an author cares

- **Adding a kind whose content is private to one party?** Putting the owner in a `p` tag
  is not enough — the kind must be added to `P_GATED_KINDS`, and if knowing the event id
  must not imply access, it also needs the `ids`-exemption withdrawal and a
  `RESULT_GATED_KINDS` entry. The tag alone gates nothing.
- **Writing a client query for anything p-gated?** Send one `#p` value equal to your own
  pubkey. Omitting `kinds` does not widen your access, it narrows it: `is_none_or` puts a
  kindless filter *into* the gate.
- **Debugging "my events are missing near the limit"?** Check the `#p` cardinality before
  suspecting the database.

## Scope and omissions

**This node covers** what a `p` tag is, the three roles it plays in Buzz, the six kinds
whose read access it controls, the order in which `p_gated_filters_authorized` decides,
the second result-level check that backs it, and the single-value SQL pushdown asymmetry.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| @-name resolution into `p` tags, mention caps, mute override | `capabilities-messaging-mention` |
| The mentions feed query, its kind allowlist and its limits | `capabilities-activity-mentions-feed` |
| DM addressing and gift-wrap recipient semantics | `capabilities-messaging-direct-message`, `capabilities-messaging-gift-wrap` |
| The `event_mentions` table's schema, indexes and rebuildability | `layers-data-postgres-events-table` |
| Where these gates sit in the full historical-query path | `architecture-flows-historical-query` |
| Tags as a general protocol construct, and the `e`, `d` and `h` tags individually | Sibling protocol-layer tasks under Feature #609, unmerged at the recorded revision |
| Per-kind semantics of each p-gated kind | Each kind's own node or owning capability node |

**Expected but not verified when this node was written:**

- **No test exercises `filter_fully_pushable`.** Every occurrence of the name in `crates/`
  is its definition or a call site — there is no unit or integration test asserting that a
  two-value `#p` is judged non-pushable. The single-value pushdown asymmetry above is read
  from the code, not confirmed by a test that would fail if it regressed. Note the
  contrast: the *authorization* half of this node has live e2e coverage (above); the
  *pushdown* half has none. Those are different confidence levels and should not be read
  as one.
- **The e2e tests were not run.** Both are `#[ignore]`-gated and require a live relay with
  Postgres and Redis; they were read, not executed, so what is established here is that
  the assertions exist and match the code path — not that they currently pass.
- **No relay was run.** The claim that a multi-value `#p` REQ loses a caller's events to
  the `LIMIT` is reasoned from the code path (SQL constraint absent, `LIMIT` applied,
  `filters_match` after) and from the code's own comment about the motivating case. It was
  not reproduced against a live relay, which is why it is classified `INFERENCE` rather
  than `FACT`.
- **No upstream NIP text is in this repository.** `docs/nips/` holds only Buzz's own
  two-letter NIPs; there is no `NIP-01.md` or `NIP-17.md`. Every claim above about what a
  `p` tag *means* is therefore sourced from Buzz's code and Buzz's own NIPs, and this node
  makes no claim about what upstream Nostr requires.
- **Case handling was read, not exercised.** The p-gate compares `#p` values byte-exactly
  against the reader's hex pubkey, `insert_mentions_in_transaction` lowercases before
  storing, and the SQL join lowercases the filter value. Those three behaviours are
  consistent on paper for lowercase-hex input; what a mixed-case `#p` filter actually
  returns end-to-end was not tested.
