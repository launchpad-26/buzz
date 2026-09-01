---
id: capabilities-communities-community-discovery
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
  - statement: "A relay host resolves to exactly one community: `bind_community` normalizes the request's Host header and resolves it through a `HostResolver`, failing closed on an unmapped host or a lookup error with no default or fallback community; the `communities` table backs this with a UNIQUE INDEX on `lower(host)`, so there is no server-side notion of 'search across communities' -- a client must already know, or be told, which host it wants."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
      - "migrations/0001_initial_schema.sql"
  - statement: "The NIP-11 relay-information document (`GET /` with `Accept: application/nostr+json`) is served before host binding and stays fail-open: an unmapped host still receives the document, with host-scoped fields such as the community `icon` simply absent, so the document itself cannot be used to enumerate which hosts are mapped to a community on a deployment. Where a host is mapped, `RelayInfo` carries the community's `name`, `description`, and an optional `icon` set by relay admins via the kind:9033 command."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "The NIP-05 identity endpoint (`GET /.well-known/nostr.json`) is explicitly commented as 'a public discovery endpoint' but is host-bound through the same `bind_community` call before any lookup, and an unmapped host or a mapped host with no matching name both fall through to the identical empty `{\"names\": {}, \"relays\": {}}` response -- so this endpoint discovers a named user's pubkey within an already-known community, and does not itself reveal which hosts have a community configured."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs"
  - statement: "Buzz ships no community directory or search: the desktop client's add-community dialog offers exactly two entry points -- 'Create a new community' (opens the Builderlab web flow) and 'Join an existing community' -- and the join path's only input is a community URL or invite link the user already has, with no browse/list/search affordance anywhere in that dialog."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/ui/AddCommunityDialog.tsx"
  - statement: "The join input is parsed into one of three accepted shapes: an `https(s)://<relay>/invite/<code>` URL, a `buzz://join?relay=<wsUrl>&code=<code>` OS-level deep link, or a bare invite code with no relay component (the caller supplies the relay separately); credentials or a URL fragment smuggled into either URL form are rejected rather than silently dropped."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/inviteHelpers.ts"
      - "desktop/src/shared/api/parseInviteInput.test.mjs"
  - statement: "A user may also add a community by relay URL alone, with no invite code: `normalizeRelayUrl` coerces a bare hostname or an `http(s)://` input into `ws(s)://` form (e.g. `https://x` to `wss://x`, a scheme-less host assumed secure), which the add-community 'join' path accepts directly when the input does not parse as an invite."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/relayProbe.ts"
      - "desktop/src/features/communities/relayProbe.test.mjs"
  - statement: "Before completing a join, the client fetches the target relay's join policy -- an age-attestation requirement plus optional Terms-of-Service and Privacy-Policy Markdown -- via `GET /api/join-policy` (webview transport) or the `fetch_join_policy` Tauri command (native transport), and the join/connect submit button stays disabled until any required age confirmation and terms/privacy agreement are checked; a relay predating join-policy support (`HTTP 404`) is treated as having no policy rather than blocking the join."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/invites.ts"
      - "desktop/src/features/onboarding/ui/InviteRedeemForm.tsx"
      - "crates/buzz-relay/src/api/invites.rs"
      - "crates/buzz-relay/src/router.rs"
  - statement: "The relay's join-policy endpoint and its end-to-end gating are exercised by a dedicated test, `join_policy_gate_end_to_end`, and the Terms/Privacy standalone HTML pages the desktop client links out to in the system browser are exercised by `join_policy_document_pages_serve_configured_markdown`, both in the same handler module as the routes themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs"
  - statement: "The Flutter mobile app follows the identical manual, URL-anchored model: `CommunityListNotifier.addCommunity` takes a `Community` value carrying a `relayUrl` directly, updates an existing entry sharing that same `relayUrl` instead of creating a duplicate, and has no directory/search step of its own."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_provider.dart"
  - statement: "No subcommand naming 'invite' appears anywhere under `crates/buzz-cli/src/commands/`, so `buzz-cli` -- the agent-facing CLI -- carries no join/invite-community command family; community discovery and joining, as built today, is a human-facing desktop/mobile onboarding flow, not an agent-facing one."
    entry_class: FACT
    evidence:
      - "grep_recursive(pattern='invite', scope='crates/buzz-cli/src/commands/*.rs') -> no matches, run against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #733's definition of done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#733 definition of done"
relationships:
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-containers-relay
  - type: implements
    target: corpus-template-capability
---

# Community discovery: capability

Buzz lets a user or agent locate and join a specific community it does not yet
belong to, using only a community URL or an invite link -- never a searchable
directory. Because a relay host maps to exactly one community
(`architecture-principles-host-selects-community`), "discovering a community"
in Buzz is inherently "learning one host", not browsing a catalog: a client
that has a host learns the community's public identity from that host's own
NIP-11 document, and joins either directly (a public community) or by
redeeming an invite code the host verifies. This is the capability every
desktop and mobile "Add community" / "Join an existing community" surface is
built on.

## Maturity

**Shipped.** Every mechanism named below is real, merged code, not a design
proposal: `bind_community`'s host resolution, the NIP-11 and NIP-05 handlers,
the desktop `AddCommunityDialog` → `InviteRedeemForm` flow with its
`parseInviteInput`/`normalizeRelayUrl` parsers, the relay's `/api/join-policy`
family of routes with a passing end-to-end gate test
(`join_policy_gate_end_to_end`), and the mobile app's equivalent
`addCommunity(relayUrl)` path. See the evidence ledger above for each
component's source and, where present, its test.

## Behavioral rules and variants

- **One host, one community, no cross-host search.** `req.community =
  resolve_host(connection.host)` is resolved once per request and never
  overridden by client-supplied data. There is no relay-side endpoint or
  client-side feature that lists or searches communities across hosts --
  discovery is always anchored on a single host the user already has.
- **Two ways in: create or join.** The desktop/mobile "Add community" surface
  offers exactly two paths -- create a new hosted community (out of scope
  here; a separate Builderlab web flow) or join an existing one. Only the
  join path is this capability's subject.
- **Three accepted join-input shapes.** An invite-style URL
  (`https(s)://<relay>/invite/<code>`), an OS-level deep link
  (`buzz://join?relay=<wsUrl>&code=<code>`), or a bare relay URL/hostname with
  no invite code at all (normalized to `ws(s)://` and connected to directly,
  for a community that accepts unsolicited joins). A bare invite *code* with
  no relay component is also accepted where the surface already has a default
  relay to pair it with (for example, redeeming a fresh invite while already
  inside a community).
- **NIP-11 identifies a host to the user; it is not a membership check.** The
  relay-information document is deliberately served *before* host binding and
  stays fail-open specifically so it cannot be used to probe which hosts on a
  deployment have a community configured -- an unmapped host gets the same
  document shape with community-specific fields simply absent, never a
  distinguishable rejection.
- **NIP-05 mirrors that non-enumerable design one level in.** Once a host is
  known to map to a community, looking up a specific handle
  (`name@host`) on it still returns the identical empty response whether the
  host is unmapped or the community exists but the name does not -- the
  lookup can confirm a *hit*, never rule a host in or out by its failure
  shape.
- **A configured join policy gates the join, not the discovery.** If the
  target relay has a join policy configured (age attestation and/or
  Terms/Privacy documents), the client must fetch and the user must accept it
  before the join call is made; a relay with no policy configured (or one
  predating this feature, surfaced as `HTTP 404`) imposes no such gate. This
  check runs against the relay's process-wide `join_policy` configuration,
  not through a per-community `bind_community` resolution the way NIP-11/NIP-05
  are -- see *Scope and omissions* for what that leaves unverified in a
  multi-community deployment.
- **This is a human-onboarding flow today, not an agent-facing one.** No
  `buzz-cli` subcommand performs an invite lookup, join-policy fetch, or
  community join; an AI agent operating through `buzz-cli` joins a community
  only in the sense that its operator has already provisioned it into one
  (via `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY`), not by discovering one itself.

## Boundary

This node does not describe:
- **How a host resolves to a community, or why that binding is
  fail-closed and non-overridable** -- that invariant, its enforcement points,
  and its verification are `architecture-principles-host-selects-community`'s
  subject; this node only relies on it (a client must already have, or
  acquire, the one host that names the community it wants).
- **Why a community is Buzz's security/tenancy boundary** -- that is
  `architecture-principles-community-is-security-boundary`'s subject. This
  node references it because the same host-anchoring the security boundary
  relies on is exactly why community *discovery* has no cross-host search
  surface to build on.
- **The interface contracts** (HTTP route shapes, CLI command groups) that
  expose the mechanisms named here in full -- no dedicated `interfaces`-type
  corpus node for the relay's public HTTP surface or `buzz-cli` exists yet to
  reference; this node cites the concrete handler and client files directly
  instead.
- **The step-by-step flow of one join** (exact request/response sequence, in
  order, for a single onboarding session) -- no `flow`-type corpus node
  exists yet for this journey; this node states the capability and its
  rules, not a numbered sequence diagram.
- **How the relay or its communities are operated** (provisioning, backups,
  incident response) -- an `operations`-type concern, not addressed here.
- **Community *creation*** (the Builderlab hosted-community flow reached from
  the same dialog's "Create" option) -- a distinct capability from joining an
  existing one, out of scope for this node.

## Relationships

- references: `architecture-principles-host-selects-community` -- the
  host-to-community binding this capability's entire "one host, one
  community" shape depends on.
- references: `architecture-principles-community-is-security-boundary` -- the
  security invariant that explains why this capability has no cross-host
  search surface to build on.
- references: `architecture-containers-relay` -- the container that serves
  every relay-side mechanism cited above (NIP-11, NIP-05, `/api/join-policy`,
  `/api/invites/claim`).
- implements: `corpus-template-capability` -- the template this node's shape
  follows (Capability statement / Maturity / Boundary / Relationships / Scope
  and omissions).

## Scope and omissions

**This node covers** how a Buzz client (desktop or mobile) locates and joins
a specific community it does not yet belong to: the absence of a
directory/search surface, the three accepted join-input shapes, what NIP-11
and NIP-05 do and do not reveal about which hosts have a community, and the
join-policy gate a configured relay can impose before a join completes.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The host-to-community binding invariant itself | `architecture-principles-host-selects-community` |
| Why a community is the security boundary | `architecture-principles-community-is-security-boundary` |
| The relay's HTTP interface contract in full | no `interfaces` node yet for this surface |
| The step-by-step join flow, request by request | no `flow` node yet for this journey |
| Community *creation* (Builderlab hosted flow) | a separate capability, not this node |
| How communities/relays are operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- **Whether `/api/join-policy` resolves per-community in a multi-host
  deployment, or reads one process-wide configuration shared by every
  community on that relay process.** The handler reads `state.config.join_policy`
  directly and was not observed calling `bind_community` the way the NIP-11
  and NIP-05 handlers do; this node states what the handler does, not what a
  multi-community deployment's operator-facing configuration surface allows
  per community, which was not traced further.
- **Whether the `buzz://` custom URL scheme is registered with the OS on
  every platform Buzz ships (macOS, Windows, Linux, iOS, Android).**
  `inviteHelpers.ts` parses a `buzz://join` URL once handed one, but the
  platform-level scheme registration that causes the OS to hand it to Buzz
  at all was not inspected.
- **Whether any non-onboarding, in-app surface (for example a workflow or
  webhook) can also trigger a community join.** Only the desktop
  `AddCommunityDialog` → `InviteRedeemForm` path and its mobile equivalent
  were inspected; a second entry point, if one exists, was not searched for
  exhaustively.
