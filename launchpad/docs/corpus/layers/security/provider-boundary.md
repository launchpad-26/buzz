---
id: layers-security-provider-boundary
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "docs/remote-agents.md is a merged formal specification whose System Model names the provider binary (`buzz-backend-<id>`) as principal P, states P is 'Untrusted by D for everything except the job it is explicitly given (deploying the agent, which requires the key)', and that 'All of P's output is treated as hostile'."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's Non-Goals section states this boundary's honest limit explicitly: 'A provider binary receives the agent's nsec by design -- that is its job. The protocol bounds the desktop's exposure ... but cannot make a hostile provider safe.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's Discovery section states a normative pre-secret negotiation gate: the deploy path MUST resolve the provider id once, copy the resolved candidate into a desktop-owned private staging file while computing its digest, invoke `info` on the staged artifact, validate an explicit supported `protocol_version`, invoke `deploy` on that same staged artifact, and delete it afterward -- and that a UI-time probe result MUST NOT satisfy this gate."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md states invariant I2, 'No secrets in configuration': `provider_config` MUST NOT carry secrets, enforced by validation that requires a flat object of scalar values, at most 20 fields, at most 64KB, and rejects any key whose word-split contains secret|password|token|key|credential; secrets flow exclusively inside the `deploy` payload's identity fields, which are never persisted or rendered by the desktop."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's deploy section states the reserved-key rule: the desktop strips BUZZ_PRIVATE_KEY, NOSTR_PRIVATE_KEY, BUZZ_AUTH_TAG, BUZZ_RELAY_URL and other reserved keys from `env_vars` before merge, and a provider MUST construct the agent environment's identity variables from the top-level payload fields (private_key_nsec, auth_tag, relay_url), never from `env_vars` -- reading `env_vars` for them yields an identityless agent."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "`stage_provider` in `desktop/src-tauri/src/managed_agents/backend.rs` copies the resolved provider binary into a private temporary directory while hashing the exact bytes copied with SHA-256, then sets the staged file to execute-only permissions (mode 0o500 on Unix; read-only plus a share-mode execution guard on Windows) before either invocation -- implementing the staged-artifact-identity guarantee docs/remote-agents.md's Discovery section names."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs"
  - statement: "`provider_deploy` in `backend.rs` stages the binary once via `stage_provider`, invokes `info` on the staged path, calls `validate_provider_info` (which requires the response's `protocol_version` to equal the desktop's own `PROVIDER_PROTOCOL_VERSION` constant, currently 1, and errors otherwise), and only then invokes `deploy` on that same staged path -- implementing the pre-secret negotiation gate end to end."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs"
  - statement: "`validate_provider_config` in `backend.rs` rejects any `provider_config` key whose word-split (on separators and camelCase boundaries) contains secret, password, token, key or credential as a whole word, and rejects any field whose value is an object or array -- the code implementing I2's key-name lint and scalar-only rule."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs"
  - statement: "`invoke_provider` in `backend.rs` passes every value collected by `env_secrets_from_request` (from the deploy request's agent.env_vars, launch.env, and launch.policy_env maps) plus fixed nsec1.../sprt_tok_.../GitHub-token-shaped prefixes through `redact_secrets_with` before returning stderr snippets or an in-band `{\"ok\": false}` error string to its caller -- provider output is never returned to the caller unscrubbed."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs"
  - statement: "`resolve_provider_binary` in `backend.rs` is documented as the only way desktop code resolves a provider id for execution: it validates the id against `^[a-z0-9][a-z0-9_-]*$` and rejects anything else, then looks the id up only among `discover_provider_candidates()` (PATH- and known-directory-derived), never accepting a raw path -- closing the path-traversal/arbitrary-binary-steering route a compromised frontend/IPC caller could otherwise take."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs"
  - statement: "`RESERVED_ENV_KEYS` in `desktop/src-tauri/src/managed_agents/reserved_env_keys.rs` enumerates identity/secret keys (BUZZ_PRIVATE_KEY, NOSTR_PRIVATE_KEY, BUZZ_AUTH_TAG, BUZZ_API_TOKEN, BUZZ_ACP_PRIVATE_KEY, BUZZ_ACP_API_TOKEN, BUZZ_RELAY_URL, and others) that a persona/agent's user-supplied env_vars cannot override, and the file's own header comment states it is `include!`d into both `build.rs` (compile-time check) and `managed_agents/env_vars.rs` (save-time validation and spawn-time filtering) from one shared source specifically to prevent the two from drifting apart."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs"
  - statement: "`build_deploy_payload` in `desktop/src-tauri/src/commands/agents_deploy.rs` calls `crate::managed_agents::spawn_key_refusal(record)` and returns its error before building any provider payload; `spawn_key_refusal` in `desktop/src-tauri/src/managed_agents/storage.rs` returns a refusal whenever `record.private_key_nsec` is empty -- the identity-fail-closed check runs before anything is constructed for a provider, let alone sent."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents_deploy.rs"
      - "desktop/src-tauri/src/managed_agents/storage.rs"
  - statement: "`deploy_payload_json` in `agents_deploy.rs` sets the wire payload's `private_key_nsec`, `auth_tag` and (via `build_deploy_payload`'s `relay_url` argument) `relay_url` fields directly from the `ManagedAgentRecord`'s own top-level fields, never from `record.env_vars` or the merged user env -- the desktop-side half of the reserved-key rule."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents_deploy.rs"
  - statement: "`build_env` in `crates/buzz-backend-kubernetes/src/env.rs` clears every key named in `AUTHORITATIVE_KEYS` and then writes BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY, NOSTR_PRIVATE_KEY, BUZZ_AUTH_TAG and BUZZ_ACP_AGENT_OWNER strictly from the payload's top-level `relay_url`/`private_key_nsec`/`auth_tag`/`launch.owner_pubkey` fields, with a code comment stating 'Identity comes from top-level payload fields, never from `env_vars`' -- the reserved-key rule's realization in the one conforming provider binding."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs"
  - statement: "`backend_tests.rs`'s `provider_deploy_refuses_mismatch_before_sending_agent_secret` stages a provider whose `info` response declares an unsupported `protocol_version`, calls `provider_deploy` with a payload carrying `private_key_nsec: \"nsec1must-not-cross\"`, and asserts the call errors, that the marker file the stub provider would only create inside its `deploy` operation body never exists, and that the returned error text does not contain the nsec value -- the pre-secret negotiation gate's core property (the nsec is never sent to a version-mismatched provider) is pinned by an executing test, not merely asserted in prose."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs"
  - statement: "`backend_tests.rs`'s `provider_deploy_uses_staged_bytes_after_same_inode_source_rewrite` and `provider_deploy_uses_staged_bytes_after_source_pathname_replacement` each rewrite the resolved provider binary between staging and the `deploy` call -- one in place at the same inode, one via a pathname swap to a different inode -- and both assert `provider_deploy` still runs the originally staged bytes, pinning the staged-artifact-identity guarantee against both attack shapes docs/remote-agents.md's Discovery section names as insufficient for a path-plus-metadata check to catch."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs"
  - statement: "`backend_tests.rs`'s `validate_provider_config_rejects_secret_key`, `validate_provider_config_rejects_nested`, and `validate_provider_config_rejects_camel_case_secrets` exercise I2's key-name lint and scalar-only rule directly against `validate_provider_config`, and `resolve_provider_binary_rejects_invalid_ids` asserts rejection of a path-traversal id (`../evil`), an id containing shell metacharacters (`foo;rm -rf /`), and other malformed shapes."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs"
  - statement: "`crates/buzz-backend-kubernetes/src/env.rs`'s `lower_tiers_cannot_spoof_authoritative_values` test supplies attacker-controlled BUZZ_PRIVATE_KEY, NOSTR_PRIVATE_KEY, BUZZ_RELAY_URL, BUZZ_AUTH_TAG and other reserved keys via the payload's `launch.env` and `launch.policy_env` maps and asserts `build_env`'s output still carries only the top-level payload's real identity values -- the provider-side reserved-key realization is test-enforced, not merely structural."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs"
  - statement: "`desktop/src-tauri/src/managed_agents/storage_tests.rs` tests `spawn_key_refusal` directly: asserting it returns `Some` for a record with an empty `private_key_nsec` and `None` for a record with a populated one."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/storage_tests.rs"
  - statement: "docs/remote-agents.md's own 'Known Defects (at 28ae6cd21)' section, item 5, states that at that commit 'The deploy path never checks protocol_version' and that `provider_deploy` sends the nsec-bearing deploy request without any preceding `info` call on the same resolved executable -- but the current `backend.rs` at this node's recorded revision already implements resolve-once, stage-and-digest, `info`, explicit-version-check, `deploy` on the same staged bytes, and `git log` shows commit 6530b58a6 ('Implements docs/remote-agents.md (merged @ 28ae6cd21) as ONE PR') touched both `backend.rs` and `docs/remote-agents.md` without removing or updating that Known Defects entry -- the doc's defect list is stale on this specific point as of the revision this node was checked against."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
      - "desktop/src-tauri/src/managed_agents/backend.rs"
      - "commit 6530b58a6"
  - statement: "Issue #1171's Definition of Done requires this node to state the invariant as one unambiguous property using MUST/MUST NOT only where normative, explain its scope, name enforcement points and observable failure behavior, and link a verification/conformance mechanism or explicitly record that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1171 definition of done"
relationships:
  - type: implements
    target: corpus-template-invariant
---

# Provider boundary: invariant

**Every byte that crosses the desktop-to-provider process boundary — a
`buzz-backend-<id>` binary's resolved identity, its `info`/`deploy` output, and any
`provider_config` value a user supplies for it — MUST be treated by the desktop as
untrusted and constrained accordingly before it is trusted, sent, or persisted, with
exactly one deliberate exception: the `deploy` payload's identity fields
(`private_key_nsec`, `auth_tag`, `relay_url`) MUST be handed to the provider verbatim,
because receiving them to perform the deploy is the one job the protocol delegates to
it.** No `provider_config` field MUST carry secret-shaped material. No agent identity
value MUST ever be sourced from provider-supplied or provider-echoed data (a request's
`env_vars`, `launch.env`, `launch.policy_env`, or the provider's own stdout/stderr). No
request carrying the identity payload MUST be sent to a resolved provider binary until
that exact binary's declared protocol version has been checked on the identical staged
bytes that answered the check.

This is a security boundary in the ordinary sense: the desktop cannot make a hostile
provider safe (docs/remote-agents.md's own words), so what this invariant buys is not
"providers cannot see the key" — they can, by design — but that every other channel
through which a provider could widen its access, misdirect a deploy, or leak what it
was handed back to the desktop is closed structurally or caught by a test.

## Scope

**Applies to:** every invocation of a `buzz-backend-<id>` provider binary from the
desktop's managed-agent deploy path — provider discovery and id resolution, the `info`
and `deploy` wire operations, `provider_config` validation, and the handling of a
provider's stdout, stderr, and in-band `{"ok": false}` error responses.

**Applies for the lifetime of one `provider_deploy` call**, not across calls: each
invocation stages, hashes, and locks its own copy of the binary and discards it
afterward, so there is no persisted "trusted provider" state between deploys — every
deploy re-resolves and re-validates from scratch.

**Does not govern** what a provider does with the identity material once it has been
correctly and verifiably handed to it — see *Boundary* below.

## Enforcement today

Naming the weakest true tier per property, not rounding any of them up:

| Property | Tier | Evidence |
|---|---|---|
| `provider_config` MUST NOT carry secret-shaped keys or non-scalar values (I2) | **Test-enforced** | `validate_provider_config_rejects_secret_key`, `_rejects_nested`, `_rejects_camel_case_secrets` (`backend_tests.rs`) |
| The nsec is never sent to a provider whose declared protocol version is unsupported | **Test-enforced** | `provider_deploy_refuses_mismatch_before_sending_agent_secret` (`backend_tests.rs`) |
| The `deploy` request runs the exact bytes that answered `info`, surviving both an in-place rewrite and a pathname swap of the source binary | **Test-enforced** | `provider_deploy_uses_staged_bytes_after_same_inode_source_rewrite`, `provider_deploy_uses_staged_bytes_after_source_pathname_replacement` (`backend_tests.rs`) |
| A provider id cannot be a path-traversal or shell-metacharacter string | **Test-enforced** | `resolve_provider_binary_rejects_invalid_ids` (`backend_tests.rs`) |
| Identity fail-closed: no deploy payload is built for a record with an empty key | **Test-enforced** | `spawn_key_refusal` tests (`storage_tests.rs`) |
| Provider-side identity comes only from top-level payload fields, never from a lower-tier env map, even when that map spoofs the reserved keys | **Test-enforced** (in the one conforming binding) | `lower_tiers_cannot_spoof_authoritative_values` (`crates/buzz-backend-kubernetes/src/env.rs`) |
| Desktop-side identity payload fields are read only from the record's own fields | **Structurally enforced** — `deploy_payload_json` has no code path reading `private_key_nsec`/`auth_tag`/`relay_url` from `env_vars` or the merged user env | `agents_deploy.rs` |
| Provider stdout/stderr/error text is redacted before being returned to any caller | **Structurally enforced**, with one end-to-end assertion — `invoke_provider` routes every return path through `redact_secrets_with`; `provider_deploy_refuses_mismatch_before_sending_agent_secret` additionally asserts a real nsec value is absent from one such returned error | `backend.rs`, `backend_tests.rs` |
| `RESERVED_ENV_KEYS` cannot drift between the desktop's build-time and save/spawn-time checks | **Structurally enforced** — both consumers `include!` the same source file | `reserved_env_keys.rs` |

No dedicated conformance suite exercises this boundary against a real `buzz-backend-*`
binary end to end (the way `conformance_multitenant.rs` does for the community
boundary) — every property above is verified through `backend.rs`'s own unit tests
using a stub shell-script provider, or through `buzz-backend-kubernetes`'s own unit
tests of its env-building function. That is a real, stated verification gap, not a
claim this node makes about a missing property: see *Scope and omissions*.

## Observable failure behavior

Each enforced check fails closed with a specific, non-generic error string returned to
the caller (all read directly from `backend.rs` and `storage.rs`):

- Unsupported or missing protocol version: `"unsupported provider protocol version
  {version}; desktop requires {PROVIDER_PROTOCOL_VERSION}"`, or `"provider info
  response missing integer protocol_version"` when the field is absent entirely
  (`validate_provider_info`).
- A `provider_config` key that lints as secret-shaped: `"provider_config: key '{}'
  looks like a secret"` (`validate_provider_config`).
- A non-scalar `provider_config` value: `"provider_config: value for '{}' must be a
  scalar"` (`validate_provider_config`).
- A malformed or path-traversal provider id: `"invalid provider ID '{provider_id}':
  must match [a-z0-9][a-z0-9_-]*"` (`resolve_provider_binary`).
- An empty identity key at payload-build time: `"agent {} has no private key available
  — the OS keyring may be unreachable. Refusing to start without an identity; retry
  once the keyring is reachable."` (`spawn_key_refusal`).
- Any non-zero provider exit, or a provider response body that fails JSON parsing:
  the caller receives a redacted stderr/error snippet capped at 4096 bytes, never the
  raw provider output (`invoke_provider`).

Unlike the community boundary's deliberately generic rejection (built to avoid leaking
which hosts exist), these errors are specific by design: the caller here is the
desktop's own deploy path and its user, not an unauthenticated network peer, so naming
exactly which check failed is diagnostic information rather than a probing surface.

## Consequence of violation

A version-mismatch or staged-bytes-identity failure that went uncaught would mean the
desktop hands a live `nsec` to a binary it has not confirmed speaks the wire contract
it is about to be sent, or to bytes different from the ones that answered `info` —
exactly the check-then-exec race docs/remote-agents.md's Discovery section calls out
by name. A `provider_config` secret-key-lint failure would mean a user-visible,
schema-rendered settings object could carry credential material the desktop persists
and displays in plaintext, defeating the "secrets flow exclusively inside the `deploy`
payload" design. A reserved-key-rule failure (desktop or provider side) would mean a
user-supplied `env_vars` entry could redirect a deployed agent's identity, relay, or
authorization — the identity-spoofing scenario `lower_tiers_cannot_spoof_authoritative_values`
exists specifically to rule out. An unredacted-output failure would mean a provider
that legitimately holds the nsec during deploy could propagate it into the desktop's
persisted `last_error` or logs simply by echoing it in a stack trace or a wrapped
`kubectl` error.

## Boundary

This node does not describe:

- **What a provider does with the identity material once correctly handed to it.**
  docs/remote-agents.md's Non-Goals section states this explicitly: "malicious-provider
  containment" is out of scope for the protocol, and choosing to run a provider is a
  trust decision the UI surfaces to the user, not one this protocol can make safe.
- **The Kubernetes binding's own deploy-state-machine, Secret-lifecycle, and
  garbage-collection mechanics** (docs/remote-agents.md's §Deploy State Machine,
  §K8s Secrets, §K8s GC) — a distinct concept about one provider's *substrate*
  behavior after a deploy call already crossed this boundary successfully, left for
  its own future node per the sibling plan that scoped
  `architecture/deployment/kubernetes.md`
  (`launchpad/plans/2026-08-27-issue-670-corpus-doc.md`'s own "LEFT OUT").
- **The remote-agent lifecycle invariants I3 (presence staleness), I4 (at-most-one-live-
  instance), and I5 (intentional-termination-is-final).** These are properties of the
  *deployed agent's* observable state and lifetime, not of the desktop-to-provider
  process boundary itself, and are the natural subject of this batch's sibling tasks
  on trust boundaries, the relay boundary, and secret management.
- **The `launch` block's six-layer environment resolution** (docs/remote-agents.md's
  §Launch data) beyond the one property this node cites (the reserved-key rule) — the
  full resolution precedence is an implementation-reference concern, not a boundary
  invariant.

## Relationships

- `implements`: `corpus-template-invariant` — this node follows the invariant
  template's required sections (Invariant statement / Scope / Enforcement today /
  Consequence of violation / Boundary / Relationships / Scope and omissions).

No `references` or `depends-on` edge is declared toward a topical neighbor: no other
`layers/` node is merged on `origin/launchpad` at this node's recorded revision — this
is the first — so, per `AGENTS.md`'s own guidance, "none" is the honest answer while
the corpus is being built out, not evidence that no such neighbor exists. The first
sibling `layers/security/*` node to merge (`trust-boundaries.md`, `relay-boundary.md`,
and `secret-management.md` are open sibling tasks in this same batch, #1168-#1192) is
the natural moment to add a `references` edge in whichever direction that node's own
authoring decides.

## Scope and omissions

**This node covers** the trust boundary between Buzz Desktop and a `buzz-backend-<id>`
provider binary: what crosses it, what the desktop MUST validate or redact before
trusting it, and the one deliberate exception (identity material, handed over by
design). It cites `buzz-backend-kubernetes` as the one conforming provider
implementation's realization of the provider-side half of this boundary, not as its own
subject.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Kubernetes binding's deploy-state-machine, Secret lifecycle, and GC | A future `architecture/deployment` or `layers` node scoped to `buzz-backend-kubernetes`'s substrate behavior |
| Remote-agent lifecycle invariants I3-I5 (presence, uniqueness, termination) | This batch's sibling tasks (`trust-boundaries.md`, `relay-boundary.md`, and related, #1168-#1192) |
| Whether a non-Kubernetes provider (e.g. the systemd/SSH deployer docs/remote-agents.md names as a live example) conforms to this same boundary | Not inspected — no such provider's source was found in this repository at the recorded revision |
| Full per-field precedence of the `launch` block's six-layer environment resolution | An implementation-reference node, if one is later scoped to `resolve_effective_harness_descriptor` |

**Expected but not verified when this node was written:**

- **No end-to-end conformance suite drives this boundary against a real
  `buzz-backend-*` binary the way `conformance_multitenant.rs` drives the community
  boundary against a live two-community relay.** Every property cited above is
  verified at the unit level, against a stub shell-script provider or a pure
  env-building function — real, but narrower than an integration-level guarantee.
- **Whether the "Known Defect 5" staleness noted in the evidence ledger reflects an
  intentional decision to keep that entry (e.g. because some residual gap remains)
  or a simple oversight in the commit that implemented the fix** was not determined —
  this node states only that current code implements and tests the gate the entry
  describes as missing.
- **Windows-specific behavior of `stage_provider`'s execution guard** (the
  `share_mode`-based lock in `backend.rs`) was read but not exercised — the test suite
  inspected covers the Unix-only staged-bytes-rewrite tests (`#[cfg(unix)]`).
