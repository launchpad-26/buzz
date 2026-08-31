---
id: layers-identity-actor
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
  - statement: "docs/spec/MultiTenantRelay.tla declares `Actors` as a formal CONSTANT, commented \"finite set of pubkeys/actors\" (line 99), and uses that same set as the type of both `actor` fields on request-scoped records (e.g. line 243) and `author` fields on persisted-message records (e.g. line 200) -- the spec's own vocabulary treats \"actor\" and \"author\" as two field names drawing from one domain, not two different kinds of identity."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla"
  - statement: "crates/buzz-conformance/src/lib.rs defines `ActorLabel` -- an opaque, hash-derived newtype -- and gives `AbstractState` an `actor: ActorLabel` field documented as \"The actor (authenticated pubkey) for this request, opaque-labelled.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs"
  - statement: "crates/buzz-relay/src/conformance/mod.rs's `state_for_request` builds that `ActorLabel` from a `nostr::PublicKey` argument literally named `actor`, and its `actor_label` helper documents the label as \"the lower 16 bytes of blake3(pubkey_bytes)\" -- the relay derives \"actor\" directly from the same Schnorr pubkey type Nostr events are signed with, not from a separate session or identity object."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs"
  - statement: "Outside the conformance/spec layer, crates/buzz-db/src/store/user.rs's `is_agent_owner` names its caller-identity parameter `actor_pubkey` (distinct from `target_pubkey`), and crates/buzz-db/src/store/archived_identities.rs's `ArchivedIdentity.actor` field is documented as \"64-char lowercase hex pubkey of the actor that requested the archive\" -- both are ordinary production data-access code, showing the term is used consistently beyond the formal-verification harness."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/user.rs"
      - "crates/buzz-db/src/store/archived_identities.rs"
  - statement: "crates/buzz-relay/src/handlers/moderation_commands.rs derives its `actor` variable directly from the incoming Nostr event (`let actor = event.pubkey.to_bytes().to_vec();`) and threads that same value through every moderation command dispatched from `handle_moderation_command` (ban, unban, timeout, untimeout, resolve-report) as the identity performing the action, with no branch on whether that pubkey belongs to a human- or agent-owned `users` row."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "migrations/0001_initial_schema.sql's `users` table stores exactly one row per `(community_id, pubkey)` for both human and agent identities, distinguished only by a nullable, self-referencing `agent_owner_pubkey` column; no separate `actors` table, and no `Actor` row type, exists anywhere in the schema."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "VISION.md, Buzz's product-facing vision document, contains no occurrence of the word \"actor\" -- at the recorded revision the term belongs to the specification and implementation layers, not to Buzz's product vocabulary (which instead speaks of \"humans and agents\")."
    entry_class: FACT
    evidence:
      - "VISION.md"
  - statement: "\"Actor\" is a cross-cutting naming convention for \"the authenticated pubkey performing a request or action,\" not a distinct Rust type or trait: across the files inspected for this node, `ActorLabel` (an opaque, hashed, observability-only wrapper local to the conformance harness) is the only place \"Actor\" appears as an actual Rust type identifier; every other occurrence is a bare `PublicKey`/`Vec<u8>`/`String` parameter or field simply named `actor` or `actor_pubkey`."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-conformance/src/lib.rs"
      - "crates/buzz-relay/src/conformance/mod.rs"
      - "crates/buzz-db/src/store/user.rs"
      - "crates/buzz-db/src/store/archived_identities.rs"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
    confidence: 0.85
  - statement: "Issue #1102's definition of done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals, link related concepts, implementation and verification without duplicating their content, and use examples only to clarify the concept rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1102 definition of done"
relationships:
  - type: references
    target: architecture-principles-humans-and-agents-are-peers
---

# Actor

Buzz code and its formal specification both need a word for "whoever is making
this request or performing this action" that does not presuppose human or
agent — that word is **actor**. This node is that concept's canonical
definition: what the term means, where it is used, and how it differs from
the neighboring terms ("author", "principal", "user") it is easy to confuse
it with.

## Definition

An **actor** is the single authenticated pubkey performing a request or
action in Buzz — whether that pubkey belongs to a human identity or an agent
identity. It is not a distinct record type: an actor *is* a pubkey, and
looking one up in the `users` table (keyed by `(community_id, pubkey)`)
returns the same row shape regardless of whether `agent_owner_pubkey` is
set. Buzz's formal TLA+ specification (`docs/spec/MultiTenantRelay.tla`)
makes this explicit at the model level, declaring `Actors` as "finite set of
pubkeys/actors" and typing both request-scoped `actor` fields and
persisted-message `author` fields against that one set. The relay's runtime
conformance harness mirrors the same idea concretely: `AbstractState.actor`
is documented as "the actor (authenticated pubkey) for this request,"
constructed straight from the `nostr::PublicKey` that authenticated the
connection.

**What "actor" is not.** It is not a Rust type or trait in production code —
searching the crates cited in this node's evidence turns up exactly one
place the word appears as an actual type identifier, `ActorLabel`, and that
is a narrow, opaque, hash-derived wrapper local to the conformance
observability harness, not a general-purpose identity type. Everywhere else
"actor" is a parameter or field name (`actor`, `actor_pubkey`) attached to a
plain `PublicKey`, `Vec<u8>`, or hex `String`. It is also not synonymous with
a full identity/profile record: `UserProfile` (display name, avatar, about,
NIP-05 handle) describes *who someone presents as*; "actor" describes *who
is doing this, right now, for authorization and audit purposes*. And it is
not itself product-facing vocabulary — `VISION.md` never uses the word,
describing the same idea instead as "humans and agents."

## Background

This term exists because Buzz deliberately does not want its authorization
and audit code to care whether a pubkey is a human's or an agent's — see
`architecture-principles-humans-and-agents-are-peers`, the corpus node
documenting that invariant directly. "Actor" is the vocabulary that
invariant's own code uses to talk about "the principal" generically: a
moderation handler, an archive request, or a conformance trace all need to
name *who* did something without first asking *what kind of who*. Using one
word for that, backed by one column (`pubkey`) and one optional discriminator
(`agent_owner_pubkey`), is what makes the peer-parity invariant mechanically
enforceable rather than merely aspirational.

## Use cases

A reader reaches for "actor" when they need to:

- **Trace an authorization decision.** `buzz-conformance`'s
  `AbstractState.actor` and `TraceAction::AuthCheck` record which actor a
  per-(channel, actor) authorization verdict was computed for, so the
  conformance checker can verify `Inv_NonInterference` against Buzz's TLA+
  model without ever seeing a raw pubkey.
- **Attribute a moderation action.** Every handler in
  `crates/buzz-relay/src/handlers/moderation_commands.rs` (ban, unban,
  timeout, untimeout, resolve-report) records the acting pubkey as `actor` in
  its audit-log call, independent of whether that pubkey is human- or
  agent-owned.
- **Record who requested an identity archive.** `ArchivedIdentity.actor`
  captures the pubkey that authorized an archive (via the `"self"`,
  `"owner"`, or `"admin"` consent path), distinct from `pubkey`, the identity
  being archived.
- **Check an agent-ownership relationship.** `is_agent_owner`'s
  `actor_pubkey` parameter is the pubkey being tested for ownership of a
  target agent pubkey — "actor" here is the candidate owner, again with no
  human/agent distinction baked into the function's own logic.

## Comparison

| Term | What it names | Where it lives |
|---|---|---|
| **actor** | The authenticated pubkey performing a request or action, human or agent, undifferentiated | `docs/spec/MultiTenantRelay.tla`'s `Actors`; `AbstractState.actor`; `actor`/`actor_pubkey` parameters across `buzz-db` and `buzz-relay` |
| **author** | The pubkey that signed a *persisted* Nostr event | `docs/spec/MultiTenantRelay.tla`'s message records (`author: Actors`) — the same underlying domain as `actor`, named differently because the record is a stored message, not a live request |
| **principal** | Prose synonym for the same idea, used narratively | `architecture-principles-humans-and-agents-are-peers`'s body text (e.g. "Once a principal is authenticated..."); not a field or type name anywhere inspected |
| **user / `UserProfile`** | The broader identity/profile record (display name, avatar, about, NIP-05 handle) that a `(community_id, pubkey)` row carries | `users` table; `crates/buzz-db/src/store/user.rs`'s `get_user`/`UserProfile` |
| **`agent_owner_pubkey` / owner** | A *relationship* between two actors — which human- or agent-owned pubkey administratively owns a given agent pubkey — not a synonym for "actor" itself | `users.agent_owner_pubkey`; `set_agent_owner`/`is_agent_owner` |

## Related resources

See the `references` relationship in this node's front matter, pointing at
`architecture-principles-humans-and-agents-are-peers` — the node documenting
the invariant that makes "one undifferentiated actor concept" a deliberate
design choice rather than an accident of naming.

## Scope and omissions

**This node covers** what "actor" means in Buzz's specification and code,
why the term exists undifferentiated by human/agent, its representative use
cases, and how it differs from the neighboring terms ("author", "principal",
"user profile", "owner") a reader is likely to conflate it with.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How an agent identity specifically is represented and provisioned | #1103 (`task: document layers/identity/agent-identity.md`), not yet drafted |
| How a human identity specifically is represented and provisioned | #1106 (`task: document layers/identity/human-identity.md`), not yet drafted |
| Keypair generation, and public/private key mechanics | #1111/#1112/#1113 (`keypair.md`/`private-key.md`/`public-key.md`), not yet drafted |
| The full `required_scope_for_kind` authorization mapping | `crates/buzz-relay/src/handlers/ingest.rs` directly, and `architecture-principles-humans-and-agents-are-peers` |
| Community/relay identity scoping (`community_id` as part of the actor's addressing) | #1104 (`task: document layers/identity/community-identity.md`), not yet drafted |

**Expected but not verified when this node was written:**

- **Not every `actor`/`actor_pubkey` call site in the repository was
  inspected.** The evidence above is a representative, individually-opened
  sample spanning the formal spec, the conformance harness, moderation
  handling, and archived-identity handling — not an exhaustive audit of
  every occurrence.
- **Only Rust source under `crates/` and the TLA+ spec were searched.**
  Desktop (TypeScript/React), mobile (Dart), and web client code were not
  checked for actor-adjacent terminology; if a client-side concept with the
  same name exists and diverges from this definition, it was not found by
  this pass.
