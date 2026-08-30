---
id: capabilities-messaging-gift-wrap
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-core/src/kind.rs defines KIND_GIFT_WRAP as kind:1059 with the doc comment 'NIP-17: Outer envelope for private DMs -- hides sender, content, timestamp', the sole first-party constant for this capability; no KIND_SEAL (NIP-17's kind:13 inner seal) or rumor (kind:14) constant exists anywhere in the registry."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:59-60"
  - statement: "The workspace's own nostr crate dependency is declared with features = [\"nip44\", \"nip98\"] only; it does not enable that crate's nip59 (gift wrap) feature, and a repository-wide search of crates/ for nip59, NIP59, KIND_SEAL, or the word 'rumor' (excluding 'sealed'/'reveal' false matches) found zero matches outside this evidence search itself."
    entry_class: FACT
    evidence:
      - "Cargo.toml:72"
      - "grep_recursive('nip59|NIP59|KIND_SEAL|\\\\brumor\\\\b', path='crates/', exclude='target/') -> zero matches, run against this node's recorded revision"
  - statement: "No code under crates/buzz-sdk, crates/buzz-cli, desktop/src, or mobile/lib builds, seals, or decrypts a kind:1059 event -- a case-insensitive search of buzz-sdk's event builders and both client apps for gift-wrap/NIP-17/1059 identifiers found zero matches -- so this repository contains no first-party producer or consumer of actual gift-wrapped DM content, only the relay-side handling described below."
    entry_class: FACT
    evidence:
      - "grep_recursive_case_insensitive('gift.wrap|nip-17|nip17|1059', path='crates/buzz-sdk/src') -> zero matches"
      - "grep_recursive_case_insensitive('gift.wrap|nip17|nip-17', path='desktop/src;mobile/lib') -> zero matches, run against this node's recorded revision"
  - statement: "KIND_GIFT_WRAP is one of six members of P_GATED_KINDS, whose doc comment states that a REQ/COUNT filter able to match any kind in this set is closed by the relay unless its `#p` values exactly equal the authenticated reader's own pubkey, enforced by p_gated_filters_authorized (called from both the REQ and COUNT handlers)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:144-166"
      - "crates/buzz-relay/src/handlers/req.rs:1182-1213"
      - "crates/buzz-relay/src/handlers/count.rs:44"
  - statement: "p_gated_filters_authorized's own comments state that the 'ids' exemption ('knowing the id implies authorization') is granted to kind:1059 specifically because a gift wrap's id is not author-bound (it is signed by a one-time ephemeral key) and its content is encrypted, so a kindless or gift-wrap-explicit `{ids:[...]}` filter is authorized without a matching `#p`; the same function explicitly withholds that exemption for KIND_DM_VISIBILITY and KIND_AGENT_TURN_METRIC, whose plaintext or metadata content would leak if the same rule applied to them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1182-1213"
  - statement: "A REQ whose filters can match a P_GATED_KINDS member without a `#p` filter equal to the caller's own pubkey is closed with the message 'restricted: p-gated events require #p matching your pubkey', checked before the NIP-50 search branch specifically so an authenticated member cannot use a `search` filter to harvest a globally-stored p-gated kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:205-227"
  - statement: "migrations/0001_initial_schema.sql's events.search_tsv generated column emits NULL (rather than an indexed tsvector) for a fixed set of kinds that includes 1059, and this storage-level exclusion is proven from the wire by an integration test, excluded_kinds_are_storage_level_unsearchable, in crates/buzz-search/tests/fts_integration.rs, and independently by an end-to-end test, test_nip17_gift_wrap_not_searchable, in crates/buzz-test-client/tests/e2e_nostr_interop.rs, both of which insert a kind:1059 event and a kind:9 control with the same unique token and assert only the control surfaces via NIP-50 search."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:204-223"
      - "crates/buzz-search/tests/fts_integration.rs:1146-1170"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:971-1040"
  - statement: "handle_event (the WebSocket EVENT path) and ingest_event_inner (the shared persistent-event path used by both WebSocket and HTTP) both compute is_gift_wrap = kind_u32 == KIND_GIFT_WRAP and skip the ordinary 'event.pubkey must equal the authenticated NIP-42 identity' rejection when it is true, because a NIP-17 gift wrap is deliberately signed by a random one-time key rather than the sender's real identity."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:653-668"
      - "crates/buzz-relay/src/handlers/ingest.rs:2021-2027"
  - statement: "handle_event's workflow-trigger dispatch explicitly excludes kind:1059 (alongside workflow-execution and command kinds) from firing buzz-workflow triggers, so a gift-wrapped event's encrypted content is never handed to the workflow engine as a trigger payload."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:527-533"
  - statement: "ingest_event_inner rejects a kind:1059 submission over the HTTP POST /events bridge outright ('invalid: kind {kind} is only accepted via WebSocket'); a gift wrap can only be submitted over the WebSocket EVENT frame."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1973-1978"
  - statement: "required_scope_for_kind maps KIND_GIFT_WRAP to Scope::MessagesWrite, the same write-authorization scope as ordinary channel messages, reactions, and forum posts -- a gift wrap needs no dedicated scope of its own to be submitted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:377-390"
  - statement: "Kind 1059 is one of five kinds in the Postgres trigger's push-eligible allow-list (7, 9, 1059, 40007, 46010) that enqueues a push_match_queue row on insert, and push_runtime.rs's push_filter_authorized_for_event specifically restricts a push lease to matching a gift wrap only when the lease's own filter's `#p` equals the lease author's own pubkey -- documented in its own comment as necessary because 'kind 1059 is globally stored and leaks recipient activity through wake timing'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs:290-306"
      - "migrations/0018_push_match_queue.sql"
  - statement: "crates/buzz-test-client/tests/e2e_nostr_interop.rs carries four #[ignore]d async tests specifically for this capability -- test_nip17_gift_wrap_accepted (pubkey-mismatch exemption), test_nip17_gift_wrap_requires_p_filter (REQ without #p is CLOSED), test_nip17_gift_wrap_recipient_receives (delivery to a #p-matching subscriber), and test_nip17_gift_wrap_not_searchable -- all requiring a live relay and run via `cargo test --test e2e_nostr_interop -- --ignored`, per the file's own module doc comment; #[ignore] is this file's blanket convention for its 25 tests, not a marker specific to gift-wrap coverage."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1-20"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:584-716"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:971-1040"
  - statement: "This repository's own Buzz-authored NIPs treat NIP-59 gift wrap as an established, cross-cutting, opaque relay privacy primitive rather than something specific to DMs: NIP-AO (agent observer frames) notes implementors MAY wrap events in NIP-59 gift wrap for maximum metadata privacy; NIP-ER (event reminders) states it intentionally does NOT use NIP-59 wrapping because the relay must read a public tag; and NIP-PL (push leases) both lists kind 1059 in an example push_kinds config and states an executor MUST NOT decrypt NIP-59 seals or gift wraps, matching only the outer envelope's `#p` tag."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md:193-195"
      - "docs/nips/NIP-ER.md:40-41"
      - "docs/nips/NIP-PL.md:16-17"
      - "docs/nips/NIP-PL.md:156"
      - "docs/nips/NIP-PL.md:177-179"
      - "docs/nips/NIP-PL.md:205"
  - statement: "An open, unmerged PR (#1914, branch task/612-batch-03-channel-dm-forum) drafting launchpad/docs/corpus/capabilities/channels/dm-channel.md independently found the same separation this node found -- its Boundary section states KIND_GIFT_WRAP (kind:1059) 'is never referenced by handle_dm_open, handle_dm_add_member, handle_dm_hide or buzz-db's dm.rs' and explicitly scopes gift-wrapped NIP-17 messaging out of the DM-channel capability as 'a separate capability node, not this one' -- confirming these are two distinct, non-duplicative capabilities rather than one capability documented twice; that node is not yet merged to origin/launchpad at this recorded revision, so no relationship edge to it is declared here."
    entry_class: FACT
    evidence:
      - "commit 3fc4b011b04fb5b9b21980c92fd0a14d875a800b (launchpad-26/buzz#1914 head, branch task/612-batch-03-channel-dm-forum, unmerged at recorded revision) -- launchpad/docs/corpus/capabilities/channels/dm-channel.md, section 'Boundary'"
  - statement: "Because the relay fully implements and tests routing, read-authorization, storage-level search exclusion, and push-gating for an opaque kind:1059 payload, but no code in this repository constructs, seals, or decrypts the NIP-17 rumor/seal/gift-wrap layers themselves, the practical, end-to-end capability this repository ships is 'a Buzz relay correctly and safely carries NIP-17 gift-wrapped events for any client that builds them', not 'a Buzz client can send or receive an encrypted private message today' -- an actual gift-wrapped conversation through a Buzz relay would have to originate from and be read by an external, standards-compliant Nostr client, not Buzz's own SDK, CLI, desktop, or mobile apps."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs:59-60"
      - "crates/buzz-relay/src/handlers/event.rs:653-668"
      - "crates/buzz-relay/src/handlers/req.rs:1182-1213"
      - "migrations/0001_initial_schema.sql:204-223"
      - "crates/buzz-relay/src/push_runtime.rs:290-306"
    confidence: 0.85
---

# Gift wrap: capability

Buzz can carry **NIP-17 gift-wrapped private messages** -- the standard Nostr
mechanism (kind:1059) for hiding a message's real sender, content, and
timestamp from everyone but its intended recipient -- through a Buzz relay
safely: a gift wrap is accepted even though it is signed by a one-time key
unrelated to any authenticated identity, is delivered only to a reader whose
own pubkey matches its recipient tag, is excluded from full-text search and
from triggering workflows, and is push-woken without ever leaking its
content or matching against anyone but its own addressee. This is a
relay-level privacy guarantee any NIP-17-compliant Nostr client can rely on
when publishing through Buzz -- it is not, at this revision, a feature any
Buzz-built client (SDK, CLI, desktop, or mobile app) uses to send or receive
an encrypted message itself.

## Maturity

**Relay-side handling: shipped and tested.** Every enforcement point --
acceptance despite pubkey mismatch, `#p`-gated read authorization (with a
deliberate `ids`-lookup exemption specific to this kind), storage-level
search exclusion, workflow-trigger exclusion, WebSocket-only submission, and
push-match authorization restricted to the event's own addressee -- exists
in `crates/buzz-relay` and `crates/buzz-core` today, each backed by at least
one test (unit-level for the storage exclusion via
`crates/buzz-search/tests/fts_integration.rs`, and four dedicated end-to-end
tests in `crates/buzz-test-client/tests/e2e_nostr_interop.rs`, run against a
live relay via `cargo test --test e2e_nostr_interop -- --ignored`).

**Client-side construction: not built.** No first-party Buzz code -- not
`buzz-sdk`'s event builders, not `buzz-cli`, not the desktop app, not the
mobile app -- builds a rumor, seals it, wraps it, or decrypts a gift wrap
addressed to a Buzz user. The workspace's own `nostr` crate dependency does
not even enable that crate's `nip59` feature. There is no `VISION_PROJECTS.md`
status-table row for this capability, unlike "Channels, forums, DMs,
canvases" -- its maturity is established here from code and tests directly,
not from a product status marker.

**Net effect.** The capability that actually ships today is a relay that is
a safe, tested carrier of gift-wrapped events for whichever client builds
and reads them -- not an encrypted-messaging feature Buzz's own clients
expose to a user or agent.

## Behavioral rules and constraints

- **Identity-binding exemption.** The relay's normal rule -- an event's
  `pubkey` must equal the authenticated NIP-42 session's pubkey -- is
  skipped specifically for `kind:1059`, both on the WebSocket `EVENT` path
  and the shared persistent-ingest path, because NIP-17 requires the outer
  gift wrap to be signed by a one-time ephemeral key, never the real
  sender's key.
- **Transport restriction.** A gift wrap can only be submitted over the
  WebSocket `EVENT` frame; the HTTP `POST /events` bridge rejects `kind:1059`
  outright with `"invalid: kind 1059 is only accepted via WebSocket"`.
- **Write scope.** Submitting a gift wrap requires the same
  `Scope::MessagesWrite` authorization as an ordinary channel message --
  no dedicated scope exists for this kind.
- **Read gate.** Any REQ or COUNT filter able to match `kind:1059` is closed
  unless its `#p` tag values exactly equal the authenticated reader's own
  pubkey (`p_gated_filters_authorized`), checked before the NIP-50 search
  branch so a member cannot use `search` to bypass the gate. This is the
  same mechanism that protects membership notifications and DM-visibility
  snapshots, reused rather than reinvented for this kind.
- **`ids`-lookup exemption, and why it differs from its P-gated siblings.**
  A filter naming `kind:1059` (or a kindless filter) with an `ids` list but
  no `#p` is still authorized, because a gift wrap's id is not bound to a
  real author and its content is opaque ciphertext -- knowing the id
  reveals nothing. The same function explicitly denies this exemption to
  `KIND_DM_VISIBILITY` and `KIND_AGENT_TURN_METRIC`, whose content or
  envelope would leak metadata if the same rule applied.
  Reader should not generalize "P-gated implies `ids`-safe" from this kind
  to its siblings.
- **Not searchable.** The `events.search_tsv` generated column stores `NULL`
  for `kind:1059` rows, so a gift wrap can never surface through NIP-50
  full-text search, proven from the wire by two independent tests (one at
  the search-service level, one end-to-end through the relay protocol).
- **Not a workflow trigger.** `buzz-workflow` is never invoked for a
  `kind:1059` event; its ciphertext is never handed to a workflow condition
  as trigger payload.
- **Push-wake authorization is self-`#p`-only.** Kind 1059 is one of five
  kinds eligible to wake a push lease, but a lease may only match a gift
  wrap whose outer `#p` tag names the lease's own author -- otherwise the
  globally-stored, unfiltered nature of gift wraps would let a wake leak
  who is receiving traffic to an observer who merely holds *some* active
  lease.

## Boundary

This node does not describe:

- **How the relay is built.** The container-level shape of `buzz-relay`
  (routing, ingest pipeline, push runtime) and `buzz-db`/Postgres (the
  `search_tsv` schema) that implement the rules above is the architecture
  family's territory -- see the `references` relationships below.
- **The identity-binding invariant as a whole.** The pubkey-match rule and
  its gift-wrap exception are one instance of a relay-wide invariant
  documented independently as its own principle node; this node cites and
  reuses that description rather than restating it.
- **The push-notification flow as a whole.** The end-to-end trigger-to-wake
  path, of which gift-wrap match authorization is one rule among several,
  is documented independently as its own flow node.
- **The interface or wire contract.** The exact NIP-17 JSON shapes (rumor,
  seal, gift-wrap event structures) are a specification the standard NIP
  itself defines, not an interface this repository exposes or restates; no
  `interfaces-events`-typed corpus node exists yet at this recorded revision
  for this node to `references`.
- **The step-by-step flow of sending or receiving a gift-wrapped message.**
  No client in this repository performs that flow today; a future flow
  node, once such a client exists, would narrate it.
- **Plaintext DM channels.** Buzz's separate, shipped "start a private
  conversation" capability (`channel_type='dm'` channels, plaintext
  content) is a distinct capability with its own code paths
  (`crates/buzz-db/src/dm.rs`, `handle_dm_open`/`handle_dm_add_member`/
  `handle_dm_hide`) that never reference `KIND_GIFT_WRAP`. An unmerged
  sibling corpus draft for that capability independently reached the same
  conclusion and scoped gift wrap out of its own document; this node is the
  other half of that split, not a duplicate of it.
- **NIP-44 encryption as a general-purpose primitive.** The `nip44` crate
  feature Buzz *does* enable is used elsewhere -- agent observer frames,
  agent memory ("engrams"), and NIP-AB device pairing all encrypt their
  content with NIP-44 -- but none of those are gift-wrapped (`kind:1059`)
  events; they are a different application of the same encryption
  primitive to a different data class, out of scope for this node.

## Relationships

- references: `architecture-containers-relay` -- owns the ingest, event, and
  push-runtime code (`ingest_event_inner`, `handle_event`,
  `push_filter_authorized_for_event`) that implements every rule above.
- references: `architecture-containers-postgres` -- owns the
  `events.search_tsv` generated-column schema that enforces this
  capability's storage-level search exclusion.
- references: `architecture-principles-signed-events` -- documents the
  relay-wide event-pubkey/identity-binding invariant, of which the
  gift-wrap exemption described here is one named exception.
- references: `architecture-flows-push-notification` -- documents the full
  trigger-to-wake push flow, of which the gift-wrap-specific push-match
  authorization rule described here is one step.

**Not declared:** a relationship to the DM-channel capability
(`capabilities-channels-dm-channel`) or to any `interfaces-events`/flow node
for this capability -- neither exists in `origin/launchpad`'s corpus tree at
the recorded revision (verified via the same tree listing the two
architecture precedent nodes above were checked against). The DM-channel
draft is an open PR (#1914) at this recorded revision; add a `references` or
boundary-clarifying edge between the two once it merges, per `AGENTS.md`'s
rule that a relationship target must resolve on the branch being merged
into, not the author's own worktree.

## Verification

- **Storage-level exclusion:** `excluded_kinds_are_storage_level_unsearchable`
  in `crates/buzz-search/tests/fts_integration.rs` (requires Postgres,
  `#[ignore]`).
- **End-to-end relay behavior:** `test_nip17_gift_wrap_accepted`,
  `test_nip17_gift_wrap_requires_p_filter`,
  `test_nip17_gift_wrap_recipient_receives`, and
  `test_nip17_gift_wrap_not_searchable` in
  `crates/buzz-test-client/tests/e2e_nostr_interop.rs` (requires a running
  relay, run via `cargo test --test e2e_nostr_interop -- --ignored`).
- **Gap, stated rather than silenced:** these tests were read from source,
  not executed, while drafting this node -- running them requires a live
  relay plus Postgres/Redis infrastructure this authoring task did not
  stand up. No test anywhere exercises actual gift-wrap *construction* or
  *decryption* (sealing a rumor, unwrapping a gift wrap), because no code
  in this repository does either.

## Scope and omissions

**This node covers** what Buzz's relay does with an opaque `kind:1059`
NIP-17 gift-wrap event: the identity-binding exemption that lets it be
submitted at all, the transport and scope requirements to submit one, the
`#p`-gated read rule and its deliberate `ids`-lookup exemption, the
storage-level search exclusion, the workflow-trigger exclusion, and the
push-wake authorization rule -- and, separately, the honest gap that no
Buzz-built client constructs or reads one.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay is built (routing, ingest, push runtime) | `architecture-containers-relay` |
| The `search_tsv` storage schema | `architecture-containers-postgres` |
| The relay-wide identity-binding invariant | `architecture-principles-signed-events` |
| The full push-notification trigger-to-wake flow | `architecture-flows-push-notification` |
| Plaintext DM channels (a distinct, shipped capability) | a separate capability node (`capabilities-channels-dm-channel`, unmerged PR #1914 at this revision) |
| NIP-44 as a general encryption primitive (observer frames, engrams, pairing) | those subsystems' own future corpus nodes |
| The NIP-17 wire contract itself (rumor/seal/gift-wrap JSON shapes) | the external NIP-17 specification; no interface node exists yet |
| The step-by-step flow of sending/receiving a gift-wrapped message | a future flow node, once a client implements one |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating, and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether any external, non-Buzz Nostr client is actually used today to
  send gift-wrapped DMs into a Buzz community** was not observed -- this
  node establishes only that the relay's design and tests support such a
  client, not that one is in active use against a real Buzz deployment.
- **Whether the four end-to-end gift-wrap tests currently pass against a
  live relay** was not confirmed by running them; they were read from
  source only, per the gap noted in *Verification*.
- **Whether first-party gift-wrap construction (a rumor/seal/wrap builder in
  `buzz-sdk` or a client) is planned** was not established -- no roadmap
  document or open issue referencing NIP-17 client support was found during
  this node's research.
- **Whether any Block-internal (`squareup/*`) deployment path changes this
  capability's behavior** was not checked; per this fork's own `AGENTS.md`,
  that infrastructure is outside this repository's visible source.
