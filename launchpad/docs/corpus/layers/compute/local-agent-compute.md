---
id: layers-compute-local-agent-compute
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "A managed agent record carries a `backend` field of type `BackendKind`, a two-variant enum: `Local` (the default) or `Provider { id: String, config: serde_json::Value }`; this is the discriminator that decides whether an agent's compute is local or remote."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/types.rs"
  - statement: "`spawn_agent_child` (desktop/src-tauri/src/managed_agents/runtime.rs) is the function that actually performs a local spawn: it refuses via `spawn_key_refusal` if the agent's private key is empty, resolves the effective harness command/args/env via `resolve_effective_harness_descriptor`, builds a `std::process::Command` for the resolved ACP harness binary, sets on it the full layered environment (identity, relay URL, respond-to gate, model/provider, team instructions, user env), and calls `command.spawn()` to launch the harness as a native OS child process of the desktop app."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs"
  - statement: "`spawn_key_refusal` (desktop/src-tauri/src/managed_agents/storage.rs) returns an error whenever `record.private_key_nsec` is empty, and its doc comment states this enforces fail-closed behavior because an empty key would otherwise be spawned with no identity (a keyring outage or genuinely absent secret, not a deliberately keyless agent); `spawn_agent_child` calls it first, before any side effect (log marker, log file, process spawn), so a refused local spawn leaves no trace."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/storage.rs"
  - statement: "The Tauri command path that starts or stops a tracked local runtime pair (`start_pair` in desktop/src-tauri/src/managed_agents/runtime_commands.rs) explicitly refuses to operate on any agent record whose `backend` is not `BackendKind::Local`, returning the error \"managed runtime pairs require a local agent\" — so this local process-lifecycle machinery only ever governs `Local`-backend agents, never `Provider`-backend ones."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime_commands.rs"
  - statement: "Desktop's launch-restore logic (desktop/src-tauri/src/managed_agents/restore.rs), which re-spawns agents configured to start when the app launches, filters its candidate set to `record.start_on_app_launch && record.backend == BackendKind::Local` and calls `spawn_agent_child` with `lazy: true` for each — so app-launch auto-restart only ever restarts local agents; a `Provider`-backend agent is never auto-respawned by the desktop process itself."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/restore.rs"
  - statement: "`desktop/src-tauri/src/managed_agents/runtime/orphan_sweep.rs` and `runtime/instance_reaper.rs` implement local-only process supervision: they read on-disk PID files and runtime receipts, verify a candidate process is Buzz-owned and belongs to the current desktop instance by checking the `BUZZ_MANAGED_AGENT` environment variable stamped on it at spawn time (against a list of known desktop binary names such as `Buzz`, `buzz-desktop`, `buzz_desktop`), and terminate processes that are orphaned or whose owning desktop instance is confirmed dead. There is no substrate-side equivalent for this mechanism — it only exists because a local agent is a real child process on the same machine the desktop can inspect."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime/orphan_sweep.rs"
      - "desktop/src-tauri/src/managed_agents/runtime/instance_reaper.rs"
  - statement: "`spawn_agent_child` stamps every spawned local process with `BUZZ_MANAGED_AGENT` (set to `current_instance_id(app)`) and `BUZZ_MANAGED_AGENT_START_NONCE` (a fresh UUID per spawn attempt) as environment variables, immediately before `command.spawn()` is called; these are the markers `orphan_sweep`/`instance_reaper` read back to identify a process as a local, desktop-owned agent."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs"
  - statement: "To stop a local agent, `stop_managed_agent_pair` (desktop/src-tauri/src/managed_agents/runtime/stop.rs) calls `terminate_process` directly on the tracked child's PID/process group — the desktop kills the OS process itself. This is a direct management channel that only exists for local compute; docs/remote-agents.md states explicitly (§Stop and Delete, and axiom M1 in its System Model section) that Stop is *not* a provider operation for a remote agent — the desktop instead publishes a relay `!shutdown` message and has no persistent management channel to a remotely-run agent at all."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime/stop.rs"
      - "docs/remote-agents.md"
  - statement: "`desktop/src-tauri/src/managed_agents/reserved_env_keys.rs` defines `RESERVED_ENV_KEYS`, a list of environment variable names (identity/secret keys such as `BUZZ_PRIVATE_KEY`, `NOSTR_PRIVATE_KEY`, `BUZZ_AUTH_TAG`; code-execution-surface keys such as `BUZZ_ACP_AGENT_COMMAND`/`BUZZ_ACP_AGENT_ARGS`; control-plane and security-gate keys such as `BUZZ_ACP_AGENTS`, `BUZZ_ACP_RESPOND_TO`, `BUZZ_ACP_AGENT_OWNER`) that user-supplied per-persona or per-agent env overrides are rejected at save time and stripped at spawn time from ever setting, so a misconfigured or malicious custom env cannot redirect a local agent's identity, relay, or executable surface."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs"
  - statement: "docs/remote-agents.md's own Abstract states it specifies the protocol by which Buzz Desktop delegates execution to \"a remote substrate — any compute environment other than the local machine\", and its System Model section states plainly that Buzz Desktop is \"one launcher among many\": what makes a process a live Buzz agent is a keypair, a NIP-OA auth tag, and a relay URL handed as environment to the buzz-acp harness, and any launcher (a bash script, a systemd unit, this document's provider protocol) that can set that environment and exec the harness is conforming. Local compute is the specific case where the launcher is Buzz Desktop itself, spawning on its own machine, and is explicitly the case this specification's own scope excludes from its \"remote substrate\" definition."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's \"Launch data\" section states that a remote provider's deploy payload carries a `launch` block resolved by the desktop \"with the same code paths as local spawn\" (`resolve_effective_harness_descriptor`), and that this exists specifically so a provider is never required to reimplement desktop runtime discovery as a second, independently-drifting copy — meaning local spawn's env-resolution logic is the canonical implementation that the remote path reuses, not a parallel one."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's \"Documented consequence\" paragraph (under §Deploy State Machine) states that because a live remote instance is a strict no-op on redeploy, configuration edits to a running remote agent do not take effect until it next exits, \"unlike local agents, which re-resolve on every spawn\" — a local agent's effective config (model, provider, prompt, harness command/args, env) is therefore always current as of its most recent local spawn, with no analogous no-op window."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's Invariant I3 (\"Presence is the status\") states that the harness's presence-suppression knob `BUZZ_ACP_NO_PRESENCE` is cosmetic when a local agent uses it — \"the process and UI remain visible\" to the desktop that spawned it — precisely because, for local compute, the desktop already has a direct process handle and does not depend on relay presence the way it must for a remote agent under invariant M1's \"no management channel\" constraint."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "Sibling corpus documentation tasks exist, filed as their own GitHub issues, for the remote/provider side of agent compute this node explicitly excludes: #1046 (remote-agent-compute), #1041 (backend-provider), #1042 (kubernetes-provider), and #1049 (sprig-runtime, the multicall binary the Kubernetes provider deploys as a container image)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#611 (parent Feature/PRD, relayed via the corpus batch-run dispatch brief that assigned this node to issue #1045)"
relationships:
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-containers-agent-runtime
---

# Concept: Local agent compute

Buzz Desktop can run an AI agent's harness process on the very same machine
the desktop app itself runs on. This document names and scopes that
mechanism — **local agent compute** — as distinct from the sibling
mechanisms that run an agent's harness somewhere else. It documents the
concept as it exists in the codebase today; the deeper provider protocol
that governs the remote alternative is `docs/remote-agents.md`'s own subject,
not restated here.

## Definition

**Local agent compute is the mode in which Buzz Desktop itself launches,
configures, and supervises a managed agent's `buzz-acp` harness process as a
native OS subprocess on the desktop's own machine**, using
`std::process::Command` directly rather than delegating to an external
provider binary. It is one of exactly two values a managed agent record's
`backend` field (`BackendKind`) can take — `Local` (the default) or
`Provider { id, config }` — and the two are mutually exclusive per agent
record: an agent is either run locally by the desktop process, or deployed
to a remote substrate through a `buzz-backend-<id>` provider binary, never
both at once for the same record.

What the term does **not** mean: it is not a claim about where the *desktop
app* runs (the desktop is always local to the human operating it); it is a
claim about where the *agent's harness process* runs, relative to the
desktop that manages it.

## How it works

```mermaid
flowchart TD
    A["Desktop: start_pair /\nrestore.rs launch-restore"] -->|"backend == BackendKind::Local\n(else refused)"| B["spawn_key_refusal\n(empty nsec -> fail closed)"]
    B -->|key present| C["resolve_effective_harness_descriptor\n(command, args, layered env)"]
    C --> D["std::process::Command\n+ identity/relay/gate env\n+ BUZZ_MANAGED_AGENT marker"]
    D --> E["command.spawn()\nbuzz-acp harness child process"]
    E --> F["orphan_sweep / instance_reaper\n(BUZZ_MANAGED_AGENT-based\nownership checks)"]
    E --> G["stop_managed_agent_pair\nterminate_process (direct kill)"]
```

The desktop-side entry point is `spawn_agent_child`
(`desktop/src-tauri/src/managed_agents/runtime.rs`). It first calls
`spawn_key_refusal` to fail closed if the agent's private key is
unavailable, then resolves the effective harness command, arguments, and
fully-layered environment through `resolve_effective_harness_descriptor`,
builds a `std::process::Command` for the resolved ACP harness binary, sets
the layered environment on it (identity, relay URL, respond-to gate,
model/provider, team instructions, then user-supplied env last so it can win
where it is not reserved), stamps `BUZZ_MANAGED_AGENT` and
`BUZZ_MANAGED_AGENT_START_NONCE`, and calls `command.spawn()`. The result is
tracked by the desktop's own runtime-process table for the lifetime of the
app.

Only agents whose `backend` is `BackendKind::Local` pass through this path
at all: `start_pair` (the Tauri command backing manual start/stop) refuses
any record whose backend is not `Local`, and launch-restore on app start
filters its candidate set the same way. A `Provider`-backend record is never
handled by `spawn_agent_child`, `orphan_sweep`, `instance_reaper`, or
`stop_managed_agent_pair` — those are local-compute-only machinery.

## Use cases

- **The default managed-agent experience.** Every managed agent record
  defaults to `BackendKind::Local`; a developer or operator creating an
  agent in Buzz Desktop is using local agent compute unless they explicitly
  configure a provider.
- **Understanding why a config edit applies immediately.** A user who edits
  a local agent's model, prompt, or harness command sees it take effect on
  the agent's *next spawn* — because `spawn_agent_child` re-resolves the
  full effective config every time it runs. This is the property
  `docs/remote-agents.md` calls out by contrast when describing why a live
  remote deploy is a no-op instead.
- **Diagnosing why a local agent process is missing or duplicated.**
  `orphan_sweep`/`instance_reaper`'s `BUZZ_MANAGED_AGENT`-marker logic is
  the mechanism that decides whether an on-disk PID/receipt still names a
  real, desktop-owned process — relevant when triaging "an agent shows
  stopped but a process is still running" or the reverse.
- **Understanding the security boundary of per-agent env overrides.** A
  developer configuring per-agent or per-persona environment variables needs
  to know that `RESERVED_ENV_KEYS` blocks identity, relay, and
  code-execution-surface keys regardless — the same reserved-key strip
  documented here also protects the local spawn path, not only the remote
  one.

## Comparison: local vs. remote (provider) compute

| Aspect | Local agent compute | Remote/provider compute (`docs/remote-agents.md`) |
|---|---|---|
| Launcher | Buzz Desktop itself, via `std::process::Command` | A `buzz-backend-<id>` provider binary, invoked by Desktop |
| Management channel | Desktop holds a direct OS process handle | None after deploy (invariant M1) — relay presence only |
| Stop | Desktop calls `terminate_process` directly | Desktop publishes a relay `!shutdown` message |
| Config edits | Re-resolved on every spawn (immediate on restart) | No-op against a live instance until it next exits |
| Auto-restart on app launch | Yes, for `start_on_app_launch` records (`restore.rs`) | No — desktop-side launch-restore filters to `Local` only |
| Orphan/liveness detection | `BUZZ_MANAGED_AGENT` env-marker scan of local processes | Relay presence events (kind:20001), bounded to ~180s staleness |
| Identity fail-closed enforcement | `spawn_key_refusal` before any side effect | `build_deploy_payload`'s equivalent refusal (per `docs/remote-agents.md`'s I1) |

This table is scoped to what a reader of *this* node needs to place local
compute against its sibling; the remote side's full protocol (five
invariants, provider discovery, the deploy state machine) is
`docs/remote-agents.md`'s own subject and #1046's document, not restated
here beyond what this comparison needs.

## Scope and omissions

**This node covers** the definition of local agent compute, the concrete
desktop-side mechanism that implements it (`spawn_agent_child` and the
functions that gate access to it), the local-only process-supervision
machinery (`orphan_sweep`, `instance_reaper`, direct `terminate_process`
stop), and how it differs from remote/provider compute at the level a reader
needs to tell the two apart.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The provider protocol (discovery, `info`/`deploy` operations, payload schema, the five invariants) | #1046 (remote-agent-compute), `docs/remote-agents.md` |
| The generic backend-provider contract from the provider-author's side | #1041 (backend-provider) |
| The Kubernetes binding of that protocol (`buzz-backend-kubernetes`) | #1042 (kubernetes-provider) |
| The `sprig` multicall runtime that both a local spawn's resolved harness binary and the Kubernetes provider's container image can be | #1049 (sprig-runtime) |
| The `buzz-acp` harness's own internal behavior once spawned (ACP protocol, agent pool, presence publication) — unchanged by whether the launch was local or remote | `architecture-containers-agent-runtime` (existing corpus node, linked below) |
| The desktop app's full architecture beyond the local-spawn slice of `managed_agents/` | `architecture-containers-desktop` (existing corpus node, linked below) |
| The full env-var layering precedence order (baked defaults, runtime metadata, definition, global, persona, agent) in detail | `desktop/src-tauri/src/managed_agents/agent_env.rs`, `env_vars.rs` — read for this node's spawn-time claims but not exhaustively catalogued here |

**Expected but not verified when this node was written:**

- **Whether every desktop UI surface that creates a managed agent defaults
  the `backend` field to `Local` explicitly, versus relying on
  `BackendKind`'s `#[default]` derive.** The Rust-side default was verified
  directly; the frontend code paths that construct new agent records were
  not read for this node.
- **The exact precedence and interaction of the six-layer env resolution**
  (`resolve_effective_harness_descriptor`) beyond confirming that user env is
  written last among the layers this node cites — a full walk of
  `agent_env.rs`'s layering order was not performed here, since
  `docs/remote-agents.md` already documents it in depth for the shared
  resolver both paths use.
- **Whether any launcher other than Buzz Desktop currently spawns a local
  Buzz agent in practice** (`docs/remote-agents.md`'s "one launcher among
  many" framing is a protocol-level claim, not a claim that a second
  launcher exists in this repository today) — no second local launcher was
  found or looked for beyond Desktop's own `managed_agents/` module.
