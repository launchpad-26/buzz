---
id: layers-identity-identity-archive
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
  - statement: "NIP-IA's abstract defines it as \"a relay-scoped protocol for archiving and unarchiving identities,\" where \"an archived identity is a pubkey that the relay says should be hidden from active-member and autocomplete surfaces on that relay, while preserving its historical events and without implying any global reputation state,\" built from three event families: user-signed requests (kind:9035/9036), relay-signed deltas (kind:8002/8003), and a relay-signed current-state snapshot (kind:13535)."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md"
  - statement: "NIP-IA's Non-Goals section states explicitly that the protocol does not delete events (\"Historical events authored by an archived pubkey remain valid Nostr events\"), does not define bans/kicks/relay-access revocation (\"Use NIP-43 membership removal for relay access control\"), does not define global reputation (\"An archive state from relay A applies only to relay A\"), does not require relays to accept every request, and does not transfer authorship of an archived agent's historical events to its owner."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md"
  - statement: "The NIP-IA kinds table defines kind:9035 (Archive Request, user/agent-signed) and kind:9036 (Unarchive Request, user/agent-signed) as policy-defined storage, kind:8002 (Archived Identity) and kind:8003 (Unarchived Identity) as relay-signed regular deltas, and kind:13535 (Archived Identities List) as a relay-signed replaceable snapshot (10000<=n<20000 per NIP-01); `crates/buzz-core/src/kind.rs` defines `KIND_IA_ARCHIVE_REQUEST = 9035`, `KIND_IA_UNARCHIVE_REQUEST = 9036`, `KIND_IA_ARCHIVED = 8002`, `KIND_IA_UNARCHIVED = 8003`, and `KIND_IA_ARCHIVED_LIST = 13535`, matching the spec's numbers exactly, plus an `is_identity_archive_request_kind` helper documented as covering \"9035–9036\" only -- the 8002/8003/13535 kinds are \"emitted by the relay, never ingested.\""
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md"
      - "crates/buzz-core/src/kind.rs"
  - statement: "`migrations/0001_initial_schema.sql` creates `archived_identities` with primary key `(community_id, pubkey)`, a `consent_path` column constrained by `CHECK (consent_path IN ('self', 'owner', 'admin'))`, `actor`, `reason`, `replaced_by`, `request_event_id`, and `archived_at` columns, preceded by the comment \"Conformance: archive cannot hide a key in another community. PK scoped.\""
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "`crates/buzz-db/src/archived_identities.rs`'s module doc states the table \"stores a community-local UI visibility hint for identity pubkeys\" and that \"Archiving is not a ban: it does not affect membership, relay access, or repository permissions\"; its `archive()` function inserts with `ON CONFLICT (community_id, pubkey) DO NOTHING` (idempotent, does not mutate an existing row), and `unarchive()` executes a `DELETE` -- the table holds current archive state per pubkey, not a history of past archive/unarchive events."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/archived_identities.rs"
  - statement: "`crates/buzz-relay/src/handlers/identity_archive.rs`'s `determine_consent_path` resolves `ConsentPath::SelfSigned` when the request actor equals the target, `ConsentPath::Admin` when the actor's community-membership role (via `get_relay_member`) is `owner` or `admin`, and otherwise calls `verify_owner_consent`, which requires the request's NIP-OA `auth` tag owner to equal the request signer and cross-checks that owner against the target's *live* `kind:0` profile's own `auth` tag before granting `ConsentPath::Owner` -- a request whose live-profile attestation has since changed is rejected even if the request's own attached credential is still valid. The handler additionally enforces a ±120-second freshness window, exactly one `p` tag and one NIP-70 `-` tag, and rejects `replaced-by` outright on unarchive requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs"
  - statement: "`crates/buzz-relay/src/handlers/ingest.rs` maps `KIND_IA_ARCHIVE_REQUEST`/`KIND_IA_UNARCHIVE_REQUEST` to `Scope::UsersWrite`, not `Scope::AdminUsers`, with an inline comment explaining the choice is deliberate because \"NIP-IA's self and owner-of-agent paths are open to ordinary users\" and \"Real authorization is the consent-path check inside handle_identity_archive_event\"; a separate ingest.rs comment groups the same two kinds with other relay-global event kinds that \"must not be channel-scoped, even if the event carries a stray `h` tag.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`desktop/src-tauri/src/commands/identity_archive.rs`'s module doc states these Tauri commands let the desktop \"resolve a viewee's NIP-OA owner via their live kind:0,\" \"submit kind:9035 and kind:9036 archive/unarchive requests\" where \"consent path is selected by the relay; we just build the wire form,\" and \"read the relay's kind:13535 archive snapshot to drive UI flair,\" citing `docs/nips/NIP-IA.md` directly and noting \"the relay performs full authorization.\""
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/identity_archive.rs"
  - statement: "`crates/buzz-cli/src/commands/agents.rs` implements `buzz agents archive`/`unarchive`/`archived` by calling `buzz_sdk::builders::build_archive_identity_request`/`build_unarchive_identity_request` to construct the kind:9035/9036 wire form, and a separate `fetch_archived_snapshot`/`verify_archived_event` path that queries the relay's kind:13535 snapshot and rejects it client-side unless its `kind` and authoring pubkey (\"does not match relay self\") check out."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/agents.rs"
  - statement: "`crates/buzz-sdk/src/builders.rs`'s `build_archive_identity_request` doc comment documents `replaced_by` as \"the rotation pointer\" that \"must differ from target_pubkey,\" and states `.allow_self_tagging()` is required because \"NIP-IA's self path has actor == target, so the request's [\"p\", target] matches the signer\" and the underlying nostr crate \"strips matching p tags by default\" without it."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "The desktop's `useClassifiedMembers` hook peels archived members out of a channel's member list before splitting the remainder into people and bots, with the inline comment \"Archived wins over bot: a zombie agent should fold into 'Archived', not appear as an active 'Bot'. This is NIP-IA's headline use case,\" using `useIsArchivedPredicate` from the `identity-archive` feature; `desktop/tests/e2e/identity-archive.spec.ts` asserts an archived user's profile view shows an `archived-flair` element and gates an \"Unarchive\" action behind an admin/self check."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/lib/useClassifiedMembers.ts"
      - "desktop/tests/e2e/identity-archive.spec.ts"
  - statement: "`crates/buzz-db/src/deletion.rs`'s `EXPECTED_SCOPED_TABLES` constant lists `\"archived_identities\"` among the community-scoped tables purged when a community is deleted, and `migrations/0029_community_deletion.sql` calls `attach_community_write_fence('archived_identities')` -- archived-identity state is ordinary tenant data with no special-cased retention across community deletion."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs"
      - "migrations/0029_community_deletion.sql"
  - statement: "NIP-IA's Motivation section distinguishes archival from three existing Nostr primitives on their own terms: NIP-09 deletion requests \"do not help when the old key is lost, and they are too destructive for normal key rotation\"; NIP-51 mute lists \"are personal\" and \"do not give the relay a single authoritative view\"; NIP-43 membership removal \"is access control\" answering \"may this pubkey connect or publish here?\", not \"should this old identity still show up as an active person/bot in UI?\", and the document states directly \"A key can be archived without being banned; a spammer can be both removed via NIP-43 and archived via this NIP.\""
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md"
  - statement: "NIP-IA documents `replaced-by` as a hint rather than proof: its Security Considerations state \"Human key rotation should use replaced-by metadata so clients can guide users to the new identity,\" while its Privacy Considerations state \"A replaced-by tag links an old pubkey to a new pubkey\" and its Invalid Cases / client-behavior guidance states clients \"MUST archive by pubkey, not by display name\" because \"a replaced-by tag is a hint, not proof that two keys belong to the same person unless independently verified.\""
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md"
  - statement: "`crates/buzz-test-client/tests/conformance_multitenant.rs` names a multi-tenant archive-isolation obligation (\"archiving a key in A cannot hide/archive it in B\") as `archive_in_a_does_not_affect_b`, but the function is annotated `#[ignore]` and its body is exactly `pending_lane(\"buzz-auth\", ...)`, where `pending_lane` is defined as `fn pending_lane(lane: &str, obligation: &str) -> ! { todo!(...) }` -- this is a declared-but-unimplemented conformance obligation, not a passing test of cross-community isolation, in that file. Community-scoped isolation of the same claim IS separately exercised by a real, executable (if Postgres-gated) test: `archived_identities.rs`'s own `#[tokio::test]` `archived_identity_state_is_community_scoped`, which archives one pubkey in two different communities and asserts each community's `is_archived`/`list_archived` results are unaffected by the other's archive/unarchive calls."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
      - "crates/buzz-db/src/archived_identities.rs"
  - statement: "Beyond the one Postgres-gated `buzz-db` unit test and the one non-ignored `buzz-relay` handler test (`owner_archive_rejects_stale_request_after_live_kind0_owner_flip`, which itself returns early rather than asserting anything if it cannot open a database connection), no automated test was found that exercises the full request -> relay-verified consent -> persisted state -> delta -> snapshot pipeline end-to-end against a running relay; the desktop Playwright specs (`identity-archive.spec.ts`, `identity-archive-hide.spec.ts`) verify UI-visible behavior against a mocked bridge, not a live relay round-trip."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/archived_identities.rs"
      - "crates/buzz-relay/src/handlers/identity_archive.rs"
      - "desktop/tests/e2e/identity-archive.spec.ts"
      - "desktop/tests/e2e/identity-archive-hide.spec.ts"
    confidence: 0.65
  - statement: "Issue #718 (\"task: document capabilities/archive/identity-archive.md\", parent PRD #613) files a separate, capability-shaped corpus node for the same subject area at a different path (`launchpad/docs/corpus/capabilities/archive/identity-archive.md`) with a different definition of done (states the capability and primary actors/outcomes, defines behavioral rules/constraints/variants, links flows/interfaces/data/platform implementation) -- distinct in both node id and required shape from this layers-shaped concept node under PRD #607/#602."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#718"
  - statement: "Issue #1107's definition of done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals, link related concepts/implementation/verification without duplicating their content, and use examples only to clarify the concept rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1107 definition of done"
---

# Identity archive

An "archived" identity keeps showing up in message history forever, but a relay
still needs a way to say *this pubkey is retired here* without deleting anything
or accusing anyone of anything. This node is the canonical definition of the
mechanism Buzz uses to say that: **NIP-IA**, a relay-scoped identity-archival
protocol with its own event kinds, database table, relay handler, and UI surface.

## Definition

**Identity archive** is NIP-IA (Identity Archival, `docs/nips/NIP-IA.md`): a
relay-scoped protocol under which a pubkey can be marked, by relay-signed
attestation, as retired from that relay's active-member and autocomplete
surfaces — while its historical events remain valid, unmodified, and still
attributed to it, and while no claim is made about that pubkey on any other
relay. Mechanically, an archive is a request (`kind:9035` to archive, `kind:9036`
to unarchive) that the relay verifies under one of three consent paths — the
target archiving itself, an agent's owner archiving it via NIP-OA proof, or a
community admin/owner acting directly — after which the relay persists a row in
Postgres (`archived_identities`, one row per `(community_id, pubkey)`) and
publishes its own signed record of the decision (a `kind:8002`/`8003` delta plus
a fresh `kind:13535` snapshot).

**What it is not.** It is not a ban or an access-control decision — NIP-43
membership removal is the separate mechanism for "may this pubkey connect or
publish here," and a pubkey can be archived without being removed, removed
without being archived, or both. It is not event deletion — NIP-09 deletion
requests remove events and are, by NIP-IA's own Motivation section, "too
destructive for normal key rotation," where the point is that old messages
should stay attributed to the old key. It is not a global reputation signal —
archive state is strictly scoped to the relay (and, in Buzz's implementation,
the community) that signed it, and clients "MUST NOT globalize archive state."
And it is not cryptographic key succession: the optional `replaced-by` pointer
a request can carry is documented, in the spec's own words, as "a hint, not
proof that two keys belong to the same person unless independently verified" —
there is no signature chain proving the old key authorized the new one.

## Background

NIP-IA's own Motivation section states the problem plainly: "Relays accumulate
stale pubkeys. Humans rotate keys, contractors leave, bots are rebuilt, and
agents created from temporary worktrees continue to appear in member pickers
long after they are useful." Buzz's desktop client names the same case as the
protocol's "headline use case" directly in code: a zombie agent — one whose
owner is still active but whose old agent key has gone dormant — needs to fold
into an "Archived" bucket rather than keep appearing as a live "Bot" in a
channel's member list. Three existing Nostr primitives each cover part of this
problem and none cover all of it: NIP-09 deletion is about removing events, not
retiring an identity; NIP-51 mute lists are personal, so they give no relay-wide
authoritative view; and NIP-43 membership removal answers a connection/access
question, not a "should this still show up as active" question. NIP-IA exists
to fill that specific gap with a transparent, relay-signed, auditable state that
a client can act on without rewriting history or globalizing a local judgment.

```mermaid
sequenceDiagram
    participant Actor as Actor (self / owner / admin)
    participant Relay
    participant DB as archived_identities (Postgres)
    participant Clients

    Actor->>Relay: kind:9035 archive request (p: target, optional replaced-by)
    Relay->>Relay: verify consent path (self / owner via NIP-OA / admin role)
    Relay->>DB: archive(community, target, consent_path, actor, ...)
    Relay-->>Clients: kind:8002 archived-identity delta
    Relay-->>Clients: kind:13535 archived identities list (fresh snapshot)
    Clients->>Clients: hide target from active-member/autocomplete surfaces
```

## Use cases

- **Self key rotation.** A user retires their own pubkey and points to its
  replacement: the spec's own worked example has Alice sign a `kind:9035` for
  herself with `reason: "rotated"` and `replaced-by: <alice_new>`; the relay
  accepts it under `consent=self` with no further proof needed.
- **Owner archives a zombie agent.** An agent's owner key is still live but the
  agent's own key is dormant and cannot sign for itself; the owner proves the
  relationship with a NIP-OA attestation (either attached to the request or
  read from the target's own last-published `kind:0` profile) and the relay
  grants `consent=owner`. This is the case Buzz's own desktop code names as
  NIP-IA's "headline use case."
- **Admin archive composed with a NIP-43 ban.** A relay admin can archive a
  spammer's identity (hiding it from UI) and separately remove it from
  membership (denying access) — two independently auditable actions, not one.
- **Self-unarchive.** NIP-IA requires relays to honor a well-formed self
  `kind:9036` from a non-banned target, which the spec calls "the
  anti-shadowban property of this NIP" — an archived party always has a
  protocol path to contest or reverse the archive, as long as they still hold
  the retired key.
- **UI-visibility filtering without hiding history.** Buzz's desktop client
  reads the relay's `kind:13535` snapshot to sort archived members into their
  own bucket ahead of the people/bot split, and shows an "Archived" flair on an
  archived identity's profile — while that identity's past messages keep
  rendering normally, because NIP-IA never touches stored events.

## Comparison

| Mechanism | Answers | Scope | Buzz/NIP-IA relationship |
|---|---|---|---|
| **NIP-IA archive** (`kind:9035`/`9036`/`8002`/`8003`/`13535`) | "Should this retired identity still appear as active in UI here?" | One relay/community; transparent, relay-signed | The subject of this node |
| **NIP-09 deletion** | "Remove this event." | Per-event, author-signed | Explicitly named as too destructive for ordinary key rotation — old messages should stay attributed to the old key |
| **NIP-51 mute list** | "I don't want to see this pubkey." | Personal, per-user | No relay-wide authoritative view; every user would have to mute the same key independently |
| **NIP-43 membership removal** (`kind:8001`) | "May this pubkey connect or publish here?" | Relay access control | Composable with archival, not a substitute for it — a pubkey may be archived, removed, both, or neither |
| **Device pairing (NIP-AB)** | "Move my existing key to a new device." | Ephemeral, no relay-side persistence | A different problem entirely: transferring the *same* key between a user's own devices, not retiring one identity in favor of another |

## Scope and omissions

**This node covers** what NIP-IA identity archival is, the event kinds and
consent paths it defines, how Buzz's relay, database, CLI, and desktop
implement it, and how it differs from the neighboring mechanisms (deletion,
mute lists, membership removal, device pairing) it is easy to confuse it with.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Human identity representation and provisioning specifically | #1106 (`task: document layers/identity/human-identity.md`), not yet drafted |
| Agent identity representation and provisioning specifically | #1103 (`task: document layers/identity/agent-identity.md`), not yet drafted |
| Broader identity-recovery mechanics beyond the `replaced-by` hint (e.g. NIP-AB device pairing itself) | #1109 (`task: document layers/identity/identity-recovery.md`), not yet drafted |
| Keypair generation and public/private key mechanics | #1111/#1112/#1113 (`keypair.md`/`private-key.md`/`public-key.md`), not yet drafted |
| The capability-shaped description of identity archive (primary actors/outcomes, flows, interfaces) | #718 (`task: document capabilities/archive/identity-archive.md`, parent PRD #613) — a distinct node at a distinct path, not this one |
| NIP-OA owner-attestation mechanics in full (the cryptographic construction NIP-IA reuses for its owner consent path) | Not yet a filed corpus node at the recorded revision; see `docs/nips/NIP-OA.md` directly |
| The full `required_scope_for_kind` authorization mapping beyond the two NIP-IA kinds | `crates/buzz-relay/src/handlers/ingest.rs` directly |

**No `relationships` in this node's own front matter.** Checked before deciding
that rather than assuming it: at the recorded revision, `origin/launchpad`'s
`launchpad/docs/corpus` tree has no `layers/` subtree at all (confirmed via
`find launchpad/docs/corpus/layers` failing with "No such file or directory"),
so none of the sibling identity nodes this document would naturally link to
(actor, human-identity, agent-identity, identity-recovery, keypair) exist there
yet to target. The one existing merged node that touches adjacent territory,
`architecture-principles-humans-and-agents-are-peers`, documents authorization
parity between human- and agent-owned pubkeys specifically — a different claim
from NIP-IA's three-consent-path model, which does distinguish self/owner/admin
requesters by design. Forcing an edge there would be the same "reads as a
general rule rather than a fact about one moment" mistake this corpus's own
`AGENTS.md` warns against, so this node names the check and leaves the edge out
rather than adding one for its own sake.

**Expected but not verified when this node was written:**

- **The multi-tenant archive-isolation obligation named in
  `conformance_multitenant.rs` (`archive_in_a_does_not_affect_b`) is not
  actually exercised there** — it is an `#[ignore]`d stub whose body calls
  `todo!()` via `pending_lane`. The equivalent claim is verified elsewhere, by
  a real (Postgres-gated) unit test in `buzz-db`, but the conformance-suite
  copy of this obligation is unimplemented at the recorded revision.
- **No end-to-end test was found that exercises the full
  request-to-snapshot pipeline against a live relay.** Coverage that does
  exist is narrower: one Postgres-gated `buzz-db` unit test, one `buzz-relay`
  handler test covering a specific owner-consent-revocation scenario, and
  desktop Playwright specs that verify UI behavior against a mocked bridge
  rather than a real relay round-trip. This is recorded as an INFERENCE in the
  evidence ledger above, not asserted as a gap nobody could find evidence
  against.
- **The `crates/buzz-cli` and NIP-OA-specific verification code
  (`buzz_sdk::nip_oa`) were read only as far as needed to confirm the consent-
  path and wire-building claims above** — a full audit of NIP-OA's own
  cryptographic construction was not performed as part of this node.
