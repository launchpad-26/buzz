---
id: capabilities-invites-invite-token
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "A v1 invite code is a compact, URL-safe, HMAC-SHA256-signed blob: base64url(payload_json) + \".\" + base64url(hmac_sha256(key, payload_json)), where payload_json is a JSON object with fields c (community UUID), r (role, only \"member\" valid), e (expiry, unix seconds) and n (random nonce), and the relay verifies the signature and expiry rather than storing the code server-side."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:1-75"
  - statement: "The v1 HMAC key is derived as sha256(relay_secret_key_bytes || \"buzz-invite-v1\") by derive_invite_key, so rotating the relay keypair invalidates every outstanding v1 code -- the token's only coarse-grained revocation mechanism."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:107-116"
  - statement: "verify_invite checks the HMAC signature before trusting any claim inside the decoded payload, then checks expiry, then community match, then that the role equals \"member\" exactly -- a correctly signed payload carrying an elevated role is still rejected as InvalidRole, defending against a hypothetical future minting bug rather than only against forgery."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:156-191"
  - statement: "v1 code minting (mint_invite) is gated #[cfg(test)] and its doc comment states \"Production minting uses database-backed v2 codes. Remove this helper with v1 claim verification after the compatibility drain window\" -- v1 is a live verification path with no live minting path, kept only so previously issued v1 codes keep working during a drain window."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:124-149"
  - statement: "A v2 invite code is opaque, not self-describing: encode_v2_code formats \"v2.\" plus the unpadded base64url encoding of a 32-byte random secret (V2_SECRET_LEN), validate_v2_code checks that shape (including rejecting non-canonical base64 encodings of an otherwise-valid secret), and hash_v2_code is SHA-256 over the complete code string including the \"v2.\" prefix -- the digest persisted by the database, never the bearer secret itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/invite.rs:23-57"
  - statement: "relay_invites (introduced by migration 0025) stores, per row: community_id, a server-generated id, token_hash (BYTEA, exactly 32 bytes, the v2 code's SHA-256 digest), role (TEXT, CHECKed to equal 'member'), max_uses (nullable INTEGER, NULL meaning unlimited), use_count (INTEGER, defaulting 0), expires_at (TIMESTAMPTZ), created_by and created_at; its primary key is (community_id, id) and it carries a UNIQUE(community_id, token_hash) constraint plus CHECK(max_uses IS NULL OR use_count <= max_uses)."
    entry_class: FACT
    evidence:
      - "migrations/0025_relay_invites.sql"
  - statement: "The relay_invites migration's own header comment states the reason a durable row exists at all: \"Stateless HMAC bearer tokens (v1) cannot enforce use limits: their signed payload is immutable and no invite row exists to record consumption,\" and that every lookup binds both (community_id, token_hash) so \"a code presented on the wrong tenant host returns Invalid -- there is no cross-tenant lookup by hash alone.\""
    entry_class: FACT
    evidence:
      - "migrations/0025_relay_invites.sql:1-13"
  - statement: "The role a token can grant is pinned to \"member\" in both formats through a different mechanism each: v1's verify_invite rejects any payload.r other than the literal string \"member\" (even one carrying a valid signature); v2's relay_invites.role column carries a SQL CHECK (role = 'member') so no other value can ever be persisted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:187-189"
      - "migrations/0025_relay_invites.sql:22"
  - statement: "POST /api/invites (mint_invite) mints only a v2 code -- its own inline comment reads \"Mint a v2 opaque, database-backed invite\" -- and POST /api/invites/claim (claim_invite) routes by exact string prefix: a code starting with \"v2.\" is validated with validate_v2_code and looked up by hash_v2_code against relay_invites, with no fallback to v1 verification for malformed v2 input; every other code is handed to the v1 HMAC verifier instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:315-320"
      - "crates/buzz-relay/src/api/invites.rs:351-396"
  - statement: "buzz-core/src/invite.rs also defines the token's time and use-count bounds as shared constants (MIN_INVITE_TTL_SECS, DEFAULT_INVITE_TTL_SECS, MAX_INVITE_TTL_SECS, MAX_INVITE_USES) consumed by both the mint-request validator and the database layer, so the token format module is also where those bound values are declared, even though their policy rationale is out of this node's scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/invite.rs:11-21"
  - statement: "invite_token.rs separately defines PolicyAcceptancePayload, a short-lived HMAC-signed receipt (fields c: sha256 of the bound invite code, v: policy version, e: expiry) minted by mint_policy_acceptance and checked by verify_policy_acceptance -- a distinct signed credential proving a browser accepted a configured join policy, not a token that itself admits a member."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:332-389"
  - statement: "The v1 stateless invite-link format (mint + claim + landing page + deep link) shipped in commit 2e529aab759a18c1bb81e447f3696fe99db53a27; join-policy acceptance binding was layered on in commit 6c2d667575cbc372ba42d26134448660fb1d2ee9; the v2 opaque, database-backed, use-limited token format shipped in commit d500c2d5cf5d9aabe0ca4ebebfcafdbe5f5b7fd3, which also added the relay_invites table this node cites."
    entry_class: FACT
    evidence:
      - "commit 2e529aab759a18c1bb81e447f3696fe99db53a27"
      - "commit 6c2d667575cbc372ba42d26134448660fb1d2ee9"
      - "commit d500c2d5cf5d9aabe0ca4ebebfcafdbe5f5b7fd3"
  - statement: "Issue #761's own Definition of Done uses the capability-shaped checklist text -- \"States the capability and primary actors/outcomes,\" \"Defines behavioral rules, constraints and relevant variants,\" \"Links major flows, interfaces, data and platform implementation,\" \"Links verification demonstrating the capability\" -- matching corpus-template-capability's required-sections shape rather than corpus-template-data-entity's identity/attributes/invariants/relationships/provenance/storage shape, which is the basis for choosing type: capabilities over the data-entity-instance type (implementation) that corpus-template-data-entity's own evidence ledger reasons toward for a domain-entity subject."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/capability.md"
      - "launchpad/docs/corpus/templates/data-entity.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
  - statement: "Issue #761 (child of Feature #613) scopes this document to launchpad/docs/corpus/capabilities/invites/invite-token.md, distinct from sibling tasks #759 (invite-expiry), #760 (invite-redemption) and #762 (invite, the overall capability), and its Definition of Done requires exactly one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links instead of duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#761 definition of done, read directly via gh issue view"
relationships:
  - type: part-of
    target: capabilities-invites-invite
  - type: implements
    target: corpus-template-capability
---

# Invite token: capability

The relay can mint and verify **invite tokens** -- compact, bearer-style
credentials that a relay owner or admin issues out-of-band (a link, a code)
and that a joining pubkey later presents to be admitted into one Nostr
community at the fixed `member` role. Two token formats coexist today: a
legacy **v1** stateless, HMAC-signed bearer code whose entire state lives
inside the code itself, and the current **v2** opaque, database-backed code
whose only externally visible content is 32 random bytes, with all state
(use count, expiry, role) held server-side in a `relay_invites` row keyed by
the code's SHA-256 hash. Either format, once verified, proves the same thing:
that an admin authorized this specific pubkey (or any pubkey, for a
multi-use code) to join this specific community as `member` -- nothing more,
and never a higher role.

## Maturity

**Shipped**, in two generations. The v1 format (mint, claim, landing page,
deep link) shipped in commit `2e529aab759a18c1bb81e447f3696fe99db53a27`; join-policy
acceptance binding was layered onto the claim flow in commit
`6c2d667575cbc372ba42d26134448660fb1d2ee9`. The v2 opaque, database-backed,
use-limited format shipped in commit `d500c2d5cf5d9aabe0ca4ebebfcafdbe5f5b7fd3`,
which introduced the `relay_invites` table this node cites and which changed
production minting to issue v2 codes exclusively. v1 is not dead: `claim_invite`
still verifies any non-`v2.`-prefixed code against the v1 HMAC path, but v1
minting is compiled out of the production binary (`#[cfg(test)]` only) --
the code comment on that test helper names this a "compatibility drain
window," a live verification surface with no corresponding live minting
surface.

## Boundary

This node describes the token's own structure, formats and role pinning. It
does not describe:

- **Expiry policy** -- the TTL bounds (`MIN_INVITE_TTL_SECS`,
  `DEFAULT_INVITE_TTL_SECS`, `MAX_INVITE_TTL_SECS`) are declared in the same
  module this node cites for the token's other constants, but their chosen
  values, defaults and rationale are `#759`'s (invite-expiry) territory, not
  restated here beyond naming that they exist.
- **The redemption/claim transaction** -- per-pubkey rate limiting, the
  atomic use-count increment and membership insertion, and the NIP-43 side
  effects `claim_invite` publishes on success are `#760`'s (invite-redemption)
  territory. This node states only how a claim *routes* by code prefix, not
  how the database layer serializes concurrent claims.
- **The invite capability as a whole** -- mint, claim, and join-policy
  acceptance considered together as one end-to-end user-facing capability is
  `#762`'s (invite) territory. This node is one constituent piece of it.
- **The join-policy acceptance receipt** (`PolicyAcceptancePayload`) -- a
  separate, similarly HMAC-signed short-lived credential that proves a
  browser accepted a configured join policy. It is bound to an invite code by
  hashing that code into its own payload, but it is not itself a token that
  admits a member, and is out of scope here.
- **How the running system is operated** -- deployment, monitoring or
  incident response for the invite subsystem is not this node's subject.

## Relationships

- implements: `corpus-template-capability` -- this node is a `capabilities`-
  typed instance of that template.

No `references` edges are declared. No architecture, interface or other
invite-family capability node exists yet in the `launchpad/docs/corpus` tree
on `origin/launchpad` at the recorded revision (checked directly via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), so
there is nothing yet to point at for how the token is built, what interface
exposes it, or the sibling capability/expiry/redemption nodes it is scoped
against above. The first of those siblings to merge is the moment to add the
corresponding edge back.

## Scope and omissions

**This node covers** the two invite token formats Buzz's relay currently
supports (v1 stateless HMAC bearer, v2 opaque database-backed), the fields
and encoding each carries, how each is verified or looked up, how the role a
token can grant is pinned to `member` in each format's own mechanism, how
`claim_invite` routes between the two formats, and the shipped-vs-draining
maturity of each generation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Expiry TTL bounds, defaults and policy rationale | `#759` (invite-expiry) |
| The redemption/claim transaction, rate limiting, atomic use-count accounting, membership side effects | `#760` (invite-redemption) |
| The invite capability end-to-end (mint + claim + join-policy) | `#762` (invite) |
| The join-policy acceptance receipt as its own credential | Not yet scheduled as a corpus task at the time this node was written |
| How a capability is built (containers, components) | No architecture node yet exists for this subject |
| The HTTP interface surface (`POST /api/invites`, `POST /api/invites/claim`) as its own boundary contract | No interface node yet exists for this subject |

**Expected but not verified when this node was written:**

- **`buzz-db`'s `mint_relay_invite` and `claim_relay_invite` implementations
  were not read in full.** This node relies on the migration's schema and the
  relay-layer call sites for what a token's persisted row contains and how it
  is looked up, not on the store layer's own transaction logic, which is
  `#760`'s subject.
- **Whether the v1 "compatibility drain window" the `mint_invite` doc comment
  names has an end date, a tracking issue, or a removal plan was not
  checked.** The comment states intent to remove the helper "after" the
  window, without naming when that is.
- **Whether `type: capabilities` is the best available fit, versus
  `type: implementation` (the fit `corpus-template-data-entity`'s own
  evidence ledger reasons toward for a domain-entity subject), is not fully
  settled.** `corpus-standard-taxonomy.md` states that when more than one
  value plausibly fits, an author should follow how the corpus has already
  used the enum and disclose an imperfect fit rather than silently pick; at
  the time this node was written, no other invite-family node had merged to
  establish that precedent, so this choice rests on the issue's own DoD
  wording rather than corpus precedent.
