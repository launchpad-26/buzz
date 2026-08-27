---
id: architecture-context-buzz-platform
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the tip of origin/launchpad at authoring time."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Buzz is a self-hosted, Apache-2.0 Rust monorepo team-communication platform built on the Nostr protocol (NIP-01 wire format), where the relay is the single source of truth: all reads and writes from every client flow through it, with no peer-to-peer event exchange, gossip, or replication."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "A Buzz community is the tenant-visible workspace selected by the request host; the self-hosted default is one host, one relay process, one implicit community, and every connection binds a TenantContext resolved from that host before any Nostr or HTTP handler runs."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "README.md"
  - statement: "A human reaches Buzz as a Nostr client: the first-party desktop app (Tauri 2 + React 19), the mobile app (Flutter), the web client served by the relay, or any other NIP-42-compatible Nostr client — all authenticate over the relay's WebSocket via a signed NIP-42 challenge/response, or over its HTTP bridge via NIP-98."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "desktop/src-tauri/Cargo.toml"
      - "mobile/pubspec.yaml"
      - "web/package.json"
  - statement: "An AI agent reaches Buzz through one of two architecturally distinct paths: buzz-cli, an agent-first CLI that speaks the relay's own REST/WebSocket surface directly under an agent's own Nostr keypair; or buzz-acp, a standalone harness that bridges relay @mention events to external agent subprocesses (goose, codex, claude) over the Agent Communication Protocol (JSON-RPC over stdio) — the spawned agent subprocess itself never speaks Buzz's Nostr wire protocol."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-cli/Cargo.toml"
      - "crates/buzz-acp/Cargo.toml"
      - "AGENTS.md"
  - statement: "A human operator manages relay membership out-of-band from the Nostr protocol itself, via buzz-admin's add-member, remove-member, list-members, generate-key, and reconcile-channels subcommands; the buzz-admin binary ships inside the relay's own Docker image as the recommended production tool for this."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-admin/Cargo.toml"
  - statement: "Postgres is the platform's primary event store — all Nostr events (monthly range-partitioned), channels, tokens, workflow definitions/runs/approvals, and the hash-chain audit log — and also backs full-text search directly, via a generated tsvector column and GIN index on the events table, with no separate search service."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "docker-compose.yml"
  - statement: "Redis provides cross-node pub/sub fan-out for channel-scoped events (a PSUBSCRIBE consumer loop feeds local WebSocket connections on other relay instances), online/away presence (SET EX, 180s TTL), and typing indicators (a sorted set, 60s window)."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "docker-compose.yml"
  - statement: "An S3-compatible object store (MinIO in the local development stack) backs media storage behind the Blossom protocol endpoints: PUT /media/upload (50 MB cap) and GET/HEAD /media/{sha256_ext}."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "docker-compose.yml"
  - statement: "The relay is itself a git remote: GET /git/{owner}/{repo}/info/refs and POST .../git-upload-pack and .../git-receive-pack implement git's smart HTTP protocol, gated by an internal git policy hook at POST /internal/git/policy."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "Two crates outside the relay let an ordinary git client authenticate against that git remote using a Nostr keypair instead of a GitHub-issued credential: git-sign-nostr signs git objects with a Nostr key, and git-credential-nostr is a git credential helper for Nostr-authed push/fetch — making a developer's local git tooling its own kind of client of the platform, distinct from a Nostr client proper."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/Cargo.toml"
      - "crates/git-credential-nostr/Cargo.toml"
      - "AGENTS.md"
  - statement: "The local development stack (docker-compose.yml) provisions a Keycloak container (quay.io/keycloak/keycloak:26.0, exposed on 127.0.0.1:8180) alongside Postgres, Redis, and MinIO, but no Rust source anywhere under crates/ references Keycloak by name — at this revision it is provisioned in local dev infrastructure with no confirmed relationship to the platform's runtime behavior."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "grep_rli('keycloak', 'crates/**/*.rs') -> no matches"
  - statement: "buzz-relay's own source states that Postgres FTS replaced a prior Typesense-backed search worker (\"the old Typesense `index_event` worker and its `search_index_tx` mpsc are gone with the Typesense backend\"), yet .env.example still carries a live-looking \"Typesense (search)\" section (TYPESENSE_API_KEY, TYPESENSE_URL) that names no system the platform actually talks to."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:502-506"
      - "crates/buzz-search/src/query.rs"
      - ".env.example"
  - statement: "block/buzz is the OSS source for the relay, desktop app, mobile app, CLI, and agent harness; four internal repositories (buzz-releases, sprout-oss, block-coder-tf-stacks, sprout-backend-blox) build, containerize, and deploy this source but are not part of the running platform's system boundary — they act on Buzz from the outside, at build and deploy time, not at runtime."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "This checkout is operated by the launchpad-26 cohort, whose own governing instructions state \"We operate Buzz; we do not develop it\" and that most of the contributor guide above the fork notice is correct for changing Buzz itself but wrong for the work most people do in this fork (deployment, CI/CD, documentation, cohort process) — this node documents the former: the system the cohort operates, not the fork's own tooling."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
relationships:
  - type: references
    target: corpus-agents
---

# Buzz Platform — System Context

The system-context view of Buzz: the platform's boundary, every actor and external
system that directly touches it, and how each relates to it. This node stays at
context level on purpose — it does not describe `buzz-relay`'s internal
decomposition (event pipeline, subscription registry, crate dependency graph).
For that, see [`ARCHITECTURE.md`](../../../../ARCHITECTURE.md), which every claim
below cites and which a future `architecture/containers/*` corpus node should
draw from once one exists.

## What "the Buzz platform" is

Buzz is a self-hosted, Apache-2.0 Rust monorepo team-communication platform built
on the Nostr protocol. `buzz-relay` is the single source of truth: every chat
message, reaction, workflow step, canvas update, and huddle event is a
cryptographically signed Nostr event, and every read and write from every client
flows through the relay — there is no peer-to-peer event exchange, gossip, or
replication between clients.

A Buzz **community** is the tenant-visible workspace selected by the request
host. The self-hosted default is one host, one relay process, one implicit
community; a hosted operator can serve many communities behind many domains from
one shared deployment, but the client-facing rule is the same either way: the URL
is authoritative for the workspace.

## Actors and external systems

| Actor / system | Relationship to Buzz |
|---|---|
| **Human** | Connects as a Nostr client — the desktop app, the mobile app, the web client, or any other NIP-42-compatible client — over the relay's WebSocket (NIP-42) or HTTP bridge (NIP-98). |
| **AI agent** | Two distinct paths: `buzz-cli` speaks the relay's REST/WebSocket surface directly under the agent's own Nostr keypair; `buzz-acp` bridges relay `@mention` events to an external agent subprocess (goose, codex, claude) over ACP JSON-RPC on stdio — the subprocess itself is never a Nostr client. |
| **Operator** | Manages relay membership via `buzz-admin` (ships inside the relay's own Docker image), out-of-band from the Nostr protocol clients use. |
| **git client** | A developer's ordinary `git` tooling is a client of the relay's git-smart-HTTP endpoints, optionally signing objects and authenticating with a Nostr keypair via `git-sign-nostr` / `git-credential-nostr` instead of a GitHub-issued credential. |
| **Postgres** | Primary event store (events, channels, tokens, workflows, audit) and the full-text search backend (generated `tsvector` + GIN index) — no separate search service. |
| **Redis** | Cross-node pub/sub fan-out, presence, and typing indicators. |
| **S3-compatible object store** (MinIO in local dev) | Media storage behind the Blossom protocol upload/download endpoints. |
| **Agent subprocess runtime** (goose / codex / claude, spawned by `buzz-acp`) | Receives batched `@mention` prompts over ACP JSON-RPC and returns tool-call output; does not connect to the relay itself. |
| **Deploy/build ecosystem** (`buzz-releases`, `sprout-oss`, `block-coder-tf-stacks`, `sprout-backend-blox`) | Builds, containerizes, and deploys this source; acts on Buzz from outside at build/deploy time, not part of the runtime system boundary. |

## Context diagram

```mermaid
graph TD
    Human["Human (desktop / mobile / web / Nostr client)"]
    Agent["AI Agent (buzz-cli or ACP subprocess)"]
    Operator["Operator (buzz-admin)"]
    GitClient["git client (git-sign-nostr / git-credential-nostr)"]

    subgraph Platform["Buzz Platform (buzz-relay)"]
        Relay["WebSocket + HTTP bridge — NIP-01 / NIP-42 / NIP-98"]
    end

    Postgres[("Postgres — events, channels, workflows, audit, full-text search")]
    Redis[("Redis — pub/sub fan-out, presence, typing")]
    Media[("S3-compatible store (MinIO in dev) — Blossom media")]
    AgentProc["Agent subprocess (goose / codex / claude)"]
    Deploy["Deploy ecosystem — buzz-releases, sprout-oss, block-coder-tf-stacks, sprout-backend-blox"]
    Keycloak["Keycloak — provisioned in dev compose, no code reference found"]
    Typesense["Typesense — retired backend, stale .env.example entry"]

    Human -->|WebSocket / HTTP| Relay
    Agent -->|WebSocket / HTTP| Relay
    Operator -->|CLI over relay API| Relay
    GitClient -->|git smart HTTP| Relay
    Relay -->|events, channels, workflows, audit, search| Postgres
    Relay -->|fan-out, presence, typing| Redis
    Relay -->|Blossom upload / download| Media
    Relay -.->|ACP JSON-RPC over stdio, via buzz-acp| AgentProc
    Deploy -.->|builds & deploys, not runtime traffic| Platform
    Keycloak -.->|provisioned, unwired| Platform
    Typesense -.->|retired, config-only| Platform
```

Dashed edges mark relationships that are provisioned or referenced but not a
confirmed part of runtime behavior — see *Verified gaps* below.

## Verified gaps

Two entries in local configuration name systems that current source does not
confirm as live, and both are worth flagging rather than silently omitting or
silently including:

- **Keycloak** is provisioned in `docker-compose.yml`'s local development stack
  (image `quay.io/keycloak/keycloak:26.0`, port 8180) alongside Postgres, Redis,
  and MinIO. No Rust source under `crates/` references Keycloak by name. It may
  be scaffolding for planned SSO/identity work, or a leftover from an earlier
  design — this node does not resolve which, only that today it has no confirmed
  runtime relationship to the platform.
- **Typesense** is not a live external system despite `.env.example` still
  carrying a "Typesense (search)" section (`TYPESENSE_API_KEY`,
  `TYPESENSE_URL`). `buzz-relay`'s own source says the Typesense-backed
  `index_event` worker is gone, replaced by Postgres FTS populating the
  searchable column on write. The `.env.example` entries are stale and should
  not be read as describing a system Buzz currently talks to.

## This checkout's own relationship to what it documents

This corpus lives in the `launchpad-26/buzz` fork, whose own governing
instructions are explicit that the cohort operates and deploys Buzz rather than
developing it. This node documents the system being operated — Buzz's own
architecture, as built in `block/buzz` and inherited by this fork — not the
fork's deployment tooling, which is a separate concern the cohort's own
`launchpad/` tree owns.

## Scope and omissions

**This document covers** the system boundary of the Buzz platform: every actor
and external system with a direct relationship to it, and what that relationship
is, at context level.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-relay`'s internal container/component decomposition (event pipeline, subscription registry, crate dependency hierarchy) | `ARCHITECTURE.md`, and a future `architecture/containers/*` corpus node |
| Whether Keycloak is planned, abandoned, or dead configuration | Unresolved — named as a verified gap above, not decided here |
| The full desktop/mobile/web feature surface each client actor exposes | Each client's own future corpus nodes |
| Deployment/CI/CD detail for the four ecosystem repos named above | Each repo's own documentation; `AGENTS.md`'s Ecosystem section is the entry point |

**Expected but not verified when this node was written:**

- **Whether any client beyond the desktop, mobile, and web apps actually
  connects to a Buzz relay in practice.** NIP-42 makes any compliant Nostr
  client capable of it in principle; no third-party client was observed
  connecting.
- **Whether Keycloak's provisioning in `docker-compose.yml` predates or
  postdates the crates that would consume it**, and therefore whether it is
  forward scaffolding or a stale leftover. `git log` on `docker-compose.yml`
  was not run for this node; the claim above is limited to "provisioned,
  unreferenced by source," not a claim about intent or timeline.
- **Whether every AI agent runtime `buzz-acp` can spawn is limited to
  goose/codex/claude**, or whether that list in `ARCHITECTURE.md` is
  illustrative rather than exhaustive; `buzz-acp`'s own subprocess-spawning code
  was not read for this node.
