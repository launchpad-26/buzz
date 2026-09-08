---
id: verification-formal-tla-plus
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
  - statement: "This repository contains two TLA+ specifications -- docs/spec/MultiTenantRelay.tla (the multi-tenant relay/database isolation model) and docs/spec/GitOnObjectStore.tla (a model of git refs over object storage) -- plus a third formal-methods artifact, docs/spec/MultiTenantAuth.spthy, which is a Tamarin Prover theory rather than TLA+."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla"
      - "docs/spec/GitOnObjectStore.tla"
      - "docs/spec/MultiTenantAuth.spthy"
  - statement: "MultiTenantRelay.tla's header docstring states its master proof obligation is non-interference encoded as a label/taint invariant -- no value labeled outside a connection's resolved community may flow into that connection's typed observational interface -- and names eight enumerated mutation tests (M1-M8) it is checked to be non-vacuous against."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla"
  - statement: "GitOnObjectStore.tla's own header docstring states it is a model-checked companion to docs/git-on-object-storage.md and asserts three safety properties: T1 fence (an observed success implies the obligated push is durably published), T2 closure (a published manifest either covers its parent's packs or names a trusted full-closure compaction pack), and T3 ref linearizability (installs form a fork-free chain, each committing exactly the value it proposed)."
    entry_class: FACT
    evidence:
      - "docs/spec/GitOnObjectStore.tla"
  - statement: "Each .tla spec has a matching TLC configuration file whose own header comment states the exact command to run it: MultiTenantRelay.cfg reads 'java -cp ~/.buzz/.scratch/tla2tools.jar tlc2.TLC -config MultiTenantRelay.cfg MultiTenantRelay.tla', and GitOnObjectStore.cfg reads 'tlc GitOnObjectStore.tla -config GitOnObjectStore.cfg'; both configs bind CONSTANTS to small finite sets (two communities, five channels and three hosts for the relay model; three pushers and MaxManifests=3 for the object-store model) and declare an INVARIANT named Safety."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.cfg"
      - "docs/spec/GitOnObjectStore.cfg"
  - statement: "TLA+ is Leslie Lamport's formal specification language for describing system behavior as a state machine (an Init predicate and a Next action), and TLC is its explicit-state model checker, which explores the finite reachable-state graph induced by a spec's Init/Next actions for the constants bound in a .cfg file and checks stated invariants over that explored graph."
    entry_class: FACT
    evidence:
      - "https://lamport.azurewebsites.net/tla/tla.html"
  - statement: "Because both .cfg files in this repository bind their CONSTANTS to small finite sets rather than leaving them unbounded, a TLC run against either spec as configured here checks the Safety invariant only for that specific bounded instance, not universally for every possible system size -- this is model checking of a finite instance, not a proof holding for arbitrary N."
    entry_class: INFERENCE
    evidence:
      - "docs/spec/MultiTenantRelay.cfg"
      - "docs/spec/GitOnObjectStore.cfg"
      - "https://lamport.azurewebsites.net/tla/tla.html"
    confidence: 0.8
  - statement: "crates/buzz-conformance/TRACE_SCHEMA.md opens by describing itself as 'the contract between the relay's emitter and the independent replay checker,' states it is grounded in docs/spec/MultiTenantRelay.tla, and maps its TraceAction enum variants one-to-one onto named actions in that spec's Next relation."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/TRACE_SCHEMA.md"
  - statement: "crates/buzz-conformance/LIMITS.md states plainly that 'spec correctness is the proof obligation of docs/spec/MultiTenantRelay.tla, machine-checked by TLC,' and that the checker re-implements the spec's Next relation independently of the relay's own production reducer specifically so a bug shared between an emitter and a checker built from the same helpers cannot hide from both."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md"
  - statement: "LIMITS.md enumerates exactly three test surfaces that 'MUST stay green on every PR': buzz-conformance's own schema/checker unit tests (9), its replay-fixture tests (5), and buzz-relay's EmitGuard coverage-breach self-test (2) -- 16 tests total -- and none of the three invoke TLC or read either .tla file."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md"
  - statement: "The repository Justfile's test-unit recipe explicitly enumerates 'cargo nextest run -p buzz-conformance', commented there as 'no infra -- pure in-process trace replay,' among the packages it runs as part of the just test-unit command."
    entry_class: FACT
    evidence:
      - "Justfile:316-359"
  - statement: "The 'Unit Tests' job in .github/workflows/ci.yml runs 'just test-unit' on every push and on every pull request that changes Rust sources, giving buzz-conformance's checker test suite unconditional CI enforcement."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:126-149"
  - statement: "No file under .github/workflows/, the repository Justfile, or scripts/ invokes tla2tools.jar, tlc2.TLC, or a tlc binary; the only run instructions for TLC anywhere in the repository are the header comments inside MultiTenantRelay.cfg and GitOnObjectStore.cfg themselves, both of which describe a manual, locally-run command rather than an automated one."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "Justfile"
      - "docs/spec/MultiTenantRelay.cfg"
      - "docs/spec/GitOnObjectStore.cfg"
  - statement: "A repository-wide search for 'GitOnObjectStore' outside the corpus returns only the spec itself, its .cfg, and docs/git-on-object-storage.md; unlike MultiTenantRelay.tla, GitOnObjectStore.tla has no Rust runtime conformance checker analogous to buzz-conformance pairing live production traces against it."
    entry_class: FACT
    evidence:
      - "docs/spec/GitOnObjectStore.tla"
      - "docs/git-on-object-storage.md"
  - statement: "docs/spec/MultiTenantAuth.spthy declares 'theory MultiTenantAuth begin' and uses Tamarin Prover's signing/hashing builtins, restrictions, and lemma syntax to model the multi-tenant relay's symbolic auth/key/audit security surface -- a different formal-methods tool from TLA+, and out of scope for this node."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantAuth.spthy"
  - statement: "Issue #1374's task brief identifies sibling issue #1371 (intended node id verification-formal-multi-tenant-relay) as covering the same MultiTenantRelay.tla + buzz-conformance pairing at the specific-obligation depth, and directs this node to take the broader/methodological TLA+ angle and cross-reference #1371's node rather than duplicating its detailed obligation coverage."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1374 task brief"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree contains no verification/ subtree at any depth and therefore no node with id verification-formal-multi-tenant-relay, so this node declares no references relationship to it."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> no verification/ subtree present at any depth, confirmed after a fresh git fetch origin launchpad"
---

# TLA+ model checking — test contract

## Purpose and boundary

This node documents TLA+ as a verification method and tool as used in this repository
**generally** -- what it is, why it is used here, the distinction between model checking
and proof, and how the one TLA+-model-checked spec that has an automated production-side
checker (`docs/spec/MultiTenantRelay.tla`, paired with `buzz-conformance`) is actually
enforced. It does not restate the multi-tenant relay's specific non-interference
obligation or its per-mutation (M1-M8) coverage in detail -- that is sibling issue
#1371's node, `verification-formal-multi-tenant-relay`, referenced here rather than
duplicated. That node does not yet exist on `origin/launchpad` at the time this node was
authored (see *Relationships*, below), so no `references` edge is declared; add one once
it lands.

## What TLA+ is, and how it is used here

TLA+ is a formal specification language: a system is written as a state machine (an
`Init` predicate plus a `Next` action describing every possible transition), and safety
properties are written as invariants that must hold in every reachable state. TLC is
TLA+'s model checker -- rather than proving an invariant algebraically, it exhaustively
(or, for larger state spaces, randomly via simulation) explores the reachable-state graph
that a spec's `Init`/`Next` actions induce for one **finite** instantiation of the spec's
`CONSTANTS`, checking the stated invariant at every state it visits.

This repository has two TLA+ specs, each with its own TLC `.cfg` file:

- **`docs/spec/MultiTenantRelay.tla`** models N stateless relay workers over one shared
  Postgres database, with the master proof obligation stated as non-interference: no
  value labeled outside a connection's resolved community may flow into that
  connection's observational interface. `MultiTenantRelay.cfg` binds `Communities`,
  `Channels`, `Hosts`, `Actors`, `Workers`, `MsgIds` and `AuditVals` to small finite sets
  (two communities, five channels, three hosts, one actor, one worker) and declares
  `INVARIANT Safety`.
- **`docs/spec/GitOnObjectStore.tla`** models pushers racing to advance a single git ref
  pointer over conditional-write (CAS) object storage, asserting three safety
  properties -- T1 fence, T2 closure, T3 ref linearizability -- as a companion to
  `docs/git-on-object-storage.md`. `GitOnObjectStore.cfg` bounds `Pushers` to three
  workers and `MaxManifests` to 3.

Because both `.cfg` files bind their constants to small finite sets, a TLC run against
either spec checks `Safety` only for that specific bounded instance -- this is model
checking of one finite case, not a proof holding for every possible system size. A third
formal-methods artifact, `docs/spec/MultiTenantAuth.spthy`, models the relay's symbolic
auth/key/audit surface in Tamarin Prover -- a different tool, using different theory
(signing/hashing builtins, restrictions, lemmas), and out of scope for this node.

## Obligation

> For the multi-tenant relay's ingest/auth/read boundary, the model-checked TLA+ spec
> (`docs/spec/MultiTenantRelay.tla`) and `buzz-conformance`'s independent Rust
> re-implementation of that spec's `Next` transition relation are engineered so that any
> relay-emitted execution trace diverging from the spec's transition relation is caught
> by `check_trace`, rather than passing silently.

`buzz-conformance`'s checker deliberately re-implements the spec's `Next` relation from
scratch, rather than reusing the relay's own decision helpers, specifically so that a bug
shared between the production emitter and its own checker cannot hide from both.

## Verifying test(s)

- `crates/buzz-conformance/src/checker.rs` -- `#[cfg(test)] mod tests` (9 tests) --
  transition-rule coverage for every `TraceAction` variant, each with a passing case and
  at least one mutation-class bite case.
- `crates/buzz-conformance/tests/replay_fixtures.rs` (5 tests) -- reconstructs three
  committed golden JSONL traces (`good.jsonl`, `bad_host_channel_mismatch.jsonl`,
  `bad_coverage_breach.jsonl`) from typed Rust, asserts they match byte-for-byte, then
  replays each through `check_trace` and asserts the expected `Ok`/`IllegalTransition`/
  `CoverageBreach` outcome.
- `crates/buzz-relay/src/conformance/mod.rs` -- `conformance::` tests (2 tests) -- proves
  `EmitGuard::Drop` records `ImplBug` when a seam's counting tracer saw zero emits, and
  stays silent when an emit did reach the tracer.

None of these three test surfaces invokes TLC or reads either `.tla` file directly; they
exercise the Rust re-implementation of the spec's transition relation and its coverage
guard.

## How to run it

The Rust conformance-checker suite (CI-enforced, no infrastructure required):

```bash
cargo nextest run -p buzz-conformance
cargo test -p buzz-relay --lib conformance::
```

Equivalently, `just test-unit` runs both of these among the rest of the workspace's
infra-free unit suite.

The TLA+ spec's own model-checking (manual only -- see *Current enforcement status*):

```bash
# requires tla2tools.jar downloaded locally first, per MultiTenantRelay.cfg's own
# header comment
java -cp ~/.buzz/.scratch/tla2tools.jar tlc2.TLC \
  -config docs/spec/MultiTenantRelay.cfg docs/spec/MultiTenantRelay.tla

# GitOnObjectStore.cfg's header comment gives the shorter form, assuming a `tlc`
# launcher script/alias is on PATH:
tlc docs/spec/GitOnObjectStore.tla -config docs/spec/GitOnObjectStore.cfg
```

## Current enforcement status

**Mixed, and the two halves must not be conflated:**

- The Rust conformance-checker test surface (`buzz-conformance`'s unit and
  replay-fixture tests, plus `buzz-relay`'s `EmitGuard` self-test -- 16 tests total) is
  **verified**: `Justfile`'s `test-unit` recipe enumerates `cargo nextest run -p
  buzz-conformance` explicitly, and CI's "Unit Tests" job runs `just test-unit`
  unconditionally on every push and every Rust-touching pull request.
- TLC model-checking of `MultiTenantRelay.tla` and `GitOnObjectStore.tla` themselves is
  **not wired into CI, a Justfile recipe, or any script anywhere in this repository** --
  no file under `.github/workflows/`, `Justfile`, or `scripts/` invokes `tla2tools.jar`,
  `tlc2.TLC`, or a `tlc` binary. The only run instructions that exist are the header
  comments inside each spec's own `.cfg` file, both of which describe a command a
  developer runs by hand. This does not cleanly fit this template's `verified`/`gated`/
  `pending` vocabulary -- the artifacts exist and are runnable today (unlike `pending`),
  but nothing gates a merge on running them (unlike `verified` or `gated`, both of which
  presume a CI-visible pass/fail). The honest label is **manual and unautomated**.

`crates/buzz-conformance/LIMITS.md` states "spec correctness is the proof obligation of
`docs/spec/MultiTenantRelay.tla`, machine-checked by TLC" -- asserting that TLC checking
has been done, but not that it is repeated or gated by anything on every change.

## Limits

- **Bounded instances, not universal proofs.** TLC as configured here explores only the
  finite constant instantiations in each `.cfg` file. A property holding for two
  communities and five channels, or three pushers and three manifests, is evidence about
  those specific bounded models -- not a proof for arbitrarily many communities, hosts,
  or pushers.
- **No CI gate re-runs TLC.** A change to either `.tla` file, or to either `.cfg` file's
  bounds, is not automatically re-checked by anything in this repository's CI. Whether
  `Safety` still holds after an edit is only as current as the last time someone ran TLC
  by hand and is not established by this node.
- **The Rust checker tests a re-implementation, not the spec.** `buzz-conformance`'s
  16-test CI-enforced suite proves the checker's own Rust logic (`checker.rs`,
  its fixtures, and `EmitGuard`) behaves as intended against golden traces. It does not
  re-run TLC and does not prove `MultiTenantRelay.tla` itself is internally consistent.
  If the spec has a bug, `LIMITS.md` itself says both TLC and the checker would agree
  and both would be wrong.
- **`GitOnObjectStore.tla` has no production-trace checker at all.** Unlike
  `MultiTenantRelay.tla`, there is no `buzz-conformance`-style Rust re-implementation
  observing real git-push traces against `GitOnObjectStore.tla`'s transition relation.
  Its only verification today is a manual TLC run against the bounded `.cfg` instance.
- **Scope of what was checked in authoring this node.** This node did not itself run
  TLC against either spec, and did not execute `buzz-conformance`'s test suite; both
  claims above rest on reading `LIMITS.md`'s and the `.cfg` files' own text, not on a
  fresh run.

## Scope and omissions

**This node covers** what TLA+ is, why this repository uses it, the model-checking-
versus-proof distinction as it applies to the two `.tla` specs here, how
`MultiTenantRelay.tla`'s model-checking connects to `buzz-conformance`'s CI-enforced
Rust checker, and that TLC's own execution is manual and unautomated in this repository.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `MultiTenantRelay.tla`'s specific non-interference obligation, its C1/C2 channel taxonomy, and per-mutation (M1-M8) obligation coverage in depth | #1371's node, `verification-formal-multi-tenant-relay` (not yet landed -- see *Relationships*) |
| `GitOnObjectStore.tla`'s specific T1/T2/T3 safety properties for the git-on-object-storage push-race model, in depth | Not yet assigned to any corpus node; a second distinct TLA+-verified obligation this node deliberately does not fold in |
| `docs/spec/MultiTenantAuth.spthy`'s Tamarin Prover model of the auth/key/audit symbolic security surface | Out of scope -- a different formal-methods tool, not TLA+ |
| Whether `Safety` currently holds for either spec, verified by an actual TLC run performed while authoring this node | Not established here; see *Limits* |
| General testing/verification practice in this repository beyond formal methods | `TESTING.md` |

**Relationships.** `AGENTS.md`'s warning against a false "nothing to point at"
justification was checked, not assumed: after a fresh `git fetch origin launchpad`,
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` shows no
`verification/` subtree at any depth, so `verification-formal-multi-tenant-relay` (issue
#1371's node) does not yet exist there and no `references` edge to it validates today.
The first PR that lands that node is the moment to add the edge here.
