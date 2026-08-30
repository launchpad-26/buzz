---
id: layers-compute-sprig-runtime
type: layers
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
  - statement: "sprig is a Rust binary crate at crates/sprig, a member of the root Cargo workspace, whose only dependencies are the buzz-acp, buzz-agent and buzz-dev-mcp crates (path dependencies)."
    entry_class: FACT
    evidence:
      - "Cargo.toml:14"
      - "crates/sprig/Cargo.toml"
  - statement: "crates/sprig/Cargo.toml describes the crate as \"All-in-one Buzz ACP harness, agent, and developer MCP\" and states it ships as a pinnable artifact released on its own cadence via sprig-v* tags, deliberately not inheriting the workspace version."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
  - statement: "sprig's binary entry point (crates/sprig/src/main.rs) is a multicall dispatcher: it reads argv[0]'s file name and, case-insensitively, dispatches to buzz_acp::run() for \"buzz-acp\", buzz_agent::run() for \"buzz-agent\", handles \"sprig\" itself only for -V/--version/-h/--help (erroring otherwise, since sprig is meant to be invoked via a personality symlink), and falls through to buzz_dev_mcp::run() for every other name."
    entry_class: FACT
    evidence:
      - "crates/sprig/src/main.rs"
  - statement: "buzz-dev-mcp's own run() function re-dispatches on the same argv[0]-derived command name for five further personality names before building a tokio runtime: rg and tree exit synchronously via internal modules (rg::run, tree::run), and git-credential-nostr and git-sign-nostr exit synchronously via the git_credential_nostr and git_sign_nostr crates' run() functions; buzz is handled after the tokio runtime is built, dispatching to buzz_cli::run_from_args(); any other name (including the literal buzz-dev-mcp) falls through to MCP server mode over stdio."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:135-181"
  - statement: "Of the five buzz-dev-mcp personality names, none shells out to a same-named system binary: tree is reimplemented in Rust using the ignore crate's gitignore-aware directory walker, buzz dispatches in-process to the buzz-cli crate's run_from_args, and git-credential-nostr/git-sign-nostr each call a path-dependency crate's own run() directly. rg is the one partial exception: it prefers a real system ripgrep found on PATH (excluding sprig's own install directory, to avoid self-recursion) and falls back to an internal search implementation only when none is found."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/tree.rs"
      - "crates/buzz-dev-mcp/src/rg.rs"
      - "crates/buzz-dev-mcp/src/lib.rs:172-174"
  - statement: "The dependency direction between sprig and the crates it bundles is one-way: buzz-acp's own Cargo.toml has no dependency on sprig and no reference to it anywhere under crates/buzz-acp/, so sprig is purely a packaging convenience layered on top of buzz-acp, buzz-agent and buzz-dev-mcp, not an architectural component those crates depend on or are aware of."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
  - statement: "crates/sprig contains only Cargo.toml and src/main.rs -- there is no tests/ directory and no #[test] function anywhere in the crate, so the multicall dispatch logic itself has zero automated test coverage at this revision."
    entry_class: FACT
    evidence:
      - "crates/sprig/src/main.rs"
  - statement: "The root Cargo.toml defines a dedicated [profile.sprig] that inherits release, sets opt-level = \"z\", lto = \"fat\", codegen-units = 1, panic = \"abort\" and strip = true -- a size-optimized build profile distinct from the default release profile, justified in the profile's own comment by sprig being distributed over the network and installed on fresh hosts, where binary size matters more than compile speed."
    entry_class: FACT
    evidence:
      - "Cargo.toml:170-176"
  - statement: "Dockerfile.sprig builds sprig with cargo build --locked --profile sprig -p sprig, strips the resulting binary, copies it to /usr/local/bin/sprig in an Alpine 3.22 runtime stage, and then creates a symlink to sprig for each of eight personality names in a loop: buzz-acp, buzz-agent, buzz-dev-mcp, rg, tree, buzz, git-credential-nostr and git-sign-nostr."
    entry_class: FACT
    evidence:
      - "Dockerfile.sprig"
  - statement: "The Dockerfile's runtime stage also configures a system-wide git identity for Nostr-based commit/tag signing (git config --system gpg.format x509, gpg.x509.program /usr/local/bin/git-sign-nostr, commit.gpgSign true, tag.gpgSign true) and sets the container entrypoint to scripts/sprig-entrypoint.sh, which scopes a git credential helper to $BUZZ_RELAY_URL (converted from ws(s):// to http(s)://) when that variable is set, and then execs buzz-acp \"$@\" -- exec, not a subshell call, so buzz-acp becomes PID 1 and receives termination signals directly."
    entry_class: FACT
    evidence:
      - "Dockerfile.sprig"
      - "scripts/sprig-entrypoint.sh"
  - statement: "Two GitHub Actions workflows build and publish sprig on independent lanes sharing the sprig-v* tag family: sprig.yml builds a static-musl (x86_64/aarch64-unknown-linux-musl) tarball, publishing a rolling sprig-latest release on push to main and a versioned release on sprig-v* tags; sprig-image.yml builds and publishes the multi-arch OCI image ghcr.io/block/buzz-sprig from Dockerfile.sprig, described in the workflow's own header comment as \"the digest-pinned box the Kubernetes backend deploys agents into.\""
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig.yml"
      - ".github/workflows/sprig-image.yml"
  - statement: "buzz-backend-kubernetes's config.rs defines DEFAULT_IMAGE as a tag+digest-qualified reference to ghcr.io/block/buzz-sprig, documented in the surrounding comments as a schema default (UI prefill) rather than a compiled-in fallback, since config::image's parser requires image to be present and digest-qualified, rejecting tag-only references (including :latest) because the object holding the reference runs with an nsec and a mutable tag is an unacceptable identity risk."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs"
      - "crates/buzz-backend-kubernetes/src/image.rs"
  - statement: "buzz-backend-kubernetes's pod.rs deliberately leaves readOnlyRootFilesystem unset on the agent pod's security context, with an inline comment stating the reason is that \"the sprig toolchain writes outside the workspace mount.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/pod.rs"
  - statement: "docs/remote-agents.md's Image section states the published ghcr.io/block/buzz-sprig image is an Alpine base plus bash, git, CA certificates and the static-musl sprig multicall binary with its personality symlinks, plus a baked system gitconfig wiring the Nostr signing/credential helpers scoped to the relay's git URL, and sizes the image at roughly 15-25MB (not FROM-scratch, because bash and git preclude it)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's Entrypoint and launch ABI section states the launch contract normatively: because sprig is a multicall binary with no supervisor personality (nothing in it reaps children or forwards signals), a conforming container entrypoint MUST end in exec so the harness process becomes PID 1 and receives Kubernetes' termination signal directly, and it further states a conforming custom/override image MUST contain the full runtime ABI (the buzz-acp entrypoint and everything the launch ABI requires) rather than merely alternate-harness dependencies -- summarized in the document as \"buzz-sprig plus your tools, never your tools instead.\""
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "The payload-to-environment mapping documented alongside the launch ABI hardcodes BUZZ_ACP_MCP_COMMAND=buzz-dev-mcp as an image-local default, and buzz-acp's own README documents BUZZ_ACP_MCP_COMMAND as an optional path to an MCP server binary provided to the agent subprocess -- consistent with sprig's buzz-dev-mcp personality being the MCP server the harness is expected to launch inside a sprig-built image, though the Kubernetes provider's own source was not found to independently assert that buzz-dev-mcp is the only MCP server any real deployment configures."
    entry_class: INFERENCE
    evidence:
      - "docs/remote-agents.md"
      - "crates/buzz-acp/README.md"
    confidence: 0.75
  - statement: "sprig's origin commit (70cb53e2c, \"Add Sprig all-in-one agent binary\", GitHub PR #605) converted what had been binary-only sprout-acp/sprout-agent/sprout-dev-mcp crates into lib.rs-plus-thin-main.rs shape so their run() logic could be called as library functions from the new multicall binary, and replaced an earlier scripts/build-agent-bundle.sh with the current scripts/build-sprig.sh; a later rename commit (d99ad131f, PR #958) renamed the sprout-* crates to buzz-* and updated sprig's dispatch accordingly. No commit reachable from this branch's history has changed the personality set or the dispatch match arms beyond those two commits plus one unrelated release-lane fix (549b7d248, PR #1173)."
    entry_class: FACT
    evidence:
      - "git_log(crates/sprig) -> 70cb53e2c, d99ad131f, 549b7d248"
  - statement: "An unmerged branch (origin/tomb/auth-tag-tool, commit bb3bd3306, \"Add local agent provisioning personality\") adds a fourth buzz-dev-mcp personality and touches crates/sprig/src/main.rs, but is not part of this branch's history and is not reflected in the sprig-runtime documented here -- it is evidence only that the current five/six-personality set is not necessarily final, not a claim about current behavior."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "git branch inspection during authoring of this node (origin/tomb/auth-tag-tool, commit bb3bd3306) -- an unmerged branch, so not independently verifiable as current repository fact"
relationships:
  - type: part-of
    target: architecture-containers-agent-runtime
---

# Sprig runtime

Sprig is the multicall Rust binary that packages Buzz's three agent-surface
crates -- `buzz-acp` (the ACP harness), `buzz-agent` (a minimal ACP-compliant
agent) and `buzz-dev-mcp` (a developer MCP server) -- into a single
deploy-anywhere executable, invoked through personality-named symlinks rather
than as separate binaries.

## Definition

`crates/sprig` is a thin binary crate whose entire logic is a dispatcher: at
startup it inspects `argv[0]` (the name it was invoked as, typically a
symlink) and calls straight into one of its three dependency crates'
library-mode `run()` functions. Invoked as `buzz-acp` it runs the ACP
harness; as `buzz-agent`, the agent; as anything else -- including
`buzz-dev-mcp` itself, or one of `buzz-dev-mcp`'s own sub-personality names
(`rg`, `tree`, `buzz`, `git-credential-nostr`, `git-sign-nostr`) -- it falls
through to `buzz-dev-mcp`, which performs a second, identically-shaped
dispatch of its own before falling through further to MCP server mode.
Invoked literally as `sprig` with no personality symlink, it prints usage and
exits with an error (unless asked for `-V`/`--version`/`-h`/`--help`), because
sprig is meant to be installed once and reached through several names, never
run under its own name in production.

This is the same multicall-binary pattern used by tools like BusyBox:
one set of compiled code, several installed names, no process supervision
built in. Sprig's crate description states this directly: "All-in-one Buzz
ACP harness, agent, and developer MCP."

Sprig ships as an independently versioned artifact (`sprig-v*` tags), not
tied to the rest of the Cargo workspace's version -- because it is
distributed and installed on hosts and in container images separately from
the relay or desktop release trains, and needs its own release cadence to
match.

## Boundary and non-goals

**Sprig is packaging, not a fourth architectural actor.** It contributes no
logic of its own beyond argv-based dispatch; every behavior a deployed sprig
binary exhibits belongs to whichever of `buzz-acp`, `buzz-agent` or
`buzz-dev-mcp` it dispatched into. The dependency direction is one-way --
`buzz-acp` has no dependency on and no awareness of `sprig` -- so sprig
cannot be understood as part of the ACP protocol or the agent loop; it is
purely a distribution unit sitting on top of them. This mirrors how the
sibling corpus node `architecture-containers-agent-runtime` already
describes it: a packaging detail of the agent-runtime container, not a
separate container in its own right.

**Sprig is not the Kubernetes backend.** `buzz-backend-kubernetes` (the
compute *provider* that launches sprig-built images as pods) is a distinct
crate and a distinct subject; this node documents what sprig **is** and how
it is **built**, not how a provider schedules or manages it. Where the
provider's behavior is relevant -- because it is sprig's actual runtime
consumer -- this node cites it as supporting evidence without duplicating
its logic.

**Sprig is not a process supervisor.** It has no personality that reaps
child processes or forwards signals; a container built from it must `exec`
into the harness so the harness becomes PID 1. This is a hard requirement on
anything that runs sprig, not a feature sprig itself provides.

## Use cases

**As a compute payload for the Kubernetes provider.** `buzz-backend-kubernetes`
schedules agent pods from the published `ghcr.io/block/buzz-sprig` image,
whose default reference is digest-pinned (never a mutable tag) because the
pod that runs it holds an `nsec`. `pod.rs` deliberately leaves
`readOnlyRootFilesystem` unset because, in its own words, "the sprig
toolchain writes outside the workspace mount." A custom/override image is
only conforming if it still contains the full runtime ABI sprig provides --
`docs/remote-agents.md` phrases this as "buzz-sprig plus your tools, never
your tools instead."

**As a single artifact to install once and symlink several ways.**
`Dockerfile.sprig` builds one stripped binary and creates eight
personality-named symlinks to it (`buzz-acp`, `buzz-agent`, `buzz-dev-mcp`,
`rg`, `tree`, `buzz`, `git-credential-nostr`, `git-sign-nostr`) in an Alpine
runtime image roughly 15-25MB in size. Any installer following the same
pattern -- not only the published container image -- gets the harness, the
agent and the dev-MCP server from one binary, so shared Rust/TLS/HTTP code
is compiled and stored once rather than three or eight times over.

**As a size-optimized release artifact.** The dedicated `[profile.sprig]`
Cargo profile (`opt-level = "z"`, `lto = "fat"`, `codegen-units = 1`,
`panic = "abort"`, `strip = true`) trades compile time for binary size,
because sprig is downloaded onto fresh hosts and into container images over
the network, where every byte is paid for on every pull.

**As a Nostr-native git identity inside the container.** The Docker image's
entrypoint wires `git-sign-nostr` as the system GPG program for commit/tag
signing and scopes `git-credential-nostr` to the configured relay URL, so a
sprig-built container can push and sign against a Buzz relay's git smart-HTTP
surface without a separate credential-helper installation step.

## Comparison of personality names

| Personality | Dispatched by | What runs |
|---|---|---|
| `buzz-acp` | sprig itself | `buzz_acp::run()` -- the ACP harness |
| `buzz-agent` | sprig itself | `buzz_agent::run()` -- the ACP-compliant agent |
| `buzz-dev-mcp` (or any unrecognized name) | sprig itself | `buzz_dev_mcp::run()` -- falls through to MCP server mode |
| `rg` | buzz-dev-mcp's own dispatch | real system `rg` if found on PATH (excluding sprig's own dir), else an internal fallback |
| `tree` | buzz-dev-mcp's own dispatch | a Rust reimplementation using the `ignore` crate's gitignore-aware walker |
| `buzz` | buzz-dev-mcp's own dispatch | `buzz_cli::run_from_args()` -- the Buzz relay CLI, in-process |
| `git-credential-nostr` | buzz-dev-mcp's own dispatch | the `git-credential-nostr` crate's `run()` |
| `git-sign-nostr` | buzz-dev-mcp's own dispatch | the `git-sign-nostr` crate's `run()` |

## Related resources

This node is `part-of` `architecture-containers-agent-runtime`, which states
the agent-runtime container's overall responsibility and technology
boundary and already carries a summary-level claim about sprig's packaging
role; this node is the deeper documentation of that specific packaging
mechanism. For the ACP harness, the agent loop and the developer MCP tool
surface themselves -- what runs once sprig has dispatched into them -- see
`crates/buzz-acp/README.md`, `crates/buzz-agent/README.md` and
`crates/buzz-dev-mcp/src/`, none of which are yet corpus nodes at this
revision. For the full Kubernetes launch-ABI contract (payload-to-environment
mapping, the five deployment invariants, digest-pinning rationale in full),
see `docs/remote-agents.md`.

## Scope and omissions

**This node covers** what the sprig binary is, how its multicall dispatch
works (both its own dispatch and the further dispatch inside `buzz-dev-mcp`
that it falls through to), how it is built and packaged as a container image
and as a standalone release tarball, and how the Kubernetes compute provider
consumes that image as its runtime payload.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The ACP wire protocol, harness configuration and BYOH tiers | `crates/buzz-acp/README.md` |
| The agent's turn loop, security model and size limits | `crates/buzz-agent/README.md` |
| The full developer MCP tool surface | `crates/buzz-dev-mcp/src/` |
| The Kubernetes provider's own scheduling, secrets and reconciliation logic | `crates/buzz-backend-kubernetes/` -- not yet a corpus node at this revision; a candidate follow-up |
| The full remote-agent provider protocol (payload schema, all five invariants) | `docs/remote-agents.md` |
| Whether any consumer besides `buzz-backend-kubernetes` currently builds or launches a sprig-based image in practice | Not established here; `docs/remote-agents.md` states the protocol admits any conforming launcher, but no second launcher was found in this repository at this revision |

**No test coverage exists for sprig's own dispatch logic.** `crates/sprig`
contains no `tests/` directory and no `#[test]` function. Correctness of the
dispatch is currently established only by manual reasoning against
`crates/sprig/src/main.rs` and `crates/buzz-dev-mcp/src/lib.rs`, not by any
automated check run against the built binary.

**Expected but not verified when this node was written:**

- **Whether `BUZZ_ACP_MCP_COMMAND=buzz-dev-mcp` is the value every real
  deployment actually configures**, versus documentation describing the
  image-local default. This is classified `INFERENCE` above, not `FACT`,
  because no source found during authoring independently confirms it as the
  only configuration in production use.
- **Whether the personality set (five `buzz-dev-mcp` sub-names plus the three
  top-level ones) is stable going forward.** An unmerged branch
  (`origin/tomb/auth-tag-tool`) adds a fourth `buzz-dev-mcp` personality; it
  is not part of this branch's history and is recorded here only as a signal,
  not as current fact.
- **The exact resource footprint of a running sprig-built container beyond
  the ~15-25MB image-size figure `docs/remote-agents.md` states** -- runtime
  memory/CPU behavior under load was not measured for this node.
