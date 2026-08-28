---
id: architecture-context-nostr-network
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Buzz is a single relay of record: all reads and writes flow through it, and there is no peer-to-peer event exchange, no gossip, and no replication between Buzz and other relays."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "A Buzz community is the tenant-visible workspace selected by the request host; unknown hosts fail closed and NIP-98/API-token stamps must agree with the host-derived community rather than override it."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "Every action in Buzz is a Nostr NIP-01 wire-format signed event, dispatched by its integer `kind`; buzz-core/src/kind.rs is the source of truth for the registry, and kinds 40000-49999 are reserved for Buzz-custom kinds."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Third-party Nostr clients connect directly to buzz-relay using NIP-29 (relay-based groups) and NIP-42 (authentication) over WebSocket; the old NIP-28 compatibility proxy has been removed."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "Client-supplied #h tags name channels/groups and are checked against the host-derived community; events without #h (profiles, gift-wrapped DMs, membership notifications, lists, status, long-form notes, workflow/system events) are global only inside the connected community."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "Some Buzz custom kinds (e.g. kind:40002 rich content, kind:40003 message edits) work correctly on the wire but no standard third-party NIP-29 client renders them, because they are Buzz-specific extensions rather than published NIPs."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "Buzz's own desktop, mobile, web, and CLI clients speak the same NIP-01/NIP-29/NIP-42 wire protocol to buzz-relay as third-party Nostr clients do — the relay's System Architecture diagram groups 'Human (Nostr app, web, mobile)' and 'Agent (CLI tools via buzz-cli)' as peer WebSocket clients of the same relay."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "AI agents connect to Buzz through the buzz-acp harness, which listens for @mentions on the relay over WebSocket and lets the agent reply through buzz-cli; each agent's identity in Buzz is a Nostr keypair generated with buzz-admin and registered as a relay member."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "buzz-pair-relay is a separate, ephemeral sidecar relay (not buzz-relay itself) that handles NIP-AB device-pairing handshakes: it accepts WebSocket connections, matches kind:24134 events against #p-filtered subscriptions, binds loopback-only, and persists nothing."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs"
  - statement: "git-sign-nostr signs git commits and tags with Nostr secp256k1 keys (BIP-340 Schnorr signatures) per NIP-GS, using git's pluggable gpg.x509.program signing interface."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md"
      - "docs/nips/NIP-GS.md"
  - statement: "git-credential-nostr is a NIP-98 git credential helper that signs HTTP auth events with a Nostr key so git can push to and pull from Buzz's git server without passwords."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md"
  - statement: "buzz-relay's HTTP router merges a dedicated git smart-HTTP router and a git-policy-hooks router alongside the Nostr WebSocket/bridge routes, so a plain git client (authenticated via git-credential-nostr) is a distinct actor from a Nostr WebSocket client even though both terminate at the same relay process."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "buzz-media implements Blossom kind:24242 auth verification (BUD-11) for its /media/upload and /media/{sha256} endpoints, so Blossom-speaking media clients/servers are a third external protocol surface alongside NIP-29/NIP-42 chat and NIP-98 git."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "buzz-relay's HTTP surface additionally serves NIP-05 identity verification at /.well-known/nostr.json and NIP-11 relay information at GET / with an Accept: application/nostr+json header, alongside the generic Nostr bridge endpoints POST /events, POST /query, POST /count and workflow webhooks at POST /hooks/{id}."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The nostr-protocol/nips GitHub repository is the upstream specification Buzz implements against for standard NIPs (NIP-01, NIP-29, NIP-42, and others); Buzz's own protocol extensions are documented as draft NIPs under docs/nips/ (e.g. NIP-GS for git signing, NIP-OA for agent owner attestation)."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
      - "docs/nips/NIP-GS.md"
      - "docs/nips/NIP-OA.md"
  - statement: "No outbound WebSocket connection to another Nostr relay exists in buzz-relay's production code path; the only connect_async call sites in buzz-relay are inside #[cfg(test)] modules that connect a test harness to the relay's own listener, and the crates that do open outbound Nostr WebSocket connections (buzz-acp, buzz-pairing-cli, via buzz-ws-client) connect to buzz-relay or buzz-pair-relay, not to a third-party relay. Combined with ARCHITECTURE.md's explicit 'no peer-to-peer event exchange, no gossip, no replication' statement, Buzz today has no relay-to-relay federation: all interoperability with the wider Nostr network happens at the client layer, not between relays."
    entry_class: INFERENCE
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-acp/src/relay.rs"
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-ws-client/src/connection.rs"
    confidence: 0.6
  - statement: "Issue #666 requires this node to define the system/actor boundary being described, name every directly relevant actor/system and its relationship to Buzz, include or link a diagram-as-code representation when it adds clarity, and not descend into container/component implementation details."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#666 definition of done"
---

# Context: Buzz and the Nostr Network

What sits outside `buzz-relay`'s own process boundary and talks to it, and what Buzz does
and does not do at the level of the wider Nostr network. This is a System Context node
(C4 level 1): it names actors and their relationship to Buzz. It does not describe what
happens inside the relay once a connection is open — that is `ARCHITECTURE.md`'s job — and
it does not restate per-NIP wire detail — that is `NOSTR.md` and `docs/nips/`'s job. Links
below point at those instead of duplicating them.

## The system boundary

**The system being described is one Buzz community**: a single `buzz-relay` deployment
(today, one process or a horizontally-scaled set of processes sharing one Postgres and one
Redis, coordinated as a single logical relay) reachable at one host/domain. That relay is
the single source of truth for the community — every read and write flows through it.
Buzz **does not federate at the relay level**: there is no peer-to-peer event exchange, no
gossip between relays, and no replication with any other Nostr relay. Everything this node
calls "the Nostr network" from Buzz's point of view is therefore interoperability that
happens at the *client* layer — a client that also knows how to talk to other relays — not
at the relay layer.

In multi-community deployments the community boundary is the request host, resolved before
any AUTH/EVENT/REQ/REST/media/git/search/workflow handling: an unknown host fails closed,
and a client-supplied auth stamp cannot override the host-derived community. That host
boundary, not any Nostr-protocol construct, is what separates one Buzz community from
another.

## Actors and their relationship to Buzz

| Actor | What it is | Relationship to Buzz |
|---|---|---|
| **Third-party Nostr clients** (e.g. Chachi, 0xchat, `nak`) | Independent NIP-29-capable Nostr clients, not built by this project | Connect directly to `buzz-relay` over WebSocket using standard NIP-29 (groups) and NIP-42 (auth). They see Buzz as an ordinary NIP-29 relay; Buzz-custom kinds (e.g. rich content/edits) are on the wire but render as nothing meaningful in a client that doesn't know them. |
| **Buzz's own clients** (desktop, mobile, web, `buzz-cli`) | First-party clients built in this repository | Speak the identical NIP-01/NIP-29/NIP-42 wire protocol to the same relay as third-party clients — there is no private back channel. They differ from third-party clients only in that they understand the Buzz-custom kinds too. |
| **AI agents** | Any agent speaking ACP (goose, codex, claude code, …), run through `buzz-acp` | The harness listens for @mentions on the relay over WebSocket and drives the agent; the agent's identity in Buzz is a Nostr keypair like any human user's, registered as a relay member via `buzz-admin`. To the relay, an agent is just another authenticated pubkey. |
| **Device-pairing peers** | A second device (e.g. mobile) pairing itself to an existing identity | Talk NIP-AB pairing events (kind:24134) to `buzz-pair-relay`, a separate, ephemeral, loopback-only sidecar process with no persistence and no auth of its own — not to `buzz-relay` directly. |
| **Git clients** (plain `git`, via `git-credential-nostr` and optionally `git-sign-nostr`) | Standard git tooling extended with Nostr-based credential and signing helpers | `git-credential-nostr` signs NIP-98 HTTP auth events so git can push/pull over Buzz's git smart-HTTP surface without a password; `git-sign-nostr` optionally signs commits/tags with the same Nostr key (NIP-GS) using git's pluggable signing-program interface. Both terminate at `buzz-relay`'s merged git and git-policy routers, a distinct HTTP surface from the Nostr WebSocket/bridge routes even though it is the same process. |
| **Blossom media clients/servers** | Any client or server implementing the Blossom blob-storage convention | Buzz's own media upload/download endpoints authenticate Blossom kind:24242 events per BUD-11, so Buzz participates in the Blossom protocol as a server, independently of the NIP-29 chat surface. |
| **`nostr-protocol/nips` (upstream)** | The community specification repository for standard NIPs | The reference Buzz implements against for NIP-01, NIP-29, NIP-42 and the other NIPs it supports. Buzz's own protocol extensions (git signing, agent owner attestation, workspace profile, and others) are written up as draft NIPs under `docs/nips/` rather than folded silently into the wire format. |

## Diagram

```mermaid
flowchart LR
    subgraph external["Wider Nostr network"]
        thirdparty["Third-party NIP-29 clients\n(Chachi, 0xchat, nak, ...)"]
        nips["nostr-protocol/nips\n(upstream spec)"]
        blossom["Blossom media\nclients/servers"]
    end

    subgraph buzz["One Buzz community (buzz-relay)"]
        relay(("buzz-relay"))
    end

    subgraph firstparty["Buzz's own clients"]
        desktop["desktop / mobile / web"]
        cli["buzz-cli"]
        acp["buzz-acp\n(AI agent harness)"]
    end

    subgraph sidecar["Adjacent Buzz processes"]
        pairrelay["buzz-pair-relay\n(NIP-AB pairing, loopback-only)"]
    end

    subgraph gittools["Git tooling"]
        gitclient["git"]
        gitcred["git-credential-nostr\n(NIP-98)"]
        gitsign["git-sign-nostr\n(NIP-GS)"]
    end

    thirdparty -- "WS: NIP-29 + NIP-42" --> relay
    desktop -- "WS: NIP-29 + NIP-42" --> relay
    cli -- "WS: NIP-29 + NIP-42" --> relay
    acp -- "WS: @mentions, ACP" --> relay
    blossom -- "HTTP: BUD-11 auth" --> relay
    gitclient -- "HTTP: git smart-HTTP" --> relay
    gitcred -. "signs NIP-98 auth event for" .-> gitclient
    gitsign -. "signs commits/tags for" .-> gitclient
    relay -. "no relay-to-relay link" .-x otherrelay["another Nostr relay"]
    pairrelay -- "WS: NIP-AB kind:24134" --- pairingpeer["pairing device"]

    nips -. "spec Buzz implements against" .-> relay
```

The crossed-out edge to "another Nostr relay" is deliberate: it records the negative claim
in the evidence ledger above, not an omission. `buzz-pair-relay` is drawn as adjacent to,
not inside, the `buzz-relay` community box because it is a separate process with its own
auth-free, unpersisted trust model.

## Scope and omissions

**This node covers** the actors and external systems that directly connect to or
interoperate with a Buzz community over the Nostr protocol, HTTP, or an adjacent sidecar
protocol, and the boundary of what "the Nostr network" means for Buzz (client-layer
interoperability, not relay federation).

**It does not cover, and these are owned elsewhere:**

| Not covered here | Owned by |
|---|---|
| Internal relay components — `buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`, `buzz-audit`, `buzz-workflow` and how `buzz-relay` orchestrates them | `ARCHITECTURE.md` |
| Per-kind wire detail, tag shapes, auth flows for each supported NIP | `NOSTR.md` and `docs/nips/` |
| The event-kind registry itself | `crates/buzz-core/src/kind.rs` |
| Multi-community host routing internals beyond the boundary statement above | `ARCHITECTURE.md` |
| Speculative future actors (e.g. peer-to-peer compute sharing across communities) | `VISION_MESH.md` — not part of this node because it is not yet built |

**Expected but not verified when this node was written:**

- **Live interop with a specific third-party client was not re-run for this node.** `NOSTR.md`
  records `nak` and `BuzzTestClient` as verified in-repo, and Chachi/0xchat as "not verified
  in-repo (anecdotal / expected)" — this node repeats that distinction rather than
  independently re-testing either client.
- **Whether any other crate outside the six greped in the INFERENCE entry above opens an
  outbound Nostr WebSocket connection was checked by name pattern (`connect_async` /
  `tokio_tungstenite::connect`) across `crates/*/src`, not by a full data-flow audit** — a
  differently-named HTTP or WebSocket client library, if one exists elsewhere in the tree,
  would not have matched that search.
