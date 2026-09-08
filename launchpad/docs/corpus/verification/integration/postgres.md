---
id: verification-integration-postgres
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
  - statement: "buzz-db's own module doc-comment describes it as \"buzz-db — Postgres event store for Buzz\", owning connection pooling, migrations, and every typed data-access module (events, channels, users, moderation, workflow, and more)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "At the recorded revision, crates/buzz-db/src contains 241 `#[ignore` test attributes, the overwhelming majority carrying the literal reason string \"requires Postgres\" (a handful spell out the specific Postgres invariant, e.g. \"requires Postgres — roster audit trail across grant/change/revoke\"), spread across runtime/tests.rs, runtime/migration.rs, runtime/observability.rs, runtime/replica_fence.rs, and every store/*.rs module that owns persistence logic."
    entry_class: FACT
    evidence:
      - "grep_count(pattern='#\\[ignore', path='crates/buzz-db/') -> 241 matches at commit 473205a7457b208455f188847bfb27b01aa83cac"
      - "crates/buzz-db/src/runtime/tests.rs:30"
      - "crates/buzz-db/src/store/event.rs:2356"
      - "crates/buzz-db/src/store/channel_members.rs:1466"
      - "crates/buzz-db/src/store/relay_operators.rs:345"
      - "crates/buzz-db/src/store/deletion.rs:3412"
  - statement: "A representative example, crates/buzz-db/src/runtime/tests.rs's setup_db() helper, connects via a PgPool built from the TEST_DATABASE_URL environment variable, falling back to the literal postgres://buzz:buzz_dev@localhost:5432/buzz -- the same credentials docker-compose.yml's postgres service (image postgres:17-alpine) exposes on 127.0.0.1:5432 -- and every test in that file that touches the database is annotated #[tokio::test] plus #[ignore = \"requires Postgres\"]."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/tests.rs:7-15"
      - "crates/buzz-db/src/runtime/tests.rs:29-31"
      - "docker-compose.yml:4-13"
  - statement: "Justfile's test-unit recipe runs `cargo nextest run -p buzz-db --lib` and its own comment states this deliberately runs only the crate's infra-free migrator/lint unit tests, because the Postgres-backed buzz-db tests are #[ignore]d; CI's \"Unit Tests\" job (unit-tests in .github/workflows/ci.yml) runs exactly `just test-unit`."
    entry_class: FACT
    evidence:
      - "Justfile:331-336"
      - ".github/workflows/ci.yml:125-142"
  - statement: "scripts/run-tests.sh's run_integration_tests() function runs `cargo test -p buzz-db -- --nocapture` for its \"buzz-db tests\" step, with no `--ignored` or `--include-ignored` flag, and the script's own comment states plainly that this integration-mode invocation does not run the #[ignore]d Postgres-backed tests either -- \"they need a separate isolated-DB gate\"."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh:93-100"
      - "scripts/run-tests.sh:125-133"
  - statement: "`just test` (Justfile's test recipe) invokes exactly `./scripts/run-tests.sh all`, which runs run_unit_tests() followed by run_integration_tests() -- so neither of `just test`'s two phases actually executes the #[ignore]d Postgres-backed buzz-db test suite."
    entry_class: FACT
    evidence:
      - "Justfile:311-313"
      - "scripts/run-tests.sh:143-146"
  - statement: "Root TESTING.md documents `just test` as running \"unit tests plus integration tests against Postgres and Redis (started automatically if not already running)\", without qualifying that the crate's own #[ignore]d Postgres-backed tests are excluded from that run."
    entry_class: FACT
    evidence:
      - "TESTING.md:10-11"
  - statement: "`just ci` -- this repository's own documented pre-PR gate (\"Run `just ci` before every PR\") -- expands to `check test-unit desktop-test desktop-build desktop-tauri-check desktop-tauri-test web-build mobile-test`, which does not include the `test` recipe at all, so `just ci` does not run buzz-db's Postgres-backed tests either directly or by way of `just test`."
    entry_class: FACT
    evidence:
      - "Justfile:307"
      - "CLAUDE.md"
  - statement: "Because `just test` (root TESTING.md's documented integration level) does not execute the crate's #[ignore]d Postgres-backed tests, and `just ci` does not run `just test` at all, no locally-documented command exercises buzz-db's Postgres-backed test suite end to end; running it requires an explicit `--ignored` (or nextest `--run-ignored`) invocation the repository's own onboarding docs do not name."
    entry_class: INFERENCE
    evidence:
      - "scripts/run-tests.sh:93-100"
      - "scripts/run-tests.sh:125-133"
      - "Justfile:307"
      - "Justfile:311-313"
      - "TESTING.md:10-11"
    confidence: 0.8
  - statement: "CI's backend-integration job (display name \"Backend Integration (relay e2e)\") is the only CI job observed to pass `--run-ignored ignored-only` against `package(buzz-db)` nextest filters; its steps select named test/module subsets rather than the crate's full ignored surface -- for example `-E 'package(buzz-db) and test(/tests::(parameterized_|concurrent_parameterized_)/)'` for replaceable-event persistence, and `-E 'package(buzz-db) and test(/observability::tests::(pool_acquire_records_success_timeout_and_error_with_wait_time|advisory_lock_records_success_contention_timeout_and_error)/)'` for pool/advisory-lock metrics."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:604-609"
      - ".github/workflows/ci.yml:690-702"
      - ".github/workflows/ci.yml:703-712"
  - statement: "backend-integration's remaining steps select further named buzz-db (and cross-crate buzz-relay) tests one filter expression at a time -- relay_invite::tests, coordinate_delete_spares_head_newer_than_the_deletion, an 8-test roster-audit block naming every relay_operators::tests function individually (run with --test-threads=1 because the sole-operator invariant tests share global roster state), and a moderation/escalation-scoping block -- each with a code comment naming why that specific test needs a live Postgres and is #[ignore]d in the default suite."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:744-752"
      - ".github/workflows/ci.yml:780-787"
      - ".github/workflows/ci.yml:815-841"
      - ".github/workflows/ci.yml:843-855"
  - statement: "backend-integration only runs when `github.event_name == 'push' || needs.changes.outputs.rust == 'true'` -- i.e. on a push event, or on a pull request only after the changes job's dorny/paths-filter detects a Rust-path diff -- so it is not unconditionally part of every pull request's checks."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:604-609"
  - statement: "As of workflow run 33468069472 (created 2026-09-01T03:57:26Z), the backend-integration job completed with conclusion \"success\", i.e. the curated buzz-db/buzz-relay Postgres-backed subset it selects currently passes."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/actions/runs/33468069472"
      - "gh_run_view(id=33468069472, repo='launchpad-26/buzz') -> job 'Backend Integration (relay e2e)' status=completed conclusion=success"
  - statement: "backend-integration's \"Apply schema and seed deployment community\" step bootstraps Postgres for every later step in that job via `./bin/pgschema apply --file schema/schema.sql --auto-approve` plus `scripts/reconcile-schema-after-pgschema.sql`, not via buzz-db's own embedded SQLx migrator; root CLAUDE.md documents that pgschema's desired-state apply does not execute INSERT statements or preserve every storage parameter, which is why the reconcile script and a manual community INSERT are layered on top."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:664-689"
      - "CLAUDE.md:474"
      - "schema/schema.sql"
      - "scripts/reconcile-schema-after-pgschema.sql"
  - statement: "Local development instead applies buzz-db's own embedded migrator: Justfile's `_ensure-migrations` recipe runs `cargo run -p buzz-admin -- migrate` against the 40 SQL files under migrations/, a different bootstrap path from the one backend-integration's CI job uses."
    entry_class: FACT
    evidence:
      - "Justfile:211-213"
      - "migrations/0001_initial_schema.sql"
  - statement: "No required status checks are configured on the launchpad branch: `gh api repos/launchpad-26/buzz/branches/launchpad/protection` returns HTTP 404, and a GraphQL branchProtectionRules query against the repository returns an empty node list; ADR-0020 (accepted decision, dated 2026-08-21) independently records the identical 404 finding and states plainly that \"the one thing missing is enforcement, not method\"."
    entry_class: FACT
    evidence:
      - "gh_api(path='repos/launchpad-26/buzz/branches/launchpad/protection') -> 404 Not Found"
      - "gh_api_graphql(query='branchProtectionRules on launchpad-26/buzz') -> nodes=[]"
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020 adopts, as this fork's accepted testing methodology, five levels separated by the infrastructure they need, naming \"integration (`just test`, Postgres and Redis started automatically)\" as the level that exercises Postgres, and records that PRs failing `just ci` are stopped only by an honour system, not by branch-protection enforcement."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "buzz-db's own embedded-migrator and tenant-scoping-lint tests are infra-free and run under `cargo nextest run -p buzz-db --lib` (the same command test-unit and CI's unit-tests job invoke), so this node's obligation -- buzz-db's behaviour against a real, migrated Postgres database -- is a distinct, narrower obligation from the migrator's own already-covered invariant that the checked-in migration set applies cleanly."
    entry_class: FACT
    evidence:
      - "Justfile:331-336"
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "Issue #1356 (\"task: document verification/ci/required-checks.md\", parent Feature #617) is open and unlanded, and at the recorded revision launchpad/docs/corpus carries no verification/ subtree at all, so no relationships target exists yet for this node to point at for the required-checks question; this node's own enforcement findings above were independently verified against the live repository rather than deferred to that unlanded node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1356 (state: OPEN, checked via `gh issue view 1356`), compared against `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`"
relationships:
  - type: references
    target: architecture-containers-postgres
---

# Postgres integration testing — buzz-db test contract

## Purpose and boundary

This node documents one obligation: that `buzz-db`'s store and runtime layers behave
correctly when exercised against a real, migrated Postgres database, and names the
concrete test(s) that verify it, how to run them, and their current, honestly-stated
enforcement status. It covers `buzz-db`'s own Postgres-backed test suite only. It does
not cover Redis-backed integration testing, the relay's end-to-end suites in
`crates/buzz-test-client`, or `buzz-db`'s infra-free migrator/lint unit tests, each of
which is either a sibling obligation or out of scope entirely — see *Scope and
omissions*.

## Obligation

> `buzz-db`'s store and runtime modules persist, mutate, query and enforce their
> invariants correctly against a real, migrated Postgres instance — not merely against
> compiled Rust logic — as exercised by the crate's `#[ignore = "requires Postgres"]`-gated
> test suite when that suite is actually run with a live database reachable at
> `DATABASE_URL`/`TEST_DATABASE_URL`.

## Verifying test(s)

The obligation's test surface is large and crate-wide rather than a single function: at
the recorded revision, `crates/buzz-db/src` carries 241 `#[ignore` test attributes
(`grep -rn '#\[ignore' crates/buzz-db/ | wc -l`), nearly all reading
`#[ignore = "requires Postgres"]`, spread across:

- `src/runtime/tests.rs` — pool/writer/replica routing, read-your-writes, database
  guard/legacy-writer interaction (e.g. `database_guard_covers_legacy_writer_and_nip09_deletion`,
  line 31; `channel_window_routes_head_to_writer_and_cursor_pages_to_replica`, line 669).
- `src/runtime/migration.rs`, `src/runtime/observability.rs`, `src/runtime/replica_fence.rs`
  — migration-adjacent runtime behaviour, pool/advisory-lock metrics, replica-fence
  correctness.
- `src/store/*.rs` — one or more `#[ignore]`d Postgres tests per domain module that owns
  real persistence logic: `event.rs`, `channel.rs`, `channel_members.rs`, `thread.rs`,
  `deletion.rs`, `replaceable.rs`, `reaction.rs`, `user.rs`, `community.rs`,
  `relay_members.rs`, `relay_operators.rs`, `relay_admin_actions.rs`, `relay_invite.rs`,
  `moderation.rs`, `admin_moderation.rs`, `push.rs`, `workflow.rs`, `usage.rs`,
  `reminder.rs`, `git_repo.rs`, `api_token.rs`, `allowlist.rs`, `archived_identities.rs`,
  `product_feedback.rs`, `feed.rs`.

Enumerate the current, exact set with `grep -rn '#\[ignore' crates/buzz-db/src` (function
names sit a few lines below each attribute) or `cargo test -p buzz-db -- --ignored --list`
against a checkout with the workspace built — this node does not reproduce all 241 names,
because a static list would silently drift the first time a test is added or renamed, and
nothing would flag it (see `standards/evidence.md`'s point on structural-only checking).

CI additionally names a curated, non-exhaustive subset explicitly, by module or by exact
function name, in `.github/workflows/ci.yml`'s `backend-integration` job:

- `package(buzz-db) and test(/tests::(parameterized_|concurrent_parameterized_)/)` —
  replaceable-event transaction/concurrency/mention-index coverage (`ci.yml:695`).
- `package(buzz-db) and test(/observability::tests::(pool_acquire_records_success_timeout_and_error_with_wait_time|advisory_lock_records_success_contention_timeout_and_error)/)`
  (`ci.yml:707`).
- `package(buzz-db) and test(/relay_invite::tests/)` plus the matching
  `buzz-relay` `api::invites::tests` (`ci.yml:747`).
- `package(buzz-db) and test(coordinate_delete_spares_head_newer_than_the_deletion)`
  (`crates/buzz-db/src/store/event.rs:2357`; `ci.yml:782`).
- Eight named `relay_operators::tests` functions covering the roster audit trail,
  per-target lock serialization, audit ordering under a backward clock, audit-failure
  rollback, and the last-DB-operator invariant (`ci.yml:839`).
- Two named `moderation::tests` functions plus one `relay_admin_actions::tests` function
  covering report auto-escalation (`ci.yml:853`).

## How to run it

**The full ignored suite, locally, against a live database** (no `just` recipe wraps this
end to end today — see *Current enforcement status*):

```bash
docker compose up -d postgres redis        # starts buzz-postgres (postgres:17-alpine)
cargo run -p buzz-admin -- migrate         # applies migrations/*.sql via buzz-db's embedded migrator
DATABASE_URL=postgres://buzz:buzz_dev@localhost:5432/buzz \
TEST_DATABASE_URL=postgres://buzz:buzz_dev@localhost:5432/buzz \
cargo test -p buzz-db -- --ignored --nocapture
```

`just setup` performs the first two steps (services + migrate) as part of a wider bootstrap;
the third step (the `--ignored` test invocation itself) is not wrapped by any `just`
recipe and must be run directly, as above, or via
`cargo nextest run -p buzz-db --run-ignored ignored-only`.

**CI's curated subset**, reproduced from `backend-integration`'s own steps (requires the
job's own Postgres/Redis/MinIO docker-compose services and schema bootstrap — see
*Limits*):

```bash
cargo nextest run -E 'package(buzz-db) and test(/tests::(parameterized_|concurrent_parameterized_)/)' --run-ignored ignored-only
```

## Current enforcement status

**Gated, and only partially.** Precisely:

- The crate's full 241-test `#[ignore]`d Postgres surface is excluded from `just
  test-unit` (infra-free by design) **and** from `just test` (`scripts/run-tests.sh`'s
  integration-mode `buzz-db` step omits `--ignored`, by its own comment, on purpose — "they
  need a separate isolated-DB gate"). `just ci`, this repository's documented pre-PR gate,
  does not invoke `just test` at all. So no single locally-documented command exercises
  this obligation's full test surface; root `TESTING.md`'s description of `just test` as
  running "integration tests against Postgres and Redis" does not, at this granularity,
  include the crate's own `#[ignore]`d tests.
- A curated, explicitly-named subset (see *Verifying test(s)*) runs automatically in CI's
  `backend-integration` job via `cargo nextest run --run-ignored ignored-only` against
  named filters — this is real, automated, currently-green coverage (workflow run
  `33468069472` completed `success` on 2026-09-01), but it is not the crate's full ignored
  surface and the job itself is conditional (`push`, or a PR only after the `changes` job
  detects a Rust-path diff), not unconditional on every pull request.
- No required status checks are configured on the `launchpad` branch at all (confirmed
  live, and independently by ADR-0020), so even `backend-integration`'s currently-passing
  curated subset does not gate merging — it can fail and a PR still merges, per this
  fork's honour-system enforcement.
- The remainder of the 241 tests — the large majority — currently run only when a
  developer or agent explicitly invokes `--ignored`/`--run-ignored` against a live,
  migrated Postgres, as shown in *How to run it*. Nothing automated currently runs them.

## Limits

- **This node does not establish that any specific test's assertions are correct**, only
  that the tests exist, are gated as described, and (for the curated CI subset) currently
  pass in one observed run. A green run proves the executions it actually took, not every
  code path the obligation statement could be read to cover — the same limit
  `buzz-conformance/LIMITS.md` states for its own gate.
- **CI's schema bootstrap is not buzz-db's own migrator.** `backend-integration` applies
  `schema/schema.sql` via `./bin/pgschema apply` plus a hand-written reconcile script, not
  via `cargo run -p buzz-admin -- migrate`. So the curated CI subset exercises `buzz-db`'s
  query/mutation logic against a pgschema-produced schema, not a proof that `buzz-db`'s
  own checked-in migration set produces that same schema from scratch — that narrower
  claim belongs to the crate's separate, infra-free migrator unit tests
  (`cargo nextest run -p buzz-db --lib`, covering `runtime/migration.rs`'s non-`#[ignore]`d
  tests), which this node does not re-document.
- **The 241 count and the specific line numbers cited above are a snapshot** at commit
  `473205a7457b208455f188847bfb27b01aa83cac`. Per `standards/evidence.md`, a line position
  is never re-verified by the corpus checker against the file's current length, so treat
  every `path:line` citation above as a pointer that can drift, not a permanent coordinate.
- **This node's enforcement claims about `backend-integration` were checked against one
  observed run and the job definition's current YAML**, not against a statistical sample
  of runs; whether the job is reliably green over time was not established here (ADR-0020
  separately records that two of its own five most recent runs, measured 2026-08-21, had
  failed).
- **Whether the curated CI subset is the *right* representative sample of the crate's 241
  Postgres-backed obligations, or merely the ones that happened to need a security or
  correctness fix, is an inference this node does not make.** Each selector step's own
  code comment states why that specific test was added there; this node reports that
  fact and does not independently judge sufficiency.

## Scope and omissions

**This node covers** `buzz-db`'s `#[ignore = "requires Postgres"]`-gated test suite as one
obligation: what it is, where it lives, how it is (and is not) currently run locally and
in CI, and what CI's curated automated subset actually is and is not.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis-backed integration testing (pub/sub, presence, typing indicators) | A sibling `verification/integration/` node, not yet authored |
| The relay's end-to-end suites in `crates/buzz-test-client` (`e2e_relay.rs` and siblings), which exercise a live relay binary rather than `buzz-db` directly | `TESTING.md`'s multi-agent E2E guide; a future `verification` node scoped to the relay |
| `buzz-db`'s own embedded-migrator and tenant-scoping-lint invariants (that the checked-in migration set applies cleanly) — infra-free, and already covered by `cargo nextest run -p buzz-db --lib` | A future, narrower `verification` node on the migrator itself, if one is written |
| Whether `launchpad`'s required-status-checks gap (or lack of one) is itself the correct policy | Any future ADR revisiting ADR-0019/ADR-0020's enforcement question; not this node's call |
| Which CI checks are formally "required" via a mechanism this session could not query (an org-level ruleset) | Not established here — see below |

**Expected but not verified when this node was written:**

- **Organization-level rulesets on `launchpad-26` were not queryable in this session** —
  `gh api orgs/launchpad-26/rulesets` returned 404 for missing the `admin:org` scope, and
  the repository-level ruleset list (`gh api repos/launchpad-26/buzz/rulesets`) came back
  empty. Combined with the empty `branchProtectionRules` GraphQL result and ADR-0020's own
  independent 404 finding, the weight of evidence is that nothing currently gates a merge
  on any check passing — but an org-level ruleset invisible to this session's token scope
  cannot be fully ruled out, and a future reader with broader access should re-check rather
  than take this node's word for it.
- **None of the 241 `#[ignore]`d tests were actually executed while authoring this node.**
  Every claim about what they test, how they connect, and which ones CI selects comes from
  reading source and CI configuration, not from running the suite against a live database
  in this session. The one execution-backed data point is the cited CI run's `success`
  conclusion for the curated subset CI itself selects.
- **Whether every one of the 241 tests genuinely requires Postgres**, as opposed to being
  marked `#[ignore]` for an unrelated or stale reason, was not checked test-by-test; the
  reason strings attached to the attributes (overwhelmingly "requires Postgres") were read
  as the source of truth for classification.
