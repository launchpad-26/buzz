---
id: verification-e2e-relay
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
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs contains 46 async test functions, every one of them annotated both #[tokio::test] and #[ignore]; there is no non-#[ignore] test in the file."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "The file's own module doc-comment (its first 19 lines) states these are end-to-end integration tests that require a running relay instance, are #[ignore]d by default 'so that cargo test does not fail in CI when the relay is not available', and gives the run command 'cargo test --test e2e_relay -- --ignored', with the relay target overridable via the RELAY_URL environment variable."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:1-19"
  - statement: "TESTING.md states in its Automated Tests section that 'just test-unit' and 'just test' do not run the E2E suites in buzz-test-client, that those suites are marked #[ignore] and require a running relay, and gives 'cargo test -p buzz-test-client -- --ignored' (after starting a relay per the rest of that document) as how to run them."
    entry_class: FACT
    evidence:
      - "TESTING.md:10-17"
  - statement: "scripts/run-tests.sh, which is what the Justfile's `test` recipe invokes, contains no reference anywhere in its source to e2e_relay or to buzz-test-client; its unit-test and integration-test steps run only buzz-core, buzz-auth, buzz-voice, buzz-cli and buzz-db (plus other workspace crates' own #[cfg(test)] and #[ignore]d-but-selected suites), never the e2e_relay binary."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh"
      - "Justfile:312-313"
  - statement: "CI's 'Relay E2E' job (relay-e2e) in .github/workflows/ci.yml starts a real buzz-relay process built from this source tree, backed by Postgres, Redis and MinIO started via docker compose in scripts/start-relay-for-tests.sh, then runs exactly two cargo test invocations against crates/buzz-test-client/tests/e2e_relay.rs: `cargo test -p buzz-test-client --test e2e_relay invite -- --ignored --nocapture` and `cargo test -p buzz-test-client --test e2e_relay nip43_membership_snapshots_are_rejected -- --ignored --nocapture`; no other CI workflow in .github/workflows/ invokes e2e_relay or buzz-test-client at all (.github/workflows/mesh-lifecycle.yml only lists crates/buzz-test-client/** as a path trigger for an unrelated mesh smoke test, and never runs this binary)."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:865-897"
      - "scripts/start-relay-for-tests.sh:62-84"
      - ".github/workflows/mesh-lifecycle.yml:11-36"
  - statement: "Running `cargo test -p buzz-test-client --test e2e_relay invite -- --ignored --list` against this file at the recorded revision lists exactly seven matching tests: test_invite_claim_rejects_invalid_code, test_invite_code_minted_for_one_host_fails_on_another, test_invite_mint_and_claim_admits_new_pubkey, test_invite_mint_requires_owner_or_admin, test_private_channel_admin_can_invite, test_private_channel_any_member_can_invite and test_private_channel_non_member_cannot_invite; combined with the second CI command's exact-name match on test_client_submitted_nip43_membership_snapshots_are_rejected, CI's relay-e2e job selects 8 of this file's 46 #[ignore]d test functions on every push and on every pull request whose changed paths satisfy the `changes` job's rust condition, and the remaining 38 are not selected by any CI job."
    entry_class: FACT
    evidence:
      - "cargo_test(-p buzz-test-client, --test e2e_relay, invite, --, --ignored, --list) -> 7 tests, 0 benchmarks: test_invite_claim_rejects_invalid_code, test_invite_code_minted_for_one_host_fails_on_another, test_invite_mint_and_claim_admits_new_pubkey, test_invite_mint_requires_owner_or_admin, test_private_channel_admin_can_invite, test_private_channel_any_member_can_invite, test_private_channel_non_member_cannot_invite"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - ".github/workflows/ci.yml:892-894"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree contains no verification/-prefixed nodes at all, and in particular carries no node with id verification-contracts-websocket or verification-contracts-http, so this node declares no relationships to either."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> no launchpad/docs/corpus/verification/** path present"
  - statement: "Each test function's own name and, where present, its immediately preceding /// module doc-comment describe what that test exercises; every doc-comment quoted in this node's Verifying test(s) section was read directly from crates/buzz-test-client/tests/e2e_relay.rs at the recorded revision, not paraphrased from memory or inferred from the name alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "architecture-containers-relay, the corpus's existing container node for buzz-relay, already cites crates/buzz-test-client/tests/e2e_relay.rs and sibling e2e suites as the relay's verification, under a heading that names TESTING.md as the fuller guide it deliberately does not duplicate — this node is the more detailed treatment that node's Implementation/verification section pointed at without a node to name."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "architecture-containers-relay (id confirmed in its own front matter) is loadable from origin/launchpad's corpus tree at the recorded revision, so a references edge from this node to it resolves on the merge target, not merely in this worktree."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> launchpad/docs/corpus/architecture/containers/relay.md present"
      - "launchpad/docs/corpus/architecture/containers/relay.md"
relationships:
  - type: references
    target: architecture-containers-relay
---

# Relay end-to-end protocol suite — test contract

## Purpose and boundary

This node documents `crates/buzz-test-client/tests/e2e_relay.rs`: the full-stack
end-to-end test suite that drives a real `buzz-relay` process, built from this
source tree, over a real WebSocket and HTTP connection, exactly as a live client
would. It covers **the suite as a whole** — connection and NIP-42 authentication,
event publish/subscribe/filter/close semantics, protocol-level limits (frame size,
subscription count), ephemeral-event handling, NIP-05/kind:0 sync, NIP-29 group
membership and role changes, invite mint/claim, private-channel invite
authorization, membership-change notifications, and live thread-summary fan-out —
rather than one narrow obligation. That is a deliberate departure from this
corpus's usual one-obligation-per-test-contract-node shape (see
`launchpad/docs/corpus/templates/test-contract.md`'s *Required sections*, which
this node otherwise follows): this file is the repository's one canonical
end-to-end exercise of the relay's WebSocket **and** HTTP surface together against
a live process, and splitting each of its 46 test functions into its own node
would fragment one integration suite that its own authors already organize,
name, and run as a single unit into forty-six thin nodes with no added
information. Any future node documenting a narrower, single testable obligation
against this same suite (for example, one drawn from
`docs/multi-tenant-conformance.md`) is out of scope here and belongs in its own
node, not folded into this one.

This node does **not** cover: the narrower websocket-protocol-only or
HTTP-bridge-only obligations a future `verification-contracts-websocket` or
`verification-contracts-http` node might state as a single testable sentence each
(neither exists in the corpus at the recorded revision — see *Relationships*
below); the relay's other e2e suites (`e2e_media*.rs`, `e2e_nostr_interop.rs`,
`e2e_persona.rs`, `e2e_team_catalog.rs`, `e2e_project.rs`, `e2e_event_reminder.rs`
and others under the same directory), each a candidate for its own future node;
or any Postgres/Redis-only integration test that never opens a live relay
connection.

## Obligation

> A `buzz-relay` process, built from this repository's own source tree and
> connected to real Postgres, Redis and (for the invite/media paths) object
> storage, correctly implements the WebSocket relay protocol and HTTP bridge
> surface exercised by `crates/buzz-test-client/tests/e2e_relay.rs` — connection
> and NIP-42 authentication, event accept/reject and fan-out, subscription
> filtering and lifecycle, protocol-level limits, ephemeral-event and NIP-05/kind:0
> handling, NIP-29 group membership and role-change authorization, invite
> mint/claim, private-channel invite authorization, membership-change
> notifications, and live thread-summary recount fan-out — when driven by a real
> client built from the same source tree (`buzz-test-client`) rather than by a
> unit-level mock of any relay-internal component.

This is one obligation about *end-to-end behavior against a live process*,
distinguished from unit- and integration-level tests elsewhere in the workspace
(for example `buzz-relay`'s own `#[cfg(test)]` modules, several of which are
`#[ignore]`d and Postgres-backed but call relay handler functions directly rather
than opening a socket) precisely because it is the one place this repository
proves the protocol as a real client sees it.

## Verifying test(s)

All 46 functions live in `crates/buzz-test-client/tests/e2e_relay.rs`, each
`#[tokio::test]` and `#[ignore]`. Grouped by what each exercises, per its own name
and — where the file carries one — its own preceding `///` doc-comment, read
directly from the file at the recorded revision:

**Connection, authentication, and identity**
- `test_connect_and_authenticate` — a client can connect and complete NIP-42 auth.
- `test_unauthenticated_rejected` — an unauthenticated client's event submission is
  rejected or the connection is closed.
- `test_pubkey_mismatch_rejected` — an event signed by a key other than the
  authenticated pubkey is rejected.
- `test_auth_event_kind_rejected` — a kind-22242 AUTH event submitted via EVENT
  (rather than the AUTH message) is rejected.
- `test_nip11_relay_info` — `GET /info` returns NIP-11 relay info including
  `limitation.max_subscriptions: 1024` and `limitation.auth_required: true`.
- `test_kind0_nip05_sync` — a valid `nip05` handle in kind:0 content syncs to the
  profile and resolves via `/.well-known/nostr.json`; an off-domain `nip05` does
  not sync and clears any previously-resolved handle.

**Publish, subscribe, and protocol-level limits**
- `test_send_event_and_receive_via_subscription` — a subscribed client receives an
  event published by a second client, live.
- `test_large_event_frame_below_configured_limit_is_accepted` — an event whose
  frame exceeds the historical 64 KiB cap but stays under the current default cap
  is accepted, and the connection remains usable afterward.
- `test_subscription_filters_by_kind` — a subscription filtered by kind receives
  only matching events.
- `test_close_subscription_stops_delivery` — closing a subscription stops further
  delivery on it.
- `test_multiple_concurrent_clients` — a broadcast event reaches every one of
  several concurrently connected, concurrently subscribed clients.
- `test_stored_events_returned_before_eose` — historical events are delivered
  before EOSE.
- `test_valid_channel_survives_malformed_or_empty_h_sibling` — an `#h` OR-sibling
  that cannot match (malformed UUID, or empty) does not cancel a valid sibling
  filter's historical and live delivery.
- `test_ephemeral_event_not_stored` — a kind 20000–29999 ephemeral event is
  accepted but not persisted (absent from a subsequent historical query).
- `test_subscription_limit_enforced` — the (limit+1)th concurrent `REQ` on one
  connection is `CLOSED`, enforcing the 1024 cap NIP-11 advertises.
- `test_eose_sent_for_empty_subscription` — a subscription matching no stored
  events still receives EOSE.

**Invite mint/claim (HTTP bridge)**
- `test_invite_mint_and_claim_admits_new_pubkey` — an owner mints an invite code,
  a new pubkey claims it and joins as `member`; re-claiming reports
  `already_member`.
- `test_invite_claim_rejects_invalid_code` — claiming a malformed/invalid code is
  rejected (`403`, `invite_invalid`).
- `test_invite_mint_requires_owner_or_admin` — a plain member or an outsider
  cannot mint an invite (`403`).
- `test_invite_code_minted_for_one_host_fails_on_another` — an invite minted for
  one host's community fails to claim against a different host.

**NIP-29 group membership and role changes**
- `test_nip29_put_user_default_policy_allows` — a kind:9000 `PUT_USER` under the
  default add-policy is accepted.
- `test_nip29_put_user_nobody_blocks` — a target with `channel_add_policy:
  "nobody"` blocks a third-party `PUT_USER` (`policy:nobody` rejection).
- `test_nip29_put_user_self_add_bypasses_policy` — self-add bypasses a `"nobody"`
  policy.
- `test_nip29_put_user_owner_only_blocks` — an `"owner_only"` policy blocks
  third-party `PUT_USER` (`policy:owner_only` rejection).
- `test_nip29_standard_client_flow` — the full standard client flow: discover
  kind:39000/39001/39002, subscribe, send a kind:9 message, react (kind:7),
  delete (kind:5), and confirm a kind:9 without an `h` tag is rejected.
- `test_unarchive_emits_member_added_notification` — archiving then unarchiving a
  channel (kind:9002) emits a kind:44100 `member_added` notification on the
  always-live global membership feed.
- `test_nip29_put_user_cannot_demote_owner` — a security regression test: an
  unprivileged non-member cannot demote an open channel's owner to `member` via a
  single kind:9000.
- `test_nip29_owner_demotion_recovery_paths` — follow-on to the above: after a
  (hypothetical) demotion, neither self-promotion to owner nor the ex-owner
  restoring its own role succeeds.
- `test_nip29_put_user_without_role_tag_preserves_role` — a kind:9000 with no
  `role` tag does not silently demote the sender (asserts resulting state, not
  just `accepted`, and deliberately seeds two owners so the last-owner guard
  cannot be the thing that passes the test).
- `test_nip29_relay_rejects_role_change_by_unprivileged_actor` — isolates the
  relay-layer `validate_admin_event` guard (not the DB guard) for "only
  owners/admins may change an active member's role," asserting `accepted: false`
  specifically.
- `test_nip29_relay_rejects_last_owner_self_demotion` — isolates the relay-layer
  last-owner guard, asserting `accepted: false` when the sole owner tries to
  demote itself.

**Membership-change notifications (kind:44100 / 44101)**
- `test_membership_notification_kind_rejected` — a client-submitted kind:44100 is
  rejected; only the relay's own key may sign these.
- `test_membership_notification_emitted_on_add` — adding a member via REST emits a
  kind:44100 to a subscriber filtering on that member's own `#p`.
- `test_membership_notification_emitted_on_remove` — removing a member via REST
  emits a kind:44101 to the same subscriber.
- `test_membership_notification_requires_p_filter` — subscribing to kind:44100/
  44101 with no `#p` filter is rejected with `CLOSED` ("restricted").
- `test_membership_notification_wildcard_filter_rejected` — an empty (wildcard)
  filter that could match these kinds is rejected with `CLOSED`.
- `test_membership_notification_requires_own_p_filter` — a `#p` filter naming
  someone else's pubkey is rejected with `CLOSED`.
- `test_membership_notification_multi_p_rejected` — a `#p` filter naming both the
  caller's own pubkey and a victim's pubkey is rejected with `CLOSED`.
- `test_membership_notification_mixed_filter_rejected` — a second, globally-scoped
  filter alongside a properly-scoped one is rejected with `CLOSED`, closing a
  bypass route.

**Private-channel invite authorization**
- `test_private_channel_any_member_can_invite` — any active member can add an
  ordinary role.
- `test_private_channel_admin_can_invite` — an admin (not only the owner) can
  invite.
- `test_private_channel_non_member_cannot_invite` — a non-member cannot invite.
- `test_private_channel_member_cannot_grant_admin` — a regular member cannot grant
  an elevated (owner/admin) role.

**Live thread-summary fan-out**
- `test_reply_ingest_pushes_live_thread_summary` — every thread mutation (reply
  added or its deletion) pushes a fresh relay-signed kind:39005 recount to
  channel subscribers.
- `test_workflow_reply_in_thread_pushes_live_thread_summary` — a workflow-posted
  threaded reply (`reply_in_thread: true`) pushes the same kind:39005 overlay the
  human-ingest path does, and the `trigger_is_reply == false` filter fires
  correctly on the top-level message.

**Cross-cutting relay-only invariant**
- `test_client_submitted_nip43_membership_snapshots_are_rejected` — a
  client-submitted kind:13534 membership snapshot is rejected over both the
  WebSocket (`restricted: relay-only kind`) and the HTTP bridge (`400`, same
  message) — proving the same actor's ordinary event still succeeds, so the
  rejection is specifically this relay-only-kind invariant.

## How to run it

Requires a running relay backed by Postgres and Redis (invite/notification and
storage paths additionally touch Postgres; media-adjacent object storage is not
required by this file). Locally, per `TESTING.md`:

```bash
. ./bin/activate-hermit
just bootstrap && just setup                 # Docker Postgres/Redis, migrations
cargo build --release -p buzz-relay
export PATH="$PWD/target/release:$PATH"
buzz-relay                                    # separate terminal, serves ws://localhost:3000

# in another terminal:
cargo test -p buzz-test-client --test e2e_relay -- --ignored --nocapture
# or a single test:
cargo test -p buzz-test-client --test e2e_relay test_nip29_standard_client_flow -- --ignored --nocapture
```

`RELAY_URL` overrides the target (default `ws://localhost:3000`); `DATABASE_URL`
defaults to `postgres://buzz:buzz_dev@localhost:5432/buzz` if unset;
`BUZZ_TEST_OWNER_PRIVATE_KEY` optionally pins the "owner" identity the invite
tests use, falling back to a freshly generated key. `just test` and `just
test-unit` do **not** run this file — see the enforcement section below.

CI runs a narrower slice automatically; see *Current enforcement status*.

## Current enforcement status

**Gated.** Every one of the 46 test functions carries `#[ignore]`, so none runs
under a bare `cargo test` anywhere, including in `just test`/`just test-unit`
(confirmed: `scripts/run-tests.sh`, what `just test` invokes, contains no
reference to `e2e_relay` or `buzz-test-client` at all).

Within that gated set, enforcement splits further:

- **CI-enforced today (verified, on every push and qualifying pull request):**
  8 of the 46 functions. `.github/workflows/ci.yml`'s `relay-e2e` job starts a
  real `buzz-relay` binary against Docker Postgres/Redis/MinIO
  (`scripts/start-relay-for-tests.sh`) and runs exactly
  `cargo test -p buzz-test-client --test e2e_relay invite -- --ignored --nocapture`
  and
  `cargo test -p buzz-test-client --test e2e_relay nip43_membership_snapshots_are_rejected -- --ignored --nocapture`.
  Running the first command's filter with `--list` against this file confirms it
  matches exactly seven tests: `test_invite_mint_and_claim_admits_new_pubkey`,
  `test_invite_claim_rejects_invalid_code`,
  `test_invite_mint_requires_owner_or_admin`,
  `test_invite_code_minted_for_one_host_fails_on_another`,
  `test_private_channel_any_member_can_invite`,
  `test_private_channel_admin_can_invite`, and
  `test_private_channel_non_member_cannot_invite` (each ends `..._invite`); the
  second command matches exactly
  `test_client_submitted_nip43_membership_snapshots_are_rejected`.
- **Locally runnable, CI-selected nowhere (gated, manual-only):** the remaining
  38 functions — everything in the *Connection/auth*, *Publish/subscribe/limits*,
  *NIP-29 membership and role changes* (all eleven), *membership-change
  notifications* (all eight), one private-channel invite test
  (`test_private_channel_member_cannot_grant_admin`, which does not contain the
  substring "invite"), and *live thread-summary fan-out* groups above. No
  workflow file under `.github/workflows/` invokes `e2e_relay` or
  `buzz-test-client` beyond the two `relay-e2e` lines quoted; nothing else
  selects them. They exist, are believed to pass (per the suite's own purpose and
  the presence of the security-regression tests among them), but that belief is
  not backed by any automated, unconditional CI run at the recorded revision —
  running them is a manual step a developer or agent performs per *How to run
  it*.

**No test in this file is unconditionally CI-enforced without the `--ignored`
gate**, and none runs at all outside the dedicated `relay-e2e` job.

## Limits

- **Proves behavior against one relay build, one run, one moment.** A green run
  of the 8 CI-selected tests establishes that this specific `buzz-relay` binary,
  at this commit, behaved correctly for those specific scenarios on that CI
  attempt. It does not establish anything about the other 38 functions unless a
  human or agent actually runs them per *How to run it* and reads the result.
- **The 38 non-CI-selected functions are not a proof of absence of a defect** —
  only their presence in the file, their `#[ignore]` gate, and (for the ones with
  security-motivated doc-comments — the three `test_nip29_relay_rejects_*` and
  `test_nip29_owner_demotion_recovery_paths`/`test_nip29_put_user_without_role_tag_preserves_role`
  pair) the explicit statement of what regression each guards against.
- **Positive assertions dominate; several tests intentionally accept multiple
  outcomes as passing** — for example `test_unauthenticated_rejected` accepts
  either an explicit `accepted: false`, a closed connection, or a timeout as all
  "acceptable," which is weaker than asserting one specific rejection mode.
- **Concurrency and scale are exercised narrowly.** `test_multiple_concurrent_clients`
  uses three clients; `test_subscription_limit_enforced` drives exactly to the
  documented 1024-subscription cap and one over. Neither claims to characterize
  behavior at larger scale or under sustained load.
- **The suite proves protocol behavior, not data-layer correctness beyond what
  each assertion reads back.** Where a test confirms state via a follow-up query
  (e.g. `test_kind0_nip05_sync`, `test_stored_events_returned_before_eose`), it
  proves that specific read-after-write path, not the underlying storage
  invariant in general — narrower storage/schema invariants are `buzz-db`'s own
  test suite's subject, not this node's.
- **Some CI-run tests rely on incidental substring matches, not a maintained
  test-tag scheme.** `test_private_channel_*_invite` tests run under CI's
  `relay-e2e` job because their names happen to contain "invite," not because
  someone declared them CI-required (confirmed by actually running the filter
  with `--list` — see the evidence ledger); a future rename that drops the
  substring would silently move a test from *verified* to *gated* with no CI
  signal that anything changed.

## Relationships

**Checked, not assumed absent**, per `launchpad/docs/corpus/AGENTS.md`'s warning
that "nothing exists to point at" stops being true the moment a sibling node
merges. At the recorded revision, `origin/launchpad`'s corpus tree carries no
`verification/`-prefixed node at all — `verification-contracts-websocket` and
`verification-contracts-http` do not exist — so no edge is declared to either;
that is the moment to revisit, not now. `architecture-containers-relay` does
exist on `origin/launchpad`, already names this suite as the relay container's
verification without a node to point at, and this node declares a `references`
edge to it accordingly.

## Scope and omissions

**Covered:** every test function in `crates/buzz-test-client/tests/e2e_relay.rs`
at the recorded revision, grouped by what it exercises, how to run the suite
(gated and ungated), and an honest per-subset enforcement status distinguishing
the 8 functions CI actually selects from the 38 it does not.

**Not covered, and left as gaps:**

- **The relay's other e2e suites** (`e2e_media.rs`, `e2e_media_extended.rs`,
  `e2e_media_video.rs`, `e2e_nostr_interop.rs`, `e2e_persona.rs`,
  `e2e_team_catalog.rs`, `e2e_project.rs`, `e2e_event_reminder.rs`, and any
  others under `crates/buzz-test-client/tests/`) — each a candidate for its own
  future `verification/e2e/*` node, not folded in here per the corpus's
  one-node-one-idea rule.
- **A narrower single-obligation contract node for the WebSocket protocol alone,
  or the HTTP bridge alone** (`verification-contracts-websocket` /
  `verification-contracts-http`) — neither exists in the corpus at the recorded
  revision (confirmed against `origin/launchpad`'s tree, not assumed), so no
  relationship is declared to either; if and when either lands, this node's
  Purpose and boundary section should be revisited to add a `references` edge and
  narrow any overlap in prose.
- **`buzz-relay`'s own unit- and integration-level `#[cfg(test)]` modules** (many
  `#[ignore]`d and Postgres-backed, several selected individually by name in
  `.github/workflows/ci.yml`'s Backend Integration job) — those call relay
  handler functions directly rather than driving a live client over a socket, so
  they are a different verification layer, not part of this suite.
- **Whether every one of the 38 non-CI-selected functions currently passes** —
  not established here. This node was authored by reading the suite's source and
  the CI configuration, not by executing the 38 ungated tests against a live
  relay in this session; doing so is the natural next step for whoever picks up
  gating more of this suite into CI.
- **Why only these two positional filters (`invite`,
  `nip43_membership_snapshots_are_rejected`) were chosen for CI**, versus the
  other 38 — no design document or issue explaining that selection was found or
  cited here; it is recorded as a fact about the current state, not justified.
