---
id: development-setup
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
  - statement: "CONTRIBUTING.md's 'First-Time Setup' section gives the path as exactly four numbered steps -- clone the repository, `. ./bin/activate-hermit` labelled '(optional but recommended)', `just setup`, and `just hooks` labelled '(optional, recommended)'."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "The Justfile's `setup` recipe declares `bootstrap` as a dependency and its own body is the single line `./scripts/dev-setup.sh`, so `just setup` is `just bootstrap` followed by that script and contains no other work of its own."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile's `bootstrap` recipe is a bash recipe that prepends the repository's own `bin/` to PATH, invokes `cargo --version`, `node --version` and `pnpm --version` as three concurrent background jobs joined by `wait`, aborts with an install link if `docker` is not on PATH, copies `.env.example` to `.env` only when no `.env` file already exists, and finally runs `./scripts/ensure-local-relay-key.sh .env`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`bin/` pins exactly ten Hermit packages, one `.<tool>-<version>.pkg` marker each -- biome, cargo-deny, cmake, flutter, just, lefthook, node, pgschema, pnpm, rustup -- and `bin/cargo` is a symlink to the rustup package marker, so the three shims `bootstrap` invokes resolve to three of those ten packages and the remaining seven are downloaded lazily by whichever later command first needs them."
    entry_class: FACT
    evidence:
      - "bin/cargo"
      - "bin/node"
      - "bin/pnpm"
  - statement: "CONTRIBUTING.md describes `just bootstrap` accurately -- it 'invokes `cargo`, `node`, and `pnpm` to trigger Hermit's lazy tool download (each tool is fetched once on first invocation and cached thereafter)' -- while README.md's Quick start describes the same recipe as one that 'downloads all required tools via Hermit', which the recipe body does not do."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
      - "README.md"
      - "Justfile"
  - statement: "`bootstrap`'s `.env` creation is guarded by `if [[ ! -f .env ]]`, so the copy happens on a first run and never again; a variable added to `.env.example` afterwards is not propagated into an existing developer's `.env` by any recipe in the Justfile."
    entry_class: FACT
    evidence:
      - "Justfile"
      - ".env.example"
  - statement: "`scripts/ensure-local-relay-key.sh` sources the env file it is given, exits after `chmod 600` when `BUZZ_RELAY_PRIVATE_KEY` already has a non-empty value, and otherwise generates 32 random bytes with `node:crypto`'s `randomBytes`, rejecting and redrawing any value that is zero or not below the secp256k1 curve order, then writes the hex key back through a `mktemp` temporary file that is `chmod 600`ed before being moved over the original."
    entry_class: FACT
    evidence:
      - "scripts/ensure-local-relay-key.sh"
  - statement: "`.env.example` ships `BUZZ_RELAY_PRIVATE_KEY` commented out, and the awk substitution in `ensure-local-relay-key.sh` matches only a line beginning with optional whitespace, an optional `export`, and then the variable name -- which a `#`-prefixed line does not satisfy -- so on a freshly copied `.env` the commented line is preserved and a generated key is appended at the end of the file instead."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "scripts/ensure-local-relay-key.sh"
  - statement: "`scripts/dev-setup.sh` runs under `set -euo pipefail` and performs, in order: a `command -v docker` check and a `docker info` daemon check that each exit 1 with a remediation message; `load_env`, which sources `.env` if present, rewrites the pre-rename `sprout` default values of DATABASE_URL/PGUSER/PGPASSWORD/PGDATABASE to their `buzz` equivalents, and exports defaults for DATABASE_URL, PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE and REDIS_URL; removal of any legacy `sprout-*` dev containers; an abort if a non-Docker `redis-server` is already listening on the port REDIS_URL names; `bin/just _ensure-services`; a `pg_isready` poll of up to ten attempts two seconds apart; `bin/cargo run -p buzz-admin -- migrate`; `scripts/seed-local-community.sh`; `pnpm install` in `desktop/` and then in `web/`; a `core.hooksPath` write plus `lefthook install --force`; and a printed summary of service URLs and next commands."
    entry_class: FACT
    evidence:
      - "scripts/dev-setup.sh"
  - statement: "The Justfile's `_ensure-services` recipe reads `.State.Health.Status` for the `buzz-postgres` and `buzz-redis` containers, exits immediately when both report `healthy`, and otherwise runs `docker compose up -d` and re-polls both containers up to forty times at three-second intervals before exiting 1 with `timed out`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`scripts/seed-local-community.sh` states in its own header comment that the relay 'intentionally fails closed when the request Host header is not in `communities`', that local dev uses loopback hosts, and that bootstrap must therefore create those rows after migrations before desktop/Tauri HTTP bridge calls can succeed."
    entry_class: FACT
    evidence:
      - "scripts/seed-local-community.sh"
  - statement: "`scripts/dev-setup.sh` installs the git hooks itself -- it sets `core.hooksPath` to the absolute shared hooks directory and runs `lefthook install --force` as its penultimate step -- and root AGENTS.md states independently that pre-commit hooks 'are installed automatically by `just setup`', so `just hooks` after a successful `just setup` re-runs an install that has already happened."
    entry_class: FACT
    evidence:
      - "scripts/dev-setup.sh"
      - "AGENTS.md"
  - statement: "The Justfile's `hooks` recipe prepends the repository's `bin/` to PATH before invoking `lefthook`, and comments that this guarantees the Hermit-pinned version rather than whatever is on PATH; `scripts/dev-setup.sh` contains no PATH assignment at all, and calls `bin/just` and `bin/cargo` by absolute path while calling `lefthook` unqualified."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/dev-setup.sh"
  - statement: "Because `scripts/dev-setup.sh` runs under `set -e` and reaches its unqualified `lefthook` call only after services, migrations, seeding and both `pnpm install` runs have already completed, a shell where Hermit was never activated and no system `lefthook` exists would fail `just setup` at that final step with the expensive work already done and the hooks not installed."
    entry_class: INFERENCE
    evidence:
      - "scripts/dev-setup.sh"
      - "Justfile"
    confidence: 0.8
  - statement: "`lefthook.yml` sets `rc: bin/.lefthookrc` and defines three hooks: `pre-commit` (parallel; `rust-fmt`, `desktop-tauri-fmt`, `desktop-fix`, `web-fix`, `mobile-fmt`, each with `stage_fixed: true`), `commit-msg` (a single `signoff` command appending the DCO `Signed-off-by` trailer via `git interpret-trailers --if-exists doNothing`), and `pre-push` (parallel; `branch-skew`, `push-head-scope`, `file-size-check`, `rust-tests`, `desktop-check`, `desktop-typecheck`, `desktop-test`, `desktop-tauri-checks`, `mobile-checks`)."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "The Justfile's `reset` recipe is gated by a `[confirm(...)]` attribute and runs `./scripts/dev-reset.sh --yes`, which removes desktop development state via `scripts/reset-desktop-dev-state.sh`, runs `docker compose down -v --remove-orphans`, and then `exec`s `scripts/dev-setup.sh` -- so a reset is a teardown immediately followed by a full re-setup, and it never re-enters `just bootstrap`, leaving `.env` and its generated relay key untouched."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/dev-reset.sh"
  - statement: "The Justfile's `down` recipe is exactly `docker compose down`, with no `-v`, so it stops the dev services and preserves their volumes."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`just relay` declares `bootstrap` and `_ensure-migrations` as dependencies, `just migrate` is an alias whose only body is that same `_ensure-migrations` dependency, and `_ensure-migrations` itself depends on `_ensure-services` and then runs both the migrate and the seed steps -- so neither command runs migrations in isolation, and the first run of the relay re-performs the service, migration and seeding portions of setup even if `just setup` was never run."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "AGENTS.md's 'Getting Started' block lists `cp .env.example .env` as an explicit step before `just setup`, which `just bootstrap` would otherwise perform itself; performing it first is harmless because `bootstrap`'s copy is conditional on the file's absence."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "Justfile"
  - statement: "The merged sibling node `development/prerequisites.md` names this node's subject as an explicit exclusion from its own scope, attributing `development/setup.md` to 'issue #868' and listing '#869' among the run-a-component nodes `run-relay.md`, `run-desktop.md`, `run-mobile.md` and `run-web.md`."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/prerequisites.md"
  - statement: "Issue #869 is 'task: document development/setup.md' and issue #868 is 'task: document development/rust-style.md'; #865, #866 and #867 are run-mobile, run-relay and run-web respectively, so the sibling node's issue-to-document pairing quoted above is inverted for #868/#869 and lists no issue for run-desktop."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issues #865, #866, #867, #868 and #869 (titles read via `gh issue view <n> --json title`)"
  - statement: "The `corpus-validate` recipe in the Justfile is exactly `python3 launchpad/project-intelligence/corpus/validate.py`, and its comment states that citations naming nothing openable print as UNVERIFIED without failing the run."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The relationship targets declared in this node's front matter -- corpus-template-procedure, development-prerequisites, development-hermit and corpus-development-build -- were each resolved by reading the `id:` line of the corresponding file as it exists on origin/launchpad, not as it exists in the authoring worktree."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/build.md"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: development-prerequisites
  - type: references
    target: development-hermit
  - type: references
    target: corpus-development-build
---

# Set up a Buzz development environment: how-to

Take a fresh clone of this repository to a state where the relay, desktop app and
tests can be run: toolchain resolved, `.env` created with a local relay key, Docker
services healthy, database migrated and seeded, JavaScript dependencies installed,
and git hooks in place. Perform this once per clone. Every later day's work starts
from `. ./bin/activate-hermit` alone.

This node is the connective procedure between three merged siblings and deliberately
does not restate them: `development-prerequisites` says *what must already be
installed*, `development-hermit` says *how the pinned toolchain works*, and
`corpus-development-build` says *how to compile* once setup is done. See *Boundary*.

## Before you start

- **Docker installed and its daemon running.** Two separate checks enforce this:
  `just bootstrap` aborts if `docker` is not on `PATH`, and `scripts/dev-setup.sh`
  additionally runs `docker info` and aborts if the daemon is not up.
- **No non-Docker Redis holding the port.** `scripts/dev-setup.sh` aborts if `lsof`
  finds a `redis-server` process listening on the port `REDIS_URL` names. The check
  is skipped entirely when `lsof` is not installed, or when a container named
  `buzz-redis` is already running.
- **The version floors and platform packages** in `development-prerequisites` — in
  particular the Linux system libraries the desktop Tauri build needs, which nothing
  in this procedure installs for you.
- **A decision about Hermit.** Activating it is the supported path and is what makes
  the rest of this procedure use pinned versions; `development-hermit` covers the
  mechanism. Step 5 below is where skipping it actually bites.

## Set up the environment

1. **Clone the repository and change into it.** `CONTRIBUTING.md` and `README.md`
   both give `https://github.com/block/buzz.git`; a cohort contributor clones the
   launchpad-26 fork instead, which changes only the remote URL and nothing in the
   steps below.

2. **Activate the pinned toolchain**, from the repository root, once per shell
   session:

   ```bash
   . ./bin/activate-hermit
   ```

   `CONTRIBUTING.md` labels this "(optional but recommended)". It is what puts the
   repository's own `bin/` ahead of your system tools; without it, step 5's final
   sub-step is the one that fails.

3. **Run setup.**

   ```bash
   just setup
   ```

   This is the whole procedure in one command. `setup` declares `bootstrap` as a
   dependency and its own body is the single line `./scripts/dev-setup.sh`, so
   steps 4 and 5 below are what that one command actually does. Read them before
   running it if you want to know what is about to change on your machine; skip to
   step 6 if you do not.

4. **What `just bootstrap` does** (safe to re-run on its own at any time):

   1. Prepends the repository's `bin/` to `PATH` for the duration of the recipe.
   2. Invokes `cargo --version`, `node --version` and `pnpm --version` as three
      concurrent background jobs and waits for all three. Each invocation triggers
      Hermit's lazy download of that package if it is not already cached. **These
      three are the only packages `bootstrap` pre-downloads.** `bin/` pins ten
      packages — biome, cargo-deny, cmake, flutter, just, lefthook, node, pgschema,
      pnpm and rustup — and `bin/cargo` resolves to the rustup package, so the other
      seven are fetched later, by whichever command first needs them.
   3. Aborts with an install link if `docker` is not on `PATH`.
   4. Copies `.env.example` to `.env` **only if no `.env` exists**, and prints
      "Created .env from .env.example — review it before running just dev."
   5. Runs `./scripts/ensure-local-relay-key.sh .env`, which leaves an existing
      non-empty `BUZZ_RELAY_PRIVATE_KEY` alone (only tightening the file to mode
      `600`), and otherwise generates one: 32 bytes from `node:crypto`'s
      `randomBytes`, redrawn if the value is zero or not below the secp256k1 curve
      order, written back through a mode-`600` temporary file that replaces the
      original. Because `.env.example` ships that variable commented out, and the
      script's substitution pattern does not match a `#`-prefixed line, a fresh
      `.env` keeps the commented line and gains a generated key appended at the end.

5. **What `scripts/dev-setup.sh` then does**, in order, under `set -euo pipefail`:

   1. Checks `docker` is installed and that `docker info` succeeds.
   2. Sources `.env`, rewrites the four pre-rename `sprout` default values
      (`DATABASE_URL`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`) to their `buzz`
      equivalents for this run only, and exports defaults for those plus `PGHOST`,
      `PGPORT` and `REDIS_URL`. Custom values are left untouched.
   3. Stops and removes any legacy `sprout-*` dev containers, preserving their
      volumes, so the `buzz-*` containers can bind the standard ports.
   4. Aborts if a non-Docker Redis is holding the port, per *Before you start*.
   5. Runs `bin/just _ensure-services`, which returns immediately if `buzz-postgres`
      and `buzz-redis` both report Docker health status `healthy`, and otherwise runs
      `docker compose up -d` and polls both up to forty times at three-second
      intervals before giving up.
   6. Polls `pg_isready` inside the `buzz-postgres` container up to ten times at
      two-second intervals, then runs `bin/cargo run -p buzz-admin -- migrate`.
   7. Runs `scripts/seed-local-community.sh`. This is not optional dressing: the
      relay fails closed when a request's `Host` header names no row in
      `communities`, and local development uses loopback hosts, so without these
      rows the desktop app's HTTP bridge calls cannot succeed.
   8. Runs `pnpm install` in `desktop/` and then in `web/`. Each is guarded by
      `command -v pnpm` and merely warns and skips if pnpm is absent.
   9. Sets `core.hooksPath` to the absolute shared hooks directory — absolute so that
      linked worktrees inherit the same hooks — and runs `lefthook install --force`.
  10. Prints the service URLs (Postgres, Redis, Adminer on `:8082`, Keycloak on
      `:8180`) and the next commands.

   **This step is where an unactivated shell fails.** `scripts/dev-setup.sh` sets no
   `PATH` of its own. It calls `bin/just` and `bin/cargo` by absolute path, but calls
   `lefthook` unqualified — so on a shell without Hermit activated and with no system
   `lefthook`, the script aborts at sub-step 9, after every expensive sub-step above
   has already succeeded and with the hooks not installed. Re-running `just hooks`
   from an activated shell is the repair; it is the same install, with `bin/` put on
   `PATH` first.

6. **Install the git hooks** — only if step 5 did not already do it:

   ```bash
   just hooks
   ```

   `CONTRIBUTING.md` lists this as step 4 and labels it "(optional, recommended)",
   and root `AGENTS.md` states that hooks are "installed automatically by
   `just setup`". Both are consistent with the code: `scripts/dev-setup.sh` performs
   the install itself, so after a successful `just setup` this command is a re-run,
   not a missing step. It is worth running anyway when step 5 aborted, or when the
   `lefthook` that ran was not the pinned one. It is **not** needed after adding a
   linked worktree: both install paths write an absolute `core.hooksPath` pointing at
   the shared hooks directory precisely so linked worktrees inherit the same hooks.

   What it installs, per `lefthook.yml`: a **pre-commit** hook (parallel formatting
   and lint-fix lanes for Rust, Tauri Rust, desktop, web and mobile, each restaging
   what it fixed), a **commit-msg** hook (appends the DCO `Signed-off-by` trailer
   idempotently), and a **pre-push** hook (parallel: branch-skew, push-head-scope,
   file-size-check, Rust tests, desktop check/typecheck/test, Tauri checks, mobile
   checks).

## Verify the setup succeeded

Run these from the repository root; each answers a different sub-step above.

1. **Services are up and healthy.**

   ```bash
   just ps        # docker compose ps
   ```

   `buzz-postgres` and `buzz-redis` are the two `_ensure-services` gates on, so both
   must be present and healthy.

2. **`.env` exists and carries a relay key.**

   ```bash
   test -f .env && grep -c '^BUZZ_RELAY_PRIVATE_KEY=' .env
   ```

   Expect `1`. A `0` means `ensure-local-relay-key.sh` did not run or did not write
   — re-run `just bootstrap`, which is safe to repeat.

3. **Hooks are wired to the shared hooks directory.**

   ```bash
   git config --local core.hooksPath
   ```

   Expect an absolute path ending in `/hooks`. A relative path, or no output, means
   sub-step 9 did not complete — see step 6.

4. **The workspace compiles.** `README.md`'s Quick start pairs setup with
   `just build` for exactly this reason. That command, its scope and its known
   failure modes are `corpus-development-build`'s subject, not this node's.

## Roll back or clean up

- **Stop the services, keep the data.**

  ```bash
  just down      # docker compose down, no -v
  ```

- **Wipe development state and rebuild it.**

  ```bash
  just reset
  ```

  Gated behind a `just` confirmation prompt, then runs `scripts/dev-reset.sh --yes`,
  which removes desktop development state, runs `docker compose down -v
  --remove-orphans`, and `exec`s `scripts/dev-setup.sh` — so a reset is a teardown
  immediately followed by a full re-run of step 5. It does **not** re-enter
  `just bootstrap`, so your `.env` and its generated relay key survive a reset. The
  installed (non-development) Buzz app's state is preserved.

- **Undo the hooks configuration only.** `git config --local --unset
  core.hooksPath` removes the one setting `scripts/dev-setup.sh` and `just hooks`
  both write, without touching anything else setup created.

- **There is no partial-undo for the database.** `just reset` is all-or-nothing.
  `just migrate` is the narrower re-run, but it is an alias for
  `_ensure-migrations`, which also ensures the services are up and re-runs the
  community seeding — it is not migrations in isolation.

## See also

- `development-prerequisites` — what must be installed before step 1, including the
  Linux desktop-build system libraries this procedure does not install.
- `development-hermit` — how the pinned toolchain resolves, and what activation in
  step 2 actually changes.
- `corpus-development-build` — compiling the workspace, referenced from
  *Verify the setup succeeded* step 4.
- `debugging` — what to do when the relay misbehaves after setup.
- `CONTRIBUTING.md` § First-Time Setup, `README.md` § Quick start, and root
  `AGENTS.md` § Getting Started — the three prose entry points this node is derived
  from. Where they disagree with the recipe bodies, the recipe bodies win; the one
  live disagreement is recorded in *Scope and omissions*.

## Boundary

This node does not describe:

- **Facts to look up rather than actions to perform** — the version floor for each
  tool, which Hermit package pins which version, the full flag surface of `just`,
  `cargo`, `pnpm` or `docker compose`. `development-prerequisites` and
  `development-hermit` own the first two; no reference node exists for the third.
- **Acquiring the underlying skill from scratch** — using Docker, reading a
  `Justfile`, or working in a Rust plus pnpm monorepo. That is a tutorial, a form
  the corpus has no template for.
- **Why the environment is shaped this way** — why the relay fails closed on an
  unknown `Host`, why hooks dispatch from the shared `.git/hooks` directory, why
  `bin/` pins the versions it does. This node states those behaviours where a step
  depends on them and explains no further.
- **Running anything after setup** — the relay, desktop, web or mobile app. Those
  are separate tasks and separate nodes.
- **Compiling the workspace** — `corpus-development-build`.
- **The quality gates** — `just ci`, `just check`, `just test`, `just test-unit`.
  Setup installs the hooks that invoke some of them; what they check is not this
  node's subject.
- **Setting up anything other than a local development environment** — CI runners,
  staging or production deployment, or the four sibling repositories in the Buzz
  ecosystem.

## Relationships

Declared, each target confirmed by reading its `id:` line as the file exists on
`origin/launchpad` rather than in the authoring worktree:

- `implements: corpus-template-procedure` — this node's body follows that template's
  required sections; the template names "a template instance of a standard" as
  `implements`' own worked example.
- `references: development-prerequisites` — background the reader is assumed to
  already have before step 1.
- `references: development-hermit` — the mechanism step 2 invokes and step 5's
  failure mode depends on.
- `references: corpus-development-build` — the completeness this node defers to in
  *Verify the setup succeeded* step 4.

Not declared: `debugging` (id `debugging`) is present on `origin/launchpad` and is
named in *See also*, but this procedure's steps do not depend on it — it is where a
reader goes after setup succeeds and something else goes wrong, which is a pointer
rather than a dependency.

## Scope and omissions

**This node covers** the first-run path from a fresh clone to a working local
development environment: the four steps `CONTRIBUTING.md` prescribes, what
`just bootstrap` and `scripts/dev-setup.sh` each actually do and in what order, how
`.env` and the local relay key are created, what `just hooks` installs and why it is
usually redundant, how to verify each part of the result, and how to tear the
environment down or reset it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Required tools, version floors, and Linux desktop-build system libraries | `development-prerequisites` |
| How Hermit pins and resolves the toolchain | `development-hermit` |
| Compiling the workspace and its known build failures | `corpus-development-build` |
| Diagnosing a misbehaving local relay | `debugging` |
| Running the relay, desktop, web or mobile app after setup | separate tasks, no node authored at this revision |
| Rust code style and conventions | a separate task, no node authored at this revision |
| CI, staging and production environment setup | outside the development surface entirely |

**A documentation disagreement, recorded rather than resolved.** `README.md`'s Quick
start says `just setup` "downloads all required tools via Hermit". The `bootstrap`
recipe invokes exactly three shims — `cargo`, `node`, `pnpm` — of the ten packages
`bin/` pins, so seven are not pre-downloaded. `CONTRIBUTING.md` describes the same
recipe correctly, as invoking those three "to trigger Hermit's lazy tool download".
This node states the recipe body's behaviour, per the corpus rule that executable
evidence outranks documentation for how the system currently behaves. The
disagreement is between two upstream documents; nothing here changes either.

**A defect in a sibling node, recorded rather than repaired.**
`development/prerequisites.md` attributes this node's subject to "issue #868" and
lists "#869" among the run-a-component nodes. The titles of those issues are the
reverse: #869 is `task: document development/setup.md` and #868 is
`task: document development/rust-style.md`. The sibling also lists no issue for
`run-desktop.md`. Correcting another node is outside this task's scope; it is stated
here so a reader does not follow the wrong pointer.

**Expected but not verified when this node was written:**

- **The procedure was not executed end to end.** Every step above is read from the
  recipe and script bodies at the recorded revision, not from a run. Running it
  requires a working Docker daemon and a full toolchain download, and the result
  would be evidence about one particular machine rather than about the repository.
  The procedure template's own preference is for a step to cite having been run, so
  this is a real shortfall in this node's evidence, not a design choice: the first
  contributor to follow these steps on a clean clone is what will actually test
  them. In particular, the timing constants in step 5 (forty three-second polls for
  service health, ten two-second polls for Postgres) are stated from the code and
  were not observed to be sufficient in practice.
- **The unactivated-shell failure in step 5 is reasoned, not reproduced.** It is
  recorded as an INFERENCE at 0.8 confidence. What is verified is that
  `scripts/dev-setup.sh` sets no `PATH`, calls `bin/just` and `bin/cargo` absolutely,
  calls `lefthook` unqualified, and runs under `set -e`. What was not tested is the
  behaviour on a machine that has a system `lefthook` from another source, where the
  script would succeed using an unpinned version instead of failing.
- **`scripts/seed-local-community.sh`'s body was read only as far as its header
  comment and its environment defaults.** The SQL it generates and applies was not
  traced, so this node states why the seeding step exists and not what rows it
  produces.
- **Windows was not considered separately.** `development-prerequisites` notes a
  Git Bash requirement; whether every command in this procedure behaves identically
  there was not established.
