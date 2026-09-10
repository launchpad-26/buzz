---
id: verification-e2e-desktop
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
  - statement: "Root AGENTS.md's 'Desktop E2E' section states desktop E2E is run via 'cd desktop && pnpm test:e2e:smoke' for mock-bridge smoke coverage, or 'pnpm test:e2e:integration' for relay-backed coverage, and that these scripts build the required E2E bridge before running Playwright."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "AGENTS.md's 'Writing E2E Screenshot Specs' section states the mock Tauri bridge is compiled in only for '--mode e2e' builds, so a plain 'pnpm run build' strips it, 'window.__TAURI_INTERNALS__' is never defined, and every mock-mode spec fails with 'Cannot read properties of undefined (reading 'invoke')' -- the app renders 'Community connection failed' instead of the UI under test, which looks like a product bug rather than a build mistake."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "desktop/src/main.tsx's installE2eBridgeIfConfigured only imports and calls maybeInstallE2eTauriMocks (from desktop/src/testing/e2eBridge) when '(import.meta.env.DEV || import.meta.env.MODE === \"e2e\")' AND 'window.__BUZZ_E2E__' is truthy, confirming in code the gate AGENTS.md describes: the mock bridge is compiled and activated only in dev or explicit e2e builds, never by the pre-bootstrap global alone."
    entry_class: FACT
    evidence:
      - "desktop/src/main.tsx:111-123"
  - statement: "desktop/package.json defines 'build:e2e' as 'tsc && vite build --mode e2e', and defines 'test:e2e:smoke' / 'test:e2e:integration' as 'pnpm build:e2e && playwright test --project=smoke' / '--project=integration' respectively, so both suites always rebuild the e2e bundle before Playwright runs."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
  - statement: "desktop/playwright.config.ts defines exactly two Playwright projects: 'smoke' (a testMatch list enumerating roughly 170 individual spec files, using devices['Desktop Chrome']) and 'integration' (a shorter testMatch list of 17 spec files including integration.spec.ts, agents.spec.ts, onboarding.spec.ts, stream.spec.ts and sidebar.spec.ts); retries are 'process.env.CI ? 2 : 0'; and the webServer serves the built 'dist' directory via 'python3 -m http.server 4173'."
    entry_class: FACT
    evidence:
      - "desktop/playwright.config.ts"
  - statement: "desktop/tests/helpers/bridge.ts exports installMockBridge (installBridge with mode: 'mock') and installRelayBridge (installBridge with mode: 'relay', defaulting the test identity to 'tyler'); installRelayBridge threads DEFAULT_RELAY_HTTP_URL/DEFAULT_RELAY_WS_URL -- read from the BUZZ_E2E_RELAY_URL environment variable, defaulting to 'http://localhost:3000' / 'ws://localhost:3000' -- into both the HTTP and WebSocket transports so the app under test reaches an isolated relay rather than its production default."
    entry_class: FACT
    evidence:
      - "desktop/tests/helpers/bridge.ts:636-638"
      - "desktop/tests/helpers/bridge.ts:961-998"
  - statement: "desktop/tests/e2e/smoke.spec.ts installs the mock bridge in a top-level test.beforeEach via installMockBridge(page), and its tests -- app-shell rendering, stream/channel creation, sending messages, opening the agent-creation dialog, and multiple sidebar/global search flows -- run entirely against that mocked Tauri IPC layer with no live relay connection."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/smoke.spec.ts"
  - statement: "desktop/tests/e2e/integration.spec.ts imports installRelayBridge and TEST_IDENTITIES from ../helpers/bridge (not installMockBridge), and exercises channel creation, channel management, desktop-notification settings and channel messaging against a real relay rather than a mocked one."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/integration.spec.ts"
  - statement: "The Justfile's 'desktop-e2e-smoke' recipe runs 'cd desktop && pnpm test:e2e:smoke' with no prerequisite recipe; 'desktop-e2e-integration' depends on '_ensure-migrations' before running 'cd desktop && pnpm test:e2e:integration'; and 'desktop-e2e-seed' (also depending on '_ensure-migrations') runs './scripts/setup-desktop-test-data.sh' to seed deterministic channel data for Playwright."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: ".github/workflows/ci.yml's 'desktop-smoke-e2e' job runs 'pnpm -C desktop build:e2e' and then 'playwright test --project=smoke --shard=${{ matrix.shard }}/4' across a 4-way shard matrix, gated by 'if: github.event_name == \"push\" || needs.changes.outputs.desktop == \"true\" || needs.changes.outputs.desktop-rust == \"true\" || needs.changes.outputs.rust == \"true\"'."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: ".github/workflows/ci.yml's 'desktop-e2e-integration-shard' job needs a prior 'desktop-e2e-relay' build job, starts 'docker compose up -d postgres redis minio minio-init' (retrying up to three times), then runs 'pnpm -C desktop build:e2e' and 'playwright test --project=integration --shard=${{ matrix.shard }}/2' across a 2-way shard matrix, gated by the same push/path-filter condition as the smoke job."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "The 'changes' job's dorny/paths-filter step defines the 'desktop' filter as 'desktop/**', 'pnpm-lock.yaml', 'scripts/model-capabilities.json' and 'scripts/normative-corpus.json', and the 'desktop-rust' filter as only 'desktop/src-tauri/**'; a pull request touching none of those paths, none of the 'rust' filter's paths, and that is not itself a push to the default branch, does not trigger either desktop E2E CI job."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "Both the smoke and integration CI jobs run 'node scripts/summarize-flaky-tests.mjs playwright-report.json \"<run label>\"' with 'if: ${{ !cancelled() }}', and that script's own header comment states Playwright's 'retries: 2' 'hid the stream.spec.ts membership race (#1798) for months'; the script walks the Playwright JSON report's suite tree and appends any test whose status is 'flaky' to the job's GitHub Actions summary without ever failing the job itself."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "desktop/scripts/summarize-flaky-tests.mjs"
  - statement: "ADR-0020 records the desktop E2E retry policy verbatim as 'retries: process.env.CI ? 2 : 0 -- zero locally so a developer feels their own flakiness, two in CI so pass-on-retry is measurable', and states that 'desktop/scripts/summarize-flaky-tests.mjs surfaces any test that passed on retry in the job summary' because 'retries hid a membership race in stream.spec.ts for months.'"
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "At the recorded revision, no corpus node under launchpad/docs/corpus/verification/ exists on origin/launchpad, so this node is the first in that surface; architecture-containers-desktop (the desktop container's own architecture node) and corpus-standard-test-references (the corpus's citation standard for tests-as-evidence) are both loadable from origin/launchpad, so 'references' edges to both resolve on the merge target."
    entry_class: FACT
    evidence:
      - "git.ls_tree('origin/launchpad', 'launchpad/docs/corpus') -> no path under verification/; architecture/containers/desktop.md and standards/test-references.md both present"
  - statement: "desktop/tests/e2e/smoke.spec.ts and desktop/tests/e2e/integration.spec.ts are representative rather than exhaustive of this obligation's verifying tests: playwright.config.ts's own testMatch arrays name roughly 170 further spec files under the 'smoke' project and 15 further files under 'integration' that install the same two bridges through the same desktop/tests/helpers/bridge.ts helpers for narrower UI surfaces, so the obligation below is verified by the two Playwright projects as a whole rather than by these two files alone."
    entry_class: INFERENCE
    evidence:
      - "desktop/playwright.config.ts"
      - "desktop/tests/e2e/smoke.spec.ts"
      - "desktop/tests/e2e/integration.spec.ts"
    confidence: 0.8
  - statement: "This node's task requires an audiences field 'appropriate to the node' without enumerating which audiences; the author selected agent, developer and reviewer for the same reason the evidence standard (corpus-standard-evidence) gives for its own identical selection: both developers and agents author and run desktop E2E specs, and a reviewer is named because most of this node's judgment -- which suites are representative, what 'verified' honestly means given the path filter -- is held by review rather than by any check."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1363 definition of done: 'schema-valid front matter with a stable node ID, type, status, origin, audiences, provenance/evidence and typed relationships appropriate to the node', reasoned by analogy to corpus-standard-evidence's own audiences justification"
relationships:
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: corpus-standard-test-references
---

# Desktop end-to-end verification — test contract

## Purpose and boundary

This node documents one obligation: that the desktop app's built frontend stays
scriptable end-to-end by Playwright, in the two backend modes the repository
actually maintains for that purpose. It covers only the existence, wiring and
enforcement of that Playwright-driven contract — not the correctness of any
individual UI behaviour a given spec file asserts, not the desktop unit-test
suite, not the native Tauri/Rust-side checks, and not the web or mobile
clients' own end-to-end suites. Those are separate obligations, named in
*Scope and omissions* below.

## Obligation

> The desktop app, once built via `pnpm build:e2e` (which compiles in the
> mock/relay-aware Tauri IPC bridge behind `window.__BUZZ_E2E__`), must render
> its full UI and support scripted browser interaction under Playwright in two
> independently exercised modes — the `smoke` project, driven entirely against
> a mocked Tauri IPC layer with no live relay, and the `integration` project,
> driven against a real relay/Postgres/Redis/MinIO backend reached through
> `installRelayBridge` — and every spec file `playwright.config.ts` assigns to
> a project must pass under that project's mode.

A plain `pnpm run build` does not satisfy the precondition of this obligation:
it never compiles in the mock bridge, so `window.__TAURI_INTERNALS__` stays
undefined and the app renders "Community connection failed" rather than the
UI any spec expects — a failure mode AGENTS.md documents precisely because it
otherwise reads as a product bug rather than a build mistake.

## Verifying test(s)

- `desktop/tests/e2e/smoke.spec.ts` — installs the mock bridge
  (`installMockBridge`, `desktop/tests/helpers/bridge.ts:961`) in a
  `test.beforeEach` and covers app-shell rendering, stream/channel creation,
  sending messages, opening the agent-creation dialog, and sidebar/global
  search — entirely against mocked Tauri IPC. Representative of the ~170
  additional spec files `playwright.config.ts`'s `smoke` project `testMatch`
  enumerates.
- `desktop/tests/e2e/integration.spec.ts` — installs the relay-backed bridge
  (`installRelayBridge`, `desktop/tests/helpers/bridge.ts:983`) and exercises
  channel creation/management, notification settings and channel messaging
  against a real relay. Representative of the 15 further spec files under the
  `integration` project.
- `desktop/playwright.config.ts` — the authoritative source of which spec
  files run under `smoke` vs. `integration`, the retry policy, and the
  `webServer` that serves the `pnpm build:e2e` build output.
- `desktop/tests/helpers/bridge.ts` — `installMockBridge` / `installRelayBridge`,
  the shared harness every spec above (and every spec not named here) is built
  on.

## How to run it

```bash
# Mock-bridge smoke suite -- no relay or database required.
cd desktop && pnpm test:e2e:smoke
# equivalently:
just desktop-e2e-smoke

# Relay-backed integration suite -- requires Postgres/Redis/MinIO and a relay
# reachable at BUZZ_E2E_RELAY_URL (default http://localhost:3000, e.g. via
# `just relay`).
just desktop-e2e-integration   # runs _ensure-migrations first
# or, with services and a relay already running:
cd desktop && pnpm test:e2e:integration
```

Both `pnpm` scripts run `pnpm build:e2e` (`tsc && vite build --mode e2e`)
before invoking Playwright, so the mock/relay bridge is always compiled in;
running `playwright test` directly against a stale `pnpm run build` output is
the documented failure mode named above, not a supported invocation.

## Current enforcement status

**Verified on every push to the default branch; gated by a path filter on
pull requests — not "verified" unconditionally.** CI runs the obligation as
two jobs:

- `desktop-smoke-e2e` — 4-way shard, `pnpm -C desktop build:e2e` then
  `playwright test --project=smoke --shard=N/4`.
- `desktop-e2e-integration-shard` — depends on a `desktop-e2e-relay` build
  job, starts `docker compose up -d postgres redis minio minio-init`, then
  runs the same build step and `playwright test --project=integration
  --shard=N/2`.

Both carry the identical trigger condition: `github.event_name == 'push' ||
needs.changes.outputs.desktop == 'true' || needs.changes.outputs.desktop-rust
== 'true' || needs.changes.outputs.rust == 'true'`. The `desktop` path filter
covers `desktop/**`, `pnpm-lock.yaml`, and two script paths; `desktop-rust`
covers only `desktop/src-tauri/**`. A pull request that touches none of those
paths (and none of the separate `rust` filter's crate/migration/schema paths)
does not run either job — the obligation is enforced for every push and for
every desktop- or Rust-affecting pull request, not for every pull request.

**A passing shard does not mean every test passed on the first try.**
`retries: process.env.CI ? 2 : 0` (`playwright.config.ts`) lets a test fail
and pass on retry with no durable signal beyond a summary line;
`summarize-flaky-tests.mjs` posts any such "flaky" test to the job summary
(`if: ${{ !cancelled() }}`) but never fails the job on its own. This exists
because that exact gap once hid a real race condition in `stream.spec.ts`
(#1798) behind a green run for months, per ADR-0020 — so "CI is green" and
"nothing here is flaky" are two different claims, and only the job summary,
not the checkmark, distinguishes them.

## Limits

- **The `smoke` project proves the UI reacts correctly to a scripted mock IPC
  layer — nothing about real relay, auth, persistence or multi-client
  fan-out behaviour.** `installMockBridge` never opens a WebSocket to a real
  relay; a bug that exists only in relay-side authorization, persistence or
  fan-out is invisible to every `smoke` spec by construction.
- **The `integration` project's real-backend coverage is narrow relative to
  the whole suite.** Only the ~15–17 spec files `playwright.config.ts` assigns
  to `integration` run against Postgres/Redis/MinIO/a real relay; the large
  majority of desktop UI behaviour is verified only in `smoke`'s mocked mode.
- **Neither project exercises the native Tauri shell.** Both run a real
  Chromium browser (`devices["Desktop Chrome"]`) against the frontend served
  statically (`python3 -m http.server`), not the Tauri webview, so native OS
  chrome, tray behaviour, OS-level deep-link registration and the Tauri
  Rust-side IPC handlers are outside this contract; `just desktop-tauri-test`
  and the Tauri-specific CI steps are the separate obligation that covers that
  surface.
- **A green shard can still contain a flaky test.** See *Current enforcement
  status* above — retries hide non-determinism behind a summary line, not a
  failure.
- **This node states whether specs pass under their assigned project, not
  what any individual spec's own assertions guarantee.** Each of the ~190
  spec files is its own narrower, unenumerated obligation; most do not yet
  have their own corpus node.

## Scope and omissions

**This document covers** the existence of the desktop `smoke` and
`integration` Playwright projects, the mock-vs-relay bridge each is built on,
how to run both, their CI wiring and the path filter that gates it on pull
requests, and what a passing run does and does not establish.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Individual spec-level obligations (per-file behaviour claims) | Each spec file; not yet given its own corpus node |
| Desktop unit tests (`just desktop-test`) | A sibling `verification/unit/*` node, not yet landed at this revision |
| Tauri native/Rust-side checks (`just desktop-tauri-test`, `desktop-tauri-clippy`, `desktop-tauri-check`) | A separate verification node, not yet landed |
| The release-smoke suite (`pnpm test:e2e:release-smoke`, `just desktop-release-smoke`, an isolated local relay) | A separate, deterministic-correctness contract distinct from CI's sharded suites |
| The web app's own e2e suite (`web-e2e-smoke`) | A separate container/platform's own node |
| Mobile end-to-end verification | A separate platform's own node |
| Whether GitHub branch protection marks `desktop-smoke-e2e` / `desktop-e2e-integration-shard` as required checks | Not established here — would need a ruleset/branch-protection query this node does not perform |
| The general corpus rule for citing a test as evidence | `corpus-standard-test-references`, which this node follows rather than restates |

**No `relationships` beyond the two declared.** At the recorded revision no
other node under `launchpad/docs/corpus/verification/` exists on
`origin/launchpad` — this is the first — so there is no sibling
unit/integration/security/performance node for desktop to point at yet. A
`references` edge to `architecture-containers-desktop` is declared because
that node is the container this one verifies; a `references` edge to
`corpus-standard-test-references` is declared because this node's ledger
follows that standard's citation rules for tests directly. Both ids are
confirmed loadable from `origin/launchpad` today, not merely from this
worktree.

**Expected but not verified when this node was written:**

- **No Playwright run was executed in this session.** Enforcement status,
  the retry policy, and the flaky-summary mechanism are established by
  reading `playwright.config.ts`, `ci.yml` and `summarize-flaky-tests.mjs`,
  not by an observed `pnpm test:e2e:smoke` or `pnpm test:e2e:integration`
  run. "Currently passes" is asserted about CI's own behaviour as configured,
  not about a pass this session witnessed.
- **Whether the two desktop E2E CI jobs are configured as required checks in
  GitHub branch protection or a ruleset was not queried.** This node
  describes what the workflow YAML runs and when, not what merge policy
  depends on it.
- **The exact current spec count under each Playwright project was read from
  `playwright.config.ts`'s `testMatch` arrays at the recorded revision and is
  liable to drift** as specs are added, removed or reassigned between
  projects; treat "~170" and "15" as this revision's counts, not a standing
  fact.
