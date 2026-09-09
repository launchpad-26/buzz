# Plan — issue #1150: document the EOSE message

**Issue**: launchpad-26/buzz#1150 (`type:task`, parent Feature #609)
**Target**: `launchpad/docs/corpus/layers/protocol/eose-message.md`
**Node id**: `layers-protocol-eose-message`
**Template**: `launchpad/docs/corpus/templates/concept.md`
**Provenance revision**: `29ca9b189bd3f639ba09c972b57c70538c0860c6` (worktree HEAD, confirmed
with `git cat-file -e`)

## Subject

`["EOSE", <subscription_id>]` — the relay→client frame that marks the end of the
stored-event phase of one subscription.

## Step 1 — evidence gathering (done before drafting)

Opened and read:

- `crates/buzz-relay/src/protocol.rs` — `RelayMessage::eose` constructs the
  two-element array; the message carries no payload beyond the subscription id.
- `crates/buzz-relay/src/handlers/req.rs` — the whole of `handle_req` and
  `handle_search_req`. Four EOSE emission sites, all in this file.
- `crates/buzz-relay/src/connection.rs` — `ConnectionState::send`, the single
  per-connection `send_tx` that both EOSE and live fan-out write into.
- `crates/buzz-relay/src/handlers/event.rs` — the fan-out dispatch that reaches
  the same `conn.send`.
- `crates/buzz-ws-client/src/message.rs` — client-side parse into
  `RelayMessage::Eose`.
- `crates/buzz-test-client/src/lib.rs` — `collect_until_eose`.
- `crates/buzz-test-client/tests/e2e_relay.rs` —
  `test_stored_events_returned_before_eose`, `test_eose_sent_for_empty_subscription`.
- `crates/buzz-pair-relay/src/lib.rs` and `crates/buzz-pair-relay/tests/integration.rs`
  — the sidecar relay's deliberately opposite ordering (EOSE **before** registration).
- `docs/nips/NIP-RS.md` — "The delivery barrier", a Buzz-own normative requirement
  stated in terms of end-of-stored-events.
- `docs/nips/` listing — no upstream numbered NIP file exists in this repository.

## Step 2 — the ordering question (the node's substance)

Answer it from `handle_req` directly rather than asserting a general rule:
registration precedes the historical query, so no event can fall in a gap; the
cost is that a live fan-out frame may reach the same outbound channel before the
EOSE and be indistinguishable from a stored one.

State honestly what could **not** be established: whether NIP-RS's delivery
barrier is actually satisfied, and whether duplicate delivery is observed in
practice — no test in the repository covers either.

## Step 3 — write the node

Body follows `templates/concept.md`'s required sections. Front matter per
`schema/node.schema.json`: seven permitted fields, `type: layers`,
`status: draft`, `origin: launchpad`, one commit-only provenance FACT.

Boundary discipline: `architecture-flows-historical-query` and
`architecture-flows-live-fanout` own the two flows either side of the marker —
link, do not restate. No relationship to any unmerged #609 sibling.

## Step 4 — validate

`python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

## Step 5 — self-review, then stamp and commit

Re-read every evidence entry against its source before stamping. Then run the
corpus test suite as a sole foreground command, confirm `OK`, and
`git commit -s`. Do not push; do not open a PR.
