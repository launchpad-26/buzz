---
id: verification-e2e-web
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
  - statement: "web/package.json defines test:e2e (`pnpm build && playwright test`) and test:e2e:smoke (`pnpm build && playwright test --project=smoke`), and web/playwright.config.ts configures exactly one project, `smoke`, matching `**/smoke.spec.ts`, run against Desktop Chrome behind a `vite preview` web server bound to 127.0.0.1:4173."
    entry_class: FACT
    evidence:
      - "web/package.json"
      - "web/playwright.config.ts"
  - statement: "web/tests/e2e/smoke.spec.ts is a real Playwright end-to-end suite of six test() cases exercising the built production bundle in a real headless browser: the home page renders Buzz branding and a Repositories section with no network mocking at all; the invite landing page enforces an age/legal consent gate before enabling 'Accept invite in Buzz' (join-policy and GitHub-releases calls intercepted via page.route); a NIP-07 browser identity can complete the invite-claim POST with a NIP-98-shaped Authorization header; Safari/macOS users are offered an architecture-specific Mac chooser dialog; and non-desktop user agents (iPhone, iPadOS desktop mode, Android, ChromeOS) fall back to a generic releases-page link instead of a direct download."
    entry_class: FACT
    evidence:
      - "web/tests/e2e/smoke.spec.ts"
  - statement: "None of the six test() cases in web/tests/e2e/smoke.spec.ts navigates to a /repos or /repos/* route, interacts with any Git-browser UI, or exercises isomorphic-git clone/fetch behavior; the suite covers only the home-page shell and the invite-acceptance flow, not the Git repository browser feature documented in architecture-containers-web."
    entry_class: FACT
    evidence:
      - "web/tests/e2e/smoke.spec.ts"
  - statement: "No workflow under .github/workflows/ references the strings 'web-e2e-smoke', 'test:e2e:smoke', or 'test:e2e'; the only CI job touching web/ (.github/workflows/ci.yml's 'web' job, lines 919-950) runs exactly `just web-check` and `just web-build` and never invokes Playwright. Justfile's own aggregate targets confirm the same gap locally: `check` (line 96) depends on `web-check` but not `web-e2e-smoke`, and `ci` (line 307) depends on `web-build` but not `web-e2e-smoke` -- the suite is reachable only by running `just web-e2e-smoke` (Justfile:730-731) or `pnpm -C web test:e2e:smoke` directly."
    entry_class: FACT
    evidence:
      - "grep(-rn, ['web-e2e-smoke','test:e2e:smoke','test:e2e'], .github/workflows/) -> no matches"
      - ".github/workflows/ci.yml:919-950"
      - "Justfile:96"
      - "Justfile:307"
      - "Justfile:730-731"
  - statement: "At commit 473205a7457b208455f188847bfb27b01aa83cac, running `pnpm install` then `pnpm test:e2e:smoke` inside web/ (headless Chromium, Playwright 1.60.0, against web/'s own freshly built dist/ served by `vite preview` on an unoccupied port) produced 6 passed, 0 failed -- every test() case in web/tests/e2e/smoke.spec.ts currently passes against this revision's built bundle."
    entry_class: FACT
    evidence:
      - "pnpm_test(script='test:e2e:smoke', cwd='web', browser='chromium', port='isolated') -> \"6 passed (2.8m), 0 failed, run 2026-09-01 in this authoring session\""
  - statement: "A first attempt to run this suite on its configured default port (4173) produced 6 spurious failures against an unrelated app (visible DOM text 'Setting up your community...', a string that exists in desktop/src/app/App.tsx but nowhere in web/'s own source or its built dist/ bundle), because a pre-existing, unrelated `vite preview --port 4173` process was already listening on that port and playwright.config.ts's `reuseExistingServer: !process.env.CI` (web/playwright.config.ts:30) silently reused it instead of starting web/'s own preview server; re-running against an unoccupied port produced the clean 6-passed result recorded above."
    entry_class: FACT
    evidence:
      - "web/playwright.config.ts"
      - "ss(flags='-ltnp', filter='4173') -> \"pre-existing vite preview process already bound to 127.0.0.1:4173, started before this session's test run\""
  - statement: "corpus-template-test-contract (this document's template) and architecture-containers-web (the web container node this document verifies) are both loadable from origin/launchpad's corpus tree at the recorded revision, so `implements` and `references` edges to them resolve on the merge target; no other corpus node under launchpad/docs/corpus/verification/ exists yet to relate to."
    entry_class: FACT
    evidence:
      - "git.ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> includes templates/test-contract.md (id corpus-template-test-contract) and architecture/containers/web.md (id architecture-containers-web); no verification/** path present"
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: architecture-containers-web
---

# Web client — end-to-end smoke suite — test contract

## Purpose and boundary

This node documents one obligation covering the `web/` browser client (the
in-browser Buzz client described by `architecture-containers-web`): that its
built production bundle boots and its home-page shell and invite-acceptance
flow render and behave correctly in a real browser. It covers only that
obligation and the Playwright suite that verifies it. It does not cover the
Git-repository-browser feature (cloning, tree/blob/commit browsing via
`isomorphic-git`) that the same container also ships — that feature exists in
`web/src/features/repos/`, but, as recorded in the evidence ledger above, no
test in this suite reaches it, so this node cannot and does not claim
coverage for it.

## Obligation

> `web/`'s built production bundle, served standalone by `vite preview` with
> no live relay behind it, renders both of its user-facing surfaces without a
> rendering or script failure: the home page (Buzz branding image, a
> "Repositories" section heading) with zero network dependency, and the
> invite-acceptance landing page (`/invite/<code>`) — including its
> age/legal consent gate, a NIP-07 browser-identity join flow that POSTs a
> correctly NIP-98-signed claim request, and platform-specific
> desktop-download link selection (a direct installer link on
> Windows/Linux/generic desktop, a macOS chip-chooser dialog on Safari/macOS,
> and a generic releases-page fallback on iOS/iPadOS/Android/ChromeOS) —
> exactly as exercised by `web/tests/e2e/smoke.spec.ts`.

## Verifying test(s)

All six cases live in one file, `web/tests/e2e/smoke.spec.ts`, run under the
`smoke` Playwright project:

- `home page loads with Buzz branding` (line 4) — the home route renders a
  `Buzz`-labelled image inside `<main>`, with no network mocking at all.
- `home page shows repositories section` (line 11) — the home route renders
  a visible "Repositories" heading.
- `invite requires age and legal consent before opening Buzz` (line 16) — the
  invite page's download link, consent checkboxes, and "Accept invite in
  Buzz" button gate correctly (disabled until both boxes are checked), and
  the Terms/Privacy links underline on hover.
- `invite can enroll a NIP-07 identity for browser access` (line 123) — a
  mocked `window.nostr` NIP-07 signer can complete "Join in browser", and the
  intercepted `POST /api/invites/claim` request carries a NIP-98 (`Nostr
  <base64 event>`) Authorization header with the correct `u`/`method`/
  `payload` tags.
- `invite asks Safari users to choose their Mac download` (line 204) — a
  spoofed Safari/macOS user agent is shown a "Which Mac do you have?" dialog
  with correct chip-generation links, and Escape closes it and restores
  focus to the trigger.
- `invite download falls back for mobile and non-desktop devices` (line 263)
  — spoofed iPhone, iPadOS-desktop-mode, Android and ChromeOS user agents all
  get a generic `https://github.com/block/buzz/releases` link rather than a
  direct installer link.

## How to run it

```bash
cd web
pnpm install
pnpm test:e2e:smoke
```

This builds the bundle (`pnpm build`) and then runs only the `smoke`
Playwright project against it. No relay, database, or other Buzz service
needs to be running — every relay-facing HTTP call the invite tests make is
intercepted with `page.route`, and the home-page tests make no network call
at all. `just web-e2e-smoke` runs the identical command from the repository
root.

**Caution — port collision silently invalidates a run.**
`web/playwright.config.ts`'s `webServer.reuseExistingServer` is
`!process.env.CI`, so outside CI it reuses *any* process already listening on
127.0.0.1:4173 instead of failing loudly. If an unrelated `vite preview` (or
any other server) already holds that port — which happened while gathering
evidence for this node — every test runs against the wrong app and fails in
a way that looks like a real defect but is not. Confirm the port is free
(`ss -ltn | grep 4173`) before trusting a red run, or set `CI=1` to force a
fresh, strict-port server instead of a silent reuse.

## Current enforcement status

**Gated**, as of `473205a7457b208455f188847bfb27b01aa83cac`. The suite is
real (not stubbed) and currently passes in full — 6 passed, 0 failed, verified
by direct execution during authoring of this node — but nothing runs it
automatically. No `.github/workflows/*.yml` file invokes `test:e2e`,
`test:e2e:smoke`, or `web-e2e-smoke`; the CI `web` job runs only
`just web-check` and `just web-build`. Locally, neither `just check` nor
`just ci` depends on `web-e2e-smoke` either. The only paths that run it are a
developer or agent invoking `just web-e2e-smoke` or `pnpm -C web
test:e2e:smoke` by hand. Nothing today would block a pull request that broke
this suite.

## Limits

**What a green run of this suite proves:** that, in a headless Chromium
browser, `web/`'s built static bundle renders its home-page shell and
completes the invite-acceptance flow's client-side logic (consent gating,
NIP-07 signing, platform-based download-link selection) correctly, entirely
decoupled from any backend — every relay-facing call the tests exercise is
intercepted and fulfilled by Playwright's own route mocks, not a real relay.

**What it does not prove:**

- **Nothing about the Git repository browser.** No test navigates to `/`,
  `/repos`, or `/repos/*` with real repository content, so cloning,
  tree/blob/commit rendering, and `isomorphic-git`'s IndexedDB-backed
  filesystem are entirely unexercised by this suite.
- **Nothing about real relay integration.** The suite never runs against a
  live `buzz-relay` process; NIP-42 WebSocket authentication, the real
  `/api/join-policy` and `/api/invites/claim` handlers, and NIP-98 signature
  *verification* server-side are all bypassed by mocks that only check the
  *shape* of the outgoing request, not that a real relay would accept it.
- **Nothing about being served by `buzz-relay` itself.** The suite runs
  against `vite preview`, not against the relay's own `ServeDir`/SPA-fallback
  routing (`BUZZ_WEB_DIR`, `BUZZ_SERVE_GIT_WEB_GUI`) that
  `architecture-containers-web` documents as this bundle's actual production
  serving path.
- **One browser engine only.** The `smoke` project runs Desktop Chrome only;
  there is no Firefox or WebKit coverage, and the "Safari" and "mobile"
  scenarios are simulated by spoofing `navigator.userAgent`/`platform` on
  Chromium, not run on real Safari, iOS, or Android browsers.
- **A single point-in-time run.** The 6-passed result above is one execution
  at one revision, captured in this authoring session; it is not a
  continuously re-verified claim, because nothing re-runs this suite on
  later commits (see *Current enforcement status*).

## Scope and omissions

**This node covers** the `web/` client's home-page and invite-flow smoke
obligation, its verifying Playwright suite, how to run it, its honest
enforcement status, and what a passing run does and does not establish.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `web` container's full responsibility, technology, and interfaces | `architecture-containers-web` |
| Whether and how the Git-repository-browser feature is end-to-end tested at all | Not yet documented in this corpus; no such test was found during authoring |
| General corpus test-citation conventions | `corpus-standard-test-references` |
| Server-side verification of NIP-98/NIP-42 the relay itself performs | Not this node's subject; would belong to a relay-side auth verification node |
| Whether this suite should be wired into CI, and where | Not decided here; this node only records that it currently is not |

**Expected but not verified when this node was written:**

- **Whether this suite has ever been run in CI, at any point in this
  repository's history, on any branch.** Only the current workflow files at
  the recorded revision were checked; git history of `.github/workflows/`
  was not searched.
- **Browser-engine coverage beyond Chromium was not exercised**, because
  `playwright.config.ts` defines no Firefox or WebKit project to run.
- **Whether the suite passes on a from-scratch CI runner (`ubuntu-latest`,
  matching the `web` job's own `runs-on`)** was not directly verified — it
  was run in this authoring session's sandbox, not on an actual GitHub
  Actions runner. The sandbox and the CI runner were not compared beyond both
  being Linux/Chromium.
