---
id: layers-configuration-defaults
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and layers is the value naming the corpus surface this node documents, since this node describes how the configuration layer resolves a default value, not a rule about authoring the corpus itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "At this node's recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists only AGENTS.md, README.md, the schema/ subtree, standards/**, and templates/** -- no layers/ subtree and no prior type: layers node exists on origin/launchpad to copy front-matter shape from."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/**, standards/**, templates/**, no layers/ subtree, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #1052 scopes this node to the cross-cutting default-value mechanism and precedence itself, deliberately distinct from any one surface's specific configuration values, which sibling issues #1051 (agent), #1053 (desktop), #1054 (environment), #1056 (mobile), #1057 (relay), #1058 (secrets) and #1059 (validation) each own."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1052 task instructions, this session"
  - statement: "crates/buzz-relay/src/config.rs's Config::from_env doc comment states it 'Loads configuration from environment variables, falling back to development defaults,' and its bind_addr, database_url, redis_url and relay_url fields are each resolved via std::env::var(NAME).unwrap_or_else(|_| \"<literal>\".to_string()), so an unset variable silently falls back to a hardcoded string rather than erroring."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "config.rs's redis_pool_size and db_pool_size fields are resolved via std::env::var(NAME).ok().and_then(|v| v.parse().ok()).filter(|&v| v > 0).unwrap_or(N), so an unset variable, an unparsable value, and a non-positive value all silently converge on the same coded default rather than being distinguished or reported."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: ".env.example's commented-out line '# BUZZ_REDIS_POOL_SIZE=16' names the same value as config.rs's own .unwrap_or(16) fallback for BUZZ_REDIS_POOL_SIZE, and the file's header states 'All defaults here work with `docker compose up` out of the box' -- the example file documents a suggested value for local development, while the code's own fallback is the authoritative default whenever the two could disagree."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-cli/src/lib.rs's Cli struct declares #[arg(long, env = \"BUZZ_RELAY_URL\", default_value = \"http://localhost:3000\")] on its relay field; the command's own long_about states outright 'Configuration (flags override env vars)', and the field's own doc comment states 'Overrides BUZZ_RELAY_URL env var' -- a three-tier precedence (explicit CLI flag, then the environment variable, then the baked default_value) stated in the CLI's own first-party text, not inferred from clap's general behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "The repository's Justfile sets 'set dotenv-load := true' (line 3), so .env is loaded into the process environment by the just task runner itself before a recipe runs, not by any buzz-* binary."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Cargo.lock lists dotenvy as a dependency only of sqlx-macros-core, sqlx-mysql and sqlx-postgres (compile-time query-macro resolution), never of buzz-relay, buzz-cli, or any other buzz-* crate, so no buzz-* binary loads .env itself at runtime."
    entry_class: FACT
    evidence:
      - "Cargo.lock"
  - statement: "Because no buzz-* binary reads .env directly, a value set in .env (loaded by just before the process starts) and a value exported directly in the calling shell are indistinguishable to std::env::var and to clap's env() resolution by the time Config::from_env or the CLI's argument parser runs -- .env is a dev-convenience layer added before process start, not a second precedence tier the code itself implements."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - "Cargo.lock"
      - "crates/buzz-relay/src/config.rs"
    confidence: 0.85
  - statement: "crates/buzz-relay/src/config.rs resolves relay_private_key as std::env::var(\"BUZZ_RELAY_PRIVATE_KEY\").ok(), carrying no literal string fallback (unlike bind_addr, database_url, redis_url and relay_url above), so an unset secret-shaped setting resolves to None rather than to a baked value."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/main.rs resolves the relay's signing keypair with three distinct outcomes: if BUZZ_RELAY_PRIVATE_KEY is set, it is parsed and used; if unset and config.require_auth_token is false (dev mode), a hardcoded, publicly-visible placeholder key ('000...0001') is used and a tracing::warn! names the resulting public key and instructs the operator to 'Set BUZZ_RELAY_PRIVATE_KEY for production'; if unset and require_auth_token is true, the process panics with 'BUZZ_RELAY_PRIVATE_KEY must be set when BUZZ_REQUIRE_AUTH_TOKEN=true. A stable relay identity is required for production.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "A secret-shaped setting's 'default' in this codebase is therefore never a hidden real secret baked into code -- it is either a well-known, non-secret placeholder used only in an explicitly weaker dev posture (require_auth_token=false), or no default at all, failing closed with a panic in the stricter posture -- structurally different from the unconditional string-literal fallback ordinary settings like bind_addr receive."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
    confidence: 0.85
  - statement: "crates/buzz-relay/src/config.rs defines an inert_env_vars helper and an INERT_MEDIA_READ_AUTH_VARS constant naming BUZZ_REQUIRE_MEDIA_GET_AUTH and BUZZ_REQUIRE_MEDIA_READ_AUTH; when Config::from_env finds either set, it logs a warn! stating the variable 'is set but is no longer read' and that a value of false 'does not re-open unauthenticated media reads' -- the setting is accepted without error but has no effect, and .env.example documents the same removal in its Media Upload Admission section."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - ".env.example"
  - statement: "mobile/lib/shared/relay/relay_provider.dart's Env class defines 'static const relayUrl = String.fromEnvironment(\"BUZZ_RELAY_URL\", defaultValue: \"http://localhost:3000\")', with the doc comment 'Compile-time environment config via --dart-define.'"
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart"
  - statement: "Because Dart's String.fromEnvironment resolves at compile time from --dart-define (or --dart-define-from-file), changing either the override or the fallback default for this mechanism requires rebuilding the mobile binary, not merely restarting it -- a materially different restart/reload story than the Rust env-var-at-process-start mechanisms above, which only require a process restart to pick up a changed variable."
    entry_class: INFERENCE
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart"
      - "crates/buzz-relay/src/config.rs"
    confidence: 0.9
  - statement: "desktop/src/shared/features/resolveEnabled.ts resolves a preview feature flag as 'overrides[featureId] ?? defaultEnabled' with defaultEnabled defaulting to false, and desktop/src/shared/features/useFeatureEnabled.ts's own doc comment states the precedence directly: 'in manifest (preview): explicit user override, then manifest default (off if omitted); NOT in manifest (stable): always true (fail-open).'"
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/resolveEnabled.ts"
      - "desktop/src/shared/features/useFeatureEnabled.ts"
  - statement: "desktop/src/shared/features/manifest.ts falls back to an empty manifest ({version: 1, features: []}) with a console.warn when the bundled preview-features.json fails its zod schema validation (FeaturesManifestSchema.safeParse), rather than throwing -- a fail-open default one level above any single feature's own default."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/manifest.ts"
  - statement: "desktop/src/shared/features/useFeatureEnabled.ts's subscribe function listens for the browser 'storage' event to sync feature-flag overrides across windows, and useFeatureSnapshot uses useSyncExternalStore, so an overridden default takes effect reactively without an app restart."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/useFeatureEnabled.ts"
  - statement: "AGENTS.md's node-creation step 9 requires a relationships[].target to name a node that exists on the branch being merged into, checked with git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, not the author's own worktree, and this node declares no relationships because no other corpus node on origin/launchpad addresses configuration-shaped subject matter at the recorded revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
---

# Configuration layer: the default-value mechanism and its precedence

This node documents **how a default value is decided and what takes precedence over
what** across Buzz's configuration surfaces -- the cross-cutting mechanism, not any
one surface's catalogue of settings. Four distinct default-resolution mechanisms
exist side by side in this repository, differing in where the default lives, what
overrides it, and what "restart required" even means for that mechanism.

**This node does not catalogue any surface's specific settings.** The agent
harness's variables, the desktop app's variables, deployment environment variables,
the mobile app's variables, the relay's variables, secret-handling specifics, and
validation rules each belong to their own corpus node (see *Scope and omissions*).
This node's job is the layer underneath all of them: the shape of a default, and
which source wins when more than one is present.

## Mechanism 1 -- runtime environment variable with a coded fallback

**Where:** `crates/buzz-relay/src/config.rs`, `Config::from_env`. Its own doc
comment: "Loads configuration from environment variables, falling back to
development defaults."

**Shape:** for a string-shaped setting, `std::env::var(NAME).unwrap_or_else(|_|
"<literal>".to_string())` -- `bind_addr`, `database_url`, `redis_url` and
`relay_url` all follow this pattern. For a numeric setting with validation,
`std::env::var(NAME).ok().and_then(|v| v.parse().ok()).filter(|&v| v > 0)
.unwrap_or(N)` -- `redis_pool_size` and `db_pool_size` follow this pattern.

**Default/required:** every field shown above has a default; none of these
particular fields are required. **Validation:** the numeric pattern silently
converges an unset variable, an unparsable value, and a non-positive value onto the
same coded fallback -- it does not distinguish "absent" from "malformed" in its
outcome.

**Environment-specific / restart:** the variable is read once, at process start
(`Config::from_env` is called during relay startup); changing it requires a process
restart, not a hot reload.

**Effect of `.env.example`:** the file's commented-out suggested values (e.g.
`# BUZZ_REDIS_POOL_SIZE=16`) match the code's own fallback exactly, and the file's
header states its defaults "work with `docker compose up` out of the box." The
example file documents a *suggested* value for local development; the code's own
fallback is the authoritative default whenever the two could disagree, because the
example file is never read by the running process -- only `.env` (via the
mechanism below) or a real exported variable is.

## Mechanism 2 -- CLI flag over environment variable over baked default (`buzz-cli`)

**Where:** `crates/buzz-cli/src/lib.rs`, the `Cli` struct. `relay` is declared
`#[arg(long, env = "BUZZ_RELAY_URL", default_value = "http://localhost:3000")]`.

**Precedence, stated first-party:** the command's own `long_about` text says
outright, "Configuration (flags override env vars)," and the `relay` field's doc
comment adds "Overrides BUZZ_RELAY_URL env var." So the order is: an explicit
`--relay` flag on this invocation, else the `BUZZ_RELAY_URL` environment variable,
else the baked `default_value`. This is stated in the CLI's own text, not inferred
from clap's general documented behavior.

**Restart concept:** does not apply the way it does to a long-running server --
`buzz-cli` is a one-shot process, so precedence is resolved fresh on every
invocation.

**Secret-shaped fields differ:** `private_key` and `auth_tag` are declared with
`env = "..."` and `hide_env_values = true` but **no** `default_value` -- there is
nothing for these to fall back to; they resolve to `None` if neither a flag nor the
named environment variable supplies a value, matching Mechanism 4 below rather than
the string-literal-fallback pattern above.

## Mechanism 3 -- compile-time baked default (`--dart-define`, mobile)

**Where:** `mobile/lib/shared/relay/relay_provider.dart`, the `Env` class:
`static const relayUrl = String.fromEnvironment("BUZZ_RELAY_URL", defaultValue:
"http://localhost:3000")`. Its own doc comment: "Compile-time environment config
via `--dart-define`."

**Structural difference from Mechanisms 1-2:** `String.fromEnvironment` resolves at
**compile time**, not at process start. The override (`--dart-define=...`) and the
fallback default are both baked into the built binary. **Restart is not the
relevant unit here -- a rebuild is.** Changing either the override value or the
coded default requires rebuilding the mobile app; restarting an already-built app
changes nothing, unlike Mechanism 1's runtime environment read.

## Mechanism 4 -- runtime user override over a static manifest default (desktop feature flags)

**Where:** `desktop/src/shared/features/resolveEnabled.ts`: `overrides[featureId]
?? defaultEnabled` (`defaultEnabled` parameter defaults to `false`).
`desktop/src/shared/features/useFeatureEnabled.ts`'s own doc comment states the
full precedence: "in manifest (preview): explicit user override, then manifest
default (off if omitted); NOT in manifest (stable): always true (fail-open)."

**Default/required:** a feature's `defaultEnabled` field in `preview-features.json`
is optional (validated by a zod schema in `manifest.ts`); omitting it is equivalent
to `false`. A feature *absent from the manifest entirely* is stable by definition
and always resolves `true` -- the inverse of the in-manifest default, and a
deliberate fail-open choice so a stale reference to a removed feature id never
hides UI.

**Failure behavior one layer up:** if the bundled `preview-features.json` itself
fails its zod schema validation, `manifest.ts` logs a `console.warn` and falls back
to an empty manifest (`{version: 1, features: []}`) rather than throwing --
every feature then resolves via the "not in manifest" branch (`true`, fail-open).

**Restart / reload:** an override is a runtime value read reactively via
`useSyncExternalStore`, and `useFeatureEnabled.ts`'s `subscribe` function listens
for the browser `storage` event so a change in one window is picked up in another
without an app restart -- the most dynamically reloadable of the four mechanisms
documented here.

## `.env` and the process environment

The repository's `Justfile` sets `set dotenv-load := true` (line 3): **`just`
itself** loads `.env` into the process environment before running a recipe.
`Cargo.lock` lists `dotenvy` as a dependency only of `sqlx-macros-core`,
`sqlx-mysql` and `sqlx-postgres` (compile-time query-macro resolution) -- never of
`buzz-relay`, `buzz-cli`, or any other `buzz-*` crate. No `buzz-*` binary loads
`.env` itself at runtime.

The practical consequence: by the time `Config::from_env` or `buzz-cli`'s argument
parser runs, a value that came from `.env` (loaded by `just` before the process
started) and a value the caller exported directly in their shell are
indistinguishable to `std::env::var`. `.env` is a dev-convenience layer added
*before* the process starts, not a second precedence tier the code itself
implements or is aware of.

## Secrets: what "default" means for a secret-shaped setting

None of the four mechanisms above hides a real secret behind a baked default.
`crates/buzz-relay/src/config.rs` resolves `relay_private_key` as
`std::env::var("BUZZ_RELAY_PRIVATE_KEY").ok()` -- no literal fallback string, unlike
`bind_addr` or `database_url`. `crates/buzz-relay/src/main.rs` then resolves the
relay's actual signing keypair with three distinct, non-secret-leaking outcomes:

1. **Set:** the provided value is parsed and used.
2. **Unset, and `require_auth_token` is false (an explicitly weaker dev posture):**
   a hardcoded, publicly-visible placeholder key (`000...0001`) is used, and a
   `tracing::warn!` names the resulting public key and states "Set
   `BUZZ_RELAY_PRIVATE_KEY` for production."
3. **Unset, and `require_auth_token` is true:** the process **panics** --
   "`BUZZ_RELAY_PRIVATE_KEY` must be set when `BUZZ_REQUIRE_AUTH_TOKEN=true`. A
   stable relay identity is required for production." No default exists in this
   posture; the setting fails closed.

So a secret-shaped setting's "default," in this codebase, is either a well-known,
non-secret placeholder confined to an explicitly weaker posture, or no default at
all -- never a hidden real value baked into the binary. This node names no live
credential, key, token or hostname value anywhere above; every quoted string is
either a public placeholder the code itself prints in a warning, or a
non-authoritative example already committed at `.env.example`.

## Compatibility and deprecation

`config.rs` defines an `inert_env_vars` helper and an
`INERT_MEDIA_READ_AUTH_VARS` constant naming `BUZZ_REQUIRE_MEDIA_GET_AUTH` and
`BUZZ_REQUIRE_MEDIA_READ_AUTH`. If either is present in the environment,
`Config::from_env` logs a `warn!` stating the variable "is set but is no longer
read" and that a value of `false` "does not re-open unauthenticated media reads."
`.env.example`'s own Media Upload Admission section documents the same removal.
This is this codebase's live pattern for deprecating a configuration input: the
variable is still accepted (so an old `.env` does not become a startup error), it
is structurally inert (parsing it changes nothing), and its presence produces a
warning rather than silence -- distinct from Mechanism 4's fail-open "unknown
feature id" case, which warns only in development builds
(`import.meta.env.DEV`) and otherwise stays silent.

## Boundary

This node does not describe:
- any surface's specific configuration values or settings tables -- see *Scope and
  omissions* below for where each lives;
- the parsing/validation logic in full for any one file (`config.rs` alone is 733
  lines; this node quotes representative fields, not an exhaustive audit);
- secret *values* -- only the shape of how a secret-shaped default resolves, per
  the *Secrets* section above, which names no live credential anywhere.

## Relationships

None declared. At this node's recorded revision, `git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus` lists only `AGENTS.md`, `README.md`, the
`schema/` subtree, `standards/**` and `templates/**` -- no other node on
`origin/launchpad` addresses configuration-shaped subject matter this node could
`references`, `depends-on`, or sit `part-of`. A useful candidate exists
(`corpus-template-configuration`, from issue `#1332`) but its branch is not merged
to `origin/launchpad` at this revision, so per `AGENTS.md` step 9's merge-target
rule, no edge is declared toward it; a future update to this node is the right
moment to add one once that node merges.

## Scope and omissions

**This node covers** the cross-cutting mechanism by which a configuration default
is decided and which source takes precedence over which, illustrated with four
structurally distinct mechanisms actually present in this repository: a runtime
environment variable with a coded fallback (relay), a CLI-flag-over-env-var-over-
baked-default layering (`buzz-cli`), a compile-time baked default resolved via
`--dart-define` (mobile), and a runtime user-override-over-static-manifest default
(desktop feature flags) -- plus where `.env` sits relative to the real process
environment, what a secret-shaped setting's "default" looks like, and one concrete
example of deprecating a configuration input in place.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The agent harness's (`buzz-acp`) specific environment variables | `#1051` |
| The desktop app's specific configuration surface | `#1053` |
| Deployment/environment-specific configuration values | `#1054` |
| The mobile app's specific configuration surface (beyond the one `Env.relayUrl` example above) | `#1056` |
| The relay's full settings catalogue (`config.rs` is 733 lines; only representative fields are quoted here) | `#1057` |
| Secret *values*, storage, and rotation practice | `#1058` |
| Configuration validation rules in general | `#1059` |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether every field in `crates/buzz-relay/src/config.rs` (733 lines) follows
  one of the two Mechanism-1 patterns quoted above, or whether exceptions exist.**
  A representative sample (string-with-fallback, numeric-with-parse-filter-
  fallback, the secret-shaped `relay_private_key`) was read; the file was not
  audited field by field.
- **Whether mobile has a manifest-equivalent mechanism beyond the single
  `Env.relayUrl` example quoted above.** Only that one call site was opened; a
  broader survey of `mobile/lib` for other `String.fromEnvironment` uses was not
  performed.
- **Whether `corpus-template-configuration` (`#1332`, unmerged at this revision)
  will, once merged, describe this same layering differently.** That node was read
  for context but is not treated as authoritative here since it is not present on
  `origin/launchpad`.
