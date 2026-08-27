---
id: architecture-principles-fail-closed-boundaries
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The relay establishes req.community = resolve_host(connection.host) before AUTH, EVENT, REQ, REST, media, git, search, workflow, or pub/sub handling, and an unknown host fails closed rather than falling through to a default tenant."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "bind_community's HostResolver contract distinguishes Ok(Some(_)) (host maps to a community), Ok(None) (host is valid input but maps to nothing), and Err(_) (the lookup could not be performed); both Ok(None) and Err(_) are treated as fail-closed and produce the same BindError, so a database outage denies exactly like an unmapped host rather than admitting a default tenant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:31-46"
      - "crates/buzz-relay/src/tenant.rs:71-92"
      - "crates/buzz-relay/src/tenant.rs:49-59"
  - statement: "bind_community also fails closed on an empty or whitespace-only raw host before any resolver lookup runs, reusing the generic UnmappedHost rejection rather than a distinct error, so an unauthenticated caller cannot distinguish a missing Host header from any other unmapped host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:71-92"
  - statement: "tenant.rs's test suite exercises this fence directly and passes: `cargo test -p buzz-relay --lib tenant::tests` reports 10 passed, 0 failed, covering unmapped_host_fails_closed and lookup_error_fails_closed_not_default_tenant (the two BindError branches) plus the redteam_attack2 module (empty_raw_host_fails_closed_even_if_db_has_empty_host_row, whitespace_only_raw_host_fails_closed_even_if_db_has_empty_host_row, non_empty_unmapped_host_still_fails_closed_after_fix), which exercise the empty/whitespace-host edge case even when the host map itself carries a misconfigured empty-host row."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:148-333"
      - "cargo_test(package=buzz-relay, module=tenant::tests, commit=a44cf52fc740ebebbdd671427480d14f0bce0115) -> 10 passed; 0 failed; 0 ignored"
  - statement: "router.rs's handler binds the connection via bind_community before any WebSocket frame is read, and on Err(_) returns a generic rejection that never echoes the requested host and never distinguishes an unmapped host from a lookup failure, so an unauthenticated caller cannot probe which hosts or communities exist on the deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:301-313"
  - statement: "The same router.rs handler documents an intentional exception immediately adjacent to the fail-closed bind: the NIP-11 relay-information document is served before host binding runs, so it stays fail-open (an unmapped host still gets a document, with host-scoped fields such as icon simply absent) rather than leaking which hosts are mapped through a differential response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:297-307"
  - statement: "Inside the authenticated connection path, the pubkey-allowlist gate denies the connection when the allowlist database lookup itself fails, logging 'allowlist DB lookup failed, denying (fail-closed)', rather than treating a lookup error as an implicit allow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:186-214"
  - statement: "The moderation ban-state check applies the identical pattern: a DB error produces a distinct BanOutcome::DbError (denying with a generic 'internal error checking restriction state' message) rather than being conflated with a confirmed ban or treated as clear, so a transient database blip denies without falsely telling an innocent caller they are banned."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:106-131"
  - statement: "The same ban-state check runs a second time against a NIP-OA-proven owner pubkey when the agent's own check is clear, and a DB error on that second lookup denies with the identical fail-closed BanOutcome::DbError path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:133-154"
  - statement: "The ingest write path enforces the same rule independently of the connection-time auth gates: a DB error while checking restriction state during event ingest is commented 'Fail closed: a DB error must not let a banned/timed-out actor write' and returns IngestError::Internal rather than admitting the write."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2162-2168"
  - statement: "NOSTR.md documents the pubkey allowlist as fail-closed ('if the DB lookup fails, the connection is denied') and documents kind:7 reactions to an unrecognized target event as rejected and explicitly labeled fail-closed, since the reaction's channel is derived by looking up the target event rather than trusted from a client-supplied tag."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "ADR-0026 makes the opposite choice for a different kind of boundary: Buzz product operations continue (fail open) when telemetry export is disabled, unavailable, backpressured, misconfigured, or failing, with bounded buffering and observable drop-counting, explicitly because failing the product on a diagnostic-path outage would turn an observability incident into a product outage."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0026-fail-open-telemetry-export.md"
  - statement: "ADR-0026 explicitly carves security audit records out of its own fail-open decision, stating they 'retain their separate durability contract and are not weakened by this decision', which draws the line this node states generally: the fail-open choice is scoped to the diagnostic/telemetry export path, not to authorization, tenant-boundary, or audit durability decisions."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0026-fail-open-telemetry-export.md"
  - statement: "docs/spec/MultiTenantRelay.tla formally models the host-binding fence as Inv_HostBindingFence (every accepted write and every recorded duplicate/no-op carries a host whose mapped community equals the write's stored community) and Inv_ResolutionFence (persisted messages and write/auth observations are labeled by the resolved community, never a client-supplied claim), and both are conjuncts of the spec's top-level Safety property alongside Inv_NoTenantContextFailsClosed (a query observation with no TenantContext label serves no rows)."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:1011-1051"
      - "docs/spec/MultiTenantRelay.tla:1114-1141"
  - statement: "The relay's runtime conformance harness (crates/buzz-relay/src/conformance/mod.rs) translates the relay's actual per-request decisions into trace steps consumed against that same TLA+ model, and its EmitGuard uses a Drop-based guard so that any critical seam exiting without an explicit trace emission is itself recorded as a coverage breach (TraceAction::ImplBug) rather than silently passing unobserved."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs"
  - statement: "The row-zero host-binding fence, the pubkey-allowlist gate, the ban-state gate (both at connection auth and independently at ingest), and the reaction-target lookup are four independently-implemented call sites that all resolve a database or lookup failure to denial rather than to an implicit allow, which is evidence of a repeated pattern rather than a single enforced repo-wide rule — no lint, CI check, or single shared helper was found that requires new lookups to follow it."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "NOSTR.md"
    confidence: 0.75
  - statement: "Issue #691's definition of done requires the invariant be stated as one unambiguous MUST/MUST NOT property, with scope, enforcement points, observable failure behavior, and at least one verification/conformance mechanism named or its absence recorded explicitly."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#691 definition of done"
---

# Fail-closed authorization and tenant-boundary decisions

## The invariant

When a relay decision that admits, authenticates, authorizes, or scopes a
request to a tenant cannot be completed as designed — the underlying lookup
returns an error, a required input is empty or missing, or the resolver
cannot reach its data source — the relay **MUST** deny or reject the request.
It **MUST NOT** substitute a default tenant, an implicit allow, or a
best-effort continuation. Denial in this failure case **MUST** be
indistinguishable, from the caller's point of view, from denial for the
"clean" negative case the same gate exists to enforce (e.g. an unmapped host
looks identical to a database outage; a database-error ban check must not
tell an innocent caller "you are banned").

This is stated as one property because every cited enforcement point below
implements the identical shape — `Ok(Some(_))` admits, `Ok(None)` denies,
`Err(_)` also denies — even though the four call sites were written
independently and none of them share a single helper that enforces the
pattern across the codebase (see the INFERENCE entry in the evidence ledger
above).

## Scope

**Applies to:** decisions that establish or check *who is allowed to act, on
whose behalf, and inside which tenant boundary*. Concretely, at the current
revision:

- Host-to-community resolution (`bind_community` / `bind_deployment_community`
  in `crates/buzz-relay/src/tenant.rs`) — the "row-zero" seam every other
  handler depends on.
- The pubkey allowlist gate for pubkey-only NIP-42 auth
  (`crates/buzz-relay/src/handlers/auth.rs`).
- The moderation ban-state check, both at connection-time auth and
  independently at event ingest (`crates/buzz-relay/src/handlers/auth.rs`,
  `crates/buzz-relay/src/handlers/ingest.rs`).
- Reaction-target channel derivation (kind:7 reactions look up their target
  event's channel rather than trusting a client-supplied `h` tag; an unknown
  target is rejected — see `NOSTR.md`).

**Does not apply to:** paths that exist to observe or diagnose the system
rather than to admit or scope a request. ADR-0026 is the explicit,
adjudicated counter-example: telemetry export fails **open** — product
operations continue when the exporter is unavailable — because failing
product behavior on a diagnostic-path outage would turn an observability
incident into a product outage. The same ADR draws this exact line in its
own text: security audit records keep their separate durability contract and
are *not* covered by that fail-open decision. `router.rs`'s NIP-11
relay-information document is a second, narrower fail-open exception,
documented immediately adjacent to the fail-closed host bind it precedes:
it is served before host binding runs so that an unmapped host still
receives a document (this is deliberate — a differential response here would
itself leak which hosts are mapped), not a case of the invariant being
violated.

**Operations covered:** connection establishment (WebSocket upgrade, NIP-42
AUTH), event ingest (`EVENT`), and any handler that reads the bound
`TenantContext` to scope a query or write. **States covered:** the failure
mode is specifically "the lookup that would decide admit/deny could not run
or returned an indeterminate result" — not "the lookup ran and returned a
definite negative," which is the ordinary deny path these gates exist for in
the first place.

## Enforcement points and observable failure behavior

| Enforcement point | Failure observed | Behavior |
|---|---|---|
| `bind_community` (`crates/buzz-relay/src/tenant.rs`) | Unmapped host, empty/whitespace host, or resolver `Err` | Generic `BindError` (`UnmappedHost` or `Lookup`); `router.rs`'s call site turns any `Err` into a rejection that never echoes the host and never distinguishes the two cases |
| Pubkey allowlist (`crates/buzz-relay/src/handlers/auth.rs`) | Allowlist DB lookup error | Treated as "not allowed"; connection denied with the generic `auth-required: verification failed` message, logged as `"allowlist DB lookup failed, denying (fail-closed)"` |
| Ban-state check, connection auth (`crates/buzz-relay/src/handlers/auth.rs`) | Moderation-state DB lookup error | Distinct `BanOutcome::DbError`, denied with `error: internal error checking restriction state` — deliberately *not* the `banned` message, so a transient blip is not misreported as a confirmed ban |
| Ban-state check, ingest (`crates/buzz-relay/src/handlers/ingest.rs`) | Moderation-state DB lookup error during event write | `IngestError::Internal`; the write is rejected |
| Reaction target lookup (kind:7, documented in `NOSTR.md`) | Target event not found | Reaction rejected; channel is never inferred from a client-supplied tag |

In every row, the caller-visible outcome of "the check could not run" and
"the check ran and said no" are the same message class — the ledger above
notes this explicitly for the ban-state case, where the code comments call
out the risk of the two being conflated in the *other* direction (a DB error
must not be reported as a confirmed ban either).

## Verification / conformance mechanisms

Two independent mechanisms exist for the host-binding fence specifically —
the node does not claim they cover the other three enforcement points listed
above, which are verified only by their own unit-level assertions and code
comments cited in the evidence ledger:

1. **Formal model.** `docs/spec/MultiTenantRelay.tla` states
   `Inv_HostBindingFence`, `Inv_ResolutionFence`, and
   `Inv_NoTenantContextFailsClosed` as conjuncts of the spec's `Safety`
   property. These model exactly the shape described above: every accepted
   write or recorded duplicate carries a host whose resolved community
   matches the write's stored community, and an observation with no
   `TenantContext` label serves no rows.
2. **Runtime conformance harness.** `crates/buzz-relay/src/conformance/mod.rs`
   turns the relay's real per-request decisions into trace steps checked
   against that same model. Its `EmitGuard` is a `Drop`-based guard: a
   critical seam that exits without emitting a trace step is itself flagged
   as a coverage breach rather than silently passing unobserved, so an
   enforcement point that forgot to wire into the conformance harness is
   caught structurally rather than by omission going unnoticed.
3. **Unit tests.** `crates/buzz-relay/src/tenant.rs`'s own test module
   (`unmapped_host_fails_closed`, `lookup_error_fails_closed_not_default_tenant`,
   and the `redteam_attack2` submodule) exercises the fail-closed branches
   directly, including the edge case of an empty/whitespace host against a
   deliberately misconfigured empty-host row in the resolver's map.

This node does not itself re-run the TLA+ model checker or the conformance
harness against a live relay — it cites the mechanisms and their location so
a reader can. `python3 launchpad/project-intelligence/corpus/validate.py`
confirms only that this node's front matter and citations are structurally
well-formed (see `launchpad/docs/corpus/AGENTS.md`); it does not check that
any cited file still says what this node claims.

## Scope and omissions

**This node covers:** the fail-closed shape as a stated architectural
property, its enforcement points at the current revision, the one adjudicated
counter-example (ADR-0026) that bounds where fail-*open* is the intentional
choice instead, and the formal and runtime mechanisms that verify the
host-binding instance of it specifically.

**This node does not cover, and these are gaps rather than silence:**

- **No exhaustive audit.** Dozens of files in this repository mention
  "fail closed" or "fail open" in comments or tests (confirmed by a
  repository-wide grep at the recorded revision); this node cites the
  row-zero host-binding contract as the canonical, most heavily-verified
  instance and three sibling gates as corroborating instances, not a
  complete catalogue of every call site that follows or should follow the
  pattern.
- **No repo-wide enforcement mechanism was found.** The INFERENCE entry
  above records this explicitly: the pattern is repeated independently at
  each call site. No lint rule, CI check, or shared helper enforcing "a
  failed lookup at a tenant/auth boundary must deny" was located. A future
  violation at a new call site would not be caught by tooling — only by
  someone applying this node's stated invariant during review.
- **The formal model and conformance harness are not shown to cover every
  enforcement point in the table above.** Only the host-binding fence is
  confirmed to have TLA+ and runtime-trace coverage. Whether the
  pubkey-allowlist, ban-state, and reaction-target gates have equivalent
  formal coverage was not verified for this node and is left as an open
  question rather than assumed.
- **No per-type corpus template exists yet** (`launchpad/docs/corpus/AGENTS.md`
  §"Scope and omissions"), so this node's structure follows `node.schema.json`
  and the category-specific DoD tail on issue #691 rather than an established
  `architecture`/`principles` template.
- **No `relationships` are declared.** No other `architecture`- or
  `principles`-typed node exists on `origin/launchpad` at the recorded
  revision (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  lists only `AGENTS.md`, `README.md`, `schema/`, and `standards/`), so there
  is nothing yet to point at. This is the moment to revisit that once a
  sibling `architecture` or `principles` node merges.
