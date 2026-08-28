---
id: architecture-principles-relay-orchestrates-subsystems
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
  - statement: "buzz-relay's Cargo.toml declares buzz-db, buzz-auth, buzz-pubsub, buzz-audit, buzz-search, buzz-media and buzz-workflow as dependencies."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
  - statement: "None of buzz-core, buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit, buzz-media or buzz-workflow declares buzz-relay as a dependency, in either [dependencies] or [dev-dependencies]."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/Cargo.toml"
      - "crates/buzz-db/Cargo.toml"
      - "crates/buzz-auth/Cargo.toml"
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-search/Cargo.toml"
      - "crates/buzz-audit/Cargo.toml"
      - "crates/buzz-media/Cargo.toml"
      - "crates/buzz-workflow/Cargo.toml"
  - statement: "AppState, buzz-relay's shared server-process state, holds one field per composed subsystem: db (buzz-db), audit (buzz-audit), pubsub (buzz-pubsub), auth (buzz-auth), search (buzz-search), workflow_engine (buzz-workflow) and media_storage (buzz-media)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:630"
      - "crates/buzz-relay/src/state.rs:634"
      - "crates/buzz-relay/src/state.rs:638"
      - "crates/buzz-relay/src/state.rs:640"
      - "crates/buzz-relay/src/state.rs:642"
      - "crates/buzz-relay/src/state.rs:644"
      - "crates/buzz-relay/src/state.rs:668"
      - "crates/buzz-relay/src/state.rs:699"
  - statement: "buzz-relay's main() constructs one instance of each subsystem service (AuditService, PubSubManager, AuthService, SearchService, WorkflowEngine, MediaStorage) and passes all of them into a single AppState::new call; nothing else in the codebase calls AppState::new to start a live server."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:355-467"
  - statement: "buzz-pubsub declares a dependency on buzz-auth and uses it directly, in rate_limiter.rs and nip98_replay.rs, for shared rate-limiting and NIP-98 replay-guard primitives -- a real cross-subsystem edge that does not run through buzz-relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "buzz-workflow declares a dependency on buzz-db -- a second cross-subsystem edge that does not run through buzz-relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/Cargo.toml"
  - statement: "buzz-admin's Cargo.toml declares buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit, buzz-media and buzz-workflow as direct dependencies -- the same subsystem set buzz-relay composes -- so buzz-relay is not the only crate in the workspace that imports every one of them."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/Cargo.toml"
  - statement: "buzz-admin's main.rs is a one-shot clap CLI (AddMember, RemoveMember, ListMembers, GenerateKey, Migrate, and more) whose subcommands connect directly to Postgres and Redis for administrative operations; it never constructs an AppState and runs no HTTP or WebSocket server."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "ARCHITECTURE.md states this repository's own architectural principle in prose: buzz-relay is 'the single source of truth' that 'orchestrates all subsystems by calling them directly', and elsewhere describes buzz-relay as 'the only crate that imports and orchestrates all subsystems'."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:97"
      - "ARCHITECTURE.md:576"
  - statement: "ARCHITECTURE.md's 'only crate' and 'isolated from each other' phrasing is imprecise at the current revision: buzz-admin also imports every subsystem crate directly (see the buzz-admin evidence above), and buzz-pubsub -> buzz-auth plus buzz-workflow -> buzz-db are real cross-subsystem edges, not full isolation."
    entry_class: INFERENCE
    evidence:
      - "ARCHITECTURE.md:97"
      - "crates/buzz-admin/Cargo.toml"
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-workflow/Cargo.toml"
    confidence: 0.8
  - statement: "deny.toml, the config cargo-deny reads in CI, governs advisories, license allow-lists and duplicate-version/wildcard bans; it contains no rule constraining which crate may depend on which other workspace crate."
    entry_class: FACT
    evidence:
      - "deny.toml"
      - ".github/workflows/ci.yml"
---

# Principle: the relay is the crate that composes the subsystems into a live process

## The invariant

**No subsystem crate composed into `AppState` -- `buzz-db`, `buzz-auth`, `buzz-pubsub`,
`buzz-search`, `buzz-audit`, `buzz-media`, or `buzz-workflow` -- MUST depend on
`buzz-relay`, in `[dependencies]` or `[dev-dependencies]`.** The Cargo package graph
between these crates and `buzz-relay` MUST remain a one-directional fan-in: every
subsystem crate is upstream of `buzz-relay`, never downstream of it, and `buzz-relay`
MUST be able to import all of them without ever being imported back.

This is the property that makes `buzz-relay` the composition point rather than one peer
among several: cross-subsystem coordination that needs more than one service (for
example, an event handler that must check auth, write to the DB and fan out over
pub/sub in one request) happens in `buzz-relay`, which can see every subsystem, not
inside a subsystem crate trying to reach sideways into a peer it cannot depend on.

## Scope

**Applies to:** the seven crates directly held as fields on `AppState` --
`buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`, `buzz-audit`, `buzz-media` and
`buzz-workflow` -- and to the one direction of dependency named above (subsystem ->
relay). `buzz-core` is the shared foundation beneath all of them and carries no
`buzz-*` dependency of its own; it is out of scope for this invariant because it is
never itself a candidate to depend on `buzz-relay`, being lower in the graph than the
subsystems this node governs.

**Does not apply to:** whether a subsystem may depend on *another* subsystem. Two such
edges already exist -- `buzz-pubsub` -> `buzz-auth` and `buzz-workflow` -> `buzz-db` --
and neither violates the invariant above, because neither closes back to `buzz-relay`.
`ARCHITECTURE.md`'s prose describes the subsystems as "isolated from each other", which
overstates what is actually enforced; see *Scope and omissions*.

**Does not apply to:** other crates in the workspace that also depend on some or all of
the subsystem crates for their own, non-serving purposes. `buzz-admin` is the clearest
case: it depends directly on the same seven subsystem crates `buzz-relay` composes, for
one-shot administrative commands (`AddMember`, `Migrate`, and similar) that talk to
Postgres and Redis directly and never start an HTTP or WebSocket server. `buzz-admin`
does not depend on `buzz-relay` either, so it does not violate the invariant -- but its
existence means the correct claim is narrower than "`buzz-relay` is the only crate that
imports these subsystems". The correct claim is the one this node states: no subsystem
crate depends back on `buzz-relay`, and `buzz-relay` is the crate that composes them
into the one live-serving process (see next section) -- a distinct property from being
the sole importer.

**States and operations this governs:** the crate-dependency graph as declared in each
crate's `Cargo.toml`, checked at `cargo build`/`cargo check` time for the whole
workspace. It does not govern runtime call graphs beyond what the dependency graph
already constrains -- a crate cannot call a function in a crate it does not depend on.

## What "orchestrates" means here

`buzz-relay`'s `main()` constructs one instance of each subsystem service -- an
`AuditService`, a `PubSubManager`, an `AuthService`, a `SearchService`, a
`WorkflowEngine`, a `MediaStorage` -- and passes all of them into a single
`AppState::new` call, producing the one `Arc<AppState>` that every WebSocket
connection and HTTP handler in the process shares for the lifetime of the server. That
composition point is what "orchestrates" refers to: not merely importing a crate, but
assembling every subsystem's already-constructed instance into the one shared state a
live server serves traffic from. No other binary in this workspace does that assembly;
`buzz-admin`'s commands construct and use individual services (e.g. a `Db` and a
`PubSubManager` for a membership-roster publish) without ever building an `AppState` or
running a server loop.

## Enforcement points and observable failure

**Mechanically enforced, incidentally:** Cargo's own dependency resolution requires an
acyclic package graph through non-dev dependencies. Because `buzz-relay` already depends
on every subsystem crate this node governs, a subsystem crate that added `buzz-relay` as
a normal dependency would make the workspace graph cyclic. This node does **not** claim
to have reproduced that failure in this repository -- no such edge was added and then
built to observe the error -- so the exact Cargo diagnostic text is not verified here;
see *Scope and omissions*.

**Not enforced by any project-specific check.** `cargo-deny` runs in CI
(`.github/workflows/ci.yml`) and reads `deny.toml`, but that configuration governs
license allow-lists, security advisories, and duplicate-version/wildcard bans -- it
contains no rule about which workspace crate may depend on which. No architecture-lint,
custom CI job, or `just` recipe in this repository checks dependency direction between
`buzz-relay` and the subsystem crates. A pull request that added `buzz-relay` as a
subsystem crate's dependency would first be caught by the resulting build failure (if
the cycle is genuine) or, if some other change avoided a literal cycle while still
routing subsystem logic through `buzz-relay`, would not be caught by any automated
check at all -- only by review against `ARCHITECTURE.md`'s stated principle and this
node.

## Verification / conformance

**No automated conformance check exists for this invariant today.** This is recorded
explicitly rather than implied: the closest CI mechanism, `cargo-deny`, does not cover
it (see above), and no dependency-graph lint runs in `just ci`. The only verification
performed for this node is the manual one recorded in its evidence ledger: reading every
named `Cargo.toml` directly and confirming no subsystem crate lists `buzz-relay`, at the
commit in provenance.

## Scope and omissions

**This document covers:** the one-directional dependency requirement between the
subsystem crates and `buzz-relay`, what "orchestrates" means in terms of the
`AppState`/`main()` composition point, and what enforces (and does not enforce) that
requirement today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Why |
|---|---|
| Whether cross-subsystem edges (`buzz-pubsub` -> `buzz-auth`, `buzz-workflow` -> `buzz-db`) are themselves desirable architecture | Out of this node's scope -- it records that they exist and that they do not violate the stated invariant, and takes no position on whether more or fewer such edges should exist. |
| Whether `buzz-admin`'s direct access to every subsystem crate is itself a property worth governing | A design question for elsewhere; this node only establishes that it does not depend on `buzz-relay` and therefore does not violate the invariant above. |
| The exact Cargo diagnostic a genuine cycle would produce | Not reproduced in this repository as part of writing this node; recorded as unverified rather than asserted. |
| Updating `ARCHITECTURE.md`'s "isolated from each other" and "only crate" phrasing | Out of scope for this task, which authors one corpus node and touches no other file. `ARCHITECTURE.md`'s core claim -- that `buzz-relay` is the crate that orchestrates the subsystems -- is corroborated by the evidence above; its stronger phrasing ("isolated", "only crate") is not, at this revision. |
| Any `relationships` edge to a sibling `architecture/*` corpus node | No other node under `launchpad/docs/corpus/architecture/` is merged at this revision, and a `relationships[].target` naming an id no loaded node carries is a hard validation error, so none is declared. |

**Expected but not verified when this node was written:** whether any subsystem crate
has, at some point in history, depended on `buzz-relay` and been reverted -- git history
for that specific pattern was not searched; only the current `Cargo.toml` state at the
recorded revision was checked.
