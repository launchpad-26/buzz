---
id: development-run-desktop
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
  - statement: "The Justfile defines five distinct recipes that launch or serve the desktop app -- dev, desktop-standalone, staging, production and desktop-dev -- and they differ in which backend the app talks to and whether a native Tauri shell is started at all, not merely in speed."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The dev recipe declares the prerequisites `bootstrap _ensure-sidecar-stubs _ensure-migrations`, so a bare `just dev` provisions the toolchain and .env, creates sidecar stubs, brings Docker services up, applies migrations and seeds the local community before any desktop process starts."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Before launching anything, the dev recipe resolves the relay port from BUZZ_BIND_ADDR (default 0.0.0.0:3000), the health port from BUZZ_HEALTH_PORT (default 8080) and the metrics port from BUZZ_METRICS_PORT (default 9102), and -- when lsof is available -- refuses to launch with the message 'Error: <name> port <port> is already in use; refusing to launch desktop against a stale relay.' and a non-zero exit if any of the three already has a listener."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The dev recipe builds exactly seven crates (`cargo build -p buzz-acp -p buzz-agent -p buzz-backend-kubernetes -p buzz-dev-mcp -p buzz-cli -p git-credential-nostr -p buzz-relay`), starts ./target/debug/buzz-relay as a background process, and installs an EXIT trap that runs ../scripts/cleanup-instance-agents.sh for the instance id and kills the relay pid."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/cleanup-instance-agents.sh"
  - statement: "The dev recipe then polls `http://127.0.0.1:${health_port}/_readiness` with curl up to 120 times at 0.5-second intervals, aborting early with 'Error: buzz-relay exited during startup; refusing to launch desktop.' if the relay process dies, and aborting with 'Error: buzz-relay did not become healthy within 60 seconds; refusing to launch desktop.' if the readiness probe never succeeds."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Only after the relay reports ready does the dev recipe change into desktop/, run `pnpm install` if and only if node_modules is absent, source ../scripts/instance-env.sh, and exec `pnpm exec tauri dev --config \"$BUZZ_TAURI_CONFIG\"`."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/instance-env.sh"
  - statement: "The Justfile variable `mesh` defaults to the empty string, and dev, staging and production each append `--features mesh-llm` to the tauri dev invocation only when it is non-empty; the Justfile's own comment states this keeps the default run from building roughly 420 extra crates plus the llama.cpp native runtime, and that the opt-in form is `just mesh=1 dev`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "_ensure-services reads the Docker health status of the containers named buzz-postgres and buzz-redis, exits immediately if both report healthy, otherwise runs `docker compose up -d` and polls both containers 40 times at 3-second intervals before printing ' timed out' and exiting 1."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "_ensure-migrations depends on _ensure-services and then runs `cargo run -p buzz-admin -- migrate` followed by ./scripts/seed-local-community.sh."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/seed-local-community.sh"
  - statement: "docker-compose.yml assigns the container names buzz-postgres, buzz-redis, buzz-adminer, buzz-keycloak, buzz-minio, buzz-minio-init and buzz-prometheus, so the two container names _ensure-services health-checks are the names compose actually creates."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "The bootstrap recipe exports the repository's bin/ ahead of PATH, invokes cargo, node and pnpm once each so Hermit's shims download the pinned versions, exits 1 with 'Error: Docker is required but not installed.' when docker is absent from PATH, copies .env.example to .env when .env does not exist, and finally runs ./scripts/ensure-local-relay-key.sh .env."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/ensure-local-relay-key.sh"
  - statement: "The setup recipe depends on bootstrap and runs ./scripts/dev-setup.sh, which requires both a docker binary and a running daemon, starts services through bin/just _ensure-services, waits for Postgres to accept connections, runs `cargo run -p buzz-admin -- migrate` and seed-local-community.sh, runs pnpm install in desktop/ and in web/, installs lefthook git hooks, and closes by printing `just relay` and `just dev` as the two next steps."
    entry_class: FACT
    evidence:
      - "scripts/dev-setup.sh"
      - "Justfile"
  - statement: "desktop-install is exactly `pnpm install` run at the repository root, which installs for the whole pnpm workspace rather than for desktop/ alone."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "pnpm-workspace.yaml"
  - statement: "The desktop-standalone recipe's own Justfile comment reads 'Run only the desktop app. No relay, database, Docker, migrations, or .env are needed. The app opens normally and asks for a community before making a relay connection.', and its only declared prerequisite is _ensure-sidecar-stubs -- not bootstrap and not _ensure-migrations."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "desktop-standalone builds six crates in debug mode, copies each resulting binary over the zero-byte stub at desktop/src-tauri/binaries/<bin>-<host-target> and chmods it executable, unsets BUZZ_PRIVATE_KEY and BUZZ_SHARE_IDENTITY, and sets BUZZ_DEV_KEYRING_SERVICE to buzz-desktop-dev.<instance-slug>."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Passing fresh=1 to desktop-standalone exports BUZZ_RESET_WEBVIEW_STATE=1 and runs ../scripts/reset-desktop-standalone-state.sh with the instance id and keyring service; the Justfile documents the invocation form as `just fresh=1 desktop-standalone` and scopes it to 'only the current standalone desktop instance'."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/reset-desktop-standalone-state.sh"
  - statement: "instance-env.sh, when BUZZ_RESET_WEBVIEW_STATE is 1, appends ?resetDevState=1 to the Tauri devUrl, and main.tsx's resetDevWebviewStateFromUrl clears window.localStorage and window.sessionStorage on that parameter -- but only under import.meta.env.DEV, and it strips the parameter from the URL afterwards."
    entry_class: FACT
    evidence:
      - "scripts/instance-env.sh"
      - "desktop/src/main.tsx"
  - statement: "The staging recipe exports BUZZ_RELAY_URL=wss://sprout-oss.stage.blox.sqprod.co and the production recipe exports BUZZ_RELAY_URL=wss://buzz.block.builderlab.xyz; both run an unconditional `pnpm install` (commented 'must always start with a clean dep tree'), build their sidecar crates with `cargo build --release`, and copy the release binaries over the stubs."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "staging and production add buzz-backend-kubernetes to the sidecars they overwrite only when the host target does not match *windows*, because -- per the Justfile's own comment -- provider discovery scans the executable's directory for executable buzz-backend-* files and a non-executable stub would hide the provider from the 'Run on' menu."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The desktop-dev recipe declares no prerequisites at all: it changes into desktop/, runs pnpm install only if node_modules is absent, sources ../scripts/instance-env.sh, and runs `pnpm exec vite --port \"${BUZZ_VITE_PORT}\" --strictPort` -- a Vite dev server with no Tauri shell, no relay, no Docker and no migrations."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "instance-env.sh derives a stable base port as 10000 plus (sha256 of the worktree root, as an integer) modulo 55000, exports BUZZ_VITE_PORT as that value and BUZZ_HMR_PORT as one more, derives BUZZ_RELAY_PORT from BUZZ_BIND_ADDR (falling back to 3000), and defaults BUZZ_RELAY_URL to ws://localhost:${BUZZ_RELAY_PORT}."
    entry_class: FACT
    evidence:
      - "scripts/instance-env.sh"
  - statement: "instance-env.sh's own comment states that hardcoding relay port 3000 'pointed the app at whatever else owned that port while the relay listened elsewhere, which surfaces as a connection failure rather than a port mismatch', which is why BUZZ_RELAY_PORT is derived from BUZZ_BIND_ADDR the same way the dev recipe derives it."
    entry_class: FACT
    evidence:
      - "scripts/instance-env.sh"
  - statement: "instance-env.sh builds BUZZ_TAURI_CONFIG as inline JSON carrying build.devUrl, build.beforeDevCommand, identifier xyz.block.buzz.app.dev and productName 'Buzz Dev'; it detects a linked worktree by comparing `git rev-parse --git-dir` against `--git-common-dir` and, only there, derives a branch slug and rewrites the identifier to xyz.block.buzz.app.dev.<slug> with productName 'Buzz Dev (<label>)'."
    entry_class: FACT
    evidence:
      - "scripts/instance-env.sh"
  - statement: "The per-worktree identity rewrite in instance-env.sh is gated on `swift \"$GENERATE_DEV_ICON\" ...` succeeding; when that swift invocation fails the script keeps the shared xyz.block.buzz.app.dev identifier and the default product name."
    entry_class: FACT
    evidence:
      - "scripts/instance-env.sh"
      - "scripts/generate-dev-icon.swift"
  - statement: "instance-env.sh only sets BUZZ_PRIVATE_KEY from a shared identity when BUZZ_SHARE_IDENTITY=1 and the run is inside a linked worktree; it reads the identity from the OS keyring (security on Darwin, secret-tool on Linux) and falls back to identity.key under ~/Library/Application Support, warning to stderr when none is found."
    entry_class: FACT
    evidence:
      - "scripts/instance-env.sh"
  - statement: "desktop/vite.config.ts sets server.port from the VITE_PORT environment variable with a 1420 fallback, sets strictPort true, and configures the HMR port from VITE_HMR_PORT with a 1421 fallback -- the two variables instance-env.sh exports."
    entry_class: FACT
    evidence:
      - "desktop/vite.config.ts"
      - "scripts/instance-env.sh"
  - statement: "desktop/package.json defines build as `tsc && vite build` and build:e2e as `tsc && vite build --mode e2e`, and defines test:e2e:smoke and test:e2e:integration as `pnpm build:e2e` followed by the matching playwright project."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
  - statement: "main.tsx's installE2eBridgeIfConfigured returns without doing anything unless BOTH `import.meta.env.DEV || import.meta.env.MODE === \"e2e\"` and `window.__BUZZ_E2E__` hold; only past that guard does it dynamically import @/testing/e2eBridge and call maybeInstallE2eTauriMocks."
    entry_class: FACT
    evidence:
      - "desktop/src/main.tsx"
  - statement: "main.tsx's configureDevE2eBridgeFromUrl runs only under import.meta.env.DEV, activates only when the URL carries ?e2e=mock, and then sets window.__BUZZ_E2E__ to { mode: \"mock\" } and seeds localStorage with a buzz-communities entry named 'E2E Test' pointing at ws://localhost:3000, an active-community id, and an onboarding-complete flag."
    entry_class: FACT
    evidence:
      - "desktop/src/main.tsx"
  - statement: "desktop/src/testing/e2eBridge.ts is the module that defines window.__TAURI_INTERNALS__ and exports maybeInstallE2eTauriMocks, the function main.tsx calls behind that guard."
    entry_class: FACT
    evidence:
      - "desktop/src/testing/e2eBridge.ts"
  - statement: "The repository's AGENTS.md states 'Always build with `pnpm build:e2e`, never `pnpm run build`', and that a plain build leaves window.__TAURI_INTERNALS__ undefined so every mock-mode spec fails and the app 'renders \"Community connection failed\" instead of the UI under test'; the root CLAUDE.md is a symlink to AGENTS.md, not a second document."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "desktop/src/features/communities/ui/CommunityApplyErrorScreen.tsx renders the literal heading 'Community connection failed' with data-testid community-apply-error, and App.tsx renders that screen when the community state carries a non-empty error."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/ui/CommunityApplyErrorScreen.tsx"
      - "desktop/src/app/App.tsx"
  - statement: "A production-mode bundle produced by plain `pnpm build` cannot install the mock bridge, because import.meta.env.DEV is false and import.meta.env.MODE is not 'e2e', so main.tsx's guard returns before the e2eBridge import and window.__TAURI_INTERNALS__ is never defined -- which is the mechanism behind the failure AGENTS.md describes, though this node did not execute a build to observe it."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/main.tsx"
      - "desktop/package.json"
      - "AGENTS.md"
    confidence: 0.85
  - statement: "desktop/playwright.config.ts sets baseURL http://127.0.0.1:4173 and a webServer block whose command is `python3 -m http.server 4173 -d dist` with reuseExistingServer set to `!process.env.CI` -- that is, reuse is enabled locally and disabled in CI, not unconditionally true."
    entry_class: FACT
    evidence:
      - "desktop/playwright.config.ts"
  - statement: "The desktop-screenshot recipe runs `pnpm -C desktop build:e2e`, then probes http://127.0.0.1:4173/ with curl and starts `python3 -m http.server 4173 -d dist` only if nothing already answers there, before running node tests/helpers/screenshot.mjs."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "desktop/tests/helpers/screenshot.mjs"
  - statement: "Because both the desktop-screenshot recipe and playwright's local webServer adopt whatever process already answers on port 4173 without checking which build produced the dist it serves, a server left running from an earlier build keeps serving stale assets to a later run -- the hazard AGENTS.md records as 'Kill port 4173 and re-run pnpm build:e2e'."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - "desktop/playwright.config.ts"
      - "AGENTS.md"
    confidence: 0.9
  - statement: "The `down` recipe is `docker compose down`, `ps` is `docker compose ps`, `logs *ARGS` is `docker compose logs -f {{ARGS}}`, and `reset` is guarded by a just [confirm(...)] attribute before running ./scripts/dev-reset.sh --yes."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/dev-reset.sh"
  - statement: "The `clean` recipe runs `cargo clean` and `cargo clean --manifest-path desktop/src-tauri/Cargo.toml`, and defines no step that removes desktop/node_modules or desktop/dist."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "On origin/launchpad at the recorded revision, launchpad/docs/corpus/development/ contains exactly four nodes -- build.md, debugging.md, hermit.md and prerequisites.md -- and no run-desktop.md, run-mobile.md, run-relay.md or run-web.md."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> development/build.md, development/debugging.md, development/hermit.md, development/prerequisites.md and no development/run-*.md, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Every relationship target this node declares was resolved against origin/launchpad rather than the authoring worktree: corpus-development-build (development/build.md), development-prerequisites (development/prerequisites.md), architecture-containers-desktop (architecture/containers/desktop.md), architecture-deployment-local-development (architecture/deployment/local-development.md), layers-configuration-desktop-configuration (layers/configuration/desktop-configuration.md) and corpus-template-procedure (templates/procedure.md)."
    entry_class: FACT
    evidence:
      - "git_show(ref='origin/launchpad', paths=['launchpad/docs/corpus/development/build.md','launchpad/docs/corpus/development/prerequisites.md','launchpad/docs/corpus/architecture/containers/desktop.md','launchpad/docs/corpus/architecture/deployment/local-development.md','launchpad/docs/corpus/layers/configuration/desktop-configuration.md','launchpad/docs/corpus/templates/procedure.md']) -> id: corpus-development-build, development-prerequisites, architecture-containers-desktop, architecture-deployment-local-development, layers-configuration-desktop-configuration, corpus-template-procedure"
  - statement: "development/build.md (id corpus-development-build) is merged on origin/launchpad and already owns compiling the Rust workspace and each platform frontend from source, including `just desktop-build`; its See also section states 'Building does not depend on that environment being up; running what you built usually does', and its Scope and omissions table hands 'Running the local dev environment / Docker services the built binaries connect to' to architecture/deployment/local-development.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
  - statement: "The procedure template requires an Overview, an optional Before-you-start section, one numbered sequence per logical goal, See also, a Boundary statement, Relationships and Scope and omissions -- and explicitly permits branch-labelled sequences instead of one flattened numbered list when the task genuinely forks."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "Issue #864 requires that this node state its goal, prerequisites and allowed environment/scope; provide ordered, executable, project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands and configuration rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#864 definition of done"
  - statement: "Issue #864's parent is Feature #619, and the sibling run-path tasks are #865 (development/run-mobile.md), #866 (development/run-relay.md) and #867 (development/run-web.md), all three of which were OPEN and unmerged when this node was written."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#864, #619, #865, #866, #867 (issue titles and states read with gh issue view)"
  - statement: "No desktop run path documented here was executed while authoring this node: the checking environment had no running Docker daemon, no Tauri build toolchain and no display, so every step is cited to the recipe source rather than to an observed run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "the authoring agent's own record of what it could not execute"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: corpus-development-build
  - type: references
    target: development-prerequisites
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-deployment-local-development
  - type: references
    target: layers-configuration-desktop-configuration
---

# Run the Buzz desktop app locally

Start the Tauri desktop app on your own machine and get it talking to a relay --
the task you perform after cloning and setting up, whenever you want to exercise
desktop behaviour by hand rather than through a test. Compiling the app from source is a
different task, owned by `development/build.md`; this node picks up where a working
checkout leaves off.

The repository offers **four distinct run paths**, and choosing wrongly is the most
common way to lose time here. They differ in what backend the app talks to and whether a
native shell is started at all -- not merely in how fast they are.

## Before you start

- **A working toolchain.** `just bootstrap` runs `cargo`, `node` and `pnpm` once each so
  Hermit's shims download the pinned versions, and exits 1 with
  `Error: Docker is required but not installed.` if `docker` is not on `PATH`. What is
  pinned and how activation works belongs to `development/hermit.md` and
  `development/prerequisites.md`, not here.
- **A `.env` file.** `just bootstrap` copies `.env.example` to `.env` when none exists,
  then runs `scripts/ensure-local-relay-key.sh .env`. Paths A and C run `bootstrap`
  automatically; path B does not need `.env` at all.
- **JavaScript dependencies.** `just desktop-install` is exactly `pnpm install` at the
  repository root -- one install covering the whole pnpm workspace, not `desktop/` alone.
  Paths A, B and D run it themselves only when `desktop/node_modules` is missing; paths C
  run `pnpm install` unconditionally on every launch.
- **Docker, for path A only.** `just dev` reaches `_ensure-services`, which health-checks
  the containers named `buzz-postgres` and `buzz-redis` and, if either is unhealthy, runs
  `docker compose up -d` and polls 40 times at 3-second intervals before giving up with
  ` timed out` and exit 1.
- **First-time setup.** `just setup` (which depends on `bootstrap`) runs
  `scripts/dev-setup.sh`: it requires a running Docker daemon, starts services, waits for
  Postgres to accept connections, applies migrations, seeds the local community, installs
  JS dependencies for `desktop/` and `web/`, installs the git hooks, and finishes by
  printing `just relay` and `just dev` as the next two steps. Run it once per checkout.

**Scope of these instructions.** They cover a developer's or agent's own machine against
either a local relay or one of the two hosted relays the `Justfile` names. They do not
cover CI runners, packaged installs, or operating a relay for anyone else.

## Choose a run path

| You want | Path | Command | Native shell | Backend |
|---|---|---|---|---|
| The normal full-stack loop | A | `just dev` | yes (Tauri) | local relay it starts for you, on Docker Postgres + Redis |
| Just the app, nothing else running | B | `just desktop-standalone` | yes (Tauri) | none until you pick a community in the UI |
| The app against a hosted relay | C | `just staging` / `just production` | yes (Tauri) | remote relay, no local services |
| Frontend iteration in a browser | D | `just desktop-dev` | no (Vite only) | whatever `BUZZ_RELAY_URL` names |

## Path A -- full local stack (`just dev`)

Use this when you need real relay behaviour: messages, channels, agents, persistence.

1. Run `just dev` from the repository root. Its declared prerequisites --
   `bootstrap _ensure-sidecar-stubs _ensure-migrations` -- run first, so a bare `just dev`
   also provisions the toolchain and `.env`, writes zero-byte sidecar stubs under
   `desktop/src-tauri/binaries/`, brings Docker services up, runs
   `cargo run -p buzz-admin -- migrate`, and runs `scripts/seed-local-community.sh`.
2. Let the port preflight run. The recipe resolves the relay port from `BUZZ_BIND_ADDR`
   (default `0.0.0.0:3000`), the health port from `BUZZ_HEALTH_PORT` (default `8080`) and
   the metrics port from `BUZZ_METRICS_PORT` (default `9102`). Where `lsof` is available,
   any existing listener on any of the three aborts the launch with
   `Error: <name> port <port> is already in use; refusing to launch desktop against a stale relay.`
   Stop the process it names -- usually a relay from a previous run -- and re-run.
3. Wait through the build. The recipe compiles seven crates in debug mode:
   `buzz-acp`, `buzz-agent`, `buzz-backend-kubernetes`, `buzz-dev-mcp`, `buzz-cli`,
   `git-credential-nostr` and `buzz-relay`.
4. Wait for the relay to report ready. `./target/debug/buzz-relay` is started in the
   background and the recipe polls `http://127.0.0.1:${health_port}/_readiness` up to 120
   times at half-second intervals. It aborts early with
   `Error: buzz-relay exited during startup; refusing to launch desktop.` if the process
   dies, and after 60 seconds with
   `Error: buzz-relay did not become healthy within 60 seconds; refusing to launch desktop.`
5. Let Tauri start. The recipe changes into `desktop/`, runs `pnpm install` only if
   `node_modules` is absent, sources `scripts/instance-env.sh`, prints
   `Starting on Vite port <port>, relay <url>`, and execs
   `pnpm exec tauri dev --config "$BUZZ_TAURI_CONFIG"`.
6. **Only if you are testing mesh compute**, run `just mesh=1 dev` instead. The `mesh`
   variable defaults to empty and only then is `--features mesh-llm` appended; the
   `Justfile`'s own comment explains that the default skips roughly 420 extra crates plus
   the llama.cpp native runtime build.

## Path B -- app only, no backend (`just desktop-standalone`)

Use this to exercise onboarding, the community picker, or any UI that does not need a
populated relay. The `Justfile`'s own comment for this recipe reads: *"Run only the
desktop app. No relay, database, Docker, migrations, or .env are needed. The app opens
normally and asks for a community before making a relay connection."* Its only
prerequisite is `_ensure-sidecar-stubs`.

1. Run `just desktop-standalone`.
2. Let it build six crates in debug mode and **copy the real binaries over the zero-byte
   stubs** at `desktop/src-tauri/binaries/<bin>-<host-target>`, chmod-ing each executable.
   This is the step that distinguishes it from path A, which leaves the stubs in place for
   everything but the relay.
3. Note that the recipe unsets `BUZZ_PRIVATE_KEY` and `BUZZ_SHARE_IDENTITY` and sets
   `BUZZ_DEV_KEYRING_SERVICE` to `buzz-desktop-dev.<instance-slug>`, so this instance gets
   its own identity rather than inheriting a shared dev key.
4. Pick a community in the UI when the app opens. Nothing is connected until you do.
5. **To start from clean state instead**, run `just fresh=1 desktop-standalone`. That
   exports `BUZZ_RESET_WEBVIEW_STATE=1` and runs
   `scripts/reset-desktop-standalone-state.sh` for this instance and keyring service.
   `instance-env.sh` then appends `?resetDevState=1` to the Tauri dev URL, and
   `main.tsx`'s `resetDevWebviewStateFromUrl` clears `localStorage` and `sessionStorage`
   before stripping the parameter back out. The `Justfile` scopes this to *"only the
   current standalone desktop instance"*.

## Path C -- against a hosted relay (`just staging` / `just production`)

Use this to reproduce something seen on a shared relay. No local Docker services are
started; both recipes depend on `bootstrap` and `_ensure-sidecar-stubs` only.

1. Run `just staging` (relay `wss://sprout-oss.stage.blox.sqprod.co`) or `just production`
   (relay `wss://buzz.block.builderlab.xyz`). The `BUZZ_RELAY_URL` is exported by the
   recipe itself.
2. Expect an unconditional `pnpm install` on every launch -- the `Justfile` comments this
   as *"must always start with a clean dep tree"* -- and a **release-mode** sidecar build,
   not debug.
3. Note which sidecars get overwritten: `buzz` always, and `buzz-backend-kubernetes` only
   on non-Windows hosts. The `Justfile` explains why: provider discovery scans the
   executable's directory for executable `buzz-backend-*` files, so leaving the
   non-executable stub in place would hide the provider from the "Run on" menu.
4. Add `mesh=1` here too if you need mesh compute (`just mesh=1 staging`).

## Path D -- frontend only, in a browser (`just desktop-dev`)

Use this for fast CSS and component iteration. It declares **no** prerequisites: it
changes into `desktop/`, installs only if `node_modules` is missing, sources
`instance-env.sh`, and runs `pnpm exec vite --port "${BUZZ_VITE_PORT}" --strictPort`.
There is no Tauri shell, so nothing provides the native IPC the app calls through.

1. Run `just desktop-dev` and open the printed Vite port.
2. **Append `?e2e=mock` to the URL** if you want the app to render without a native shell.
   `main.tsx`'s `configureDevE2eBridgeFromUrl` runs only under `import.meta.env.DEV` and
   only on that parameter; it sets `window.__BUZZ_E2E__` and seeds `localStorage` with a
   community named "E2E Test" pointing at `ws://localhost:3000`, an active-community id,
   and an onboarding-complete flag. `installE2eBridgeIfConfigured` then imports
   `@/testing/e2eBridge`, which is the module that defines `window.__TAURI_INTERNALS__`.
3. **Do not try to get the same result from a plain `pnpm build`.** The bridge guard
   requires `import.meta.env.DEV || import.meta.env.MODE === "e2e"`, and
   `desktop/package.json` gives `build` as `tsc && vite build` against `build:e2e` as
   `tsc && vite build --mode e2e`. `AGENTS.md` states the rule directly -- *"Always build
   with `pnpm build:e2e`, never `pnpm run build`"* -- and records the symptom: the bundle
   has no `window.__TAURI_INTERNALS__` and the app renders **"Community connection
   failed"**, the literal heading in `CommunityApplyErrorScreen.tsx`, instead of the UI you
   wanted. That looks like a product bug and is not one.
4. **Kill any stale server on port 4173 before a screenshot or Playwright run.**
   `just desktop-screenshot` runs `pnpm -C desktop build:e2e`, then starts
   `python3 -m http.server 4173 -d dist` *only if nothing already answers on 4173*;
   `playwright.config.ts` sets `reuseExistingServer: !process.env.CI`, so locally it adopts
   whatever is already listening. Neither checks which build produced the `dist` being
   served, so an old server silently serves old assets.

## Verify it is running

- **Path A.** The recipe prints `Starting on Vite port <port>, relay <url>` only after the
  relay's `/_readiness` probe succeeded, so reaching that line is itself the relay
  health check. Confirm independently with
  `curl -sf http://127.0.0.1:8080/_readiness` (substitute your `BUZZ_HEALTH_PORT`) and
  `just ps` for container status; `just logs` tails all service logs.
- **Paths B and C.** The Tauri window opens and, for C, the printed line names the hosted
  relay URL the app was pointed at. Seeing **"Community connection failed"** here means
  the app started and could not reach or apply that community -- `App.tsx` renders that
  screen from a non-empty community error, with a Retry and a Change community button.
- **Path D.** The Vite port responds. With `?e2e=mock`, the app renders against mock IPC;
  without it, the absence of a native shell is expected, not a fault.
- **Which instance am I looking at?** In a linked worktree, `instance-env.sh` rewrites the
  app identifier to `xyz.block.buzz.app.dev.<branch-slug>` and the product name to
  `Buzz Dev (<label>)` -- but **only if** its `swift scripts/generate-dev-icon.swift`
  invocation succeeds. Where it does not, every worktree shares the plain
  `xyz.block.buzz.app.dev` identity and the default name, so two instances are
  indistinguishable by title. Ports still differ: the base port is
  `10000 + sha256(worktree-root) % 55000`, stable per worktree.

## Stop, roll back, and clean up

1. **Stop the app.** Ctrl-C in the terminal running the recipe. Path A's `EXIT` trap kills
   the background relay and runs `scripts/cleanup-instance-agents.sh` for that instance;
   paths B and C install the agent-cleanup half of the same trap.
2. **Stop the services** (path A only): `just down` runs `docker compose down`, which stops
   containers and keeps volumes.
3. **Reset one standalone instance's state:** `just fresh=1 desktop-standalone`, per path B
   step 5. This is the narrow rollback -- it touches this instance only.
4. **Wipe the whole dev environment:** `just reset` runs `scripts/dev-reset.sh --yes` behind
   a `just` `[confirm(...)]` prompt whose text warns that it deletes all development data
   while preserving an installed Buzz. This is destructive; prefer step 2 or 3 first.
5. **Remove build artifacts:** `just clean` runs `cargo clean` and
   `cargo clean --manifest-path desktop/src-tauri/Cargo.toml`. It defines **no** step that
   removes `desktop/node_modules` or `desktop/dist`, so a stale `dist` survives it -- delete
   that directory by hand when a stale bundle is the thing you are chasing.

## See also

- `launchpad/docs/corpus/development/build.md` (`corpus-development-build`) -- compiling
  the workspace and the frontends from source, including `just desktop-build`. Building is
  a separate task from running and that node is canonical for it.
- `launchpad/docs/corpus/development/prerequisites.md` (`development-prerequisites`) and
  `launchpad/docs/corpus/development/hermit.md` (`development-hermit`) -- the toolchain
  these paths assume is already installed.
- `launchpad/docs/corpus/development/debugging.md` (`debugging`) -- what to do once the app
  is running and behaving wrongly.
- `launchpad/docs/corpus/architecture/containers/desktop.md`
  (`architecture-containers-desktop`) -- what the desktop container *is*, as architecture
  rather than as a command to run.
- `launchpad/docs/corpus/architecture/deployment/local-development.md`
  (`architecture-deployment-local-development`) -- the local topology path A brings up.
- `launchpad/docs/corpus/layers/configuration/desktop-configuration.md`
  (`layers-configuration-desktop-configuration`) -- the desktop configuration surface these
  environment variables belong to.
- `Justfile`, `scripts/instance-env.sh`, `scripts/dev-setup.sh`, `desktop/package.json` --
  the authoritative sources for every command above. Where this node and they disagree,
  they win.

## Boundary

This node does not describe:

- **Facts to look up rather than actions to perform** -- the full flag surface of `tauri
  dev`, `vite`, `cargo` or `just`, or an exhaustive list of `BUZZ_*` environment variables.
  `layers-configuration-desktop-configuration` owns the configuration surface; this node
  names only the variables a run path actually reads.
- **How to acquire the underlying skill from scratch** -- a newcomer's tutorial on Tauri,
  React or a pnpm workspace. No corpus template exists for the tutorial form as of this
  writing.
- **Why the desktop app is built this way** -- why community switching remounts rather than
  reloads, why sidecars are stubbed at compile time, why the relay is the source of truth.
  Those are architecture and concept material; `architecture-containers-desktop` is the
  nearest existing node.
- **Compiling the app** -- `corpus-development-build` owns `cargo build --workspace`,
  `just desktop-build` and the platform frontend builds. Where a run path compiles
  something as a side effect (paths A, B and C all do), this node states only what that
  path compiles and why, and defers the build task itself.
- **Running any other Buzz surface** -- the relay on its own (`just relay`,
  `just relay-web`), the web client (`just web`), the admin dashboard (`just admin`), or
  the mobile app (`just mobile-dev`). Those are separate tasks; see *Scope and omissions*.
- **Writing or running desktop tests** -- `just desktop-e2e-smoke`,
  `just desktop-e2e-integration`, `just desktop-screenshot` as a test workflow. Path D
  borrows the mock bridge's *mechanism* because a browser run depends on it, and stops
  there.
- **Packaging or releasing a desktop build** -- `just desktop-release-build`, signing,
  installers and the release pipelines.

## Relationships

Declared, each target resolved with `git show origin/launchpad:<path>` rather than against
this worktree:

- `implements: corpus-template-procedure` -- this node is a how-to-shaped instance of
  `templates/procedure.md`, which names *"a template instance of a standard"* as
  `implements`' own worked case.
- `references: corpus-development-build` -- the build task this run task assumes has either
  already happened or will happen inside the recipe.
- `references: development-prerequisites` -- the toolchain assumed present.
- `references: architecture-containers-desktop` -- what the thing being run is.
- `references: architecture-deployment-local-development` -- the local topology path A
  stands up.
- `references: layers-configuration-desktop-configuration` -- the configuration surface the
  `BUZZ_*` variables named here belong to.

`development-hermit` and `debugging` are linked in *See also* in prose without an authored
edge: activation belongs to `development-prerequisites`' neighbourhood and is reached
through it, and `debugging` picks up strictly after this node's last step rather than
supporting any claim inside it.

## Scope and omissions

**This node covers** the four ways to start the Buzz desktop app on a developer's own
machine -- `just dev`, `just desktop-standalone`, `just staging`/`just production` and
`just desktop-dev` -- what each brings up, what each requires beforehand, how to tell it is
actually running, and how to stop or reset it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Compiling the workspace and frontends from source | `corpus-development-build` (`development/build.md`, merged) |
| Installing and activating the toolchain | `development-prerequisites`, `development-hermit` |
| Diagnosing a running app that misbehaves | `debugging` (`development/debugging.md`) |
| Running the mobile app | `#865` (`development/run-mobile.md`), open and unmerged |
| Running the relay on its own | `#866` (`development/run-relay.md`), open and unmerged |
| Running the web client | `#867` (`development/run-web.md`), open and unmerged |
| The full `BUZZ_*` configuration surface | `layers-configuration-desktop-configuration` |
| The local Docker topology itself | `architecture-deployment-local-development` |
| Writing or running desktop E2E tests and screenshot specs | no corpus node found at this revision; `AGENTS.md` is the current source |
| Packaging, signing or releasing a desktop build | no corpus node found at this revision; `RELEASING.md` and the release workflows |

**Expected but not verified when this node was written:**

- **No run path was executed.** The checking environment had no running Docker daemon, no
  Tauri build toolchain and no display, so every step above is cited to the `Justfile`,
  the scripts and the frontend source, not to an observed run. The procedure template is
  explicit that an executed step is stronger evidence than a described one; this node does
  not have that stronger evidence, and the step ordering, the timeout constants and the
  exact console output are therefore unconfirmed against reality.
- **The plain-build failure mode is reasoned, not reproduced.** That a production bundle
  leaves `window.__TAURI_INTERNALS__` undefined follows from `main.tsx`'s guard and
  `package.json`'s two build scripts, and matches what `AGENTS.md` records; no build was
  run to watch "Community connection failed" appear. It is recorded as an INFERENCE at 0.85
  confidence, not as a FACT.
- **The stale-4173 hazard is reasoned from two configurations, not observed.** Recorded as
  an INFERENCE at 0.9. Note also that `AGENTS.md` describes the setting as
  `reuseExistingServer: true` while `playwright.config.ts` actually sets
  `!process.env.CI`; the practical local behaviour is the same, but the guide's wording is
  imprecise about CI.
- **Whether `?e2e=mock` is a supported developer workflow or only a test affordance was not
  established.** `main.tsx` gates it behind `import.meta.env.DEV` and it plainly works
  under `just desktop-dev`, but no document found at this revision recommends it for
  ordinary frontend iteration.
- **Platform coverage of the per-worktree identity rewrite is unresolved.**
  `instance-env.sh` gates it on a `swift` invocation succeeding, and the shared-identity
  fallback path reads `~/Library/Application Support`. Both read as macOS-first; what
  happens to instance naming on Linux or Windows was not tested here, only read.
