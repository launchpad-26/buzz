---
id: interfaces-nostr-buzz-nips-nip-ia
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "docs/nips/NIP-IA.md defines a relay-scoped protocol with three event families: user-signed requests (kind:9035 archive request, kind:9036 unarchive request), relay-signed deltas (kind:8002 archived identity, kind:8003 unarchived identity), and a relay-signed replaceable current-state snapshot (kind:13535 archived identities list)."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md:15-19"
      - "docs/nips/NIP-IA.md:62-72"
  - statement: "buzz-core/src/kind.rs declares the five NIP-IA kind constants with the same numeric values the spec assigns: KIND_IA_ARCHIVE_REQUEST=9035, KIND_IA_UNARCHIVE_REQUEST=9036, KIND_IA_ARCHIVED=8002, KIND_IA_UNARCHIVED=8003, KIND_IA_ARCHIVED_LIST=13535."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:406-417"
  - statement: "is_identity_archive_request_kind(kind) in buzz-core/src/kind.rs matches only the two request kinds (9035/9036); its own doc comment states the relay-signed delta/snapshot kinds are intentionally excluded because they are emitted by the relay, never ingested as commands."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:805-811"
  - statement: "crates/buzz-relay/src/handlers/identity_archive.rs's handle_identity_archive_event is the relay-side entry point for kind:9035/9036 requests: it enforces a freshness window, requires exactly one NIP-70 '-' tag and exactly one valid p tag, validates an optional replaced-by tag, determines a consent path, applies the archive/unarchive state change, and (if state changed) publishes the corresponding delta and a fresh snapshot."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs:39-139"
  - statement: "enforce_freshness in identity_archive.rs rejects a request whose created_at differs from the relay's current time by more than 120 seconds, matching the spec's RECOMMENDED plus-or-minus-120-second freshness window."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs:140-153"
      - "docs/nips/NIP-IA.md:290"
  - statement: "determine_consent_path in identity_archive.rs resolves the consent path in this order: actor==target is treated as self-signed unconditionally; otherwise an actor whose relay-membership role is owner or admin is treated as admin; otherwise the request must pass verify_owner_consent (the owner-of-agent path) or the request is rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs:225-247"
  - statement: "verify_owner_consent in identity_archive.rs requires both a request-borne auth tag on the kind:9035/9036 event itself (verified with time-bound conditions evaluated against the request's created_at) and a matching auth tag naming the same owner on the target's own latest stored kind:0 profile; it returns an error if either check fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs:249-283"
  - statement: "docs/nips/NIP-IA.md frames the request-borne and published-profile-attestation owner-of-agent proofs as two interchangeable ways to establish consent=owner, stating a relay MAY support either or both -- it does not describe them as jointly required."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md:241-246"
  - statement: "Buzz's relay implementation therefore requires strictly more than the spec's minimum for the owner-of-agent path: a request lacking a request-borne auth tag, or one whose target has no live kind:0 carrying a matching auth tag, is rejected even though the spec would accept either proof alone."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs:249-283"
      - "docs/nips/NIP-IA.md:241-279"
    confidence: 0.85
  - statement: "crates/buzz-relay/src/handlers/side_effects.rs's publish_nipia_archived and publish_nipia_unarchived (both delegating to a shared publish_nipia_delta) sign and store the kind:8002/8003 delta with the relay keypair, including consent, e (request id), reason, and (for archive only) replaced-by tags."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:3578-3661"
  - statement: "publish_nipia_archival_list in side_effects.rs rebuilds the kind:13535 snapshot from the canonical archived-identities list on every accepted state change, retrying up to 8 times against a concurrent-mutation race, and forces the new snapshot's created_at strictly past the previous head's."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:3378-3470"
  - statement: "crates/buzz-db/src/store/archived_identities.rs persists archive state keyed by (community_id, pubkey), not by a single relay-global set; list_archived, archive, and unarchive all take a CommunityId parameter."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/archived_identities.rs:38-118"
      - "crates/buzz-db/src/store/archived_identities.rs:173"
  - statement: "docs/multi-tenant-conformance.md names archived_identities directly, stating relay membership, pubkey allowlist, and archived identities are relay-global gates over pubkeys that should be community-scoped in Buzz's multi-tenant model, with primary/unique keys becoming (community_id, pubkey)."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:45"
  - statement: "Buzz's community is therefore the unit that instantiates the spec's abstract per-relay scope: NIP-IA's own text defines relay-scoping in terms of a single relay identity, and Buzz maps that onto one archived_identities row set per community rather than per physical relay process."
    entry_class: INFERENCE
    evidence:
      - "docs/nips/NIP-IA.md:51-60"
      - "crates/buzz-db/src/store/archived_identities.rs:1-3"
      - "docs/multi-tenant-conformance.md:45"
    confidence: 0.8
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs carries an archive_in_a_does_not_affect_b test asserting the community-scoping obligation, but it is marked #[ignore] and its body only calls pending_lane(...) -- it is a named pending obligation, not a currently executing or passing test."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:900-911"
  - statement: "crates/buzz-cli/src/lib.rs declares three buzz-cli subcommands under AgentsCmd for this interface: Archive (kind 9035), Unarchive (kind 9036), and Archived (a read of kind 13535), each with clap-derived --help text describing the command's own auth-retry and verification behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:299-361"
  - statement: "crates/buzz-cli/src/commands/agents.rs's dispatch for AgentsCmd::Archive and AgentsCmd::Unarchive validates the target is 64-hex, resolves an auth tag via resolve_auth (retrying once on extraction failure unless --admin is passed), builds the event with build_archive_identity_request or build_unarchive_identity_request from buzz-sdk, signs it, and submits it, printing {ok, event_id, action, target}."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/agents.rs:88-163"
  - statement: "fetch_archived_snapshot in agents.rs (shared by the Archived command and the roster-archive filter) fetches the relay's NIP-11 self pubkey, queries for the latest kind:13535 authored by that pubkey, and verifies it in verify_archived_event before trusting any pubkey it lists; a trust failure is fatal for the Archived command specifically, so a verification command can never look like a false success."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/agents.rs:406-460"
  - statement: "crates/buzz-sdk/src/builders.rs provides build_archive_identity_request (kind 9035) and build_unarchive_identity_request (kind 9036) as the typed event builders this interface's write side is constructed from."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:1838-1963"
  - statement: "crates/buzz-sdk/src/nip_oa.rs's verify_auth_tag implements the NIP-OA Schnorr-signature verification over the nostr:agent-auth: preimage that identity_archive.rs's verify_auth_tag_owner calls to check an auth tag's owner against a given target pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:179"
      - "crates/buzz-relay/src/handlers/identity_archive.rs:319-325"
  - statement: "node.schema.json's type enum has no literal interface value; interfaces-events is the single combined value PRD #602 assigned to both interface-shaped and event-kind-shaped corpus subject matter, per the corpus's own interface template's 'A note on type' section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "Every corpus node merged to origin/launchpad at this node's recorded revision uses origin: launchpad; none uses upstream, cohort, or supporting, despite several documenting Buzz's own upstream product architecture (e.g. architecture/principles/relay-is-source-of-truth.md)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/relay-is-source-of-truth.md"
      - "launchpad/docs/corpus/AGENTS.md"
---

# NIP-IA (Identity Archival): interface

This node documents Buzz's implementation of NIP-IA, a Buzz-authored, relay-scoped
Nostr protocol extension (`docs/nips/NIP-IA.md`) for archiving and unarchiving
identities: hiding a retired pubkey from active-member and autocomplete surfaces
without deleting its historical events or implying any global reputation state. The
boundary is the relay's Nostr event-ingestion path: clients (human users, agents, or
`buzz-cli`) submit signed `kind:9035`/`9036` requests over the same WebSocket/HTTP
event-submission surface every other Nostr event uses, and the relay answers with
signed `kind:8002`/`8003`/`13535` state events on the same channel. `buzz-cli`'s
`agents archive`/`unarchive`/`archived` subcommands are the primary agent-facing
surface over this same wire protocol.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Submit archive request (`kind:9035`) | `docs/nips/NIP-IA.md:76-108`; built by `crates/buzz-sdk/src/builders.rs:1838-1963` (`build_archive_identity_request`); relay-side handling in `crates/buzz-relay/src/handlers/identity_archive.rs:39-139` | User/agent/owner-signed request asking the relay to archive a target pubkey |
| Submit unarchive request (`kind:9036`) | `docs/nips/NIP-IA.md:110-133`; built by `builders.rs:1838-1963` (`build_unarchive_identity_request`); same relay handler | User/agent/owner-signed request asking the relay to unarchive a target pubkey |
| Relay archive delta (`kind:8002`) | `docs/nips/NIP-IA.md:135-169`; emitted by `crates/buzz-relay/src/handlers/side_effects.rs:3578-3661` (`publish_nipia_archived`) | Relay-signed announcement that a target became archived, naming the consent path |
| Relay unarchive delta (`kind:8003`) | `docs/nips/NIP-IA.md:170-189`; emitted by `side_effects.rs:3578-3661` (`publish_nipia_unarchived`) | Relay-signed announcement that a target became unarchived |
| Archive snapshot (`kind:13535`) | `docs/nips/NIP-IA.md:191-217`; emitted by `side_effects.rs:3378-3470` (`publish_nipia_archival_list`) | Relay-signed, replaceable, current-state list of every archived pubkey |
| `buzz agents archive <PUBKEY>` | `crates/buzz-cli/src/lib.rs:299-329`; dispatch in `crates/buzz-cli/src/commands/agents.rs:88-126` | CLI wrapper: resolves owner-auth, builds and submits a `kind:9035` request |
| `buzz agents unarchive <PUBKEY>` | `buzz-cli/src/lib.rs:330-349`; dispatch in `agents.rs:128-163` | CLI wrapper: resolves owner-auth, builds and submits a `kind:9036` request |
| `buzz agents archived` | `buzz-cli/src/lib.rs:350-361`; dispatch in `agents.rs:457-461` (`cmd_archived`), verification in `agents.rs:406-460` (`fetch_archived_snapshot`/`verify_archived_event`) | Reads and cryptographically verifies the relay's current `kind:13535` snapshot |

## Contract and stability

**Freshness.** The relay rejects a `kind:9035`/`9036` request whose `created_at` is
more than 120 seconds from the relay's clock (`identity_archive.rs:140-153`), matching
the spec's RECOMMENDED window (`docs/nips/NIP-IA.md:290`).

**Idempotency.** Archiving an already-archived target or unarchiving a non-archived
target is a no-op that returns success without emitting a new delta or snapshot: the
handler checks the database's `changed` return value and returns early when nothing
changed (`identity_archive.rs:100-102`), matching the spec's idempotency requirement
(`docs/nips/NIP-IA.md:292`).

**Versioning.** `kind:13535` is a replaceable event per NIP-01 and is Buzz's
authoritative current-state view; `publish_nipia_archival_list` forces each new
snapshot's `created_at` strictly past the previous head's own `created_at`
(`side_effects.rs:3378-3470`) so that same-second replacement ordering cannot silently
strand a stale archive set. Clients (`buzz agents archived`) are expected to always
re-fetch and re-verify the latest snapshot rather than cache it indefinitely.

**Authentication and authorization.** Every relay-signed event (`8002`/`8003`/`13535`)
must be verified against the relay's own NIP-11 `self` pubkey before being trusted;
`fetch_archived_snapshot`/`verify_archived_event` implement this client-side, and a
verification failure is fatal for `buzz agents archived` specifically rather than a
false-empty success (`agents.rs:406-421`). On the write side, consent resolves to one
of `self` (actor equals target), `admin` (actor's relay-membership role is
`owner`/`admin`), or `owner` (owner-of-agent proof) — see `identity_archive.rs:225-247`.
**Buzz's owner-of-agent check is stricter than the spec's:** the spec frames the
request-borne `auth` tag and the target's published-profile `auth` tag as two
independently sufficient proofs (`docs/nips/NIP-IA.md:241-246`), but
`verify_owner_consent` requires both to be present and to agree
(`identity_archive.rs:249-283`) — a request with only one of the two proofs is
rejected here even where the spec would accept it.

**Error/rejection behavior.** A malformed or unauthorized request never mutates
archive state and never produces a delta or snapshot; the relay handler returns a
descriptive `Err(String)` for every rejection path (missing/multiple `p` tags, missing
NIP-70 tag, invalid `replaced-by`, failed consent resolution) rather than silently
dropping the event (`identity_archive.rs:39-139`).

## Boundary

This node does not describe:
- **NIP-OA's own wire contract** (the `auth` tag's preimage, Schnorr verification, and
  condition-clause grammar) — that is implemented in `crates/buzz-sdk/src/nip_oa.rs`
  and specified in NIP-OA; this node only cites the call site
  (`identity_archive.rs:319-325`) where NIP-IA reuses it.
- **NIP-43's membership/access-control semantics**, which NIP-IA composes with but does
  not redefine (`docs/nips/NIP-IA.md:31,39`); a pubkey can be archived without being
  banned and vice versa.
- **A field-by-field, domain-expert-depth catalogue** of every tag and condition-clause
  grammar rule — `docs/nips/NIP-IA.md` itself is that catalogue and is cited throughout
  rather than restated.
- **`buzz-desktop`'s UI treatment** of archived identities (hiding them from pickers,
  showing "Archived on this relay" metadata) — this node covers the relay/CLI wire
  contract, not the desktop rendering layer.

## Relationships

- implements: corpus-template-interface
- references: architecture-principles-community-is-security-boundary

No relationship to a corpus node for NIP-OA, NIP-DV, or NIP-43 is declared: none of
those sibling `buzz-nips` interface nodes exists yet on `origin/launchpad`, and a
`relationships[].target` naming an id no node carries is a hard validation error.

## Examples

**Valid: self-archive after key rotation.** Alice signs a `kind:9035` with
`actor == target == alice_old`, a `reason` of `rotated`, and a `replaced-by` tag naming
`alice_new`. `determine_consent_path` resolves `ConsentPath::SelfSigned` immediately
because `actor_hex == target_hex` (`identity_archive.rs:230-232`), the relay archives
`alice_old`, and `publish_nipia_archived` emits a `kind:8002` delta with
`consent=["self","<alice_old>"]` plus the `replaced-by` tag, followed by a refreshed
`kind:13535` snapshot including `alice_old` (`docs/nips/NIP-IA.md:462-498`,
mirrored in `side_effects.rs:3378-3470,3578-3661`).

**Failure: owner-of-agent request with only one proof.** An owner signs a `kind:9035`
targeting a stale agent key, attaching a request-borne `auth` tag, but the target's
stored `kind:0` profile carries no `auth` tag at all (e.g. the agent never published
one, or its profile was republished without it). `verify_owner_consent` extracts the
request's `auth` tag successfully but then fails to extract a valid `auth` tag from the
target's live profile, returning `Err("missing auth tag")` from
`extract_single_auth_tag_json` on the profile lookup path
(`identity_archive.rs:249-283,300-317`). The request is rejected, no state changes, and
no `kind:8002`/`kind:13535` event is emitted — even though `docs/nips/NIP-IA.md:264-268`
describes the published-profile-attestation path as usable independently for exactly
this "owner has no saved credential" case, and this request supplies the *other*
sufficient proof instead.

## Scope and omissions

**This node covers** the wire contract for Buzz's NIP-IA implementation: the five
event kinds, the relay's request-processing algorithm (freshness, tag validation,
consent resolution, idempotent state application, delta/snapshot emission), the
`buzz-cli` agent-facing surface, and the one confirmed divergence between the spec's
minimum owner-of-agent proof and Buzz's stricter implementation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-OA's own auth-tag cryptographic contract | NIP-OA's own specification and `crates/buzz-sdk/src/nip_oa.rs` |
| NIP-43's membership/ban semantics | NIP-43's own specification |
| Desktop/mobile UI treatment of archived identities | the desktop/mobile client code, not this relay/CLI-facing node |
| Whether Buzz's stricter both-paths-required owner check is an intentional hardening decision or an unnoticed gap versus the spec | not resolved by this node; recorded as an `INFERENCE`, not adjudicated |

**Expected but not verified when this node was written:**
- The `conformance_multitenant.rs::archive_in_a_does_not_affect_b` test that would
  exercise the community-scoping claim end-to-end is `#[ignore]`d and only calls
  `pending_lane(...)` — the community-scoping behavior is confirmed from the
  `(community_id, pubkey)` schema and query code directly, not from a passing
  integration test.
- Admin-role resolution (`get_relay_member` returning `role == "owner"/"admin"`) was
  read at the call site but its own role-assignment implementation was not traced in
  this pass.
- Whether any `buzz-desktop` surface currently reads `kind:13535` client-side (per the
  spec's Client Behavior section) was not checked; this node's Operations table covers
  only the relay and `buzz-cli` sides confirmed by code.
