---
id: capabilities-agents-backend-provider
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
  - statement: "docs/remote-agents.md, status `draft`, specifies the protocol by which Buzz Desktop delegates execution of a managed agent to a remote substrate through a backend provider binary named `buzz-backend-<id>`, covering the provider protocol (info/deploy), the remote lifecycle model, and the Kubernetes binding as the first conforming provider."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1-24"
  - statement: "The provider protocol is one process per operation: the desktop writes one JSON request object to the provider's stdin and reads one JSON response object from its stdout, with a non-zero exit code treated as failure regardless of stdout content."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:361-377"
  - statement: "crates/buzz-backend-kubernetes/src/wire.rs types the stdin/stdout contract: a `Request` enum tagged on `op` with `Info` and `Deploy` variants, and a flat, untagged `Response` enum (`Info`/`Deploy`/`Error`) so the desktop can read `ok`/`error`/`agent_id` off the top level."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/wire.rs:21-118"
  - statement: "crates/buzz-backend-kubernetes/tests/fixtures/provider-wire/ holds golden request/response JSON fixtures that are the shared arbiter for the stdin/stdout contract between the desktop (agents_deploy.rs) and this provider; tests/wire_fixtures.rs asserts the provider side against them."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/tests/fixtures/provider-wire/README.md"
      - "crates/buzz-backend-kubernetes/tests/wire_fixtures.rs"
  - statement: "desktop/src-tauri/src/managed_agents/backend.rs implements provider discovery (`discover_provider_candidates`, `resolve_provider_binary`), invocation with bounded reads (`invoke_provider`), output redaction (`redact_secrets`, `env_secrets_from_request`), provider_config validation against the no-secrets-in-configuration rule (`validate_provider_config`), and the staged pre-secret negotiation deploy path (`stage_provider`, `provider_deploy`)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:75"
      - "desktop/src-tauri/src/managed_agents/backend.rs:330"
      - "desktop/src-tauri/src/managed_agents/backend.rs:395"
      - "desktop/src-tauri/src/managed_agents/backend.rs:436"
      - "desktop/src-tauri/src/managed_agents/backend.rs:509"
      - "desktop/src-tauri/src/managed_agents/backend.rs:536"
      - "desktop/src-tauri/src/managed_agents/backend.rs:593"
      - "desktop/src-tauri/src/managed_agents/backend.rs:650"
  - statement: "provider_deploy (desktop/src-tauri/src/managed_agents/backend.rs:509) stages the resolved provider binary once, sends an `info` request to the staged copy, validates the response before proceeding, then sends `deploy` to that same staged copy — the pre-secret negotiation gate docs/remote-agents.md:334-359 requires so the agent's nsec is only ever sent to the exact bytes that answered `info`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:509-531"
  - statement: "desktop/src-tauri/src/commands/agents_deploy.rs builds the deploy payload (`build_deploy_payload`, `deploy_payload_json`) and, separately, the desktop-resolved `launch` block (`build_launch_block`) that a provider applies mechanically rather than re-deriving; deploy_payload_json's construction calls build_launch_block and folds its result into the emitted payload."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents_deploy.rs:49"
      - "desktop/src-tauri/src/commands/agents_deploy.rs:173"
      - "desktop/src-tauri/src/commands/agents_deploy.rs:236"
  - statement: "desktop/src-tauri/src/commands/agents.rs's start_managed_agent unconditionally issues a `deploy` request for any non-local agent on Start, rather than tracking substrate state on the desktop side — deploy is a reconciliation call, not a create call."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents.rs:860"
  - statement: "docs/remote-agents.md's own 'Implementation Correspondence' table, pinned to commit 28ae6cd21, listed the launch-data resolver's emission into agents_deploy.rs and the deploy path's protocol_version negotiation gate as 'to be added' (Known Defects 3 and 5); at the repository revision this node cites, both are present in the current tree — deploy_payload_json already folds in build_launch_block's output, and provider_deploy already performs stage → info → validate → deploy before sending deploy — so the implementation has progressed past that snapshot on these two points."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1597-1642"
      - "desktop/src-tauri/src/commands/agents_deploy.rs:172-198"
      - "desktop/src-tauri/src/managed_agents/backend.rs:509-522"
  - statement: "docs/remote-agents.md's Known Defects list (at commit 28ae6cd21) also names a harness-side inactivity reaper that does not yet exist, an unpinned clean-exit exit-code contract, and a shutdown tail that can exceed its declared grace budget; whether these remain open at this node's cited revision was not independently re-verified when this node was drafted."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1626-1673"
  - statement: "launchpad/docs/corpus/architecture/deployment/kubernetes.md, already merged, explicitly states that buzz-backend-kubernetes is a distinct compute-provisioning concern from the relay's own deployment topology and is deliberately out of that node's scope, leaving this capability node as the place that concern is documented rather than a duplicate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md:114-117"
  - statement: "Root CLAUDE.md's ecosystem table names squareup/sprout-backend-blox as 'Desktop backend provider script connecting Blox workstation agents to the relay,' a second, independently maintained implementation of this same capability whose source is not part of this repository."
    entry_class: FACT
    evidence:
      - "CLAUDE.md:40"
      - "CLAUDE.md:47"
---

# Backend provider: capability

Buzz Desktop can launch a managed agent onto compute other than the user's own
machine — a **remote substrate** — through a pluggable **backend provider**
binary, without changing anything about the agent's own identity, its
conversational behavior, or how it connects to the relay. A user (an agent
owner) configures an agent's backend as `Local` or as a named provider (for
example `kubernetes`) with provider-specific settings, presses Start, and the
agent comes up running somewhere else while remaining, from the relay's point
of view, the exact same kind of `buzz-acp` harness process it would be
locally. This is the capability that lets "run more agents than one laptop can
host" be a configuration choice rather than a different product.

## Maturity

**In progress**, per the governing specification's own status marker and its
own defect list, though several of its pieces are checked into the repository
and covered by tests.

Shipped, at the repository revision this node cites:

- The wire protocol itself — a tagged `Request` enum (`info`/`deploy`) and a
  flat `Response` enum — typed in `crates/buzz-backend-kubernetes/src/wire.rs`
  and pinned by golden request/response fixtures under
  `crates/buzz-backend-kubernetes/tests/fixtures/provider-wire/`.
- The desktop side of the contract: binary discovery, bounded-read invocation,
  output redaction, and `provider_config` validation against the
  no-secrets-in-configuration rule, all in
  `desktop/src-tauri/src/managed_agents/backend.rs`.
- The staged pre-secret negotiation deploy path (stage the resolved binary
  once, `info` it, validate, then `deploy` the same staged bytes) in
  `provider_deploy`.
- Payload construction, including the desktop-resolved `launch` block
  (command, layered env, policy env, owner pubkey) that a provider applies
  mechanically instead of re-deriving, in
  `desktop/src-tauri/src/commands/agents_deploy.rs`.
- The Kubernetes binding (`buzz-backend-kubernetes`) as a real crate with its
  own reconciliation, naming, secret, and garbage-collection modules.

Not yet fully hardened, per the spec document's own accounting (`docs/
remote-agents.md`, "Known Defects (at 28ae6cd21)"): a harness-side inactivity
reaper that does not exist yet, an exit-code contract for "intentional exit"
that is emergent rather than pinned by test, a shutdown tail whose total
duration is not yet bounded to the declared grace period, a Windows discovery
bug, and a numeric-provider-config-field coercion gap. Two items from that
same defect list — the `launch` block's emission into the deploy payload, and
the deploy path's `protocol_version` negotiation gate — are verified present
in the current tree (see evidence), so the implementation has moved past that
snapshot on those two points specifically; the remaining defects were not
re-verified for this node and should be treated as open until checked against
current code, not assumed fixed by analogy.

This is a maturity statement about the *capability*, not the corpus document's
own authoring `status: draft` above — the two are independent, per the
template's own caution against conflating them.

## Boundary

This node does not describe:

- **How the Kubernetes binding is built internally** — its reconciliation
  loop, secret scheme, naming, and garbage collection are container/component
  detail. `docs/remote-agents.md` §The Kubernetes Binding is the authoritative
  source; no dedicated architecture-component corpus node for it exists yet
  at this node's cited revision.
- **The relay's own Kubernetes deployment topology.** That is a different
  concern — deploying the relay binary itself — already documented by
  `architecture-deployment-kubernetes`, which explicitly scopes
  `buzz-backend-kubernetes` out of its own coverage rather than folding it in.
- **The step-by-step flow of one deploy** (discovery → stage → info → deploy →
  reconcile) as a narrated sequence. That belongs to a flow-shaped node, not
  drafted at this node's cited revision.
- **The interface(s) a user or agent drives this through** — the desktop's
  agent-configuration UI and its Tauri commands (`start_managed_agent` et
  al.). No dedicated interface node for it exists yet at this node's cited
  revision.
- **Substrate security** (Kubernetes RBAC, namespace isolation, secret
  encryption at rest) and **malicious-provider containment** — both are
  explicit non-goals of the governing specification itself, not gaps this
  node is silent about.
- **sprout-backend-blox**, the separate desktop-backend-provider script named
  in root `CLAUDE.md`'s ecosystem table that connects Blox workstation agents
  to the relay. Its source lives outside this repository, so this node makes
  no claim about its internal behavior beyond the fact of its existence as a
  second implementation of the same provider contract.

## Relationships

- references: `architecture-containers-agent-runtime` — the `buzz-acp` /
  `buzz-agent` / `buzz-dev-mcp` harness composition this capability launches
  onto a remote substrate. The harness's own conversational and connection
  behavior is unchanged by where it runs; this capability only changes what
  launches it and where.

## Scope and omissions

**This node covers** the backend-provider capability at the level a product
stakeholder would recognize it: what it lets a user do (run a managed agent
somewhere other than their own machine), the shape of the provider contract
that makes a substrate pluggable (discovery, `info`/`deploy` over
stdin/stdout, no persistent management channel after deploy), the security
posture that makes handing a provider binary the agent's private key
tractable (redaction, no secrets in `provider_config`, staged pre-secret
negotiation), and its current maturity as checked directly against this
node's cited revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The provider protocol's full normative detail (invariants I1-I5, the deploy reconciliation state machine, the Kubernetes binding's pod/secret/GC shape) | `docs/remote-agents.md` |
| The relay's own Kubernetes deployment | `architecture-deployment-kubernetes` |
| The step-by-step deploy flow | a future flow-shaped node (not yet drafted) |
| The desktop UI/command surface for configuring a backend | a future interface-shaped node (not yet drafted) |
| Kubernetes RBAC, namespace isolation, secret-at-rest encryption | cluster-operator concern; explicit non-goal of the governing spec |
| sprout-backend-blox's internal behavior | `squareup/sprout-backend-blox` (separate repository, not evidenced here) |

**Expected but not verified when this node was written:**
- Whether the remaining "Known Defects" in `docs/remote-agents.md` (the
  harness inactivity reaper, the pinned clean-exit exit-code contract, the
  shutdown-tail grace budget, the Windows `.exe`-suffix discovery bug, and the
  cleared-numeric-field coercion gap) are still open at this node's cited
  revision — only two of the eight listed defects were independently checked
  against current code for this node.
- Whether `crates/buzz-backend-kubernetes`'s test suite currently passes end
  to end (cluster-dependent conformance beyond the static wire fixtures was
  not run while drafting this node).
- Any detail of sprout-backend-blox's own implementation, since its source is
  outside this repository.
