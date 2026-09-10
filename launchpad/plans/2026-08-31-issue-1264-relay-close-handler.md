# Plan: issue #1264 — document platforms/relay/close-handler.md

## ALREADY TRUE

- Issue #1264 (parent Feature #614) asks for exactly one new canonical corpus
  node at `launchpad/docs/corpus/platforms/relay/close-handler.md`.
- No file exists yet at that path, and `launchpad/docs/corpus/platforms/`
  does not exist at all on `origin/launchpad` — confirmed via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`.
- `launchpad/docs/corpus/templates/component.md` is merged and present
  (`type: implementation`, rustdoc-adapted shape: Responsibility / Public
  interface / Dependencies / Boundary / Relationships / Scope and omissions).
  No `platforms`-specific template exists in `templates/`. Per prior-batch
  convention (sibling `platforms/**` nodes), this node borrows
  `component.md`'s section shape but sets front matter `type: platforms`
  (the schema enum value matching this node's actual corpus surface), and
  says so explicitly in its Scope section since this is an inference, not a
  merged template decision.
- The real handler is `crates/buzz-relay/src/handlers/close.rs`
  (`handle_close`), 36 lines, dispatched from
  `crates/buzz-relay/src/connection.rs:639-640`
  (`ClientMessage::Close(sub_id) => handlers::close::handle_close(...)`).
  Parsing lives in `crates/buzz-relay/src/protocol.rs` (`"CLOSE" =>` arm,
  lines 146-158) and response formatting in `RelayMessage::closed`
  (`protocol.rs:209-211`). Registry-side removal is
  `SubscriptionRegistry::remove_subscription` in
  `crates/buzz-relay/src/subscription.rs:238-267`, and topic release-counting
  is `buzz_pubsub`'s `release_topic` (`crates/buzz-pubsub/src/lib.rs:215+`).
- An e2e test, `test_close_subscription_stops_delivery`
  (`crates/buzz-test-client/tests/e2e_relay.rs:538-574`), exercises the
  close-then-no-more-delivery behavior end to end (marked `#[ignore]`,
  live-infra only, but present and read in full).
- `architecture/flows/websocket-connection.md` (id
  `architecture-flows-websocket-connection`) already documents connection
  teardown, including the disconnect-triggered `remove_connection` sweep at
  `connection.rs:288-301` that reuses the same `release_topic` cleanup this
  node describes for the client-initiated `CLOSE` command. This node scopes
  itself to the explicit `CLOSE` command path and references that node for
  the disconnect path rather than re-describing it.
- `architecture/flows/live-fanout.md` documents post-commit event dispatch
  and fan-out, not subscription teardown — no overlap requiring a
  `references` edge for this node's actual claims.

## STEP 1 — Confirm scaffolding state and evidence set (done, this session)

Confirmed: target file absent, template absent-for-`platforms`, sibling
`architecture-flows-websocket-connection` node covers connection-teardown
CLOSE handling and is citable by id. Evidence gathered by direct source
reads (`close.rs`, `protocol.rs`, `subscription.rs`, `connection.rs`,
`buzz-pubsub/src/lib.rs`, `e2e_relay.rs`) — no `evidence.py`/`scaffold.py`
tooling invocation needed since the template branch is "absent altogether"
per `AGENTS.md`'s documented path (hand-author front matter).

## STEP 2 — Hand-author front matter

Write `id: platforms-relay-close-handler`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`, and one evidence entry per substantive claim below, each `FACT`
citing an opened file (or `INFERENCE` with confidence where the claim is
reasoned rather than read verbatim, e.g. the `type: platforms` convention
choice itself and the missing-template gap).

## STEP 3 — Write the body

Sections, following `component.md`'s shape adapted for a message handler
rather than a whole component:
- Purpose/scope: the `CLOSE` command handler for NIP-01 subscription
  cancellation.
- Responsibility: what `handle_close` does (three effects: per-connection
  map removal, registry deregistration + topic release, `CLOSED` ack).
- Public interface: `handle_close` signature; `ClientMessage::Close` parsing
  contract (and its parity gap vs. `REQ`/`COUNT` — no empty/length
  validation on the `sub_id`).
- Dependencies: `ConnectionState.subscriptions`, `AppState.sub_registry`,
  `buzz_pubsub::release_topic`, `RelayMessage::closed`.
- Ordering/idempotency behavior: deregister-before-ack ordering (comment at
  `close.rs:15-16`), and that an unknown `sub_id` still gets an
  unconditional `CLOSED` reply (no error surfaced to the client).
- Boundary: explicitly not the disconnect-triggered teardown path (owned by
  `architecture-flows-websocket-connection`), not `REQ`/subscription
  creation, not the channel-revocation partial-unsubscribe path
  (`remove_channel_subscriptions_scoped`).
- Relationships: `references` →
  `architecture-flows-websocket-connection` (confirmed present on
  `origin/launchpad`).
- Scope and omissions: named gaps — no dedicated unit test for `close.rs`
  itself found (only the `#[ignore]`d e2e test); NIP-01/NIP-45 spec text
  itself not fetched from an external source, only this repo's own
  NIP-11-derived constants.

## STEP 4 — Validate: zero new FAILs

Run `python3 launchpad/project-intelligence/corpus/validate.py` with the
new file present, then with it moved aside, and diff the FAIL sets — must
be identical. Then restore the file.

## STEP 5 — Earn the commit gate

Run the corpus unittest command alone (step 5a), then stage + commit (step
5b), per the two-separate-calls rule. Retry once on stamp refusal; stop and
report BLOCKED on a second failure.

## GATES

- `validate.py` introduces zero new FAIL lines versus the with-file-removed
  baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`, run as the sole content of its Bash call.
- Every evidence citation is a real, opened file (or a commit hash for the
  provenance entry); no citation is a bare directory.
- Every DoD bullet in issue #1264 is addressed by a body section or the
  Scope-and-omissions table.
- No `relationships[].target` other than `architecture-flows-websocket-connection`, confirmed present on `origin/launchpad`.

## OPEN

- Whether `type: platforms` is the durable convention or a placeholder that
  a later corpus-standards issue reshapes — flagged in the node's own body,
  not resolved here.
- Whether the `CLOSE` sub_id validation gap (no empty/length check, unlike
  `REQ`/`COUNT`) is intentional or a latent bug — documented as an observed
  asymmetry, not adjudicated; no runtime behavior change is in scope for
  this task.

## LEFT OUT

- Any change to `close.rs`, `protocol.rs`, `subscription.rs`, or their
  tests — this is a documentation-only task.
- A new unit test for `handle_close` — out of scope; the gap is named in
  Scope and omissions instead.
- Re-litigating `architecture-flows-websocket-connection`'s content —
  referenced, not duplicated or edited.
