---
id: events-kinds-kind-22242-auth
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a8b5021efb92264e724366d08b47b2a3839eb90a."
    entry_class: FACT
    evidence:
      - "commit a8b5021efb92264e724366d08b47b2a3839eb90a"
  - statement: "Kind 22242 is registered in Buzz's kind registry as KIND_AUTH, documented there as the NIP-42 auth event that is never stored because it carries bearer tokens."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:76-77"
  - statement: "NIP-42 (Authentication of Clients to Relays), at the commit this repository already pins elsewhere for the nips specification set, requires the AUTH event to be 'kind: 22242' carrying at least a relay tag (the relay URL) and a challenge tag (the nonce received from the relay), and requires a client's AUTH message to be answered with an OK message, with failure messages using the 'auth-required:' or 'restricted:' prefixes."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/42.md"
  - statement: "buzz-auth's own module documentation states that the NIP-42 path is 'Challenge/response; client signs kind:22242 event' and, as a stated security invariant, that 'AUTH events (kind:22242) are NEVER stored or logged.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs:9"
      - "crates/buzz-auth/src/lib.rs:14"
  - statement: "NIP-01, at the same pinned commit, classifies a kind n such that 20000 <= n < 30000 as ephemeral ('not expected to be stored by relays'); kind.rs independently defines the identical boundary (EPHEMERAL_KIND_MIN=20000, EPHEMERAL_KIND_MAX=29999) and kind 22242 falls inside it, so kind.rs's own is_ephemeral classification for KIND_AUTH agrees with NIP-01's range."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
      - "crates/buzz-core/src/kind.rs:457-459"
      - "crates/buzz-core/src/kind.rs:769-771"
  - statement: "KIND_AUTH is not a member of ALL_KINDS, the array kind.rs itself documents as 'used for duplicate detection and iteration' over the registry."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:634-766"
  - statement: "verify_nip42_event rejects an AUTH event unless: event.kind is Kind::Authentication (22242); buzz_core::verify_event confirms a valid id and signature; the event's challenge tag equals the challenge issued for that connection; the event's relay tag, normalized, equals the relay's own URL, normalized (including a localhost/127.0.0.1 equivalence and trailing-slash stripping); and created_at is within TIMESTAMP_TOLERANCE_SECS (60 seconds) of now."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:35"
      - "crates/buzz-auth/src/nip42.rs:47-86"
  - statement: "An AUTH event MAY carry a third tag, auth, shaped [\"auth\", \"<owner-pubkey-hex>\", \"<conditions>\", \"<sig-hex>\"] per NIP-OA/NIP-AA; the relay's handle_auth extracts it via extract_auth_tag_json, treating zero or exactly one auth tag as valid and more than one as no valid tag at all (fail-closed)."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md:29"
      - "crates/buzz-relay/src/handlers/auth.rs:26-36"
  - statement: "Buzz's own shared WebSocket client builds the AUTH event via build_auth_event, which wraps EventBuilder::auth(challenge, relay_url) and optionally attaches one caller-supplied tag (the NIP-OA auth tag); no call on this path sets a content value."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs:169-190"
  - statement: "This repository's own crate inventory documents buzz-ws-client as the 'Shared NIP-42 WebSocket client (connect, auth, publish)', i.e. the one implementation the CLI, desktop, and other Buzz-authored clients build a kind-22242 AUTH event through, rather than each reimplementing NIP-42 independently."
    entry_class: FACT
    evidence:
      - "AGENTS.md:84"
  - statement: "The AUTH event's content field carries no meaningful payload: NIP-42 at the pinned commit states no content requirement for it, verify_nip42_event never inspects event.content, and neither of Buzz's own AUTH-event constructors (nip42.rs's test helper, buzz-ws-client's build_auth_event) ever sets one."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/nip42.rs:47-86"
      - "crates/buzz-ws-client/src/message.rs:174-190"
    confidence: 0.8
  - statement: "The relay generates a fresh NIP-42 challenge per WebSocket connection at accept time, sends it as [\"AUTH\", \"<challenge>\"], stores it as AuthState::Pending{challenge} on the connection, and dispatches a client's [\"AUTH\", <event>] message to handlers::auth::handle_auth."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:167"
      - "crates/buzz-relay/src/connection.rs:182-188"
      - "crates/buzz-relay/src/connection.rs:204"
      - "crates/buzz-relay/src/connection.rs:560-566"
      - "crates/buzz-relay/src/protocol.rs:160-169"
      - "crates/buzz-relay/src/protocol.rs:182-184"
  - statement: "On successful NIP-42 verification, handle_auth chains three further gates before marking the connection authenticated: a community ban check on the pubkey (and, via NIP-OA, its cryptographically-proven owner) that fails closed on a DB error rather than an established ban; an optional pubkey-allowlist check that applies only to pubkey-only NIP-42 auth; and relay-membership enforcement (with NIP-OA owner-delegation fallback). Only after all three pass does it set AuthState::Authenticated(auth_ctx) and reply with an OK success message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:93-184"
      - "crates/buzz-relay/src/handlers/auth.rs:186-214"
      - "crates/buzz-relay/src/handlers/auth.rs:216-238"
      - "crates/buzz-relay/src/handlers/auth.rs:277-283"
  - statement: "AuthService::verify_auth_event returns an AuthContext with scopes set to Scope::all_known() and auth_method: AuthMethod::Nip42 whenever NIP-42 verification succeeds; per-channel access after that point is enforced separately by the relay's NIP-29 membership checks, not by narrowing scopes at auth time."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs:126-154"
  - statement: "A kind-22242 event cannot be submitted as an ordinary event: the WebSocket EVENT handler rejects it with 'invalid: AUTH events cannot be submitted via EVENT', and the shared WS/HTTP ingest path (used by POST /events) rejects it with 'invalid: AUTH events cannot be submitted', both via an early return before any database insert or channel broadcast runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:670-678"
      - "crates/buzz-relay/src/handlers/ingest.rs:2182-2186"
  - statement: "Even if an AUTH event reached the database layer, both insert paths (insert_event_on and insert_event_with_serving_write_guard) refuse it explicitly, returning DbError::AuthEventRejected ('AUTH events (kind 22242) must not be stored') before any row is written; buzz-db's own crate- and module-level docs state the same invariant."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:304-306"
      - "crates/buzz-db/src/runtime/mod.rs:924-926"
      - "crates/buzz-db/src/error.rs:16-18"
      - "crates/buzz-db/src/lib.rs:6"
      - "crates/buzz-db/src/store/event.rs:3"
  - statement: "No file in buzz-search or buzz-audit references KIND_AUTH or the literal 22242, consistent with an event that is never inserted into the event store those two systems index (search) or hash-chain (audit) from."
    entry_class: FACT
    evidence:
      - "grep(KIND_AUTH|22242, crates/buzz-search, crates/buzz-audit) -> no matches"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs::test_auth_event_kind_rejected asserts that submitting a signed kind-22242 event via the test client's send_event (i.e. as an ordinary EVENT) is rejected with a message containing 'invalid' or 'auth'; the test is marked #[ignore] because it requires a live relay instance, the same convention the file's other e2e cases use."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:844-871"
  - statement: "buzz-auth's own unit tests (in nip42.rs and lib.rs) directly exercise: challenge uniqueness and hex format, a valid AUTH event passing, wrong-challenge/wrong-relay/wrong-kind rejection, an expired-timestamp rejection, localhost/127.0.0.1 relay-URL equivalence, trailing-slash normalization, and AuthService::verify_auth_event succeeding end-to-end with full read/write scopes."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:88-183"
      - "crates/buzz-auth/src/lib.rs:180-254"
  - statement: "Issue #873's definition of done requires this node to state the kind number/name and persistence classification, define required/optional tags and validation rules, name producers/consumers/authorization/persistence/fanout/search/audit treatment, and link the NIP/spec plus handler/registry/conformance evidence -- the checklist this document is organized against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#873 definition of done"
---

# Event kind: `KIND_AUTH` (22242) — NIP-42 AUTH event

The NIP-42 challenge/response authentication event. A client signs one of these in
response to the relay's `["AUTH", "<challenge>"]` message to prove control of a Nostr
keypair over the current WebSocket connection. It is Buzz's primary authentication
mechanism for WebSocket clients (the HTTP-side counterpart is NIP-98, kind 27235,
documented separately).

## 1. Title and kind identity

- **Name**: NIP-42 AUTH event.
- **Number**: `22242`.
- **Constant**: `KIND_AUTH: u32 = 22242` in `crates/buzz-core/src/kind.rs:77`.
- **Front-matter `type`**: `interfaces-events` — the corpus-surface value
  `node.schema.json` reserves for the combined interface/event surface.
- **Status**: implemented and enforced today, not proposed. Every claim below is
  checked against code already merged to `origin/launchpad` at the recorded revision.

## 2. Referenced NIP

**NIP-42 — Authentication of Clients to Relays**
(`nostr-protocol/nips`, pinned at commit
[`dabfcb2`](https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/42.md)).
This is a base community NIP, not a Buzz custom-NIP proposal — there is no
`docs/nips/NIP-*.md` file for kind 22242 itself.

Buzz also defines **NIP-AA (Agent Authentication)**, its own custom-NIP at
`docs/nips/NIP-AA.md`, which *extends* the same kind-22242 AUTH event with an
optional NIP-OA credential tag (see §4 below) to grant an agent virtual relay
membership derived from its owner's membership. NIP-AA "adds no new event kinds" —
kind 22242 remains the single vehicle for both the base NIP-42 flow and the NIP-AA
extension.

## 3. Kind range and delivery classification

**Ephemeral** (NIP-01 range `20000 <= n < 30000`, "not expected to be stored by
relays"). `crates/buzz-core/src/kind.rs`'s own `EPHEMERAL_KIND_MIN`/`MAX` constants
(20000 / 29999) and `is_ephemeral` helper agree with that range, and 22242 falls
inside it — this cross-check turns up no mismatch between the NIP-01 range and
`kind.rs`'s own classification.

Two things sharpen "ephemeral" for this specific kind, beyond the generic NIP-01
definition:

- `KIND_AUTH` is **not** a member of `ALL_KINDS`, the registry array `kind.rs` itself
  says exists "for duplicate detection and iteration." Every other ephemeral or
  regular kind that participates in ordinary ingest/storage is listed there; AUTH is
  not, because it never reaches the code paths that array supports.
- Storage is refused **twice**, independently, at two different layers (§6) — the
  generic ephemeral-kind skip in the store layer is not the only thing standing
  between a kind-22242 event and a database row; there is a second, kind-specific
  guard for exactly this kind.

## 4. Tag shape

| Tag | Cardinality | Value | Source |
|---|---|---|---|
| `relay` | exactly one | The relay's own WebSocket URL, as this relay derives it for the connecting tenant. Compared to the event's `relay` tag after normalizing both (`ws`/`wss` scheme preserved, `localhost` and `::1` treated as `127.0.0.1`, trailing path slash stripped). | NIP-42; `crates/buzz-auth/src/nip42.rs:19-33,68-76` |
| `challenge` | exactly one | The exact challenge string this relay issued for this WebSocket connection, generated once per connection and never reused. | NIP-42; `crates/buzz-auth/src/nip42.rs:37-41,58-66`; `crates/buzz-relay/src/connection.rs:167` |
| `auth` | zero or one | NIP-OA credential: `["auth", "<owner-pubkey-hex>", "<conditions>", "<sig-hex>"]`. Optional — only present when the signing pubkey is an *agent* seeking virtual membership through an owner's relay membership (NIP-AA). More than one `auth` tag is treated as if none were present (fail-closed), not as an ambiguous choice between them. | `docs/nips/NIP-AA.md:29`; `crates/buzz-relay/src/handlers/auth.rs:26-36` |

Beyond tag shape, the event as a whole must satisfy:

- A valid `id` (SHA-256 over the standard NIP-01 serialization) and a valid Schnorr
  `sig` for `pubkey` — checked by `buzz_core::verify_event`, the same signature/id
  check every other Buzz kind uses.
- `created_at` within **60 seconds** of the relay's current time
  (`TIMESTAMP_TOLERANCE_SECS`) — narrower than NIP-01's general looseness about
  timestamps, and specific to this kind's replay-resistance goal.

## 5. Content field semantics

**Empty / unused.** Neither NIP-42's text at the pinned commit nor
`verify_nip42_event` describe or check a `content` requirement, and neither of
Buzz's own AUTH-event constructors — the test helper in `nip42.rs` or the real
producer, `build_auth_event` in `crates/buzz-ws-client/src/message.rs` — ever sets
one. This is recorded as an INFERENCE in the evidence ledger above (not a directly
stated invariant anywhere) at `confidence: 0.8`.

## 6. Access control and storage model

**Never persisted, by design, enforced twice.**

1. **Submission is refused before it can become an ordinary event at all.** Both
   surfaces a client could use to push an event into the relay reject kind 22242
   outright, before any database call or channel broadcast:
   - The WebSocket `EVENT` handler:
     `"invalid: AUTH events cannot be submitted via EVENT"`
     (`crates/buzz-relay/src/handlers/event.rs:670-678`).
   - The shared WS/HTTP ingest path used by `POST /events`:
     `"invalid: AUTH events cannot be submitted"`
     (`crates/buzz-relay/src/handlers/ingest.rs:2182-2186`).
2. **The database layer refuses it a second time, independently**, as defense in
   depth: both `insert_event_on` and
   `insert_event_with_serving_write_guard` return
   `DbError::AuthEventRejected` ("AUTH events (kind 22242) must not be stored")
   before any row is written
   (`crates/buzz-db/src/store/event.rs:304-306`,
   `crates/buzz-db/src/runtime/mod.rs:924-926`).

Because it is never inserted, it also never reaches the systems that operate on
stored rows: it is not indexed by `buzz-search`'s full-text search, not chained by
`buzz-audit`'s hash-chain audit log, and not fanned out to subscribers by
`buzz-pubsub` — none of those crates reference `KIND_AUTH` or the literal `22242`
at all.

**Producers.** Any Nostr client — human-operated app or agent — that has received
this relay's `["AUTH", "<challenge>"]` message on its WebSocket connection.
Buzz's own clients (CLI, desktop, and others) all build the event through the one
shared implementation, `buzz-ws-client`'s `build_auth_event`
(`AGENTS.md:84`; `crates/buzz-ws-client/src/message.rs:169-190`), rather than each
constructing the tags independently.

**Consumer.** The relay itself, and only the relay: `handlers::auth::handle_auth`
on the WebSocket connection that issued the matching challenge. No other
component ever reads a kind-22242 event, because none is ever stored or
broadcast for one to read.

**Authorization outcome.** A successful `verify_nip42_event` call alone does not
authenticate a connection. `handle_auth` chains three further gates afterward, in
this order, each capable of independently failing the attempt:

1. **Community ban check** — on the authenticated pubkey directly, and, via a
   self-proving NIP-OA `auth` tag, on its cryptographically-attested owner too (a
   banned owner's agents are blocked even though the agent pubkey itself was never
   banned). A DB error here **fails closed** — denied, not silently waved through —
   but is distinguished in logs/metrics from an actual ban.
2. **Pubkey allowlist** — only applies to pubkey-only NIP-42 auth
   (`auth_method == AuthMethod::Nip42`), when the relay has
   `pubkey_allowlist_enabled` configured.
3. **Relay membership** — NIP-29/NIP-43 membership enforcement, with NIP-OA
   owner-delegation fallback (NIP-AA) so an agent whose owner is a member can gain
   virtual membership without being separately enrolled.

Only once all three pass does `handle_auth` set
`AuthState::Authenticated(auth_ctx)` and reply with an `OK` success message. On
success in *pure-Nostr mode*, `AuthService::verify_auth_event` grants
`Scope::all_known()` — full read/write scopes — to the `AuthContext`; the
relay does not narrow scopes at the AUTH step itself. Finer-grained access (which
channels a pubkey may read or write) is enforced separately, per-operation, by the
relay's NIP-29 channel-membership checks, not by anything encoded in the AUTH
event or its resulting `AuthContext.scopes`.

**Rejection responses.** Failure messages in this repository's implementation use
the NIP-42-style prefixes `auth-required:` and `restricted:`, plus this repository's
own `invalid:`, `banned:`/`blocked:`, and `error:` prefixes for cases NIP-42 itself
does not enumerate (a submitted-as-EVENT rejection, a ban, or an internal DB
failure) — see `crates/buzz-relay/src/handlers/auth.rs` and
`crates/buzz-relay/src/handlers/event.rs` for the exact strings.

## 7. Worked example

A direct-member AUTH event (no NIP-OA credential):

```json
{
  "id": "5c2c...redacted-for-illustration...a91f",
  "pubkey": "aa3344...redacted...bb7788",
  "created_at": 1735689600,
  "kind": 22242,
  "tags": [
    ["relay", "wss://relay.example.com"],
    ["challenge", "9f2b6a1d4e7c8035b1f0a6d2c4e8f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5"]
  ],
  "content": "",
  "sig": "..."
}
```

The NIP-AA variant, sent by an agent key whose owner is the relay member, adds the
`auth` tag carrying the owner's NIP-OA credential:

```json
{
  "id": "7e1a...redacted-for-illustration...c204",
  "pubkey": "cc5566...redacted...dd9900",
  "created_at": 1735689600,
  "kind": 22242,
  "tags": [
    ["relay", "wss://relay.example.com"],
    ["challenge", "b7b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1"],
    ["auth", "ee7788...redacted-owner-pubkey...ff1122", "", "...redacted-owner-signature..."]
  ],
  "content": "",
  "sig": "..."
}
```

## 8. Versioning and supersession

Not applicable. Kind 22242 is used directly as the base NIP-42 protocol defines
it; Buzz has never used, and does not document, a different kind number for this
same purpose.

## 9. Relationships to other kinds and nodes

None declared. At the recorded revision, `origin/launchpad`'s
`launchpad/docs/corpus` tree carries no other event-kind or interface node this
node could point at without inventing an id — the only sibling corpus content that
exists is the four meta-documents (`corpus-agents`, `corpus-readme`,
`corpus-standard-confidence`, `corpus-standard-decision-references`) plus the
`templates/event-kind.md` template itself, none of which is a node id a
`relationships` entry can target. The template this node was written against
(`corpus-template-event-kind`) also carries no `id` a real instance can currently
target with `implements`, since the enum value for a relationship target is the
front matter `id` field and the template file's own front matter uses
`corpus-template-event-kind` as its id — that target does exist, but adding a
speculative `implements` edge before any sibling event-kind node exists to
cross-check the convention against is deferred rather than guessed at here. The
likeliest future edges are `implements` → the event-kind template once a second
instance confirms the convention, and `references`/`depends-on` edges to a future
NIP-98 (kind 27235) node and to a future NIP-AA/NIP-OA interface or capability
node, once those are authored.

## Scope and omissions

**This document covers** kind 22242's own wire contract: its number, range
classification, tag shape, content semantics, and the relay-side verification and
authorization sequence a NIP-42 AUTH event of this kind triggers. It intentionally
does not restate NIP-42's full text, and it does not describe NIP-AA's or NIP-OA's
own credential-issuance and delegation semantics beyond the one tag NIP-AA adds to
this kind's own tag shape — those are a different kind's or a different node's
subject.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-98 HTTP Auth (kind 27235) — the HTTP-transport sibling auth path | a future `events-kinds-kind-27235-*` node |
| NIP-OA's owner-attestation issuance format and NIP-AA's full virtual-membership algorithm beyond the one `auth` tag this kind carries | a future capability/interface node for NIP-OA/NIP-AA |
| A `buzz-cli`/`buzz-ws-client` consumer-facing "how do I authenticate" operation surface | a future interface node (the event-kind vs. interface boundary the corpus template names) |
| Whether every Buzz-proposed kind needs a `docs/nips/NIP-XX.md` file — not applicable here since kind 22242 already has an external community NIP | not this node's question to answer |

**Expected but not verified when this node was written:**

- **NIP-AA's own recommended ±120-second freshness window for the credential
  itself** (distinct from this kind's own ±60-second `TIMESTAMP_TOLERANCE_SECS`
  check on `created_at`) was read in `docs/nips/NIP-AA.md` as spec text, but
  whether Buzz's relay enforces that second, NIP-AA-specific window anywhere in
  code was not traced in this node — it belongs to NIP-AA's own credential
  validation, not to this kind's base wire contract, and is named as a gap rather
  than assumed either way.
- **Whether any client other than `buzz-ws-client`'s consumers (CLI, desktop,
  mobile, the agent harness) constructs a kind-22242 event through a different
  code path** was not checked; a third-party Nostr client is free to build one
  independently and correctly per NIP-42 without touching this repository's code
  at all.
- **The exact set of relay configuration flags that change AUTH's required-ness**
  (e.g. whether authentication is ever optional for some connections) was not
  traced end-to-end in this node; `state.config.pubkey_allowlist_enabled` and
  `state.config.require_relay_membership` are both read directly in
  `handlers/auth.rs`, but their own defaults and interactions are a configuration
  node's subject, not this kind's.
