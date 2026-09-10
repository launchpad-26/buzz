# Plan — issue #1122: document `layers/networking/connection-lifecycle.md`

Feature #609 (protocol and networking layer corpus). One flow node, one commit,
no push, no PR.

## ALREADY TRUE

- `origin/launchpad` is at `96782d1035f5bcb878edaa4b75b95ccc85ef4ce0`; worktree
  `__worktrees/task-1122-connection-lifecycle` on branch
  `task/1122-connection-lifecycle` is checked out there.
- `launchpad/docs/corpus/layers/networking/` does not exist yet — this is the
  first node in it.
- All 78 merged nodes under `launchpad/docs/corpus/layers/` carry `type: layers`
  (78/78, checked against the merged-id index). Brief decision 1 applies.
- `architecture-flows-websocket-connection` is **already merged** and narrates the
  relay-internal connection flow: host binding, shutdown 503, community-active
  check, connection semaphore, NIP-42 challenge, the four-task set, the auth gates
  and trust boundaries, a failure table, and cleanup. It never mentions
  `buzz-ws-client`, and it does not cover the 1012 restart close.
- Sibling issues in this Feature own the depth for individual steps:
  #1121 connection-admission, #1123 connection-limits, #1125 heartbeat,
  #1126 host-routing, #1132 slow-client-handling, #1134 websocket. None is merged,
  so none may be a `relationships` target.
- Code read in full: `crates/buzz-relay/src/connection.rs`,
  `crates/buzz-ws-client/src/connection.rs`; read in part:
  `crates/buzz-relay/src/state.rs`, `crates/buzz-relay/src/router.rs`,
  `crates/buzz-relay/src/protocol.rs`.
- Candidate relationship targets confirmed present in the merged-id index:
  `architecture-flows-websocket-connection`,
  `architecture-flows-websocket-authentication`, `architecture-containers-relay`,
  `implementation-crates-buzz-relay`, `implementation-crates-buzz-ws-client`,
  `verification-contracts-websocket`, `layers-lifecycle-graceful-shutdown`,
  `layers-lifecycle-cancellation`, `layers-lifecycle-resource-cleanup`.

## STEP 1 — fix the non-duplication boundary before drafting

The merged flow node is close enough that a careless draft would restate it.
This node's distinct subject: **the networking-layer, two-actor lifecycle** —
`buzz-ws-client` and `buzz-relay` — from socket open to the final Close frame,
including the client's own timeouts and terminal states, and the three distinct
close-frame shapes the relay emits. Relay-internal admission gates, auth gates and
trust boundaries stay the merged node's canonical content and are linked, not
restated.

*Done when:* every section of the draft either narrates something the merged node
does not, or explicitly defers to it by id.

## STEP 2 — write front matter

Seven permitted fields only. `id: layers-networking-connection-lifecycle`,
`type: layers`, `status: draft`, `origin: launchpad`, audiences `agent`,
`developer`, `operator` (a relay operator reads close codes and drain behaviour).
Exactly one commit-only FACT (provenance). Every other FACT cites a bare
repo-relative path opened during evidence gathering. One INFERENCE for the
absence of client-side reconnect. No line numbers.

*Done when:* front matter validates and no second commit-only FACT exists.

## STEP 3 — write the body per `templates/flow.md`

Sections: `A note on type` (house style, matching `layers-lifecycle-*`), Flow
statement, Sequence (every step cited), Diagram (Mermaid `sequenceDiagram`,
participants matching the prose actors), Outcome (success plus real failure
paths), Boundary, Relationships, Scope and omissions (two distinct things: what it
does not cover and who owns it; and separately what could not be verified).

*Done when:* all seven template sections present and every sequence step carries a
citation.

## STEP 4 — validate

`python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

*Done when:* exit 0 with no error naming this node.

## STEP 5 — stamp, then commit

Sole-command, unpiped, foreground:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Then, in a separate call, `git add` + `git commit -s`.

*Done when:* commit exists on `task/1122-connection-lifecycle`. Stop there.

## GATES

- Validator exit 0.
- Unit-test stamp reports `OK` before any commit.
- No `relationships` target outside the merged-id index; no sibling from #609.
- Exactly one hand-authored file changed, plus the plan.

## BUDGET

5 steps. Two files touched: the node and this plan. No code changes.

## OPEN

- Whether the corpus wants this node and `architecture-flows-websocket-connection`
  to coexist long-term, or whether one should eventually `supersedes` the other, is
  not this node's call — flagged in Scope and omissions rather than decided.

## LEFT OUT

- The relay-mesh cluster-wide disconnect paths
  (`disconnect_pubkey_clusterwide`, `disconnect_community_clusterwide`) — a
  separate subject, and #1129 owns `layers/networking/relay-mesh.md`.
- The huddle-audio WebSocket handler and git smart-HTTP transport — separate
  connection flows.
- Numeric defaults for `max_frame_bytes`, `send_buffer_size`,
  `slow_client_grace_limit` — operator-configurable; #1123 and #1132 own them.
