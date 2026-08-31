---
id: platforms-relay-git-api
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The git hosting module's own module-level doc comment states its responsibility as 'Git hosting — Smart HTTP transport, permission hooks, and policy engine', and enumerates its own submodules: transport (Smart HTTP protocol: info/refs, upload-pack, receive-pack), hook (pre-receive hook script and injection), and policy (internal policy endpoint, HMAC-authenticated callback from the hook)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/mod.rs"
  - statement: "`git_router` mounts three public HTTP endpoints under `/git/{owner}/{repo}/...`: `GET info/refs`, `POST git-upload-pack`, and `POST git-receive-pack`, all behind one `RequestBodyLimitLayer` sized from `state.config.git_max_pack_bytes`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "A separate `git_policy_router` mounts `POST /internal/git/policy` behind a `require_localhost` middleware (rejects any request whose connection is not from a loopback address) and a fixed 1 MB body limit; its doc comment states this is the endpoint the pre-receive hook calls back to for push authorization."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/mod.rs"
  - statement: "`GitAuth`, an axum `FromRequestParts` extractor, is the single shared authentication gate for every route on both routers: it requires an `Authorization: Nostr <base64-event>` header, decodes and NIP-98-verifies it, and rejects with 401 plus a `WWW-Authenticate: Nostr` challenge otherwise. Its own doc comment states the authorization split this node documents: reads (ref advertisement, upload-pack) require the caller's current active channel membership, while push authorization is additionally handled by the pre-receive hook calling back to the internal policy endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`authorize_git_read` is the read-path authorization function: it resolves the repo's kind:30617 announcement, resolves its `buzz-channel` binding (denying on `NotBound` or `Broken`, with a remediation-message carve-out when the caller is the announcement's own author), and denies unless `read_role_allows` recognizes the caller's current channel-membership role. Unlike push authorization, there is no role-tiered permission matrix for reads — any current, recognized membership role is sufficient."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`upload_pack`'s handler comment explicitly notes that the reused NIP-98 token from the `info/refs` GET cannot stand in for POST-time membership, so `authorize_git_read` is called independently at the start of both `info_refs` and `upload_pack` before any hydration or subprocess work begins."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`info_refs` (`GET info/refs?service=...`) validates the `service` parameter against an exact allowlist (`git-upload-pack` or `git-receive-pack`) and, for a `git-upload-pack` request against a manifest with no tag refs (`fast_path_eligible`), serves the ref advertisement built directly from the published manifest — no ephemeral-workspace hydration, no git subprocess, and no `git_semaphore` permit acquired. Any other case (a receive-pack advertisement, or an upload-pack advertisement for a repo with tags) falls back to `info_refs_subprocess`, which does acquire a permit and hydrate a repo before shelling out to `git <service> --advertise-refs`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`upload_pack` (`POST git-upload-pack`, clone/fetch) decodes a gzip-compressed request body if present (`decode_git_request_body`, bounding the inflated size at `UPLOAD_PACK_MAX_DECODED_BYTES` independently of the router's compressed-bytes body limit, to bound a gzip-bomb amplification), then hydrates the published state into an ephemeral bare repository and streams the `git upload-pack` subprocess's stdout directly into the HTTP response body rather than buffering the whole pack in memory."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`receive_pack` (`POST git-receive-pack`, push) is mounted on the same router and gated by the same `GitAuth` extractor, but its authorization, hook-callback, permission-matrix, and CAS-publish behavior are already fully documented by architecture-flows-git-push; this node does not restate that detail."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "The git hosting module's Cargo dependency edges include `buzz-auth` (NIP-98 event verification), `buzz-core` (kind constants, `channel::MemberRole` used by `read_role_allows`), `buzz-db` (kind:30617 announcement and channel-membership queries), `tower-http` (`RequestBodyLimitLayer`), and `async-compression` (the gzip decoder used to decompress smart-HTTP request bodies)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
  - statement: "`git-credential-nostr` is a separate, independently built client-side crate — a git credential helper that signs the NIP-98 authentication event this API surface's `GitAuth` extractor verifies, letting `git push`/`git pull`/`git fetch` authenticate without a password prompt. It is not a Cargo dependency of `buzz-relay`; it interoperates with this API purely over the HTTP protocol this node describes."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md"
  - statement: "`git-sign-nostr` is a further separate, independently built client-side program that signs git commit and tag objects with a Nostr secp256k1 key (NIP-GS, via `git config gpg.format x509`). It signs the git objects themselves, which this API surface neither requires nor inspects when serving or accepting them — it is orthogonal client tooling, not a dependency of the relay's git hosting module."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md"
  - statement: "`read_gate_allows_current_member_denies_removed_and_owner_bypass`, `read_gate_denies_missing_or_malformed_binding_and_absent_repo`, `read_gate_gives_author_of_unbound_repo_remediation_body`, and `read_gate_follows_current_announcement_not_stale_registry` are unit tests exercising `authorize_git_read`'s decision logic directly, without needing a live relay, Postgres, or git subprocess."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`fast_path_eligible_branches_only`, `fast_path_rejects_any_tag`, `fast_path_rejects_head_not_in_refs`, `fast_path_rejects_unsafe_refname`, `fast_path_rejects_malformed_oid`, and `fast_path_rejects_overlong_refname` are unit tests covering the conditions under which `info_refs` takes its manifest-only fast path versus falling back to the subprocess path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`upload_pack_stream_returns_timeout_error_at_deadline` and `upload_pack_stream_counts_response_bytes` are unit tests covering the streamed-response path's timeout and byte-accounting behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The end-to-end suite's `git_clone_push_fetch_force_roundtrip` test (already cited by architecture-flows-git-push for its push assertions) also exercises this node's read path indirectly, since every push in that test is followed by a fresh clone that must observe the pushed state; it is `#[ignore]`-gated behind a live relay, MinIO, and git, and was read rather than executed for this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
---

# Platform component: relay git smart-HTTP API

The Buzz relay's git hosting surface — the Smart HTTP endpoints
(`crates/buzz-relay/src/api/git/`) that let a standard `git` client clone,
fetch from, and push to a Buzz-hosted repository. This node documents the
API surface as a whole: its routes, shared authentication, the read path
(`info/refs`, `git-upload-pack`), its dependencies, and its client-side
interop tooling. It does not restate the push-specific authorization,
hook-callback, and CAS-publish detail that
[`architecture-flows-git-push`](../../architecture/flows/git-push.md)
already documents in depth — see *Boundary* below.

**No `platforms`-specific corpus template is merged yet.** Per this Feature's
settled convention for the `platforms/**` surface, this node uses
`type: platforms` and borrows `templates/component.md`'s section shape
(Responsibility, Public interface, Dependencies, Boundary, Relationships,
Scope and omissions), since that template already documents "one software
component ... as a standalone knowledge artifact" and no closer-fitting
template exists at this revision. Expect this node to be reshaped once a
`platforms`-specific template lands.

## Responsibility

Per its own module doc comment, this module is "Git hosting — Smart HTTP
transport, permission hooks, and policy engine," organized into three
submodules: `transport` (the Smart HTTP protocol itself — `info/refs`,
`upload-pack`, `receive-pack`), `hook` (the pre-receive hook script and its
injection into an ephemeral workspace), and `policy` (the internal,
HMAC-authenticated policy callback the hook calls back to). This node's
subject is the API surface `transport` exposes and the authentication and
dependency shape common to all of it; `hook` and `policy`'s push-specific
behavior is covered by `architecture-flows-git-push`.

## Public interface

| Route | Method | Handler | Purpose |
|---|---|---|---|
| `/git/{owner}/{repo}/info/refs?service=...` | GET | `info_refs` | Advertise refs for clone (`git-upload-pack`) or push (`git-receive-pack`) negotiation |
| `/git/{owner}/{repo}/git-upload-pack` | POST | `upload_pack` | Clone/fetch: client sends wants/haves, server streams pack data |
| `/git/{owner}/{repo}/git-receive-pack` | POST | `receive_pack` | Push: see `architecture-flows-git-push` for full detail |
| `/internal/git/policy` | POST | `policy::hook_policy_check` | Loopback-only pre-receive hook callback; see `architecture-flows-git-push` |

All three `/git/{owner}/{repo}/...` routes share one `RequestBodyLimitLayer`
sized from `state.config.git_max_pack_bytes` (`git_router`). The internal
policy route is mounted on a separate router (`git_policy_router`) behind a
`require_localhost` middleware and a fixed 1 MB body limit — defense in
depth on top of the HMAC binding `architecture-flows-git-push` documents.

Every route on both routers is gated by the same `GitAuth` extractor: a
`Authorization: Nostr <base64-event>` header, NIP-98-verified, rejecting
with 401 and a `WWW-Authenticate: Nostr` challenge when absent or invalid.
`GitAuth`'s own doc comment states the authorization split this node
documents: **reads** (`info_refs`, `upload_pack`) require only the caller's
current, active channel membership — no push-style role tiering — while
**push** authorization is additionally handled by the pre-receive hook's
callback to the internal policy endpoint.

### Read-path authorization

`authorize_git_read` is called independently at the start of both
`info_refs` and `upload_pack`, before any hydration or subprocess work. This
matters because git's smart-HTTP credential protocol reuses one token
across the `info/refs` GET and the following POST in a session — a comment
at the top of `upload_pack` notes explicitly that the GET's authorization
cannot stand in for POST-time membership, so the check is repeated rather
than cached across the two requests.

`authorize_git_read`'s decision: resolve the repo's kind:30617 announcement,
resolve its `buzz-channel` binding (deny on `NotBound` or `Broken`, with a
remediation-message carve-out — same 404 status, different body — when the
caller is the announcement's own author), then deny unless
`read_role_allows` recognizes the caller's current channel-membership role
string. Unlike push, there is no permission matrix by ref-update kind: any
current, recognized role suffices to read.

### Ref advertisement: fast path versus subprocess

`info_refs` validates its `service` query parameter against an exact
allowlist (`git-upload-pack` | `git-receive-pack`) before anything else. For
a `git-upload-pack` advertisement against a manifest with no `refs/tags/*`
entries (`fast_path_eligible`), the response is built directly from the
published manifest: no ephemeral workspace, no `git` subprocess, no
`git_semaphore` permit. Any other case — a `git-receive-pack` advertisement
(different capability set), or an upload-pack advertisement for a repo that
has tags — falls back to `info_refs_subprocess`, which acquires a permit,
hydrates a fresh ephemeral workspace, and shells out to
`git <service> --advertise-refs`.

### Upload-pack: decompression and streaming

`upload_pack` first decodes a gzip-compressed request body if present
(git's smart-HTTP client compresses the request once it exceeds an internal
threshold). `decode_git_request_body` bounds the *inflated* size at a fixed
constant independently of the router's body-limit layer (which only caps
compressed bytes), specifically to bound a gzip-bomb amplification attack.
After hydrating the published state into an ephemeral bare repository, the
handler streams the `git upload-pack` subprocess's stdout directly into the
HTTP response body rather than buffering the whole pack in memory.

## Dependencies

**Depends on** (this module requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-auth` | NIP-98 signed-event verification behind `GitAuth` | `crates/buzz-relay/Cargo.toml` |
| `buzz-core` | Kind constants; `channel::MemberRole`, parsed by `read_role_allows` | `crates/buzz-relay/Cargo.toml` |
| `buzz-db` | kind:30617 announcement lookup and channel-membership role queries | `crates/buzz-relay/Cargo.toml` |
| `tower-http` | `RequestBodyLimitLayer` on both routers | `crates/buzz-relay/Cargo.toml` |
| `async-compression` | Gzip decoding of smart-HTTP request bodies | `crates/buzz-relay/Cargo.toml` |

**Client-side interop, not a build dependency:**

| Tool | Relationship to this API | Evidence |
|---|---|---|
| `git-credential-nostr` | Signs the NIP-98 event `GitAuth` verifies; lets `git` authenticate to this API without a password prompt | `crates/git-credential-nostr/README.md` |
| `git-sign-nostr` | Signs git commit/tag objects with a Nostr key (NIP-GS) — orthogonal to this API, which neither requires nor inspects object-level signatures | `crates/git-sign-nostr/README.md` |

## Boundary

This node does not describe:
- **Push transport authentication, the pre-receive policy callback, the
  role/ref-update permission matrix, or the CAS-publish → kind:30618
  sequence.** All of that is `architecture-flows-git-push`'s subject, in
  detail this node deliberately does not duplicate.
- **The object-store hydration/publish machinery's internals**
  (`hydrate.rs`, `manifest.rs`, `store.rs`, `pack_cache.rs`,
  `cas_publish.rs`) — this node cites what the HTTP handlers observe (a
  hydrated ephemeral repo, a published manifest, a CAS outcome), not how
  those subsystems are implemented.
- **NIP-GS commit/tag object signing mechanics** — named above as related
  client-side tooling, not detailed further; it is orthogonal to this
  relay-side API surface.
- **A component/architecture-component-style decomposition diagram** — no
  `platforms`-specific template requiring one is merged at this revision;
  see the template note above.

## Relationships

- references: architecture-flows-git-push

## Scope and omissions

**This node covers** the relay's git smart-HTTP API surface as a whole: its
four HTTP routes and how they are mounted and body-limited, the shared
`GitAuth` NIP-98 authentication gate, the read-path authorization model
(distinct from push's permission matrix), the ref-advertisement fast path
versus subprocess fallback, upload-pack's decompression and streaming
behavior, its Cargo-level dependencies, and its client-side interop tooling
(`git-credential-nostr`, `git-sign-nostr`).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Push transport authentication, policy callback, permission matrix, CAS publish, kind:30618 emission | `architecture-flows-git-push` |
| Object-store hydration/publish internals (pointer format, manifest canonicalization, pack/idx storage) | `crates/buzz-relay/src/api/git/{hydrate,manifest,store,cas_publish,pack_cache}.rs` — not yet a corpus node |
| NIP-GS commit/tag signing mechanics | `crates/git-sign-nostr/` — not yet a corpus node |
| Repo creation from a kind:30617 announcement and the invite/community-provisioning flow that grants channel membership in the first place | Separate architecture/flow nodes, none of which exist in the merged corpus at this revision (same gap `architecture-flows-git-push` names) |

**No further `relationships` are declared beyond the one above.** At the
recorded revision, no `platforms/**` node other than this one exists on
`origin/launchpad` — this is the first. The natural future edges (to a
repo-creation/announcement flow node, and to a corpus node for the
object-store hydration/publish machinery, should one be authored) are named
above as a pointer for whoever authors those nodes, or for a later pass over
this one once they exist.

**Expected but not verified when this node was written:**

- **The end-to-end clone/push/fetch test was read, not executed.**
  `git_clone_push_fetch_force_roundtrip` is `#[ignore]`-gated behind a live
  relay, MinIO, and `git`, none of which were started for this task. Its
  clone assertions (a fresh clone observes the exact pushed or rewritten
  content) are the closest representative coverage of this node's read
  path, but this node's confidence rests on reading that test's assertions
  and the production code path they exercise, not on a passing run.
- **`hook.rs` and `policy.rs` were read only to the extent needed to state
  the API-surface boundary** (that push authorization is "additionally
  handled" by the hook and policy endpoint) — their internal logic is
  `architecture-flows-git-push`'s subject and was not independently
  re-verified for this node beyond confirming that node's own citations
  still match the files at the recorded revision.
- **Whether desktop or mobile clients depend on this API's exact error
  bodies or status codes for the read path** (as `architecture-flows-git-push`
  documents for one push-specific denial body) was not traced into
  `desktop/` or `mobile/` for this node.
