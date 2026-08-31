---
id: platforms-desktop-local-agent-management
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "node.schema.json's type enum includes platforms as one of its thirteen members, and this node's own path (launchpad/docs/corpus/platforms/desktop/local-agent-management.md) matches that surface, mirroring the precedent already set by architecture/containers/desktop.md carrying type: architecture."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "At the recorded revision no per-type template exists for a platforms-surface node (launchpad/docs/corpus/templates/ has no platforms-*.md file), so this node is hand-authored against node.schema.json, borrowing the already-merged component.md template's section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) because it is the closest structural fit to issue #1242's own Definition of Done, per AGENTS.md's documented no-template path."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "ManagedAgentRecord.backend is typed BackendKind, an enum with exactly two variants -- Local (the default, a unit variant) and Provider { id: String, config: serde_json::Value } -- and this is the code-level boundary this node uses to scope itself to Local, leaving Provider-backed (remote) agent management to a separate node."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/types.rs:6-13"
      - "desktop/src-tauri/src/managed_agents/types.rs:328"
  - statement: "desktop/src-tauri/src/managed_agents/backend.rs implements the Provider (remote) side of BackendKind: it discovers buzz-backend-<id> executables on PATH, stages an immutable copy of the resolved binary, and speaks a stdin/stdout JSON protocol (info, then deploy) to hand the agent's definition to an external provider process such as a Kubernetes-backed backend -- a materially different code path from spawning and directly supervising a local subprocess."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:509-533"
      - "desktop/src-tauri/src/managed_agents/backend.rs:593-677"
  - statement: "runtime.rs::spawn_agent_child is the sole local-spawn entry point: it resolves the effective harness descriptor (command, args, layered env) via resolve_effective_harness_descriptor, builds a std::process::Command for the resolved ACP harness binary, and sets its working directory to default_agent_workdir()."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs:142-235"
      - "desktop/src-tauri/src/managed_agents/runtime.rs:267-270"
  - statement: "spawn_agent_child injects the spawned agent's own nsec into the child's BUZZ_PRIVATE_KEY environment variable and the resolved relay URL into BUZZ_RELAY_URL, giving each local agent its own signing identity distinct from the desktop owner's."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs:278-279"
  - statement: "A guard at runtime.rs:569 checks record.backend == BackendKind::Local before applying the ANTHROPIC_MODEL startup-authority env write for local Claude agents, confirming spawn_agent_child's own code distinguishes local from provider-backed records mid-function rather than being local-only by convention alone."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs:569-572"
  - statement: "RESERVED_ENV_KEYS (reserved_env_keys.rs) is a fixed list of env var keys -- identity/secret keys (BUZZ_PRIVATE_KEY, NOSTR_PRIVATE_KEY, BUZZ_AUTH_TAG, BUZZ_API_TOKEN, BUZZ_ACP_PRIVATE_KEY, BUZZ_ACP_API_TOKEN), code-execution surface (BUZZ_ACP_AGENT_COMMAND, BUZZ_ACP_AGENT_ARGS, BUZZ_ACP_MCP_COMMAND), and security-gate/ownership-marker keys (BUZZ_ACP_RESPOND_TO and its allowlist forms, BUZZ_RELAY_URL, BUZZ_ACP_AGENTS, BUZZ_ACP_SETUP_PAYLOAD, BUZZ_MANAGED_AGENT, BUZZ_MANAGED_AGENT_START_NONCE, among others) -- that a persona or per-agent env_vars configuration must never be able to override."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs:28-76"
  - statement: "Reserved-key enforcement is defense-in-depth across two independent points: env_vars.rs's save-time validator rejects a reserved key outright when a persona/agent record is saved, and env_vars.rs::merged_user_env silently strips any reserved key at spawn time (logging that it did so), so an older on-disk record saved before the validator existed still cannot smuggle a reserved key into a spawned process's environment."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/env_vars.rs:137-149"
      - "desktop/src-tauri/src/managed_agents/env_vars.rs:220-239"
  - statement: "Local agents are persisted to a JSON file (managed-agents.json) inside the Tauri app-data directory's agents/ subfolder, resolved by managed_agents_base_dir/managed_agents_store_path in storage.rs; each agent's nsec is kept out of that JSON file when a system keyring is available and is re-hydrated from the keyring on load, per ManagedAgentRecord.private_key_nsec's own field documentation."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/storage.rs:35-47"
      - "desktop/src-tauri/src/managed_agents/types.rs:232-242"
  - statement: "Cross-platform process-tree teardown for a spawned local agent uses two different OS mechanisms: on Windows, process_lifecycle.rs (compiled only under #[cfg(windows)], wired into managed_agents via mod.rs) assigns the spawned child to a Win32 Job Object with JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE so the whole descendant tree dies when the job handle drops (finish_spawn/create_job_for_child), with taskkill_tree as the after-restart fallback when no job handle survived; on Unix the equivalent mechanism is a process group plus group signals in runtime.rs, outside this Windows-only file."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/process_lifecycle.rs:17-105"
      - "desktop/src-tauri/src/managed_agents/process_lifecycle.rs:161-207"
      - "desktop/src-tauri/src/managed_agents/mod.rs:27-28"
  - statement: "A local agent's ownership is verified by process name/marker rather than trusted by PID alone: process.rs's KNOWN_AGENT_BINARIES lists the binary name fragments Buzz may spawn (buzz-acp, buzz-agent, claude-agent-acp, codex-acp, goose, buzz-dev-mcp, in both hyphenated and underscored spellings), and process_belongs_to_us reads the OS process name (proc_name on macOS, /proc/<pid>/comm with an /proc/<pid>/exe fallback on other Unix) to match against that list before a stale-process check is allowed to treat a PID as one of Buzz's own -- closing the PID-reuse hazard where an old, tracked PID has since been recycled by an unrelated process."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime/process.rs:8-25"
      - "desktop/src-tauri/src/managed_agents/runtime/process.rs:71-119"
  - statement: "kill_stale_tracked_processes_with (runtime/lifecycle.rs) only acts on records whose backend is BackendKind::Local, and additionally requires the found PID to carry the BUZZ_MANAGED_AGENT marker (via process_has_buzz_marker) before killing it, terminating and clearing runtime_pid only for a local record whose PID is alive but not present in the current in-memory runtimes map -- i.e. a leftover from a previous desktop session."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime/lifecycle.rs:22-52"
  - statement: "sync_managed_agent_processes (runtime/lifecycle.rs) polls every tracked local runtime's child via try_wait, and on exit records last_stopped_at, last_exit_code, and a best-effort last_error/last_error_code parsed from the agent's own log file, then removes the exited pair from the in-memory runtimes map."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime/lifecycle.rs:54-125"
  - statement: "restore.rs restores previously-persisted local agents at desktop launch: backfill_persona_snapshots (called first) backfills a missing persona snapshot on pre-existing records, and restore_managed_agents_on_launch then runs a two-phase restore -- a locked Phase A that collects the agents to start, followed by a Phase B that resolves commands and spawns them -- while reconcile.rs separately reconciles managed-agents.json against the local retention store into kind:30177 events at boot, so a hand-edited or previously-unpublished record is republished without a live file watcher."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/restore.rs:42-72"
      - "desktop/src-tauri/src/managed_agents/restore.rs:94-105"
      - "desktop/src-tauri/src/managed_agents/reconcile.rs:1-55"
  - statement: "desktop/src-tauri/src/lib.rs calls managed_agents::resolve_repos_at_boot before restoring agents at app setup, and only proceeds with agent restore this launch if that check succeeds, per an inline comment explaining that restoring agents before the REPOS symlink is resolved could let an agent clone into the wrong directory."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:388-392"
  - statement: "The managed_agents module statically depends on the nostr crate (0.44, with nip44/nip49 features) for signing/parsing the kind:30177 identity events built in agent_events.rs and consumed by reconcile.rs, on rusqlite (0.37, bundled) for the local retention SQLite store opened by reconcile.rs's open_retention_db, and on tauri (2, with the app's own default feature set) for AppHandle/AppState and the Tauri command surface in runtime_commands.rs -- all compiled directly into the buzz_lib desktop binary, per Cargo.toml, not called as separate services."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:96"
      - "desktop/src-tauri/Cargo.toml:141"
      - "desktop/src-tauri/Cargo.toml:74"
  - statement: "architecture-containers-desktop already exists on origin/launchpad's corpus tree at the recorded revision and its Implementation paths section already names desktop/src-tauri/src/managed_agents/ (runtime.rs, reserved_env_keys.rs, agent_env.rs, storage.rs) as part of the desktop container's outbound surface, supporting a part-of relationship from this node to that container-level node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
relationships:
  - type: part-of
    target: architecture-containers-desktop
---

# Component: Desktop local agent management

This node documents **local agent management** in the Buzz desktop app: how
the desktop process spawns, supervises, persists and restores AI agent (ACP
harness) subprocesses running **on the same machine as the desktop app
itself**. It answers the question "what does the desktop do to run and keep
alive an agent process it fully owns?" — as distinct from handing an agent's
deployment off to an external, possibly remote, provider process.

## Responsibility

The code's own `BackendKind` enum is the authoritative boundary this node
scopes itself to: `Local` (the default, a unit variant with no further data)
versus `Provider { id, config }`. A `Local` agent is a subprocess the desktop
spawns directly with `std::process::Command`, supervises via its own
`Child` handle, and tears down itself; a `Provider` agent is handed off to an
externally discovered `buzz-backend-<id>` binary over a JSON stdin/stdout
protocol (`backend.rs`), which is a materially different code path and is
this node's sibling task (#1247), not its subject.

Within the `Local` scope, `desktop/src-tauri/src/managed_agents/` is
responsible for:

- **Spawning** a local agent's ACP harness process with the correct
  resolved command, arguments and layered environment
  (`runtime.rs::spawn_agent_child`).
- **Enforcing security-sensitive env boundaries** so a saved persona/agent
  configuration cannot override identity, code-execution or gate-critical
  variables (`reserved_env_keys.rs`, `env_vars.rs`).
- **Supervising** the spawned process tree cross-platform, including exit
  detection and stale/orphaned-process cleanup
  (`runtime/lifecycle.rs`, `runtime/process.rs`, `runtime/orphan_sweep.rs`,
  `process_lifecycle.rs` on Windows).
- **Persisting** agent records and their secrets locally
  (`storage.rs`), and **restoring/reconciling** them at desktop launch
  (`restore.rs`, `reconcile.rs`).

## Local spawn and env interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `spawn_agent_child` | fn (`runtime.rs`) | Sole local-spawn entry point: resolves the effective harness descriptor, builds and spawns the `std::process::Command`, returns a `ManagedAgentProcess` (or refuses per `require_resolved()` for an orphaned/unresolved record). | `desktop/src-tauri/src/managed_agents/runtime.rs:142-235` |
| `RESERVED_ENV_KEYS` / `is_reserved_env_key` | const + fn (`reserved_env_keys.rs`) | Identity, code-execution and security-gate env keys that user-supplied persona/agent `env_vars` can never set. | `desktop/src-tauri/src/managed_agents/reserved_env_keys.rs:28-82` |
| `merged_user_env` | fn (`env_vars.rs`) | Spawn-time defense-in-depth filter: silently strips any reserved key surviving from an older on-disk record. | `desktop/src-tauri/src/managed_agents/env_vars.rs:220-239` |
| `sync_managed_agent_processes` | fn (`runtime/lifecycle.rs`) | Polls every tracked local child, records exit code/error, drops it from the in-memory runtime map. | `desktop/src-tauri/src/managed_agents/runtime/lifecycle.rs:54-125` |
| `kill_stale_tracked_processes` | fn (`runtime/lifecycle.rs`) | Local-only (`backend == BackendKind::Local`); kills a previous-session PID still alive but untracked, gated on the `BUZZ_MANAGED_AGENT` process marker. | `desktop/src-tauri/src/managed_agents/runtime/lifecycle.rs:6-52` |
| `process_belongs_to_us` | fn (`runtime/process.rs`) | Confirms a PID's OS-reported process name matches a known agent binary before any stale-PID logic treats it as ours — the PID-reuse guard. | `desktop/src-tauri/src/managed_agents/runtime/process.rs:71-119` |
| `create_job_for_child` / `finish_spawn` / `taskkill_tree` | fns (`process_lifecycle.rs`, Windows-only) | Win32 Job Object process-tree teardown, the Windows counterpart to the Unix process-group teardown in `runtime.rs`. | `desktop/src-tauri/src/managed_agents/process_lifecycle.rs:17-207` |
| `managed_agents_base_dir` / `managed_agents_store_path` | fns (`storage.rs`) | Resolve the local `managed-agents.json` store under the Tauri app-data directory's `agents/` subfolder. | `desktop/src-tauri/src/managed_agents/storage.rs:35-47` |

## Dependencies

**Depends on** (this subsystem requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `tauri` (2, app default features) | `AppHandle`/`AppState` access, app-data-dir resolution, the Tauri command surface (`runtime_commands.rs`) local agent commands are exposed through. | `desktop/src-tauri/Cargo.toml:74` |
| `nostr` (0.44, `nip44`/`nip49`) | Signing the kind:30177 managed-agent identity events built in `agent_events.rs` and reconciled in `reconcile.rs`; deriving each agent's own keypair from its persisted nsec. | `desktop/src-tauri/Cargo.toml:96` |
| `rusqlite` (0.37, `bundled`) | The local retention SQLite store `reconcile.rs::open_retention_db` reads/writes for boot-time disk-to-relay reconciliation. | `desktop/src-tauri/Cargo.toml:141` |
| The bundled ACP harness binaries (`buzz-acp`, `buzz-agent`, and preset/custom runtimes such as `claude-agent-acp`, `codex-acp`, `goose`) | The actual local processes spawned; `spawn_agent_child` resolves and launches one of these per agent. | `desktop/src-tauri/src/managed_agents/runtime/process.rs:8-25` |

**Depended on by** (these require this subsystem):

| Component | Why | Evidence |
|---|---|---|
| `desktop/src-tauri/src/lib.rs` app-setup sequence | Calls `managed_agents::resolve_repos_at_boot` and restores local agents at launch, gated on that check succeeding. | `desktop/src-tauri/src/lib.rs:388-392` |
| `runtime_commands.rs` (Tauri command surface) | The frontend-facing commands (create/start/stop/update a managed agent) that call into `spawn_agent_child` and the lifecycle functions documented above; not separately verified for this node — see *Scope and omissions*. | `desktop/src-tauri/src/managed_agents/mod.rs:36` |

## Boundary

This node does not describe:

- **Remote/provider-backed agent management** (`BackendKind::Provider`, the
  `buzz-backend-<id>` discovery/staging/JSON-protocol machinery in
  `backend.rs`) — that is issue #1247's subject
  (`platforms/desktop/remote-agent-management.md`), a distinct code path
  with its own security model (staged-binary hashing, provider protocol
  negotiation) that this node does not duplicate.
- **The desktop container's other responsibilities** — identity-key
  storage, the media proxy, the embedded terminal, the relay connection
  itself — already covered by `architecture-containers-desktop`, this
  node's `part-of` target.
- **The internal behavior of a spawned harness once running** (`buzz-acp`,
  `buzz-agent`, and third-party ACP adapters) — those are their own
  components; this node covers only how the desktop launches and
  supervises them as OS processes, not their ACP protocol behavior.
- **Personas and teams as data models** (`personas.rs`, `teams.rs`,
  `team_catalog.rs`) beyond the one fact that they feed a spawn's effective
  configuration — their own lifecycle (creation, catalog sharing,
  team-import) is a separate concern from process spawn/supervision.

## Relationships

- `part-of`: `architecture-containers-desktop` — this subsystem is a
  constituent piece of the desktop container's outbound surface, which
  already names `desktop/src-tauri/src/managed_agents/` in its own
  Implementation paths.
- No `depends-on`/`references` edges are declared toward any other corpus
  node: at the recorded revision, `platforms/` has no other sibling node on
  `origin/launchpad` (checked via `git ls-tree -r --name-only
  origin/launchpad -- launchpad/docs/corpus`) and the sibling remote-agent
  task (#1247) is authored independently and unmerged, so it is not a valid
  target per `AGENTS.md`'s rule against pointing at nodes absent from the
  merge-target branch.

## Scope and omissions

**This node covers** how the Buzz desktop app spawns, secures, supervises,
persists and restores local (same-machine, `BackendKind::Local`) ACP-harness
agent subprocesses: the spawn entry point and its environment contract, the
reserved-env-key security gate, cross-platform process-tree supervision and
stale/orphan cleanup, local JSON persistence with keyring-backed secrets, and
boot-time restore/reconcile.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Remote/provider-backed agent management (`BackendKind::Provider`, `backend.rs`) | #1247 (`platforms/desktop/remote-agent-management.md`), sibling task, unmerged at time of writing |
| The desktop container as a whole (identity storage, media proxy, terminal, relay connection) | `architecture-containers-desktop` |
| The ACP protocol and spawned harness binaries' own internal behavior | Not yet a corpus node; out of this node's one-idea scope |
| Persona/team data-model lifecycle (creation, catalog sharing, team import) beyond their role as spawn-config inputs | Not yet a corpus node |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| A per-type template for `type: platforms` nodes | Not yet authored, per the gap `AGENTS.md` names at #1307-#1351; this node borrows `component.md`'s section shape in the meantime and says so above |

**Expected but not verified when this node was written:**

- **`runtime_commands.rs`'s Tauri command surface was not read in full.**
  It is named in *Dependencies* as a consumer of `spawn_agent_child` and the
  lifecycle functions, but its own command-by-command contract (request/
  response shapes, which commands exist) was not enumerated — only its
  existence and role as the frontend-facing entry point were confirmed via
  `mod.rs`'s module list.
- **The Unix side of process-tree teardown (process-group creation and
  group-signal delivery in `runtime.rs`) was not read line-by-line**, only
  referenced by contrast with the Windows `process_lifecycle.rs`
  mechanism this node does cite directly; the claim that Unix uses a
  process group is stated in `architecture-containers-desktop`'s own prior
  research and was not independently re-verified against `runtime.rs`'s
  Unix-specific code for this node.
- **`runtime/orphan_sweep.rs` and `runtime/stop.rs` were not read.** They
  are named in `mod.rs`'s module list as part of local supervision but
  their specific sweep/stop algorithms are not claimed here.
- **Whether every one of the reserved-env-key categories in
  `reserved_env_keys.rs` has a corresponding save-time AND spawn-time
  enforcement point was checked only for the general mechanism
  (`validate_user_env_keys`-style save rejection plus `merged_user_env`
  spawn-time stripping), not exhaustively per key.**
