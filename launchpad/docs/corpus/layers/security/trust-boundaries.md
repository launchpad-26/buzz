---
id: layers-security-trust-boundaries
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
  - statement: "node.schema.json's type enum includes layers, and this node's front matter uses it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "At the recorded revision, launchpad/docs/corpus/layers/security/ does not exist on origin/launchpad: a directory listing of the checked-out worktree (branched directly from origin/launchpad) returns no such directory, and this worktree carries no uncommitted changes that would explain its absence."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/layers') -> no layers/security subtree at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #1181 (parent PRD #607) commissions this node as the single canonical document for launchpad/docs/corpus/layers/security/trust-boundaries.md, with a Definition of Done requiring it to define scope, assumptions, assets/values and trust boundaries; include or link a data-flow view and enumerate threats systematically; link mitigations/controls and verification evidence; and record residual/accepted risks and open issues without presenting proposals as implemented controls."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1181 definition of done"
  - statement: "Five sibling issues under the same parent PRD #607 each commission one specific trust-boundary node this index is meant to tie together, and all five were open (not yet merged) at the checked revision: #1168 (layers/security/admin-boundary.md), #1169 (layers/security/cryptographic-boundary.md), #1171 (layers/security/provider-boundary.md), #1172 (layers/security/relay-boundary.md), and #1179 (layers/security/tenancy-boundary.md)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1168, #1169, #1171, #1172, #1179 (issue titles, bodies and open state, read directly)"
  - statement: "Two further sibling issues under parent PRD #607 commission documents distinct in kind from this index rather than in overlapping subject: #1182 (layers/security/trust-model.md, WHO/WHAT is trusted at each level) and #1180 (layers/security/threat-model.md, a STRIDE-structured attacker-perspective analysis built from the corpus threat-model template). Neither existed on disk at the checked revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1182, #1180 (issue titles and bodies, read directly)"
  - statement: "docs/multi-tenant-relay.md states a community as the tenant/security boundary that a shared relay deployment enforces, and separately states that a Buzz relay process was the security boundary before that model: 'Today a Buzz relay process is the security boundary ... The model proven here demotes the relay process to stateless compute and elevates a new community entity to the tenant/security boundary.'"
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "crates/buzz-relay/src/tenant.rs implements bind_community, the single seam that resolves a connection's Host header to a CommunityId before any tenant-scoped handling runs, and fails closed (denies) on an unmapped host, an empty/whitespace host, or a resolver lookup error alike, with no fallback or default tenant on any of those paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "The merged corpus node architecture-principles-community-is-security-boundary documents this same invariant in full, citing bind_community, 24 call sites across 11 files that invoke it before tenant-scoped work begins, the communities table's unique host index, and the crates/buzz-test-client/tests/conformance_multitenant.rs A/B isolation suite as its verification mechanism."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
  - statement: "crates/buzz-relay/src/router.rs's WebSocket handler calls bind_community (line 308) before WebSocketUpgrade::from_request (line 323), so no frame is read on a connection that failed to bind to a community; crates/buzz-relay/src/handlers/auth.rs implements the NIP-42 AUTH handler (handle_auth) that verifies the challenge-response signature before any database lookup runs, per its own comment 'Pure NIP-42 verification -- crypto only, no DB lookups.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:308"
      - "crates/buzz-relay/src/router.rs:323"
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "crates/buzz-core/src/verification.rs's verify_event checks both the event-id hash (recomputed from pubkey, created_at, kind, tags and content) and the Schnorr signature, returning a distinct VerificationError for each failure mode, and its own doc comment states it is CPU-bound and must be called through tokio::task::spawn_blocking rather than directly on an async task."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
  - statement: "verify_event is called on the event-ingest path in crates/buzz-relay/src/handlers/ingest.rs and twice in crates/buzz-relay/src/handlers/event.rs, in every case wrapped in spawn_blocking, before the event is treated as authentic input to any downstream handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1990"
      - "crates/buzz-relay/src/handlers/event.rs:805"
      - "crates/buzz-relay/src/handlers/event.rs:960"
  - statement: "docs/admin/README.md documents a private, deployment-wide read-only moderation dashboard activated by BUZZ_ADMIN_HOST, requires the configured admin host and matching browser origin, and states plainly: 'The human trust boundary remains the private admin ingress. VPN/source-IP admission is not per-operator identity. Anyone admitted to the dashboard can read attachments for feedback records they can access. Per-person attribution or revocation requires authenticated operator identity at ingress/application level; this endpoint deliberately does not claim to provide it.'"
    entry_class: FACT
    evidence:
      - "docs/admin/README.md"
  - statement: "docs/remote-agents.md specifies a provider protocol boundary between Buzz Desktop and a backend provider binary (buzz-backend-<id>): Desktop is trusted, Substrate is opaque to Desktop, and Provider is stated explicitly as 'Untrusted by D for everything except the job it is explicitly given (deploying the agent, which requires the key)' with 'All of P's output ... treated as hostile.' The document's own framing states naming the trust boundary is part of the claim, the same posture docs/git-on-object-storage.md and docs/multi-tenant-relay.md state for their own proofs."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md states five invariants for the remote-agent lifecycle -- identity fail-closed, no secrets in configuration, presence-is-status, at-most-one-live-instance, and intentional-termination-is-final -- and states as an explicit non-goal that the protocol cannot make a hostile provider safe, only bound the desktop's exposure to one (discovery-only resolution, output caps, secret redaction, an explicit UI trust warning)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "crates/buzz-agent/README.md's Security Model section states a distinct trust boundary for the agent harness itself: 'The trust boundary is the operator who launched the agent. The harness, MCP server binaries, and API keys are all trusted. Untrusted input -- model output, tool results, prompts -- is bounded,' backed by a table of concrete mechanisms (stdout single-consumer channel, MCP child environment whitelist, process-group teardown on transport break, frame/response/session size caps)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:294"
  - statement: "docs/git-on-object-storage.md states that its safety proof holds only relative to three explicitly named object-store axioms, each admitted per-backend by an empirical conformance gate rather than proven universally, and frames this the same way as docs/multi-tenant-relay.md: 'Provably sound without naming the trust boundary does not survive scrutiny.'"
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "docs/multi-tenant-relay.md's own Scope and Non-Goals names a specific, unclosed boundary carve-out: 'Physical-resource isolation. Communities share an id space, time partitions, a connection pool, and a CPU. The proof covers the logical interface; bandwidth-limited physical channels are a named, explicit carve-out (§Isolation Boundary, class C1).'"
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "The merged corpus node architecture-principles-fail-closed-boundaries documents that authorization and tenant-boundary decisions across the relay -- host-to-community resolution, the pubkey-allowlist gate, the moderation ban-state check at both connection auth and ingest, and reaction-target channel derivation -- deny rather than admit when the underlying lookup errors, and names docs/spec/MultiTenantRelay.tla and crates/buzz-relay/src/conformance/mod.rs as the two mechanisms that verify the host-binding instance of that pattern formally and at runtime."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/fail-closed-boundaries.md"
  - statement: "The merged corpus node architecture-principles-subsystem-isolation documents a distinct boundary among six in-process subsystem crates (buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit, buzz-workflow) orchestrated by buzz-relay, and reports as fact that two of the six currently violate the stated no-cross-call invariant (buzz-pubsub calls buzz-auth; buzz-workflow calls buzz-db)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/subsystem-isolation.md"
  - statement: "The subsystem-isolation boundary between in-process service crates is architecturally significant but is not itself a trust boundary in this node's sense, because no principal's authority or privilege level changes when a call crosses it -- every subsystem crate runs inside the same relay process at the same trust level, orchestrated by the same buzz-relay AppState, whereas every boundary this node enumerates below has a principal on one side that is differently authorized, differently authenticated, or differently trusted than the principal on the other."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/principles/subsystem-isolation.md"
      - "ARCHITECTURE.md:97"
    confidence: 0.75
  - statement: "The five sibling boundary docs #1168/#1169/#1171/#1172/#1179 map onto five of the process boundaries this node found evidence for at the checked revision (admin ingress, cryptographic verification, remote-agent provider/substrate, the relay's external network door, and community/tenancy), while at least two further trust-relevant boundaries observed in the codebase -- the agent-harness operator boundary documented in crates/buzz-agent/README.md, and the object-storage conformance-gate boundary documented in docs/git-on-object-storage.md -- are not assigned to any of PRD #607's currently filed child tasks."
    entry_class: INFERENCE
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/1168"
      - "https://github.com/launchpad-26/buzz/issues/1169"
      - "https://github.com/launchpad-26/buzz/issues/1171"
      - "https://github.com/launchpad-26/buzz/issues/1172"
      - "https://github.com/launchpad-26/buzz/issues/1179"
      - "crates/buzz-agent/README.md:292"
      - "docs/git-on-object-storage.md"
    confidence: 0.7
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: references
    target: architecture-principles-subsystem-isolation
---

# Security trust boundaries: index

An enumeration and map of every point in Buzz where a request, event, or process
crosses from one trust level to another. This node answers "where are the seams,
and what changes at each one" for a reader who needs the whole picture before
opening any one boundary's own document. It does not itself decide who is trusted
at each level (`layers-security-trust-model`, issue #1182) and it does not run a
structured attacker-perspective analysis of any one boundary (`layers-security-threat-model`,
issue #1180, built from the corpus's `threat-model` template). Both of those, and
the five specific boundary documents this index ties together, are separate tasks
under the same parent PRD (#607) and none had merged at the revision this node was
checked against — see *Scope and omissions* for what that means for this node's
`relationships`.

## Purpose and scope

**This node covers:** every process boundary in the current architecture where the
trust level of the data or the authority of the acting principal changes, named and
briefly described, with a pointer to its expected canonical corpus node and to the
primary source this index verified it against.

**It does not cover:**

- **Who or what is trusted at each level**, and why — that is `layers-security-trust-model`
  (issue #1182)'s subject.
- **A systematic, STRIDE-structured threat enumeration** for any one boundary — that
  is `layers-security-threat-model` (issue #1180)'s subject, built against the
  corpus's `corpus-template-threat-model` template.
- **The full internal detail of any one boundary** — the specific mitigations,
  failure modes, and verification evidence for, say, the admin ingress or the
  provider protocol belong in that boundary's own node (`layers-security-admin-boundary`,
  `layers-security-cryptographic-boundary`, `layers-security-provider-boundary`,
  `layers-security-relay-boundary`, `layers-security-tenancy-boundary`). This index
  names each boundary's controls only at the depth needed to justify that a real,
  evidenced boundary exists there — deep coverage belongs in the boundary's own node.

## Assumptions and protected assets

The boundaries below exist to protect four kinds of asset, stated once here so each
row in *Boundary enumeration* can name which it primarily protects rather than
repeating the reasoning:

| Asset | What crossing the wrong boundary would expose or corrupt |
|---|---|
| **Tenant data and side effects** | One community's messages, channel membership, workflow state, and audit trail becoming observable or actionable from another community. |
| **Agent and operator private keys** | An `nsec` (a remote agent's signing key, handed to a provider binary by design) or an admin operator's session being exposed to, or exercised by, a party that should not hold it. |
| **Event authenticity** | The relay or a client treating unsigned or tampered content as if it had been produced by the pubkey it claims. |
| **Deployment-operational state** | Moderation reports, feedback, and configuration reachable only through the admin surface, and the substrate a remote agent actually runs on. |

**Assumption this index makes and states rather than silently relies on:** every
boundary below is a *documented* seam with at least one enforcement point this node
verified in code or in a primary-source specification document at the checked
revision. This index does not assert that no other, undocumented trust boundary
exists in the system — see *Scope and omissions* for what was and was not checked
to arrive at the list below.

## Data-flow view

Every edge below is a boundary crossing this node names in *Boundary enumeration*,
with the same primary-source citation backing it there.

```mermaid
flowchart LR
  CLIENT["Client (desktop / mobile / CLI / web)"]
  RELAY_DOOR["Relay network door\n(router.rs, handlers/auth.rs)"]
  CRYPTO["Cryptographic verification\n(buzz-core::verification::verify_event)"]
  TENANT["Community / tenancy binding\n(tenant.rs::bind_community)"]
  RELAY_CORE["Relay-scoped handling\n(community-scoped data + side effects)"]
  ADMIN_OP["Admin operator, on VPN / allow-listed source IP"]
  ADMIN["Admin ingress\n(BUZZ_ADMIN_HOST, docs/admin/README.md)"]
  DESKTOP["Buzz Desktop\n(holds agent nsec)"]
  PROVIDER["Provider binary\nbuzz-backend-<id> (untrusted)"]
  SUBSTRATE["Substrate\n(opaque compute, e.g. Kubernetes)"]
  AGENT["Remote agent harness\n(buzz-acp, operator-trusted)"]

  CLIENT -- "unauthenticated network request" --> RELAY_DOOR
  RELAY_DOOR -- "NIP-42 challenge-response" --> RELAY_CORE
  CLIENT -- "signed Nostr event" --> CRYPTO
  CRYPTO -- "verified authentic event" --> RELAY_CORE
  RELAY_DOOR -- "Host header resolution" --> TENANT
  TENANT -- "bound CommunityId" --> RELAY_CORE
  ADMIN_OP -- "private ingress, host+origin match" --> ADMIN
  ADMIN -- "read-only, tenant-scoped queries" --> RELAY_CORE
  DESKTOP -- "hands nsec, invokes deploy" --> PROVIDER
  PROVIDER -- "opaque deploy call" --> SUBSTRATE
  SUBSTRATE -- "runs" --> AGENT
  AGENT -- "presence, relay-authenticated" --> RELAY_CORE
```

## Notation legend

| Shape | Meaning |
|---|---|
| Rectangle | A principal or process — a person, a client, a relay subsystem, a provider binary, or a substrate. |
| Labeled arrow | A trust-boundary crossing: the label names what travels across it and, where relevant, what changes (unauthenticated → authenticated, claimed → verified, desktop-trusted → provider-untrusted). |

Mermaid has no dedicated data-flow-diagram or trust-boundary notation (confirmed
against Mermaid's current syntax-reference page while a sibling template task
researched this same gap); this diagram approximates one with plain flowchart
nodes and edges rather than inventing new syntax.

## Boundary enumeration

| Boundary | Expected corpus id | What changes crossing it | Primary source verified | On disk at this revision |
|---|---|---|---|---|
| **Relay network door** — unauthenticated network request → NIP-42-authenticated connection | `layers-security-relay-boundary` (#1172) | Trust: an anonymous TCP/TLS peer becomes a connection bound to a verified pubkey (or remains unauthenticated for the surfaces that permit it). | `crates/buzz-relay/src/router.rs` (WebSocket upgrade gate), `crates/buzz-relay/src/handlers/auth.rs` (`handle_auth`, NIP-42) | No |
| **Cryptographic verification** — claimed event → verified event | `layers-security-cryptographic-boundary` (#1169) | Authenticity: content asserted to come from a pubkey becomes content whose id hash and Schnorr signature were checked. | `crates/buzz-core/src/verification.rs` (`verify_event`), called from `handlers/ingest.rs` and `handlers/event.rs` | No |
| **Community / tenancy binding** — connection → tenant-scoped context | `layers-security-tenancy-boundary` (#1179) | Scope: a bare connection becomes a `TenantContext` that is the sole authority for every downstream tenant-scoped read or write. | `crates/buzz-relay/src/tenant.rs` (`bind_community`); `docs/multi-tenant-relay.md`; merged node `architecture-principles-community-is-security-boundary` | No |
| **Admin ingress** — deployment operator → moderation/feedback read access | `layers-security-admin-boundary` (#1168) | Privilege: network admission (VPN / source-IP allow-list) becomes access to deployment-wide, cross-tenant moderation and feedback data — without per-operator identity. | `docs/admin/README.md` | No |
| **Provider / substrate** — Desktop-held agent key → remote compute environment | `layers-security-provider-boundary` (#1171) | Custody: an agent's private key, held only by the trusted Desktop, is handed to an explicitly untrusted provider binary that deploys it onto an opaque substrate. | `docs/remote-agents.md` (`§Provider Protocol`, `§System Model`) | No |

Two further trust-relevant boundaries were found in the codebase during this
survey and are **not** assigned to any of PRD #607's five currently filed child
tasks (see the INFERENCE entry in this node's evidence ledger):

| Boundary | Expected corpus id | What changes crossing it | Primary source verified | On disk at this revision |
|---|---|---|---|---|
| **Agent-harness operator boundary** — the operator who launched an agent → the model/tool-call loop that operator's agent runs | Not yet assigned a task | Privilege: the harness, MCP server binaries, and API keys are trusted; model output, tool results, and prompts are treated as untrusted input and bounded. | `crates/buzz-agent/README.md` (`§Security Model`) | No — no corpus task found |
| **Object-storage conformance gate** — git ref/pack data → an S3-compatible backend | Not yet assigned a task | Durability/consistency: the protocol's safety proof holds only relative to three stated object-store axioms, each admitted per-backend by an empirical conformance probe rather than proven universally. | `docs/git-on-object-storage.md` | No — no corpus task found |

**Not a trust boundary in this node's sense:** the boundary between `buzz-relay`
and the six in-process subsystem crates it orchestrates (`buzz-db`, `buzz-auth`,
`buzz-pubsub`, `buzz-search`, `buzz-audit`, `buzz-workflow`), documented in the
merged node `architecture-principles-subsystem-isolation`. Every crate on both
sides of that boundary runs inside the same relay process at the same trust
level — nothing crossing it becomes more or less authenticated, authorized, or
privileged. It is a real architectural boundary and is cited here because a
reader assembling "every boundary in the system" from `ARCHITECTURE.md` alone
would reasonably expect to find it; it is excluded from the enumeration table
above because its crossing changes no principal's trust level. See the
INFERENCE entry in this node's evidence ledger for the reasoning.

## Threat categories (survey level)

A STRIDE-labelled summary of the threat category each boundary is most exposed
to, at survey depth — enough to show every boundary has been considered, not a
row-by-row attack enumeration. `layers-security-threat-model` (#1180) is where a
full STRIDE table with per-row evidence belongs, per the corpus's own
`threat-model` template requirement that a diagram element have a matching
threat-table row.

| Boundary | Primary STRIDE exposure | Why |
|---|---|---|
| Relay network door | Spoofing, Denial of Service | Pre-authentication surface; anyone can attempt a connection or a NIP-42 challenge response. |
| Cryptographic verification | Spoofing, Tampering | Its entire purpose is rejecting exactly these two categories before content is trusted. |
| Community / tenancy binding | Information Disclosure, Elevation of Privilege | A defeated binding would let one community observe or act on another's data. |
| Admin ingress | Information Disclosure, Repudiation | Network-level admission with no per-operator identity means an admitted read cannot be attributed to a specific person. |
| Provider / substrate | Tampering, Information Disclosure, Elevation of Privilege | The provider is handed a private key by design; a hostile or compromised provider can act as the agent it was given custody of. |

## Mitigations and verification evidence

Each row names the strongest verification mechanism this node found for that
boundary at the checked revision, not an exhaustive catalogue of every control —
the boundary's own future node owns the full list.

| Boundary | Control | Verification evidence |
|---|---|---|
| Community / tenancy binding | `bind_community` fails closed on unmapped host, empty host, and lookup error alike; called before any tenant-scoped work at every request surface. | `docs/spec/MultiTenantRelay.tla`'s `Inv_HostBindingFence` and `Inv_ResolutionFence`; the runtime conformance harness `crates/buzz-relay/src/conformance/mod.rs`; the `#[ignore]`-gated A/B suite `crates/buzz-test-client/tests/conformance_multitenant.rs` (per the merged `architecture-principles-fail-closed-boundaries` and `architecture-principles-community-is-security-boundary` nodes — neither mechanism was re-run while authoring this index). |
| Relay network door | `bind_community` runs before `WebSocketUpgrade::from_request`; NIP-42 signature verification runs before any database lookup. | Unit tests in `crates/buzz-relay/src/tenant.rs`'s own `tests` module (cited by the merged `architecture-principles-fail-closed-boundaries` node as 10 passed, 0 failed at a prior revision — not re-run here). |
| Cryptographic verification | `verify_event` checks the event-id hash and Schnorr signature independently, with a distinct error per failure mode. | `crates/buzz-core/src/verification.rs`'s own `#[cfg(test)]` module, including `rejects_tampered_id` (read directly; not executed while authoring this index). |
| Admin ingress | Private-ingress binding on exact `Host` + browser origin; feedback-attachment reads re-derive the community from server-owned provenance and re-check host resolution before serving bytes. | `docs/admin/README.md`'s own stated behavior; no automated conformance suite for the admin surface was found during this survey. |
| Provider / substrate | Discovery-only resolution, output size caps, secret redaction, anti-secret config validation, and an explicit UI trust warning bound (not eliminate) the desktop's exposure to a provider it does not otherwise trust. | `docs/remote-agents.md`'s stated invariants (`§Invariants`) and its own `§Conformance` and `§Known Defects` sections — not independently re-verified for this index. |

**This table does not claim any of the cited verification mechanisms were run
while authoring this node.** Every row states explicitly what was read versus
executed. A `FACT` in this node's own ledger established that the cited source
exists and says what is quoted; it did not re-run a test suite, TLA+ model
checker, or conformance harness.

## Residual and accepted risks, and open issues

Stated as what they are — proposed, planned, or explicitly accepted — never as
implemented controls this node has verified:

- **The provider boundary is fundamentally, not incidentally, untrusted.**
  `docs/remote-agents.md` states directly that "Malicious-provider containment"
  is out of scope for its own specification: a provider binary is handed the
  agent's private key by design, and the protocol bounds the desktop's
  exposure without claiming to make a hostile provider safe. This is a stated,
  accepted risk in the primary source, not a gap this index is raising for the
  first time.
- **The admin ingress has no per-operator attribution or revocation today.**
  `docs/admin/README.md` states this as a property of the current design
  ("Anyone admitted to the dashboard can read attachments for feedback records
  they can access"), not a defect being tracked for a fix in this node's
  evidence.
- **Physical-resource isolation between communities is a named, unclosed
  carve-out**, not a proven property: `docs/multi-tenant-relay.md`'s own scope
  states its isolation proof covers the logical interface only, and that
  communities sharing a connection pool and CPU is bandwidth-limited physical
  channel exposure the proof does not close.
- **The subsystem-isolation boundary (excluded from this index's enumeration
  as not a trust boundary) is not fully honored by current code.** The merged
  `architecture-principles-subsystem-isolation` node reports `buzz-pubsub` →
  `buzz-auth` and `buzz-workflow` → `buzz-db` as real, functioning violations
  of the stated no-cross-call rule. Recorded here because a reader building a
  complete picture of the relay's internal seams should know it, even though
  the boundary itself sits outside this node's trust-boundary definition.
- **Two observed trust-relevant boundaries have no assigned corpus task**: the
  agent-harness operator boundary (`crates/buzz-agent/README.md`) and the
  object-storage conformance-gate boundary (`docs/git-on-object-storage.md`).
  Filing tasks for either is not something this documentation task does —
  noted here as an open gap in PRD #607's current child-task set, per the
  INFERENCE entry in this node's ledger.
- **None of the five sibling boundary documents, the trust-model document, or
  the threat-model document exist yet.** This index names their expected
  corpus ids and primary sources; it does not substitute for their content,
  and every "On disk at this revision: No" row in *Boundary enumeration* is a
  currently-open gap in PRD #607's document set, not a claim that the boundary
  itself is unenforced in the running system — the code and specification
  citations in *Mitigations and verification evidence* are this node's
  evidence that each boundary is real regardless of whether its own corpus
  node has been written yet.

## Scope and omissions

**This node covers** the enumeration and a data-flow map of every process
boundary in the current architecture where trust level or acting authority
changes, at a depth sufficient to justify that each is real and evidenced; a
survey-level STRIDE label per boundary; the strongest verification mechanism
found for each; and the residual risks and open documentation gaps this survey
surfaced.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Who/what is trusted at each boundary and why | `layers-security-trust-model` (issue #1182), not yet written |
| A full STRIDE threat table per boundary, with mitigation status and review cadence | `layers-security-threat-model` (issue #1180), not yet written, built against `corpus-template-threat-model` |
| The full internal detail (all controls, all failure modes, full verification) of any one boundary | That boundary's own node — `layers-security-admin-boundary` (#1168), `layers-security-cryptographic-boundary` (#1169), `layers-security-provider-boundary` (#1171), `layers-security-relay-boundary` (#1172), `layers-security-tenancy-boundary` (#1179) — none written yet |
| Whether a corpus task should be filed for the agent-harness operator boundary or the object-storage conformance-gate boundary | Not yet filed as a task at time of writing; a decision for PRD #607's owner |
| The `docs/multi-tenant-relay.md` and `docs/git-on-object-storage.md` formal proofs themselves (axioms, theorems, TLA+/Tamarin models) | Those documents directly; this node cites their scope-and-boundary statements only |
| Fixing the `buzz-pubsub` → `buzz-auth` or `buzz-workflow` → `buzz-db` subsystem-isolation violations | Implementation work, not corpus authorship — see the merged `architecture-principles-subsystem-isolation` node |

**No `relationships` to the five sibling boundary documents, the trust-model
document, or the threat-model document.** `AGENTS.md`'s node-creation step 9
requires a `relationships[].target` to name an id that exists on the branch
being merged into; none of those six ids exist on `origin/launchpad` at the
checked revision (confirmed by directory listing, not assumed), and declaring
one would be a hard validation error on the merge target even though it might
resolve inside this task's own worktree. The three `references` edges this
node does declare — to `architecture-principles-community-is-security-boundary`,
`architecture-principles-fail-closed-boundaries`, and
`architecture-principles-subsystem-isolation` — target nodes confirmed present
on `origin/launchpad` at the checked revision.

**Expected but not verified when this node was written:**

- **None of the verification mechanisms cited in *Mitigations and verification
  evidence* were re-run.** Every row states this explicitly; what this node
  establishes is that the cited source exists and currently says what is
  quoted, read directly, not that the referenced test suite or model checker
  currently passes.
- **This node's survey of "every trust boundary in the system" is not
  exhaustive by construction.** It is bounded by what a targeted search of
  primary-source specification documents (`docs/*.md`), the corpus's own
  merged architecture nodes, and the five already-commissioned sibling issues
  surfaced. A boundary with no corresponding primary-source document and no
  filed issue would not have been found by this method, and this node makes
  no claim that none exists.
- **Whether the two boundaries flagged as unassigned (agent-harness operator,
  object-storage conformance gate) genuinely warrant their own PRD #607 child
  task, versus folding into an existing one once written, was not decided
  here** — it is recorded as an open question for the batch owner.
