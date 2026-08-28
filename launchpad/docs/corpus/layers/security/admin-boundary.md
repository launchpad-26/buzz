---
id: layers-security-admin-boundary
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
  - statement: "community_provisioning.rs's own module doc states the boundary directly: every other admin surface in the relay is community-scoped (the sender's role is looked up in relay_members for the host-resolved tenant), but community creation cannot work that way because its effect is the creation of tenancy itself, so the authorizing identity must sit above tenants -- gated by the deployment-level RELAY_OPERATOR_PUBKEYS allowlist, which is disabled entirely (fails closed) when empty."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:1-26"
  - statement: "authorize_operator_request (the sole gate in front of every /operator/communities* handler) verifies a NIP-98-signed pubkey against state.config.relay_operator_pubkeys only; it never looks up the caller in relay_members and never resolves a tenant from the request Host header. A pubkey absent from that allowlist is rejected with 403 FORBIDDEN and the message 'actor not authorized: not a relay operator', regardless of any community role it may hold."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:60-102"
  - statement: "The test non_allowlisted_operator_key_gets_403 signs a valid NIP-98 POST /operator/communities request with a freshly generated keypair that was never added to the operator allowlist, and asserts the response status is exactly StatusCode::FORBIDDEN."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:707-735"
  - statement: "config.rs documents relay_operator_pubkeys as deployment-level and explicitly contrasts it with relay_owner_pubkey, 'a role *within* the deployment community': operators 'span tenants: they may create new communities and bootstrap initial owners, but hold no implicit tenant membership row.' The same doc comment states the empty-list default 'disables community provisioning entirely -- fail closed.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:190-206"
  - statement: "Config::from_env parses RELAY_OPERATOR_PUBKEYS as a comma-separated list and returns a hard ConfigError::InvalidValue -- refusing to start -- for any entry that is not a 64-char hex string, rather than silently dropping the bad entry; it also errors at startup if RELAY_OPERATOR_PUBKEYS is non-empty but RELAY_OPERATOR_API_ORIGIN is unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:662-690"
  - statement: "handle_relay_admin_event enforces a durable-ban check (admits_relay_admin_command) that wraps the entire in-community admin command execution, specifically because ingest_event exempts relay-admin kinds 9030-9033 from its normal write-path restriction gate so a merely-timed-out admin can still administer the roster; the ban check exists so that exemption does not also admit a banned admin, and a restriction-lookup DB failure is itself treated as a fail-closed refusal (RelayAdminError::Internal), never a silent admit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:145-214"
  - statement: "execute_relay_admin_command looks up the sender's role via state.db.get_relay_member(tenant.community(), sender_hex) -- scoped to the single community already resolved onto tenant by the caller -- and, for kind:9030 (add member), refuses the command with 'actor not authorized: must be admin or owner' unless sender_role is admin or owner for that same community; there is no code path in this function that reads or writes relay_members for any community other than tenant.community()."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:223-252"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:311-317"
  - statement: "buzz-admin's main.rs imports only buzz_db, buzz_pubsub, clap, nostr and tracing; it depends on buzz_auth in Cargo.toml but the crate is never named in main.rs, and no subcommand in the Command enum (AddMember, RemoveMember, ListMembers, GenerateKey, Migrate, ProductFeedback, Deletions, ReconcileChannels) takes or verifies a caller identity of any kind -- there is no NIP-42 or NIP-98 verification anywhere in the CLI's command-dispatch path."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:30-120"
      - "crates/buzz-admin/Cargo.toml"
  - statement: "resolve_admin_tenant resolves which community buzz-admin operates on purely from the RELAY_URL environment variable's host, looked up against the durable communities table -- an unmapped host fails closed with an error -- but nothing in this resolution step authenticates *who* is running the CLI; that identity question is answered entirely outside Buzz's own code, by whoever can reach a shell with RELAY_URL set to the target relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:452-470"
  - statement: "ARCHITECTURE.md documents buzz-admin as 'the recommended way to manage relay membership in production,' shipped inside the relay's own Docker image at /usr/local/bin/buzz-admin, and NOSTR.md's own examples invoke it as `docker compose exec relay buzz-admin add-member ...` -- i.e. its access control is whoever can exec into the running relay container (or its equivalent orchestrator-level access), a boundary this repository's own code does not implement or check."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:678-690"
      - "NOSTR.md:242-245"
  - statement: "Reasoning from the six FACT entries above: the in-community admin tier (relay_members role lookup, scoped to tenant.community()), the deployment operator tier (RELAY_OPERATOR_PUBKEYS allowlist, checked independently of any relay_members row), and the buzz-admin CLI/container tier (no Buzz-internal identity check at all) are three separate authority checks with no call path in this codebase that promotes a grant in one tier into a grant in another -- an admin/owner role in one community does not appear anywhere in authorize_operator_request's logic, and operator-allowlist membership does not appear anywhere in execute_relay_admin_command's role lookup."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:60-102"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:223-252"
      - "crates/buzz-admin/src/main.rs:452-470"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:1-26"
    confidence: 0.8
  - statement: "Issue #1168 (parent PRD #607) asks this node to document layers/security/admin-boundary.md as 'the line between admin/operator-level control and everything else,' framed as what's on each side of the boundary, what crossing it means, and what's at risk -- distinct from #1038's sibling layers-authorization-operator-authorization node, which will cover the authorization *mechanism* rather than this security-boundary framing, and which does not exist on disk in this worktree as of commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1168"
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: implements
    target: corpus-template-invariant
---

# Admin boundary: invariant

A grant of authority in one of Buzz's three administrative tiers --
in-community admin/owner role, deployment-wide relay-operator allowlist, or
host/container-level access to the `buzz-admin` CLI -- never confers
authority in another tier. Each tier is checked by a separate, independent
mechanism, and no code path in this repository promotes a grant from one
tier into a grant in another.

## Scope

This binds every request that reaches one of the three tiers' enforcement
points, at the moment that enforcement point runs:

- **In-community admin** -- Nostr kinds 9030 (add member), 9031 (remove
  member), 9032 (change role), 9033 (set workspace profile/icon), handled by
  `execute_relay_admin_command`. The check is `sender_role` looked up from
  `relay_members` for `tenant.community()` -- the single community the
  request's `TenantContext` was already resolved to before this handler ever
  runs. This tier binds every externally-visible outcome of those four
  kinds; it does not bind, and cannot see, any other community's roster.
- **Deployment operator** -- `POST /operator/communities`,
  `/operator/communities/archive`, `/operator/communities/unarchive`,
  `/operator/communities/transfer`, and the two `GET` listing/availability
  endpoints, all gated by `authorize_operator_request`. This tier binds the
  creation of tenancy itself (and archival, unarchival, and ownership
  transfer of a community, and cross-tenant listing by owner pubkey) --
  operations that structurally cannot be scoped to a single community's
  roster, because their effect is on the roster of communities as a whole.
- **`buzz-admin` CLI / container access** -- every subcommand of the
  `buzz-admin` binary (`add-member`, `remove-member`, `list-members`,
  `generate-key`, `migrate`, `product-feedback`, `deletions`,
  `reconcile-channels`), reachable by anyone who can execute it with
  `RELAY_URL` and DB/Redis connectivity pointed at a target deployment --
  in practice, `docker compose exec relay buzz-admin ...` in the documented
  production workflow. This tier binds direct DB/Redis mutation of relay
  membership and moderation-adjacent state, with no Buzz-internal caller
  identity involved at all.

Crossing a tier boundary means acting with a *different* authority than the
one just checked -- e.g. an in-community admin's role row is irrelevant to
whether `/operator/communities` admits them, and operator-allowlist
membership is irrelevant to whether `execute_relay_admin_command` admits
them for any given community.

## Enforcement today

- **In-community tier: predicate-enforced, scoped by construction.**
  `execute_relay_admin_command` reads `sender_role` from one
  `get_relay_member(tenant.community(), sender_hex)` call and branches on it
  per kind (e.g. kind:9030 requires `admin` or `owner`; granting `admin`
  itself requires `owner`). `tenant.community()` is fixed before this
  function runs, so the query is structurally incapable of reading another
  community's roster -- there is no community parameter it could be handed
  instead. `handle_relay_admin_event` additionally wraps the whole command in
  a durable-ban predicate (`admits_relay_admin_command`) that fails closed on
  a DB error, specifically because `ingest_event`'s normal write-path
  restriction gate exempts these four kinds so a timed-out admin can still
  administer -- the ban check is what stops that exemption from also
  admitting a banned one.
- **Deployment-operator tier: allowlist-enforced, fail-closed on
  misconfiguration.** `authorize_operator_request` checks a NIP-98-verified
  pubkey against `state.config.relay_operator_pubkeys` -- a `Vec<String>`
  populated once at startup from `RELAY_OPERATOR_PUBKEYS`, with any
  malformed entry refusing the whole process to start rather than being
  dropped, and provisioning disabled outright (empty allowlist) when the
  variable is unset. No `relay_members` lookup, and no request `Host`
  header, enters this decision.
- **`buzz-admin` CLI / container tier: convention-and-deployment-access
  only -- no Buzz-internal enforcement exists.** No subcommand in `main.rs`'s
  `Command` enum authenticates a caller; `buzz_auth` is a declared dependency
  but is never invoked from this binary's command path. The only gate is
  whatever controls who can reach a shell with `RELAY_URL` set to the target
  relay and DB/Redis network access -- container/orchestrator access
  control, entirely outside this repository's own authorization code.

## Consequence of violation

- **In-community tier collapsing** (e.g. a role check reading the wrong
  community, or the ban gate being skipped) reproduces exactly the
  regression `regression_relay_admin_ban_gate.rs` exists to catch: a banned
  admin mutating `relay_members` -- the same table `moderation_authz`
  derives moderator capability from -- until a human manually deletes the
  row, and `execute_relay_admin_command`'s own doc calls the ban gate
  precisely the thing standing between that exemption and a banned actor
  regaining administrative capability.
- **Deployment-operator tier collapsing** (e.g. `authorize_operator_request`
  accepting an unlisted pubkey, or falling back to a default when
  `RELAY_OPERATOR_PUBKEYS` is unset instead of disabling provisioning) would
  let an arbitrary NIP-98-capable caller create, archive, unarchive, or
  transfer ownership of *any* community on the deployment -- a
  cross-tenant compromise, not a single-community one.
- **`buzz-admin` CLI tier collapsing** is not a code regression to test for,
  because no code enforces it today: the actual risk is organizational --
  container/orchestrator access broader than intended -- and this document
  is the record that Buzz's own code provides zero defense-in-depth here.
  There is no test to cite because there is no enforcement to test.

## Boundary

This node does not describe:
- **The wording of MUST/SHOULD language inside corpus prose** -- a corpus
  authoring-standard concern, not a claim about Buzz's runtime behavior.
- **The full authorization *mechanism*** (how `relay_members` rows are
  created, how roles map to capabilities, NIP-29/NIP-43 role semantics in
  general) -- that is `layers-authorization-operator-authorization`'s
  territory (issue #1038, PR #1805), which does not exist on disk in this
  worktree as of the recorded revision and so is not a valid relationship
  target here yet.
- **The tenant/community boundary itself** (how a request's community is
  resolved from its Host header, and why that resolution cannot be
  client-supplied) -- `architecture-principles-community-is-security-boundary`
  owns that; this node assumes it and describes a boundary that sits
  *above* it (the operator tier) and *within* it (the in-community tier).
- **A general fail-closed-authorization policy statement** --
  `architecture-principles-fail-closed-boundaries` owns that as a
  system-wide principle; this node cites it as the pattern the operator
  tier's empty-allowlist default follows, not as this node's own subject.
- **Whether the `buzz-admin` CLI tier *should* someday gain Buzz-internal
  enforcement** -- a product decision this node does not make.

## Relationships

- references: `architecture-principles-community-is-security-boundary`
- references: `architecture-principles-fail-closed-boundaries`
- implements: `corpus-template-invariant`

## Scope and omissions

**This node covers** the three-tier admin/operator authority boundary in
Buzz's relay -- in-community admin role, deployment-wide operator allowlist,
and `buzz-admin` CLI/container access -- stating that a grant in one tier
never confers a grant in another, naming each tier's actual enforcement
mechanism (or its absence), and naming the concrete consequence if any tier
boundary were to collapse.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The authorization mechanism's full shape (role semantics, NIP-29/NIP-43 details) | `layers-authorization-operator-authorization` (#1038, not yet drafted) |
| The tenant/community boundary itself | `architecture-principles-community-is-security-boundary` |
| Fail-closed authorization as a general principle | `architecture-principles-fail-closed-boundaries` |
| MUST/SHOULD wording inside corpus prose | corpus normative-language standard |
| Whether `buzz-admin` CLI access should gain in-repo enforcement | Not a documentation decision |

**Expected but not verified when this node was written:**
- **No live deployment was exercised.** Every claim above is drawn from
  reading source and existing prose documentation (`ARCHITECTURE.md`,
  `NOSTR.md`), not from running `docker compose exec relay buzz-admin ...`
  or a live `/operator/communities` request against a real relay.
- **Whether any other HTTP surface implicitly trusts an operator- or
  admin-tier grant** beyond the call sites cited above was not exhaustively
  swept; the evidence here covers the four files most directly named by the
  boundary (`operator.rs`, `relay_admin.rs`, `community_provisioning.rs`,
  `buzz-admin/src/main.rs`) rather than every HTTP handler in the relay.
- **Whether `layers-authorization-operator-authorization` (#1038), once
  drafted, will `references` this node or the reverse** is left to that
  task, since it does not exist yet.
