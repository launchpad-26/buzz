---
id: layers-tenancy-cross-community-isolation
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The formal specification docs/multi-tenant-relay.md states tenant isolation as non-interference: for any two executions equal on community B's inputs and initial B-visible state, B's observable outputs are equal regardless of community-A-only actions, encoded as a label-flow invariant -- every state element carries the community label it originated from, and the safety invariant is that no high-labeled value ever flows into a low-labeled observation."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md:143-155"
  - statement: "The TLA+ model docs/spec/MultiTenantRelay.tla defines Inv_NonInterference as 'no observation scoped to community C may be influenced by a row, projection, audit head, auth decision, write-conflict source, or error source labeled outside C', formalized as `\\A o \\in observations : o.labels \\subseteq {o.community}`, and derives Inv_ReadConfinement from it as 'every ResultRows observation's rows all carry the observing community's own label', formalized as `\\A o \\in observations : o.kind = \"ResultRows\" => \\A r \\in o.rows : r.community = o.community`."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:981-1001"
  - statement: "docs/multi-tenant-relay.md enumerates the relay's full client-observable interface this invariant must hold over -- WebSocket EVENT/EOSE/OK/NOTICE/CLOSED/AUTH/COUNT frames, the REST body and status-code/error envelope, the audit-chain read/verify surface, and the unauthenticated NIP-11 relay-info document -- and states that any observation outside that enumerated set is either the declared-out-of-scope C1 physical-timing class or a model violation, with no third category."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md:229-290"
  - statement: "The same document enumerates four in-scope logical channels (C2) that are not simple row-return predicates and must each be closed by a named mechanism: the event-id existence oracle from INSERT...ON CONFLICT DO NOTHING (closed by a composite community_id-leading uniqueness constraint), the constraint-violation error surface (closed by a fixed sanitized error alphabet), the projection-rebuild path (closed by the invariant that rebuilds never serve rows to a tenant-scoped connection), and the unauthenticated NIP-11 document (closed by a typed-input code fence limiting its builder to relay-static configuration)."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md:167-214"
  - statement: "crates/buzz-relay/src/nip11.rs's RelayInfo::build takes only relay_self, icon, advertise_nip43, max_message_length and pairing_relay_url -- no database pool and no tenant context -- and a comment directly above nip11_facts names this the 'Multi-tenant conformance static-input fence (surface row \"NIP-11 relay info and relay self\")', confirming in code the typed-input-fence closure the specification claims for the C2.4 channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:141-147"
      - "crates/buzz-relay/src/nip11.rs:306-313"
  - statement: "migrations/0001_initial_schema.sql leads every tenant-scoped table's primary key or unique index with community_id: channels' PRIMARY KEY (community_id, id), channel_members' PRIMARY KEY (community_id, channel_id, pubkey), users' PRIMARY KEY (community_id, pubkey), events' PRIMARY KEY (community_id, created_at, id), and event_mentions' PRIMARY KEY (community_id, pubkey_hex, event_id) -- the migration's own header states this is deliberate: 'No UNIQUE / PRIMARY KEY / FK on a scoped table is observable across communities: each leads with community_id'."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:17-19"
      - "migrations/0001_initial_schema.sql:97"
      - "migrations/0001_initial_schema.sql:142"
      - "migrations/0001_initial_schema.sql:170"
      - "migrations/0001_initial_schema.sql:234"
      - "migrations/0001_initial_schema.sql:293"
  - statement: "crates/buzz-db/src/event.rs's EventQuery struct cannot be built from its only constructor, for_community, without supplying a CommunityId; the field itself (community_id: pub CommunityId) is nonetheless a public field on the struct, so a struct-literal or struct-update-syntax construction elsewhere in the crate could still set it to an arbitrary CommunityId value without going through for_community."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:29-31"
      - "crates/buzz-db/src/event.rs:113-136"
  - statement: "crates/buzz-db/src/channel.rs's get_accessible_channel_ids takes an explicit community_id: CommunityId parameter and scopes both halves of its UNION query with WHERE cm.community_id = $1 and WHERE community_id = $1 respectively; every call site found in the repository (crates/buzz-relay/src/handlers/req.rs:114, handlers/count.rs:85, api/bridge.rs:1011 and :1488, api/workflows.rs:96, via the cached wrapper in crates/buzz-relay/src/state.rs:1232) passes tenant.community() or conn.tenant.community(), the resolved TenantContext's own community, not a value derived from client-supplied data."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:754-774"
      - "crates/buzz-relay/src/handlers/req.rs:114"
      - "crates/buzz-relay/src/handlers/count.rs:85"
      - "crates/buzz-relay/src/api/bridge.rs:1011"
      - "crates/buzz-relay/src/api/bridge.rs:1488"
      - "crates/buzz-relay/src/api/workflows.rs:96"
      - "crates/buzz-relay/src/state.rs:1232-1245"
  - statement: "buzz-core's tenant.rs module doc states the whole multi-tenant safety story is a 'lint-and-review fence, not a compiler fence': TenantContext::resolved and CommunityId::from_uuid are both pub, so while the type removes the accidental path (deserializing a client-chosen community), a determined or mistaken caller elsewhere could still construct a CommunityId or TenantContext outside host resolution, and only review closes that deliberate path."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs:1-25"
  - statement: "A repository-wide search for Postgres native row-level security ('CREATE POLICY', 'ENABLE ROW LEVEL SECURITY', 'FORCE ROW LEVEL SECURITY') across every file under migrations/ returned zero matches at this revision, even though docs/multi-tenant-relay.md's Axioms section states five obligations (A-RLS-1 through A-RLS-5, including 'every queryable tenant-bearing table has RLS enabled with a restrictive policy' and 'uniqueness and foreign-key constraints include community_id') under the heading 'Row-level security (the fail-closed backstop)', names this the precondition for Theorem I4 ('a missed application predicate fail[s] closed rather than leak[s]'), and states in its Conformance section that A-RLS-1..5 are 'admitted by a startup/CI assertion suite' per deployment, with a failing assertion rejecting the deployment; no script or workflow matching that description was found under scripts/ or .github/workflows/ either."
    entry_class: FACT
    evidence:
      - "grep(pattern='CREATE POLICY|ENABLE ROW LEVEL SECURITY|FORCE ROW LEVEL SECURITY', scope='migrations/**/*.sql') -> zero matches, verified against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "docs/multi-tenant-relay.md:344-376"
      - "docs/multi-tenant-relay.md:651-660"
  - statement: "docs/multi-tenant-relay.md's own Implementation Correspondence section carries at least one bullet -- 'Today there is no community layer; channel_id is the only locality' -- that git blame attributes to the document's original commit 2ecdcce7bd (2026-06-26), predating the comprehensive rewrite in commit 14fba21e5 that introduced crates/buzz-core/src/tenant.rs's CommunityId and TenantContext; that bullet is stale relative to the current codebase, which does carry a community layer, so this node verifies enforcement directly against current code rather than trusting that section of the specification wholesale."
    entry_class: FACT
    evidence:
      - "git_blame(file='docs/multi-tenant-relay.md', lines='883-885') -> commit 2ecdcce7bd, 2026-06-26"
      - "git_log(path='docs/multi-tenant-relay.md') -> commits 2ecdcce7bd, 14fba21e5, 54638ff4b"
      - "crates/buzz-core/src/tenant.rs"
  - statement: "crates/buzz-conformance/src/transitions.rs implements Inv_NonInterference's row-label check as check_row_labels, which fails a trace with TransitionError::NonInterference the moment any row in a ResultRows/WriteResult observation carries a community label other than the model's resolved_community for that step; crates/buzz-conformance/tests/replay_fixtures.rs exercises this against a committed fixture, bad_foreign_row_leak.jsonl, in an always-run (not #[ignore]-gated) unit test named foreign_row_leak_is_non_interference."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/transitions.rs:285-311"
      - "crates/buzz-conformance/tests/replay_fixtures.rs:154"
      - "crates/buzz-conformance/tests/replay_fixtures.rs:281"
      - "crates/buzz-conformance/tests/fixtures/bad_foreign_row_leak.jsonl"
  - statement: "crates/buzz-relay/src/conformance/mod.rs's own module doc comment, under 'Wire points', states the ingest.rs write path (AuthCheck, WriteInsert/WriteInsertGlobal/WriteDuplicate, SanitizedError) is wired to emit runtime trace steps, while the read path is not: 'req.rs / event.rs: (held back as additive patch for Eva to apply onto Max's req.rs writes...)'; at this revision the runtime conformance checker is therefore exercised against constructed fixture traces (including the foreign-row-leak fixture above) but not yet fed live read-path traces from the running relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs:1-29"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs is an A/B isolation suite that runs two host-to-community mappings against one live relay deployment sharing one database and Redis instance; every test in the file carries #[ignore] and requires RELAY_URL_A/RELAY_URL_B/RELAY_URL_UNKNOWN environment variables plus `cargo test -p buzz-test-client --test conformance_multitenant -- --ignored`; this node was authored without standing up that two-host deployment, so this suite's current pass/fail status against this revision was not executed or observed while writing this node -- the same gap the sibling architecture-principles-community-is-security-boundary node already recorded for the same suite."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1-33"
  - statement: "Because every scoped storage function inspected above (EventQuery::for_community, get_accessible_channel_ids, and the composite primary keys in migrations/0001_initial_schema.sql) requires or is keyed by a CommunityId sourced from the resolved TenantContext at every call site found, and because CommunityId cannot be parsed from client-supplied request data anywhere in the codebase, defeating cross-community read confinement today would require either a future call site that skips the community-scoped query path entirely, or a bug/deliberate misuse constructing a wrong-but-valid CommunityId -- the second of which the type system does not prevent, per tenant.rs's own 'lint-and-review, not compiler' admission."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/event.rs:113-136"
      - "crates/buzz-db/src/channel.rs:754-774"
      - "migrations/0001_initial_schema.sql:17-19"
      - "crates/buzz-core/src/tenant.rs:1-25"
    confidence: 0.6
  - statement: "Issue #1188's Definition of Done requires this node to state the invariant as one unambiguous property using MUST/MUST NOT only where normative, explain scope and the states/operations it applies to, name enforcement points and observable failure behavior, and link at least one verification/conformance mechanism or explicitly record that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1188 definition of done"
relationships:
  - type: depends-on
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: references
    target: architecture-deployment-multi-community
  - type: implements
    target: corpus-template-invariant
---

# Cross-community isolation: invariant

**No connection resolved to community B may observe, anywhere in the relay's
client-visible interface, a value that originated from another community's
state.** Concretely: for every WebSocket `EVENT`/`OK`/`COUNT` frame, REST
response body or status code, and audit-chain entry a B-scoped connection
receives, every row, count, and error it is built from carries community
label `B` and no other. This is the property `docs/multi-tenant-relay.md`
proves as non-interference and `docs/spec/MultiTenantRelay.tla` mechanizes as
`Inv_NonInterference` (with `Inv_ReadConfinement` as its read-specific
corollary).

This node documents **confinement of already-resolved tenant data** — it is
deliberately narrower than "which community does this request belong to,"
which `architecture-principles-host-selects-community` already covers in
depth (the row-zero `bind_community` selection mechanism) and which
`architecture-principles-community-is-security-boundary` covers from the
client-cannot-override angle. This node picks up *after* that selection has
correctly happened and asks: given a connection genuinely bound to community
B, can any part of what it observes still leak from community A? It
`depends-on` the host-selection node because the whole claim below is
meaningless unless "community B" is itself correctly and immutably resolved
first.

## Scope

**Applies to every server-resolved read or write already bound to a
community** — i.e. every operation downstream of `bind_community`/
`bind_deployment_community` (see the depended-on node for that binding
step itself), across:

- **Row-return channels.** Event queries (`EventQuery`), channel listings
  (`get_accessible_channel_ids`), and any other `SELECT` that returns rows
  to a tenant-scoped connection.
- **The event-id existence oracle.** `INSERT ... ON CONFLICT DO NOTHING` on
  a content-hash id: whether a community-B write reports a conflict must be
  a function of community B's own state alone, never of whether community A
  already holds that id.
- **The error surface.** Any error message reaching a tenant-scoped
  connection must not leak a constraint name, a conflicting tuple, or any
  other fragment naming another community's data.
- **The audit chain.** Reading or verifying community B's audit chain must
  never depend on, or reveal facts about, another community's chain.
- **Numeric channels.** A `COUNT` (NIP-45) or `EOSE` cardinality returned to
  a B-scoped connection must be the count of B-labeled rows matching the
  filter, never inflated or deflated by another community's matching rows.

**Explicitly out of scope, by construction, not by omission.** The
unauthenticated NIP-11 relay-info document (`/`) carries no tenant label at
all — no connection has bound to a community when it is served — so this
invariant does not reach it; `RelayInfo::build`'s signature (relay-static
configuration only, no database handle, no tenant context) is the code-level
fence that keeps it that way, and a future field that requires a `&PgPool`
argument would need review precisely because this invariant's labeling
discipline would not catch it automatically.

**Applies whether the query narrows further or not.** A client-supplied `#h`
tag or NIP-98/token community stamp may narrow *which channel inside*
community B is meant (see `architecture-principles-community-is-security-
boundary`), but every row that narrowing can possibly surface is already
constrained to have `community_id = B` — this node's claim is that the outer
constraint is never bypassable, independent of whatever narrowing a filter
adds on top.

## Enforcement today

**The weakest true tier, named honestly: predicate-enforced at the database
layer, backed by convention-and-review rather than the type system, and
partially test-enforced at the conformance-checker level.**

- **Predicate-enforced (DB constraints).** Every tenant-scoped table's
  primary key or unique index leads with `community_id`
  (`migrations/0001_initial_schema.sql`) — `events`, `channels`,
  `channel_members`, `users`, and `event_mentions` all key on
  `(community_id, ...)`. This is the mechanism that actually closes the
  event-id existence-oracle channel the formal specification names: a
  community-B write at an id community A already holds gets a *fresh*
  composite key, not a conflict.
- **Construction-requires-community, not compiler-enforced.**
  `EventQuery::for_community` and `get_accessible_channel_ids` both require
  a `CommunityId` argument to build a query at all, and every call site
  found passes the resolved `TenantContext`'s own community. But
  `EventQuery.community_id` is a `pub` field and `CommunityId::from_uuid`
  is a `pub` constructor — per `crates/buzz-core/src/tenant.rs`'s own
  admission, this is "a lint-and-review fence, not a compiler fence." A
  future call site that constructs an `EventQuery` by struct-update syntax
  with the wrong community, or that mints a `CommunityId` from an
  attacker-influenced UUID, would not be caught by the type system.
- **RLS is not the backstop here, despite the formal model's axiom.**
  `docs/multi-tenant-relay.md`'s Axioms section treats Postgres row-level
  security as the "fail-closed backstop" its I4 theorem depends on,
  admitted per-deployment by a startup/CI assertion suite. No `CREATE
  POLICY`, `ENABLE ROW LEVEL SECURITY`, or matching startup/CI assertion
  exists anywhere in this repository's `migrations/`, `scripts/`, or
  `.github/workflows/` at this revision. The formal proof's precondition
  for I4 is therefore not admitted by the shipped schema — the composite-key
  discipline above is the closure that actually exists for the
  existence-oracle channel, but a query that omitted its `WHERE
  community_id = $1` predicate entirely (rather than colliding on the
  primary key) would not be caught by any database-level backstop, only by
  review.
- **Test-enforced, but only against constructed traces so far.**
  `crates/buzz-conformance`'s `check_row_labels` implements
  `Inv_NonInterference`'s row-label check directly, and an always-run unit
  test (`foreign_row_leak_is_non_interference`) proves the checker itself
  catches a foreign-community row when one appears in a trace. The gap:
  `crates/buzz-relay/src/conformance/mod.rs`'s own doc comment states the
  live relay's read path (`req.rs`/`event.rs`) is not yet wired to emit
  those traces from real traffic — only the write/ingest path is. The
  checker is proven correct against fixtures; it is not yet proven to be
  watching the live read path.

## Consequence of violation

A violation is a **cross-tenant data leak**: a connection bound to community
B receiving a row, count, or error fragment that originated in community A —
private channel content, DM participants, or another community's audit
history becoming visible where they must not be. Concretely, at the
mechanisms named above:

- A query that used the wrong `CommunityId` (construction-requires-community
  bypassed) would return community A's rows to a B-scoped caller; the
  runtime conformance checker's `Inv_NonInterference` check would flag it
  as `TransitionError::NonInterference` *if* the code path were wired to
  emit a trace — which, per the enforcement gap above, the read path
  currently is not.
- A migration that dropped or narrowed a `community_id`-leading composite
  key would reopen the event-id existence oracle: a community-B writer
  could learn that community A already holds a given event id purely from
  whether their own insert reports a conflict.

## Boundary

This node does not describe:

- **The host-to-community selection mechanism itself** (`bind_community`,
  host normalization, the fail-closed rejection of an unmapped host) — see
  `architecture-principles-host-selects-community`, which this node
  `depends-on` rather than restates.
- **Why client-supplied signals cannot override the resolved community** —
  see `architecture-principles-community-is-security-boundary`, referenced
  above.
- **Authorization soundness** (S1–S8 in `docs/multi-tenant-relay.md`): token
  minting integrity, signing-key non-confusion, and NIP-43 admission
  confinement are a related but distinct family of claims, mechanized
  separately in `docs/spec/MultiTenantAuth.spthy` under a Dolev-Yao
  adversary model. They concern whether a *credential* can cross a
  community boundary, not whether already-admitted data can. A future node
  may cover them; this one does not.
- **The C1 bandwidth-limited physical channels** (buffer cache, autovacuum,
  planner statistics, connection-pool timing) that `docs/multi-tenant-
  relay.md` explicitly declares out of scope and does not claim
  non-interference over. Named, not proven, by the specification itself.
- **The P3 NIP-98 replay-freshness obligation** and its HA-deployment
  caveats (sticky routing vs. a shared seen-set) — a different obligation
  about authentication-mint freshness under multiple relay pods, not about
  data confinement between communities.
- **The security-framing sibling document**, `layers/security/tenancy-
  boundary.md` (issue #1179, PR #1832) — not present on disk in this
  worktree (branched before that PR would have merged), so no
  `relationships` edge is declared toward it. Per the task brief, that
  document covers cross-community isolation from the security-boundary
  framing angle; this node covers it from the tenancy-taxonomy/mechanism
  angle — the actual runtime guarantees, their enforcement tier, and their
  verification status. The two should not duplicate each other's evidence
  ledgers once both are merged.
- **`docs/multi-tenant-conformance.md`'s full per-surface obligation
  table** (search, git object storage, presence, pub/sub key prefixing,
  and so on for every scoped surface) — linked as supporting context, not
  reproduced; the two sibling architecture nodes already made the same
  choice for the same reason.

## Relationships

- **`depends-on`** `architecture-principles-host-selects-community` — this
  node's confinement claim presupposes that "community B" was itself
  correctly and immutably resolved; if host selection is wrong or
  overridable, this node's claim is vacuous.
- **`references`** `architecture-principles-community-is-security-boundary`
  — the sibling claim that client signals cannot override the resolved
  community; related, not restated.
- **`references`** `architecture-principles-fail-closed-boundaries` — the
  general fail-closed pattern this invariant's own rejection behavior
  (generic error, no default tenant) instantiates.
- **`references`** `architecture-deployment-multi-community` — the
  deployment shape (one relay process, N communities) this invariant is
  stated over.
- **`implements`** `corpus-template-invariant` — this node's shape (Invariant
  statement / Scope / Enforcement today / Consequence of violation /
  Boundary) follows that template.

All four topical targets were confirmed present in `origin/launchpad`'s
corpus tree at the recorded revision before being declared, per `AGENTS.md`'s
"Creating a node" step 9.

## Scope and omissions

**This node covers** the cross-community read/write confinement invariant
(non-interference) for a request already resolved to a community: which
observable channels it binds (row returns, the existence oracle, the error
surface, the audit chain, numeric counts), the weakest enforcement tier that
actually holds it today (composite-key predicate enforcement plus
convention-and-review, explicitly *not* Postgres RLS despite the formal
model's axiom), what verification exists and its current gaps, and the
consequence of a violation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Host-to-community selection mechanism | `architecture-principles-host-selects-community` |
| Client-signal-cannot-override-community | `architecture-principles-community-is-security-boundary` |
| Authorization/credential soundness (S1–S8) | Not yet a corpus node; `docs/multi-tenant-relay.md` and `docs/spec/MultiTenantAuth.spthy` |
| Full per-surface conformance obligation table | `docs/multi-tenant-conformance.md` |
| Security-framing treatment of the tenancy boundary | `layers/security/tenancy-boundary.md` (#1179, PR #1832, not merged in this worktree) |

**Expected but not verified when this node was written:**

- **Whether `conformance_multitenant.rs`'s `#[ignore]`-gated A/B isolation
  suite currently passes against a live two-host deployment.** Not run this
  session; requires standing up a relay with two real host mappings sharing
  one database and Redis, out of scope for a documentation task.
- **Whether the `req.rs`/`event.rs` runtime trace-emission gap named above
  has since been closed.** `crates/buzz-relay/src/conformance/mod.rs`'s doc
  comment described it as "held back as an additive patch" at the recorded
  revision; whether that patch has landed since was not re-checked.
- **Whether every scoped query in the repository was audited for the
  construction-requires-community discipline**, versus the representative
  sample actually opened (`EventQuery`, `get_accessible_channel_ids`, the
  migration's composite keys). A query-building path elsewhere in the
  codebase that omits a `community_id` predicate would not be caught by
  re-reading this document.
- **Whether a startup or CI assertion suite admitting the formal model's
  RLS axiom exists outside this repository** (for example in a private
  deployment-configuration repo) — only this checkout was searched.
