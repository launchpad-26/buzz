---
id: capabilities-agents-agent-auth-tag
type: capabilities
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
  - statement: "BUZZ_AUTH_TAG carries a NIP-OA owner-attestation `auth` tag as JSON — `[\"auth\",\"<owner-pubkey-hex>\",\"<conditions>\",\"<sig-hex>\"]` — computed over the preimage `nostr:agent-auth:<agent-pubkey-hex>:<conditions>`, SHA-256 hashed and BIP-340 Schnorr-signed by the owner's own secret key; `compute_auth_tag` builds it and rejects owner-pubkey == agent-pubkey as meaningless self-attestation."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:1-18"
      - "crates/buzz-sdk/src/nip_oa.rs:146-166"
  - statement: "`verify_auth_tag` reconstructs the preimage from the tag's own fields, hashes it, verifies the BIP-340 Schnorr signature against the owner pubkey embedded in the tag, and returns that owner's `PublicKey` on success; it independently re-rejects owner-pubkey == agent-pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:179-236"
  - statement: "`parse_auth_tag` is a structural-only fast path — exactly 4 elements, first element `\"auth\"`, a 64-char lowercase-hex owner pubkey, a 128-char lowercase-hex signature, and a syntactically valid `conditions` string — used where no cryptographic verification is wanted yet (e.g. relay-membership delegation at connection time); it performs no Schnorr check."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:238-299"
  - statement: "The `conditions` grammar is: the empty string, or `&`-joined clauses of the shape `kind=<0-65535>`, `created_at<<u32>` or `created_at><u32>`, each a canonical decimal with no leading zero and no whitespace; `crates/git-sign-nostr` independently re-implements this exact grammar (including the leading-zero rejection) rather than depending on `buzz-sdk`, and the two implementations agree."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:31-107"
      - "crates/git-sign-nostr/src/lib.rs:562-649"
  - statement: "`buzz-acp` resolves a managed agent's owner pubkey at startup by trying `BUZZ_AUTH_TAG` first — verifying it against the agent's own pubkey via `verify_auth_tag` — and falling back to the `--agent-owner` flag / `BUZZ_ACP_AGENT_OWNER` env var only when the tag is absent, empty, or fails verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:135-161"
  - statement: "Independently of owner resolution, `buzz-acp` also parses `BUZZ_AUTH_TAG` structurally (via `parse_auth_tag`, no crypto) into a `nostr::Tag` that it hands to `HarnessRelay::connect`, so the same credential additionally drives NIP-OA relay-membership delegation on the harness's own WebSocket connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2001-2010"
  - statement: "`buzz-acp` forwards `BUZZ_AUTH_TAG` verbatim as an env var into the MCP server subprocess (`buzz-dev-mcp`) it spawns, so that subprocess can attach the same owner attestation to every event it signs on the agent's behalf; a unit test asserts the var is forwarded when set and omitted when empty."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:5099-5108"
      - "crates/buzz-acp/src/lib.rs:6862-6886"
  - statement: "`buzz-cli` exposes the same credential as both the `BUZZ_AUTH_TAG` env var and a `--auth-tag` flag (flag overrides env, value hidden from `--help` env dumps, documented as optional in the CLI's own long help text); when present it is parsed and Schnorr-verified before use, and only the re-serialized, verified canonical form — never the raw operator-supplied bytes — is attached to the CLI's own outgoing signed events and requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:70-73"
      - "crates/buzz-cli/src/lib.rs:89-91"
      - "crates/buzz-cli/src/lib.rs:2070-2095"
  - statement: "`buzz-cli` additionally accepts a hand-typed, unquoted bracket shorthand for the tag (e.g. `[auth,<hex>,,<hex>]`, as it might be pasted into a `.env` file) and rewrites it to strict JSON before handing it to the SDK's strict parser and verifier; this leniency exists only at this configuration-input edge and never relaxes the wire format or the signature check itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:2016-2049"
  - statement: "Because an agent process signs every event as itself, an agent running under `BUZZ_AUTH_TAG` can only ever satisfy the \"self\" path of an owner/admin action such as an identity-archive request (target pubkey == request signer's pubkey) — it cannot act as another identity's owner merely by holding its own attestation. `buzz-cli`'s own `agents archive` help text states this constraint directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:300-313"
  - statement: "On the relay, `extract_auth_tag_json` pulls a NIP-OA `auth` tag from a signed WebSocket AUTH (kind:22242) event before verification consumes the event, and treats more than one `auth` tag on the same event as no valid tag at all, per the NIP-OA spec's own ambiguity rule."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:1-33"
  - statement: "After NIP-42 verification succeeds, the relay's connection handler runs a community-ban check that cascades from the authenticated pubkey to its NIP-OA-proven owner — an owner ban blocks the agent, but an agent-only ban does not cascade back to the owner — then a relay-membership check (`enforce_relay_membership`) that itself supports NIP-OA owner-delegation fallback; both checks fail closed (deny) on a database error rather than treating the error as a pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:75-272"
  - statement: "The same attestation has an HTTP-header variant: requests to the bridge API that cannot carry a Nostr event's own tags pass it as an `x-auth-tag` header, which the relay's membership enforcement consumes exactly as it would consume the tag from a signed event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:890-892"
  - statement: "Git push over smart HTTP is a second HTTP-shaped consumer: because git's credential-helper protocol cannot add a standalone header, `git-credential-nostr` reads `BUZZ_AUTH_TAG` (env, or `nostr.authtag` git config as a fallback) client-side to build the NIP-98 auth event's own `auth` tag, and the relay's git transport handler accepts either that event-carried tag or a bare `x-auth-tag` header, running the same ban-cascade logic used for WebSocket connections."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs:74-96"
      - "crates/buzz-relay/src/api/git/transport.rs:205-227"
  - statement: "`git-sign-nostr` (signing git objects, not the HTTP push itself) prefers `BUZZ_AUTH_TAG` over the `nostr.authtag` git-config fallback so CI pipelines and agent harnesses can inject the attestation without touching repo config, and fails closed — returning a hard error rather than silently omitting the attestation — when the env var or config value is present but malformed (bad JSON, wrong shape, non-hex, wrong length, or over its 1024-byte cap); an entirely absent tag, by contrast, is a valid `None`."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:452-549"
  - statement: "`crates/buzz-backend-kubernetes`'s tiered env-merge for pod-hosted agents treats `BUZZ_AUTH_TAG` as one of its authoritative top-level identity fields: a lower-priority tier's `policy_env`/`env` cannot spoof it — a test asserts a forged `BUZZ_AUTH_TAG` supplied in a lower tier is silently overwritten by the authoritative value, not merely rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs:27"
      - "crates/buzz-backend-kubernetes/src/env.rs:330-373"
  - statement: "Desktop's managed-agent launcher treats `BUZZ_AUTH_TAG` as a reserved env key a persona/agent record's user-editable env cannot override (identity/secret category), injects it from the agent's own stored `auth_tag` field at spawn time (removing the env var entirely when the record has none), and a dedicated validator closes an `=`-in-key bypass (`BUZZ_AUTH_TAG=x` as a literal key smuggling a value past the reserved-key string compare) that earlier let a forged value reach the child process's real `BUZZ_AUTH_TAG`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs:28-76"
      - "desktop/src-tauri/src/managed_agents/runtime.rs:506-510"
      - "desktop/src-tauri/src/managed_agents/env_vars/tests.rs:242-298"
  - statement: "The Buzz CLI's auth environment variables (`BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`) are auto-injected by the ACP harness into managed agent subprocesses, and root `AGENTS.md` documents this as the standard way a managed agent authenticates — it is not something the agent configures for itself."
    entry_class: FACT
    evidence:
      - "AGENTS.md:203-206"
      - "crates/buzz-acp/src/base_prompt.md:11"
  - statement: "An owner (or any script holding the owner's secret key) computes a fresh `BUZZ_AUTH_TAG` for a given agent pubkey via the `compute_auth_tag` SDK function, also exposed as a small standalone example binary (`cargo run --example compute_auth_tag -- <owner_secret_hex> <agent_pubkey_hex> [conditions]`) that prints the tag JSON to stdout for pasting into an agent's environment."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/examples/compute_auth_tag.rs:1-29"
  - statement: "Treating `BUZZ_AUTH_TAG` as a single security-tier secret across every host surface that can inject it (Desktop launcher, Kubernetes backend, CI/agent-harness env) rather than as ordinary configuration is a deliberate, repeated design choice, not an incidental side effect of it happening to hold a signature — every injection site this node examined guards it at the same tier as `BUZZ_PRIVATE_KEY`."
    entry_class: INFERENCE
    confidence: 0.85
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs:28-76"
      - "crates/buzz-backend-kubernetes/src/env.rs:27"
      - "crates/buzz-acp/src/lib.rs:5099-5108"
relationships:
  - type: part-of
    target: capabilities-agents-agent
---

# Agent owner attestation (`BUZZ_AUTH_TAG`): capability

The product lets an AI agent act under its own Nostr keypair while still
carrying cryptographic proof of the human (or organization) that authorized
it — a NIP-OA `auth` tag, transported as the `BUZZ_AUTH_TAG` environment
variable, a request header, or an event tag depending on the surface. An
owner never hands the agent their own secret key or a bearer token; instead
they sign a short attestation once, and every surface that consumes it —
relay membership, community bans, moderation, git push, and (for the agent
itself) identity archival — can verify that attestation without a database
round trip, because the proof is self-contained and cryptographically
signed. This is what lets Buzz treat "a process with a keypair, this
attestation, and a relay URL" as a legitimate agent identity regardless of
which launcher spawned it — the Desktop app, a Kubernetes-hosted backend, or
a bare CI job.

## Maturity

Shipped. The attestation format, its signing/verification functions and
their test vectors live in `crates/buzz-sdk/src/nip_oa.rs`. It is consumed
today by the ACP harness (`crates/buzz-acp`) for owner resolution, relay
membership delegation, and MCP-subprocess forwarding; by `buzz-cli` for
outgoing signed events and requests; by the relay
(`crates/buzz-relay/src/handlers/auth.rs`,
`crates/buzz-relay/src/api/bridge.rs`,
`crates/buzz-relay/src/handlers/identity_archive.rs`,
`crates/buzz-relay/src/api/git/transport.rs`) for WebSocket auth, the HTTP
bridge, identity archival, and git push; and by the git-signing/credential
helpers (`crates/git-sign-nostr`, `crates/git-credential-nostr`) for signed
git objects and git's own credential protocol. Two independent host
launchers — the Desktop app's managed-agent runtime and
`crates/buzz-backend-kubernetes`'s pod launcher — both treat it as an
authoritative, non-overridable identity field.

## Behavioral rules, constraints, and variants

- **Self-attestation is rejected.** Both `compute_auth_tag` and
  `verify_auth_tag` refuse a tag whose owner pubkey equals the agent
  pubkey — an identity cannot vouch for itself.
- **`conditions` is a closed grammar**, not free text: empty, or
  `&`-joined `kind=<0-65535>` / `created_at<<u32>` / `created_at><u32>`
  clauses in canonical decimal (no leading zero, no whitespace). Two
  independent implementations of this grammar exist (`buzz-sdk`,
  `git-sign-nostr`) and agree.
- **More than one `auth` tag on an event is treated as no valid tag**,
  per the NIP-OA spec's own ambiguity rule, not as "use the first" or
  "use the last."
- **An agent can only ever prove itself, not act as another identity's
  owner.** Because the agent signs with its own key, `BUZZ_AUTH_TAG`
  lets it satisfy the "self" path of an owner/admin-gated action (e.g.
  archiving its own identity) but never the "I am this other identity's
  owner" path — that requires the actual owner key to sign the request.
- **Absent vs. malformed are different outcomes, and the difference is
  deliberate.** Consumers that read the tag from configuration
  (`buzz-acp`, `git-sign-nostr`) treat a missing tag as `None` (proceed
  without an owner) but a *present-but-malformed* tag as a hard,
  fail-closed error — silently dropping a tag someone configured but
  mistyped would be a worse failure mode than refusing to start.
- **Two independent env-injection layers guard it as a secret, not as
  ordinary config.** The Desktop launcher lists it as a reserved key a
  persona/agent's user-editable env cannot override, and closes an
  `=`-in-key bypass that could otherwise smuggle a forged value past that
  guard. The Kubernetes backend's tiered env merge overwrites (not merely
  rejects) a forged value supplied at a lower-priority tier with the
  authoritative one.
- **Transport varies by surface, the credential does not.** The same
  signed attestation appears as: the `BUZZ_AUTH_TAG` env var (CLI, ACP
  harness, MCP subprocess, Kubernetes pod); an `auth` tag on a signed
  Nostr event (WebSocket AUTH, git's NIP-98 request event); or an
  `x-auth-tag` HTTP header (bridge API, git smart HTTP, when no event tag
  is available). `buzz-cli` additionally accepts a hand-typed, unquoted
  bracket shorthand at its own configuration-input edge only, normalizing
  it to strict JSON before the shared strict parser ever sees it.
- **A ban cascades from owner to agent, never the reverse.** The relay's
  connection-auth ban gate checks the authenticated pubkey directly, then
  falls back to its NIP-OA-proven owner; banning only the agent does not
  ban the owner or its other agents.

## Boundary

This node does not describe:
- **How the mechanism is built** — the container/component architecture
  (which crates exist, how they depend on each other) is
  `architecture-containers-agent-runtime`'s territory, not this node's.
- **The interface(s) it is exposed through** — the concrete CLI flags, HTTP
  routes, and WebSocket message shapes belong to an interface node, not yet
  drafted for this capability.
- **The step-by-step path a single request or connection takes** — that is
  `architecture-flows-websocket-authentication` and
  `architecture-flows-git-push`'s territory; this node names the rules
  those flows implement, not the sequence of steps.
- **How the running relay or its hosts are operated** — deployment,
  monitoring, and incident response for any of these components are outside
  this node.
- **The NIP-OA protocol specification itself** — this node documents how
  Buzz implements and uses it, not the spec text.

## Relationships

- references: `architecture-context-ai-agent` — the actor (an AI agent) this
  capability authenticates and authorizes.
- references: `architecture-flows-websocket-authentication` — the flow where
  the WebSocket variant of this attestation is verified and its ban/
  membership cascade runs.
- references: `architecture-flows-git-push` — the flow where the git-push
  HTTP variant of this attestation is verified.
- references: `architecture-containers-agent-runtime` — the container
  (the ACP harness) that resolves, forwards, and depends on this
  attestation at runtime.

## Scope and omissions

**This node covers** what the `BUZZ_AUTH_TAG` / NIP-OA owner-attestation
capability lets an agent, an owner, and a relay each do; its current
maturity; the behavioral rules and transport variants that hold across every
consumer this node examined (ACP harness, `buzz-cli`, relay WebSocket auth,
relay HTTP bridge, relay git transport, identity archival, git signing and
git credentials, and two independent host launchers); and its boundary
against the architecture, interface, flow and operations material that
documents the same subject from other angles.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The container/component architecture realizing this capability | `architecture-containers-agent-runtime` |
| The step-by-step WebSocket-auth and git-push flows | `architecture-flows-websocket-authentication`, `architecture-flows-git-push` |
| A dedicated interface node for the CLI/HTTP/WebSocket surfaces this attestation flows through | not yet drafted |
| The NIP-OA protocol specification itself, beyond how Buzz implements it | out of scope for a capability node |
| Whether `buzz-dev-mcp`'s own direct read of `BUZZ_AUTH_TAG` (`crates/buzz-dev-mcp/src/view_image.rs`) needs its own documentation, versus being folded into this capability's forwarding behavior | future corpus task |

**Expected but not verified when this node was written:**
- **`crates/buzz-relay/src/api/relay_members.rs`** (the module owning
  `enforce_relay_membership` / `extract_nip_oa_owner` /
  `materialize_nip_oa_owner`, called from every relay consumer cited above)
  was referenced but not opened directly for this node; its behavior is
  described only as `crates/buzz-relay/src/handlers/auth.rs`'s and
  `crates/buzz-relay/src/api/git/transport.rs`'s own call sites and comments
  present it, not from reading that module's own implementation.
- **`sprout-backend-blox`**, the private Blox workstation-agent provider
  referenced in root `AGENTS.md`'s ecosystem table as a consumer of this
  same environment-injection contract, is a separate repository this node
  could not read; only the OSS `crates/buzz-backend-kubernetes` launcher was
  verified directly.
- **The relationship enums in `node.schema.json` and
  `relationships.schema.json`** were read, but the test asserting they never
  drift apart was not re-run for this node specifically.
