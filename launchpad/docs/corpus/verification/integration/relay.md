---
id: verification-integration-relay
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "may_set_workspace_profile, in crates/buzz-relay/src/handlers/relay_admin.rs, implements a 'steward-wins' rule for who may set the relay's workspace profile (kind:9033, the community icon): on a closed relay (membership_enforced), or on an open relay where any admin/owner row already exists, only sender_role == \"admin\" or \"owner\" is admitted; only a genuinely rosterless open relay admits any authenticated sender."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:97-124"
  - statement: "handle_relay_admin_event's kind:9033 branch (crates/buzz-relay/src/handlers/relay_admin.rs:259-305) is the production call site for this rule: it looks up community_has_steward via state.db.has_admin_or_owner when the relay is open, calls may_set_workspace_profile, returns Err(\"actor not authorized: must be admin or owner\") when it is false, and otherwise persists the icon via state.db.set_community_icon."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:259-305"
  - statement: "The kind:9033 branch's own comment states it 'writes no audit row and publishes no announcement event (unlike 9030/9031)', unlike the other relay-admin commands in the same file."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:280-288"
  - statement: "Two #[tokio::test] functions in crates/buzz-relay/src/handlers/relay_admin.rs's own #[cfg(test)] mod tests — open_relay_9033_admits_roleless_only_until_a_steward_exists (lines 787-839) and closed_relay_9033_still_requires_admin_or_owner (lines 846-898) — are each annotated #[ignore = \"requires Postgres\"] and call handle_relay_admin_event (via a submit_9033 helper, lines 760-771) directly, in-process, against a real AppState built by workspace_profile_test_state (lines 701-756)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:787-839"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:846-898"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:760-771"
  - statement: "workspace_profile_test_state builds its AppState from a real sqlx::PgPool connected to BUZZ_TEST_DATABASE_URL, falling back to DATABASE_URL, falling back to the hardcoded constant TEST_DB_URL = \"postgres://buzz:buzz_dev@localhost:5432/buzz\" (line 699), and both test functions read/write real Postgres rows through it (db.ensure_configured_community, db.add_relay_member, db.get_community_icon)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:699-756"
  - statement: "workspace_profile_test_state hardcodes config.redis_url to \"redis://127.0.0.1:1\", an address the AppState it builds never actually needs to reach for this obligation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:713"
  - statement: "buzz_pubsub::PubSubManager::new/with_config never opens a network connection at construction — it only allocates in-process broadcast channels and stores the pool/URL for later use; the actual Redis connection loop (run_subscriber) is a separate method that workspace_profile_test_state never calls, so the two ignored 9033 tests never exercise a real Redis connection despite AppState nominally holding one."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs:115-161"
  - statement: "open_relay_9033_admits_roleless_only_until_a_steward_exists and closed_relay_9033_still_requires_admin_or_owner together are the right and sufficient verifying tests for the obligation as stated below, because between them they exercise all three admission outcomes the obligation describes — rosterless-open admits any authenticated sender, stewarded-open admits only admin/owner, closed admits only admin/owner for both a plain member and a roleless sender — and each assertion additionally checks that a refused write leaves the previously stored icon unchanged."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:787-839"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:846-898"
    confidence: 0.8
  - statement: "crates/buzz-relay/src/handlers/relay_admin.rs's own tests live in a #[cfg(test)] mod tests block embedded in that same production source file (lines 486-899), the same pattern crates/buzz-relay/src/handlers/identity_archive.rs and crates/buzz-relay/src/api/admin/mod.rs also use for their own Postgres-backed tests, rather than a standalone file under a separate crates/buzz-relay/tests/ integration-test directory."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:486-899"
      - "crates/buzz-relay/src/handlers/identity_archive.rs:438-530"
      - "crates/buzz-relay/src/api/admin/mod.rs:2370"
  - statement: ".github/workflows/ci.yml's backend-integration job (named 'Backend Integration (relay e2e)') runs a step called 'Workspace profile (kind:9033) gate tests' that executes `cargo nextest run -E 'package(buzz-relay) and test(/handlers::relay_admin::tests/)' --run-ignored ignored-only` with DATABASE_URL pointed at a dockerized Postgres started earlier in the same job, and its own comment states this is 'Call-site integration for the 9033 authorization gate: open relay rosterless/steward transitions and the closed-relay admin/owner rule, against real Postgres. #[ignore]d in the default suite, selected explicitly here.'"
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:751-762"
  - statement: "The backend-integration job runs on 'if: github.event_name == 'push' || needs.changes.outputs.rust == 'true'', i.e. on every push and on every pull request that the changes job detects touches a Rust-relevant path — not only on manual trigger."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:604-609"
  - statement: "Although the backend-integration job's earlier 'Start relay' step (lines 715-742) boots a live ./target/ci/buzz-relay process before the Workspace profile gate tests step runs, that step's own env block sets only DATABASE_URL, not RELAY_URL — consistent with the test code calling handle_relay_admin_event in-process rather than issuing any request to the already-running relay binary. The same job's later 'NIP-ER reminder e2e' step, by contrast, does set RELAY_URL and runs a buzz-test-client binary (binary(e2e_event_reminder)) against that live process."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:715-774"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs's own module doc-comment states these are 'End-to-end integration tests for the Buzz relay' that 'require a running relay instance', are '#[ignore]' by default, are run via `cargo test --test e2e_relay -- --ignored`, and may target a different relay via the RELAY_URL environment variable."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:1-16"
  - statement: "A separate CI job, relay-e2e (named 'Relay E2E'), downloads the same relay binary the backend-integration job builds, starts it as a live process via scripts/start-relay-for-tests.sh, and runs buzz-test-client's e2e_persona/e2e_team_catalog/e2e_nostr_interop/e2e_project/e2e_relay/e2e_media* suites against it with `cargo test ... -- --ignored --nocapture` and RELAY_URL set — the full black-box, real-network-client-against-a-live-relay suite."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:865-897"
  - statement: "scripts/run-tests.sh's run_integration_tests function (the body of `just test`'s and `just test-integration`'s local invocation) runs `cargo test -p buzz-db -- --nocapture`, an auth/workspace conditional, and `cargo test --test '*' -- --nocapture`, none of which passes --ignored or --include-ignored, and never names buzz-relay at all."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh:127-145"
  - statement: "scripts/run-tests.sh's own comment on its buzz-db unit-tests step states explicitly that 'The Postgres-backed buzz-db tests are #[ignore]d; nothing here (or in integration mode below, which runs `cargo test -p buzz-db` without --ignored) runs them' — the script's own authors documenting that neither its unit nor its integration mode runs the #[ignore]d Postgres-backed tests."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh:92-98"
  - statement: "When no .env file is present, scripts/run-tests.sh defaults DATABASE_URL to postgres://buzz:buzz_dev@localhost:5432/buzz, the same credentials workspace_profile_test_state's own TEST_DB_URL constant hardcodes, and the script's own comment says this matches docker-compose.yml's defaults."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh:40-48"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries no path under a verification/ prefix at all, so no verification-e2e-relay node (the id this node's own task, #1378, names as covering #1367's full-stack e2e relay protocol suite) exists yet to declare a relationship toward."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> AGENTS.md, README.md, agents/**, architecture/**, capabilities/**, development/**, layers/**, standards/**, templates/**, schema/** (excluded); no verification/** path present"
  - statement: "Issue #1378's own task description frames this node's obligation as 'integration'-level relay testing (Postgres+Redis-backed, `just test`), distinct from #1367's full-stack e2e relay protocol suite (e2e_relay.rs), and names verification-e2e-relay as the id #1367 would produce."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1378 task description"
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-principles-relay-orchestrates-subsystems
---

# Workspace-profile (kind:9033) authorization gate — relay integration test contract

## Purpose and boundary

This node documents **one** relay-integration obligation: that setting the relay's
workspace profile (kind:9033, the community icon) is gated by the "steward-wins" rule
`may_set_workspace_profile` encodes, and that the gate is correctly wired into the
production entry point `handle_relay_admin_event`, not only correct as an isolated pure
function. It covers this obligation only.

**Integration, not end-to-end.** The verifying tests below build a real `AppState` —
wiring `buzz-db` against a real Postgres database exactly as the production binary does
— and call `handle_relay_admin_event` as a plain Rust function call, in-process, with no
relay process listening on a socket and no NIP-01/WebSocket or HTTP client in the loop.
That is the boundary this node draws explicitly: `crates/buzz-test-client/tests/e2e_relay.rs`
and its sibling suites are the opposite shape — a real client connecting over the network
to a separately running `./target/ci/buzz-relay` binary — and are `#[ignore]`d by default,
run via `cargo test --test e2e_relay -- --ignored` against `RELAY_URL`. Those suites are
the intended subject of a future `verification-e2e-relay` node (issue #1367's own naming);
at this node's recorded revision no node under a `verification/` prefix exists anywhere in
`origin/launchpad`'s corpus tree, so no `relationships` edge to it is declared — see *Scope
and omissions*.

## Obligation

> Setting the relay's workspace profile (kind:9033) is admitted for a plain authenticated
> sender only on a genuinely rosterless open relay (`require_relay_membership == false`
> and no `admin`/`owner` row yet exists for the community); the moment either the relay is
> closed (`require_relay_membership == true`) or any steward already exists on an open
> relay, only a sender whose role is `admin` or `owner` is admitted, and a refused attempt
> must not change the previously stored icon.

## Verifying test(s)

- `crates/buzz-relay/src/handlers/relay_admin.rs` —
  `handlers::relay_admin::tests::open_relay_9033_admits_roleless_only_until_a_steward_exists`
  (lines 787-839) — covers the open-relay half: a rosterless open community admits a
  roleless sender's icon write; once an `owner` row is seeded, the same roleless sender is
  refused and the previously stored icon is unchanged; the steward can still write.
- `crates/buzz-relay/src/handlers/relay_admin.rs` —
  `handlers::relay_admin::tests::closed_relay_9033_still_requires_admin_or_owner`
  (lines 846-898) — covers the closed-relay half: both a roleless sender and a plain
  `member`-role sender are refused (icon stays unset), while an `admin`-role sender
  succeeds.

Both are `#[tokio::test]` functions annotated `#[ignore = "requires Postgres"]`, and both
drive `handle_relay_admin_event` through a shared `submit_9033` helper (lines 760-771)
against an `AppState` built by `workspace_profile_test_state` (lines 701-756), which opens
a real `sqlx::PgPool` and performs real inserts (`add_relay_member`) and reads
(`get_community_icon`) against it.

## How to run it

The obligation needs a reachable Postgres and nothing else (see *Limits* for why Redis is
not actually required here despite `AppState`'s general Postgres+Redis wiring):

```bash
docker compose up -d postgres   # or export DATABASE_URL / BUZZ_TEST_DATABASE_URL yourself
cargo nextest run -p buzz-relay \
  -E 'test(/handlers::relay_admin::tests::(open_relay_9033_admits_roleless_only_until_a_steward_exists|closed_relay_9033_still_requires_admin_or_owner)/)' \
  --run-ignored ignored-only
```

Without `cargo-nextest`, the plain-`cargo` equivalent:

```bash
DATABASE_URL=postgres://buzz:buzz_dev@localhost:5432/buzz \
  cargo test -p buzz-relay --lib \
  handlers::relay_admin::tests::open_relay_9033_admits_roleless_only_until_a_steward_exists \
  handlers::relay_admin::tests::closed_relay_9033_still_requires_admin_or_owner \
  -- --ignored --nocapture
```

**`just test` / `scripts/run-tests.sh` does not run this obligation.** `run_integration_tests`
never passes `--ignored`/`--include-ignored` and never names `buzz-relay` at all — its own
comment on the neighboring `buzz-db` unit-test step says as much for that crate, and
inspection confirms the same gap extends to `buzz-relay`. CI's own reproduction is the
`.github/workflows/ci.yml` `backend-integration` job's "Workspace profile (kind:9033) gate
tests" step, which uses the exact `nextest` selector shown above.

## Current enforcement status

**Gated**, as of `473205a7457b208455f188847bfb27b01aa83cac`. Both tests carry
`#[ignore = "requires Postgres"]`, so a bare `cargo test -p buzz-relay` (and `just test`,
per above) silently skips them — that is the named condition. They are explicitly
re-enabled and do run in CI's `backend-integration` job ("Backend Integration (relay
e2e)"), whose own comment names this exact obligation, via
`--run-ignored ignored-only` plus the selector above, against a real dockerized Postgres.
That job's trigger condition (`push`, or any pull request whose changed paths include
Rust) means the obligation is checked on effectively every relevant change despite the
`#[ignore]` annotation — but only through that job's specific invocation, never through a
developer's unqualified local `cargo test` or `just test`.

## Limits

**What these two tests prove.** That `may_set_workspace_profile`'s steward-wins rule is
wired correctly into the real production call site (`handle_relay_admin_event`), not only
correct in isolation as a pure function; that the community-has-steward lookup
(`has_admin_or_owner`) and the icon read/write (`get_community_icon` /
`set_community_icon`) genuinely round-trip through Postgres rather than being mocked; and
that a refused write is a true no-op on the stored icon.

**What they do not prove:**

- **Only kind:9033.** Kinds 9030–9032 (add member, remove member, and the other
  relay-admin commands `handle_relay_admin_event` also dispatches) are untouched by this
  obligation and would each need their own test-contract node.
- **Not the transport or admission path above this handler.** WebSocket/NIP-42
  authentication, and the ban gate `admits_relay_admin_command` wraps this handler with,
  are covered by separate non-ignored unit tests in the same file
  (e.g. `banned_actor_is_not_admitted_to_a_relay_admin_command`) and are out of this
  node's scope.
- **Not actually Redis-backed, despite the general framing of this integration surface.**
  `workspace_profile_test_state` points `config.redis_url` at `redis://127.0.0.1:1`, and
  `buzz_pubsub::PubSubManager::new`/`with_config` never opens a connection at
  construction — only the separate `run_subscriber` method does, and neither test spawns
  it. Kind:9033's own handler comment confirms it "publishes no announcement event"
  either. So this specific obligation is Postgres-only in practice; a genuinely
  Redis-exercising relay-integration obligation (e.g. a kind whose handler does fan out
  over pub/sub) is a gap this node does not cover.
- **No live relay process, no real client.** The test never opens a socket. It says
  nothing about how this same decision is reached and returned over a real NIP-01/HTTP
  request to a running relay — that is `verification-e2e-relay`'s territory (see *Scope
  and omissions*).

## Scope and omissions

**This node covers:** the boundary between relay-crate in-process integration testing and
`buzz-test-client`'s full black-box e2e relay-protocol suite; one worked obligation from
the integration surface — the kind:9033 workspace-profile authorization gate — its two
verifying tests, how to run them honestly (including that `just test` does not), and its
current enforcement status.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Where it would go |
|---|---|
| The many other Postgres/Redis-backed `#[ignore]`d tests CI's `backend-integration` job also selects under separately named steps — e.g. "Invite security tests" (`api::invites::tests`, `buzz-db relay_invite::tests`), "Admin API roster-audit / timeout / canonicalization security tests", "Admin API escalation-scoping tests", "NIP-MP coordinate deletion guard" (`buzz-db`), and `handlers::identity_archive.rs`'s archival-snapshot tests | Each is a separate obligation and, per this corpus's one-node-one-idea rule, belongs in its own future `verification/integration/` node rather than being folded in here |
| The "NIP-ER reminder e2e" step inside that same `backend-integration` job, which — unlike every other step in the job — sets `RELAY_URL` and runs a `buzz-test-client` binary against the job's own live relay process; it is e2e-shaped despite living inside the nominally "integration" job | Not reclassified or relocated by this node; noted here so a reader does not assume every step in that job matches this node's boundary |
| `buzz-test-client`'s full black-box e2e relay-protocol suite (`e2e_relay.rs` and siblings), and the separate `relay-e2e` CI job that runs it against a live relay | `verification-e2e-relay`, once issue #1367 produces it — no `relationships` edge is declared because, at this node's recorded revision, no node under a `verification/` prefix exists anywhere in `origin/launchpad`'s corpus tree to point at |
| Whether kinds 9030–9032's own admission rules hold under the same or a different pattern | A future test-contract node per kind/obligation |

**Expected but not verified when this node was written:**

- **The two verifying tests were not executed.** Their behavior is established by reading
  their source and the production code they call, and by their `#[ignore]` annotation and
  CI's own selection of them — not by a local test run against a live Postgres instance in
  this session.
- **Whether CI's `backend-integration` job's selector actually resolves to just these two
  tests and no others** was read from the job's `-E` filter string, not confirmed by
  running `cargo nextest list` against it.
