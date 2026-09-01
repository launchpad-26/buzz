---
id: verification-strategy-test-levels
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
  - statement: "ADR-0020 adopts upstream's testing methodology unchanged: five levels separated by the infrastructure they need -- unit (`just test-unit`, no infrastructure), integration (`just test`, Postgres and Redis started automatically), relay E2E (`cargo test -p buzz-test-client -- --ignored`, needs a running relay), desktop E2E smoke, and desktop E2E integration -- with every relay-dependent test marked `#[ignore]` so a plain `cargo test` stays safe everywhere."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "Root TESTING.md documents `just test-unit` (no infrastructure) and `just test` (unit plus Postgres/Redis-backed integration, starting Docker if needed) as the two automated entry points, and states explicitly that neither runs the E2E suites in `buzz-test-client`, which are `#[ignore]`d and invoked separately as `cargo test -p buzz-test-client -- --ignored`."
    entry_class: FACT
    evidence:
      - "TESTING.md"
  - statement: "The `test-unit` Justfile recipe does not run `cargo test --workspace`; it is a curated, explicitly enumerated list of per-crate `cargo nextest`/`cargo test` invocations (buzz-core, buzz-auth --lib plus its doctests, buzz-voice, buzz-cli, buzz-db --lib, buzz-conformance, buzz-push-gateway, buzz-backend-kubernetes, buzz-agent --lib, and a filtered slice of buzz-relay --lib), and its own inline comments state this enumeration exists because 'nothing in CI runs `cargo test --workspace`' -- an unlisted crate's tests would otherwise ship green without ever executing."
    entry_class: FACT
    evidence:
      - "Justfile:316-388"
  - statement: "In CI, the 'Unit Tests' job runs `just test-unit` and is gated on `github.event_name == 'push' || needs.changes.outputs.rust == 'true'` -- on a pull request it only runs when the `changes` job's `dorny/paths-filter` marks the `rust` path group as touched; every push to a branch (including `launchpad` itself) always runs it regardless of the filter."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:125-146"
  - statement: "The CI job named 'Backend Integration (relay e2e)' starts Postgres, Redis and MinIO via `docker compose up -d`, applies the schema with `pgschema apply`, seeds a `localhost:3000` deployment community, and then runs specific `#[ignore]`d, Postgres-backed `buzz-db` test filters directly via `cargo nextest run --run-ignored ignored-only` -- this is a different invocation from the developer-facing `just test`, which instead calls `scripts/run-tests.sh all` (a separate script that starts local infra via `just _ensure-migrations` and runs its own unit-then-integration sequence); the two are not the same command even though both exercise the same infrastructure tier."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:604-711"
      - "scripts/run-tests.sh:1-70"
  - statement: "The CI job named 'Relay E2E' downloads a prebuilt `buzz-relay` binary artifact (produced by the Desktop E2E Relay job), starts it via `scripts/start-relay-for-tests.sh --no-build`, and then runs several `#[ignore]`d `buzz-test-client` integration-test binaries directly with `cargo test -p buzz-test-client --test <name> -- --ignored --nocapture` against that live relay on `ws://localhost:3000` -- this is the concrete invocation behind ADR-0020's and TESTING.md's more general `cargo test -p buzz-test-client -- --ignored` description."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:865-917"
  - statement: "Desktop E2E has two Playwright projects invoked as separate package.json scripts -- `test:e2e:smoke` (`pnpm build:e2e && playwright test --project=smoke`) and `test:e2e:integration` (`pnpm build:e2e && playwright test --project=integration`) -- and CI runs them as two distinct jobs: 'Desktop Smoke E2E' (sharded across 4 parallel shards) and 'Desktop E2E Integration' (fanning out to a sharded job and then a gate job that fails if any shard did not succeed)."
    entry_class: FACT
    evidence:
      - "desktop/package.json:21-22"
      - ".github/workflows/ci.yml:240-260"
      - ".github/workflows/ci.yml:587-604"
  - statement: "The CI job named 'Mobile' runs `dart format --output=none --set-exit-if-changed .`, `flutter analyze`, then `flutter test`, then builds an Android debug APK, all under `mobile/`; the Justfile's `mobile-test` recipe runs only `flutter test` directly. ADR-0020 does not name a mobile test level in its five-level list, so this level's presence in this repository-wide inventory is drawn from ci.yml and the Justfile rather than from ADR-0020 itself."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:954-1011"
      - "Justfile:754-755"
  - statement: "`crates/buzz-cli/TESTING.md` is a manual, step-by-step live-testing runbook that an agent or developer follows against a locally started relay, checking output by hand -- it is not an automated level alongside `just test-unit`, `just test`, or the `--ignored` E2E suites, and running it produces no pass/fail signal CI can consume."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/TESTING.md:1-20"
  - statement: "As of 2026-09-01 at the recorded revision, `GET /repos/launchpad-26/buzz/branches/launchpad/protection` returns 404 (branch protection not configured) and `GET /repos/launchpad-26/buzz/rulesets` returns an empty list -- so no unit, integration, relay-E2E, desktop-E2E, or mobile CI job is a required status check on `launchpad` today, matching ADR-0020's own 2026-08-21 finding for `required_status_checks` and showing the gap has not closed in the interim."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad/protection') -> 404 Not Found, checked 2026-09-01"
      - "gh_api('repos/launchpad-26/buzz/rulesets') -> [], checked 2026-09-01"
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "Every level-running CI job in ci.yml (Unit Tests, Desktop Core/Smoke E2E, Desktop E2E Integration, Backend Integration, Relay E2E, Mobile) is conditioned on `github.event_name == 'push' || needs.changes.outputs.<group> == 'true'`, so on a pull request each level only executes when the `changes` job's `dorny/paths-filter` marks its own path group as touched; a job existing and running in CI is therefore a narrower fact than a job running on every PR, independent of the separate required-status-check question above."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:125-146"
      - ".github/workflows/ci.yml:148-153"
      - ".github/workflows/ci.yml:865-870"
      - ".github/workflows/ci.yml:954-959"
  - statement: "`desktop/playwright.config.ts` sets `retries: process.env.CI ? 2 : 0` -- zero locally, two in CI -- and `desktop/scripts/summarize-flaky-tests.mjs`'s header comment states this exists because Playwright's retry-then-pass behavior hid a `stream.spec.ts` membership race (issue #1798) for months; the script walks the JSON reporter's suite tree and appends any test whose status is `flaky` to the CI job summary so a retried failure stays visible even when the shard ultimately goes green. Both are still present unchanged at the recorded revision."
    entry_class: FACT
    evidence:
      - "desktop/playwright.config.ts:6"
      - "desktop/scripts/summarize-flaky-tests.mjs:1-11"
  - statement: "ADR-0020 records, as a deliberate and named non-coverage rather than an oversight, that the web client has zero tests and that agent behavior has no deterministic harness, and tracks both under issue #290 rather than leaving them silently absent."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "At the recorded revision, `origin/launchpad`'s corpus tree under `launchpad/docs/corpus/` contains no `verification/` subtree and no node named `verification-ci-required-checks`, so this node declares no `references` relationship toward it -- there is nothing yet to point at."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no verification/** entries, checked 2026-09-01 at commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "ADR-0020's own test-and-suite counts (4,615 Rust test functions, 37 integration test files, 19 relay E2E suites, 146 Playwright specs, 481 desktop `*.test.mjs` files, 123 Flutter tests) are dated to 2026-08-21 at `launchpad` tip `db4305a4a` and were not re-measured for this node; the counts are cited here as ADR-0020's own dated snapshot, not re-asserted as current."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
---

# Verification strategy — repository-wide test levels

## Scope

This node covers **the whole-repository, multi-tier automated test strategy for
Buzz** (`block/buzz`, operated as the `launchpad-26` fork): which automated test
levels exist across the Rust workspace, the desktop app, and the mobile app; what
infrastructure each needs; the exact command that invokes each; and whether any of
them currently gates a merge. It applies to this scope only.

It does **not** cover: the web client (which ADR-0020 records as having zero tests
today), a deterministic harness for agent behavior (which ADR-0020 records as not
existing), the manual `crates/buzz-cli/TESTING.md` live-testing runbook (a
step-by-step human/agent procedure, not an automated pass/fail level), or
non-test CI jobs such as `rust-lint`, `security`, `dead-token-guard`,
`server-cross-compile`, `windows-rust`, `desktop-build-macos`, and the Tauri/desktop
static-check jobs (`desktop-tauri-check` and friends) — those check formatting,
linting, cross-compilation, or supply-chain posture, not runtime behavior, and are
a different node's subject.

## Levels

| Level | Purpose | Infrastructure | Command | Gating |
|---|---|---|---|---|
| Rust unit | Fast, infrastructure-free regression coverage for a curated, explicitly enumerated set of crates (buzz-core, buzz-auth, buzz-voice, buzz-cli, buzz-db --lib, buzz-conformance, buzz-push-gateway, buzz-backend-kubernetes, buzz-agent --lib, a filtered slice of buzz-relay --lib) | None | `just test-unit` | Runs unconditionally in CI (job "Unit Tests"), not `#[ignore]`d |
| Backend integration | Postgres-backed persistence, concurrency, and observability behavior that cannot be exercised without a real database | Postgres, Redis, MinIO on `localhost` (Docker) | Developer: `just test` (→ `scripts/run-tests.sh all`). CI: a distinct curated `cargo nextest --run-ignored ignored-only` invocation in the "Backend Integration (relay e2e)" job | `#[ignore]`d in source; the CI job's own filters select only the ignored tests it names, and it is not identical to the developer command even though both target the same infrastructure tier |
| Relay E2E | End-to-end behavior against a live, single-process relay (Nostr interop, persona, invites, membership snapshots, media read-auth) | A running `buzz-relay` binary (built once, reused as a CI artifact) | `cargo test -p buzz-test-client -- --ignored` (CI runs several named `--test` binaries individually against `ws://localhost:3000`) | `#[ignore]`d; opt-in, requires a live relay |
| Desktop E2E smoke | Fast Playwright coverage of core desktop UI flows against the E2E mock Tauri bridge | Playwright browser automation, `pnpm build:e2e` (mock-bridge build) | `pnpm test:e2e:smoke` (`pnpm build:e2e && playwright test --project=smoke`) | Runs in CI, sharded 4-way ("Desktop Smoke E2E"); not `#[ignore]`d, but the desktop CI jobs only run on `push` or when the `changes` job marks `desktop`/`desktop-rust`/`rust` as touched |
| Desktop E2E integration | Broader Playwright coverage requiring a real relay-backed desktop bridge, not just the mock | Playwright browser automation plus relay-backed integration bridge, `pnpm build:e2e` | `pnpm test:e2e:integration` (`pnpm build:e2e && playwright test --project=integration`) | Runs in CI as a sharded job plus a gate job that fails if any shard did not succeed ("Desktop E2E Integration"); same push/path-filter gating as smoke |
| Mobile | Flutter format, static analysis, and widget/unit tests for the Flutter app | Flutter SDK, no external services | `flutter test` (also `dart format --output=none --set-exit-if-changed .` and `flutter analyze` alongside it in CI; `just mobile-test` runs `flutter test` alone) | Runs in CI ("Mobile" job) only when the `changes` job marks the `mobile` path group as touched, or on push; not named as one of ADR-0020's five levels, drawn instead from `ci.yml` and the Justfile |

## Current enforcement

**No level in this table is a required status check on `launchpad` today.** As of
2026-09-01, `GET /repos/launchpad-26/buzz/branches/launchpad/protection` returns 404
(not configured) and `GET /repos/launchpad-26/buzz/rulesets` returns an empty list —
the same gap ADR-0020 found on 2026-08-21 for `required_status_checks`, unchanged in
the interim. Every job in the table above **runs in CI** (on every push, and on pull
requests whose changed paths match the job's `dorny/paths-filter` group), but a job
running in CI is not the same fact as a job a PR cannot merge past. Upstream's own
"PRs that fail `just ci` will not be merged" is, today, an honour system rather than
an enforced gate. ADR-0019 already ruled on what may gate at all and deferred
enforcement to a future CI/CD pipeline programme; this node does not revisit that
question, only records the current state honestly.

## Risks and quality goals by level

| Level | Risk it is meant to catch |
|---|---|
| Rust unit | Regressions in pure logic and in-process behavior for the crates it enumerates, cheaply and on every run |
| Backend integration | Persistence, concurrency, and pooling bugs that only manifest against a real Postgres/Redis, not a fake |
| Relay E2E | Protocol-level and cross-subsystem regressions only visible when a real relay process handles real WebSocket/HTTP traffic |
| Desktop E2E smoke | Breakage in core desktop user flows against the UI as actually rendered, not just its unit-tested pieces |
| Desktop E2E integration | Breakage specific to the relay-backed bridge path that the mock bridge cannot exercise |
| Mobile | Regressions in the Flutter app's own logic and widget behavior, plus formatting/lint drift |

None of these levels, individually or together, currently assert anything about the
web client or about agent behavior — see *Deliberately out of scope*.

## Environments, data and fixtures

- **Rust unit** needs no external service; `test-unit` first runs
  `scripts/test-ensure-local-relay-key.sh` and then dispatches per-crate
  `cargo nextest`/`cargo test` invocations in-process.
- **Backend integration** runs against Postgres, Redis and MinIO started via
  `docker compose up -d postgres redis minio minio-init` on `localhost`; CI applies
  the schema with `pgschema apply` and seeds a fixed deployment community
  (`localhost:3000`) before running its filtered, `#[ignore]`d test set.
- **Relay E2E** reuses a prebuilt `buzz-relay` binary artifact (compiled once by the
  Desktop E2E Relay job) started via `scripts/start-relay-for-tests.sh --no-build`,
  and points `buzz-test-client` binaries at it over `RELAY_URL=ws://localhost:3000`.
- **Desktop E2E (smoke and integration)** both require the E2E-mode build
  (`pnpm build:e2e`), which compiles in the mock Tauri bridge; a plain `pnpm run
  build` omits it and every mock-mode spec fails with a misleading
  "Community connection failed" UI state rather than a build error (see root
  `CLAUDE.md`'s "Writing E2E Screenshot Specs" section for this exact failure mode).
  Integration additionally needs the relay-backed bridge path, not just the mock.
- **Mobile** needs only the Flutter SDK and `mobile/pubspec.lock`-pinned
  dependencies (`flutter pub get`); no external service.

## Traceability

Every command and gating claim in the levels table above is cited directly to the
Justfile recipe or `ci.yml` job that defines it, at line ranges pinned to the
revision recorded in this node's provenance. Where the developer-facing command and
the CI job's actual invocation diverge — as they do for backend integration (`just
test` vs. the CI job's own curated `cargo nextest` filters) — both are named rather
than treating one as a stand-in for the other. A claim that a level "gates merges"
is treated as needing branch-protection or ruleset evidence specifically, not the
mere existence of a CI job, per the confidence standard's rule that reasoning must
be visible and re-checked at the revision it is stated for.

This node does not establish a requirements-to-tests traceability matrix for
individual product claims (e.g., which test proves which capability-level
obligation) — that is the shape `templates/test-contract.md` (issue #1349, not yet
merged as a node) exists for, one obligation at a time. This node's own
traceability claim is narrower: that its own statements about levels, commands, and
gating are each pinned to a citable source at a stated revision.

## Flakiness and quarantine policy

`desktop/playwright.config.ts` sets `retries: process.env.CI ? 2 : 0` — no retries
locally, so a developer feels their own flakiness directly, and two retries in CI.
`desktop/scripts/summarize-flaky-tests.mjs` exists specifically because a bare
retry-then-pass hid a real bug (a `stream.spec.ts` membership race, issue #1798) for
months: it walks the Playwright JSON reporter's suite tree and appends any test
whose final status is `flaky` to the CI job summary, so a retried failure stays
visible even when the shard ultimately reports success. **There is no formal
quarantine mechanism** (no skip-list, no dedicated quarantine CI lane) for any level
in this table — visibility via the flaky-test summary is the only mitigation that
exists today, and it is Playwright-specific; the Rust levels (unit, backend
integration, relay E2E) and the mobile level have no retry or flakiness-visibility
mechanism recorded anywhere this node's evidence reaches.

## Deliberately out of scope

- **The web client has zero tests.** ADR-0020 records this as a deliberate,
  named non-coverage tracked under issue #290, not an oversight this node repeats
  silently.
- **Agent behavior has no deterministic harness.** ADR-0020 records this as the
  same kind of named gap, also tracked under #290; the risk accepted by leaving it
  out is that the cohort can assert what an agent contracts to do but not what it
  actually does at runtime.
- **The nine product-code divergences this fork carries** (`crates/buzz-cli`,
  `crates/buzz-persona`, six files under `desktop/src-tauri/`, per ADR-0020) are not
  separately protected by any level in this table beyond whatever incidental
  coverage the existing levels provide; ADR-0020 names the need for fork-specific
  protection without this node claiming it exists.
- **Static/lint/build CI jobs** (`rust-lint`, `desktop-tauri-check`,
  `desktop-tauri-fmt-check`, `web-build`/`web-check`, `security`,
  `dead-token-guard`, `server-cross-compile`, `windows-rust`,
  `desktop-build-macos`) are excluded from this table because they check
  formatting, static types, cross-compilation, or supply-chain posture rather than
  runtime test behavior.
- **`crates/buzz-cli/TESTING.md`** is excluded because it is a manual runbook with
  no automated pass/fail signal, not a level a CI job or `just` recipe invokes.

## Relationships

None declared. `origin/launchpad`'s corpus tree carries no `verification/**` nodes
at the recorded revision — including no `verification-ci-required-checks` node to
`references` for the enforcement-gap claim this node also makes independently above
— and ADR-0020 itself is a decision record under `launchpad/decisions/`, not a
corpus node with a stable `id`, so it is cited as evidence rather than linked as a
`relationships` target. The first of either to land as a corpus node is the moment
to add the corresponding edge; until then a relationship naming either would be
either invalid (no such node exists) or fabricated (pointing at a file, not a node
id).

## Scope and omissions

**This node covers** the levels table, current enforcement status (checked live,
not merely quoted from ADR-0020), risks each level addresses, the environment/data
each needs, this node's own (narrow) traceability claim, and the flakiness/retry
policy that exists today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| One testable obligation and the specific test(s) that verify it | `templates/test-contract.md` (issue #1349), not yet merged as a corpus node |
| General citation mechanics for how any corpus node should cite a test | `standards/test-references.md`, present in this tree but not read against this node's own citations beyond what this node already does |
| Step-by-step manual CLI testing instructions | `crates/buzz-cli/TESTING.md` |
| Why this repository's methodology looks the way it does, and the adopt-vs-design decision itself | `launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md` |
| What may gate a merge at all, as a policy question | `launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md`, deferred further by ADR-0020 |
| Whether `required_status_checks` or rulesets change after this node's recorded revision | Re-check `gh api repos/launchpad-26/buzz/branches/launchpad/protection` and `gh api repos/launchpad-26/buzz/rulesets` directly; this node's claim is dated 2026-09-01 |
| A full CI-job inventory (build, lint, security, cross-compile jobs) | `.github/workflows/ci.yml` directly; this node lists only the jobs that constitute a test level |

**Expected but not verified when this node was written:**

- **Whether the six levels in this table currently pass reliably was not
  re-measured.** ADR-0020 itself states two of its five most recent `ci.yml` runs
  (as of 2026-08-21) had failed, and this node did not re-run or re-sample CI
  history at its own recorded revision to see whether that has changed.
- **ADR-0020's dated test/suite counts (4,615 Rust test functions, 37 integration
  files, 19 relay E2E suites, 146 Playwright specs, 481 desktop `*.test.mjs` files,
  123 Flutter tests, measured 2026-08-21 at `db4305a4a`) were not re-measured at
  this node's own revision.** They are cited above as ADR-0020's own snapshot, not
  re-asserted as current; a fresh count would very likely differ.
- **Whether the mobile level's absence from ADR-0020's own five-level list was a
  deliberate omission or simply predates mobile CI being wired up was not
  investigated** — this node states the level exists today (per `ci.yml` and the
  Justfile) without resolving why ADR-0020 did not name it.
- **The `dorny/paths-filter` group boundaries** (which specific paths map to
  `rust`, `desktop`, `desktop-rust`, `web`, `mobile`) were not enumerated in full;
  this node states only that each level-running job is conditioned on its
  corresponding group.
