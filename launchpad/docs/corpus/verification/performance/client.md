---
id: verification-performance-client
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
  - statement: "Root CLAUDE.md's Common Gotchas #6 documents a React render-performance debugging methodology -- React.memo is defeated by any single reference-unstable prop, two repeat offenders (React Query result objects, derived Map/array state that recomputes on a version bump) and their fixes, and a rule to measure with DevTools closed and no per-keystroke console.log probes -- as prose guidance for a developer chasing interaction lag, not as a description of any automated test or benchmark."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "desktop/src/shared/hooks/useStableReference.ts implements three hooks -- useStableMap, useStableArrayShallow, useStableSet -- each of which returns the previous reference when the new value is content-equal to it, specifically so a React.memo boundary downstream can bail; this is the fix CLAUDE.md's gotcha #6 names for derived Map/array state."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/hooks/useStableReference.ts"
  - statement: "No test file in the repository imports or exercises useStableMap, useStableArrayShallow or useStableSet from useStableReference.ts; the one test file matching a 'useStable*' name search, useStableSendToChannel.test.mjs, tests an unrelated hook of the same naming pattern in features/messages/ui/."
    entry_class: FACT
    evidence:
      - "grep_repo('useStable(Map|ArrayShallow|Set)', scope='desktop/src/**/*.test.*') -> no matches; glob('desktop/src/**/useStable*') -> useStableReference.ts (no adjacent test file) and features/messages/ui/useStableSendToChannel.ts + .test.mjs (a different hook)"
  - statement: "desktop/tests/e2e/ contains five Playwright spec files matching *.perf.ts -- typing-latency.perf.ts, warm-switch-markdown.perf.ts, cold-switch-longtask.perf.ts, scroll-smoothness.perf.ts and scrollback-buzzbugs.perf.ts -- each an automated, runnable harness that measures a specific desktop-app interaction (composer keystroke latency under simulated agent load, warm channel-switch cost, cold channel-switch main-thread longtasks, scroll main-thread layout cost, and live-relay scroll-back page latency respectively) under CDP CPU throttling or against a real relay."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/typing-latency.perf.ts"
      - "desktop/tests/e2e/warm-switch-markdown.perf.ts"
      - "desktop/tests/e2e/cold-switch-longtask.perf.ts"
      - "desktop/tests/e2e/scroll-smoothness.perf.ts"
      - "desktop/tests/e2e/scrollback-buzzbugs.perf.ts"
  - statement: "typing-latency.perf.ts and warm-switch-markdown.perf.ts each end their test body with a comment reading, verbatim or near-verbatim, 'Instrument, not a gate', followed by an assertion that only confirms the harness recorded real measurements (e.g. a count greater than zero, or that every sample has a positive duration) rather than asserting any latency or longtask value stays under a threshold."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/typing-latency.perf.ts"
      - "desktop/tests/e2e/warm-switch-markdown.perf.ts"
  - statement: "scroll-smoothness.perf.ts's own module doc-comment states, verbatim, 'This is NOT a pass/fail correctness test -- it's an instrument', and cold-switch-longtask.perf.ts's own module doc-comment states it is 'the instrument the timeline-virtualization acceptance gate is defined against' without itself asserting a pass/fail threshold in the test body."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/scroll-smoothness.perf.ts"
      - "desktop/tests/e2e/cold-switch-longtask.perf.ts"
  - statement: "The phrase 'timeline-virtualization acceptance gate' in cold-switch-longtask.perf.ts's doc-comment names no other file in the repository; grep for 'acceptance gate' outside that one comment matches only an unrelated onboarding-agent-defaults.spec.ts reference in desktop/src/features/agents/AGENTS.md, so what specifically constitutes that gate (a PR review criterion, a since-closed issue, or something else) is not established from source."
    entry_class: FACT
    evidence:
      - "grep_repo('acceptance gate', scope='desktop/**') -> desktop/tests/e2e/cold-switch-longtask.perf.ts (this node's subject) and desktop/src/features/agents/AGENTS.md (unrelated onboarding-agent-defaults.spec.ts gate)"
  - statement: "playwright.perf.config.ts defines its own Playwright configuration, separate from playwright.config.ts, with a single project named 'perf' whose testMatch is '**/*.perf.ts' and which serves prebuilt static files from dist/ over a plain HTTP server rather than the mock-Tauri-bridge dev/e2e build."
    entry_class: FACT
    evidence:
      - "desktop/playwright.perf.config.ts"
  - statement: "None of the five *.perf.ts files' own run instructions invoke playwright.config.ts's 'smoke' or 'integration' projects; each names playwright.perf.config.ts explicitly and states it is run manually (e.g. 'pnpm build && npx playwright test --config=playwright.perf.config.ts <file>'), and scrollback-buzzbugs.perf.ts additionally requires manually port-forwarding a live staging relay and supplying an nsec via environment variable."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/typing-latency.perf.ts"
      - "desktop/tests/e2e/warm-switch-markdown.perf.ts"
      - "desktop/tests/e2e/cold-switch-longtask.perf.ts"
      - "desktop/tests/e2e/scroll-smoothness.perf.ts"
      - "desktop/tests/e2e/scrollback-buzzbugs.perf.ts"
  - statement: ".github/workflows/ci.yml is the workflow that runs Playwright in this repository -- invoking 'pnpm exec playwright test --project=smoke --shard=.../4' and 'pnpm exec playwright test --project=integration --shard=.../2' -- and contains no invocation of a 'perf' project anywhere in the file."
    entry_class: FACT
    evidence:
      - "grep_repo('project=perf', scope='.github/workflows/ci.yml') -> no matches; grep_repo('project=', scope='.github/workflows/ci.yml') -> only 'smoke' and 'integration'"
  - statement: "No workflow file under .github/workflows other than ci.yml mentions Playwright at all, and desktop/package.json's scripts block contains no script naming 'perf'."
    entry_class: FACT
    evidence:
      - "grep_repo('playwright', scope='.github/workflows/*.yml') -> ci.yml only"
      - "grep_repo('perf', scope='desktop/package.json') -> no matches"
  - statement: "Neither web/ nor mobile/ contains a file matching *perf*, *benchmark* or *lighthouse* (case-insensitive) outside build/tooling directories, so at the recorded revision no equivalent automated performance-measurement harness exists for the web client or the Flutter mobile client."
    entry_class: FACT
    evidence:
      - "glob('web/**/*perf*|*benchmark*|*lighthouse*') -> no matches"
      - "glob('mobile/**/*perf*|*benchmark*', exclude='.dart_tool,build') -> no matches"
  - statement: "Because none of the five *.perf.ts harnesses is invoked by any CI workflow and none of them asserts a latency, longtask or layout-cost threshold against the obligation stated below, no automated check in this repository currently fails a pull request for a client-performance regression at the recorded revision."
    entry_class: INFERENCE
    evidence:
      - "desktop/tests/e2e/typing-latency.perf.ts"
      - "desktop/tests/e2e/warm-switch-markdown.perf.ts"
      - "desktop/tests/e2e/cold-switch-longtask.perf.ts"
      - "desktop/tests/e2e/scroll-smoothness.perf.ts"
      - ".github/workflows/ci.yml"
    confidence: 0.8
relationships:
  - type: references
    target: architecture-containers-desktop
---

# Client performance -- test contract

## Purpose and boundary

This node documents one obligation: whether the Buzz **desktop client's**
(Tauri + React 19) common interactions -- composer typing, channel switching,
scrollback -- stay within their latency and main-thread-blocking budget as
synthetic load increases, and whether any automated, CI-enforced check exists
to catch a regression in that cost before it merges. It covers that
obligation only. It does not cover server/relay-side latency (a distinct
obligation belonging to a relay-focused verification node, not authored
here), and it does not cover the web (`web/`) or mobile (`mobile/`) clients,
for which no equivalent harness was found to exist at all (see *Scope and
omissions*).

## Obligation

> The desktop app's message composer, channel-switch and scrollback
> interactions keep their per-keystroke input-to-paint latency and
> main-thread blocking time inside the browser's ~50ms frame-budget as
> synthetic agent load (typing indicators, live messages, streaming edits,
> deep message/thread history) increases, and a change to the
> message-timeline or composer render path does not silently regress that
> cost.

This is the property the five harnesses named below were each written to
measure. None of them currently asserts it as a pass/fail check -- see
*Current enforcement status*.

## Verifying test(s)

None of the following **verifies** the obligation in the sense this
template's *Evidence expectations* distinguishes: each is real, automated,
and runnable, but each measures and logs rather than asserting a threshold,
and none runs in CI. They are named here as the instrumentation that exists
today, not as a passing gate.

- `desktop/tests/e2e/typing-latency.perf.ts` -- `MEASURE: composer keystroke
  latency, quiet vs agent-busy channel` -- records per-keystroke
  input-to-paint duration (Event Timing API) and longtask totals across six
  scenarios (quiet, 8-agent-busy, observer-frame storm, everything-at-once,
  streaming markdown, and a 68-reply thread quiet/busy). Its only assertion
  is that some input events were recorded across three of those scenarios;
  it prints per-scenario median/p95/max/over-50ms-count but asserts none of
  them.
- `desktop/tests/e2e/warm-switch-markdown.perf.ts` -- `MEASURE: warm
  channel-switch cost (plain 300-row + markdown-heavy)` -- measures wall-clock
  time and longtask totals for eight repeated warm re-entries into a
  plain-text-heavy channel and a markdown-heavy channel. Its only assertions
  are that eight samples were collected per scenario and each has a positive
  duration.
- `desktop/tests/e2e/cold-switch-longtask.perf.ts` -- measures the longest
  single longtask and total longtask time for the *first* (cold) switch into
  a 600-message channel windowed to 300 rows, under 4x CPU throttle. Its own
  doc-comment calls itself the instrument an (unnamed, not located in source)
  "timeline-virtualization acceptance gate is defined against."
- `desktop/tests/e2e/scroll-smoothness.perf.ts` -- measures cumulative
  Chromium main-thread layout/style-recalc cost (via CDP Performance
  metrics) during a synthetic fast-wheel scroll through a 600-row busy
  channel. Its own doc-comment states explicitly it is "NOT a pass/fail
  correctness test."
- `desktop/tests/e2e/scrollback-buzzbugs.perf.ts` -- measures scroll-back
  page latency, network RTT and payload composition against a **live staging
  relay**, requiring a manually port-forwarded relay and an operator-supplied
  `nsec`; it is not runnable in an ordinary CI job at all.

Related but out of this node's scope: `desktop/src/shared/hooks/useStableReference.ts`
implements the `useStableMap`/`useStableArrayShallow`/`useStableSet` helpers
that CLAUDE.md's render-perf guidance recommends for defeating `React.memo`
breakage, but no test file in the repository exercises them directly (see
ledger). That guidance is a debugging methodology for a developer chasing a
specific symptom, not itself an automated check, and is not restated as a
second obligation here.

## How to run it

Each harness must be run manually, against a fresh production build, using
the dedicated perf Playwright config -- not the smoke/integration configs CI
uses:

```bash
cd desktop
pnpm build
npx playwright test --config=playwright.perf.config.ts typing-latency.perf.ts
npx playwright test --config=playwright.perf.config.ts warm-switch-markdown.perf.ts
npx playwright test --config=playwright.perf.config.ts cold-switch-longtask.perf.ts
npx playwright test --config=playwright.perf.config.ts --headed scroll-smoothness.perf.ts
```

`scrollback-buzzbugs.perf.ts` additionally requires a live relay reachable
over HTTP and an `nsec`, e.g.:

```bash
kubectl -n sprout port-forward svc/sprout-relay 13000:3000 &
BUZZ_E2E_RELAY_URL=http://127.0.0.1:13000 \
BUZZ_COMMUNITY_HOST=sprout-oss.stage.blox.sqprod.co \
BUZZ_PERF_NSEC=nsec1... \
npx playwright test --config=playwright.perf.config.ts scrollback-buzzbugs.perf.ts
```

`playwright.perf.config.ts`'s webServer step (`reuseExistingServer: true`)
reuses whatever is already listening on `:4173`; kill that process and
rebuild before re-running after a code change, or the measurement is stale.

## Current enforcement status

**Pending.** A real, automated measurement methodology exists -- five
Playwright specs that exercise the actual production build under realistic
synthetic load and print reproducible numbers -- but nothing in this
repository turns those numbers into a pass/fail signal:

- None of the five files is invoked by any GitHub Actions workflow; CI's
  Playwright steps in `.github/workflows/ci.yml` run only the `smoke` and
  `integration` projects defined in `playwright.config.ts`, never the `perf`
  project `playwright.perf.config.ts` defines.
- Where a spec's test body makes an assertion at all, it asserts only that
  the harness recorded real measurements (a non-zero count, a positive
  duration), never that any latency, longtask or layout-cost number stayed
  under a threshold. Two of the five state this in their own comments,
  verbatim: "Instrument, not a gate."

So a change that regresses composer typing latency, channel-switch cost, or
scroll smoothness produces no automated signal today. Catching one requires
a person to run the relevant harness by hand, read the printed numbers, and
judge them -- exactly the manual methodology CLAUDE.md's Common Gotchas #6
already documents for the general React-render-perf case.

## Limits

What the existing harnesses do and do not establish, even when run by hand:

- **No stored baseline.** Nothing in the repository records a previous run's
  numbers to diff against; a human reads the printed report and judges it
  from memory or from a linked issue, not from a comparison the tooling
  performs.
- **Simulated load, not measured production traffic.** Scenario parameters
  (8 agents, 250ms typing-indicator interval, 600-row seeded channels, and
  so on) are chosen by each spec's author as "realistic," per their own
  comments, not derived from measured production telemetry.
- **Headless/headed Chromium under CDP throttle, not the shipped shell.**
  `scroll-smoothness.perf.ts` and `cold-switch-longtask.perf.ts` both state
  explicitly, in their own doc-comments, that they measure Chromium
  main-thread cost and do **not** reproduce the WKWebView compositor
  behavior of the actual shipped Tauri desktop app -- named in
  `scroll-smoothness.perf.ts` as a separately-tracked "real-wheel pass."
- **`scrollback-buzzbugs.perf.ts` depends on a live staging relay and a
  human-supplied key**, so it cannot run unattended and its results also
  reflect that relay's current load and network path, not only the client.
- **Desktop only.** This node's obligation and evidence are scoped to
  `desktop/`. The web (`web/`) and mobile (`mobile/`) clients were checked
  (see ledger) and have no comparable automated performance harness at the
  recorded revision -- that is an absence, not a claim that either performs
  adequately.
- **The render-perf debugging methodology in CLAUDE.md is unverified by any
  test.** `useStableReference.ts`'s three hooks have no adjacent test file,
  so nothing in the repository asserts they actually preserve reference
  identity as documented, nor that any specific desktop component's
  `React.memo` boundary depends on them working correctly.

## Scope and omissions

**This node covers** whether an automated, CI-enforced performance
regression gate exists for the Buzz desktop client's composer, channel-switch
and scrollback interactions, and catalogs the real (but non-gating, non-CI)
instrumentation that exists today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Why |
|---|---|
| Relay/server-side latency and throughput | A distinct obligation about a different container (`architecture-containers-relay`); would need its own test-contract node if one is written. |
| Web client (`web/`) performance | Checked at the recorded revision: no `*perf*`/`*benchmark*`/`*lighthouse*` file exists there. Absence, not a verified-good result. |
| Mobile client (`mobile/`) performance | Same check, same result: no comparable Flutter benchmark harness found. |
| Whether `useStableReference.ts`'s hooks correctly preserve reference identity | No test exercises them; that is a gap in the *implementation's* test coverage, not this documentation node's to close. |
| What specifically constitutes the "timeline-virtualization acceptance gate" `cold-switch-longtask.perf.ts`'s doc-comment names | Not located in any other file, issue, or PR description read for this node; the phrase is reported rather than resolved. |
| Whether or when this instrumentation should be wired into CI as a real gate | A product/process decision this node does not make. |

**No second obligation was folded in.** The five `*.perf.ts` harnesses
measure different interactions (typing, switching, scrolling, live
scroll-back) but share one property this node treats as a single obligation:
none of them currently gates anything. If any one of them gains a real,
CI-enforced threshold in the future, that harness's obligation becomes
independently verifiable and should get its own test-contract node at that
point, superseding its coverage here.

**Relationships, checked rather than assumed absent.** At the recorded
revision, `origin/launchpad`'s corpus tree carries no other node under
`verification/` -- this is the first. `architecture-containers-desktop`
(the Tauri desktop container this obligation concerns) is loadable from
`origin/launchpad`, so the `references` edge above resolves today.
`corpus-standard-test-references` and `corpus-standard-evidence` are also
loadable, but neither states anything specific to this node's subject that a
reader does not already reach via `AGENTS.md`'s own cross-references, so no
edge to either is declared, per the same reasoning `standards/confidence.md`
and `standards/evidence.md` give for their own sparse relationship sections.

**Expected but not verified when this node was written:**

- **Whether `useStableReference.ts`'s hooks are actually load-bearing for any
  specific desktop component's render performance was not established** --
  only that the helpers exist and that CLAUDE.md recommends them for the
  general pattern.
- **The "timeline-virtualization acceptance gate" `cold-switch-longtask.perf.ts`
  names was not traced to a specific PR, issue or review checklist.** It may
  be a PR-review convention rather than anything encoded in the repository;
  this node reports the phrase rather than resolving what backs it.
- **Whether any of the five harnesses have ever actually been run against a
  real desktop build, and what numbers they produced, was not established.**
  This node cites what the files measure and how they are invoked, not any
  historical run's output.
