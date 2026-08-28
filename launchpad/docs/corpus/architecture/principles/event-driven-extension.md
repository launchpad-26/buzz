---
id: architecture-principles-event-driven-extension
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "AGENTS.md's Key Patterns section instructs that new feature work should be modeled as a Nostr event (a new kind defined in buzz-core/src/kind.rs, handled in buzz-relay) rather than as an endpoint-specific JSON API, and names the exceptions where HTTP is reserved: media upload/download (Blossom), webhooks, git smart HTTP, NIP-11/NIP-05 metadata, health checks, and the generic Nostr bridge endpoints POST /events, POST /query, POST /count."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "CONTRIBUTING.md's 'How to Add a New API Endpoint' section states that the relay intentionally exposes only a narrow HTTP surface (NIP-11/NIP-05 metadata, /events, /query, /count, /hooks/{id}, Blossom media, git smart HTTP, git policy hooks, health probes) and instructs preferring a signed Nostr event over the existing WebSocket/POST /events ingest path before adding a new endpoint."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "CONTRIBUTING.md's Architecture Overview states that event kinds are the only switch in the system: every action — a message, a reaction, a workflow step, a canvas update — is a Nostr event carrying a kind integer, and adding a feature means defining a new kind rather than making a breaking change for existing clients."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "buzz-core/src/kind.rs is the authoritative registry of Buzz kind integers; its ALL_KINDS constant enumerates every registered kind, and the no_duplicate_kind_values unit test asserts that no two registered kind constants share a numeric value."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-relay/src/router.rs's actual registered HTTP route set is broader than the narrow surface enumerated in AGENTS.md and CONTRIBUTING.md: at the recorded revision it additionally registers /api/invites, /api/join-policy, /api/join-policy/terms, /api/join-policy/privacy, /api/invites/accept-policy, /api/invites/claim, /operator/communities and its archive/unarchive/availability/transfer sub-routes, /moderation/reports, /moderation/audit, /moderation/restricted, /_mesh/demo/echo, and /huddle/{channel_id}/audio, none of which appear in either document's list."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "CONTRIBUTING.md's own 'How to Add a New API Endpoint' section provides the escape hatch that would govern additions like these if used: register the route using the narrowest path possible, and do not add new /api/* compatibility routes unless the product decision explicitly calls for one."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "crates/buzz-relay/src/handlers/event.rs's handle_event enqueues an EventCreated audit-log entry via enqueue_event_created_audit for every event stored through the generic Nostr event-storage path, without the caller needing to invoke the audit service itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-relay/src/api/invites.rs and crates/buzz-relay/src/api/operator.rs — whose routes sit outside the documented narrow HTTP surface — contain no call into the audit service from their request-handling functions; every reference to buzz_audit in either file is an AuditService::new(...) call inside #[cfg(test)] AppState bootstrap code, not a runtime audit-log call reached by a live request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs"
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "A capability implemented as a bespoke HTTP handler instead of a new event kind does not receive an audit-log entry unless someone adds one by hand, because only the generic event-storage path enqueues one automatically — so choosing HTTP over an event kind has an observable, if indirect, consequence: the loss of the audit coverage the event path provides for free."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/api/invites.rs"
      - "crates/buzz-relay/src/api/operator.rs"
    confidence: 0.6
  - statement: "A repository-wide search for a test, lint, or CI check that compares the relay's registered routes against the documented narrow-surface list, or that otherwise verifies a new capability chose the event-kind path over a new HTTP endpoint, found no such mechanism; the only text found governing the choice is the code-review-facing prose in AGENTS.md and CONTRIBUTING.md."
    entry_class: FACT
    evidence:
      - "grep_repo('narrow HTTP surface', glob='*.rs') -> zero matches outside AGENTS.md and CONTRIBUTING.md themselves, run at revision a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "buzz-core/src/kind.rs's no_duplicate_kind_values test enforces only that no two registered kind constants share a numeric value; it cannot and does not check whether a given capability should have been modeled as a new kind in the first place."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
---

# Principle: event-driven extension

## Statement

A new client-facing capability in Buzz's relay surface MUST be modeled as a new
Nostr event kind — registered in `buzz-core/src/kind.rs` and handled through the
relay's generic event-storage path — rather than as a new endpoint-specific
HTTP/JSON API. A new HTTP endpoint MUST NOT be added for a capability that the
event-storage path can already serve.

This is stated as a MUST because both governing documents (`AGENTS.md` and
`CONTRIBUTING.md`) phrase it as an instruction to follow, not a suggestion to weigh,
and `CONTRIBUTING.md`'s Architecture Overview states the underlying design fact
plainly: event kinds are the system's only switch. See *Evidence* for the exact
wording each source uses.

## Scope

**Applies to:** adding a new *capability* to the relay — a new action a user, agent,
or client can take, or a new piece of state the relay stores and fans out (a
message, a reaction, a workflow step, a canvas update, and anything of that shape).
For these, `CONTRIBUTING.md`'s "How to Add a New Event Kind" section is the
procedure to follow, and it is not restated here.

**Does not apply to** a closed, already-enumerated set of surfaces that the event
path cannot serve because they are not eventable operations in the first place:

- Media upload/download (Blossom) — binary blob transport.
- Webhook triggers at `/hooks/{id}` — secret-authenticated, no NIP-98, called by
  external systems rather than a Nostr-authenticated client.
- Git smart HTTP and git policy hooks — protocol compliance with an external tool
  (`git`), not a Buzz-native operation.
- NIP-11/NIP-05 metadata — fetched by URL convention, not through a Nostr
  subscription.
- Health/liveness/readiness probes — infrastructure plumbing, not product surface.
- The three generic Nostr bridge endpoints themselves, `POST /events`, `POST
  /query`, `POST /count` — these exist so the event/kind path can be *reached* over
  plain HTTP; they are not endpoint-specific APIs and are the mechanism this
  principle argues for, not an exception to it.

`CONTRIBUTING.md` also documents a narrow, explicit escape hatch for anything
outside that set: an HTTP endpoint is still permitted "if... still necessary,"
registered "using the narrowest path possible," with new `/api/*` compatibility
routes gated on an explicit product decision. This node does not restate that
procedure; see `CONTRIBUTING.md` §"How to Add a New API Endpoint."

## What the documented surface misses today

The narrow-surface lists in `AGENTS.md` and `CONTRIBUTING.md` are not a complete
description of `crates/buzz-relay/src/router.rs` at the revision this node was
checked against. The router additionally registers invite/join-policy routes
(`/api/invites`, `/api/join-policy` and its sub-routes), operator/community
management routes (`/operator/communities` and its archive/unarchive/
availability/transfer sub-routes), moderation-queue reads (`/moderation/reports`,
`/moderation/audit`, `/moderation/restricted`), a test-only mesh echo probe
(`/_mesh/demo/echo`), and the huddle audio WebSocket
(`/huddle/{channel_id}/audio`). None of these are named in either document's list.

This node does not resolve that gap and does not assert it is a violation of the
principle above — `CONTRIBUTING.md`'s own escape hatch permits an HTTP endpoint
"if... still necessary," and whether each of these routes was added under an
explicit, documented product decision was not checked here (see *Scope and
omissions*). What is established is narrower and still useful: the two documents
that state this principle both understate the relay's actual HTTP surface, so a
reader relying on either list alone to judge whether an addition is precedented
will be working from stale information.

## Enforcement points and observable failure

**Enforced by code review, not by tooling.** The choice — event kind versus HTTP
endpoint — is governed by prose in `AGENTS.md` and `CONTRIBUTING.md`, read and
applied by whoever reviews the PR. A search of the repository found no automated
test, lint rule, or CI check that verifies a new capability took the event path, or
that flags a new route added to `router.rs` against the documented narrow-surface
list. A PR that adds a bespoke endpoint for something the event path could serve
will not be blocked by anything mechanical.

**The one mechanical check adjacent to this principle guards a narrower thing.**
`buzz-core::kind::tests::no_duplicate_kind_values` (in `crates/buzz-core/src/
kind.rs`) fails the build if two registered kind constants share a numeric value.
That protects the integrity of the registry once a capability has already been
built as an event kind; it says nothing about whether HTTP was chosen instead, and
cannot — a kind that was never defined has nothing in `ALL_KINDS` for the test to
even see.

**The nearest thing to an observable failure signal is indirect, and is recorded
here as an INFERENCE, not a FACT.** Every event stored through the relay's generic
event-storage path (`handle_event` in `crates/buzz-relay/src/handlers/event.rs`)
gets an `EventCreated` audit-log entry automatically, with no extra code required
from the feature author. The two HTTP handlers found outside the documented narrow
surface — `invites.rs` and `operator.rs` — call into the audit service nowhere in
their request-handling code; their only `buzz_audit` references are test-fixture
`AppState` construction. So a capability that takes the HTTP path instead of the
event path plausibly loses this audit coverage unless someone wires it in by hand.
This was not traced further (for example, into whether `operator.rs`'s actions are
audited by some other mechanism this review did not find), so it is offered as a
reasoned consequence of the two directly-observed facts, not as a confirmed
guarantee.

## Verification / conformance

**No verification or conformance mechanism enforces this principle directly.**
That is recorded here explicitly, per this node's own category requirement, rather
than pointed at something that only partially covers it:

- `no_duplicate_kind_values` (`crates/buzz-core/src/kind.rs`) is the closest
  automated check that exists, and it verifies kind-registry hygiene, not the
  event-versus-HTTP choice — see *Enforcement points* above.
- The only verification that does reach the choice itself is a human reviewer
  reading a PR against `CONTRIBUTING.md`'s "How to Add a New API Endpoint"
  section. That is real, but it is not a check this node can link to as a
  conformance mechanism in the sense the rest of this corpus uses the term —
  it produces no artifact, and nothing fails a build if it is skipped.

## Scope and omissions

**This document covers:** the MUST/MUST-NOT statement, which capabilities it
applies to and which enumerated surfaces it does not, what enforces the choice
today (code review) and what does not (no automated check), and the gap between
the documented narrow HTTP surface and the router's actual route table at the
recorded revision.

**It does not cover:**

| Not covered here | Why |
|---|---|
| The step-by-step procedure for adding a new event kind | `CONTRIBUTING.md` §"How to Add a New Event Kind" already owns this; restating it here would be a second, driftable copy. |
| The step-by-step procedure for adding an HTTP endpoint under the documented escape hatch | `CONTRIBUTING.md` §"How to Add a New API Endpoint" already owns this. |
| Per-kind semantics — what any individual kind number means | `buzz-core/src/kind.rs`'s own doc comments, and future per-kind corpus nodes. |
| Whether each of the routes named in *What the documented surface misses today* was added under an explicit, documented product decision, as `CONTRIBUTING.md`'s escape hatch requires | Not checked by this task. Establishing it would mean reading the PR history behind each route individually — out of scope for a single principle node, and named here as a gap rather than resolved by assumption. |
| Whether any mechanism other than `buzz-audit`'s automatic `EventCreated` enqueue gives `invites.rs` or `operator.rs`'s actions audit coverage by another path | Not traced. The INFERENCE above is scoped to what was directly checked: the two files' own handler code makes no audit call. |

**Expected but not verified when this node was written:** whether a product
decision was recorded (issue, ADR, or PR description) for each of the routes
listed in *What the documented surface misses today*. This node treats their
existence as a documentation gap between two prose sources and the code, not as
evidence the principle itself was violated — that determination needs the PR
history this task did not read.
