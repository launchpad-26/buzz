# Plan — issue #1146: document the CLOSE message

**Issue:** launchpad-26/buzz#1146 (task, parent Feature #609)
**Target:** `launchpad/docs/corpus/layers/protocol/close-message.md`
**Node id:** `layers-protocol-close-message`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Worktree:** `__worktrees/task-1146-close-message`, branch `task/1146-close-message`
**Provenance revision:** `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`git rev-parse HEAD` in the
worktree; `git cat-file -e` exits 0)

## Subject

The client→relay `["CLOSE", <subscription_id>]` message — the verb a client uses to end a
subscription it opened with `REQ`. One independently maintainable idea.

## Step 1 — gather evidence (done before drafting)

Opened, and cited only from what was opened:

- `crates/buzz-relay/src/protocol.rs` — `ClientMessage::Close`, the `"CLOSE"` arm of
  `ClientMessage::parse`, `RelayMessage::closed`, and the parser unit test.
- `crates/buzz-relay/src/handlers/close.rs` — the whole 35-line handler.
- `crates/buzz-relay/src/connection.rs` — `handle_text_message` dispatch,
  `enforce_ws_admission`, `request_rejection_message`, and the `WsMessage::Close` arm of
  the receive loop.
- `crates/buzz-relay/src/subscription.rs` — `remove_subscription` /
  `remove_subscription_inner`.
- `crates/buzz-relay/src/handlers/req.rs` — the `conn.subscriptions` slot check that
  `CLOSE` frees.
- `crates/buzz-pubsub/src/lib.rs` — `release_topic`, for the downstream consequence only.
- Senders: `crates/buzz-test-client/src/lib.rs`,
  `desktop/src-tauri/src/native_relay_client.rs`,
  `mobile/lib/shared/relay/relay_session.dart`.
- Tests: `crates/buzz-test-client/tests/e2e_relay.rs`.

Confirmed absent: no upstream NIP-01 file in this repository (`docs/nips/` holds only
Buzz's own two-letter NIPs), so no claim about what the standard mandates may be a `FACT`
on a repo path.

**Done when:** every claim the draft intends to make names a source that was opened.

## Step 2 — write the front matter

`id: layers-protocol-close-message`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer]`. Ledger carries exactly one
commit-only `FACT` (the provenance entry). Upstream-NIP claims and issue-only claims are
`TEAM_KNOWLEDGE` with `provided_by`; reasoning is `INFERENCE` with honest `confidence`.

`relationships` — `references` edges only, each grepped in the merged-id list:
`implementation-crates-buzz-relay`, `implementation-crates-buzz-pubsub`,
`verification-contracts-nostr`, `architecture-flows-websocket-connection`,
`verification-e2e-relay`. No #609 sibling.

**Done when:** every field is one of the schema's seven and every target appears in the
merged-id list.

## Step 3 — write the body against `templates/concept.md`

Sections: Definition (with the mandatory disambiguation of `CLOSE` vs `CLOSED` vs the
WebSocket close frame), Background, Use cases, Comparison (`CLOSE` against `REQ`'s and
`COUNT`'s sub-id validation), Related nodes, Scope and omissions.

**Done when:** the definition names the boundary explicitly and no section documents
`CLOSED`'s own behaviour, the fan-out machinery, or the WebSocket transport frame.

## Step 4 — validate

`python3 launchpad/project-intelligence/corpus/validate.py`

**Done when:** exit status 0.

## Step 5 — self-review, stamp, commit

Re-read every evidence entry against its source before stamping. Then the verify-gate
suite as a sole foreground command, then `git add` + `git commit -s` as a separate call.
Stop at the local commit — no push, no PR.

**Done when:** the suite ends `OK` and the commit exists.
