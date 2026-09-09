---
id: layers-protocol-filter
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "buzz-core's filter module states its own composition rule in its module doc: multiple filters are OR-ed, and fields within one filter are AND-ed, which filters_match implements as filters.iter().any(...) over filter_match_one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "filter_match_one evaluates kinds, authors, since, until, ids and the filter's generic single-letter tag clauses, and returns false on the first clause that does not match."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "The ids clause matches by hex prefix rather than by equality, and the code records NIP-01 as the reason in its own comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "The #h clause carries a Buzz-specific fallback: an event with no h tags at all may still match through StoredEvent.channel_id, but an event that carries explicit h tags is matched strictly on those and the fallback must not override them."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "A unit test named h_tag_fallback_uses_stored_channel_id asserts all four branches of that fallback, including that an explicit h tag pointing at another channel must not be rescued by a matching stored channel_id."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "filter_to_query_params pushes into SQL exactly kinds, authors (a single author through the pubkey column, several through an authors IN-list), ids, since, until, #e values of any count, a single-value #p through the event_mentions join, and #d only when the filter targets NIP-33 parameterized-replaceable kinds exclusively; the authorized channel scope is injected separately by apply_channel_scope_to_query."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "filter_fully_pushable's own documentation names the clauses SQL cannot represent — multi-value #p, #t, #a, search, and #d on a filter that is not NIP-33-only — and it returns false for any of them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The REQ historical-delivery loop re-applies filters_match to every row the database returned, unconditionally and per filter, before applying channel accessibility, event_visible_to_reader and dedupe."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "filter_fully_pushable is called only from the COUNT paths — twice in handlers/count.rs and twice in api/bridge.rs — and never from the REQ historical path, which post-filters unconditionally instead of testing pushability."
    entry_class: FACT
    evidence:
      - "grep_r('filter_fully_pushable', path='crates/', include='*.rs') -> 5 matches: the definition in buzz-relay/src/handlers/req.rs, 2 call sites in buzz-relay/src/handlers/count.rs, 2 call sites in buzz-relay/src/api/bridge.rs; no call site in the REQ historical-delivery path"
      - "crates/buzz-relay/src/handlers/count.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Because the database applies LIMIT over the pushed clauses only and the remaining clauses are evaluated in Rust afterwards, a filter carrying a non-pushable clause can be served fewer events than match it, without any error being returned."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-core/src/filter.rs"
    confidence: 0.9
  - statement: "COUNT answers the same asymmetry differently: a filter that is not fully pushable falls back to fetching COUNT_FALLBACK_CANDIDATE_LIMIT (5000) candidates plus one, and when count_fallback_exceeded reports the extra row it refuses the request with 'restricted: count filter requires narrower constraints' rather than returning a truncated count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
  - statement: "A filter's limit is silently clamped rather than rejected: filter_to_query_params takes the minimum of the requested value and buzz_db::DEFAULT_MAX_PAGE_LIMIT, an absent limit defaults to that same ceiling, and DEFAULT_MAX_PAGE_LIMIT is 1000."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-db/src/store/event.rs"
  - statement: "That ceiling is the value the relay advertises as NIP-11 limitation.max_limit, derived from the same constant so the advertised and enforced ceilings cannot drift, and a unit test named req_filter_limit_clamps_to_advertised_nip11_max_limit asserts the two agree."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "An empty collection clause means match-nothing rather than no-constraint at both evaluation tiers: filter_match_one's contains/any checks reject on any empty clause (pinned for #h by the test empty_h_tag_filter_matches_nothing), the query layer independently short-circuits to zero rows when kinds, authors, ids or e_tags arrives present-and-empty, and filter_to_query_params passes kinds:[] through as a documented match-no-kinds sentinel while normalising empty authors, ids and #e to absent."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A REQ or COUNT carrying more than MAX_FILTERS_PER_REQ (10) filters is rejected during message parsing, before any filter is deserialized, and the relay advertises the same 10 as NIP-11 limitation.max_filters."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "p_gated_filters_authorized treats an absent kinds clause as able to match a p-gated kind, so a kindless filter is authorized only when it carries a non-empty ids clause or when every #p value equals the authenticated reader's pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The ids exemption is withdrawn for a filter that explicitly names KIND_DM_VISIBILITY or KIND_AGENT_TURN_METRIC, because those events are relay-signed or leak cleartext turn-activity metadata, so knowing an event id is not authorization for them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "P_GATED_KINDS is the set the gate is defined against — agent observer frames, member-added and member-removed notifications, gift wraps, DM visibility snapshots, and agent turn metrics — and kind.rs names p_gated_filters_authorized as the relay's filter-layer enforcement point for it."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "On a WebSocket REQ the gate runs only for global subscriptions (channel_id is None) and closes the subscription with 'restricted: p-gated events require #p matching your pubkey'; the HTTP bridge runs the same gate on POST /query and POST /count and returns HTTP 403 with 'restricted: p-gated kinds require #p tag matching your pubkey'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The repository's own contributor guide states the rule as 'omitting kinds triggers the p-gate (403)', which names the correct trigger but describes only the HTTP response shape; on a WebSocket REQ the same condition produces a CLOSED frame, and only for a global subscription."
    entry_class: INFERENCE
    evidence:
      - "CLAUDE.md"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
    confidence: 0.9
  - statement: "A search clause diverts the whole request to the Postgres FTS path, and mixing a search filter with a non-search filter in one REQ is rejected outright with 'error: mixed search and non-search filters not supported'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Filters arrive as nostr::Filter (crate version 0.44), which silently drops JSON members it does not model, so Buzz's own extension fields are recovered by a second raw-JSON parse on the HTTP bridge rather than by the filter type."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "No upstream numbered Nostr specification text is present in this repository, so any claim about what NIP-01 itself requires cannot be cited to a file here."
    entry_class: FACT
    evidence:
      - "ls(docs/nips/) -> 24 entries: 22 Buzz-authored two-letter NIP markdown files (NIP-AA, NIP-AE, NIP-AM, NIP-AO, NIP-AP, NIP-CW, NIP-DV, NIP-ER, NIP-FI, NIP-FI-CONF, NIP-FI-DELEG, NIP-FI-EDGE, NIP-FI-LIFECYCLE, NIP-FI-MODEL, NIP-GS, NIP-IA, NIP-MP, NIP-OA, NIP-PL, NIP-PMA, NIP-RS, NIP-WP) plus 2 NIP-MP JSON fixture files; no numbered upstream spec, no NIP-01.md, no NIP-42.md"
  - statement: "Issue #1157 requires that this node define the term in one sentence before deeper explanation, state its boundaries and what it must not be confused with, and link to related concepts, implementation and verification without duplicating their canonical content."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1157 definition of done"
relationships:
  - type: references
    target: architecture-flows-historical-query
  - type: references
    target: capabilities-search-search-query
  - type: references
    target: layers-data-postgres-indexes
  - type: references
    target: implementation-crates-buzz-core
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: verification-contracts-nostr
---

# Filter

A **filter** is the JSON object a client puts inside a `REQ` or `COUNT` message to say which
events it wants: a set of clauses that an event must satisfy to be selected.

That one sentence is the whole idea. Everything below is about what the clauses are, how they
compose, and — the part that actually catches people — the fact that a filter in Buzz is
evaluated in **two places**, not one, with a `LIMIT` sitting between them.

## What a filter is not

Naming these up front, because the vocabulary around a filter is crowded and three of the four
neighbours are separate nodes:

| Not this | What it actually is |
|---|---|
| The `REQ` message | The envelope. A `REQ` carries a subscription id **and** one or more filters; the filter is only the selection object inside it. |
| A subscription | The long-lived registration a `REQ` creates. The same filter set is used twice — once to scan history, once to match live events — but the filter is the predicate, not the registration. |
| A tag | A tag is a field on an *event*. A filter's `#`-prefixed clause *queries* tags; the two are matched against each other, not the same thing. |
| A SQL `WHERE` clause | Only some of a filter reaches SQL. See *Two-tier evaluation* below — this is the distinction that matters most. |

## Clause vocabulary

Buzz deserializes a filter into `nostr::Filter` (crate version 0.44) and matches it with
`filter_match_one` in `crates/buzz-core/src/filter.rs`. The clauses that function evaluates are:

| Clause | Meaning as implemented |
|---|---|
| `kinds` | Event kind must appear in the list. |
| `authors` | Event pubkey must appear in the list. |
| `since` / `until` | Inclusive bounds on `created_at`. |
| `ids` | Event id must *begin with* one of the listed values — prefix matching, which the code notes NIP-01 allows, not equality. |
| `#<letter>` | Generic tag clause: the event must carry a tag of that letter whose content equals one of the listed values. |
| `limit` | How many events the client wants back. Silently clamped — see below. |
| `search` | NIP-50 full-text query. Diverts the whole request; see *Boundaries*. |

**Composition.** `filter.rs`'s own module doc states the rule: *multiple filters are OR-ed;
fields within one filter are AND-ed.* `filters_match` is a plain `any()` across the filter list,
and `filter_match_one` returns `false` on the first clause that fails.

**Empty is not absent.** A clause present but empty means *match nothing*, not *no constraint*,
and this holds at both evaluation tiers independently. In Rust, every empty clause fails its
`contains`/`any` check and rejects the event — `empty_h_tag_filter_matches_nothing` pins that for
`#h`. In SQL, the query layer short-circuits to zero rows whenever `kinds`, `authors`, `ids` or
`e_tags` arrives present-and-empty, and `filter_to_query_params` passes `kinds: []` through as a
deliberate match-no-kinds sentinel while normalising the other empty collections to "absent"
before the query is built. An absent clause is the one that means "unconstrained".

**`#h` is the one clause with Buzz-specific behaviour.** `#h` is the channel clause, but some
events — reactions and deletions among them, as `filter.rs`'s own comment notes — derive their
channel from the event they target and carry no `h` tag of their own. So `#h` falls back to the
stored
`StoredEvent.channel_id` **only when the event has no `h` tags at all**. An event that *does*
carry `h` tags is matched strictly on those, and a stored `channel_id` must never rescue it;
`h_tag_fallback_uses_stored_channel_id` asserts exactly that, on the grounds that the looser
rule would leak across channels.

## Two-tier evaluation, and why a filter can under-return

This is the most consequential thing about filters in Buzz, and it is not visible from the
filter's JSON.

A filter is evaluated **twice**, in two different languages, with the row limit applied in
between:

1. `filter_to_query_params` translates *part* of the filter into an `EventQuery`. What it can
   push into SQL is: `kinds`, `authors` (one author via the indexed `pubkey` column, several via
   an `authors` IN-list), `ids`, `since`, `until`, `#e` values of any count, a **single-value**
   `#p` via the `event_mentions` join, and `#d` **only** when the filter targets NIP-33
   parameterized-replaceable kinds exclusively — because `d_tag` is `NULL` for everything else,
   so pushing it on a mixed or kindless filter would wrongly exclude rows. The authorized
   channel scope is injected separately by `apply_channel_scope_to_query`.
2. Postgres runs that partial predicate and applies `ORDER BY` and `LIMIT`.
3. The relay then re-applies the **complete** filter, in Rust, to each row that came back —
   `filters_match` against that one filter, then channel accessibility, then
   `event_visible_to_reader`, then dedupe.

Step 3 can only *remove* rows. It never fetches more. So **any clause that step 1 could not push
is applied after the `LIMIT` has already been spent**, and a filter carrying such a clause can
be served fewer events than actually match it — with no error, no notice, and no signal that
anything was truncated.

`filter_fully_pushable` is the authoritative list of which clauses those are. Its own
documentation names the non-pushable set:

- multi-value `#p` (single `#p` is pushed; two or more is not)
- `#t`, `#a`, and any other generic tag beyond `#h`, `#p`, `#d`, `#e`
- `#d` on a filter that is not NIP-33-only
- `search`

**But `filter_fully_pushable` is not consulted on the REQ path.** Its five occurrences in the
crate tree are its own definition plus four call sites, two in `handlers/count.rs` and two in
`api/bridge.rs` — all COUNT paths. The historical-delivery loop in `handlers/req.rs` post-filters
unconditionally and never asks whether it needed to. Nothing in the source states whether that
asymmetry was intended; what is observable is that the two message types behave differently
under the same filter:

| | `COUNT` | `REQ` |
|---|---|---|
| Tests pushability | Yes, via `filter_fully_pushable` | No — there is no such branch |
| Fully pushable | Exact `count_events()` in SQL | Query, then post-filter anyway |
| Not fully pushable | Fetches `COUNT_FALLBACK_CANDIDATE_LIMIT` (5000) candidates + 1; if the extra row comes back it refuses with `restricted: count filter requires narrower constraints` rather than returning a truncated number | Post-filters whatever the `LIMIT` returned; a short result is indistinguishable from a complete one |

The practical consequence for anyone writing a filter: **push what you can.** A `#t` or `#a`
clause, or a second `#p` value, moves the whole selection behind the limit. Splitting one filter
into several — remembering the cap below — is often better than one filter the SQL layer cannot
represent.

`architecture-flows-historical-query` owns the end-to-end request flow this sits inside;
`layers-data-postgres-indexes` owns which of those pushed clauses are actually indexed.

## Limits the relay imposes on a filter

**`limit` is clamped, never rejected.** `filter_to_query_params` takes the minimum of the
requested value and `buzz_db::DEFAULT_MAX_PAGE_LIMIT`, which is `1000`; a filter with no `limit`
gets the same ceiling. A client asking for 10,000 receives no error — it receives at most 1000
and is not told the number was changed. The ceiling is derived from the same constant the relay
advertises as NIP-11 `limitation.max_limit`, so the advertised and enforced values cannot drift,
and `req_filter_limit_clamps_to_advertised_nip11_max_limit` asserts that.

**Ten filters per message.** `MAX_FILTERS_PER_REQ` is `10`, enforced in `protocol.rs` while the
`REQ` or `COUNT` message is still being parsed — before any filter is deserialized — and
advertised as NIP-11 `limitation.max_filters`. An eleventh filter fails the whole message, not
just itself.

## The kindless-filter gate

A filter with **no `kinds` clause** is treated as able to match anything, including the kinds
whose read access is bound to a `#p` tag. `p_gated_filters_authorized` implements that directly:
it asks whether the filter *can* match a p-gated kind using `is_none_or` over `kinds`, so an
absent `kinds` clause answers yes without any kind being named. The filter is then authorized
only if one of these holds:

- it carries a **non-empty `ids`** clause — the "knowing the id implies authorization" exemption; or
- its **`#p` values are non-empty and every one equals** the authenticated reader's pubkey.

Otherwise the request is refused. The exemption is **withdrawn** for a filter that explicitly
names `KIND_DM_VISIBILITY` or `KIND_AGENT_TURN_METRIC`: those events are relay-signed (so the id
is not author-bound) or leak cleartext turn-activity metadata in their envelope, and for them
knowing an id is not authorization.

Where the refusal shows up depends on the surface:

| Surface | Condition | Response |
|---|---|---|
| WebSocket `REQ` | Global subscriptions only (`channel_id` is `None`) | `CLOSED` — `restricted: p-gated events require #p matching your pubkey` |
| `POST /query`, `POST /count` | Always | HTTP **403** — `restricted: p-gated kinds require #p tag matching your pubkey` |

`P_GATED_KINDS` is the set this is defined against: agent observer frames, member-added and
member-removed notifications, gift wraps, DM visibility snapshots, and agent turn metrics.
`kind.rs` names `p_gated_filters_authorized` as the filter-layer enforcement point for the set.

**A note on the contributor guide's wording.** `CLAUDE.md` states the rule as *"omitting `kinds`
triggers the p-gate (403). Always include explicit kind filters."* The trigger is right and the
advice is right. The response shape is only right for HTTP: on a WebSocket `REQ` the same
condition produces a `CLOSED` frame with a `restricted:` reason, and only for a subscription
that is not channel-scoped. Read the guide's line as "your kindless filter will be refused",
not as "you will see a 403".

## Boundaries

**A `search` clause changes what the filter is.** A filter with `search` set is diverted to the
Postgres FTS path, is never registered for live fan-out, and cannot be mixed with a non-search
filter in the same `REQ` — that combination is refused with `error: mixed search and non-search
filters not supported`. `capabilities-search-search-query` owns that capability; this node stops
at the boundary.

**`nostr::Filter` is not the whole wire object.** Buzz's own extension fields on the HTTP bridge
are silently dropped by `nostr::Filter`, which models only the standard members, so the bridge
parses the raw JSON a second time to recover them. Those fields are a distinct contract from the
filter concept and are not documented here.

## Scope and omissions

**This node covers** what a filter is, its clause vocabulary and composition rules, the
Buzz-specific `#h` fallback, the two-tier SQL-then-Rust evaluation and the under-return it
permits, the `limit` clamp and per-message filter cap, and the kindless-filter `#p` gate.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `REQ` message envelope itself | A separate, not-yet-merged node in Feature #609 |
| Subscriptions and live fan-out matching | A separate, not-yet-merged node in Feature #609 |
| Tags as a property of events | A separate, not-yet-merged node in Feature #609 |
| `EOSE` and the history/live handover | A separate, not-yet-merged node in Feature #609 |
| The end-to-end historical-query flow | `architecture-flows-historical-query` |
| NIP-50 search as a capability | `capabilities-search-search-query` |
| Which pushed clauses have supporting indexes | `layers-data-postgres-indexes` |
| The HTTP bridge's non-standard filter extension fields (cursor, depth and feed-type members recovered by the second raw parse) | Not filed as its own task at the recorded revision |

**Expected but not verified when this node was written:**

- **No test was found that demonstrates the under-return.** The claim that a non-pushable clause
  can silently return fewer events than match is reasoned from the code path — `LIMIT` in SQL,
  then `filters_match` in Rust, with no re-fetch — and is classified `INFERENCE` for that reason.
  Searching the crate tree for `filter_fully_pushable` returned only its definition and four
  COUNT-path call sites and no test naming pushability at all, so nothing in the suite pins this
  behaviour either way. If a reviewer knows of an integration test that covers it, this entry
  should be promoted; if none exists, that is a genuine coverage gap worth filing.
- **The relay was not run.** Every claim here is read from source at the recorded revision. No
  live `REQ` was issued, so the response strings quoted above are the ones the code constructs,
  not ones observed on the wire.
- **Upstream NIP text is not in this repository.** `docs/nips/` holds only Buzz's own two-letter
  NIPs and two JSON fixture files; there is no `NIP-01.md` and no `NIP-42.md`, and no numbered
  upstream spec anywhere in the tree. So where this node says NIP-01 permits
  something, it is reporting what Buzz's own code comments record about NIP-01, not quoting the
  specification. Anyone needing the normative wording must go to the upstream `nostr-protocol/nips`
  repository, which is outside this corpus's evidence reach.
