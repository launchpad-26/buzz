---
id: layers-identity-public-key
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
  - statement: "migrations/0001_initial_schema.sql's `users` and `pubkey_allowlist` tables both declare `PRIMARY KEY (community_id, pubkey)`, and `channel_members` declares the three-column `PRIMARY KEY (community_id, channel_id, pubkey)` — in all three, `pubkey BYTEA NOT NULL` is part of the primary key, not merely an indexed column. `users` additionally carries `CONSTRAINT chk_users_pubkey_len CHECK (LENGTH(pubkey) = 32)`, fixing the stored form at exactly 32 raw bytes."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "`api_tokens.owner_pubkey`, `subscriptions.owner_pubkey`, and `workflows.owner_pubkey` are each declared `BYTEA NOT NULL` with a composite `FOREIGN KEY (community_id, owner_pubkey) REFERENCES users (community_id, pubkey)`, so a pubkey used to attribute ownership of a token, subscription, or workflow must already have a `users` row in the same community; `events.pubkey`, `reactions.pubkey`, and `event_mentions.pubkey_hex` carry the same value on high-volume tables without a declared foreign key."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "`crates/buzz-core/src/verification.rs`'s `verify_event` reads `event.pubkey` (a `nostr::PublicKey`, the crate's type for a NIP-01/BIP-340 x-only secp256k1 Schnorr public key) both to recompute the event's id hash and, via `event.verify_signature()`, to check the event's Schnorr signature — the pubkey is the value a signature is verified against, not merely stored alongside it."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
  - statement: "`crates/buzz-auth/src/lib.rs`'s `AuthContext` struct carries `pubkey: nostr::PublicKey` as \"the authenticated Nostr public key,\" and `AuthService::verify_auth_event` sets it directly from the verified NIP-42 auth event's own `pubkey` field (`auth_event.pubkey`) after a successful signature check — the pubkey becomes the identity attached to a connection for every subsequent request, not a separately issued session id."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "`crates/buzz-sdk/src/mentions.rs`'s `extract_nostr_uris` decodes NIP-27 `nostr:npub1…` references by calling `nostr::PublicKey::from_bech32` and then re-encodes the result with `.to_hex()`, and its own doc comment states it \"Decodes each to a 32-byte pubkey hex string\" — confirming hex and npub (NIP-19 bech32) are two textual encodings of the same 32-byte value, convertible losslessly between each other."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/mentions.rs"
  - statement: "`crates/buzz-cli/src/commands/messages.rs`'s `resolve_author` treats a 64-character all-hex-digit string and an `npub1`-prefixed string (decoded via `nostr::PublicKey::parse`) as two acceptable spellings of the same author filter, converting the npub form to hex before use; its sibling `normalize_explicit_mentions` likewise calls `PublicKey::parse` on each `--mention` value and re-serializes to hex — `buzz-cli` accepts either encoding interchangeably across its pubkey-taking flags rather than picking one canonical input form."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "`crates/buzz-db/src/user.rs` declares `UserProfile.pubkey: Vec<u8>`, documented as \"Raw 32-byte compressed public key,\" alongside presentation fields (`display_name`, `avatar_url`, `about`, `nip05_handle`) that are all optional — the pubkey is the one field a profile cannot exist without, and it is what the rest of the profile is attached to, not itself part of the presentation data."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/user.rs"
  - statement: "Unmerged draft PR #1803 (issue #1102, `layers/identity/actor.md`) defines \"actor\" as \"the single authenticated pubkey performing a request or action,\" stating explicitly \"an actor *is* a pubkey\" — i.e. actor is a role/usage label for a pubkey in a given request, not a different identifier or a distinct value from the pubkey this node defines."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1803 (unmerged draft PR body, Definition section, read directly while authoring this node)"
  - statement: "Issues #1111 (`task: document layers/identity/keypair.md`) and #1112 (`task: document layers/identity/private-key.md`) are filed as separate sibling tasks under the same parent PRD #607, and neither has a PR or corpus file yet at this node's recorded revision — key generation and private-key handling are out of scope for this node and are gaps this node names rather than covers."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1111 and #1112 issue titles, read directly while authoring this node"
relationships:
  - type: references
    target: architecture-principles-signed-events
  - type: references
    target: architecture-principles-humans-and-agents-are-peers
---

# Public key

A **public key** (pubkey) is the 32-byte secp256k1 Schnorr public key
(NIP-01/BIP-340, x-only) that identifies a Nostr identity in Buzz — the
value every signed event is signed by, every authenticated connection is
bound to, and every `users` row is keyed on. It is Buzz's one universal
identifier for "who" — human or agent, member or owner — with no separate
identity type layered underneath it.

## Definition

Structurally, a pubkey is 32 raw bytes. Buzz stores it that way: `users`,
`channel_members`, and `pubkey_allowlist` all use `pubkey BYTEA` as part of
their primary key, and `users` enforces the length with
`CHECK (LENGTH(pubkey) = 32)`. Ownership columns elsewhere —
`api_tokens.owner_pubkey`, `subscriptions.owner_pubkey`,
`workflows.owner_pubkey` — are foreign keys back to that same
`(community_id, pubkey)` pair, and high-volume tables (`events`, `reactions`,
`event_mentions`) carry the value directly without a declared foreign key.
A pubkey does not, on its own, imply a `users` row exists — the row is what
turns a bare pubkey into a member with a profile, capabilities, and channel
membership; a pubkey that has never joined a community is still a valid
pubkey.

Two things give a pubkey meaning beyond "a 32-byte value":

1. **It is a signature-verification key.** `verify_event` recomputes an
   event's id from its `pubkey` field and calls `event.verify_signature()`
   to check the event's Schnorr signature against it. A pubkey that did not
   sign an event cannot make that event verify.
2. **It is the identity NIP-42/NIP-98 authentication attaches to a
   connection.** `AuthContext.pubkey` is set directly from the verified
   auth event's own `pubkey` — there is no separate session identifier;
   every subsequent authorization check reasons about *this* pubkey.

**Encodings.** A pubkey has two interchangeable textual forms in Buzz code
and tooling: 64-character lowercase hex, and NIP-19 bech32 `npub1…`.
`buzz-sdk`'s NIP-27 mention parser decodes `npub1…` to hex and back;
`buzz-cli` accepts either form on most pubkey-taking flags (a 64-hex-digit
string, or an `npub1`-prefixed string decoded via `nostr::PublicKey::parse`)
and normalizes to hex internally. Neither encoding is a different key —
they are two spellings of the same 32 bytes, chosen for readability
(`npub1…`, with its checksum) versus raw storage/comparison (hex/`BYTEA`).

## Boundary — what this is not

**Not "actor" (#1102, `layers/identity/actor.md`, unmerged as of this
revision).** That sibling node's subject is a *role* — "the pubkey
performing this particular request or action" — and its own definition
states plainly "an actor *is* a pubkey." This node defines the identifier
itself: its byte shape, its two encodings, and its structural role as a
database key and a signature-verification key. "Actor" is a way of talking
about a pubkey in a specific request context; it is not a second kind of
identifier.

**Not a keypair or a private key (#1111, #1112 — neither authored yet).**
This node covers the *public* half only: what it is, how it is stored, and
how it is encoded. It says nothing about how a keypair is generated, how a
private key signs an event, or how private-key material should be handled —
those are separate concepts, filed as their own tasks, and this node does
not fold them in.

**Not a user profile.** `UserProfile` (display name, avatar, about,
NIP-05 handle) is presentation data *about* a pubkey, keyed by it —
`UserProfile.pubkey` is the one required field, and everything else on the
struct is optional. The pubkey is the identifier; the profile is what a
human or agent chooses to present alongside it. A pubkey is valid and
meaningful with no profile at all.

**Not a community identifier.** `communities.id` (a `UUID`) identifies a
*community*, not a person or agent. A pubkey is scoped *within* a community
via the `(community_id, pubkey)` composite key pattern used throughout the
schema, but the pubkey's own bytes are the same regardless of which
community it has joined.

## Use cases

- **Verifying a signed event.** Any code that needs to trust an event's
  authorship calls `verify_event`, which checks the event's Schnorr
  signature against its own `pubkey` field — this is the mechanism, not an
  incidental detail, of how Buzz trusts who published something.
- **Authorizing a request.** Once `AuthContext.pubkey` is set, every
  downstream authorization check (membership, ownership, scopes) reasons
  about that one value — looking up a `users` row, checking an
  `owner_pubkey` foreign key, or matching an NIP-29 `p` tag.
- **Accepting a pubkey from a human or another tool.** CLI flags, mention
  syntax, and admin commands all need to accept both the hex form (easy to
  copy from a database row or a `nak` command) and the npub form (checksum-
  protected, the form NIP-19 recommends for user-facing display) without
  requiring the caller to convert first.

## Scope and omissions

**This document covers** the pubkey as a value: its byte/hex/npub shapes,
its role as a database primary/foreign key across the schema, and its role
as the value signature verification and authentication both check against.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Keypair generation, and how a private key produces a signature | #1111, `layers/identity/keypair.md` (not yet authored) |
| Private-key handling and storage | #1112, `layers/identity/private-key.md` (not yet authored) |
| "Actor" as a request-scoped role label for a pubkey | #1102, `layers/identity/actor.md` (draft PR #1803, unmerged) |
| Human identity and agent identity as distinguished by `agent_owner_pubkey` | #1103 (agent identity, draft PR #1804), #1106 (human identity, draft PR #1808) — neither merged |
| Community identity (`communities.id`, host resolution) | `layers/tenancy/community-id.md`, not yet authored at this revision |
| The full NIP-42/NIP-98 authentication flow | `architecture/flows/websocket-authentication.md` |

**Expected but not verified when this node was written:** whether any
in-progress work plans to store or accept pubkeys in a form other than
32-byte `BYTEA`/64-char hex/`npub1` bech32 (e.g. compressed/uncompressed
secp256k1 point forms) — no such issue was found, but the search was not
exhaustive across the full issue tracker.
