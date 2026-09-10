---
id: capabilities-git-nostr-git-authentication
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "The git smart-HTTP transport module's own top-of-file comment states its authentication model in one line: 'Auth: NIP-98 on all routes (clone + push). No public repos for v1.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:8"
  - statement: "Every git HTTP request (`GET /git/{owner}/{repo}/info/refs`, `POST .../git-upload-pack`, `POST .../git-receive-pack`) is gated by the `GitAuth` axum extractor, which rejects any request missing an `Authorization: Nostr <base64>` header before the request body is read, returning 401 with a `WWW-Authenticate: Nostr` challenge header."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:72-112"
  - statement: "The base64-decoded Authorization payload is a Nostr event verified by `buzz_auth::nip98::verify_nip98_event`, which requires event kind 27235, a valid Schnorr signature via `buzz_core::verify_event`, and a `created_at` within a ±60 second window of the server's clock (`TIMESTAMP_TOLERANCE_SECS = 60`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs:32"
      - "crates/buzz-auth/src/nip98.rs:55-85"
  - statement: "Before verifying the NIP-98 event, the relay resolves the request's Host header to a server-side tenant via `crate::tenant::bind_community` and constructs the expected `u` (URL) tag from that resolved tenant host rather than from any client-supplied value or a single deployment-global `config.relay_url`, so a NIP-98 token signed for one community's host cannot authenticate a git request against a different community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:120-143"
      - "crates/buzz-relay/src/api/git/transport.rs:316-341"
  - statement: "Two in-repo unit tests directly exercise this cross-host binding: `git_nip98_rejects_token_signed_for_wrong_community_host` asserts a token signed for community A's URL fails verification against community B's expected URL, and `git_nip98_accepts_token_signed_for_matching_community_host` asserts the same token verifies and returns the correct pubkey when the expected URL matches."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:2983-3019"
  - statement: "The HTTP method carried in the NIP-98 event is intentionally not checked against the actual request method, because git's credential-helper protocol signs one token with method=GET (the initial info/refs request) and reuses it for the subsequent POST (pack data); the code's own comments call the resulting check tautological and state the real security boundary is the repo-root URL lock plus the ±60s timestamp window plus HTTPS in production."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:160-183"
  - statement: "NIP-98 event-ID replay protection is deliberately not implemented for git routes, on the stated grounds that git's credential protocol reuses one signed token across the info/refs GET and the following upload-pack/receive-pack POST within a session, and rejecting a replayed event id would break normal clone/push; the ±60s window plus URL scoping plus transport security are treated as the acceptable trade-off instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:194-199"
  - statement: "After NIP-98 verification, the relay enforces relay membership for the authenticated pubkey via `enforce_relay_membership`, which on a closed relay denies any pubkey that is neither a direct relay member nor delegated through a verified NIP-OA (agent-owner) attestation carried either in the signed event's own tags or an `x-auth-tag` header — git's credential-helper protocol cannot carry a standalone header through every leg of the flow, so agents attach the NIP-OA attestation to the signed NIP-98 event itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:204-225"
      - "crates/buzz-relay/src/api/mod.rs:115-147"
  - statement: "Every git HTTP request also re-checks moderation ban state per request via `deny_banned_git_principal`, cascading from the authenticated pubkey to its proven NIP-OA owner (a ban on the owner also blocks their agents), and fails closed with 503 if the restriction-state read itself errors, rather than treating a lookup failure as an implicit allow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:233-298"
  - statement: "Passing NIP-98 verification and the relay-membership/ban gates is not sufficient to read a repository: `authorize_git_read` (labeled SEC-005 in its own doc comment) additionally requires the caller's current active membership in the repository's bound channel, resolved by looking up the repo's live kind:30617 announcement, following its `buzz-channel` tag to a channel id, and requiring `buzz_db::Db::get_member_role` to return a role the relay recognizes; a member removed from the channel loses read access even though their NIP-98 credential still verifies, and every denial reason collapses to an identical generic 404 so channel membership cannot be probed through the git endpoints."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:445-564"
  - statement: "Push authorization is enforced by a separate mechanism layered on top of the same NIP-98 identity: a pre-receive hook installed into every bare repository posts an HMAC-signed callback (bounded to a 30-second age via `MAX_CALLBACK_AGE_SECS`) to an internal, loopback-only policy endpoint, which resolves the pusher's channel role, applies branch-protection rules parsed from the repo's kind:30617 announcement, and calls `buzz_core::git_perms::evaluate_push` to allow or deny each ref update."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs:1-54"
      - "crates/buzz-relay/src/api/git/hook.rs"
  - statement: "`crates/buzz-test-client/tests/e2e_git.rs` contains real (non-mocked) end-to-end test functions covering the full authenticated clone/push/fetch/tag roundtrip and concurrent-push behavior against a live relay, git binary, and MinIO; these are marked `#[ignore = \"requires live relay + MinIO + git\"]` rather than run in the default unit-test pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs:268-270"
      - "crates/buzz-test-client/tests/e2e_git.rs:411-413"
relationships:
  - type: part-of
    target: capabilities-git-git-hosting
---

# Nostr git authentication: capability

Buzz authenticates every git smart-HTTP request — ref advertisement, clone/fetch, and
push — using the caller's Nostr identity instead of a separate git-specific credential
system. A user or agent proves control of a Nostr keypair by signing a NIP-98 HTTP-auth
event and presenting it as the `Authorization: Nostr <base64>` header; the relay verifies
that signature, binds it to the specific community and repository the request targets,
and layers relay-membership, moderation-ban, and channel-role checks on top before any
git object is served or accepted. The net effect for a user or agent is that the same
Nostr keypair used to talk to a Buzz community over WebSocket is also the credential that
authenticates `git clone`, `git fetch`, and `git push` against that community's
repositories — no separate git password, SSH key, or platform-specific token is issued or
required.

## Maturity

**Shipped.** The transport module's own header comment states the model directly: "Auth:
NIP-98 on all routes (clone + push). No public repos for v1." (`transport.rs:8`). The
`GitAuth` extractor, the cross-host URL-binding logic, the relay-membership/ban gates, and
the channel-role read gate are all present, non-stubbed code on `origin/launchpad` today,
and are exercised both by in-repo unit tests (the cross-host accept/reject pair) and by a
real end-to-end suite (`e2e_git.rs`) that drives an actual `git` binary, a live relay, and
MinIO through authenticated clone/push/fetch/tag flows, gated behind `#[ignore]` because it
needs that live infrastructure rather than because the feature is unfinished.

## Boundary

This node does not describe:

- **How the push-side policy engine itself decides allow/deny.** Branch-protection tag
  syntax, the `MemberRole` hierarchy, and `buzz_core::git_perms::evaluate_push`'s per-ref
  decision logic are a distinct, larger subject — this node establishes only that pushes
  are additionally gated by that engine, called back into from the pre-receive hook, after
  the same NIP-98 identity has already been established. No corpus node currently owns
  that engine's own rules; see *Scope and omissions* below.
- **The credential-helper client tooling that signs NIP-98 events on the git client side**
  (`git-credential-nostr`) — that is `#744`'s subject, a distinct capability node.
- **Git hosting as a whole** — repository creation from kind:30617 announcements, storage,
  and the broader product capability — that is `#745`'s subject; this node covers only the
  authentication/authorization gates a request must pass, not how a repository is created
  or stored.
- **Commit and tag signing** (signing git objects themselves with a Nostr key via
  `git-sign-nostr`) — that is `#747`'s subject and is orthogonal: it concerns the integrity
  of the objects being pushed, not the identity of the pusher.
- **The smart-HTTP transport mechanics** — subprocess shelling, quarantine object
  directories, pkt-line encoding, and the fast-path ref-advertisement optimization — that
  is `#753`'s subject; this node cites `transport.rs` only for the authentication code it
  contains, not the transport protocol itself.
- **How the running system is operated** (deployment, monitoring, incident response) — not
  this capability's subject.

## Relationships

- references: architecture-flows-git-push
- references: architecture-principles-signed-events

## Scope and omissions

**This node covers** the authentication and identity-adjacent authorization gates every
git smart-HTTP request passes through: NIP-98 signature and timestamp verification, the
repo-root URL binding that prevents a token signed for one community authenticating
against another, the deliberate non-checks (HTTP method, event-id replay) and the stated
reasoning for each, relay-membership enforcement with NIP-OA agent-delegation fallback,
per-request moderation-ban cascading, and the channel-role gate that additionally governs
reads. It also states, at a boundary level only, that push carries a further
authorization step (the pre-receive hook calling back into a branch-protection policy
engine) without describing that engine's own rules.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Branch-protection rules and the push-policy decision engine (`git_perms::evaluate_push`) | no corpus node yet — a gap this node surfaces rather than fills |
| Client-side credential-helper signing tooling | `#744` (credential-helper) |
| Git hosting as a product capability (repo creation, storage, lifecycle) | `#745` (git-hosting) |
| Commit/tag signing with a Nostr key | `#747` (git-signing) |
| Smart-HTTP transport mechanics (subprocess shelling, pkt-lines, quarantine) | `#753` (smart-http) |
| The step-by-step push flow this authentication gates | `architecture-flows-git-push` |
| How a signed Nostr event's signature is itself verified | `architecture-principles-signed-events` |

**Expected but not verified when this node was written:**
- **The full pre-receive hook script and its HMAC secret lifecycle** (`hook.rs`'s
  `install_hook` and the `PRE_RECEIVE_HOOK` script constant) were located and their role
  stated, but the hook script's own shell logic was not read line by line — only the
  policy endpoint it calls back into (`policy.rs`) was read in depth.
- **Live end-to-end verification was not run.** `e2e_git.rs`'s authenticated-flow tests are
  marked `#[ignore = "requires live relay + MinIO + git"]` and were read as source, not
  executed, for this node.
- **Whether a future corpus node will own the push-policy engine** (branch protection,
  role evaluation) as its own capability, or whether that content folds into this node
  later, is unresolved — recorded here as an explicit gap, not decided by this node.
