---
id: layers-tenancy-community
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, the tip of origin/launchpad at authoring time."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "ARCHITECTURE.md defines a Buzz community as \"the tenant-visible workspace selected by the request host,\" states that the self-hosted default is one host, one relay process, one implicit community, and that req.community = resolve_host(connection.host) is established before AUTH, EVENT, REQ, REST, media, git, search, workflow, or pub/sub handling, with unknown hosts failing closed and NIP-98/API-token stamps required to agree with the host-derived community rather than override it."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:9-15"
  - statement: "ARCHITECTURE.md's connection-lifecycle 'Step 0: Community Binding' states the server resolves TenantContext from the request host before any handler can observe tenant data, that in single-community mode the configured host maps to the default community, that in multi-community mode an unknown or unmapped host rejects generically and never falls through to a default tenant, and that client-supplied #h tags are channel identifiers that must resolve to a channel inside the host-derived community."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:169-177"
  - statement: "docs/multi-tenant-conformance.md states the compatibility rule as 'today's Buzz is one implicit community selected by its relay URL,' defines row zero as req.community = resolve_host(connection.host) bound at connection establishment before any WebSocket, REST, media, git transport, webhook, workflow side-effect, search, or pub/sub path observes tenant data, and states that the single-community deployment is 'the degenerate case: one configured host resolves to the one default community, so existing clients observe the same behavior.'"
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:1-33"
  - statement: "buzz-core's tenant.rs module documents CommunityId as 'the first-class tenant key on every scoped row' and TenantContext as 'the resolved tenant of an in-flight request, bound once at connection / request establishment before any handler observes tenant data,' states that TenantContext has no Default and no Deserialize impl so a community can never be parsed from client input, and states this is 'a lint-and-review fence, not a compiler fence' because TenantContext::resolved and CommunityId::from_uuid remain pub for the host-resolution path to call."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs:1-30"
      - "crates/buzz-core/src/tenant.rs:37-38"
      - "crates/buzz-core/src/tenant.rs:68-90"
  - statement: "buzz-core's normalize_host lowercases a host, strips a single trailing FQDN-root dot, and strips a default port (:80 or :443) while preserving non-default ports and IPv6 bracket literals, so that Relay.Example, relay.example., and relay.example:443 all normalize to the identical community lookup key and can never split into distinct tenants."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs:121-150"
  - statement: "buzz-relay's tenant.rs defines a HostResolver trait (resolve_host: normalized host -> Option<CommunityId>) and a bind_community function documented as 'the single row-zero entry point,' which normalizes the host, resolves it, and returns a BindError on any non-success -- an unmapped host or a lookup error -- with no code path that yields a default or fallback community; a sibling bind_deployment_community resolves a relay's own deployment community from its configured relay_url host for server-internal paths (git Smart-HTTP, the pre-receive hook callback, the workflow execution sink, startup tasks) that have no inbound request Host header, through that same fail-closed path rather than a separate default."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:31-46"
      - "crates/buzz-relay/src/tenant.rs:48-58"
      - "crates/buzz-relay/src/tenant.rs:60-95"
      - "crates/buzz-relay/src/tenant.rs:97-114"
  - statement: "migrations/0001_initial_schema.sql creates a communities table (id UUID primary key, host VARCHAR(255), signing_key BYTEA, created_at) with a unique index on lower(host), documented in an adjoining comment as 'OPERATOR-GLOBAL: it is the registry of tenants, not itself tenant-scoped, so it carries no community_id of its own (its id IS the community key),' and states that resolve_host(host) reads exactly one row from this table to mint the request's TenantContext."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:39-61"
  - statement: "migrations/0001_initial_schema.sql's header states the schema is 'multi-tenant' and that community_id is 'a first-class, server-resolved key on every tenant-scoped row,' and its migration-lint obligations require every tenant-scoped table to carry community_id NOT NULL and no UNIQUE/PRIMARY KEY/FK observable across communities; the immediately following channels table comment confirms this concretely for one such table, stating channels.community_id is immutable (enforced by a trigger, no UPDATE path) and that the channels primary key is (community_id, id), so the same channel UUID may legitimately exist in two different communities without collision."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:1-22"
      - "migrations/0001_initial_schema.sql:63-70"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_NIP29_GROUP_METADATA = 39000, KIND_NIP29_GROUP_ADMINS = 39001, and KIND_NIP29_GROUP_MEMBERS = 39002 as NIP-29 group-state kinds in the addressable range 39000-39003; these events describe a channel's metadata and membership (a channel is Buzz's implementation of a NIP-29 group), not a community -- a community has no NIP-29-shaped event of its own and is instead a purely server-side row (communities.id) selected by host, never advertised to clients as a signed event kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:420-426"
  - statement: "crates/buzz-relay/src/handlers/community_provisioning.rs implements provision_community, documented as the handler for 'a relay-operator community provisioning request,' explicitly noting the caller is an HTTP operator endpoint rather than the Nostr event ingest path so 'the tenant data-plane fences [stay] unchanged: no relay-membership bypass, no special event kind, no command routed ahead of moderation/write blocks'; ProvisionCommunityRequest carries host, an optional initial_owner_pubkey, and a create_only flag that, when set, atomically creates the host and owner and rejects an existing host instead of converging or rotating ownership."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:43-56"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:249-260"
  - statement: "ARCHITECTURE.md names 'single-community mode' and 'multi-community mode' as the two deployment modes throughout its subsystem descriptions -- e.g. 'In single-community mode the configured host maps to the default community. In multi-community mode, an unknown or unmapped host rejects generically' (Step 0), and repeated per-subsystem notes that Redis pub/sub keys, audit-log chains, workflow scoping, and the events/channels/workflows/audit_log tables all behave identically in the N=1 single-community case but partition or key by community_id once multi-community mode is active."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:173-174"
      - "ARCHITECTURE.md:434"
      - "ARCHITECTURE.md:786-792"
  - statement: "migrations/0001_initial_schema.sql's own header comment states that existing single-community deployments migrate via 'the documented backfill migration (0002), which assigns all pre-existing rows to one default community,' but the migration currently numbered 0002 in this repository (migrations/0002_git_repo_names.sql) is the NIP-34 git-repo-name registry and makes no mention of a default-community backfill; no other migration filename or content matches a default-community backfill either. This is left as a verified gap below rather than resolved."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:1-8"
      - "migrations/0002_git_repo_names.sql"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs documents, as a named obligation checked by an executable test, that 'the same channel UUID legitimately co-exists in two communities (DB PK (community_id, id)); an h tag resolving to a channel in another community is rejected generically' -- the same isolation property migrations/0001_initial_schema.sql's schema comment states, here confirmed at the verification layer rather than the schema layer alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1471-1473"
  - statement: "launchpad/docs/corpus/architecture/context/buzz-platform.md already states, at context level, that 'A Buzz community is the tenant-visible workspace selected by the request host; the self-hosted default is one host, one relay process, one implicit community, and every connection binds a TenantContext resolved from that host before any Nostr or HTTP handler runs' -- the same claim this node develops in depth, so this node references rather than duplicates it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/buzz-platform.md"
relationships:
  - type: references
    target: architecture-context-buzz-platform
---

# Community (tenancy)

A **community** is Buzz's unit of tenancy: the workspace a client is talking to,
selected entirely by which host it connected to. This node explains what a
community is, how it is bound to a request, and where it sits relative to the
concepts most likely to be confused with it — a **channel**, and the
still-unwritten `community-id` and `tenant-context` nodes that describe its
mechanics in more depth. Those depth topics, and Buzz's `single-community-mode`
and `multi-community-mode` deployment modes, are named here and deliberately
left to their own future corpus nodes; see *Scope and omissions* below.

## Definition

A Buzz community is the tenant-visible workspace selected by the request host.
Concretely: `req.community = resolve_host(connection.host)`, resolved by the
server **before** any WebSocket `AUTH`/`EVENT`/`REQ`, REST handler, media
handler, git transport handler, webhook handler, workflow side effect, search
query, or pub/sub fan-out path can observe tenant data. Nothing about a
community is client-supplied: it is derived purely from which host the client
connected to, never from a request body, a signed event, or a tag.

The self-hosted default — and still the common case today — is one host, one
relay process, one implicit community. A hosted, multi-tenant deployment moves
the same semantic boundary up one level: many communities behind many hosts,
served by one relay deployment. Either way, the client-facing rule never
changes: the URL is authoritative for the workspace.

**What a community is not.** It is not a channel. A channel (`h` tag; Buzz's
implementation of a NIP-29 group, advertised via kind `39000` metadata, `39001`
admins, and `39002` members) is a locality boundary *inside* one community — a
client-supplied `h` tag must resolve to a channel inside the host-derived
community, and can never reach another community's channel. A community itself
has no NIP-29-shaped event and is never advertised to clients as a signed event
kind at all: it is a purely server-side row in the `communities` table, keyed
by its own UUID (`communities.id`), looked up by normalized host.

It is also not the same thing as `TenantContext` or `CommunityId` — those are
the typed, code-level representations of "the community currently bound to
this request" and "a community's UUID" respectively, and are documented in
depth by the (not yet written) `tenant-context` and `community-id` corpus
nodes. This node is the conceptual one level up: what the tenant unit *is* and
why it exists, not how the type system enforces it.

## How a community is resolved

```mermaid
flowchart LR
    A["Inbound connection\n(WebSocket / REST / media / git / webhook)"] --> B["Host header"]
    B --> C["normalize_host()\n(lowercase, strip default port,\nstrip trailing FQDN dot)"]
    C --> D{"communities table\nlower(host) lookup"}
    D -->|"match"| E["TenantContext bound\n(CommunityId + normalized host)"]
    D -->|"no match / empty"| F["Reject: generic error\n(fail closed, never a default tenant)"]
    E --> G["Every scoped handler\n(auth, events, REQ, media, git,\nsearch, pub/sub, workflow)"]
```

The `communities` table is deliberately **operator-global**, not itself
tenant-scoped — it carries no `community_id` of its own because its own `id`
*is* the community key, and it is the one table the migration-lint harness
allowlists as an exception to "every scoped table carries `community_id`."
Every other tenant-scoped table (channels, events, workflows, audit entries,
and the rest) instead carries `community_id NOT NULL`, and the schema's own
migration-lint obligations forbid any `UNIQUE`/`PRIMARY KEY`/foreign key on
such a table that is observable across communities — each key leads with
`community_id` (or a joined parent already pins it). `channels`, for example,
has a compound primary key `(community_id, id)`, so the very same channel UUID
may legitimately exist in two different communities without colliding — an
isolation property `crates/buzz-test-client/tests/conformance_multitenant.rs`
exercises directly as a named obligation, not merely a schema-level
assertion.

Server-internal code paths that have no inbound request `Host` header at all
(the git Smart-HTTP transport, the localhost pre-receive hook callback, the
workflow execution sink, startup tasks) still go through the same fail-closed
binding path: they resolve the relay's own configured `relay_url` host through
the identical lookup, rather than taking a separate "internal" shortcut that
bypasses host resolution.

## Use cases

Understanding "community" matters before touching almost any server-side code
in this repository, because it is the axis every tenant-scoped table, cache
key, and Redis channel is partitioned on:

- **Writing or reviewing a new handler.** Any new WebSocket, REST, media, git,
  webhook, search, or pub/sub code path must obtain its `TenantContext` from
  host binding before reading anything from the request that could cause a
  tenant-visible effect — not derive a community from a client-supplied field.
- **Adding a new tenant-scoped table or index.** It needs a `community_id`
  column, and any uniqueness constraint on it must lead with `community_id`
  (or be scoped through an already-pinned parent) so two communities can never
  collide on the same key.
- **Operating a deployment.** An operator provisioning a new tenant calls the
  `POST /operator/communities` endpoint (`provision_community`), which
  ensures/creates a community by host and, given `create_only: true`, rejects
  an already-existing host rather than silently converging into it — the same
  fail-closed discipline as request-time resolution, applied to provisioning.
- **Debugging cross-tenant leakage.** Because the community is resolved once,
  at connection establishment, from the host alone, the first question for any
  suspected cross-community bug is always "where did this code path get its
  `community_id` from, and did it come from `TenantContext` or from something
  client-supplied?"

## Scope and omissions

**This document covers** what a community is, how it is bound to a request
(row zero / host resolution, conceptually), why the `communities` table sits
outside the tenant-scoping pattern every other table follows, and the boundary
between a community and a channel.

**It does not cover, and these are gaps rather than silence — each is a named
sibling node from this task's parent PRD (#607), none of which exist on
`origin/launchpad` at this revision, so no `relationships` entry can target
them yet:**

| Not covered here | Owned by (future node) |
|---|---|
| `CommunityId`'s type-level design in depth | `community-id` |
| `TenantContext`'s full lifecycle and the "lint-and-review fence, not a compiler fence" argument | `tenant-context` |
| How host resolution itself works end-to-end (`HostResolver`, `bind_community`, `bind_deployment_community`, the exact normalization rules) | `host-resolution` |
| Who belongs to a community and how membership is granted/checked | `community-membership` |
| How caches (Redis pub/sub, presence, typing) are partitioned by community | `community-scoped-cache` |
| How persisted data more broadly (beyond the schema-level pattern named here) is community-scoped | `community-scoped-data` |
| The isolation guarantees and tests that prove one community cannot observe another's data | `cross-community-isolation` |
| The single-host, single-implicit-community deployment shape named throughout `ARCHITECTURE.md` as "single-community mode" | `single-community-mode` |
| The many-communities-behind-many-hosts deployment shape named as "multi-community mode" | `multi-community-mode` |

**Verified gap, not resolved here:** `migrations/0001_initial_schema.sql`'s
own header comment states that pre-existing single-community deployments
migrate via "the documented backfill migration (0002), which assigns all
pre-existing rows to one default community." At this revision, the migration
actually numbered `0002` (`migrations/0002_git_repo_names.sql`) is the NIP-34
git-repo-name registry and has nothing to do with a default-community
backfill, and no other migration filename matches "default community" or
"backfill" either. Whether the backfill migration was renumbered, folded into
`0001` itself, or genuinely never landed under that number is not established
by anything read for this node.

**Expected but not verified when this node was written:**

- **Whether a `default_community` id/name convention exists anywhere in code
  or configuration** for the self-hosted, single-community case, beyond "the
  one row `communities` happens to contain." No config file or startup-seeding
  code path was read for this node.
- **The full list of "operator-global" tables** beyond `communities` itself —
  `migrations/0001_initial_schema.sql`'s header names an "explicit allowlist"
  of such tables but this node did not enumerate it.
