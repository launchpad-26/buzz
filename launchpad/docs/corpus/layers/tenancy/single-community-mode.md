---
id: layers-tenancy-single-community-mode
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "docs/multi-tenant-conformance.md states the compatibility rule for the multi-tenant rewrite as: today's Buzz is one implicit community selected by its relay URL, and multi-tenant Buzz makes that selector explicit at the backend boundary while preserving existing wire behavior 'when N = 1'."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "docs/multi-tenant-conformance.md's row-zero section states explicitly: 'The single-community deployment is the degenerate case: one configured host resolves to the one default community, so existing clients observe the same behavior.'"
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "bind_community, the single row-zero host-resolution entry point in crates/buzz-relay/src/tenant.rs, contains no branch, count, or special case keyed on how many rows exist in the communities table; it normalizes the host, looks it up through a HostResolver, and fails closed on an unmapped host or a lookup error, identically whether one or many communities are configured."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "Db::ensure_configured_community (crates/buzz-db/src/lib.rs) is doc-commented as 'the startup/config seeding path for N=1 deployments': it upserts a communities row for a given normalized host, is idempotent (ON CONFLICT DO UPDATE ... RETURNING id, host, (xmax = 0) AS created), and errors if the host is permanently tombstoned rather than silently reusing a deleted community."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-relay/src/main.rs derives the deployment's own community host from config.relay_url via tenant::relay_url_authority (the same normalization live request resolution uses), calls db.ensure_configured_community(&host) on every boot before any membership backfill or owner bootstrap, and treats an empty derivable host as a hard startup error only when BUZZ_REQUIRE_RELAY_MEMBERSHIP is true; a non-empty host always produces exactly one community row per distinct configured host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "RELAY_URL defaults to 'ws://localhost:3000' when unset, per crates/buzz-relay/src/config.rs's Config::from_env; this default host is what a fresh boot with no other configuration auto-provisions as the deployment's one community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/handlers/community_provisioning.rs's module documentation states that POST /operator/communities is gated by the deployment-level RELAY_OPERATOR_PUBKEYS allowlist and that 'an empty allowlist (the default) disables provisioning entirely'; crates/buzz-relay/src/config.rs's own test asserts relay_operator_pubkeys defaults empty with the comment 'provisioning disabled'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "require_relay_membership defaults to false, asserted directly by a config test in crates/buzz-relay/src/config.rs; a fresh single-community deployment therefore does not require BUZZ_RELAY_PRIVATE_KEY or RELAY_OWNER_PUBKEY to start, though main.rs still runs the same ensure_configured_community bootstrap unconditionally."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs's module doc and its n1_parity module state that N=1 parity -- existing clients observing byte-identical behavior with one configured host mapping to one default community -- is asserted by the pre-existing e2e_relay/e2e_media/... suites staying green against the new relay, not by a new test written for that module; the file frames the pre-rewrite single-community relay as the 'wire-parity oracle' for the rewrite."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "Buzz's schema before migration 1321 had no communities table and no community_id column on any table -- it was structurally single-community-only, not merely single-community by configuration -- per scripts/cutover/README.md and the guard block in scripts/cutover/1321_backfill_default_community.sql, which refuses to run on a database that already has a communities table or any community_id column."
    entry_class: FACT
    evidence:
      - "scripts/cutover/README.md"
      - "scripts/cutover/1321_backfill_default_community.sql"
  - statement: "scripts/cutover/1321_backfill_default_community.sql's one-off cutover creates exactly one default community from an operator-supplied :host, stamps every pre-1321 row with that community_id, and its README instructs booting the post-cutover relay with BUZZ_AUTO_MIGRATE=false since the idempotent boot-time ensure_configured_community/allowlist-to-relay_members backfill then finds that community and no-ops."
    entry_class: FACT
    evidence:
      - "scripts/cutover/README.md"
      - "scripts/cutover/1321_backfill_default_community.sql"
  - statement: "scripts/seed-local-community.sh seeds a communities row for the local-dev RELAY_URL authority so that row-zero host binding does not fail-closed on loopback development traffic, and its own comments warn that seeding multiple loopback host aliases (localhost, 127.0.0.1) creates separate, non-aliased communities rather than one community reachable by several names."
    entry_class: FACT
    evidence:
      - "scripts/seed-local-community.sh"
  - statement: "Because bind_community carries no code path conditioned on community count (per the tenant.rs FACT above) and ensure_configured_community is the same idempotent upsert run on every boot regardless of how many hosts a deployment ends up configuring, 'single-community mode' names a deployment-time state -- exactly one row in communities, reached by never calling the operator-gated provisioning endpoint -- rather than a distinct relay build, feature flag, or code branch."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
      - "crates/buzz-db/src/lib.rs"
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs"
    confidence: 0.85
  - statement: "Issue #1191's Definition of Done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals distinguishing it from what it must not be confused with, link the concept to related concepts/implementation/verification, and use examples only to clarify rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1191 definition of done"
relationships:
  - type: references
    target: architecture-deployment-single-relay
  - type: references
    target: architecture-principles-host-selects-community
---

# Single-community mode

**Single-community mode is the state of a Buzz relay deployment in which exactly
one row exists in the `communities` table, so every request host that resolves
successfully resolves to that one community.** It is not a separate relay build,
a feature flag, or a distinct code path — it is the `N = 1` case of the same
host-resolution model multi-community deployments use, reached simply by never
provisioning a second community.

## Boundary: what this is not

**Not a deployment topology.** [`architecture-deployment-single-relay`](../../architecture/deployment/single-relay.md)
documents the *infrastructure* shape most single-community deployments run on
today — one relay process, one host, the Compose bundle under `deploy/compose/`.
That node is about where the process runs. This node is about what the relay's
*tenancy behavior* does — or, more precisely, does not have to do specially —
when it is serving exactly one community. The two are related but independent:
a multi-replica Kubernetes deployment could still serve exactly one community
(single-community mode, multi-node topology), and nothing in `bind_community`
couples the two.

**Not a special case in the host-resolution code.** [`architecture-principles-host-selects-community`](../../architecture/principles/host-selects-community.md)
documents the row-zero invariant (`req.community = resolve_host(connection.host)`)
that governs every deployment regardless of community count, and already states
the core fact this node expands on: "the single-community deployment is the
degenerate case of the same rule." This node does not restate that invariant's
enforcement points or verification — it links to that node for those — and
instead focuses on what is specific to the `N = 1` state: how a deployment
arrives there, what stays disabled while it stays there, and what changed
historically to make it a state rather than the *only* possible state.

**Not a permanent ceiling.** A single-community deployment can become a
multi-community one at any time an operator explicitly provisions a second
community; nothing about single-community mode locks a deployment out of that.
Conversely, nothing auto-grows a single-community deployment into a
multi-community one — provisioning is opt-in, off by default, and gated above
the tenant boundary (see *How single-community mode is reached*, below).

## How single-community mode is reached

A fresh Buzz relay boot always ends up in single-community mode unless an
operator deliberately provisions a second community:

1. **Auto-provisioning at boot, every boot.** `crates/buzz-relay/src/main.rs`
   derives a host from `config.relay_url` (`RELAY_URL`, defaulting to
   `ws://localhost:3000`) using the same normalization live request resolution
   uses, then calls `Db::ensure_configured_community` with that host. That
   function is an idempotent upsert — `INSERT ... ON CONFLICT (lower(host)) DO
   UPDATE ... RETURNING id, host, (xmax = 0) AS created` — documented directly
   in its own doc comment as "the startup/config seeding path for N=1
   deployments." It runs unconditionally on every startup, not only on first
   boot, and it errors rather than silently reusing a host whose community was
   permanently tombstoned.
2. **Nothing grows the count without an explicit operator action.** The only
   way a deployment gains a second community is `POST /operator/communities`,
   which is NIP-98-authenticated and gated by the `RELAY_OPERATOR_PUBKEYS`
   allowlist. That allowlist defaults empty, and the handler module's own
   documentation states plainly that an empty allowlist "disables provisioning
   entirely." A deployment that never sets `RELAY_OPERATOR_PUBKEYS` therefore
   cannot leave single-community mode through this endpoint, by construction,
   not by convention.
3. **Membership enforcement is independent of community count.**
   `require_relay_membership` (`BUZZ_REQUIRE_RELAY_MEMBERSHIP`) defaults to
   `false`. A single-community deployment can run open (no owner key required
   to boot) or closed (membership-enforced, requiring `RELAY_OWNER_PUBKEY` and
   `BUZZ_RELAY_PRIVATE_KEY`) — both are orthogonal to whether the deployment
   has one community or many; this node's `N = 1` state says nothing about
   which membership posture is chosen.

## What does not change because a deployment is single-community

`bind_community` (`crates/buzz-relay/src/tenant.rs`), the row-zero
host-resolution seam, contains no branch, counter, or special case conditioned
on how many rows `communities` holds. It normalizes the raw host, resolves it
through a `HostResolver`, and fails closed on an unmapped host or a lookup
error — the exact same function single- and multi-community deployments call.
This is why `docs/multi-tenant-conformance.md` frames `N = 1` compatibility as
a *parity obligation on the rewrite*, not a distinct implementation: the
document's compatibility rule states that multi-tenant Buzz "makes that
selector explicit at the backend boundary while preserving the Nostr wire
format, existing REST paths, channel UUIDs, event shapes, media URLs, git Smart
HTTP behavior, workflow behavior, and CLI/Desktop/MCP expectations when `N =
1`," and its own migration-gate 5 requires "N=1 conformance tests [to] prove
existing clients do not need new tags, paths, event fields, CLI flags, or
protocol messages." `crates/buzz-test-client/tests/conformance_multitenant.rs`
implements that gate not with new tests but by naming the pre-existing
`e2e_relay`/`e2e_media`/… suites, run against the new relay, as the parity
oracle: "the current single-community relay is the wire-parity *oracle*," and
its `n1_parity` module states the obligation as those suites "staying green,
unchanged."

## Historical note: before single-community was a choice

Before migration 1321, Buzz's schema had no `communities` table and no
`community_id` column on any table at all — every deployment was
single-community *structurally*, not by configuration. `scripts/cutover/README.md`
and the guard block at the top of
`scripts/cutover/1321_backfill_default_community.sql` make this precondition
explicit: the cutover script refuses to run on a database that already has a
`communities` table or any `community_id` column, because its entire job is
carrying a pre-1321, necessarily-single-community deployment across the
schema rewrite. It renames every pre-1321 table into a `legacy` schema,
rebuilds the current schema from `migrations/0001_initial_schema.sql`
verbatim, creates exactly one default community from an operator-supplied
host, and copies every row forward stamped with that one `community_id`. This
is a one-time operator-run script, not startup behavior — `migrations/0001`
alone is what a fresh deployment's embedded `sqlx` migrator applies — and its
own README instructs booting the post-cutover relay with
`BUZZ_AUTO_MIGRATE=false`, since the ordinary boot-time
`ensure_configured_community` path described above then finds the
already-created community and no-ops.

## Local development example

`scripts/seed-local-community.sh` is a concrete instance of reaching
single-community mode deliberately: it seeds one `communities` row for the
local-dev `RELAY_URL` authority so row-zero host binding does not fail-closed
on loopback traffic. Its own comments record a lesson worth carrying into any
other single-community setup: seeding multiple loopback aliases (`localhost`,
`127.0.0.1`) does not create one community reachable by several names — each
host row is a *separate* community with its own id, so aliasing would silently
create several empty parallel single-community deployments rather than one.
The script therefore seeds only the primary authority, converting what would
otherwise be a silent split into the same loud fail-closed rejection
`bind_community` gives any other unmapped host. This example illustrates the
general mechanism above; it introduces no concept beyond it.

## Scope and omissions

**This node covers** what single-community mode is (the `N = 1` state of the
tenancy model), how a deployment is auto-provisioned into it at boot, why the
host-resolution code itself has no special case for it, what stays off by
default while a deployment remains in it (multi-community provisioning), and
the historical schema state that preceded it having been a choice at all.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The row-zero host-binding invariant's enforcement points, failure behavior, and verification in full | `architecture-principles-host-selects-community` |
| The Compose/Kubernetes deployment topology a single-community relay typically runs on | `architecture-deployment-single-relay` |
| Multi-community mode: how a deployment serves more than one community, and the full per-surface tenant-scoping table | `docs/multi-tenant-conformance.md`; the corresponding `layers/tenancy/multi-community-mode.md` node (issue #1190) does not exist in the corpus at this node's recorded revision, so no `relationships` edge to it is declared here |
| Community archival and deletion state machines, which apply identically regardless of how many communities a deployment has | `migrations/0016_community_archival.sql`, `migrations/0029_community_deletion.sql` |
| Whether any deployment in this cohort's own environments (`launchpad/ENVIRONMENTS.md`) is presently running in single- or multi-community mode | `launchpad/ENVIRONMENTS.md` — not re-checked for this node |

**Expected but not verified when this node was written:** whether any
integration or e2e suite explicitly asserts that a fresh boot with no prior
`communities` row ends up with exactly one row afterward (as opposed to this
being established by reading `ensure_configured_community` and `main.rs`
directly) was not located as a dedicated test; the `n1_parity` module in
`crates/buzz-test-client/tests/conformance_multitenant.rs` documents the
broader parity gate but is not itself a test of the provisioning count.
