---
id: operations-administration-membership-management
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "`buzz-admin`'s subcommand set for relay-wide (community) membership is `add-member` (`--pubkey`, `--role`, default role `member`), `remove-member` (`--pubkey`, optional `--role` guard), and `list-members` (no arguments); this was confirmed by building the binary at the recorded revision (`cargo build -p buzz-admin`) and running `--help` against each subcommand, not only by reading the source."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "buzz_admin_help(binary='target/debug/buzz-admin', subcommands=['add-member','remove-member','list-members'], commit='473205a7457b208455f188847bfb27b01aa83cac') -> confirmed subcommand names, flags, and defaults exactly as stated, via --help on the binary itself and on each of the three subcommands"
  - statement: "`buzz-admin add-member`'s role validation rejects `\"owner\"` before any database connection is attempted, printing `error: role 'owner' cannot be set via CLI — use RELAY_OWNER_PUBKEY config` and exiting 1; an invalid pubkey (neither bech32 npub nor 64-char hex) is likewise rejected pre-connection with exit 1."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "buzz_admin_add_member(pubkey='npub1abc', role='owner', commit='473205a7457b208455f188847bfb27b01aa83cac') -> exit 1, stderr \"error: role 'owner' cannot be set via CLI — use RELAY_OWNER_PUBKEY config\"; a second run with pubkey='not-a-valid-key' and no --role -> exit 1, stderr \"error: invalid pubkey ...: Invalid public key\" (both ahead of any DB/Redis connection, per validate_role/parse_pubkey_hex running before connect_member_services in cmd_add_member)"
  - statement: "`buzz-admin`'s own module doc comment states that `add-member`/`remove-member` publish an authoritative kind:13534 membership-list snapshot (not kind:8000/8001 deltas, because the delta publish path is in-process-only and would silently no-op from a `compose exec` sidecar invocation), and that the timestamp bump defeating same-second domination for one process does not serialize two concurrent CLI invocations — `deploy/compose/run.sh`'s own help text tells an operator adding multiple members in a loop to insert `sleep 1` between invocations for exactly this reason."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "deploy/compose/run.sh"
  - statement: "`buzz-admin`'s exit codes are 0 (success), 1 (validation error), 2 (member not found on remove), 3 (cannot remove the relay owner — change `RELAY_OWNER_PUBKEY` and restart instead), 4 (role-filter mismatch on remove), 5 (DB/Redis/internal error), and both `ARCHITECTURE.md` and `NOSTR.md` document the same table alongside the required `DATABASE_URL`/`REDIS_URL`/`BUZZ_RELAY_PRIVATE_KEY` environment variables for member management."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "ARCHITECTURE.md"
      - "NOSTR.md"
  - statement: "In a Docker Compose deployment, `deploy/compose/run.sh` wraps `buzz-admin` as `docker compose exec relay /usr/local/bin/buzz-admin add-member|remove-member|list-members ...`, exposed to the operator as `./run.sh add-member <npub-or-hex> [--role member|admin]`, `./run.sh remove-member <npub-or-hex> [--role member|admin]`, and `./run.sh list-members`; the binary is shipped inside the relay image at that fixed path."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
      - "ARCHITECTURE.md"
  - statement: "Relay-wide membership can alternatively be managed live over the Nostr WebSocket wire, with no shell access to the deployment at all, by an already-authenticated owner or admin signing NIP-43 admin-command events: kind:9030 (add member, tags `p` + optional `role`), kind:9031 (remove member, tags `p` + optional `role`), and kind:9032 (change an existing member's role, tags `p` + `role`, owner-only); `NOSTR.md` gives a worked `nak event -k 9030 --tag \"p=...\" --tag \"role=member\" --auth --sec <owner-or-admin-privkey> ws://localhost:3000` example for each."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
      - "crates/buzz-core/src/kind.rs"
  - statement: "`buzz-admin reconcile-channels` (`--channel <uuid>` optional, `--relay-key` falling back to `BUZZ_RELAY_PRIVATE_KEY`) republishes a channel's kind:39000/39001/39002 discovery snapshot — either every channel missing discovery metadata (no `--channel`) or one targeted channel's kind:39002 member roster only (with `--channel`) — and is the operator's repair tool for a channel roster that live clients are not seeing correctly, distinct from granting or revoking membership itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "buzz_admin_help(binary='target/debug/buzz-admin', subcommand='reconcile-channels', commit='473205a7457b208455f188847bfb27b01aa83cac') -> confirmed the --channel/--relay-key flags and the without-vs-with-channel behavior stated in the subcommand's own doc comment"
  - statement: "Per-channel membership has no `buzz-admin` surface at all; it is managed through `buzz-cli channels {add-member,remove-member,members,join,leave}`, confirmed by building `buzz-cli` at the recorded revision and running `--help` against each subcommand: `add-member` takes `--channel`, `--pubkey`, optional `--role` (owner/admin/member/guest/bot); `remove-member` and `members` take `--channel` (+ `--pubkey` for remove); `join`/`leave` take only `--channel`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "buzz_cli_channels_help(binary='target/debug/buzz', subcommands=['add-member','remove-member','members','join','leave'], commit='473205a7457b208455f188847bfb27b01aa83cac') -> confirmed flag names and requiredness exactly as stated"
  - statement: "`buzz-cli` is a global-flag, not per-subcommand, tool: it reads `BUZZ_RELAY_URL` (default `http://localhost:3000`), `BUZZ_PRIVATE_KEY` (required — hex or nsec, the identity every channel-membership command signs as), and optional `BUZZ_AUTH_TAG`, and reports exit codes 0=ok, 1=bad input, 2=relay/network error, 3=auth error, 4=other, 5=write conflict, printing errors as `{\"error\": \"<category>\", \"message\": \"<detail>\"}` JSON on stderr."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "buzz_cli_help(binary='target/debug/buzz', commit='473205a7457b208455f188847bfb27b01aa83cac') -> confirmed the Configuration/Exit-codes banner verbatim"
  - statement: "Which identity a `buzz-cli channels add-member`/`remove-member` call may successfully execute as is not re-derived here — `capabilities-channels-channel-membership` already states the authorization rule (an elevated actor is required to add/change-to an elevated role, and specifically to remove someone other than themselves without being that member's registered agent owner), enforced independently in both the relay's pre-storage validator and `buzz-db`'s own write path; the operator's job is to hold or obtain a `BUZZ_PRIVATE_KEY` for a pubkey the target channel already recognizes as owner/admin, not to bypass that rule."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/capabilities/channels/channel-membership.md"
  - statement: "A deployment operator (distinct from a community owner/admin) can transfer a community's ownership directly, without needing the current owner's private key at all, via `POST /operator/communities/transfer` — a NIP-98-signed, deployment-global endpoint in `crates/buzz-relay/src/api/operator.rs` requiring the signer's pubkey to be listed in `RELAY_OPERATOR_PUBKEYS`, taking a JSON body of `{community_id, new_owner_pubkey, expected_owner_pubkey}`, and returning `transferred`/`already_owner` on success or 404/409 on a stale `expected_owner_pubkey` or a transferee already at the per-owner community cap."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
      - "crates/buzz-db/src/store/relay_members.rs"
  - statement: "The `/operator/communities/transfer` route's own doc comment and its handler's authorization prelude (`authorize_operator_request`) both confirm the request is verified through `buzz_auth`'s bridge NIP-98 verification (`bridge::verify_bridge_auth_with_options`) against a canonical origin from configuration (`RELAY_OPERATOR_API_ORIGIN`), independent of the request's inbound `Host` header — the same NIP-98 machinery used elsewhere in the relay's HTTP surface, not a bespoke check for this route."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "`RELAY_OPERATOR_PUBKEYS` (comma-separated 64-char hex pubkeys; an invalid entry is a hard config error) and `RELAY_OPERATOR_API_ORIGIN` (an http(s) origin with no path/query/fragment; required whenever `RELAY_OPERATOR_PUBKEYS` is non-empty) are the two environment variables an operator must configure before `/operator/communities/transfer` accepts any request; `layers-configuration-relay-configuration` already documents both variables' full validation semantics and default states, which this node does not re-derive."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/configuration/relay-configuration.md"
      - "crates/buzz-relay/src/config.rs"
  - statement: "`capabilities-communities-community-provisioning` explicitly excludes the `/operator/communities/transfer` (and `/archive`, `/unarchive`, `/availability`) routes from its own scope, naming them 'a future interface- or flow-shaped node, not yet drafted' — confirming that documenting the transfer endpoint's operator-facing procedure here does not duplicate an existing corpus claim."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/capabilities/communities/community-provisioning.md"
  - statement: "`deploy/charts/buzz/README.md`, the Kubernetes/Helm deployment chart's own documentation, names `buzz-admin migrate` as a supported one-shot Job pattern but documents no equivalent `kubectl exec`-based pattern for `add-member`, `remove-member`, `list-members`, or `reconcile-channels` anywhere in the file, established by grepping the file for each subcommand name and for `kubectl exec`."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "Issue #1194's Definition of Done requires this node to be one hand-authored canonical document with schema-valid front matter, one independently maintainable idea, claims traceable to current code/tests/specification/decision/configuration or attributed GitHub evidence, links to relevant implementation/verification/specification/decision and neighboring corpus nodes without duplicating their canonical content, checked against the recorded revision, passing corpus validation, and — as its type-specific tail bullets — a stated goal/prerequisites/scope, executable and project-specific ordered steps, defined success verification and rollback/cleanup, and links to authoritative commands/config rather than generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1194 definition of done"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped body: one-line Overview, optional Before-you-start prerequisites, one numbered action-verb task sequence per logical goal capped near 8-10 steps (forking into lettered sub-sequences when a task genuinely branches), a See-also list deferring lookup completeness to reference/concept nodes, an explicit Boundary paragraph against the reference/tutorial/concept-explanation neighbors, Relationships, and a Scope-and-omissions section separating what the node excludes from what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
relationships:
  - type: references
    target: capabilities-communities-community-members
  - type: references
    target: capabilities-channels-channel-membership
  - type: references
    target: capabilities-communities-community-roles
  - type: references
    target: layers-configuration-relay-configuration
  - type: implements
    target: corpus-template-procedure
---

# Managing community and channel membership: how-to

How an operator adds, removes, lists, and repairs who belongs to a community
(relay-wide membership) and to a channel within it (per-channel membership),
and how a deployment operator transfers ownership of a whole community — the
executable commands and their prerequisites, not the authorization design
those commands enforce.

## Before you start

- **Know which membership you are changing.** Relay-wide (community)
  membership decides whether a pubkey may connect to this community at all;
  channel membership decides whether an already-admitted member may read or
  write in one particular channel. They are separate rosters with separate
  tooling below — see
  [`capabilities-communities-community-members`](../../capabilities/communities/community-members.md)
  and
  [`capabilities-channels-channel-membership`](../../capabilities/channels/channel-membership.md)
  if it is unclear which one a request is actually asking for.
- **Have the target pubkey** as a bech32 `npub1...` or 64-char hex string.
- **Know which tool your deployment gives you shell access to.** A Docker
  Compose deployment ships `./run.sh` and the `buzz-admin` binary inside the
  relay container. A deployment with no shell access at all can still manage
  relay-wide membership live over the Nostr wire (task 1c below) or transfer
  ownership over HTTP (task 3 below), provided the signing identity already
  holds the right role.

## Add, remove, or list relay-wide (community) members

1. **Choose a role.** `member` or `admin` — `buzz-admin`'s own validation
   refuses `owner`; the owner role is set only via the `RELAY_OWNER_PUBKEY`
   deployment config variable (applied on the next relay restart) or by the
   ownership-transfer procedure in task 3 below.
2. **Add a member, Docker Compose deployment:**
   ```
   ./run.sh add-member npub1abc...
   ./run.sh add-member npub1abc... --role admin
   ```
   or, invoking the binary inside the container directly:
   ```
   docker compose exec relay buzz-admin add-member --pubkey npub1abc... --role admin
   ```
   Requires `DATABASE_URL`, `REDIS_URL`, and `BUZZ_RELAY_PRIVATE_KEY` set in
   the relay container's environment — the command signs and publishes a
   fresh kind:13534 membership-roster snapshot after the database write.
3. **Remove a member** the same way, optionally guarding on their current
   role so a stale removal request cannot silently remove the wrong person:
   ```
   ./run.sh remove-member npub1abc...
   ./run.sh remove-member npub1abc... --role member
   ```
4. **List the current roster** to verify the change:
   ```
   ./run.sh list-members
   ```
5. **Read the exit code if a command fails**: 1 = validation error (bad
   pubkey, bad role, usage error), 2 = member not found (remove), 3 = tried
   to remove the relay owner (change `RELAY_OWNER_PUBKEY` and restart the
   relay instead), 4 = the `--role` guard did not match, 5 = database/Redis/
   internal error.
6. **Adding several members in one script?** Insert a short pause (`sleep
   1`) between invocations. Each `add-member`/`remove-member` call publishes
   its own kind:13534 snapshot with a timestamp bumped past the previous one
   to defeat same-second domination for that one process — it does not
   serialize two near-simultaneous CLI invocations racing on the same
   second, so back-to-back scripted calls need the pause `run.sh` itself
   documents.

### 1a. Verification

Re-run `./run.sh list-members` (or `docker compose exec relay buzz-admin
list-members`) and confirm the target pubkey's row shows the expected role,
or is absent after a remove.

### 1b. Rollback

Adding a member back after a mistaken removal, or removing one after a
mistaken add, is the direct inverse command from step 2 or 3 above — there
is no separate undo command, and neither operation is destructive to
anything beyond the roster row and its kind:13534 snapshot.

### 1c. No shell access: manage membership live over the wire

An already-authenticated relay owner or admin can add, remove, or re-role a
member without touching the deployment at all, by signing a NIP-43 admin
event:

```
nak event -k 9030 --tag "p=<target-hex-pubkey>" --tag "role=member" \
  --auth --sec <owner-or-admin-privkey> ws://localhost:3000   # add (kind:9030)
nak event -k 9031 --tag "p=<target-hex-pubkey>" \
  --auth --sec <owner-or-admin-privkey> ws://localhost:3000   # remove (kind:9031)
nak event -k 9032 --tag "p=<target-hex-pubkey>" --tag "role=admin" \
  --auth --sec <owner-or-admin-privkey> ws://localhost:3000   # change role, owner-only (kind:9032)
```

This reaches the same `relay_members` roster as task 1's CLI path and
republishes the same kind:13534 snapshot; use whichever path fits the
deployment's access model.

## Add, remove, or list channel members

1. **Confirm your signing identity already holds the right role in the
   target channel.** Adding a member, or changing anyone to an elevated
   role, requires the signer to already be an elevated (owner/admin) member
   of that channel — this node does not restate that authorization rule; see
   [`capabilities-channels-channel-membership`](../../capabilities/channels/channel-membership.md)
   for it. Set `BUZZ_PRIVATE_KEY` to that identity's hex or `nsec` key, and
   `BUZZ_RELAY_URL` to the target relay (defaults to
   `http://localhost:3000`).
2. **Add a member:**
   ```
   buzz channels add-member --channel <channel-uuid> --pubkey <hex-pubkey> --role member
   ```
   `--role` accepts `owner`, `admin`, `member`, `guest`, or `bot`; omit it to
   default to `member`.
3. **Remove a member:**
   ```
   buzz channels remove-member --channel <channel-uuid> --pubkey <hex-pubkey>
   ```
4. **List current channel members:**
   ```
   buzz channels members --channel <channel-uuid>
   ```
5. **Self-service join/leave**, for the signer's own membership rather than a
   third party's:
   ```
   buzz channels join --channel <channel-uuid>
   buzz channels leave --channel <channel-uuid>
   ```
   `join` only succeeds against an open channel.
6. **Read the exit code if a command fails**: `buzz`'s global exit codes are
   0=ok, 1=bad input, 2=relay/network error, 3=auth error, 4=other, 5=write
   conflict, with error detail as `{"error": "<category>", "message":
   "<detail>"}` JSON on stderr.

### 2a. Verification

Re-run `buzz channels members --channel <channel-uuid>` and confirm the
target pubkey's role, or its absence after a remove.

### 2b. Rollback

The inverse `add-member`/`remove-member` call, signed by the same or another
sufficiently elevated identity. There is no separate undo command.

## Transfer ownership of a community

1. **Configure the deployment-level operator allowlist**, if not already
   done: set `RELAY_OPERATOR_PUBKEYS` to the comma-separated hex pubkey(s)
   permitted to call this endpoint, and `RELAY_OPERATOR_API_ORIGIN` to the
   relay's canonical `http(s)` origin (required whenever
   `RELAY_OPERATOR_PUBKEYS` is non-empty) — see
   `layers-configuration-relay-configuration` for the full validation rules
   for both variables.
2. **Sign and send a NIP-98-authenticated `POST /operator/communities/transfer`**
   as one of the configured operator pubkeys, with a JSON body:
   ```json
   { "community_id": "<uuid>", "new_owner_pubkey": "<hex>", "expected_owner_pubkey": "<hex>" }
   ```
   `expected_owner_pubkey` must match the community's current owner exactly —
   it is the concurrency guard against transferring away from an owner who
   already changed underneath the request. There is no `buzz-admin` or
   `buzz-cli` subcommand for this; it is reached only through this HTTP
   route.
3. **Read the response.** `"status": "transferred"` with a
   `"previous_owner"` field on success; `"status": "already_owner"` if the
   transferee already owned the community (a no-op, not an error); HTTP 404
   if the community has no owner to transfer from; HTTP 409 if
   `expected_owner_pubkey` no longer matches the current owner (`owner_
   conflict`) or the transferee is already at the per-owner community cap
   (`limit_reached`).

### 3a. Verification

List the community's members (task 1's `list-members`, or the equivalent
NIP-43 kind:13534 snapshot) and confirm the new owner's row shows role
`owner` and the previous owner's row shows role `member` — a transfer always
demotes the outgoing owner to `member`, never `admin`.

### 3b. Rollback

Call the same endpoint again with `new_owner_pubkey` and
`expected_owner_pubkey` swapped, once the new owner is confirmed. This is an
ordinary transfer in the opposite direction, not a special undo path, and
still requires an operator pubkey in `RELAY_OPERATOR_PUBKEYS` to sign it.

## See also

- [`capabilities-communities-community-members`](../../capabilities/communities/community-members.md) —
  the relay-wide membership capability these commands operate on: the
  `relay_members` roster, its role model, the NIP-43 event kinds, and the
  invite-based bulk-onboarding path this node does not cover.
- [`capabilities-channels-channel-membership`](../../capabilities/channels/channel-membership.md) —
  the per-channel membership capability, its role hierarchy, and the
  authorization rules a `buzz-cli channels add-member`/`remove-member` call
  must satisfy.
- [`capabilities-communities-community-roles`](../../capabilities/communities/community-roles.md) —
  the community-wide role model (owner/admin/member) and why the owner role
  is reachable only through configuration or transfer, never a direct grant.
- [`layers-configuration-relay-configuration`](../../layers/configuration/relay-configuration.md) —
  full validation semantics for `RELAY_OWNER_PUBKEY`, `RELAY_OPERATOR_PUBKEYS`,
  `RELAY_OPERATOR_API_ORIGIN`, and `BUZZ_REQUIRE_RELAY_MEMBERSHIP`.

## Boundary

This node does not describe:

- **Why the authorization rules exist, or the full role/permission model.**
  Which role can add, remove, or promote whom is the linked capability
  nodes' territory (`capabilities-communities-community-members`,
  `capabilities-channels-channel-membership`, `capabilities-communities-
  community-roles`); this node assumes the reader already knows the rule and
  wants the command that exercises it.
- **Acquiring the underlying concepts from scratch, for a newcomer.** A
  tutorial teaching what relay membership or channel membership *is* has no
  corpus template as of this writing; this node assumes an already-competent
  operator.
- **Why the two membership systems are designed as two separate rosters**,
  or how the underlying tables/events/handlers are built. That is
  explanatory/architectural content the linked capability nodes touch on but
  do not fully own either, since no architecture-family node for this
  subject exists yet in this corpus.
- **Bulk onboarding by invite code**, community deletion
  (`buzz-admin deletions`), or moderation (bans/timeouts/reports). Each is a
  distinct capability with its own (existing or future) corpus node, not a
  variant of membership management.
- **The Kubernetes/Helm deployment path**, beyond naming the gap below. No
  chart-documented equivalent to `run.sh add-member`/`remove-member`/
  `list-members` exists to describe.

## Relationships

- `references`: `capabilities-communities-community-members` — the
  relay-wide membership capability this node's task 1 and task 1c operate.
- `references`: `capabilities-channels-channel-membership` — the per-channel
  membership capability this node's task 2 operates, including the
  authorization rule this node explicitly does not restate.
- `references`: `capabilities-communities-community-roles` — the role model
  underlying both the `--role` flags in tasks 1-2 and the ownership-transfer
  semantics in task 3.
- `references`: `layers-configuration-relay-configuration` — the
  full validation rules for the environment variables tasks 1 and 3
  require the operator to set.
- `implements`: `corpus-template-procedure` — this node is a how-to-shaped
  instance of that template.

Checked against `origin/launchpad`'s corpus tree at the recorded revision:
all five ids are present. No node yet exists for the architecture, interface,
or flow layer of either membership system, so no `part-of` or `depends-on`
edge is declared toward one.

## Scope and omissions

**This node covers** the operator's executable procedure for relay-wide
(community) membership (`buzz-admin add-member`/`remove-member`/
`list-members`/`reconcile-channels` via Docker Compose `run.sh` or direct
`docker compose exec`, and the equivalent live NIP-43 WebSocket admin
events), for per-channel membership (`buzz-cli channels {add-member,
remove-member,members,join,leave}`), and for deployment-level community
ownership transfer (`POST /operator/communities/transfer`) — each task's
prerequisites, exact commands, exit codes, verification step, and rollback.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The membership/role authorization design and data model | `capabilities-communities-community-members`, `capabilities-channels-channel-membership`, `capabilities-communities-community-roles` |
| Full env-var validation semantics | `layers-configuration-relay-configuration` |
| Bulk onboarding via invite codes | `capabilities-communities-community-members`'s own scope, not restated here |
| Whole-community deletion (`buzz-admin deletions`) | a separate concept — community lifecycle, not membership |
| Moderation (bans, timeouts, reports) | `capabilities/moderation/**`, a separate capability family |
| A Kubernetes/Helm `kubectl exec` equivalent to `run.sh add-member`/`remove-member`/`list-members` | not found in `deploy/charts/buzz/README.md`; no corpus node documents one because none exists in this repository as of the recorded revision |

**Expected but not verified when this node was written:**

- **The database-backed halves of these commands were not run against a live
  Postgres/Redis.** `buzz-admin add-member`/`remove-member`, `reconcile-
  channels`'s actual event publication, and `/operator/communities/
  transfer`'s actual database transaction were confirmed by reading the code
  and by executing each command's argument-validation path (which runs
  before any database connection and was directly observed to succeed or
  fail exactly as documented) — not by exercising a full add/remove/transfer
  round trip against a running deployment.
- **Whether any deployment in this repository's Kubernetes/Helm path
  actually performs `kubectl exec ... buzz-admin add-member` as an
  undocumented local convention** was not checked beyond reading
  `deploy/charts/buzz/README.md` itself; the gap named above is an absence
  of *documentation*, not proof that no operator has ever done this by hand.
- **Whether a desktop or mobile client surfaces an equivalent
  operator-facing membership-management UI** was not checked while writing
  this node; `capabilities-communities-community-members` separately
  documents a `CommunityMembersCard` desktop Settings surface for the same
  relay-wide roster, which an operator with UI access may prefer over the
  CLI paths this node documents, but this node itself covers only the
  CLI/HTTP surfaces.
