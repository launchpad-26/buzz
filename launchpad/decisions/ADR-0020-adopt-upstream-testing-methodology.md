---
status: Accepted
date: 2026-08-21
issue: launchpad-26/buzz#84
decided_in: launchpad-26/buzz#84
supersedes: none
---

# ADR-0020 — Adopt upstream's testing methodology; the cohort adds a gate, not a second methodology

## Decision

**Upstream's testing methodology is adopted unchanged.** Specifically, and deliberately not
re-litigated:

1. **Five levels, separated by the infrastructure they need** — unit (`just test-unit`, no
   infrastructure), integration (`just test`, Postgres and Redis started automatically),
   relay E2E (`cargo test -p buzz-test-client -- --ignored`, needs a running relay),
   desktop E2E smoke, and desktop E2E integration.
2. **The `#[ignore]` convention for E2E.** Every test needing a live relay is marked
   `#[ignore]`, so `cargo test` is safe everywhere and E2E is opt-in. This replaces a
   tagging framework and needs no addition.
3. **Change detection over run-everything.** The `changes` job's `dorny/paths-filter`
   filters (`rust`, `desktop`, `desktop-rust`, `web`, `mobile`) gate all 19 CI jobs, which
   is what keeps the pipeline at roughly 30 minutes.
4. **Sharding with `fail-fast: false` and explicit `timeout-minutes`** on every job.
5. **The retry policy: `retries: process.env.CI ? 2 : 0`** — zero locally so a developer
   feels their own flakiness, two in CI so pass-on-retry is measurable.
6. **Flakiness stays visible.** `desktop/scripts/summarize-flaky-tests.mjs` surfaces any
   test that passed on retry in the job summary. Its header records why: retries hid a
   membership race in `stream.spec.ts` for months.
7. **`just ci` is the contract.** One command, locally identical to CI.

**What the cohort adds is not a level. It is a gate, and coverage of its own surface.** Both
are tracked under [#290](https://github.com/launchpad-26/buzz/issues/290) as the umbrella,
so additive testing work has one home and its gaps are visible in one place.

**Deliberately not covered, recorded so a future reader can tell a choice from an oversight:**
the web client has zero tests, and agent behaviour has no deterministic harness. Both are
named in #290 rather than silently absent.

## Context

#84 asked what levels the cohort tests at, which are mandatory, and what counts as evidence.
It was right that no answer existed and right that the gap was invisible by construction —
six issues each carried a competent evidence rule of its own and none stated the whole.

What #84 could not know is how much already exists. Measured on 2026-08-21 at `launchpad` tip `db4305a4a`: **4,615 Rust test
functions across 28 of 30 crates**, 37 integration test files, 19 relay E2E suites, 146
Playwright specs, 481 desktop `*.test.mjs` files, 123 Flutter tests, and 19 CI jobs running in
roughly 28–32 minutes. Upstream's methodology is not thin, and inventing a second one would
mean maintaining a parallel scheme against a suite the cohort mostly inherits.

#84's framing also needs one correction. It reasoned from `launchpad/AGENTS.md` §1 — *"We
operate Buzz. We do not develop Buzz."* — and concluded the cohort's characteristic assertion
is convergence and externally observable behaviour rather than unit coverage. That was true
when filed. The fork now carries **nine deliberate product-code divergences** (`crates/buzz-cli`,
`crates/buzz-persona`, six files under `desktop/src-tauri/`), so the cohort partially does
develop Buzz, and needs the ordinary kind of test for the parts it wrote.

**And #84 was right for a reason this decision must not erase.** Upstream's methodology is real
but it is *tacit* — assembled from `TESTING.md`, `CONTRIBUTING.md`, the `changes` job's filters in
`ci.yml`, a `retries` line in `desktop/playwright.config.ts`, and a header comment in
`desktop/scripts/summarize-flaky-tests.mjs`. No single document states it. That is precisely why
the cohort could not find it and raised an ADR asking what the methodology was. Adopting an
undocumented methodology without writing it down would leave the next person exactly where #84's
author stood, so **recording it in the cohort's documentation corpus is #290's first task**, ahead
of any new test.

Three findings shaped the decision to adopt rather than design:

- **The retry and flake-visibility problem is already solved upstream**, and solved better than
  a first attempt would manage — with a real bug as the stated motivation.
- **What upstream cannot cover is the cohort's own code**, which is where every real gap is: the
  cohort's Python suites do not run in CI, the web client has no tests, and no test protects the
  fork's divergence from being reverted by an upstream merge.
- **The one thing missing is enforcement, not method.** `required_status_checks` on `launchpad`
  returns 404 — not configured. Upstream's own words are *"PRs that fail `just ci` will not be
  merged"*, which is an honour system. ADR-0019 already ruled on what may gate and deferred the
  enforcement to the CI/CD pipeline programme; this decision does not re-open it.

## Consequences

**Good.** The methodology becomes legible: adopting it forces it to be written down in one place,
which is the gap #84 was actually reporting. No parallel methodology to maintain. The cohort's testing effort points at the gaps
that are actually its own rather than duplicating a 4,615-test suite. #84's real contribution —
that coverage gaps must be visible rather than inferred — is preserved by #290 carrying an
explicit non-coverage list.

**Bad, stated honestly.**

- **Adopting upstream's methodology means inheriting its blind spots**, and the cohort has not
  audited them. Two of the five most recent `ci.yml` runs failed; whether the inherited suite is
  reliably green is unverified.
- **Quarantine becomes necessary the moment checks are required.** Upstream needs no quarantine
  because upstream gates nothing. With 146 Playwright specs and 19 relay E2E suites behind a
  required check, a flaky test blocks merges — and ADR-0019 already names the consequence: people
  route around a gate they cannot trust, and a gate that is routed around is worth less than none.
- **This decision closes the methodology question while the enforcement question stays open**
  elsewhere. A reader could take "testing methodology: decided" as meaning tests gate merges.
  They do not, and will not until the pipeline programme lands.
- **The nine product-code divergences remain unprotected today.** The decision names the need; the
  work is #290's.

## Security implications

Adopting a methodology changes nothing about exposure by itself. Two consequences of what it
routes are worth recording.

**CI logs are a disclosure surface on a public repository, and wiring the cohort's own suites into
CI increases what gets printed there.** This has already happened once: #279 exists because raw
`gitleaks` stderr reached a public log. Every suite added under #290 inherits that risk.

**The deliberate non-coverage is security-relevant, not merely incomplete.** Agent behaviour has no
deterministic harness, which means the cohort cannot currently assert what an agent does — only
what it contracts to do. That is the same gap `buzz-infrastructure` #103 addresses from the
containment side, approached from the testing side, and neither is closed.

## Provenance

Decided by @tucktuck101 in conversation on 2026-08-21, after research into upstream's actual
methodology and into industry practice on deterministic agent testing and flaky-test policy. The
call to adopt rather than author, and to raise #290 as a bucket for additive work rather than fold
it into this record, are both his.

Drafted by an AI agent (Claude Opus 5). Verified by reading this repository on 2026-08-21: the test
and file counts above (at `launchpad` tip `db4305a4a`), `TESTING.md`'s level descriptions, `CONTRIBUTING.md`'s `just ci` statement,
the `changes` job filters, the shard matrices and timeouts in `ci.yml`, `retries: CI ? 2 : 0` and
the flaky summarizer's header comment, the `#[ignore]` marking across the E2E suites, the 404 from
`required_status_checks`, and the nine product-code divergences. Not verified: whether the inherited
suite passes reliably, or what the cohort's own Python suites cover.
