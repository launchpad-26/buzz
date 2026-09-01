---
id: capabilities-media-attachment-authorization
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
  - statement: "Root VISION_PROJECTS.md's Status table lists 'Blossom media storage (SHA-256, S3)' as its own capability row, marked Ships today."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247"
      - "VISION_PROJECTS.md:252"
  - statement: "verify_blossom_auth_event_for_verb requires a Schnorr-valid signature, kind exactly 24242, a non-empty content string, a `t` tag matching the requested verb ('upload' or 'get'), an `expiration` tag still in the future, a `created_at` no more than 5 seconds in the future and no older than the caller-supplied `max_age_secs`, and -- if any `server` tags are present -- at least one matching the request's bound tenant host under `normalize_server_host`, failing closed (ServerMismatch) when the bound host is unknown; every one of these is a documented precondition of authorizing either read or write access to an attachment, not merely of authenticating the signer."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "verify_blossom_get_auth (called from the read path) additionally requires the event to carry either an `x` tag equal to the requested blob's sha256 (authorization scoped to one attachment) or a `server` tag matching the bound tenant host (authorization scoped to every attachment on that host until expiration); an event with neither is rejected as MediaError::InsufficientScope, and its own unit tests (test_verify_get_accepts_matching_x_without_server_tag, test_verify_get_accepts_matching_server_without_x_tag, test_verify_get_requires_x_or_server_scope, test_verify_get_rejects_wrong_server_scope) exercise exactly these branches."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "verify_blossom_upload_auth (called from the write path) requires at least one `x` tag on the auth event to equal the uploaded content's own sha256, so upload authorization is scoped to the exact bytes being written and can never authorize substituting different content under the same signed grant."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "In the read path, authenticate_media_read (crates/buzz-relay/src/api/media.rs) runs three checks in this fixed order before any blob is served: bind_media_read_tenant resolves the request Host header to a TenantContext (or MediaError::NotFound on an unmapped host); verify_blossom_get_auth validates the Blossom event's signature, verb, freshness, and hash-or-server scope against that bound host; and enforce_relay_membership checks the authenticated pubkey against the resolved community's own membership, mapping a failed check to MediaError::RelayMembershipRequired."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "In the write path, AuthenticatedUpload's FromRequestParts impl runs the same shape of gate before the handler body executes: it binds the community from the request Host header first (fail-closed to a generic 404 on an unmapped host, never a default tenant), then validates the Blossom upload auth event against that bound host, then requires an X-SHA-256 header matching an `x` tag on the event, then calls enforce_relay_membership for the signer's pubkey against the bound community -- explicitly documented in the code as 'the only upload authority: independent of bearer-token / api_tokens storage and of require_auth_token (which governs the REST API, not media)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "enforce_relay_membership (crates/buzz-relay/src/api/mod.rs) delegates to check_relay_membership, which returns MembershipDecision::OpenRelay unconditionally when the deployment's require_relay_membership config is false, returns MembershipDecision::Member when the caller's pubkey is a direct relay member, and otherwise -- only when allow_nip_oa_auth is enabled and an x-auth-tag header is present -- verifies a NIP-OA delegation tag and, if the tag's owner pubkey is itself a member, returns MembershipDecision::ViaOwner(owner); every other case returns MembershipDecision::Denied, which enforce_relay_membership turns into a 403 relay_membership_required rejection before any blob I/O runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "MediaError::into_response collapses every distinct Blossom-authentication failure (missing/malformed header, bad base64, invalid event, bad signature, wrong kind, wrong verb, expired token, out-of-window timestamp, hash mismatch, server-tag mismatch, missing tag) to the same generic 401 body, by explicit design, to prevent an attacker from using the response to learn which specific check failed; MediaError::InsufficientScope (attachment-scope failure) is instead mapped to a distinct 403, because it is only reachable once a valid signed identity is already established and so does not create the same oracle."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "crates/buzz-test-client/tests/e2e_media.rs exercises this capability end to end at the HTTP level: test_upload_no_auth_returns_401 and test_upload_missing_x_sha256_returns_401 assert the write path rejects a missing/incomplete Blossom grant, and test_unauthenticated_reads_are_rejected asserts the read path rejects a request presenting no Blossom authorization at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "The already-merged architecture-flows-media-download and architecture-flows-media-upload nodes document these same read and write HTTP flows step by step, including tenant binding, Blossom auth verification, relay membership, and failure-status mapping, at a level of implementation detail this capability node deliberately does not restate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/media-download.md"
      - "launchpad/docs/corpus/architecture/flows/media-upload.md"
  - statement: "The already-merged architecture-principles-community-is-security-boundary node documents, as its own subject, that the Host-header-derived community binding this capability's tenant step depends on is enforced fail-closed across every request surface including media upload and download, and that no client-supplied signal may override it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
  - statement: "Issue #763's own definition of done requires this capability node to state the capability and its primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#763 definition of done"
relationships:
  - type: references
    target: architecture-flows-media-download
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Attachment authorization: capability

Buzz can decide, for every read of and write to a media attachment (an image,
video, or other file stored through its Blossom-compatible media endpoint),
whether the party asking is allowed to do so -- and it makes that decision the
same way every time: a freshly signed cryptographic grant proves who is asking
and what they are asking for, and community membership proves whether that
identity may touch this community's attachments at all. There is no
configuration that serves an attachment to an unauthenticated caller, and no
path that authorizes a write without both a matching signed grant and a
matching community membership.

## Primary actors and outcomes

- **An uploading client** (a human user's desktop/mobile/CLI session, or an
  agent acting through `buzz-cli`) presents a signed grant scoped to the exact
  bytes it is writing, and — if it is a community member (directly, or as an
  agent whose declared owner is a member) — the write succeeds; otherwise it is
  rejected before any bytes reach storage.
- **A downloading client** presents a signed grant scoped either to one
  specific attachment or to the whole host, and — under the same membership
  test — either receives the bytes or is rejected before any storage read.
- **A relay operator** configures whether community membership is required at
  all (an "open" relay admits any validly-signed grant; a "closed" relay
  requires it) and whether an unregistered agent may inherit its declared
  owner's membership.

## Maturity

**Shipped.** Root `VISION_PROJECTS.md`'s own Status table lists "Blossom media
storage (SHA-256, S3)" as a capability marked "Ships today" (`VISION_PROJECTS.md:252`),
and the authorization gates described below are live code exercised by
`crates/buzz-test-client/tests/e2e_media.rs`, not a design still in progress.

## Behavioral rules, constraints, and variants

1. **Every read and every write requires a signed Blossom (kind:24242, BUD-11)
   grant.** There is no configuration flag or code path that admits an
   unauthenticated request to either operation. The grant must carry a valid
   Schnorr signature, the correct verb (`get` for reads, `upload` for writes),
   an `expiration` still in the future, and a `created_at` inside a bounded
   freshness window -- so a grant cannot be replayed indefinitely and cannot be
   pre-dated into validity.
2. **A grant's scope is checked, not just its validity.** A read grant must
   name either the exact attachment being requested (an `x` tag matching its
   sha256) or the whole host (a `server` tag matching the request's bound
   tenant host) -- a valid grant naming neither is rejected as insufficiently
   scoped. A write grant must name the exact content being uploaded (an `x` tag
   matching the uploaded bytes' own sha256), so a signed grant for one file can
   never authorize writing different bytes.
3. **A `server`-scoped grant is host-wide, not community-wide by accident.**
   Because the community itself is derived from the same request's `Host`
   header (see *Relationships*), a `server` tag matching the bound host and a
   community boundary are the same boundary in practice on a single-tenant
   deployment, and remain aligned on a multi-tenant one because the tag is
   checked against the *per-request bound host*, never a single process-global
   domain.
4. **Identity is necessary but not sufficient — membership is checked
   separately, after identity.** A signature proves *who* is asking; it does
   not by itself grant that identity permission to use this community's media
   store. That permission is a second, later check: relay membership,
   evaluated only once the signed grant has already passed.
5. **Membership has three outcomes, not two.** A community configured as
   "open" (membership not required) admits any validly-signed, correctly-scoped
   grant. A community configured as "closed" requires either that the
   requesting pubkey is itself a direct member, or — only when the operator has
   separately enabled it — that the requesting pubkey is an agent whose
   self-proving NIP-OA delegation names an owner who is a member. Every other
   case is denied.
6. **Authorization failures do not distinguish which check failed, on
   purpose.** Every failure in identity/grant verification (missing grant,
   malformed grant, bad signature, wrong verb, expired, out of the freshness
   window, wrong content, wrong host) collapses to the same generic rejection,
   so a caller cannot use the response to learn which specific precondition it
   failed. A grant that scopes to the wrong attachment is distinguished from
   this group, because by that point identity is already established and
   revealing the distinction creates no such oracle; failing membership after
   a valid, correctly-scoped grant is likewise its own distinguishable outcome.

## Boundary

This node does not describe:

- **How the capability is built.** The HTTP routing, request extractors,
  storage pipelines, and error-to-status mapping that implement authorization
  are documented step by step in `architecture-flows-media-download` (reads)
  and `architecture-flows-media-upload` (writes); this node states what the
  capability guarantees, not how the relay code achieves it.
- **The interface(s) the capability is exposed through.** No corpus interface
  node for the relay's Blossom HTTP surface exists yet at this revision; when
  one is drafted, this capability references it rather than restating its
  route/method inventory.
- **The step-by-step flow through this capability.** Covered by the two
  `architecture/flows/*` nodes above, not narrated again here.
- **How community membership itself is administered** (invites, admin
  actions that add or remove a member) — this node only documents that
  membership is *checked*, not how a pubkey comes to be a member.
- **How the running system is operated** (rate limiting, concurrency limits,
  moderation records) — those are part of the upload flow's own operational
  detail, not part of what this capability authorizes.

## Relationships

- `references`: `architecture-flows-media-download` — the read-path
  implementation this capability's read-side rules are drawn from.
- `references`: `architecture-flows-media-upload` — the write-path
  implementation this capability's write-side rules are drawn from.
- `references`: `architecture-principles-community-is-security-boundary` — the
  Host-header-derived community binding that this capability's membership
  check is scoped by; that node documents the tenant-binding invariant itself,
  which this node depends on rather than restates.

All three targets were confirmed present in `origin/launchpad`'s corpus tree
(`launchpad/docs/corpus/architecture/flows/media-download.md`,
`.../media-upload.md`, and
`launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md`)
at the recorded revision before being declared, per `AGENTS.md`'s
merge-target rule. No sibling `capabilities` node exists yet in that tree for
this node to sit `part-of` or be `superseded` by.

## Scope and omissions

**This node covers** the attachment-authorization capability at the level a
product stakeholder would recognize it: that every read and write is gated by
a signed, scoped grant plus a separate community-membership check, the three
membership outcomes, and the deliberate uniformity of authentication failure
responses versus the distinguishable authorization ones.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The HTTP routes, extractors, and storage pipeline implementing this capability | `architecture-flows-media-download`, `architecture-flows-media-upload` |
| The Host-header community-binding mechanism this capability's membership check relies on | `architecture-principles-community-is-security-boundary` |
| The boundary contract (routes/methods) this capability is exposed through | not yet drafted as a corpus node |
| How a pubkey becomes a relay member in the first place (invites, admin actions) | not yet drafted as a corpus node |
| Rate limiting, concurrency limits, and moderation-record side effects of an authorized upload | `architecture-flows-media-upload` |

**Expected but not verified when this node was written:**

- **Client-side construction of the signed grant** (desktop, mobile, CLI) was
  not inspected for this node; only the relay-side authorization contract was
  verified directly, matching the same boundary the two flow nodes above
  already state.
- **Whether every request surface that can reach a media attachment by a path
  other than the `/media`/`/upload` HTTP routes** (for example, a future
  surface) enforces the same two-stage grant-then-membership check was not
  audited; this node documents the capability as implemented on the routes
  inspected, not a guarantee that binds surfaces added later.
