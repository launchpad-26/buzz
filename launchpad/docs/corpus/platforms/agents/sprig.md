---
id: platforms-agents-sprig
type: implementation
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
  - statement: "crates/sprig/Cargo.toml describes the crate as 'All-in-one Buzz ACP harness, agent, and developer MCP', builds one binary (sprig, src/main.rs), declares no [lib] target, and lists exactly three path dependencies -- buzz-acp, buzz-agent, buzz-dev-mcp -- with no external crates of its own."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
  - statement: "crates/sprig/src/main.rs is 53 lines and carries no crate-level `//!` doc comment. Its entire logic is `dispatch()`: it reads argv0's basename, lowercases it, and matches on 'buzz-acp' -> buzz_acp::run(), 'buzz-agent' -> buzz_agent::run(), 'sprig' -> handling -V/--version, -h/--help/no-args, or an unknown-option error, with every other name (including the documented rg/tree/buzz/git-credential-nostr/git-sign-nostr multicall names) falling through to buzz_dev_mcp::run()."
    entry_class: FACT
    evidence:
      - "crates/sprig/src/main.rs"
  - statement: "main.rs's print_usage() states the supported personality names verbatim: 'buzz-acp ACP harness', 'buzz-agent ACP-compliant agent', 'buzz-dev-mcp Developer MCP server', plus 'Developer MCP helper names are also supported: rg, tree, buzz, git-credential-nostr, git-sign-nostr', and shows the installer pattern `ln -s sprig buzz-acp` (and so on for the other two primary personalities)."
    entry_class: FACT
    evidence:
      - "crates/sprig/src/main.rs"
  - statement: "The root Cargo.toml declares crates/sprig as a workspace member and defines a dedicated [profile.sprig] (inherits = \"release\", opt-level = \"z\", lto = \"fat\", codegen-units = 1, panic = \"abort\", strip = true), with a comment stating this profile exists because Sprig is distributed over the network and installed on fresh hosts, so binary size matters more than compile speed, and is kept separate so desktop/dev release builds do not inherit it."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "Dockerfile.sprig builds crates/sprig with `cargo build --locked --profile sprig -p sprig`, strips the binary, copies it to /usr/local/bin/sprig in an Alpine 3.22 runtime image, and symlinks buzz-acp, buzz-agent, buzz-dev-mcp, rg, tree, buzz, git-credential-nostr and git-sign-nostr to it -- the same name set main.rs's dispatch() and print_usage() document. It also configures git to use git-sign-nostr for commit/tag signing system-wide and sets ENTRYPOINT to /usr/local/bin/sprig-entrypoint."
    entry_class: FACT
    evidence:
      - "Dockerfile.sprig"
  - statement: "scripts/sprig-entrypoint.sh optionally configures a URL-scoped git credential helper (git-credential-nostr) against BUZZ_RELAY_URL when set, then unconditionally execs `buzz-acp \"$@\"` -- so the container's default runtime personality, reached via the sprig-built symlink, is the ACP harness, not sprig's own bare CLI."
    entry_class: FACT
    evidence:
      - "scripts/sprig-entrypoint.sh"
  - statement: ".github/workflows/sprig.yml builds a static-musl sprig binary for x86_64-unknown-linux-musl and aarch64-unknown-linux-musl via `cross` and `scripts/build-sprig.sh`, publishing a rolling `sprig-latest` GitHub release on push to main and a versioned release on `sprig-v*` tags; it runs no `cargo test` step, only build/package/publish."
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig.yml"
  - statement: ".github/workflows/sprig-image.yml builds and publishes the multi-arch container image ghcr.io/block/buzz-sprig from Dockerfile.sprig, per-architecture on native runners merged into one manifest, triggered on push to main (paths-filtered), sprig-v* tags, and pull_request (build-only, no push)."
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig-image.yml"
  - statement: "crates/buzz-backend-kubernetes/src/image.rs parses and validates references to the published image, including literal ghcr.io/block/buzz-sprig test fixtures in its own unit tests, making buzz-backend-kubernetes a real internal consumer of the artifact sprig-image.yml publishes -- reached through the built image reference, not through a Cargo.toml path dependency on the sprig crate itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/image.rs"
  - statement: "No crate in this repository's workspace declares a path dependency on crates/sprig; sprig is a top-level bundling binary with no internal reverse dependents at the Cargo level."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
      - "grep_repo(pattern='path = \"\\.\\./sprig\"', scope='crates/*/Cargo.toml') -> no matches"
  - statement: "The already-merged architecture-containers-agent-runtime node describes sprig as 'a multicall Rust binary whose only dependencies are buzz-acp, buzz-agent and buzz-dev-mcp; it dispatches to one of the three based on the argv0 name it was invoked as ... packaging the harness, the agent and the developer MCP server as one deploy-anywhere artifact', names its Technology table row, cites both sprig.yml and sprig-image.yml as its release pipelines, and states that none of the agent-runtime crates (including sprig) depend on buzz-db or buzz-search -- the runtime's only path to Buzz's durable data is the relay's Nostr surface, never a direct database connection."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "launchpad/docs/corpus/templates/component.md is the merged template for a standalone software-component corpus node; it directs authors to set `type: implementation`, requires Responsibility/Public interface/Dependencies/Boundary/Relationships/Scope-and-omissions sections, and states a `part-of` relationship toward an architecture-component node's building-block table is optional, never required for the node's own validity."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
  - statement: "Because crates/sprig has no `lib.rs` and exports no `pub` Rust items at all -- its only artifact is the `sprig` binary -- this node's Public interface section documents the process-level argv0-dispatch contract and CLI surface (personality names, -V/-h handling) as the component's real external interface, rather than a table of exported functions/types/traits as the sibling buzz-agent node's Public interface table does."
    entry_class: INFERENCE
    evidence:
      - "crates/sprig/src/main.rs"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.75
  - statement: "No architecture-component instance node (as distinct from the architecture-component template) exists in this corpus decomposing the agent-runtime container with a building-block table naming sprig as a row; the closest existing, merged, resolvable target for this node's part-of relationship is architecture-containers-agent-runtime itself, whose own Technology table already lists sprig as one of the container's constituent crates -- the same reasoning the in-flight platforms-agents-buzz-agent sibling node applies to buzz-agent."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
      - "launchpad/docs/corpus/templates/architecture-component.md"
    confidence: 0.65
  - statement: "sprig.yml runs no test step of its own, and crates/sprig has no tests/ directory, so sprig's argv0-matching dispatch logic itself has no dedicated automated test; the behavior each personality dispatches to (buzz-acp, buzz-agent, buzz-dev-mcp) is exercised by those crates' own test suites, not by any test that invokes the sprig binary under its personality names."
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig.yml"
      - "find(crates/sprig, type=dir) -> crates/sprig, crates/sprig/src only"
relationships:
  - type: part-of
    target: architecture-containers-agent-runtime
---

# Component: sprig

`sprig` (crate `crates/sprig`, binary `sprig`, no library target) is a
multicall Rust binary bundling `buzz-acp`, `buzz-agent` and `buzz-dev-mcp`
into one deploy-anywhere artifact. This node documents it as one standalone
software component per
[`templates/component.md`](../../templates/component.md) — its
responsibility, its process-level public interface, and its real dependency
edges — one level below the agent-runtime container it lives inside
([`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md)).
See [`node.schema.json`](../../schema/node.schema.json) for the front-matter
contract this satisfies and [`AGENTS.md`](../../AGENTS.md) for how this node
was authored and checked.

## Responsibility

`crates/sprig/src/main.rs` carries no crate-level `//!` doc comment, so this
responsibility statement is grounded in `Cargo.toml`'s `description` field —
*"All-in-one Buzz ACP harness, agent, and developer MCP"* — and in
`main.rs` itself: the crate's entire logic is `dispatch()`, which reads the
process's own `argv0` basename and routes to `buzz_acp::run()`,
`buzz_agent::run()`, or (falling through for any unrecognized name, including
the documented `rg`/`tree`/`buzz`/`git-credential-nostr`/`git-sign-nostr`
helper names) `buzz_dev_mcp::run()`. Invoked directly as `sprig`, it handles
only `-V`/`--version` and `-h`/`--help`, and otherwise errors, directing the
caller to invoke it through a personality symlink instead. `sprig` has no
`[lib]` target and exports no public Rust API — its only artifact is the
binary.

## Public interface

Because this component has no library crate, its real public interface is
the personality-dispatch contract, not a table of exported Rust items.

| Surface | Kind | Contract | Evidence |
|---|---|---|---|
| `buzz-acp` (argv0 or symlink name) | process personality | Dispatches to `buzz_acp::run()` — the ACP harness. | `crates/sprig/src/main.rs` |
| `buzz-agent` (argv0 or symlink name) | process personality | Dispatches to `buzz_agent::run()` — the ACP-compliant agent. | `crates/sprig/src/main.rs` |
| `rg`, `tree`, `buzz`, `git-credential-nostr`, `git-sign-nostr` (argv0 or symlink name) | process personality | Falls through, along with any other unrecognized name, to `buzz_dev_mcp::run()`, which handles these specific multicall names itself. | `crates/sprig/src/main.rs` |
| `sprig -V` / `--version` | CLI flag (invoked bare, not via symlink) | Prints `sprig <CARGO_PKG_VERSION>`. | `crates/sprig/src/main.rs` |
| `sprig -h` / `--help` / no args | CLI flag (invoked bare) | Prints usage naming all supported personalities; exits with an error if invoked with no arguments at all. | `crates/sprig/src/main.rs` |
| `sprig <unrecognized-option>` (invoked bare) | CLI flag | Prints usage and errors, naming the unrecognized value. | `crates/sprig/src/main.rs` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-acp` | Path dependency; provides the `buzz_acp::run()` personality — "ACP harness that bridges Buzz events to AI agents" per its own `Cargo.toml` description. | `crates/sprig/Cargo.toml` |
| `buzz-agent` | Path dependency; provides the `buzz_agent::run()` personality — "Minimal, unbreakable ACP-compliant agent. Non-streaming. Tool-calls-as-output." per its own `Cargo.toml` description. | `crates/sprig/Cargo.toml` |
| `buzz-dev-mcp` | Path dependency; provides the `buzz_dev_mcp::run()` personality (developer MCP server, and the fallback target for every unrecognized multicall name) — "Developer MCP server — shell + file-edit tools" per `CLAUDE.md`'s own crate table. | `crates/sprig/Cargo.toml`, `CLAUDE.md` |
| *(no external crate)* | `sprig`'s `[dependencies]` table names only the three path dependencies above — no external crate is a direct dependency of `sprig` itself (each wrapped crate pulls its own externals). | `crates/sprig/Cargo.toml` |

**Depended on by** (these require this component):

*(none, at the Cargo dependency-graph level)* — no crate in this workspace
declares a path dependency on `crates/sprig`; it is a top-level bundling
binary, not a library other Rust code links against.

| Consumer | Why | Evidence |
|---|---|---|
| `Dockerfile.sprig` | Builds `sprig` under the dedicated `[profile.sprig]` and symlinks every personality name to the resulting binary, producing the `ghcr.io/block/buzz-sprig` runtime image. | `Dockerfile.sprig`, `Cargo.toml` (`[profile.sprig]`) |
| `scripts/sprig-entrypoint.sh` | The container's `ENTRYPOINT`; always execs `buzz-acp` (one of `sprig`'s personalities) as the default runtime behavior. | `scripts/sprig-entrypoint.sh` |
| `crates/buzz-backend-kubernetes` | Parses and validates references to the published `ghcr.io/block/buzz-sprig` image (not a Cargo dependency on the `sprig` crate — a consumer of the built artifact). | `crates/buzz-backend-kubernetes/src/image.rs` |

## Boundary

This node does not describe:
- **The agent-runtime container's own decomposition, interfaces, deployment or
  security summary** — that is
  [`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md)'s
  subject; this node is one row of deeper detail it points at, not a
  replacement for it.
- **The internal responsibility, public interface or dependencies of
  `buzz-acp`, `buzz-agent`, or `buzz-dev-mcp`** — each is (or will be) its
  own component node; this node covers only the multicall binary that bundles
  them, not what each personality does once dispatched to.
- **How this crate satisfies any spec, decision or contract** (ACP protocol
  conformance, etc.) — that traceability question belongs to an
  `implementation-reference` node, per
  [`templates/component.md`](../../templates/component.md)'s own boundary,
  and none has been authored for this crate.
- **The release pipelines' or container image's own internal steps in full**
  (matrix targets, signing, manifest merging) — `.github/workflows/sprig.yml`
  and `.github/workflows/sprig-image.yml` already cover this, and this node
  cites them rather than restating their steps.
- **`docs/remote-agents.md`'s remote-agent provider contract, or the
  Kubernetes backend's in-pod narrowing of sprig's dev-MCP shim** — that
  belongs to `buzz-backend-kubernetes`'s own subject matter, cited above only
  as evidence of a real image consumer.

## Relationships

- `part-of`: [`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md)
  — `sprig` is one of the crates that container node's own Technology table
  names as a constituent of the agent-runtime container. No dedicated
  `architecture-component` instance node exists yet for this container (only
  the template does); this node's own `INFERENCE` above records that the
  container node's Technology table is the closest existing, merged,
  resolvable target for the containment relationship
  [`templates/component.md`](../../templates/component.md) describes.

## Scope and omissions

**This node covers** `sprig`'s responsibility as a multicall binary, its
process-level public interface (argv0 personality dispatch plus its own bare
CLI flags — there is no exported Rust API to table), its real dependency
edges in both directions (cited to `Cargo.toml` for the build-time direction,
and to `Dockerfile.sprig`/`scripts/sprig-entrypoint.sh`/
`buzz-backend-kubernetes` for real consumers of the built artifact, since
nothing in this workspace depends on it as a library), and its boundary
against the container-level node and against the three components it bundles.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The agent-runtime container's full responsibility, interfaces and deployment implications | [`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md) |
| `buzz-acp`, `buzz-agent`, `buzz-dev-mcp`'s own responsibility, interface and dependencies | Their own component nodes (in progress as issues #1229, #1230, #1231) |
| The Kubernetes remote-agent provider's image-reference parsing, pod lifecycle, and in-pod narrowing | `crates/buzz-backend-kubernetes`, `docs/remote-agents.md` |
| The release/publish pipelines' full step-by-step behavior | `.github/workflows/sprig.yml`, `.github/workflows/sprig-image.yml` |
| How this crate's behavior satisfies the ACP specification as a traceability artifact | Not yet authored (`implementation-reference` template exists; no instance for this crate) |

**Expected but not verified when this node was written:**

- **`sprig`'s own argv0-dispatch logic has no dedicated automated test.**
  `.github/workflows/sprig.yml` runs no `cargo test` step, and `crates/sprig`
  has no `tests/` directory. The behavior each personality dispatches to is
  covered by `buzz-acp`, `buzz-agent` and `buzz-dev-mcp`'s own test suites,
  not by any test that invokes the `sprig` binary itself under its
  personality names or symlinks. This is stated as a gap, not papered over.
- **This is one of the first nodes authored from `templates/component.md`
  for a binary-only crate with no `lib.rs` and no exported Rust API.**
  Whether the Public interface section's process-dispatch framing (rather
  than an exported-item table) holds up as a pattern for other binary-only
  crates in this repository was not tested beyond this one instance.
- **Whether any consumer outside this repository's own workspace pulls the
  published `sprig` binary or `ghcr.io/block/buzz-sprig` image was not
  checked** — only this repository's own `Cargo.toml` files and
  `buzz-backend-kubernetes` source were searched for consumers.
