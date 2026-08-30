---
id: capabilities-notifications-push-capability
type: capabilities
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
  - statement: "NIP-PL's own abstract defines the push lease as a stored, installation-scoped, expiring authorization asking a push executor to keep a constrained filter active after the client's socket closes and to wake a specific application installation through a platform push transport (APNs, FCM, optionally UnifiedPush) when the filter matches; the wake payload is a fixed, transport-authored reconnect signal that never carries relay-supplied content, and the client fetches authoritative events over ordinary authenticated REQ after waking."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "kind:30350 (the NIP-PL push lease) is registered in the relay's kind table as KIND_PUSH_LEASE."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:109"
  - statement: "The relay's push_lease module validates a kind:30350 event's envelope and NIP-44-encrypted plaintext, and defines PUSH_KINDS = [7, 9, 1059, 40007, 46010] as the allow-list of event kinds eligible to trigger a wake."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs:1-19"
  - statement: "The relay's push_runtime module implements a durable NIP-PL matcher and gateway delivery worker: a matcher that claims due match-queue batches and evaluates filters, and a delivery worker that claims due wakes and sends delivery requests to the gateway, each with its own poll cadence, retry ceiling, and poison-job reap interval."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs:1-40"
  - statement: "buzz-push-gateway exposes seven POST routes under /v1/, including /v1/deliveries/apns as the relay-facing delivery endpoint and six App Attest-authenticated routes (challenges, installations, delegations, delegations/revoke, installations/endpoint, installations/revoke) for client enrollment, delegation, rotation and revocation."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs:739-745"
  - statement: "The gateway's AppProfile enum, as of the recorded revision, has exactly two members -- BuzzIosProduction and BuzzIosSandbox -- so only the iOS/APNs transport profile is implemented server-side today, even though NIP-PL's own abstract names APNs, FCM and UnifiedPush as transport options."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs:12-24"
  - statement: "As of the recorded revision, no mobile (Flutter) or desktop (Tauri) client code in this repository creates, rotates, or revokes a push lease, performs App Attest enrollment, or references kind:30350 -- confirmed by an independent case-insensitive recursive search of mobile/lib and desktop/src for '30350|push_lease|PushLease|kind_push_lease|NIP-PL|nip-pl', which returned no matches."
    entry_class: FACT
    evidence:
      - "grep_recursive_case_insensitive('30350|push_lease|PushLease|kind_push_lease|NIP-PL|nip-pl', paths='mobile/lib desktop/src', ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> no matches"
  - statement: "Root VISION_PROJECTS.md's own 'Capability | Status' table (the corpus's own precedent for a product-level capability catalogue) lists eleven rows and none of them names push notifications, notifications, or wake delivery -- confirmed by reading the table directly, not assumed from its general shape."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-259"
  - statement: "Because no VISION status marker exists for this capability, its maturity claim below rests on code and test evidence read directly for this node (the FACT entries above), not on a citable product-status row the way the capability template's evidence-expectations section prefers when one is available."
    entry_class: INFERENCE
    evidence:
      - "VISION_PROJECTS.md:247-259"
      - "crates/buzz-relay/src/handlers/push_lease.rs:1-19"
      - "crates/buzz-relay/src/push_runtime.rs:1-40"
    confidence: 0.85
  - statement: "Sibling issue #788 exists specifically to document launchpad/docs/corpus/capabilities/notifications/apns.md as its own canonical capability node for the APNs transport profile, distinct from this node's own scope; at the time this node was authored, #788 had not been drafted into any PR, so no capabilities-notifications-apns node id exists in the merged corpus to relate to."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#788 issue body (read directly via gh issue view)"
  - statement: "At the recorded revision, origin/launchpad's corpus tree carries no nodes under launchpad/docs/corpus/capabilities/ at all -- confirmed via git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/capabilities -- so this node's only valid relationship targets are the two already-merged architecture nodes for the push gateway and the push-notification flow, plus the merged capability template."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/capabilities') -> empty"
relationships:
  - type: references
    target: architecture-containers-push-gateway
  - type: references
    target: architecture-flows-push-notification
  - type: implements
    target: corpus-template-capability
---

# Push notifications: capability

Buzz can wake an installed client through a platform push transport when an
event the client is authorized to read arrives while its connection to the
relay is closed, so a user does not have to keep the app open or the socket
connected to learn about new activity. Under NIP-PL (Push Leases), an
installation authorizes a push executor (the user's relay, paired with the
push gateway) to hold a narrow, expiring, encrypted subscription on its
behalf and to trigger a wake through the configured transport when that
subscription matches — never by carrying event content through the
transport itself. The primary actors are the installation (one app install
on one device), the executor (relay + `buzz-push-gateway`), and the platform
transport (currently Apple's APNs). The outcome for the actor holding the
lease is a reconnect signal; the outcome for the user is a timely nudge to
reopen the app and fetch what actually changed over ordinary authenticated
`REQ`.

## Behavioral rules, constraints and variants

- **The wake carries no content.** The push payload is a fixed,
  transport-authored reconnect instruction. No event id, event content,
  ciphertext, or relay-supplied byte ever transits the platform push
  service — a client that receives a wake still has to reconnect and fetch
  before it knows what changed.
- **A lease is scoped, expiring, and revocable.** `kind:30350` events are
  per-installation, NIP-44-encrypted to the executor, and bounded by a
  mandatory `expiration`; the executor stops matching once a lease expires,
  and reinstalling an app or rotating a transport token replaces rather than
  reuses the lease identity.
- **Only push-eligible event kinds trigger a wake.** The relay's allow-list
  (`{7, 9, 1059, 40007, 46010}` at the recorded revision) gates which
  accepted events even enter the match pipeline; a community with no active
  lease pays no matching cost at all.
- **Two independently authenticated trust boundaries carry the capability.**
  Client-to-executor enrollment and lease management use Apple App Attest;
  relay-to-gateway delivery uses a NIP-98 signed request keyed to the
  relay's own identity. Neither boundary is bypassed by the other.
- **Delivery is lossy and best-effort by design, not by defect.** NIP-PL
  does not define delivery receipts or acknowledgement semantics; a dropped,
  suppressed, or duplicate wake never becomes a correctness problem, because
  the relay stays the authoritative source and the client reconciles by
  fetching after any reconnect.
- **The variant actually shipped today is narrower than the protocol
  allows.** NIP-PL's own abstract names APNs, FCM, and optionally
  UnifiedPush as transport profiles; the gateway's `AppProfile` enum
  currently implements only the two iOS/APNs profiles (production and
  sandbox). Android/FCM and UnifiedPush are protocol-defined variants of
  this same capability, not yet built.

## Maturity

**In progress — shipped on the server side, not yet reachable by any real
client.** The relay-side lease acceptance and validation
(`push_lease.rs`), the durable matcher and gateway delivery worker
(`push_runtime.rs`), and the gateway's App Attest-authenticated enrollment
routes and NIP-98-authenticated delivery route
(`buzz-push-gateway/src/http.rs`) all exist and are exercised by their own
module-level tests, per the FACT evidence above. But as of the recorded
revision, neither the Flutter mobile client nor the Tauri desktop client
contains any code that creates, rotates, or revokes a push lease, or
performs App Attest enrollment — confirmed by an independent search of
`mobile/lib` and `desktop/src` that returned no matches for any push-lease
vocabulary. A reader should not infer from the server-side completeness that
a real user can receive a push notification today: the capability's backend
half is built and tested; the client half that would make it end-to-end
usable does not exist yet in this repository. No VISION status marker
exists for this capability to cite instead (VISION_PROJECTS.md's own
"Capability | Status" table has no push/notification row), so this maturity
claim rests on the code and its absence, not on a product-status citation.

## Boundary

This node does not describe:
- **How the capability is built.** The push gateway's technology, ownership
  boundary, deployment, and security model are the architecture container
  node's territory — see `architecture-containers-push-gateway`. The
  relay-side step-by-step trigger-to-wake sequence, its trust-boundary
  crossings, and its failure/retry/abort behavior are the flow node's
  territory — see `architecture-flows-push-notification`. This node states
  that the capability exists and what it does for a user; it does not
  re-narrate either document's content.
- **The specific APNs transport profile's own wire contract.** Sibling
  issue #788 scopes `capabilities/notifications/apns.md` to the
  APNs-specific transport profile (App Attest enrollment mechanics, the
  compiled-in reconnect payload, the gateway's APNs-classification logic).
  This node covers the general "can an installed client receive a wake"
  capability across whichever transport profile is configured; it
  deliberately does not restate APNs-specific mechanics that belong to that
  sibling node, which was not merged at the time this node was authored.
- **The interface(s) the capability is exposed through.** No interface-typed
  corpus node for the gateway's HTTP surface or the relay's NIP-PL handling
  exists yet in the merged corpus to `references`; this node names the
  routes and the event kind only as evidence for its own claims, not as a
  substitute for that interface node once it is written.
- **The step-by-step flow through this capability**, beyond what is
  necessary to state the capability and cite its maturity — see
  `architecture-flows-push-notification` for the full ordered sequence,
  trust-boundary crossings, and failure handling.
- **How the running system is operated** — environment variables, key
  rotation, Helm chart mechanics, and alerting thresholds are
  `docs/push-gateway-deployment.md`'s territory, referenced by the
  architecture container node above, not restated here.

## Relationships

- references: `architecture-containers-push-gateway` — the container that
  implements the executor's gateway half of this capability.
- references: `architecture-flows-push-notification` — the step-by-step
  trigger-to-wake sequence this capability's server-side half actually
  executes.
- implements: `corpus-template-capability` — this node follows that
  template's required-sections shape.

No relationship targets a capabilities-notifications-apns node: at the
recorded revision `origin/launchpad`'s corpus tree carries no nodes under
`launchpad/docs/corpus/capabilities/` at all (confirmed via `git ls-tree`),
so no such node exists yet to point at, even though sibling issue #788
scopes exactly that document. Revisit once it merges.

## Scope and omissions

**This node covers** the push-notification capability at the product level:
what it lets an installed client and its user do, the primary actors,
behavioral rules and constraints that hold regardless of transport, the
one variant currently shipped versus the variants the protocol defines,
and its maturity grounded in code rather than a VISION status marker (none
exists for this capability).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the executor (relay + gateway) is built, deployed, and secured | `architecture-containers-push-gateway` |
| The step-by-step trigger-to-wake sequence, its trust boundaries, and its failure/retry/abort behavior | `architecture-flows-push-notification` |
| The APNs transport profile's own specific wire contract and App Attest mechanics | `capabilities/notifications/apns.md` (issue #788, not yet merged) |
| The full NIP-PL wire protocol (event schemas, HTTP request/response bodies, quota parameters) | `docs/nips/NIP-PL.md` |
| Gateway deployment, secrets, metrics, and alerting | `docs/push-gateway-deployment.md` |
| The boundary contract (interface) the capability is exposed through | Not yet written — no interface-typed corpus node exists for this surface |

**Expected but not verified when this node was written:**
- **Whether any mobile or desktop client work for this capability is
  currently in flight but unmerged.** This node checked only the committed
  state of `mobile/lib` and `desktop/src` at the recorded revision, not open
  branches or draft PRs elsewhere in the fleet.
- **Whether FCM or UnifiedPush support is planned on any concrete
  timeline.** NIP-PL's abstract names both as transport options; nothing
  found during authoring commits this repository to building either.
- **Whether this fork (launchpad-26/buzz) actually operates the push
  gateway against any live host.** Per `architecture-containers-push-gateway`'s
  own recorded gap, no launchpad-scoped deployment evidence was found; this
  node makes no claim about live operational status beyond what the code
  itself shows.
