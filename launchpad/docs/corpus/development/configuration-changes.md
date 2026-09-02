---
id: development-configuration-changes
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "`.env.example` is the repository's configuration template: its header block instructs `cp .env.example .env`, states that all defaults work with `docker compose up` out of the box, and lists the default service ports for Postgres, Redis, Typesense and Adminer."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "`just bootstrap` copies `.env.example` to `.env` only when no `.env` already exists -- the copy is guarded by `if [[ ! -f .env ]]` -- and then unconditionally runs `./scripts/ensure-local-relay-key.sh .env`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Because that copy is guarded on the absence of `.env`, adding a variable to `.env.example` never propagates into an existing developer's or agent's `.env`; only a contributor who has no `.env` yet receives the new line."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - ".env.example"
    confidence: 0.9
  - statement: "`just setup` depends on `bootstrap` and then runs `./scripts/dev-setup.sh`, whose `load_env` function sources `.env` under `set -o allexport` and rewrites only the legacy `sprout` default values for `DATABASE_URL`, `PGUSER`, `PGPASSWORD` and `PGDATABASE`, leaving custom values untouched."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/dev-setup.sh"
  - statement: "`just relay` depends on `bootstrap`, sources `.env` under `set -o allexport`, and then runs `cargo run -p buzz-relay`, so the relay process inherits every assignment in `.env` as a real environment variable."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`scripts/ensure-local-relay-key.sh` preserves an existing non-empty `BUZZ_RELAY_PRIVATE_KEY` and exits early after `chmod 600`; only when the value is absent or empty does it generate a fresh 32-byte scalar inside the secp256k1 curve order and rewrite the file in place with mode 600."
    entry_class: FACT
    evidence:
      - "scripts/ensure-local-relay-key.sh"
  - statement: "Every relay environment variable is read in `Config::from_env` in `crates/buzz-relay/src/config.rs`, whose module doc line is 'Relay configuration from environment variables.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`crates/buzz-relay/src/main.rs` calls `Config::from_env()` and maps any `ConfigError` into a startup abort, logging `error!(\"Invalid configuration: {e}\")` and returning `anyhow::anyhow!(\"Configuration error: {e}\")` before any listener is bound."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "`ConfigError` has exactly two variants, `InvalidBindAddr` for an unparseable `BUZZ_BIND_ADDR` and `InvalidValue` for any other rejected value."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`config.rs` provides typed parse helpers rather than ad-hoc parsing: `parse_bool` accepts `true`/`1`/`on` and `false`/`0`/`off`/empty case-insensitively after trimming and rejects anything else, `positive_u64_from_env` reads an integer with a coded default, and `ensure_git_path` creates the named directory and turns a creation failure into `InvalidValue`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "A variable that has stopped being read is retired by adding it to `INERT_MEDIA_READ_AUTH_VARS` and reporting it through `inert_env_vars`, so startup warns the operator rather than silently ignoring it; the doc comment states the deliberate reason an operator who pinned the old flag to `false` must be told it is inert rather than left believing media reads are still open."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`inert_env_vars` takes its `lookup` as an injected closure rather than calling `std::env::var`, and its doc comment gives the reason: process env is global mutable state, so a test that set real variables would race every other test in the binary."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "Config tests that must mutate real process environment serialize on a `static ENV_MUTEX: std::sync::Mutex<()>`, whose comment records the concrete flake it prevents -- parallel mutation let `defaults_are_valid` observe the invalid value set by `invalid_bind_addr_returns_error`; tests that do not need real env instead use the `env_of` helper, which builds a lookup closure over a fixed slice of pairs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`.env.example` documents removed and inert settings in prose rather than deleting the lines silently: it records that `BUZZ_ADMIN_TOKEN` is ignored with a startup warning and should be removed from the environment, and that `BUZZ_REQUIRE_MEDIA_GET_AUTH` and `BUZZ_REQUIRE_MEDIA_READ_AUTH` are no longer read so setting either changes nothing."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "In `.gitleaks.toml` exactly one rule -- `buzz-s3-minio-key` -- carries a per-rule `[rules.allowlist]` exempting `paths = ['''.*\\.env\\.example$''']`, justified by a comment that env example files are by convention entirely placeholder values; the only other per-rule allowlist, on `postgres-url-with-password`, exempts by regex (localhost/127.0.0.1 URLs) and not by path, and the file-level `[allowlist]` exempts only `launchpad/scripts/security_audit_fixtures/secrets/.*` and `Cargo.lock`, so the `.env.example` exemption is narrow rather than blanket."
    entry_class: FACT
    evidence:
      - ".gitleaks.toml"
  - statement: "The fork's authorized secret-scanning arrangement, per accepted ADR-0006's Decision section, is gitleaks with detection rules and allowlist living together in a single root `.gitleaks.toml`, where the allowlist is hand-maintained TOML `[allowlist]` and per-rule `allowlist` blocks each carrying a `#` comment stating why the entry is safe; gitleaks' auto-generated `--baseline-path` snapshot is explicitly rejected as a footgun that accepts a real finding without a human typing a reason."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0006-secret-scanning-engine-and-allowlist-location.md"
  - statement: "Deployment-time host configuration is a separately decided surface: accepted ADR-0013's Decision section names Ansible as the configuration-management tool, Ubuntu 24.04 LTS as the supported starting state, and containers via the existing `deploy/compose/` bundle as the runtime shape -- which is why this node's boundary excludes it rather than merely omitting it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0013-config-management-ubuntu-baseline-runtime-shape.md"
  - statement: "The `dead-token-guard` job in `.github/workflows/ci.yml` greps `.env.example` alongside `desktop/src/`, `desktop/tests/`, `mobile/test/` and `mobile/lib/` for the dead API token patterns `TokenScope|MintTokenResponse|hasApiToken|spr_tok_` and fails the build on a match."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "`CONTRIBUTING.md`'s 'What a Good PR Looks Like' checklist requires under item 3 that public APIs, new event kinds, new MCP tools and new config variables are documented, naming `README.md`, `AGENTS.md` or `VISION.md` as the places to update."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "No automated check compares `.env.example` against `Config::from_env`, so a variable added to one and not the other produces no failure in any gate; keeping the two in step is review-enforced."
    entry_class: INFERENCE
    evidence:
      - "grep_recursive(pattern='env.example', paths=['crates/', 'scripts/'], revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> crates/buzz-relay/src/config.rs (two doc comments), scripts/dev-setup.sh, scripts/test-ensure-local-relay-key.sh -- no comparison or parity assertion among them"
      - "crates/buzz-relay/src/config.rs"
      - "CONTRIBUTING.md"
    confidence: 0.8
  - statement: "Desktop preview feature flags are declared in the repository-root `preview-features.json`, which `desktop/vite.config.ts` aliases as `@features-manifest`; `desktop/src/shared/features/manifest.ts` runtime-validates that JSON with a zod schema requiring a non-negative integer `version` and a `features` array of `{id, name, description, defaultEnabled?, platforms?}`, and falls back to an empty manifest with a console warning if the parse fails, so gated UI stays hidden rather than leaking."
    entry_class: FACT
    evidence:
      - "preview-features.json"
      - "desktop/vite.config.ts"
      - "desktop/src/shared/features/manifest.ts"
  - statement: "`desktop/src/shared/features/resolveEnabled.ts` resolves a preview feature as `overrides[featureId] ?? defaultEnabled`, with `defaultEnabled` itself defaulting to `false` -- an explicit user override wins, otherwise the manifest default applies, otherwise the feature is off."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/resolveEnabled.ts"
  - statement: "Desktop also reads build-time Vite variables through `import.meta.env`, including `VITE_BUZZ_FORCE_FRESH_ONBOARDING`, which `desktop/src/features/onboarding/devFreshOnboarding.ts` honours only when `import.meta.env?.DEV === true`, and which `.env.example` documents under a 'Desktop development' heading as DEV-only."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/devFreshOnboarding.ts"
      - ".env.example"
  - statement: "Mobile configuration defaults are compile-time constants: the `Env` class in `mobile/lib/shared/relay/relay_provider.dart` declares `relayUrl` and `pushGatewayUrl` with `String.fromEnvironment`, defaulting to `http://localhost:3000` and `https://push.buzz.xyz`, and `RelayConfigNotifier.build` uses `Env.relayUrl` only as a dev-mode fallback when no active community is selected."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart"
  - statement: "`just check` runs `fmt-check clippy desktop-check desktop-tauri-fmt-check desktop-tauri-clippy web-check mobile-check security-review-check file-size-check`, and `just ci` runs `check test-unit desktop-test desktop-build desktop-tauri-check desktop-tauri-test web-build mobile-test`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The corpus already carries a nine-node configuration shelf under `launchpad/docs/corpus/layers/configuration/` -- agent-configuration, defaults, desktop-configuration, environment-configuration, feature-flags, mobile-configuration, relay-configuration, secrets and validation -- which catalogues the configuration surface itself."
    entry_class: FACT
    evidence:
      - "ls(launchpad/docs/corpus/layers/configuration/) -> agent-configuration.md, defaults.md, desktop-configuration.md, environment-configuration.md, feature-flags.md, mobile-configuration.md, relay-configuration.md, secrets.md, validation.md"
      - "launchpad/docs/corpus/layers/configuration/environment-configuration.md"
      - "launchpad/docs/corpus/layers/configuration/relay-configuration.md"
      - "launchpad/docs/corpus/layers/configuration/validation.md"
  - statement: "At the recorded revision `launchpad/docs/corpus/development/` contains build.md, debugging.md, hermit.md and prerequisites.md, and every relationship target declared by this node resolves to a file present on `origin/launchpad`."
    entry_class: FACT
    evidence:
      - "ls(launchpad/docs/corpus/development/) -> build.md, debugging.md, hermit.md, prerequisites.md"
      - "git_grep(ref='origin/launchpad', pattern='^id: <target>$', path='launchpad/docs/corpus') -> development-prerequisites->development/prerequisites.md; layers-configuration-environment-configuration->layers/configuration/environment-configuration.md; layers-configuration-relay-configuration->layers/configuration/relay-configuration.md; layers-configuration-validation->layers/configuration/validation.md; corpus-template-procedure->templates/procedure.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/debugging.md"
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "`launchpad/docs/corpus/templates/procedure.md` states that a node built from it should declare `implements` targeting `corpus-template-procedure`, citing `relationships.schema.json`'s own worked example of 'a template instance of a standard'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "Issue #848's definition of done requires that the node state goal, prerequisites and allowed environment/scope, provide ordered executable project-specific steps, define success verification and rollback/cleanup where relevant, link authoritative commands and config rather than giving generic advice, and carry an explicit scope-and-omissions section."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#848 definition of done"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: layers-configuration-environment-configuration
  - type: references
    target: layers-configuration-relay-configuration
  - type: references
    target: layers-configuration-validation
  - type: references
    target: development-prerequisites
---

# Changing configuration in Buzz

How a contributor adds, changes or retires a configuration value in this
repository, across the three surfaces that hold one: the relay's environment
variables, the desktop preview-feature manifest, and the mobile compile-time
defaults. Perform this when a change needs a value that varies between
deployments, or when an existing value's name, default, type or meaning changes.

This is a how-to. It does not catalogue the configuration surface — the
`layers/configuration/` shelf already does that, and each task below links to
the node that owns the catalogue for its surface.

## Before you start

- **A working development environment.** `just setup` has completed at least
  once, so a `.env` exists and the Hermit toolchain is resolved. The
  prerequisites and Hermit activation are owned by the sibling nodes
  `development-prerequisites` and `development-hermit`; this node assumes them.
- **Hermit activated** in the shell you will run gates from:
  `. ./bin/activate-hermit`.
- **Scope.** This procedure covers configuration read by code in *this*
  repository. It does not cover deployment-time configuration of a running
  relay — Helm values, Terraform, `deploy/compose/` — which belongs to the
  operations surface, not to a development change. That surface is separately
  decided: ADR-0013 (accepted) names Ansible, Ubuntu 24.04 LTS and the existing
  `deploy/compose/` bundle as the authorized shape for host configuration
  management.
- **A secrets rule that has no exceptions.** Never put a live credential in
  `.env.example` or in any tracked file. One gitleaks rule — `buzz-s3-minio-key`
  — carries a per-rule allowlist exempting paths matching `.*\.env\.example$`,
  on the stated convention that those files hold only placeholders. That
  exemption is narrow, not blanket: other rules still scan the file. But it does
  mean a real S3 access or secret key committed there would *not* be reported.
  Treat the allowlist as a statement about what the file is for, not as a safe
  place to put a key. If a change genuinely needs a new allowlist entry, ADR-0006
  (accepted) is the authority for how: a hand-written TOML block carrying a `#`
  comment stating why the entry is safe, never a regenerated baseline snapshot.

## Task 1 — add or change a relay environment variable

The relay reads every environment variable in one place: `Config::from_env` in
`crates/buzz-relay/src/config.rs`.

1. **Decide the variable is genuinely deploy-varying.** If the value is the same
   in every deployment, it is a constant, not configuration. `config.rs` already
   holds coded constants such as `DEFAULT_MAX_FRAME_BYTES` for that case.
2. **Read the value in `Config::from_env`** using an existing typed helper
   rather than parsing inline:
   - a boolean → `parse_bool(name, default)`, which accepts `true`/`1`/`on` and
     `false`/`0`/`off`/empty case-insensitively after trimming, and returns
     `ConfigError::InvalidValue` for anything else;
   - a positive integer → `positive_u64_from_env(name, default)`;
   - a filesystem path the relay must own → `ensure_git_path(setting, raw)`,
     which creates the directory and converts a creation failure into
     `InvalidValue`.

   Add a new helper only when none of these fits, and give it the same shape:
   return `Result<T, ConfigError>`, never panic, never `unwrap()`.
3. **Fail closed on a bad value.** Return `ConfigError::InvalidValue` with a
   message that names the variable and says what a valid value looks like.
   `main.rs` maps any `ConfigError` to a startup abort — it logs
   `Invalid configuration: {e}` and returns `Configuration error: {e}` before
   any listener is bound — so a rejected value stops the process rather than
   letting it serve with a half-applied setting. A setting that silently falls
   back to a permissive default on a typo is the failure mode this step exists
   to prevent.
4. **Add the variable to `.env.example`**, in the section that matches its
   subsystem, with a comment giving its default and its effect. Comment the line
   out when the coded default is the right local-development value; leave it
   live only when a local run genuinely needs a non-default. Nothing checks this
   step for you — see *Known gap* below.
5. **Write a test in `config.rs`'s `mod tests`.** Prefer a pure test that injects
   a lookup closure over a fixed set of pairs, using the existing `env_of`
   helper, exactly as the `inert_env_vars` tests do. Only if the test genuinely
   needs real process environment, take the `ENV_MUTEX` guard first — its
   comment records the concrete flake that omitting it caused, where parallel
   mutation let `defaults_are_valid` observe the invalid value set by
   `invalid_bind_addr_returns_error`.
6. **Update the documentation the PR checklist asks for.** `CONTRIBUTING.md`'s
   "What a Good PR Looks Like" item 3 requires new config variables to be
   documented, naming `README.md`, `AGENTS.md` or `VISION.md`. If the variable
   changes the corpus's picture of the configuration surface, the node to update
   is `layers-configuration-relay-configuration` or
   `layers-configuration-environment-configuration` — not this one.

### 1a — retiring a variable that has stopped being read

Deleting the line is the wrong move: an operator who still sets it keeps
believing it does something.

1. **Leave the name discoverable.** Add it to the inert-variable list —
   `INERT_MEDIA_READ_AUTH_VARS` is the worked precedent — so `inert_env_vars`
   reports it and startup warns.
2. **Keep the injected-lookup shape.** `inert_env_vars` takes its `lookup` as a
   closure rather than calling `std::env::var`, because process env is global
   mutable state and a test that set real variables would race every other test
   in the binary. Do not "simplify" that back to a direct read.
3. **Say so in `.env.example` rather than deleting the line.** The file already
   does this twice: it records that `BUZZ_ADMIN_TOKEN` is ignored with a startup
   warning and should be removed from the environment, and that
   `BUZZ_REQUIRE_MEDIA_GET_AUTH` and `BUZZ_REQUIRE_MEDIA_READ_AUTH` are no
   longer read so setting either changes nothing.

### 1b — the variable does not reach an existing `.env`

`just bootstrap` copies `.env.example` to `.env` **only when `.env` does not
exist** — the copy sits behind `if [[ ! -f .env ]]`. A contributor or agent who
already has a `.env` will never receive your new line, and `just relay` sources
that stale `.env` under `set -o allexport` before running the relay. Say so in
the pull request, and give reviewers the one-line diff they need to apply by
hand. Do not attempt to have `bootstrap` rewrite an existing `.env`: the only
in-place rewrites in the repository are deliberately narrow —
`ensure-local-relay-key.sh` touches `BUZZ_RELAY_PRIVATE_KEY` only when it is
absent or empty, and `dev-setup.sh` rewrites only the legacy `sprout` default
values, leaving custom values untouched.

## Task 2 — add or change a desktop preview feature flag

A desktop feature that ships behind a flag is declared in data, not in code.

1. **Add an entry to the repository-root `preview-features.json`**, matching the
   shape the existing entries use: `id`, `name`, `description`, and optionally
   `defaultEnabled` and `platforms`.
2. **Keep it schema-valid.** `desktop/src/shared/features/manifest.ts`
   runtime-validates the file with a zod schema requiring a non-negative integer
   `version` and a `features` array of `{id, name, description, defaultEnabled?,
   platforms?}`. On a parse failure the app does not crash — it logs a console
   warning and falls back to an empty manifest, which means **every** gated
   feature disappears, not just the malformed one. A typo therefore shows up as
   missing UI, not as an error.
3. **Expect it to default off.** `resolveEnabled` returns
   `overrides[featureId] ?? defaultEnabled`, with `defaultEnabled` itself
   defaulting to `false`. Omitting `defaultEnabled` is the correct choice for a
   preview feature; setting it to `true` makes the feature on-by-default for
   everyone who has not overridden it.
4. **Do not add a build-time Vite variable for a user-facing toggle.** The
   `import.meta.env` variables are for development-only behaviour — for example
   `VITE_BUZZ_FORCE_FRESH_ONBOARDING`, which `devFreshOnboarding.ts` honours only
   when `import.meta.env?.DEV === true` and which `.env.example` documents as
   DEV-only. A flag a user is meant to toggle belongs in the manifest.

The catalogue of what flags exist is owned by `layers-configuration-feature-flags`
and `layers-configuration-desktop-configuration`.

## Task 3 — add or change a mobile compile-time default

Mobile configuration is baked at build time, not read at runtime.

1. **Add a constant to the `Env` class** in
   `mobile/lib/shared/relay/relay_provider.dart`, using `String.fromEnvironment`
   with an explicit `defaultValue`, matching `relayUrl` and `pushGatewayUrl`.
2. **Understand the precedence before choosing the default.**
   `RelayConfigNotifier.build` watches the active community and uses it when one
   is selected; `Env.relayUrl` is reached only as the dev-mode fallback when
   there is none. A default here changes developer experience, not the behaviour
   of an app with a community configured.
3. **Pass it at build time** with `--dart-define`, since `String.fromEnvironment`
   is a compile-time constant — changing it requires a rebuild, not a restart.

The catalogue for this surface is `layers-configuration-mobile-configuration`,
and the precedence mechanism itself is documented in
`layers-configuration-defaults`.

## Verify

Run these in order, from the repository root with Hermit activated.

1. **Unit-level, fastest signal.**
   `cargo test -p buzz-relay config` for a relay variable;
   `cd desktop && pnpm test` for a manifest change;
   `just mobile-test` for a mobile default.
2. **Prove the relay actually rejects a bad value.** Set the variable to
   something invalid and start the relay:
   `BUZZ_BIND_ADDR=not-an-address just relay`. A correctly wired setting aborts
   at startup with `Invalid configuration:` in the log. If the relay starts, the
   value is not being validated and step 3 of Task 1 is incomplete.
3. **Prove a good value is applied.** Start the relay normally and read the
   `Config loaded` line `main.rs` emits after `Config::from_env` succeeds; it
   logs `bind_addr`, `relay_url`, `health_port`, `metrics_port`,
   `max_frame_bytes`, `audit_enabled` and `push_enabled`. Extend that log line
   only for a non-secret value — it is a structured field, not a debug dump.
4. **Full local gate.** `just ci`. It runs `just check` — which includes
   `file-size-check` — plus the unit tests and the desktop, Tauri, web and mobile
   suites and builds.
5. **Confirm no secret was staged.** Read your own diff. Gitleaks' coverage of
   `.env.example` has a hole — the `buzz-s3-minio-key` rule allowlists that
   filename shape — so a real S3 key placed there is not reported by that rule.

## Roll back and clean up

- **A change that is only in `.env.example` and code** is reverted by reverting
  the commit; nothing persists outside the repository.
- **Your own `.env` is not reverted with it.** It is untracked and
  developer-local. If you added a line to `.env` by hand while testing, remove
  it by hand. Never revert `.env` by re-copying `.env.example` over it: that
  discards `BUZZ_RELAY_PRIVATE_KEY`, and losing that value is not cosmetic —
  `ensure-local-relay-key.sh` will generate a *new* key on the next
  `just bootstrap`, giving the relay a different identity from the one your
  local data was signed against.
- **To restore a relay key you did not save**, there is no recovery path; the
  script only preserves a key that is still present. Treat the value as
  something to back up before editing `.env`, which is also why
  `ensure-local-relay-key.sh` leaves the file at mode 600.
- **A directory created by `ensure_git_path`** — for example the default
  `./repos` — is not removed when you revert the setting that created it.
  Delete it explicitly if the change is abandoned.
- **A retired variable is not rolled back by deletion.** Per Task 1a, put it on
  the inert list so operators are warned, rather than removing the warning
  together with the code.

## See also

Prose links, so that this node does not depend on nodes it has not confirmed:

- `launchpad/docs/corpus/layers/configuration/relay-configuration.md` — the
  catalogue of the relay's runtime configuration surface.
- `launchpad/docs/corpus/layers/configuration/environment-configuration.md` —
  the environment-variable surface across Buzz.
- `launchpad/docs/corpus/layers/configuration/validation.md` — the distinct
  validation mechanisms this procedure tells you to reuse.
- `launchpad/docs/corpus/layers/configuration/secrets.md` — the secret-shaped
  subset, and its handling rules.
- `launchpad/docs/corpus/layers/configuration/defaults.md` — how a default is
  decided and what takes precedence over it, across all four mechanisms.
- `launchpad/docs/corpus/development/prerequisites.md` and
  `launchpad/docs/corpus/development/hermit.md` — the environment this procedure
  assumes.
- `CONTRIBUTING.md` — the pull-request checklist item that requires new config
  variables to be documented.
- `launchpad/decisions/ADR-0006-secret-scanning-engine-and-allowlist-location.md`
  — the accepted decision governing how a secret-scanning allowlist entry is
  written, if your change needs one.
- `launchpad/decisions/ADR-0013-config-management-ubuntu-baseline-runtime-shape.md`
  — the accepted decision for the deployment-time surface this node excludes.

## Boundary

This node does not describe:

- **What the configuration values are.** Their names, types, defaults, required
  flags and effects are lookup content, owned by the `layers/configuration/`
  shelf. Reproducing a table here would create a second copy that drifts.
- **How to acquire the underlying skills from scratch.** It assumes a
  contributor who can already build and run the relay, desktop and mobile apps.
- **Why the configuration layer is shaped the way it is.** The precedence model,
  the twelve-factor reasoning and the fail-closed principle are explanatory
  content held elsewhere in the corpus.
- **Deployment-time configuration of a running relay** — Helm values, Terraform
  stacks, `deploy/compose/`. That is an operations change, not a development one.
- **Responding to a misconfigured relay already in production.** That is a
  runbook's shape: triggered by a condition, not chosen on your own schedule.

## Relationships

Declared: `implements` → `corpus-template-procedure`, because
`templates/procedure.md` names exactly that edge for a node built from it; and
`references` → `layers-configuration-environment-configuration`,
`layers-configuration-relay-configuration`, `layers-configuration-validation`
and `development-prerequisites`.

Each target was checked against the merge target rather than this worktree, with
`git grep -l "^id: <target>$" origin/launchpad -- launchpad/docs/corpus`, and
each resolved to a file present on `origin/launchpad`. Other configuration-shelf
nodes named in *See also* are deliberately left as prose links rather than
declared edges: they are useful reading, but this procedure does not depend on
them, and `references` is documented as citation, not dependency.

## Scope and omissions

**This node covers** the ordered, executable procedure for changing
configuration in this repository across three surfaces — relay environment
variables, desktop preview feature flags, mobile compile-time defaults — the
verification that proves the change took effect, the rollback and cleanup that
each surface actually needs, and the repository-specific hazards a generic
"add an env var" instruction would miss.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The catalogue of configuration values themselves | `launchpad/docs/corpus/layers/configuration/` |
| The default-precedence mechanism across configuration surfaces | `launchpad/docs/corpus/layers/configuration/defaults.md` |
| Secret handling rules and the secret-shaped surface | `launchpad/docs/corpus/layers/configuration/secrets.md` |
| Development prerequisites and Hermit activation | `launchpad/docs/corpus/development/prerequisites.md`, `launchpad/docs/corpus/development/hermit.md` |
| Deployment-time configuration of a running relay | the operations surface, outside this node; the authorized shape is `launchpad/decisions/ADR-0013-config-management-ubuntu-baseline-runtime-shape.md` |
| Which secret-scanning engine the fork uses and where its allowlist lives | `launchpad/decisions/ADR-0006-secret-scanning-engine-and-allowlist-location.md` |
| The corpus front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |

**Known gap, stated because a reader will otherwise assume a gate exists.**
Nothing compares `.env.example` against `Config::from_env`. Searching `crates/`
and `scripts/` for `env.example` at the recorded revision returns only two doc
comments in `config.rs`, `scripts/dev-setup.sh` and
`scripts/test-ensure-local-relay-key.sh` — none of which asserts parity. The two
CI touchpoints that do read the file check something else entirely: gitleaks
allowlists it, and `dead-token-guard` greps it for dead API-token patterns. So a
variable added to the code and not to `.env.example`, or the reverse, ships
green. Step 4 of Task 1 is enforced by review only.

**Expected but not verified when this node was written:**

- **The procedures were not executed end to end.** Every step is grounded in
  reading `Justfile`, `config.rs`, `main.rs`, the two shell scripts, the desktop
  manifest and resolver, and the mobile `Env` class at the recorded revision. No
  relay was started, no invalid value was fed to `BUZZ_BIND_ADDR`, and no
  desktop or mobile build was produced to confirm the *Verify* commands behave as
  described. The template this node implements asks for execution evidence where
  practical; that evidence is absent here and the claims rest on source reading.
- **`just ci` was not run.** Its composition is quoted from `Justfile`, not from
  a run.
- **The `layers/configuration/` nodes were read only far enough to establish
  their scope** — headings and their opening scope sentences — not in full. The
  non-duplication claim in *Boundary* rests on that partial reading, so an
  overlap deeper inside one of those nodes would not have been caught.
- **No claim is made about what links *to* this node.** Nothing was checked, so
  nothing is asserted.
