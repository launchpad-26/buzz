---
id: interfaces-nostr-buzz-nips-nip-dv
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "NIP-DV (\"DM Visibility\") is a draft, optional, relay-scoped NIP that depends on NIP-01, NIP-11 and NIP-43, and defines exactly one relay-signed event kind: kind:30622, the DM Visibility Snapshot. There is no user-signed request kind for this NIP; hide/unhide intent is carried by the existing kind:41012 (hide) and kind:41010 (open/re-open) DM commands."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-DV.md:1-19"
  - statement: "buzz-core declares KIND_DM_VISIBILITY = 30622, asserts at compile time that it falls in the parameterized-replaceable range (30000-39999), and lists it in is_relay_only_kind, whose doc comment states the kind 'may only be authored by the relay' and that 'client submission of these kinds must be rejected'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:449"
      - "crates/buzz-core/src/kind.rs:828-839"
      - "crates/buzz-core/src/kind.rs:863"
  - statement: "The relay's event-ingest path calls is_relay_only_kind on every submitted event and rejects a match with IngestError::Rejected(\"restricted: relay-only kind\"), so a client-submitted kind:30622 event is rejected before signature verification runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2199-2201"
  - statement: "publish_dm_visibility_snapshot builds the snapshot's tags as exactly one d tag (the viewer's hex pubkey), one p tag (the same value, for the read-authorization gate), and one h tag per currently hidden DM channel id, signs the event with the relay's own keypair (state.relay_keypair), forces created_at strictly past any prior snapshot for that viewer, and stores it via replace_parameterized_event -- NIP-01 parameterized-replaceable semantics, so only the newest event per (kind, pubkey, d-tag) is current."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:3482-3563"
  - statement: "publish_dm_visibility_snapshot is called from two sites in command_executor.rs: the DM-hide command handler (kind:41012), after state.db.hide_dm commits, and the DM-open/re-open command handler (kind:41010), only on the branch where an existing hidden DM is being re-opened (not on first-open of a new DM, which has nothing hidden to clear)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:409-415"
      - "crates/buzz-relay/src/handlers/command_executor.rs:614-629"
  - statement: "publish_dm_visibility_snapshot is invoked as a best-effort post-commit side effect: its Err case is only logged with warn! in both call sites, so a snapshot-publish failure does not fail or roll back the hide/re-open command itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:412-414"
      - "crates/buzz-relay/src/handlers/command_executor.rs:629-631"
  - statement: "p_gated_filters_authorized denies any filter that can match a P_GATED_KINDS member (which includes KIND_DM_VISIBILITY) unless its #p tag is present and every value equals the authenticated reader's pubkey, and its own code comment states that for KIND_DM_VISIBILITY specifically, the ordinary kindless-ids exemption is deliberately withheld because the kind is relay-signed (its id is not author-bound) and its content is plaintext -- so an explicit kinds:[30622] filter loses the ids exemption even when an id is known."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1182-1211"
  - statement: "Live WebSocket fan-out applies a second, result-level owner gate for kind:30622 (and kind:44200) events: handle_event computes owner_only_kind for these two kinds and restricts delivery to the connection whose authenticated pubkey matches the event's own #p tag value, closing the gap a kindless ids:[...] subscription would otherwise leave open at the filter-level gate alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:457-472"
  - statement: "buzz-search's integration test suite inserts a kind:30622 row and asserts it MUST NOT appear in full-text-search results, alongside a comment identifying it as 'kind:30622 DM visibility snapshot -- MUST NOT be searchable'; this is asserted as a negative, load-bearing case distinct from the positive kind:9 control row in the same test."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs:1218-1228"
      - "crates/buzz-search/tests/fts_integration.rs:1295-1305"
  - statement: "crates/buzz-test-client/tests/e2e_nostr_interop.rs::test_nipdv_hide_then_reopen_updates_snapshot is a (currently #[ignore]'d, live-relay) end-to-end test that hides a DM via kind:41012, reads the viewer's kind:30622 snapshot filtered by #p, asserts the hidden channel id appears in its h tags, then re-opens the DM via kind:41010 and asserts the channel id is absent from the refreshed snapshot -- exercising the full hide-then-reopen round trip this NIP exists to support."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1256-1323"
  - statement: "crates/buzz-test-client/tests/e2e_nostr_interop.rs::test_nipdv_explicit_kind_query_forbidden_for_third_party is a (currently #[ignore]'d, live-relay) end-to-end test asserting that a viewer B who queries POST /query with an explicit kinds:[30622] filter plus a known snapshot id belonging to viewer A receives HTTP 403 Forbidden, demonstrating the explicit-kind path's loss of the ids exemption described by p_gated_filters_authorized."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1601-1641"
  - statement: "node.schema.json's type enum has thirteen members and the only one covering interface-shaped subject matter is the single hyphenated value interfaces-events (per parent Feature #602's success criteria, which lists 'interfaces/events' as one combined in-scope surface); the merged corpus template for interface-shaped nodes (templates/interface.md, id corpus-template-interface) states explicitly that 'a node built from this template therefore carries type: interfaces-events.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md:216-228"
  - statement: "As of this node's recorded revision, no corpus node of type interfaces-events (or any event-kind-shaped node) is merged to origin/launchpad, and no other buzz-nip interface node exists yet in this worktree's own tree either, so no relationships target exists that would resolve once this node merges to origin/launchpad; per AGENTS.md's own rule, a relationships target must already be merged on the branch being merged into, not merely present in the author's own worktree."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md:37-40"
      - "launchpad/docs/corpus/AGENTS.md:342-350"
  - statement: "NIP-DV's own Security Considerations section states that the desktop client currently trusts whatever its configured relay returns from the authenticated /query endpoint and does not yet re-verify the relay-identity signature client-side, and names wiring explicit client-side relay-identity verification as future cross-cutting hardening to be applied uniformly across NIP-DV, NIP-IA and NIP-OA rather than piecemeal."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-DV.md:118-122"
---

# NIP-DV: DM Visibility Snapshot interface

This node documents Buzz's custom NIP-DV extension: a relay-signed, per-viewer,
parameterized-replaceable Nostr event (`kind:30622`) that projects a viewer's
hidden-DM-conversation set so a pure-Nostr client can filter hidden DMs out of
its sidebar. The boundary is a WebSocket/HTTP Nostr event surface between the
Buzz relay (publisher and read-gatekeeper) and any connected client (reader);
there is no user-signed request side to this NIP — the write side is
relay-only, and the read side is a standard Nostr `REQ`/`/query` filter scoped
by `#p`.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Publish `kind:30622` DM Visibility Snapshot | `crates/buzz-relay/src/handlers/side_effects.rs::publish_dm_visibility_snapshot` (`docs/nips/NIP-DV.md` §Event Formats, §Relay Processing Algorithm) | Relay recomputes a viewer's full hidden-DM set and republishes it as a fresh relay-signed, parameterized-replaceable event, `d`/`p` = viewer pubkey, one `h` tag per hidden DM channel. |
| Trigger: hide a DM (`kind:41012`) | `crates/buzz-relay/src/handlers/command_executor.rs:614-629` | After `hide_dm` commits, the relay republishes the caller's snapshot as a post-commit, best-effort side effect. |
| Trigger: re-open a hidden DM (`kind:41010`, re-open branch only) | `crates/buzz-relay/src/handlers/command_executor.rs:409-415` | After a re-open clears an existing `hidden_at`, the relay republishes the caller's snapshot. First-open of a brand-new DM does not trigger this — nothing was hidden to clear. |
| Read the viewer's current snapshot | `docs/nips/NIP-DV.md` §Client Behavior; relay-side gate in `crates/buzz-relay/src/handlers/req.rs::p_gated_filters_authorized` | Client issues `kinds:[30622]`, `#p:[<own pubkey>]`, `limit:1` over WebSocket `REQ` or `POST /query`; the relay serves at most the caller's own current snapshot. |

## Inputs, outputs and errors

**Input** to the relay is never a client-signed `kind:30622` event — there is
none. The only client-facing inputs are the two existing DM commands
(`kind:41012` hide, `kind:41010` open/re-open) that indirectly trigger a
republish, and a read filter (`kinds:[30622]`, `#p:[<viewer>]`).

**Output** is a `kind:30622` event: `pubkey` = the relay's own signing key,
empty `content`, exactly one `d` tag and one `p` tag (both the viewer's hex
pubkey), and zero or more `h` tags (one per currently hidden DM channel id).
Clients must treat the `h` tags as an unordered set and must not parse
`content`.

**Error and rejection behavior:**
- A client attempting to submit a `kind:30622` event directly is rejected at
  ingest with `restricted: relay-only kind`, before signature verification —
  `is_relay_only_kind` includes `KIND_DM_VISIBILITY` and `ingest.rs` enforces
  it unconditionally.
- A read query naming `kinds:[30622]` (or any `P_GATED_KINDS` member) without
  a matching `#p` filter is rejected by the filter-level gate
  (`p_gated_filters_authorized`) — over HTTP this surfaces as `403 Forbidden`
  (see the failure example below); over WebSocket it surfaces as `CLOSED`.
- Snapshot publication itself is best-effort: if it fails after a successful
  hide/re-open command, the underlying command still succeeds (its own
  transaction already committed) and only a `warn!` log is emitted. The next
  hide/unhide state change republishes a fresh snapshot, so a stale snapshot
  is a presentation-only, self-healing condition, never a data-loss one.

## Authentication and authorization

Two independent layers gate reads, matching the spec's stated defense in
depth:

1. **Filter-level `#p` gate.** `p_gated_filters_authorized` requires any
   filter that can match `kind:30622` to carry `#p` equal to the
   authenticated reader's own pubkey. For this kind specifically, the
   ordinary "a kindless `ids` filter is exempt" rule is withheld even when
   `ids` is present and `kinds` is explicit, because the event's `id` is not
   author-bound (it's relay-signed) and its plaintext content would
   otherwise leak through a known-id lookup.
2. **Result-level owner check.** Independent of the filter gate,
   `handle_event`'s live fan-out path restricts delivery of `kind:30622`
   events to the connection whose authenticated pubkey equals the event's own
   `#p` value — closing the residual gap a kindless `ids` subscription could
   otherwise exploit at delivery time.

Write authorization is binary and relay-only: only the relay's own keypair
(`state.relay_keypair`) may produce a valid `kind:30622` event; every other
signer is rejected at ingest regardless of any other permission the caller
holds.

Per NIP-DV's own Security Considerations, the current implementation posture
is that connected clients do not verify the relay-identity signature
client-side and instead trust the authenticated, configured relay connection
(NIP-42/NIP-98) — the same posture NIP-IA currently has. Wiring explicit
client-side verification is named as a deferred, cross-cutting hardening
task spanning NIP-DV, NIP-IA and NIP-OA, not something this interface commits
to today.

## Versioning, compatibility and ordering

`kind:30622` is a NIP-01 parameterized-replaceable kind (30000–39999),
keyed by its `d` tag (the viewer's pubkey), so there is exactly one current
snapshot address per viewer and the relay's own compile-time assertion
confirms the constant sits in that range. The relay always **recomputes and
replaces** the full hidden-DM set rather than emitting incremental deltas, so
there is no ordering hazard to reconcile client-side: NIP-01 replaceable-event
"newest wins" semantics make a stale snapshot simply be superseded by the next
one, and `publish_dm_visibility_snapshot` additionally forces `created_at`
strictly past the viewer's prior snapshot to avoid a same-second replacement
losing a stale-write race. There is no separate protocol version for this
kind; a compatible client is any client that understands NIP-01 replaceable
events and NIP-29-style `h`-tag channel ids.

## Examples

**Valid:** `test_nipdv_hide_then_reopen_updates_snapshot` hides a DM
(`kind:41012`), reads the viewer's `kind:30622` snapshot filtered by
`#p:[<viewer>]`, confirms the hidden channel id appears among its `h` tags,
then re-opens the DM (`kind:41010`) and confirms the channel id is absent from
the refreshed snapshot.

**Failure:** `test_nipdv_explicit_kind_query_forbidden_for_third_party` has
viewer B query `POST /query` with an explicit `kinds:[30622]` filter and
viewer A's known snapshot event id; the relay responds `403 Forbidden` rather
than serving A's private hidden-DM set to B.

## Boundary

This node does not describe:
- The wire contract of `kind:41012`/`kind:41010` themselves (their own tag
  shape and command semantics) — those are separate event kinds this
  interface is triggered by, not part of it.
- NIP-IA's or NIP-OA's own relay-signed-snapshot interfaces, referenced above
  only to note they share the same signing/trust posture and the same
  deferred client-verification gap.
- A full parameter-by-parameter API-reference catalogue — this node follows
  the corpus's interface template's own stated depth (interface description,
  operations, contract/stability), not domain-expert-depth cataloguing.

## Relationships

None declared. No merged corpus node (interfaces-events-shaped or otherwise)
is a legitimate target today, and other buzz-nip interface nodes being
authored in the same dispatch batch are unmerged siblings, not valid targets
per `AGENTS.md`'s rule that a relationship must resolve against the branch
being merged into. The first sibling NIP interface node to merge is the
natural point to revisit this.

## Scope and omissions

**This node covers** the `kind:30622` DM Visibility Snapshot event: what
triggers its publication, its tag shape, its relay-only write protection, its
two-layer read authorization, its parameterized-replaceable versioning and
ordering guarantees, and one passing/one failing example drawn from the
repository's own end-to-end test suite.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `kind:41012`/`kind:41010` DM hide/open command semantics | A future event-kind-shaped corpus node for those kinds, not yet authored |
| NIP-IA's and NIP-OA's own relay-signed-snapshot interfaces | Their own future interface nodes |
| Client-side relay-identity signature verification | Unimplemented cross-cutting hardening NIP-DV's own spec names as future work |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- The two end-to-end tests cited above (`test_nipdv_hide_then_reopen_updates_snapshot`,
  `test_nipdv_explicit_kind_query_forbidden_for_third_party`) are marked
  `#[ignore]` and require a live relay plus Postgres/Redis to execute; their
  assertions were read and confirmed by inspection, not by running the live
  suite in this task.
- Whether `audiences` should additionally include `operator` (given the
  security-posture note above) was left to reviewer judgment rather than
  decided here — see this task's plan document for the same open question.
