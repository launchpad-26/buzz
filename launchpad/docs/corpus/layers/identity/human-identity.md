---
id: layers-identity-human-identity
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "crates/buzz-core/src/kind.rs declares `pub const KIND_PROFILE: u32 = 0;`, documented as \"NIP-01: User profile metadata\" -- kind:0 is the Nostr-standard event a human user publishes to declare or update their own profile."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-relay/src/handlers/side_effects.rs's `handle_kind0_profile` is dispatched for every ingested kind:0 event (`0 => handle_kind0_profile(tenant, event, state).await` in the kind-dispatch match), parses the event's JSON content, and treats it as absolute replaceable state: a field present in the JSON is written, a field absent is cleared by passing an empty string, because `update_user_profile` only ever writes `Some` values and never leaves a prior value untouched by omission."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "handle_kind0_profile reads four fields out of the kind:0 JSON content -- `display_name` (falling back to `name`), `picture` (falling back to `image`) as `avatar_url`, `about`, and `nip05` -- and, for `nip05`, calls `crate::api::nip05::canonicalize_nip05` before storing it; an invalid or off-domain handle is silently cleared (treated as absent) rather than causing the already-persisted kind:0 event to be rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "canonicalize_nip05(raw, expected_host_or_url) in crates/buzz-relay/src/api/nip05.rs requires the handle's domain to lowercase-match the community's bound tenant host exactly (`extract_domain(expected_host_or_url)`), rejecting any handle whose domain does not match -- confirmed directly by its own unit test, which accepts `Alice@tenant-b.example` against tenant host `tenant-b.example` but rejects `alice@config.example` against that same tenant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs"
  - statement: "handle_kind0_profile calls buzz-db's `ensure_user` (creating the community-scoped `users` row on first sight of a pubkey) and then `update_user_profile(community, pubkey, Some(display_name), Some(avatar_url), Some(about), Some(nip05_handle))`; if the NIP-05 handle collides with another user's UNIQUE constraint the write is retried once with `nip05_handle` set to `None` so the rest of the profile still lands, and a `warn!` is logged noting the contested handle."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "crates/buzz-db/src/store/user.rs's `UserProfile` struct carries exactly five fields: `pubkey: Vec<u8>` (raw 32-byte compressed public key), `display_name: Option<String>`, `avatar_url: Option<String>`, `about: Option<String>`, and `nip05_handle: Option<String>` -- this is the row shape returned by `get_user` and written by `update_user_profile`, and it is the same struct and the same `users` table for both human and agent identities; nothing in this struct or its surrounding functions distinguishes the two."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/user.rs"
  - statement: "migrations/0001_initial_schema.sql's `users` table has `PRIMARY KEY (community_id, pubkey)` and a nullable, self-referencing `agent_owner_pubkey BYTEA` column with `FOREIGN KEY (community_id, agent_owner_pubkey) REFERENCES users (community_id, pubkey) ON DELETE SET NULL` -- there is no separate table, row type, or schema for a \"human\" identity distinct from an agent identity; a human user is simply a `users` row whose own `agent_owner_pubkey` is null (it is not itself owned by another pubkey)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "desktop/src-tauri/src/secret_store.rs's module doc states plainly: \"OS keyring access for desktop nsec private keys,\" and that all secrets are stored \"as a single JSON blob under one keychain entry\" so that exactly one OS keychain prompt occurs per process lifetime; the backend is selected at compile time (legacy `keyring` crate SecKeychain API on macOS for the blob entry, the `keyring` crate directly on Windows and Linux, with a one-time Data Protection Keychain migration path for old per-key entries)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs"
  - statement: "desktop/src-tauri/src/commands/profile.rs's `get_profile` Tauri command reads the signed-in human's own profile by querying the relay directly for `{\"kinds\": [0], \"authors\": [my_pubkey], \"limit\": 1}` and converting the most recent kind:0 event -- it does not read the `users` table row; `update_profile` performs a read-merge-write of the same kind:0 JSON content (comment: \"kind 0 is a full profile snapshot\") and publishes a new kind:0 event signed with `nostr::EventBuilder::new(nostr::Kind::Metadata, ...)`, which is the same Nostr-library constant as `buzz-core`'s `KIND_PROFILE = 0`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/profile.rs"
  - statement: "mobile/lib/shared/community/community_storage.dart's `CommunityStorage` class stores per-community credentials, including the private key, using `flutter_secure_storage` (`import 'package:flutter_secure_storage/flutter_secure_storage.dart';`, `pubspec.yaml` pins `flutter_secure_storage: ^10.0.0`); a `Community` object carries an `nsec` field, and the legacy single-community migration path explicitly reads a `_legacyNsec` key (`'buzz_nsec'`) out of secure storage into that field."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart"
      - "mobile/pubspec.yaml"
  - statement: "Both custody mechanisms found -- the desktop single-blob OS keychain and the mobile flutter_secure_storage-backed per-community record -- store the human's Nostr private key (`nsec`) client-side, never on the relay; the relay's own `users` table (UserProfile) and kind:0 events carry only the human's public identity (pubkey and profile fields), never private key material, so \"how a human's identity is represented\" is necessarily a two-sided answer: public profile state synced through the relay, and private key custody that stays entirely on the client and is never transmitted to or stored by buzz-relay."
    entry_class: INFERENCE
    evidence:
      - "desktop/src-tauri/src/secret_store.rs"
      - "mobile/lib/shared/community/community_storage.dart"
      - "crates/buzz-db/src/store/user.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
    confidence: 0.85
  - statement: "Issue #1106's definition of done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals, link related concepts, implementation and verification without duplicating their content, and use examples only to clarify the concept rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1106 definition of done"
relationships:
  - type: references
    target: architecture-context-human-user
---

# Human Identity

A human user's identity in Buzz is a Nostr keypair, represented to the rest of the
system through a **kind:0 (NIP-01) profile-metadata event** that the relay syncs
into a community-scoped `users` row, with the **private key itself held only by
the client** — never by the relay.

## Definition

Concretely, a human identity has two parts, and this node's job is to describe both
without duplicating the node that already covers the human user as an architecture-
level actor (`architecture-context-human-user`, linked below).

**1. The public side: pubkey + kind:0 profile metadata, synced by the relay.**
`buzz-core` declares kind 0 as `KIND_PROFILE` (NIP-01: "User profile metadata").
When a client publishes a kind:0 event, `buzz-relay`'s `handle_kind0_profile` side
effect parses its JSON content and syncs four fields — `display_name` (or `name`),
`picture`/`image` as `avatar_url`, `about`, and a NIP-05 `nip05` handle — onto the
signer's row in the community-scoped `users` table (`UserProfile`: `pubkey`,
`display_name`, `avatar_url`, `about`, `nip05_handle`). Kind:0 is treated as
**absolute state**, not a patch: a field missing from the JSON clears the
corresponding column, because the sync path only ever passes `Some` values through
to the database write. A `nip05` value is additionally validated and canonicalized
against the community's own bound host — `alice@tenant-a.example` is only accepted
on `tenant-a.example`'s community, never on another tenant — and a value that fails
validation, or collides with another user's NIP-05 uniqueness constraint, is
silently dropped rather than causing the event itself to be rejected (the event was
already persisted by the time the side effect runs).

There is **no separate "human" row type**. The same `users` table, the same
`UserProfile` shape, and the same kind:0 sync path serve agent identities too — the
schema's own primary key is `(community_id, pubkey)`, and a human is simply a row
whose `agent_owner_pubkey` is null, meaning it is not itself owned by another
identity.

**2. The private side: the keypair, held only by the client.** A human's identity
is only as trustworthy as the private key that can sign as that pubkey, and that
key never reaches the relay or the `users` table. The desktop app stores it in the
OS keychain — `secret_store.rs` describes its purpose plainly as "OS keyring
access for desktop nsec private keys," keeping every secret as a single JSON blob
under one keychain entry so the OS prompts the user once per process rather than
once per key. The mobile app stores it with `flutter_secure_storage`, keyed per
community on a `Community.nsec` field (with a legacy single-community `buzz_nsec`
migration path). Reading one's own profile (`get_profile`) does not even consult
the `users` table — it queries the relay directly for the latest kind:0 event
signed by the caller's own pubkey; updating it (`update_profile`) does a
read-merge-write of that same JSON and re-signs a fresh kind:0 event with the
locally-held key.

## Diagram

```mermaid
flowchart LR
    Human(["Human user"])
    Keypair["Nostr keypair (nsec/npub)"]

    subgraph Custody["Client-side custody (never leaves the client)"]
        Desktop["Desktop: OS keychain\n(secret_store.rs, single blob)"]
        Mobile["Mobile: flutter_secure_storage\n(per-community nsec)"]
    end

    Human --> Keypair
    Keypair --> Desktop
    Keypair --> Mobile

    Desktop -- "signs kind:0 event\n(nostr::Kind::Metadata)" --> Relay["buzz-relay\ningest"]
    Mobile -- "signs kind:0 event" --> Relay

    Relay --> SideEffect["handle_kind0_profile\n(side_effects.rs)"]
    SideEffect -- "ensure_user +\nupdate_user_profile" --> UsersTable[("users table\nUserProfile row")]

    UsersTable -. "read via get_user_profile,\nsearch_users, etc." .-> Readers["Other clients / relay reads"]
```

The private key never crosses the right-hand boundary of the diagram: only the
*signed event* leaves the client, and only the *parsed profile fields* the event
carries end up in the `users` table.

## Use cases

A reader reaches for this node when they need to:

- **Understand how a display name, avatar, bio, or NIP-05 handle gets from a client
  into the rest of the system.** The path is always: client builds/merges kind:0
  JSON → signs and publishes it → relay's `handle_kind0_profile` parses and syncs
  it into `UserProfile` on the `users` row.
- **Reason about why a profile field silently reverted or disappeared.** Because
  kind:0 is absolute state, republishing an older cached copy of the JSON (missing
  a field a newer client version added) clears that field, and an off-domain or
  contested NIP-05 handle is dropped rather than rejected.
- **Trace where a human's private key material actually lives.** Never in
  `buzz-db`, never in the `users` table, never transmitted to `buzz-relay` — only
  in the desktop OS keychain or the mobile app's `flutter_secure_storage`, and only
  a signature (or a freshly signed kind:0 event) ever leaves the client.
- **Distinguish "identity" from "actor" or "boundary."** This node describes the
  representation mechanics; it does not restate who a human user is as a system
  actor or where the human/agent/relay/community boundary sits — that belongs to
  `architecture-context-human-user`, linked below.

## Comparison

| Concept | What it is | Where it lives |
|---|---|---|
| **kind:0 event** | The Nostr wire event a client publishes to declare/update profile metadata | Published by the client, ingested by `buzz-relay`; `KIND_PROFILE = 0` in `crates/buzz-core/src/kind.rs` |
| **`UserProfile` / `users` row** | The synced, queryable *result* of the latest kind:0 event — not itself a signed event | `crates/buzz-db/src/store/user.rs`; `migrations/0001_initial_schema.sql`'s `users` table |
| **Keypair custody** | The private key material proving control of the pubkey; never synced to the relay | Desktop: `desktop/src-tauri/src/secret_store.rs` (OS keychain); Mobile: `mobile/lib/shared/community/community_storage.dart` (`flutter_secure_storage`) |
| **Human user (architecture-context actor)** | The person as a system actor: their boundary, their relationship to agents, clients, the relay, and the community | `architecture-context-human-user` (linked below) — not restated here |

## Related resources

See the `references` relationship in this node's front matter, pointing at
`architecture-context-human-user` — the node documenting the human user as an
architecture-context actor, the client/relay boundary they sit inside, and their
relationship to agents, the relay, and the community. This node instead documents
the mechanics of how that actor's identity is represented and kept current: kind:0
profile sync plus client-side keypair custody.

## Scope and omissions

**This document covers** how a human user's identity is represented at the data
level (kind:0 profile-metadata events, synced into the community-scoped `users`
table via `UserProfile`) and how the private key backing that identity is
custodied client-side (desktop OS keychain, mobile secure storage) rather than by
the relay.

**This document does not cover, deliberately:**

- The human user as an architecture-context actor — their system boundary and
  relationship to agents, clients, the relay, and the community. That is
  `architecture-context-human-user`'s subject, linked above rather than restated.
- The generic "actor" naming convention (the authenticated pubkey performing a
  request, independent of whether it is human- or agent-owned). That concept does
  not yet have a node merged on `origin/launchpad` to link to at this node's
  recorded revision, so it is named here only as a boundary, not linked.
- Agent identity specifically (how an agent's `users` row and `agent_owner_pubkey`
  relationship work) — a related but separate node's subject once it exists.
- Authentication mechanics (NIP-42 for humans, NIP-98 for agents) — a separate
  concern from how identity is *represented*, already covered at the
  architecture-context level by `architecture-context-human-user`.
- Any detail of desktop's keyring backend selection beyond what its own module doc
  states (macOS legacy `keyring` crate vs. Windows/Linux `keyring` crate vs. the
  one-time Data Protection Keychain migration path) — implementation detail for a
  future container/component-level corpus node, not this one.

**Expected but not verified when this node was written:**

- Whether any code path other than `handle_kind0_profile` also writes to
  `UserProfile` fields (e.g. an admin/moderation tool, a migration script, or a
  workflow action) was not searched for beyond the one call site cited above and
  `workflow_sink.rs`'s own `update_user_profile` call for agent profiles, which
  this node does not describe in detail.
- Whether the mobile app's `flutter_secure_storage` configuration enables any
  platform-specific hardware-backed storage (e.g. Android Keystore, iOS Secure
  Enclave) versus its default backend was not inspected — only that the package is
  used and that it is where `nsec` is stored.
- Whether a human user can ever hold more than one active keypair/identity
  simultaneously within one community was not investigated; the `users` table's
  primary key (`community_id`, `pubkey`) suggests one row per keypair per
  community, but whether product UX ever presents multiple simultaneously was out
  of scope for this review.
