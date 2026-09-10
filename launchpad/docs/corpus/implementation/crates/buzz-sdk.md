---
id: implementation-crates-buzz-sdk
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "crates/buzz-sdk/Cargo.toml declares the package description \"Typed Nostr event builders for Buzz operations\" and depends on buzz-core, nostr, uuid, serde, serde_json, and thiserror — no network or storage crates."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/Cargo.toml"
  - statement: "crates/buzz-sdk/src/lib.rs's crate doc states the mental model as \"caller params -> builder fn -> validates -> EventBuilder -> caller signs -> Event\", and says explicitly that no keys are held and no network calls are made; the crate declares four public modules (broker, builders, mentions, nip_oa) and re-exports buzz_core::kind plus buzz_core::channel::{canonical_channel_name, ChannelType, ChannelVisibility, MemberRole} so consumers don't need to depend on buzz-core directly for those items."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs"
  - statement: "crates/buzz-sdk/src/builders.rs's module doc states it holds \"Typed event builder functions (38 builders)\", all returning Result<nostr::EventBuilder, SdkError>; grep of `^pub fn` confirms the count, spanning messages/reactions/channels/profiles/git objects (repo announcement, patch, issue, status, pull request, PR update)/workflows/DMs/presence/moderation/identity-archive/project events; its own #[cfg(test)] mod tests contains 189 #[test] functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "crates/buzz-sdk/src/mentions.rs implements @-name and NIP-27 nostr:npub… mention resolution as pure functions with no network calls, documents its own extract -> match -> merge -> normalize pipeline, defines MENTION_CAP = 50 as the hard cap on mention p-tags, and its #[cfg(test)] mod tests contains 51 #[test] functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/mentions.rs"
  - statement: "crates/buzz-sdk/src/nip_oa.rs implements NIP-OA owner-attestation auth tags — compute_auth_tag, verify_auth_tag, parse_auth_tag — and its own module doc states the tag format [\"auth\", owner-pubkey-hex, conditions, sig-hex] and signing preimage \"nostr:agent-auth:\" || agent_pubkey_hex || \":\" || conditions, hashed with SHA-256 and signed with BIP-340 Schnorr; its #[cfg(test)] mod tests contains 22 #[test] functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs"
  - statement: "docs/nips/NIP-OA.md defines the same auth tag shape independently: exactly four elements [\"auth\", \"<owner-pubkey-hex>\", \"<conditions>\", \"<sig-hex>\"], the same signing preimage \"nostr:agent-auth:\" || event.pubkey || \":\" || <conditions>, SHA256 of that preimage as the signed message, and a BIP-340 Schnorr signature by the owner's secret key — matching nip_oa.rs's implementation field-for-field where compared."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md"
      - "crates/buzz-sdk/src/nip_oa.rs"
  - statement: "crates/buzz-sdk/src/broker/mod.rs's module doc describes the broker submodule as \"a contract only: the request envelope, the closed set of Actions, the result shape, the HTTP binding, and a client trait\" for an agent-to-host operation broker, states \"the full design rationale lives in the English spec (docs/agent-broker.md)\", and states BROKER_PROTOCOL_VERSION = 1 with the comment \"the protocol is unshipped\"; its Action enum (crates/buzz-sdk/src/broker/actions/mod.rs) has exactly nine variants: ChannelRead, MessagePost, MessageReply, ReactionAdd, ProfileSet, StorageAddress, AgentsCreate, AgentsUpdate, AgentsDelete."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/broker/mod.rs"
      - "crates/buzz-sdk/src/broker/actions/mod.rs"
  - statement: "docs/agent-broker.md, the English spec crates/buzz-sdk/src/broker/mod.rs's own doc comment names as the source of the broker contract's design rationale, does not exist anywhere in this repository — a repository-wide filename search for '*agent-broker*' returns no matches."
    entry_class: FACT
    evidence:
      - "find(pattern='*agent-broker*', root='.') -> no matches"
  - statement: "No crate under crates/ other than buzz-sdk itself references buzz_sdk::broker at this revision — a recursive grep for 'buzz_sdk::broker' across every crate's src/ and tests/, excluding crates/buzz-sdk/, returns no matches — so the broker module is unshipped by its own doc comment and has zero external consumers in this repository today."
    entry_class: FACT
    evidence:
      - "grep(pattern='buzz_sdk::broker', path='crates/*/src;crates/*/tests', exclude='crates/buzz-sdk/**') -> no matches"
  - statement: "crates/buzz-sdk/src/broker/tests.rs contains 39 #[test] functions covering the broker request/response validation, correlation, and wire-strictness rules described in broker/mod.rs's doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/broker/tests.rs"
  - statement: "A repository-wide grep of every crate's Cargo.toml for the string \"buzz-sdk\" finds it declared as a dependency in crates/buzz-cli/Cargo.toml, crates/buzz-acp/Cargo.toml, crates/buzz-relay/Cargo.toml, and crates/buzz-test-client/Cargo.toml, in addition to buzz-sdk's own manifest."
    entry_class: FACT
    evidence:
      - "grep(pattern='buzz-sdk', path='crates/*/Cargo.toml') -> crates/buzz-sdk/Cargo.toml, crates/buzz-cli/Cargo.toml, crates/buzz-acp/Cargo.toml, crates/buzz-test-client/Cargo.toml, crates/buzz-relay/Cargo.toml"
  - statement: "crates/buzz-relay/src/handlers/auth.rs, crates/buzz-relay/src/api/mod.rs, crates/buzz-relay/src/handlers/identity_archive.rs, and crates/buzz-relay/src/api/git/transport.rs call buzz_sdk::nip_oa::verify_auth_tag or buzz_sdk::nip_oa::compute_auth_tag directly, and crates/buzz-relay/src/handlers/ingest.rs calls buzz_sdk::normalize_custom_emoji_shortcode — buzz-relay consumes the crate's NIP-OA and builder-adjacent helpers, not its broker module."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/api/mod.rs"
      - "crates/buzz-relay/src/handlers/identity_archive.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "crates/buzz-relay/src/workflow_sink.rs contains code comments stating it independently reimplements thread-tagging logic to match buzz_sdk::builders::thread_tags's behavior (\"matching buzz_sdk::builders::thread_tags\"), but thread_tags itself is a private (non-pub) function in crates/buzz-sdk/src/builders.rs, so this is parity-by-comment against private SDK behavior, not an actual dependency edge — buzz-relay cannot and does not call it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/workflow_sink.rs"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "crates/buzz-acp/src/lib.rs, crates/buzz-acp/src/pool.rs, crates/buzz-acp/src/relay.rs, and crates/buzz-acp/src/setup_mode.rs call buzz_sdk::nip_oa::verify_auth_tag, buzz_sdk::build_reaction, buzz_sdk::build_agent_observer_frame, and buzz_sdk::nip_oa::parse_auth_tag respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs"
      - "crates/buzz-acp/src/pool.rs"
      - "crates/buzz-acp/src/relay.rs"
      - "crates/buzz-acp/src/setup_mode.rs"
  - statement: "crates/buzz-cli/src/agent_management.rs and crates/buzz-cli/src/commands/{agents,channels,dms,emoji,issues,messages,moderation}.rs call or import buzz_sdk builder functions and types (build_agent_observer_frame, the builders module, Visibility, kind::KIND_DM_HIDE, CustomEmoji, GitIssueMeta/GitRepoCoord/GitStatusMeta, DeleteMessageOptions/DiffMeta/ThreadRef/VoteDirection, build_moderation_ban), so buzz-cli is the widest consumer of the typed-builder surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/agent_management.rs"
      - "crates/buzz-cli/src/commands/agents.rs"
      - "crates/buzz-cli/src/commands/channels.rs"
      - "crates/buzz-cli/src/commands/dms.rs"
      - "crates/buzz-cli/src/commands/emoji.rs"
      - "crates/buzz-cli/src/commands/issues.rs"
      - "crates/buzz-cli/src/commands/messages.rs"
      - "crates/buzz-cli/src/commands/moderation.rs"
  - statement: "crates/buzz-test-client/tests/e2e_project.rs and crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs reference buzz_sdk::, so buzz-test-client's use of the crate is confined to its integration-test suite rather than production code."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_project.rs"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs"
  - statement: "crates/buzz-sdk has no README.md and no tests/ integration-test directory at this revision; every test lives in inline #[cfg(test)] mod tests blocks (builders.rs, mentions.rs, nip_oa.rs, broker/tests.rs) plus one runnable example, crates/buzz-sdk/examples/compute_auth_tag.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/examples/compute_auth_tag.rs"
  - statement: "AGENTS.md's crate table describes buzz-core as \"Core types, event verification, filter matching, kind registry\" and buzz-sdk as \"Typed Nostr event builders\" — two adjacent, distinct roles; crates/buzz-core/src/kind.rs's own module doc states \"This module is the authoritative source for Buzz kind numbers\", and buzz-sdk/src/lib.rs re-exports it (`pub use buzz_core::kind`) rather than redefining kind constants or owning the registry itself."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-sdk/src/lib.rs"
  - statement: "buzz-sdk performs no general Nostr event signature verification: nip_oa.rs's verify_auth_tag checks only the NIP-OA auth-tag's own embedded Schnorr signature over its own preimage, a narrower, unrelated check from the event-id/signature verification architecture-principles-signed-events.md documents for crates/buzz-core/src/verification.rs's verify_event, which buzz-sdk does not call and does not re-export."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs"
      - "launchpad/docs/corpus/architecture/principles/signed-events.md"
  - statement: "launchpad/docs/corpus/architecture/principles/nostr-first.md's own Scope section states it \"applies to design and code-review decisions made when adding new backend capability to buzz-relay\" and does not apply to client-side libraries; buzz-sdk is a client-side builder crate consumed by buzz-cli, buzz-acp, and buzz-relay's own handlers, not buzz-relay's route/kind-handler decision itself, so this node does not declare an implements edge toward it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/nostr-first.md"
  - statement: "At this revision, git ls-tree of origin/launchpad's launchpad/docs/corpus tree contains no node under implementation/ — this is the first node in that subtree — and the only two architecture-typed nodes present (architecture-principles-nostr-first, architecture-principles-signed-events) are both scoped to buzz-relay-side behavior rather than to buzz-sdk, so no valid implements/part-of target exists yet for this node to declare."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> no implementation/** entries; architecture/principles/{nostr-first,signed-events}.md present"
---

# buzz-sdk: implementation reference

This node documents `crates/buzz-sdk`, the crate AGENTS.md's own crate table names "Typed
Nostr event builders" and whose `Cargo.toml` description matches verbatim ("Typed Nostr
event builders for Buzz operations"). It claims to realize two independently checkable
targets: NIP-OA (`docs/nips/NIP-OA.md`, owner-attestation `auth` tags) via its `nip_oa`
module, and Buzz's own house convention — codified in `AGENTS.md`'s "Prefer Nostr events
over new HTTP endpoints" guidance — that new operations are modeled as typed, signable
Nostr events rather than bespoke request/response structs, realized by the 38 builder
functions in `builders.rs`. It additionally carries a `broker` submodule that is a
self-described wire *contract* for a not-yet-shipped agent↔host protocol, whose own claimed
target (`docs/agent-broker.md`) does not exist in this repository — see *Divergences*.

## Target

Two named targets, of different kinds:

1. **NIP-OA** — `docs/nips/NIP-OA.md`, a repository-local NIP specification file (not yet a
   corpus node). Defines the `auth` tag's four-element shape, signing preimage, and
   condition-clause grammar.
2. **The "model operations as Nostr events" house convention** — stated in this
   repository's own `AGENTS.md` ("Prefer Nostr events over new HTTP endpoints" and "New
   agent-facing operations go in `buzz-cli`... then wire the REST/WebSocket call in
   `client.rs`"), not a formal spec document. `buzz-sdk`'s builder functions are the layer
   that turns validated parameters into an unsigned `nostr::EventBuilder`, the shape every
   caller (`buzz-cli`, `buzz-acp`, `buzz-relay`) then signs or forwards.

A third candidate target, `docs/agent-broker.md` (cited by `broker/mod.rs`'s own doc
comment as "the English spec" for the broker contract), does not exist anywhere in this
repository at this revision — checked by a repository-wide filename search. This is
recorded under *Divergences* rather than treated as a valid target.

None of the three targets above has a corpus node id yet, so this node declares no
`implements` edge toward any of them, per the template's instruction not to invent an edge
to a nonexistent id — see *Relationships*.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `src/nip_oa.rs`: `compute_auth_tag`, `verify_auth_tag`, `parse_auth_tag` | NIP-OA `auth` tag: four-element shape, `"nostr:agent-auth:"` preimage, BIP-340 Schnorr over SHA-256 | Field-for-field match confirmed against `docs/nips/NIP-OA.md`; 22 inline tests |
| `src/builders.rs`: 38 `build_*` functions (messages, reactions, channels, profiles, git objects, workflows, DMs, presence, moderation, identity-archive, project events) | The "operations as typed Nostr events" convention — validated params → `nostr::EventBuilder`, caller signs | 189 inline tests; consumed directly by `buzz-cli` and `buzz-acp` |
| `src/mentions.rs`: `extract_at_names`, `extract_at_mentions_with_known`, `match_names_to_profiles`, `merge_mentions`, `normalize_mention_pubkeys`, `strip_code_regions`, `extract_nostr_uris` | `@name` and NIP-27 `nostr:npub1…` mention resolution, pure functions feeding `p`-tag construction in the message builders above | 51 inline tests; `MENTION_CAP = 50` |
| `src/lib.rs`: `pub use buzz_core::kind;`, `pub use buzz_core::channel::{canonical_channel_name, ChannelType, ChannelVisibility, MemberRole}` | Re-export only — explicitly *not* an implementation surface owned by this crate; see *Divergences*/*Scope* for the boundary against `buzz-core` | No logic here, just visibility |
| `src/broker/{mod,actions/*,client,wire,correlate}.rs` | A self-contained agent↔host action-broker wire contract (envelope, closed `Action` set, HTTP binding, client trait) — its own doc comment states it targets `docs/agent-broker.md`, not NIP-OA or the house convention above | 39 inline tests in `broker/tests.rs`; zero consumers anywhere else in `crates/` at this revision — see *Divergences* |
| `examples/compute_auth_tag.rs` | A runnable CLI demonstrating `nip_oa::compute_auth_tag` | `cargo run --example compute_auth_tag` |

## Divergences

- **`docs/agent-broker.md` does not exist.** `broker/mod.rs`'s own doc comment names it as
  "the English spec" for the broker contract's design rationale, and a repository-wide
  filename search finds no file by that name anywhere in this repository. Either the spec
  was never committed, was written and later removed, or lives outside this repository —
  none of these was distinguished; the fact checked is only that the cited path is absent
  from `HEAD`. Until it exists (or the comment is corrected), the broker module's design
  rationale is unverifiable against any target, only against its own doc comments.
- **The broker contract is unshipped, with zero consumers.** `BROKER_PROTOCOL_VERSION`'s own
  comment states "the protocol is unshipped," and this was independently confirmed: no
  crate under `crates/` other than `buzz-sdk` itself references `buzz_sdk::broker`. This is
  not a defect — the module's own doc comment frames it as a contract published ahead of any
  host or transport implementation — but it means the *Implementation surface* row above
  documents a contract with no realized caller yet, unlike the `nip_oa` and `builders` rows,
  which have multiple live callers today.
- **No divergence found between `nip_oa.rs` and NIP-OA's tag shape, preimage, or signing
  scheme**, checked directly by reading both side by side (see the evidence ledger). This
  is a compliance finding, not silence: the comparison was made, not skipped.
- **`thread_tags` is independently reimplemented, not shared.** `buzz-relay`'s
  `workflow_sink.rs` carries comments stating its own thread-tagging logic is written to
  match `buzz_sdk::builders::thread_tags`'s behavior, but that function is private
  (non-`pub`) in `buzz-sdk`. The two implementations are maintained in parallel by
  convention, not by a shared dependency — a latent drift risk this node surfaces but does
  not resolve.

## Verification

**Automated, today:** `cargo test -p buzz-sdk` runs the crate's roughly 300 inline unit
tests (189 in `builders.rs`, 51 in `mentions.rs`, 22 in `nip_oa.rs`, 39 in
`broker/tests.rs`), all `#[cfg(test)] mod tests` blocks colocated with the code they cover —
there is no separate `tests/` integration directory and no crate-level `README.md`. `just
ci` (per this repository's own `AGENTS.md`) runs workspace-wide `cargo test` as part of the
required pre-PR gate, so this crate's tests run on every PR that touches it.

**Not found at this revision:** no end-to-end or integration test was found that exercises
a `buzz-sdk` builder's output through an actual signed submission to `buzz-relay` and back —
coverage here is at the builder-function/unit level (does the function produce the expected
tags/kind/content, does validation reject bad input), not at the wire-round-trip level. This
gap was checked by inspecting `crates/buzz-sdk` itself for a `tests/` directory (absent) and
was not separately checked against `buzz-test-client`'s own E2E suite, which is out of scope
for this node — see *Scope and omissions*.

## Relationships

**Declared: none.** Checked, not assumed: at this revision no node exists under
`launchpad/docs/corpus/implementation/` for this to sit `part-of`, and the two
`architecture`-typed nodes that exist (`architecture-principles-nostr-first`,
`architecture-principles-signed-events`) both scope themselves explicitly to `buzz-relay`
behavior in their own Scope sections — `buzz-sdk` is a client-side library the relay
consumes narrowly (NIP-OA verification, emoji normalization), not the relay itself, so an
`implements` edge to either would misstate what those nodes govern. `docs/nips/NIP-OA.md`
and the house event-modeling convention in `AGENTS.md` are the real targets (see *Target*),
but neither has a corpus node id yet. The first NIP-OA-focused or event-modeling-convention
corpus node to merge is the natural moment to add an `implements` edge back here.

## Scope and omissions

**This node covers** what `crates/buzz-sdk` is responsible for (typed, validated Nostr
event builders for Buzz operations, NIP-OA auth-tag computation/verification, mention
resolution, and a separate unshipped agent-broker wire contract), its public
interfaces/entry points, its dependency on `buzz-core` for kind constants and channel types
without owning either, which crates consume which parts of its surface, and its test
coverage as it exists today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The kind number registry itself (what each `KIND_*` constant means, which events exist) | `buzz-core/src/kind.rs`; no corpus node yet |
| General Nostr event id/signature verification (`verify_event`) | `launchpad/docs/corpus/architecture/principles/signed-events.md` (relay-side; distinct from NIP-OA's narrower `auth`-tag check) |
| The relay-side decision to model new operations as events rather than HTTP endpoints | `launchpad/docs/corpus/architecture/principles/nostr-first.md` (scoped to `buzz-relay`, not this crate) |
| NIP-OA's full specification (motivation, non-goals, verifier obligations beyond what `nip_oa.rs` implements) | `docs/nips/NIP-OA.md` |
| The broker contract's design rationale in full | `docs/agent-broker.md` — does not exist; see *Divergences* |
| `buzz-test-client`'s own E2E test suite and whether it exercises `buzz-sdk` output end-to-end | Not opened for this node; `crates/buzz-test-client/tests/` |

**Expected but not verified when this node was written:**

- Whether `docs/agent-broker.md` was ever committed and later deleted, or never existed, was
  not distinguished — only its absence at `HEAD` was checked (via a filesystem search, not
  `git log --diff-filter=D`).
- Whether any `buzz-relay` handler is planned to become the broker contract's host
  implementation was not checked; the broker module's zero-consumer status is reported as a
  fact about this revision, not a prediction about its future.
- Whether `buzz-test-client`'s E2E suite exercises any `buzz-sdk` builder output through a
  real relay round-trip was not checked — only that two of its test files reference
  `buzz_sdk::` at all.
