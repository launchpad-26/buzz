---
id: verification-unit-web
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
  - statement: "web/package.json defines only two test-related scripts, test:e2e and test:e2e:smoke, both of which build the app and then run Playwright, and it declares no unit test runner (no Vitest, Jest, or similar) in either its dependencies or devDependencies."
    entry_class: FACT
    evidence:
      - "web/package.json"
  - statement: "web/vite.config.ts defines no `test` configuration block, so no Vitest instance is wired through Vite for web/."
    entry_class: FACT
    evidence:
      - "web/vite.config.ts"
  - statement: "web/playwright.config.ts scopes testDir to ./tests/e2e and defines a single project, smoke, matching only **/smoke.spec.ts, run against a built preview server on port 4173 -- a browser end-to-end test, not a unit test."
    entry_class: FACT
    evidence:
      - "web/playwright.config.ts"
  - statement: "Justfile's web-scoped recipes are web (dev server), web-check (biome lint/format), web-fix, web-typecheck (tsc --noEmit), web-build, and web-e2e-smoke (pnpm test:e2e:smoke); none of them invokes a unit test suite."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: ".github/workflows/ci.yml's `web` job runs on push or when the changes filter detects a diff under web/**, and its only two run steps are `just web-check` (\"Web lint and format\") and `just web-build` (\"Web build\") -- no unit-test step."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "TESTING.md's 'Automated Tests' section documents only `just test-unit` and `just test`, and Justfile's test-unit recipe runs `cargo nextest run -p buzz-core -p buzz-auth --lib`, scoped to two Rust crates; neither TESTING.md nor the test-unit recipe covers web/."
    entry_class: FACT
    evidence:
      - "TESTING.md"
      - "Justfile"
  - statement: "web/src/shared/lib contains pure, DOM-independent TypeScript functions with documented boundary behaviour, for example truncatePubkey in pubkey.ts (returns its input unchanged at length <= 12, otherwise an 8+4-character ellipsis form) and relativeTime in relative-time.ts (branches on singular vs. plural time units and on a >30-day cutoff) -- the kind of logic a fast unit-test suite would normally exercise without a browser."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/pubkey.ts"
      - "web/src/shared/lib/relative-time.ts"
  - statement: "desktop/src/shared/lib/pubkey.ts -- which web/src/shared/lib/pubkey.ts's own doc comment says it mirrors -- has a companion unit test, desktop/src/shared/lib/pubkey.test.mjs, exercising truncatePubkey and normalizePubkey directly via node:test and node:assert/strict, run by desktop/package.json's `test` script (`node --test` against src/**/*.test.mjs); the equivalent logic is unit-tested for the desktop client today, and web/'s copy is not."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/lib/pubkey.test.mjs"
      - "web/src/shared/lib/pubkey.ts"
      - "desktop/package.json"
  - statement: "Issue #1396's definition of done requires this node to name negative/error cases when they are part of the contract and to not claim coverage that is not present; because no unit test exists for web/ today, the honest content of those two bullets is that no automated test yet enforces any negative case, stated as a pending obligation rather than a verified one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1396 definition of done"
---

# Web unit tests — test contract

## Purpose and boundary

This node documents one obligation: **the `web/` browser client's pure,
DOM-independent application logic should be covered by an automated unit test
suite that runs without a browser, without Playwright, and without a live
relay.** It covers unit-level verification of `web/` only. It is deliberately
narrower than, and does not cover:

- **`web/`'s browser end-to-end coverage** — that is Playwright, driven by
  `web/playwright.config.ts` and exercised through `pnpm test:e2e` /
  `pnpm test:e2e:smoke`, a different obligation with a different verifying
  mechanism (a real browser, a built preview server, no unit-level isolation).
  At the recorded revision, `origin/launchpad`'s corpus tree carries no
  `verification/` subtree at all (checked via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), so
  no `verification-e2e-web` node exists yet to link. See *Relationships*
  below.
- **Unit testing for desktop, mobile, or any Rust crate.** Those are separate
  clients with their own test runners and, where they exist, their own
  test-contract nodes.
- **Whether `web/` *should* adopt a specific unit-test runner, or when.** That
  is a product/tooling decision for whoever picks this obligation up; this
  node states the gap and the shape of the obligation, not the fix.

## Obligation

> Every pure, DOM- and network-independent utility function under
> `web/src/shared/lib` (and any equivalent non-component module added later)
> is exercised by an automated unit test that runs without a browser, without
> Playwright, and without a live relay, and that test asserts both the
> function's typical behaviour and its documented boundary/edge-case inputs.

Concretely, for the two functions cited above as illustrative examples of the
kind of logic in scope:

- `truncatePubkey` (`web/src/shared/lib/pubkey.ts`): given a pubkey longer
  than 12 characters, returns the canonical `abcd1234…wxyz` form; given a
  pubkey of length <= 12, returns it unchanged (the boundary/negative case —
  nothing is truncated).
- `relativeTime` (`web/src/shared/lib/relative-time.ts`): given a Unix
  timestamp, returns a human-readable relative string, correctly branching
  singular vs. plural units and the >30-day "N months ago" cutoff.

## Verifying test(s)

**None exist today.** There is no unit test file anywhere under `web/` for
`truncatePubkey`, `relativeTime`, or any other module in
`web/src/shared/lib` (or elsewhere in `web/src`). The evidence entries above
establish this by elimination: `web/package.json` declares no unit test
runner, `web/vite.config.ts` wires no Vitest `test` block, `web/tests`
contains only the Playwright `smoke.spec.ts`, and neither `Justfile` nor
`.github/workflows/ci.yml`'s `web` job nor `TESTING.md` names a `web/`
unit-test step anywhere.

This is a genuinely different situation from the equivalent desktop logic:
`desktop/src/shared/lib/pubkey.test.mjs` already unit-tests
`desktop/src/shared/lib/pubkey.ts` (which `web`'s copy says it mirrors) via
Node's built-in test runner. That precedent shows the obligation is
practically testable in this monorepo's toolchain; it is not evidence that
`web/` inherits that coverage, and it does not.

## How to run it

There is no runnable command today. `web/package.json`'s only test-related
scripts are `test:e2e` and `test:e2e:smoke`, both of which build the app and
run Playwright — neither runs a unit test. No unit-test runner is installed
under `web/`'s `devDependencies`, so there is nothing to invoke.

## Current enforcement status

**Pending.** No automated unit test exists for `web/`, no unit-test runner is
configured, and no CI step exercises one. The obligation above is stated so a
future contribution has something concrete to satisfy and a specific node to
update once it does — not because anything currently enforces it. Claiming
"verified" or "gated" here would misstate the repository as it stands at the
recorded revision.

## Limits

- **This node proves nothing about current behaviour.** Because no test
  exists, nothing here establishes that `truncatePubkey`, `relativeTime`, or
  any other `web/src/shared/lib` function actually behaves as documented —
  only that their source currently states that behaviour in a doc comment or
  implementation, which is not the same as a passing assertion.
- **The two functions named under *Obligation* are illustrative, not an
  exhaustive obligation list.** `web/src/shared/lib` holds other modules
  (`cn.ts`, `nip98.ts`, `nostr-signer.ts`, `relay-url.ts`, `buzz-download.ts`,
  `nostr-client.ts`) not individually inspected for testability here; some
  (`nostr-signer.ts`, `nostr-client.ts`) likely have side effects or external
  dependencies that would need isolation (mocking, dependency injection)
  rather than being pure-function unit tests in the same style as
  `pubkey.ts`. Whether each is realistically unit-testable in isolation was
  not evaluated file-by-file.
- **The desktop precedent is cited for contrast and feasibility, not as a
  plan.** This node does not assert that `web/` should adopt Node's built-in
  test runner, `.test.mjs` files, or any other specific mechanism — only that
  an equivalent, already-working precedent exists elsewhere in this
  repository's toolchain.

## Relationships

**Checked, not assumed absent**, per `launchpad/docs/corpus/AGENTS.md`. At the
recorded revision, `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` lists no `verification/` path at all — this is the
first node under that surface, so no sibling `verification-e2e-web` node (or
any other verification node) exists on the merge target to point at. None is
declared. The first `verification/` node to land alongside this one, in
particular a future `web/` end-to-end test-contract node, is the moment to
revisit this and add a `references` edge distinguishing unit-level coverage
from browser end-to-end coverage.

## Scope and omissions

**This node covers** the obligation that `web/`'s pure application logic have
automated unit test coverage, the concrete absence of any such coverage or
runner today, two illustrative example functions and their documented
boundary behaviour, and an honest statement that enforcement is pending.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `web/`'s Playwright browser end-to-end coverage | A future `verification-e2e-web` node (none exists on `origin/launchpad` yet; see *Relationships*) |
| Unit testing for desktop, mobile, or any Rust crate | Their own test-contract nodes, where they exist |
| Which unit-test runner `web/` should adopt, or a migration plan | Not decided here — a tooling/product decision for whoever picks up this obligation |
| Whether every non-`pubkey.ts`/`relative-time.ts` module in `web/src/shared/lib` is realistically unit-testable in isolation | Not evaluated file-by-file; named as a limit above |
| The general corpus rule for how any node cites a test as evidence | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/standards/evidence.md` |

**Expected but not verified when this node was written:**

- **Whether `web/`'s other `shared/lib` modules beyond the two named above are
  pure enough for the same style of unit test was not checked file-by-file.**
  Only `pubkey.ts` and `relative-time.ts` were opened and read in full.
- **Whether any hidden or WIP unit-test configuration exists outside the
  files inspected (`package.json`, `vite.config.ts`, `playwright.config.ts`,
  `Justfile`, `.github/workflows/ci.yml`, `TESTING.md`) was not exhaustively
  ruled out beyond those sources — no other configuration file under `web/`
  was found to inspect, but a directory-wide negative cannot be cited as a
  single openable file per this corpus's citation rules.**
