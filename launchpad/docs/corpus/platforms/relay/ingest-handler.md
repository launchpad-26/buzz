---
id: platforms-relay-ingest-handler
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "`crates/buzz-relay/src/handlers/ingest.rs` opens with the crate-level doc comment \"Transport-neutral event ingestion pipeline. Both WebSocket `[\"EVENT\", ...]` and HTTP `POST /events` feed into `ingest_event` — two doors, one room.\", and the module is registered as `pub mod ingest;` in `crates/buzz-relay/src/handlers/mod.rs`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1-4"
      - "crates/buzz-relay/src/handlers/mod.rs:20"
  - statement: "Two existing corpus nodes already document this module's behavior in full: `architecture-flows-event-ingestion` narrates the shared `ingest_event`/`ingest_event_inner` pipeline as sixteen ordered steps with its trust-boundary crossings and failure/rollback behavior, and `architecture-flows-http-event-submission` narrates the full `POST /events` request lifecycle (router body-size gate, tenant binding, NIP-98 auth, replay guard, admission) up to the same shared pipeline handoff. Both nodes exist in the corpus tree at the recorded revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
      - "launchpad/docs/corpus/architecture/flows/http-event-submission.md"
  - statement: "The module's public (cross-module, crate-visible) surface is: `HttpAuthMethod` (an enum of `Nip98`/`DevPubkey`), `IngestAuth` (an enum of `Nip42`/`Http` variants with accessor methods `pubkey`, `principal_pubkey_bytes`, `scopes`, `conn_id`, `channel_ids`, `is_http`), `IngestResult` (a struct of `event_id`/`accepted`/`message`), `IngestError` (an enum of `Rejected`/`AuthFailed`/`Internal`), the free function `reject_with_transport`, and the entry-point async function `ingest_event`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:196"
      - "crates/buzz-relay/src/handlers/ingest.rs:205-226"
      - "crates/buzz-relay/src/handlers/ingest.rs:228-276"
      - "crates/buzz-relay/src/handlers/ingest.rs:374-381"
      - "crates/buzz-relay/src/handlers/ingest.rs:385-392"
      - "crates/buzz-relay/src/handlers/ingest.rs:298"
      - "crates/buzz-relay/src/handlers/ingest.rs:2100"
  - statement: "Beyond the fully-public surface, five `pub(crate)` helpers in this module are called from other modules in the same crate rather than being purely internal to `ingest.rs`: `extract_channel_id`, `check_channel_membership`, `requires_h_channel_scope`, `resolve_relay_reply_thread_meta`, and `effective_message_author`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:550"
      - "crates/buzz-relay/src/handlers/ingest.rs:742"
      - "crates/buzz-relay/src/handlers/ingest.rs:704"
      - "crates/buzz-relay/src/handlers/ingest.rs:1012"
      - "crates/buzz-relay/src/handlers/ingest.rs:1105"
  - statement: "`ingest_event`'s own doc comment states it is \"Shared by WebSocket and HTTP transports. The caller constructs `IngestAuth` from their transport-specific auth mechanism and maps the result to their transport-specific response format\", and that it arms a `crate::conformance::EmitGuard` around the inner logic so every exit path has fail-closed trace coverage, citing `crates/buzz-relay/src/conformance/mod.rs` and `docs/spec/MultiTenantRelay.tla`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2085-2100"
  - statement: "Six other files in `crates/buzz-relay/src` reference this module across module/crate boundaries: `handlers/event.rs` (the WebSocket `EVENT` handler — imports `IngestAuth`/`IngestError`/`reject_with_transport`, calls `ingest_event`, `extract_channel_id`, `check_channel_membership`, and `requires_h_channel_scope`), `api/bridge.rs` (the HTTP `POST /events` bridge — imports `IngestAuth`/`IngestError`, calls `ingest_event`, `reject_with_transport`, and constructs `HttpAuthMethod::Nip98`), `handlers/command_executor.rs` (imports `extract_channel_id`, `IngestAuth`, `IngestError`, `IngestResult`), `workflow_sink.rs` (calls `resolve_relay_reply_thread_meta`), `handlers/side_effects.rs` (calls `effective_message_author`), and `conformance/mod.rs` (defines `sanitized_reason_for`, which maps an `IngestError` onto the conformance tracer's closed `SanitizedReason` alphabet)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:27"
      - "crates/buzz-relay/src/handlers/event.rs:761"
      - "crates/buzz-relay/src/handlers/event.rs:850-851"
      - "crates/buzz-relay/src/handlers/event.rs:1232"
      - "crates/buzz-relay/src/api/bridge.rs:19"
      - "crates/buzz-relay/src/api/bridge.rs:875"
      - "crates/buzz-relay/src/api/bridge.rs:922"
      - "crates/buzz-relay/src/api/bridge.rs:925"
      - "crates/buzz-relay/src/handlers/command_executor.rs:30"
      - "crates/buzz-relay/src/workflow_sink.rs:276"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2371"
      - "crates/buzz-relay/src/conformance/mod.rs:432-433"
  - statement: "This module's own top-of-file imports draw on the crate-level dependencies `buzz-auth` (for `Scope`), `buzz-core` (for the `kind` constants, `TenantContext`, `verify_event`, `CommunityId`), `nostr` (for `Event`/`PublicKey`), `uuid`, `chrono`, `tracing`, and — for the two rejection/acceptance counters emitted inside `ingest_event`/`reject_with_transport` — `metrics`; all of these are declared as workspace dependencies of the `buzz-relay` crate in its manifest."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1-49"
      - "crates/buzz-relay/Cargo.toml:19"
      - "crates/buzz-relay/Cargo.toml:24"
      - "crates/buzz-relay/Cargo.toml:39"
      - "crates/buzz-relay/Cargo.toml:50-51"
      - "crates/buzz-relay/Cargo.toml:42-44"
      - "crates/buzz-relay/Cargo.toml:79"
  - statement: "No crate in this workspace other than `buzz-relay` itself declares `buzz-relay` as a dependency in its `Cargo.toml` — `buzz-relay` is the relay server binary, not a library other crates build on, so a crate-manifest-level 'depended on by' direction does not apply to this module the way it would to a library crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
  - statement: "Because this node's subject is one module inside the `buzz-relay` crate rather than a separate crate, its 'Depends on'/'Depended on by' dependency claims are cited to the module's own `use` statements and to the real cross-module call sites found by searching `crates/buzz-relay/src/**` for references into `ingest.rs`, rather than to `Cargo.toml` alone for both directions as `templates/component.md` prescribes for a whole-crate component — `Cargo.toml` can express this module's crate-level dependencies but cannot express which sibling modules in the same crate call into it."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "crates/buzz-relay/Cargo.toml"
    confidence: 0.7
  - statement: "`ingest.rs` carries 175 `#[test]`/`#[tokio::test]` functions in its own `#[cfg(test)] mod tests`, covering (among others) the scope allowlist, global/channel-scoped kind classification, the community serving-fence mapping, and relay-admin ban/timeout error-mapping behavior — for example `serving_fence_active_community_admits_write`, `serving_fence_lookup_outage_fails_closed_as_internal`, `long_form_requires_messages_write_scope`, and `relay_admin_ban_maps_to_blocked_auth_failure`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3277-3278"
  - statement: "No `README.md` exists for the `buzz-relay` crate; of this repository's 30 crates only 6 carry one (`buzz-agent`, `buzz-pairing-cli`, `buzz-cli`, `buzz-acp`, `git-credential-nostr`, `git-sign-nostr`), and `buzz-relay` is not among them, so this node has no existing crate README to link as supporting evidence per `templates/component.md`'s guidance."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "launchpad/docs/corpus/templates/component.md"
  - statement: "No `architecture-component` node yet exists in the corpus decomposing the relay container into its constituent components, so this node declares no `part-of` relationship — there is nothing to point at yet, per `AGENTS.md`'s instruction to enumerate what exists rather than assume the absence is permanent."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Issue #1269 (sibling, unmerged at the time of writing) targets `platforms/relay/event-handler.md` for the WebSocket-side `crates/buzz-relay/src/handlers/event.rs` module, so it is not a valid relationship target for this node yet — `AGENTS.md` requires relationship targets to resolve against the branch being merged into, not the author's own worktree."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1269 (task: document platforms/relay/event-handler.md)"
---

# Ingest handler (`crates/buzz-relay/src/handlers/ingest.rs`)

This node documents the `ingest` module inside the `buzz-relay` crate as a
standalone component: its responsibility, its public interface, and its real
dependency edges in both directions. It deliberately does not restate the
detailed behavioral narrative of the pipeline this module implements — that
is already covered by two existing flow nodes (see *Boundary* below), and
this node exists to answer a different question: what is this piece of code,
what does it expose, and what depends on it.

## Responsibility

Per its own crate-level doc comment, `ingest.rs` is the "transport-neutral
event ingestion pipeline" — the single seam that both the WebSocket
`["EVENT", ...]` handler and the HTTP `POST /events` bridge feed into, so
that acceptance, rejection, storage, and fan-out behavior is defined exactly
once regardless of which transport an event arrived on. The module is
registered as `pub mod ingest;` in `crates/buzz-relay/src/handlers/mod.rs`.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `HttpAuthMethod` | enum (`Nip98`, `DevPubkey`) | How an HTTP caller authenticated, carried inside `IngestAuth::Http`. | `crates/buzz-relay/src/handlers/ingest.rs:196` |
| `IngestAuth` | enum (`Nip42 { .. }`, `Http { .. }`) | Transport-neutral auth context handed to `ingest_event`; carries the authenticated pubkey, granted scopes, and transport-specific detail (WS connection id / token channel restriction, or HTTP auth method). | `crates/buzz-relay/src/handlers/ingest.rs:205-226` |
| `IngestAuth::pubkey`/`principal_pubkey_bytes`/`scopes`/`conn_id`/`channel_ids`/`is_http` | methods | Transport-agnostic accessors so callers never match on the enum variant directly. | `crates/buzz-relay/src/handlers/ingest.rs:228-276` |
| `IngestResult` | struct (`event_id`, `accepted`, `message`) | The success return value — `accepted` distinguishes a new row from an idempotent duplicate. | `crates/buzz-relay/src/handlers/ingest.rs:374-381` |
| `IngestError` | enum (`Rejected`, `AuthFailed`, `Internal`) | The error return value; each caller maps these three variants onto its own transport's response shape (WS `OK false` / HTTP 400, 401/403, 500). | `crates/buzz-relay/src/handlers/ingest.rs:385-392` |
| `reject_with_transport(transport, reason)` | fn | Increments `buzz_events_rejected_total` with a bounded `{transport, reason}` label pair, shared by both callers so dashboards aren't skewed by only one transport's rejections. | `crates/buzz-relay/src/handlers/ingest.rs:298` |
| `ingest_event(state, tenant, event, auth)` | async fn | The single entry point: arms a conformance `EmitGuard`, delegates to the private `ingest_event_inner`, emits the stored-event metric, and maps any error onto a sanitized trace action. | `crates/buzz-relay/src/handlers/ingest.rs:2100` |
| `extract_channel_id`, `check_channel_membership`, `requires_h_channel_scope`, `resolve_relay_reply_thread_meta`, `effective_message_author` | `pub(crate)` fns | Crate-visible helpers reused by sibling modules outside this file (see *Dependencies* below) rather than purely private to `ingest_event_inner`. | `crates/buzz-relay/src/handlers/ingest.rs:550`, `:742`, `:704`, `:1012`, `:1105` |

## Dependencies

Because this node's subject is one module inside a crate, not the crate
itself, the two directions below are cited to real `use` statements and
cross-module call sites rather than to `Cargo.toml` alone for both
directions — see the `INFERENCE` entry in the evidence ledger for why.

**Depends on** (this module requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-auth` | `Scope` — the permission-scope type checked against a kind's required scope. | `crates/buzz-relay/src/handlers/ingest.rs:10`; `crates/buzz-relay/Cargo.toml:24` |
| `buzz-core` | `kind` constants, `TenantContext`, `verify_event`, `CommunityId` — the event-kind taxonomy, tenant identity, and NIP-01 signature/id verification. | `crates/buzz-relay/src/handlers/ingest.rs:12-39`; `crates/buzz-relay/Cargo.toml:19` |
| `nostr` | `Event`, `PublicKey` — the signed-event type this whole module operates on. | `crates/buzz-relay/src/handlers/ingest.rs:40`; `crates/buzz-relay/Cargo.toml:39` |
| `uuid`, `chrono` | Channel/connection identifiers and event timestamp bounds-checking. | `crates/buzz-relay/src/handlers/ingest.rs:8-9`; `crates/buzz-relay/Cargo.toml:50-51` |
| `tracing`, `metrics` | Structured logging and the `buzz_events_stored_total`/`buzz_events_rejected_total` counters. | `crates/buzz-relay/src/handlers/ingest.rs:7`; `crates/buzz-relay/Cargo.toml:42-44,79` |
| `crate::state::AppState`, `crate::conformance` | The shared relay application state and the conformance tracer/`EmitGuard` this module arms around every call. | `crates/buzz-relay/src/handlers/ingest.rs:44,46-49` |

**Depended on by** (these require this module):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/handlers/event.rs` | The WebSocket `EVENT` handler — the other of the "two doors" that call `ingest_event`; also calls `extract_channel_id`, `check_channel_membership`, `requires_h_channel_scope` directly. | `crates/buzz-relay/src/handlers/event.rs:27,761,850-851,1232` |
| `crates/buzz-relay/src/api/bridge.rs` | The HTTP `POST /events` bridge — constructs `IngestAuth::Http`/`HttpAuthMethod::Nip98` and calls `ingest_event`/`reject_with_transport`. | `crates/buzz-relay/src/api/bridge.rs:19,875,922,925` |
| `crates/buzz-relay/src/handlers/command_executor.rs` | Imports `extract_channel_id`, `IngestAuth`, `IngestError`, `IngestResult` for command-kind dispatch. | `crates/buzz-relay/src/handlers/command_executor.rs:30` |
| `crates/buzz-relay/src/workflow_sink.rs` | Calls `resolve_relay_reply_thread_meta` to resolve NIP-10 thread metadata for workflow-originated messages. | `crates/buzz-relay/src/workflow_sink.rs:276` |
| `crates/buzz-relay/src/handlers/side_effects.rs` | Calls `effective_message_author` to attribute a relay-signed event back to its real human/agent author. | `crates/buzz-relay/src/handlers/side_effects.rs:2371` |
| `crates/buzz-relay/src/conformance/mod.rs` | `sanitized_reason_for` maps an `IngestError` onto the conformance tracer's closed `SanitizedReason` alphabet. | `crates/buzz-relay/src/conformance/mod.rs:432-433` |

No crate outside `buzz-relay` depends on it (it is the relay server binary,
not a library), so there is no crate-manifest-level "depended on by" edge to
report at that level.

## Boundary

This node does not describe:

- **The pipeline's ordered behavior.** `ingest_event`/`ingest_event_inner`'s
  sixteen-step sequence — the community write fence, categorical rejections,
  signature/timestamp/size checks, scope checks, channel resolution,
  membership enforcement, storage, and post-commit dispatch — plus its
  trust-boundary crossings and failure/rollback semantics, is
  `architecture-flows-event-ingestion`'s subject, not this node's.
- **The HTTP request lifecycle around this module.** Tenant binding from the
  `Host` header, NIP-98 signature verification, the replay guard, and
  per-principal admission rate-limiting all happen in `api/bridge.rs` before
  `ingest_event` is ever called, and are `architecture-flows-http-event-submission`'s
  subject.
- **The roughly thirty per-kind structural validators** inside
  `ingest_event_inner` (edit ownership, forum-vote target, diff metadata,
  persona/team-catalog/project envelopes, and others) — both flow nodes above
  already name this as an open question neither settles; this node doesn't
  settle it either.
- **Install/usage instructions for a human running the relay** — there is no
  `crates/buzz-relay/README.md` to link in place of restating one.
- **The WebSocket `EVENT` handler itself** (`crates/buzz-relay/src/handlers/event.rs`)
  — that is issue #1269's subject (`platforms/relay/event-handler.md`), unmerged
  at the time of writing.

## Relationships

- `references`: `architecture-flows-event-ingestion` — the ordered-behavior
  narrative of the pipeline this module implements.
- `references`: `architecture-flows-http-event-submission` — the HTTP request
  lifecycle that leads into this module from the `POST /events` transport.

Both targets are present in the corpus tree at the recorded revision. No
`part-of` is declared: no `architecture-component` node yet exists to
decompose the relay container, so there is nothing to point at (see the
`AGENTS.md`-grounded evidence entry above). No `depends-on` is declared: this
node's own claims do not require either flow node to stay current for this
node's claims about the module's interface and dependencies to hold —
`references` is the correct type per `relationships.schema.json`'s stated
directionality ("source cites target as supporting context; no ownership or
currency dependency implied").

## Scope and omissions

**This node covers** the `ingest` module inside `buzz-relay` as a standalone
component: its crate-doc responsibility statement, its public
(cross-module-visible) interface, and its real dependency edges in both
directions, cited to source rather than to prose recollection.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The pipeline's ordered behavior, trust boundaries, and failure/rollback semantics | `architecture-flows-event-ingestion` |
| The HTTP `POST /events` request lifecycle (tenant binding, NIP-98, replay, admission) | `architecture-flows-http-event-submission` |
| The ~30 per-kind structural validators inside `ingest_event_inner` | Not yet owned by any node; both flow docs above leave this open |
| The WebSocket `EVENT` handler | Issue #1269 / `platforms/relay/event-handler.md`, unmerged at time of writing |
| Container-level decomposition of the relay, with a required diagram | No `architecture-component` node exists yet for the relay container |

**Expected but not verified when this node was written:**

- Whether all 175 tests in `ingest.rs`'s own `#[cfg(test)] mod tests` exercise
  this module's public interface specifically (as opposed to private
  internals of `ingest_event_inner`) was not individually confirmed test by
  test — the four named in the evidence ledger were spot-checked by name,
  not the full 175.
- Whether a non-Rust equivalent of this component (there is none in this
  case — `ingest.rs` is Rust) would need a different evidence anchor was not
  a live question here and is out of scope for this node.
