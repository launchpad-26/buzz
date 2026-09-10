---
id: interfaces-nostr-buzz-nips-nip-oa
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "docs/nips/NIP-OA.md defines an optional `auth` tag, status `draft` `optional`, by which an owner key authorizes an agent key to publish events under the agent's own authorship. It states it reuses NIP-26 as prior art for the credential format and signing flow only, and explicitly states 'NIP-26 assigns the event to the delegator semantically, and that semantic MUST NOT be reused for agent provenance' -- an event carrying a valid `auth` tag remains authored by `event.pubkey`, never the owner."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md"
  - statement: "The `auth` tag is exactly four elements -- [\"auth\", \"<owner-pubkey-hex>\", \"<conditions>\", \"<sig-hex>\"] -- and is a reusable capability: the same tag MAY appear on multiple events by the same agent key. The signing preimage is the literal string `nostr:agent-auth:` concatenated with the agent's hex pubkey, `:`, and the conditions string, hashed with SHA-256 and signed with a BIP-340 Schnorr signature by the owner's key. More than one `auth` tag on an event means the event has no valid `auth` tag at all, per the spec's explicit rule."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md"
  - statement: "The `conditions` string is either empty or one or more `&`-joined clauses restricted to `kind=<0-65535>`, `created_at<<0-4294967295>` or `created_at><0-4294967295>`, in canonical base-10 with no leading zeros and no whitespace; a trailing/leading/double `&` is malformed. Self-attestation (owner pubkey equal to the agent's own pubkey) is invalid and MUST be rejected by both signer and verifier."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md"
  - statement: "crates/buzz-sdk/src/nip_oa.rs is the canonical implementation: `compute_auth_tag` rejects self-attestation and invalid conditions before signing and returns the tag as a JSON array string; `verify_auth_tag` reconstructs the preimage and verifies the BIP-340 Schnorr signature, returning the owner's `PublicKey` on success; `parse_auth_tag` performs structural-only validation (four elements, lowercase-hex lengths, conditions grammar) with no cryptographic check, documented in its own doc comment as 'the fast path used at MCP startup -- no crypto is performed'."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:146-166"
      - "crates/buzz-sdk/src/nip_oa.rs:179-236"
      - "crates/buzz-sdk/src/nip_oa.rs:238-299"
  - statement: "buzz-sdk's own unit tests reproduce the spec's published test vector (owner_secret ending `...0001`, agent_secret ending `...0002`, conditions `kind=1&created_at<1713957000`) and assert both the SHA-256 preimage hash and the Schnorr signature verify against the exact values docs/nips/NIP-OA.md publishes in its 'Test Vectors' section."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:301-333"
      - "crates/buzz-sdk/src/nip_oa.rs:486-494"
      - "docs/nips/NIP-OA.md"
  - statement: "crates/buzz-core/src/kind.rs, the authoritative source for Buzz kind numbers, defines no kind for NIP-OA. NIP-OA's `auth` tag attaches to events of any existing kind rather than introducing a new one; its own `kind=<n>` condition clause optionally restricts which kinds one attestation covers, but the tag mechanism itself is kind-agnostic."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "docs/nips/NIP-OA.md"
  - statement: "crates/buzz-relay/src/handlers/auth.rs extracts the `auth` tag from the client's already-signed NIP-42 AUTH event itself, not from a separate header, via `extract_auth_tag_json`, and its own doc comment states the tag 'is integrity-protected by the event signature' -- if tampered, NIP-42 verification fails before the tag is ever inspected. `extract_auth_tag_json` treats more than one `auth` tag as no valid tag, matching the spec's own multiplicity rule."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:1-36"
  - statement: "crates/buzz-relay/src/api/mod.rs's relay_members module implements the delegation contract: `check_relay_membership`/`enforce_relay_membership` let an agent that is not itself a relay member gain session-scoped access when its NIP-OA-attested owner IS a member, but only on a closed relay (`require_relay_membership = true`) and only when the `allow_nip_oa_auth` config flag is also true. That flag defaults to `false`, set via `BUZZ_ALLOW_NIP_OA_AUTH`, and a dedicated config test asserts the false default."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:63-147"
      - "crates/buzz-relay/src/config.rs:277-287"
      - "crates/buzz-relay/src/config.rs:1367-1368"
  - statement: "`extract_nip_oa_owner` performs owner extraction unconditionally on open relays (`require_relay_membership = false`), with no config flag gating it -- its own doc comment states 'the NIP-OA signature is cryptographically self-proving, so no feature flag is needed'. `materialize_nip_oa_owner` then persists the resulting agent-to-owner mapping first-write-wins: an existing mapping is accepted only when it names the same owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:149-169"
      - "crates/buzz-relay/src/api/mod.rs:171-234"
  - statement: "crates/buzz-relay/src/handlers/auth.rs's `handle_auth` cascades a moderation ban from a banned owner to that owner's cryptographically-proven agents at the NIP-42 AUTH seam: a ban on the agent pubkey itself blocks directly; if the agent is otherwise clear, its NIP-OA owner (extracted with no DB round-trip) is also checked, and an owner ban denies the connection. crates/buzz-relay/src/api/git/transport.rs's `deny_banned_git_principal` implements the identical cascade independently for git smart HTTP, citing the WebSocket gate in its own doc comment as the pattern it mirrors."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:86-184"
      - "crates/buzz-relay/src/api/git/transport.rs:233-271"
  - statement: "crates/buzz-relay/src/api/bridge.rs (the `POST /events` bridge), api/media.rs, api/gifs.rs and api/workflows.rs all read an `x-auth-tag` HTTP header and feed it through the same `enforce_relay_membership`/`extract_nip_oa_owner` functions the WebSocket handler uses, so the delegation mechanism is uniform between the WebSocket protocol and the narrow HTTP bridge surface -- one shared verification path, two transports."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:889-915"
      - "crates/buzz-relay/src/api/media.rs:211"
      - "crates/buzz-relay/src/api/media.rs:537"
      - "crates/buzz-relay/src/api/gifs.rs:156"
      - "crates/buzz-relay/src/api/workflows.rs:72"
  - statement: "crates/buzz-relay/src/api/git/transport.rs's own comment states that git 'cannot carry a standalone x-auth-tag header through the credential-helper protocol', so on the git smart-HTTP path the NIP-OA tag instead rides inside the already-signed NIP-98 auth event, with the bare `x-auth-tag` header accepted only as a fallback when the event itself carries none."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:203-227"
  - statement: "crates/buzz-relay/src/handlers/identity_archive.rs reuses `verify_auth_tag` (via its own `verify_auth_tag_owner` wrapper) to gate a non-admin actor's identity-archive request: the actor must supply a NIP-OA tag naming themselves as owner of the target, AND the target's own live kind:0 profile event must independently carry a valid NIP-OA tag naming that same owner. Consent is established by two independently-verified attestations agreeing, not by a bare request parameter."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs:252-296"
      - "crates/buzz-relay/src/handlers/identity_archive.rs:320-325"
  - statement: "crates/buzz-cli/src/lib.rs parses and verifies `BUZZ_AUTH_TAG` at startup through the SDK's `parse_auth_tag`/`verify_auth_tag` before it is used anywhere, with a documented presentation-layer leniency (`normalize_auth_tag_input`) that rewrites an unquoted shorthand `[auth,hex,,hex]` (as hand-typed into a `.env` file) into strict JSON before the strict SDK parser ever sees it; inputs that are already valid JSON, or not recognizable as the shorthand, pass through unchanged so the parser's error references the caller's original bytes. crates/buzz-cli/src/client.rs then attaches the verified tag's canonical JSON as the `x-auth-tag` header on relay HTTP requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:2020-2096"
      - "crates/buzz-cli/src/client.rs:527"
      - "crates/buzz-cli/src/client.rs:615-618"
  - statement: "crates/buzz-cli/src/commands/users.rs's `owner_verification` helper, used by `cmd_get_users`, classifies each returned profile's NIP-OA status as one of `missing_auth`, `multiple_auth_tags`, `invalid_agent_pubkey`, `invalid_auth`, `owner_mismatch`, `condition_mismatch` or `verified`, by re-running `verify_auth_tag` against the profile's own tag and separately checking whether the tag's `conditions` clauses evaluate true against that same profile event's `kind`/`created_at`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/users.rs:190-236"
  - statement: "crates/buzz-acp/src/lib.rs's `resolve_agent_owner` resolves an agent's owner pubkey at startup from `BUZZ_AUTH_TAG` via `verify_auth_tag`, with a documented priority order (NIP-OA attestation first, falling back to an explicit `--agent-owner`/`BUZZ_ACP_AGENT_OWNER` config value); separately, `setup_mode.rs`'s `run_setup_listener` parses the same env var with the lighter-weight `parse_auth_tag` (structural only) to build the `Tag` it hands to `HarnessRelay::connect`. The harness then attaches that tag as the `x-auth-tag` header on its own REST bridge client (`RestClient`) for `POST /query` and `POST /events` calls."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:135-159"
      - "crates/buzz-acp/src/setup_mode.rs:307-320"
      - "crates/buzz-acp/src/relay.rs:255"
      - "crates/buzz-acp/src/relay.rs:393-406"
  - statement: "crates/buzz-acp/src/lib.rs's `check_sibling_via_profile` (starting line 309) fully cryptographically verifies a candidate sibling agent's NIP-OA tag against an expected owner via `verify_auth_tag` (the check itself at lines 355-364) before trusting a reply-anchoring relationship between two agent profiles. This is a distinct, stricter check from pool.rs's presence-only heuristic (next entry) and the two must not be conflated."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:309-378"
  - statement: "crates/buzz-acp/src/pool.rs's `profile_event_is_agent` checks only for the presence of a well-formed four-element `auth` tag on a kind:0 profile, and its own doc comment states this is 'a cheap routing heuristic for reply anchoring, not a verified security gate' -- the full cryptographic check lives separately in lib.rs's sibling-verification path cited above. A reader of this node must not conflate the two: tag-presence classifies agent-vs-human without proving an owner relationship; only a successful `verify_auth_tag` call establishes one."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:3578-3593"
  - statement: "crates/git-credential-nostr/tests/integration.rs has a test named `includes_nip_oa_auth_tag_in_signed_event` asserting this git credential helper includes a NIP-OA `auth` tag in the Nostr events it signs for git push, and a test named `malformed_nip_oa_auth_tag_fails_closed` asserting a malformed tag causes the operation to fail rather than proceed unauthenticated."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/tests/integration.rs:126"
      - "crates/git-credential-nostr/tests/integration.rs:174"
  - statement: "docs/nips/NIP-OA.md states relays 'require no changes to support this NIP', 'MUST NOT rewrite event authorship on the basis of an auth tag', and 'MUST NOT be required to verify an auth tag' -- an unrecognizing relay stores and forwards the tag as an ordinary opaque tag array, so the mechanism composes without a relay-side compatibility break. Nothing about the tag or its verification requires bumping a protocol version."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md"
  - statement: "docs/nips/NIP-OA.md states that its `created_at<`/`created_at>` clauses constrain the event's self-declared `created_at` field, which the agent itself controls, and explicitly warns 'a misbehaving agent can backdate event.created_at to satisfy an expired window' and that 'Verification MUST NOT depend on the verifier's local clock, receipt time, or relay storage time' -- so NIP-OA's own conditions grammar provides no wall-clock freshness guarantee, only a self-declared one a verifier can choose to trust or not."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md"
  - statement: "A NIP-OA `auth` tag is a reusable capability by the spec's own design (the same tag MAY appear on multiple events), so this interface has no replay-prevention or single-use semantics of its own; ordering/idempotency at the delegation layer instead comes from `materialize_nip_oa_owner`'s first-write-wins persistence, which is idempotent by construction (a repeat call with the same agent/owner pair returns the same accepted state)."
    entry_class: INFERENCE
    evidence:
      - "docs/nips/NIP-OA.md"
      - "crates/buzz-relay/src/api/mod.rs:171-234"
    confidence: 0.85
  - statement: "`architecture-flows-websocket-authentication`, an already-merged corpus node on origin/launchpad, documents the NIP-42 challenge/response flow (relay sends [\"AUTH\",\"<challenge>\"], client signs a kind:22242 event) that NIP-OA's `auth` tag rides inside of on the WebSocket path -- the concrete tie-in this node's `references` relationship points at."
    entry_class: FACT
    evidence:
      - "git_show(ref='origin/launchpad', path='launchpad/docs/corpus/architecture/flows/websocket-authentication.md') -> front matter id: architecture-flows-websocket-authentication"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# NIP-OA (Owner Attestation): interface

This node documents Buzz's own custom NIP extension, NIP-OA (Owner Attestation),
specified in `docs/nips/NIP-OA.md`: an optional `auth` tag any signed Nostr event
may carry, by which an owner key cryptographically authorizes an agent key to act
on its behalf without the event ever being reassigned to the owner as author. The
boundary is not a single wire message but a capability artifact (the tag itself,
self-proving via a BIP-340 Schnorr signature) that is checked at several distinct
call sites across this repository -- the relay's WebSocket NIP-42 AUTH path, its
narrow HTTP bridge surface, its git smart-HTTP path, `buzz-cli`'s own auth-tag
commands, and the `buzz-acp` agent harness -- all funneling through one shared
implementation, `crates/buzz-sdk/src/nip_oa.rs`.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `compute_auth_tag` | `crates/buzz-sdk/src/nip_oa.rs:146-166` | Owner signs an agent pubkey + conditions into a tag; rejects self-attestation and invalid conditions. |
| `verify_auth_tag` | `crates/buzz-sdk/src/nip_oa.rs:179-236` | Cryptographically verifies a tag against an agent pubkey; returns the owner `PublicKey` on success. |
| `parse_auth_tag` | `crates/buzz-sdk/src/nip_oa.rs:238-299` | Structural-only validation (arity, hex shape, conditions grammar); no signature check. |
| WebSocket NIP-42 AUTH delegation | `crates/buzz-relay/src/handlers/auth.rs:26-295` | Tag extracted from the signed AUTH event itself; grants closed-relay membership via a verified owner, or backfills owner on open relays; bans cascade owner→agent. |
| HTTP `x-auth-tag` header delegation | `crates/buzz-relay/src/api/bridge.rs:889-915`, `api/media.rs`, `api/gifs.rs`, `api/workflows.rs` | Same delegation functions as the WebSocket path, fed from a header instead of an event tag. |
| Git smart-HTTP delegation | `crates/buzz-relay/src/api/git/transport.rs:204-271` | Tag rides inside the signed NIP-98 auth event (no bare header available in the credential-helper protocol); same membership + ban-cascade logic. |
| Identity-archive owner consent | `crates/buzz-relay/src/handlers/identity_archive.rs:252-325` | Requires two independently-verified NIP-OA attestations (requester + target's live profile) to agree on the same owner. |
| `buzz users` owner-verification | `crates/buzz-cli/src/commands/users.rs:190-236` | Classifies a listed profile's tag as verified/owner_mismatch/condition_mismatch/invalid/missing, for operator inspection. |
| `BUZZ_AUTH_TAG` (env var / CLI) | `crates/buzz-cli/src/lib.rs:2020-2096` | Client-side parse + verify + `x-auth-tag` header attachment (`client.rs:615-618`), with shorthand-input normalization at the config edge only. |
| `buzz-acp` owner resolution + attachment | `crates/buzz-acp/src/lib.rs:135-159`, `crates/buzz-acp/src/relay.rs:255,393-406` | Harness resolves its own owner from `BUZZ_AUTH_TAG` at startup and attaches it to its own REST bridge calls. |
| `git-credential-nostr` signed push | `crates/git-credential-nostr/tests/integration.rs:126,174` | Includes a NIP-OA tag in signed git-push events; fails closed on a malformed tag. |

## Contract and stability

- **The tag is the auth artifact.** There is no separate token, session, or
  registration step -- a syntactically valid, Schnorr-verified `auth` tag *is*
  authorization, and it is a reusable capability (the same tag may appear on many
  events), not a single-use credential. Callers may rely on `verify_auth_tag`
  returning `Ok(owner_pubkey)` if and only if all of the spec's structural and
  cryptographic rules hold, and `Err(SdkError::InvalidInput(..))` otherwise --
  the SDK never partially succeeds.
- **No relay-side compatibility break.** Per the spec, relays "require no
  changes to support this NIP" and "MUST NOT be required to verify an auth tag";
  Buzz's own relay treats an absent or invalid tag as simply no delegation, never
  as a protocol error. No Nostr event kind is added for this NIP (confirmed
  against `crates/buzz-core/src/kind.rs`, which has no NIP-OA-specific entry) --
  the tag attaches to events of whatever kind the agent is already publishing.
- **`allow_nip_oa_auth` gates the *access-granting* half only, not extraction.**
  On a closed relay, an agent may only gain membership through a proven owner
  when this config flag (default `false`, `BUZZ_ALLOW_NIP_OA_AUTH`) is set. On
  an open relay, owner extraction for agent→owner backfill happens
  unconditionally, because the spec's own security property (self-proving
  Schnorr signature) makes a feature flag unnecessary for that half.
- **Ban cascade is owner→agent, one direction only.** A ban on a proven owner
  denies that owner's agents; the spec itself does not define this behavior --
  it is this repository's own moderation-plan decision, implemented twice
  (WebSocket `handlers/auth.rs`, git `api/git/transport.rs`) with the git path's
  comment explicitly citing the WebSocket path as the pattern being mirrored.
  Banning an agent does not ban its owner or its siblings.
- **No wall-clock freshness guarantee.** The `created_at<`/`created_at>`
  conditions constrain the event's own self-declared `created_at`, which the
  agent controls; the spec itself warns a misbehaving agent can backdate it, and
  states verification "MUST NOT depend on the verifier's local clock." A caller
  needing real expiry must build it on top of this interface, not rely on it.
- **`x-auth-tag` is a stable header name and `BUZZ_AUTH_TAG` a stable env var
  name** depended on identically by `buzz-relay`'s HTTP bridge, `buzz-cli`, and
  `buzz-acp` -- renaming either is a breaking change across all three.
- **Presence is not proof.** `pool.rs`'s `profile_event_is_agent` checks only
  that a well-formed four-element `auth` tag exists, by its own admission "not a
  verified security gate." Any consumer of this interface that needs an actual
  owner relationship must call `verify_auth_tag` (or the relay's
  `extract_nip_oa_owner`/`enforce_relay_membership`), never infer it from
  tag presence alone.

## Errors and rejection behavior

- **Malformed tag (SDK level):** `parse_auth_tag`/`verify_auth_tag` return
  `SdkError::InvalidInput(String)` for: wrong element count, non-`"auth"` first
  element, non-hex or wrong-length owner pubkey/signature, malformed
  `conditions` grammar (whitespace, leading zero, unsupported clause, wrong
  operator, out-of-range value, empty/trailing/leading/double `&`),
  self-attestation, or a signature that fails Schnorr verification.
- **Malformed or absent tag (relay level):** treated as "no valid delegation" --
  `extract_nip_oa_owner` returns `None` (logged at `info` level) rather than
  propagating an error; the caller then falls through to whatever the
  non-delegated path already does (deny on a closed relay, no backfill on an
  open one).
- **DB failure during a ban check is fail-closed, not fail-open:** a
  moderation-restriction DB error denies the connection with `error: internal`,
  distinguished in the response from an actual ban, per
  `handlers/auth.rs`'s own `BanOutcome::DbError` branch.
- **`BUZZ_AUTH_TAG` malformed at CLI startup** is a hard `CliError::Auth`,
  surfaced before any relay call is attempted, naming the caller's own pubkey in
  the message for operator debugging.

## Authentication and authorization

Authorization is entirely cryptographic and stateless: there is no bearer
token, session cookie, or server-issued credential distinct from the Schnorr
signature itself. Three related but distinct authorization questions this
interface answers, and the exact function each answers:

1. **Is this a valid attestation at all?** -- `verify_auth_tag` (structure +
   signature).
2. **Does a valid attestation grant *this* agent relay access?** --
   `enforce_relay_membership`, gated by `allow_nip_oa_auth` on closed relays,
   unconditional extraction-only on open ones.
3. **Is a banned owner's agent still allowed to authenticate?** -- No: the ban
   cascade (`handlers/auth.rs`, `api/git/transport.rs`) denies it regardless of
   `allow_nip_oa_auth`, because a ban check runs before and independently of
   the membership gate.

## Ordering and idempotency

A signed `auth` tag is reusable across events by design (no nonce, no
single-use marker) -- this is a documented spec property, not an
implementation gap. The one idempotency guarantee this interface does make is
at the persistence layer: `materialize_nip_oa_owner`'s agent→owner mapping is
first-write-wins, and a repeated call with the same (agent, owner) pair is
accepted as already-satisfied rather than rejected or duplicated.

## Boundary

This node does not describe:
- **Any single Nostr event kind's own wire contract.** NIP-OA defines a tag,
  not a kind -- `crates/buzz-core/src/kind.rs` has no NIP-OA-specific kind, and
  the tag can attach to an event of any kind. The kind-22242 NIP-42 AUTH event
  the tag often rides inside of on the WebSocket path is documented by the
  `architecture-flows-websocket-authentication` node this one `references`, not
  restated here.
- **A full parameter-by-parameter catalogue** of every one of the dozen-plus
  call sites' surrounding function signatures for domain-expert readers -- the
  *Operations* table above points at each one by file/line instead.
- **NIP-26, NIP-42, or NIP-98 as their own subjects.** NIP-26 is cited only as
  this NIP's acknowledged prior art for the credential/signing-flow shape (and
  explicitly *not* reused for its authorship semantic); NIP-42 is the WebSocket
  challenge/response flow the tag piggybacks on (own corpus node,
  `references`d above); NIP-98 is the HTTP/git auth event the tag piggybacks on
  in the git transport. None of the three has a corpus node yet and none is
  created by this task, per the Definition of done's rule that a newly
  discovered second concept becomes its own task.
- **`buzz-db`'s `agent_owner_pubkey` storage schema** beyond the one fact
  needed for the contract above (first-write-wins persistence) -- the table's
  full shape is a data-entity concern, not this interface's.

## Relationships

- `references`: `architecture-flows-websocket-authentication` -- the NIP-42
  challenge/response flow whose signed AUTH event is where the WebSocket path's
  `auth` tag is extracted from.

## Valid and failure examples

**Valid** -- `docs/nips/NIP-OA.md`'s own published test vector: owner secret
`...0001`, agent secret `...0002`, `conditions=kind=1&created_at<1713957000`,
producing the signed event

```json
{
  "id": "d892a65e7677e0554ebb70ee16deeb6a0727dba46450fb4bc001291d7bff971b",
  "pubkey": "c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5",
  "created_at": 1713956400,
  "kind": 1,
  "tags": [["auth", "79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798", "kind=1&created_at<1713957000", "8b7df2575caf0a108374f8471722b233c53f9ff827a8b0f91861966c3b9dd5cb2e189eae9f49d72187674c2f5bd244145e10ff86c9f257ffe65a1ee5f108b369"]],
  "content": "owner-attested agent event",
  "sig": "7fd38992b70b5e9e113644e51b4c8ee2227f3bdd402b1855f8786c0600394ab3ec2621742a7bad0b0000b93d4d1ae6e39525f286a3c1029f43f46c3359a6c76f"
}
```

`crates/buzz-sdk/src/nip_oa.rs`'s own `test_verify_spec_test_vector` and
`test_spec_sha256_hash` reproduce this exact vector's hash and signature.

**Failure** -- `docs/nips/NIP-OA.md`'s own "Invalid Test Vectors" section lists,
among others: an event with two `auth` tags; an `auth` tag with fewer or more
than four elements; `conditions = "kind=1&"` (trailing delimiter);
`conditions = "kind=01"` (leading zero); `owner-pubkey-hex` equal to
`event.pubkey` (self-attestation); and an otherwise well-formed tag on an event
whose Nostr `id`/`sig` is itself invalid. `crates/buzz-sdk/src/nip_oa.rs`'s
`test_reject_*` unit tests independently exercise each of these categories
(`test_reject_self_attestation`, `test_reject_trailing_ampersand`,
`test_reject_leading_zero`, `test_reject_malformed_tag`).

## Scope and omissions

**This node covers** the NIP-OA `auth` tag as one interface: its wire shape and
signing contract per `docs/nips/NIP-OA.md`, the canonical SDK implementation in
`crates/buzz-sdk/src/nip_oa.rs`, and how every call site in this repository --
WebSocket NIP-42 AUTH, the HTTP `x-auth-tag` header (bridge/media/gifs/
workflows), git smart HTTP, identity-archive consent, `buzz-cli`'s auth-tag
commands, and the `buzz-acp` harness -- consumes it for relay-membership
delegation, moderation ban cascade, and owner-relationship classification.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The NIP-42 challenge/response wire flow the WebSocket `auth` tag rides inside of | `architecture-flows-websocket-authentication` (already merged) |
| NIP-26, NIP-98 as their own subjects | No corpus node yet; not created by this task |
| The `agent_owner_pubkey` storage schema in `buzz-db` | A future data-entity node, if one is written |
| Field-by-field, domain-expert-depth API-parameter cataloguing of each call site | `#1346`/`#1532`'s undecided reference-depth scope |

**Expected but not verified when this node was written:**
- **Whether `allow_nip_oa_auth` is exercised by any current integration test**
  beyond the config-default unit test cited above was not separately checked --
  this node cites the config flag's existence and default, not a live-relay
  demonstration of the closed-relay delegation grant succeeding end to end.
- **`crates/buzz-test-client`'s `authenticate_with_nip_oa` helper** was located
  but its own body was not opened in this pass; it is a test-support function
  that exercises this interface, not a distinct operation of it, and citing it
  would have added a citation with no new claim behind it.
