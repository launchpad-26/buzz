---
id: development-run-web
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Justfile binds `web_dir := \"web\"` and defines a `web` recipe with no prerequisite recipes whose body is exactly: a bash shebang with `set -euo pipefail`; `[[ -d node_modules ]] || pnpm install`; `source scripts/instance-env.sh`; `export VITE_PORT=$((BUZZ_VITE_PORT + 100))`; `export VITE_RELAY_URL=\"${BUZZ_RELAY_URL}\"`; an echo of the chosen port and relay; `cd {{web_dir}}`; and `pnpm exec vite --port \"${VITE_PORT}\" --strictPort`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The `web` recipe's `[[ -d node_modules ]] || pnpm install` guard and its `source scripts/instance-env.sh` both run before `cd {{web_dir}}`, so both act on the repository root rather than on web/."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "web/package.json declares the package name buzz-web, private, version 0.1.0, type module, and scripts dev (`vite`), build (`tsc && vite build`), typecheck (`tsc --noEmit`), check:file-sizes, check:pubkey-truncation, lint (`biome lint .`), check (`biome check . && pnpm check:pubkey-truncation`), format, preview (`vite preview`), test:e2e (`pnpm build && playwright test`) and test:e2e:smoke (`pnpm build && playwright test --project=smoke`)."
    entry_class: FACT
    evidence:
      - "web/package.json"
  - statement: "web/vite.config.ts sets `server.port` to `parseInt(process.env.VITE_PORT || \"5173\", 10)` with `strictPort: true`, aliases `@` to `/src`, and registers the TanStack router plugin (routes directory ./src/app/routes, generated tree ./src/app/routeTree.gen.ts, virtual route config ./src/app/routes.ts) alongside @vitejs/plugin-react."
    entry_class: FACT
    evidence:
      - "web/vite.config.ts"
  - statement: "scripts/instance-env.sh derives BASE_PORT as `10000 + sha256(worktree root path) % 55000`, exports BUZZ_VITE_PORT=BASE_PORT, reads the relay port out of BUZZ_BIND_ADDR (defaulting to 0.0.0.0:3000, hence port 3000) into BUZZ_RELAY_PORT, and exports BUZZ_RELAY_URL defaulting to ws://localhost:${BUZZ_RELAY_PORT}; the worktree root comes from `git rev-parse --show-toplevel`."
    entry_class: FACT
    evidence:
      - "scripts/instance-env.sh"
  - statement: "Because `just web` sets VITE_PORT to BUZZ_VITE_PORT + 100 and BUZZ_VITE_PORT is 10000 + (hash % 55000), the web dev server's port is deterministic per worktree path and always lands in the range 10100-65099, which is why two worktrees do not collide and why the port is not a fixed, memorable number."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - "scripts/instance-env.sh"
    confidence: 0.9
  - statement: "web/src/shared/lib/relay-url.ts's relayWsUrl() returns import.meta.env.VITE_RELAY_URL when that is set, and otherwise derives the relay URL from the current page's own origin as `ws(s)://window.location.host`; relayHttpBaseUrl() converts that result from ws:// to http:// and wss:// to https://."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/relay-url.ts"
  - statement: "Running the dev server without VITE_RELAY_URL set (for example a bare `pnpm -C web dev`) leaves relayWsUrl()'s same-origin fallback pointing the client at the Vite dev server's own host and port rather than at a relay, so the client would attempt to speak the relay protocol to Vite; `just web` avoids this by exporting VITE_RELAY_URL from BUZZ_RELAY_URL before starting Vite."
    entry_class: INFERENCE
    evidence:
      - "web/src/shared/lib/relay-url.ts"
      - "Justfile"
      - "scripts/instance-env.sh"
    confidence: 0.85
  - statement: ".env.example documents BUZZ_WEB_DIR as an optional path to the web UI dist directory that makes the relay serve the web frontend at / for browser requests, and instructs the reader to \"Leave unset for local dev (use `just web` for Vite HMR instead)\", with the variable itself left commented out."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "Justfile's `relay-web` recipe depends on `bootstrap` and `_ensure-migrations`, exports the repo's bin/ onto PATH, allexport-sources .env, runs `[[ -d node_modules ]] || pnpm install`, then `pnpm -C web build`, then `BUZZ_WEB_DIR=./web/dist cargo run -p buzz-relay`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "crates/buzz-relay/src/config.rs reads BUZZ_WEB_DIR (trimmed, empty treated as unset) and BUZZ_SERVE_GIT_WEB_GUI (true only for the literal strings \"true\" or \"1\", default false), and returns ConfigError::InvalidValue -- a startup failure, not a warning -- when BUZZ_WEB_DIR names a directory that does not contain an index.html file; a unit test in the same file asserts serve_git_web_gui defaults to false."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/router.rs installs the static bundle only as a fallback service: with a web_dir configured it serves any path under /assets/ from the directory, and otherwise serves index.html only when should_serve_spa(path, serve_git_web_gui) is true -- which is is_invite_landing_path(path) (a non-empty /invite/{code} containing no further slash) OR, only when serve_git_web_gui is enabled, is_git_web_gui_path(path) (\"/\", \"/repos\", or anything starting \"/repos/\"). Everything else returns 404."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "web/src/app/routes.ts declares five client routes -- index \"/\", /invite/$code, /repos, /repos/$repoId and /repos/$repoId/blob/$ -- so the relay's default served surface (invite links only) is narrower than the route set the Vite dev server serves."
    entry_class: FACT
    evidence:
      - "web/src/app/routes.ts"
      - "crates/buzz-relay/src/router.rs"
  - statement: "pnpm-workspace.yaml lists exactly three packages -- desktop, web and admin-web -- so they share one workspace and one root pnpm-lock.yaml; the same file carries the repository's dependency overrides and patchedDependencies."
    entry_class: FACT
    evidence:
      - "pnpm-workspace.yaml"
  - statement: "Because web is a member of the root pnpm workspace, a `pnpm install` run at the repository root -- which is what `just desktop-install` runs and what the `web` recipe's node_modules guard falls back to -- is expected to resolve web's dependencies too rather than requiring a separate install inside web/."
    entry_class: INFERENCE
    evidence:
      - "pnpm-workspace.yaml"
      - "Justfile"
    confidence: 0.8
  - statement: "Justfile's `setup` recipe depends on `bootstrap` and runs ./scripts/dev-setup.sh, and that script installs Node dependencies by running `pnpm install` inside the desktop directory and again inside the web directory as two separate steps, warning and skipping if pnpm is not on PATH."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/dev-setup.sh"
  - statement: "Justfile's `bootstrap` recipe puts the repository's bin/ on PATH, warms cargo/node/pnpm through Hermit, hard-fails when docker is absent, copies .env.example to .env when .env is missing, and runs ./scripts/ensure-local-relay-key.sh .env."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Justfile defines the web quality recipes as thin wrappers: web-check is `cd web && pnpm check`, web-fix is `cd web && pnpm exec biome check --write .`, web-typecheck is `cd web && pnpm typecheck`, web-build is `cd web && pnpm build`, and web-e2e-smoke is `cd web && pnpm test:e2e:smoke`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "web/playwright.config.ts sets testDir ./tests/e2e, baseURL http://127.0.0.1:4173, a single smoke project matching **/smoke.spec.ts, and a webServer that runs `pnpm exec vite preview --port 4173 --strictPort --host 127.0.0.1` with reuseExistingServer enabled whenever CI is unset."
    entry_class: FACT
    evidence:
      - "web/playwright.config.ts"
  - statement: "web/tests/e2e/smoke.spec.ts's first two tests navigate to \"/\" and assert the Buzz branding image inside the main landmark and the text \"Repositories\" are visible, so a passing smoke run is evidence the served bundle renders its home route."
    entry_class: FACT
    evidence:
      - "web/tests/e2e/smoke.spec.ts"
  - statement: ".github/workflows/ci.yml runs `just web-check` and `just web-build` as job steps after `pnpm install --frozen-lockfile`, and no workflow under .github/workflows/ references web-e2e-smoke or test:e2e at all, so the browser smoke suite is a local-only command."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "grep(-rn 'web-e2e|test:e2e', .github/workflows/, cwd=repo root, revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> no matches, exit 0 on the surrounding pipeline"
  - statement: "lefthook.yml runs `just web-fix` as a hook lane, so web formatting and lint fixes are applied by the repository's own git hooks rather than only by a manual command."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "Justfile's `down` recipe is `docker compose down` and `ps` is `docker compose ps`; the `clean` recipe runs only `cargo clean` and `cargo clean --manifest-path desktop/src-tauri/Cargo.toml`, so it removes neither web/dist nor node_modules."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "admin-web is a separate bundle with its own run path: Justfile's `admin` recipe builds it with `pnpm -C admin-web build`, points BUZZ_ADMIN_WEB_DIR at admin-web/dist, defaults BUZZ_ADMIN_HOST to admin.localhost:3000 and BUZZ_ADMIN_AUTH to disabled, and router.rs checks the admin host first so admin requests can never fall through to the public web bundle."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "crates/buzz-relay/src/router.rs"
  - statement: "At revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90 the corpus directory launchpad/docs/corpus/development/ contains exactly four Markdown files -- build.md, debugging.md, hermit.md and prerequisites.md -- so no run-desktop, run-mobile or run-relay node exists to link to yet."
    entry_class: FACT
    evidence:
      - "ls(launchpad/docs/corpus/development/, cwd=worktree root, revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> build.md, debugging.md, hermit.md, prerequisites.md"
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
  - statement: "The node ids named in this node's relationships were each read from origin/launchpad rather than from this branch: development/build.md carries id corpus-development-build, development/prerequisites.md carries development-prerequisites, development/hermit.md carries development-hermit, architecture/containers/web.md carries architecture-containers-web, and layers/configuration/relay-configuration.md carries layers-configuration-relay-configuration."
    entry_class: FACT
    evidence:
      - "git_show(origin/launchpad:launchpad/docs/corpus/development/build.md, development/prerequisites.md, development/hermit.md, architecture/containers/web.md, layers/configuration/relay-configuration.md; line 2 of each) -> id: corpus-development-build, id: development-prerequisites, id: development-hermit, id: architecture-containers-web, id: layers-configuration-relay-configuration"
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/architecture/containers/web.md"
  - statement: "The default local development loop for the web client is the Vite dev server, and the relay-served bundle exists to exercise the narrower production-shaped surface (invite landing, and the git browser behind a flag) rather than as the everyday way to work on the client."
    entry_class: INFERENCE
    evidence:
      - ".env.example"
      - "Justfile"
      - "crates/buzz-relay/src/router.rs"
    confidence: 0.85
  - statement: "This node exists as the single canonical procedure for running the web client locally, scoped to running rather than building, per its authoring task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issue #867 (parent PRD #619)"
relationships:
  - type: depends-on
    target: development-prerequisites
  - type: depends-on
    target: development-hermit
  - type: references
    target: corpus-development-build
  - type: references
    target: architecture-containers-web
  - type: references
    target: layers-configuration-relay-configuration
---

# Running the Buzz web client locally

## Goal

Get the browser web client — the `web/` package, `buzz-web`, which serves the
invite landing page and the repository browser — running on your machine so you
can load it, change its source, and see the change. This node covers **running**
it. Producing the compiled bundle is `corpus-development-build`'s subject, and
what the bundle *is* architecturally is `architecture-containers-web`'s.

There are two run modes and they are not interchangeable:

| Mode | Command | What it gives you | What it costs |
|---|---|---|---|
| Vite dev server | `just web` | Hot module reload, every client route, no relay build | Client is served by Vite, not by the relay |
| Relay-served bundle | `just relay-web` | The production serving path, exactly as the relay does it | Full rebuild per change; only `/invite/{code}` by default |

Pick the dev server unless you are specifically testing how the relay serves the
bundle. `.env.example` says so in as many words next to `BUZZ_WEB_DIR`: *"Leave
unset for local dev (use `just web` for Vite HMR instead)."*

## Prerequisites and allowed scope

**Environment.** Activate the repository's Hermit toolchain first so the pinned
`node`, `pnpm` and `cargo` win over anything else on `PATH`:

```bash
. ./bin/activate-hermit
```

`development-hermit` owns that toolchain; `development-prerequisites` owns the
wider machine setup.

**Dependencies.** `web` is one of exactly three packages in the root pnpm
workspace (`desktop`, `web`, `admin-web`, per `pnpm-workspace.yaml`), sharing a
single root `pnpm-lock.yaml`. You do not need a `web`-specific install step:

- `just setup` runs `scripts/dev-setup.sh`, which installs Node dependencies for
  `desktop/` and `web/` as two separate `pnpm install` steps.
- `just desktop-install` runs a plain `pnpm install` at the repository root.
- `just web` itself falls back to `pnpm install` at the repository root whenever
  a root `node_modules` directory is absent — so the recipe self-heals a missing
  install rather than failing.

**A relay is only required for mode B.** `just web` has *no* prerequisite
recipes: it does not start Docker, does not run migrations, and does not build
or start the relay. It merely *points* the client at a relay URL. Load the client
without a relay running and the page will render but its relay-backed data will
not resolve. `just relay-web`, by contrast, depends on `bootstrap` and
`_ensure-migrations`, so it does start Docker services and apply migrations.

**Scope of this node.** Local development only. Not deployment, not the desktop
or mobile clients, not `admin-web` (see the last section).

## Mode A — the Vite dev server (`just web`)

This is the loop you want almost always.

### Step 1 — start a relay, if you want relay-backed data

In a separate shell, from the repository root:

```bash
just relay
```

Skip this only if you are working on something that does not need relay data.
The client will still load.

### Step 2 — start the dev server

```bash
just web
```

The recipe, in order: ensures root `node_modules` exists, sources
`scripts/instance-env.sh`, sets `VITE_PORT` to `BUZZ_VITE_PORT + 100`, exports
`VITE_RELAY_URL` from `BUZZ_RELAY_URL`, prints the port and relay it chose, then
runs `pnpm exec vite --port "$VITE_PORT" --strictPort` from inside `web/`.

### Step 3 — read the port off the recipe's own output

**Do not guess the URL.** `scripts/instance-env.sh` derives a base port as
`10000 + sha256(<worktree root path>) % 55000`, so `BUZZ_VITE_PORT` — and hence
the web port at `+100` — is deterministic *per checkout path* and lands somewhere
in 10100–65099. That is deliberate: two worktrees of this repository get
different ports and can run side by side. The recipe echoes the value it picked:

```
Starting web dev server on port <port>, relay ws://localhost:3000
```

Open `http://localhost:<port>`. `--strictPort` means Vite fails rather than
silently sliding to the next free port, so the printed number is the real one.

### Why not just run `pnpm -C web dev`?

You can, but understand what you lose. That script is a bare `vite`, so:

- The port comes from `vite.config.ts`, which reads `process.env.VITE_PORT` and
  falls back to **5173** — no worktree isolation.
- `VITE_RELAY_URL` is unset, and `web/src/shared/lib/relay-url.ts` then falls back
  to deriving the relay from the page's own origin
  (`ws(s)://window.location.host`). That points the client at the Vite dev server
  itself instead of at a relay. Expect relay connections to fail in a way that
  looks like a relay bug and is not.

Set `VITE_RELAY_URL` yourself if you take this path.

## Mode B — the bundle served by the relay (`just relay-web`)

Use this when the thing under test is *the relay serving the bundle*: the invite
landing page, asset paths, the SPA fallback, cross-origin behaviour.

### Step 1 — run the combined recipe

```bash
just relay-web
```

It builds `web/dist` with `pnpm -C web build` and then starts the relay in the
same shell with `BUZZ_WEB_DIR=./web/dist`. There is no separate web server
process in this mode — the relay is the server.

### Step 2 — expect a narrow served surface

This is the step that surprises people. `crates/buzz-relay/src/router.rs`
installs the bundle as a *fallback service* and serves `index.html` only for
paths that pass `should_serve_spa`:

- `/invite/{code}` — always, provided `{code}` is non-empty and contains no
  further slash.
- `/`, `/repos`, `/repos/...` — **only** when `BUZZ_SERVE_GIT_WEB_GUI` is set to
  the literal `true` or `1`. It defaults to false, and `just relay-web` does not
  set it.
- `/assets/...` — served from the directory whenever a web dir is configured.

Everything else 404s. So under a default `just relay-web`, browsing to `/`
returns 404 even though `web/src/app/routes.ts` declares an index route. The
client declares five routes (`/`, `/invite/$code`, `/repos`, `/repos/$repoId`,
`/repos/$repoId/blob/$`); the relay's default serves one of them. To see the
repository browser through the relay, set `BUZZ_SERVE_GIT_WEB_GUI=true` in
`.env` before starting. `layers-configuration-relay-configuration` owns the full
variable contract.

### Step 3 — know the startup failure mode

If `BUZZ_WEB_DIR` names a directory with no `index.html`, the relay does not warn
and continue — `config.rs` returns `ConfigError::InvalidValue` and the relay
refuses to start. A stale or missing `web/dist` therefore surfaces as a relay
that will not boot, not as a blank page.

## Success verification

Verify in this order, cheapest first.

1. **The server is up on the port it announced.** For mode A, the URL printed by
   the recipe loads. For mode B, the relay logs
   `BUZZ_WEB_DIR=... — serving web UI from relay` at startup (emitted by
   `config.rs` when the directory validates).
2. **The bundle renders.** Mode A: `http://localhost:<port>/` shows the home
   page. Mode B (default flags): `http://localhost:3000/invite/<any-code>` serves
   the SPA; `/` correctly 404s.
3. **Types and lint still hold.**

   ```bash
   just web-typecheck   # cd web && pnpm typecheck  (tsc --noEmit)
   just web-check       # cd web && pnpm check      (biome + pubkey-truncation guard)
   ```

   These are the same commands CI runs — `.github/workflows/ci.yml` invokes
   `just web-check` and `just web-build` directly. `lefthook.yml` also runs
   `just web-fix` as a hook lane, so formatting is normally fixed for you.
4. **The browser smoke suite passes.**

   ```bash
   just web-e2e-smoke   # cd web && pnpm test:e2e:smoke
   ```

   This builds first (`pnpm build && playwright test --project=smoke`) and starts
   its own preview server — `vite preview --port 4173 --strictPort --host
   127.0.0.1`, with `baseURL` `http://127.0.0.1:4173`. Its first two tests load
   `/` and assert the Buzz branding image and the text "Repositories" are
   visible, which is a real end-to-end check that the built bundle renders.

   **Two cautions.** `reuseExistingServer` is enabled whenever `CI` is unset, so
   a preview server left running from an earlier build will serve *stale* code to
   your test run — kill port 4173 first if you have rebuilt. And no workflow
   under `.github/workflows/` references `web-e2e-smoke` or `test:e2e`, so this
   suite is local-only: CI will not catch what it would have caught.

## Rollback and cleanup

Nothing in either mode mutates tracked files, so there is no rollback in the
version-control sense. What does persist:

| Left behind | Removed by |
|---|---|
| The dev server / relay process | `Ctrl-C` in its shell |
| Docker services started by `just relay-web`'s `bootstrap`/`_ensure-migrations` | `just down` (`docker compose down`); `just ps` to check |
| `web/dist` from mode B | Delete it by hand — `just clean` runs only the two `cargo clean` invocations and touches neither `web/dist` nor `node_modules` |
| `web/playwright-report/` from a smoke run | Delete by hand |
| A `.env` created by `bootstrap` when none existed | Left in place deliberately; it is gitignored and holds your generated relay key |

If mode B has confused your local relay, the return path is to unset
`BUZZ_WEB_DIR` (leave it commented in `.env`, as shipped) and use `just relay`
plus `just web` again.

## Authoritative commands

Every command here is defined in the repository; none is generic advice. Read
the definition rather than trusting this table if they ever disagree.

| Command | Defined in | Expands to |
|---|---|---|
| `just web` | `Justfile` | port/relay env from `scripts/instance-env.sh`, then `pnpm exec vite --port $VITE_PORT --strictPort` in `web/` |
| `just relay-web` | `Justfile` | `pnpm -C web build`, then `BUZZ_WEB_DIR=./web/dist cargo run -p buzz-relay` |
| `just relay` | `Justfile` | `cargo run -p buzz-relay` after `bootstrap` and `_ensure-migrations` |
| `just web-check` | `Justfile` | `cd web && pnpm check` |
| `just web-fix` | `Justfile` | `cd web && pnpm exec biome check --write .` |
| `just web-typecheck` | `Justfile` | `cd web && pnpm typecheck` |
| `just web-e2e-smoke` | `Justfile` | `cd web && pnpm test:e2e:smoke` |
| `just setup` | `Justfile`, `scripts/dev-setup.sh` | Docker services, migrations, `pnpm install` in `desktop/` and `web/` |
| `just down` | `Justfile` | `docker compose down` |

Configuration surfaces: `web/vite.config.ts` (port, aliases, router plugin),
`web/package.json` (scripts), `web/playwright.config.ts` (preview server, base
URL), `scripts/instance-env.sh` (port derivation), `.env.example`
(`BUZZ_WEB_DIR`, `BUZZ_BIND_ADDR`).

## Scope and omissions

### What this node does not cover, and who owns it

- **Building the bundle.** `just web-build` and the wider build story belong to
  `corpus-development-build`.
- **What the web container is.** Its architecture, deployment shape and
  production wiring belong to `architecture-containers-web`.
- **Relay environment variables in full.** `BUZZ_WEB_DIR`,
  `BUZZ_SERVE_GIT_WEB_GUI` and the rest are described here only as far as running
  the client requires; `layers-configuration-relay-configuration` is canonical.
- **Toolchain and machine setup.** `development-hermit` and
  `development-prerequisites`.
- **Running the desktop client, the mobile app, or the relay as subjects in
  their own right.** At the recorded revision `launchpad/docs/corpus/development/`
  holds exactly four files — `build.md`, `debugging.md`, `hermit.md`,
  `prerequisites.md` — so there is no `run-desktop`, `run-mobile` or `run-relay`
  node to link to yet, and this node deliberately does not absorb their subject
  matter.
- **`admin-web`.** It is a *separate* bundle with a separate run path, not part
  of this loop: `just admin` builds it with `pnpm -C admin-web build`, serves it
  via `BUZZ_ADMIN_WEB_DIR` on a distinct host (`BUZZ_ADMIN_HOST`, defaulting to
  `admin.localhost:3000`) with auth defaulted to `disabled` locally, and
  `router.rs` checks the admin host *first* so an admin request can never fall
  through to the public web bundle. It shares only the pnpm workspace and
  lockfile. Running it deserves its own node.

### What was expected but not verified here

- **Neither `just web` nor `just relay-web` was executed.** Every claim about
  their behaviour is read from the recipes and from the code they invoke, at the
  recorded revision. The printed-port line, the relay startup log and the 404
  behaviour are traced through `Justfile`, `scripts/instance-env.sh`,
  `config.rs` and `router.rs` rather than observed running.
- **The pnpm workspace claim is reasoned, not run.** That a root `pnpm install`
  populates `web/`'s dependencies follows from `web` being a workspace member;
  it is recorded as an inference with confidence, not as fact, because no install
  was performed to confirm it.
- **The smoke suite was not run.** Its behaviour is read from
  `web/playwright.config.ts` and `web/tests/e2e/smoke.spec.ts`.
- **Browser-side runtime behaviour was not observed.** The same-origin fallback
  in `relay-url.ts` is traced through the source; no browser was pointed at a
  dev server to watch the resulting connection attempt.
