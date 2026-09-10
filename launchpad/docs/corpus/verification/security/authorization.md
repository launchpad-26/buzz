---
id: verification-security-authorization
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "handle_event requires the connection to already be in AuthState::Authenticated (a completed NIP-42 handshake) before any event is dispatched, and separately rejects an event whose declared pubkey does not match the authenticated identity (except gift wraps) -- so authentication and signature-identity matching both complete before any channel-authorization check below runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:608-667"
  - statement: "check_channel_membership(tenant, state, ch_id, pubkey_bytes, channel) returns Ok(()) if the pubkey is a member of (tenant.community(), ch_id) per is_member_cached, and otherwise returns Ok(()) only if the channel's visibility is \"open\"; every other case returns Err(\"restricted: not a channel member\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:742-772"
  - statement: "ingest_event_inner calls check_channel_membership for every persistent event that resolves an h-tag channel, except a fixed skip-list (KIND_NIP29_JOIN_REQUEST, KIND_NIP29_CREATE_GROUP, KIND_STREAM_MESSAGE_EDIT, KIND_NIP29_EDIT_METADATA, KIND_NIP29_DELETE_EVENT, KIND_NIP29_DELETE_GROUP) whose own per-kind validators are documented as the authority instead; a failing result is propagated as IngestError::Rejected before any per-kind admin validator (validate_admin_event) runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2509-2551"
      - "crates/buzz-relay/src/handlers/ingest.rs:2655-2661"
  - statement: "KIND_NIP29_PUT_USER (kind:9000, the group-membership/role-grant command) is not in ingest_event_inner's skip-list, so a kind:9000 event scoped to a channel by its h tag is subject to the check_channel_membership gate like any other non-skip-listed channel-scoped kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2517-2522"
      - "crates/buzz-core/src/kind.rs:335"
  - statement: "handle_event's error branch forwards an IngestError::Rejected(message) to the client verbatim as the NIP-01 OK message's third field, with no additional wrapping or sanitization beyond that already applied when the message was constructed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:781-790"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs::test_private_channel_non_member_cannot_invite connects as an outsider holding no role in a private channel, submits a kind:9000 PUT_USER event naming that channel's h tag, and asserts the response is not accepted and its message contains \"not authorized\" or \"not a channel member\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:2476-2518"
  - statement: "e2e_relay.rs's own module doc-comment states its tests are #[ignore]-gated by default because they require a running relay instance, and names the command to run them: `cargo test --test e2e_relay -- --ignored` (optionally with RELAY_URL set)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:1-18"
  - statement: "test_private_channel_non_member_cannot_invite itself carries #[ignore] and is not stubbed with todo!() or an empty body -- its assertions exercise a real request/response round trip against a live relay, so its current state is \"gated pending a live relay\", not \"pending, no test exists\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:2477-2478"
  - statement: "For a private channel, validate_admin_event's own kind:9000 branch also contains an actor-authorization check (actor_role.is_none() => \"actor not authorized\") and an elevated-role-grant check (a non-elevated actor requesting an elevated role for someone else => \"only owners/admins may grant elevated roles\"), run after check_channel_membership and only reached if that gate already returned Ok."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:342-381"
  - statement: "Because check_channel_membership already rejects a true non-member of a private (non-open) channel before validate_admin_event runs, and kind:9000 is not skip-listed, the rejection that test_private_channel_non_member_cannot_invite observes is produced by check_channel_membership's generic gate rather than by validate_admin_event's own actor_role.is_none() branch, which the test's request never reaches."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2509-2551"
      - "crates/buzz-relay/src/handlers/side_effects.rs:342-381"
    confidence: 0.8
  - statement: "launchpad-26/buzz#1384's definition of done requires the document to state preconditions/context, action/event and observable expected outcome; name negative/error cases when they are part of the contract; link actual verification implementing the contract; and not claim coverage that is not present."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1384 definition of done"
  - statement: "capabilities-channels-channel-membership.md's own Boundary section names check_channel_membership and filter_fanout_by_access as enforcing membership as a read/write \"access gate\" on ordinary channel-scoped events, explicitly calling that \"a related but distinct concern\" that its own node does not cover -- leaving it unclaimed by that node at the recorded revision this node was checked against."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/capabilities/channels/channel-membership.md"
  - statement: "A targeted search of crates/buzz-test-client/tests/*.rs for test function names matching moderation- or operator-authorization rejection scenarios, and of crates/buzz-relay/src/api/operator.rs for the same, returned no matches at the recorded revision; a query-authorization-specific rejection test name was found only in e2e_persona.rs, which was not opened for this node."
    entry_class: FACT
    evidence:
      - "grep(pattern='fn test_.*moderat|fn test_.*operator', path='crates/buzz-test-client/tests/*.rs') -> no matches"
      - "grep(pattern='fn test_.*query.*author|fn test_.*scope.*quer', path='crates/buzz-test-client/tests/*.rs') -> crates/buzz-test-client/tests/e2e_persona.rs"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree contains architecture-principles-fail-closed-boundaries, architecture-principles-community-is-security-boundary and capabilities-channels-channel-membership as loaded node ids."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> architecture/principles/fail-closed-boundaries.md (id: architecture-principles-fail-closed-boundaries), architecture/principles/community-is-security-boundary.md (id: architecture-principles-community-is-security-boundary), capabilities/channels/channel-membership.md (id: capabilities-channels-channel-membership)"
relationships:
  - type: references
    target: capabilities-channels-channel-membership
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Channel-membership authorization gate — test contract

## Purpose and boundary

This node documents **one** authorization obligation: that a persistent, channel-scoped
event is rejected unless the sending pubkey is authorized to act in that channel, and
that this rejection happens regardless of the connection already holding valid NIP-42
authentication and the event's own signature already having been verified against that
authenticated identity. It covers only the relay's generic, pre-per-kind-validator
channel-membership gate (`check_channel_membership`) and the one negative test that
exercises it end to end. It does **not** cover every authorization surface named in
`launchpad-26/buzz#1384` -- channel *roles* (who may grant an elevated role once already
a member), moderation authorization, operator authorization, and query authorization are
each a different obligation with a different enforcement point; see *Limits* and *Scope
and omissions* below for what each of those does and does not have in the way of a
rejection test at this revision.

## Obligation

> A persistent event carrying an `h` tag that names a channel is rejected with a
> client-visible error, before any per-kind admin validator runs, unless the sending
> pubkey is an active member of that channel within the request's host-resolved
> community, or the channel's visibility is `open` -- and this rejection occurs even
> though the connection has already completed NIP-42 authentication and the event's
> Schnorr signature has already been verified to match that authenticated pubkey.

**Preconditions/context.** A WebSocket connection has completed NIP-42 authentication
(`AuthState::Authenticated`); the submitted event's declared pubkey matches that
authenticated identity; the event's kind is not one of the six kinds
(`KIND_NIP29_JOIN_REQUEST`, `KIND_NIP29_CREATE_GROUP`, `KIND_STREAM_MESSAGE_EDIT`,
`KIND_NIP29_EDIT_METADATA`, `KIND_NIP29_DELETE_EVENT`, `KIND_NIP29_DELETE_GROUP`) whose
own per-kind validators are the documented authority instead of this generic gate; and
the event carries an `h` tag naming a channel.

**Action/event.** The sending pubkey is not an active member of that channel in the
request's community, and the channel's `visibility` is not `open` (e.g. a private
channel the sender never joined).

**Observable expected outcome.** The relay responds with a NIP-01 `OK` message whose
third field is `false` (not accepted) and whose message text is
`"restricted: not a channel member"` -- forwarded verbatim from
`check_channel_membership`'s own error string, with no further wrapping.

## Verifying test(s)

- `crates/buzz-test-client/tests/e2e_relay.rs` --
  `test_private_channel_non_member_cannot_invite` -- connects as an outsider pubkey
  holding no role in a freshly created private channel, submits a `kind:9000` (NIP-29
  `PUT_USER`) event tagging that channel's `h` id and a target pubkey to add, and
  asserts the response is `!accepted` with a message containing `"not authorized"` or
  `"not a channel member"`.

This is the only automated test found, at the recorded revision, that submits a
channel-scoped event as a genuine non-member of a non-open channel and asserts the
specific rejection. It exercises the obligation through one concrete kind (`9000`); see
*Limits* for what that does and does not establish about the other kinds the same gate
applies to.

## How to run it

```bash
cargo test --test e2e_relay -- --ignored test_private_channel_non_member_cannot_invite
```

This test is gated behind `#[ignore]` because, per the test file's own module
doc-comment, the whole `e2e_relay` suite requires a running relay instance (reachable at
`RELAY_URL`, default `ws://localhost:3000`) with its Postgres/Redis dependencies up.
`just relay` (see repository root `CLAUDE.md`) starts that dependency stack; the full
suite convention is `cargo test -p buzz-test-client -- --ignored`, per
`crates/buzz-cli/TESTING.md`'s sibling pattern.

## Current enforcement status

**Gated**, as of `473205a7457b208455f188847bfb27b01aa83cac`. The obligation is enforced
in production code (`check_channel_membership`, called unconditionally for non-skip-listed
channel-scoped kinds before any per-kind admin validator), and a real, non-stubbed test
asserts the specific rejection end to end -- but that test carries `#[ignore]` and requires
a live relay plus Postgres/Redis to execute, so it does not run unconditionally in CI. This
node was authored by reading the test's current source and confirming it is not
`todo!()`-stubbed or empty; the test was **not executed** as part of authoring this node
(no live relay was stood up for this task). "Gated" here means: the enforcement code path
is real and reachable, the test that proves it is real and not a stub, but the test's own
pass/fail state at HEAD was not observed by running it.

## Limits

**What this node's evidence establishes:** that `check_channel_membership` exists, runs
before per-kind admin validators for non-skip-listed channel-scoped kinds (including
`kind:9000`), and that a real (non-stubbed) test asserts its rejection behavior for one
such kind against one non-open channel.

**What it does not establish:**

- **Whether the test currently passes.** It was read, not executed, at the recorded
  revision -- see *Current enforcement status*.
- **Coverage of every kind the gate applies to.** The test exercises `kind:9000` only.
  The same `check_channel_membership` call site gates every other non-skip-listed
  channel-scoped kind (ordinary messages, reactions, threads, and more), and none of
  those kinds has its own dedicated non-member-rejection test found at this revision.
- **The skip-listed kinds' own authorization.** `KIND_NIP29_JOIN_REQUEST`,
  `KIND_NIP29_CREATE_GROUP`, `KIND_STREAM_MESSAGE_EDIT`, `KIND_NIP29_EDIT_METADATA`,
  `KIND_NIP29_DELETE_EVENT` and `KIND_NIP29_DELETE_GROUP` bypass this gate by design and
  are authorized by their own per-kind validators, which this node does not document or
  test.
- **Role-based authorization once already a member.** `validate_admin_event`'s
  `kind:9000` branch additionally rejects a member without an elevated role who tries to
  grant an elevated role to someone else (`"only owners/admins may grant elevated
  roles"`), verified by a separate test,
  `e2e_relay.rs::test_private_channel_member_cannot_grant_admin`. That is a distinct
  obligation -- membership is a precondition of reaching it, not the thing it tests --
  and this node does not claim it as covered. It is a candidate for its own
  test-contract node.
- **`validate_admin_event`'s own `actor_role.is_none()` check** (line-adjacent to the
  elevated-role check, also in the `kind:9000` branch) is, per this node's one INFERENCE
  above, not the code path `test_private_channel_non_member_cannot_invite` actually
  reaches for a true non-member on a private channel, because `check_channel_membership`
  already rejects that request first. Whether any request shape reaches
  `validate_admin_event`'s own check in practice was not established here.
- **Moderation, operator and query authorization.** A targeted search for test names
  matching those surfaces in `crates/buzz-test-client/tests/` and
  `crates/buzz-relay/src/api/operator.rs` found no moderation- or operator-authorization
  rejection test, and found a query-authorization-named test only in `e2e_persona.rs`,
  which this node did not open. This is a negative search result at this revision, not a
  proof that no such test exists anywhere in the repository.
- **The media/Blossom scope check** (`crates/buzz-media/src/auth.rs`'s
  `MediaError::InsufficientScope`/`ServerMismatch` rejections) is a separate
  authorization mechanism, already the subject of the existing
  `capabilities-media-attachment-authorization` capability node, and is out of scope
  here.

## Scope and omissions

**This node covers** the generic channel-membership gate (`check_channel_membership`)
that runs ahead of per-kind admin validators for channel-scoped persistent events, the
one obligation it enforces, and the one end-to-end test that proves rejection for a
non-member on a private channel via a `kind:9000` event.

**It does not cover, filed here as gaps rather than folded in:**

| Not covered here | Where it belongs |
|---|---|
| Role-based authorization once already a channel member (elevated-role grants) | A separate test-contract node; candidate test is `e2e_relay.rs::test_private_channel_member_cannot_grant_admin` |
| The six skip-listed kinds' own per-kind authorization | Their own validators (`validate_edit_ownership` and others named in `ingest.rs`'s skip-list comment), not documented by this node |
| Moderation authorization | `capabilities-moderation-moderation-authorization` (capability content; no rejection test was found paired with it at this revision) |
| Operator authorization | Not yet a corpus node at this revision; no rejection test was found for it in this search |
| Query/search authorization and re-authorization | `capabilities-search-result-reauthorization` (capability content; not evaluated for a paired rejection test by this node) |
| Media/Blossom auth-event scope checks | `capabilities-media-attachment-authorization` |
| Channel-membership *roster* mutations (join/leave/add/remove as a capability, not this gate) | `capabilities-channels-channel-membership`, which explicitly names this gate as a "related but distinct concern" it does not cover |

**Expected but not verified when this node was written:**

- **Whether `test_private_channel_non_member_cannot_invite` currently passes.** Not run;
  see *Current enforcement status*.
- **Whether any other test in the repository covers a non-`kind:9000` non-member
  rejection through this same gate.** Only a targeted grep for the literal rejection
  string and for kind:9000-shaped helper functions was performed; a broader search
  across `crates/buzz-test-client/tests/` and `crates/buzz-db`'s own test suites was not
  exhaustively done for this node.
- **Whether `validate_admin_event`'s `actor_role.is_none()` branch is reachable by any
  real request shape.** Flagged as an open question in *Limits*, not resolved here.
