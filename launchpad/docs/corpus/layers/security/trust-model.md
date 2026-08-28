---
id: layers-security-trust-model
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
  - statement: "The relay operator level is authorized by a fixed, deployment-configured pubkey allowlist: authorize_operator_request checks the NIP-98-authenticated pubkey against state.config.relay_operator_pubkeys (RELAY_OPERATOR_PUBKEYS) and returns 403 'actor not authorized: not a relay operator' for any pubkey not on that list, with a separate NIP-98 replay guard (check_operator_replay) that fails closed on a DB error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "The operator module's own header states these routes are 'outside the Nostr event data plane' -- they use NIP-98 request signing and replay protection but do not run through event ingest, relay membership, channel scoping, storage, or fan-out -- and cover community lifecycle: provision_community (create a host and bootstrap its initial owner), archive_community / unarchive_community, list_owned_communities, and transfer_community, whose own doc comment states the previous owner is demoted to member, not admin, on transfer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "Community owner and community admin are the two tenant-scoped relay_members.role values that authorize_moderation_action recognizes; its own doc comment states 'community owner/admin (tenant-scoped relay_members.role) are authorized for every ModerationAction in any channel of their community,' and the module header states there is no separate Moderator tier in v1."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "decide_authority grants the owner every ModerationAction with no guard rail, but an admin performing Ban or Timeout against a target whose own relay_members.role is 'owner' or 'admin' is rejected with 'an admin cannot ban or time out a community owner or fellow admin' -- the guard is scoped to Ban/Timeout only and does not apply to Unban/Untimeout, which the source comment states is intentional because a banned actor is already rejected on every transport before reaching this seam."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "A community member -- an actor with no owner/admin relay_members row and no channel-level owner/admin role -- is denied every ModerationAction: decide_authority's final match arm returns 'moderator access required' for any actor that is not a community owner/admin and not a channel owner/admin performing DeleteMessage or Kick; the enum's own doc comment states plainly that 'members hold none' of the eight moderation capabilities."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "An agent proves its own identity through the same NIP-42 challenge/response every other WebSocket connection uses -- a Schnorr-signed kind:22242 event -- verified by verify_nip42_event and gated by handle_auth's ban/allowlist/relay-membership checks; there is no separate agent credential type or agent-specific authentication path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "An agent's identity is distinguished from its human owner's by a NIP-OA 'auth' tag carried inside that same signed AUTH event: handle_auth's source comments state the ban cascade explicitly -- 'a ban on the authenticated pubkey blocks it directly; a ban on its cryptographically-proven owner cascades to the agent (owner ban => agents banned; agent ban is agent-only)' -- and the module doc states relay-membership enforcement supports a NIP-OA owner-delegation fallback so an agent can authenticate on its owner's behalf."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "NIP-PMA (private_managed_agent.rs) defines an owner-encrypted wire format for an agent's own configuration: build_event's payload carries an owner_pubkey field that is checked against the signing key ('owner_pubkey does not match signing key' otherwise), and validate_and_decrypt uses nip44::decrypt so only the owner's own key can read the plaintext; the module's own top-of-file doc comment states relays must not accept KIND_PRIVATE_MANAGED_AGENT until dedicated privacy and aggregate-CAS transactions are deployed, so this format is defined but not yet a live trust boundary."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/private_managed_agent.rs"
  - statement: "An agent's own runtime binary is a further, distinct trust question from the agent's Nostr identity: buzz-acp's Bring Your Own Harness model tiers a harness executable as compiled-in (goose/claude/codex/buzz-agent, auto-installers and auth probes), preset (PATH-probed only, 'not editable or deletable by the user'), or custom (a user-supplied JSON file naming an arbitrary command); its own 'Security guarantees' section states no install shell commands ever run, can_auto_install is always false for preset and custom entries, there are no user-supplied icon URLs, and BUZZ_MANAGED_AGENT and other Buzz identity keys 'cannot be overridden by env in a custom definition; they are stripped before merging.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "Buzz's own Blossom media server is one instance of the external-provider level: verify_blossom_auth_event_for_verb requires a kind:24242 event with a valid Schnorr signature, a t tag matching the verb (upload/get), a future expiration tag, a created_at within a 5-second clock-skew tolerance, and -- when server tags are present -- this deployment's own domain named in at least one of them; the function's doc comment states explicitly to call it 'BEFORE trusting the event's pubkey for scope resolution.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "A second external-provider surface is a workflow's own webhook action, which calls out to an operator-configured external HTTP endpoint: buzz-workflow's executor resolves the target host via the OS resolver and rejects the request with a 'SSRF blocked' WorkflowError if any resolved address is private or reserved, checked with buzz_core::network::is_private_ip -- the only caller of that function outside buzz-core's own tests -- and buzz-core's is_private_ip doc comment states its purpose is exactly this: 'webhook targets must not resolve to these addresses.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-core/src/network.rs"
  - statement: "Every trust decision documented in this node -- the operator allowlist check, the community owner/admin/member role read, the agent's own NIP-42 identity proof, and the ban/allowlist/membership gates the WebSocket-authentication flow runs -- resolves inside a community that is itself bound solely from the connection's Host header before any of those checks run; the community-is-security-boundary principle node states this as its own invariant and names bind_community as the single seam every request surface calls."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
  - statement: "The relay-operator level is architecturally outside that host-derived community binding rather than scoped by it: the operator module's own header states its routes 'do not run through event ingest, relay membership, channel scoping, storage, or fan-out,' and authorize_operator_request authenticates against a fixed relay_operator_api_origin rather than any inbound Host header or resolved TenantContext -- so the operator level is deployment-root authority, checked once against configuration, not a role inside any one community."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
    confidence: 0.75
  - statement: "Issue #1182 ('task: document layers/security/trust-model.md', parent Feature #607) frames this node's subject as WHO/WHAT is trusted at each level -- relay operator, community admin, community member, agent, external provider -- and states this is distinct from sibling issue #1181's trust-boundaries node, which maps the process boundaries themselves rather than the actors and their granted authority."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1182 objective and definition of done, relayed via the corpus-doc batch dispatch brief for tasks under parent Feature #607"
  - statement: "What each trust level protects is a synthesis reasoned from the same authorization source read for the rest of this node, not a separately documented 'asset' concept in the codebase: the relay operator's asset (the deployment's community registry) follows from operator.rs's provision/archive/transfer surface; the community owner/admin/member asset (one community's content and membership) follows from moderation_authz.rs's tenant-scoped role grants; and the agent asset (the owner/agent ban-cascade distinction) follows from handle_auth's cascade logic -- each already cited above as FACT, with this entry covering only the framing that groups them as 'what is protected.'"
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
    confidence: 0.7
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-flows-websocket-authentication
---

# Security: trust model

Who and what Buzz's relay grants authority to, at each of five levels -- relay
operator, community owner/admin, community member, agent, and external
provider -- and the mechanism that establishes each one's identity and the
extent of what it is trusted to do. This is a **who/what** document: it names
the actors and the boundary of their granted authority. It is deliberately
not a map of the process/data-flow boundaries those actors cross (sibling
issue #1181's `trust-boundaries.md`, not yet on disk) and not an
attacker-perspective enumeration of what could go wrong at each boundary
(sibling issue #1180's `threat-model.md`, not yet on disk). Both are named
here in prose only, per this task's own instructions, since neither file
exists in this corpus yet to link.

## Scope, assumptions, and what each level protects

**Scope.** This node covers every actor that can reach the relay's own
authorization seams: the deployment operator, the two tenant-scoped
community roles, an unprivileged member, an agent process, and the external
systems the relay itself calls out to or accepts signed requests from. It
stops at the boundary of the relay's own process -- what a client
application does with the authority it is granted (for example, how Buzz
Desktop renders a moderation action) is out of scope.

**Assumptions.** Every level above the relay-operator allowlist assumes the
host-derived community binding documented in
`architecture-principles-community-is-security-boundary` continues to hold --
that `bind_community` is the sole seam producing a `TenantContext`, and that
no request surface bypasses it. This node's own claims about community
owner/admin/member/agent authority are read directly from
`decide_authority` and `handle_auth`; they assume those functions are the
only path by which a moderation decision or an authentication decision is
made, which is what each module's own "one seam" doc comment states, cited
throughout this node.

**What each level protects (its asset).** The relay operator level protects
the *deployment's own community registry* -- which hosts exist and who owns
them. Community owner/admin protect *one community's own content and
membership* -- messages, channel membership, and who else may act inside it.
Community member is the baseline: it protects nothing beyond the member's
own identity claim (its role read returns no elevated capability). Agent
protects the *distinction between an agent's own actions and its owner's
standing* -- specifically, that an agent's misbehavior does not, by itself,
implicate its owner (the ban cascade runs owner-to-agent only, never the
reverse). External provider protects the *relay's own internal network and
media-serving surface* from being reached or impersonated by an unauthenticated
or redirected external request.

## Trust levels at a glance

| Level | Identity proof | Scope of granted authority | Enforcement point |
|---|---|---|---|
| Relay operator | NIP-98 request signed by a pubkey in a fixed allowlist (`RELAY_OPERATOR_PUBKEYS`) | Deployment-root: create/archive/transfer any community on this deployment | `authorize_operator_request` (`crates/buzz-relay/src/api/operator.rs`) |
| Community owner | `relay_members.role = 'owner'` inside one community | Every moderation capability in that community, unrestricted, including actioning admins | `decide_authority` (`crates/buzz-relay/src/handlers/moderation_authz.rs`) |
| Community admin | `relay_members.role = 'admin'` inside one community | Every moderation capability in that community, except it cannot Ban/Timeout the owner or a fellow admin | `decide_authority`, same file |
| Community member | Authenticated pubkey with no owner/admin role, and (for channel-local actions only) an optional channel owner/admin role | None community-wide; channel owner/admin get `DeleteMessage`/`Kick` in their own channel only | `decide_authority`, same file |
| Agent | The same NIP-42 proof as any pubkey, optionally carrying a NIP-OA `auth` tag naming a human owner | Whatever its own pubkey's community role grants; a ban on its NIP-OA owner cascades to it (not the reverse) | `handle_auth` (`crates/buzz-relay/src/handlers/auth.rs`) |
| External provider | Per-surface: a signed Blossom kind:24242 event, or a workflow-configured webhook URL resolved and SSRF-checked at dispatch time | Only what that one signed request or dispatch explicitly authorizes; never ambient trust in the provider itself | `verify_blossom_auth_event_for_verb` (`crates/buzz-media/src/auth.rs`); the webhook resolver in `crates/buzz-workflow/src/executor.rs` |

## Relay operator

The relay operator level is deployment-root authority, not a role inside any
one community. `authorize_operator_request` checks the NIP-98-authenticated
pubkey against a fixed, deployment-configured allowlist
(`state.config.relay_operator_pubkeys`, sourced from `RELAY_OPERATOR_PUBKEYS`)
and rejects any pubkey not on that list with `403 actor not authorized: not a
relay operator`, guarded by a separate NIP-98 replay check that fails closed
on a DB error. The operator module's own header states these routes are
"outside the Nostr event data plane" -- they authenticate with NIP-98 but do
not run through event ingest, relay membership, channel scoping, storage, or
fan-out, and they authenticate against a fixed `relay_operator_api_origin`
rather than any inbound `Host` header. This deployment-root shape is why the
level sits outside the host-derived community binding every other level below
is scoped by (see *Relationships*).

What this level is trusted to do: `provision_community` (create a community
host and atomically bootstrap its initial owner), `archive_community` /
`unarchive_community`, `list_owned_communities`, and `transfer_community` --
whose own doc comment states the previous owner is demoted to `member`, not
`admin`, on transfer, so a completed transfer leaves no residual admin-level
authority with the old owner.

## Community owner and community admin

Both are values of the tenant-scoped `relay_members.role` column, and both
route through one authorization seam, `authorize_moderation_action` /
`decide_authority`. The module's header states there is no separate
Moderator tier in v1 -- "all authorization routes through
`authorize_moderation_action` so adding one later is a policy change, not a
rewrite" -- and its `ModerationAction` enum names eight capabilities: delete
any message, kick, ban, unban, timeout, untimeout, resolve/dismiss/escalate
moderation-queue reports, and view the queue/audit log.

**Owner** holds every one of those eight, community-wide, with no guard
rail -- `decide_authority`'s `Some("owner")` arm returns unconditionally, even
against a target whose own role is admin.

**Admin** holds the same eight, with one guard rail: `decide_authority`
rejects an admin's `Ban` or `Timeout` action when the *target's* role is
`owner` or `admin`, returning "an admin cannot ban or time out a community
owner or fellow admin." The guard is scoped narrowly -- it does not cover
`Unban`/`Untimeout` -- and the source comment explains why that is
intentional rather than an oversight: a banned actor is already rejected on
every transport before reaching this authorization seam, so the only
reachable case is an unrestricted admin lifting another admin's own
restriction, which the comment calls "benign, audited, and owner-reversible."

Community-role authority never crosses the tenant boundary: the module's own
"Tenant invariant" section states the actor's role is read from
`relay_members` under `tenant.community()` only, and callers must have
already resolved the moderation target inside that same tenant.

## Community member

A community member is an authenticated pubkey holding no owner/admin
`relay_members` row. `decide_authority`'s final match arm denies every
community-wide `ModerationAction` for such an actor with "moderator access
required," and grants only `DeleteMessage`/`Kick` when the actor separately
holds an owner/admin role on the specific channel the target belongs to --
authority that is channel-local, not community-wide. The `ModerationAction`
enum's own doc comment states this plainly: "members hold none" of the eight
capabilities.

## Agent

An agent proves its own identity through exactly the same mechanism as any
other connection: a Schnorr-signed NIP-42 (kind:22242) challenge/response,
verified by `verify_nip42_event` and gated by `handle_auth`'s ban, allowlist,
and relay-membership checks. There is no separate agent credential type --
what makes a pubkey "an agent" in Buzz's trust model is not a different proof
mechanism, but an optional NIP-OA `auth` tag riding inside that same signed
AUTH event, naming a human owner pubkey the agent claims to act for.

That claim is integrity-protected by the same Schnorr signature covering the
rest of the event (a forged or duplicated `auth` tag is treated as no valid
tag at all), and it changes exactly one thing observed directly in
`handle_auth`'s own source comments: the ban cascade. "A ban on the
authenticated pubkey blocks it directly; a ban on its cryptographically-proven
owner cascades to the agent (owner ban => agents banned; agent ban is
agent-only)." An owner's ban reaches every agent claiming to act for them; an
agent's own ban reaches only that agent. `enforce_relay_membership` separately
supports a NIP-OA owner-delegation fallback, so an agent can satisfy a
closed-relay membership check on its owner's behalf.

Two further, narrower trust questions sit beside that identity proof:

- **The agent's own configuration.** NIP-PMA (`private_managed_agent.rs`)
  defines a wire format where an agent's private configuration is encrypted
  to its owner's key with NIP-44 (`build_event` checks the payload's
  `owner_pubkey` against the signing key; `validate_and_decrypt` calls
  `nip44::decrypt`, so only the owner's own key can read the plaintext). This
  format is **defined but not yet a live trust boundary**: the module's own
  top-of-file doc comment states relays must not accept
  `KIND_PRIVATE_MANAGED_AGENT` until dedicated privacy and aggregate-CAS
  transactions are deployed.
- **The agent's own runtime binary.** Which *executable* Buzz Desktop spawns
  to run an agent is a distinct question from the agent's Nostr identity,
  covered by `buzz-acp`'s Bring Your Own Harness model: compiled-in runtimes
  (goose, Claude Code, Codex, Buzz Agent) get auto-installers and auth
  probes; preset-catalog runtimes are PATH-probed only and "not editable or
  deletable by the user"; user-custom harnesses are an arbitrary
  user-supplied command. Across all three tiers, the README's own "Security
  guarantees" section states: no install shell commands ever run,
  `can_auto_install` is always `false` for preset and custom entries, there
  are no user-supplied icon URLs, and `BUZZ_MANAGED_AGENT` and other Buzz
  identity keys "cannot be overridden by `env` in a custom definition; they
  are stripped before merging" -- so a third-party harness binary can be
  spawned with Buzz's own identity keys, but it can never override which
  identity those keys assert.

## External provider

Buzz does not extend ambient trust to an external system as a category; each
surface that talks to something outside the relay's own process re-proves
authorization per request or per dispatch, in a way scoped to that one
interaction:

- **Blossom media (BUD-11).** `verify_blossom_auth_event_for_verb` requires a
  kind:24242 event carrying a valid Schnorr signature, a `t` tag matching the
  verb being performed (`upload` or `get`), a future `expiration` tag, a
  `created_at` within a 5-second clock-skew tolerance, and -- when `server`
  tags are present -- this deployment's own domain named in at least one of
  them. Its own doc comment is explicit about ordering: call this "BEFORE
  trusting the event's pubkey for scope resolution." Trust in a Blossom
  request is established by that one signed event, not by any standing
  relationship with a media provider.
- **Workflow webhooks.** A workflow's webhook action calls out to an
  operator-configured external HTTP endpoint. Before dispatching, the
  executor resolves the target host via the OS resolver and rejects the
  request with a `WorkflowError::WebhookError` ("SSRF blocked...") if any
  resolved address is private or reserved, using
  `buzz_core::network::is_private_ip` -- whose own doc comment states its
  purpose is exactly this: "webhook targets must not resolve to these
  addresses." This is the only call site of that function outside
  `buzz-core`'s own unit tests, so it is a narrow, single-purpose
  enforcement point rather than a general egress filter.

## Relationships

This node `references` two existing architecture nodes rather than
duplicating their content:

- `architecture-principles-community-is-security-boundary` -- every
  community-scoped level documented here (owner, admin, member, and an
  agent's own community role) resolves *inside* a community that principle
  node states is bound solely from the connection's Host header, before any
  of the role checks above ever run. This node cites that binding as
  supporting context; it does not restate `bind_community`'s mechanics.
- `architecture-flows-websocket-authentication` -- the ordered NIP-42
  challenge/response steps, and the ban/allowlist/membership gates that run
  immediately after cryptographic verification, are that flow node's own
  subject. This node names the actors those gates decide between; it does
  not re-walk the state machine.

`references` (not `depends-on`) was chosen for both edges: this node's own
claims about *who* holds *what* authority are read directly from the
authorization source files above and do not stop holding if either
referenced node's prose changes -- they would only need re-verification if
the underlying code changed, which is exactly what a `references` edge
signals per `relationships.schema.json` ("source cites target as supporting
context; no ownership or currency dependency implied").

No `relationships` target `layers-security-trust-boundaries` (issue #1181) or
`layers-security-threat-model` (issue #1180): neither file exists on disk in
this worktree, and `AGENTS.md` treats a relationship target that resolves
nowhere as a hard validation error. Both are named in prose above instead,
per this task's own instructions.

## Boundary: what this node is not

- **Not the trust-boundaries map.** This node names the actors and what each
  is trusted to do; it does not enumerate the process/data-flow crossings
  between them (Host-header binding, WebSocket vs. HTTP surfaces, the
  database and Redis boundary, and so on). That is `trust-boundaries.md`
  (issue #1181), not yet on disk.
- **Not a threat model.** This node makes no STRIDE-style claim about what
  could go wrong if a given trust level's controls failed, and it records no
  mitigation-status table. That is `threat-model.md` (issue #1180), not yet
  on disk.
- **Not the full NIP-29 channel-membership and moderation surface.** This
  node covers the roles `authorize_moderation_action` recognizes; it does not
  describe channel invite/join mechanics, `buzz-auth/src/access.rs`'s
  channel-level read/write model, or the moderation-queue/report workflow
  beyond naming `ResolveReport`/`ViewQueue` as capabilities.
- **Not a security-control catalog.** This node names the enforcement point
  for each trust level; it does not restate every control's full mechanics
  (NIP-42's verification steps, Blossom's replay window, SSRF IP-range
  classification) -- those live in their own source files and, where one
  already exists, the referenced architecture node.

## Scope and omissions

**This node covers** the five trust levels named in issue #1182 -- relay
operator, community owner/admin, community member, agent, and external
provider -- each one's identity-proof mechanism, the scope of authority it is
granted, and the code location that enforces that grant.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The process/data-flow trust boundaries between these actors | #1181, `layers/security/trust-boundaries.md` (not yet on disk) |
| An attacker-perspective, STRIDE-style analysis of each boundary | #1180, `layers/security/threat-model.md` (not yet on disk) |
| NIP-42's full verification mechanics and the connection state machine | `architecture-flows-websocket-authentication` (referenced above) |
| The host-derived community-binding mechanism itself | `architecture-principles-community-is-security-boundary` (referenced above) |
| NIP-98 HTTP Auth's own replay-protection mechanics (`nip98_replay.rs`) | Not yet in this corpus |
| The full NIP-29 channel invite/join and membership model | Not yet in this corpus |
| Whether `KIND_PRIVATE_MANAGED_AGENT` has since been enabled for live relay acceptance | Not verified here -- see below |

**Expected but not verified when this node was written:**

- **Whether `KIND_PRIVATE_MANAGED_AGENT` is currently accepted by any live
  relay deployment.** The module doc comment states relays "must not" accept
  it until further transactions are deployed; this node did not check a
  running relay's kind-acceptance configuration to confirm that gate is still
  enforced at the recorded revision, only that the source-level admonition is
  present.
- **Whether every `ModerationAction` in the V1 capability grid has an
  end-to-end test exercising `decide_authority`'s guard rail against a live
  database.** The unit tests in `moderation_authz.rs` exercise the pure
  `decide_authority` function directly (see the file's own `#[cfg(test)] mod
  tests`); this node did not additionally run or trace an integration test
  covering `authorize_moderation_action`'s DB-backed role resolution.
- **Whether any request surface added after this revision correctly
  distinguishes these five levels.** This node documents the mechanism as it
  exists now, not a guarantee that a future authorization seam reuses it
  rather than reinventing a weaker one.
