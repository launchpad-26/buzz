---
id: capabilities-communities-community
type: capabilities
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
  - statement: "VISION.md's own 'Communities' section states that a community is 'the tenant boundary: one workspace, one URL, one isolated world of channels, members, profiles, DMs, repos, and search,' and that the single-community deployment most operators run today is identical to a Buzz relay today -- the community level adds nothing observable at N=1; what changes is that one shared deployment can host many communities at once."
    entry_class: FACT
    evidence:
      - "VISION.md:50-52"
  - statement: "VISION.md states three product-level rules for communities: the URL is the community and every connection binds to its host's community before any request runs, with an unknown host rejected rather than defaulted into a neighbor; isolation is the boundary rather than a filter, proven (not merely asserted) by a formal model; and identity is portable across communities while profile, DMs, and channel-less content are per-community, requiring an explicit repost into each community joined."
    entry_class: FACT
    evidence:
      - "VISION.md:54-56"
  - statement: "docs/multi-tenant-relay.md defines community isolation as non-interference -- a label-flow invariant, not a `WHERE community_id = $1` predicate -- and states it is mechanized with TLA+ for the concurrency/serving model and Tamarin for the authorization protocol, with the guarantees mutation-tested rather than merely written down."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md:11"
      - "docs/multi-tenant-relay.md:30-32"
  - statement: "buzz-core's tenant module implements the community boundary as a type-level fence: `CommunityId` is an opaque UUID newtype with no `Default` and no `Deserialize`, constructible only via `CommunityId::from_uuid` from a server-trusted value (host resolution or an already-scoped DB row); `TenantContext` is likewise constructible only through `TenantContext::resolved`, called only from the host-resolution path, and every other call site takes `&TenantContext` and only reads it. The module's own doc comment names this a 'lint-and-review fence, not a compiler fence' -- the type removes the accidental client-input path, and review/lint closes the deliberate one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "`normalize_host` is the one normalization rule shared by both sides of the host-to-community lookup: it ASCII-lowercases, strips a single trailing FQDN-root dot, and strips a default port (`:80`/`:443`) while preserving a non-default port and IPv6 brackets, so that `Relay.Example`, `relay.example.`, and `relay.example:443` all resolve to one community and can never split into two; an empty or unmapped host is left to fail closed rather than mapped to a default tenant. Its unit tests assert this collapsing behavior directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "The `communities` table (migration 0001) stores one row per tenant: a UUID primary key (checked non-nil), a `host VARCHAR(255) NOT NULL`, an optional `signing_key BYTEA`, and `created_at`, with `CREATE UNIQUE INDEX idx_communities_host ON communities (lower(host))` enforcing exactly one community per normalized host at the database level."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "The `relay_members` table (migration 0001, labelled 'NIP-43' in its own comment) is the community-scoped role membership store: primary key `(community_id, pubkey)`, and a `role` column constrained to exactly `'owner'`, `'admin'`, or `'member'` by a CHECK constraint, indexed by `(community_id, role)`."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "A community's lifecycle extends past simple existence: migration 0016 adds a nullable `archived_at TIMESTAMPTZ` column to `communities` for a lighter-weight, non-destructive archived state, and migration 0029 adds a `deletion_state TEXT NOT NULL DEFAULT 'active'` column constrained to `'active'`, `'quiescing'`, `'fenced'`, or `'tombstone'`, backing a durable deletion state machine that never removes the `communities` row itself."
    entry_class: FACT
    evidence:
      - "migrations/0016_community_archival.sql"
      - "migrations/0029_community_deletion.sql"
  - statement: "Community creation is authorized above the tenant boundary rather than through the community-scoped `relay_members` role lookup every other admin action uses, because creation's effect is the creation of tenancy itself and there is no community yet to look a role up in. The handler's own module doc states this directly: `POST /operator/communities` is NIP-98-authenticated and gated solely by the deployment-level `RELAY_OPERATOR_PUBKEYS` allowlist (empty by default, disabling provisioning entirely), and is deliberately outside the Nostr event ingest data plane -- no relay-membership bypass, no special event kind, no storage or fan-out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs"
  - statement: "buzz-core's kind registry defines addressable NIP-29 group state at kinds 39000 (metadata), 39001 (admins), and 39002 (members) -- all scoped to one channel inside a community -- and community moderation commands at kinds 9040-9044, also scoped within a community; no kind in the registry represents a community itself. A community is created and read entirely off the Nostr event plane, through the HTTP handler above, not as a signed event of any kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs"
  - statement: "The corpus already carries two merged nodes that document parts of this same boundary in depth: `architecture-principles-community-is-security-boundary` states the host-resolution invariant as a MUST-level security principle with its enforcement points and observable failure behavior, and `architecture-deployment-multi-community` documents the deployment topology, the `communities`/`relay_members` schema, community creation's operator-gated authorization, and the lifecycle columns above -- both confirmed present in `origin/launchpad`'s corpus tree at the recorded revision by reading their own front matter."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
      - "launchpad/docs/corpus/architecture/deployment/multi-community.md"
  - statement: "Issue #737 scopes this node to community.md as the single canonical capability node for 'community', separate from four sibling task issues in the same batch: #732 (community-creation), #733 (community-discovery), #734 (community-members), #735 (community-provisioning), and #736 (community-roles) -- each its own document, not yet drafted or merged as of this revision, so none is a valid relationship target from this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#737 definition of done, plus #732-#736 titles read directly via gh issue view"
  - statement: "Issue #737's definition of done requires this node to state the capability and its primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability -- in addition to the corpus-wide schema and evidence requirements every task in this batch carries."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#737 definition of done"
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-deployment-multi-community
---

# Community: capability

A Buzz relay lets a client reach one **community**: a relay-scoped tenant
boundary that is, on its own, an entire isolated workspace -- one URL, one
set of channels, members, profiles, DMs, repos, and search, all
inaccessible from any other community sharing the same deployment. A
single-operator deployment running exactly one community looks and behaves
identically to a plain Buzz relay; nothing about the community concept is
observable until a second community exists on the same infrastructure. What
a community *adds* at that point is the ability for one shared deployment
(one relay process, one Postgres database, one Redis, one object store) to
host many independent workspaces at once, so an operator can bring up a new
workspace with a database write and a DNS route instead of provisioning a
whole stack per signup.

**Primary actors and outcomes:**

- **A human or agent user** connects to a community by its host (a domain
  or subdomain); once bound, every channel, message, DM, profile, repo, and
  search result they can reach belongs to that one community and no other.
- **A relay operator** provisions and administers communities on
  infrastructure they run -- from a single self-hosted community up to many
  communities sharing one deployment -- and holds the deployment-level
  authority (`RELAY_OPERATOR_PUBKEYS`) that can create tenancy itself,
  distinct from any role inside a community.
- **A community owner/admin/member** (the roles `relay_members` enforces)
  administers or participates inside one already-created community; that
  authority is scoped to the one community their role row names and confers
  nothing in any other.

## Behavioral rules and constraints

- **The URL is the community.** A connection's `Host` is resolved to
  exactly one community before any request runs; an unmapped or empty host
  is rejected, never defaulted into a neighboring community. This is a
  type-level fence in `buzz-core`, not only a runtime check: `CommunityId`
  cannot be deserialized or defaulted, and `TenantContext` can only be
  constructed from a completed host resolution.
- **Host normalization prevents accidental tenant splitting, in one
  direction only.** Case, a trailing FQDN-root dot, and a default port
  (`:80`/`:443`) all collapse to the same community; a non-default port is
  kept as a legitimate distinct selector. This rule runs identically on the
  stored `communities.host` value and on every incoming `Host` header, so
  the two sides can never disagree.
- **Isolation is a boundary, not a filter, and it is checked formally, not
  only asserted.** `docs/multi-tenant-relay.md` states the guarantee as a
  non-interference / label-flow invariant, mechanized with TLA+ for the
  concurrency/serving model and Tamarin for the authorization protocol,
  with the guarantees mutation-tested. `architecture-principles-community-is-security-boundary`
  (referenced below) documents this same invariant's enforcement points and
  observable failure behavior in the running relay code.
- **Identity is portable across communities; almost everything else is
  not.** A user's keypair is the same everywhere, but their profile, DMs,
  and channel-less content are stored per-community -- joining a second
  community means reposting a profile into it, not reusing one across a
  boundary that does not share it.
- **Role-based authority inside a community does not extend outside it.**
  `relay_members` scopes every row to `(community_id, pubkey)` with a role
  of `owner`, `admin`, or `member`; every ordinary admin action is
  authorized by looking up the caller's role within the one community
  already resolved for their request.
- **Creating a community is authorized above the tenant boundary, by
  necessity, not by choice.** Every other admin action can be authorized
  by a `relay_members` role lookup because a community already exists to
  look the role up in; creating one cannot use that mechanism, since its
  effect is the creation of tenancy itself. The relay instead gates
  `POST /operator/communities` on a deployment-level pubkey allowlist,
  empty (provisioning disabled) by default, deliberately outside the
  Nostr event ingest data plane.
- **A community is not a Nostr event of any kind.** Channels inside a
  community carry NIP-29 addressable state (kinds 39000-39002) and
  moderation commands (kinds 9040-9044) that are themselves community-
  scoped, but no kind in `buzz-core`'s registry represents a community.
  A community is created, provisioned, and looked up entirely through the
  relay's own HTTP surface, not by publishing a signed event.
- **A community's existence outlives simple deletion.** Beyond plain
  existence, a community carries lifecycle state -- an `archived_at`
  timestamp for a lighter-weight non-destructive pause, and a
  `deletion_state` progressing `active -> quiescing -> fenced -> tombstone`
  that never removes the `communities` row itself. The mechanics of both
  belong to the architecture/deployment node referenced below, not to this
  one.

## Boundary

This node states what a community fundamentally is and the invariants that
hold across every concern built on top of it. It deliberately does not
re-derive the depth its sibling capability nodes in this same batch own:

- **Community creation** (mechanism, request/response shape, atomic
  create-vs-converge semantics) -- its own node, not yet drafted (issue
  #732).
- **Community discovery** (how a user or operator finds or is directed to
  a community) -- its own node, not yet drafted (issue #733).
- **Community members** (joining, invitation, allowlisting, membership
  lifecycle beyond the role column named above) -- its own node, not yet
  drafted (issue #734).
- **Community provisioning** (the operator-facing provisioning flow and
  its relationship to creation) -- its own node, not yet drafted (issue
  #735).
- **Community roles** (the semantics and permission boundaries of owner,
  admin, and member beyond the schema constraint named above) -- its own
  node, not yet drafted (issue #736).

It also does not re-describe:

- **How one relay deployment is built to host many communities** --
  execution topology, containers, data stores, network/trust boundaries,
  and failure/recovery behavior. That is
  `architecture-deployment-multi-community` (referenced below).
- **The security-boundary invariant's enforcement points and observable
  failure behavior in code.** That is
  `architecture-principles-community-is-security-boundary` (referenced
  below).
- **How channels, DMs, or other in-community surfaces work.** Those are
  their own capabilities, scoped inside an already-resolved community, not
  properties of the community boundary itself.

## Relationships

- `references`: `architecture-principles-community-is-security-boundary`
  -- the security invariant this capability rests on, and its enforcement
  points in the running relay.
- `references`: `architecture-deployment-multi-community` -- how one
  deployment hosts many communities, the `communities`/`relay_members`
  schema, and community lifecycle (archival, deletion).

No `implements`, `part-of`, or `depends-on` edges are declared. No
capability-level parent or sibling node (community-creation,
-discovery, -members, -provisioning, -roles) is merged in `origin/launchpad`'s
corpus tree at the recorded revision, so none is a valid relationship
target yet -- see *Scope and omissions*.

## Verification

- **`docs/multi-tenant-relay.md`** is the formal verification surface: a
  TLA+ model of the concurrency/serving model and a Tamarin model of the
  authorization protocol, both stated as mechanizing isolation as
  non-interference rather than a filtered query predicate, with the
  guarantees mutation-tested.
- **`crates/buzz-test-client/tests/conformance_multitenant.rs`** is the
  executable A/B isolation conformance suite referenced by both
  `architecture-principles-community-is-security-boundary` and
  `architecture-deployment-multi-community`; every test in it is
  `#[ignore]`-gated and requires a live relay with two real host-to-community
  mappings, selected explicitly with `--ignored`. This node did not run
  that suite -- see *Scope and omissions*.
- **`crates/buzz-core/src/tenant.rs`'s own unit tests** exercise
  `normalize_host`'s collapsing behavior directly (case, trailing dot,
  default port, IPv6 literal, empty-stays-empty) and were read as part of
  this node's evidence, though not independently re-run.

## Scope and omissions

**This node covers** what a community fundamentally is: a relay-scoped
tenant boundary, its primary actors and outcomes, the behavioral rules and
constraints that hold for every community regardless of which specific
concern (creation, discovery, membership, provisioning, roles) is in play,
and the taxonomy split across this capability's sibling documents.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Community creation mechanism and request/response shape | issue #732 (not yet drafted) |
| Community discovery | issue #733 (not yet drafted) |
| Community membership lifecycle (joining, invitation, allowlisting) | issue #734 (not yet drafted) |
| Community provisioning flow | issue #735 (not yet drafted) |
| Owner/admin/member role semantics and permission boundaries | issue #736 (not yet drafted) |
| Deployment topology, schema detail, and lifecycle (archival/deletion) mechanics | `architecture-deployment-multi-community` |
| Security-boundary enforcement points and observable failure behavior | `architecture-principles-community-is-security-boundary` |
| Per-type corpus template conformance for the `capabilities` category | No per-type template exists yet in the merged corpus (`launchpad/docs/corpus/AGENTS.md`); the draft `launchpad/docs/corpus/templates/capability.md` was used for shape, and this node expects a later reshaping task |

**Expected but not verified when this node was written:**

- **`conformance_multitenant.rs`'s `#[ignore]`-gated assertions were not
  run** against this revision -- their presence and shape were read from
  source, not their current pass/fail status. Both referenced sibling
  nodes record the same gap independently.
- **The exact boundary between "community creation" (#732) and "community
  provisioning" (#735)** was not resolved here; both issues exist as
  separate sibling tasks in the same batch and this node makes no claim
  about how their scopes divide -- that is for those documents to
  establish.
- **Community discovery's mechanism (#733) was not investigated at all**
  beyond confirming the sibling task exists; no discovery-related code
  path was read while authoring this node.
