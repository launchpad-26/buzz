---
id: implementation-crates-sprig
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
  - statement: "crates/sprig/Cargo.toml declares sprig as a single `[[bin]]` target whose only dependencies are path dependencies on buzz-acp, buzz-agent and buzz-dev-mcp, and carries its own independent `version = \"0.1.0\"` with a comment stating it deliberately does not inherit the workspace version because it ships as a pinnable artifact on its own release cadence (`sprig-v*` tags)."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
  - statement: "crates/sprig/src/main.rs dispatches purely on the lowercased basename of argv0: the literal names `buzz-acp` and `buzz-agent` call `buzz_acp::run()` and `buzz_agent::run()` respectively; the literal name `sprig` prints usage and handles `-V`/`--version`/`-h`/`--help`, erroring \"invoke Sprig via a personality symlink\" when invoked with no arguments; every other name (including `rg`, `tree`, `buzz`, `git-credential-nostr`, `git-sign-nostr`) falls through to `buzz_dev_mcp::run()`."
    entry_class: FACT
    evidence:
      - "crates/sprig/src/main.rs"
  - statement: "crates/buzz-dev-mcp/src/lib.rs independently owns the dispatch for the `rg`, `tree`, `git-credential-nostr` and `git-sign-nostr` personality names (matched on the same kind of basename string) plus a `buzz` case, corroborating sprig's own main.rs comment that buzz-dev-mcp, not sprig itself, is responsible for those five additional multicall names."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:149-152"
      - "crates/buzz-dev-mcp/src/lib.rs:169"
  - statement: "Root Cargo.toml lists `crates/sprig` as a normal workspace member and separately defines a dedicated `[profile.sprig]` (inherits release, opt-level \"z\", lto \"fat\", codegen-units 1, panic \"abort\") used only for sprig's own optimized build, not the workspace-wide `release` profile."
    entry_class: FACT
    evidence:
      - "Cargo.toml:14"
      - "Cargo.toml:173-178"
  - statement: "Dockerfile.sprig builds the binary with `cargo build --locked --profile sprig -p sprig`, then symlinks all eight personality names (`buzz-acp`, `buzz-agent`, `buzz-dev-mcp`, `rg`, `tree`, `buzz`, `git-credential-nostr`, `git-sign-nostr`) to the single compiled `sprig` executable inside the runtime Alpine image, and its `ENTRYPOINT` is `scripts/sprig-entrypoint.sh`."
    entry_class: FACT
    evidence:
      - "Dockerfile.sprig"
  - statement: "scripts/sprig-entrypoint.sh configures a URL-scoped git credential helper pointing at `/usr/local/bin/git-credential-nostr` when `BUZZ_RELAY_URL` is set, then unconditionally execs `buzz-acp \"$@\"` as the container's PID 1 (a comment states this is so the harness receives Kubernetes' termination signal directly) — the image's entrypoint always launches the ACP harness personality, never `buzz-agent` or `buzz-dev-mcp` directly."
    entry_class: FACT
    evidence:
      - "scripts/sprig-entrypoint.sh"
  - statement: "buzz-acp's own `BUZZ_ACP_AGENT_COMMAND` CLI argument defaults to \"goose\" (a separate, non-Buzz agent CLI), not to \"buzz-agent\" — so a sprig image launched with no further configuration would attempt to spawn `goose`, not the bundled buzz-agent, as its agent subprocess."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:197-198"
      - "crates/buzz-acp/src/config.rs:256-257"
  - statement: "crates/buzz-backend-kubernetes/src/env.rs sets `BUZZ_ACP_MCP_COMMAND` unconditionally to the literal string \"buzz-dev-mcp\" for every agent it launches, while `BUZZ_ACP_AGENT_COMMAND` is set only if the launch descriptor's `command` field is non-empty (populated from the agent's own persona/definition, not hardcoded to `buzz-agent`) — so the Kubernetes remote-agent provider explicitly wires sprig's bundled MCP server every time, but wires sprig's bundled agent binary only when a caller's launch descriptor names it."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs:254-267"
  - statement: "docs/remote-agents.md states directly that buzz-backend-kubernetes is the first conforming remote-agent provider and realizes the provider contract as a bare Kubernetes Pod running the sprig image; crates/buzz-backend-kubernetes/src/image.rs independently corroborates this from the consumer side, parsing and defaulting image references to `ghcr.io/block/buzz-sprig@sha256:<digest>`."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:22-24"
      - "crates/buzz-backend-kubernetes/src/image.rs"
  - statement: ".github/workflows/sprig.yml builds and publishes a static-musl multicall binary tarball for x86_64/aarch64 Linux (a rolling `sprig-latest` release on push to `main`, a versioned release on `sprig-v*` tags), and .github/workflows/sprig-image.yml separately builds and publishes the multi-arch container image `ghcr.io/block/buzz-sprig` — two dedicated, sprig-specific CI workflows, distinct from the workspace's general Rust CI."
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig.yml"
      - ".github/workflows/sprig-image.yml"
  - statement: "scripts/test-sprig-image.sh is sprig's representative test: it builds the Docker image and asserts, inside a running container, that every personality name symlinks to `sprig`, that `sprig-entrypoint` execs `buzz-acp` (and never invokes it any other way), and that the git-credential-nostr URL-scoped configuration is wired correctly — crates/sprig/src/main.rs itself contains no `#[test]` functions, so this Docker-contract script is the crate's only representative verification found."
    entry_class: FACT
    evidence:
      - "scripts/test-sprig-image.sh"
      - "crates/sprig/src/main.rs"
  - statement: "The merged corpus node architecture-containers-agent-runtime already documents sprig as one of four crates composing the agent-runtime container (\"a multicall binary bundling all three above into one deploy-anywhere artifact, dispatched on argv0\"), citing crates/sprig/src/main.rs and crates/sprig/Cargo.toml directly."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "At repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3, no `implementation`-typed node exists anywhere in the corpus tree on origin/launchpad (git ls-tree lists only architecture/, schema/, standards/, templates/, AGENTS.md and README.md under launchpad/docs/corpus), so this is the first implementation-reference-shaped node in the corpus; no sibling implementation node for buzz-acp, buzz-agent or buzz-dev-mcp is a valid relationship target yet."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**, at commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "sprig's own source (main.rs, Cargo.toml) contains no logic beyond argv0-based dispatch to the three bundled crates' existing `run()` entry points and its own bare-name usage/version handling — it defines no new business logic, event kinds, HTTP routes or CLI subcommands of its own."
    entry_class: INFERENCE
    evidence:
      - "crates/sprig/src/main.rs"
      - "crates/sprig/Cargo.toml"
    confidence: 0.85
---

# sprig: implementation reference

`crates/sprig` is a Rust multicall binary that statically links `buzz-acp`,
`buzz-agent` and `buzz-dev-mcp` into one compiled executable and dispatches to
whichever of the three (or `buzz-dev-mcp`'s own five additional personality
names) was invoked, resolved purely from the basename of `argv0`. It claims no
protocol or spec of its own to realize; what it realizes is the packaging half
of `docs/remote-agents.md`'s provider contract — the runtime ABI a conforming
remote-agent image must expose — by being the artifact `Dockerfile.sprig`
builds and `buzz-backend-kubernetes` deploys as that image.

## Target

`docs/remote-agents.md` is the closest thing to a governing specification:
it defines the provider protocol between Buzz Desktop (or any launcher) and a
`buzz-backend-<id>` binary, names `buzz-backend-kubernetes` as the first
conforming provider realizing that protocol "as a bare Pod running the sprig
image" (`docs/remote-agents.md:22-24`), and states an image override "MUST
contain the runtime ABI — the `buzz-acp` entrypoint and everything §Entrypoint
and launch ABI requires" (`docs/remote-agents.md:1046-1049`). That document
has no corpus node id at the time this node was written, so no `implements`
edge is declared here (see *Relationships*) — the target is named by its real
repository path, `docs/remote-agents.md`, and by the `sprig-image` and
`sprig-v*` tag matrix `.github/workflows/sprig-image.yml` and
`.github/workflows/sprig.yml` build against.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/sprig/src/main.rs::dispatch` | argv0-based multicall dispatch to `buzz_acp::run()` / `buzz_agent::run()` / fallback `buzz_dev_mcp::run()` | Bare `sprig` invocation (no personality symlink) is a deliberate error path, not a fourth mode. |
| `crates/sprig/Cargo.toml` | Path dependencies on `buzz-acp`, `buzz-agent`, `buzz-dev-mcp`; independent `version` not inheriting the workspace | Confirms sprig adds no dependency of its own beyond the three it bundles. |
| `Cargo.toml` `[profile.sprig]` (root) | The optimized build profile `scripts/build-sprig.sh` and `Dockerfile.sprig` compile against | `inherits = "release"`, `opt-level = "z"`, `lto = "fat"`, `panic = "abort"` — a size/perf-tuned variant of `release`, not a new profile family. |
| `Dockerfile.sprig` | The `ghcr.io/block/buzz-sprig` image `docs/remote-agents.md`'s "Image" section describes | Builds via `cargo build --profile sprig -p sprig`, symlinks all eight personality names, sets up git's `x509`/`gpg.x509.program` for `git-sign-nostr`. |
| `scripts/sprig-entrypoint.sh` | The container's `ENTRYPOINT`, and `docs/remote-agents.md`'s runtime-ABI requirement that an image expose the `buzz-acp` entrypoint | Configures a URL-scoped git credential helper, then `exec buzz-acp "$@"` — PID 1 is always the harness personality. |
| `.github/workflows/sprig.yml` | The standalone static-musl tarball release (`sprig-latest` rolling, `sprig-v*` versioned) | x86_64/aarch64 Linux only — no macOS build in this workflow. |
| `.github/workflows/sprig-image.yml` | The multi-arch `ghcr.io/block/buzz-sprig` container image release | Digest-pinned per-arch manifests merged into one multi-arch manifest, per its own header comment. |
| `crates/buzz-backend-kubernetes/src/env.rs` (consumer, not owned by this crate) | Wires `BUZZ_ACP_MCP_COMMAND=buzz-dev-mcp` unconditionally into every launched agent's environment | Named here because it is the concrete evidence that a real deployment activates one of sprig's three bundled personalities by convention, not by any default baked into sprig itself. |

## Divergences

**The bundled agent is not the default agent.** `buzz-acp`'s own
`BUZZ_ACP_AGENT_COMMAND` CLI argument defaults to `"goose"`
(`crates/buzz-acp/src/config.rs:197-198,256-257`), a separate agent CLI
outside this repository — not `"buzz-agent"`. A sprig image run with no
further configuration would therefore try to spawn `goose` as its agent
subprocess, not the `buzz-agent` crate it bundles. `buzz-backend-kubernetes`
only sets `BUZZ_ACP_AGENT_COMMAND` when a launch descriptor's `command` field
is non-empty (`crates/buzz-backend-kubernetes/src/env.rs:254-259`) — populated
from the agent's own persona/definition, not hardcoded to `buzz-agent`. By
contrast, the same code unconditionally hardcodes
`BUZZ_ACP_MCP_COMMAND=buzz-dev-mcp` (`crates/buzz-backend-kubernetes/src/env.rs:267`).
So of sprig's three bundled personalities, only the MCP server is wired in by
convention at the deployment layer; the harness personality is always active
(the entrypoint execs it directly) and the agent personality is opt-in per
launch, exactly like any other agent command name a caller could name
instead. This was checked directly in `buzz-acp`'s config and
`buzz-backend-kubernetes`'s env-building code, not inferred from sprig's own
source, which has no opinion on the matter at all.

**No other divergence was found** between sprig's own code and
`docs/remote-agents.md`'s stated runtime-ABI requirement (the `buzz-acp`
entrypoint, per `docs/remote-agents.md:1046-1049`) — `scripts/sprig-entrypoint.sh`
execs `buzz-acp` unconditionally, matching the requirement, and
`scripts/test-sprig-image.sh` asserts this directly against the built image.
What was checked: the entrypoint script's exec line, the image's personality
symlinks, and the git-credential wiring the same test script asserts.

## Verification

`scripts/test-sprig-image.sh` is the crate's representative test: a
Docker-contract script (not a Rust `cargo test`) that builds `Dockerfile.sprig`
and, inside the running container, asserts every personality symlink resolves
to `sprig`, that `sprig-entrypoint` contains an `exec buzz-acp` line and no
other invocation shape, and that `BUZZ_RELAY_URL` correctly wires the
git-credential-nostr helper. `crates/sprig/src/main.rs` itself contains no
`#[test]` functions — its dispatch logic is exercised only through this
image-level contract test and, indirectly, through whatever unit/integration
tests `buzz-acp`, `buzz-agent` and `buzz-dev-mcp` carry for the `run()`
functions sprig calls unchanged. `.github/workflows/sprig-image.yml` runs on
`pull_request` (paths-filtered to `Dockerfile.sprig`,
`scripts/sprig-entrypoint.sh`, the workflow file itself, `Cargo.toml`,
`Cargo.lock`, `rust-toolchain.toml`, `crates/**`) as a build-only check with no
push, and `.github/workflows/sprig.yml` builds the tarball on the same
triggers — neither workflow file, as read, was confirmed to invoke
`scripts/test-sprig-image.sh` itself; that script's CI wiring (if any) was not
located and is named under *Scope and omissions* below as unverified.

## Relationships

- part-of: architecture-containers-agent-runtime
- implements: none declared — `docs/remote-agents.md` has no corpus node id yet; see *Target* above.
- references: none declared — no verification/test-strategy corpus node exists yet to cite for the *Verification* section above.

## Scope and omissions

**This node covers** what `crates/sprig` is responsible for (argv0-based
multicall dispatch to three bundled crates, plus its own bare-name usage/error
handling), what it deliberately does not own (any business logic, event kind,
HTTP route, or CLI subcommand — those belong to the crates it dispatches to),
its public entry points (the `sprig` binary and its personality symlinks), its
build/release surface (the dedicated `sprig` Cargo profile and two dedicated
CI workflows), its one representative test, and the deployment-time
divergence between which of its three bundled personalities is wired in by
convention versus which is opt-in.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-acp`'s own ACP harness lifecycle, configuration and agent-pool behavior | `crates/buzz-acp/README.md`; a future `implementation-crates-buzz-acp` node |
| `buzz-agent`'s own LLM-call/tool-call loop and security model | `crates/buzz-agent/README.md`; a future `implementation-crates-buzz-agent` node |
| `buzz-dev-mcp`'s own tool surface and its five additional multicall personality names' individual behavior | `crates/buzz-dev-mcp/src/`; a future `implementation-crates-buzz-dev-mcp` node |
| The agent-runtime container's full responsibility, interfaces and security boundary | `launchpad/docs/corpus/architecture/containers/agent-runtime.md` |
| `docs/remote-agents.md`'s full provider protocol, five invariants and Kubernetes binding | `docs/remote-agents.md` directly (no corpus node yet) |
| `buzz-backend-kubernetes`'s own env-building, image-resolution and reconciliation logic beyond the two facts cited above | Not yet a corpus node |

**Expected but not verified when this node was written:**

- **Whether `scripts/test-sprig-image.sh` is actually invoked by any CI
  workflow.** Both `.github/workflows/sprig.yml` and
  `.github/workflows/sprig-image.yml` were read for their trigger and build
  steps; neither was confirmed (nor denied) to call this script. If it is
  currently run only by hand, that is a verification gap worth its own
  finding, not asserted here as fact either way.
- **Whether any real deployment's persona/definition currently sets
  `agent_command` to `\"buzz-agent\"`** (activating sprig's bundled agent
  rather than `goose` or another external agent CLI) was not checked beyond
  the code path that would allow it; no live configuration was inspected.
- **`scripts/build-sprig.sh`'s cross-compilation (`USE_CROSS`) and non-Linux
  target behavior** was read only for its documented usage header, not
  exercised.
