---
id: platforms-agents-kubernetes-backend
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
  - statement: "launchpad/docs/corpus/templates/component.md is a merged corpus template whose subject is one standalone software component (a crate, or a cohesive module inside one) and which directs an author to set type: implementation for such a node, since node.schema.json's type enum has no dedicated component member."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "crates/buzz-backend-kubernetes/src/main.rs opens with a crate-level doc comment describing the crate as 'Kubernetes backend provider for Buzz remote agents (spec docs/remote-agents.md)', stating its process contract as 'read exactly one JSON request from stdin, write exactly one JSON response to stdout, exit', with the exit code carrying 'exactly one bit' and every distinguishable outcome living inside the response's ok field."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs"
  - statement: "crates/buzz-backend-kubernetes/Cargo.toml declares only a [[bin]] target (name buzz-backend-kubernetes, path src/main.rs) and no [lib] section, so nothing in this repository can depend on this crate as a Rust library; any other component that uses it does so by invoking the built binary as a subprocess."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/Cargo.toml"
  - statement: "The crate has no crates/buzz-backend-kubernetes/README.md; the only README under its directory is tests/fixtures/provider-wire/README.md, which documents the wire-fixture test files rather than the crate's own install/usage."
    entry_class: FACT
    evidence:
      - "find_buzz_backend_kubernetes_readmes() -> only crates/buzz-backend-kubernetes/tests/fixtures/provider-wire/README.md exists; no crates/buzz-backend-kubernetes/README.md, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "docs/remote-agents.md is a 1779-line formal specification with a dedicated section '## The Kubernetes Binding (buzz-backend-kubernetes)' (lines 991-1410) that names this crate explicitly as 'The first conforming provider: a Rust crate in block/buzz, distributed as a standalone binary', and states 'Everything above is the contract; this section is its realization.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's Provider Protocol section (lines 305-990) specifies the generic contract every provider (including this one) must implement: discovery of buzz-backend-<id> executables, one-process-per-operation stdin/stdout invocation with bounded reads and a 10s info / 600s deploy timeout, an info operation returning protocol_version and a JSON config_schema, and a deploy operation."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "crates/buzz-backend-kubernetes/src/wire.rs defines the crate's wire contract: a Request enum (Info, Deploy(DeployRequest)) deserialized from the stdin JSON object, a Response enum (Info, Deploy, Error) serialized flat to stdout so the desktop can read ok/error/agent_id off the top level, PROTOCOL_VERSION as a const u32, and DeployRequest/AgentPayload/LaunchBlock structs typing only the fields this binding consumes."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/wire.rs"
  - statement: "crates/buzz-backend-kubernetes/src/main.rs's respond function parses stdin as raw JSON first, calls refuse_relay_mesh against the raw value before typed deserialization, then dispatches Request::Info to Response::info() (no cluster contact) and Request::Deploy to an async deploy_agent run on a fresh current-thread Tokio runtime, returning Response::deployed(agent_id) or Response::error(message)."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs"
  - statement: "main.rs's refuse_relay_mesh function reads agent.provider from the raw wire JSON and, if it equals \"relay-mesh\" after trimming, refuses the deploy with an explicit message; its own doc comment states this is the spec's backstop because a mesh agent runs on the relay's compute and deploying it as a pod would create a second, contending consumer of the same agent identity."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs"
  - statement: "main.rs's deploy_agent function runs one deploy to a terminal outcome in this order: parse provider_config via config::parse, derive an AgentIdentity from the payload's nsec via naming::AgentIdentity::from_nsec (a malformed key is refused before any cluster contact), build the pod environment via env::build_env, connect a kube-rs Client via client::connect(cfg.context), construct a cluster::Cluster, and call reconcile::deploy."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs"
  - statement: "crates/buzz-backend-kubernetes/src/classify.rs implements the deploy state machine described in docs/remote-agents.md's Deploy State Machine section as a pure function (classify), mapping a verified observation plus the desired create intent to one Action, with no I/O, so its own doc comment states every row of the spec's table is a unit test with no cluster."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/classify.rs"
      - "docs/remote-agents.md"
  - statement: "crates/buzz-backend-kubernetes/src/reconcile.rs implements the deploy loop that executes classify's actions against a Substrate trait and re-enters; its own doc comment states the Substrate is a trait specifically so the conformance tests can drive the same reconciler that ships, with a fake cluster and fake clock, rather than a test-only reimplementation."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/reconcile.rs"
  - statement: "crates/buzz-backend-kubernetes/src/cluster.rs implements the Substrate trait against a real kube-rs Client, and discriminates two distinct HTTP-409 outcomes (Status.reason AlreadyExists vs Conflict) rather than branching on the HTTP status code alone, because the two reasons mean different things to the reconciler (a lost create race vs a stale delete precondition)."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/cluster.rs"
  - statement: "crates/buzz-backend-kubernetes/src/naming.rs derives an AgentIdentity from the agent's nsec and exposes the deterministic names/labels/annotations the rest of the crate uses for reconciliation and GC: a pod name (buzz-agent-<first-12-hex-of-pubkey>, also the returned agent_id), a truncated 32-hex label value for the selector, a full-64-hex annotation used as a load-bearing identity check, a management-marker label pair (app.kubernetes.io/managed-by, a binding-version label), and a fresh per-attempt Secret name (buzz-agent-<first-12-hex>-<generation>)."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/naming.rs"
  - statement: "crates/buzz-backend-kubernetes/src/pod.rs builds the per-attempt Kubernetes Secret and Pod objects, applying hardening defaults (automountServiceAccountToken: false, runAsNonRoot with a fixed UID/GID, allowPrivilegeEscalation: false, all capabilities dropped, seccompProfile RuntimeDefault), a bare Pod with no controller, an emptyDir workspace mounted as HOME, and a required (non-optional) envFrom reference to the attempt's Secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/pod.rs"
  - statement: "crates/buzz-backend-kubernetes/src/intent.rs computes a Fingerprint (a hex SHA-256 digest) over an IntentTemplate describing only the non-secret, scheduling-relevant pod shape (namespace, normalized image reference, resource requests/limits, service account, restart policy, grace period, sorted env key names, workspace path, UID/GID) so that two create attempts of the same configuration produce the same fingerprint regardless of their distinct per-attempt generation token, while Secret values and the generation are structurally excluded from the type."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/intent.rs"
  - statement: "crates/buzz-backend-kubernetes/src/gc.rs implements a preflight garbage-collection pass (plan) that collects terminated, marker-verified pods and their referenced Secrets plus age-eligible orphan Secrets, gated by an ORPHAN_SECRET_MIN_AGE_SECS of twice the 600-second deploy operation deadline, and requires the age comparison to use the apiserver's own HTTP Date header rather than the provider's local clock, skipping the orphan sweep entirely if that header is absent or unparseable."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/gc.rs"
  - statement: "crates/buzz-backend-kubernetes/src/image.rs parses and normalizes a user- or default-supplied image reference into a digest-qualified ImageRef, rejecting every tag-only reference (not only :latest) because a movable tag is unsafe to run with an nsec-holding pod, and normalizing a tag+digest form by dropping the tag so two spellings of the same bytes produce one fingerprint input."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/image.rs"
  - statement: "crates/buzz-backend-kubernetes/src/config.rs parses the deploy request's provider_config JSON into a ProviderConfig (context, namespace, image, resources, inactivity_seconds, service_account), exposes config_schema() driving the desktop's dynamic config form including a freshly generated buzz-agents-<rand6> namespace default per info call, and refuses inactivity_seconds: 0 (the indefinite-lifetime opt-in) because it would require an OnFailure restart policy not yet safe to ship."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs"
  - statement: "crates/buzz-backend-kubernetes/src/client.rs builds the kube-rs Client for the selected kubeconfig context, and first prepends /opt/homebrew/bin, /usr/local/bin, and ~/.local/bin to the process PATH because Block's kubeconfigs near-universally authenticate through exec credential plugins (aws eks get-token, gke-gcloud-auth-plugin) that resolve via PATH, and a Finder-launched desktop's inherited PATH is otherwise too minimal to find them."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/client.rs"
  - statement: "crates/buzz-backend-kubernetes/Cargo.toml declares runtime dependencies on kube, k8s-openapi, nostr, tokio, serde, serde_json, sha2, hex, rand, chrono, http, http-body-util, and an explicit rustls dependency (ring provider, default-features = false) needed to install a process-level TLS CryptoProvider at startup, with a code comment explaining that the release build's unified cargo invocation across sidecars otherwise leaves rustls unable to auto-select one."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/Cargo.toml"
  - statement: "desktop/src-tauri/tauri.conf.json lists \"binaries/buzz-backend-kubernetes\" in its externalBin array alongside buzz-acp, buzz-agent, buzz-dev-mcp, git-credential-nostr, and buzz, meaning the desktop app's Tauri bundler packages the built buzz-backend-kubernetes binary as a sidecar executable inside the shipped application."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
  - statement: "desktop/src-tauri/src/managed_agents/backend.rs's discover_provider_candidates function scans PATH (plus the running executable's own directory and ~/.local/bin) for files whose name starts with the literal prefix \"buzz-backend-\", and its provider_id_from_filename helper strips that prefix (and, case-insensitively, a trailing .exe/.bat/.cmd) to derive the provider id a buzz-backend-kubernetes binary on disk would be discovered under: \"kubernetes\"."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs"
  - statement: "Five GitHub Actions workflows (.github/workflows/ci.yml, linux-canary.yml, signed-macos-canary.yml, macos-intel-canary.yml, release.yml) reference buzz-backend-kubernetes explicitly, either as a cargo build -p target alongside buzz-acp/buzz-agent/buzz-dev-mcp/git-credential-nostr/buzz-cli for desktop sidecar bundling, or (in ci.yml) as a placeholder binary path touched for a build-verification step."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - ".github/workflows/linux-canary.yml"
      - ".github/workflows/signed-macos-canary.yml"
      - ".github/workflows/macos-intel-canary.yml"
      - ".github/workflows/release.yml"
  - statement: "crates/buzz-backend-kubernetes/tests/wire_fixtures.rs is a golden-fixture integration test that spawns the actual built binary (Command::new(env!(\"CARGO_BIN_EXE_buzz-backend-kubernetes\"))) over a real OS pipe against recorded *.request.json/*.response.json fixture pairs under tests/fixtures/provider-wire/, and its own doc comment states this exercises the stdin -> one JSON object on stdout -> exit code contract the desktop actually depends on, which an in-process function call would not."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/tests/wire_fixtures.rs"
  - statement: "crates/buzz-backend-kubernetes/tests/fixtures/provider-wire/README.md states that its request fixtures are 'recorded, not invented' -- captured from the desktop's real build_launch_block -> deploy_payload_json path rather than derived by reading those functions -- and that a completeness guard in wire_fixtures.rs stops a case from going missing but cannot prove a recorded case is still accurate."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/tests/fixtures/provider-wire/README.md"
  - statement: "Every module file under crates/buzz-backend-kubernetes/src/ (classify.rs, client.rs, cluster.rs, config.rs, env.rs, gc.rs, image.rs, intent.rs, main.rs, naming.rs, pod.rs) carries its own #[cfg(test)] mod tests with unit tests exercising that module's pure logic in isolation from any real Kubernetes cluster."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/classify.rs"
      - "crates/buzz-backend-kubernetes/src/client.rs"
      - "crates/buzz-backend-kubernetes/src/cluster.rs"
      - "crates/buzz-backend-kubernetes/src/config.rs"
      - "crates/buzz-backend-kubernetes/src/gc.rs"
      - "crates/buzz-backend-kubernetes/src/image.rs"
      - "crates/buzz-backend-kubernetes/src/intent.rs"
      - "crates/buzz-backend-kubernetes/src/main.rs"
      - "crates/buzz-backend-kubernetes/src/naming.rs"
      - "crates/buzz-backend-kubernetes/src/pod.rs"
  - statement: "launchpad/docs/corpus/architecture/deployment/kubernetes.md (id architecture-deployment-kubernetes) documents a different subject: the relay's own deployment topology onto Kubernetes via the Helm chart at deploy/charts/buzz, serving WebSocket/REST/web-UI traffic backed by PostgreSQL, Redis, and object storage -- not the per-agent pod provisioning this node documents."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "Because crates/buzz-backend-kubernetes has no [lib] target, nothing in this repository can express a dependency on it through Cargo, so the crate's real inbound dependency (the desktop app) is only discoverable through the runtime/bundling wiring that names its binary -- tauri.conf.json's externalBin entry and backend.rs's PATH-prefix discovery -- rather than through any Cargo.toml [dependencies] entry, which is a genuine deviation from the component template's preferred manifest evidence for the 'depended on by' direction and is disclosed as such rather than silently substituted."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-backend-kubernetes/Cargo.toml"
      - "desktop/src-tauri/tauri.conf.json"
      - "desktop/src-tauri/src/managed_agents/backend.rs"
    confidence: 0.85
  - statement: "Issue #1232 requires exactly one hand-authored canonical corpus document with schema-valid front matter, evidence traceable to current code/tests/specification/decisions, links to implementation/verification/specification/neighboring nodes without duplicating their content, a stated responsibility and well-defined interface/boundary, named dependencies and collaborators, links to source implementation and tests, and component-level (not whole-platform) scope."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1232 definition of done"
---

# `buzz-backend-kubernetes`

`buzz-backend-kubernetes` is a standalone Rust binary crate at
`crates/buzz-backend-kubernetes` that lets the Buzz desktop app launch and
manage a remote agent as a Kubernetes Pod instead of a local subprocess. It
implements one side of a generic, harness-agnostic contract the desktop calls
the Provider Protocol (`docs/remote-agents.md`): the desktop discovers,
invokes, and interprets this binary's stdout exactly the same way it would
any other conforming `buzz-backend-<id>` provider, and this binary is the
protocol's first — and, at the time of writing, only — conforming
implementation. This node answers: what does this one component do, what is
its interface with the rest of the system, and what does it depend on and
get depended on by?

## Responsibility

The crate's own top-of-file doc comment states its job plainly: *"Kubernetes
backend provider for Buzz remote agents (spec `docs/remote-agents.md`).
One process per operation: read exactly one JSON request from stdin, write
exactly one JSON response to stdout, exit."* Concretely, one invocation of
the binary does one of two things:

- **`info`** — describe itself (name, version, protocol version, a JSON
  Schema for its own configuration) without touching a cluster, so the
  desktop can render a config form before any kubeconfig is known to exist.
- **`deploy`** — given an agent's Nostr keypair and launch payload plus a
  Kubernetes-specific `provider_config`, converge a target Kubernetes
  namespace to hold exactly one running Pod (plus its per-attempt Secret)
  for that agent's identity, and return the resulting `agent_id`, or an
  in-band error.

Internally this is implemented as a pure state machine
(`classify::classify`, `docs/remote-agents.md`'s Deploy State Machine) driven
by a reconciliation loop (`reconcile::deploy`) against a `Substrate` trait
that `cluster::Cluster` implements for a real kube-rs client. The crate also
refuses one input outright before doing anything else: an agent configured
for the shared-compute `relay-mesh` provider, because that agent already
runs on the relay's own compute and deploying it as a second pod would
create a second, contending consumer of the same agent identity
(`main.rs`'s `refuse_relay_mesh`).

## Public interface

This crate has **no Rust library surface** — its `Cargo.toml` declares only
a `[[bin]]` target and no `[lib]` section, so no other crate in this
repository can `use` anything from it. Its actual public interface is the
**wire contract** other processes talk to it through: one JSON request on
stdin, one JSON response on stdout, an exit code that carries only
success-or-not (every distinguishable outcome lives inside the response's
`ok` field).

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| stdin → stdout process contract | process protocol | Exactly one JSON `Request` read from stdin; exactly one JSON `Response` written to stdout; exit 0 unless stdin could not even be read | `main.rs` (`main`, `respond`) |
| `Request::Info` | wire request variant | `{"op":"info"}` → self-description, no cluster contact | `wire.rs` |
| `Request::Deploy(DeployRequest)` | wire request variant | `{"op":"deploy","agent":{...},"provider_config":{...}}` → converge one Pod for the agent's identity | `wire.rs` |
| `DeployRequest.agent: AgentPayload` | struct field | `relay_url`, `private_key_nsec`, `auth_tag`, `respond_to`, `respond_to_allowlist`, `env_vars`, optional `launch: LaunchBlock` — only the fields this binding consumes are typed | `wire.rs` |
| `Response::Info` / `Response::Deploy` / `Response::Error` | wire response variants | Serialized flat (`{"ok":..., ...}`), so a caller reads `ok`/`error`/`agent_id` at the top level | `wire.rs` |
| `PROTOCOL_VERSION` | `const u32` | The wire-contract version this binary speaks; the desktop must reject a mismatch before sending a request carrying `private_key_nsec` (`docs/remote-agents.md` §Discovery, pre-secret negotiation gate) | `wire.rs` |
| `config::config_schema()` | function (internal, drives `info`'s `config_schema` field) | JSON Schema for `provider_config`'s 9 v1 fields (`context`, `namespace`, `image`, `cpu_request`, `memory_request`, `cpu_limit`, `memory_limit`, `inactivity_seconds`, `service_account`) | `config.rs` |

Because there is no linkable Rust API, every other component that "uses"
this crate does so by spawning the compiled binary as a subprocess and
speaking this wire contract to it — not by depending on it in a
`Cargo.toml`.

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `kube`, `k8s-openapi` | Typed Kubernetes apiserver client and object types (`Pod`, `Secret`, list/create/delete calls) | `Cargo.toml` |
| `nostr` | Derives the agent's Nostr identity (pubkey, labels) from its `nsec` | `Cargo.toml`, `naming.rs` |
| `tokio` | Runs the async `deploy` path on a dedicated current-thread runtime built per invocation | `Cargo.toml`, `main.rs` |
| `serde`, `serde_json` | Wire (de)serialization and `provider_config`/`config_schema` JSON handling | `Cargo.toml`, `wire.rs`, `config.rs` |
| `sha2`, `hex` | Create-intent fingerprint hashing (SHA-256) and hex encoding of pubkeys/fingerprints | `Cargo.toml`, `intent.rs`, `naming.rs` |
| `rand` | Generates the per-attempt generation token and the random default namespace suffix | `Cargo.toml`, `naming.rs`, `config.rs` |
| `chrono` | Same-clock GC age comparison against the apiserver's HTTP `Date` header | `Cargo.toml`, `gc.rs`, `cluster.rs` |
| `http`, `http-body-util` | Reading the raw `http::Response` (headers included) off `kube`'s `Client::send`, needed to reach the apiserver's `Date` header | `Cargo.toml`, `cluster.rs` |
| `rustls` (`ring` feature, explicit) | Installs a process-level TLS `CryptoProvider` at startup; required because the release build's single cargo invocation across all sidecars otherwise leaves `rustls` unable to auto-select a provider | `Cargo.toml`, `main.rs` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| Desktop app (Tauri bundle) | Bundles the compiled binary as an `externalBin` sidecar shipped inside the app | `desktop/src-tauri/tauri.conf.json` |
| `desktop/src-tauri/src/managed_agents/backend.rs` | Discovers this binary on `PATH` (and the app's own directory, and `~/.local/bin`) by matching the `buzz-backend-` filename prefix, deriving provider id `kubernetes` | `desktop/src-tauri/src/managed_agents/backend.rs` |
| CI release/canary workflows | Build the crate as part of the desktop's sidecar set for macOS/Linux release and canary artifacts | `.github/workflows/release.yml`, `.github/workflows/linux-canary.yml`, `.github/workflows/signed-macos-canary.yml`, `.github/workflows/macos-intel-canary.yml` |

This "depended on by" direction is **not** a Cargo dependency — this crate
has no `[lib]` target for anything to link against. It is a
process-invocation dependency: the desktop discovers the binary by name on
`PATH`/bundle directory and talks to it over the stdin/stdout wire contract
in *Public interface* above, never by importing its code. That is a genuine
departure from the component template's preferred manifest evidence
(`Cargo.toml` in both directions) for a subprocess-shaped component, and is
disclosed here rather than forced into a Cargo-shaped answer that does not
exist.

## Boundary

This node does not describe:
- **The generic Provider Protocol itself** — discovery rules, the
  pre-secret negotiation gate, timeouts, output-scrubbing, the `info`/
  `deploy` wire shapes in full, or the harness-agnostic parts of the Deploy
  State Machine. All of that is normative content of `docs/remote-agents.md`
  (`##Provider Protocol`, `##Deploy State Machine`), which this crate
  *realizes* rather than defines. Link to it; do not restate it.
- **The desktop-side discovery and invocation code**
  (`desktop/src-tauri/src/managed_agents/backend.rs`,
  `desktop/src-tauri/src/commands/agents_deploy.rs`) as its own component —
  it is the caller of this provider, not this provider, and would be its
  own corpus node if one is written.
- **The relay's own Kubernetes deployment.**
  `launchpad/docs/corpus/architecture/deployment/kubernetes.md` documents a
  different subject entirely: deploying the *relay itself* (WebSocket/REST/
  web UI, backed by Postgres/Redis/object storage) via the Helm chart at
  `deploy/charts/buzz`. This crate does not deploy the relay; it deploys
  per-agent compute pods that then talk *to* a relay over `BUZZ_RELAY_URL`.
  The shared word "kubernetes" names two unrelated systems in this
  repository — do not conflate the two nodes.
- **Install/usage instructions for a human running this binary.** No
  `README.md` exists for this crate to link to; the only README under its
  directory (`tests/fixtures/provider-wire/README.md`) documents the wire
  test fixtures, not the binary itself.
- **Class/function-level design detail** beyond what is needed to cite a
  responsibility, interface item, or dependency — the module list in
  *Responsibility* names each module's job at a paragraph level, not its
  internals.

## Relationships

None declared. `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` at the recorded revision carries no
`platforms/**` node and no other node whose subject is remote-agent compute
provisioning for this `part-of`/`depends-on` to target; the one
superficially similar node,
`architecture-deployment-kubernetes`, documents an unrelated subject (see
*Boundary*) and a `references` edge to it would suggest a connection that
does not exist. The first sibling node under `platforms/agents/` or a future
architecture-component node decomposing a "remote agent compute" container
is the natural moment to revisit this.

## Scope and omissions

**This node covers** what `buzz-backend-kubernetes` is for, its wire-level
public interface (it exports no Rust API), its build-time dependencies and
its two forms of "depended on by" (desktop bundling/discovery, CI release
builds), and an explicit boundary against the generic Provider Protocol
spec, the desktop-side caller code, and the unrelated relay-deployment
corpus node that shares the word "kubernetes".

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full Provider Protocol contract (discovery, negotiation gate, `info`/`deploy` wire shapes, output scrubbing) | `docs/remote-agents.md` `##Provider Protocol` |
| The full Deploy State Machine and its conformance test families | `docs/remote-agents.md` `##Deploy State Machine`, `##Conformance` |
| The desktop-side discovery/invocation code as its own component | Not yet written as a corpus node |
| The relay's own Kubernetes deployment topology | `launchpad/docs/corpus/architecture/deployment/kubernetes.md` |
| Per-type corpus standards beyond `templates/component.md` that might later refine what a component node needs | Any future revision to `templates/component.md` |

**Expected but not verified when this node was written:**

- **No conformance/envtest run against a real or `kind` apiserver was
  performed for this node.** All claims about `reconcile.rs`/`cluster.rs`/
  `gc.rs` behavior are grounded in reading the source and its unit tests,
  not in observing a live deploy against a cluster.
- **The open decisions and known defects `docs/remote-agents.md` itself
  records** (e.g. Windows binary support, the nest-workspace scaffolding
  decision, the harness exit-code contract required before `OnFailure`
  ships) were read but are the spec's own open items, not settled facts
  about this crate's current behavior — this node does not attempt to
  resolve them.
