---
id: architecture-containers-desktop
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The desktop container is a Tauri 2 application: a Rust backend crate (lib name buzz_lib) paired with a React 19 + Vite frontend, per the project's own contributor guide."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
      - "desktop/package.json"
      - "CLAUDE.md"
  - statement: "The desktop backend links buzz-core, buzz-persona, buzz-sdk, buzz-agent and buzz-voice as direct Rust path dependencies compiled into the same binary, not consumed over a network boundary."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The desktop crate is deliberately excluded from the repository root Cargo workspace (its own [workspace] table only lists a local buzz-terminal path member), so `cargo test` at repo root does not exercise it; it is tested via its own manifest path."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
      - "CLAUDE.md"
  - statement: "The app's bundle identifier is xyz.block.buzz.app, and it registers a `buzz://` OS-level deep-link scheme it can be launched or focused from."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
  - statement: "The desktop app resolves the relay WebSocket URL with precedence workspace-configured override, then BUZZ_RELAY_URL env var, then a build-time constant, then a ws://localhost:3000 default -- and the same precedence, translated to an HTTP base URL, governs the relay's REST surface."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/relay.rs"
  - statement: "The desktop app bundles and can spawn five external binaries as managed subprocesses -- buzz-acp, buzz-agent, buzz-backend-kubernetes, buzz-dev-mcp, git-credential-nostr -- plus the buzz CLI, all listed as externalBin in the Tauri bundle config."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
  - statement: "When the desktop app spawns a managed agent's process, it injects that agent's own nsec into the child's BUZZ_PRIVATE_KEY environment variable, giving each managed agent its own signing identity distinct from the human owner's."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs"
  - statement: "A reserved-keys list blocks user-supplied per-agent environment configuration from overwriting BUZZ_PRIVATE_KEY (and sibling identity/relay vars) at spawn time, so a misconfigured or malicious custom env cannot redirect an agent's identity or relay."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs"
  - statement: "The human owner's Nostr identity key is held in memory as an AppState field and is durably persisted through one of four backends -- OS system keyring (default, via the `keyring` crate on macOS/Linux/Windows), a local 0600-permission file fallback, an environment-variable-only mode, or fully ephemeral -- tracked by an explicit IdentityStorage enum."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs"
      - "desktop/src-tauri/src/identity_storage.rs"
      - "desktop/src-tauri/src/secret_store.rs"
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The desktop app runs a localhost-only HTTP proxy (axum, spawned at startup on an OS-assigned port) that fetches authenticated relay media on the frontend's behalf; it rejects any request whose Origin header is neither empty nor the Tauri webview's own origin, and caps buffered response size to defend against unbounded memory use."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/media_proxy.rs"
  - statement: "A second, no-redirect HTTP client (media_fetch_client, distinct from the app's general-purpose http_client) is used specifically for authenticated relay media fetches, because the general client's default redirect-following would forward a minted media Authorization header to a 3xx target outside the validated relay origin -- a redirect-hop SSRF the dedicated client closes by treating any 3xx as a non-success response."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs"
  - statement: "The webview's Content-Security-Policy restricts script-src to self plus wasm-unsafe-eval and one pinned CDN origin, and scopes connect-src/img-src/media-src to self, the Tauri IPC origin, the app's own buzz-media: custom URI scheme, and generic https/http/ws/wss -- the last group because the relay URL is operator- and workspace-configurable rather than fixed at build time."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
  - statement: "Managed-agent and persona/team state written locally is drained to the relay by a single dedicated flush loop started at app setup, which polls a pending_sync-tagged local store every 30 seconds and is skipped entirely while the app is in identity-recovery mode, so writes are never published under an ephemeral or lost identity."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs"
  - statement: "The desktop app maintains a local data directory (the \"nest\", ~/.buzz or ~/.buzz-dev for dev builds) created at startup before managed agents are restored, used as the default agent working directory and as the root for locally cloned/synced project repositories."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs"
      - "desktop/src-tauri/src/managed_agents/mod.rs"
  - statement: "The desktop app embeds a PTY-backed terminal subsystem (the portable-pty crate, exposed via terminal_attach/terminal_input/etc. Tauri commands) used for project and agent-recovery terminal sessions opened from the UI."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
      - "desktop/src-tauri/src/lib.rs"
  - statement: "An optional mesh-llm Cargo feature (off by default in this OSS checkout's externalBin/default feature set, gated behind dep:iroh and the Mesh-LLM SDK crates) adds a peer-to-peer shared-compute coordinator that starts at app setup when compiled in; the default feature set is only system-keyring."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
      - "desktop/src-tauri/src/lib.rs"
  - statement: "Desktop is released through its own independent lane -- `just release-desktop <version>` produces an immutable candidate PR, and a `desktop-v<version>` tag is what the squareup/buzz-releases Buildkite pipeline builds into signed/notarized macOS, unsigned Windows, and Linux artifacts, separate from the relay's release lane."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
      - "CLAUDE.md"
  - statement: "No relationships to other corpus nodes are declared because, at this task's merge base (origin/launchpad), no other `architecture` node exists yet for this document to point at -- not because none is warranted; the merged corpus tree was enumerated before writing this node, per the corpus AGENTS.md's explicit warning against copying that justification forward unchecked."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
---

# Container: Desktop app

## Responsibility

The desktop container is Buzz's native cross-platform client: a **Tauri 2**
shell wrapping a **React 19 + Vite** UI over a **Rust** backend crate
(`buzz_lib`). It is the primary surface through which a human owner reads
and writes channel messages, manages their Nostr identity, and — distinctly
from the web and mobile clients — **launches, configures and supervises
locally-running AI agent processes** against a Buzz community.

## Technology and ownership boundary

- **Frontend**: React 19, Vite, Tailwind, organized under
  `desktop/src/features/`. Communicates with the Rust backend exclusively
  through Tauri's IPC (`invoke_handler` commands) and Tauri events — it
  never talks to the relay directly over the network.
- **Backend**: a Rust crate (`desktop/src-tauri/`, package `buzz-desktop`,
  lib name `buzz_lib`) built on `tauri = "2"`. It statically links
  `buzz-core`, `buzz-persona`, `buzz-sdk`, `buzz-agent` and `buzz-voice` as
  path dependencies — these are compiled into the desktop binary itself,
  not called as separate services.
- **Ownership boundary**: this crate is excluded from the repository's root
  Cargo workspace by its own nested `[workspace]` table (only a local
  `buzz-terminal` path crate is a member), so root-level `cargo test`/`cargo
  check --workspace` never exercises it. It is built and tested through its
  own manifest path (`cargo test --manifest-path desktop/src-tauri/Cargo.toml`),
  and its release lane, versioning and build pipeline are independent of the
  relay's (see *Deployment* below).

## Inbound and outbound interfaces

**Inbound (into the desktop process):**
- OS deep links on the `buzz://` scheme (registered via
  `tauri-plugin-deep-link`), used for community, entity and navigation
  targets.
- Local IPC from its own webview only — the Tauri command surface in
  `desktop/src-tauri/src/lib.rs`'s `invoke_handler!` is not reachable from
  outside the app's own frontend.
- A localhost-bound `buzz-media:` custom URI scheme handler and a localhost
  HTTP media proxy (see *Data and security implications*), both scoped to
  the app's own webview origin.

**Outbound (from the desktop process):**
- **Relay** (`buzz-relay`), the container this app is a client of: NIP-42
  WebSocket connection plus the relay's narrow HTTP surface (`/events`,
  `/query`, media, git smart HTTP, workflow webhooks), resolved through
  `relay.rs`'s override chain (workspace override → `BUZZ_RELAY_URL` →
  build-time default → `ws://localhost:3000`).
- **Managed agent subprocesses**: the app spawns and supervises the bundled
  `buzz-acp`, `buzz-agent` and `buzz-dev-mcp` binaries (and optionally
  `buzz-backend-kubernetes` for remote compute backends) as child processes,
  injecting each agent's own relay auth and identity via environment
  variables — see `crates/buzz-acp`, `crates/buzz-agent` and
  `crates/buzz-dev-mcp` for what those processes do once spawned.
- **`git-credential-nostr`**: bundled and installed as a git credential
  helper for project repositories cloned/managed under the app's local
  "nest" directory, so git push/fetch against the relay's git smart HTTP
  surface authenticates with the same Nostr identity.
- **OS keychain / Secret Service** (via the `keyring` crate, feature
  `system-keyring`, on by default) for durable private-key storage, with a
  local `0600` file as the non-keyring fallback.
- **Local filesystem**: the "nest" directory (`~/.buzz`, or `~/.buzz-dev`
  for dev builds) as the default working directory for managed agents and
  locally cloned project repositories.
- Optionally, when built with the `mesh-llm` Cargo feature (not part of
  this checkout's default feature set), a peer-to-peer shared-compute
  network via `iroh` and the Mesh-LLM SDK.

## Data and security implications

- The human owner's signing key lives in memory as a `nostr::Keys` value on
  `AppState` and is durably backed by one of four states tracked by an
  explicit `IdentityStorage` enum: OS keyring (default), a `0600` local
  file, an environment-variable-sourced key, or fully ephemeral (recovery
  paths). See `identity_storage.rs` and `secret_store.rs`.
- Each managed agent gets its **own** nsec, injected into its subprocess
  environment as `BUZZ_PRIVATE_KEY` at spawn time — agents do not share the
  owner's key. A reserved-environment-keys check blocks user-supplied
  per-agent env configuration from clobbering that (or the relay/auth
  vars), closing an identity- or relay-redirection vector through the
  per-agent env config surface.
- Relay media fetches that carry a minted auth header go through a
  dedicated **no-redirect** HTTP client, distinct from the app's
  general-purpose client, specifically to prevent a redirect response from
  forwarding that header outside the validated relay origin.
- The local media proxy and the `buzz-media:` scheme handler are
  origin-checked against the app's own webview origin and cap buffered
  response size, so neither is a general-purpose local HTTP proxy reachable
  by arbitrary local processes with knowledge of the port.
- The CSP's `connect-src`/`img-src`/`media-src` allow generic `https:` /
  `http:` / `ws:` / `wss:` (in addition to the app's own origins) because
  the relay URL — and therefore the community a given install talks to —
  is workspace-configurable rather than fixed at build time; this is a
  wider network allowance than a single-origin app would need, traded for
  multi-community support.
- Locally-buffered writes (managed agent, persona and team records) are
  drained to the relay by one dedicated flush loop, and that loop is
  suppressed entirely while the app is in identity-recovery mode, so
  pending local writes are never published under a recovery-mode ephemeral
  identity.

## Deployment implications

Desktop has its own release lane, independent of the relay's: `just
release-desktop <version>` produces an immutable candidate PR, and pushing
a `desktop-v<version>` tag is what the `squareup/buzz-releases` Buildkite
pipeline (external to this OSS repo) builds into signed/notarized macOS,
unsigned Windows, and Linux installers, plus a rolling
`buzz-desktop-latest` auto-update release. See `RELEASING.md` for the full
procedure and `CLAUDE.md`'s ecosystem table for how this repo's source
relates to that build pipeline.

## Implementation paths

- `desktop/src-tauri/src/lib.rs` — Tauri builder: plugins, managed state,
  the full `invoke_handler!` command surface, and app-lifecycle setup.
- `desktop/src-tauri/src/relay.rs` — relay URL/override resolution.
- `desktop/src-tauri/src/app_state.rs` — the process-lifetime `AppState`
  (identity, HTTP clients, managed-agent process table, huddle state).
- `desktop/src-tauri/src/identity_storage.rs`,
  `desktop/src-tauri/src/secret_store.rs` — identity key persistence
  backends.
- `desktop/src-tauri/src/managed_agents/` — spawning, supervising,
  reconciling and persisting managed agent subprocesses (`runtime.rs`,
  `reserved_env_keys.rs`, `agent_env.rs`, `storage.rs`).
- `desktop/src-tauri/src/media_proxy.rs` — the localhost media proxy.
- `desktop/src-tauri/src/terminal_runtime.rs` — the embedded PTY terminal.
- `desktop/src-tauri/tauri.conf.json` — bundle identity, CSP, deep-link
  scheme, bundled external binaries.
- `desktop/src-tauri/Cargo.toml` — the crate's dependency and feature
  boundary.
- `desktop/src/` — the React 19 frontend; see its own
  `desktop/src/features/` tree rather than duplicated here.

This node deliberately does not restate the implementation detail housed
at those paths — see them directly for command signatures, spawn
sequencing, or frontend component structure.

## Scope and omissions

**Covers**: the desktop app as one architectural container — its
responsibility, technology boundary, interfaces to the relay and to
spawned agent processes, and the deployment/data/security implications of
that boundary.

**Does not cover, and these are gaps rather than silence**:
- The internal design of `buzz-acp`, `buzz-agent`, `buzz-dev-mcp` or
  `buzz-voice` themselves — each is its own container/component and, per
  this corpus's one-idea-per-node rule, belongs in its own node.
- The huddle (voice channel) audio pipeline's internal design — it was
  read only far enough to confirm it is part of this container's outbound
  surface (relay-connected, `desktop/src-tauri/src/huddle/`), not deep
  enough to make claims about its protocol or codec choices.
- The React frontend's internal feature/component architecture — only its
  existence and IPC-only relationship to the backend is claimed here.
- The `mesh-llm` feature's shared-compute protocol — confirmed to exist as
  an optional, non-default Cargo feature; its network protocol and trust
  model were not inspected for this node.
- Whether any agent harness has been tested treating this repository's own
  `AGENTS.md`/`CLAUDE.md` files as *desktop-runtime* instructions is
  unrelated to this node's subject and out of scope here.

Per this task's category tail, this document links implementation paths
without duplicating their reference detail, and links deployment (this
node's *Deployment implications*), data and security implications
(*Data and security implications*) directly rather than in a separate
node, since no dedicated deployment/security node exists yet in the merged
corpus for this container to point at instead.
