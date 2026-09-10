---
id: development-run-relay
type: development
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The Justfile's `relay` recipe declares two prerequisites, `bootstrap` and `_ensure-migrations`, and its own body exports the repository's `bin/` directory onto PATH, sources `.env` under `set -o allexport`, and then runs `cargo run -p buzz-relay`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`_ensure-migrations` itself declares `_ensure-services` as its prerequisite and runs `cargo run -p buzz-admin -- migrate` followed by `./scripts/seed-local-community.sh`, so a single `just relay` invocation transitively starts Docker services, applies migrations and seeds the local community before the relay process is launched."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`bootstrap` runs `cargo`, `node` and `pnpm` once each to trigger Hermit's lazy tool download, aborts with an install link if the `docker` command is absent, copies `.env.example` to `.env` when `.env` does not exist, and then runs `./scripts/ensure-local-relay-key.sh .env`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`scripts/ensure-local-relay-key.sh` sources the target env file, exits early after `chmod 600` when `BUZZ_RELAY_PRIVATE_KEY` is already non-empty, and otherwise generates a fresh 32-byte secp256k1-range hex key via Node's `randomBytes`, rejecting zero and any value at or above the curve order."
    entry_class: FACT
    evidence:
      - "scripts/ensure-local-relay-key.sh"
  - statement: "The relay refuses to start without a relay key: `relay_keypair_from_config` returns an error reading `BUZZ_RELAY_PRIVATE_KEY must be set. Run \\`just bootstrap\\` for local development or configure a stable 32-byte hex private key.` when the configured value is absent."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "`.env.example` ships `BUZZ_BIND_ADDR=0.0.0.0:3000`, `RELAY_URL=ws://localhost:3000`, `DATABASE_URL=postgres://buzz:buzz_dev@localhost:5432/buzz` and `REDIS_URL=redis://localhost:6379` as live (uncommented) values, while `BUZZ_RELAY_PRIVATE_KEY` is present only as a commented placeholder."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "`.env.example` contains no `BUZZ_AUTO_MIGRATE` assignment at all, commented or otherwise."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "`crates/buzz-relay/src/main.rs` applies migrations only when `buzz_auto_migrate_enabled` accepts the `BUZZ_AUTO_MIGRATE` environment variable -- it treats only `true`, `1`, `yes` and `on` (case-insensitively, after trimming) as enabled, and logs `Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled` in every other case, including when the variable is unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The relay emits an ordered startup log sequence a developer can read as a success signal: `Starting buzz-relay`, then a `Config loaded` record carrying `bind_addr`, `relay_url`, `health_port` and `metrics_port` fields, then either `Database migrations complete` or the skip message above, then `Health probe listener started` with a `port` field, and finally `buzz-relay TCP listening` with an `addr` field."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Both listener binds fail closed and name the offending port in the error: the health listener maps its bind error to `Failed to bind health port {port}: {e}` and the main listener to `Failed to bind {bind_addr}: {e}`, each propagated with `?` so startup aborts rather than continuing with one listener missing."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "`config.rs` reads `BUZZ_HEALTH_PORT` and falls back to 8080, and reads `BUZZ_METRICS_PORT` and falls back to 9102, in both cases treating an unparseable value the same as an unset one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`router.rs` registers `/health`, `/_liveness` and `/_readiness` on the main API router, and separately `build_health_router` registers `/_liveness`, `/_readiness`, `/_status` and `/_mesh` on a health-only router documented in its own doc comment as having no metrics middleware, no auth, no CORS and no body limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The relay's shutdown path waits on SIGTERM or Ctrl+C, sets a shutting-down flag, logs `Shutdown signal received -- readiness now returns 503`, sleeps five seconds, logs `Starting graceful drain (30s timeout)`, and arms a backstop that logs `Drain timeout exceeded -- forcing exit` and calls `std::process::exit(1)` after the drain timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "`just down` runs `docker compose down` with no `-v` flag, and `just ps` and `just logs *ARGS` wrap `docker compose ps` and `docker compose logs -f {{ARGS}}` respectively."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Three run variants exist alongside `just relay`: `relay-web` builds `web` with pnpm and starts the relay with `BUZZ_WEB_DIR=./web/dist`, `relay-release` runs `cargo run -p buzz-relay --release`, and `admin` builds `admin-web`, defaults `BUZZ_ADMIN_HOST` to `admin.localhost:3000` and `BUZZ_ADMIN_AUTH` to `disabled`, then runs the same relay binary."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`scripts/seed-local-community.sh`'s own header comment states the relay intentionally fails closed when the request Host header is not in `communities`, and that local dev uses loopback hosts so bootstrap must create those rows after migrations before desktop/Tauri HTTP bridge calls can succeed."
    entry_class: FACT
    evidence:
      - "scripts/seed-local-community.sh"
  - statement: "TESTING.md documents the port-collision workaround for running a second relay alongside Buzz Desktop as exporting `BUZZ_BIND_ADDR`, `BUZZ_HEALTH_PORT`, `BUZZ_METRICS_PORT` and `RELAY_URL` in the relay's own terminal before launching, noting `RELAY_URL` is the value advertised in NIP-42 challenges."
    entry_class: FACT
    evidence:
      - "TESTING.md"
  - statement: "The Justfile sets `set dotenv-load := true` at file scope, so `just` loads `.env` for every recipe independently of the explicit `source .env` inside the `relay` recipe body."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The already-merged corpus node architecture-deployment-local-development owns the compose topology, the network boundaries, the persistence model, the `_ensure-services` health-wait behavior and the destructive `just reset` recovery path, and separately records that the top-level AGENTS.md description of migrations as auto-applied on relay startup is production framing rather than the local mechanism."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/local-development.md"
  - statement: "The already-merged corpus node debugging owns the `curl` reachability probes against `/health` and `/_readiness`, the `just logs` widening step and the symptom-localization workflow for a misbehaving local relay."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/debugging.md"
  - statement: "The already-merged corpus node layers-observability-health-checks owns the health-check surface itself -- the dedicated listener, the endpoint semantics and the Kubernetes probe plumbing -- so this procedure links to it rather than restating endpoint behavior."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/health-checks.md"
  - statement: "The already-merged corpus node layers-lifecycle-graceful-shutdown owns the relay's drain contract and its timing budget, documenting the 30-second GRACEFUL_DRAIN_TIMEOUT backstop, the preceding 5-second grace, and the 5s + 30s = 35s worst case from SIGTERM to forced exit."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md"
  - statement: "The already-merged corpus node layers-configuration-relay-configuration catalogues the relay's environment variables in per-area settings tables (network/pool/connection, auth/membership/identity, rate limiting, media and S3, ephemeral channels, product toggles, git server, push gateway, join policy/admin/web UI), including BUZZ_HEALTH_PORT with its 8080 default."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/configuration/relay-configuration.md"
  - statement: "The already-merged corpus nodes development-hermit and development-prerequisites own toolchain activation and the tool floor respectively -- development-hermit states that Hermit is activated once per shell with `. ./bin/activate-hermit` and that `just bootstrap` can pre-download every pinned tool, and development-prerequisites catalogues the tools and minimum versions needed before building or running Buzz from source."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
  - statement: "The already-merged corpus node corpus-development-build owns compiling the Rust workspace and each platform frontend and confirming each build produced its output, a distinct task from running an already-buildable relay."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
  - statement: "Because `.env.example` sets no `BUZZ_AUTO_MIGRATE` and the relay's gate is opt-in, invoking `cargo run -p buzz-relay` directly rather than through `just relay` starts a relay that neither applies pending migrations nor seeds the local community, since both are Justfile prerequisites rather than relay startup behavior."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - ".env.example"
      - "crates/buzz-relay/src/main.rs"
    confidence: 0.9
  - statement: "Ctrl+C in the terminal running `just relay` reaches the relay process's own signal handler rather than killing it outright, because the handler selects over `tokio::signal::ctrl_c()` alongside SIGTERM, so the graceful drain sequence is the expected foreground stop path."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
    confidence: 0.85
  - statement: "Issue #866 requires that this node state goal, prerequisites and allowed environment/scope, provide ordered executable project-specific steps, define success verification and rollback/cleanup where relevant, and link authoritative commands rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#866 definition of done"
  - statement: "Issue #866 requires that any newly discovered second concept, contract or procedure be filed as a separate task rather than folded into this document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#866 definition of done"
  - statement: "This node's claims were established by reading the cited files at the recorded revision; no `just setup`, `just relay`, `just down` or `docker compose` invocation was executed while authoring it, so the log lines, error strings and timings quoted above are read from source rather than observed from a running relay."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#866 task scope (author one corpus node from repository evidence, not operate the dev stack)"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: architecture-deployment-local-development
  - type: references
    target: development-prerequisites
  - type: references
    target: layers-observability-health-checks
---

# Run the relay locally: how-to

Start a local `buzz-relay` on your own machine and confirm it came up — the task a
developer or agent performs before exercising the desktop app, the CLI, the web
client, or any integration test that needs a live relay. This guide covers the
foreground development relay only; it is not about deploying one.

## Before you start

- **The pinned toolchain, activated.** Run `. ./bin/activate-hermit` from the
  repository root so `./bin` leads `PATH` and the pinned `cargo`, `node`, `pnpm` and
  `just` win over anything installed system-wide. `just relay` also prepends the
  repository's `bin/` to `PATH` inside its own recipe body, so the pinned toolchain
  is used either way — but every command in this guide that is *not* a `just` recipe
  assumes an activated shell. See `development-prerequisites` for the tool floor and
  `development-hermit` for how the pin itself works.
- **A running Docker daemon.** `just bootstrap` aborts with an install link if the
  `docker` command is missing, and the service-start step fails against a daemon that
  is not up.
- **Nothing else already bound to `:3000`, `:8080` or `:9102`.** The relay binds all
  three. If Buzz Desktop or an earlier session is already listening, jump to
  *Run a second relay alongside an existing one* below rather than starting this one.
- **You do not need `.env` in place yet.** Step 1 creates it.

## Start the relay

1. **Create `.env` and the local relay identity.**

   ```bash
   just bootstrap
   ```

   This triggers Hermit's lazy tool download, checks for `docker`, copies
   `.env.example` to `.env` if `.env` does not already exist, and runs
   `scripts/ensure-local-relay-key.sh .env`. That script leaves an existing
   `BUZZ_RELAY_PRIVATE_KEY` untouched (only tightening the file to mode `600`) and
   otherwise generates a fresh 32-byte hex key inside the secp256k1 curve order. The
   relay will not start without that key — it exits with
   `BUZZ_RELAY_PRIVATE_KEY must be set. Run \`just bootstrap\` for local development
   or configure a stable 32-byte hex private key.`

   `just relay` declares `bootstrap` as a prerequisite, so this step is really a
   *review* opportunity, not a separate obligation: run it on its own the first time
   so you can read `.env` before anything consumes it.

2. **Review `.env`.** The values that decide where the relay lands are already live
   in `.env.example` and therefore in your fresh copy: `BUZZ_BIND_ADDR=0.0.0.0:3000`,
   `RELAY_URL=ws://localhost:3000`,
   `DATABASE_URL=postgres://buzz:buzz_dev@localhost:5432/buzz`, and
   `REDIS_URL=redis://localhost:6379`. Change them now if you need to; the Justfile
   sets `set dotenv-load := true`, and the `relay` recipe additionally sources `.env`
   under `set -o allexport`, so edits take effect on the next `just relay` with no
   further wiring.

3. **Run first-time setup, once per clone.**

   ```bash
   just setup
   ```

   This is the only step in this guide that installs anything beyond the relay's own
   dependencies: it runs `scripts/dev-setup.sh`, which starts and health-waits the
   Docker services, applies migrations, seeds the local community, installs the
   desktop and web JS dependencies, and installs the git hooks. Skip it on subsequent
   runs — step 4 covers everything the relay itself needs.

4. **Start the relay.**

   ```bash
   just relay
   ```

   One command covers the whole chain. `relay` declares `bootstrap` and
   `_ensure-migrations` as prerequisites; `_ensure-migrations` in turn declares
   `_ensure-services`. So `just relay` starts the Docker services and waits for
   Postgres and Redis to report healthy, runs `cargo run -p buzz-admin -- migrate`,
   runs `scripts/seed-local-community.sh`, and only then exports the repository
   `bin/` onto `PATH`, sources `.env`, and executes `cargo run -p buzz-relay` in the
   foreground.

   **Why this matters more than it looks.** The relay does *not* migrate itself by
   default: `main.rs` gates `db.migrate()` behind `BUZZ_AUTO_MIGRATE`, accepting only
   `true`, `1`, `yes` or `on`, and `.env.example` sets that variable nowhere.
   Launching `cargo run -p buzz-relay` by hand therefore starts a relay against
   whatever schema happens to be present, with no local community seeded — and
   `seed-local-community.sh`'s own header notes the relay fails closed when a request
   Host header is not in `communities`, which is exactly the loopback-host case local
   dev depends on. Use `just relay`. The migration mechanism itself belongs to
   `architecture-deployment-local-development`, which also explains why the top-level
   `AGENTS.md` describes migrations as auto-applied.

5. **Leave the terminal open.** `just relay` runs in the foreground. Everything that
   follows happens either in the relay's own terminal or in a second one.

## Verify it started

The relay's own startup log is the primary success signal, and it is emitted in a
fixed order. Read it in the terminal from step 4 rather than probing from outside:

1. **`Starting buzz-relay`** — the process is alive and reached `main`.
2. **`Config loaded`** — configuration parsed. This record carries `bind_addr`,
   `relay_url`, `health_port` and `metrics_port` fields; confirm they are the values
   you intended, especially if you overrode any of them.
3. **A migration line** — either `Database migrations complete` (only if you
   deliberately set `BUZZ_AUTO_MIGRATE`) or, in the default local flow,
   `Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled`. The skip
   message is expected here and is not a failure: step 4's `_ensure-migrations`
   prerequisite already applied them.
4. **`Health probe listener started`**, carrying a `port` field — the health-only
   listener is up. `BUZZ_HEALTH_PORT` defaults to `8080`.
5. **`buzz-relay TCP listening`**, carrying an `addr` field — the main listener is up
   and the relay is accepting connections. This is the line that means "started".

**If a listener cannot bind, startup aborts and names the port.** The health bind
error reads `Failed to bind health port {port}: {e}` and the main bind error reads
`Failed to bind {bind_addr}: {e}`; both are propagated with `?`, so the process exits
rather than running half-listening. A missing final line in the sequence above,
followed by one of those errors, is a port collision — see the next section.

For probing the relay from outside the process — `curl` against `/health` or
`/_readiness` — and for what to do when it does *not* come up, use the `debugging`
node; it owns the reachability probes and the symptom-localization workflow, and this
guide deliberately does not restate them.

## Run a second relay alongside an existing one

Buzz binds three ports, and any of them can collide with Buzz Desktop or a relay left
running from an earlier session. Export all four variables in the relay's own terminal
before launching — `RELAY_URL` included, because it is the value advertised in NIP-42
challenges and a mismatched one produces auth failures rather than connection
failures:

```bash
export BUZZ_BIND_ADDR=0.0.0.0:3030
export BUZZ_HEALTH_PORT=8088
export BUZZ_METRICS_PORT=9202
export RELAY_URL=ws://localhost:3030
```

`TESTING.md` is the authoritative version of this workaround, including which
variables the *client* terminals then need.

## Variants

Pick one of these instead of `just relay` when you need what it adds; all three share
the same `bootstrap` and `_ensure-migrations` prerequisites.

| Command | Adds |
|---|---|
| `just relay-web` | Builds `web` with pnpm and serves it from the relay via `BUZZ_WEB_DIR=./web/dist` |
| `just relay-release` | `cargo run -p buzz-relay --release` — slower to build, representative performance |
| `just admin` | Builds `admin-web` and starts the same relay binary with `BUZZ_ADMIN_HOST` defaulting to `admin.localhost:3000` and `BUZZ_ADMIN_AUTH` defaulting to `disabled` |

## Stop and clean up

1. **Stop the relay with Ctrl+C** in its own terminal. The signal handler selects over
   `tokio::signal::ctrl_c()` and SIGTERM, so this is a graceful stop, not a kill: the
   relay logs `Shutdown signal received — readiness now returns 503`, waits five
   seconds so a load balancer can stop routing to it, logs
   `Starting graceful drain (30s timeout)`, and arms a backstop that logs
   `Drain timeout exceeded — forcing exit` and exits `1` if the drain overruns.
   Expect the process to take a few seconds to return your prompt. The full drain
   contract is `layers-lifecycle-graceful-shutdown`'s subject, not this guide's.

2. **Leave the Docker services running** if you will start the relay again shortly —
   `_ensure-services` is a no-op once Postgres and Redis are healthy, so the next
   `just relay` starts faster.

3. **Or stop them, keeping your data.**

   ```bash
   just down     # docker compose down — no -v, so named volumes survive
   just ps       # docker compose ps — confirm what is still up
   just logs     # docker compose logs -f — tail every service
   ```

   `just down` carries no `-v` flag, so the Postgres, MinIO and Prometheus volumes are
   untouched and the next `just relay` resumes against the same data.

**Rollback is not part of this procedure.** Nothing in the start path above writes
irreversible state: `bootstrap` only creates `.env` if it is absent and only generates
a key if none is set, and stopping the relay leaves the database as it was. If local
state is genuinely corrupt and needs discarding, that is the destructive
`just reset` path — owned in full by `architecture-deployment-local-development`,
which documents what it deletes and what it preserves. Do not reach for it as a
routine part of starting the relay.

## Authoritative commands and configuration

This node describes them; it does not replace reading them.

- [`Justfile`](../../../../Justfile) — `bootstrap`, `setup`, `relay`, `relay-web`,
  `relay-release`, `admin`, `down`, `ps`, `logs`, and the internal `_ensure-services`
  and `_ensure-migrations` recipes.
- [`.env.example`](../../../../.env.example) — every variable the relay reads, with
  its default and comment.
- [`scripts/dev-setup.sh`](../../../../scripts/dev-setup.sh) — what `just setup` runs.
- [`scripts/ensure-local-relay-key.sh`](../../../../scripts/ensure-local-relay-key.sh)
  — relay identity generation.
- [`scripts/seed-local-community.sh`](../../../../scripts/seed-local-community.sh) —
  the loopback host-to-community rows the relay's fail-closed host binding requires.
- [`TESTING.md`](../../../../TESTING.md) — the live local relay runbook, the
  port-collision workaround, and the full environment variable table.

## See also

- `architecture-deployment-local-development` — the local topology this procedure
  starts a process inside: what runs in Docker, what runs natively, the network and
  persistence boundaries, and the destructive reset path.
- `debugging` — what to do when the relay does not come up, or misbehaves once it has.
- `layers-observability-health-checks` — the health surface itself: the dedicated
  listener, the endpoint semantics, and the probe plumbing.
- `corpus-development-build` — compiling the workspace and confirming a build
  produced its output, for when `cargo run` is not the shape you want.
- `development-prerequisites` and `development-hermit` — the tool floor and the pin.

## Boundary

This node does not describe:

- **Facts to look up rather than actions to perform** — the full environment variable
  table (`TESTING.md` and `layers-configuration-relay-configuration`), the health
  endpoint semantics (`layers-observability-health-checks`), or the compose service
  inventory (`architecture-deployment-local-development`).
- **How to acquire the underlying skill from scratch**, for someone who has never run
  a service locally — a tutorial, which has no corpus template as of this writing.
- **Why the local architecture is shaped this way** — why migrations are an explicit
  step, why the relay binds three ports, why host binding fails closed. Those are
  `architecture-deployment-local-development`'s and the principle nodes' subject.
- **Diagnosing a relay that started and then behaved unexpectedly.** This guide stops
  at "it came up". `debugging` picks up there.
- **Running any other Buzz surface** — the desktop app (`just dev`), the web client
  (`just web`), the mobile app (`just mobile-dev`) or the ACP harness. Each is a
  separate procedure, not a subsection of this one.
- **Running a relay anywhere but a development machine.** Staging and production
  relay operation is owned by the deployment nodes and the operator repositories.

## Relationships

- `implements: corpus-template-procedure` — this node takes the how-to form that
  template prescribes.
- `references: architecture-deployment-local-development` — background the reader is
  assumed to have, and the owner of the reset path and migration mechanism this guide
  deliberately does not restate.
- `references: development-prerequisites` — the tool floor *Before you start* defers
  to.
- `references: layers-observability-health-checks` — the lookup content the
  *Verify it started* section defers to rather than inlining.

Each target was confirmed present on `origin/launchpad` before being declared, with
`git grep -l "^id: <id>$" origin/launchpad -- launchpad/docs/corpus`, not against this
worktree.

## Scope and omissions

**This node covers** the ordered, repository-specific procedure for starting a
`buzz-relay` on a local development machine: creating `.env` and the local relay
identity, the one-time `just setup`, the single `just relay` invocation and the
prerequisite chain it triggers, the startup log sequence that signals success, the
port-collision variant for running alongside an existing relay, the three run
variants, and the graceful foreground stop plus the non-destructive
`just down` / `ps` / `logs` cleanup commands.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Compose topology, network/persistence boundaries, and the destructive `just reset` recovery path | `architecture-deployment-local-development` |
| `curl` reachability probes and symptom localization for a misbehaving relay | `debugging` |
| Health/readiness/liveness endpoint semantics and probe plumbing | `layers-observability-health-checks` |
| The graceful drain contract and its timing budget | `layers-lifecycle-graceful-shutdown` |
| The full relay environment variable table | `layers-configuration-relay-configuration` and `TESTING.md` |
| Tool floor and toolchain pinning | `development-prerequisites`, `development-hermit` |
| Compiling the workspace and verifying build outputs | `corpus-development-build` |
| Running the desktop, web, mobile or agent surfaces | separate tasks, not filed by this node |

**Expected but not verified when this node was written:**

- **No relay was started while authoring this node.** Every log line, error string
  and default quoted above was read from `crates/buzz-relay/src/main.rs`,
  `config.rs`, `router.rs`, the `Justfile` and the scripts at the recorded revision —
  not observed from a running process. The *order* of the startup lines is the source
  order in `main.rs`; a reader who sees them interleaved with the many other startup
  records `main.rs` emits (Postgres, Redis, media storage, workers) is seeing normal
  behavior, and the five lines named above are the ones to look for, not the only
  ones printed.
- **The five-second pre-drain pause and the thirty-second drain timeout were read
  from source, not timed.** A stop that takes noticeably longer than that was not
  reproduced or explained here.
- **Whether `just setup` can be skipped entirely on a fresh clone** — that is, whether
  `just relay`'s own prerequisite chain covers everything a first run needs without
  the desktop/web dependency install and git hook install `dev-setup.sh` adds — was
  not tested. This guide keeps `just setup` as step 3 for a first clone rather than
  asserting it is optional.
- **The top-level `AGENTS.md` claim that `migrations/` are "auto-applied on relay
  startup"** conflicts with the opt-in `BUZZ_AUTO_MIGRATE` gate this node read in
  `main.rs`. `architecture-deployment-local-development` already records that
  discrepancy and reads it as production framing; this node states only the local
  mechanism and does not resolve the wider claim.
