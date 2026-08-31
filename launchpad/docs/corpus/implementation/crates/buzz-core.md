---
id: implementation-crates-buzz-core
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "crates/buzz-core/src/lib.rs's own doc comment describes the crate as 'zero-I/O foundation types for the Buzz relay', providing StoredEvent, filter matching, kind constants, and event verification, and states 'All other Buzz crates depend on this one'; it declares 18 public modules (agent_turn_metric, channel, engram, error, event, filter, git_perms, invite, kind, network, nip10, observer, pairing, presence, private_managed_agent, relay, tenant, verification) plus a cfg-gated test_helpers module."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/lib.rs"
  - statement: "crates/buzz-core/Cargo.toml declares dependencies on base64, nostr, serde, serde_json, thiserror, uuid, chrono, hex, hmac, sha2, rand, subtle, zeroize, percent-encoding, and url only; a trailing comment in the file itself states 'NO tokio, NO sqlx, NO redis, NO axum -- zero I/O dependencies', which the dependency list corroborates directly rather than merely asserting."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/Cargo.toml"
  - statement: "16 crates under crates/ declare a real buzz-core dependency in their own Cargo.toml (buzz-acp, buzz-admin, buzz-audit, buzz-auth, buzz-cli, buzz-db, buzz-deletion, buzz-dev-mcp, buzz-media, buzz-pairing-cli, buzz-pubsub, buzz-relay, buzz-sdk, buzz-search, buzz-test-client, buzz-workflow); AGENTS.md's own crate-list description of buzz-core as foundational and used by nearly every other crate is corroborated by this count but not literal -- of 29 crates total under crates/, 13 (buzz-agent, buzz-backend-kubernetes, buzz-datastore-tracing, buzz-pair-relay, buzz-persona, buzz-push-gateway, buzz-relay-mesh, buzz-voice, buzz-ws-client, git-credential-nostr, git-sign-nostr, sprig, and buzz-conformance) declare no such dependency. buzz-conformance's Cargo.toml mentions 'buzz-core' only inside a code comment, not as a dependency line."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
      - "crates/buzz-admin/Cargo.toml"
      - "crates/buzz-audit/Cargo.toml"
      - "crates/buzz-auth/Cargo.toml"
      - "crates/buzz-cli/Cargo.toml"
      - "crates/buzz-db/Cargo.toml"
      - "crates/buzz-deletion/Cargo.toml"
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/buzz-media/Cargo.toml"
      - "crates/buzz-pairing-cli/Cargo.toml"
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-sdk/Cargo.toml"
      - "crates/buzz-search/Cargo.toml"
      - "crates/buzz-test-client/Cargo.toml"
      - "crates/buzz-workflow/Cargo.toml"
      - "crates/buzz-conformance/Cargo.toml"
  - statement: "crates/buzz-core/src/kind.rs defines 129 pub const KIND_* event-kind integer constants plus the classification predicates is_ephemeral, is_replaceable, is_parameterized_replaceable, is_moderation_command_kind, is_shared_gated_kind, is_unshared_gated_event, event_is_shared, is_workflow_execution_kind, event_kind_u32, and event_kind_i32 -- this is the registry AGENTS.md's own 'Event kinds' section names as canonical ('All event kind integers are defined in buzz-core/src/kind.rs')."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "AGENTS.md's claim that all event kind integers are defined in buzz-core/src/kind.rs does not hold universally: crates/buzz-relay/src/handlers/push_lease.rs:21 declares its own `pub const KIND_PUSH_LEASE: u32 = 30_350`, the identical value already registered as `KIND_PUSH_LEASE` at crates/buzz-core/src/kind.rs:109. Within buzz-relay itself, crates/buzz-relay/src/handlers/ingest.rs:443,699,2918 and crates/buzz-relay/src/handlers/side_effects.rs:2189,2324 reference the local `super::push_lease::KIND_PUSH_LEASE`, while crates/buzz-relay/src/handlers/req.rs:2117-2138 references the canonical `buzz_core::kind::KIND_PUSH_LEASE` -- two definitions of the same constant are both live inside one crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/push_lease.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "crates/buzz-cli/src/commands/notes.rs:38 declares its own `pub const KIND_LONG_FORM: u16 = 30023`, duplicating buzz-core's canonical `KIND_LONG_FORM: u32 = 30023` at crates/buzz-core/src/kind.rs, at a different integer width but the same numeric value; this is a narrow, single-file divergence, not a systemic one -- the same crate's commands/mem.rs, projects.rs, users.rs, project_channel.rs, and agents.rs all import kind constants directly from buzz_core::kind (KIND_AGENT_ENGRAM, KIND_PROJECT, KIND_GIT_REPO_ANNOUNCEMENT, KIND_MANAGED_AGENT, KIND_IA_ARCHIVED_LIST) rather than redefining them."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/notes.rs"
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-cli/src/commands/mem.rs"
      - "crates/buzz-cli/src/commands/projects.rs"
  - statement: "verify_event in crates/buzz-core/src/verification.rs checks that an event's id is the correct hash of its own fields and that its signature is a valid Schnorr signature, returning the VerificationError::InvalidId or VerificationError::InvalidSignature variants defined in crates/buzz-core/src/error.rs when either check fails; its own doc comment states it is CPU-bound and must be called via tokio::task::spawn_blocking in async contexts."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-core/src/error.rs"
  - statement: "StoredEvent (crates/buzz-core/src/event.rs) wraps a nostr::Event with received_at, channel_id, and a verified: bool field defaulting to false in StoredEvent::new; is_verified() reads that field, but a repository-wide grep for '.is_verified()' outside crates/buzz-core/src/event.rs itself returned no matches, so the field is not consulted by any downstream call site at this revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/event.rs"
  - statement: "filters_match (NIP-01 filter matching) and reader_authorized_for_event in crates/buzz-core/src/filter.rs are the two public entry points; reader_authorized_for_event's own doc comment states it gates KIND_DM_VISIBILITY and KIND_AGENT_TURN_METRIC by requiring the reader equal the event's #p tag, and that it 'guards every delivery surface -- WS historical pull (req.rs), HTTP bridge (bridge.rs), and live fan-out (event.rs)' so a kindless ids-only lookup still cannot read another user's private event."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "crates/buzz-core/src/tenant.rs defines CommunityId (an opaque UUID newtype constructible only via CommunityId::from_uuid) and TenantContext (constructible only via TenantContext::resolved), plus normalize_host and relay_url_authority; its own module doc comment states these types exist in buzz-core specifically so the DB, auth, pub/sub, search, audit, media, and relay-wiring layers can name a community the same way without depending on each other, and describes itself explicitly as 'a lint-and-review fence, not a compiler fence' because TenantContext::resolved and CommunityId::from_uuid are pub and so could in principle be called by a determined caller outside host resolution."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "The corpus node architecture-principles-host-selects-community's own evidence ledger already treats crates/buzz-core/src/tenant.rs and crates/buzz-relay/src/tenant.rs jointly as 'the implementation' of the row-zero invariant (req.community = resolve_host(connection.host)); its body names bind_community, the actual host-to-community resolution function, as living in crates/buzz-relay/src/tenant.rs, a different file of the same name in a different crate -- buzz-core supplies the type-level fence (CommunityId, TenantContext, normalize_host) but not the resolution mechanism itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/host-selects-community.md"
      - "crates/buzz-core/src/tenant.rs"
  - statement: "The corpus node architecture-principles-signed-events already cites crates/buzz-core/src/verification.rs as the single function enforcing its invariant, and crates/buzz-core/src/verification.rs's own unit tests (rejects_tampered_id, rejects_tampered_signature) plus crates/buzz-core/src/event.rs's tampered_signature_fails_verify are the tests that node names as the invariant's unit-level verification."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/signed-events.md"
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-core/src/event.rs"
  - statement: "buzz-core hosts several Buzz-custom NIP encodings whose spec documents are not themselves corpus nodes: agent_turn_metric.rs's own doc comment names NIP-AM, engram.rs names NIP-AE (with docs/nips/NIP-AE.md existing on disk), pairing/mod.rs names NIP-AB (with crates/buzz-core/src/pairing/NIP-AB.md and NIP-AB.spthy living alongside the module's own source), and private_managed_agent.rs names NIP-PMA (with docs/nips/NIP-PMA.md existing on disk)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/agent_turn_metric.rs"
      - "crates/buzz-core/src/engram.rs"
      - "docs/nips/NIP-AE.md"
      - "crates/buzz-core/src/pairing/mod.rs"
      - "crates/buzz-core/src/pairing/NIP-AB.md"
      - "crates/buzz-core/src/private_managed_agent.rs"
      - "docs/nips/NIP-PMA.md"
  - statement: "No crates/buzz-core/README.md exists (checked directly: `ls crates/buzz-core/*.md` reports no matches), unlike six other crates in this repository (buzz-acp, buzz-agent, buzz-cli, buzz-pairing-cli, git-credential-nostr, git-sign-nostr) that do carry their own README.md."
    entry_class: FACT
    evidence:
      - "ls(crates/buzz-core/*.md) -> no matches found"
      - "crates/buzz-acp/README.md"
      - "crates/buzz-agent/README.md"
      - "crates/buzz-cli/README.md"
      - "crates/buzz-pairing-cli/README.md"
      - "crates/git-credential-nostr/README.md"
      - "crates/git-sign-nostr/README.md"
  - statement: "buzz-core carries 262 #[test]-annotated unit tests across its own src/ files (counted via grep -rc '#[test]' across every .rs file under crates/buzz-core/src/, including crates/buzz-core/src/pairing/), run inline via `cargo test -p buzz-core`; the crate has no top-level tests/ directory (confirmed via `find crates/buzz-core -maxdepth 1 -type d`, which lists only Cargo.toml and src), consistent with its zero-I/O design -- there is nothing here that would need an integration harness."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-core/src/tenant.rs"
      - "crates/buzz-core/src/filter.rs"
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-core/src/engram.rs"
  - statement: "Taken together, the 129-constant registry in kind.rs plus the two locally-redefined constants found in buzz-relay and buzz-cli support the conclusion that AGENTS.md's 'All event kind integers are defined in buzz-core/src/kind.rs' describes the intended and overwhelmingly followed convention, not an enforced or universal one -- no lint, clippy rule, or CI check was searched for or found that would catch a new local KIND_ constant duplicating a buzz-core one."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/push_lease.rs"
      - "crates/buzz-cli/src/commands/notes.rs"
    confidence: 0.75
relationships:
  - type: implements
    target: architecture-principles-signed-events
  - type: implements
    target: architecture-principles-host-selects-community
---

# buzz-core: implementation reference

`buzz-core` (`crates/buzz-core`) is the zero-I/O foundation crate every other
substantial Buzz crate builds on: it owns the Buzz custom event-kind registry, the
Nostr event verification function the relay calls to accept or reject a submitted
event, NIP-01 filter matching and a private-content read gate, the multi-tenant
`CommunityId`/`TenantContext` types that make a community un-constructible from
client input, and the wire codecs for several Buzz-custom NIPs (NIP-AM, NIP-AE,
NIP-AB, NIP-PMA). It declares no I/O dependency (no `tokio`, `sqlx`, `redis`, or
`axum`) and is depended on directly by 16 of the repository's 29 crates. This node
documents what `buzz-core` is responsible for, what it deliberately is not (it
verifies and matches; it does not call the network, touch a database, or decide
authorization policy beyond the one reader-gate function it exposes), and where its
realization of two existing architecture-principle corpus nodes is partial rather
than complete.

## Target

`buzz-core` realizes several independent targets rather than one single spec, which
this node names individually instead of forcing a single artificial "the target":

- **`architecture-principles-signed-events`** (corpus node, `launchpad/docs/corpus/architecture/principles/signed-events.md`) -- the invariant that every accepted event carries a valid id-hash and Schnorr signature. `buzz-core::verification::verify_event` is the single function that node's own body names as enforcing it.
- **`architecture-principles-host-selects-community`** (corpus node, `launchpad/docs/corpus/architecture/principles/host-selects-community.md`) -- the row-zero multi-tenant invariant. `buzz-core::tenant` supplies only the type-level fence (`CommunityId`, `TenantContext`, `normalize_host`); the resolution mechanism itself (`bind_community`) lives in `crates/buzz-relay/src/tenant.rs`, outside this crate. See *Divergences*.
- **NIP-01** (base Nostr protocol; no corpus node exists for it at this revision) -- event id/signature construction (delegated to the `nostr` crate, trusted as an external dependency and not itself opened for this node) and subscription filter semantics, adapted for Buzz in `buzz-core::filter`.
- **Buzz-custom NIPs with no corpus node yet**: NIP-AM (`crates/buzz-core/src/agent_turn_metric.rs`, `docs/nips/NIP-AM.md`), NIP-AE (`crates/buzz-core/src/engram.rs`, `docs/nips/NIP-AE.md`), NIP-AB (`crates/buzz-core/src/pairing/`, `crates/buzz-core/src/pairing/NIP-AB.md` and `.spthy`), and NIP-PMA (`crates/buzz-core/src/private_managed_agent.rs`, `docs/nips/NIP-PMA.md`). None of these spec documents carry a corpus node id at this revision, so no `implements` edge is declared toward them; they are named here by path per the template's own instruction not to invent an edge to a nonexistent id.
- **AGENTS.md's own "Event kinds" convention** ("All event kind integers are defined in `buzz-core/src/kind.rs`") -- a repository convention, not a formal spec, that `buzz-core::kind` mostly but not universally realizes. See *Divergences*.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `kind::KIND_*` (129 constants) + `is_ephemeral`/`is_replaceable`/`is_parameterized_replaceable`/`is_moderation_command_kind`/`is_shared_gated_kind`/`is_unshared_gated_event`/`event_is_shared`/`is_workflow_execution_kind` (`crates/buzz-core/src/kind.rs`) | AGENTS.md's event-kind registry convention | Two local shadow constants exist outside this file -- see *Divergences* |
| `verification::verify_event` (`crates/buzz-core/src/verification.rs`) | `architecture-principles-signed-events`'s id-hash + Schnorr-signature invariant | CPU-bound; callers must wrap in `spawn_blocking` per its own doc comment |
| `error::VerificationError` (`crates/buzz-core/src/error.rs`) | The two rejection variants (`InvalidId`, `InvalidSignature`) `verify_event` returns | Also carries a `Secp` variant for low-level secp256k1 errors |
| `event::StoredEvent` (`crates/buzz-core/src/event.rs`) | The relay's in-memory event wrapper (`received_at`, `channel_id`, `verified`) | `verified` is set but not read outside this module -- see *Divergences* |
| `filter::{filters_match, reader_authorized_for_event}` (`crates/buzz-core/src/filter.rs`) | NIP-01 filter matching plus the `#p`-tag private-content read gate for `KIND_DM_VISIBILITY`/`KIND_AGENT_TURN_METRIC` | Its own doc comment states it guards WS historical pull, HTTP bridge, and live fan-out |
| `tenant::{CommunityId, TenantContext, normalize_host, relay_url_authority}` (`crates/buzz-core/src/tenant.rs`) | The type-level half of `architecture-principles-host-selects-community`'s row-zero invariant | Resolution mechanism (`bind_community`) is not in this crate -- see *Divergences* |

**Not itemized above, present but not individually evidenced in this node:**
`agent_turn_metric` (NIP-AM), `channel`, `engram` (NIP-AE), `git_perms`, `invite`,
`network`, `nip10`, `observer`, `pairing` (NIP-AB), `presence`,
`private_managed_agent` (NIP-PMA), and `relay`. Each is a real, tested module (see
the doc-comment citations in the front-matter evidence ledger for the NIP-bearing
ones) but was not read deeply enough during this node's authoring to write an
evidenced row for it; a reader needing detail on any of these should open the
module directly rather than rely on an inference from this table.

## Divergences

- **Two local shadow constants duplicate `kind.rs`'s registry.** `crates/buzz-relay/src/handlers/push_lease.rs:21` declares its own `KIND_PUSH_LEASE: u32 = 30_350`, the same value already registered in `kind.rs:109`; two different files inside `buzz-relay` reference the two different definitions (`ingest.rs`/`side_effects.rs` use the local one, `req.rs` uses the canonical `buzz_core::kind` one). `crates/buzz-cli/src/commands/notes.rs:38` declares its own `KIND_LONG_FORM: u16 = 30023`, the same numeric value as `kind.rs`'s canonical `u32`, at a narrower integer width, even though the same file's sibling command modules import kind constants from `buzz_core::kind` directly. Both were found by grepping `crates/` for `pub const KIND_` outside `kind.rs` and confirming each site's actual usage, not by inference. Neither is large in surface area -- this is drift on two constants, not a systemic pattern -- but it means "all event kind integers are defined in `buzz-core/src/kind.rs`" is a convention with two known, verified exceptions rather than an enforced invariant.
- **`StoredEvent.verified` is set but not consulted.** The field defaults to `false` in `StoredEvent::new` and is set explicitly by `with_received_at` at various relay call sites, but a repository-wide grep for `.is_verified()` outside `event.rs` itself returns nothing. It does not gate any decision downstream at this revision. This was independently re-verified for this node (not merely taken from `architecture-principles-signed-events`, which reports the same finding).
- **`host-selects-community`'s realization is deliberately split, not drift.** `buzz-core::tenant` supplies `CommunityId` and `TenantContext` -- an opaque, review-fenced type that cannot be constructed from client input -- but the actual host-to-community resolution function (`bind_community`) lives in `crates/buzz-relay/src/tenant.rs`, a same-named file in a different crate that this node does not document. The `implements` edge this node declares toward `architecture-principles-host-selects-community` covers only the type-level fence; a reader wanting the resolution mechanism itself needs a (not-yet-written) `buzz-relay` implementation-reference node.
- **No divergence found, and checked, in the verification and filter surfaces.** `verify_event`'s two error variants, and `reader_authorized_for_event`'s two gated kinds, match what `architecture-principles-signed-events` and the corpus node text elsewhere in this repository already describe; nothing found while authoring this node contradicts them.

## Verification

**Unit-level, at this revision:** 262 `#[test]`-annotated functions across `buzz-core`'s
own `src/` tree (including `src/pairing/`), run via `cargo test -p buzz-core`. This
count was produced with `grep -rc '#[test]' crates/buzz-core/src/*.rs
crates/buzz-core/src/pairing/*.rs` and summed, not estimated. Representative examples
cited elsewhere in this node's evidence ledger: `verification::tests::rejects_tampered_id`
and `rejects_tampered_signature`; `tenant::tests::normalize_host_collapses_tenant_split_variants`
and five sibling `tenant::tests` cases; `filter::tests::reader_authorized_for_event_gates_dm_visibility_by_p`;
`invite::tests::v2_code_round_trip_is_canonical`.

**No integration or end-to-end suite exists for this crate specifically**, and none is
expected: `buzz-core` has no top-level `tests/` directory (confirmed via `find
crates/buzz-core -maxdepth 1 -type d`, which lists only `Cargo.toml` and `src`), and its
zero-I/O design means there is no live relay, database, or network behavior to exercise
end-to-end from within this crate alone. `crates/buzz-test-client` (a `buzz-core`
dependent) is where cross-crate, wire-level behavior involving `buzz-core` types is
exercised, but that is a different crate's node to document, not this one's.

## Relationships

- implements: `architecture-principles-signed-events` -- `verify_event` is the function that invariant's own corpus node names as its enforcement mechanism.
- implements: `architecture-principles-host-selects-community` -- `buzz-core::tenant` supplies the type-level fence that invariant's own corpus node already treats as part of "the implementation," jointly with `buzz-relay`'s resolution code (not documented by this node -- see *Divergences*).
- No `implements` edge toward `architecture-principles-nostr-first`, despite that node naming `buzz-core/src/kind.rs` as the location a new kind constant belongs: that principle governs a relay-level design *choice* (event-vs-HTTP-endpoint) that `buzz-core`'s kind registry merely supports infrastructure for. `buzz-core` does not decide, encode, or enforce that choice itself, so declaring `implements` here would overclaim.
- No `references` or `part-of` edges declared. No verification/test-strategy corpus node exists yet to `references`, and `buzz-core` is not a sub-component of any broader implementation-reference node that exists at this revision (it is the first node in `implementation/crates/`).

## Scope and omissions

**This node covers** what `buzz-core` is responsible for (kind registry, event
verification, filter matching, tenant/community types, several Buzz-custom NIP wire
codecs), its public entry points and dependents, representative tests, and two
verified divergences from the "single source of truth" framing AGENTS.md gives its
kind registry and this repository's own architecture-principle nodes give the
community-boundary invariant.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `agent_turn_metric`, `channel`, `engram`, `git_perms`, `invite`, `network`, `nip10`, `observer`, `pairing`, `presence`, `private_managed_agent`, `relay` module internals in evidenced detail | a future revision of this node, or their own dedicated corpus nodes if any is independently substantial enough |
| The `nostr` crate's own NIP-01 hash/Schnorr implementation `buzz-core` calls | out of scope; treated here as a trusted external dependency, per the same boundary `architecture-principles-signed-events` already draws |
| `bind_community`, the host-to-community resolution mechanism | `crates/buzz-relay/src/tenant.rs` -- a future `buzz-relay` implementation-reference node |
| The specification documents for NIP-AM, NIP-AE, NIP-AB, and NIP-PMA themselves | `docs/nips/*.md` and `crates/buzz-core/src/pairing/NIP-AB.md`; none carry a corpus node id yet |
| Whether any lint or CI check could catch a future local `KIND_` constant duplicating `kind.rs`'s registry | not designed here; the `INFERENCE` entry in this node's evidence ledger records that none was found, not that none should exist |

**Expected but not verified when this node was written:**

- **Whether `crates/buzz-conformance`'s formal model exercises any `buzz-core` type directly.** Its `Cargo.toml` mentions `buzz-core` only in a comment about a deliberate `CommunityId` API fence ("no Serde, no From&lt;Uuid&gt;"), but whether the conformance suite's own model code imports `buzz-core` types some other way (e.g. via a re-export) was not checked.
- **Whether `buzz-core`'s 262 unit tests currently pass.** `cargo test -p buzz-core` was not run for this node; the test count and representative names were established by reading source, not by executing the suite.
- **Whether any `.github/workflows/` job or `deny.toml`-style lint would catch a new local `KIND_` constant duplicating `buzz-core::kind`'s registry.** Not searched for; recorded as a gap in the `INFERENCE` entry above, not as a checked absence.
