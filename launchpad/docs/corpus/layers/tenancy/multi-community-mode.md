---
id: layers-tenancy-multi-community-mode
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
  - statement: "Every request's community is resolved from the connection host by the single row-zero seam (bind_community / TenantContext) in exactly the same way regardless of how many communities exist on the deployment; the seam contains no branch on the number of communities configured, and TenantContext can only be constructed from a completed host resolution."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
      - "crates/buzz-core/src/tenant.rs"
  - statement: "At every startup the relay unconditionally seeds exactly one 'deployment community' derived from its own configured relay_url via Db::ensure_configured_community, before any membership backfill or owner bootstrap runs, regardless of whether operator-driven provisioning is enabled; ensure_configured_community is idempotent, so this is safe on every restart."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "RELAY_OPERATOR_PUBKEYS is a deployment-level allowlist of pubkeys permitted to call the /operator/communities management endpoints; its own field doc states 'Empty (the default) disables community provisioning entirely -- fail closed,' and the config loader additionally rejects any invalid hex entry as a hard startup error and requires RELAY_OPERATOR_API_ORIGIN whenever the allowlist is non-empty."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "The community_provisioning module's own doc comment states the same rule from the handler side: 'An empty allowlist (the default) disables provisioning entirely,' and authorize_operator_request in the HTTP layer enforces it by returning 403 Forbidden for any NIP-98-authenticated signer whose pubkey is not found in relay_operator_pubkeys -- with an empty allowlist, no signer can ever pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs"
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "The POST /operator/communities route (and its sibling archive/unarchive/availability/transfer operator routes) is registered in the router unconditionally, whether or not RELAY_OPERATOR_PUBKEYS is configured; there is no separate 'single-community' build, binary flag, or router variant -- the same process always exposes the route, and the allowlist decides at request time whether any call succeeds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Two distinct code paths create a community row, with different limit semantics documented explicitly against each other: create_community_with_owner (the end-user-facing create_only path, reachable only through the already-gated operator endpoint) enforces MAX_COMMUNITIES_PER_OWNER against the requested owner; bootstrap_owner and Db::ensure_configured_community (the startup path and the legacy operator convergence path) are documented as 'deployment-root authority' that 'may exceed it by design' and do NOT enforce that limit at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_members.rs"
      - "crates/buzz-db/src/lib.rs"
  - statement: "MAX_COMMUNITIES_PER_OWNER defaults to 5 and is overridable per deployment via BUZZ_MAX_COMMUNITIES_PER_OWNER (a missing, unparsable, or non-positive value falls back to the default of 5); create_community_with_owner enforces it atomically inside one transaction, serialized on a per-owner Postgres advisory lock, so concurrent create requests for the same owner cannot both pass the count check."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_members.rs"
      - "crates/buzz-db/src/lib.rs"
  - statement: "No relay-wide cap on the total number of communities exists in this codebase; buzz-db's community_count is a Prometheus usage-rollup query (a bare SELECT COUNT(*) FROM communities) consulted by the metrics poller, not by provision_community or create_community_with_owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/usage.rs"
      - "crates/buzz-db/src/lib.rs"
  - statement: "Because the only code-level distinctions found are a deployment-level allowlist gating whether any additional community can be created at all (RELAY_OPERATOR_PUBKEYS) and a per-owner cap gating how many one pubkey can create through the end-user path (BUZZ_MAX_COMMUNITIES_PER_OWNER), 'single-community' and 'multi-community' describe configuration states of one otherwise-identical relay process and its request-handling code, not two branches that code switches between."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs"
      - "crates/buzz-db/src/store/relay_members.rs"
    confidence: 0.75
  - statement: "Issue #1190's Definition of Done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals, link related implementation/verification/decision and neighboring corpus nodes without duplicating their canonical content, and use examples only to clarify rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1190 definition of done"
relationships:
  - type: references
    target: architecture-deployment-multi-community
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-fail-closed-boundaries
---

# Multi-community mode

**Multi-community mode is the configuration state of a Buzz relay deployment
in which its operator has enabled `RELAY_OPERATOR_PUBKEYS`, so an authorized
signer may provision communities beyond the one the relay always seeds for
itself at startup — not a distinct code path the relay's request handling
switches into.**

**Authoritative sources — this node duplicates none of their detail:**

| For | Read |
|---|---|
| Deployment topology, execution nodes, and infrastructure for serving many communities | `architecture-deployment-multi-community` (`launchpad/docs/corpus/architecture/deployment/multi-community.md`) |
| Why the connection host, not the client, selects the community | `architecture-principles-host-selects-community` |
| Why the community boundary is a security boundary | `architecture-principles-community-is-security-boundary` |
| The fail-closed discipline this node's provisioning gate is one instance of | `architecture-principles-fail-closed-boundaries` |
| The row-zero host-binding seam itself | `crates/buzz-relay/src/tenant.rs`, `crates/buzz-core/src/tenant.rs` |
| Deployment-level operator provisioning | `crates/buzz-relay/src/handlers/community_provisioning.rs`, `crates/buzz-relay/src/api/operator.rs` |
| The per-owner community cap | `crates/buzz-db/src/store/relay_members.rs` |

Where this document and any of those disagree, **they win**.

## Definition

**Multi-community mode is the state a Buzz relay deployment is in once its
operator has configured a non-empty `RELAY_OPERATOR_PUBKEYS` allowlist**,
enabling authorized calls to `POST /operator/communities` that create
communities beyond the single "deployment community" every relay process
seeds for itself from its own `relay_url` at every startup. With the default,
empty allowlist, that seeded community is the only one any client can ever
reach — the relay is, in effect, single-community, though nothing in its
request-handling code is aware of the distinction.

This is a **deployment configuration state**, not a build variant, a binary
flag, or a branch in how an in-flight request is handled. The row-zero
host-to-community resolution seam (`bind_community`, `TenantContext`) runs
identically whether the deployment has seeded one community or fifty; no
handler asks "am I in single- or multi-community mode" before deciding how to
resolve, scope, or fan out a request. The mode is entirely a property of two
independent gates evaluated only on the provisioning path:

1. **Whether provisioning is possible at all** — `RELAY_OPERATOR_PUBKEYS`,
   empty by default, which fails closed: `authorize_operator_request` returns
   `403 Forbidden` for every signer when the allowlist is empty, and the
   config loader requires `RELAY_OPERATOR_API_ORIGIN` whenever the allowlist
   is set.
2. **How many communities one owner may create through the gated,
   end-user-facing path** — `MAX_COMMUNITIES_PER_OWNER` (default `5`,
   overridable per deployment via `BUZZ_MAX_COMMUNITIES_PER_OWNER`), enforced
   only by `create_community_with_owner`. The startup path
   (`Db::ensure_configured_community` plus `bootstrap_owner`) and the legacy
   operator convergence path deliberately do **not** enforce this limit —
   both are documented as deployment-root authority that "may exceed it by
   design," distinct from the end-user `create_only` path the limit exists to
   bound.

Neither gate touches how an already-created community behaves once it
exists. A community created through the default-disabled provisioning path
and a community seeded at startup are indistinguishable to every other part
of the relay: both get one row in `communities`, both get the same
host-normalization and fail-closed resolution, and both get the same
per-community isolation described by `architecture-principles-community-is-security-boundary`.

## Use cases

- **An operator deciding whether their deployment can host more than one
  community** reads `RELAY_OPERATOR_PUBKEYS`'s presence, not any relay
  "mode" setting — there is none.
- **A developer changing community-creation code** needs to know which of the
  two creation paths (`create_community_with_owner` vs.
  `bootstrap_owner`/`ensure_configured_community`) their change touches,
  because only one of them enforces the per-owner cap, and the split is
  intentional rather than an oversight to "fix" by adding the check to both.
- **A reviewer auditing a change to request-handling code** can use this
  node to confirm that the number of communities configured on a deployment
  is never a legitimate reason for that code to branch — if a proposed change
  introduces such a branch, that is new behavior this node does not already
  describe, not an application of an existing "mode."

## Comparison

| | Default (`RELAY_OPERATOR_PUBKEYS` empty) | Operator-enabled (`RELAY_OPERATOR_PUBKEYS` non-empty) |
|---|---|---|
| Communities reachable by any client | Exactly the one deployment community seeded from `relay_url` at startup | The seeded deployment community, plus any created via `POST /operator/communities` |
| `POST /operator/communities` | Registered, but every call returns `403 Forbidden` (no signer can match an empty allowlist) | Callable by a NIP-98 signer whose pubkey is in the allowlist, from `RELAY_OPERATOR_API_ORIGIN` |
| Per-owner cap on new communities | Not reachable — provisioning is closed | `create_only` requests enforce `MAX_COMMUNITIES_PER_OWNER` (default 5, or `BUZZ_MAX_COMMUNITIES_PER_OWNER`); the legacy convergence request does not |
| Per-request tenant resolution (`bind_community`) | Identical | Identical |
| Community isolation once a community exists | Identical | Identical |

## Scope and omissions

**This node covers** what distinguishes a Buzz relay deployment that can
provision additional communities from one that cannot: the
`RELAY_OPERATOR_PUBKEYS` provisioning gate, the per-owner `MAX_COMMUNITIES_PER_OWNER`
cap and its deliberate exemption for deployment-root paths, and the fact that
neither gate changes how the relay resolves or isolates a request once a
community exists.

**This node does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Deployment topology, execution nodes, Helm chart profiles, and infrastructure for running one relay serving many communities | `architecture-deployment-multi-community` |
| The row-zero host-resolution mechanism itself, and why the host (not the client) selects the community | `architecture-principles-host-selects-community` |
| Why the community boundary is a security boundary, and the fail-closed tests that back it | `architecture-principles-community-is-security-boundary` |
| Client-side community *switching* in the desktop app (React-key remount, `resetCommunityState()`) — a UI concern local to one already-connected client, not relay runtime behavior | `desktop/src/features/communities/useCommunityInit.ts` (no corpus node yet) |
| The `communities` table schema and its archival/deletion lifecycle | `migrations/0001_initial_schema.sql`, `migrations/0016_community_archival.sql`, `migrations/0029_community_deletion.sql` (cited by `architecture-deployment-multi-community`, not restated here) |
| Per-type corpus template conformance for the `layers` surface | No `layers`-specific template exists in the merged corpus at the recorded revision; this node follows `templates/concept.md` (the closest-fitting merged documentation-form template) directly against `node.schema.json`, per `AGENTS.md`'s documented no-template path |

**Expected but not verified when this node was written:**

- **Whether any real deployment (staging or otherwise) sets
  `RELAY_OPERATOR_PUBKEYS` non-empty today** was not checked — the
  repositories that would show this (`squareup/block-coder-tf-stacks`,
  `squareup/sprout-backend-blox`) are private and not present in this
  checkout, matching the same limit `architecture-deployment-multi-community`
  already names for its own deployment claims.
- **Whether `BUZZ_MAX_COMMUNITIES_PER_OWNER` has ever been set away from its
  default of 5 in any real deployment** was not checked, for the same
  reason.
- **Whether a future change adds a third community-creation path** that
  would need the same "does it enforce the per-owner cap" question answered
  was not speculated about; this node describes the two paths found at the
  recorded revision only.
