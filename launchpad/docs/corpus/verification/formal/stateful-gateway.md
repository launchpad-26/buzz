---
id: verification-formal-stateful-gateway
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
  - statement: "NIP-PL.md's normative 'Public APNs Gateway Profile' section states: 'The gateway is stateful: it retains installation authority, encrypted APNs-token custody, relay delegations, replay reservations, and endpoint quotas. The relay remains the executor and retains lease acceptance, matching, tenant authorization, endpoint uniqueness, coalescing, durable jobs/retries, and lease-generation invalidation.'"
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "docs/formal/STATEFUL_GATEWAY.md is titled 'Stateful gateway safety model', describes the public gateway as persisting installation authority, encrypted APNs-token custody, relay delegations, replay reservations, and endpoint quotas in PostgreSQL (with the relay separately owning lease matching, event authorization, coalescing, and durable delivery jobs), and names nip-pl/delivery.py and nip-pl/delivery_mutation.py as its bounded executable model and mutation suite."
    entry_class: FACT
    evidence:
      - "docs/formal/STATEFUL_GATEWAY.md"
  - statement: "docs/formal/nip-pl/NOTE.md's own section heading is 'Stateful public gateway', under which it states delivery.py models 'the authority actually shipped by the public gateway: relay signer confinement; installation/delegation epoch, generation, and expiry; atomic replay/quota admission; revocation ordering; custody; terminal request burn versus transient release; and the exact constant APNs body', and delivery_mutation.py 'requires signer, epoch, terminal-burn, quota-refund, and fixed-body mutants to be detected.'"
    entry_class: FACT
    evidence:
      - "docs/formal/nip-pl/NOTE.md"
  - statement: "crates/buzz-push-gateway/src/lib.rs's crate-level doc comment reads '//! Stateful, capability-gated APNs last hop for NIP-PL.', and model.rs's own module doc opens '//! Closed wire types for the stateful gateway.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/lib.rs"
      - "crates/buzz-push-gateway/src/model.rs"
  - statement: "The public push gateway (buzz-push-gateway), not the relay's push_runtime.rs delivery worker, is the correct referent of issue #1372's 'stateful gateway': every self-description in this repository that uses the literal word 'stateful' for a push-related component names the public gateway (NIP-PL.md's gateway profile, docs/formal/STATEFUL_GATEWAY.md's own title, docs/formal/nip-pl/NOTE.md's section heading, and buzz-push-gateway's own lib.rs/model.rs doc comments), while push_runtime.rs's own module doc comment calls itself 'Durable NIP-PL event matcher and gateway delivery worker' -- 'durable', never 'stateful' -- and a direct search of that file for the word 'stateful' returns no match."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
      - "docs/nips/NIP-PL.md"
      - "docs/formal/STATEFUL_GATEWAY.md"
      - "docs/formal/nip-pl/NOTE.md"
      - "crates/buzz-push-gateway/src/lib.rs"
      - "grep_file('stateful', 'crates/buzz-relay/src/push_runtime.rs') -> no match, exit status 1"
    confidence: 0.8
  - statement: "delivery.py's Gateway.admit method and module docstring implement exactly the invariants NOTE.md's 'Stateful public gateway' section lists in prose (signer/relay confinement, epoch/generation/expiry, atomic replay/quota admission, revocation ordering, custody, terminal-burn versus transient-release, and the fixed APNs body), and its explore() function exhaustively checks all 2^6 = 64 combinations of six boolean admission dimensions (relay/epoch/generation/grant-liveness/request-liveness/custody), both admit-then-revoke orderings, both terminal and transient outcome branches, and one epoch-rotation case."
    entry_class: FACT
    evidence:
      - "docs/formal/nip-pl/delivery.py"
  - statement: "delivery_mutation.py requires exactly five named mutants -- signer, epoch, terminal-burn, quota-refund, fixed-body -- to be caught, asserting the set of caught mutant labels equals that exact expected set."
    entry_class: FACT
    evidence:
      - "docs/formal/nip-pl/delivery_mutation.py"
  - statement: "Running delivery.py and delivery_mutation.py against this revision passes: delivery.py reports 69 combinations/interleavings checked and 'stateful gateway invariants: HOLD', and delivery_mutation.py reports all five expected mutants caught (signer, epoch, terminal-burn, quota-refund, fixed-body)."
    entry_class: FACT
    evidence:
      - "docs/formal/nip-pl/delivery.py"
      - "docs/formal/nip-pl/delivery_mutation.py"
      - "run_command('python3 docs/formal/nip-pl/delivery.py') -> stateful delivery combinations/interleavings checked: 69; stateful gateway invariants: HOLD"
      - "run_command('cd docs/formal/nip-pl && python3 delivery_mutation.py') -> stateful delivery mutants caught: signer, epoch, terminal-burn, quota-refund, fixed-body"
  - statement: "The production HTTP handler for POST /v1/deliveries/apns (deliver, in crates/buzz-push-gateway/src/http.rs) calls s.authority.authorize_delivery(delegation_id, relay, endpoint_epoch, generation, event_id, request_id, expires_at, quota_window_seconds, quota_max_deliveries, now) -- the same relay/epoch/generation/replay-id/expiry/quota parameters delivery.py's Gateway.admit abstracts -- and crates/buzz-push-gateway/src/postgres.rs's #[cfg(test)] mod tests carries four #[tokio::test] #[ignore = \"requires PostgreSQL\"] functions (concurrent_same_request_id_admits_exactly_once, concurrent_admissions_never_over_admit_past_quota_ceiling, duplicated_retryable_release_does_not_permanently_unfence_request_id, retryable_release_frees_request_id_on_real_postgres) that exercise the identical replay/quota/terminal-vs-transient invariants against the real PostgresAuthorityStore under real concurrent execution (tokio::join!), including two races the Python model cannot express: two concurrent admissions colliding on the same request_id, and two concurrent admissions racing a quota ceiling of 1."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/postgres.rs"
  - statement: "Neither verifying test is currently invoked by any CI workflow or Justfile recipe: a repository-wide search of every .github/workflows/*.yml file and the root Justfile found no reference to docs/formal/nip-pl or delivery.py; the Justfile's own 'cargo nextest run -p buzz-push-gateway' unit-test line runs only the crate's infra-free (non-#[ignore]d) tests, with an adjacent comment asserting the Postgres-backed contract/race tests 'run in the dedicated CI job below', but no job in .github/workflows/ci.yml names package buzz-push-gateway or selects any of postgres.rs's four #[ignore]'d tests, and the crate's own .github/workflows/push-gateway-helm-chart.yml only shells out to Helm chart render/release-contract scripts, never cargo test or cargo nextest."
    entry_class: FACT
    evidence:
      - "Justfile"
      - ".github/workflows/ci.yml"
      - ".github/workflows/push-gateway-helm-chart.yml"
      - "crates/buzz-push-gateway/src/postgres.rs"
      - "grep_repo('docs/formal/nip-pl|delivery.py|acceptance.py|fixed_payload|nip-pl', paths='.github/workflows/*.yml Justfile') -> no matches, exit status 1"
  - statement: "http.rs's own seven #[test] functions cover request-body size limits, APNs failure-code-to-outcome classification, and App Attest transcript byte vectors; none of them calls authorize_delivery or otherwise exercises the admission/replay/quota/epoch logic, and authority.rs and model.rs carry zero #[test] functions of their own -- that logic's only Rust-level test coverage is the four #[ignore]'d functions in postgres.rs cited above."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/authority.rs"
      - "crates/buzz-push-gateway/src/model.rs"
      - "grep_count('#[test]', 'crates/buzz-push-gateway/src/authority.rs crates/buzz-push-gateway/src/model.rs') -> 0, 0"
  - statement: "docs/formal/nip-pl/NOTE.md states 'They do not model the not-yet-shipped relay matcher/worker', but crates/buzz-relay/src/push_runtime.rs -- a real, non-stub module whose own doc comment calls it 'Durable NIP-PL event matcher and gateway delivery worker' -- exists and is shipped at this revision; NOTE.md is stale on that specific point. This does not weaken this node's own obligation, which is scoped to the gateway's authority plane and never depended on the relay matcher being unshipped."
    entry_class: FACT
    evidence:
      - "docs/formal/nip-pl/NOTE.md"
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "architecture-containers-push-gateway is a corpus node id loadable from origin/launchpad at this revision, so a references edge to it from this node resolves on the merge target, not only on this authoring branch."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/push-gateway.md"
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> includes architecture/containers/push-gateway.md"
relationships:
  - type: references
    target: architecture-containers-push-gateway
---

# Stateful gateway (public push gateway) — delivery-admission test contract

## Purpose and boundary

**What "stateful gateway" refers to, and how that was determined.** Issue #1372 does
not itself name the subsystem. The most literal referent is the public push gateway
(the `buzz-push-gateway` crate, deployed as `https://push.buzz.xyz`) — the only
push-related component in this repository that consistently self-describes as
**stateful**: NIP-PL's own normative "Public APNs Gateway Profile" section states "the
gateway is stateful"; `docs/formal/STATEFUL_GATEWAY.md` is titled "Stateful gateway
safety model"; `docs/formal/nip-pl/NOTE.md` files its formal model of this component
under the heading "Stateful public gateway"; and `buzz-push-gateway`'s own `lib.rs` and
`model.rs` doc comments each use the word directly. The relay's own push delivery
worker (`crates/buzz-relay/src/push_runtime.rs`) was considered and rejected as the
referent: its own module doc comment calls it "durable", never "stateful", and no
occurrence of the word "stateful" appears anywhere in that file. This node therefore
documents the public gateway's authority plane, not the relay's matcher/worker.

**One obligation, not the whole gateway.** The gateway exposes seven routes and several
distinct guarantees (App Attest enrollment, installation/delegation lifecycle, endpoint
rotation, revocation). This node covers exactly one of them: the **delivery-admission
authority obligation** — the rule that decides whether a `POST /v1/deliveries/apns`
request is admitted, and what state that admission durably changes. It does not cover
enrollment, delegation issuance, endpoint rotation, or revocation as their own
obligations, and it does not cover the separate "fixed payload" and "lease acceptance"
contracts `docs/formal/nip-pl/NOTE.md` documents alongside this one — see *Scope and
omissions*.

## Obligation

> The public push gateway admits a `POST /v1/deliveries/apns` request if and only if
> the request's relay, endpoint epoch, and delegation generation exactly match the
> live, unrevoked installation-and-delegation state; both the installation and the
> delegation are unexpired at admission time and the request's own expiry does not
> exceed the delegation's; and neither the auth-event id nor the request id has been
> admitted before. Admission is a single durable step that burns both ids and charges
> quota, and that charge is never refunded. A **terminal** disposition keeps the
> request id burned permanently; a **transient** disposition releases only the request
> id, leaving the auth-event id burned and the quota charge intact. The delivered APNs
> body is always the one normative constant and never varies with any admitted input.

Negative/error cases that are part of this contract, named explicitly:

- A relay other than the delegation's own relay, a stale or future epoch, or a stale
  generation is rejected outright (no partial admission).
- A revoked delegation rejects every subsequent admission attempt, regardless of
  ordering against the revoke call.
- An auth-event id or request id seen before — whether from a prior admission or a
  still-burned terminal disposition — is rejected; only a transient disposition's
  released request id may be reused.
- APNs-token custody failure (an already-admitted attempt) still burns the request id
  and charges quota, but sends nothing and reports a transient (not terminal)
  disposition.
- Endpoint-epoch rotation immediately invalidates every grant issued against the prior
  epoch; a grant for the current epoch remains admissible.

## Verifying test(s)

- **`docs/formal/nip-pl/delivery.py`** — `explore()` — a bounded, exhaustive model of
  the `Gateway.admit`/`finish`/`rotate`/`revoke` state machine. Checks all 64
  combinations of six boolean admission dimensions (relay match, epoch match,
  generation match, grant liveness, request liveness, custody), both orderings of a
  racing admit/revoke pair, both terminal and transient outcome branches (with quota
  and replay-fence bookkeeping asserted after each), and one epoch-rotation case.
- **`docs/formal/nip-pl/delivery_mutation.py`** — module-level script — five targeted
  mutants (drop signer confinement, drop epoch fence, drop terminal-request burn,
  refund quota on transient completion, let the APNs body vary) that the model must
  catch; asserts the caught set equals exactly `{signer, epoch, terminal-burn,
  quota-refund, fixed-body}`.
- **`crates/buzz-push-gateway/src/postgres.rs`**, `mod tests` —
  `concurrent_same_request_id_admits_exactly_once`,
  `concurrent_admissions_never_over_admit_past_quota_ceiling`,
  `duplicated_retryable_release_does_not_permanently_unfence_request_id`,
  `retryable_release_frees_request_id_on_real_postgres` — the same obligation exercised
  against the real production `PostgresAuthorityStore` (the store
  `authorize_delivery`/`finish_delivery` actually run against in `deliver`,
  `crates/buzz-push-gateway/src/http.rs`), under real Postgres and real concurrent
  execution (`tokio::join!`), covering two races the Python model cannot express: two
  admissions colliding on the same request id, and two admissions racing a quota
  ceiling of 1.

## How to run it

Bounded model and mutation suite — plain Python, no infrastructure:

```bash
python3 docs/formal/nip-pl/delivery.py
cd docs/formal/nip-pl && python3 delivery_mutation.py
```

Real-Postgres admission/replay/quota race tests — requires a live PostgreSQL reachable
via `DATABASE_URL` (see `docs/push-gateway-deployment.md` / `TESTING.md` for bringing
one up locally):

```bash
cargo nextest run -p buzz-push-gateway --run-ignored ignored-only \
  -E 'test(/postgres::tests::(concurrent_same_request_id_admits_exactly_once|concurrent_admissions_never_over_admit_past_quota_ceiling|duplicated_retryable_release_does_not_permanently_unfence_request_id|retryable_release_frees_request_id_on_real_postgres)/)'
```

## Current enforcement status

**Gated — both verifying paths exist, currently pass, and are not run automatically.**

- `delivery.py` / `delivery_mutation.py` are plain scripts with no `#[ignore]` concept
  of their own; they are gated only in the sense that nothing invokes them. A
  repository-wide search of every `.github/workflows/*.yml` file and the root
  `Justfile` found no reference to `docs/formal/nip-pl` or `delivery.py` anywhere.
- The four `postgres.rs` tests carry `#[tokio::test] #[ignore = "requires
  PostgreSQL"]`. The condition named by that attribute is a live PostgreSQL instance,
  but even that is not sufficient today: `Justfile`'s `cargo nextest run -p
  buzz-push-gateway` unit-test line runs only the crate's infra-free tests, and its own
  adjacent comment claims the Postgres-backed tests "run in the dedicated CI job
  below" — no such job exists. `.github/workflows/ci.yml`'s Backend Integration job
  enumerates every ignored Postgres test it runs by explicit package/test selector, and
  `buzz-push-gateway` is never named; the crate's own
  `.github/workflows/push-gateway-helm-chart.yml` only runs Helm chart render/contract
  scripts. So today these four tests run only when a developer (or agent) invokes the
  command above manually against a local Postgres.

Both scripts were run against the revision recorded above and passed (see the ledger
entry citing the exact output). The four `postgres.rs` tests were read, not executed,
for this node — starting a local PostgreSQL instance was judged out of scope for
authoring a documentation node; see *Limits*.

## Limits

- **The bounded model is not exhaustive over unbounded state.** `explore()` checks 64
  admission-dimension combinations plus a small number of ordering/outcome cases (69
  total) — a finite, hand-chosen abstraction, not a proof over arbitrary request
  sequences, arbitrary numbers of relays, or real wall-clock timing.
- **The Python model is not cross-checked against the real implementation by any
  automated mechanism.** `Gateway` in `delivery.py` is a hand-written reimplementation
  of the rules `authority.rs`/`postgres.rs` implement in Rust; nothing replays a real
  execution trace through both and diffs them (contrast `buzz-conformance`'s
  independently-reimplemented checker, which exists for exactly that trace-comparison
  reason). Fidelity between the Python model and the Rust implementation rests on the
  author's manual correspondence, not a checked one.
- **`delivery_mutation.py` covers five specific mutants, not exhaustive mutation
  testing.** A defect outside the five named categories (signer, epoch, terminal-burn,
  quota-refund, fixed-body) would not be caught by this suite.
- **The Postgres tests were not executed while authoring this node** (see *Current
  enforcement status*); their current pass/fail state is read from their own assertions
  and is not independently re-confirmed here. They are also gated behind
  `#[ignore]` and, as recorded above, are not selected by any CI job today — a
  regression here is caught only by a developer or agent choosing to run them locally.
- **No test in either suite drives the full HTTP surface end to end.** `http.rs`'s own
  unit tests (request-size limits, App Attest transcript vectors, APNs
  failure-code classification) never call `authorize_delivery`; there is no test that
  sends a real `POST /v1/deliveries/apns` HTTP request through the router and asserts
  on the admission outcome.
- **The delivered-body invariant here is a single assertion inside `delivery.py`
  (`assert all(body == FIXED_BODY for _, body in g.sends)`), not the dedicated,
  exhaustive check.** `docs/formal/nip-pl/fixed_payload.py` /
  `fixed_payload_mutation.py` model that invariant far more thoroughly and are a
  separate obligation — see *Scope and omissions*.

## Scope and omissions

**This node covers** the public push gateway's delivery-admission authority obligation
only: what makes `POST /v1/deliveries/apns` accept or reject a request, and what
durable state that decision changes.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The "fixed payload" content-invariant (APNs body never derived from any relay/gateway-state input), modeled exhaustively by `fixed_payload.py`/`fixed_payload_mutation.py` | A separate test-contract node, not yet authored |
| The relay-side "lease acceptance" ordering model (`acceptance.py`/`mutation_test.py`) — a distinct contract on the relay's own lease replacement/revocation logic, not the gateway's | A separate test-contract node, not yet authored |
| Installation enrollment (App Attest), delegation issuance, endpoint rotation, and revocation as their own obligations | Not yet authored as corpus nodes |
| The gateway as a deployable container — technology, listeners, deployment topology | `launchpad/docs/corpus/architecture/containers/push-gateway.md` (`architecture-containers-push-gateway`), referenced from this node |
| The end-to-end push-notification flow (enroll → delegate → relay match → gateway deliver) | `launchpad/docs/corpus/architecture/flows/push-notification.md` (`architecture-flows-push-notification`) |
| NIP-PL's normative wire protocol in full | `docs/nips/NIP-PL.md` |
| The relay's own push delivery worker (`push_runtime.rs`) as its own verification subject | Not this node; considered and rejected as the "stateful gateway" referent (see *Purpose and boundary*) |

**Relationships.** This node declares one `references` edge, to
`architecture-containers-push-gateway` — the corpus's existing description of the same
component as a deployable container, confirmed loadable from `origin/launchpad` at the
recorded revision. No `implements` edge is declared: no decision or PRD node
establishing this specific obligation exists yet in the corpus to point at.

**Expected but not verified when this node was written:**

- **The four `postgres.rs` tests were read, not run.** No local PostgreSQL instance was
  started to execute `concurrent_same_request_id_admits_exactly_once` and its three
  siblings; their current behavior is asserted from reading the test bodies and their
  own assertions, not from a fresh run's output.
- **Whether any out-of-repository process (a manual release checklist, a runbook not
  checked into this repository) runs the Postgres-backed tests before a
  `buzz-push-gateway` deploy was not established.** Only this repository's own CI
  configuration and `Justfile` were searched.
- **Whether `docs/formal/nip-pl/NOTE.md`'s "not-yet-shipped relay matcher/worker" line
  is stale only for `push_runtime.rs`, or also for some other component the same
  sentence might have meant, was not fully explored** — the correction recorded in this
  node's evidence ledger is limited to the one component checked.
