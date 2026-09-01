---
id: verification-strategy-risk-model
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
  - statement: "Issue #1390's own objective text names this document 'the single canonical test strategy node for risk model' at launchpad/docs/corpus/verification/strategy/risk-model.md, which is why this node is authored against templates/test-strategy.md rather than templates/test-contract.md."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1390, Objective section"
  - statement: "ADR-0020 (Accepted, 2026-08-21) adopts upstream's testing methodology unchanged: five levels separated by the infrastructure they need -- unit (just test-unit, no infrastructure), integration (just test, Postgres and Redis started automatically), relay E2E (cargo test -p buzz-test-client -- --ignored, needs a running relay), desktop E2E smoke, and desktop E2E integration -- and states this is an adoption of an existing scheme rather than a newly designed one."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020's own Decision section states plainly that the cohort adopted rather than designed a testing methodology, and that this was a deliberate choice reasoned from three findings, none of which mentions organizing test investment by risk score or severity classification."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020 records, as of 2026-08-21, that required_status_checks on the launchpad branch returns 404 (not configured), so upstream's own 'PRs that fail just ci will not be merged' is an honour system rather than an enforced gate, and that ADR-0019 already ruled on what may gate and deferred enforcement to the CI/CD pipeline programme."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "Re-run on the recorded revision, both required-status-check surfaces for the launchpad branch of launchpad-26/buzz are still empty: the legacy branch-protection endpoint returns 404 and the repository's rulesets list is an empty array, so ADR-0020's 2026-08-21 finding still holds today and no level in this document's Levels table is a required check."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad/protection') -> 404 Not Found, run 2026-09-01 against commit 473205a7457b208455f188847bfb27b01aa83cac"
      - "gh_api('repos/launchpad-26/buzz/rulesets') -> [], run 2026-09-01 against commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "A case-insensitive grep for 'risk' across docs/multi-tenant-conformance.md, TESTING.md, ADR-0020, and CONTRIBUTING.md returns exactly one hit, in ADR-0020's Security implications section, about CI logs being a public disclosure surface -- not about scoring or prioritizing test investment by product risk -- so none of these documents describes a risk-based test-prioritization scheme."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('risk', paths=['docs/multi-tenant-conformance.md','TESTING.md','launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md','CONTRIBUTING.md']) -> one match, launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md:112, run 2026-09-01 against commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "docs/multi-tenant-conformance.md is a source-vs-model conformance checklist for the host-derived community (tenant) boundary: one table row per architectural surface (row-zero host binding, NIP-11, API tokens, membership, users, channel-less events, channels, workflows, search, pub/sub, media, git hosting, mesh/agents, audit log), each row naming the surface's tenant source, required DB/index scope, auth/fan-out effects, and an explicit single-community compatibility check plus an open decision/test column."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "docs/multi-tenant-conformance.md's own Migration gates section requires automated gates before multi-tenant mode is admitted, covering per-tenant DB/RLS scoping, community-scoped lookups, community-scoped cache/search/pub-sub keys, TenantContext resolution before tenant-affecting handling, and N=1 conformance tests -- a gate list scoped entirely to this one surface, not a repository-wide risk register."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs is a 2,749-line test file whose own module doc-comment states it 'mirrors the obligation table in docs/multi-tenant-conformance.md, one row per module' and is the executable form of that conformance contract; it is marked #[ignore] by default and requires a running multi-tenant relay with two host mappings, run as cargo test -p buzz-test-client --test conformance_multitenant -- --ignored."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "crates/buzz-test-client/tests/nip42_host_binding_live.rs is a second dedicated multi-tenancy test file, requiring a running multi-tenant relay with two seeded communities, with every test function marked #[ignore = \"requires two-host multi-tenant relay\"]."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/nip42_host_binding_live.rs"
  - statement: "crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs is a regression test whose own module doc-comment names it a regression test for 'the NIP-43 relay-admin durable-ban bypass (BUZZ-SEC-007 class, reported 2026-07-27)', pinning that a banned admin can no longer add/remove relay members or change the workspace icon via signed NIP-98 POST /events; it requires a running relay and Postgres and is ignored by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs"
  - statement: "crates/buzz-auth/src/nip_fi/verifier/tests.rs is a 1,603-line unit-test file, and a count of #[test] and #[tokio::test] attributes across all of crates/buzz-auth/src returns 113, all of them inline unit tests co-located with the code they exercise rather than in a separate integration or E2E suite; crates/buzz-auth has no tests/ directory of its own."
    entry_class: FACT
    evidence:
      - "grep_count('#\\[test\\]|#\\[tokio::test\\]', path='crates/buzz-auth/src') -> 113, run 2026-09-01 against commit 473205a7457b208455f188847bfb27b01aa83cac"
      - "crates/buzz-auth/src/nip_fi/verifier/tests.rs"
  - statement: "No test file under crates/buzz-test-client/tests names authentication or NIP-42/NIP-98 verification alone as its subject; the one E2E-level exercise of host-bound auth (nip42_host_binding_live.rs) is scoped and gated as a multi-tenancy test, not a standalone auth test."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/nip42_host_binding_live.rs"
  - statement: "The .github/workflows/ci.yml backend-integration job ('Backend Integration (relay e2e)') starts Postgres, Redis and MinIO via docker compose and runs a cargo-nextest filter of package(buzz-db) and test(/tests::(parameterized_|concurrent_parameterized_)/) with --run-ignored ignored-only, i.e. Postgres-dependent replaceable-event persistence tests that the infrastructure-free unit-tests job does not run."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "crates/buzz-test-client/tests/e2e_nostr_interop.rs covers NIP-50 search, NIP-10 threads, NIP-17 gift wraps and DM discovery against a running relay, marked #[ignore] by default, run as cargo test --test e2e_nostr_interop -- --ignored -- a protocol-interop suite, not a money or data-loss surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "ADR-0020 states the retry policy (retries: process.env.CI ? 2 : 0) and that desktop/scripts/summarize-flaky-tests.mjs surfaces any test that passed on retry in the job summary, citing a real bug (a membership race in stream.spec.ts hidden by retries for months) as the reason that visibility exists; ADR-0020 names no policy for removing or quarantining a test once it is known to be flaky, only for surfacing that it happened."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020's Consequences section states as a stated bad consequence that 'quarantine becomes necessary the moment checks are required' and that this has not yet happened, because no level is a required check today -- so the absence of a quarantine mechanism is a named, accepted gap rather than an oversight."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "Buzz's test investment is organized by ADR-0020's architectural/infrastructure levels rather than by an explicit, documented risk score, and the extra depth visible on the multi-tenancy and admin/ban-bypass surfaces (a 2,749-line conformance harness mirroring a named obligation table, and an incident-named regression test) arose from a conformance-obligation document and a reported security incident respectively, not from a repository-wide risk-prioritization process that does not exist in this repository at the recorded revision."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
      - "docs/multi-tenant-conformance.md"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
      - "crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs"
    confidence: 0.8
  - statement: "Because no document in this repository scores or ranks a surface's risk, the dedicated depth found on multi-tenancy and admin/ban-bypass cannot be compared against the depth any other surface 'should' have under a risk model that has never been written down; this table names what exists today, not what a risk-scored strategy would prescribe."
    entry_class: INFERENCE
    evidence:
      - "grep_case_insensitive('risk', paths=['docs/multi-tenant-conformance.md','TESTING.md','launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md','CONTRIBUTING.md']) -> one unrelated match, run 2026-09-01 against commit 473205a7457b208455f188847bfb27b01aa83cac"
    confidence: 0.6
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: references
    target: layers-observability-audit-log
---

# Buzz verification strategy: the risk model, and its absence

## Scope

This node covers one narrow question about Buzz's testing effort, repository-wide:
**is test investment explicitly prioritized by risk today, and if not, what actually
decides where extra verification depth goes?** It is not a restatement of
`ADR-0020`'s whole testing methodology (that decision, and the five levels it
adopts, are cited here and not reproduced) and it is not a second copy of
`docs/multi-tenant-conformance.md`'s own obligation table. This node's scope is the
risk lens laid over what already exists: which levels run, which surfaces get more
than the baseline, and whether any of that is driven by a documented risk score.

**This scope applies to the whole `block/buzz` repository as inherited by this fork**,
not to one crate or client. Where a claim is scoped narrower (a single crate, a single
CI job), the claim says so.

## Levels

The five levels below are `ADR-0020`'s, adopted unchanged from upstream. This table
restates them because a risk-prioritization question cannot be answered without
knowing what infrastructure and gating each level actually has; the levels themselves
are not this node's subject and are covered in full by `ADR-0020`.

| Level | Purpose | Infrastructure | Command | Gating |
|---|---|---|---|---|
| Unit | Fast, infrastructure-free correctness for individual crates | None | `just test-unit` | Runs unconditionally; not a required check (see *Current enforcement*) |
| Integration | Postgres/Redis-backed correctness (e.g. replaceable-event persistence under concurrency) | `localhost` Postgres, Redis, MinIO | `just test` (CI: the `backend-integration` job's `cargo nextest` filter) | Runs in CI on push and on Rust-path changes; not a required check |
| Relay E2E | Full-relay behavior needing a live process | A running relay (`cargo test -p buzz-test-client -- --ignored`) | `cargo test -p buzz-test-client -- --ignored` | `#[ignore]`d by default everywhere; opt-in even where CI runs it |
| Desktop E2E smoke | Mock-bridge UI behavior, no live relay | None (mocked Tauri bridge) | `pnpm test:e2e:smoke` | Runs in CI (`desktop-core`/smoke matrix job); not a required check |
| Desktop E2E integration | Full desktop app against a live relay | A running relay + built desktop app | `pnpm test:e2e:integration` | Runs in CI (`Desktop E2E Relay` / `Desktop E2E Integration` jobs); not a required check |

## Risk-relevant depth today

No document in this repository assigns a risk score, severity tier, or coverage
target to a surface. What exists instead is uneven, surface-specific extra depth,
each traceable to a different origin. This table names what was found; it is not a
risk register, because none exists to summarize.

| Surface | Why it looks high-risk | Dedicated verification found today | Level(s) | Enforcement | Where the extra depth came from |
|---|---|---|---|---|---|
| Multi-tenant community boundary | Cross-tenant data leakage (auth/authorization + data isolation combined) | `docs/multi-tenant-conformance.md` obligation table (14 rows) + `conformance_multitenant.rs` (2,749 lines, one test module per obligation row) + `nip42_host_binding_live.rs` | Relay E2E, all `#[ignore]`d | Runs only when explicitly invoked with `--ignored` against a two-host relay; not a required check | A written conformance-obligation document, mirrored 1:1 into an executable suite by design (the suite's own doc comment states the mirroring) |
| Auth (NIP-42/NIP-98 signature and identity verification) | Forged or impersonated identity | 113 inline unit tests under `crates/buzz-auth/src` (no dedicated auth E2E suite; `nip42_host_binding_live.rs` exercises host-bound auth only as a multi-tenancy test) | Unit only, at scale (1,603-line verifier test file) | Unit tests run in the CI `unit-tests` job; not a required check | Ordinary crate-level unit-test discipline, not a named risk decision |
| Admin/moderation ban enforcement | Privilege escalation surviving a ban | `regression_relay_admin_ban_gate.rs`, named for a specific reported class of bug (BUZZ-SEC-007, 2026-07-27) | Relay E2E, `#[ignore]`d | Opt-in only, not a required check | A single reported incident, pinned after the fact -- reactive, not derived from a documented risk assessment |
| Data persistence under concurrency (replaceable events) | Data loss or corruption from races | `buzz-db` `parameterized_*`/`concurrent_parameterized_*` tests, run against real Postgres | Integration | Runs in CI's `backend-integration` job on push/Rust-path changes; not a required check | Ordinary integration-test discipline for a Postgres-backed store |
| Nostr protocol interop (NIP-50/10/17) | Client interop breakage, not data loss or auth | `e2e_nostr_interop.rs` | Relay E2E, `#[ignore]`d | Opt-in only, not a required check | Protocol-conformance testing for specific NIPs the relay implements |

**What this table does not show.** It does not show a surface receiving *less* than
some documented baseline, because no baseline is documented. It also cannot show
whether the depth on these five surfaces is proportionate to their actual risk,
because nothing in this repository states what "proportionate" would mean here.

## Current enforcement

**No level in the table above is a required status check on `launchpad` today.**
`ADR-0020` recorded this as a 404 from the branch-protection endpoint on
2026-08-21; re-running the same class of check at this node's recorded revision
confirms it still holds: the legacy branch-protection endpoint still 404s and the
repository's rulesets list is still empty. Every level that "runs in CI" (unit,
integration, desktop smoke, desktop E2E integration) runs as an ordinary job whose
failure does not, by itself, block a merge — `just ci`'s promise that failing PRs
"will not be merged" is an honour system, exactly as `ADR-0020` states.

**Flakiness is made visible, not quarantined.** `ADR-0020`'s retry policy
(`retries: CI ? 2 : 0`) and `summarize-flaky-tests.mjs` surface a test that passed
only on retry in the job summary. Nothing in `ADR-0020` or in this repository
removes, downgrades, or gates around a test once it is known to be flaky; `ADR-0020`
itself names the absence of quarantine as a consequence that becomes necessary only
once a check is required, and states that has not happened yet.

**Traceability from a written obligation to a test exists in exactly one place.**
`conformance_multitenant.rs`'s own doc comment states it mirrors
`docs/multi-tenant-conformance.md` one row per module -- a stated, checkable (by a
human, not a tool) claim of traceability from a specification-shaped document to
its verifying tests. No comparably explicit claim was found for the auth,
admin/ban, persistence, or protocol-interop rows above: their tests exist, but
nothing states which specification, decision, or requirement each one traces back
to beyond the code it sits next to.

## Deliberately out of scope

**A formal, documented risk-scoring or risk-tiering process for test investment is
out of scope for this node to prescribe, because none exists to describe.**
`ADR-0020`'s own Decision section states plainly that the cohort chose to *adopt*
upstream's level-based methodology rather than *design* a new one, and gives three
reasons for that choice, none of them risk-based prioritization. This node does not
invent the risk-scoring framework `ADR-0020` did not build; doing so would
misrepresent an absence as a decision. The risk this leaves accepted, stated
honestly: without a documented risk model, whether the depth on the five surfaces
above is the *right* depth -- too much on one, too little on another -- is a
judgment nobody has been asked to make explicitly, and it will not surface as a
CI failure if it is wrong.

**ISTQB's fuller strategy-type taxonomy** (`templates/test-strategy.md` names
analytical/risk-based, methodical, and other types) is not adopted here beyond
using "risk-based" as the lens this node applies; Buzz's own methodology does not
organize itself around that vocabulary, so this node does not retrofit it.

## Relationships

**Checked, not assumed absent**, per `AGENTS.md`'s own requirement: at the recorded
revision, `origin/launchpad`'s corpus tree includes
`architecture-principles-community-is-security-boundary`,
`architecture-principles-fail-closed-boundaries`, and
`layers-observability-audit-log` among many others (confirmed via `git ls-tree -r
--name-only origin/launchpad -- launchpad/docs/corpus`). This node declares
`references` to the first two because they state the architectural reasons the
multi-tenant boundary is treated as high-risk in the table above, and to the third
because the audit hash-chain is this repository's closest analog to a data-integrity
verification surface. No corpus node exists yet for `ADR-0020` itself (decision
records live under `launchpad/decisions/`, not `launchpad/docs/corpus/`, and no
`decision-reference`-template node instantiates it), so this node cites `ADR-0020`
directly as a file rather than declaring a relationship to it; that edge is a
follow-up once such a node exists.

## Scope and omissions

**This node covers** whether Buzz's testing effort is explicitly prioritized by
risk (it is not), what actually decides where extra verification depth goes today
(a conformance-obligation document for multi-tenancy, an incident report for
admin/ban enforcement, and ordinary per-level test discipline for everything else),
`ADR-0020`'s five levels restated only as far as this risk question needs them,
current enforcement and gating honesty, and the one place traceability from a
written obligation to its tests is explicit.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full rationale for adopting a level-based (not risk-based) testing methodology | `launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md` |
| The multi-tenant conformance obligations themselves, row by row | `docs/multi-tenant-conformance.md` |
| One testable obligation and the specific test(s) that verify it | `templates/test-contract.md` (issue #1349, unmerged) |
| How any corpus node should cite a test as evidence | `standards/test-references.md` |
| Step-by-step instructions for running any of the levels above | `TESTING.md`, `crates/buzz-cli/TESTING.md` |
| What may gate a merge at all, and the CI/CD enforcement programme | `launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md`, deferred further by `ADR-0020` |
| Whether the depth on non-multi-tenant, non-auth, non-admin surfaces (search, media, workflows, mesh) is adequate | Not assessed by this node; a future task, not this one, since assessing every surface is a second, much larger idea |

**Expected but not verified when this node was written:**

- **Whether any risk-prioritization discussion exists outside this repository's
  text** (a Slack thread, a design review, a person's stated intent) was not
  checked. This node's claim is scoped to what is written down in this repository
  at the recorded revision; it does not claim no risk conversation has ever
  happened.
- **Whether the CI jobs named in *Current enforcement* (`unit-tests`,
  `backend-integration`, desktop smoke/integration) reliably pass** was not
  measured here. `ADR-0020` itself records, as of 2026-08-21, that two of the five
  most recent `ci.yml` runs failed and that whether the inherited suite is
  reliably green was unverified there too; this node did not re-measure that.
- **Whether `crates/buzz-persona`, `crates/buzz-cli`, and the six
  `desktop/src-tauri/` files `ADR-0020` names as the fork's own product-code
  divergences carry any dedicated risk-relevant testing of their own** was not
  checked; this node's surface list (multi-tenancy, auth, admin/ban, persistence,
  protocol interop) came from what `crates/buzz-test-client/tests/` and
  `crates/buzz-auth/src` already contain, not from a survey of the fork's
  divergent code.
- **Whether a monetary-transaction surface exists anywhere in this repository**
  was not searched for beyond the surfaces already named above; this node treats
  data-loss (replaceable-event persistence, the audit hash-chain) as the nearest
  analog to a money-shaped risk and makes no claim about payments existing or not
  existing here.
