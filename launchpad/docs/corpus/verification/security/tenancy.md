---
id: verification-security-tenancy
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
  - statement: "docs/multi-tenant-conformance.md's 'Row zero: request community binding' section states, as conformance obligations, that unknown or unmapped hosts fail closed with a generic rejection and never fall through to a default tenant, and that a client-supplied signal such as an event's h tag or a token's community stamp may narrow or authenticate authority inside the host-resolved community but never override which community that is -- a disagreeing stamp is rejected."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "bind_community (crates/buzz-relay/src/tenant.rs) is the single row-zero entry point: it normalizes the raw host, rejects an empty or whitespace-only host before the resolver is ever consulted, and returns a fail-closed BindError -- UnmappedHost on a successful lookup that finds no community, Lookup(e) on a resolver error -- with no code path that yields a default or fallback TenantContext."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:71-92"
  - statement: "router.rs's nip11_or_ws_handler calls bind_community before WebSocketUpgrade::from_request and, on any Err(_) (unmapped host or lookup failure alike), returns HTTP 404 with the fixed body 'relay: no community is configured for this host' without branching on which BindError variant occurred, so an unauthenticated caller cannot distinguish 'unmapped' from 'lookup error' from the response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:343-354"
  - statement: "tenant.rs's own #[cfg(test)] mod tests contains five relevant #[tokio::test] functions exercising bind_community directly against an in-memory fake HostResolver, none carrying #[ignore]: unmapped_host_fails_closed, lookup_error_fails_closed_not_default_tenant, and a redteam_attack2 submodule (empty_raw_host_fails_closed_even_if_db_has_empty_host_row, whitespace_only_raw_host_fails_closed_even_if_db_has_empty_host_row, non_empty_unmapped_host_still_fails_closed_after_fix) that specifically covers the empty/whitespace-host edge case even when the resolver's map carries a misconfigured empty-host row."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:243-332"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs's module doc-comment describes the file as mirroring docs/multi-tenant-conformance.md's obligation table one module per row and calls itself 'the executable form of the conformance contract'; its row_zero_host_binding module contains two #[tokio::test] functions, unmapped_host_fails_closed_generically and client_supplied_community_cannot_override_host, both marked #[ignore] and both carrying real, fully-written assertion bodies rather than being stubbed via the file's own pending_lane(...)/todo!() helper -- unlike sibling modules in the same file such as membership_allowlist::archive_in_a_does_not_affect_b, which is a #[ignore]d test whose entire body is a pending_lane(...) call."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1-38"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:74-339"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:899-912"
  - statement: "unmapped_host_fails_closed_generically asserts three wire-observable properties against a live two-host relay: an unmapped host's non-nostr+json HTTP request returns 404 while a mapped host's does not; the unmapped-host response body does not echo the host's authority or label; and a raw WebSocket handshake to the unmapped host is rejected at the upgrade rather than accepted and bound to a default tenant."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:77-191"
  - statement: "client_supplied_community_cannot_override_host asserts that an A-bound connection posting a kind:9 event whose #h tag names a channel that exists only in community B is rejected, with the rejection pinned to the exact channel-scope reason string 'restricted: not a channel member' (so the red cannot be an incidental earlier gate) and asserted not to echo B's channel UUID; a positive control confirms the same post succeeds against B directly, isolating the override property from an unrelated membership or setup failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:193-338"
  - statement: "The row_zero_host_binding suite's own module doc-comment gives its run command as RELAY_URL_A and RELAY_URL_B pointed at the same relay process/Postgres/Redis with only the Host header differing, selected explicitly with `cargo test -p buzz-test-client --test conformance_multitenant -- --ignored`."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:20-31"
  - statement: "At the recorded revision, neither tenant.rs's tenant::tests module nor conformance_multitenant.rs's row_zero_host_binding module is selected by any automated CI job or documented just recipe: Justfile's test-unit recipe's only -p buzz-relay --lib invocation is filtered to test(/^api::admin::/) and its own comments state that nothing in CI runs `cargo test --workspace` and that buzz-relay --lib coverage must be enumerated test-by-test; ci.yml's Backend Integration job archives -p buzz-relay --lib but consumes that archive only through steps filtered to other, unrelated exact test names; and scripts/run-tests.sh never invokes -p buzz-relay at all."
    entry_class: FACT
    evidence:
      - "Justfile:316-385"
      - ".github/workflows/ci.yml:374-387"
      - ".github/workflows/ci.yml:743-759"
      - "grep(pattern='tenant::', scope='.github/workflows/*.yml,Justfile,scripts/*.sh') -> no matches"
      - "grep(pattern='conformance_multitenant|RELAY_URL_A', scope='.github/workflows/*.yml,Justfile,scripts/*.sh') -> no matches"
  - statement: "architecture-principles-host-selects-community and architecture-principles-fail-closed-boundaries are both present on origin/launchpad at the recorded revision and each independently states and partially verifies the same row-zero fail-closed invariant this node's obligation and tests cover; fail-closed-boundaries.md additionally names docs/spec/MultiTenantRelay.tla's Inv_HostBindingFence/Inv_ResolutionFence and crates/buzz-relay/src/conformance/mod.rs's runtime trace harness as further, non-test-layer verification mechanisms for the same seam, which this node does not restate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/host-selects-community.md"
      - "launchpad/docs/corpus/architecture/principles/fail-closed-boundaries.md"
  - statement: "A relationships[].target naming an id no node in the corpus carries is a hard validation error, and at the recorded revision origin/launchpad's corpus tree contains no verification-typed node at all -- specifically neither a verification-security-isolation nor a verification-formal-multi-tenant-auth id exists to reference -- so neither prospective sibling edge resolves and both are correctly declared absent below rather than assumed."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> AGENTS.md, README.md, agents/invariants.md, architecture/** (containers, context, deployment, flows, principles), capabilities/**, development/**, layers/**, schema/** (excluded from validation), standards/**, templates/**; no verification/ subtree"
  - statement: "The client_supplied_community_cannot_override_host test's own doc-comment distinguishes itself from two named siblings that assert different properties of the same NIP-98/token/AUTH-tag community-stamp scope branch: api_tokens_nip98_replay's verify_nip42_rejects_event_signed_for_wrong_communitys_host and channels_membership's same_channel_uuid_in_two_communities_is_isolated -- neither of which this node's obligation or tests cover."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:206-224"
relationships:
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-fail-closed-boundaries
---

# Row-zero host binding fails closed — test contract

## Purpose and boundary

This node documents one obligation: **the request host is the sole, non-overridable
community selector, and an unknown or unmapped host fails closed rather than falling
through to a default tenant.** This is Buzz's own "row zero" -- the obligation
`docs/multi-tenant-conformance.md` states first, because every other per-surface
tenant-scoping rule in that table assumes row zero already holds.

**This node covers the tenancy *resolution mechanism* itself, and only that.** It is
about how `req.community` gets bound from `connection.host` and what happens when that
binding cannot succeed -- not about what happens *after* a community is bound. It does
not cover:

- **Per-surface `community_id` scoping** (channels, search, pub/sub, media, git,
  workflows, audit, and the rest of `docs/multi-tenant-conformance.md`'s table) -- the
  scope of a prospective `verification-security-isolation` node, which does not exist
  in the corpus at the recorded revision (checked, not assumed absent -- see the
  evidence ledger).
- **NIP-98/API-token community-stamp verification and NIP-42 `AUTH`-tag cross-host
  forgery** -- the scope of a prospective `verification-formal-multi-tenant-auth` node,
  which also does not exist yet. `docs/multi-tenant-conformance.md`'s own "API tokens
  and NIP-98 replay" row and `crates/buzz-test-client/tests/nip42_host_binding_live.rs`
  are that obligation's territory, and this node's own verifying test explicitly
  distinguishes itself from those siblings in its doc-comment (see the evidence
  ledger).
- **The formal-methods and runtime-trace verification layer** for this same seam --
  `docs/spec/MultiTenantRelay.tla`'s `Inv_HostBindingFence`/`Inv_ResolutionFence` and
  `crates/buzz-relay/src/conformance/mod.rs`'s trace harness, both named by
  `architecture-principles-fail-closed-boundaries` (referenced below). This node is
  scoped to the automated Rust test layer, per the `test-contract` template it is
  built from; it does not restate the formal model.
- **The architecture-level statement of the invariant itself.**
  `architecture-principles-host-selects-community` already states this same "row zero"
  invariant as a system property, with its own scope, enforcement points, and
  verification section. This node is narrower and complementary: it is the
  schema-mandated `verification`-typed test-contract shape for the same obligation --
  one obligation, its named verifying test(s), and their current enforcement status --
  not a second statement of the invariant.

## Obligation

> An unknown or unmapped request host fails closed with a generic rejection and never
> falls through to a default tenant; a client-supplied community-like signal (for
> example, an event's `#h` channel tag) can never override the host-derived community --
> a request whose supplied signal disagrees with `resolve_host(connection.host)` is
> rejected, not honored.

## Verifying test(s)

Two layers, at different granularity, both exercising this same obligation:

- **`crates/buzz-relay/src/tenant.rs`, `mod tests`** -- unit-level, in-process, no
  live relay:
  - `unmapped_host_fails_closed` -- a `bind_community` call against a host absent
    from the resolver's map returns `BindError::UnmappedHost`.
  - `lookup_error_fails_closed_not_default_tenant` -- a resolver `Err` also returns a
    `BindError` (`Lookup`), never a `TenantContext`.
  - `redteam_attack2::empty_raw_host_fails_closed_even_if_db_has_empty_host_row` and
    `::whitespace_only_raw_host_fails_closed_even_if_db_has_empty_host_row` -- an
    empty or whitespace-only raw host fails closed *before* the resolver runs, even
    when the resolver's map carries a misconfigured `""`-keyed row.
  - `redteam_attack2::non_empty_unmapped_host_still_fails_closed_after_fix` -- negative
    control, so the empty-host fix cannot over-narrow to only the empty case.
- **`crates/buzz-test-client/tests/conformance_multitenant.rs`, `mod
  row_zero_host_binding`** -- wire-level, end-to-end, against a live two-host relay:
  - `unmapped_host_fails_closed_generically` -- covers the fail-closed half of the
    obligation on the wire: HTTP 404 on the unmapped host vs. non-404 on a mapped
    host, a generic (non-host-echoing) rejection body, and a rejected raw WebSocket
    handshake.
  - `client_supplied_community_cannot_override_host` -- covers the non-overridability
    half: an A-bound connection cannot post into a channel that exists only in
    community B by supplying that channel's UUID as a `#h` tag; the rejection is
    pinned to the exact channel-scope reason string so the assertion cannot be
    satisfied by an unrelated, earlier gate.

## How to run it

Unit layer, no infrastructure required:

```bash
cargo test -p buzz-relay --lib tenant::tests
```

Wire layer, requires a single running relay process reachable under two distinct
`Host` values, backed by the same Postgres and Redis (per the test file's own
doc-comment):

```bash
RELAY_URL_A=http://a.localhost:3000 \
RELAY_URL_B=http://b.localhost:3000 \
cargo test -p buzz-test-client --test conformance_multitenant -- --ignored
```

(`RELAY_URL_UNKNOWN` defaults to `http://unknown.localhost:3000` if unset; `*.localhost`
resolves to `127.0.0.1`, so this addresses the same relay process under a `Host` no
community is bound to.)

## Current enforcement status

**Gated -- and the honest picture is more specific than that single word.**

The wire-level half of the obligation
(`conformance_multitenant.rs::row_zero_host_binding`) is `#[ignore]`-gated behind a
live two-host relay deployment and must be selected explicitly with `--ignored`; that
is a conventional, named gate.

The unit-level half (`tenant.rs::tests`, including `unmapped_host_fails_closed`,
`lookup_error_fails_closed_not_default_tenant`, and `redteam_attack2`) carries **no**
`#[ignore]` and would pass under a plain `cargo test -p buzz-relay --lib tenant::tests`
-- but at the recorded revision **no automated CI job or documented `just` recipe
actually selects it**. This was checked, not assumed: `Justfile`'s `test-unit`
recipe's only `-p buzz-relay --lib` invocation filters to
`test(/^api::admin::/)`, and its own adjacent comments state plainly that "nothing in
CI runs `cargo test --workspace`" and that `buzz-relay --lib` coverage must be
enumerated test-by-test; `.github/workflows/ci.yml`'s Backend Integration job builds a
`-p buzz-relay --lib` nextest archive but every step that consumes it filters to other,
specific, unrelated test names; and `scripts/run-tests.sh` never invokes `-p
buzz-relay` at all. A repository-wide grep for `tenant::` across every CI workflow,
the `Justfile`, and `scripts/*.sh` returns zero matches.

So both verifying tests exist, are not stubbed, and would pass if invoked -- but
**neither currently runs automatically anywhere in this repository's CI at the recorded
revision.** The wire layer is skipped by explicit, named design (`#[ignore]`, pending
CI infrastructure this obligation's own tests already anticipate). The unit layer's
absence from any test-selection surface reads as an enumeration gap rather than an
intentional gate -- the tests were written and are ready to run, but nothing invokes
them. This asymmetry is itself the load-bearing fact this section exists to report,
and it is not softened here.

## Limits

**What `unmapped_host_fails_closed_generically` proves, and no further:** the
non-`nostr+json` HTTP door and the raw WebSocket-upgrade door, for exactly one
unmapped host and one mapped host, on one live relay process. It does not exercise
every in-scope surface `architecture-principles-host-selects-community` lists (media,
git, search, workflow, pub/sub, and more) -- those, if covered at all, are each their
own module in `conformance_multitenant.rs` (`media_blossom`, `git_hosting`,
`search_fts`, `workflows`, `pubsub_presence_typing`), not this test.

**What `client_supplied_community_cannot_override_host` proves, and no further:**
only the `#h` channel-tag override vector, on a single kind:9 message, against a
single open channel. It does not exercise the NIP-98/API-token community-stamp
override vector or the NIP-42 `AUTH`-tag cross-host forgery vector -- named
explicitly, in the test's own doc-comment, as the territory of
`api_tokens_nip98_replay` and `nip42_host_binding_live.rs` respectively.

**What the unit tests prove, and no further:** `bind_community`'s own fail-closed
branching against an in-memory fake `HostResolver`. They do not exercise the real
`Db`-backed `HostResolver` implementation, the router's HTTP wiring around
`bind_community`, or the WebSocket-upgrade call site -- that wiring is exercised only
by the wire layer above.

**Neither layer was executed by this node's author at the recorded revision.** The
enforcement-status section above is derived from reading the `#[ignore]` attributes,
the test bodies, and the CI/`Justfile`/script wiring -- not from a live `cargo test`
run. A future update to this node should record an actual run rather than repeat this
static analysis, per `launchpad/docs/corpus/standards/evidence.md`'s point that "this
test currently passes" needs executable evidence with a short shelf life.

## Scope and omissions

**This node covers** the row-zero host-binding-and-non-overridability obligation, its
two named verifying test layers, how to run each, their honest current enforcement
status (including the CI-selection gap discovered while authoring this node), and what
each test does and does not prove.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Per-surface `community_id` scoping across channels, search, pub/sub, media, git, workflows, and audit | A prospective `verification-security-isolation` node -- checked and confirmed absent from `origin/launchpad`'s corpus at the recorded revision |
| NIP-98/API-token community-stamp verification and NIP-42 `AUTH`-tag cross-host forgery rejection | A prospective `verification-formal-multi-tenant-auth` node -- also checked and confirmed absent |
| The formal TLA+ model (`Inv_HostBindingFence`/`Inv_ResolutionFence`) and the runtime conformance trace harness for this same seam | `docs/spec/MultiTenantRelay.tla`, `crates/buzz-relay/src/conformance/mod.rs`, cited (not restated) by `architecture-principles-fail-closed-boundaries` |
| The architecture-level statement of the row-zero invariant itself, its full enforcement-point inventory, and the empty-host red-team narrative | `architecture-principles-host-selects-community` (referenced above) |
| The NIP-11 fail-*open* exception (the relay-info document is deliberately served before host binding) | `architecture-principles-host-selects-community`; this node's obligation applies to admitting/scoping surfaces, not to that deliberately host-agnostic document |
| Why nothing in this repository's CI currently selects `tenant::tests` -- whether that is an oversight or a deliberate deferral | Not established here; recorded as a fact under *Current enforcement status*, not diagnosed further |

**No second distinct obligation was folded into this node.** The fail-closed clause
and the non-overridability clause are treated as one obligation, following the same
precedent `docs/multi-tenant-conformance.md`'s own "Row zero" row and
`architecture-principles-host-selects-community`'s single stated invariant already
set, rather than re-splitting what two existing sources already treat as one property.
