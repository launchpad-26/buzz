---
id: capabilities-agents-remote-agent
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "docs/remote-agents.md, status `draft`, specifies the protocol by which Buzz Desktop delegates execution of a managed agent to a remote substrate through a backend provider binary, and states its remote lifecycle model rests on the deliberate design constraint that 'the desktop holds no management channel to the remote process. Relay presence is the sole status signal; shutdown is a relay message; liveness bounds are enforced by the agent harness itself, not by the desktop.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1-24"
  - statement: "The document's own closing summary states 'Remote agents extend Buzz's managed-agent model across a deliberately thin boundary: one untrusted binary, two JSON operations, and a relay ... the relay was the management plane all along, and the desktop was only ever one of its doors' -- naming the managed-agent model explicitly as the base this capability extends, not a separate concept."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1768-1775"
  - statement: "The design axiom M1 ('No management channel') states that after a successful deploy, the desktop holds no persistent management session to the running agent: the desktop-provider protocol contains no substrate API (no status query, no exec, no log fetch, no kill); all post-deploy observation and control flows through the relay -- status is relay presence, stop is a relay message, reconfiguration is a future re-deploy."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:90-104"
  - statement: "The document's 'Stop and Delete' section states plainly that Stop is not a provider operation -- the desktop publishes a signed `!shutdown` mention on the relay, the harness verifies the sender is the owner and exits through its graceful path -- and that 'the desktop's local stop command rejects remote agents'; Delete with a live backend_agent_id requires force_remote_delete: true from the UI's orphan-warning confirmation, 'a buggy IPC caller cannot silently orphan substrate objects.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:884-923"
  - statement: "desktop/src-tauri/src/commands/agents.rs's stop_managed_agent command inspects the agent's stored BackendKind and, when it is not BackendKind::Local, returns the error 'remote agents are stopped via !shutdown message, not this command' instead of touching the process -- the desktop's own backend command surface enforces the no-direct-control boundary, not merely the frontend UI."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents.rs:1039-1073"
  - statement: "The same file's delete_managed_agent command refuses to delete a record whose backend is not BackendKind::Local and which already carries a backend_agent_id (a deployed remote agent), unless the caller explicitly passes force_remote_delete: true, returning the error 'cannot delete a deployed remote agent without force_remote_delete: true' otherwise -- turning the UI's own orphan-warning convention into a backend-enforced invariant an IPC caller cannot bypass."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents.rs:1092-1136"
  - statement: "tauri_platform_configs_bundle_kubernetes_only_on_supported_hosts, a real test in the desktop crate, asserts against the parsed Tauri bundle config that the buzz-backend-kubernetes external binary is bundled for macOS and Linux targets but not for Windows -- direct, runnable verification that the one shipped remote-agent substrate today is platform-gated rather than universally available."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents_tests.rs:545-566"
  - statement: "responses_match_their_fixtures, a test in crates/buzz-backend-kubernetes's own test suite, runs the actual built buzz-backend-kubernetes binary over a real OS pipe (not an in-process function call) against golden request/response JSON fixtures for its deploy and info operations, and fails if a produced response drifts from its fixture, exits non-zero, or emits anything other than exactly one JSON object -- direct verification of the wire contract that provisions a remote agent, exercising the actual boundary the desktop depends on rather than asserting the shape of an in-process value."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/tests/wire_fixtures.rs:49-92"
  - statement: "Sibling capability node capabilities-agents-managed-agent (issue #713, drafted as a local, unmerged worktree commit) states its own Boundary that 'a remote agent extends this same managed-agent model across a thinner boundary -- a provider binary and a relay, with the desktop holding no process handle to the running agent at all,' naming this as a distinct capability rather than a variant of managed-agent, and explicitly declines to declare a relationship to it because it was unmerged at that node's own recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#713's own committed node body (read directly from the task-713-managed-agent worktree, commit e84fc234a/367c95c9f), unmerged to origin/launchpad at this node's recorded revision"
  - statement: "Sibling capability node capabilities-agents-backend-provider (issue #712, drafted as a local, unmerged worktree commit) documents the pluggable backend-provider mechanism itself -- discovery, the info/deploy wire protocol, redaction, provider_config validation and the staged pre-secret negotiation deploy path -- as its own capability: 'the capability that lets \"run more agents than one laptop can host\" be a configuration choice rather than a different product.' That is the mechanism a remote agent is deployed through; this node is the resulting agent's own operating capability (identity, status, stop, delete) once deployed, not the deployment mechanism."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#712's own committed node body (read directly from the task-712-backend-provider worktree, commit 4106cf311), unmerged to origin/launchpad at this node's recorded revision"
  - statement: "Sibling capability node capabilities-agents-agent (issue #711, drafted as a local, unmerged worktree commit) is the umbrella agent capability and explicitly lists remote-agent (#716) as one of twelve more specific, not-yet-merged sibling facets, declaring no relationships target any capabilities-typed node 'because none of this subject's twelve sibling facets is merged on origin/launchpad as of this writing.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#711's own committed node body (read directly from the task-711-agent worktree, commit 6f7b10182), unmerged to origin/launchpad at this node's recorded revision"
  - statement: "layers-compute-remote-agent-compute (issue #1048, drafted as a local, unmerged worktree commit) documents remote agent compute as an umbrella technical concept at layers level -- the provider protocol, the five invariants I1-I5, and the three-layer conformance split -- and states it is the corpus's single canonical entry point for that concept, explicitly deferring the Kubernetes binding's own mechanics and the provider protocol's full wire contract to other, separately-owned nodes."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1048's own committed node body (read directly from the task-1048-remote-agent-compute worktree, commit 964385685), unmerged to origin/launchpad at this node's recorded revision"
  - statement: "platforms-desktop-remote-agent-management (issue #1247, drafted as a local, unmerged worktree commit, front matter type: architecture) decomposes the desktop container's component-level realization of remote agent deployment -- the backend discriminator, provider discovery/invocation, deploy-payload construction, deploy orchestration and lifecycle-command branching -- citing the same stop_managed_agent and delete_managed_agent guards this node cites directly from source rather than through that node, since it is unmerged."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1247's own committed node body (read directly from the task-1247-desktop-remote-agent-management worktree, commit 5c9eeebe9), unmerged to origin/launchpad at this node's recorded revision"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus contains no capabilities/, layers/, or platforms/ subtree at all -- confirmed directly -- so none of managed-agent, backend-provider, agent, remote-agent-compute or desktop-remote-agent-management is a valid relationships target under AGENTS.md's own rule to resolve targets against the merge-target branch, never against an author's own worktree."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**, no capabilities/layers/platforms subtree present, checked 2026-08-31"
relationships:
  - type: references
    target: architecture-containers-agent-runtime
---

# Remote agent: capability

Buzz can run a managed agent's `buzz-acp` harness on a **remote substrate** --
compute other than the user's own machine -- through a pluggable backend
provider, such that once the agent is deployed the desktop keeps no direct
process handle to it at all: no exec, no log tail, no kill signal. A user (an
agent owner) picks a backend other than `Local` when creating or configuring
an agent, presses Start, and gets an agent identity that authenticates,
converses, and posts to Buzz exactly the way a locally-run agent does -- the
same keypair, the same NIP-OA auth tag, the same relay. What changes is the
desktop's own relationship to it afterward: everything it can still tell the
user -- whether the agent is alive, and how to make it stop -- travels over
the same Nostr relay every other Buzz participant already depends on, not
through a channel unique to this one agent. This is the capability that
`docs/remote-agents.md` calls extending "the managed-agent model ... across a
deliberately thin boundary."

## Maturity

**In progress overall, with the parts an operator exercises today shipped and
tested.** The governing specification (`docs/remote-agents.md`) itself
carries `status: draft`, and names its own open items (an unimplemented
harness-side inactivity reaper, an unpinned clean-exit exit-code contract, a
shutdown tail whose total duration is not yet bounded to its declared grace
budget). Independent of that overall status, three pieces of this specific
capability -- what an operator gets and how the desktop enforces the
no-management-channel boundary -- are checked-in, tested code today:

- **The desktop refuses to let anyone route around the boundary.**
  `stop_managed_agent` returns an explicit error rather than acting on any
  agent whose backend is not `BackendKind::Local`; `delete_managed_agent`
  refuses to delete a deployed remote agent unless the caller explicitly
  passes `force_remote_delete: true`. Both are enforced in the backend
  command itself, not only as a frontend convention a compromised or buggy
  IPC caller could bypass.
- **The one shipped substrate is platform-gated, not universal.** A real
  test asserts the Kubernetes provider binary is bundled with the desktop
  app on macOS and Linux but not on Windows, so "remote agent" does not
  silently mean "available everywhere the desktop runs."
- **The wire contract that provisions a remote agent is exercised against
  the real built binary**, not merely asserted from a reading of the
  source: a golden-fixture test suite pipes real request JSON into the
  actual `buzz-backend-kubernetes` executable over stdin/stdout and checks
  its response byte-for-byte, catching drift the desktop's own reader would
  otherwise see as `undefined`.

## Boundary

This node does not describe:

- **The local-subprocess counterpart.** Running a managed agent as a
  directly-supervised local process -- the desktop or another launcher
  holding a live process handle it can observe and kill -- is a distinct
  capability (`launchpad-26/buzz#713`, drafted but unmerged at this node's
  recorded revision, not a valid `relationships` target today).
- **The pluggable backend-provider mechanism itself.** Discovery of
  `buzz-backend-<id>` binaries, the `info`/`deploy` wire protocol, output
  redaction, and `provider_config` validation are the *mechanism* a remote
  agent is deployed through -- a separate capability
  (`launchpad-26/buzz#712`, drafted but unmerged). This node describes the
  resulting agent's own operating capability once deployed (identity,
  status, stop, delete), not how the substrate becomes pluggable.
- **The provider protocol's full normative detail.** The five invariants
  (I1 identity fail-closed through I5 intentional-termination-is-final),
  the deploy reconciliation state machine, and the three-layer conformance
  split are `docs/remote-agents.md`'s own subject, restated at umbrella
  technical level by a separate, unmerged `layers`-typed node
  (`launchpad-26/buzz#1048`). This node cites the invariants that bound an
  operator's own experience (no management channel, presence-is-status,
  intentional-termination-is-final) without re-deriving any of the five.
- **The Kubernetes binding's own internals.** Cluster auth, namespace and
  image handling, the pod shape, Secret lifecycle and garbage collection
  belong to `docs/remote-agents.md`'s own "The Kubernetes Binding" section;
  no dedicated corpus node for that binding exists yet at this node's
  recorded revision.
- **The desktop's own component decomposition of this surface.** A
  separate, unmerged node (`launchpad-26/buzz#1247`) already decomposes the
  desktop-side code (backend discriminator, deploy orchestrator, lifecycle
  command branching) that realizes this capability; this node cites the
  same underlying source directly rather than through that node, since it
  is not yet a valid `relationships` target.
- **How the running system is operated.** Provider infrastructure
  deployment, monitoring, and incident response are the `operations`
  corpus surface, not this capability's own subject matter.

## Behavioral rules, constraints and variants

- **No management channel survives a successful deploy.** Once deployed,
  the desktop's only window onto a remote agent is the same relay every
  other Buzz client uses: liveness is derived from presence, and control is
  a relay message, never a direct call to the substrate or the process.
- **Stop is a signed relay message, not a command.** The desktop publishes
  an owner-signed `!shutdown` mention naming the agent; the harness itself
  verifies the sender and exits through its own graceful path (drain
  in-flight turns, publish presence `offline`, close the relay connection).
  The desktop's backend command layer enforces that this is the *only*
  path for a non-local agent: `stop_managed_agent` rejects any attempt to
  act on one directly.
- **Delete is guarded against orphaning live substrate objects.** Deleting
  a managed-agent record that is both non-local and already deployed
  (carries a `backend_agent_id`) is refused unless the caller passes
  `force_remote_delete: true` -- the UI only sends that flag after an
  explicit orphan-warning confirmation from the user, and the backend
  enforces the same rule independent of what the frontend does.
- **The substrate that realizes this capability today is platform-gated.**
  Kubernetes is the one shipped backend; the desktop bundles its provider
  binary on macOS and Linux builds and not on Windows builds, a fact
  checked by a real test rather than assumed from the provider protocol
  being substrate-agnostic in principle.
- **Identity still reaches the agent, through a different path than a
  local subprocess uses.** A locally-run managed agent inherits its
  `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG` from the launching
  process's own environment; a remote agent instead receives the
  equivalent values inside the provider's `deploy` payload, built by the
  desktop's own launch-block resolver and applied by the provider
  mechanically rather than re-derived -- the same three values, delivered
  through the provider contract instead of direct environment inheritance.

## Relationships

- `references`: `architecture-containers-agent-runtime` -- the `buzz-acp`
  harness this capability provisions onto a remote substrate; its
  conversational behavior, ACP wire protocol and tool-calling are
  unchanged by where the harness runs, so this node references that
  container rather than restating it.

No `capabilities`-, `layers`-, or `platforms`-typed relationship is
declared. `capabilities-agents-managed-agent` (#713), `capabilities-agents-
backend-provider` (#712), `capabilities-agents-agent` (#711),
`layers-compute-remote-agent-compute` (#1048), and `platforms-desktop-
remote-agent-management` (#1247) are all drafted, but each exists only as a
local, unmerged worktree commit at this node's recorded revision --
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
contains no `capabilities/`, `layers/`, or `platforms/` subtree at all, so
none is a valid target under `AGENTS.md`'s own rule to resolve
`relationships` against the merge-target branch, never against an author's
own worktree. This mirrors the precedent both `#713` and `#711` already set
for the identical situation: the first moment any of these five merges is
the right moment to add the corresponding edge back, not before.

## Scope and omissions

**This node covers** the remote-agent capability at the level a product
stakeholder would recognize it: what changes for an operator once an agent
is deployed to a remote substrate (no management channel, presence-only
status, relay-message stop, guarded delete), its current maturity as
checked directly against this node's cited revision, and its boundary
against the local-subprocess counterpart, the pluggable provider mechanism,
the full invariant specification, the Kubernetes binding's own internals,
and the desktop's own component decomposition.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The local-subprocess managed-agent capability | `launchpad-26/buzz#713` (capabilities/agents/managed-agent.md, unmerged) |
| The pluggable backend-provider mechanism (discovery, wire protocol, redaction) | `launchpad-26/buzz#712` (capabilities/agents/backend-provider.md, unmerged) |
| The umbrella agent capability and its other eleven facets | `launchpad-26/buzz#711` (capabilities/agents/agent.md, unmerged) |
| The provider protocol's full normative detail (invariants I1-I5, conformance layering) | `docs/remote-agents.md` directly; `launchpad-26/buzz#1048` (layers/compute/remote-agent-compute.md, unmerged) |
| The Kubernetes binding's own internals (pod shape, Secret lifecycle, GC) | `docs/remote-agents.md`'s own "The Kubernetes Binding" section; no dedicated corpus node yet |
| The desktop's own component-level decomposition of this surface | `launchpad-26/buzz#1247` (platforms/desktop/remote-agent-management.md, unmerged) |
| How provider infrastructure is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- **Whether the "Stop and Delete" shutdown-tail Known Defect** (the
  post-signal segment total not yet bounded to the declared grace budget)
  is still open at this node's cited revision -- read directly in
  `docs/remote-agents.md` but not independently re-verified against
  current harness code for this node.
- **Whether the in-progress SSH/systemd binding (block/buzz#3449)** would
  change any of the operator-facing behavior this node states (no
  management channel, relay-message stop) if it lands -- that binding is
  unmerged upstream and was not opened while drafting this node.
- **Whether the five sibling nodes named above** (`#713`, `#712`, `#711`,
  `#1048`, `#1247`) will carry the exact same claims once they and this
  node are integrated together -- each was read directly from its own
  worktree commit for this node's `TEAM_KNOWLEDGE` entries, not from a
  merged, reviewed copy.
