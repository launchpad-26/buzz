---
id: capabilities-agents-agent-owner
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "NIP-OA defines an optional four-element `auth` tag (`[\"auth\", <owner-pubkey-hex>, <conditions>, <sig-hex>]`) by which an owner key authorizes an agent key to publish events under the agent's own authorship; the event remains authored by `event.pubkey` (the agent), and clients MUST NOT treat the auth tag as an identity override or merge the event into the owner's own timeline."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md:9"
      - "docs/nips/NIP-OA.md:17"
      - "docs/nips/NIP-OA.md:86-89"
  - statement: "NIP-OA's signing preimage is `\"nostr:agent-auth:\" || agent_pubkey_hex || \":\" || conditions`, signed by the owner's BIP-340 Schnorr key over its SHA-256 hash; self-attestation (owner pubkey equal to agent pubkey) is rejected at both signing and verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:109-116"
      - "crates/buzz-sdk/src/nip_oa.rs:146-166"
      - "crates/buzz-sdk/src/nip_oa.rs:179-236"
  - statement: "The `users` table carries a nullable `agent_owner_pubkey BYTEA` column with a composite foreign key on `(community_id, agent_owner_pubkey)`, and a `channel_add_policy` enum (`anyone`, `owner_only`, `nobody`) governing whether a third party may add the agent to a channel."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:37"
      - "migrations/0001_initial_schema.sql:168-173"
  - statement: "`buzz-db`'s `set_agent_owner` sets `agent_owner_pubkey` only when it is currently NULL (an atomic conditional UPDATE, first-mint-wins with no TOCTOU race), and `is_agent_owner` answers whether a given actor pubkey is the recorded owner of a given target pubkey by querying that column directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/user.rs:293-327"
      - "crates/buzz-db/src/store/user.rs:356-371"
  - statement: "The relay's `extract_nip_oa_owner` verifies a request's NIP-OA `auth` tag against the requesting agent's pubkey and, on success, `materialize_nip_oa_owner` persists the agent-to-owner mapping via `set_agent_owner` (or confirms an existing mapping names the same owner via `is_agent_owner`) -- opportunistic backfill available even on open relays, since the NIP-OA signature is self-proving and needs no feature flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:156-169"
      - "crates/buzz-relay/src/api/mod.rs:176-225"
  - statement: "The relay enforces `channel_add_policy: owner_only` by denying a third-party channel-add request unless the actor's pubkey matches the target agent's recorded `agent_owner_pubkey`, and denies it outright under `channel_add_policy: nobody` regardless of actor."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:421-448"
  - statement: "The relay lets an actor edit a message they did not author only when `is_agent_owner` confirms the actor is the recorded owner of the message's author pubkey -- \"allow the owning human to edit messages authored by their agent\"; every other non-author edit attempt is denied."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1206-1214"
  - statement: "The git smart-HTTP push-policy handler grants `MemberRole::Owner` repository authority to a pusher who is either the announcing repo's own pubkey or a pubkey `is_agent_owner` confirms owns the announcing pubkey -- \"a cryptographically verified managed-agent owner has the same repository authority as the agent key itself\" -- independent of that owner's own channel membership role."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs:339-365"
  - statement: "`buzz-cli`'s `agents draft-create` and `agents draft-update` subcommands require `BUZZ_AUTH_TAG` (parsed by `require_owner` into the owner pubkey from the NIP-OA auth tag), build an encrypted `agent_management_request` observer-frame event addressed to that owner, publish it as an ephemeral event, and report back `{request_id, action, saved: false}` with the message \"Draft sent to Buzz Desktop for owner review. Nothing changes until the owner saves it.\" -- the agent proposes; only the human owner's Desktop client applying the request changes anything."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/agents.rs:12-44"
      - "crates/buzz-cli/src/commands/agents.rs:172-177"
      - "crates/buzz-cli/src/agent_management.rs:102-142"
  - statement: "`BuzzClient::auth_tag_owner_hex` reads the owner pubkey out of index 1 of the configured NIP-OA `auth` tag (`[\"auth\", owner_pubkey, conditions, sig]`), and `sign_event` injects that same tag onto every event the CLI signs, enforcing that at most one `auth` tag ever reaches a signed event."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:571-598"
  - statement: "Root `VISION_PROJECTS.md` frames NIP-OA as the mechanism by which \"agents inherit access from their owner\": a git push is accepted if it carries a valid NIP-OA auth tag naming an owner pubkey already present in the repository's `push-allowed` list, so adding or removing a maintainer adds or instantly revokes every agent that maintainer owns, without editing the agents' own identities."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:39"
  - statement: "Root `VISION_PROJECTS.md` also frames agent ownership as a reputation mechanism: \"the agent's reputation is on the line with every contribution,\" and NIP-OA is described as \"the owner attestation mechanism that proves which human authorized which agent -- independent keys, contained blast radius.\""
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:148"
  - statement: "`architecture-context-ai-agent`, already merged on `origin/launchpad`, names a \"Human owner\" actor (\"every managed AI agent identity is declared with an owning human... the owner is who the agent acts on behalf of\") and explicitly records, in its own Scope and omissions table, an unfilled gap: \"Whether/how a human reviews or approves an agent-originated event before it reaches other users -- no such gate was found in the sources opened for this node... A gap.\" This capability node is written to close exactly that named gap for the owner-reviewed-draft path; it does not claim to close it for every agent-originated event."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/ai-agent.md"
  - statement: "NIP-PMA's private managed-agent wire codec (`crates/buzz-core/src/private_managed_agent.rs`) separately requires that the outer signed event's `pubkey` equal an `expected_owner` key before the encrypted payload is decrypted, and that the decrypted payload's own `owner_pubkey` field match both the signing key and the outer envelope -- a second, independent place where an owner key gates an agent's data, encrypting the agent's configuration/secrets rather than attesting to the agent's public authorship."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/private_managed_agent.rs:262-269"
      - "crates/buzz-core/src/private_managed_agent.rs:341-357"
  - statement: "Whether NIP-PMA's owner-gated encryption and this node's NIP-OA/`agent_owner_pubkey`-based ownership model are meant to converge on one \"owner\" concept, or are deliberately two independent mechanisms that happen to share a key role, was not settled by any source opened for this node -- named as a gap rather than resolved here."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/private_managed_agent.rs:1-5"
      - "docs/nips/NIP-OA.md:9-24"
    confidence: 0.55
  - statement: "The NIP-OA sign/verify round trip and self-attestation rejection are unit-tested (`test_sign_then_verify_round_trip`, `test_reject_self_attestation`); `agent_owner_pubkey`'s owner_only-with-no-owner behavior is covered by a Postgres-gated test (`test_owner_only_with_no_owner`) marked `#[ignore = \"requires Postgres\"]`, so it runs under `just test` but not under `just test-unit`."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs:335-349"
      - "crates/buzz-sdk/src/nip_oa.rs:367-385"
      - "crates/buzz-db/src/store/user.rs:762-782"
---

# Agent owner: capability

Every AI agent identity in Buzz has at most one owner: a human (or other principal)
whose pubkey is cryptographically bound to the agent's pubkey, and who holds
exclusive authority to review and approve certain lifecycle actions the agent
proposes -- above all, creating or updating the agent's own definition -- before
those actions take effect. An agent can act autonomously inside the bounds already
granted it, but it cannot mint or change its own identity, and it cannot silently
gain access some other principal did not extend to it: access, editing rights, and
channel-add rights it holds "as itself" are separate from the access it inherits
because someone owns it.

## Maturity

**Shipped.** The cryptographic attestation (NIP-OA `auth` tag, `crates/buzz-sdk/src/
nip_oa.rs`), the persisted relationship (`agent_owner_pubkey` on the `users` table,
`migrations/0001_initial_schema.sql:168-173`), and its enforcement points (channel-add
policy, message-edit-by-owner, git push authority) are all implemented, and the
sign/verify round trip, self-attestation rejection, and owner_only-with-no-owner
behavior are each unit-tested (`crates/buzz-sdk/src/nip_oa.rs:335-349,367-385`,
`crates/buzz-db/src/store/user.rs:762-782` -- the last is Postgres-gated and does not
run under `just test-unit`). The owner-reviewed draft flow (`buzz agents
draft-create`/`draft-update`) is also implemented end to end in `buzz-cli`. This
node makes no claim about the corresponding Buzz Desktop review/approval UI beyond
what the CLI-side response message states it does (`"Draft sent to Buzz Desktop for
owner review"`) -- the Desktop-side application of an approved draft was not opened
for this node (see *Scope and omissions*).

## Boundary

This node does not describe:
- **How ownership is implemented at the protocol/wire level.** NIP-OA's tag format,
  signing preimage, and verification algorithm are `docs/nips/NIP-OA.md`'s own
  specification; this node cites it rather than restating it.
- **The interface(s) an owner or agent uses to exercise this capability** (the
  `buzz agents draft-create`/`draft-update` CLI subcommands, or any future HTTP/event
  surface) -- no `interfaces-events`-type corpus node exists yet to reference.
- **The step-by-step flow of a draft request reaching Buzz Desktop and an owner
  approving or rejecting it** -- that is a flow-level node, not yet authored.
- **How the running system is operated** (deploying, monitoring the relay) -- an
  `operations`-type concern, not this capability's subject matter.
- **NIP-PMA's private managed-agent encryption** (`crates/buzz-core/src/
  private_managed_agent.rs`) -- a related but distinct concept, in which an owner key
  gates decryption of an agent's own configuration/secrets rather than attesting to
  the agent's public authorship. It is named in this node's evidence ledger as a
  second, independent mechanism, not folded into this node's own claims.

## Relationships

- references: architecture-context-ai-agent
- references: architecture-containers-cli
- references: architecture-flows-git-push

`architecture-context-ai-agent` already names the "Human owner" actor and the exact
gap ("whether/how a human reviews or approves an agent-originated event") this node
addresses for the draft-review path. `architecture-containers-cli` documents the
`buzz-cli` ownership boundary and NIP-OA auth-tag mechanics this capability's
enforcement depends on. `architecture-flows-git-push` documents one concrete
enforcement point -- managed-agent-owner git push authority -- in flow-level detail
this node deliberately does not repeat. All three are merged on `origin/launchpad` at
the recorded revision (confirmed via `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` before this front matter was finalized), so all three targets
resolve.

## Scope and omissions

**This node covers** the agent-owner capability as a product-level concept: what it
means for an agent to have an owner, the cryptographic mechanism (NIP-OA) that
establishes and proves that relationship, the persisted relationship
(`agent_owner_pubkey`) the relay checks against, the concrete places that check is
enforced (channel-add policy, message-edit-by-owner, git push authority), and the
owner-reviewed draft-request path (`buzz agents draft-create`/`draft-update`) through
which an agent proposes changes to its own identity that only its owner can commit.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-OA's wire format and verification algorithm in full | `docs/nips/NIP-OA.md` |
| The CLI/interface surface for exercising this capability | An `interfaces-events`-type corpus node, not yet authored |
| The step-by-step draft-review flow (agent proposes, Desktop displays, owner approves/rejects) | A `flow`-type corpus node, not yet authored |
| NIP-PMA's owner-gated private managed-agent encryption | A separate capability or component node, not yet authored |
| How the running system is operated | The `operations` corpus surface |
| Front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **The Buzz Desktop-side application of an approved draft** (how `openCreateAgentEvent`/
  `openEditAgentEvent`'s consuming UI actually turns an owner's approval into the
  agent's live identity/config) was located (`desktop/src/features/agents/
  openCreateAgentEvent.ts`) but its full review-and-save implementation was not opened
  for this node -- the claim above rests on the CLI-side response message and the
  desktop-managed-agent skill prompt (`desktop/src-tauri/src/managed_agents/
  nest_skill.md`), not on reading the Desktop review dialog's own code.
- **Whether NIP-PMA's owner-gated encryption and this node's ownership model are
  meant to be the same "owner" concept enforced twice, or two deliberately independent
  mechanisms**, was not resolved -- see the `INFERENCE` entry in the evidence ledger
  above.
- **The `push-allowed` list mechanism `VISION_PROJECTS.md:39` describes** (where it is
  stored, how it is administered) was read only from that document's own product-level
  framing, not traced into `crates/buzz-relay/src/api/git/policy.rs`'s full
  implementation beyond the `is_agent_owner` check cited above.
