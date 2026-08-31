---
id: implementation-crates-git-credential-nostr
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "The crate's Cargo.toml declares a library (`git_credential_nostr`, path `src/lib.rs`) and a binary (`git-credential-nostr`, path `src/main.rs`), with dependencies `nostr`, `serde_json`, `zeroize`, and `base64 = \"0.22\"`; `main.rs` is a three-line wrapper that calls `git_credential_nostr::run()` and exits with its return code."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/Cargo.toml"
      - "crates/git-credential-nostr/src/main.rs"
  - statement: "`run()` in `src/lib.rs` implements git's credential-helper stdin/stdout protocol: it reads `capability[]=`, `protocol=`, `host=`, `path=`, and `wwwauth[]=` lines via `parse_stdin`, and for anything other than the `get` subcommand (or no argument) it exits 0 silently without touching stdin."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:107-133"
      - "crates/git-credential-nostr/src/lib.rs:152-158"
  - statement: "The helper declines gracefully (exit 0, no credential emitted) in three specific cases, in this order: no `capability[]=authtype` line present; no `wwwauth[]=Nostr ...` challenge present; a `wwwauth[]=Nostr ...` challenge present but `parse_method` cannot extract a `method=\"...\"` parameter from it — each case lets git fall through to another credential helper or an unauthenticated request rather than erroring."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:135-188"
  - statement: "Past the decline checks, missing `protocol=`, `host=`, or `path=` input lines are hard errors (exit 1, message to stderr) rather than silent declines, since a `Nostr` challenge with a method hint means git does expect this helper to answer; a missing `path=` specifically reports \"credential.useHttpPath must be true for NIP-98 auth\"."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:190-198"
  - statement: "The request URL signed into the NIP-98 event is repo-root scoped: `repo_path` strips a trailing `/info/refs` (splitting at that substring) or a trailing `/git-upload-pack` or `/git-receive-pack` suffix from the credential request's `path=` before building `{protocol}://{host}/{repo_path}`, so the same signed token covers the initial `info/refs` GET and the following pack POST in one push/fetch session."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:200-206"
  - statement: "The Nostr private key is loaded by `load_key`: it first checks the `NOSTR_PRIVATE_KEY` environment variable (used as-is if non-empty), and only if that is unset or empty falls back to `git config --get nostr.keyfile`, then requires the keyfile be a regular file no larger than 256 bytes (`MAX_KEYFILE_BYTES`) and, on Unix, requires file mode bits `0o177` be clear (rejecting any group/other read/write/execute) via `check_keyfile_permissions`; on non-Unix targets that permission check is a no-op that only prints a warning."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:16-72"
  - statement: "The raw key string is held in a local `String` and explicitly `zeroize()`d immediately after `Keys::parse` succeeds or fails, so the plaintext key material does not linger in the process's memory beyond the parse call — this is the crate's only defensive-memory-handling measure and the only reason `zeroize` is a dependency."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:208-224"
  - statement: "An optional NIP-OA `auth` tag is loaded by `load_auth_tag` from the `BUZZ_AUTH_TAG` environment variable (falling back to `git config --get nostr.authtag`), parsed as a 4-element JSON array whose first element must be the literal string `\"auth\"`; a value present but malformed (wrong length, wrong first element, or invalid tag syntax) is a hard error (exit 1, \"invalid NIP-OA auth tag\"), and this tag, when present, is attached to the `EventBuilder` before signing so it is covered by the NIP-98 event's own signature."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:74-96"
      - "crates/git-credential-nostr/src/lib.rs:228-239"
  - statement: "docs/nips/NIP-OA.md specifies the `auth` tag as exactly `[\"auth\", \"<owner-pubkey-hex>\", \"<conditions>\", \"<sig-hex>\"]` (four elements, literal `\"auth\"` first element) and states an owner-pubkey equal to the event's own pubkey is invalid — the same four-element, `\"auth\"`-first shape `load_auth_tag` validates before attaching the tag to the signed event."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md:31"
      - "docs/nips/NIP-OA.md:34"
      - "docs/nips/NIP-OA.md:41"
      - "docs/nips/NIP-OA.md:66"
  - statement: "The comment above `load_auth_tag` states this tag must be part of the signed NIP-98 event because git's credential-helper protocol can return only an `Authorization` value, not a separate HTTP header, so an out-of-band NIP-OA attestation header is not an option for this transport."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:74-77"
  - statement: "The signed artifact is a NIP-98 kind:27235 event built via `nostr::EventBuilder::http_auth(HttpData::new(parsed_url, method))` and `sign_with_keys`; on success the event is JSON-serialized and base64-encoded (standard alphabet) into the credential-helper response's `credential=` line, alongside `capability[]=authtype`, `authtype=Nostr`, `ephemeral=true`, and `quit=true`."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:235-263"
  - statement: "The crate's own README documents the NIP-98 kind-27235 event and links `https://github.com/nostr-protocol/nips/blob/master/98.md` as the specification the signed event follows; this repository carries no local `docs/nips/NIP-98.md`, so NIP-98 is an external, upstream Nostr Improvement Proposal rather than a Buzz-specific one."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md:41-50"
  - statement: "The README also documents the operator-facing setup (`git config --global credential.helper nostr`, `credential.useHttpPath true`, a 0600 keyfile at a configured path, or `NOSTR_PRIVATE_KEY` for CI/CD) and a troubleshooting table covering every error string the binary can emit (`no nostr key configured`, `insecure permissions`, missing method hint, `useHttpPath`, empty output on old git, clock skew)."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md:16-39"
      - "crates/git-credential-nostr/README.md:60-69"
  - statement: "The crate's own integration tests (`crates/git-credential-nostr/tests/integration.rs`) spawn the compiled binary as a subprocess and assert on stdout/stderr/exit code for eight scenarios: happy path (well-formed credential response containing a valid kind:27235 event), a NIP-OA auth tag correctly folded into and covered by the event signature, a malformed auth tag failing closed with exit 1, old-git input with no `authtype` capability declining silently with exit 0, a missing Nostr key producing exit 1, a `wwwauth[]` challenge missing the `method=\"...\"` hint declining gracefully with exit 0, a missing `path=` line producing exit 1 mentioning `useHttpPath`, and (Unix-only) a 0644 keyfile being rejected with exit 1 mentioning `insecure permissions`."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/tests/integration.rs"
  - statement: "The crate is consumed two ways elsewhere in this repository: as a standalone installable binary (its own `[[bin]]` target, per the README's `cargo install --path crates/git-credential-nostr`), and as a library dependency of `buzz-dev-mcp` (`git-credential-nostr = { path = \"../git-credential-nostr\" }`), whose multicall dispatcher recognizes the personality name `git-credential-nostr` and calls `git_credential_nostr::run()` directly — that multicall entry point is itself reached through `sprig`'s own multicall dispatch, which forwards any unrecognized argv[0] to `buzz_dev_mcp::run()`."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml:18"
      - "crates/buzz-dev-mcp/src/lib.rs:149-153"
      - "crates/sprig/src/main.rs:38-42"
  - statement: "`scripts/bundle-sidecars.sh` lists `git-credential-nostr` among the sidecar binaries built and copied into `desktop/src-tauri/binaries` for the desktop app bundle, alongside `buzz-acp`, `buzz-agent`, `buzz-dev-mcp`, and `buzz`."
    entry_class: FACT
    evidence:
      - "scripts/bundle-sidecars.sh:4"
  - statement: "Desktop wires the helper into two independent flows via a shared `resolve_command(\"git-credential-nostr\")` lookup: `desktop/src-tauri/src/managed_agents/runtime.rs` sets ephemeral, agent-scoped `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_*`/`GIT_CONFIG_VALUE_*` environment variables (naming the helper and enabling `useHttpPath`) plus `NOSTR_PRIVATE_KEY` mirroring the managed agent's own signing key, scoped to the relay's HTTP base URL, when launching a managed agent's subprocess; `desktop/src-tauri/src/commands/project_git_exec.rs`'s `build_git_auth_config_for_keys` resolves the same binary path (falling back to `credential_helper: None` when not found) to drive Desktop's own project-level git subprocess calls, so the identity key never touches disk or global git config in either path."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs:526-550"
      - "desktop/src-tauri/src/commands/project_git_exec.rs:1-5"
      - "desktop/src-tauri/src/commands/project_git_exec.rs:222-235"
  - statement: "When `resolve_command(\"git-credential-nostr\")` finds nothing, `runtime.rs` logs a warning to stderr (\"buzz-desktop: git-credential-nostr not found — agent {name} will not have automatic Buzz git auth\") and proceeds without configuring git auth for that managed agent, rather than failing the agent launch outright."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs:545-550"
  - statement: "`architecture-flows-git-push` (merged corpus node, `launchpad/docs/corpus/architecture/flows/git-push.md`) already documents this crate as the client-side signer in its push flow's first ordered interaction and precondition list, citing this crate's own README as its evidence for that claim — this implementation-reference node is the crate-level counterpart that node's flow-level description points at."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md:27-30"
      - "launchpad/docs/corpus/architecture/flows/git-push.md:186-189"
      - "launchpad/docs/corpus/architecture/flows/git-push.md:195-200"
  - statement: "`crates/buzz-test-client/tests/e2e_git.rs` is a separate, `#[ignore]`-gated live-relay end-to-end suite whose header comment documents building this crate's release binary and pointing `GIT_CREDENTIAL_NOSTR_BIN` at it to exercise real push/fetch/clone flows; it was read for its documentation of how the compiled binary is invoked, not executed, in the course of writing this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs:7-18"
  - statement: "Object-level commit/tag signing with a Nostr key (NIP-GS, implemented by the separate `git-sign-nostr` crate) is a distinct concern this crate does not implement: this crate authenticates the HTTP request that carries git's smart-HTTP protocol exchange, while NIP-GS signs the git objects themselves after they exist, independent of how the push transport was authenticated."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md"
      - "docs/nips/NIP-GS.md"
  - statement: "Issue #943's Definition of Done requires the node to state implementation responsibility and what it deliberately does not own, name public interfaces/entry points and important dependencies, and link owned source paths and representative tests."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#943 (issue body, Definition of Done)"
relationships:
  - type: references
    target: architecture-flows-git-push
---

# git-credential-nostr: implementation reference

`crates/git-credential-nostr` is a git credential-helper binary (and library) that
answers git's credential-helper stdin/stdout protocol by signing a NIP-98 kind:27235
HTTP-auth event over the request URL with the caller's Nostr key, optionally carrying
a NIP-OA `auth` tag, and handing git back a base64-encoded token so it can retry the
request as `Authorization: Nostr <token>`. It claims to realize the client side of two
specifications it does not itself define: NIP-98 (external, upstream Nostr
Improvement Proposal — HTTP authentication) and, optionally, NIP-OA (this repository's
own owner-attestation NIP, `docs/nips/NIP-OA.md`).

## Target

- **NIP-98** — `https://github.com/nostr-protocol/nips/blob/master/98.md`, an
  upstream Nostr spec with no corpus node and no local copy in this repository
  (`docs/nips/` contains no `NIP-98.md`); a reader opens the upstream document
  directly. No `implements` edge is declared toward it because it carries no corpus
  node id.
- **NIP-OA** — `docs/nips/NIP-OA.md`, a repository-local NIP defining the `auth` tag
  this crate optionally attaches to the signed event. It also has no corpus node id
  today, so no `implements` edge is declared; a reader opens the file directly.
- **The server-side counterpart this crate's output authenticates against** is
  `crates/buzz-relay/src/api/git/transport.rs`'s `GitAuth` extractor, already
  documented at the flow level by the merged corpus node `architecture-flows-git-push`,
  which this node `references`.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `src/main.rs` | Binary entry point | Three lines: calls `git_credential_nostr::run()` and exits with its return code |
| `src/lib.rs::run` | Git credential-helper protocol loop | Subcommand dispatch (`get` only; everything else exits 0 silently), stdin parsing, decline/error branching, credential emission |
| `src/lib.rs::parse_stdin` / `CredRequest` | Reads `capability[]=`, `protocol=`, `host=`, `path=`, `wwwauth[]=` lines | Only the first `wwwauth[]=Nostr ...` line is kept |
| `src/lib.rs::parse_method` | Extracts `method="..."` from the `WWW-Authenticate: Nostr ...` challenge | Tolerates both `, ` and `,` separators |
| `src/lib.rs::load_key` / `check_keyfile_permissions` | Loads the Nostr private key: `NOSTR_PRIVATE_KEY` env var first, then `git config nostr.keyfile`, with a 256-byte size cap and (Unix) a `0600`-equivalent permission check | Zeroized (`zeroize`) immediately after `Keys::parse` |
| `src/lib.rs::load_auth_tag` | Optional NIP-OA `auth` tag from `BUZZ_AUTH_TAG` env var or `git config nostr.authtag`, validated as a 4-element `["auth", owner, conditions, sig]` array | Fails closed on malformed input rather than silently omitting the tag |
| `src/lib.rs::run` (event construction) | Builds and signs a NIP-98 kind:27235 event (`nostr::EventBuilder::http_auth`) over the repo-root-scoped URL and method, with the optional `auth` tag attached before signing | Repo-root scoping strips `/info/refs`, `/git-upload-pack`, `/git-receive-pack` suffixes from the request path so one token covers a whole push/fetch session |
| `Cargo.toml` | Crate manifest: `[lib]` `git_credential_nostr` + `[[bin]]` `git-credential-nostr`; deps `nostr`, `serde_json`, `zeroize`, `base64` | No workspace-internal dependencies — a leaf crate |

## Divergences

None found, checked against: the crate's own `README.md` "How It Works" section
against `src/lib.rs::run`'s actual control flow (decline order, error messages,
output lines); the NIP-OA `auth` tag shape in `docs/nips/NIP-OA.md` against
`load_auth_tag`'s validation (both require exactly four elements with a literal
`"auth"` first element); and the crate's behavior claims in
`architecture-flows-git-push`'s evidence ledger (that this crate signs a NIP-98
kind:27235 event over URL and method, and reuses one token across `info/refs` and the
following pack request) against `src/lib.rs` directly. All three checks agree with
the code as read at this node's recorded revision.

## Verification

- **Representative automated tests**: `crates/git-credential-nostr/tests/integration.rs`,
  eight subprocess-level tests exercising the happy path, NIP-OA tag inclusion and
  signature coverage, malformed-tag fail-closed behavior, old-git graceful decline,
  missing-key failure, missing-method-hint graceful decline, missing-path failure, and
  (Unix-only) insecure-keyfile-permission rejection. These are ordinary `cargo test`
  tests, not `#[ignore]`-gated, so they run in a default local or CI test invocation.
- **Not exercised in this task**: `crates/buzz-test-client/tests/e2e_git.rs`'s
  `#[ignore]`-gated live-relay suite, which builds this crate's release binary and
  drives it against a real relay + MinIO + git; it was read for its documented
  invocation contract only.
- **No CI job specific to this crate** was located beyond the workspace-wide
  `cargo test`/`cargo clippy` gates that would run `tests/integration.rs` as part of
  the standard suite; no crate-specific CI configuration file was found under
  `.github/workflows/` naming this crate individually.

## Relationships

- references: architecture-flows-git-push — the merged flow-level corpus node that
  already documents this crate's role as the push flow's client-side signer, citing
  this crate's own README as its evidence.

## Scope and omissions

**This node covers** what `crates/git-credential-nostr` is responsible for: answering
git's credential-helper protocol by signing a NIP-98 (optionally NIP-OA-tagged) event,
its public entry points (the `git-credential-nostr` binary and the
`git_credential_nostr::run()` library function), its dependencies, its error/decline
behavior, and where it is consumed elsewhere in the repository (standalone install,
`buzz-dev-mcp`'s multicall dispatch under `sprig`, desktop's managed-agent and
project-git wiring, and the desktop sidecar bundle).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Server-side NIP-98/NIP-43 verification of the token this crate produces | `architecture-flows-git-push` (`crates/buzz-relay/src/api/git/transport.rs`, `crates/buzz-auth/src/nip98.rs`) |
| NIP-GS commit/tag object signing | The separate `git-sign-nostr` crate, a distinct concern from HTTP-transport auth |
| The `nostr` crate's own NIP-98 event-building/signing internals | External dependency, not owned by this repository |
| Desktop's full managed-agent environment-variable layering (`build_respond_to_env`, descriptor env precedence) beyond the git-auth-specific `GIT_CONFIG_*` block | `desktop/src-tauri/src/managed_agents/runtime.rs`, out of this node's scope |
| `buzz-dev-mcp`'s other multicall personalities (`rg`, `tree`, `buzz`, `git-sign-nostr`) | `crates/buzz-dev-mcp` itself, not this crate |

**Expected but not verified when this node was written:**

- **No CI workflow file naming this crate specifically was located** — only the
  workspace-wide `just ci`/`cargo test` gates described in this repository's
  `AGENTS.md` were inferred to cover it; no `.github/workflows/*.yml` was opened
  specifically to confirm a per-crate job exists or does not.
- **Whether `desktop/src-tauri/binaries` actually contains a built
  `git-credential-nostr` sidecar in a shipped release** was not checked at runtime —
  only that `scripts/bundle-sidecars.sh` lists it as one of the binaries the build
  step copies in.
