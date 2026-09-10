---
id: interfaces-nostr-buzz-nips-nip-ap
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "NIP-AP defines kind:30175 for agent persona definitions and kind:30178 for the team-catalog projection, both parameterized replaceable (30000-39999 per NIP-01), addressed by (pubkey, kind, d_tag) with only the latest event per address retained."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AP.md:11-13"
  - statement: "buzz-core/src/kind.rs declares KIND_PERSONA = 30175, KIND_TEAM = 30176, KIND_MANAGED_AGENT = 30177 and KIND_TEAM_CATALOG = 30178, and const-asserts each is inside the 30000-39999 parameterized-replaceable range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:196"
      - "crates/buzz-core/src/kind.rs:282"
      - "crates/buzz-core/src/kind.rs:291"
      - "crates/buzz-core/src/kind.rs:319"
      - "crates/buzz-core/src/kind.rs:856-859"
  - statement: "A persona event's content is a plaintext (unencrypted) JSON object; display_name is the only required field, and system_prompt, avatar_url, runtime, model, provider, name_pool, respond_to, respond_to_allowlist and parallelism are optional with stated defaults; the content MUST NOT carry an env_vars field or any other secret."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AP.md:58-117"
  - statement: "The spec marks respond_to, respond_to_allowlist and parallelism as reserved: parsed and preserved at the wire layer today, but not yet applied by the local definition store, and a definition carrying them does not survive a local edit-and-republish cycle until the create-path unification lands."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AP.md:93-109"
  - statement: "buzz-acp/src/config.rs defines respond_to and respond_to_allowlist fields on both its CLI-argument struct CliArgs (fields at lines 468/473) and its resolved runtime Config struct (fields at lines 569/571), matching the NIP's reserved instance-level default fields; no field literally named parallelism was found anywhere in that file."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:468"
      - "crates/buzz-acp/src/config.rs:473"
      - "crates/buzz-acp/src/config.rs:569"
      - "crates/buzz-acp/src/config.rs:571"
  - statement: "Standard NIP-33 replacement applies: for a given (pubkey, kind:30175, d_tag) the event with the greatest created_at is the head, ties broken by lowest event id (hex comparison); the spec's writing procedure sets created_at := max(now, T+1) where T is the current head's created_at, guaranteeing a fresh write always supersedes the prior head regardless of clock skew."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AP.md:127-129"
      - "docs/nips/NIP-AP.md:137"
      - "docs/nips/NIP-AP.md:376-378"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's validate_persona_envelope enforces the shared-tag shape plus exactly one d tag matching the persona slug grammar ^[a-z0-9][a-z0-9_-]{0,63}$; validate_team_catalog_envelope enforces the same shared-tag shape plus exactly one non-empty, length-bounded d tag but deliberately does NOT apply the slug grammar, because a team id (UUID or a built-in id such as builtin-team:welcome) legitimately contains characters, notably ':', the slug grammar forbids."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1486-1503"
      - "crates/buzz-relay/src/handlers/ingest.rs:1517-1522"
  - statement: "The relay enforces the shared tag's exact two-element shape (validate_shared_tag, called by both validate_persona_envelope and validate_team_catalog_envelope): a shared tag present with any value other than exactly [\"shared\",\"true\"], or more than one shared tag, is rejected at ingest with an invalid: error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1408-1445"
      - "crates/buzz-relay/src/handlers/ingest.rs:1486-1489"
      - "crates/buzz-relay/src/handlers/ingest.rs:1517-1519"
  - statement: "buzz-core/src/kind.rs's SHARED_GATED_KINDS constant is exactly [KIND_PERSONA, KIND_TEAM_CATALOG] (30175, 30178); is_shared_gated_kind(kind) tests membership; KIND_TEAM (30176) is deliberately excluded because its writers never emit a shared tag and it needs owner-private semantics instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:215"
      - "crates/buzz-core/src/kind.rs:219-220"
  - statement: "crates/buzz-db/src/store/event.rs applies a shared-gated visibility pushdown clause -- AND (kind NOT IN (30175,30178) OR pubkey = $reader OR tags @> '[[\"shared\",\"true\"]]') -- before ORDER BY/LIMIT in query_events, so a page of newer private personas cannot starve an older shared persona off the result set; the code comment states the JSONB containment check is served by idx_events_tags_gin (migration 0004, jsonb_path_ops)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:100-146"
      - "crates/buzz-db/src/store/event.rs:564-582"
      - "migrations/0004_events_tags_gin.sql"
  - statement: "The relay's author-only-unless-shared read gate for kind:30175/30178 is documented, per the spec, as covering REQ historical delivery, NIP-01 ids lookup, live fan-out, COUNT, the NIP-98 HTTP /query and /count bridges, and FTS/search (no shared-gated kind is in the FTS allowlist); device sync (authors:[self]) is unaffected because it always returns the author's own events."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AP.md:262-291"
  - statement: "Owners MAY publish NIP-09 deletion requests targeting persona (kind:30175) or team-catalog (kind:30178) events, authored by the same key, SHOULD include a k tag naming the target kind and an a-tag identifier of the form <kind>:<pubkey_o>:<d-tag>; a later-timestamped write resurrects the slug/team-id under NIP-33 replacement."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AP.md:159-165"
  - statement: "crates/buzz-cli/src/commands/channels.rs's fetch_team_persona_slugs queries kind:30176 (KIND_TEAM) events by owner and #d = [team_id] and reads content.persona_ids; scan_managed_agents_by_owner keyset-paginates kind:30177 (KIND_MANAGED_AGENT) events by owner (never page/offset, to avoid skipping a live instance across requests) and parses each event's content into a local ManagedAgentContent struct that reads only persona_id, ignoring the wire content's other fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:346-352"
      - "crates/buzz-cli/src/commands/channels.rs:407-445"
      - "crates/buzz-cli/src/commands/channels.rs:448-470"
  - statement: "No struct literally named PersonaEventContent (or an equivalent single typed model of the full kind:30175 wire content) exists anywhere in the crates searched (buzz-core, buzz-cli, buzz-acp, buzz-relay, buzz-persona); the call sites inspected parse persona/team/managed-agent event content ad hoc as serde_json::Value or a narrow local struct reading only the fields that call site needs."
    entry_class: FACT
    evidence:
      - "grep_repo('PersonaEventContent', path='crates/') -> zero matches, verified against commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
      - "crates/buzz-cli/src/commands/channels.rs:346-352"
  - statement: "crates/buzz-core/src/private_managed_agent.rs's PrivateConfig carries an optional definition_coordinate string validated against the literal grammar 30175:<owner-pubkey>:<non-empty d>, and its DefinitionBinding/InstanceBinding structs separately pin a kind:30175 definition event id and a kind:30177 instance event id plus a content SHA-256 -- concrete evidence of the unified agent model where an instance is definition-backed via an explicit 30175 coordinate rather than carrying its own copy of every definition field."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/private_managed_agent.rs:98-122"
      - "crates/buzz-core/src/private_managed_agent.rs:148-151"
      - "crates/buzz-core/src/private_managed_agent.rs:579-583"
  - statement: "End-to-end coverage of this interface's kinds exists as separate suites: e2e_persona.rs (kind:30175 envelope validation, NIP-33 replacement, and the full shared-read-gate access-control matrix), e2e_team.rs (kind:30176), e2e_managed_agent.rs (kind:30177) and e2e_team_catalog.rs (kind:30178, including its own shared-gate assertions)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_persona.rs:1-23"
      - "crates/buzz-test-client/tests/e2e_team.rs:1-26"
      - "crates/buzz-test-client/tests/e2e_managed_agent.rs:1-30"
      - "crates/buzz-test-client/tests/e2e_team_catalog.rs:1-38"
  - statement: "No writer/publisher code path that constructs and signs a kind:30175 persona event was located in the Rust crates searched (buzz-sdk/src/builders.rs, the typed Nostr event builder module, contains no persona builder); a publisher may exist in the desktop or web TypeScript client, which was not inspected as part of this node."
    entry_class: INFERENCE
    evidence:
      - "grep_repo('30175|persona', path='crates/buzz-sdk/src/builders.rs') -> zero matches, verified against commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
    confidence: 0.7
---

# NIP-AP: Agent Personas (interface)

## Interface description

This node documents the wire-level boundary defined by
[NIP-AP](../../../../../../docs/nips/NIP-AP.md), Buzz's own custom Nostr Implementation
Possibility for agent personas: how an **owner** (a workspace-controlling Nostr
identity) publishes a public, addressable persona definition, and how the **relay**
and downstream **readers** (other clients, the CLI, spawned agents) exchange and
gate access to that definition and its related projections. The exchange happens as
signed Nostr events over the relay's WebSocket (and equivalently its NIP-98 HTTP
bridge) using four kinds in the NIP-33 parameterized-replaceable range: `30175`
(persona definition), `30176` (team), `30177` (managed-agent instance) and `30178`
(team-catalog projection). Two of these kinds, `30175` and `30178`, additionally
carry a non-standard **author-only-unless-shared** read gate layered on top of
ordinary NIP-33/NIP-29 visibility, which is the part of this interface a plain
reading of NIP-33 alone would not predict.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Publish/replace a persona | `docs/nips/NIP-AP.md` "Writing" section; NIP-33 semantics | Owner signs a `kind:30175` event with exactly one `d` tag (persona slug) and a JSON `content` body; `created_at` monotonically exceeds the prior head. |
| Read a persona by slug | `docs/nips/NIP-AP.md` "Reading" section | Filter `{kinds:[30175], authors:[pubkey_o], "#d":[slug]}`, select the NIP-33 head. |
| List an owner's personas (catalog) | `docs/nips/NIP-AP.md` "Reading" section | Filter `{kinds:[30175], authors:[pubkey_o]}` returns all heads; catalog reads rely on the shared-gate to withhold unshared ones from foreign callers. |
| Delete a persona / team-catalog entry | `docs/nips/NIP-AP.md` "Deletion" section; NIP-09 | Owner-authored NIP-09 deletion request with a `k` tag naming the kind and an `a`-tag coordinate `<kind>:<pubkey_o>:<d>`; a later write resurrects the slug/team-id. |
| Relay ingest validation (persona) | `crates/buzz-relay/src/handlers/ingest.rs#validate_persona_envelope` (line 1486) | Enforces the shared-tag exact shape and the slug grammar `^[a-z0-9][a-z0-9_-]{0,63}$`. |
| Relay ingest validation (team-catalog) | `crates/buzz-relay/src/handlers/ingest.rs#validate_team_catalog_envelope` (line 1517) | Enforces the shared-tag exact shape and a bounded non-empty `d`, deliberately without the slug grammar. |
| Shared-gated read enforcement | `crates/buzz-db/src/store/event.rs` (`shared_gated_reader`, lines 100-146, 564-582); `buzz-core/src/kind.rs#SHARED_GATED_KINDS` (line 215) | Pre-`LIMIT` SQL pushdown withholds `30175`/`30178` events from foreign readers unless the event carries `["shared","true"]`. |
| CLI: fetch a team's persona slugs | `crates/buzz-cli/src/commands/channels.rs#fetch_team_persona_slugs` (line 407) | Queries `kind:30176` by owner + `#d`, reads `content.persona_ids`. |
| CLI: resolve live managed-agent roster | `crates/buzz-cli/src/commands/channels.rs#scan_managed_agents_by_owner` (line 448) | Keyset-paginates `kind:30177` by owner, matches `content.persona_id` against the team's slugs. |
| Definition-backed instance binding | `crates/buzz-core/src/private_managed_agent.rs` (`PrivateConfig.definition_coordinate`, `DefinitionBinding`, `InstanceBinding`; lines 98-151, 579-583) | An instance's private config pins an explicit `30175:<owner>:<d>` coordinate and separately records the exact `30175` definition event id and `30177` instance event id it was bound from. |

## Contract and stability

- **Addressing and replacement.** Standard NIP-33: `(pubkey, kind, d_tag)` is the
  coordinate, only the greatest-`created_at` event per coordinate is live (the
  "head"), ties break on lowest hex event `id`. A writer MUST set
  `created_at := max(now, T+1)` against the current head's timestamp so a fresh
  write always supersedes it regardless of clock skew (`docs/nips/NIP-AP.md:127-137`).
- **Slug/d-tag grammar differs by kind, and this is a deliberate, enforced
  asymmetry.** `30175`'s `d` tag MUST match the persona slug grammar
  `^[a-z0-9][a-z0-9_-]{0,63}$`; `30178`'s `d` tag MUST be non-empty, at most 64
  characters, control-character- and whitespace-free, but is explicitly NOT run
  through the slug grammar, because team ids legitimately contain `:` (e.g.
  `builtin-team:welcome`), which the slug grammar forbids. Both rules are enforced
  by the relay at ingest, not left to client discipline
  (`crates/buzz-relay/src/handlers/ingest.rs:1486-1522`).
- **Access control: author-only-unless-shared.** `30175` and `30178` (the exact
  membership of `SHARED_GATED_KINDS`) are readable by their author unconditionally
  and by any other reader only when the event carries exactly `["shared","true"]`.
  This is orthogonal to Buzz's usual community/channel `h`-tag scoping -- these
  events are stored globally (`channel_id = NULL`) -- and is instead a per-event
  tag-gated visibility rule enforced identically across every relay read surface
  the spec enumerates: REQ, `ids` lookup, live fan-out, COUNT, the NIP-98 HTTP
  `/query` and `/count` bridges, and FTS/search (`docs/nips/NIP-AP.md:262-291`).
  Toggling `shared` does not touch content bytes, so it cannot be mistaken for a
  content edit by drift-detection code that hashes content
  (`crates/buzz-relay/src/handlers/ingest.rs` `KIND_PERSONA` doc comment,
  `crates/buzz-core/src/kind.rs:180-203`).
  Malformed `shared` tags (wrong value, extra elements, more than one tag) are
  rejected outright at ingest so no ambiguous head can exist.
  A future or unshared team-catalog head, once shared, exposes **every embedded
  member's** instructions, including members whose own `30175` head is unshared
  and therefore otherwise private -- a caller relying on this interface's write
  side MUST treat "share the team" and "share each member individually" as
  distinct, non-overlapping operations (`docs/nips/NIP-AP.md:301`).
- **Versioning / forward compatibility.** Unknown `content` fields MUST be
  ignored by readers. The behavioral fields (`respond_to`, `respond_to_allowlist`,
  `parallelism`) are specified but marked **reserved**: parsed and round-tripped at
  the wire layer, not yet applied by the local definition store, and do not survive
  a local edit-and-republish cycle until a later create-path unification lands
  (`docs/nips/NIP-AP.md:93-109`). Consistent with that, `buzz-acp/src/config.rs`
  today carries `respond_to`/`respond_to_allowlist` on its own config structs but no
  field named `parallelism` -- code has not yet caught up to the full reserved set.
  Separately, clients released before `system_prompt` became optional will fail to
  parse (and silently drop) prompt-less `30175` definitions from newer clients; the
  spec calls this benign, not corruption, and recommends logging rather than
  surfacing per-event errors (`docs/nips/NIP-AP.md:210-215`).
- **Ordering / idempotency.** Publishing is idempotent under NIP-33 replacement:
  republishing identical content with a fresh, later `created_at` is a no-op head
  change; there is no separate create-vs-update operation. Deletion is likewise
  reversible by design -- a later write at the same coordinate resurrects the slug.
- **Byte limit.** A persona's serialized `content` MUST NOT exceed 65,535 bytes;
  the writing procedure rejects oversized bodies before signing
  (`docs/nips/NIP-AP.md:136`).

### Example — valid persona definition and its head after replacement

From the spec's pinned reference test vectors (`docs/nips/NIP-AP.md:303-374`, test
keys only, not for production use): a `kind:30175` event with
`tags:[["d","test-agent"]]` and `content:{"display_name":"Test Agent", ...}` at
`created_at:1700000000` (Event 1) is superseded by a same-slug event with an updated
`system_prompt` and `created_at:1700000002` (Event 3); after Event 3, the NIP-33 head
for slug `test-agent` is Event 3, and a reader selecting by `(pubkey, 30175,
"test-agent")` MUST resolve to it, not Event 1.

### Example — ingest rejection

Per `validate_shared_tag` (`crates/buzz-relay/src/handlers/ingest.rs:1408-1445`),
publishing a persona event whose tags include `["shared","false"]`, or two separate
`["shared", ...]` tags, is rejected by the relay at ingest with an `invalid:` error
before the event is ever stored -- the malformed-shared-tag case the spec requires
(`docs/nips/NIP-AP.md:252`).

## Boundary

This node does not describe:
- **A single kind's full tag/content wire format in isolation.** `docs/nips/NIP-AP.md`
  itself remains the authoritative source for the exact JSON shape of each kind's
  `content` body; this node cites it and the code that enforces it rather than
  re-encoding the format a second time. No event-kind-shaped sibling corpus node
  for kind `30175`/`30176`/`30177`/`30178` exists yet on `origin/launchpad` to
  `references` instead.
- **A full parameter-by-parameter API-reference catalogue** of every optional
  content field for a domain-expert audience -- this node's Operations table and
  Contract section state what a caller may rely on, not an exhaustive field
  dictionary.
- **The write/publish code path.** No Rust code that constructs and signs a
  `kind:30175` event was located in the crates searched; see *Scope and omissions*.
- **NIP-AE (agent engrams), NIP-OA (owner attestation), or the `mem/persona`
  encrypted snapshot** in their own right -- this node only describes how NIP-AP
  relates to them at the envelope level (persona events carry no encryption by
  design; secrets belong in a NIP-AE engram or out-of-band spawn-time injection;
  spawned agents separately carry NIP-OA attestation issued at spawn time), per
  `docs/nips/NIP-AP.md:119-125` and `:167-219`. Their own contracts are those NIPs'
  and, eventually, their own corpus nodes' territory.
- **The `buzz-persona` crate's markdown pack format** (`.persona.md` files loaded by
  `crates/buzz-persona/src/pack.rs`). That is a distinct, file-based local
  definition format with its own `display_name`/`description`/`hooks` fields; it is
  not shown by this investigation to be the direct source of a published `30175`
  event, and conflating the two would misdescribe both.

## Relationships

Declared: none. Checked against `origin/launchpad`'s corpus tree
(`launchpad/docs/corpus/interfaces/` does not exist there at all, confirmed by
`find launchpad/docs/corpus/interfaces -type f` returning nothing before this node
was created) -- there is no event-kind-shaped or capability-shaped sibling node yet
merged for this node to `references` or sit `part-of`. The corpus's four
already-merged nodes (`corpus-agents`, `corpus-readme`, and the two
`standards/*` governance nodes) are procedural/meta-documents about the corpus
itself, not subject matter this interface node would point at.

## Scope and omissions

**This node covers** the wire-level contract of Buzz's NIP-AP kinds
(`30175`/`30176`/`30177`/`30178`) as specified in `docs/nips/NIP-AP.md` and as
enforced today by the relay's ingest validation and shared-gated read pushdown, plus
how `buzz-cli` and `buzz-core`'s private-managed-agent state consume those kinds.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The exact JSON schema of every optional content field, field by field | `docs/nips/NIP-AP.md` itself; a future reference-depth corpus node |
| NIP-AE engram format and NIP-OA attestation format | Their own NIPs and, eventually, their own corpus nodes |
| The desktop/web client-side persona editor and any TypeScript publisher | Not inspected in this pass |
| The `buzz-persona` markdown pack format and its relationship (if any) to publishing a `30175` event | Not established in this pass |

**Expected but not verified when this node was written:**
- **No writer/publisher code path for `kind:30175` was located in the Rust crates
  searched** (`buzz-sdk/src/builders.rs`, the typed Nostr event builder module with
  38 builders for other kinds, contains none for personas). Whether a persona
  publisher exists in the desktop or web TypeScript client is unverified here.
- **Whether `respond_to`/`respond_to_allowlist`/`parallelism` have since become
  applied** (rather than merely parsed-and-preserved) in `buzz-acp`'s create path is
  unverified beyond the single revision this node cites; the spec itself frames
  this as pending a "create-path unification" whose landing state was not checked.
- **Whether the FTS/search allowlist (`docs/nips/NIP-AP.md:283`'s claim that
  migration 8 indexes only kinds `0, 9, 40002, 45001, 45003`) still holds at the
  recorded revision** was not independently re-verified against the migration file
  in this pass; it is cited to the spec, not opened as a second source.
