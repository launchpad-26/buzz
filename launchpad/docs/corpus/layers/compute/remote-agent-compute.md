---
id: layers-compute-remote-agent-compute
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
  - statement: "docs/remote-agents.md specifies the protocol by which Buzz Desktop delegates execution of a managed agent to a 'remote substrate -- any compute environment other than the local machine -- through a backend provider binary,' and states it covers three layers: the provider protocol (a zero-registration plugin contract between the desktop and any executable named buzz-backend-<id>), the remote lifecycle model (how a remote agent is started, observed, stopped and reaped), and the Kubernetes binding (the first conforming provider, realizing the contract as a bare Pod running the sprig image)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1-24"
  - statement: "The document states five invariants -- identity fail-closed, no secrets in configuration, presence-is-status, at-most-one-live-instance, and intentional-termination-is-final -- as holding for the protocol as a whole, not only for the Kubernetes binding."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:26-29"
  - statement: "A scoping note stated to govern the whole document: 'the desktop is one launcher among many. What makes a process a live Buzz agent is a keypair, a NIP-OA auth tag, and a relay URL, handed as environment to the buzz-acp harness; anything that can set that environment and exec the harness -- a bash script, a systemd unit, a CI job, or this document's provider protocol -- is a conforming launcher.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:31-36"
  - statement: "The specification names five principals: Desktop (D, holds the agent's identity and the only UI), Provider (P, an untrusted-except-for-its-job executable buzz-backend-<id> invoked one process per operation), Substrate (S, the remote compute environment P deploys into, opaque to D), Agent (A, a buzz-acp harness process running on S), and Relay (R, 'the only channel that connects D to a running A')."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:71-88"
  - statement: "The defining design axiom, stated as (M1) 'No management channel': after a successful deploy, D holds no persistent management session to A on S, and the desktop-provider protocol contains no substrate API (no status query, no exec, no log fetch, no kill); all post-deploy observation and control flows through R -- status is relay presence, stop is a relay message, reconfiguration is a future re-deploy."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:90-104"
  - statement: "M1 is stated to buy 'protocol surface, not credential absence': ambient substrate credentials may exist on D's machine regardless (the Kubernetes binding uses the user's kubeconfig by design), and D can always re-invoke P; what M1 guarantees is that nothing in the protocol itself -- its persisted records, its wire operations, its stored backend_agent_id -- constitutes or requires a channel to the substrate, at the accepted price of the staleness bound in the presence invariant."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:98-104"
  - statement: "The document draws a three-contract layering that does not all bind at the same layer: (1) the agent/harness contract binds every launcher (a valid keypair, relay URL and auth tag delivered as environment; fail-closed identity; presence publication; owner-verified shutdown; intentional clean exit is terminal to automatic restart) and a bash script exporting the three env vars and exec'ing the harness is stated to be a conforming launcher at this layer 'today, with no code change'; (2) the provider/deployer contract binds provider-managed launches only (the info/deploy operations, the reconciliation loop, at-most-one-live-instance per deploy scope); (3) the binding policy is per-substrate policy such as fingerprints, restart-policy selection and grace budgets, and the document names the systemd/SSH deployer of an in-progress pull request as a second binding that conforms to layers 1-2 and writes its own layer 3, 'not \"non-conforming\" for lacking pods.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:115-149"
  - statement: "The document states plainly that 'the desktop is therefore one launcher among many, and the provider protocol is the desktop's door to substrates, not the only door,' with a Conformance section carrying one checklist per layer."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:147-149"
  - statement: "Invariant I1 (identity fail-closed) requires that no agent is ever launched with an empty or missing private key: 'whatever assembles the harness environment -- desktop, provider, bash script -- MUST refuse rather than launch identityless,' binding at every non-provider launcher as well as at the provider's payload construction."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:173-183"
  - statement: "Invariant I2 (no secrets in configuration) requires the persisted, UI-visible provider_config object to never carry secrets; secrets flow exclusively inside the deploy payload (private_key_nsec, auth_tag, env_vars), which is never persisted by D and never rendered, with a corollary that cluster credentials must come from ambient substrate config, never from provider_config."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:185-198"
  - statement: "Invariant I3 (presence is the status) states D derives a remote agent's live state exclusively from relay presence events self-signed by the agent key (kind:20001, ephemeral), that the deployment axis (deployed/not_deployed) is bookkeeping and not liveness, and that the staleness bound between an abnormal agent death and the relay's presence expiry is 180 seconds (PRESENCE_TTL_SECS, buzz-pubsub/src/presence.rs:16), described as 'the accepted cost of M1.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:200-212"
  - statement: "Invariant I4 (at most one live instance per agent key per deployment scope) is enforced by the deploy reconciliation loop keyed on the derived pubkey; the document states the protocol cannot prevent the same nsec being deployed to two different scopes (two namespaces, two clusters, or remote plus local simultaneously) -- 'deploying one key twice is user error with confusing-but-safe results (both instances answer), not a safety violation.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:228-241"
  - statement: "Invariant I5 (intentional termination is final) states a remote agent 'stops when told, stays down when it stops, and is never silently resurrected,' that 'final' means terminal to automatic supervisor restart only (the owner may always issue a fresh Start), and that lifetime is owner policy rather than a fixed law: an owner may choose no inactivity bound at all, expressed per-binding (the Kubernetes binding's inactivity_seconds: 0)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:243-262"
  - statement: "I5 states the distinction that makes indefinite agents safe as intent versus accident: 'if a supervisor exists, its restart policy MAY revive an abnormal death and MUST NOT revive an intentional clean exit,' stated launcher-neutrally so a launcher with no supervisor at all satisfies the rule vacuously."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:264-272"
  - statement: "Provider discovery is zero-registration: D scans the directory containing the desktop executable, every PATH entry, and ~/.local/bin for executables named buzz-backend-<id>, where the id after the prefix must match [a-z0-9][a-z0-9_-]*; discovery executes nothing."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:307-315"
  - statement: "The Scope and Non-Goals section states the specification deliberately does not specify agent conversational behavior (governed by the ACP harness unchanged by where it runs), malicious-provider containment ('a provider binary receives the agent's nsec by design -- that is its job'; the protocol bounds the desktop's exposure but cannot make a hostile provider safe), substrate security (Kubernetes RBAC, namespace isolation and secret encryption at rest are cluster-operator concerns), or liveness of the substrate itself (reported as structured, fail-closed errors, not formally specified)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:45-68"
  - statement: "Conformance is split into three layers matching the Launchers section: [L1] launcher conformance binds every launcher (desktop, provider-deployed pod, systemd unit, bash script) to five properties -- valid nonempty identity, not suppressing presence or the inactivity knob, forwarding the substrate's termination signal with adequate grace, exiting through the graceful path with a pinned clean-exit contract, and never letting a configured supervisor restart an intentional clean exit; [L2] provider conformance adds the wire-contract and reconciliation-loop obligations for provider-managed launches only; [L3] is the binding's own realization of L1/L2 in its substrate's vocabulary, stated generically as a required obligation of every binding ('its binding documents how it realizes each L2 term on its substrate') before the document specializes L3 to the Kubernetes binding specifically."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1411-1493"
  - statement: "The document's own closing summary states: 'Remote agents extend Buzz's managed-agent model across a deliberately thin boundary: one untrusted binary, two JSON operations, and a relay ... Everything else -- status, control, memory -- was already on the relay, which is why the design holds: the relay was the management plane all along, and the desktop was only ever one of its doors.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1768-1779"
  - statement: "The Kubernetes binding (buzz-backend-kubernetes) is realized by a Rust crate present in this repository at crates/buzz-backend-kubernetes, distributed as a standalone binary distinct from the desktop and relay crates."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/Cargo.toml"
      - "docs/remote-agents.md:991-995"
  - statement: "A second binding of the same provider protocol -- buzz-backend-ssh, a systemd/SSH deployer -- is under active, unmerged development as block/buzz pull request #3449, titled 'feat: remote agents over SSH -- provider contract, buzz-backend-ssh, and where-runs-first,' open at the time this node was written; this corroborates docs/remote-agents.md's own claim that the protocol is designed for more than one substrate, but the PR itself is not a merged or released feature."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "block/buzz#3449 (open pull request, read via `gh pr view 3449 --repo block/buzz`)"
  - statement: "The already-merged corpus node architecture-containers-agent-runtime names 'the remote-agent provider protocol in full (payload schema, five invariants, Kubernetes binding)' as explicitly not covered by its own container-level scope, and assigns ownership of that subject to docs/remote-agents.md directly -- the same primary source this node draws its own claims from."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "The already-merged corpus node architecture-deployment-kubernetes states directly that 'buzz-backend-kubernetes is a separate crate -- a Kubernetes backend provider that lets Buzz's agent harness launch remote coding agents as their own pods -- and is a distinct compute-provisioning concern from the relay's own deployment topology documented in this node, so it is deliberately out of scope here rather than folded in,' drawing the identical boundary line this node sits on the other side of."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "No corpus node with type: layers exists on origin/launchpad at the recorded revision, and no id in the layers-compute-* family besides this node's own exists there either, confirmed by git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus immediately before this front matter was finalized; the five sibling layers/compute/* documents from the same #611 batch (including kubernetes-provider.md, issue #1042) are drafted on other branches and are not valid relationships targets today."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no layers/ directory present"
relationships:
  - type: references
    target: architecture-context-ai-agent
  - type: references
    target: architecture-containers-agent-runtime
  - type: references
    target: architecture-deployment-kubernetes
---

# Remote agent compute

Remote agent compute is the umbrella concept, not a description of any one binding: it
names the general capability for a Buzz-managed AI agent's harness process to run away
from Buzz Desktop's own machine -- on a Kubernetes pod, and (in active but unmerged
development) over SSH to a systemd unit, or on any future substrate a conforming
provider targets -- while the desktop keeps only a thin, revocable relationship to it.
This node is the corpus's single canonical entry point for that idea; it defines the
concept, states the invariants every binding shares, and explicitly declines to
re-describe any one binding's own mechanics.

## Definition

**Remote agent compute** is the design under which a Buzz-managed agent's `buzz-acp`
harness process runs on a compute substrate other than the machine running Buzz
Desktop, reached through a small, untrusted, zero-registration **provider binary**
(named `buzz-backend-<id>`) that Desktop discovers on its `PATH` and invokes as one
process per operation, and governed by a **deliberate absence of a persistent
management channel** from Desktop to the running agent: once deployed, Desktop's only
window onto the agent is the same Nostr relay every other Buzz client uses.

Three things this definition deliberately keeps separate, because each is easy to
collapse into the others:

- **The protocol is not the binding.** `docs/remote-agents.md` specifies a provider
  protocol (discovery, two JSON operations -- `info` and `deploy` -- and a
  reconciliation loop), a remote lifecycle model (five invariants every binding must
  honor), and, as one instance of both, the Kubernetes binding realized by the
  `buzz-backend-kubernetes` crate in this repository. This node documents the first
  two; the Kubernetes binding's own pod shape, image pinning, Secret lifecycle and
  garbage collection belong to a separate, binding-specific corpus node (see
  *Boundaries and non-goals*).
- **"Remote" is a substrate distinction, not a trust distinction.** The specification's
  own scoping note states the desktop is "one launcher among many": what makes a
  process a live Buzz agent is a keypair, a NIP-OA auth tag and a relay URL handed as
  environment to the harness, and *any* mechanism that can set that environment and
  `exec` the harness -- a bash script, a systemd unit, a CI job, or a provider binary --
  is a conforming launcher. The Kubernetes and (in-progress) SSH bindings are two
  concrete instances of "remote"; a hand-launched process on a machine other than
  Desktop's is a third, conforming today with no code change.
- **No management channel is the design constraint everything else follows from.**
  After a successful deploy, Desktop holds no exec, log-fetch, status-query or kill
  capability against the remote process. Status is relay presence; stop is a relay
  message; reconfiguration is a future re-deploy. The specification's own closing line
  states the consequence directly: "the relay was the management plane all along, and
  the desktop was only ever one of its doors."

## Visual aid

```mermaid
flowchart LR
    subgraph desktop ["Buzz Desktop (D)"]
        UI["UI + agent record\n(nsec in OS keyring)"]
    end

    subgraph provider_boundary ["Untrusted boundary"]
        P["Provider binary\nbuzz-backend-&lt;id&gt;\n(e.g. buzz-backend-kubernetes)"]
    end

    subgraph substrate ["Substrate (S) -- opaque to D"]
        A["Agent (A)\nbuzz-acp harness\n+ ACP agent process"]
    end

    R[["Relay (R)\nthe only channel D<->A"]]

    UI -- "info / deploy\n(one process per op,\nJSON stdin/stdout)" --> P
    P -- "provisions" --> A
    A -- "presence (kind:20001),\n!shutdown, all state" <--> R
    UI -- "status = relay presence\nstop = relay message\n(no direct channel to A or S)" --> R
```

The diagram shows the shape every binding shares: Desktop never speaks to the
substrate or the agent directly. The provider is invoked once per operation and then
exits; everything that happens on the substrate afterward is invisible to Desktop
except through the relay.

## Background

The document that defines this concept, `docs/remote-agents.md`, states its own
governing complexity budget: "the complexity budget is spent in this document, not in
the code" -- each of the five invariants is enforced by one small, boring mechanism (a
refusal at payload construction, a key-shape validator, an ephemeral event the agent
already publishes, a name-plus-annotation compare, a timer firing an existing shutdown
channel) rather than by heavier machinery such as Leases, controllers or a genuine
management channel. Where a richer guarantee would have required that machinery, the
specification either found a name-and-timestamp argument that made it unnecessary, or
dropped the property and said so explicitly in its Non-Goals. This is presented as a
deliberate design stance, not an accident of scope: no management channel is treated as
the one property expensive enough, and central enough, that it is worth stating as a
formal design axiom (M1) rather than an implementation detail.

The reason "no management channel" is survivable at all is that the relay was already
the source of truth for everything else in Buzz -- messages, presence, reactions,
memory. Remote agent compute does not introduce a second source of truth for a remote
agent's state; it reuses the one the whole platform already depends on, at the cost of
a bounded staleness window (I3's 180-second presence bound) rather than the
instantaneous view a direct management channel would have provided.

## Use cases

- **Deciding where a managed agent's harness process should live.** An operator or
  power user choosing between "run this agent as a local Desktop-managed subprocess"
  and "run this agent on a substrate away from my machine" needs this concept to
  understand what changes (no direct control channel, presence-only status, a trust
  decision about the provider binary) and what does not (the ACP harness's
  conversational behavior is unchanged by where it runs).
- **Writing or evaluating a new provider binding.** Anyone building a `buzz-backend-<id>`
  executable for a substrate the Kubernetes binding does not cover -- the in-progress
  SSH/systemd binding is the live example -- needs the invariants and the three-layer
  conformance split (agent/harness, provider/deployer, binding policy) stated here
  before descending into any one substrate's mechanics.
- **Reasoning about the security boundary a provider crosses.** Because a provider
  binary is handed the agent's private key by design, understanding this concept is a
  prerequisite to understanding why the protocol's guarantees are about bounding
  Desktop's exposure to a hostile provider, not about making a hostile provider safe --
  a distinction the specification states as an explicit non-goal rather than an
  oversight.
- **Diagnosing "why does the agent's status look wrong."** Because status is derived
  exclusively from relay presence with a bounded staleness window, an operator seeing a
  stale-online remote agent needs this concept -- not the Kubernetes binding's pod
  internals -- to understand that the window is a known, bounded cost of the
  no-management-channel design, not a bug specific to one substrate.

## Comparison

At the recorded revision, exactly one binding of this protocol is merged into this
repository (Kubernetes, `buzz-backend-kubernetes`), so there is no comparison to draw
between shipped alternatives yet. One further binding is visible in active but
unmerged development (`buzz-backend-ssh`, block/buzz#3449) as a second conforming
instance of the same protocol on a different substrate. This section is deliberately
left without a comparison table rather than forcing one against an unmerged pull
request's design, which could drift or be abandoned before landing.

## Related resources

See `relationships` in this node's front matter for the corpus nodes this concept sits
beside:

- `architecture-context-ai-agent` -- the system-context view of the AI Agent actor,
  including the "one launcher among many" framing this node also draws on.
- `architecture-containers-agent-runtime` -- the container-level view of the agent
  runtime (`buzz-acp`, `buzz-agent`, `buzz-dev-mcp`, `sprig`), which names the
  remote-agent provider protocol as explicitly out of its own scope and assigns it to
  the same primary source this node documents.
- `architecture-deployment-kubernetes` -- the relay's own Kubernetes deployment
  topology, which explicitly and independently excludes `buzz-backend-kubernetes` /
  remote agent compute as "a distinct compute-provisioning concern," drawing the same
  boundary line from the other side.

The Kubernetes binding's own canonical document (a separate, not-yet-merged corpus
node, tracked as issue #1042) is deliberately not linked here as a `relationships`
target -- see *Boundaries and non-goals*.

## Boundaries and non-goals

**This node covers** the umbrella concept of remote agent compute: what "remote" means
in this specification, why the design forgoes a management channel, the five
invariants (I1-I5) that bind across any binding, and the three-layer conformance split
(agent/harness contract, provider/deployer contract, binding policy) that states which
obligations apply to which kind of launcher.

**It deliberately does not cover, and a reader looking for these should go
elsewhere:**

| Not covered here | Owned by |
|---|---|
| The Kubernetes binding's own mechanics: cluster auth, namespace/image handling, the pod shape, the entrypoint and launch ABI, Secret lifecycle and garbage collection, `provider_config`'s v1 field set | `docs/remote-agents.md`'s own "The Kubernetes Binding" section directly, and the not-yet-merged corpus node for issue #1042 (`layers/compute/kubernetes-provider.md`) once it lands -- not linked here today because its `id` does not exist on `origin/launchpad` yet (see the ledger's `git_ls_tree` entry) |
| The full wire contract for `info` and `deploy` (payload field lists, the pre-secret negotiation gate, the deploy state machine's per-row reconciliation rules) | `docs/remote-agents.md`'s "Provider Protocol" and "Deploy State Machine" sections directly; a candidate for its own procedure- or interface-shaped corpus node, not filed as of this writing |
| The ACP harness's conversational behavior itself (what an agent does with a prompt once it receives one) | `architecture-containers-agent-runtime`, governed unchanged by where the harness runs, per the specification's own Non-Goals |
| Malicious-provider containment and substrate security (Kubernetes RBAC, namespace isolation, secret-at-rest encryption) | Explicitly out of scope for the specification itself, per its own Non-Goals section; not a gap this node is positioned to close |
| The Auto-Stop inactivity mechanism's exact env-var contract and the harness-side Known Defects (the unimplemented reaper, the unpinned clean-exit contract, the shutdown-tail overrun) | `docs/remote-agents.md`'s "Auto-Stop" and "Known Defects" sections directly -- these are implementation-status claims that will change quickly and are exactly the kind of volatile detail this node's own corpus (per `standards/atomicity.md`'s boundary-case guidance on a stable concept versus a volatile detail) should not restate |

**Why the Kubernetes binding is named here at all, without being described.** A reader
arriving at "remote agent compute" needs to know at least one binding exists and is
shipped, or the concept reads as entirely hypothetical. This node names
`buzz-backend-kubernetes` and cites where its crate lives, and stops there -- every
claim about *how* it works is deferred to its own canonical node.

## Scope and omissions

**Expected but not verified when this node was written:**

- **The full wire-level `deploy` payload schema and the three-tier environment
  precedence rules (`launch.policy_env` / `launch.env` / authoritative tier) were read
  in the primary source but are not restated here**, deliberately -- they are
  provider-protocol mechanics, not the umbrella concept, and a future
  interface-shaped corpus node for the protocol itself is the more natural home for
  them than either this node or the Kubernetes-specific one.
- **Whether the in-progress SSH/systemd binding (block/buzz#3449) will land with the
  same invariants this node describes, or whether review changes them, is unverified**
  -- it is cited here only as TEAM_KNOWLEDGE corroborating that the protocol is
  designed for more than one substrate, not as a FACT about a shipped capability.
- **The eight items `docs/remote-agents.md` itself lists under "Known Defects at
  `28ae6cd21`"** (for example, that the deploy path does not yet check
  `protocol_version` before sending secrets, and that the inactivity reaper does not
  yet exist in the harness) were read but are not enumerated in this node's body; they
  describe implementation status at one commit and are the kind of volatile detail this
  concept-level node avoids restating, per the boundary this node draws against a
  "stable concept versus volatile detail" split.
- **No corpus node yet exists for the provider protocol's own wire contract** (as
  distinct from this umbrella concept and from the Kubernetes binding). Whether that
  becomes its own node, or is folded into a future interfaces-events-typed node, was
  not decided while writing this one, per this task's own instruction not to resolve a
  second concept discovered mid-draft -- named here as a candidate follow-up rather
  than filed.
