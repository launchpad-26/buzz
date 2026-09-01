---
id: verification-contracts-nostr
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "crates/buzz-test-client/tests/e2e_nostr_interop.rs's own module doc-comment states these are end-to-end integration tests for NIP-50 search, NIP-10 threads, NIP-17 gift wraps and DM discovery, that they require a running relay, that they are marked #[ignore] by default so a plain `cargo test` does not run them, that they are run with `cargo test --test e2e_nostr_interop -- --ignored`, and that the target relay is overridden with the `RELAY_URL` environment variable (default `ws://localhost:3000`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1-28"
  - statement: "This repository's root AGENTS.md (identical to CLAUDE.md) names e2e_nostr_interop.rs, among the e2e suites under crates/buzz-test-client/tests/, as covering 'Nostr interop (NIP-50 search, NIP-10 threads, NIP-17 gift wraps)'."
    entry_class: FACT
    evidence:
      - "AGENTS.md:255"
  - statement: "buzz-core's kind registry documents kind:9 (KIND_STREAM_MESSAGE, Buzz's ordinary channel message kind) as 'NIP-29 group chat message kind', and documents kind:1059 (KIND_GIFT_WRAP) as 'NIP-17: Outer envelope for private DMs -- hides sender, content, timestamp'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:473-479"
      - "crates/buzz-core/src/kind.rs:59-60"
  - statement: "This repository's root AGENTS.md states that Buzz channels use `h` tags -- NIP-29's group tag -- rather than `e` tags for channel scoping, and that this applies to events inside a channel."
    entry_class: FACT
    evidence:
      - "AGENTS.md:182"
  - statement: "e2e_nostr_interop.rs contains four #[ignore]-gated tests naming NIP-50 in their own doc-comments or names: test_nip50_search_returns_results_and_eose (a unique-token search returns the matching message before EOSE, and no further event is delivered on that subscription after EOSE because NIP-50 search is one-shot), test_nip50_search_mixed_filters_rejected (a REQ combining a search filter and a non-search filter in one subscription is closed with a message containing 'mixed'), test_nip50_search_empty_results (a search matching nothing returns EOSE with zero events), and test_nip50_search_relevance_order (of three messages with varying token overlap, the exact-match message, not the most recent one, is returned first)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:260-336"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:340-397"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:401-433"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1053-1107"
  - statement: "e2e_nostr_interop.rs contains four #[ignore]-gated tests exercising NIP-10 e-tag threading: test_nip10_thread_reply_creates_metadata (a kind:9 reply carrying an ['e', root_id, '', 'reply'] tag is accepted and is returned by a thread query keyed on that root, while the root itself is never returned as its own reply), test_nip10_unknown_parent_rejected (a reply e-tagging a nonexistent parent id is rejected with OK=false and a message containing 'parent not found'), test_nip10_root_mismatch_rejected (a reply whose e-tag 'root' marker names an id other than the real ancestor of its 'reply'-marked parent is rejected with a message containing 'root tag does not match' or 'root'), and test_nip10_thread_reply_not_in_top_level (a depth-1 reply without a ['broadcast','1'] tag is excluded from the channel's top-level view while an otherwise-identical depth-1 reply carrying that tag is surfaced, and the root itself remains top-level)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:437-500"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:502-538"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:540-583"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:863-963"
  - statement: "e2e_nostr_interop.rs contains four #[ignore]-gated tests exercising NIP-17 gift wraps (kind:1059): test_nip17_gift_wrap_accepted (a kind:1059 event signed by an ephemeral key different from the connection's authenticated key is accepted rather than rejected for the pubkey mismatch that would fail any other kind), test_nip17_gift_wrap_requires_p_filter (subscribing to kind:1059 with no #p filter is closed with a message containing 'p-gated', '#p', or 'restricted'), test_nip17_gift_wrap_recipient_receives (a gift wrap #p-addressed to a recipient's pubkey is delivered live to that recipient's matching subscription), and test_nip17_gift_wrap_not_searchable (a gift wrap is never returned by a NIP-50 search that does return a control kind:9 message carrying the same unique token)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:585-616"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:618-670"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:672-753"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:965-1049"
  - statement: "buzz-relay's handle_search_req is documented as handling 'a NIP-50 search REQ: query Postgres FTS, fetch full events, deliver results, EOSE' and states search subscriptions are one-shot with no persistent subscription registered; a sibling code path in the same file rejects a REQ mixing search and non-search filters with the literal message 'error: mixed search and non-search filters not supported'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:581-583"
      - "crates/buzz-relay/src/handlers/req.rs:253"
  - statement: "buzz-core's P_GATED_KINDS constant includes KIND_GIFT_WRAP, and its doc-comment states the relay enforces this at the filter layer via p_gated_filters_authorized -- closing a REQ that can match any listed kind unless its #p values exactly equal the authenticated reader's pubkey -- and that stored kinds in this set additionally get a NULL search_tsv at the storage layer, making them unsearchable through NIP-50 full-text search."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:144-169"
      - "crates/buzz-relay/src/handlers/req.rs:1182-1195"
  - statement: "buzz-relay's resolve_nip10_thread_meta returns the literal error 'reply parent not found' when an e-tagged parent event id does not resolve, and returns 'root tag does not match thread ancestry' when a reply's e-tag 'root' marker does not match the resolved ancestry of its 'reply'-marked parent."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:813-891"
  - statement: "buzz-relay exempts gift-wrapped events from its rule that a submitted event's pubkey must match the connection's authenticated pubkey: both the HTTP ingest path (event.rs) and the WebSocket ingest path (ingest.rs) compute is_gift_wrap from kind_u32 == KIND_GIFT_WRAP and only enforce the pubkey-match check `event.pubkey != auth_pubkey` when !is_gift_wrap."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:659-660"
      - "crates/buzz-relay/src/handlers/ingest.rs:2242-2243"
  - statement: "The gift-wrap pubkey-mismatch exemption, the #p-gate on KIND_GIFT_WRAP in P_GATED_KINDS, and that same kind's NULL search_tsv are, respectively, the exact three server-side properties that test_nip17_gift_wrap_accepted, test_nip17_gift_wrap_requires_p_filter, and test_nip17_gift_wrap_not_searchable each probe -- the source code and the test names/bodies were read side by side, and each test's setup and assertions map onto exactly one of the three code properties with nothing left over."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:659-660"
      - "crates/buzz-core/src/kind.rs:144-169"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:585-616"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:618-670"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:965-1049"
    confidence: 0.8
  - statement: "None of the twelve tests cited above was executed while authoring this node -- no live relay, Postgres or Redis stack was started -- so this node makes no claim about whether they currently pass; only their existence, their #[ignore] gating, and their source code were verified."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:260-1049"
  - statement: "Issue #1360's definition of done requires this node to have schema-valid front matter with typed relationships appropriate to the node, to link relevant implementation/verification/specification nodes without duplicating their content, to state preconditions/action/expected outcome, to name negative/error cases that are part of the contract, to link actual verification implementing the contract, and to not claim coverage that is not present."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1360 definition of done"
  - statement: "At the recorded revision, capabilities-messaging-gift-wrap, capabilities-messaging-thread and capabilities-search-full-text-search are all loadable ids on origin/launchpad's corpus tree, and no node of type verification exists anywhere in that tree yet, confirmed by listing the full corpus tree at origin/launchpad rather than assuming either fact."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> includes capabilities/messaging/gift-wrap.md (id capabilities-messaging-gift-wrap), capabilities/messaging/thread.md (id capabilities-messaging-thread), capabilities/search/full-text-search.md (id capabilities-search-full-text-search); no verification/ subtree present"
relationships:
  - type: references
    target: capabilities-messaging-gift-wrap
  - type: references
    target: capabilities-messaging-thread
  - type: references
    target: capabilities-search-full-text-search
---

# Nostr NIP interop — test contract

## Purpose and boundary

This node documents one obligation: that Buzz's relay honors the wire-level Nostr
NIPs it claims interoperability with, as exercised end to end against a live relay
by `crates/buzz-test-client/tests/e2e_nostr_interop.rs`. It covers exactly the
NIP-50 search, NIP-10 threading and NIP-17 gift-wrap behavior that file's own
module doc-comment and this repository's root `AGENTS.md` both name it as
covering, and the twelve tests in that file which exercise those three NIPs. It
does not cover NIP-01's wire protocol generally, NIP-29 group administration
generally, or the other things `e2e_nostr_interop.rs` also happens to contain --
see *Scope and omissions*.

## Obligation

> Buzz's relay honors the specific Nostr NIP behaviors `e2e_nostr_interop.rs`
> exercises against a live relay: NIP-50 `search` filters return matching
> results once, ordered by relevance, and reject being mixed with a
> non-search filter in the same subscription; NIP-10 `e`-tagged replies are
> recorded under their resolved root, rejected when their parent or root
> ancestry does not resolve, and excluded from a channel's top-level view
> unless explicitly broadcast; and NIP-17 gift-wrap events (kind:1059) are
> accepted despite a signer/authenticated-pubkey mismatch, gated behind a
> `#p` filter for read access, delivered live to their addressed recipient,
> and excluded from search.

## Verifying test(s)

All twelve tests live in `crates/buzz-test-client/tests/e2e_nostr_interop.rs`.

**NIP-50 search:**

- `test_nip50_search_returns_results_and_eose` (lines 260-336) -- a unique-token
  search returns the matching message before EOSE, and no further event
  arrives on that subscription after EOSE (search is one-shot).
- `test_nip50_search_mixed_filters_rejected` (lines 340-397) -- a REQ combining
  a search filter and a non-search filter in one subscription is closed with a
  message containing "mixed".
- `test_nip50_search_empty_results` (lines 401-433) -- a search matching
  nothing returns EOSE with zero events.
- `test_nip50_search_relevance_order` (lines 1053-1107) -- of three messages
  with varying token overlap, the exact-match message is returned first, not
  the most recently sent one.

**NIP-10 threads:**

- `test_nip10_thread_reply_creates_metadata` (lines 437-500) -- a kind:9 reply
  carrying `["e", root_id, "", "reply"]` is accepted and is returned by a
  thread query keyed on that root; the root itself is never returned as its
  own reply.
- `test_nip10_unknown_parent_rejected` (lines 502-538) -- a reply e-tagging a
  nonexistent parent id is rejected (`OK` false, message containing "parent
  not found").
- `test_nip10_root_mismatch_rejected` (lines 540-583) -- a reply whose e-tag
  `root` marker names an id other than the real ancestor of its `reply`-marked
  parent is rejected (message containing "root tag does not match" / "root").
- `test_nip10_thread_reply_not_in_top_level` (lines 863-963) -- a depth-1 reply
  without a `["broadcast","1"]` tag is excluded from the channel's top-level
  view; an otherwise-identical depth-1 reply carrying that tag is surfaced,
  and the root itself remains top-level.

**NIP-17 gift wraps:**

- `test_nip17_gift_wrap_accepted` (lines 585-616) -- a kind:1059 event signed
  by an ephemeral key different from the connection's authenticated key is
  accepted rather than rejected for the pubkey mismatch that would fail any
  other kind.
- `test_nip17_gift_wrap_requires_p_filter` (lines 618-670) -- subscribing to
  kind:1059 with no `#p` filter is closed (message containing "p-gated",
  "#p", or "restricted").
- `test_nip17_gift_wrap_recipient_receives` (lines 672-753) -- a gift wrap
  `#p`-addressed to a recipient's pubkey is delivered live to that recipient's
  matching subscription.
- `test_nip17_gift_wrap_not_searchable` (lines 965-1049) -- a gift wrap is
  never returned by a NIP-50 search that does return a control kind:9 message
  carrying the same unique token.

## How to run it

Requires a running relay (and the Postgres/Redis stack it depends on) reachable
at `RELAY_URL` (default `ws://localhost:3000`):

```bash
cargo test --test e2e_nostr_interop -- --ignored
```

To target a non-default relay:

```bash
RELAY_URL=ws://relay.example.com cargo test --test e2e_nostr_interop -- --ignored
```

A plain `cargo test` (no `--ignored`) runs none of these twelve tests, by design
-- every test in this file is `#[tokio::test]` plus `#[ignore]`, per the file's
own module doc-comment, so `cargo test` stays safe to run without a relay
available.

## Current enforcement status

**Gated.** All twelve tests exist, are `#[ignore]`-annotated in source, and are
never executed by a plain `cargo test` or by any CI job that does not pass
`--ignored` against a live relay. This node was authored without starting a
relay, Postgres or Redis, so it makes no claim about whether the suite
currently passes -- only that the tests exist, are conditionally run, and that
their assertions (read directly, not inferred from their names) match the
server-side code paths cited in this node's evidence ledger. See *Limits*.

## Limits

**What is exercised:** three NIPs' worth of externally observable relay
behavior, driven by a real Nostr client (`buzz-test-client`) against a real
relay process over WebSocket and the HTTP bridge: NIP-50 search's
result-then-EOSE shape, its one-shot nature, its filter-mixing rejection, and
its relevance ordering; NIP-10 threading's acceptance, parent/root-mismatch
rejection, and top-level/broadcast visibility rule; and NIP-17 gift wrap's
signer exemption, `#p` read-gate, live delivery, and search exclusion.

**What is not exercised by these twelve tests:**

- **NIP-01's wire protocol in general** -- connection handling, signature
  verification for ordinary (non-gift-wrapped) events, and most filter fields
  are exercised by `e2e_relay.rs` and other e2e suites, not here. This node
  does not extend to that broader surface.
- **NIP-29 group administration** (`KIND_NIP29_PUT_USER`,
  `KIND_NIP29_CREATE_GROUP`, membership/admin lists, etc.) beyond the `h`-tag
  channel-scoping convention these twelve tests already depend on to isolate
  their own test data. No test here specifically exercises NIP-29's
  admin-event kinds.
- **Multiple relays, or the NIP-50 search backend's actual PostgreSQL FTS
  ranking algorithm** -- `test_nip50_search_relevance_order` observes one
  ordering outcome, not the ranking function's behavior across query shapes
  generally.
- **Whether the suite currently passes** -- not run while authoring this node;
  see *Current enforcement status*.
- **Concurrency, load, or multi-relay-mesh interaction with any of these NIP
  behaviors** -- every test here uses a single relay instance and at most two
  concurrently connected clients.

## Scope and omissions

**This node covers** the twelve `e2e_nostr_interop.rs` tests exercising NIP-50
search, NIP-10 threading and NIP-17 gift wraps, the server-side code paths
they exercise, and this suite's `#[ignore]`-gated enforcement status.

**It deliberately does not cover, and these are gaps rather than silence:**

| Not covered here | Where it lives instead |
|---|---|
| NIP-01 core protocol conformance generally (connection lifecycle, ordinary event signature verification, most filter semantics) | `crates/buzz-test-client/tests/e2e_relay.rs` and sibling e2e suites; no corpus test-contract node exists for it yet |
| NIP-29 group administration and membership events | `crates/buzz-core/src/kind.rs`'s `KIND_NIP29_*` constants and their relay handlers; not exercised by this file |
| `e2e_nostr_interop.rs`'s other tests -- NIP-DV visibility-snapshot behavior (`test_nipdv_*`) and the channel-window pagination tests (`test_channel_window_*`, `test_historical_req_dedup_preserves_or_semantics`, `test_empty_kinds_returns_zero_events`) | These are Buzz-specific extensions and query semantics, not NIP interop claims, and are a distinct obligation from this node's; not folded in here |
| Whether the twelve cited tests currently pass | Not established by this node; run the command in *How to run it* against a live relay to find out |
| General corpus rules for creating, updating and citing tests as evidence | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/standards/test-references.md`, `launchpad/docs/corpus/standards/evidence.md` |

**Relationships, checked rather than assumed absent.** At the recorded
revision, `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
shows `capabilities-messaging-gift-wrap`, `capabilities-messaging-thread` and
`capabilities-search-full-text-search` as loadable ids, and this node declares
a `references` edge to each -- the obligation above is the test-verified half
of the behavior those capability nodes describe. No `implements` edge is
declared toward `corpus-template-test-contract`: that template's own body
states a node built from it "should expect to declare `implements`... once
template nodes carry a stable enough identity for `implements`'s directionality
to make sense," which the template itself says is not yet the case. No node of
`type: verification` exists anywhere in the corpus tree at the recorded
revision, so this is the first, and there is no sibling test-contract node to
link.

**Expected but not verified when this node was written:**

- **Whether the twelve cited tests currently pass against a live relay** -- no
  relay, Postgres or Redis instance was started while authoring this node. See
  *Current enforcement status* and *Limits*.
- **Whether any of the twelve tests is flaky under retry** -- this repository's
  own `corpus-standard-test-references` node notes that Rust test runs in this
  repository carry no repository-provided retry/flaky signal comparable to
  desktop's Playwright summarizer; that gap applies here too and was not
  independently re-investigated for this specific file.
- **Whether `e2e_relay.rs` or another suite already exercises NIP-01 core
  protocol conformance to a degree that would deserve its own test-contract
  node** -- named as a gap above rather than filed as a new issue, per this
  node's own scope.
