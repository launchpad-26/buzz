---
id: implementation-desktop-tauri-backend
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "The desktop backend is the Rust crate at desktop/src-tauri/ (package buzz-desktop, lib name buzz_lib), built on tauri = \"2\", excluded from the repository root Cargo workspace by that root manifest's own `exclude = [\"desktop/src-tauri\"]` line -- so root-level `cargo test`/`cargo check --workspace` never exercises it, confirming CLAUDE.md's own gotcha #5."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
      - "Cargo.toml"
  - statement: "The crate statically links five Buzz path dependencies into the same binary: buzz-core (55 files reference it), buzz-sdk (17 files), buzz-voice (2 files, both under src/huddle/), buzz-persona (1 file, migration.rs only) and buzz-agent (4 files, all for shared config/error types -- WINDOWS_SHELL_RESOLUTION_ENV, DatabricksModelFilter, Provider, AgentError -- never for running an agent turn in-process)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
      - "desktop/src-tauri/src/huddle/pocket.rs"
      - "desktop/src-tauri/src/huddle/tts_voice_import.rs"
      - "desktop/src-tauri/src/migration.rs"
      - "desktop/src-tauri/src/managed_agents/git_bash.rs"
      - "desktop/src-tauri/src/commands/agent_models_databricks.rs"
  - statement: "Two further path dependencies are linked for narrower purposes: buzz-ws-client (used only by native_relay_client.rs, the app's own NIP-42 WebSocket connection to the relay) and a local nested crate, buzz-terminal (package buzz-terminal, a member of desktop/src-tauri's own separate [workspace] table), used only by terminal_runtime.rs, terminal_transport.rs and terminal_runtime/scroll_sign.rs for the embedded PTY terminal."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/native_relay_client.rs"
      - "desktop/src-tauri/Cargo.toml"
      - "desktop/src-tauri/src/terminal_runtime.rs"
  - statement: "The crate's src/ tree contains 92 files that carry at least one #[tauri::command] attribute, totaling 348 attribute occurrences (counted directly); the generate_handler! macro in lib.rs registers roughly 336-337 comma-separated entries in the default (non-mesh-llm) build, and the ~12-entry gap is explained by mesh_llm.rs's six #[cfg(feature = \"mesh-llm\")] commands each pairing with a same-named #[cfg(not(feature = \"mesh-llm\"))] stub in mesh_llm_stubs.rs -- two attributed definitions of one registered identifier, active one at a time depending on the crate's default feature set (system-keyring only; mesh-llm is opt-in)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs"
      - "desktop/src-tauri/src/commands/mesh_llm.rs"
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The command surface is organized into families by source directory: commands/ (agent_* -- config/access/auth/discovery/logs/metrics/models/providers/settings/update-rollback; channels, messages, personas, teams, project_git_* for local git operations, media_* for upload/download/transcode/gif/animated-snapshot, identity, pairing, workflows, canvas, social, dms, notifications, updater, window_chrome/window_vibrancy, workspace), huddle/ (voice channel session, TTS/STT pipeline, audio device control -- ~37 #[tauri::command] attributes), and managed_agents/ (agent process lifecycle -- ~6 top-level commands plus the internal spawn/discovery/reconcile machinery those commands call into)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/mod.rs"
      - "desktop/src-tauri/src/huddle/mod.rs"
      - "desktop/src-tauri/src/lib.rs"
  - statement: "Local git operations run the system `git` binary as a subprocess (commands/project_git_exec.rs), with a 60-second timeout for local operations and a 300-second timeout for remote operations, and an identity nsec handed to git-credential-nostr via environment variables only -- explicitly so no key material touches disk or global git config."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/project_git_exec.rs"
  - statement: "managed_agents/discovery.rs (and its discovery/ submodule -- presets.rs, login_shell.rs, windows_install.rs, bounded_command.rs, auth_status_cache.rs) is the native integration that locates installed AI-agent CLIs on the host (Claude Code, Codex, Goose, buzz-agent, and other presets), resolving each one's command path across platform-specific shells, including a login-shell probe and an nvm-aware PATH search on macOS/Linux and a dedicated Windows install-detection path."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/discovery.rs"
      - "desktop/src-tauri/src/managed_agents/discovery/presets.rs"
      - "desktop/src-tauri/src/managed_agents/discovery/login_shell.rs"
      - "desktop/src-tauri/src/managed_agents/discovery/windows_install.rs"
  - statement: "managed_agents/runtime.rs (plus its runtime/ submodule -- process.rs, lifecycle.rs, spawn_key.rs, stop.rs, sweep.rs, orphan_sweep.rs, instance_reaper.rs) is the process-lifecycle hub for managed agent subprocesses: building each agent's environment, spawning, tracking, stopping and reaping orphaned processes."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs"
  - statement: "managed_agents/backend.rs implements a versioned (protocol_version: 1) JSON-over-stdio handshake -- a provider must return {ok: true, name, version, description, config_schema, ...} -- that the desktop app uses to talk to any external compute-provider subprocess, with stdout capped at 1 MB and stderr at 64 KB against a buggy or malicious provider; this is the interface buzz-backend-kubernetes (bundled as an externalBin, not linked as a Cargo path dependency) is spawned and driven through."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs"
      - "desktop/src-tauri/tauri.conf.json"
  - statement: "crates/buzz-relay-mesh's own Cargo.toml describes it as \"Inter-relay QUIC mesh: transport, membership, and the fenced wire contract\" -- relay-to-relay networking, not a compute backend -- and it is referenced nowhere under desktop/src-tauri/ (zero matches for buzz_relay_mesh or buzz-relay-mesh). The crate actually wired to the desktop backend as a Kubernetes compute backend is buzz-backend-kubernetes (Cargo.toml description: \"Kubernetes backend provider for Buzz remote agents\"), bundled as the `binaries/buzz-backend-kubernetes` externalBin. managed_agents/relay_mesh.rs's RELAY_MESH_* constants are unrelated to either crate: they are wire-format glue for the mesh-llm shared-compute Cargo feature (translating a stored \"relay-mesh\" provider selection into OpenAI-compatible transport env vars for buzz-agent), a naming collision with the buzz-relay-mesh crate's name that is coincidental, not a dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/Cargo.toml"
      - "crates/buzz-backend-kubernetes/Cargo.toml"
      - "desktop/src-tauri/tauri.conf.json"
      - "desktop/src-tauri/src/managed_agents/relay_mesh.rs"
  - statement: "The updater integration (commands/updater.rs, tauri-plugin-updater) is registered only in non-debug builds behind a `buzz_updater_enabled` compile-time cfg flag, and is_auto_update_supported() further gates Linux specifically on the APPIMAGE environment variable, since Tauri's updater can only swap an AppImage bundle, not a .deb/.rpm install."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs"
      - "desktop/src-tauri/src/commands/updater.rs"
  - statement: "Tauri plugins registered in lib.rs's builder chain are: tauri-plugin-single-instance, tauri-plugin-deep-link, tauri-plugin-notification, tauri-plugin-opener, a push-to-talk global-shortcut plugin installed via ptt_shortcut::install, a custom native_websocket plugin, tauri-plugin-dialog, tauri-plugin-process, and (release builds only) tauri-plugin-updater; the app also registers a custom `buzz-media:` asynchronous URI scheme handler backed by media_proxy::handle_buzz_media."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs"
  - statement: "Root-of-trust key storage is one of four states tracked by an explicit IdentityStorage enum (identity_storage.rs, secret_store.rs, app_state_keyring.rs), defaulting to the OS keyring/Secret Service via the `keyring` crate under the `system-keyring` Cargo feature, which is the crate's only feature enabled by default."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/identity_storage.rs"
      - "desktop/src-tauri/src/secret_store.rs"
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The crate's test convention is a sibling `_tests.rs` file wired in via `#[cfg(test)] #[path = \"..._tests.rs\"] mod ..._tests;` next to the module it tests (verified directly on app_state.rs -> app_state_tests.rs), and this pattern recurs across dozens of modules (agents_tests.rs, channels_tests.rs, discovery/tests.rs, runtime/tests.rs, and others named in the module listing read for this node)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs"
  - statement: "just desktop-tauri-test runs `cd desktop/src-tauri && cargo test --workspace` (desktop/src-tauri's own nested [workspace], whose only member is crates/buzz-terminal) after an `_ensure-sidecar-stubs` dependency that creates placeholder externalBin files; just desktop-tauri-check and just desktop-tauri-clippy run `cargo check`/`cargo clippy --manifest-path desktop/src-tauri/Cargo.toml` respectively; all three run inside `just desktop-ci`, which itself runs inside the root `just ci`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Issue #948's Definition of Done requires that this node state implementation responsibility and what it deliberately does not own, name public interfaces/entry points and important dependencies, and link owned source paths and representative tests without restating domain semantics already canonical in architecture-containers-desktop."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#948 (issue body, Definition of Done section)"
  - statement: "A sibling batch task documents desktop/src/ (the React frontend) as implementation/desktop/frontend.md; this node's dispatch instructions direct it to cover desktop/src-tauri/ (the Rust backend) instead, to avoid the two nodes duplicating each other's territory."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "this task's own dispatch instructions (issue #948 batch context, not yet merged as a corpus node at the recorded revision)"
  - statement: "No `implements` relationship is declared toward any ADR because no accepted decision record specifically governs this crate's own IPC/module shape, and no ADR in launchpad/decisions/ (searched by filename for desktop/tauri/agent/ipc) is itself a corpus node yet -- an implements edge to a non-corpus-node id is a hard validation error per this corpus's own schema and AGENTS.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
relationships:
  - type: part-of
    target: architecture-containers-desktop
---

# Desktop Tauri backend: implementation reference

This node documents `desktop/src-tauri/` -- the Rust crate (package
`buzz-desktop`, lib name `buzz_lib`) that is Buzz's Tauri 2 desktop backend --
as the concrete realization of the technology and interface boundary that
`architecture-containers-desktop` already describes at the architecture
level. That node states the boundary (a Rust backend, IPC-only from its own
frontend, statically-linked Buzz crates, a set of native integrations) and
explicitly declines to restate implementation detail; this node supplies
that detail: the actual module tree, the IPC command surface the frontend
calls, and the concrete shape of the native integrations named there.

## Target

The target is `architecture-containers-desktop`'s own *Technology and
ownership boundary* and *Inbound and outbound interfaces* sections --
specifically its claims that the backend is excluded from the root Cargo
workspace, statically links `buzz-core`, `buzz-persona`, `buzz-sdk`,
`buzz-agent` and `buzz-voice`, and exposes Tauri IPC commands plus a set of
native integrations (keyring-backed identity storage, a managed-agent
subprocess supervisor, a localhost media proxy, deep links, an embedded PTY
terminal). No ADR, NIP or other decision record in `launchpad/decisions/`
specifically governs this crate's own command/module shape (checked by
filename for `desktop`/`tauri`/`agent`/`ipc`), and none of the two closest
candidates found (`ADR-0037-sync-agent-replay-only.md`,
`ADR-0041-pin-main-to-relay-desktop-tags.md`) is itself a corpus node yet --
so this node declares `part-of` toward `architecture-containers-desktop`
rather than an `implements` edge toward a spec that has no id to point at.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `desktop/src-tauri/Cargo.toml` (`exclude` in root `Cargo.toml`) | `architecture-containers-desktop`'s workspace-exclusion claim | Root workspace `exclude = ["desktop/src-tauri"]`; tested via `cargo test --manifest-path`/`cd`-scoped invocation, never root `cargo test --workspace`. |
| `src/lib.rs` `invoke_handler!(tauri::generate_handler![...])` | The IPC command surface `architecture-containers-desktop` names as "Local IPC from its own webview only" | ~336-337 registered commands in the default build; 348 raw `#[tauri::command]` attributes across 92 files, the gap explained by mesh-llm feature/stub command pairs. |
| `src/commands/` (65 files: `agent_*`, `channels`, `messages`, `personas`, `teams`, `project_git_*`, `media_*`, `identity`, `pairing`, `workflows`, `canvas`, `social`, `dms`, `updater`, `window_*`, `workspace`, `notifications`) | The bulk of the frontend-facing command surface | Grouped by domain; see `src/commands/mod.rs` for the authoritative module list. |
| `src/huddle/` (voice channel: session state, STT/TTS pipeline, audio I/O) | The `buzz-voice` outbound integration `architecture-containers-desktop` gestures at but leaves undetailed | ~37 `#[tauri::command]` attributes; the module's own audio-pipeline internals are out of scope here (see *Scope and omissions*). |
| `src/managed_agents/discovery.rs` + `discovery/` submodule | Locating installed AI-agent CLIs on the host (Claude Code, Codex, Goose, buzz-agent presets) | Login-shell probing, nvm-aware PATH search, dedicated Windows install detection. |
| `src/managed_agents/runtime.rs` + `runtime/` submodule | Managed-agent subprocess lifecycle: env build, spawn, track, stop, orphan-sweep | The concrete mechanism behind `architecture-containers-desktop`'s per-agent-`BUZZ_PRIVATE_KEY` claim. |
| `src/managed_agents/backend.rs` | The subprocess protocol the bundled `buzz-backend-kubernetes` externalBin is driven through | Versioned (`protocol_version: 1`) JSON-over-stdio handshake, capped stdout/stderr. Not a Cargo path dependency -- a separate compiled binary. |
| `src/commands/project_git_exec.rs` | Local git operations against project repos in the "nest" | Runs system `git` as a subprocess; nsec handed to `git-credential-nostr` via env only, never written to disk or global git config; 60s local / 300s remote timeout. |
| `src/identity_storage.rs`, `src/secret_store.rs`, `src/app_state_keyring.rs` | `architecture-containers-desktop`'s "durably persisted through one of four backends" claim | Default: OS keyring/Secret Service via the `keyring` crate, gated by the crate's only default-on feature, `system-keyring`. |
| `src/deep_link.rs` | The `buzz://` OS deep-link scheme, registered via `tauri-plugin-deep-link` | Community/entity/navigation deep-link targets. |
| `src/commands/updater.rs`, `tauri-plugin-updater` registration in `lib.rs` | Auto-update support | Registered only in non-debug builds behind a `buzz_updater_enabled` cfg; further gated on Linux by the `APPIMAGE` env var (AppImage-only updatability). |
| `src/terminal_runtime.rs`, `src/terminal_transport.rs`, nested `crates/buzz-terminal` | The embedded PTY terminal `architecture-containers-desktop` names | `buzz-terminal` is a member of `desktop/src-tauri`'s own nested `[workspace]`, not the repo root workspace. |
| `buzz_core_pkg`, `buzz_sdk_pkg`, `buzz_voice_pkg`, `buzz_persona_pkg`, `buzz_agent_pkg`, `buzz_ws_client_pkg` path dependencies | The five-plus-one statically-linked crate claim | Usage is uneven: `buzz-core` (55 files) and `buzz-sdk` (17 files) are pervasive; `buzz-voice` (2 files, huddle only), `buzz-persona` (1 file, migration only) and `buzz-agent` (4 files, shared types/errors only, never turn execution) are narrow; `buzz-ws-client` (1 file, `native_relay_client.rs`) backs the app's own NIP-42 relay connection. |

## Divergences

- **The task brief that produced this node's dispatch names `buzz-relay-mesh`
  as "the Kubernetes backend."** Checked directly: `buzz-relay-mesh`'s own
  `Cargo.toml` describes it as inter-relay QUIC mesh transport/membership, it
  is a relay-side crate, and it is referenced nowhere under
  `desktop/src-tauri/` (zero grep matches). The crate actually bundled and
  spawned as the desktop app's Kubernetes compute backend is
  `buzz-backend-kubernetes`. `managed_agents/relay_mesh.rs`'s
  `RELAY_MESH_*` symbols are unrelated to either crate -- they are wire-format
  glue for the opt-in `mesh-llm` shared-compute Cargo feature, and the name
  collision with the `buzz-relay-mesh` crate is coincidental. This node
  reports the verified pairing rather than the brief's premise.
- **`buzz-agent` is a compile-time dependency for shared types only, not for
  running agent turns.** The desktop backend links `buzz_agent_pkg` in four
  files, all for config/error types (`WINDOWS_SHELL_RESOLUTION_ENV`,
  `DatabricksModelFilter`, `Provider`, `AgentError`). The `buzz-agent` a
  managed session actually runs is the separately compiled `binaries/buzz-agent`
  externalBin, spawned as its own OS process by `managed_agents/runtime.rs` --
  the linked crate and the spawned binary are the same source, built two
  different ways, and neither is a shortcut for the other.
- **No divergence was found between `architecture-containers-desktop`'s
  claims and the code checked for this node.** Its workspace-exclusion,
  static-linkage, keyring-default, and deep-link claims were each re-checked
  against the same or adjacent source files this node cites, and held.

## Verification

- `just desktop-tauri-check` (`cargo check --manifest-path
  desktop/src-tauri/Cargo.toml`) and `just desktop-tauri-clippy` (`cargo
  clippy --manifest-path desktop/src-tauri/Cargo.toml --workspace --all-targets
  -- -D warnings`) gate compilation and lint.
- `just desktop-tauri-test` runs `cd desktop/src-tauri && cargo test
  --workspace` (that nested workspace's only member is `crates/buzz-terminal`)
  after `_ensure-sidecar-stubs` creates placeholder externalBin files so the
  build has something to bundle. All three run inside `just desktop-ci`,
  itself part of the root `just ci` gate.
- Per-module tests live in sibling `_tests.rs` files wired in with
  `#[cfg(test)] #[path = "..."]`, verified directly on
  `app_state.rs`/`app_state_tests.rs` and recurring across dozens of modules
  (`commands/agents_tests.rs`, `managed_agents/discovery/tests.rs`,
  `managed_agents/runtime/tests.rs`, and others visible in the module
  listing read for this node).
- A separate, explicitly non-shared-CI gate,
  `just desktop-terminal-performance-test`, runs a wall-clock latency
  assertion on the embedded terminal renderer; the `Justfile` states it is
  excluded from shared CI because scheduler contention makes the assertion
  flaky.

## Relationships

- part-of: `architecture-containers-desktop` -- the desktop container this
  crate is the backend half of.
- No `implements` edge: no ADR/NIP/decision record specifically governing
  this crate's own shape has a corpus node id yet (see *Target* above).
- No `references` edge to a verification/test-strategy node: none exists in
  the merged corpus at this node's recorded revision.

## Scope and omissions

**This node covers** `desktop/src-tauri/`'s implementation surface: its
workspace/build boundary, its statically-linked crate dependencies, its
IPC command-family breakdown, and the concrete shape of the native
integrations (secure key storage, managed-agent process supervision, agent
CLI discovery, the git subprocess helper, the Kubernetes-backend subprocess
protocol, deep links, the auto-updater, the embedded PTY terminal) that
`architecture-containers-desktop` names but does not itself detail.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `desktop/src/` -- the React 19 + Vite frontend | A sibling corpus task (`implementation/desktop/frontend.md`), by this task's own dispatch instructions |
| `buzz-core`, `buzz-sdk`, `buzz-voice`, `buzz-persona`, `buzz-agent`, `buzz-ws-client`, `buzz-backend-kubernetes` internal implementations | Each crate's own implementation-reference node, not yet authored |
| The huddle audio pipeline's internal protocol/codec design (jitter buffer, STT/TTS model selection, wire format) | Only its existence as ~37 commands under `src/huddle/` is claimed here; `architecture-containers-desktop` already states the same boundary |
| The `mesh-llm` Cargo feature's peer-to-peer network protocol and trust model | `architecture-containers-desktop`'s own *Scope and omissions*; not re-verified here beyond confirming it is off by default |
| Exhaustive per-command documentation (each of the ~336 registered commands' exact signature/behavior) | Out of scope for a corpus node at this altitude; `src/commands/mod.rs` and the individual command files are the source of truth |
| Front-end-side IPC call sites (which React feature invokes which command) | The sibling frontend node |

**Expected but not verified when this node was written:**

- **The exact registered-command count was not obtained by compiling and
  introspecting the running app** -- it is a static count of
  `#[tauri::command]` attributes and a manual reconciliation against the
  `generate_handler!` macro body's comma count, not a runtime enumeration.
  The reconciliation (348 attributes, ~336-337 registered, gap explained by
  6 mesh-llm command/stub pairs) is arithmetic, not executed verification.
- **Whether every one of the 92 command-bearing files was individually
  opened is false** -- this node read the module tree exhaustively
  (`find ... -name "*.rs"`), `commands/mod.rs`'s full re-export list, and a
  representative, deliberately-named subset (`project_git_exec.rs`,
  `managed_agents/runtime.rs`, `managed_agents/discovery.rs`,
  `managed_agents/backend.rs`, `updater.rs`, `identity_storage.rs`,
  `secret_store.rs`, `deep_link.rs`, `terminal_runtime.rs`,
  `native_relay_client.rs`), plus grep-based confirmation of crate-linkage
  claims across the full tree. Claims about specific files cite only files
  actually opened; the family-level table rows for files not individually
  opened are scoped to what `commands/mod.rs`'s module list and directory
  structure alone support.
- **The Windows-specific and Linux-specific native integration code paths
  (`windows_install.rs`, `webkit2gtk`/`linux_media.rs`,
  `macos_notifications.rs`) were read for their existence and stated purpose
  from source, not exercised on their target platforms** -- this node was
  authored on Linux without cross-platform runtime verification.
