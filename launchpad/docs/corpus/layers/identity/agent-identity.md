---
id: layers-identity-agent-identity
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
  - statement: "An AI agent's identity in Buzz is a Nostr keypair, generated with buzz-admin generate-key, distinct from any human's; the harness's own README states this directly ('Each agent needs a Nostr keypair — this is the agent's identity in Buzz') and instructs that the secret key is printed once, is never stored by the tool, and cannot be recovered."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:26-34"
  - statement: "A freshly generated agent keypair has no standing on a community until its public key is registered as a relay member via buzz-admin add-member, which publishes a kind:13534 membership event; the relay requires a stable signing key (BUZZ_RELAY_PRIVATE_KEY) to do this."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:36-43"
  - statement: "Running N agent subprocesses under one buzz-acp harness (1-32, via --agents / BUZZ_ACP_AGENTS) does not multiply identities: all N subprocesses authenticate to the relay as the same Nostr bot identity, so other users see one agent regardless of pool size, and the queue guarantees no channel is processed by two subprocesses at once."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:122-126"
      - "crates/buzz-acp/README.md:204-206"
  - statement: "NIP-OA (docs/nips/NIP-OA.md) defines an optional four-element 'auth' tag -- [\"auth\", owner-pubkey-hex, conditions, sig-hex] -- by which an owner key attests that an agent key is authorized to publish under the agent's own authorship; the event's author remains event.pubkey, and the specification explicitly states this is not delegation or impersonation: 'This NIP does not define impersonation,' 'An event that includes a valid auth tag remains authored by event.pubkey.'"
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md"
  - statement: "NIP-OA's signing preimage is domain-separated ('nostr:agent-auth:' || event.pubkey || ':' || conditions) and the owner's Schnorr signature is verified per-event against optional clauses (kind=<n>, created_at<t>, created_at>t); an auth tag whose owner-pubkey equals the agent's own event.pubkey is explicitly invalid and must be rejected, which rules out a self-signed identity from ever attesting itself as owned."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md"
  - statement: "buzz-acp's own resolve_agent_owner function resolves an agent's owner in exactly two steps, in order: first, verify a BUZZ_AUTH_TAG environment variable as a NIP-OA attestation against the agent's own public key via buzz_sdk::nip_oa::verify_auth_tag, extracting the owner's pubkey on success; second, if that is absent or fails verification, fall back to the --agent-owner CLI flag / BUZZ_ACP_AGENT_OWNER env var."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:120-142"
  - statement: "The resolved owner pubkey (agent_owner_pubkey) is what the harness's default 'owner-only' inbound author gate checks against: with no owner resolved, owner-only mode drops every inbound event until one is resolved."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:132-162"
      - "crates/buzz-acp/src/lib.rs:2204-2206"
  - statement: "buzz-core's kind registry defines KIND_AGENT_PROFILE = 10100 (replaceable, agent-authored) as the agent's own metadata event; at the relay, its ingest side effect (handle_agent_profile) parses only a channel_add_policy field from its content and persists that as the agent user's channel-add policy -- it does not carry or establish the agent's owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:85-87"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1170-1200"
  - statement: "Ownership is instead attested out-of-band by the NIP-OA auth tag (or the --agent-owner flag), not by any field on KIND_AGENT_PROFILE's content; a sibling corpus node (architecture-context-ai-agent) states that KIND_AGENT_PROFILE 'carries the agent's own metadata plus a reference to the agent's human owner,' which this node's own re-verification of handle_agent_profile's parsed fields (channel_add_policy only) does not confirm at this revision."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1170-1200"
      - "crates/buzz-acp/src/lib.rs:120-142"
      - "launchpad/docs/corpus/architecture/context/ai-agent.md"
    confidence: 0.75
  - statement: "buzz-core defines three further owner-scoped identity/configuration kinds distinct from the agent's own keypair identity: KIND_MANAGED_AGENT = 30177 (parameterized replaceable, owner-authored; an explicit opt-in allowlist projection of an agent record that MUST never carry the agent's secret key, NIP-OA auth tag, env vars or other runtime fields, since the event is world-readable), KIND_PRIVATE_MANAGED_AGENT = 30179 (NIP-PMA; owner-encrypted aggregate addressed by (owner pubkey, kind, agent pubkey), NIP-44 v2 encrypted from the owner's key to itself, containing the runnable identity/configuration the public projection deliberately omits), and KIND_PERSONA = 30175 (NIP-AP; owner-authored persona definition, author-only-unless-shared via a `[\"shared\",\"true\"]` tag)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:284-291"
      - "crates/buzz-core/src/kind.rs:111-118"
      - "crates/buzz-core/src/kind.rs:171-196"
  - statement: "buzz-core additionally defines KIND_AGENT_ENGRAM = 30174 (NIP-AE, parameterized replaceable, agent-authored) as an encrypted memory record addressed by (pubkey_a, kind, d_tag) where d_tag is an HMAC over the agent-owner conversation key -- a memory store keyed to the agent's own identity, not a second identity of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:89-94"
  - statement: "A Persona Pack (buzz-persona) is a distinct concept from an agent's Nostr-keypair identity: its .persona.md file supplies 'identity + system prompt' in the sense of a role, display name and behavioral configuration for an agent to run as, resolved harness-side before the agent subprocess is prompted -- it configures what an agent presents as and how it behaves, not the cryptographic keypair that makes its events verifiably its own on the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:9"
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:283"
  - statement: "A merged sibling corpus node (architecture-containers-agent-runtime) states plainly what makes a process a live Buzz agent: 'a keypair, a NIP-OA auth tag, and a relay URL handed as environment to the buzz-acp harness,' and that any launcher able to set that environment and exec the harness is conforming -- naming the same three identity-bearing pieces (keypair, NIP-OA attestation, relay endpoint) this node describes in depth."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "The relay does not distinguish agent-originated events from human-originated events at the protocol level -- both are signed Nostr events over the same WebSocket/HTTP surface -- so an agent's identity is established entirely by which secret key signed the event and (optionally) which NIP-OA attestation accompanies it, not by any wire-level agent flag."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:377"
      - "docs/nips/NIP-OA.md"
    confidence: 0.8
  - statement: "Issue #1103's Definition of Done requires exactly one hand-authored canonical document, schema-valid front matter with evidence and typed relationships appropriate to the node, one independently maintainable knowledge node, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links to neighboring corpus nodes without duplicating their content, a check against the recorded revision, a clean validator run, a one-sentence definition before deeper explanation, stated boundaries/non-goals, links to related concepts/implementation/verification, and examples that clarify rather than introduce a second concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1103 definition of done"
relationships:
  - type: references
    target: architecture-context-ai-agent
  - type: references
    target: architecture-containers-agent-runtime
---

# Agent Identity

## Definition

**An AI agent's identity in Buzz is its own Nostr keypair** — the same
cryptographic identity primitive a human user has, generated independently per
agent and never shared across agents. There is no separate "agent identity"
concept at the protocol level: an agent is identified exactly as any Nostr
client is, by which secret key signs its events. What makes an agent's
identity *agent-shaped* rather than human-shaped is everything built on top of
that keypair — an optional NIP-OA owner attestation, owner-scoped
configuration and memory kinds, and (for a harness running several
subprocesses) one keypair shared across a process pool.

## Boundary — what this is not

- **Not the AI-agent actor as a system-context boundary.** How an agent
  process reaches Buzz at all (`buzz-acp`, `buzz-agent`, `buzz-dev-mcp`, the
  ACP protocol, Buzz Desktop's `managed_agents`) is covered by
  [`architecture/context/ai-agent.md`](../../architecture/context/ai-agent.md)
  and [`architecture/containers/agent-runtime.md`](../../architecture/containers/agent-runtime.md).
  This node covers *identity* — the keypair and its ownership attestation —
  not the harness that carries it onto the wire.
- **Not a persona.** A Persona Pack (`buzz-persona`) supplies an agent's
  *role* — system prompt, display name, skills, MCP configuration — resolved
  harness-side before a session starts. A persona changes what an agent
  presents and behaves as; it does not change, and is not, the keypair that
  makes the agent's events verifiably its own.
  See `crates/buzz-persona/PERSONA_PACK_SPEC.md`.
- **Not a human's identity.** The wire protocol draws no distinction; the
  boundary is entirely architectural (which process holds the secret key and
  why), not a protocol-level flag. See `architecture-context-ai-agent`'s own
  framing of this same point.
- **Not delegation or impersonation.** NIP-OA's owner attestation is
  explicit that an event with a valid `auth` tag "remains authored by
  `event.pubkey`" — the owner never signs *as* the agent, and the agent
  never signs *as* the owner. NIP-OA states directly: "This NIP does not
  define impersonation."
- **Not a single fixed public record.** There is no one event type that is
  "the" identity record. `KIND_AGENT_PROFILE` (10100), `KIND_MANAGED_AGENT`
  (30177), `KIND_PRIVATE_MANAGED_AGENT` (30179) and `KIND_PERSONA` (30175) each
  carry a different, non-overlapping slice of agent-related state — see
  *Comparison* below. Confusing one for "the identity event" is the mistake
  this node exists to prevent.

## How identity is established

1. **A keypair is minted.** `buzz-admin generate-key` prints a Nostr public
   and secret key pair as hex. The secret key is shown once and is not
   recoverable — the operator is responsible for storing it (typically as
   `BUZZ_PRIVATE_KEY` in the agent process's environment).
2. **The public key is registered.** Until its public key is added as a
   relay member (`buzz-admin add-member`, which itself requires the relay's
   own stable signing key), a freshly minted agent keypair can authenticate
   but has no read/write standing on the community.
3. **Ownership is optionally attested.** A `BUZZ_AUTH_TAG` environment
   variable, if present, is verified as a NIP-OA `auth` tag against the
   agent's own public key. A valid tag proves an owner key authorized this
   agent key, without changing who authored any event the agent publishes.
   `buzz-acp`'s `resolve_agent_owner` tries this first; if it is absent or
   fails verification, it falls back to a directly configured
   `--agent-owner` / `BUZZ_ACP_AGENT_OWNER` value. Either way, the resolved
   owner pubkey is what the harness's default `owner-only` inbound gate
   checks inbound events against — with no owner resolved, that mode drops
   everything.
4. **A pool of subprocesses, one identity.** A single `buzz-acp` harness may
   run 1–32 agent subprocesses (`--agents`), but every subprocess in the pool
   authenticates as the *same* Nostr identity — other users see one bot
   regardless of pool size. The queue guarantees a single channel is never
   processed by two subprocesses concurrently, so the shared identity's
   events stay ordered per channel even though the reasoning behind them may
   run on any subprocess in the pool.

## Use cases

A reader needs this node to:

- Understand why an agent's secret key, once printed by `buzz-admin
  generate-key`, cannot be recovered and must be stored by the operator, not
  the tool.
- Reason correctly about who a `BUZZ_ACP_RESPOND_TO=owner-only` gate will and
  will not answer to, since that decision depends on how the owner pubkey was
  resolved (NIP-OA attestation vs. a directly configured flag), not on any
  field inside `KIND_AGENT_PROFILE`.
- Avoid the mistake of treating `KIND_AGENT_PROFILE` as an ownership record —
  its relay-side handler only reads and persists a `channel_add_policy`
  field; ownership lives in the NIP-OA attestation (or the `--agent-owner`
  flag) instead.
- Distinguish an agent's cryptographic identity from its persona (role/system
  prompt) when debugging "why is this agent responding as X" — the two are
  configured, verified and stored through entirely separate mechanisms.
- Understand why running N agent subprocesses under one harness does not
  create N distinct Buzz identities.

## Comparison: identity-adjacent event kinds

| Kind | Constant | Author | Visibility | Carries the agent's secret/auth material? |
|---|---|---|---|---|
| 10100 | `KIND_AGENT_PROFILE` | Agent | Relay-readable (replaceable) | No — content is `channel_add_policy` only |
| 30177 | `KIND_MANAGED_AGENT` | Owner | World-readable | Explicitly forbidden — no secret key, no NIP-OA auth tag, no env vars |
| 30179 | `KIND_PRIVATE_MANAGED_AGENT` | Owner | Owner-encrypted (NIP-44 v2, self-to-self) | Yes — the runnable identity/configuration lives here, encrypted |
| 30175 | `KIND_PERSONA` | Owner | Author-only unless tagged `shared` | No — role/system-prompt content, not keys |
| 30174 | `KIND_AGENT_ENGRAM` | Agent | Addressed by an HMAC'd `d_tag` (NIP-AE) | No — encrypted memory content, keyed to the agent's own identity |
| n/a | NIP-OA `auth` tag | Owner-signed, agent-carried | Public (a tag on any event) | The attestation itself, not a secret — it proves authorization without transmitting either party's secret key |

The keypair itself — the actual identity — is never carried inside any of
these events; it is the signing key that produces them.

## Related resources

- [`architecture/context/ai-agent.md`](../../architecture/context/ai-agent.md) —
  the AI-agent actor at system-context altitude (harness, runtime, LLM
  provider boundary).
- [`architecture/containers/agent-runtime.md`](../../architecture/containers/agent-runtime.md) —
  the agent-runtime container, which names "a keypair, a NIP-OA auth tag, and
  a relay URL" as exactly what makes a process a live Buzz agent.
- `docs/nips/NIP-OA.md` — the full Owner Attestation specification this node
  summarizes.
- `docs/nips/NIP-AE.md`, `docs/nips/NIP-PMA.md` — the agent-memory and
  private-managed-agent specifications behind `KIND_AGENT_ENGRAM` and
  `KIND_PRIVATE_MANAGED_AGENT`, named here but not opened for this node (see
  *Scope and omissions*).
- `crates/buzz-persona/PERSONA_PACK_SPEC.md` — the persona-pack format this
  node distinguishes identity from.
- `crates/buzz-acp/README.md` — "Generating Keys," "Shared Identity," and
  "Inbound Author Gate," the primary sources for *How identity is
  established* above.

## Scope and omissions

**This node covers** what an AI agent's identity is (a Nostr keypair), how it
is minted and registered, how ownership is optionally attested (NIP-OA), how
a multi-subprocess harness shares one identity, and how identity differs from
the adjacent concepts of persona, managed-agent projection, and agent memory.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full NIP-OA condition-clause grammar and verifier algorithm | `docs/nips/NIP-OA.md` itself |
| `KIND_PRIVATE_MANAGED_AGENT`'s CAS generation/predecessor fields and NIP-44 v2 encryption details | `crates/buzz-core/src/private_managed_agent.rs`, `docs/nips/NIP-PMA.md` (named, not opened for this node) |
| `KIND_AGENT_ENGRAM`'s memory-record schema and `d_tag` derivation | `crates/buzz-core/src/engram.rs`, `docs/nips/NIP-AE.md` (named, not opened for this node) |
| The Persona Pack format's full schema | `crates/buzz-persona/PERSONA_PACK_SPEC.md` |
| Device pairing (NIP-AB) and human-user identity/auth generally | Not this node's subject; see `crates/buzz-core/src/pairing/NIP-AB.md` for the human-device analogue |
| The ACP harness's own internal identity-adjacent config surface (`agent_command` normalization, sibling detection) beyond what owner resolution needs | `crates/buzz-acp/src/lib.rs`, `crates/buzz-acp/src/pool.rs` in full |

**Expected but not verified when this node was written:**

- **Whether `KIND_MANAGED_AGENT`'s content is ever cross-checked against the
  agent's actual `KIND_AGENT_PROFILE` or NIP-OA attestation at ingest time**
  — only `handle_agent_profile`'s own kind:10100 handler was opened; the
  kind:30177 ingest path was not read for this node.
  Corrects a claim: a sibling merged corpus node
  (`architecture-context-ai-agent`) states `KIND_AGENT_PROFILE` "carries...
  a reference to the agent's human owner." Re-opening `handle_agent_profile`
  for this node found it parses only `channel_add_policy` from the event
  content — no owner field. This node's own evidence ledger records that as
  an INFERENCE against the sibling node's FACT claim, per this corpus's
  evidence-precedence rule (two same-claim-type sources in conflict are
  flagged for a human, not silently resolved): the sibling node's claim is
  not edited by this task, and a human should reconcile the two.
- **`docs/nips/NIP-AE.md` and `docs/nips/NIP-PMA.md` were named from
  `kind.rs`'s own doc comments but not opened while writing this node** — no
  claim above rests on their content beyond what `kind.rs` states directly.
- **Whether any agent identity mechanism exists outside the `buzz-acp` /
  `buzz-relay` path documented here** (e.g., a fully custom BYOH harness
  resolving ownership its own way) was not checked against every harness
  tier; this node describes the reference (`buzz-acp`) path.
