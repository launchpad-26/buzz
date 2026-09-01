---
id: interfaces-nostr-buzz-nips-nip-aa
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
  - statement: "NIP-AA ('Agent Authentication') is a draft, optional, relay-scoped Nostr protocol extension that lets a relay implementing NIP-43 relay membership grant an agent key implicit ('virtual') relay access during NIP-42 authentication when the agent presents a NIP-OA `auth` tag proving its owner is an active relay member, without enrolling the agent in the member list itself."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md:1-21"
  - statement: "NIP-AA's relay verification algorithm is: Step 1 standard NIP-42 verification plus a freshness window (RECOMMENDED ±120s) on the AUTH event's created_at; Step 2 grant access directly if event.pubkey is already an active member; Step 3 extract exactly one `auth` tag (reject if zero or more than one); Step 4 verify the tag (four elements, valid owner pubkey, sig-hex, no self-attestation, syntactically valid conditions, correct preimage/signature, and evaluate any created_at<t / created_at>t clauses against the AUTH event's created_at); Step 5 check the owner is an active relay member; Step 6 grant virtual membership scoped to the agent's own pubkey, with no persistent membership record created for the agent."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md:71-115"
  - statement: "Step 1 failures (malformed event, invalid id/sig, wrong relay tag, stale created_at) MUST get an OK-false response prefixed \"invalid: <reason>\"; Steps 3-5 failures (missing/invalid credential, non-member owner) MUST get an OK-false response prefixed \"restricted: <reason>\"."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md:73"
  - statement: "kind= clauses in the NIP-OA credential are NOT evaluated at connection admission in NIP-AA — they are only a declared intent signal — but a relay MAY optionally enforce them per-event once a virtual member is admitted, in which case every EVENT from that pubkey must satisfy every kind= clause or be rejected with an OK-false \"restricted: <reason>\" response; created_at clauses are evaluated only once, at connection admission (Step 4), and are not re-evaluated per event."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md:117-127"
  - statement: "NIP-AA depends on NIP-OA (Owner Attestation, which defines the auth tag's format, signing preimage and conditions grammar), NIP-43 (Relay Access Metadata and Requests, which defines relay membership) and NIP-42 (Authentication of Clients to Relays, whose kind:22242 AUTH event is the credential-presentation vehicle); NIP-AA itself adds no new event kinds and does not itself define the auth tag format."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md:7-9"
      - "docs/nips/NIP-AA.md:239-247"
  - statement: "buzz-relay's handle_auth (the NIP-42 AUTH message handler) extracts a NIP-OA `auth` tag from the signed AUTH event via extract_auth_tag_json before crypto verification consumes the event, returning None when zero or more than one `auth` tag is present -- matching NIP-AA Step 3's exactly-one-tag rule."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:1-10"
      - "crates/buzz-relay/src/handlers/auth.rs:26-36"
      - "crates/buzz-relay/src/handlers/auth.rs:78"
  - statement: "After base NIP-42 crypto verification succeeds and the community-ban and pubkey-allowlist gates pass, handle_auth calls crate::api::relay_members::enforce_relay_membership, which -- via the inner check_relay_membership -- returns MembershipDecision::Member when the caller's own pubkey is a direct relay member (NIP-AA Step 2), and otherwise, only when the deployment's allow_nip_oa_auth flag is enabled, extracts the auth tag, verifies it with buzz_sdk::nip_oa::verify_auth_tag, and returns MembershipDecision::ViaOwner(owner_pubkey) when that owner is itself an active relay member (NIP-AA Steps 3-5); any other outcome is MembershipDecision::Denied."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:39-48"
      - "crates/buzz-relay/src/api/mod.rs:63-112"
      - "crates/buzz-relay/src/api/mod.rs:126-145"
  - statement: "On a MembershipDecision::ViaOwner outcome, enforce_relay_membership returns Ok(Some(owner_pubkey)) rather than inserting any row into the relay_members table -- the agent's access is derived at authentication time on every connection and no persistent relay-membership record is created for it, matching NIP-AA Step 6's 'MUST NOT create a persistent membership record for the agent.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:126-145"
  - statement: "Separately from relay-membership admission, handle_auth calls crate::api::relay_members::materialize_nip_oa_owner to persist a first-write-wins agent-to-owner pubkey mapping (ensuring both principals exist as users, then calling state.db.set_agent_owner) used for observer-frame auth and ban cascades -- this is a distinct, lower-level agent/owner identity mapping, not a relay-membership record, and runs even on open relays where no membership check occurs at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:240-275"
      - "crates/buzz-relay/src/api/mod.rs:156-174"
      - "crates/buzz-relay/src/api/mod.rs:176-215"
  - statement: "buzz_sdk::nip_oa::verify_auth_tag implements NIP-AA/NIP-OA's tag-verification structure: it requires exactly 4 JSON array elements with the first equal to \"auth\", parses the owner pubkey and signature hex, calls validate_conditions on the conditions string, rejects self-attestation (owner_pubkey == agent_pubkey), reconstructs the preimage as \"nostr:agent-auth:<agent_pubkey_hex>:<conditions>\", hashes it with SHA-256, and verifies it as a BIP-340 Schnorr signature against the owner pubkey -- returning the owner PublicKey on success."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:109-111"
      - "crates/buzz-sdk/src/nip_oa.rs:179-236"
  - statement: "validate_conditions (called from both compute_auth_tag and verify_auth_tag) only checks the conditions string's *syntax* -- that it is empty, or '&'-joined clauses each matching kind=<0-65535>, created_at<<0-4294967295> or created_at><0-4294967295> with canonical (no-leading-zero) decimals -- it never compares a created_at< or created_at> bound against any event's actual created_at timestamp; no other function in buzz-sdk, buzz-relay's auth.rs, or buzz-relay's relay_members module performs that comparison either, so NIP-AA Step 4's ninth check ('Evaluate any created_at<t and created_at>t clauses against the AUTH event's created_at field... If the AUTH event does not satisfy a timestamp clause, reject') is not enforced anywhere in the connection-admission path as implemented today."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:36-59"
      - "crates/buzz-sdk/src/nip_oa.rs:61-73"
      - "crates/buzz-sdk/src/nip_oa.rs:179-236"
  - statement: "buzz-auth's verify_nip42_event (the base NIP-42 crypto/challenge/relay-URL check invoked before any NIP-OA/NIP-AA logic runs) enforces a fixed ±60-second timestamp tolerance (TIMESTAMP_TOLERANCE_SECS = 60) between the AUTH event's created_at and the relay's clock, tighter than NIP-AA's own RECOMMENDED ±120-second freshness window."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:35"
      - "crates/buzz-auth/src/nip42.rs:47-86"
  - statement: "When base NIP-42 verification fails (auth_svc.verify_auth_event returns Err), handle_auth sends an OK-false response with reason \"auth-required: verification failed\" -- the same generic prefix used for the already-authenticated and already-failed short-circuits and for a pubkey-allowlist denial -- not the \"invalid: <reason>\" prefix NIP-AA Step 1 specifies; only the relay-membership-gate failure path (owner not found or not an active member, i.e. the NIP-AA Steps 3-5 outcome) actually sends the spec's \"restricted: <reason>\" prefix, as \"restricted: not a relay member\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:54"
      - "crates/buzz-relay/src/handlers/auth.rs:63"
      - "crates/buzz-relay/src/handlers/auth.rs:210"
      - "crates/buzz-relay/src/handlers/auth.rs:234"
      - "crates/buzz-relay/src/handlers/auth.rs:291"
  - statement: "A successful AUTH -- whether by direct membership or NIP-OA owner delegation -- always produces the same OK-true response with an empty message (conn.send(RelayMessage::ok(&event_id_hex, true, \"\"))), matching NIP-AA's protocol-flow example [\"OK\", \"<event-id>\", true, \"\"]."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:282"
      - "docs/nips/NIP-AA.md:59"
  - statement: "Two deployment config flags gate this behavior: require_relay_membership (env BUZZ_REQUIRE_RELAY_MEMBERSHIP, default false) turns the entire relay-membership check into a no-op when false, and allow_nip_oa_auth (env BUZZ_ALLOW_NIP_OA_AUTH, default false) specifically controls whether a valid NIP-OA auth tag can grant membership access at all when require_relay_membership is true; on an open relay (require_relay_membership=false), the NIP-OA owner is still opportunistically extracted (via extract_nip_oa_owner, unconditionally, since the signature is self-proving) for agent-to-owner backfill, but no membership decision is made at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:206-210"
      - "crates/buzz-relay/src/config.rs:275-287"
      - "crates/buzz-relay/src/handlers/auth.rs:240-253"
  - statement: "This repository's relay-side implementation (handle_auth plus the relay_members module and buzz_sdk::nip_oa) is a faithful, if partial, realization of NIP-AA's connection-admission algorithm and error-prefix convention, even though no source file or doc comment in this repository names the code \"NIP-AA\" anywhere; the correspondence was established by comparing the spec's six-step algorithm and error-prefix rule directly against the cited code, not by finding an explicit label."
    entry_class: INFERENCE
    evidence:
      - "docs/nips/NIP-AA.md:71-115"
      - "crates/buzz-relay/src/handlers/auth.rs:216-253"
      - "crates/buzz-relay/src/api/mod.rs:39-215"
    confidence: 0.85
  - statement: "No source file under crates/ or docs/ (other than docs/nips/NIP-AA.md itself, docs/remote-agents.md:53 and launchpad/docs/corpus/templates/specification.md's own evidence ledger) contains the literal string \"NIP-AA\"; the implementing symbols above were located by tracing NIP-AA's dependencies (NIP-OA auth tag, NIP-43 relay membership, NIP-42 AUTH) into this repository's code, not by a direct name match."
    entry_class: FACT
    evidence:
      - "grep_repo('NIP-AA', types='rs,md') -> docs/nips/NIP-AA.md, docs/remote-agents.md:53, launchpad/docs/corpus/templates/specification.md:64,67 (repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052)"
  - statement: "No per-event kind= enforcement (the optional mechanism NIP-AA describes for restricting a virtual member's publishable event kinds after connection admission) was found anywhere in buzz-relay's ingest/event-handling code; the auth tag's conditions are consulted only at connection-admission time (inside verify_auth_tag, for structural/self-attestation checks) and are not retained or re-checked against event.kind for subsequent EVENT submissions on the connection."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:39-215"
      - "crates/buzz-relay/src/handlers/auth.rs:1-350"
    confidence: 0.7
  - statement: "A sibling corpus node, architecture-flows-websocket-authentication, already documents the same handle_auth code path end-to-end (challenge/response mechanics, connection state machine, ban/allowlist/membership gate ordering, NIP-OA agent-to-owner delegation as it appears in that flow) and explicitly names \"NIP-OA's full owner-delegation and attestation format\" as a gap not yet covered in the corpus."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "Per templates/interface.md's own 'A note on type' section, node.schema.json's type enum encodes interface-shaped and event-kind-shaped corpus subject matter as the single combined value interfaces-events, not two separate enum values, so this node -- despite documenting a protocol extension rather than a CLI/HTTP surface -- carries type: interfaces-events rather than any other enum member."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md:216-228"
  - statement: "Issue #990's Definition of Done requires this node to cite the authoritative machine/spec representation and to include at least one valid example and one failure example; NIP-AA's own 'Verification Examples' section provides an Accept case (owner is an active member, AUTH created_at within the freshness window, all Step 4 checks pass) and a Reject-cases table (nine distinct failing scenarios each mapped to the step that rejects them)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#990 definition of done"
---

# Buzz NIP-AA: Agent Authentication (relay virtual membership)

NIP-AA is a Nostr protocol extension that lets an AI agent obtain relay
access it was never explicitly enrolled for, by proving during NIP-42
authentication that its owner already holds that access. The boundary
documented here is the **relay's NIP-42 AUTH message handling**, extended by
NIP-OA credential verification and a NIP-43 relay-membership lookup: one side
is a Nostr client (human or agent) opening a WebSocket connection; the other
is `buzz-relay`. The technology is WebSocket + a signed `kind:22242` Nostr
event carrying an optional NIP-OA `auth` tag. No new event kind is
introduced; NIP-AA reuses NIP-42's existing AUTH event and NIP-43's existing
relay-membership concept, adding a decision rule for what happens when the
authenticating pubkey is not itself a member but presents a valid
owner-attestation.

## Operations

This interface exposes exactly one operation: presenting a NIP-42 AUTH event
that may carry a NIP-OA `auth` tag.

| Operation | Defined in | Summary |
|---|---|---|
| `["AUTH", <kind:22242 event>]` (NIP-42 AUTH, optionally NIP-AA-extended) | NIP-42 (event format); `docs/nips/NIP-AA.md` (the extension rule); `crates/buzz-relay/src/handlers/auth.rs::handle_auth` (relay handler) | Client responds to the relay's AUTH challenge; the relay verifies the event, then decides connection access via direct membership, NIP-OA owner delegation, or denial. |
| NIP-OA `auth`-tag verification (subroutine of the above) | `crates/buzz-sdk/src/nip_oa.rs::verify_auth_tag` | Structural + cryptographic verification of the `auth` tag: 4-element array, non-self-attesting owner pubkey, syntactically valid `conditions`, correct BIP-340 Schnorr signature over `SHA256("nostr:agent-auth:<agent_pubkey>:<conditions>")`. |
| Relay-membership admission decision (subroutine) | `crates/buzz-relay/src/api/mod.rs::relay_members::{check_relay_membership, enforce_relay_membership}` | Direct-member fast path (Step 2), else NIP-OA-owner fallback (Steps 3-5), else denial. Feature-gated by `require_relay_membership` and `allow_nip_oa_auth` (`crates/buzz-relay/src/config.rs`). |

## Contract and stability

**Authentication/authorization.** Access is per-pubkey, not per-connection:
a virtual member's grant applies only to the specific `event.pubkey` that
completed this AUTH round trip, matching NIP-AA's "not to the WebSocket
connection as a whole" scoping. Two independent config flags control whether
this path can activate at all: `require_relay_membership` (default `false`)
must be `true` for any membership check to run, and `allow_nip_oa_auth`
(default `false`) must also be `true` for a NIP-OA `auth` tag to be able to
grant access on a closed relay. With either flag off, no agent gains access
through this mechanism; it falls through to ordinary NIP-42 (direct
membership only, or, on an open relay, unconditional access, with NIP-OA
owner-extraction still running opportunistically for backfill purposes only).

**Ordering/idempotency.** The relay-membership decision is evaluated fresh
on every new connection's AUTH event; it is never cached across reconnects.
If the same agent pubkey re-authenticates on the same connection with a
different `auth` credential, `enforce_relay_membership`/`check_relay_membership`
simply re-run the same decision — this repository's code does not implement
NIP-AA's stated requirement to explicitly replace a stored prior credential,
because no credential is stored server-side across the admission decision at
all; each AUTH event is verified independently.

**Error/rejection behavior.** A successful AUTH — whether via direct
membership or NIP-OA delegation — always produces
`["OK", "<event-id>", true, ""]`. On failure, this implementation's error
prefixes only partially match NIP-AA's own convention:

| Failure | NIP-AA's specified prefix | This implementation's actual response |
|---|---|---|
| Base NIP-42 crypto/challenge/relay-URL/freshness failure (spec Step 1) | `"invalid: <reason>"` | `"auth-required: verification failed"` |
| Already authenticated / already failed on this connection (not NIP-AA-specific) | n/a | `"auth-required: already authenticated"` / `"auth-required: authentication already failed"` |
| Pubkey-allowlist denial (not NIP-AA-specific) | n/a | `"auth-required: verification failed"` |
| No active membership, and no valid/owner-eligible NIP-OA delegation (spec Steps 3-5) | `"restricted: <reason>"` | `"restricted: not a relay member"` |
| Community ban on the pubkey or its NIP-OA-proven owner (not part of NIP-AA) | n/a | `"blocked: you are banned from this community"` |

Only the membership-gate failure actually uses the spec's `"restricted:"`
prefix; the base-verification failure path uses this repository's own
generic NIP-42 `"auth-required:"` convention rather than NIP-AA's
`"invalid:"` prefix. This is a real divergence between the spec text and the
shipped behavior, not a documentation gap — see *Boundary* below for why it
is recorded rather than corrected here.

**Versioning/compatibility.** NIP-AA is `draft` and `optional`; nothing in
this repository advertises NIP-AA support via NIP-11 or any other
capability-negotiation surface (not verified beyond a targeted search — see
*Scope and omissions*). A relay operator can withdraw the behavior entirely
by leaving `allow_nip_oa_auth` at its default `false`.

## Boundary

This node does not describe:

- **NIP-OA's own credential format, signing preimage, or minting
  procedure** — `buzz_sdk::nip_oa::compute_auth_tag`/`verify_auth_tag` are
  cited here only insofar as NIP-AA's connection-admission algorithm calls
  them; the attestation's own design (why it takes this shape, how an owner
  is expected to mint and rotate it) belongs to a future NIP-OA corpus node,
  which does not exist yet on `origin/launchpad`.
- **NIP-42's own generic challenge/response mechanics or the full
  connection-state machine** (ban gate, pubkey allowlist, per-message-type
  auth enforcement for `EVENT`/`REQ`/`COUNT`) — `architecture-flows-websocket-authentication`
  already documents that flow end-to-end; this node references it rather
  than restating it.
- **NIP-43's own relay-membership metadata format** (`kind:13534` and the
  `relay_members` table's own shape) — this node only describes how NIP-AA
  consumes a membership lookup, not how membership itself is modeled or
  advertised.
- **Whether to fix the two spec/code divergences named above** (missing
  `created_at` clause evaluation; the `"invalid:"` vs. `"auth-required:"`
  prefix mismatch). Issue #990 explicitly excludes "changing runtime product
  behavior unless a separately linked implementation issue owns that
  change" — this node's job is to state what the code does today
  accurately, not to correct it.

## Relationships

- references: architecture-flows-websocket-authentication

No `implements`/`depends-on`/`part-of`/`supersedes` edges are declared. A
`references` edge toward a NIP-OA corpus node, or toward a NIP-43/relay-membership
node, would be appropriate once either exists — neither is present in
`origin/launchpad`'s corpus tree at the recorded revision, and per
`AGENTS.md`'s own rule a relationship target must already resolve there, not
merely in this worktree.

## Verification examples

**Valid (Accept).** Per `docs/nips/NIP-AA.md`'s own Verification Examples
section: the owner pubkey is an active relay member; the AUTH event's
`created_at` is `1713956400`, within the relay's freshness window; the
credential's conditions are `kind=1&created_at<1713957000`. Steps 1-2 run as
ordinary NIP-42 (agent pubkey not a direct member, so continue); Step 3
finds exactly one `auth` tag; Step 4's structural/signature checks all pass
in `verify_auth_tag`; Step 5's owner-membership lookup succeeds. The relay's
code path is: `handle_auth` → `enforce_relay_membership` →
`check_relay_membership` returns `MembershipDecision::ViaOwner(owner_pubkey)`
→ `enforce_relay_membership` returns `Ok(Some(owner_pubkey))` → the
connection is marked `Authenticated` and the relay sends
`["OK", "<event-id>", true, ""]`. Note that the *syntactic* validity of
`created_at<1713957000` is checked by `validate_conditions`, but — per the
evidence entry above — its value is never compared against the AUTH event's
actual `created_at` anywhere in this code path, so this example's outcome
would be identical even if that clause's numeric bound were already expired.

**Failure (Reject).** Per the same section's Reject-cases table: an `auth`
tag whose `<owner-pubkey-hex>` equals `event.pubkey` (self-attestation) MUST
be rejected at Step 4. In this repository, `verify_auth_tag` implements
exactly this check (`if owner_pubkey == *agent_pubkey { return
Err(SdkError::InvalidInput(...)) }`), so `check_relay_membership`'s
`match buzz_sdk::nip_oa::verify_auth_tag(...) { Err(e) => ... }` branch logs
the invalid tag and falls through to `MembershipDecision::Denied` (no other
`auth` tag or direct membership exists in this scenario) →
`enforce_relay_membership` returns the `FORBIDDEN`/`relay_membership_required`
error shape at the HTTP call sites, or, on the WebSocket AUTH path, `handle_auth`
sends `["OK", "<event-id>", false, "restricted: not a relay member"]` and
marks the connection `Failed`.

## Scope and omissions

**This node covers** the relay-side connection-admission algorithm NIP-AA
defines — extracting a NIP-OA `auth` tag from a NIP-42 AUTH event,
verifying it, checking the named owner's relay membership, and granting
scoped, non-persistent virtual membership — as actually implemented in
`buzz-relay`/`buzz-sdk`/`buzz-auth`, cross-checked line-by-line against the
spec text at `docs/nips/NIP-AA.md`, including two places where the shipped
behavior diverges from the spec's stated requirements.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-OA's own attestation format, signing procedure and design rationale | A future dedicated NIP-OA corpus node (not yet created) |
| NIP-42's full connection-state machine, ban/allowlist gates, per-message auth enforcement | `architecture-flows-websocket-authentication` |
| NIP-43's relay-membership metadata format and `relay_members` table shape | Not yet in this corpus |
| Whether/how to fix the two named spec/code divergences | A separately filed implementation issue, per #990's own "Out of scope" |
| Client-side (`buzz-ws-client`) construction of the AUTH event and its own `auth` tag | Not independently verified for this node — see below |

**Expected but not verified when this node was written:**

- **Whether any deployment actually advertises or enables NIP-AA today**
  (i.e. whether `allow_nip_oa_auth=true` is set anywhere outside tests) was
  not checked — this node describes the code path that exists, not whether
  it is switched on in any running environment.
- **Client-side construction of the `auth` tag and the AUTH event** (in
  `buzz-ws-client`) was not independently re-verified for this node; the
  sibling `architecture-flows-websocket-authentication` node already covers
  it and is cited rather than duplicated, but this node's own evidence
  ledger does not include a `FACT` about client behavior.
- **Whether any relay deployment implements the optional per-event `kind=`
  enforcement** NIP-AA describes is recorded above as an `INFERENCE`
  (confidence 0.7), not a `FACT` — the search for it was a repository-wide
  read of the auth/membership modules, not an exhaustive trace of every
  event-ingestion code path.
- **NIP-11 capability advertisement for NIP-AA** was not checked against
  `crates/buzz-relay/src/nip11.rs` in this pass; absence of NIP-AA from any
  advertised NIP list is plausible but unverified.
