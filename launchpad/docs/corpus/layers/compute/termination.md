---
id: layers-compute-termination
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
  - statement: "docs/remote-agents.md's invariant (I5), 'Intentional termination is final', states that a remote agent 'stops when told, stays down when it stops, and is never silently resurrected': an instance whose harness is live terminates on owner `!shutdown` or when a configured inactivity bound expires, and 'final' means terminal to automatic supervisor restart only -- the owner may always issue a fresh Start."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:243-249"
  - statement: "I5 states that lifetime is owner policy, not law: an owner may always choose no inactivity bound (an indefinitely-lived agent), expressed per-binding -- the Kubernetes binding's `inactivity_seconds: 0` is a legal, blessed value meaning 'no inactivity bound', not a misconfiguration -- and that the invariant was never 'every instance terminates' but 'termination, once intended, sticks'."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:251-262"
  - statement: "I5 states the distinction that makes indefinite agents safe as intent versus accident: 'if a supervisor exists, its restart policy MAY revive an abnormal death and MUST NOT revive an intentional clean exit', and that this precondition depends on a formal, test-pinned exit-code contract (intentional exit = code 0, abnormal otherwise) which at the document's own `28ae6cd21` pin is 'emergent, not defended' -- its own Known Defect 6."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:264-287"
  - statement: "docs/remote-agents.md's 'Stop and Delete' section states Stop is not a provider operation: the desktop publishes a relay message and the harness exits through its own graceful path (agent-pool shutdown, drain of in-flight turns, publish presence offline, close relay connection), and that the document deliberately does not state a single derived upper bound for that path because two earlier attempts to sum the visible segment timeouts were proven wrong by review -- the real tail is bounded by a declared per-binding grace budget with a reserved finalization slice instead, tracked as its own Known Defect 7."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:884-920"
  - statement: "The same section states Delete (removing a managed-agent record whose backend is not local and which carries a live `backend_agent_id`) requires an explicit `force_remote_delete: true` confirmation, and that the desktop's local stop command rejects remote agents outright -- Stop and Delete are two different operations with two different guards, not one action under two names."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:921-923"
  - statement: "docs/remote-agents.md's 'Auto-Stop' section defines a harness knob, `--exit-after-inactivity` / `BUZZ_ACP_EXIT_AFTER_INACTIVITY`, defaulting to 0 (disabled) so every local agent ships the same flag without risk of a reaper bug killing a laptop agent; on expiry the harness fires the identical shutdown channel `!shutdown` uses, so an inactivity exit gets the same in-flight drain, presence-offline and graceful relay close as an owner-initiated stop."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:925-946"
  - statement: "crates/buzz-acp/src/lib.rs's is_owner_control_command checks that an inbound event's kind matches, its trimmed content equals the given command string, and it mentions the harness's own agent pubkey -- the same function gates `!shutdown`, `!cancel` and `!rotate` by passing a different command string, so shutdown recognition is one instance of a shared owner-control-command check, not a bespoke parser."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3641-3649"
  - statement: "crates/buzz-acp/src/lib.rs's main event loop checks `is_shutdown` via is_owner_control_command with the literal command \"!shutdown\", and only sends on the internal shutdown_tx watch channel after separately re-confirming the event's sender against a cached owner value; a `!shutdown`-shaped message from a non-owner falls through to normal prompt handling rather than being silently dropped."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2737-2759"
  - statement: "crates/buzz-acp/src/lib.rs's own unit test owner_control_command_requires_kind_content_and_agent_mention directly exercises is_owner_control_command (the same function that gates !shutdown) against four cases -- correct kind/content/mention, wrong kind, wrong content, and no agent mention -- and asserts it returns true only for the first, verifying the gating logic this node cites rather than merely reading it uncorroborated."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:5234-5264"
  - statement: "crates/buzz-acp/src/lib.rs wires both an OS SIGTERM handler (`signal(SignalKind::terminate())`) and, near the end of the main loop, an explicit `shutdown_tx.send(())` guarding a graceful wake-task drain -- SIGTERM (the substrate's own termination signal) and an in-band `!shutdown` message converge on the same shutdown_tx channel rather than each having its own independent exit path."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2328"
      - "crates/buzz-acp/src/lib.rs:3429"
  - statement: "desktop/src-tauri/src/managed_agents/runtime/stop.rs's stop_managed_agent_pair terminates a local agent by calling terminate_process directly on the tracked child process (or, on Windows, dropping/killing its job object), then waits on the child and records its exit code -- the desktop itself performs the kill; there is no relay message involved in stopping a local agent."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime/stop.rs:40-69"
  - statement: "desktop/src-tauri/src/commands/agents.rs's delete_managed_agent refuses to delete a managed-agent record whose backend is not BackendKind::Local and which carries a backend_agent_id, unless the caller passes force_remote_delete: true, returning the error \"cannot delete a deployed remote agent without force_remote_delete: true\" -- this guard exists specifically so deleting the record cannot silently orphan a live remote deployment, and its comment states the frontend only sends the flag after the user confirms an orphan-warning dialog."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents.rs:1190-1234"
  - statement: "crates/buzz-backend-kubernetes/src/wire.rs's Request enum has exactly two variants, Info and Deploy, with no undeploy/destroy/stop operation in protocol version 1 -- the provider wire contract itself carries no way to ask a remote substrate to terminate an agent; termination is driven entirely through the relay, never through this protocol."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/wire.rs:11-24"
  - statement: "crates/buzz-backend-kubernetes/src/classify.rs's Action enum carries a Delete { name, fence } variant used for a terminated or provably-broken pod, and its module comment states 'Action::Delete carries the Fence from the exact observation that authorized it' so deletion is always compare-and-delete, never an unconditional remove; this Delete acts on substrate objects (Pod/Secret), not on the harness process itself, which has already exited by the time this code runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/classify.rs:9-14"
      - "crates/buzz-backend-kubernetes/src/classify.rs:89"
      - "crates/buzz-backend-kubernetes/src/classify.rs:134"
  - statement: "crates/buzz-backend-kubernetes/src/gc.rs's module comment states GC 'runs on every deploy, after identity derivation and before the state transition' and deletes terminated pods (and their referenced Secrets) plus age-eligible orphan Secrets; an unreferenced Secret is only GC-eligible once older than ORPHAN_SECRET_MIN_AGE_SECS (twice the 600-second deploy deadline) -- so destroying a terminated agent's substrate residue happens asynchronously, on a later deploy call or after an age gate, never synchronously as part of the termination event itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/gc.rs:1-9"
      - "crates/buzz-backend-kubernetes/src/gc.rs:17-26"
  - statement: "Issues #1041 (backend-provider), #1042 (kubernetes-provider), #1043 (lifecycle), #1044 (liveness), #1045 (local-agent-compute), #1046 (mesh-compute), #1048 (remote-agent-compute) are filed, open sibling tasks under this node's own parent Feature (#611); their exact numbers were confirmed directly (`gh issue view`) rather than assumed from worktree directory names, since an already-drafted sibling node's own citation of one of these numbers was found to be incorrect during this node's authoring."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue view 1041/1042/1043/1044/1045/1046/1048 --repo launchpad-26/buzz, run directly while authoring this node"
  - statement: "At the recorded revision, `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` contains no `layers/` directory at all, so none of this node's sibling `layers/compute/*` documents (#1041-#1049, all still open) exist as mergeable `relationships` targets, even though drafts of several already exist in other worktrees at the same recorded revision."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**; no layers/ directory present"
relationships:
  - type: references
    target: architecture-containers-agent-runtime
---

# Concept: Compute termination

An agent's compute instance does not run forever, and how it stops is not one
mechanism but a small family of related ones that this document names and
distinguishes. This node defines **termination** as a single concept and
draws its boundary against the things most easily confused with it: the
signal that *detects* an agent has stopped, the cleanup that happens *after*
it stops, and the flow-level narration of a full deploy-to-teardown scenario.

## Definition

**Termination is the event by which a Buzz-managed agent's running
`buzz-acp` harness process permanently stops executing, as the direct or
indirect result of an intentional decision** — an owner-issued stop, or the
harness's own opt-in inactivity self-stop — as opposed to an *abnormal*
death (a crash, an OOM kill, a node eviction) which the agent's compute
substrate or supervisor may cause without anyone intending it.

`docs/remote-agents.md`'s invariant **(I5) "Intentional termination is
final"** is this concept's defining source: a remote agent "stops when told,
stays down when it stops, and is never silently resurrected." Two things
that sentence keeps separate on purpose:

- **"Final" means terminal to automatic supervisor restart, not that the
  agent can never run again.** An owner may always issue a fresh Start. What
  I5 forbids is a supervisor silently reviving an agent that exited on
  purpose — it does not forbid the owner from choosing to start a new
  instance.
- **Termination is not mandatory.** An owner may choose no inactivity bound
  at all (an indefinitely-lived agent, expressed as `inactivity_seconds: 0`
  in the Kubernetes binding's schema) and that is a legitimate, explicit
  choice, not a conformance failure. The invariant is "termination, once
  intended, sticks" — never "every agent eventually terminates."

**What termination is not:**

- **Not liveness detection.** Whether the desktop currently believes an
  agent is running (relay presence, `kind:20001`) is a separate signal that
  can lag the true moment of termination by up to its own staleness bound.
  This node documents the event that causes that signal to eventually read
  `offline`; the mechanism that reads and interprets the signal is a
  sibling concept's subject (see *Scope and omissions*).
- **Not destroying substrate residue.** Once a Kubernetes-backed agent's
  harness process exits, its Pod reaches a terminal phase but is not deleted
  synchronously — that Pod, and its Secret, are removed only by the *next*
  deploy call's preflight garbage collection, or by an orphan-Secret sweep
  gated on an age bound. Termination is the harness stopping; destroying the
  leftover substrate objects is a distinct, later, asynchronous step this
  node names but does not itself narrate in detail.
- **Not one mechanism for every launcher.** A local agent (`BackendKind::
  Local`) is terminated by the desktop calling `terminate_process` directly
  on a process it holds a handle to. A remote agent (`BackendKind::
  Provider`) has no such handle — the desktop publishes a relay message and
  waits for the harness, on the substrate, to notice it and exit itself.
  Same concept, two structurally different mechanisms, driven by whether
  the desktop has a direct process handle at all.
- **Not the full deploy/lifecycle flow.** How an agent is created, observed,
  restarted and eventually reaped by garbage collection is a scenario this
  concept participates in but does not itself narrate; that sequence
  belongs to a sibling flow-shaped document (see *Scope and omissions*).

## Visual aid

```mermaid
flowchart TD
    subgraph Local["Local agent (BackendKind::Local)"]
        L1["Desktop: stop_managed_agent_pair"] --> L2["terminate_process(child.id())\n(direct OS kill)"]
        L2 --> L3["Harness process exits"]
    end

    subgraph Remote["Remote agent (BackendKind::Provider)"]
        R1["Owner: kind:9 \"!shutdown\"\n(mentions agent) via Relay"] --> R2["Harness: is_owner_control_command\nverifies sender == owner"]
        R2 --> R3["shutdown_tx.send(())\n(same channel as SIGTERM,\nAuto-Stop inactivity expiry)"]
        R3 --> R4["Graceful path: drain in-flight turns,\npresence -> offline, close relay conn"]
        R4 --> R5["Harness process exits"]
        R5 -.->|"not synchronous --\nnext deploy's GC, or\norphan-Secret age sweep"| R6["Pod + Secret deleted\n(destroy, a later step)"]
    end
```

Both paths converge on the same idea — the harness process stops running,
intentionally — but only the local path gives the desktop a direct handle to
act on; the remote path has no such handle by design (`docs/remote-agents.md`'s
invariant M1), so it goes through the relay instead.

## Use cases

- **Distinguishing "the agent stopped" from "the agent is gone."** An
  operator troubleshooting a remote agent that shows as offline but whose
  Pod is still visible in the cluster needs this concept to understand that
  termination (the harness exiting) and destruction (the Pod/Secret being
  deleted) are deliberately not the same moment — the Pod's continued
  existence for a while after termination is expected, not a leak.
- **Reviewing or writing code that stops an agent.** Anyone touching
  `stop_managed_agent_pair`, `delete_managed_agent`, or the harness's
  `!shutdown`/Auto-Stop handling needs to know which of the two mechanisms
  (direct kill vs. relay message) applies to the `BackendKind` they are
  working with, and that both intentional paths funnel into the same
  underlying guarantee (I5) even though their code paths do not share a
  process boundary.
- **Reasoning about restart safety.** Understanding that "final" (I5) binds
  only *intentional* termination — never an abnormal death — is a
  prerequisite for correctly configuring or reviewing any supervisor/restart
  policy: a policy that revives every death regardless of intent silently
  breaks the guarantee an owner-issued Stop is supposed to provide.
- **Auditing the Delete confirmation flow.** A developer changing
  `delete_managed_agent`'s `force_remote_delete` guard needs to know that
  Delete is not synonymous with Stop — deleting the *record* of a remote
  agent that is still deployed is a separate, explicitly-confirmed action
  from terminating its running harness.

## Comparison: local vs. remote termination

| Aspect | Local agent | Remote (provider) agent |
|---|---|---|
| Trigger (owner-initiated) | Desktop UI action → `stop_managed_agent_pair` | Owner publishes `kind:9` `!shutdown` mentioning the agent |
| Mechanism | `terminate_process` on the tracked child PID/process group — a direct OS kill | Harness verifies sender is owner, then `shutdown_tx.send(())` drives its own graceful exit |
| Auto-Stop (inactivity) | Same harness flag exists but ships disabled by default for every local agent | Fires the identical `shutdown_tx` channel as an owner `!shutdown` |
| Substrate termination signal | N/A — the desktop already holds the process handle | SIGTERM (or the pod's grace-period signal) reaches the harness, wired to the same `shutdown_tx` channel |
| Provider wire operation for stopping | N/A (no provider involved) | None — the two-operation wire contract (`Info`, `Deploy`) has no stop/undeploy operation at all |
| Destroying residue | Immediate — the OS process is gone; no separate substrate object outlives it | Deferred — the terminated Pod and its Secret are removed by the *next* deploy's preflight GC, or an age-gated orphan sweep |
| Record-level Delete guard | None beyond normal record deletion | Requires explicit `force_remote_delete: true` if a `backend_agent_id` is still present |

## Scope and omissions

**This node covers** the definition of termination as a Buzz concept — what
counts as termination, why "intentional" is the load-bearing word in I5, the
distinct local (direct-kill) and remote (relay-message) mechanisms that both
realize it, and the boundary between termination itself and the things most
easily mistaken for it (liveness detection, substrate destruction/GC, and
the full lifecycle flow).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the desktop detects and displays whether an agent is currently alive (relay presence, staleness bounds) | #1044, `layers/compute/liveness.md` |
| The full create/start/observe/restart/reap sequence across one deploy's lifetime, narrated as a scenario | #1043, `layers/compute/lifecycle.md` |
| The Kubernetes binding's own deploy state machine, fencing and garbage-collection mechanics in detail | #1042, `layers/compute/kubernetes-provider.md` |
| Local-only process-supervision machinery (`orphan_sweep`, `instance_reaper`) beyond the direct-kill stop path this node names | #1045, `layers/compute/local-agent-compute.md` |
| The remote-agent umbrella concept and its five invariants beyond I5 | #1048, `layers/compute/remote-agent-compute.md` |
| Shared/mesh compute's own termination particulars, if any differ from the Kubernetes binding's | #1046, `layers/compute/mesh-compute.md` |
| The general provider wire protocol beyond the fact that it carries no stop operation | #1041, `layers/compute/backend-provider.md` |

**No `relationships` to the sibling `layers/compute/*` documents above.**
Checked before deciding that rather than assumed: at the recorded revision,
`origin/launchpad`'s `launchpad/docs/corpus` tree carries no `layers/`
directory at all, so none of #1041-#1049 (including drafts of several that
already exist in other worktrees at this same revision) are valid
`relationships` targets today. One edge is declared instead, to a node that
does exist: `architecture-containers-agent-runtime`, which describes the
`buzz-acp` harness whose termination this node's local- and remote-path
mechanisms both act on.

**Expected but not verified when this node was written:**

- **Whether Known Defect 6 (the pinned intentional-exit-implies-exit-code-0
  contract) or Known Defect 7 (a single shared shutdown-tail budget with a
  reserved finalization slice) have closed since `docs/remote-agents.md`'s
  own `28ae6cd21` pin.** This node cites both as open per the spec's own
  text; no independent re-check of `crates/buzz-acp`'s current exit-code
  behavior or shutdown-tail timing was performed against the recorded
  revision beyond the code already cited in the evidence ledger.
- **Whether `sprout-backend-blox` (the closed-repository Blox workstation
  compute provider named in this repository's own `CLAUDE.md`) terminates
  agents through the same relay-message mechanism, or has substrate-specific
  particulars.** Nothing about it can be verified from this repository.
- **Whether mesh/shared compute (`RELAY_MESH_PROVIDER`) has its own
  termination path distinct from the Kubernetes binding's** was not
  independently checked here; #1046's own node is better placed to confirm
  or refine this.
