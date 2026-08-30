---
id: capabilities-notifications-apns
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-push-gateway's own Cargo manifest describes it as a 'Blind, capability-gated NIP-PL gateway for the Buzz mobile app,' built as its own binary and library crate distinct from the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/Cargo.toml"
  - statement: "The gateway's ApnsTransport (crates/buzz-push-gateway/src/apns.rs) builds provider-JWT-authenticated APNs HTTP/2 requests and classifies every APNs status/reason pair into a small sanitized DeliveryOutcome enum -- Accepted, InvalidEndpoint, Retry, RefreshCredential, ConfigurationFault, PermanentRequestFault -- so raw APNs response bodies never cross into gateway logs or metrics."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/apns.rs"
  - statement: "The gateway sends exactly one compiled-in payload for every APNs delivery -- APNS_RECONNECT_PAYLOAD, the literal bytes {\"aps\":{\"alert\":{\"body\":\"Reconnect to your relay now\"},\"mutable-content\":1}} -- defined as a constant in crates/buzz-push-gateway/src/model.rs; DeliveryRequest (the relay-to-gateway wire type) carries no application-payload field at all, only an opaque endpoint_grant, a request_id, and an expiry."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs"
  - statement: "AppProfile, the gateway's closed enum of registered APNs application profiles, has exactly two variants -- BuzzIosProduction (\"buzz-ios-production\") and BuzzIosSandbox (\"buzz-ios-sandbox\") -- both iOS; no Android/FCM or UnifiedPush variant exists in this enum."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs"
  - statement: "Startup configuration (crates/buzz-push-gateway/src/config.rs) parses BUZZ_PUSH_ENABLED_PROFILES against a match arm recognizing only the literal strings \"buzz-ios-production\" and \"buzz-ios-sandbox\", rejects any other value as ConfigError::Invalid, and refuses to start if the resulting enabled-profile set is empty -- an operator cannot enable a non-iOS profile because the parser has no arm for one."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "The gateway's HTTP router registers POST /v1/deliveries/apns (crates/buzz-push-gateway/src/http.rs), the relay-facing route that accepts a DeliveryRequest, admits it against the decrypted endpoint_grant, and calls the ApnsTransport to send the fixed reconnect payload; this is one of seven public routes the gateway serves in total."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "As of the recorded revision, no mobile (Flutter) or desktop (Tauri) client code in this repository creates, rotates, or revokes a push lease, performs App Attest enrollment, or references kind:30350, NIP-PL, or APNs -- confirmed by a case-insensitive search of mobile/lib and desktop/src for 30350, push_lease, PushLease, kind_push_lease, NIP-PL, nip-pl, and apns, which returned no matches."
    entry_class: FACT
    evidence:
      - "grep_recursive_case_insensitive('30350|push_lease|PushLease|kind_push_lease|NIP-PL|nip-pl|apns', paths='mobile/lib desktop/src') -> no matches, run against this worktree at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The already-merged architecture-containers-push-gateway node describes the gateway as the sole holder of APNs provider credentials, deliberately separate from the relay image, and the already-merged architecture-flows-push-notification node describes the end-to-end trigger-to-wake flow this capability participates in; both are already-merged corpus nodes this capability node references rather than restates."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/push-gateway.md"
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
  - statement: "VISION_PROJECTS.md's own 'Capability | Status' table (its Status section) lists eleven product capabilities with maturity markers -- Channels/forums/DMs/canvases, workflow engine, MCP server + ACP agent harness, Blossom media storage, approval gates, project binding, multi-repo projects, git hosting, merge coordinator, NIP-34 issues, web-of-trust reputation -- and none of the eleven rows names push notifications, APNs, or NIP-PL; this capability's maturity is therefore established from code and the already-merged architecture nodes, not from a VISION_PROJECTS.md status marker, because no such marker exists for it."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-259"
---

# APNs push notification delivery: capability

Buzz can wake an installed iOS client through Apple Push Notification service
(APNs) when a message it is authorized to read arrives while its WebSocket
connection is disconnected, without any relay-supplied event content, event
id, or ciphertext ever transiting Apple's infrastructure. The wake is a fixed,
transport-authored reconnect signal; the client always re-fetches
authoritative content over an ordinary authenticated `REQ` after waking.

## Maturity

**Shipped, server-side; not reachable end-to-end today.** The relay-side
lease acceptance, durable match/delivery pipeline, and the `buzz-push-gateway`
service's APNs transport are implemented and covered by dedicated tests (see
`architecture-flows-push-notification`'s evidence ledger for the specific
test names). The gateway's `ApnsTransport`
(`crates/buzz-push-gateway/src/apns.rs`) builds real provider-JWT-authenticated
APNs HTTP/2 requests, and its `AppProfile` enum
(`crates/buzz-push-gateway/src/model.rs`) registers two live iOS profiles,
`buzz-ios-production` and `buzz-ios-sandbox`. However, no mobile or desktop
client in this repository creates, rotates, or revokes a `kind:30350` push
lease or performs the App Attest enrollment the gateway requires (confirmed by
a repository-wide search of `mobile/lib` and `desktop/src`, evidence ledger
above) -- so the capability has no shipped client half, and a real user cannot
receive an APNs wake from Buzz today. `VISION_PROJECTS.md`'s own capability
status table does not list this capability at all, so its maturity is
established here from code and the two already-merged architecture nodes
this document references, not from a VISION status marker.

## Boundary

This node does not describe:
- how the capability is built -- container-level responsibility, ownership
  boundary, deployment, and security implications for `buzz-push-gateway`
  live in the already-merged `architecture-containers-push-gateway` node.
- the interface(s) the capability is exposed through -- the full NIP-PL wire
  protocol (`kind:30350` event shape, the gateway's HTTP request/response
  bodies, quota parameters, key rotation) is normative spec text in
  `docs/nips/NIP-PL.md`; no dedicated `interfaces-events` corpus node exists
  for it yet.
- the step-by-step flow through this capability -- the ordered trigger,
  match, delivery, and failure/retry path is the already-merged
  `architecture-flows-push-notification` node's subject, not this one's.
- any node-specific exclusion: Android/FCM and UnifiedPush transport
  profiles. `AppProfile` (`crates/buzz-push-gateway/src/model.rs`) and its
  `BUZZ_PUSH_ENABLED_PROFILES` parser (`crates/buzz-push-gateway/src/config.rs`)
  recognize only the two iOS profile strings; this capability node is scoped
  to the APNs transport specifically, not to push notifications in general.

## Relationships

- references: architecture-containers-push-gateway
- references: architecture-flows-push-notification

## Scope and omissions

**This node covers** the APNs push-notification capability at the level a
product stakeholder would recognize it: what a user or agent can do because
it exists (a reconnect wake with no content leakage to Apple), its current
maturity (server-side shipped and tested, no shipped client), and its
boundary against the architecture, interface, and flow documents that own
the how, the wire contract, and the step-by-step path respectively.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the capability is built (container responsibility, ownership boundary, deployment, security) | `architecture-containers-push-gateway` |
| The step-by-step trigger-to-wake flow, failure/retry behavior | `architecture-flows-push-notification` |
| The full NIP-PL wire protocol (event shape, HTTP bodies, quota parameters, key rotation) | `docs/nips/NIP-PL.md` (no dedicated interfaces-events corpus node exists yet) |
| Android/FCM and UnifiedPush transport profiles | Not yet a conforming v1 public-gateway profile per `docs/nips/NIP-PL.md`; no corpus node exists for either |
| Whether this fork (launchpad-26/buzz) operates the push gateway against a live host | Not established here; `architecture-containers-push-gateway` records the same open question |

**Expected but not verified when this node was written:**
- **Whether a mobile client implementation exists in an unmerged branch or
  PR outside this checkout.** Only the checked-out worktree's `mobile/lib`
  and `desktop/src` were searched; an in-progress client implementation on an
  unmerged branch would not appear in this search.
- **Whether the gateway's `/v1/deliveries/apns` route or `ApnsTransport` has
  ever been exercised against Apple's real (non-sandbox) APNs endpoint** --
  the code paths and their unit-level tests were read, not a live delivery.
