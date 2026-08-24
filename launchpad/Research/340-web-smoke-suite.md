---
description: What web/tests/e2e/smoke.spec.ts covers and whether it passes — six fully-mocked tests covering the home page and the invite flow, all green, and no automation anywhere runs them.
tags: [testing, web, playwright, e2e, ci-gap, research, issue-340]
---

# What does the web smoke suite cover, and does it pass?

## Finding

**Six tests. All six pass. Nothing runs them.**

#290 states twice that "the web client has zero tests" and lists web-client tests as one of only
three pieces of genuinely unowned new scope. That premise is wrong. `web/tests/e2e/smoke.spec.ts`
is 349 lines covering the home page and four invite-flow paths, it is fully mocked so it needs no
relay, and it passes in nine seconds.

What is true — and is the actual gap — is that **no CI job and no `just` recipe in `just ci` runs
it.** The work is not "write the first web test". It is "run the suite that already exists".

## The six tests

```
$ grep -nE "^test\(" web/tests/e2e/smoke.spec.ts
4:test("home page loads with Buzz branding",
11:test("home page shows repositories section",
16:test("invite requires age and legal consent before opening Buzz",
123:test("invite can enroll a NIP-07 identity for browser access",
204:test("invite asks Safari users to choose their Mac download",
263:test("invite download falls back for mobile and non-desktop devices",
```

Two cover the repository-browser home page the relay serves: that the Buzz logo renders inside
`<main>`, and that the "Repositories" section appears.

Four cover the **invite landing flow**, which is the substantive part:

- **Consent gating** — age attestation and legal consent must be satisfied before the flow opens
  Buzz. Backed by a mocked `/api/join-policy` returning `terms_markdown`, `privacy_markdown`,
  `age_attestation_required: true` and a policy version.
- **NIP-07 enrollment** — a browser extension identity can be enrolled for browser access. The
  test injects a fake extension via `page.addInitScript` and mocks `/api/invites/claim`.
- **Safari download choice** — Safari users are asked to choose their Mac download.
- **Non-desktop fallback** — mobile and other non-desktop devices get a fallback download path.

That is a real slice of a user-facing flow with security-relevant behaviour in it (consent before
enrollment), not a placeholder smoke test.

## It needs no relay

Eight route interceptions and two init scripts:

```
$ grep -c "page.route" web/tests/e2e/smoke.spec.ts
8
```

`**/api/join-policy`, `**/api/invites/claim` and `https://api.github.com/**` are all fulfilled from
the test. `web/playwright.config.ts` declares its own `webServer` — a `vite preview` on
`127.0.0.1:4173` — so the only dependency is a built frontend. This is the cheapest possible suite
to wire into CI: no Postgres, no Redis, no relay, no live network.

It also mirrors the desktop config exactly, including the retry policy ADR-0020 adopts:

```typescript
  retries: process.env.CI ? 2 : 0,
```

## The run

```
Running 6 tests using 1 worker

  ✓  1 [smoke] › tests/e2e/smoke.spec.ts:4:1 › home page loads with Buzz branding (2.0s)
  ✓  2 [smoke] › tests/e2e/smoke.spec.ts:11:1 › home page shows repositories section (488ms)
  ✓  3 [smoke] › tests/e2e/smoke.spec.ts:16:1 › invite requires age and legal consent before opening Buzz (1.1s)
  ✓  4 [smoke] › tests/e2e/smoke.spec.ts:123:1 › invite can enroll a NIP-07 identity for browser access (612ms)
  ✓  5 [smoke] › tests/e2e/smoke.spec.ts:204:1 › invite asks Safari users to choose their Mac download (1.9s)
  ✓  6 [smoke] › tests/e2e/smoke.spec.ts:263:1 › invite download falls back for mobile and non-desktop devices (1.5s)

  6 passed (9.0s)
test_exit=0
```

**Nine seconds.** Whatever the argument against wiring this into CI, runtime is not it.

### How it had to be run, and why that qualifies the result

`just web-e2e-smoke` could not be used. It calls `pnpm test:e2e:smoke`, and this host cannot
resolve pnpm at all — the repo pins `pnpm@11.4.0` and pnpm dropped macOS-Intel builds at v11.0.5
(established in #322). So dependencies were installed with **npm**, not from `pnpm-lock.yaml`:

```
$ npm install --no-audit --no-fund     # in web/
reinstall_exit=0
```

Two consequences worth stating plainly. First, the installed `@playwright/test` is **1.60.0** while
`web/package.json` pins `^1.58.2` — npm resolved the caret to a newer version than the lockfile
would have. Second, the preview server was started by hand (`./node_modules/.bin/vite preview
--port 4173`) because the config's `webServer` command also shells out to pnpm.

A first attempt failed for an environment reason worth recording, since it looks exactly like a
product failure:

```
    - You have two different versions of @playwright/test. This usually happens
      when one of the dependencies in your package.json depends on @playwright/test.
  1 failed
  5 did not run
```

A root `node_modules/.pnpm/playwright@1.60.0` tree exists in this checkout (installed by another
process, not by me), so `npx playwright` resolved the runner from the root while the spec imported
`@playwright/test` from `web/node_modules` — the same version, two copies. Invoking
`web/node_modules/.bin/playwright` directly resolved it. **The failure was mine, not the suite's**,
and it is the kind of thing that would read as "the web tests are broken" in a hasty report.

## Nothing runs it

The `web` CI job (`.github/workflows/ci.yml:815-849`) has exactly two substantive steps:

```yaml
      - name: Web lint and format
        run: just web-check
      - name: Web build
        run: just web-build
```

`just web-check` is `pnpm check` (biome plus two file-size guards); `just web-build` is
`pnpm build`. Neither runs a test.

A recipe exists and is not called by anything:

```
justfile:658:web-e2e-smoke:
justfile:659:    cd {{web_dir}} && pnpm test:e2e:smoke
```

And `just ci` (`justfile:292`) chains `web-build` without it:

```
ci: check test-unit desktop-test desktop-build desktop-tauri-check desktop-tauri-test web-build mobile-test
```

So the suite is reachable only by a human typing `just web-e2e-smoke`, which nothing in the
repository asks anyone to do.

## What this changes for #290

**Two statements in the PRD need correcting.** "The web client has zero tests. There is a `web` CI
job; nothing under `web/` matches a test pattern" is false — one 349-line spec matches, and the
`find` in #340's own body demonstrates it. And web-client tests should come off the list of
"genuinely unowned, and this PRD's only new scope", because the suite exists and has an author.

**Criterion 3 gains its cheapest possible win.** Nine seconds, no infrastructure, one recipe that
already exists. Adding `web-e2e-smoke` to the `web` job is close to free, and per #328 the `web`
job already skips entirely unless `web/**` or `pnpm-lock.yaml` changed, so it costs nothing on
unrelated pull requests.

**Criterion 8 gains a more accurate entry.** Not "the web client is untested" but "the web client
has a six-test smoke suite covering the home page and the invite flow; it is not run by
automation, and nothing covers the repository browser beyond two visibility assertions."

## Confidence and what was not checked

**High confidence:** the six test names and what each asserts (read from source), that the suite is
fully mocked (eight interceptions counted, all endpoints named), that it passes (raw output above),
and that nothing runs it (`ci.yml` and `justfile` read directly).

**Not checked:**

- **The suite was not run with lockfile-pinned dependencies.** `@playwright/test` 1.60.0 was used
  where the lockfile would have chosen something satisfying `^1.58.2`. The suite passing here is
  strong evidence it passes in CI, but it is not the same run. Anyone with a working pnpm can settle
  it in nine seconds with `just web-e2e-smoke`.
- **It was run once.** Nothing here speaks to flakiness, which matters because `retries: CI ? 2 : 0`
  means CI would silently absorb a flake that a local run would expose.
- **Only the `smoke` project was run.** `web/package.json` also declares `test:e2e`, which runs the
  whole `testDir`. Since `smoke`'s `testMatch` is `**/smoke.spec.ts` and that is the only spec
  present, I expect these are currently the same set — but I did not verify that no other spec is
  picked up by the broader command.
- **Chromium only.** The config declares a single project using `devices["Desktop Chrome"]`. The
  Safari-specific test asserts behaviour for a spoofed Safari user agent, not on real WebKit.
- **I left `web/node_modules` in place** (~gitignored, confirmed via `git check-ignore`). The
  tracked tree is unchanged, but the working directory now has an npm-installed dependency tree
  where a pnpm one would normally be, which could confuse a later `pnpm install` on this machine.
