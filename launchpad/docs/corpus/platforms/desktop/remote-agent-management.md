---
id: platforms-desktop-remote-agent-management
type: architecture
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
  - statement: "BackendKind is a two-variant enum -- Local (default) and Provider{id, config} -- serialized with an internal `type` tag; ManagedAgentRecord.backend carries it, so every managed agent is either spawned locally or deployed through a named provider binary with an opaque JSON config."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/types.rs:6-13"
  - statement: "Provider binaries are discovered by scanning PATH (plus the executable's own parent directory and ~/.local/bin) for files named buzz-backend-<id>, without executing any of them; resolve_provider_binary re-validates the id against `^[a-z0-9][a-z0-9_-]*$` and only returns a path already present in that discovered set, explicitly to prevent a compromised frontend/IPC caller from redirecting execution to an arbitrary binary."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:593-638"
      - "desktop/src-tauri/src/managed_agents/backend.rs:650-677"
  - statement: "invoke_provider spawns the provider binary once, writes a JSON request to stdin, streams stdout/stderr over channels with a byte cap (1 MB stdout, 64 KB stderr) and a caller-supplied timeout, and treats a non-zero exit as failure regardless of stdout content."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:75-288"
  - statement: "provider_deploy stages the resolved provider binary into a private, hashed, read-only temporary copy before invoking it, then calls the `info` operation to negotiate and validate the protocol version before sending the secret-bearing `deploy` request to that same staged, immutable copy -- closing a path-replacement/in-place-rewrite race between negotiation and the secret-bearing call."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:436-505"
      - "desktop/src-tauri/src/managed_agents/backend.rs:509-533"
  - statement: "validate_provider_config rejects a provider_config that is not a flat JSON object, has more than 20 fields, exceeds 64 KB serialized, contains a non-scalar value, or has a key whose word-split (splitting on separators and camelCase boundaries) matches secret/password/token/key/credential."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:536-566"
  - statement: "redact_secrets_with scrubs stderr/error text from a provider both by exact-value replacement of every non-empty env value the deploy request carried and by prefix-based redaction of nsec1/GitHub-token-shaped substrings, and desktop/src/features/agents/ui/runOnSummary.ts documents itself as mirroring the same secret-word list and the same key-splitting function on the frontend side for display-time redaction of saved provider config."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:345-390"
      - "desktop/src/features/agents/ui/runOnSummary.ts:36-45"
      - "desktop/src/features/agents/ui/runOnSummary.ts:59-66"
  - statement: "build_deploy_payload resolves the same effective config (model, provider, prompt, harness descriptor, parallelism) that local spawn uses, rejects deployment of a relay-mesh-backed agent because the mesh endpoint is local to the desktop, and assembles a `launch` block (command, args, layered env, policy_env, owner_pubkey) via build_launch_block -- the portable contract shared with provider-backed execution so remote execution does not reimplement local's resolution logic."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents_deploy.rs:173-229"
      - "desktop/src-tauri/src/commands/agents_deploy.rs:49-160"
      - "desktop/src-tauri/src/commands/agents_deploy.rs:162-170"
  - statement: "deploy_to_provider serializes concurrent deploys of the same agent behind a per-pubkey lock, rebuilds the deploy payload from the live record AFTER acquiring that lock (not the caller's pre-lock snapshot), and asserts any caller-captured relay/signer scope against that rebuilt payload -- so a workspace or identity switch that lands while the call waited behind another deployment fails closed instead of deploying into the new tenant under the old caller's authorization."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents/provider_deploy.rs:35-122"
      - "desktop/src-tauri/src/commands/agents/provider_deploy.rs:131-160"
  - statement: "needs_reconciliation_with_policy selects a record for redeploy when it is provider-backed, already has a backend_agent_id, and either the build enforces owner-only access or the record's own provider_policy_pending flag is set; reconcile_on_workspace_apply runs this selection and redeploys every match on each workspace apply, failing the whole apply closed if any selected provider rejects the current policy."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents/provider_access.rs:14-21"
      - "desktop/src-tauri/src/commands/agents/provider_access.rs:61-113"
  - statement: "reconcile_on_workspace_apply is invoked from the workspace-apply command path, and owner-only access enforcement (BUZZ_BUILD_AGENT_ACCESS_OWNER_ONLY) projects RespondTo::OwnerOnly into both the local-spawn env and the provider deploy payload without altering the stored record, so the same saved agent definition keeps its user-chosen access if opened in a build without that policy compiled in."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/workspace.rs:264"
      - "desktop/src-tauri/src/managed_agents/access_policy.rs:60-69"
  - statement: "discover_backend_providers and probe_backend_provider are the Tauri commands the frontend uses to list PATH-discovered buzz-backend-* binaries and query a provider's self-reported name/version/config_schema before a user picks one; probe_backend_provider re-validates the given path against the same discovered-candidate set before invoking it."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agent_providers.rs:4-16"
      - "desktop/src-tauri/src/commands/agent_providers.rs:19-46"
  - statement: "create_managed_agent resolves and caches the provider binary path at creation time and, when spawn_after_create is set for a Provider-backed record, calls deploy_to_provider inline; start_managed_agent branches on BackendKind at every start, routing Provider-backed records through deploy_to_provider instead of the local spawn path; stop_managed_agent refuses to act on a non-Local record with the message 'remote agents are stopped via !shutdown message, not this command'; delete_managed_agent refuses to delete a non-Local record that already has a backend_agent_id unless the caller passes force_remote_delete: true."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents.rs:380"
      - "desktop/src-tauri/src/commands/agents.rs:515"
      - "desktop/src-tauri/src/commands/agents.rs:801-802"
      - "desktop/src-tauri/src/commands/agents.rs:860"
      - "desktop/src-tauri/src/commands/agents.rs:1039"
      - "desktop/src-tauri/src/commands/agents.rs:1069"
      - "desktop/src-tauri/src/commands/agents.rs:1092"
      - "desktop/src-tauri/src/commands/agents.rs:1128"
  - statement: "docs/remote-agents.md is the formal specification for the provider protocol (discovery, invocation, the deploy state machine, stop/delete, auto-stop, the Kubernetes binding and conformance levels) and its own 'Implementation Correspondence' table maps each spec concept to the exact desktop files this node decomposes -- discovery/resolution and invocation/redaction/config-validation to backend.rs, the payload/launch resolver to agents_deploy.rs, and unconditional deploy-on-start to agents.rs's start_managed_agent."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1687-1707"
  - statement: "docs/remote-agents.md states that stop is not a provider operation -- the frontend publishes a signed `!shutdown` mention that the harness itself verifies and acts on -- and that the desktop's local stop command rejects remote agents outright, matching the refusal this node cites in stop_managed_agent."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:884-923"
  - statement: "The architecture-containers-agent-runtime corpus node already names 'Desktop's local/remote launch and access-policy logic' at desktop/src-tauri/src/managed_agents/ as the place its own remote-deployment interface is realized on the desktop side, and separately states that docs/remote-agents.md is the formal specification governing remote deployment between Buzz Desktop and any buzz-backend-<id> binary."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:219-228"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:241-250"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:281"
  - statement: "The desktop app bundles buzz-backend-kubernetes as one of its externalBin entries in the Tauri bundle configuration, so the Kubernetes provider ships inside the same desktop installer as the rest of the managed-agent surface even though it runs as a separate spawned process implementing the provider protocol from the outside."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json:58"
  - statement: "This node's building blocks realize the desktop side of a two-party protocol whose other side is the buzz-acp harness the architecture-containers-agent-runtime node documents, so a depends-on edge to that node is the closest fit among relationships.schema.json's five types: this component's launch/env contract is only meaningful because that container's harness reads it the way agent-runtime.md's own Implementation Correspondence table assumes."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:281"
    confidence: 0.65
  - statement: "This node declares part-of targeting architecture-containers-desktop because the C4 model defines a component as residing inside exactly one container and the desktop container node is the one whose Tauri/Rust+React description matches every file this node cites."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/architecture-component.md"
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
    confidence: 0.7
  - statement: "Issue #1247's Definition of Done requires exactly one hand-authored canonical document, schema-valid front matter with typed relationships, FACT/INFERENCE/TEAM_KNOWLEDGE not conflated, links to implementation/tests/specification without duplicating their content, and component-level (not whole-platform) scope."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1247 definition of done"
  - statement: "Issue #1247 identifies BackendKind::Local vs BackendKind::Provider{id,config} in desktop/src-tauri/src/managed_agents/types.rs as the code-level boundary between this node's subject (remote agent management) and sibling issue #1242's subject (local agent management), and states that #1242 is not this node's to edit."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1247 issue body, dispatched batch instructions"
relationships:
  - type: part-of
    target: architecture-containers-desktop
  - type: depends-on
    target: architecture-containers-agent-runtime
---

# Desktop: remote agent management (component view)

This node decomposes the `architecture-containers-desktop` container's
**remote** managed-agent surface: the code path exercised when a managed
agent's `backend` is `BackendKind::Provider { id, config }` rather than
`BackendKind::Local`. It answers "what inside the desktop app turns a saved
provider-backed agent definition into a running remote deployment, and back
into a stopped/deleted one?" Local spawn (`BackendKind::Local`) is sibling
issue #1242's subject and is named here only where a code path branches on
`BackendKind` and both arms live in the same function.

## Notation legend

| Shape | Meaning |
|---|---|
| Rounded rectangle | A component inside the desktop container (Rust unless marked TS) |
| Cylinder | A persisted or external data boundary the component reads/writes |
| Double-bordered rectangle | An external process/container outside this component diagram's boundary |
| Solid arrow | A direct call or data flow |
| Dashed arrow | A cross-cutting concern applied by the source to the target (e.g. redaction) |

## Component diagram

```mermaid
flowchart TB
    subgraph desktop["Desktop app container (Tauri: Rust backend + React frontend)"]
        LC["Lifecycle commands<br/>create / start / stop / delete<br/>_agents.rs_"]
        PC["Provider catalog commands<br/>discover_backend_providers<br/>probe_backend_provider<br/>_agent_providers.rs_"]
        DPB["Deploy payload builder<br/>build_deploy_payload / build_launch_block<br/>_agents_deploy.rs_"]
        DO["Deploy orchestrator<br/>deploy_to_provider<br/>_provider_deploy.rs_"]
        APR["Access-policy reconciler<br/>reconcile_on_workspace_apply<br/>_provider_access.rs_"]
        PDI["Provider discovery &amp; invocation<br/>discover/resolve/invoke/stage<br/>_backend.rs_"]
        RED["Secret redaction<br/>redact_secrets_with (Rust)<br/>runOnSummary (TS)"]
        BK[("BackendKind record field<br/>_types.rs_")]
    end
    Provider[["Provider binary<br/>buzz-backend-&lt;id&gt;<br/>(e.g. buzz-backend-kubernetes)"]]
    Relay[("Buzz relay<br/>presence + !shutdown")]

    LC -->|reads/writes| BK
    LC --> DPB
    LC --> PC
    PC --> PDI
    DPB --> DO
    APR --> DO
    DO --> PDI
    PDI -->|JSON over stdin/stdout| Provider
    RED -.applies to.-> PDI
    RED -.applies to.-> DO
    LC -.owner-signed !shutdown via.-> Relay
    Provider -.publishes presence.-> Relay
```

## Building blocks

| Component | Responsibility | Interface | Evidence |
|---|---|---|---|
| Backend discriminator (`BackendKind`) | Records whether an agent is spawned locally or deployed to a named provider with an opaque config blob | `enum BackendKind { Local, Provider { id, config } }` field on `ManagedAgentRecord.backend` | `desktop/src-tauri/src/managed_agents/types.rs:6-13` |
| Provider discovery & invocation | Finds `buzz-backend-*` binaries on PATH without executing them, re-validates an id before resolving it to a path, stages a hashed read-only copy, and runs the JSON-over-stdio provider protocol (`info`, `deploy`) with output caps and a timeout | `discover_provider_candidates`, `resolve_provider_binary`, `invoke_provider`, `provider_deploy`, `validate_provider_config` | `desktop/src-tauri/src/managed_agents/backend.rs:593-638,650-677,75-288,436-533,536-566` |
| Provider catalog commands | Tauri-command surface the frontend uses to list discovered providers and probe one's self-reported `info` before the user configures it | `discover_backend_providers`, `probe_backend_provider` | `desktop/src-tauri/src/commands/agent_providers.rs:4-46` |
| Deploy payload builder | Resolves the same effective config local spawn uses (model/provider/prompt/harness/parallelism), refuses relay-mesh agents, and serializes the portable `launch` block (command, args, layered env, policy_env, owner_pubkey) | `build_deploy_payload`, `build_launch_block`, `ensure_remote_provider_supported`, `deploy_payload_json` | `desktop/src-tauri/src/commands/agents_deploy.rs:49-266` |
| Deploy orchestrator | Serializes concurrent deploys per agent, rebuilds the payload from the live record after acquiring the lock, and asserts any caller-captured tenant scope against that rebuilt payload before invoking the provider | `deploy_to_provider`, `assert_payload_scope`, `apply_deploy_result` | `desktop/src-tauri/src/commands/agents/provider_deploy.rs:35-196` |
| Access-policy reconciler | Selects provider-backed, already-deployed agents needing an access-policy redeploy (owner-only build or pending policy) and redeploys them on every workspace apply, failing the apply closed on rejection | `needs_reconciliation_with_policy`, `reconcile_on_workspace_apply` | `desktop/src-tauri/src/commands/agents/provider_access.rs:14-113`; call site `desktop/src-tauri/src/commands/workspace.rs:264` |
| Lifecycle command branching | Branches every create/start/stop/delete on `BackendKind`: caches the provider binary path and optionally deploys inline at create, routes start through the provider path, refuses local `stop` for remote agents (stopped via signed `!shutdown` instead), and refuses `delete` of a deployed remote agent without explicit confirmation | `create_managed_agent`, `start_managed_agent`, `stop_managed_agent`, `delete_managed_agent` | `desktop/src-tauri/src/commands/agents.rs:380,515,801-802,860,1039,1069,1092,1128` |
| Secret redaction | One word-split/secret-word definition shared (by convention, not by shared code) between the Rust diagnostic path and the frontend's saved-config display, so a provider's stderr/error text and a screenshot of a saved config redact the same shapes | `redact_secrets_with` (Rust), `runOnSummary.ts`'s `SECRET_WORDS`/`splitConfigKey` (TS) | `desktop/src-tauri/src/managed_agents/backend.rs:345-390`; `desktop/src/features/agents/ui/runOnSummary.ts:36-45,59-66` |

## Boundary

This node does not describe:

- **Local agent management** (`BackendKind::Local`'s own spawn, readiness and
  process-lifecycle machinery) — sibling issue #1242's subject. It is named
  above only where a single function branches on both `BackendKind` arms.
- **The desktop container's own deployment topology or bundling** (Tauri
  bundle config, externalBin list as a whole, the app's other features) —
  see the `architecture-containers-desktop` node for that.
- **External actors talking to the system from outside** (the human owner,
  the relay operator) — no architecture-context node exists yet for this
  container; when one does, it — not this node — names those actors.
- **The buzz-acp harness's own internals** (ACP wire protocol, session pool,
  shutdown/reap timing) — `architecture-containers-agent-runtime` and
  `crates/buzz-acp`'s own documentation own that, including the shutdown-
  timing gap `docs/remote-agents.md`'s Stop-and-Delete section documents as a
  Known Defect against the harness, not against anything in this component
  diagram.
- **The provider protocol's wire schema and stated invariants in full** —
  `docs/remote-agents.md` is authoritative; this node cites the sections that
  place its own building blocks rather than restating the spec.
- **`buzz-backend-kubernetes`'s own internals** (cluster auth, pod shape,
  image resolution, garbage collection) — a separate binary/crate this
  component invokes as an opaque subprocess over the provider protocol, not
  a building block of the desktop container. No corpus node documents that
  crate yet; see *Scope and omissions*.

## Relationships

- `part-of`: `architecture-containers-desktop` — this node decomposes that
  container's remote managed-agent surface.
- `depends-on`: `architecture-containers-agent-runtime` — the `launch` block
  this component's deploy payload builder emits is only meaningful because
  that container's harness (`buzz-acp`) reads it the way `docs/remote-
  agents.md`'s Implementation Correspondence table assumes; a drift in that
  harness contract would invalidate claims in this node's building-block
  table without any code in this node itself changing.

## Scope and omissions

**This node covers** the desktop-side components that turn a `BackendKind::
Provider`-backed managed-agent record into a deployed, access-policy-
enforced, stoppable/deletable remote agent: the backend discriminator,
provider discovery/invocation/redaction, deploy-payload construction, deploy
orchestration under a tenant-scope guard, access-policy reconciliation on
workspace apply, and the lifecycle-command branching that ties them together.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `BackendKind::Local` spawn/readiness/process-lifecycle | Issue #1242 (local agent management), not filed as a corpus node at time of writing |
| The desktop container's full deployment/bundling picture | `architecture-containers-desktop` |
| The ACP harness's internal protocol, pool and shutdown mechanics | `architecture-containers-agent-runtime`, `crates/buzz-acp` |
| The provider protocol's wire schema, five invariants, and conformance levels in full | `docs/remote-agents.md` |
| `buzz-backend-kubernetes`'s own internals (cluster auth, pod shape, image, GC) | No corpus node yet; a candidate for a future component- or container-level task, not folded in here |
| An architecture-context node naming the human owner / relay operator as external actors | Not yet drafted for this container |

**Expected but not verified when this node was written:**

- **Whether the pre-secret negotiation gate (`info` before `deploy` on one
  staged, hashed copy) matches `docs/remote-agents.md`'s own description of
  itself.** The spec's Implementation Correspondence table marks that row
  "*to be added*" (citing its own Known Defect 5), while the `backend.rs`
  source read for this node already implements exactly that sequence
  (`provider_deploy` at `backend.rs:509-533` calls `stage_provider`, then
  `info`, then `deploy` on the staged path). This node treats the code as
  ground truth for its own FACT claims and flags the discrepancy rather than
  resolving it — it may mean the spec table is stale, or that "to be added"
  refers to a narrower sub-requirement (an explicit protocol-version pinning
  test, say) than the sequencing itself.
- **Whether any provider binary besides `buzz-backend-kubernetes` exists or
  is planned.** Only one `buzz-backend-*` binary was found in this repository
  at the recorded revision; the protocol and this node's components are
  written to be provider-agnostic, but that genericity is untested against a
  second implementation.
- **The exact runtime behavior of `reconcile_on_workspace_apply` failing a
  workspace apply closed** (what the user sees, whether the workspace remains
  usable) was read from source, not exercised end-to-end in a running app.
