---
id: layers-configuration-desktop-configuration
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
  - statement: "The desktop backend resolves its relay WebSocket URL via relay_ws_url() with precedence BUZZ_RELAY_URL env var (trimmed, empty treated as unset) > a BUZZ_DESKTOP_BUILD_RELAY_URL compile-time constant > a ws://localhost:3000 default; the same file's relay_api_base_url() resolves the relay's HTTP base URL with precedence BUZZ_RELAY_HTTP env var > a BUZZ_DESKTOP_BUILD_RELAY_HTTP compile-time constant > deriving it from relay_ws_url() by mapping ws->http and wss->https."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/relay.rs"
  - statement: "A workspace/community override, applied at runtime via the apply_workspace Tauri command, takes precedence over relay.rs's own env/build-time/default chain: relay_ws_url_with_override() and relay_api_base_url_with_override() check AppState.relay_url_override first and only fall back to relay_ws_url()/relay_api_base_url() when no override is set."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/relay.rs"
      - "desktop/src-tauri/src/commands/workspace.rs"
  - statement: "BUZZ_PRIVATE_KEY, parsed by identity_from_env() and consulted in build_app_state(), MUST win over any persisted/keyring identity when present and valid (the dev/CI/harness override); a present-but-malformed value is logged and treated as absent rather than left on an ephemeral identity, and this check runs before resolve_persisted_identity() executes in setup()."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs"
  - statement: "auto_connect_default_relay_enabled() reports true purely on the presence of the compile-time BUZZ_DESKTOP_BUILD_AUTO_CONNECT_DEFAULT_RELAY constant (option_env!(...).is_some()), not its value, so a build that sets it to an empty string still enables the flag; useCommunityInit.ts consumes this to auto-connect internal builds to their compiled default relay as the first community, skipping community-selection UI."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/identity.rs"
      - "desktop/src/features/communities/useCommunityInit.ts"
  - statement: "The frontend Community type declares relayUrl: string as required and token?: string / reposDir?: string as optional, in that declaration order in types.ts; a nsec?: never field is kept only so legacy localStorage entries deserialize without error, and loadCommunities() strips any lingering nsec value on read before it can leak into a later session."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/types.ts"
      - "desktop/src/features/communities/communityStorage.ts"
  - statement: "Community records are persisted as a JSON array under the buzz-communities localStorage key and the active community id under buzz-active-community-id, both read/written through communityStorage.ts's loadCommunities()/saveCommunities()/loadActiveCommunityId()/saveActiveCommunityId(), with a one-time migration from the legacy buzz-workspaces/buzz-active-workspace-id keys."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/communityStorage.ts"
  - statement: "useCommunityInit.ts calls applyCommunity(activeCommunity.relayUrl, undefined, activeCommunity.token, activeCommunity.reposDir, ...) on every community switch and deliberately never passes an nsec argument -- the persisted identity.key file resolved at startup is the single source of truth for the active key, and this call site refuses to apply a legacy-stored nsec even if one were present on the record."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts"
  - statement: "applyCommunity() (frontend) invokes the apply_workspace Tauri command with relayUrl, nsec, token, reposDir and agentManagedProfiles fields, but apply_workspace's Rust command signature (relay_url: String, nsec: Option<String>, repos_dir: Option<String>, agent_managed_profiles: Option<bool>, app: AppHandle) declares no token parameter, so the invite/join token carried on a Community record is not applied to backend state through this call."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/tauri.ts"
      - "desktop/src-tauri/src/commands/workspace.rs"
  - statement: "apply_workspace sets AppState.relay_url_override unconditionally from the given relay_url, parses and installs nsec only if it is present and non-empty, and resolves repos_dir through effective_repos_dir(): an invalid candidate is NOT persisted and does not fail the command -- relay/keys still apply, a repos-dir-error event surfaces the reason, and the REPOS symlink is skipped rather than pointed at a bad path."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/workspace.rs"
  - statement: "The effective repos_dir (None on validation failure) is persisted to a .repos-dir dotfile at the nest root by write_persisted_repos_dir(), read back at the next boot, and used to decide whether REPOS inside the nest is a real directory or a symlink to the configured path."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/repos.rs"
  - statement: "The desktop app's data/nest directory is ~/.buzz for a build whose Tauri identifier is xyz.block.buzz.app and ~/.buzz-dev for one whose identifier starts xyz.block.buzz.app.dev, selected once at startup by init_nest_dir(is_dev) and cached in a process-lifetime OnceLock; the identifier itself comes from tauri.conf.json's base identifier/productName, overridden by tauri.dev.conf.json's xyz.block.buzz.app.dev/Buzz Dev for dev builds."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/nest.rs"
      - "desktop/src-tauri/tauri.conf.json"
      - "desktop/src-tauri/tauri.dev.conf.json"
  - statement: "tauri.windows.conf.json overlays the base tauri.conf.json's bundle.externalBin list, omitting binaries/buzz-backend-kubernetes for Windows builds while the base list (used by every other platform) includes it."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
      - "desktop/src-tauri/tauri.windows.conf.json"
  - statement: "This OSS checkout's tauri.conf.json configures plugins.updater.endpoints as an empty array, so this repository's own build carries no auto-update endpoint; the root CLAUDE.md's ecosystem table documents that Block-signed builds are produced by the separate squareup/buzz-releases Buildkite pipeline, which this repository does not contain configuration for."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
      - "CLAUDE.md"
  - statement: "tauri.conf.json's app.windows (dimensions, title bar style, traffic-light position), app.security.csp, and bundle.macOS.dmg layout are static values identical across every deploy of the same build variant, failing Twelve-Factor's litmus test as internal application config that does not vary between deploys; architecture-containers-desktop already documents the CSP's security implications, so this node excludes that content rather than duplicating it."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "desktop/src/shared/features/ is a dedicated feature-flag module (manifest.ts, store.ts, FeatureGate.tsx) exporting getOverrides(); useCommunityInit.ts reads getOverrides().agentManagedProfiles to build the agentManagedProfiles argument passed to applyCommunity(), so that value is a feature-flag override, not a configuration setting documented here."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/index.ts"
      - "desktop/src/features/communities/useCommunityInit.ts"
  - statement: ".env.example documents BUZZ_PRIVATE_KEY and BUZZ_RELAY_URL in its ACP-harness (buzz-acp) section as the agent harness's own identity/connection variables; the desktop app reads the same two variable names independently, for its own process identity and relay resolution, via a separate code path (app_state.rs / relay.rs) that .env.example does not describe."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "Because each row in this node's settings table governs which relay/community a given desktop install talks to, which identity signs its events, or which build variant is running -- exactly the kind of value Twelve-Factor's litmus test asks whether the codebase could survive being open-sourced with -- the localStorage-persisted Community fields and the tauri.conf.json build-overlay identifiers are treated as deploy-varying configuration under this template's definition even though only a minority of the rows are literal OS environment variables read via std::env::var."
    entry_class: INFERENCE
    evidence:
      - "https://12factor.net/config"
      - "desktop/src-tauri/src/relay.rs"
      - "desktop/src/features/communities/communityStorage.ts"
    confidence: 0.75
  - statement: "Issue #1051's Objective is to create layers/configuration/agent-configuration.md as the canonical configuration node for agent configuration, so this node's BUZZ_PRIVATE_KEY/relay rows describe only the desktop app's own process identity/relay resolution, not the per-managed-agent environment injection (reserved_env_keys.rs, agent_env.rs) that #1051 owns."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1051 Objective"
  - statement: "Issue #1052's Objective is to create layers/configuration/defaults.md as the canonical configuration node for defaults, so a cross-cutting inventory of default values as a subject in their own right is that node's scope, not this one's (this node still states each of its own rows' default, per this template's required Structured entries section)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1052 Objective"
  - statement: "Issue #1054's Objective is to create layers/configuration/environment-configuration.md as the canonical configuration node for environment configuration, so a cross-cutting reference of every BUZZ_* environment variable across the whole repository is that node's scope, not this one's (this node covers only the subset the desktop app process itself reads)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1054 Objective"
  - statement: "Issue #1055's Objective is to create layers/configuration/feature-flags.md as the canonical configuration node for feature flags, so getOverrides()/agentManagedProfiles and any other desktop/src/shared/features value is that node's scope, not this one's."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1055 Objective"
  - statement: "relay.rs's configured_env_var() calls std::env::var(name) fresh on every invocation of relay_ws_url()/relay_api_base_url(), but nothing in the running desktop app mutates its own process environment at runtime, so a changed OS-level BUZZ_RELAY_URL/BUZZ_RELAY_HTTP value only takes effect on the app's next launch; build_app_state(), which reads BUZZ_PRIVATE_KEY exactly once via identity_from_env(), is itself invoked exactly once, from lib.rs's single .manage(build_app_state()) call at setup."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/relay.rs"
      - "desktop/src-tauri/src/app_state.rs"
      - "desktop/src-tauri/src/lib.rs"
  - statement: "relay.rs carries a #[cfg(test)] module exercising the relay URL/HTTP resolution precedence documented above; communityStorage.test.mjs exercises shouldAutoConnectDefaultRelay()'s exclusion of localhost/127.0.0.1/[::1]/0.0.0.0 hosts, the check that gates BUZZ_DESKTOP_BUILD_AUTO_CONNECT_DEFAULT_RELAY's auto-connect behavior; repos.rs carries its own test module exercising effective_repos_dir()'s persist/clear/reject behavior for a candidate repos_dir."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/relay.rs"
      - "desktop/src/features/communities/communityStorage.test.mjs"
      - "desktop/src-tauri/src/managed_agents/repos.rs"
  - statement: "No relationships were declared to any of this batch's four sibling configuration documents (#1051 agent-configuration, #1052 defaults, #1054 environment-configuration, #1055 feature-flags) because none is merged on origin/launchpad at this node's recorded revision -- AGENTS.md requires a relationships[].target to resolve against the merge-target branch, not the author's own worktree, and a target that only resolves in-worktree is a hard CI error on launchpad."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
relationships:
  - type: implements
    target: corpus-template-configuration
  - type: references
    target: architecture-containers-desktop
---

# Desktop app: configuration

This node catalogues the configuration surface of the **desktop app process
itself** — the settings a running `buzz-desktop` (Tauri) instance reads to
decide which relay/community it talks to, which identity it signs events
with, where it keeps its local working directory, and which build variant it
is. It covers the OSS checkout at `desktop/src-tauri/` and `desktop/src/`
only; it does not cover configuration of the managed-agent subprocesses the
desktop app spawns, a cross-repository inventory of `BUZZ_*` environment
variables, default values as a subject in their own right, or feature flags —
see *Boundary* below for the split against this dispatch's sibling
configuration documents.

Two distinct mechanisms feed this surface: (1) process environment
variables and Rust compile-time constants, read once at process
start/compile time, and (2) per-community settings a user enters in the
desktop UI, persisted to `localStorage`, and applied to the running Tauri
backend on every community switch via the `apply_workspace` command — the
pattern the root `CLAUDE.md`'s "Community Switching" section names, driven
from `desktop/src/features/communities/useCommunityInit.ts`.

## Settings

Row order follows each setting's own source file, in that file's own
declaration/read order; where more than one file is involved, rows are
grouped file-by-file (`relay.rs`'s two functions, then `app_state.rs`, then
`commands/identity.rs`, then `types.ts`'s own field order, then
`tauri.conf.json`'s top-level fields) rather than alphabetized.

| Variable / setting | Type | Default | Required | Secret | Reload behavior | Effect |
|---|---|---|---|---|---|---|
| `BUZZ_RELAY_URL` (env var) | string, WebSocket URL | none — falls through the chain | No | No | Restart required — read fresh from the process environment on each call, but nothing in the running app changes the process's own env, so a new value only takes effect on relaunch (or is superseded by a `Community.relayUrl` override). | Relay WS URL the desktop app connects to when no workspace/community override is active. |
| `BUZZ_DESKTOP_BUILD_RELAY_URL` (compile-time constant) | string, WebSocket URL | none — falls through to `ws://localhost:3000` | No | No | Rebuild required — `option_env!` bakes the value in at `cargo build` time. | Build-baked fallback relay WS URL, used only when `BUZZ_RELAY_URL` is unset at runtime; set by the build pipeline, not by an installed app's user. |
| `BUZZ_RELAY_HTTP` (env var) | string, HTTP(S) base URL | none — falls through the chain | No | No | Restart required, same as `BUZZ_RELAY_URL`. | Overrides the relay's HTTP API base URL independently of the WS URL. |
| `BUZZ_DESKTOP_BUILD_RELAY_HTTP` (compile-time constant) | string, HTTP(S) base URL | none — falls through to deriving it from the resolved WS URL | No | No | Rebuild required, same as `BUZZ_DESKTOP_BUILD_RELAY_URL`. | Build-baked fallback HTTP base URL, used only when `BUZZ_RELAY_HTTP` is unset at runtime. |
| `BUZZ_PRIVATE_KEY` (env var) | string, hex or `nsec1…` bech32 Nostr private key | none — falls through to persisted/keyring identity, or a freshly generated ephemeral key | No | **Yes** | Restart required — read once in `build_app_state()`, called once at process startup. | When present and parseable, becomes the desktop app's own active signing identity for the process, overriding any persisted/keyring identity (the dev/CI/harness override path). |
| `BUZZ_DESKTOP_BUILD_AUTO_CONNECT_DEFAULT_RELAY` (compile-time constant, presence-only) | opaque — only presence is checked, not value | unset | No | No | Rebuild required. | When set (to any value, including empty), an internal build auto-connects to its compiled default relay as the first community on first run, skipping community-selection UI, for non-shared-identity flows. |
| `Community.relayUrl` (per-community, UI-entered, `localStorage`-persisted) | string, WebSocket URL | none — required per community record | **Yes** (per community) | No | Dynamically reloadable — applied live by `apply_workspace` on every community switch, no app restart. | Applied to `AppState.relay_url_override` via `apply_workspace`, taking precedence over every env/build-time/default value above for the active community. |
| `Community.token` (per-community, UI-entered, `localStorage`-persisted) | string, opaque invite/join token | none | No | **Yes** (community-access credential) | Not applicable through `apply_workspace` — see *Effect*. | Passed by the frontend to `apply_workspace`, but `apply_workspace`'s Rust signature accepts no `token` parameter — see *Boundary* and *Scope and omissions* for what this pass could and could not confirm about it. |
| `Community.reposDir` (per-community, UI-entered, `localStorage`-persisted) | string, absolute filesystem path (`~` expanded client-side before save) | unset = the nest's own real `REPOS` directory | No | No | Dynamically reloadable — applied live by `apply_workspace`, no app restart. | Applied via `apply_workspace`; a valid path is persisted to a `.repos-dir` dotfile and `REPOS` inside the nest is symlinked to it. An invalid candidate is non-fatal: not persisted, `REPOS` stays a real directory, and a `repos-dir-error` event surfaces the reason. |
| `identifier` / `productName` (`tauri.conf.json`, overlaid per build variant by `tauri.dev.conf.json`) | string | `xyz.block.buzz.app` / `Buzz` (prod); `xyz.block.buzz.app.dev` / `Buzz Dev` (dev) | Yes (base file always present) | No | Rebuild required — resolved once at startup from the compiled bundle identifier via `init_nest_dir()`, itself fixed by which overlay was baked in at build time. | Selects the OS app-data/bundle identity and, via `init_nest_dir()`, whether the local nest directory is `~/.buzz` or `~/.buzz-dev`. |

**Verification.** `relay.rs`'s own `#[cfg(test)]` module exercises the
env/build-time/default precedence rows above; `communityStorage.test.mjs`
exercises `shouldAutoConnectDefaultRelay()`'s local-host exclusion (the check
that gates `BUZZ_DESKTOP_BUILD_AUTO_CONNECT_DEFAULT_RELAY`'s auto-connect
behavior); `repos.rs`'s own test module exercises `effective_repos_dir()`'s
three-way persist/clear/reject behavior for `Community.reposDir`. Cited here
rather than restated — see those files directly for the individual cases.

## Litmus test

Every row above genuinely varies between deploys per the Twelve-Factor
litmus test — "whether the codebase could be made open source at any moment,
without compromising any credentials." Each row governs which
relay/community a given install talks to, which identity signs its events,
where its working files live, or which build variant is running, and none of
those values is safe to bake identically into every install.

**Excluded as internal application config**, per Twelve-Factor's own
carve-out for values that "do not vary between deploys": `tauri.conf.json`'s
`app.windows` (dimensions, title bar style, traffic-light position),
`app.security.csp`, and `bundle.macOS.dmg` layout. These are identical
across every deploy of the same build variant. `architecture-containers-
desktop` already documents the CSP's security implications; this node does
not duplicate that content. `Community.token`'s status is not fully resolved
by this pass — see *Boundary* and *Scope and omissions*.

## Secrets discipline

No row above quotes a live credential, key, token, or hostname value.
`BUZZ_PRIVATE_KEY`'s row cites the environment variable name and the code
path that reads it (`app_state.rs`'s `identity_from_env()`), never a key
value. `Community.token`'s row cites the field name and the code paths that
carry it, never a token value.

## Boundary

This node does not describe:

- **Per-managed-agent environment configuration** — the reserved-keys guard
  (`reserved_env_keys.rs`), per-agent env building (`agent_env.rs`), and the
  `BUZZ_DESKTOP_BUILD_BUZZ_AGENT_PROVIDER`/`BUZZ_DESKTOP_BUILD_BUZZ_AGENT_MODEL`/
  `BUZZ_DESKTOP_BUILD_AGENT_ENV` compile-time constants that shape a *spawned
  agent's* environment are `layers/configuration/agent-configuration.md`'s
  subject (#1051), not this node's. This node's `BUZZ_PRIVATE_KEY` row is
  strictly about the desktop app's own process identity, a distinct code path
  (`app_state.rs`) from what it injects into an agent subprocess.
- **A cross-cutting defaults inventory** — this node states each of its own
  rows' default, as the template requires, but a broader treatment of
  default values as a subject in their own right is
  `layers/configuration/defaults.md`'s scope (#1052).
- **A cross-repository `BUZZ_*` environment-variable reference** —
  `layers/configuration/environment-configuration.md` (#1054) is the
  cross-cutting catalogue; this node covers only the subset the desktop app
  process itself reads.
- **Feature flags** — `getOverrides()`/`agentManagedProfiles` and any other
  value sourced from `desktop/src/shared/features/` is
  `layers/configuration/feature-flags.md`'s subject (#1055), not
  configuration in this template's sense.
- **The relay's own configuration surface** — `crates/buzz-relay/src/
  config.rs`'s `Config` struct is a different process entirely and out of
  scope here.
- **The identity-storage backend mechanism's full detail** (system keyring /
  local file / environment / ephemeral) — `architecture-containers-desktop`
  already documents it; this node's `references` edge points there rather
  than restating it.
- **Internal application config that fails the litmus test** — see
  *Litmus test* above for what was excluded and why.

## Relationships

- `implements: corpus-template-configuration` — this node is an instance of
  the configuration template, per that template's own required-relationships
  guidance.
- `references: architecture-containers-desktop` — the merged container node
  already documents the desktop app's relay-URL override chain and identity-
  storage backends at architecture altitude; this node cites it as
  supporting context rather than restating it, consistent with `references`'
  directionality ("source cites target as supporting context; no ownership
  or currency dependency implied").
- No `relationships` were declared toward `layers-configuration-agent-
  configuration`, `layers-configuration-defaults`, `layers-configuration-
  environment-configuration`, or `layers-configuration-feature-flags` — none
  of the four exists on `origin/launchpad` at this node's recorded revision
  (all four are open, unmerged sibling tasks in this same dispatch batch).
  Per `AGENTS.md`, a `relationships[].target` must resolve against the
  merge-target branch, not the author's own worktree; adding those edges is
  the natural follow-up once any of the four siblings merges.

## Scope and omissions

**This node covers** the desktop app process's own configuration surface:
environment variables and Rust compile-time constants read at process
start/compile time (relay URL/HTTP base, the app's own signing identity, the
internal-build auto-connect flag), and per-community settings entered in the
desktop UI, persisted to `localStorage`, and applied to the running Tauri
backend via `apply_workspace` (relay URL override, invite token, repos
directory), plus the build-variant identifiers in `tauri.conf.json` and its
dev/platform overlays that select the app's data directory and bundled
binaries.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Per-managed-agent environment configuration | `layers/configuration/agent-configuration.md`, #1051 (open, unmerged) |
| Default values as a cross-cutting subject | `layers/configuration/defaults.md`, #1052 (open, unmerged) |
| A full `BUZZ_*` environment-variable reference | `layers/configuration/environment-configuration.md`, #1054 (open, unmerged) |
| Feature flags (`getOverrides()` and friends) | `layers/configuration/feature-flags.md`, #1055 (open, unmerged) |
| The relay's own `Config` struct / environment surface | `crates/buzz-relay/src/config.rs`, no corpus node found for it yet |
| Identity-storage backend selection detail (keyring/local-file/ephemeral) | `architecture-containers-desktop` |
| The per-type configuration standard's own future revision | `launchpad/docs/corpus/templates/configuration.md`, `corpus-template-configuration` |

**Expected but not verified when this node was written:**

- **Whether `Community.token` is consumed anywhere in the invite/join-request
  flow, or is effectively dead weight passed into `apply_workspace` and
  silently ignored, was not resolved.** This pass confirmed the Rust command
  signature has no `token` parameter, and found the field threaded through
  onboarding code (`desktop/src/features/onboarding/communityOnboarding.tsx`)
  as a plain carried value, but did not trace whether a join-request Nostr
  event or some other code path reads it independently of `apply_workspace`.
  Flagged as a candidate follow-up rather than resolved here, per this
  corpus's one-idea-per-node rule.
- **Whether an internal/Block-signed build (`squareup/buzz-releases`)
  overlays `plugins.updater.endpoints` or other `tauri.conf.json` fields with
  real values was not checked** — that pipeline lives in a separate
  repository this corpus does not currently ingest; only this repository's
  own checked-in `tauri.conf.json` (empty `updater.endpoints`) was read.
- **Whether the `BUZZ_DESKTOP_BUILD_*` compile-time constants excluded here
  as agent-configuration (#1051's scope) form a complete list was not
  audited.** Only `relay.rs`, `commands/identity.rs`,
  `commands/relay_reconnect.rs`, `managed_agents/access_policy.rs` and
  `managed_agents/agent_env.rs` were grepped for the prefix; a full-repository
  sweep for other, undiscovered compile-time build variables was not run.
