---
id: verification-strategy-traceability
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
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree has no verification/ subtree at all, and all 45 of Feature #617's own child task issues (#1352-#1396, including this node's own #1392) are open -- so this node has no merged sibling verification-surface corpus node to reference, and the mechanisms described below are documented from Buzz's and the corpus tooling's own existing structure, not from any already-merged instance of this Feature's own output."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, agents/, architecture/, capabilities/, development/, layers/, schema/ (excluded from validation), standards/, templates/ -- no verification/ entry"
      - "gh_issue_list('617 in:body', state='all', repo='launchpad-26/buzz') -> 45 issues, #1352 through #1396, all state OPEN, queried 2026-09-01"
  - statement: "launchpad/project-intelligence/corpus/validate.py performs five structural checks over every corpus node -- schema conformance, duplicate ids, unresolved relationship targets, non-finite confidence values, and citation-shape/ownership rules -- and none of those checks opens a cited file's contents or confirms that a named test actually asserts the obligation a node claims it verifies; a citation's path is confirmed to resolve to a real file and nothing more."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "launchpad/docs/corpus/standards/evidence.md states plainly that citation checking is structural and that a FACT citing a real file silent on its subject passes with no notice at all, and launchpad/docs/corpus/AGENTS.md makes the identical statement independently; both name this as the single most important fact about what a passing validation run does not establish."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "launchpad/docs/corpus/templates/test-contract.md's Required Sections 3 and 5 require a node built from it to name its verifying test(s) exactly (file path plus test or module name, not a paraphrase) and to state current enforcement status honestly as one of verified, gated, or pending -- explicitly forbidding a pending obligation from being worded as verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/test-contract.md"
  - statement: "docs/multi-tenant-conformance.md is a prose table of conformance obligations, one row per relay surface (row zero: request community binding is the first), each row stating today's observable behavior, the required scoping change, and an explicit 'Open decision/test' column naming what a test still has to prove."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:12-19"
      - "docs/multi-tenant-conformance.md:38-56"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs states in its own module doc-comment that it mirrors the obligation table in docs/multi-tenant-conformance.md one row per module and calls itself 'the executable form of the conformance contract'; it defines one Rust module per obligation row (row_zero_host_binding, nip11_relay_info, api_tokens_nip98_replay, membership_allowlist, users_profiles_nip05, channelless_global_events_dms, feed_read_side_isolation, channels_membership, workflows, search_fts, pubsub_presence_typing, media_blossom, git_hosting, mesh_agents_cli, audit_log, n1_parity), and a row not yet backed by a landed lane calls a pending_lane(lane, obligation) helper whose body is exactly `todo!(\"conformance pending [{lane}]: {obligation}\")`, so an empty test body can never pass as a completed obligation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1-6"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:67-68"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:74"
  - statement: "conformance_multitenant.rs's own module doc-comment states its A/B isolation tests require a running multi-tenant relay with two host mappings and are #[ignore] by default, invoked as `RELAY_URL_A=... RELAY_URL_B=... cargo test -p buzz-test-client --test conformance_multitenant -- --ignored`; N=1 parity is asserted instead by the existing e2e suites (e2e_relay, e2e_media, e2e_git) staying green, not by a new test in this file."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:8-30"
  - statement: "crates/buzz-conformance/TRACE_SCHEMA.md opens by calling itself 'the contract between the relay's emitter and the independent replay checker,' grounded in docs/spec/MultiTenantRelay.tla, and states that changing the schema requires changing that document in the same commit."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/TRACE_SCHEMA.md:5-9"
  - statement: "crates/buzz-conformance/LIMITS.md states the runtime conformance harness is 'not a proof,' that it establishes only that executions which actually ran with tracing on matched a trace the spec accepts, that coverage is exactly the set of code paths exercised, and that the harness is wired only at the ingest/auth/read accept-reject boundary in crates/buzz-relay/src/handlers/{ingest,req,event}.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:3-6"
      - "crates/buzz-conformance/LIMITS.md:11-12"
  - statement: "buzz-conformance's Cargo.toml states an explicit independence rule: the crate must depend on no production Buzz crate and must never call the relay's own production reducer, so that a bug shared between the relay's emitter and its own checker cannot hide from both by construction."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/Cargo.toml:9-21"
  - statement: "Justfile's unit-test recipe runs `cargo nextest run -p buzz-conformance` unconditionally, alongside a comment stating the crate's checker and fixtures need no infrastructure; the repository's `unit-tests` CI job (name: Unit Tests, in .github/workflows/ci.yml) runs `just test-unit` on every push and on pull requests that changed Rust paths, so this mechanism's tests execute in ordinary CI, not only on request."
    entry_class: FACT
    evidence:
      - "Justfile:339-343"
      - ".github/workflows/ci.yml:125-146"
  - statement: "Querying the GitHub API directly for the launchpad branch found no enforced required check: the legacy branch-protection endpoint returns 404 (not configured), and the branch's rulesets endpoint returns an empty list, so no ruleset enforces any status check either -- both mechanisms were checked, not only the one ADR-0020 originally reported."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad/protection') -> 404 Not Found, queried 2026-09-01"
      - "gh_api('repos/launchpad-26/buzz/rules/branches/launchpad') -> [] (empty ruleset list), queried 2026-09-01"
  - statement: "A repository-wide search for scripts or tools naming both docs/multi-tenant-conformance.md and conformance_multitenant.rs found only the two files themselves plus two unrelated source files (crates/buzz-auth/src/nip98.rs, crates/buzz-relay/src/api/bridge.rs) that reference the conformance document in an incidental comment; no diffing, linting or consistency-checking tool comparing the document's row list against the test file's module list was found."
    entry_class: FACT
    evidence:
      - "grep_recursive('multi-tenant-conformance', include=['*.py','*.sh','*.mjs','*.rs']) -> docs/multi-tenant-conformance.md, crates/buzz-test-client/tests/conformance_multitenant.rs, crates/buzz-auth/src/nip98.rs, crates/buzz-relay/src/api/bridge.rs; the last two are single incidental comment references"
  - statement: "Given that no tool was found comparing the obligation table's rows against the test file's modules (previous entry) and that launchpad/project-intelligence/corpus/validate.py never reads any path outside launchpad/docs/corpus (so it cannot be that check either), a row renamed, removed, or added on one side of the docs/multi-tenant-conformance.md / conformance_multitenant.rs pairing without the matching change on the other side would not be caught by any automated check in this repository -- only by a human reading both documents side by side."
    entry_class: INFERENCE
    evidence:
      - "grep_recursive('multi-tenant-conformance', include=['*.py','*.sh','*.mjs','*.rs']) -> docs/multi-tenant-conformance.md, crates/buzz-test-client/tests/conformance_multitenant.rs, crates/buzz-auth/src/nip98.rs, crates/buzz-relay/src/api/bridge.rs"
      - "launchpad/project-intelligence/corpus/validate.py"
    confidence: 0.8
  - statement: "launchpad/docs/corpus/standards/test-references.md's MUST 6 forbids wording a test's mere existence as evidence that the behavior it exercises is currently correct, and its 'Flakiness and staleness' section documents that this repository's desktop E2E suite retries a failed test up to twice in CI, that a retried-then-passed test is invisible in the ordinary green summary, and that desktop/scripts/summarize-flaky-tests.mjs is the only tool that surfaces it -- scoped to desktop E2E only, with no equivalent signal found for Rust `cargo nextest` runs."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/test-references.md"
  - statement: "Issue #1392's definition of done requires that every substantive factual claim be traceable to current code, test, specification, accepted decision, migration/configuration, or attributed GitHub evidence, that FACT/INFERENCE/TEAM_KNOWLEDGE not be conflated, and specifically that this node define traceability expectations from claims/specs to tests, state risks/quality goals and which verification levels address them, define environments/data-fixtures and gating/advisory behavior, and name known non-coverage and flakiness/quarantine policy where applicable."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1392 definition of done"
  - statement: "Issue #1392 directs that this node be authored from launchpad/docs/corpus/templates/test-strategy.md (the test-strategy template) rather than templates/test-contract.md, even though this node's subject -- how a claim is traced to its verifying test across the corpus and across Buzz's own existing conformance precedents -- is a cross-cutting property of the verification surface rather than a single system or component's own multi-tier test plan, which is the shape templates/test-strategy.md's own 'Purpose' section describes."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1392 task body (title and objective) and the corpus-batch-author dispatch instructions for this task"
relationships:
  - type: implements
    target: corpus-template-test-strategy
  - type: references
    target: corpus-agents
  - type: references
    target: corpus-standard-evidence
  - type: references
    target: corpus-standard-test-references
  - type: references
    target: corpus-template-test-contract
---

# Traceability — verification strategy

## Scope

This node covers **traceability**: whether a requirement or obligation can be traced
from its source (a GitHub issue, a design document, an accepted decision, or a
conformance-table row) through implementation to the specific test(s) that verify it,
and, for each mechanism this repository actually has for making that trace, whether the
trace is checked automatically or only by convention and review. The scope is this
repository's own real mechanisms as they exist at the recorded revision — the
documentation corpus's own evidence-and-node structure, and Buzz's two existing
obligation-plus-executable-test precedents (`docs/multi-tenant-conformance.md` and
`crates/buzz-conformance`) — not a proposal for a mechanism that does not yet exist.

**This node does not evaluate whether any single obligation is actually true.** That is
each obligation's own `test-contract` node's job, once one is written (see *Deliberately
out of scope* below); this node evaluates whether the *linking* mechanism between a
claim and its test exists and is checked, not the claim's own correctness.

## Note on adapting this template's required table

`launchpad/docs/corpus/templates/test-strategy.md`'s *Purpose* section describes a node
built from it as answering, for **one system or component**, "what is the plan for
testing it, tier by tier" — unit, integration, relay E2E, and so on, each level
distinguished by the infrastructure it needs (`ADR-0020`'s own axis). Traceability is
not that: it is a property that cuts across every level, asking whether a *claim* —
wherever it is checked — can be followed back to its source and forward to a concrete
verifying test. There is no single system or component in scope here, and no
infrastructure-footprint axis to tier by.

Rather than force this subject into levels it does not have, the required table below
keeps the template's actual required content — one row per named thing, its purpose,
what it needs to run, the command that invokes or checks it, and whether it is
currently gated — and renames the axis from **test level** to **traceability
mechanism**: a named, real way this repository already links a claim to a test. This is
the same move `templates/test-contract.md` makes when it rejects Pact's
consumer/provider vocabulary in favor of this repository's own real precedents rather
than importing a shape that does not fit; here the departure is in the row's subject,
not the industry model.

## Traceability mechanisms

| Mechanism | What it links | Precondition / infrastructure | How to check it today | Enforcement status |
|---|---|---|---|---|
| Corpus evidence ledger | A claim in any corpus node's body → the citation(s) supporting it | None | `python3 launchpad/project-intelligence/corpus/validate.py` | **Enforced in CI**, but structural only: confirms a citation's path resolves to a real file; never confirms the file supports the statement. |
| Task-issue DoD → corpus node | A GitHub task issue's Definition-of-done checklist → the merged node's front matter and body | None | Manual: a reviewer (or the `corpus-review` skill) reads the node against the issue's own DoD text | **Review-only.** No automated check compares a node's content against its own issue's DoD. |
| `test-contract` node → named verifying test | One testable obligation → the specific test file/function that verifies it | None to declare; the named test's own infrastructure need (unit/integration/E2E) if actually run | Per-node, from `templates/test-contract.md` Required Section 4's copy-pasteable command | **Structural only** (same as the evidence ledger row), and **not yet instantiated**: zero `verification`-type nodes exist on `origin/launchpad` at the recorded revision, so this mechanism is fully specified by its template but has no real example to check yet. |
| Obligation table ↔ executable module (`docs/multi-tenant-conformance.md` ↔ `conformance_multitenant.rs`) | One relay-surface obligation row → one Rust test module | The A/B isolation modules need a live, two-host multi-tenant relay (`RELAY_URL_A`/`RELAY_URL_B`); the doc-to-module mapping itself needs nothing | `cargo test -p buzz-test-client --test conformance_multitenant -- --ignored` | **Partially enforced.** An unlanded obligation's module is `#[ignore]`d and calls `pending_lane(...)` → `todo!()`, so a stub can never silently pass. Nothing diffs the table's row list against the module list (see evidence above), so a row added, renamed or dropped on one side without the other would not be caught mechanically — only by a reader comparing both. |
| Trace schema ↔ independent replay checker (`TRACE_SCHEMA.md` ↔ `checker.rs`/`transitions.rs`) | A documented event-trace schema → a from-scratch reimplementation of the TLA+ spec's transition relation | None — in-process, no infrastructure | `cargo nextest run -p buzz-conformance` (also `cargo test -p buzz-conformance --lib` / `--test replay_fixtures`) | **Runs unconditionally in CI**: this recipe is part of `just test-unit`, which the `unit-tests` job runs on every push and on pull requests touching Rust paths. It is **not a required status check**: the `launchpad` branch has neither branch protection nor an active ruleset (verified directly, see evidence). |
| GitHub issue/PR linkage | A task issue's existence → the pull request that closes it | None | `gh issue view <n>`, `gh pr view <n> --json closingIssuesReferences` | **GitHub-native**, but not a test-to-claim check at all — it links an issue to a code change, not an obligation to a verifying test, and this repository's own experience is that `closingIssuesReferences` only populates against the default-branch merge target. |

## Current enforcement

Restating the table's rightmost column plainly, because `templates/test-strategy.md`'s
Required Section 3 asks for that explicitly: **no mechanism above is a required status
check today.** Two mechanisms (the corpus evidence ledger, and `buzz-conformance`'s
replay checker) run unconditionally in ordinary CI; one (the obligation-table/module
pairing's `#[ignore]`d rows) runs only on request against live infrastructure; the
task-issue-DoD-to-node link and the doc-to-module row correspondence are checked by
nobody but a reviewer. Every one of these runs and passes today at the recorded
revision — "runs in CI" is not the same claim as "blocks a merge if it fails," and this
repository's `launchpad` branch blocks nothing today (verified directly against the
GitHub API, not inherited from an older document's finding — see evidence).

## Deliberately out of scope

- **Whether any specific claimed obligation is currently true.** That is the subject a
  real `test-contract` node takes on, one obligation at a time, once one exists; this
  node names the linking mechanism, not any claim that travels through it.
- **The general, per-system shape of a multi-tier test strategy** (unit → integration →
  E2E, by infrastructure footprint). That is `test-strategy-<system>` nodes generally,
  and this Feature's own sibling task (`document verification/strategy/test-levels.md`,
  issue #1391) specifically — open and unmerged at the recorded revision, so this node
  does not reference it (see *Relationships* below).
- **Building an automated tool that diffs `docs/multi-tenant-conformance.md`'s row list
  against `conformance_multitenant.rs`'s module list, or a corpus-wide checker that
  opens a cited test file and confirms it asserts the claim above it.** Both gaps are
  named honestly in the table above. The risk accepted by leaving them unbuilt is the
  one this node's own evidence demonstrates is live: a claim and its test can drift
  apart with nothing but a reviewer's attention standing in the way. Building either
  checker is implementation work outside a documentation task's scope, not something
  this node judges unnecessary.
- **The formal-verification lane beyond the one precedent already covered.** `docs/spec/
  MultiTenantRelay.tla` and the wider `verification/formal/*` subject (this Feature's
  own sibling tasks, e.g. issue #1371) are a distinct, larger topic; this node cites
  `TRACE_SCHEMA.md`/`checker.rs` only as a second worked example of the
  obligation-plus-test shape, not as a treatment of formal verification generally.

## Relationships

**Checked against `origin/launchpad`'s corpus tree, not this worktree's**, per
`AGENTS.md`'s own required check: `corpus-agents`, `corpus-standard-evidence`,
`corpus-standard-test-references`, `corpus-template-test-contract` and
`corpus-template-test-strategy` are all present on `origin/launchpad` at the recorded
revision (see the ledger's provenance entry), so all five are valid targets.

- `implements: corpus-template-test-strategy` — this node is the concrete realization
  of that template, per `relationships.schema.json`'s own directionality for
  `implements` ("a template instance of a standard").
- `references: corpus-agents` — this node follows `AGENTS.md`'s evidence and citation
  rules throughout, as any corpus node does.
- `references: corpus-standard-evidence` — the claim that citation checking is
  structural (used repeatedly above) is stated authoritatively there.
- `references: corpus-standard-test-references` — the flakiness/staleness discussion
  and the test-citation shape rules this node's table relies on are that standard's
  subject, not restated here.
- `references: corpus-template-test-contract` — the `test-contract` mechanism named in
  the table above is that template's own subject; this node names that the mechanism
  exists and is unused so far, without restating its required sections.

**No relationship is declared to any Feature #617 sibling task's node** (e.g. a future
`verification-strategy-test-levels` for issue #1391, or any `verification/*` node this
same batch may produce). All 45 of this Feature's own child issues are open at the
recorded revision (see the ledger), so none has a merged node yet to target — declaring
one now would validate on this branch and become a hard error on `origin/launchpad`,
the exact hazard `AGENTS.md` step 9 names. The first of those siblings to merge is the
moment to revisit this.

## Scope and omissions

**This node covers** what traceability means for this repository (claim → source →
verifying test), the real mechanisms that provide it today inside the corpus and
inside Buzz's own conformance tooling, each mechanism's actual enforcement status
stated honestly (structural-only, review-only, CI-run-but-not-required, or fully
manual), what those mechanisms are deliberately not built to do, and the known
flakiness/staleness caveat that already applies to citing any test as evidence at all.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Whether any specific obligation (multi-tenant or otherwise) is currently true | The obligation's own future `test-contract` node |
| The general multi-tier test-strategy shape for one system or component | `test-strategy-<system>` nodes generally; this Feature's own `verification/strategy/test-levels.md` (issue #1391), open and unmerged |
| Formal verification as a subject in its own right | `verification/formal/*`, this Feature's own sibling tasks (e.g. issue #1371), open and unmerged |
| The `confidence` field's meaning and bands | `launchpad/docs/corpus/standards/confidence.md` |
| Test citation shapes, flakiness and staleness discipline in general | `launchpad/docs/corpus/standards/test-references.md` |
| Creating, updating and retiring any corpus node | `launchpad/docs/corpus/AGENTS.md` |
| Whether a recorded revision may stay put across edits | #1321, unresolved as of `AGENTS.md`'s own text |

**Expected but not verified when this node was written:**

- **No real `test-contract` node exists yet to check the mechanism's third table row
  against.** Whether `templates/test-contract.md`'s required sections actually produce
  a checkable, unambiguous obligation-to-test link in practice — as opposed to in the
  template's own worked skeleton — is untested until the first such node is written.
- **Whether any Feature #617 sibling task currently being worked in a parallel,
  unpushed worktree will independently declare a relationship this node should have
  matched, or vice versa, was not checked** — per-issue branches in this batch are
  local-only until the Feature's integration phase, so no sibling's content was visible
  to check against.
- **The `cargo nextest run -p buzz-conformance` and `conformance_multitenant.rs`
  commands named above were read from the Justfile, the CI workflow and the test
  file's own doc-comments; they were not executed as part of authoring this node.**
  Whether they currently pass is not asserted by any claim above.
- **Whether GitHub's `closingIssuesReferences` behavior (named in the GitHub
  issue/PR linkage row) still holds exactly as this repository's own prior experience
  recorded it was not independently re-verified against a live PR for this task.**
