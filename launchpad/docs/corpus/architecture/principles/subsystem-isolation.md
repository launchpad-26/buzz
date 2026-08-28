---
id: architecture-principles-subsystem-isolation
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
  - statement: "ARCHITECTURE.md documents buzz-relay as the single source of truth that imports and directly orchestrates buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit, and buzz-workflow, and states that those subsystems are isolated from each other, coordinating only through the relay."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:97"
  - statement: "ARCHITECTURE.md separately describes buzz-relay as 'the only crate that imports and orchestrates all subsystems.'"
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:576"
  - statement: "ARCHITECTURE.md's crate dependency hierarchy diagram places buzz-core, described there as zero-I/O (types, verification, filter matching, kind registry), as the common root that buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit, buzz-workflow, and buzz-relay itself all depend on."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:75-95"
      - "ARCHITECTURE.md:78"
  - statement: "buzz-db's Cargo.toml declares dependencies only on buzz-core and buzz-datastore-tracing."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/Cargo.toml:11-12"
  - statement: "buzz-auth's Cargo.toml declares a buzz-* dependency only on buzz-core."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/Cargo.toml:15"
  - statement: "buzz-search's Cargo.toml declares dependencies only on buzz-core and buzz-datastore-tracing, matching ARCHITECTURE.md's own example that buzz-search never calls buzz-db."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/Cargo.toml:11-12"
  - statement: "buzz-audit's Cargo.toml declares dependencies only on buzz-core and buzz-datastore-tracing."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/Cargo.toml:11-12"
  - statement: "buzz-pubsub's Cargo.toml declares a dependency on buzz-auth in addition to buzz-core, and buzz-pubsub's rate_limiter.rs and nip98_replay.rs call buzz_auth::rate_limit::rate_limit_key, buzz_auth::rate_limit::ip_rate_limit_key, and other buzz_auth items directly, not through buzz-relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml:11-12"
      - "crates/buzz-pubsub/src/rate_limiter.rs:12"
      - "crates/buzz-pubsub/src/rate_limiter.rs:108"
      - "crates/buzz-pubsub/src/rate_limiter.rs:118"
      - "crates/buzz-pubsub/src/nip98_replay.rs:7"
  - statement: "buzz-workflow's Cargo.toml declares a dependency on buzz-db in addition to buzz-core and buzz-deletion, and buzz-workflow's lib.rs, executor.rs and error.rs call and convert errors from buzz_db::Db, buzz_db::workflow::RunStatus, buzz_db::workflow::WorkflowRecord and buzz_db::error::DbError directly, not through buzz-relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/Cargo.toml:11-13"
      - "crates/buzz-workflow/src/lib.rs:49-50"
      - "crates/buzz-workflow/src/executor.rs:1027"
      - "crates/buzz-workflow/src/error.rs:86-87"
  - statement: "buzz-relay's Cargo.toml declares dependencies on all six named subsystem crates (plus others outside this node's scope), and ARCHITECTURE.md's AppState struct listing shows the relay holding each subsystem's service — db, audit, pubsub, auth, search, workflow_engine — as a field on one shared, Arc-wrapped struct."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:19-28"
      - "crates/buzz-relay/Cargo.toml:65"
      - "ARCHITECTURE.md:581-589"
  - statement: "deny.toml configures only RUSTSEC advisory exceptions and an allowed-license list for the Cargo dependency graph; it contains no rule constraining which crate may depend on which."
    entry_class: FACT
    evidence:
      - "deny.toml"
  - statement: "The Justfile's check and ci recipes run cargo clippy --workspace --all-targets -- -D warnings alongside the desktop, Tauri, web and mobile checks; nothing in that pipeline lints or blocks a new cross-crate dependency edge."
    entry_class: FACT
    evidence:
      - "Justfile:95"
      - "Justfile:105-107"
  - statement: "No automated mechanism in this repository enforces the subsystem-isolation boundary ARCHITECTURE.md states: a new Cargo.toml dependency edge and matching call site between two of the six named subsystem crates would compile cleanly and pass just ci without any check flagging it."
    entry_class: INFERENCE
    evidence:
      - "deny.toml"
      - "Justfile:95"
      - "Justfile:105-107"
    confidence: 0.6
  - statement: "Issue #698's category tail for this node (category: principles) requires stating the invariant as one unambiguous MUST/MUST-NOT property, explaining its scope, naming enforcement points and observable failure behavior, and linking a verification mechanism or explicitly recording that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#698 definition of done, architecture-principles category tail"
---

# Subsystem isolation

The boundary rule between the service crates `buzz-relay` orchestrates: they may be
called by the relay, and they may not call each other.

| For | Read |
|---|---|
| The full crate map and dependency diagram this node narrows | `ARCHITECTURE.md`, "Crate Dependency Hierarchy" |
| Corpus front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating/updating a corpus node | `launchpad/docs/corpus/AGENTS.md` |

Where this document and `ARCHITECTURE.md` disagree on the diagram or the crate list,
`ARCHITECTURE.md` is the fuller source — this node exists to state one property of it
precisely and to check that property against the code, not to duplicate the diagram.

## The invariant

`buzz-relay` is documented as the single source of truth: it imports and directly
orchestrates six subsystem crates — `buzz-db`, `buzz-auth`, `buzz-pubsub`,
`buzz-search`, `buzz-audit`, and `buzz-workflow` — each providing one capability
(Postgres persistence, authn/authz, Redis pub/sub and presence, full-text search, the
hash-chain audit log, and the workflow automation engine, respectively).

Stated as a property: a subsystem crate in that set **MUST NOT** depend on, import, or
call directly into another subsystem crate in that set. Cross-subsystem coordination
**MUST** happen through `buzz-relay`, which holds each subsystem's service as a field on
one shared `AppState` and calls across them from its own handlers.

This is documented intent, not (as *Current compliance* below shows) a property that
holds for every crate in the set today.

## Scope

**Applies to** the six crates named above, at two levels:

- **Declared dependency** — a `buzz-*` line in one of these crates' `[dependencies]` in
  `Cargo.toml` naming another crate in the set.
- **Call site** — a `use buzz_x::...` or fully-qualified `buzz_x::...` reference inside
  one subsystem crate's source resolving to a public item of another.

Both must be absent for the invariant to hold for a given pair; a dependency without a
call site would be dead weight rather than a violation, but none of the crates in scope
carry one — every declared cross-subsystem dependency found while checking this node
had a real call site behind it.

**Does not apply to:**

- **`buzz-core`.** It sits as the common root every one of the six subsystem crates —
  and `buzz-relay` itself — depends on directly, and is documented as zero-I/O (types,
  event verification, filter matching, the kind registry). It is the shared foundation
  the subsystems are built on, not one of the orchestrated subsystems itself.
- **`buzz-relay`'s own dependencies on the six.** That is the orchestration point this
  invariant protects, not an instance of it — the relay depending on all six and calling
  across them from its own handlers is exactly what "coordination happens through the
  relay" means.
- **Small shared-utility crates such as `buzz-datastore-tracing`.** Several of the six
  depend on it for tracing instrumentation; it carries no `buzz-*` dependency of its own
  and plays the same foundation role as `buzz-core` for this invariant's purposes.
- **Every other crate in the workspace** (`buzz-media`, `buzz-acp`, `buzz-cli`,
  `buzz-deletion`, `buzz-conformance`, and the rest). Several of them are not named in
  ARCHITECTURE.md's stated principle or its dependency diagram at all — see *Scope and
  omissions*.

## Enforcement points and observable failure behavior

**Enforcement point:** none automated. The only place this boundary is checked today is
human PR review — reading a diff that adds a `buzz-*` line to one of the six subsystem
crates' `Cargo.toml` and the call site that uses it. `deny.toml` governs RUSTSEC
advisories and license allow-listing only, and carries no rule about which crate may
depend on which. The `Justfile`'s `check`/`ci` recipes run `cargo clippy --workspace
--all-targets -- -D warnings` plus desktop/Tauri/web/mobile checks; none of those lints
a cross-crate dependency edge. **Verification of this invariant is, as a matter of
current fact, missing** — see the INFERENCE entry in this node's evidence ledger.

**Observable failure behavior:** none, automatically. Adding a cross-subsystem
dependency and a matching call site compiles cleanly (the Rust compiler only requires
the `Cargo.toml` edge to exist, and enforces nothing about which edges are appropriate)
and passes `just ci` unchanged, because nothing in that pipeline inspects the crate
dependency graph for this property. A violation is discoverable only by reading the
`Cargo.toml` diff, or by running `cargo tree -p <crate> | grep buzz-` against one of the
six and comparing the result against this node's *Current compliance* table below.

## Current compliance

Checked against `Cargo.toml` and the actual call sites in each of the six crates, at the
revision recorded in this node's evidence ledger:

| Crate | Declares a `buzz-*` dependency on another subsystem crate | Compliant |
|---|---|---|
| `buzz-db` | none (`buzz-core`, `buzz-datastore-tracing` only) | Yes |
| `buzz-auth` | none (`buzz-core` only) | Yes |
| `buzz-search` | none (`buzz-core`, `buzz-datastore-tracing` only) | Yes |
| `buzz-audit` | none (`buzz-core`, `buzz-datastore-tracing` only) | Yes |
| `buzz-pubsub` | `buzz-auth` — calls `buzz_auth::rate_limit::rate_limit_key` and `ip_rate_limit_key` for rate limiting | **No** |
| `buzz-workflow` | `buzz-db` — calls `buzz_db::Db`, persists/reads `buzz_db::workflow::WorkflowRecord`/`RunStatus`, converts `buzz_db::error::DbError` | **No** |

**Two of the six named subsystem crates violate the stated invariant as written.**
`ARCHITECTURE.md`'s own worked examples ("`buzz-workflow` never calls `buzz-pubsub`,
`buzz-search` never calls `buzz-db`") both hold — but the broader claim they illustrate,
"those subsystems are isolated from each other," does not hold for the `buzz-pubsub` →
`buzz-auth` and `buzz-workflow` → `buzz-db` pairs. Both are real, functional
dependencies (rate-limit key derivation; workflow run persistence), not stale or unused
`Cargo.toml` entries — see the call-site citations in this node's evidence ledger.

This node reports that gap rather than resolving it. Whether the fix is to route those
two call paths through `buzz-relay`, to narrow the stated invariant to exclude
`buzz-auth` (a plausible reading, since `buzz-auth`'s own dependency footprint looks
more like a foundation crate than a peer subsystem — it depends on nothing but
`buzz-core`), or to update `ARCHITECTURE.md`'s wording, is an implementation or
documentation decision this corpus-authoring task does not own.

## Scope and omissions

**This document covers** the specific boundary among the six subsystem crates
`ARCHITECTURE.md` names as orchestrated by `buzz-relay`: what MUST NOT cross-depend on
what, where that is and is not currently true, and what would (and would not) catch a
new violation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Why |
|---|---|
| `buzz-relay`'s propagation of `TenantContext`/community-scoped inputs to these crates | A related but distinct rule named in the same `ARCHITECTURE.md` sentence as this invariant; it is about tenancy derivation, not crate-to-crate call boundaries, and belongs in its own node. |
| Whether `buzz-deletion`, `buzz-conformance`, `buzz-relay-mesh`, `buzz-datastore-tracing`, `buzz-voice`, `buzz-push-gateway`, or `buzz-backend-kubernetes` should be in scope of this invariant | None of these crates appear in `ARCHITECTURE.md`'s stated principle or its crate dependency diagram at all — that diagram and crate list predate them. Whether the corpus's architecture documentation should be updated to include them is out of scope for this node. |
| Fixing the `buzz-pubsub` → `buzz-auth` or `buzz-workflow` → `buzz-db` coupling, or resolving whether `buzz-auth` is a peer subsystem or a foundation crate | Implementation and documentation decisions, not corpus authorship. |
| A general test/lint that would enforce this invariant mechanically going forward | No such mechanism exists in this repository today (see *Enforcement points and observable failure behavior*); designing one is future work, not something this node can point at. |

**Expected but not verified when this node was written:** whether `buzz-relay`'s own
handler code, beyond the `AppState` field listing cited here, ever calls a subsystem
crate's function from *inside* another subsystem crate's code path (as opposed to from
`buzz-relay` itself) was not checked line-by-line across the whole relay crate — only
`AppState`'s shape and the two known cross-subsystem edges above were verified in
detail.

**No `relationships`** — no other node currently merged on `launchpad` describes Buzz's
architecture or crate structure. The four merged nodes at the time of writing
(`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references`) are all `type: governance` nodes about the corpus
itself, not about Buzz. A `relationships[].target` naming an id no loaded node carries is
a hard validation error, so none is declared here. The first sibling architecture node to
merge is the point to revisit this.
