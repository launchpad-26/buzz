---
id: layers-data-data-ownership
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
  - statement: "The events table requires a pubkey column (BYTEA NOT NULL) and scopes every row to a community_id (UUID NOT NULL REFERENCES communities(id)), so a stored event cannot exist without recording both which key authored it and which community it belongs to."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "The relay's handle_event rejects any client-submitted event whose pubkey does not equal the authenticated NIP-42 identity, with a single exception carved out for kind:1059 gift-wrap events, replying with the OK-false message 'invalid: event pubkey does not match authenticated identity'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "validate_standard_deletion_event, called from ingest_event_inner in crates/buzz-relay/src/handlers/ingest.rs, rejects a NIP-09 deletion event unless the deleting actor's pubkey equals the pubkey that authored the targeted event, for both e-tag (regular event) and a-tag (addressable/replaceable event) deletion targets -- returning the error 'must be event author' otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The one exception to the author-match requirement is a registered agent owner: is_agent_owner (crates/buzz-db/src/user.rs) lets the deletion proceed when the actor's pubkey is recorded in the target author's own agent_owner_pubkey column, so an owner may delete on a managed agent's behalf without holding or using the agent's own signing key."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/user.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "set_agent_owner assigns that column exactly once per agent pubkey: it is a conditional UPDATE guarded by WHERE agent_owner_pubkey IS NULL, and the function's own comment states this is deliberate 'first mint wins' semantics chosen to avoid a race between concurrent claims -- so an agent's owner, once set by this function, is not reassigned by a second call."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/user.rs"
  - statement: "is_agent_owner's query filters on community_id in addition to the target and actor pubkeys, so an agent-owner binding established in one community says nothing about the same two pubkeys in another community."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/user.rs"
  - statement: "A stored event's own row-level ownership (its pubkey column) is a different concept from a community's ownership: transfer_community and list_owned_communities in crates/buzz-relay/src/api/operator.rs, backed by transfer_ownership in crates/buzz-db/src/relay_members.rs, govern who administers a whole community, keyed by a relay-membership 'owner' role rather than by any individual event's pubkey column."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "crates/buzz-db/src/deletion.rs implements a separate, whole-community destructive-deletion pipeline (DeletionRequest, DeletionStage, manifest freezing, quiescing, a Postgres purge step) that operates on a community as a unit rather than checking any individual event's author pubkey -- a different mechanism from the per-event ownership check this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs"
  - statement: "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs carries E2E coverage of this exact author-match/agent-owner boundary at the kind:5 NIP-09 path: test_owner_can_delete_agent_message_kind5 asserts a registered owner's kind:5 deletion of their agent's message is accepted, and the adjacent test_third_party_cannot_delete_agent_message_kind5 asserts the same deletion attempted from an unrelated third party's key is rejected. Both are marked #[tokio::test] #[ignore] and require a live relay, so their assertions were read directly but neither was executed this session."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs"
  - statement: "Issue #1063's definition of done requires this node to define data ownership in one sentence before deeper explanation, state boundaries/non-goals distinguishing it from what it must not be confused with, link related implementation/verification/corpus nodes without duplicating their content, and use examples only to clarify the concept rather than introduce a second canonical one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1063 definition of done"
relationships:
  - type: references
    target: architecture-principles-signed-events
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Data ownership

Every row Buzz stores at the data layer is a Nostr event, and every stored event
belongs to exactly one identity: the pubkey that signed it. This node documents that
binding — where it lives in the schema, how it is established, and which storage-layer
operations consult it to decide who may act on a piece of data.

## Definition

**Data ownership**, at Buzz's data/storage layer, is the binding between one stored
event and the single pubkey recorded in that event's own `pubkey` column — never a
separate ownership field, foreign key, or ACL table. `migrations/0001_initial_schema.sql`
declares `pubkey` `NOT NULL` on the `events` table itself, alongside the `community_id`
every row is also scoped to: ownership and tenancy are both intrinsic properties of the
row, not derived from a lookup elsewhere.

This is the one binding every storage-layer authorization check that cares about "whose
data is this" consults: the write-time identity check in `handle_event` (an event's
`pubkey` must equal the authenticated session, gift-wrap excepted), and the NIP-09
deletion check in `validate_standard_deletion_event` (the deleting actor's pubkey must
equal the target's author pubkey, or be that author's registered agent owner). Neither
check reads a separate "owner" table for the common case — the `pubkey` column *is* the
ownership record.

**What this is not.** "Data ownership" here means *content* ownership — which pubkey
authored a given event, and what that authorizes. It is a different concept from
*community* ownership — which pubkey administers a whole community (provisioning,
archiving, transferring it to another owner). Buzz tracks the second as a
`relay_members` role, entirely independent of any individual event's `pubkey` column.
See *Scope and omissions* for where that boundary is drawn and why this node does not
cross it.

## Background

Cryptographic authorship — the fact that only the holder of a private key can produce a
valid signature over an event's own id — is what makes the `pubkey` column trustworthy
as an ownership record in the first place. That mechanism (id-hash correctness, Schnorr
signature validity, and the separate check binding `event.pubkey` to the authenticated
NIP-42 session) is a sibling invariant this node depends on rather than restates; see
the `references` relationship to `architecture-principles-signed-events`. This node
picks up *after* that binding is established: given a trustworthy `pubkey`, what does
Buzz let that pubkey do to the data it owns, and who else, if anyone, may act alongside
it.

Similarly, every ownership check described here operates *within* one community —
`is_agent_owner`'s query filters on `community_id` exactly as the `events` table does —
so an ownership binding never crosses the tenant boundary a community represents. See
the `references` relationship to `architecture-principles-community-is-security-boundary`
for that boundary's own enforcement, which this node does not re-derive.

## Use cases

- **A developer adding a new storage-layer operation** (a new deletion path, a new
  replaceable-event kind) needs to know which check gates "may this actor touch this
  data": compare the acting pubkey to the row's own `pubkey`, or consult
  `is_agent_owner` for the one documented delegation path. Getting this wrong either
  lets a stranger act on data they do not own, or locks a legitimate owner out.
- **A reviewer auditing an authorization change** needs the two valid ownership paths
  named in one place — author match, or a registered agent owner — so a missing check
  in a diff (an endpoint that skips both) is recognizable as a gap rather than an
  unfamiliar pattern.
- **Anyone reasoning about "who owns this data"** needs to know it is two different
  questions with two different answers in this codebase: which pubkey authored this
  *event* (this node), and which pubkey administers this *community* (a different,
  undocumented-here concept). Conflating them misreads either a per-message
  authorization bug or a community-administration change as the other.

## Verification

`crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs` exercises this exact
boundary end to end at the kind:5 NIP-09 path: `test_owner_can_delete_agent_message_kind5`
asserts a registered owner's kind:5 deletion of their agent's message is accepted, and
`test_third_party_cannot_delete_agent_message_kind5` asserts the same deletion attempted
by an unrelated third party's key is rejected. Both tests carry `#[ignore]` and require a
live relay; their assertions were read directly for this node but neither was run this
session — see *Expected but not verified* below.

## Scope and omissions

**This document covers** the binding between a stored event and the pubkey that owns
it, where that binding lives in the schema, the two storage-layer checks that consult
it (write-time identity binding, NIP-09 deletion authorization for both `e`-tag and
`a`-tag targets), and the one documented delegation mechanism (agent ownership) that
lets a second pubkey act on an owned event's behalf.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Why it is a different concept |
|---|---|
| Community/tenant-level ownership — who administers a whole community, `transfer_community`, `list_owned_communities`, the `relay_members` `owner` role | Keyed by a membership role, not by any event's `pubkey` column; a different data model answering a different question. No corpus node exists for it yet at this revision. |
| The agent-owner delegation mechanism's full semantics — revocation, multiple owners, the CLI/UI surface for minting or viewing an agent's owner | Only the shape relevant to the deletion-authorization check documented here (first-mint-wins, community-scoped) was verified. A fuller treatment is a candidate for its own future node rather than folded in here, per the corpus's one-node-one-idea rule. |
| The whole-community destructive-deletion pipeline (`crates/buzz-db/src/deletion.rs`: `DeletionRequest`, `DeletionStage`, manifest freezing, quiescing, Postgres purge) | Operates on an entire community as a unit; it does not check or consult any individual event's author pubkey, so it is a different mechanism from the per-event ownership binding this node documents. |
| Channel-level roles (owner/admin/member via `relay_members`, moderation bans and timeouts) | Capability-layer governance over who may act *within* a channel, not the data-layer binding between one event and its authoring pubkey. |
| The cryptographic mechanism that makes a `pubkey` column trustworthy (id-hash correctness, Schnorr signature validity) | Documented in `architecture-principles-signed-events`, linked via this node's `references` relationship rather than restated. |
| The tenant-isolation mechanism that scopes every ownership check to one community | Documented in `architecture-principles-community-is-security-boundary`, linked via this node's `references` relationship rather than restated. |

**No `relationships` beyond the two declared.** Checked directly against
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` immediately
before finalizing this front matter, at the recorded revision: this is the first node
under `layers/data/`, so it has no data-layer sibling yet to point at, and the two
architecture-principle nodes named above are the only merged nodes this node's own
claims draw on directly.

**Expected but not verified when this node was written:**

- **No live database or relay was exercised.** `is_agent_owner`'s SQL and
  `set_agent_owner`'s "first mint wins" behavior were verified by reading the query text
  and the function's own comment, not by running either against a live Postgres
  instance, and the two `#[ignore]`-gated E2E tests named in *Verification* were read,
  not run, for the same reason (no live relay was stood up this session).
- **NIP-33 (addressable/replaceable event) semantics beyond the `a`-tag deletion
  authorization branch** — whether ownership plays any further role in *replacement*
  (as opposed to deletion) of an addressable event — was not checked beyond what
  `validate_standard_deletion_event`'s own `a`-tag branch does directly.
