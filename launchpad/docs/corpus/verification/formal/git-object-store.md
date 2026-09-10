---
id: verification-formal-git-object-store
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
  - statement: "docs/git-on-object-storage.md states axiom (A3), linearizable conditional write: a PUT of the manifest pointer with If-Match succeeds iff the compared value equals the pointer's current value, and at most one of several concurrent conditional PUTs against the same current value succeeds; it names A3 'the single load-bearing backend assumption' that the design substitutes for POSIX rename()."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "GitStore::classify_cas (crates/buzz-relay/src/api/git/store.rs:521-553) maps an S3 PUT outcome to CasOutcome: a 2xx response with an ETag header becomes Won(etag); Err(S3Error::HttpFailWithBody(412, _)) becomes LostRace; a 2xx response missing an ETag header, or any other status/error, is rejected as StoreError::Backend rather than silently treated as a win."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:521-553"
  - statement: "GitStore::run_conformance_probe's if_match_race phase (crates/buzz-relay/src/api/git/store.rs:620-724) seeds a pointer key, then races race_width concurrent put_pointer(..., Precond::IfMatch(etag)) calls against the same etag for race_rounds rounds; it fails the round if fewer than two racers received a classified (non-transport-error) outcome (lines 700-711), and fails the round if the number of classified winners is not exactly 1 (lines 712-722)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:620-724"
  - statement: "GitStore::run_conformance_probe's if_none_match_race phase (crates/buzz-relay/src/api/git/store.rs:726-841) races race_width concurrent create-only put_immutable_raw writes against the same not-yet-existing key, fails the round unless at least two racers are classified (lines 792-804), fails the round unless exactly one racer is classified 2xx and every other classified racer is 412 (lines 805-820), and then verifies the object read back afterward hashes to the winning racer's own bytes (lines 821-840)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:726-841"
  - statement: "run_conformance_probe's own doc comment (crates/buzz-relay/src/api/git/store.rs:555-575) labels the if_match_race phase as testing A3, and the if_none_match_race phase as testing A1 (content addressing) plus A3 together on the create-only primitive."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:555-575"
  - statement: "crates/buzz-relay/src/main.rs:489-525 calls state.git_store.run_conformance_probe(cfg) once during relay startup, gated on BUZZ_GIT_CONFORMANCE_PROBE defaulting to enabled (main.rs:493-495), with its own comment stating 'Failure is fatal: a backend that cannot satisfy pointer CAS invalidates the manifest-pointer protocol,' and propagates any Err via `?` into main's Result, which fails the process rather than continuing to serve traffic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:489-525"
  - statement: "crates/buzz-relay/src/api/git/store.rs's own probe module doc comment (lines 1019-1027) states probe::probe_conformance is run manually via 'BUZZ_GIT_S3_PROBE=1 cargo test -p buzz-relay --lib api::git::store::probe -- --nocapture --test-threads=1' against a local MinIO started by 'docker compose up minio', and probe_enabled() (lines 1031-1033) reads that same environment variable; every #[tokio::test] in the probe module (probe_412_surfacing, probe_full_roundtrip, probe_conformance, probe_get_exposes_etag) returns immediately without exercising its body when the variable is unset, rather than being marked #[ignore]."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:1019-1214"
  - statement: "probe::probe_conformance (crates/buzz-relay/src/api/git/store.rs:1176-1192) calls st.run_conformance_probe with race_width: 8, race_rounds: 2 and asserts the call succeeds and the returned report echoes those parameters, exercising exactly the if_match_race and if_none_match_race phases described above whenever it actually runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:1176-1192"
  - statement: "tests::classify_cas_412_is_lost_race and tests::classify_cas_other_4xx_bubbles (crates/buzz-relay/src/api/git/store.rs:935-948) are plain #[test] functions -- no #[tokio::test], no #[ignore], no environment-variable gate -- that assert GitStore::classify_cas maps Err(S3Error::HttpFailWithBody(412, _)) to CasOutcome::LostRace and maps Err(S3Error::HttpFailWithBody(403, _)) to Err(StoreError::Backend(..)) rather than to LostRace."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:935-948"
  - statement: "launchpad/docs/corpus/standards/test-references.md distinguishes a bare-path citation to a test file (proves the test exists, nothing about its contents or whether it runs in any lane) from a tool-result citation (an actually observed run), and requires an author citing a test's current pass as evidence to have reproduced it at or near the node's recorded revision rather than trusting an earlier or assumed pass."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/test-references.md"
  - statement: "Justfile's test-unit recipe (lines 316-385) enumerates every package and, for buzz-relay specifically, only a filtered set of api::admin tests (line 384, filter 'test(/^api::admin::/) - ...'); its own comment on that line block states 'nothing in CI runs cargo test --workspace' and that buzz-relay --lib tests outside that filter therefore run in no infrastructure-free lane, naming this exact gap as the reason a prior broken admin test once shipped green."
    entry_class: FACT
    evidence:
      - "Justfile:316-385"
  - statement: "No line in .github/workflows/ci.yml or Justfile selects the api::git::store::tests module (by package(buzz-relay) filter, by path, or by a plain unfiltered cargo test/cargo nextest run over buzz-relay), and the only buzz-relay --lib invocation in the infrastructure-free unit-tests job (Justfile:384) is scoped to api::admin::, which does not include api::git."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/ci.yml"
      - "Justfile:316-385"
    confidence: 0.6
  - statement: "The classify_cas unit tests therefore compile and would run under an unfiltered `cargo test -p buzz-relay --lib`, but are not invoked by any CI job or documented just recipe found in this repository at the recorded revision, so their current pass/fail status is not continuously observed by anything but a developer running them by hand."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:935-948"
      - ".github/workflows/ci.yml"
      - "Justfile:316-385"
    confidence: 0.6
  - statement: "crates/buzz-test-client/tests/e2e_git.rs:412-413 marks git_concurrent_push_one_wins_and_repo_recovers with #[ignore = \"requires live relay + MinIO + git\"]; the test drives 8 concurrent git-clone worktrees each committing and pushing to the same freshly announced repo's main branch, then asserts exactly one of the 8 concurrent `git push` invocations succeeds (line 495), the other 7 fail (line 496), the S3 manifest pointer advances (lines 502-505), and the branch a fresh clone observes afterward equals the single winning contender's own commit (line 520), never a merge of two or a different contender's commit."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs:412-520"
  - statement: "No occurrence of 'e2e_git' or 'git_concurrent_push' appears in any file under .github/workflows/, so this end-to-end test is not invoked by any CI job at the recorded revision."
    entry_class: FACT
    evidence:
      - "grep_files('e2e_git|git_concurrent_push', scope='.github/workflows/') -> no matches"
  - statement: "crates/buzz-relay/src/main.rs's 'Start relay' code path is exercised for real, against a live MinIO container started by docker compose, in three CI jobs -- backend-integration (.github/workflows/ci.yml:715, 'Start relay' step), desktop-e2e-integration-shard (.github/workflows/ci.yml:529), and relay-e2e (.github/workflows/ci.yml:886) -- each of which polls the relay's /_readiness endpoint in a loop and fails the job if the relay process exits before becoming ready, which is what a run_conformance_probe failure (BUZZ_GIT_CONFORMANCE_PROBE defaults to enabled) would cause via main's early-return on Err."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:706-745"
      - ".github/workflows/ci.yml:410-580"
      - "crates/buzz-relay/src/main.rs:489-525"
  - statement: "Those three jobs run whenever a pull request or push changes a path the 'changes' job's rust filter matches (crates/**, migrations/**, schema/**, Cargo.toml, Cargo.lock, per .github/workflows/ci.yml:17-45) or on any push, so the production conformance-probe code path is exercised on essentially every relay-affecting change, not only on a manual invocation."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:17-45"
      - ".github/workflows/ci.yml:327-333"
      - ".github/workflows/ci.yml:604-609"
  - statement: "docs/git-on-object-storage.md's 'Mechanized Verification' section states that docs/spec/GitOnObjectStore.tla models concurrent pushers racing to advance the manifest pointer with the CAS action as the sole pointer writer, that TLC checks eight named invariants including Inv_NoFork ('no two published manifests share a parent, a fork = a lost update'), Inv_RefEffectApplied and Inv_RefDerivedFromParent, and that each invariant was shown non-vacuous by a specific mutation that trips it, including a mutation that drops the CAS guard entirely to confirm Inv_NoFork actually catches a fork."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "docs/git-on-object-storage.md records the TLC invocation and outcome as a transcript ('$ tlc GitOnObjectStore.tla -config GitOnObjectStore.cfg' / 'Model checking completed. No error has been found.') and states the model is bounded to Pushers = {p1,p2,p3} and MaxManifests = 3 under a BoundedManifests constraint, describing this explicitly as 'a bounded model check, not an unbounded proof.'"
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "No workflow file under .github/workflows/ invokes tlc or otherwise references GitOnObjectStore.tla, so the TLA+ model check recorded in docs/git-on-object-storage.md is not re-run automatically by CI; it is a point-in-time, manually-run proof artifact, and a later change to the pointer-CAS protocol could drift from the model without any automated check noticing."
    entry_class: INFERENCE
    evidence:
      - "grep_files('tlc|GitOnObjectStore', scope='.github/workflows/') -> no matches"
      - "docs/git-on-object-storage.md"
    confidence: 0.6
  - statement: "docs/spec/GitOnObjectStore.tla and docs/spec/GitOnObjectStore.cfg exist in this repository and were last touched, per git history, by commit 3467a67b2 (introducing the spec) and commit 80e0ab16b (updating it for pack compaction), i.e. the model has been kept in sync with at least one later implementation change rather than abandoned at its original commit."
    entry_class: FACT
    evidence:
      - "docs/spec/GitOnObjectStore.tla"
      - "docs/spec/GitOnObjectStore.cfg"
      - "git_log(docs/spec/GitOnObjectStore.tla) -> 80e0ab16b 'perf(relay): compact Git packs before manifest limits (#2172)', 3467a67b2 'docs: formal spec + machine-checked proof for git refs over object storage (#721)'"
  - statement: "crates/buzz-conformance's own package description names it a runtime trace schema and independent replay checker for MultiTenantRelay.tla, and no file under crates/buzz-conformance/ mentions git or GitOnObjectStore, so buzz-conformance's CI-run replay-fixture gate (part of the infrastructure-free unit-tests job per Justfile) does not cover this node's obligation at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/Cargo.toml"
      - "grep_files('git|GitOnObjectStore', scope='crates/buzz-conformance/') -> no matches"
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-git-push
  - type: references
    target: corpus-standard-test-references
---

# Git object store: manifest-pointer CAS linearizability — test contract

## Purpose and boundary

This node documents **one obligation** of the relay's git-on-object-storage
subsystem (`crates/buzz-relay/src/api/git/`, formally specified in
`docs/git-on-object-storage.md`): that the object-store backend the relay
writes the per-repo manifest *pointer* through provides a linearizable
conditional write, so that concurrent writers racing to advance the same
pointer never produce two winners, a silently-dropped winner, or a
misclassified loser. It covers only this property — content addressing (A1),
read-after-write visibility (A2), the fence between "manifest published" and
"success returned" (Theorem 1), and manifest reconstruction (Theorem 2) are
named where they intersect this obligation's own tests, but are not this
node's subject and would each need their own node.

## Obligation

> Under `N` (`N ≥ 2`) concurrent conditional writes targeting the same
> git-object-store manifest-pointer key — either `If-Match` against the
> pointer's current ETag, or `If-None-Match: *` against a not-yet-created
> key — the backend the relay is admitted against always lets **exactly
> one** writer's `PUT` succeed; every other writer's `PUT` is classified as
> a precondition failure (`GitStore::classify_cas` maps HTTP 412 to
> `CasOutcome::LostRace`), never as a second success and never as an
> unclassified error; and a read issued after the race returns the sole
> winner's body under a fresh ETag, never a losing writer's payload.

This is axiom (A3) from `docs/git-on-object-storage.md`, which the document
itself calls "the single load-bearing backend assumption": the design
substitutes one S3-compatible conditional `PUT` for the advisory-lock/POSIX
`rename()` that reftable-style git backends use, and `architecture/flows/git-push.md`
records the corresponding product decision — there is deliberately no
per-repo advisory lock; two same-repo concurrent pushes each pay the full
hydrate-plus-`receive-pack` cost and rely entirely on this CAS for
correctness at publish time.

## Verifying test(s)

1. **`crates/buzz-relay/src/api/git/store.rs`, `probe::probe_conformance`
   (lines 1176–1192)**, calling `GitStore::run_conformance_probe`'s
   `if_match_race` phase (lines 620–724) and `if_none_match_race` phase
   (lines 726–841). These phases race `race_width` concurrent writers
   against the same pointer state, count how many are classified (excluding
   transport-level drops that never reached the backend), and fail the round
   unless exactly one classified racer wins and the rest lose — the code
   asserting this is at lines 700–722 (`if_match_race`) and lines 792–820
   (`if_none_match_race`). `if_none_match_race` additionally re-reads the
   object afterward and asserts its bytes equal the winner's payload (lines
   821–840).
2. **`crates/buzz-relay/src/api/git/store.rs`, `tests::classify_cas_412_is_lost_race`
   and `tests::classify_cas_other_4xx_bubbles` (lines 935–948)** — unit tests
   of the classification function both race phases and production
   `put_pointer` calls depend on: a 412 must become `LostRace`, and no other
   4xx may be mistaken for one.
3. **`crates/buzz-relay/src/main.rs`, the startup admission gate (lines
   489–525)** — not a `#[test]` function, but the production code path that
   invokes the same `run_conformance_probe` against the relay's actually
   configured backend, unconditionally by default, and treats a probe
   failure as fatal to relay startup.
4. **`crates/buzz-test-client/tests/e2e_git.rs`,
   `git_concurrent_push_one_wins_and_repo_recovers` (lines 412–520)** — an
   end-to-end check of the same property one layer up, at the `git push`
   surface: 8 concurrent clone-and-push clients race to advance one repo's
   `main`; exactly one push must succeed (line 495), the rest must fail
   cleanly (line 496), and a fresh clone afterward must show the winner's
   own commit (line 520).
5. **`docs/spec/GitOnObjectStore.tla` + `docs/spec/GitOnObjectStore.cfg`** —
   a TLA+ model of the same pointer-CAS protocol, model-checked with TLC.
   `Inv_NoFork`, `Inv_RefEffectApplied` and `Inv_RefDerivedFromParent` are the
   invariants that state this obligation's consequence at the abstract
   manifest-history level ("no two published manifests share a parent," "an
   installed push's committed value is the value it proposed," "an install is
   derived from the pointer it actually read"), and `docs/git-on-object-storage.md`
   records each as shown non-vacuous by a mutation that trips it — including a
   mutation that removes the CAS guard entirely, which forks the model.

## How to run it

```bash
# 1. Pure classification unit tests — no infrastructure:
cargo test -p buzz-relay --lib api::git::store::tests::classify_cas

# 2. Live conformance probe against MinIO (per store.rs's own probe-module
#    doc comment):
docker compose up -d minio            # bucket `buzz-git` must exist
BUZZ_GIT_S3_PROBE=1 cargo test -p buzz-relay --lib \
  api::git::store::probe -- --nocapture --test-threads=1

# 3. The production gate runs automatically on every relay boot; observe it
#    by starting the compiled relay against live Postgres/Redis/MinIO
#    (as .github/workflows/ci.yml's "Start relay" steps do) and reading its
#    startup log for "git object-store backend admitted: A3 conformance
#    probe passed", or watching it fail closed if the backend does not
#    satisfy the probe.

# 4. End-to-end, one layer up (requires a live relay + MinIO + git on PATH):
cargo test -p buzz-test-client --test e2e_git \
  git_concurrent_push_one_wins_and_repo_recovers -- --ignored --nocapture

# 5. The TLA+ model, from docs/spec/:
tlc GitOnObjectStore.tla -config GitOnObjectStore.cfg
```

## Current enforcement status

**Mixed, and the honest picture does not collapse to one word cleanly —
each verifying test above sits at a different enforcement tier:**

- **Verified, unconditionally, in CI — but as a production admission gate,
  not as a `#[test]`.** `main.rs`'s startup call to `run_conformance_probe`
  runs, against a real MinIO container, in three CI jobs
  (`backend-integration`, `desktop-e2e-integration-shard`, `relay-e2e`)
  every time a pull request or push touches a rust-affecting path. Those
  jobs poll the relay's readiness endpoint and fail if the relay process
  dies during startup — which a probe failure would cause. This is the one
  tier of this obligation that is genuinely, continuously exercised against
  live infrastructure today.
- **Gated.** `probe::probe_conformance` and
  `e2e_git::git_concurrent_push_one_wins_and_repo_recovers` are real,
  assertion-bearing tests of this exact obligation, but both are
  conditionally skipped by design — the former behind the
  `BUZZ_GIT_S3_PROBE=1` environment variable (with no `#[ignore]`, so a plain
  `cargo test` run executes the function body and returns immediately,
  reporting a pass that exercised nothing), the latter behind
  `#[ignore = "requires live relay + MinIO + git"]`. Neither is invoked by
  any CI job found in this repository at the recorded revision.
- **Not selected by any lane, though nothing gates it.** The pure
  `classify_cas` unit tests need no infrastructure and carry no `#[ignore]`
  or environment gate, yet no CI job or documented `just` recipe runs them —
  `just test-unit`'s only `buzz-relay --lib` invocation is filtered to
  `api::admin::`. This mirrors, for `api::git`, the exact gap that Justfile's
  own comment says once let a broken `api::admin` test ship green before it
  was enumerated explicitly.
- **Formally verified, but as a one-time proof, not a re-run check.** The
  TLA+ model is model-checked and its invariants are shown non-vacuous by
  mutation — this is real mechanized verification of the abstract protocol —
  but no CI job invokes `tlc`, so a future change to the pointer-CAS
  implementation could silently diverge from the model this obligation's
  formal half rests on.

## Limits

- **The conformance probe (tiers 1–2 above) tests the object-store
  backend's behavior, not the relay's own git-handling logic above it.** It
  proves the *backend* honors A1/A3 for small single-object conditional
  writes; it does not exercise `receive-pack`, ref validation, or the pack
  hydration pipeline at all.
- **The probe explicitly does not test conditional multipart upload or
  conditional delete** (`docs/git-on-object-storage.md`'s "Proof surface"
  paragraph) — packs are plain content-addressed `PUT`s without
  conditionals, and garbage collection uses retention/sweep, not `If-Match`
  delete. A backend that satisfies this obligation for single-object CAS
  could still misbehave under either of those, and this node's tests would
  not detect it.
- **`run_conformance_probe`'s race phases drop transport-level failures
  (`Reqwest`/`Http`/`Io`) from the observer set** before asserting "exactly
  one winner," specifically so a flaky socket cannot masquerade as a
  linearizability violation. A backend that silently swallowed *most*
  requests as transport errors could pass a degraded probe run; the report's
  `transport_drops` field surfaces this on the admission log line, but the
  probe does not fail merely because drops are non-zero.
- **The end-to-end test (tier 4) exercises 8 real concurrent contenders
  once**, not the `race_width`/`race_rounds` sweep the unit-level probe
  runs; it is evidence the property holds at the git-push layer for that
  scale, not a substitute for the lower-level race coverage.
- **The TLA+ model (tier 5) is bounded** to three pushers and a maximum of
  three published manifests under a finiteness constraint the model needs to
  terminate at all; `docs/git-on-object-storage.md` states this plainly as
  "a bounded model check, not an unbounded proof" and argues a fourth pusher
  adds no qualitatively new interleaving, without formally proving that
  claim for arbitrarily many pushers.
- **Whether the compiled relay binary that CI actually boots reached the
  admission gate's success branch, versus reaching it via
  `BUZZ_GIT_CONFORMANCE_PROBE=false`, was not independently reproduced
  while authoring this node.** The `Start relay` steps set
  `BUZZ_GIT_PROBE_WRITERS=8` but never set `BUZZ_GIT_CONFORMANCE_PROBE`,
  and `main.rs` defaults that variable to enabled, so the gate should run;
  this was established by reading the workflow file and the default in
  `main.rs` together, not by re-running the CI job and reading its log.

## Scope and omissions

**This node covers** the manifest-pointer CAS linearizability obligation
(A3, and A1's create-only half where the two are tested together), its five
verifying artifacts across unit, production-gate, end-to-end and
formal-model tiers, how to run each, and each tier's actual enforcement
status.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Content-addressing detectability on its own (A1's digest-mismatch behavior, `get_verified`) and read-after-write visibility (A2) | A separate node, not yet written |
| Theorem 1 (durability-ordering / the `finalize_push` single-constructor-seam fence) and Theorem 2 (manifest reconstruction from a published pointer) | Separate nodes, not yet written |
| The git push flow's authentication, tenancy and validation surface (NIP-98, NIP-43, `validate_repo_id`) | `architecture/flows/git-push.md` |
| Pack compaction and cache behavior (`pack_cache.rs`, proactive full-closure compaction) | Not yet a corpus node |
| The TLA+ specification language and methodology in general, independent of this specific model | Issue #1374 (`verification/formal/tla-plus.md`), a sibling task under the same parent PRD, not yet merged at the recorded revision |
| Whether every conformance obligation like this one should become its own corpus node versus staying inside `docs/git-on-object-storage.md` | Not decided here |

**Relationships, checked against the corpus tree on `origin/launchpad`** at
the recorded revision (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`): `corpus-template-test-contract`,
`architecture-containers-relay`, `architecture-flows-git-push` and
`corpus-standard-test-references` are all present, so the four edges above
resolve today. `architecture-containers-object-storage` was considered and
deliberately not linked — it documents `buzz-media`'s S3 client (Blossom
media blobs), a different crate, different bucket and different obligation
from `GitStore`'s manifest pointer; the two share only the general pattern
of sitting on S3-compatible storage. No corpus node for issue #1374
(`verification/formal/tla-plus.md`) exists on `origin/launchpad` yet, so no
edge to it is declared; that is a follow-up once it merges, not an
oversight now.

**Expected but not verified when this node was written:**

- **The live conformance probe (`BUZZ_GIT_S3_PROBE=1`) and the `#[ignore]`d
  end-to-end test were not actually executed while authoring this node** —
  doing so needs a running MinIO (and, for the e2e test, a live relay and
  `git` on `PATH`), which was outside this documentation task's scope. Their
  behavior is established by reading their assertions and gating logic, per
  `standards/test-references.md`'s "test exists / test's assertions read"
  citation shape, not by a reproduced tool-result citation of a pass.
- **The TLA+ model was not re-run with `tlc` while authoring this node.**
  Its stated invariants, mutation table and the "Model checking completed.
  No error has been found." transcript are `docs/git-on-object-storage.md`'s
  own words, cited as `FACT` about what that document says, not as an
  independently reproduced proof run.
- **Whether the CI jobs' compiled relay binary actually reaches and logs
  "git object-store backend admitted" was not confirmed against a live CI
  run's logs** — see the corresponding *Limits* entry above.
