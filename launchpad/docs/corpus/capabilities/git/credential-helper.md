---
id: capabilities-git-credential-helper
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "git-credential-nostr is a standard git credential helper: it implements git's credential-helper stdin/stdout protocol (reading `get`/`store`/`erase` invocations, capability negotiation lines, and `protocol=`/`host=`/`path=`/`wwwauth[]=` fields) rather than any Buzz-specific transport of its own."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
  - statement: "When invoked with a Buzz git server's `WWW-Authenticate: Nostr realm=\"...\", method=\"...\"` challenge present on stdin, the helper loads a Nostr private key, builds a NIP-98 (kind:27235) event signed over the request's URL and method, base64-encodes the serialized event, and writes it back to git as `credential=<base64>` alongside `authtype=Nostr`, so git retries the request with `Authorization: Nostr <token>`."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
      - "crates/git-credential-nostr/README.md"
  - statement: "The signed URL is the repo-root path with the trailing `/info/refs`, `/git-upload-pack`, or `/git-receive-pack` suffix stripped, so one signed token covers the whole push/clone session rather than one distinct URL per git operation."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
  - statement: "The private key is resolved from `$NOSTR_PRIVATE_KEY` (checked first, for CI/CD use without touching the filesystem) or else from the path in `git config nostr.keyfile`; a configured keyfile is rejected if it is not a regular file, exceeds a 256-byte size cap, or (on Unix) is readable by group or other (anything beyond the low 9 bits' owner-write/read bits, i.e. not effectively 0600)."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
  - statement: "The raw key string is explicitly zeroized (via the `zeroize` crate) immediately after being parsed into `nostr::Keys`, both on the success path and when key parsing fails, so the secret does not linger in process memory longer than needed to construct the signing keys."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
  - statement: "A NIP-OA owner-attestation `auth` tag, sourced from `$BUZZ_AUTH_TAG` or `git config nostr.authtag` as a 4-element JSON array (`[\"auth\", owner_pubkey, conditions, signature]`), is attached to the same signed NIP-98 event when present, because git's credential-helper protocol has no way to carry an attestation as a separate HTTP header alongside the `Authorization` value it returns."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
  - statement: "An `includes_nip_oa_auth_tag_in_signed_event` integration test confirms the auth tag survives inside the signed event (verifiable via `event.verify()`) rather than being appended unsigned after the fact, and `malformed_nip_oa_auth_tag_fails_closed` confirms a non-JSON or wrong-shaped `$BUZZ_AUTH_TAG` value exits 1 with no `credential=` line emitted, rather than silently authenticating without the intended delegation."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/tests/integration.rs"
  - statement: "The helper only acts on the `get` subcommand (or no subcommand); `store`, `erase`, and any other invocation exit 0 silently, matching the credential-helper contract that a helper need not persist or clear anything it does not manage."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
  - statement: "The helper declines gracefully (exit 0, no `credential=` output) rather than erroring in two cases that mean this is not a Buzz remote or the request context does not support Nostr auth: no `capability[]=authtype` line from git (old git, pre-2.46), and a present `wwwauth[]=` value that either is not the `Nostr` scheme or has no parseable `method=\"...\"` parameter -- both confirmed by the `old_git_no_authtype_capability` and `missing_method_hint` integration tests -- so a global `credential.helper nostr` configuration is safe to set even when git talks to non-Buzz remotes, letting git fall through to another configured helper."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
      - "crates/git-credential-nostr/tests/integration.rs"
  - statement: "Once the request is recognized as a Buzz/Nostr challenge, missing protocol, host, or path fields are treated as hard errors (exit 1, message to stderr) rather than declined -- the `missing_path` test specifically asserts that an absent `path=` field (meaning `git config credential.useHttpPath true` was not set) fails with a message naming `useHttpPath`, and `missing_key` asserts that no configured Nostr key at all fails with `no nostr key configured` rather than silently producing no credential."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
      - "crates/git-credential-nostr/tests/integration.rs"
  - statement: "The helper requires git 2.46 or newer because it depends on the credential protocol's `authtype` capability (returning `authtype=Nostr` plus a raw `credential=` value rather than a conventional `username`/`password` pair); this version requirement and the required one-time setup (`git config --global credential.helper nostr`, `git config --global credential.useHttpPath true`, plus a keyfile or `$NOSTR_PRIVATE_KEY`) are documented in the crate's own README rather than enforced by any runtime version check in the code."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md"
      - "crates/git-credential-nostr/src/lib.rs"
  - statement: "The crate is a normal Cargo workspace member (not excluded the way the Tauri desktop crate is), so its 8 subprocess-level integration tests -- covering the happy path, the NIP-OA auth-tag pass-through and its fail-closed malformed case, the old-git and missing-method-hint graceful declines, the missing-key and missing-path hard errors, and insecure keyfile permissions -- run under a plain `cargo test` with no live relay, network, or `#[ignore]` gate required."
    entry_class: FACT
    evidence:
      - "Cargo.toml:25"
      - "crates/git-credential-nostr/tests/integration.rs"
  - statement: "VISION_PROJECTS.md's own Status table marks \"Git hosting (smart HTTP + NIP-34)\" as shipped (\"Ships today\"), and states directly that \"git hosting ships today -- git clone/git push over smart HTTP with NIP-34 manifests\"; this credential helper is the client-side authentication mechanism that makes an ordinary `git push`/`git clone` against that shipped smart-HTTP surface work without manual token handling."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-259"
  - statement: "The merged `architecture-flows-git-push` node already documents this same helper as the client-side signing step (its step 1, \"Client-side signing\") of the git-push transport flow, describing the identical NIP-98 kind:27235 signing and base64-token hand-off this node describes from the helper's own perspective."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
---

# Git credential helper: capability

A user or agent with a Nostr key can use ordinary `git clone`, `git push`,
and `git fetch` against a Buzz git server without ever handling a password
or manually constructing an auth header. `git-credential-nostr`, installed
as a standard git credential helper, intercepts the credential prompt git
issues on an `HTTP 401` challenge, signs a short-lived NIP-98 authentication
event with the caller's Nostr private key, and hands the result back to git
to retry the request as `Authorization: Nostr <token>` -- transparent to
every normal git command a person or an agent already knows how to run.

## Maturity

**Shipped**, as part of a shipped parent capability. VISION_PROJECTS.md's own
Status table marks "Git hosting (smart HTTP + NIP-34)" as "Ships today," and
the credential helper is the client-side half of that already-shipped
transport: it is a real, buildable Cargo workspace crate
(`crates/git-credential-nostr`) with a compiled binary, a documented
installation and setup procedure, and 8 integration tests exercising its
subprocess behavior end to end (input on stdin, assertions on stdout/
stderr/exit code) -- run under a plain `cargo test`, with no live relay or
network dependency, unlike the flow's own server-side e2e coverage.

## Boundary

This node does not describe:

- **How the server verifies the token this helper produces.** NIP-98 event
  verification, tenant/URL binding, and the NIP-43 relay-membership gate are
  server-side concerns, already documented by `architecture-flows-git-push`
  (its "Ordered interactions" steps 2-4) rather than restated here.
- **The smart-HTTP transport and object-store publish path** the
  authenticated request ultimately drives (ref advertisement, pack
  negotiation, CAS publish, the derived kind:30618 event). Also owned by
  `architecture-flows-git-push`.
- **Commit/tag object signing (NIP-GS, `git-sign-nostr`).** A separate,
  orthogonal capability: NIP-GS signs the git objects themselves, while this
  helper authenticates the HTTP request that carries them. The two do not
  depend on each other.
- **Push/pull authorization policy** (role-based ref-update rules, branch
  protection). This helper only produces an authenticated identity; what
  that identity is allowed to do is decided entirely server-side.

## Relationships

- references: `architecture-flows-git-push` -- the push-transport flow this
  helper's signing step feeds into; that node documents the server-side
  verification and authorization this node's boundary excludes.

No other sibling capability node in this batch (`git-hosting`,
`nostr-git-authentication`, `smart-http`, `git-signing`, and others) is
merged on `origin/launchpad` at the recorded revision, so no further
`relationships` targets resolve; the natural next edges are a `part-of`
toward a merged `git-hosting` overview node and a `references` toward a
`nostr-git-authentication` node, once either exists.

## Scope and omissions

**This node covers** what the `git-credential-nostr` helper does (NIP-98
event signing triggered by git's credential-helper protocol), how it locates
and protects the signing key (env var precedence, keyfile permission and
size checks, zeroization), how it carries an optional NIP-OA owner
attestation inside the signed event, its graceful-decline behavior for
non-Buzz remotes and old git versions, its fail-closed behavior for
misconfiguration once a Buzz challenge is recognized, its git-version
requirement and one-time setup, and the test coverage backing each of these
behaviors.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Server-side NIP-98/NIP-43 verification of the token this helper produces | `architecture-flows-git-push` |
| Smart-HTTP transport and object-store publish mechanics | `architecture-flows-git-push` |
| Commit/tag object signing (NIP-GS) | A separate capability (`git-signing`, sibling task, not yet merged) |
| The broader "Git hosting" product capability this helper is one part of | A separate capability (`git-hosting`, sibling task, not yet merged) |
| Push/pull authorization policy (roles, branch protection) | Server-side authorization, documented in `architecture-flows-git-push` |

**Expected but not verified when this node was written:**

- **No live end-to-end run against a real Buzz relay was performed.** The 8
  integration tests cited above exercise the helper as a subprocess with
  synthetic stdin and environment, not against a live server issuing a real
  `WWW-Authenticate: Nostr` challenge; that live path is covered (but
  `#[ignore]`-gated, per `architecture-flows-git-push`) by
  `crates/buzz-test-client/tests/e2e_git.rs`, not by this crate's own tests.
- **Windows/non-Unix keyfile-permission behavior was not exercised.** The
  `#[cfg(not(unix))]` branch of `check_keyfile_permissions` only emits a
  warning and always succeeds; this was read in code but not run on a
  non-Unix platform.
- **Whether any git client other than the reference `git` CLI (e.g. a
  library implementation of the credential-helper protocol) invokes this
  helper compatibly was not checked.**
