---
id: development-public-api-changes
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Root AGENTS.md states three 'Additional rules' for contributed code -- no `unsafe` code, no new `unwrap()` or `expect()` in production paths, and 'New public API must have doc comments' -- as a bare list with no named enforcement mechanism attached to any of the three."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "CONTRIBUTING.md's 'What a Good PR Looks Like' item 3 ('Documented') requires that public APIs, new event kinds, new MCP tools and new config variables are documented, and to update README.md, AGENTS.md or VISION.md as appropriate."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "CONTRIBUTING.md's 'Linting' section states clippy is run with warnings-as-errors as `cargo clippy --all-targets --all-features -- -D warnings`, and that a believed false positive is handled with a targeted `#[allow(...)]` carrying a comment explaining why."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "The Justfile's `clippy` recipe is exactly `cargo clippy --workspace --all-targets -- -D warnings`; the `check` recipe depends on nine prerequisites -- fmt-check, clippy, desktop-check, desktop-tauri-fmt-check, desktop-tauri-clippy, web-check, mobile-check, security-review-check and file-size-check -- and the `ci` recipe depends on `check` plus test-unit, desktop-test, desktop-build, desktop-tauri-check, desktop-tauri-test, web-build and mobile-test."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "CI's `rust-lint` job runs `just clippy` after `just fmt-check` and `just desktop-tauri-fmt-check`, and is gated on the `changes` job reporting Rust or desktop-Rust changes (or on a push event)."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "Twelve of the twenty-six workspace crates that have a `src/lib.rs` carry `#![warn(missing_docs)]` at the crate root -- buzz-audit, buzz-auth, buzz-conformance, buzz-core, buzz-db, buzz-deletion, buzz-pubsub, buzz-relay, buzz-sdk, buzz-search, buzz-test-client and buzz-workflow -- and buzz-cli is not one of them."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs"
      - "crates/buzz-core/src/lib.rs"
      - "crates/buzz-cli/src/lib.rs"
      - "grep(pattern='warn(missing_docs)', path='crates/*/src/lib.rs', revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> 12 crates match; buzz-acp, buzz-agent, buzz-cli, buzz-datastore-tracing, buzz-dev-mcp, buzz-media, buzz-pair-relay, buzz-persona, buzz-push-gateway, buzz-relay-mesh, buzz-voice, buzz-ws-client, git-credential-nostr and git-sign-nostr do not; buzz-admin, buzz-backend-kubernetes, buzz-pairing-cli and sprig have no src/lib.rs"
  - statement: "In a crate carrying `#![warn(missing_docs)]`, an undocumented public item fails the repository's own clippy invocation: appending `pub struct UndocumentedProbe;` to crates/buzz-sdk/src/lib.rs and running `cargo clippy -p buzz-sdk --all-targets -- -D warnings` exits 101 with 'error: missing documentation for a struct' and 'note: `-D missing-docs` implied by `-D warnings`', while the identical command against the unmodified file exits 0."
    entry_class: FACT
    evidence:
      - "cargo_clippy(-p buzz-sdk --all-targets -- -D warnings, revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90, unmodified) -> Finished `dev` profile in 1m 10s, exit status 0"
      - "cargo_clippy(-p buzz-sdk --all-targets -- -D warnings, revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90, with `pub struct UndocumentedProbe;` appended to crates/buzz-sdk/src/lib.rs) -> error: missing documentation for a struct --> crates/buzz-sdk/src/lib.rs:115:1; note: `-D missing-docs` implied by `-D warnings`; error: could not compile `buzz-sdk` (lib) due to 1 previous error; exit status 101"
  - statement: "The `missing_docs` escape hatch is already used inside the tree: buzz-relay carries `#[allow(dead_code, missing_docs)]` in src/handlers/mod.rs and `#[allow(missing_docs)]` in src/tunnel/reliable.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/mod.rs"
      - "crates/buzz-relay/src/tunnel/reliable.rs"
  - statement: "AGENTS.md's doc-comment rule is therefore enforced by tooling only inside the twelve crates that opted in via the crate-root attribute, and is review-enforced everywhere else in the workspace."
    entry_class: INFERENCE
    evidence:
      - "AGENTS.md"
      - "Justfile"
      - "crates/buzz-cli/src/lib.rs"
      - "cargo_clippy(-p buzz-sdk --all-targets -- -D warnings, with an undocumented pub item) -> exit status 101 on `missing_docs`"
    confidence: 0.9
  - statement: "crates/buzz-cli/src/lib.rs declares `client`, `commands`, `error`, `links` and `validate` as private modules; only `agent_management` is `pub mod`, and the crate's public Rust entry point is the single function `run_from_args`, which returns a process exit code."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "buzz-cli's stable contract for its consumers is therefore its command-line surface -- subcommand and flag names, the JSON written to stdout, the JSON error object written to stderr, and the process exit code -- rather than its Rust API, because `error::exit_code`, `error::print_error` and the `client` normalizers are all `pub` items inside private modules and so are unreachable from any other crate."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-cli/src/error.rs"
      - "crates/buzz-cli/README.md"
    confidence: 0.9
  - statement: "`exit_code` maps CliError variants to 1 (Usage, NotFound), 2 (Network, DeliveryUnknown, and Relay with any status other than 401/403), 3 (Auth, Key, and Relay with status 401 or 403), 4 (Other) and 5 (Conflict), with 0 returned by `run_from_args` on success."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "The same exit-code table is written out in four places that must be edited together -- the doc comment on `exit_code`, the clap `long_about` string in crates/buzz-cli/src/lib.rs (so it appears in `buzz --help`), crates/buzz-cli/README.md's Usage section, and root AGENTS.md's Agent CLI section (lines 201-244) -- and while all four assign the same numbers, they describe code 1 differently: '1=user/not-found', '1=bad input', '1=user error' and '1=input error' respectively, only the first of which reflects that `exit_code` maps both `Usage` and `NotFound` to 1."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-cli/README.md"
      - "AGENTS.md"
  - statement: "No test in the repository asserts `exit_code`'s mapping: crates/buzz-cli/src/error.rs's `#[cfg(test)] mod tests` covers `is_retryable_error` for network/relay/other errors, the `retryable` field and `error` category of the stderr JSON, and the `Display` source chain, but never calls `exit_code`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
      - "grep(pattern='exit_code', path='crates/ desktop/ scripts/', revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> matches in buzz-persona's own unrelated Report::exit_code, buzz-dev-mcp's shell JSON field, buzz-backend-kubernetes and the e2e last_exit_code field; no assertion against buzz_cli::error::exit_code"
  - statement: "The CLI's read output shape is pinned by unit tests: `normalize_events` rebuilds each event from the six always-present canonical Nostr fields plus `sig` when it is a string, and `normalize_events_preserves_the_complete_signed_event_shape` asserts the result round-trips into a `nostr::Event`, verifies its signature, retains `sig`, and drops an injected `relay_internal` field."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "The CLI's write output shape is produced by `normalize_write_response`, which emits exactly `{event_id, accepted, message}` when the relay body carries either `event_id` or `accepted`, and otherwise passes the raw body through unchanged."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "`just test-unit` runs `cargo nextest run -p buzz-cli` (the whole package, not only `--lib`) and, separately, `cargo test -p buzz-auth --doc`, the latter with an inline comment stating that nextest does not run doctests and that the sealed-authority `compile_fail` doctests prove the default-feature public API alone cannot forge the issuer-to-JWKS authority."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "buzz-auth uses ```compile_fail``` doctests as executable negative API tests in three places: on `AssertionKeySet` (naming the crate-private constructor `AssertionKeySet::new` must not compile downstream), on the sealed `IssuerKeySource` trait (an external implementation must not compile), and on `TokenClass` (the removed `NamedCompatibility` variant must not compile)."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip_fi/verifier.rs"
      - "crates/buzz-auth/src/nip_fi/config.rs"
  - statement: "buzz-sdk's crate documentation states its contract as: each builder function validates its inputs and returns an `nostr::EventBuilder`, the caller signs with their own keys, no keys are held and no network calls are made; it re-exports `buzz_core::kind` so consumers do not need buzz-core directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs"
  - statement: "buzz-sdk is depended on from five other manifests in this repository -- crates/buzz-acp, crates/buzz-cli, crates/buzz-relay, crates/buzz-test-client and desktop/src-tauri -- the last of which is outside the root Cargo workspace, which Cargo.toml excludes."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/Cargo.toml"
      - "Cargo.toml"
      - "grep(pattern='buzz-sdk', path='crates/*/Cargo.toml desktop/src-tauri/Cargo.toml', revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> crates/buzz-acp/Cargo.toml, crates/buzz-cli/Cargo.toml, crates/buzz-relay/Cargo.toml, crates/buzz-test-client/Cargo.toml, crates/buzz-sdk/Cargo.toml, desktop/src-tauri/Cargo.toml"
  - statement: "Every workspace crate inherits one shared version, \"0.1.0\", from Cargo.toml's [workspace.package]; no crate declares an independent version; and only crates/git-sign-nostr/Cargo.toml sets `publish = false`, with the comment 'internal workspace tool, not published to crates.io'."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "crates/git-sign-nostr/Cargo.toml"
      - "crates/buzz-sdk/Cargo.toml"
  - statement: "A Cargo-level semantic-version bump is therefore not a signal available to this repository's crate consumers: one shared 0.1.0 cannot express that buzz-sdk broke while buzz-core did not, and inside 0.x Cargo's own compatibility rules would treat a minor bump as breaking anyway."
    entry_class: INFERENCE
    evidence:
      - "Cargo.toml"
      - "crates/buzz-sdk/Cargo.toml"
    confidence: 0.85
  - statement: "The only compatibility rule this repository states in prose is CONTRIBUTING.md's Architecture Overview: 'Event kinds are the only switch ... Adding a new feature means defining a new kind. No breaking changes to existing clients.'"
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "There is no repository-wide semantic-versioning, backward-compatibility or deprecation policy document: searching CONTRIBUTING.md, AGENTS.md and RELEASING.md case-insensitively for 'semver', 'backward compat' and 'breaking change' returns exactly one line, the event-kind sentence above."
    entry_class: FACT
    evidence:
      - "grep(pattern='semver|backward.compat|breaking change', flags='-i', path='CONTRIBUTING.md AGENTS.md RELEASING.md', revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> CONTRIBUTING.md:390 only"
  - statement: "CONTRIBUTING.md's 'How to Add a New API Endpoint' opens by preferring a signed Nostr event over a new endpoint, names the relay's narrow HTTP surface, and then gives six steps: define the handler under crates/buzz-relay/src/api/ resolving the tenant before auth, register the route in crates/buzz-relay/src/router.rs using the narrowest path, add buzz-db queries only when the event query paths cannot express it, use the `api_error()`/`internal_error()`/`not_found()` helpers, write buzz-test-client tests covering auth and community scoping, and document any public endpoint in ARCHITECTURE.md and user-facing docs."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "ARCHITECTURE.md's HTTP endpoints table in section 6 lists seventeen rows, while crates/buzz-relay/src/router.rs additionally mounts routes that table does not list -- among them /workflows/{workflow_id}/runs, /workflows/{workflow_id}/runs/{run_id}/approvals, five /operator/communities paths, /api/invites, /api/invites/claim, /api/invites/accept-policy, /api/join-policy and its /terms and /privacy pages, /moderation/reports, /moderation/audit, /moderation/restricted, the two GIF proxy paths, /huddle/{channel_id}/audio, the testbed-only /_mesh/demo/echo, /upload, and a conditionally-nested /api/admin/v1 sub-router."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-relay/src/router.rs"
  - statement: "The merged corpus node architecture-principles-nostr-first already owns the analysis of router.rs's route list against the narrow HTTP surface AGENTS.md and CONTRIBUTING.md enumerate, and separately records that nothing mechanical fails a build or CI run that adds an endpoint outside that documented set; it compares router.rs against those two files rather than against ARCHITECTURE.md's section 6 table."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/nostr-first.md"
  - statement: "An author adding an HTTP endpoint must therefore treat CONTRIBUTING.md's documentation step as an obligation rather than reading the table's existing silence about a neighboring route as evidence that documenting theirs is optional."
    entry_class: INFERENCE
    evidence:
      - "CONTRIBUTING.md"
      - "ARCHITECTURE.md"
      - "crates/buzz-relay/src/router.rs"
      - "launchpad/docs/corpus/architecture/principles/nostr-first.md"
    confidence: 0.8
  - statement: "The merged corpus node architecture-containers-cli carries the CLI's exit-code mapping and its stderr JSON error object as FACT entries in its own provenance ledger, citing crates/buzz-cli/src/error.rs and crates/buzz-cli/README.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
  - statement: "The merged corpus node corpus-development-build records that a full `cargo build --workspace` failed in the checking environment inside buzz-voice's sherpa-onnx-sys build script on an HTTPS download, while `cargo build --workspace --exclude buzz-voice` succeeded for the other 29 members at the same revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
  - statement: "CONTRIBUTING.md states that `just test` starts Docker services automatically if they are not already running, and that integration tests spin up the relay and exercise the full stack."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "`cargo` is not on PATH in this environment until the repository's Hermit environment is activated, after which `bin/cargo` resolves and reports cargo 1.95.0."
    entry_class: FACT
    evidence:
      - "which(cargo, cwd=repo root, before activation) -> 'timeout: failed to run command cargo: No such file or directory'; after `. ./bin/activate-hermit` -> /home/serina/Launchpad/buzz/__worktrees/task-862-development-public-api-changes/bin/cargo, 'cargo 1.95.0 (f2d3ce0bd 2026-03-21)'"
      - "AGENTS.md"
  - statement: "crates/buzz-cli/TESTING.md is a per-command live-testing runbook whose sections carry literal `# Expected:` output lines for each subcommand, so a change to a subcommand's stdout shape invalidates the specific expected line rather than the document generally."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/TESTING.md"
  - statement: "AGENTS.md states that the required DCO Check fails any PR with a commit missing a `Signed-off-by` trailer, that `just hooks` installs a commit-msg hook adding it to locally created commits while `git rebase` and `git cherry-pick` still need `--signoff`, and that the repair path for a branch with unsigned commits is `git rebase --signoff` followed by a force-push."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "CONTRIBUTING.md's 'PRs We're Unlikely to Merge' section names large refactors or dependency swaps without a prior issue agreeing on the direction, and entirely new features with no prior discussion, and asks the contributor to open an issue first."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "At the recorded revision the corpus has no governance/ directory; launchpad/docs/corpus/development/ holds exactly four merged nodes -- build.md, debugging.md, hermit.md and prerequisites.md -- so this node is the fifth; and launchpad/docs/corpus/architecture/containers/ holds desktop.md, web.md and mobile.md among its nodes."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, path='launchpad/docs/corpus') -> AGENTS.md, README.md, agents/, architecture/, capabilities/, development/{build,debugging,hermit,prerequisites}.md, layers/, schema/, standards/, templates/; no governance/ entry"
  - statement: "Compatibility policy and deprecation policy are owned by separate open tasks -- launchpad-26/buzz#908 'task: document governance/compatibility-policy.md' and #911 'task: document governance/deprecation-policy.md' -- both reported OPEN and neither merged into the corpus at the recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#908 and #911 (gh issue list --repo launchpad-26/buzz --state all, both rows state OPEN)"
  - statement: "The two neighboring development procedures are likewise owned by separate open tasks -- launchpad-26/buzz#861 'task: document development/protocol-changes.md' and #858 'task: document development/event-kind-changes.md' -- both reported OPEN and neither merged at the recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#861 and #858 (gh issue view --repo launchpad-26/buzz, both state OPEN)"
  - statement: "Issue #862's definition of done requires that the procedure state goal, prerequisites and allowed environment/scope; give ordered executable project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands and configuration rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#862 definition of done"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: architecture-containers-cli
  - type: references
    target: corpus-development-build
  - type: references
    target: architecture-principles-nostr-first
---

# Changing a public API surface: how-to

How to land a change to a surface that code outside its own crate depends on -- a `pub`
item in a library crate, the `buzz` CLI's command-line contract, or one of the relay's
HTTP routes -- so that the change carries its documentation, its tests, and the edits to the
other files that restate the same contract. Read this when you are about to widen,
narrow, rename or re-shape one of those three surfaces. If you are only changing
behavior *behind* an unchanged surface, none of this applies.

## What counts as a public surface here

Three surfaces, and they are enforced by three different mechanisms. Knowing which one
you are touching decides which steps below you owe.

| Surface | What "public" means | What holds it |
|---|---|---|
| A library crate's Rust API | Any `pub` item reachable from the crate root | `#![warn(missing_docs)]` in twelve crates, plus `cargo clippy --workspace --all-targets -- -D warnings` |
| The `buzz` CLI | Subcommand and flag names, stdout JSON, stderr JSON, process exit code | Unit tests on the normalizers; nothing on exit codes; four hand-maintained copies of the exit-code table |
| The relay's HTTP routes | Any path registered in `crates/buzz-relay/src/router.rs` | `buzz-test-client` integration tests, and a documentation step in `CONTRIBUTING.md` |

Two clarifications that repeatedly catch authors out:

**`pub` inside a private module is not public.** `crates/buzz-cli/src/lib.rs` declares
`client`, `commands`, `error`, `links` and `validate` as private modules. `exit_code`,
`print_error` and `normalize_events` are all `pub`, and none of them is reachable from
another crate: buzz-cli's only exported Rust items are `agent_management` and
`run_from_args`. So changing `exit_code`'s signature breaks nothing at compile time --
and changing what it *returns* breaks every script that reads `$?`. The compiler is
silent about exactly the change that matters.

**A doc-comment gate you did not opt into does not exist.** Twelve of the twenty-six
crates with a `src/lib.rs` carry `#![warn(missing_docs)]`: `buzz-audit`, `buzz-auth`,
`buzz-conformance`, `buzz-core`, `buzz-db`, `buzz-deletion`, `buzz-pubsub`,
`buzz-relay`, `buzz-sdk`, `buzz-search`, `buzz-test-client` and `buzz-workflow`. In
those, an undocumented `pub` item is a hard CI failure -- verified by appending
`pub struct UndocumentedProbe;` to `crates/buzz-sdk/src/lib.rs` and running the
repository's own clippy invocation, which exited 101 with ``note: `-D missing-docs`
implied by `-D warnings` ``. In the other fourteen -- `buzz-cli` among them --
`AGENTS.md`'s "New public API must have doc comments" is held by review alone.

## Before you start

- **Activate the pinned toolchain.** `. ./bin/activate-hermit` from the repository
  root. Without it `cargo` may not be on `PATH` at all, and the version that is will
  not be the pinned one.
- **Open an issue first if the change is a refactor, a dependency swap, or a new
  feature.** `CONTRIBUTING.md`'s "PRs We're Unlikely to Merge" names those three
  categories as things that get closed without a prior issue agreeing on the direction.
  A public-surface change is very often one of them.
- **Know which of the three surfaces you are touching**, per the table above. If the
  answer is "the wire format" or "a new event kind", stop -- see *Boundary* below.
- **Have Docker available** if your surface change needs the integration suite.
  `CONTRIBUTING.md` states `just test` starts the Docker services itself when they are
  not already running, so this is an "installed and usable" prerequisite rather than a
  "started by hand" one. The infra-free gates below need none of it.

## Change the surface

1. **Make the source change**, in the crate that owns the surface. For a new HTTP
   route, follow `CONTRIBUTING.md`'s "How to Add a New API Endpoint" in order: handler
   under `crates/buzz-relay/src/api/` with the tenant resolved before any auth or data
   lookup, route registered in `crates/buzz-relay/src/router.rs` at the narrowest path,
   errors returned through the `api_error()` / `internal_error()` / `not_found()`
   helpers as `(StatusCode, Json<Value>)`.

2. **Write the doc comment, on every new or newly-`pub` item.** Not only in the twelve
   opted-in crates -- `AGENTS.md`'s rule is workspace-wide; the attribute is only what
   makes twelve of them fail loudly. Where an item is deliberately undocumented,
   `#[allow(missing_docs)]` with a reason is the in-tree pattern
   (`crates/buzz-relay/src/handlers/mod.rs` and `src/tunnel/reliable.rs` both use it),
   matching `CONTRIBUTING.md`'s instruction to make any lint suppression targeted and
   commented.

3. **If you narrowed or removed something, add the negative test that proves it.**
   `buzz-auth` is the worked example: ```compile_fail``` doctests assert that a
   downstream crate cannot name the crate-private `AssertionKeySet::new`, cannot
   implement the sealed `IssuerKeySource` trait, and cannot construct the removed
   `TokenClass::NamedCompatibility` variant. A removal with no such test is a removal
   that silently comes back. Note that `cargo nextest` does not run doctests, which is
   why the Justfile carries a separate `cargo test -p buzz-auth --doc` line -- if you
   add `compile_fail` doctests to a different crate, that crate needs its own line too.

4. **If you changed CLI output, update the normalizer and its test together.**
   `normalize_events` in `crates/buzz-cli/src/client.rs` rebuilds each event from the
   six always-present canonical Nostr fields plus `sig`;
   `normalize_events_preserves_the_complete_signed_event_shape` asserts the result
   round-trips into a `nostr::Event`, verifies its signature, and drops an injected
   `relay_internal` field. `normalize_write_response` pins writes to
   `{event_id, accepted, message}`. Changing the shape without changing the test means
   the test is now asserting the old contract against new code, or nothing at all.

5. **If you changed an exit code, edit all four copies of the table.** There is no
   single source: the doc comment on `exit_code` in `crates/buzz-cli/src/error.rs`, the
   clap `long_about` string in `crates/buzz-cli/src/lib.rs` (which is what `buzz --help`
   prints), the Usage section of `crates/buzz-cli/README.md`, and root `AGENTS.md`'s
   Agent CLI section. No test asserts the mapping, and none of the four copies is
   checked against another, so a partial edit ships green.

6. **Update the documents that restate the contract.** `CONTRIBUTING.md` item 3 requires
   public APIs, new event kinds, new MCP tools and new config variables to be
   documented, and names `README.md`, `AGENTS.md` and `VISION.md` as the files to
   update. For an HTTP route, `CONTRIBUTING.md` step 6 additionally requires
   `ARCHITECTURE.md`. Treat that as an obligation, not a convention: `ARCHITECTURE.md`'s
   section 6 endpoint table lists seventeen rows while `router.rs` mounts considerably
   more, so its silence about a route near yours is evidence of drift, not of scope. The
   parallel drift between `router.rs` and the narrow surface `AGENTS.md` and
   `CONTRIBUTING.md` enumerate is already analysed in
   `architecture/principles/nostr-first.md`, which also records that nothing mechanical
   fails a build or CI run for adding an endpoint outside that set -- read it rather
   than re-deriving it here.

7. **Update `crates/buzz-cli/TESTING.md` if you changed a subcommand's output.** It is a
   per-command runbook with literal `# Expected:` lines, so the edit is to the specific
   expected line for your subcommand, not a general refresh.

8. **Add the integration test the surface needs.** For an HTTP endpoint,
   `CONTRIBUTING.md` step 5 requires a `crates/buzz-test-client/tests/` test covering
   auth, community scoping and the success path.

## Verify the change

Run these in order; each is cheap enough to run before the one after it.

1. `cargo clippy -p <your-crate> --all-targets -- -D warnings` -- the fastest signal
   that a missing doc comment will fail CI, scoped to one crate.
2. `just clippy` -- the exact command CI's `rust-lint` job runs
   (`cargo clippy --workspace --all-targets -- -D warnings`). Passing per-crate does not
   imply passing workspace-wide, because a downstream crate may now fail to compile
   against your changed signature.
3. `just test-unit` -- runs `cargo nextest run -p buzz-cli` and
   `cargo test -p buzz-auth --doc`, so it covers both the CLI normalizer tests and the
   `compile_fail` doctests. Needs no Docker.
4. `just check` -- adds the formatting, desktop, web, mobile and file-size gates
   `just clippy` alone does not cover.
5. `just test` -- the integration suite, if you touched `buzz-relay`, `buzz-db` or
   `buzz-auth`. It needs Postgres and Redis, and starts those Docker services itself if
   they are not already up.
6. `just ci` -- the whole local gate, before you push.

**What none of these establish.** No test asserts the CLI's exit-code mapping, and no
check compares the four copies of the exit-code table against one another. A green run
after step 5 above is not evidence that the exit codes still agree; only reading all
four is.

## Roll back or clean up

- **Before committing:** `git checkout -- <paths>` restores the source files. If you ran
  the doc-comment probe from step 2 of *Verify* by hand, confirm the revert with
  `git status --porcelain <path>` rather than assuming -- an empty result is the check.
- **After committing, before pushing:** prefer `git revert` over rewriting history. If
  you do rewrite, note that `AGENTS.md` requires every commit to carry a
  `Signed-off-by` trailer for the DCO check, and that `git rebase` and `git cherry-pick`
  do not add it -- `AGENTS.md`'s own repair path is `git rebase --signoff`, then a
  force-push.
- **After merging:** a public-surface removal cannot be un-shipped by a revert alone
  once a consumer has adopted it. Because every crate shares one `0.1.0` version from
  `[workspace.package]`, there is no per-crate semantic-version signal a downstream
  consumer could pin against, so the revert has to be announced rather than inferred.
  Sequencing a removal so consumers get warning is deprecation *policy*, which this node
  does not own -- see *Boundary*.
- **Build artifacts** left behind by the clippy and test runs above are removed by
  `cargo clean`. Apart from the source files you deliberately edited, `target/` is the
  only thing this procedure creates.

## See also

- `launchpad/docs/corpus/architecture/containers/cli.md` -- the `buzz-cli` container
  node, which carries the exit-code and stderr-JSON contract as reference material this
  procedure deliberately does not restate in full.
- `launchpad/docs/corpus/development/build.md` -- the build procedure the verification
  steps above assume.
- `launchpad/docs/corpus/architecture/principles/nostr-first.md` -- why the HTTP surface
  is narrow, and the existing analysis of how far `router.rs` has drifted from it.
- `CONTRIBUTING.md` -- "Linting", "What a Good PR Looks Like", "PRs We're Unlikely to
  Merge", and "How to Add a New API Endpoint".
- `AGENTS.md` -- the "Additional rules" list, the narrow-HTTP-surface pattern, and the
  Agent CLI section carrying one of the four exit-code copies.
- `ARCHITECTURE.md` section 6 -- the HTTP endpoint table a new route must be added to.
- `crates/buzz-cli/TESTING.md` -- the per-command expected-output runbook.

## Boundary

This node does not describe:

- **How to change the wire protocol or the event format.** That is
  `development/protocol-changes.md`'s subject.
- **How to add or change an event kind.** That is `development/event-kind-changes.md`'s
  subject. The boundary is worth stating plainly because `CONTRIBUTING.md` routes most
  new capability *away* from this node: its "How to Add a New API Endpoint" section
  opens by preferring a signed Nostr event over an HTTP endpoint, and its Architecture
  Overview states "Event kinds are the only switch ... Adding a new feature means
  defining a new kind." So the common case for adding capability is
  `event-kind-changes.md`'s procedure, and this node is for the cases where an
  existing Rust, CLI or HTTP surface genuinely has to move.
- **What compatibility guarantees the project offers, or when a break is permitted.**
  That is compatibility *policy*, owned by `governance/compatibility-policy.md`. This
  node's steps say what a change must carry, not whether it is allowed.
- **How to sequence a deprecation, or how long a deprecated surface must survive.**
  That is deprecation *policy*, owned by `governance/deprecation-policy.md`. The
  rollback section above stops at the boundary deliberately.
- **Facts about the CLI's surface that you want to look up rather than act on** --
  the full subcommand list, the exit-code semantics, the stderr JSON shape. Those are
  reference content; `architecture/containers/cli.md` and `crates/buzz-cli/README.md`
  hold them.
- **Why the relay's HTTP surface is deliberately narrow, and how far `router.rs` has
  drifted from that.** `architecture/principles/nostr-first.md` owns both, including
  the finding that no check bounds the router's route list. This node instructs; that
  node explains.

## Relationships

- `implements: corpus-template-procedure` -- this node is an instance of the procedure
  template, which names "a template instance of a standard" as `implements`' own worked
  example.
- `references: architecture-containers-cli` -- the CLI container node holds the
  exit-code and output contract this procedure instructs the reader to keep in sync,
  and is the reference this node defers completeness to.
- `references: corpus-development-build` -- the verification steps above are build and
  test invocations whose own procedure that node owns.
- `references: architecture-principles-nostr-first` -- step 6 defers the router-versus-
  documented-surface analysis to it rather than restating it.

All four targets were confirmed to resolve on the merge target, not merely in this
worktree: `git show origin/launchpad:launchpad/docs/corpus/templates/procedure.md`,
`.../architecture/containers/cli.md`, `.../development/build.md` and
`.../architecture/principles/nostr-first.md` report `corpus-template-procedure`,
`architecture-containers-cli`, `corpus-development-build` and
`architecture-principles-nostr-first` respectively. At the recorded revision, no edge
was declared toward `development-protocol-changes`, `development-event-kind-changes`,
`governance-compatibility-policy` or `governance-deprecation-policy`, because none of
those nodes existed on `origin/launchpad` yet and a `relationships[].target` naming an
unloaded id is a hard validation error. All four have since landed in this same
integration, so the natural edges now resolve; they are not added here, since wiring
them in under the pressure of a pre-merge fix pass risks the same kind of error this
fix pass exists to catch. Adding them belongs to a dedicated pass across the whole
`development`/`governance`/`releases` shelf once all 37 nodes are stable.

## Scope and omissions

**This node covers** which three surfaces count as public in this repository, what
mechanism holds each one, the ordered steps for landing a change to any of them, the
verification ladder from a single-crate clippy run up to `just ci`, and the rollback and
cleanup available at each stage.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Wire-protocol and event-format changes | `development/protocol-changes.md` |
| Event-kind additions and changes | `development/event-kind-changes.md` |
| Compatibility guarantees and when a break is permitted | `governance/compatibility-policy.md` |
| Deprecation sequencing and support windows | `governance/deprecation-policy.md` |
| The `buzz-cli` surface as lookup reference | `launchpad/docs/corpus/architecture/containers/cli.md` |
| Building and testing the workspace | `launchpad/docs/corpus/development/build.md` |
| The desktop, web and mobile clients' own API surfaces | `architecture/containers/{desktop,web,mobile}.md` exist as container nodes; whether any owns a change procedure for those surfaces was not checked |

**The desktop, web and mobile surfaces are a deliberate omission, not an oversight.**
This node scopes "public API" to the Rust workspace, the CLI and the relay's HTTP
routes. `desktop/src-tauri` sits outside the root Cargo workspace -- `Cargo.toml`
excludes it -- so `just clippy`'s `--workspace` does not reach it, and its Tauri command
surface is held by the separate `desktop-tauri-clippy` gate. Whether that constitutes a
fourth public surface was not decided here.

**Expected but not verified when this node was written.** Each item below is a gap in
what the claims above rest on, not a boundary; the revision every claim was checked
against is recorded as the first entry of this node's provenance ledger.

- **The clippy behavior was proven on one crate, not on the workspace.** The
  undocumented-item probe was run as `cargo clippy -p buzz-sdk --all-targets -- -D
  warnings`, not as `just clippy`. The two use the same flags, and the failure came from
  rustc's `missing_docs` lint rather than anything crate-specific, but a full
  `just clippy` run was not executed at the recorded revision -- and the sibling
  `development/build.md` node records that a clean full-workspace build fails in some
  environments inside `buzz-voice`'s `sherpa-onnx-sys` build script for reasons
  unrelated to any source defect.
- **No step below the clippy probe was executed.** `just test-unit`, `just check`,
  `just test` and `just ci` are cited from the Justfile and from CI's `rust-lint` job,
  not from runs made here. The procedure template's own stronger expectation -- that a
  step's evidence cite having run the command -- is met for step 1 of *Verify* only, and
  not for steps 2 through 6.
- **The four exit-code copies already differ in wording, and the significance of that
  was not resolved.** All four were opened and all four assign the same numbers, but
  code 1 is described as "user/not-found" in `error.rs`, "bad input" in the clap
  `long_about`, "user error" in `README.md` and "input error" in `AGENTS.md` -- and
  `exit_code` does in fact map both `Usage` and `NotFound` to 1, which only the first of
  the four says. Whether the three shorter phrasings are an acceptable abbreviation or a
  documentation defect was not decided here; no tooling compares them.
- **Whether `buzz-sdk` or any other crate is actually published to crates.io was not
  established.** Only `git-sign-nostr` sets `publish = false`; whether the rest have ever
  been published, and therefore whether a real external consumer exists outside this
  repository's five in-tree dependents, was not verifiable from the tree.
- **The exact count of routes `router.rs` mounts was not computed.** The claim above is
  that `ARCHITECTURE.md`'s seventeen-row table omits specific named routes that
  `router.rs` registers, each of which was read; it is not a claim about a total.
