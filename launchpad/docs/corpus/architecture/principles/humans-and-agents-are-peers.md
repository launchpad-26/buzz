---
id: architecture-principles-humans-and-agents-are-peers
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "VISION.md states the product intent directly: \"Humans and agents get the same thing\" -- a secp256k1 keypair, an optional NIP-05 handle, NIP-42 or NIP-98 Schnorr auth, and a Bot role on agent channel membership -- closing with \"where humans and agents are just colleagues.\""
    entry_class: FACT
    evidence:
      - "VISION.md"
  - statement: "Humans and agents are rows in the same `users` table (one schema, no separate agent table); an agent row is distinguished only by a nullable, self-referencing `agent_owner_pubkey` column (plus optional `agent_type`/`capabilities` columns), enforced with a foreign key back into `users` in the same community."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "Kind 0 (`KIND_PROFILE`), the standard NIP-01 profile event, is the one identity/profile event kind in the kind registry; no separate profile kind exists for agent identities."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "`required_scope_for_kind` maps kind 0 to `Scope::UsersWrite` unconditionally -- the function's match arms switch only on the event's `kind` and never inspect the author's identity or agent/human status."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`IngestAuth` is documented as \"transport-neutral\" and has exactly two variants, `Nip42` (WebSocket) and `Http` (NIP-98 or dev `X-Pubkey`), each carrying its own `scopes: Vec<Scope>` field of the identical `Scope` type; `IngestAuth::scopes()` and `IngestAuth::pubkey()` read that field through the same match arm for both variants, with no third variant or field keyed on agent/human identity."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`crates/buzz-acp` (the ACP agent harness) connects to the relay over NIP-01 WebSocket and authenticates via NIP-42 -- the same mechanism VISION.md documents for humans -- rather than being confined to the NIP-98 HTTP bridge; `buzz-ws-client`, the crate `crates/buzz-acp` uses for this, is documented as a NIP-42 WebSocket client shared across clients, not a human-only one."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/relay.rs"
  - statement: "`enforce_http_admission` reads a single configured `human_api_calls_per_min` value and applies it to whatever `pubkey` it is called with, with no branch that reads `agent_owner_pubkey` or otherwise distinguishes an agent-owned pubkey from any other; the field name does not correspond to a code-level human/agent branch."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "`author_type_label`, the one place in the ingest path that reads `users.agent_owner_pubkey` to distinguish \"agent\" from \"human\", is documented as \"Metric-labeling only -- never used for authorization\", and a lookup failure is defined to count as \"human\" specifically so the label cannot introduce a new ingest failure path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`MemberRole`'s doc comment states the channel-role hierarchy is `Owner > Admin > Member > Guest` and that \"Bot is a separate designation -- it is not part of the linear hierarchy\"; `permission_level()` returns 0 for `Bot` (documented as \"must use explicit grants\"), and `has_at_least` is documented as never satisfied by a `Bot` role for any non-Bot requirement, because it is a numeric comparison against that 0."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "The git pre-receive policy endpoint explicitly promotes `MemberRole::Bot` to `MemberRole::Member` for push-permission evaluation only, with the module doc comment stating \"Bot is a designation (what it is), not a permission tier (what it can do)\" and that \"the promotion is scoped to this module; the core `MemberRole::Bot` hierarchy is unchanged.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "`push:bot` is rejected as an invalid git branch-protection rule value specifically because \"Bot is promoted to Member at the policy layer,\" i.e. an agent's git-push permission is evaluated as whatever role it is promoted to, not as a distinct Bot permission tier."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs"
  - statement: "No automated test in this repository was found that asserts, as a standalone proposition, that a human-owned pubkey and an agent-owned pubkey (`agent_owner_pubkey` set) receive identical `Scope` grants or identical `required_scope_for_kind` results for the same event kind; existing coverage is indirect, through `Scope`/`MemberRole`/`git_perms` unit tests and ingest e2e tests that are not themselves partitioned by author type. This is expected-but-unverified coverage of the invariant as its own claim, not a claim that the underlying scope/role mechanisms are untested."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/scope.rs"
      - "crates/buzz-core/src/git_perms.rs"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
    confidence: 0.6
  - statement: "Issue #693's definition of done requires this node to state the invariant as one unambiguous property (MUST/MUST NOT where normative), explain its scope, name enforcement points and observable failure behavior, and link a verification/conformance mechanism or explicitly record that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#693 definition of done"
---

# Humans and agents are peers

## The invariant

Once a principal is authenticated, Buzz's relay-side authorization logic **MUST NOT**
branch on whether that principal is a human or an agent. An agent's identity
representation, the `Scope` grant it is issued, and the `Scope` a given event kind
requires (`required_scope_for_kind`) **MUST** be computed by exactly the same code
path, given the same inputs, as they would be for a human principal. Concretely: the
only signal that distinguishes an agent row from a human row anywhere in the schema is
a nullable `users.agent_owner_pubkey` column, and the authorization pipeline described
below never reads that column.

This is narrower than the plain-language framing in `VISION.md` ("humans and agents
get the same thing" / "just colleagues"), which is the product statement of intent.
This node documents the mechanism that intent maps to today, and — see *Where parity
does not (yet) hold*, below — one place where it explicitly does not, by design.

## Scope: what this covers and where it applies

This invariant governs three layers, all reachable from an authenticated Nostr event
or HTTP request:

1. **Identity representation.** A human and an agent are both a row in the single
   `users` table, keyed by `(community_id, pubkey)`. An agent row differs only by a
   populated `agent_owner_pubkey` (a self-referencing foreign key to another `users`
   row in the same community) and optional `agent_type`/`capabilities` columns. There
   is no separate agent table, and kind 0 (`KIND_PROFILE`, the standard NIP-01 profile
   event) is the one profile/identity event kind either principal type publishes.
2. **Authentication and the `Scope` it yields.** `IngestAuth` is the transport-neutral
   auth context the ingest pipeline operates on. It has exactly two variants —
   `Nip42` (WebSocket) and `Http` (NIP-98, or dev-mode `X-Pubkey`) — and both carry a
   `scopes: Vec<Scope>` field of the same `Scope` type, read through the same accessor.
   Which variant applies is a function of **transport**, not of principal type: the
   ACP agent harness (`crates/buzz-acp`) authenticates over WebSocket via NIP-42, the
   same mechanism a human desktop/web client uses — it is not confined to the NIP-98
   HTTP bridge. Per-principal HTTP admission (`enforce_http_admission`) is likewise
   applied to whatever pubkey it is called with, regardless of `agent_owner_pubkey`.
3. **Event-kind authorization.** `required_scope_for_kind` maps an event's `kind` to
   the `Scope` required to submit it. Its match arms switch on `kind` alone.

**What this invariant does not claim:** it is not a claim that every operation an
agent can perform a human can also perform (or the reverse) — it is a claim that
*where* the two are compared against the *same* required scope or role for the *same*
kind or operation, the comparison logic itself does not special-case which kind of
principal it is looking at.

## Enforcement points and observable failure behavior

- **`crates/buzz-relay/src/handlers/ingest.rs` — `IngestAuth` and
  `required_scope_for_kind`.** The primary enforcement point. A violation would look
  like a new `IngestAuth` variant, or a new match arm inside
  `required_scope_for_kind`, that reads `agent_owner_pubkey` (directly or via
  `get_agent_channel_policy`) to compute a *different* required or granted `Scope` for
  an otherwise-identical request. No such branch exists today.
- **`crates/buzz-relay/src/handlers/ingest.rs` — `author_type_label`.** The one place
  in the ingest path that *does* read `agent_owner_pubkey`. Its doc comment states
  this is "Metric-labeling only — never used for authorization," and a lookup error or
  unknown pubkey is defined to resolve to `"human"` rather than failing the request —
  a deliberate choice so this observability path cannot become a second, silent
  authorization branch. If a future change threaded this label's result back into an
  authorization decision, that would be an observable, reviewable violation of this
  invariant at this exact function.
- **`crates/buzz-relay/src/api/bridge.rs` — `enforce_http_admission`.** Applies the
  single configured `human_api_calls_per_min` quota to any authenticated pubkey passed
  to it. The name suggests a human-only quota; the code applies it uniformly. A
  reviewer relying on the name alone could misjudge this as agent-exempt — it is not.

**Observable failure behavior**, i.e. what the invariant would look like breaking:
- A request from an agent-owned pubkey receiving a `Scope` grant, or being able to
  satisfy `required_scope_for_kind` for a given kind, that a human-owned pubkey could
  not obtain for the identical auth transport and identical prior grants (or the
  reverse) — this would surface as a passing request that should have been a `403`
  (`IngestError::AuthFailed`) under the pre-existing scope model, or a rejected
  request that should have succeeded.
- `author_type_label`'s result changing ingest outcome (acceptance, `Scope`,
  admission) rather than only a `metrics::counter!` label.

## Where parity does not (yet) hold: the channel-role `Bot` designation

The invariant above governs identity, auth transport, and event-kind `Scope`
authorization. It does **not** extend unconditionally to **channel-role**
authorization, and this is a deliberate, named exception rather than a gap:

`MemberRole`'s hierarchy for permission checks is `Owner > Admin > Member > Guest`.
`Bot` — the role assigned to an agent added to a channel — is documented as "a
separate designation... not part of the linear hierarchy." `permission_level()`
returns `0` for `Bot`, and `has_at_least` (`self.permission_level() >=
required.permission_level()`) therefore **MUST NOT** be satisfied by a `Bot` role for
any non-`Bot` requirement — an agent in the default `Bot` role cannot pass an
`Owner`/`Admin`/`Member`-gated check by virtue of channel membership alone.

One narrow, explicit exception exists: the git pre-receive policy endpoint
(`crates/buzz-relay/src/api/git/policy.rs`) promotes `Bot` to `Member` when evaluating
git push permission, so an agent's push is checked against the same branch-protection
rules a `Member`'s push would be, "protection rules still apply." The module's own doc
comment names the principle this node borrows its title from at the boundary of its
own scope: **"Bot is a designation (what it is), not a permission tier (what it can
do)."** The promotion is scoped to that one module — the core `MemberRole::Bot`
hierarchy elsewhere is unchanged — and `push:bot` is deliberately rejected as an
invalid branch-protection rule value, because bot push permission is derived from the
promotion, not from a distinct Bot tier.

## Verification / conformance

There is **no dedicated automated test** in this repository that asserts the
peer-parity invariant as its own standalone proposition (e.g. "given the same
transport and the same prior grants, a human-owned pubkey and an agent-owned pubkey
receive the same `Scope` for the same kind"). This is recorded here explicitly per
this node's own "expected but not verified" evidence entry, rather than implied by
omission.

What exists instead is **verification by code reading of a single shared code path**,
backed by test coverage of the underlying mechanisms individually:
- `crates/buzz-auth/src/scope.rs`'s unit tests (`all_known_returns_all_known_variants`,
  `all_non_admin_excludes_admin_scopes`, `round_trip`) verify `Scope`'s own behavior,
  not that it is applied identically across principal types.
- `crates/buzz-core/src/git_perms.rs`'s tests exercise `MemberRole` push-permission
  evaluation, including a `MemberRole::Bot` case.
- `crates/buzz-test-client/tests/e2e_relay.rs` exercises the shared `ingest_event`
  pipeline end-to-end, but its cases are not partitioned by `agent_owner_pubkey`.

Because there is one `IngestAuth` type and one `required_scope_for_kind` function
regardless of caller, these tests exercising "the" pipeline is itself indirect
evidence for the invariant — but it is evidence by construction (one function, one
code path) rather than evidence by a test that would fail if the invariant were
violated by a future change adding an agent-specific branch.

## Scope and omissions

**This node covers** the identity/auth/event-kind-authorization parity between human
and agent principals, and the one named channel-role exception (`Bot`).

**It does not cover, and these are boundaries, not gaps:**
- The full `required_scope_for_kind` mapping for every event kind — see
  `crates/buzz-relay/src/handlers/ingest.rs` directly; this node establishes that the
  mapping does not branch on principal type, not what every kind maps to.
- The HTTP event-submission request/response lifecycle in general (tenant binding,
  NIP-98 replay protection, admission ordering) — see
  `architecture-flows-http-event-submission`.
- UI-level distinctions such as the "visual badges" VISION.md's Identity section notes
  as planned but not yet built — those are presentational, not authorization.
- Whether other admission/quota configuration besides `human_api_calls_per_min`
  differs by principal type; only that one call site was inspected.
- Any other, not-yet-discovered code path that might read `agent_owner_pubkey` for an
  authorization decision. This node names the enforcement points inspected; it is not
  a repository-wide static-analysis guarantee that no such path exists.

**Expected but not verified against the current repository:** no dedicated automated
test asserting the peer-parity invariant as its own proposition — see *Verification /
conformance* above.
