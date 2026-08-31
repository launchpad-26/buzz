---
id: implementation-crates-buzz-relay
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "crates/buzz-relay/src/lib.rs's crate doc is `#![deny(unsafe_code)]` / `#![warn(missing_docs)]` / \"NIP-01 WebSocket relay for Buzz private team communication\", and declares 22 public modules with one-line doc comments each: api, audio, config, conformance, connection, error, handlers, invite_token, mesh_boot, metrics, nip11, protocol, push_runtime, router, state, storage_sweep, subscription, telemetry, tenant, tunnel, webhook_secret, workflow_sink (plus two private modules, admission and build_info), re-exporting Config, RelayError/Result and AppState at the crate root."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/lib.rs"
  - statement: "crates/buzz-relay/src/protocol.rs defines ClientMessage (Event/Req/Close/Count/Auth, the five NIP-01 client message variants) with a single ClientMessage::parse(raw: &str) entry point enforcing NIP-11-advertised limits (MAX_SUB_ID_LENGTH, MAX_FILTERS_PER_REQ), and RelayMessage as a set of associated functions (auth_challenge, event, notice, eose, ok, closed, count) that format the corresponding relay-to-client NIP-01 JSON strings; both are exercised by 8 in-file unit tests covering valid parses, the two length/count limits, and every RelayMessage format."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:1-64"
      - "crates/buzz-relay/src/protocol.rs:381-459"
  - statement: "crates/buzz-relay/src/connection.rs's module doc states the WebSocket connection lifecycle as \"semaphore -> challenge -> recv/send/heartbeat loops -> cleanup\"; ConnectionState (conn_id, tenant: TenantContext resolved before any frame is read, remote_addr, auth_state: RwLock<AuthState>, subscriptions: Mutex<HashMap<String, Vec<Filter>>>, send_tx/ctrl_tx as two separate mpsc channels with priority drain for control frames, a CancellationToken, and a shared backpressure_count/grace_limit pair) is the per-socket state handed to every handler; AuthState is a three-variant enum (Pending{challenge}, Authenticated(AuthContext), Failed) tracking NIP-42 progress, and AUTH_TIMEOUT (5s) bounds how long an unauthenticated socket may hold a connection slot."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:1-87"
  - statement: "crates/buzz-relay/src/admission.rs's check_principal<L: RateLimiter> function and ws_admission_budget helper implement per-principal, per-limit-type admission control (AdmissionError::Exceeded{reset_in_secs}/Unavailable) generic over a RateLimiter trait object, with 4 in-file unit tests (a stubbed limiter) covering both the budget math and the deny/fail-unavailable paths independent of any live Redis."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/admission.rs"
  - statement: "crates/buzz-relay/src/handlers/mod.rs declares the WS/HTTP command handler modules (auth, close, count, event, ingest, req, side_effects, command_executor, plus moderation/relay-admin/identity-archive/product-feedback/report handler modules for their respective NIP-scoped command kinds) and one shared helper, resolve_ttl, doc-commented per-file: \"EVENT handler -- WS dispatcher -> ingest pipeline -> fan-out\", \"REQ handler -- subscribe, deliver historical events, then EOSE\", \"Transport-neutral event ingestion pipeline\", \"Subscription close (CLOSE) handler\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/mod.rs"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's module doc states 'Both WebSocket [\"EVENT\", ...] and HTTP POST /events feed into ingest_event() -- two doors, one room', and the crate's own public entry point pub async fn ingest_event(state, tenant, event, auth: IngestAuth) -> Result<IngestResult, IngestError> (ingest.rs:2100-2105) takes an IngestAuth enum with exactly two variants, Nip42{pubkey, scopes, channel_ids, conn_id} for the WebSocket path and Http{pubkey, scopes, auth_method} for the HTTP bridge path (ingest.rs:205-226), confirming the two-transport, one-pipeline claim in code, not only in the doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1-5"
      - "crates/buzz-relay/src/handlers/ingest.rs:205-226"
      - "crates/buzz-relay/src/handlers/ingest.rs:2100-2105"
  - statement: "ingest_event's own doc comment (ingest.rs:2095-2099) cites crates/buzz-relay/src/conformance/mod.rs and docs/spec/MultiTenantRelay.tla directly, and conformance/mod.rs's module doc states its 'Wire points' include ingest.rs's check_channel_membership call site and the two dispatch_persistent_event sites, describing itself as 'the relay's side of the trace seam' whose emitted TraceSteps are replayed by the separate buzz-conformance checker against the TLA+ spec; docs/spec/MultiTenantRelay.tla exists in the repository (1142 lines) and buzz-relay's own Cargo.toml lists no dependency edge back from buzz-conformance, confirming the emitter (buzz-relay) and checker (buzz-conformance) are separate crates joined only by this trace schema."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2095-2099"
      - "crates/buzz-relay/src/conformance/mod.rs:1-32"
      - "docs/spec/MultiTenantRelay.tla"
      - "crates/buzz-relay/Cargo.toml"
  - statement: "crates/buzz-relay/src/handlers/event.rs defines pub async fn handle_event(event, conn, state) (the WS EVENT command handler, event.rs:608), pub(crate) async fn dispatch_persistent_event(..) (event.rs:349) which conformance/mod.rs names as one of its two wire points, and pub async fn fan_out_pubsub_event(state, channel_event: buzz_pubsub::ChannelEvent) (event.rs:282) which delivers a Redis pub/sub-received event to this pod's locally-subscribed WebSocket connections -- the live-fanout half of the pipeline, separate from the persistence half ingest_event owns."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:282"
      - "crates/buzz-relay/src/handlers/event.rs:349"
      - "crates/buzz-relay/src/handlers/event.rs:608"
  - statement: "crates/buzz-relay/src/handlers/req.rs defines pub async fn handle_req (req.rs:51), MAX_SUBSCRIPTIONS = 1024 per connection, and FILTER_QUERY_CONCURRENCY = 4 with a doc comment explaining NIP-01's per-filter OR semantics require one buzz_db::EventQuery per filter and bounding concurrent in-flight queries so one multi-filter REQ cannot monopolize the Postgres pool; MAX_EXPLICIT_CHANNEL_VALUES = 128 separately bounds the number of explicit #h channel tags accepted in one REQ, COUNT, HTTP /query, or HTTP /count request before any per-channel membership lookup work begins."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1-46"
  - statement: "crates/buzz-relay/src/handlers/close.rs's pub async fn handle_close(sub_id, conn, state) is a 35-line handler; crates/buzz-relay/src/subscription.rs's module doc describes a 'Subscription registry with (channel, kind) fan-out index' (51 declarations, 1967 lines, 34 in-file unit tests) that both handle_req's registration path and fan_out_pubsub_event's delivery path read/write."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
      - "crates/buzz-relay/src/subscription.rs:1-10"
  - statement: "crates/buzz-relay/src/state.rs defines CommunityConnectionRegistry (tracks which live sockets are bound to which community), run_registered_community_connection (registers a socket for the duration of its handler future and cancels it if a pre-check fails), and ConnectionManager (a DashMap<Uuid, ConnEntry> plus a sticky draining: AtomicBool flag whose doc comment states registrations landing after a drain snapshot self-signal, so no upgrade-vs-shutdown interleaving misses the restart close)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:37-88"
      - "crates/buzz-relay/src/state.rs:189-257"
  - statement: "AppState::revalidate_live_communities (state.rs:1219-1234) is doc-commented as 'the durable backstop for Redis pub/sub's lossy offline-subscriber semantics: a pod that missed a successful publish eventually observes the archived row directly', calling revalidate_registered_communities against buzz-db's is_community_active per bound community and cancelling sockets for any community found inactive; AppState::disconnect_community_clusterwide (state.rs:1204-1217) is the fast path -- a pubsub-published DisconnectCommunity command awaited before returning, so a community-deletion caller can distinguish durable state from propagation completion. main.rs's run_community_revalidator (main.rs:1208-1223) drives revalidate_live_communities on a periodic timer via run_periodic_until_cancelled, so the two mechanisms (immediate broadcast, periodic poll) are both live, not just the one main.rs's own doc comment mentions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1200-1234"
      - "crates/buzz-relay/src/main.rs:1208-1223"
  - statement: "A grep for '^\\s*#\\[(test|tokio::test)\\]' across every file under crates/buzz-relay/src counts 1087 unit/async test functions; a grep for '#\\[ignore' across the same tree counts 93, concentrated in api/invites.rs (12), api/operator.rs (11), api/git/transport.rs (10, split 7 'requires Postgres' + 3 'requires Postgres and MinIO'), workflow_sink.rs (4), api/bridge.rs (6, split 4 Postgres + 2 Redis), handlers/relay_admin.rs (2), handlers/command_executor.rs (2), and api/admin/mod.rs (2)."
    entry_class: FACT
    evidence:
      - "grep(pattern='^\\s*#\\[(test|tokio::test)\\]', path='crates/buzz-relay/src/**/*.rs') -> 1087 matches, commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
      - "grep(pattern='#\\[ignore', path='crates/buzz-relay/src/**/*.rs') -> 93 matches, same commit"
  - statement: "Justfile's test-unit recipe's cargo-nextest branch runs exactly one buzz-relay-scoped step: `cargo nextest run -p buzz-relay --lib -E 'test(/^api::admin::/) - test(=api::admin::tests::disabled_mode_allows_unauthenticated_requests_on_the_admin_host) - test(=api::admin::tests::nip98_mode_unrostered_signer_does_not_consume_a_replay_slot)'`, whose own inline comment states it exists because 'nothing in CI runs cargo test --workspace, just test-unit did not enumerate buzz-relay --lib, and Backend Integration selects only the #[ignore]d Postgres suites -- so these non-ignored tests ran in no lane'; crates/buzz-relay/src/api/admin/mod.rs and api/admin/auth.rs together carry 95 test functions (85 + 10), so this filter is the only place in this repository's test-running commands that exercises any non-ignored buzz-relay test outside that one api::admin scope."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "crates/buzz-relay/src/api/admin/mod.rs"
      - "crates/buzz-relay/src/api/admin/auth.rs"
  - statement: "scripts/run-tests.sh's run_unit_tests and run_integration_tests functions name buzz-core, buzz-auth, buzz-voice, buzz-cli, buzz-db, buzz-conformance, buzz-push-gateway, and buzz-backend-kubernetes by package flag; neither function names buzz-relay anywhere (grep for 'buzz-relay' in the file returns zero matches), and run_integration_tests' final 'workspace integration tests' step runs `cargo test --test '*'` -- Cargo's --test flag selects files under a crate's tests/ directory, and crates/buzz-relay has no tests/ directory, so that step also cannot reach buzz-relay's in-file #[cfg(test)] modules."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh"
      - "ls(path='crates/buzz-relay/tests/') -> No such file or directory"
  - statement: ".github/workflows/ci.yml's unit-tests job (name 'Unit Tests') runs exactly `just test-unit` as its only test step, so it inherits the api::admin-only buzz-relay scope above; the backend-integration job archives buzz-relay's --lib tests (line 380-387: `cargo nextest archive --cargo-profile ci -p buzz-db -p buzz-relay -p buzz-test-client --lib ...`) but every later step that consumes that archive passes `--run-ignored ignored-only` together with a hand-enumerated -E filter naming specific test paths or individual test names (api::invites::tests, handlers::relay_admin::tests, and named api::admin::tests:: functions across four separate steps) -- `--run-ignored ignored-only` restricts execution to #[ignore]d tests matching the filter, so this job never executes buzz-relay's non-ignored tests either."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:125-146"
      - ".github/workflows/ci.yml:379-387"
      - ".github/workflows/ci.yml:743-760"
      - ".github/workflows/ci.yml:786-853"
  - statement: "Given the prior three evidence entries, the majority of buzz-relay's 1087 test functions -- everything outside the ~95 api::admin tests just(test-unit) runs and the handful of individually-named #[ignore]d tests backend-integration selects -- are not executed by any test-running command this repository defines (Justfile, scripts/run-tests.sh, or .github/workflows/ci.yml); this includes every test in protocol.rs, connection.rs, admission.rs, subscription.rs, handlers/event.rs, handlers/req.rs, handlers/ingest.rs, and handlers/close.rs -- the WS protocol/connection/ingestion pipeline this node's Implementation surface documents. Whether developers run them ad hoc with a manual `cargo test -p buzz-relay --lib` during focused work is plausible but not verifiable from the repository alone."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - "scripts/run-tests.sh"
      - ".github/workflows/ci.yml"
    confidence: 0.8
  - statement: "architecture-containers-relay.md (recorded at revision a44cf52fc740ebebbdd671427480d14f0bce0115, unchanged at this node's own recorded revision) was authored by reading buzz-relay's own source directly (its evidence ledger cites crates/buzz-relay/src/state.rs, router.rs, main.rs, config.rs, mesh_boot.rs, push_runtime.rs), not the reverse -- so it is a sibling corpus node describing the same crate from the container-architecture altitude, not a governing spec buzz-relay was built to satisfy; the still-unmerged buzz-relay-mesh implementation-reference sibling node reaches the identical conclusion about the same node and declares it as `references`, not `implements`, which this node follows."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') at this node's recorded revision lists architecture-containers-relay.md and all thirteen architecture/flows/*.md nodes (event-ingestion, websocket-connection, websocket-authentication, live-fanout, historical-query, git-push, huddle-audio, http-event-submission, search-query, workflow-execution, media-upload, media-download, push-notification) as already merged, and event-ingestion.md, websocket-connection.md, websocket-authentication.md, live-fanout.md, and historical-query.md each cite one or more of the exact buzz-relay source paths this node's Implementation surface table documents (protocol.rs/connection.rs/router.rs, handlers/auth.rs, handlers/event.rs, handlers/ingest.rs, handlers/req.rs, subscription.rs) -- confirmed by grepping each flow node's front-matter evidence for 'crates/buzz-relay' citations."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/architecture/flows') -> 13 flow nodes present, commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
      - "launchpad/docs/corpus/architecture/flows/live-fanout.md"
      - "launchpad/docs/corpus/architecture/flows/historical-query.md"
  - statement: "router.rs's build_router (router.rs:33-38) doc comment -- 'Pure Nostr protocol: WebSocket (NIP-01), HTTP bridge (NIP-98), media (Blossom), git (smart HTTP), NIP-05, and health probes' -- and its actual route construction (media_router, git_router at router.rs:39-49 onward) were re-opened at this node's recorded revision and match architecture-containers-relay.md's route table with no discrepancy found; no divergence was found between that container node's specific line citations (state.rs AppState fields, router.rs route construction, main.rs shutdown sequencing) and the current source at the same, unmoved commit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:1-50"
  - statement: "Issue #936's Definition of Done requires that the node states implementation responsibility and what it deliberately does not own, names public interfaces/entry points and important dependencies, links owned source paths and representative tests, and avoids restating domain semantics already canonical in capability/layer/interface nodes."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#936 definition of done"
relationships:
  - type: references
    target: architecture-containers-relay
---

# buzz-relay: implementation reference

`crates/buzz-relay` is the Rust/Axum crate realizing Buzz's NIP-01 WebSocket relay
binary: NIP-01 wire parsing, per-connection lifecycle and admission control, the
transport-neutral EVENT ingestion pipeline shared by WebSocket and the HTTP bridge,
REQ/historical-query and live-fanout delivery, the community-scoped connection
registry, and the runtime conformance harness that traces relay decisions for replay
against a TLA+ specification. `architecture-containers-relay` already documents this
same crate at the container-architecture altitude -- its responsibility, listeners,
route table, outbound systems, and graceful-shutdown/health-probe behavior. This node
goes one layer deeper: concrete modules, functions, and tests in the WebSocket
protocol/connection/ingestion pipeline, plus an evidenced gap between the crate's
1087 test functions and what this repository's test-running commands actually
execute. Given the crate's size (~41k lines across top-level files alone, plus
~29.7k in `api/`, ~23.6k in `handlers/`, ~6.4k in `audio/`), this node does not
attempt exhaustive coverage of every handler -- see *Scope and omissions*.

## Target

Two targets, neither of which carries a corpus node id yet (checked directly against
`origin/launchpad`'s corpus tree at this node's recorded revision), so no `implements`
edge is declared toward either -- both are named here by path instead, per
`AGENTS.md`'s rule against inventing an edge to a nonexistent id:

- **The crate's own module documentation as a self-specifying contract** --
  `crates/buzz-relay/src/lib.rs`'s crate doc (`#![deny(unsafe_code)]`,
  `#![warn(missing_docs)]`, "NIP-01 WebSocket relay"), `connection.rs`'s stated
  lifecycle ("semaphore -> challenge -> recv/send/heartbeat loops -> cleanup"), and
  `handlers/ingest.rs`'s "two doors, one room" claim that WebSocket EVENT and HTTP
  `POST /events` share one pipeline. These are self-authoritative: the crate states
  them and the crate is also where they are enforced.
- **`docs/spec/MultiTenantRelay.tla`**, via `crates/buzz-relay/src/conformance/mod.rs`'s
  wire points. The conformance module's own doc comment names `ingest.rs`'s
  `check_channel_membership` call site and the two `dispatch_persistent_event` sites
  as where relay decisions are projected into `TraceStep`s for replay by the separate
  `buzz-conformance` checker against this spec. `buzz-conformance` itself has an
  unmerged sibling implementation-reference node in this same batch (issue #923); this
  node does not declare a relationship to it, since it is not yet present on
  `origin/launchpad`.

`architecture-containers-relay`, already merged, describes this same crate from the
container-architecture altitude. It was authored by reading `buzz-relay`'s own source
directly, not the reverse, so it is a sibling description at a different altitude --
documented below as a `references` relationship, not as an `implements` target,
following the same reasoning the unmerged `buzz-relay-mesh` sibling node reaches about
the identical container node.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-relay/src/protocol.rs` -- `ClientMessage::parse`, `RelayMessage::{auth_challenge,event,notice,eose,ok,closed,count}` | NIP-01 wire parsing/formatting, both directions | Enforces `MAX_SUB_ID_LENGTH`/`MAX_FILTERS_PER_REQ`; 8 in-file unit tests |
| `crates/buzz-relay/src/connection.rs` -- `ConnectionState`, `AuthState`, `handle_connection` | Per-socket WS lifecycle: "semaphore -> challenge -> recv/send/heartbeat loops -> cleanup" | `send_tx`/`ctrl_tx` are separate channels so control frames (Pong/Close) have priority drain over data; `AUTH_TIMEOUT` = 5s |
| `crates/buzz-relay/src/admission.rs` -- `check_principal`, `ws_admission_budget`, `AdmissionError` | Per-principal, per-limit-type admission/rate-limit control ahead of handler dispatch | Generic over a `RateLimiter` trait; 4 in-file unit tests with a stub limiter |
| `crates/buzz-relay/src/handlers/auth.rs` -- `handle_auth`, `extract_auth_tag_json` | NIP-42 AUTH challenge-response and NIP-OA `auth`-tag delegation extraction | Doc comment: "pure crypto verification -- no API tokens, no JWT, no DB token lookups" |
| `crates/buzz-relay/src/handlers/ingest.rs` -- `ingest_event`, `IngestAuth::{Nip42,Http}` | The crate's own "two doors, one room" claim: shared WS/HTTP validation-storage-fanout pipeline | Wired to the conformance trace seam (see *Target*); largest file in the crate (5524 lines) |
| `crates/buzz-relay/src/handlers/event.rs` -- `handle_event`, `dispatch_persistent_event`, `fan_out_pubsub_event` | WS EVENT command dispatch into `ingest_event`, plus the live-fanout delivery half (Redis pub/sub -> locally-subscribed sockets) | `fan_out_pubsub_event` is the read side of the same pub/sub channel `dispatch_persistent_event`'s persistence path publishes to |
| `crates/buzz-relay/src/handlers/req.rs` -- `handle_req`, `MAX_SUBSCRIPTIONS`, `FILTER_QUERY_CONCURRENCY`, `MAX_EXPLICIT_CHANNEL_VALUES` | REQ: subscribe, deliver historical events, then EOSE | One `buzz_db::EventQuery` per NIP-01 filter (OR semantics), bounded to 4 concurrent per request |
| `crates/buzz-relay/src/handlers/close.rs` -- `handle_close` | CLOSE: cancel a named subscription | 35 lines |
| `crates/buzz-relay/src/subscription.rs` -- `SubscriptionRegistry` | `(channel, kind)` fan-out index shared by `handle_req`'s registration path and `fan_out_pubsub_event`'s delivery path | 1967 lines, 34 in-file unit tests |
| `crates/buzz-relay/src/state.rs` -- `ConnectionManager`, `CommunityConnectionRegistry`, `run_registered_community_connection`, `AppState::{revalidate_live_communities,disconnect_community_clusterwide}` | Community-scoped connection lifecycle: an immediate pub/sub broadcast path plus a periodic revalidation backstop for Redis's lossy offline-subscriber semantics | `ConnectionManager`'s `draining` flag is sticky so a registration racing a restart still self-signals |
| `crates/buzz-relay/src/main.rs` -- `run_community_revalidator` | Drives `revalidate_live_communities` on a periodic timer | Not previously named at the container-node altitude |
| `crates/buzz-relay/src/conformance/mod.rs` -- wire points in `ingest.rs` | Relay-side half of the TLA+ conformance trace seam (see *Target*) | The checker (`buzz-conformance`) is a separate, undeclared-dependency crate |

## Divergences

None found, checked as follows:

- `router.rs`'s `build_router` doc comment and route construction were re-opened at
  this node's recorded revision (unchanged from `architecture-containers-relay`'s own
  recorded revision) and match that node's route table with no discrepancy.
- `main.rs`'s community-revalidation timer (`run_community_revalidator`, calling
  `AppState::revalidate_live_communities`) was checked against `state.rs`'s own doc
  comment describing itself as "the durable backstop for Redis pub/sub's lossy
  offline-subscriber semantics" -- the mechanism is real and wired, not merely
  documented.
- `handlers/ingest.rs`'s "two doors, one room" doc-comment claim was checked against
  `IngestAuth`'s actual two variants (`Nip42`, `Http`) and `ingest_event`'s single
  entry point taking either -- the code matches the claim.

An empty divergence section on a node checked against real code is itself a claim, per
the template's evidence expectations -- the three checks above are what that claim
rests on, not silence. This check was not exhaustive across the whole crate; see
*Scope and omissions* for what was not read.

## Verification

`cargo test -p buzz-relay` was not run for this node (the crate requires Postgres and
Redis for the majority of its integration-shaped tests, and building it is expensive);
instead, this node establishes what runs it, from the repository's own test-running
commands:

- **`just test-unit`** (the `cargo-nextest` branch) runs exactly one buzz-relay-scoped
  step: `test(/^api::admin::/)` minus two explicitly excluded tests, covering the 95
  test functions across `api/admin/mod.rs` (85) and `api/admin/auth.rs` (10). The
  recipe's own inline comment states this exists because no other lane in this
  repository executed those non-ignored tests at all.
- **`scripts/run-tests.sh`** (`run_unit_tests`/`run_integration_tests`, used by `just
  test`) never names `buzz-relay` by package flag, and its final `cargo test --test
  '*'` step cannot reach buzz-relay's in-file tests either, since the crate has no
  `tests/` directory.
- **`.github/workflows/ci.yml`**'s `unit-tests` job runs only `just test-unit` (the
  `api::admin`-scoped subset above). Its `backend-integration` job archives
  `buzz-relay --lib` but every consuming step passes `--run-ignored ignored-only`
  with a hand-enumerated filter naming specific `#[ignore]`d test paths or individual
  test names (`api::invites::tests`, `handlers::relay_admin::tests`, and several named
  `api::admin::tests::` functions) -- never a blanket run of the crate's `#[ignore]`d
  suite, and never the crate's non-ignored tests outside `api::admin`.

Net effect: of the crate's 1087 test functions, roughly 95 (`api::admin`) run in CI's
unit-tests job, a further small hand-enumerated set of `#[ignore]`d tests run in
CI's backend-integration job, and everything else -- including every test in
`protocol.rs`, `connection.rs`, `admission.rs`, `subscription.rs`, and the bulk of
`handlers/event.rs`/`req.rs`/`ingest.rs`/`close.rs` this node documents above -- has
no verified execution path in this repository's committed tooling. No separate CI job
or manual-review procedure specific to this crate's WS protocol/connection pipeline
was found beyond the workspace-wide `just ci` gate (which does not execute these
tests either, since `just ci` calls `test-unit`, not a broader target).

## Relationships

- references: architecture-containers-relay

## Scope and omissions

**This node covers** `buzz-relay`'s implementation responsibility for the NIP-01
WebSocket protocol layer: wire parsing/formatting (`protocol.rs`), per-connection
lifecycle and admission control (`connection.rs`, `admission.rs`), the shared
WS/HTTP EVENT ingestion pipeline (`handlers/ingest.rs`, `handlers/event.rs`), REQ/
historical-query and live-fanout delivery (`handlers/req.rs`, `subscription.rs`),
CLOSE (`handlers/close.rs`), community-scoped connection lifecycle (`state.rs`'s
`ConnectionManager`/`CommunityConnectionRegistry`), the relay-side conformance trace
seam, its module-level ownership boundaries, and the evidenced gap between its test
suite and what this repository's test-running commands actually execute.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The container-level responsibility, technology, listener/route table, outbound systems, graceful shutdown, and health-probe behavior | `architecture-containers-relay` |
| The full Nostr wire protocol and kind registry semantics | `ARCHITECTURE.md` §2-3, `crates/buzz-core/src/kind.rs` |
| Git smart HTTP hosting (`api/git/`, 10 files) | `architecture/flows/git-push.md` |
| Blossom media upload/download (`api/media.rs`) | `architecture/flows/media-upload.md`, `media-download.md` |
| Huddle voice audio relay (`audio/`, 6 files) | `architecture/flows/huddle-audio.md` |
| Push notification lease/delivery (`handlers/push_lease.rs`, `push_runtime.rs`) | `architecture/flows/push-notification.md` |
| Workflow webhook/event triggers (`workflow_sink.rs`, `api/workflows.rs`) | `architecture/flows/workflow-execution.md` |
| Search-backed queries within REQ/bridge (`buzz-search` integration inside `req.rs`) | `architecture/flows/search-query.md` |
| Inter-relay mesh wiring (`mesh_boot.rs`) and the mesh crate itself | The (unmerged, this batch) `buzz-relay-mesh` implementation-reference node |
| Moderation/relay-admin/identity-archive/product-feedback command handlers (`handlers/moderation_*.rs`, `relay_admin.rs`, `identity_archive.rs`, `product_feedback.rs`, `report*.rs`) | Not read in depth for this node; named in *Implementation surface* only where they intersect the admission/test-gate findings above |
| Every per-kind ingestion/side-effect rule inside `handlers/ingest.rs` (5524 lines) and `handlers/side_effects.rs` (3791 lines), the two largest files in the crate | Not exhaustively read; this node documents their role in the pipeline, not their per-kind bodies |
| Prometheus metrics (`metrics.rs`), OpenTelemetry wiring (`telemetry.rs`), config parsing (`config.rs`, 2378 lines), NIP-11 document generation (`nip11.rs`) | Not read for this node |

**Expected but not verified when this node was written:**

- **Whether the ~92 test functions not run by any documented gate would pass if
  executed.** This node establishes that they are not run, not whether they are
  currently green -- distinct claims, and only the first is evidenced here.
- **Whether developers run `cargo test -p buzz-relay --lib` manually during local
  work on the WS protocol/connection pipeline.** Plausible, per the INFERENCE entry
  above, but not verifiable from the repository alone.
- **Whether any of the thirteen flow nodes this node's evidence ledger confirms cite
  the same source paths also describe behavior that has since diverged from this
  node's own reading.** Only a citation-presence check was performed (grepping each
  flow node's evidence for `crates/buzz-relay` paths), not a line-by-line
  cross-verification of their claims against current source.
