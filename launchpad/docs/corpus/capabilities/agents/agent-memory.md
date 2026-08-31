---
id: capabilities-agents-agent-memory
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
  - statement: "NIP-AE (docs/nips/NIP-AE.md) defines agent engrams: kind:30174 parameterized-replaceable events, NIP-44-encrypted with the conversation key between an agent (pubkey_a, the signer) and its owner (pubkey_o, the `p` tag), addressed by a per-slug `d` tag derived by HMAC-SHA256 over that conversation key so the slug itself is never revealed on the wire. Memory is scoped to a single (pubkey_a, pubkey_o) pair; an agent serving multiple owners holds an independent memory per pair."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AE.md:9"
      - "docs/nips/NIP-AE.md:17-26"
      - "docs/nips/NIP-AE.md:47-59"
  - statement: "NIP-AE defines two record types sharing one envelope: exactly one `core` record per (pubkey_a, pubkey_o) pair holding agent identity/rules/goals, and zero or more `memory` records (slug matching `mem/...`) each holding one logical entry with a UTF-8 `value` or a `null` tombstone. Head selection for any slug is the surviving valid event with the greatest `created_at`, ties broken by lowest event id."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AE.md:28-35"
      - "docs/nips/NIP-AE.md:78-94"
      - "docs/nips/NIP-AE.md:113-123"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_AGENT_ENGRAM as the constant 30174, documented as NIP-AE's parameterized-replaceable, agent-authored engram kind and cross-referencing docs/nips/NIP-AE.md and the crate::engram module directly in its doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:89-94"
  - statement: "crates/buzz-core/src/engram.rs implements the NIP-AE envelope end to end: build_event signs a kind:30174 event with a NIP-44-encrypted body and the derived d/p tags; validate_and_decrypt re-checks kind, pubkey, tag shape, and slug-to-d-tag re-derivation before returning the decoded body; select_head picks the greatest-created_at survivor (lowest id on tie); monotonic_created_at enforces the writing rule max(now, prior_head + 1)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/engram.rs:435-473"
      - "crates/buzz-core/src/engram.rs:488-557"
      - "crates/buzz-core/src/engram.rs:564-584"
      - "crates/buzz-core/src/engram.rs:588-593"
  - statement: "crates/buzz-cli/src/commands/mem.rs exposes the agent-facing surface as `buzz mem {ls, get, hash, set, patch, rm}`, dispatched from a single `dispatch` function; `buzz mem set` refuses to write an empty value read from stdin unless `--allow-empty` is passed, and `buzz mem patch` requires an explicit `--base-hash` (or `--no-base-hash` override) and verifies each unified-diff hunk applies at its exact declared line position rather than letting diffy silently slide it, refusing the patch otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/mem.rs:1-16"
      - "crates/buzz-cli/src/commands/mem.rs:305-372"
      - "crates/buzz-cli/src/commands/mem.rs:522-698"
      - "crates/buzz-cli/src/commands/mem.rs:737-778"
  - statement: "crates/buzz-cli/README.md documents the `buzz mem` command group under an \"Agent Memory (NIP-AE)\" heading with example invocations, and lists `ls`, `get`, `hash`, `set`, `patch`, `rm` in its Commands table with one-line descriptions matching the implementation in mem.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/README.md:82-87"
      - "crates/buzz-cli/README.md:164-169"
  - statement: "crates/buzz-acp/src/engram_fetch.rs fires one synchronous query for the agent's `core` engram when a new ACP session is created and, on success, renders it into a `<core-memory>` prompt section; if no core exists yet it instead emits a fixed onboarding nudge telling the agent to run `buzz mem set core \"...\"` and ask its user about itself; on any transport/parse/decrypt error it emits no section at all, specifically to avoid mistaking a relay outage for an absent core and inviting the agent to overwrite real memory."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/engram_fetch.rs:1-59"
  - statement: "VISION_REMOTE_AGENTS.md states, as part of the product's rationale for remote/portable agent execution, \"Its durable memory is engrams on the relay\" — naming agent memory as one of the things that make an agent's identity independent of the machine currently running it."
    entry_class: FACT
    evidence:
      - "VISION_REMOTE_AGENTS.md:13"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's validate_engram_envelope rejects any kind:30174 event that does not carry exactly one `d` tag and exactly one `p` tag, requires both to be exactly 64 lowercase hex characters (lowercase strictly, since a submitter could otherwise replace the lowercase head with a variant subsequent lowercase-`#p` queries can't see), and rejects content that is not a syntactically plausible NIP-44 v2 payload — all enforced at ingest time before the event is stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2728-2731"
      - "crates/buzz-relay/src/handlers/ingest.rs:1341-1393"
  - statement: "KIND_AGENT_ENGRAM is treated by the relay as addressed by (pubkey_a, kind, d_tag) and is explicitly never channel-scoped (no `h` tag gating applies to it), the same treatment given to other pubkey-keyed replaceable/parameterized-replaceable kinds like emoji sets and event reminders."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:644"
  - statement: "crates/buzz-relay/src/handlers/req.rs's engram_filters_authorized restricts read access to filters matching KIND_AGENT_ENGRAM: a filter is authorized only if every `authors` entry equals the authenticated pubkey (the agent reading its own engrams), or every `#p` entry equals the authenticated pubkey (the owner reading engrams addressed to them), or the filter carries explicit `ids`. A bare or wildcard kind filter with neither condition is rejected, because the public `#p` tag and timestamps on an otherwise-encrypted engram would otherwise leak who pairs with whom and write-activity patterns to any authenticated reader."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1218-1269"
  - statement: "req.rs's own test module exercises this read-authorization gate directly with named cases (engram_gate_allows_agent_querying_own, engram_gate_allows_owner_querying, engram_gate_rejects_unrelated_reader, engram_gate_rejects_bare_kind_filter, engram_gate_rejects_wildcard_kind_filter, engram_gate_allows_ids_lookup, engram_gate_rejects_mixed_authors_with_unauthed, among others), and buzz-core/src/engram.rs and buzz-cli/src/commands/mem.rs each carry their own #[test]-annotated unit test modules covering envelope build/validate/decrypt, head selection, and the mem patch command's strict-position and multi-file-rejection behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:2162-2296"
      - "crates/buzz-core/src/engram.rs:607-1049"
      - "crates/buzz-cli/src/commands/mem.rs:780-1045"
  - statement: "desktop/src/features/agent-memory/ui/MemorySection.tsx's own header comment describes it as an \"IXI-7 phase 1 read-only viewer\" that is owner-gated by the caller (returns null for non-owners) and renders a tree rooted at the agent's `core` engram, with orphaned (unreferenced) memories and dangling `[[slug]]` references surfaced separately rather than hidden."
    entry_class: FACT
    evidence:
      - "desktop/src/features/agent-memory/ui/MemorySection.tsx:21-56"
  - statement: "At repository revision 131b02f989684117d9ab1dd426f1673fa638e523, `origin/launchpad`'s corpus tree carries no `capabilities/` node of any kind, and no other hand-authored node declares an id this node could reference — this is the first capability-shaped instance node, and no `relationships` target resolves yet."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/capability.md, at commit 131b02f989684117d9ab1dd426f1673fa638e523; no capabilities/ path present"
  - statement: "Whether desktop's Tauri-side engram query command (desktop/src-tauri/src/commands/engrams.rs) or any buzz-persona use of engrams beyond what is cited above adds further capability-relevant behavior was not independently verified for this node; those files were located but not read in full."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "author's own note recorded while gathering evidence for launchpad-26/buzz#705, 2026-08-31"
relationships:
  - type: part-of
    target: capabilities-agents-agent
---

# Agent memory: capability

An AI agent operating in Buzz can keep **durable, encrypted, cross-session memory** that
survives the process, the machine, and the conversation that created it. The two actors are
the **agent** (a Nostr keypair that authors its own memory) and its **owner** (the human or
team the agent serves, who can always decrypt everything the agent remembers because the
underlying encryption key is symmetric between the pair). The outcome this capability gives
each of them: the agent gets a `core` identity/rules/goals record plus any number of freeform
`memory` entries that persist independently of any one running process, auto-loaded into a
fresh session's prompt so it doesn't have to be told who it is every time; the owner gets the
ability to read (and, through the same key material, recover) everything the agent has written
to itself, without needing the agent's runtime available. This is the concrete mechanism behind
Buzz's stated design goal that "what makes an agent *that agent* was never the process" —
identity, memory, and reputation live on the relay, not on whichever machine happens to be
running the agent right now (`VISION_REMOTE_AGENTS.md:13`).

## Maturity

**Shipped.** The wire specification (`docs/nips/NIP-AE.md`), the encoding/decoding
implementation (`crates/buzz-core/src/engram.rs`), the agent-facing CLI surface
(`crates/buzz-cli/src/commands/mem.rs`, documented in `crates/buzz-cli/README.md`), automatic
session-start injection into the ACP agent harness (`crates/buzz-acp/src/engram_fetch.rs`),
relay-side envelope validation and read-authorization (`crates/buzz-relay/src/handlers/
ingest.rs`, `crates/buzz-relay/src/handlers/req.rs`), and an owner-facing read-only viewer in
the desktop app (`desktop/src/features/agent-memory/`) are all present in this repository at
the recorded revision, each with its own unit test coverage (see *Verification* below).

## Behavioral rules, constraints and variants

- **Scoping.** Memory is per `(agent pubkey, owner pubkey)` pair, never shared across owners
  or agents. An agent serving several owners holds an independent memory per pair (`docs/nips/
  NIP-AE.md:17-26`).
- **Two record shapes, one envelope.** Exactly one `core` record per pair (identity, rules,
  goals); any number of `mem/...` records, each one logical entry. Both are addressable
  (NIP-01 parameterized-replaceable): only the latest per slug is authoritative (`docs/nips/
  NIP-AE.md:28-35`, `crates/buzz-core/src/engram.rs:564-584`).
  - `core` cannot be tombstoned — `buzz mem rm core` is refused; overwriting it with an empty
    profile is the documented alternative (`crates/buzz-cli/src/commands/mem.rs:706-717`).
  - A `memory` record with `value: null` is a tombstone: the event still exists, but readers
    must treat the slug as absent (`docs/nips/NIP-AE.md:94`).
- **Writes are monotonic.** Each write's `created_at` must be `max(now, prior_head_created_at +
  1)`, defeating same-second NIP-01 tie-breaking under NIP-44's random nonces
  (`crates/buzz-core/src/engram.rs:588-593`).
- **Concurrency safety is opt-in but the default is strict.** `buzz mem patch` requires an
  explicit `--base-hash` (the sha256 of the value the patch was generated against) unless
  `--no-base-hash` is passed; a mismatch is surfaced as a conflict rather than silently
  overwriting a concurrent edit. Patch hunks must apply at their exact declared line position —
  the implementation deliberately refuses the fuzzy/sliding match its underlying diff library
  would otherwise allow (`crates/buzz-cli/src/commands/mem.rs:522-649`).
- **Empty writes require explicit intent.** Both `mem set` (reading from stdin) and `mem patch`
  refuse to commit an empty value unless `--allow-empty` is passed, guarding against an upstream
  pipeline failure silently destroying a slug (`crates/buzz-cli/src/commands/mem.rs:339-346`,
  `crates/buzz-cli/src/commands/mem.rs:659-665`).
- **Session-start variant: automatic core injection.** The ACP harness does not wait to be
  asked — it fetches the agent's `core` engram once per new session and renders it as a
  `<core-memory>` prompt section, or an onboarding nudge if none exists yet. A fetch error
  (as opposed to a confirmed-absent core) yields neither, so a relay outage is never mistaken
  for "no memory" (`crates/buzz-acp/src/engram_fetch.rs:1-59`).
- **Read authorization is asymmetric from write authorization.** Only the agent itself can
  author engrams (no protocol-level owner-write path exists), but either the agent or its
  declared owner can read/list them; the relay enforces this at query time by rejecting any
  filter that could match `KIND_AGENT_ENGRAM` events unless every `authors` entry or every
  `#p` entry equals the authenticated pubkey, or the filter names explicit event `ids`
  (`crates/buzz-relay/src/handlers/req.rs:1218-1269`).
- **Never channel-scoped.** Engrams are addressed by `(pubkey_a, kind, d_tag)` only; the relay
  explicitly excludes `KIND_AGENT_ENGRAM` from `h`-tag channel scoping
  (`crates/buzz-relay/src/handlers/ingest.rs:644`).
- **Owner-side recovery.** `buzz mem ls/get/hash` support an `--agent <pubkey>` flag that
  flips perspective: the CLI identity is treated as the owner, decrypting the named agent's
  engrams through the same conversation key, for when the agent's own runtime isn't available
  (`crates/buzz-cli/src/commands/mem.rs:48-79`).

## Verification

- Relay-side read-authorization is unit-tested directly: `engram_gate_allows_agent_querying_own`,
  `engram_gate_allows_owner_querying`, `engram_gate_rejects_unrelated_reader`,
  `engram_gate_rejects_bare_kind_filter`, `engram_gate_rejects_wildcard_kind_filter`,
  `engram_gate_allows_ids_lookup`, `engram_gate_rejects_mixed_authors_with_unauthed`, and further
  cases in the same module (`crates/buzz-relay/src/handlers/req.rs:2162-2296`).
- `crates/buzz-core/src/engram.rs` carries its own `#[cfg(test)]` module covering envelope
  build/validate/decrypt round-trips, slug validation, and head selection.
- `crates/buzz-cli/src/commands/mem.rs` carries its own `#[cfg(test)]` module covering
  `resolve_reader`'s owner/agent-flag branching, sha256 hashing against known vectors, and the
  patch command's strict-position hunk verification (including the offset-slide case that a
  looser diff-apply would silently accept).

## Boundary

This node does not describe:
- **The NIP-AE wire specification itself** — exact byte-level envelope encoding, key
  derivation formulas, and the reference test vectors are `docs/nips/NIP-AE.md`'s own content;
  this node cites it rather than restating it.
- **A dedicated interface contract for `buzz mem`** as a CLI command-group boundary in its own
  right (flags, exit codes, argument grammar in full) — no interface-shaped corpus node exists
  yet to hold that; `crates/buzz-cli/README.md` is today's closest thing.
- **The step-by-step flow of one write or read cycle** (head-selection walk, HTTP round trip,
  relay response shape) — no flow-shaped corpus node exists yet for this capability.
- **How the relay is operated** (deployment, monitoring, incident response for the service
  hosting this data) — that is the `operations` corpus surface, not this capability's own
  description.
- **Desktop's Tauri-side query command internals** (`desktop/src-tauri/src/commands/
  engrams.rs`) beyond the fact that it queries `KIND_AGENT_ENGRAM` — its internals were not
  read for this node (see *Scope and omissions*).

## Relationships

None declared. No architecture, interface, or flow node exists yet on `origin/launchpad`'s
corpus tree for this node to `references`, and this is the first `capabilities`-typed node, so
no `part-of` target exists either.

## Scope and omissions

**This node covers** what the agent-memory capability is (durable, encrypted, per-(agent,
owner) memory with a `core` identity record and freeform `memory` entries), who the actors are
and what each gets from it, its current maturity (shipped, with implementation and test
citations), the behavioral rules and constraints that govern reads, writes, concurrency, and
session-start auto-injection, and the verification evidence that demonstrates the read-
authorization and envelope-handling rules actually hold.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The NIP-AE wire format, encoding, and reference test vectors | `docs/nips/NIP-AE.md` |
| A CLI-interface-shaped node for `buzz mem`'s own command boundary | not yet drafted (no interface node exists) |
| A flow-shaped node for one write/read cycle through this capability | not yet drafted (no flow node exists) |
| How the relay serving this data is deployed and operated | the `operations` corpus surface |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **`desktop/src-tauri/src/commands/engrams.rs`'s internals** were located (it references
  `KIND_AGENT_ENGRAM`) but not read in full — this node makes no claim about its behavior
  beyond that reference.
- **Any use of engrams by `buzz-persona`** (agent persona packs) was not searched for beyond
  what surfaced incidentally; if persona packs read or write engrams, that behavior is not
  captured here.
- **No end-to-end relay-backed integration test** (as opposed to in-process unit tests) exercising
  a full write-then-read-then-list cycle over a running relay was found under
  `crates/buzz-test-client/tests/`; the verification cited above is unit-level, not full-stack
  end-to-end.
