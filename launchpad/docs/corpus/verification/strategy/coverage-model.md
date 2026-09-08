---
id: verification-strategy-coverage-model
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "ADR-0020 adopts upstream's testing methodology unchanged as five levels separated by the infrastructure they need: unit (`just test-unit`, no infrastructure), integration (`just test`, Postgres and Redis started automatically), relay E2E (`cargo test -p buzz-test-client -- --ignored`, needs a running relay), desktop E2E smoke, and desktop E2E integration; every test needing a live relay is marked `#[ignore]` so a plain `cargo test` is safe everywhere and E2E execution is opt-in."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020 uses the word 'coverage' four times, and in every occurrence it means the qualitative question of which surfaces have tests at all (unit coverage of a subsystem, a non-coverage list of untested surfaces, coverage of the cohort's own added surface) -- never a measured code-coverage percentage or an instrumentation tool. The word 'tarpaulin', 'llvm-cov', 'grcov', 'codecov', 'istanbul' or 'nyc' does not appear anywhere in the document."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "No code-coverage measurement tool is configured anywhere in this repository: a search of the root Justfile, every file under .github/workflows/, Cargo.lock, every crate's Cargo.toml under crates/, desktop/package.json, and the repository root for cargo-tarpaulin, cargo-llvm-cov, grcov, codecov, nyc, istanbul, or a `--coverage` flag on `flutter test` returns zero matches; no `.codecov.yml`, `codecov.yml`, or `.coveragerc` file exists at the repository root."
    entry_class: FACT
    evidence:
      - "Justfile"
      - ".github/workflows/ci.yml"
      - "Cargo.lock"
      - "desktop/package.json"
      - "grep_search('tarpaulin|cargo-llvm-cov|grcov', scope='crates/*/Cargo.toml, every crate manifest') -> no matches, checked 2026-09-01"
  - statement: "No code-coverage measurement tool is configured anywhere in this repository, including forms this node's own search could not directly confirm the absence of -- a coverage integration wired purely through a GitHub App (for example Codecov installed as an app rather than a repository config file) or a per-crate Cargo.toml this search missed -- so the claim rests on the files actually opened rather than on exhaustive enumeration of every possible integration point."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - ".github/workflows/ci.yml"
      - "Cargo.lock"
      - "desktop/package.json"
      - "README.md"
    confidence: 0.6
  - statement: "ADR-0020 records that `required_status_checks` on the `launchpad` branch returns 404 (not configured), so upstream's own words -- \"PRs that fail `just ci` will not be merged\" -- are an honour system rather than an enforced gate, and that ADR-0019 already ruled on what may gate and deferred the enforcement question to the CI/CD pipeline programme rather than reopening it here."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020 names, as deliberate rather than accidental non-coverage, that the web client has zero tests and that agent behaviour has no deterministic harness, and tracks both under issue #290 rather than leaving them silently absent."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020 measured, on 2026-08-21 at launchpad tip db4305a4a, 4,615 Rust test functions across 28 of 30 crates, 37 integration test files, 19 relay E2E suites, 146 Playwright specs, 481 desktop *.test.mjs files, and 123 Flutter tests, and states this count explicitly as a snapshot at that revision rather than a timeless fact -- a large, quantified test population whose pass/fail status is asserted at every level, with no line, branch or function coverage percentage measured over any of it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020 states desktop's CI retry policy as two retries in CI and zero locally, and that desktop/scripts/summarize-flaky-tests.mjs exists specifically because that retry policy previously hid a real race condition in stream.spec.ts behind a green run for months; this is a flakiness-visibility mechanism for pass/fail status, not a coverage mechanism, and it exists for the desktop Playwright suite only."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
      - "desktop/scripts/summarize-flaky-tests.mjs"
  - statement: "No repository-wide test-quarantine mechanism exists today: ADR-0020 raises quarantine only as a consequence that 'becomes necessary the moment checks are required' -- a stated future need, not a policy already in force -- and a search of Rust source, CI workflow files, and Research notes for the word 'quarantine' returns no hit that names a test-exclusion or flaky-test-isolation policy for any of the five ADR-0020 levels."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
      - "grep_search('quarantine', scope='Rust source, .github/workflows, launchpad/Research') -> hits only in macOS Gatekeeper file-quarantine code/docs, a corrupt-identity-key quarantine routine, git object-store quarantine, and duplicate-sequence quarantine in an unrelated data-processing test; none names a test-exclusion or flaky-test-isolation policy, each hit opened and read, checked 2026-09-01"
  - statement: "At this node's recorded revision, the corpus tree on origin/launchpad contains no node of type verification and no node whose id begins with verification-strategy or verification-contract, so no existing corpus node documents test levels, a coverage model, or any other verification-surface content this node could reference or duplicate."
    entry_class: FACT
    evidence:
      - "git_ls_tree('origin/launchpad', 'launchpad/docs/corpus') -> no file under a verification/ directory and no front matter with type: verification, checked 2026-09-01 at commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "crates/buzz-cli/TESTING.md documents a manual, step-by-step live-relay runbook distinct in kind from the automated just test-unit / just test / --ignored levels, including a step that inserts fixture members directly into an isolated local database and then drives discovery and messaging through the release CLI and relay to prove boundaries a DB-only test cannot."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/TESTING.md"
  - statement: "Desktop E2E specs under desktop/tests/e2e/ import installMockBridge from a shared helper to install a mocked Tauri bridge before a test runs, and CLAUDE.md documents a --messages JSON fixture format (an array of objects naming channelName and content plus optional fields) injected into a running mock session via __BUZZ_E2E_EMIT_MOCK_MESSAGE__."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/agent-access-warning.spec.ts"
      - "CLAUDE.md"
  - statement: "Issue #1388 (this task, under parent PRD #617) names the objective as a test strategy node for 'coverage model' specifically, distinct from the sibling issues under the same PRD that produce other verification-surface nodes, and its Definition of Done requires stating risks/quality goals and which verification levels address them, defining environments/fixtures/gating, defining traceability expectations from claims to tests, and naming known non-coverage and flakiness/quarantine policy where applicable."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1388 definition of done"
  - statement: "This node is built from templates/test-strategy.md rather than templates/test-contract.md, per this task's own instruction that issue #1388's objective names a test strategy node even though most sibling issues under the same PRD produce test contract nodes; templates/test-strategy.md itself states that a node built from it carries type: verification, and requires a scope statement, a levels table naming purpose/infrastructure/command/gating per level, honestly-stated per-level enforcement status, and a statement of what is deliberately out of scope and why."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1388 task brief, cross-checked against launchpad/docs/corpus/templates/test-strategy.md's own 'Required sections'"
---

# Buzz — coverage model

## Scope

This node covers **Buzz's code-coverage model**: whether code coverage (line, branch, or
function coverage measured by an instrumentation tool) is measured anywhere in this
repository, at which of ADR-0020's five test levels, by what tooling, and whether any of
it gates a merge. It covers the whole repository, because coverage tooling — unlike a
test suite — is typically wired in once, at the CI-workflow or build-tooling level, rather
than per crate or per client.

This node does **not** cover ADR-0020's overall test-level methodology on its own terms
(which levels exist, what each needs to run, what each level's own pass/fail gating is)
except as background this coverage model sits inside. A node documenting that broader
subject directly would be `verification-strategy-test-levels` or similar; no such node
exists in the corpus at this node's recorded revision (checked below, under
*Relationships*), so this node states the relevant parts of ADR-0020's level structure
inline rather than deferring to a sibling that does not yet exist.

**The central claim of this node, stated plainly and up front:** Buzz has no code-coverage
model today. No tool measures line, branch, or function coverage at any of the five test
levels ADR-0020 adopts, no CI job computes or reports a coverage number, and nothing gates
a merge on one. What ADR-0020 calls "coverage" is a different, qualitative idea — which
surfaces have tests written for them at all — and that distinction is the substance of
this node, not a caveat to it.

## Levels

The table below is ADR-0020's own five levels. The **Coverage tooling** column is this
node's addition and is where the central claim lives: every row reads "none."

| Level | Purpose | Infrastructure | Command | Gating | Coverage tooling |
|---|---|---|---|---|---|
| Unit | Exercise a single crate's logic in isolation | None | `just test-unit` | Runs unconditionally in CI; not a required status check (see *Current enforcement*) | None |
| Integration | Exercise cross-crate behavior against real Postgres and Redis | `localhost` Postgres and Redis, started automatically | `just test` | Runs unconditionally in CI when the relevant `changes` filter fires; not a required status check | None |
| Relay E2E | Exercise the relay's externally observable protocol behavior against a running relay process | A live, separately started relay | `cargo test -p buzz-test-client -- --ignored` | `#[ignore]`'d by default; opt-in, not run by a plain `cargo test` and not a required status check | None |
| Desktop E2E smoke | Exercise the desktop UI against a mocked Tauri bridge, no live relay | A built E2E frontend bundle (`pnpm build:e2e`) and a mock bridge; no relay | `pnpm test:e2e:smoke` | Runs in CI per the `desktop` change filter; not a required status check | None |
| Desktop E2E integration | Exercise the desktop UI against a real relay | A built E2E frontend bundle and a live relay | `pnpm test:e2e:integration` | Runs in CI per the relevant change filter; not a required status check | None |

**Why every cell in that last column is "none," restated as a mechanism rather than an
absence:** `cargo test`, `cargo nextest`, Playwright, and `flutter test` as invoked by the
commands above report only pass/fail per test. None of the invocations anywhere in
`Justfile` or `.github/workflows/ci.yml` add a coverage-instrumenting wrapper
(`cargo tarpaulin`, `cargo llvm-cov`, `grcov`) or a coverage flag (`flutter test
--coverage`, an Istanbul/nyc-instrumented Vitest or Jest run). Nothing produces a `.lcov`,
`cobertura.xml`, or equivalent artifact for any level, and nothing uploads one to Codecov
or an equivalent service.

## Environments and fixtures

The *Infrastructure* column above states each level's environment. Data and fixtures, at
the level of detail this coverage-scoped node can support without restating a full test
strategy: integration tests run against an ephemeral Postgres and Redis started
automatically (`just test`), with pending SQL migrations applied before the suite runs;
desktop E2E specs seed state through `installMockBridge` and a documented `--messages`
JSON fixture format (`channelName`/`content` plus optional fields) injected via
`__BUZZ_E2E_EMIT_MOCK_MESSAGE__`; and `crates/buzz-cli/TESTING.md` documents a manual
live-relay runbook, distinct from the automated levels above, that inserts fixture data
(for example a roster beyond 1,000 members) directly against an isolated local database
for scenarios DB-only tests cannot prove. This node does not inventory per-crate Rust unit
or integration test fixtures (factories, seed builders, or golden files) beyond that —
doing so belongs to a full test-levels strategy node, not to this one's coverage-model
scope, and is named as a gap in *Scope and omissions* below.

## Risks and quality goals

**The risk this coverage-model finding names is not "tests might be wrong."** ADR-0020's
own pass/fail test population is large (4,615 Rust test functions alone, per the citation
above) and each of the five levels in the table above targets a real, stated risk: unit
catches a single crate's logic regressing in isolation; integration catches cross-crate
and cross-subsystem behavior that only breaks against real Postgres and Redis; relay E2E
and both desktop E2E levels catch externally observable protocol and UI regressions that
no in-process test can see. **What no level's tooling can currently answer is a narrower
but different question: how much of the code those tests actually execute.** A test suite
can grow indefinitely in count while a specific function, branch, or error path is never
once executed by any of it, and today nothing in this repository would surface that
silently-untested branch as a number, a report, or a merge check — the only way to find
one is to go looking for it directly. That is the quality goal a coverage model exists to
serve elsewhere, and it is the one this repository's testing methodology does not
currently pursue.

## Current enforcement

**No level in the table above has coverage enforcement, because no level has coverage
measurement.** There is nothing to state a gating status for.

**Test *pass/fail* enforcement, for contrast, and stated with the same honesty ADR-0020
uses:** `required_status_checks` on the `launchpad` branch returns 404 — not configured —
so no CI job, coverage or otherwise, is a required status check that blocks a merge today.
Upstream's own stated intent ("PRs that fail `just ci` will not be merged") is an honour
system, not an enforced gate, per ADR-0020's own finding. ADR-0019 already ruled on what
may gate at all and deferred enforcement to a separate CI/CD pipeline programme; this node
does not reopen that question and a coverage gate specifically is not a live proposal
anywhere this node's evidence reaches.

## Deliberately out of scope, and why

**This is the section where a coverage model built by design and a gap that has not been
named are easy to conflate, and this node does not conflate them.** ADR-0020 explicitly
lists two deliberate non-coverage items — the web client has zero tests, and agent
behavior has no deterministic harness — tracked under issue #290 as chosen omissions
rather than oversights. **Code-coverage measurement is not on that list.** Nothing in
ADR-0020, in the CI workflows, or in the Justfile states that coverage instrumentation was
considered and rejected, for a stated reason, at any level. The honest reading is that the
absence of a coverage model is an **unaddressed gap**, not a decision ADR-0020 or any other
accepted record made — and this node does not manufacture a rationale ADR-0020 never gave.

What *is* named, and does function like a deliberate coverage-adjacent choice: the
`#[ignore]` convention keeps relay and desktop-integration E2E tests out of the default
`cargo test` run so that a plain build stays fast and safe everywhere, at the accepted cost
that those tests (and whatever they would have exercised) run opt-in only. That is a
choice about *which tests run by default*, not about *coverage measurement*, and conflating
the two would misstate ADR-0020.

## Traceability from claims to tests

**No corpus mechanism yet exists to trace a specific claim to the specific test that
verifies it.** `templates/test-contract.md` (id `corpus-template-test-contract`) is the
shape the corpus has adopted for exactly that unit — one testable obligation paired with
the test(s) that verify it — but at this node's recorded revision no node has been
authored from that template (see *Relationships* below for what was checked). Until such
nodes exist, traceability for any specific claim in this repository is established the
way `launchpad/docs/corpus/standards/test-references.md` (id
`corpus-standard-test-references`) describes citing a test as evidence: a bare repository
path or `path:line` citation to a test file, checked structurally (the file exists) but
never checked for whether it actually proves the claim above it. That is a citation
discipline, not a traceability *mechanism* — nothing in this repository maintains a
requirements-to-tests matrix, and this node does not claim one exists.

**Coverage measurement and traceability are two different questions, and this repository
has an answer to neither today.** A coverage percentage would answer "how much of the code
executed during some test run"; a traceability matrix would answer "which specific test
proves this specific claim." Neither exists. Recording both absences in one place is this
node's own scope choice, made because a reader asking "is this covered?" is usually asking
about one of the two and needs to be told which one has no answer.

## Relationships

**Checked, not assumed absent**, per `launchpad/docs/corpus/AGENTS.md`'s own guidance
against a false "nothing to point at" justification. At this node's recorded revision, the
corpus tree on `origin/launchpad` contains no node of `type: verification` and no node
whose `id` begins with `verification-` — confirmed by listing every file under
`launchpad/docs/corpus/` on `origin/launchpad` and finding none under a `verification/`
directory. `corpus-template-test-contract` and `corpus-standard-test-references` both
exist and are cited above as evidence, but neither is a natural `relationships` target for
this node: the first is a template describing an authoring shape (`type: governance`), and
`templates/test-strategy.md` itself states that a strategy node's edge belongs to the
*instances* built from that template once they exist, not to the template document; the
second is a citation-discipline standard this node followed rather than a subject this
node's own claims are about.

**None declared.** The nearest candidate — a `references` edge from this node to a future
`verification-strategy-test-levels` node describing ADR-0020's overall level structure —
cannot be declared because no such node exists yet on the merge target. The moment one
merges, this node's *Levels* section should be trimmed to defer to it rather than
restating ADR-0020's level structure inline, and that edge should be added then.

## Scope and omissions

**This node covers** whether Buzz measures code coverage today, at which of ADR-0020's
five test levels, with what tooling, and whether any of it gates a merge — concluding that
no coverage model exists at any level, and that this absence is an unaddressed gap rather
than a decision any accepted record made. It also covers the traceability question
(whether a claim can be traced to the specific test that verifies it) and Buzz's current,
narrow flakiness-visibility and quarantine posture, because the issue's Definition of Done
asks this node to name both alongside the coverage-tooling finding.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ADR-0020's overall five-level test methodology, in its own right | `launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md`, and a future `verification-strategy-test-levels`-shaped node, not yet authored |
| One testable obligation and the specific test that verifies it | `templates/test-contract.md` (`corpus-template-test-contract`); no instance node exists yet |
| The citation mechanics for how any corpus node cites a test as evidence | `launchpad/docs/corpus/standards/test-references.md` (`corpus-standard-test-references`) |
| Whether or how to adopt a coverage tool | Not decided by any accepted record this node found; a gap, not a ruling |
| What may gate a merge at all, and the CI/CD pipeline programme | `launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md`, deferred further by ADR-0020 |
| Additive testing work closing the cohort's own gaps | issue #290 |
| Creating, updating and retiring any corpus node, including this one | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether a coverage tool is configured through a channel this node's file-based search
  cannot see** — a GitHub App integration (Codecov, Coveralls) wired through repository
  settings or an organization-level installation rather than a checked-in config file or
  workflow step. This node's finding rests on `Justfile`, `.github/workflows/*.yml`,
  `Cargo.lock`, `desktop/package.json`, and the repository root; it does not reach GitHub's
  own App/Integrations configuration for this repository, which no file in the repository
  exposes.
- **Whether any cohort member runs a coverage tool locally, ad hoc, outside of anything
  committed to the repository** — this node can only speak to what is configured and
  checked in, not to undocumented local practice.
