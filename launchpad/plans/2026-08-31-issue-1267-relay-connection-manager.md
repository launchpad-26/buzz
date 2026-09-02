# Plan: issue #1267 — platforms/relay/connection-manager corpus node

## ALREADY TRUE

- Feature #614 ("runtime platform corpus exists") is the parent PRD; this
  task authors exactly one node,
  `launchpad/docs/corpus/platforms/relay/connection-manager.md`.
- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  or in this worktree — this is the first node under `platforms/`.
- `node.schema.json`'s `type` enum includes `platforms` as one of PRD #602's
  thirteen named surfaces; no `platforms`-specific template exists in
  `launchpad/docs/corpus/templates/` (confirmed by listing the directory).
- `launchpad/docs/corpus/templates/component.md` is a real, merged template
  (type: implementation) whose section shape — Responsibility, Public
  interface, Dependencies, Boundary, Relationships, Scope and omissions —
  is the closest structural analog for documenting one standing
  component-like subsystem, even though its own front matter directs
  `type: implementation` rather than `platforms`.
- `crates/buzz-relay/src/state.rs` defines `ConnectionManager` (tracks live
  Nostr WebSocket connections, keyed by connection id, with pubkey lookup,
  fan-out send, disconnect, and graceful-drain methods) and
  `CommunityConnectionRegistry` (a lighter-weight, socket-type-agnostic
  lifecycle registry shared by both WebSocket and audio/huddle connections).
  `crates/buzz-relay/src/connection.rs` is the WebSocket handler that
  registers/deregisters against both.
- `launchpad/docs/corpus/architecture/flows/websocket-connection.md`
  (id `architecture-flows-websocket-connection`) already exists on
  `origin/launchpad` and documents the WS connect → NIP-42 auth → terminate
  flow in detail, including calls into the connection manager at each step.
  Per known finding #5, this node must not duplicate that — it should
  reference it and scope itself to what that flow node does not cover:
  the connection-manager/registry component itself (its data model, full
  public interface, cross-connection-type sharing, cross-pod fan-out,
  graceful-drain mechanics, and the periodic revalidation backstop), rather
  than one connection's request/response sequence.
- Sibling issue #1263 (app-state) is not on `origin/launchpad` yet — no
  relationship may target it; scope stays on per-connection lifecycle, not
  the global `AppState` struct.

## STEP 1 — Confirm scope boundary against the existing flow node

Read `architecture/flows/websocket-connection.md` in full (done). Identify
what it already claims about the connection manager (registration order,
disconnect_pubkey, disconnect_community, cleanup ordering) versus what it
does not touch: `CommunityConnectionRegistry`'s sharing with the audio
handler, `drain_all` / `drain_all_jittered` graceful-shutdown mechanics,
`disconnect_pubkey_clusterwide` / `disconnect_community_clusterwide`
cross-pod Redis fan-out, and `revalidate_live_communities`'s periodic
durable-state backstop. Scope this node to the latter set, declaring
`references` toward the flow node for the former.

## STEP 2 — Gather evidence from source

Read `crates/buzz-relay/src/state.rs` (ConnEntry, CommunityConnectionRegistry,
CommunityConnectionGuard, ConnectionManager and all their methods,
`run_registered_community_connection`, `revalidate_registered_communities`),
`crates/buzz-relay/src/connection.rs` (register/deregister call sites),
`crates/buzz-relay/src/audio/handler.rs` (registry sharing with the huddle
handler), and `crates/buzz-relay/src/main.rs` (drain invocation, cross-pod
conn-control consumer, periodic revalidator task, connection-count metrics
poller). Record every symbol and line range actually opened.

## STEP 3 — Record the revision

`git rev-parse HEAD` in this worktree, cited as the provenance FACT.

## STEP 4 — Draft the node

Front matter: `id: platforms-relay-connection-manager`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [developer, operator,
agent]`. Body follows component.md's section shape (Responsibility, Public
interface, Dependencies, Boundary, Relationships, Scope and omissions),
explicitly noting in the body that no `platforms`-specific template exists
yet and that the shape is borrowed from `component.md` as a structural aid,
not authority. One `relationships` entry: `references` →
`architecture-flows-websocket-connection` (confirmed present on
`origin/launchpad`).

## STEP 5 — Validate, then commit

Run the corpus unittest suite as its own sole Bash call, then
`validate.py` with the new file present and with it temporarily removed to
confirm zero new FAIL lines, then stage and commit both files with `-s`.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`, as the sole content of its own Bash call.
- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with the new node present.
- Removing the new node and re-running `validate.py` reproduces the identical pre-existing FAIL set (no new FAILs attributable to this node).
- Every DoD checklist bullet from issue #1267 satisfied.

## OPEN

- Whether a `platforms`-specific template lands later and reshapes this
  node's structure (per `AGENTS.md`'s documented no-template path, expected).
- Whether sibling issue #1263 (app-state) merges before this task, which
  would make a `references`/`depends-on` edge toward it valid; not the case
  at the time of writing.

## LEFT OUT

- The WS connect/auth/terminate request-response sequence itself — owned by
  `architecture-flows-websocket-connection`.
- NIP-01 message-level semantics (EVENT/REQ/COUNT dispatch, filter matching)
  — owned by their own handler modules.
- The moderation/ban system's own rules for creating or lifting a ban —
  only the connection-manager-side effect (`disconnect_pubkey`) is in scope.
- The global `AppState` struct and its full field set — sibling issue #1263,
  unmerged.
