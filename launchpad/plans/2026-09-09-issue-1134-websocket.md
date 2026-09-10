Issue #1134 — task: document layers/networking/websocket.md
Stated size: no `Size` line; scope is exactly one hand-authored corpus node  ->  cap: 5 steps

Provenance: worktree `__worktrees/task-1134-websocket`, branched from `origin/launchpad`
at `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`git rev-parse HEAD` inside the worktree).

ALREADY TRUE  (verified by reading the files, not from notes)

  This subject is heavily pre-owned. Five merged nodes were read IN FULL before any
  drafting, and each one's actual coverage was recorded rather than assumed:

    `verification-contracts-websocket` — owns the WebSocket *test contract*: the five
      inbound / six outbound NIP-01 message shapes parsed and formatted by
      `crates/buzz-relay/src/protocol.rs`, the NIP-42-gated accept/reject behaviour for
      EVENT and REQ, CLOSE's deliberate lack of an auth gate, the six tests that exercise
      all of that, and the precise gap between "a test exists" and "a lane runs it".
    `architecture-flows-websocket-connection` — owns the *connection flow* end to end:
      the `/` route's content negotiation, host-to-community binding, the 404/503
      pre-upgrade paths, the community-active and connection-semaphore admission checks,
      the four-tasks-around-one-CancellationToken structure, per-variant dispatch,
      the `max_frame_bytes` rejection, binary-frames-decoded-as-text, slow-client
      backpressure, every termination path and the cleanup that follows.
    `architecture-flows-websocket-authentication` — owns the NIP-42 challenge/response
      round trip, the 5s `AUTH_TIMEOUT`, the ban / allowlist / membership gates, NIP-OA
      owner delegation, and per-message-type auth enforcement.
    `architecture-principles-nostr-first` — owns the *design invariant* that new backend
      capability is modelled as a signed Nostr event rather than a new HTTP JSON route,
      where that invariant is written down, and the current route inventory that already
      sits outside it.
    `implementation-crates-buzz-ws-client` — owns the client crate: its public surface,
      its timeout constants, its three consumers, and its verification.

  Unmerged #609 siblings additionally own, by subject (their ids may NOT be targeted):
  connection admission (#1121), connection lifecycle incl. client timeouts and close
  frames (#1122), connection limits incl. the frame-byte cap (#1123), transport
  heartbeat/ping-pong (#1125), the HTTP surface (#1127), slow-client backpressure (#1132).

  What is left genuinely unowned, established by reading the source directly:

    (a) `crates/buzz-relay/src/handlers/ingest.rs` documents `IngestAuth` as
        "transport-neutral" and `ingest_event` as "Shared by WebSocket and HTTP
        transports. The caller constructs `IngestAuth` from their transport-specific auth
        mechanism and maps the result to their transport-specific response format." No
        merged node states that the two transports share one ingest core.
    (b) The same file rejects two kinds on HTTP only —
        `auth.is_http() && (kind_u32 == KIND_GIFT_WRAP || kind_u32 == KIND_PRESENCE_UPDATE)`
        -> `"invalid: kind {n} is only accepted via WebSocket"`. No merged node states
        that any capability is WebSocket-exclusive at the relay.
    (c) The relay itself labels its own metrics by transport
        (`"transport" => "websocket"` in `connection.rs`, `"transport" => "http"` in
        `api/bridge.rs`, and `reject_with_transport` in `ingest.rs`) — the repository
        models these as two transports over one protocol, in code.
    (d) The outbound writer is THREE prioritised queues, not one: data
        (`send_buffer_size`), control (fixed capacity 8), and restart (capacity 1), with a
        `biased` select ordering restart > cancel > control > data; data frames are
        `feed`-batched up to `MAX_WS_SEND_BATCH = 64` before a single `flush`, while
        control frames flush individually. `architecture-flows-websocket-connection` says
        only "prioritizing control frames over data" — the third queue, the fixed control
        capacity and the batching discipline are not stated anywhere in the corpus.

  Divergence found while gathering evidence (NOT fixed here, NOT folded in):
  `crates/buzz-cli/src/client.rs`'s `publish_ephemeral_event` doc comment says "The relay
  rejects ephemeral kinds (20000–29999) over HTTP", and `implementation-crates-buzz-ws-client`
  repeats that claim. The relay's actual gate blocks exactly two kinds — 1059
  (`KIND_GIFT_WRAP`, which is not ephemeral) and 20001 (`KIND_PRESENCE_UPDATE`) — so the
  comment is wrong in both directions. Reported as a candidate follow-up task.

  Conclusion: a node IS warranted, but narrower than the issue's headline. It is the
  transport-layer concept — one protocol, two transports, one of them strictly more
  capable — and NOT a restatement of the connection flow, the auth flow, the test
  contract, the nostr-first principle, or the client crate.

STEP 1  Write the node at `launchpad/docs/corpus/layers/networking/websocket.md`  [independent]
        with front matter per the brief: `id: layers-networking-websocket`,
        `type: layers`, `status: draft`, `origin: launchpad`, audiences
        `agent`/`developer` (not `operator` — this node makes no claim about running the
        relay; the operator-facing limits belong to #1123/#1132). Exactly one commit-only
        FACT, recording `29ca9b189bd3f639ba09c972b57c70538c0860c6`.
        done when: the file exists and its front matter carries only the seven schema-
        permitted fields, with one and only one commit-only evidence entry.

STEP 2  Write the evidence ledger so every substantive claim in the body has an     [needs 1]
        entry, and every FACT cites a bare repo-relative path to a file actually opened
        while authoring: `crates/buzz-relay/src/protocol.rs`,
        `crates/buzz-relay/src/connection.rs`, `crates/buzz-relay/src/router.rs`,
        `crates/buzz-relay/src/handlers/ingest.rs`, `crates/buzz-relay/src/api/bridge.rs`,
        `crates/buzz-core/src/kind.rs`, `crates/buzz-cli/src/client.rs`. No line numbers
        (#1459 — unverified against file length). No GitHub URLs. The
        buzz-cli-comment-versus-relay-gate divergence is an INFERENCE with an honest
        confidence, since it is a comparison this author drew, not a claim either file
        makes.
        done when: no FACT in the ledger rests on a citation shape the validator reports
        UNVERIFIED, other than the single provenance entry.

STEP 3  Write the body as a concept node per `templates/concept.md`: a one-sentence   [needs 2]
        definition first, then the transport-capability argument (server-initiated
        frames; the two WebSocket-only kinds; the shared transport-neutral ingest core),
        then the prioritised-queue property, then a Boundary section naming ALL FIVE
        merged nodes by id with exactly what each owns, plus the six sibling subjects by
        subject rather than by id.
        done when: the body contains no restatement of the connection lifecycle, the
        NIP-42 round trip, the message-shape catalogue, or the client crate's surface —
        each is referenced, not reproduced.

STEP 4  Add `relationships`, `references`-typed, only to ids confirmed present in     [needs 3]
        the merged-ids list: `architecture-flows-websocket-connection`,
        `architecture-flows-websocket-authentication`, `verification-contracts-websocket`,
        `architecture-principles-nostr-first`, `implementation-crates-buzz-ws-client`,
        `implementation-crates-buzz-relay`. No #609 sibling id.
        done when: each target is grepped out of the merged-ids file before it is written,
        and `git ls-tree origin/launchpad` confirms the backing file exists on the base
        branch.

STEP 5  Validate, self-review, stamp, commit.                                         [needs 4]
        `python3 launchpad/project-intelligence/corpus/validate.py` exits 0; then a full
        self-review of every DoD bullet and every evidence entry re-read against its
        source BEFORE stamping; then the unittest stamp as a sole foreground command with
        `timeout: 600000`; then `git add` + `git commit -s` as a separate call.
        done when: validator exits 0, the stamp run's final line is `OK`, and the commit
        exists. No push, no PR.
