---
id: interfaces-nostr-buzz-nips-nip-ae
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
  - statement: "docs/nips/NIP-AE.md defines kind:30174 'Agent Engrams' as an addressable-range NIP-01 record type for AI agent memory, encrypted with NIP-44 using the symmetric conversation key between an agent (pubkey_a) and its owner (pubkey_o), with two record types sharing the kind ('core', exactly one per pair, and 'memory', zero or more), a `d` tag derived as `lower_hex(HMAC-SHA256(K_c, \"agent-memory/v1/d-tag\" || 0x00 || slug))`, and a head-selection procedure (greatest created_at, ties broken by lowest event id) used identically for reading, write-verification and listing."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AE.md"
  - statement: "buzz-core/src/kind.rs declares `pub const KIND_AGENT_ENGRAM: u32 = 30174`, with its own doc comment citing docs/nips/NIP-AE.md and the engram module directly, confirming the wire kind number the spec assigns is the one this codebase actually uses."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:94"
  - statement: "buzz-core/src/engram.rs implements the spec's core mechanics as free functions: validate_slug (Slugs grammar), normalize_slug (shorthand-to-slug), conversation_key and d_tag (Addressing), extract_refs (wiki-link References convention), build_event (Writing), validate_and_decrypt (Head selection rules 1 and 5, post-signature), select_head (Head selection's greatest-created_at/lowest-id tie-break), and monotonic_created_at (Writing's `max(now, T_head + 1)` monotonicity rule) -- each function corresponds to a named section of the spec, not a paraphrase of it."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/engram.rs:67"
      - "crates/buzz-core/src/engram.rs:123"
      - "crates/buzz-core/src/engram.rs:136"
      - "crates/buzz-core/src/engram.rs:144"
      - "crates/buzz-core/src/engram.rs:384"
      - "crates/buzz-core/src/engram.rs:435"
      - "crates/buzz-core/src/engram.rs:488"
      - "crates/buzz-core/src/engram.rs:564"
      - "crates/buzz-core/src/engram.rs:588"
  - statement: "buzz-cli's MemCmd enum defines the `buzz mem` subcommand group -- Ls, Get, Hash, Set, Patch, Rm -- as the CLI-facing surface over kind:30174 engrams, and commands/mem.rs's dispatch match arms wire each variant to its handler function."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1801-1875"
      - "crates/buzz-cli/src/commands/mem.rs:740"
      - "crates/buzz-cli/src/commands/mem.rs:743"
      - "crates/buzz-cli/src/commands/mem.rs:746"
      - "crates/buzz-cli/src/commands/mem.rs:749"
      - "crates/buzz-cli/src/commands/mem.rs:755"
      - "crates/buzz-cli/src/commands/mem.rs:776"
  - statement: "buzz-relay/src/handlers/ingest.rs's required_scope_for_kind maps kind:30174 (KIND_AGENT_ENGRAM) to Scope::UsersWrite, so publishing an engram event requires the same authorization scope as ordinary user-owned writes; this is checked before validate_engram_envelope runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:437-444"
  - statement: "buzz-relay/src/handlers/ingest.rs's validate_engram_envelope rejects a kind:30174 event unless it has exactly one `d` tag (64 lowercase hex chars) and exactly one `p` tag (64 lowercase hex chars), and unless its `content` is a syntactically plausible NIP-44 v2 payload; this runs at ingest for every kind:30174 event before NIP-33 parameterized-replacement can act on it, specifically to stop a malformed envelope from silently superseding a valid head."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1341"
      - "crates/buzz-relay/src/handlers/ingest.rs:2728-2730"
  - statement: "ingest.rs's own unit tests confirm both directions of that envelope check: engram_envelope_accepts_canonical asserts a well-formed 64-hex `d`+`p` envelope with a syntactically valid NIP-44 payload passes, and engram_envelope_rejects_missing_p asserts an envelope missing its `p` tag is rejected with an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:4290"
      - "crates/buzz-relay/src/handlers/ingest.rs:4298"
  - statement: "buzz-relay/src/handlers/req.rs's engram_filters_authorized requires that, for a global (non-channel) subscription, any filter that could match kind:30174 must constrain either `authors` to exactly the authenticated pubkey or the `#p` generic tag to exactly the authenticated pubkey; req.rs enforces this before the NIP-50 search branch runs specifically so an authenticated member cannot use `{\"search\":...,\"kinds\":[30174]}` to read another pair's engrams via full-text search."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1239-1269"
      - "crates/buzz-relay/src/handlers/req.rs:210-231"
  - statement: "ingest.rs lists kind:30174 (KIND_AGENT_ENGRAM) among kinds that are never channel-scoped, with an inline comment stating engrams are addressed by `(pubkey_a, kind, d_tag)` and a stray `h` tag must not channel-scope them -- consistent with the spec's own statement that engrams have no channel concept."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:641-644"
  - statement: "buzz-acp/src/engram_fetch.rs fetches the agent's `core` engram once at new-session creation (build_core_section) and renders it into the agent's prompt as a `<core-memory>` section when found, or emits a fixed ONBOARDING_NUDGE string directing the agent to `buzz mem set core` when no core exists yet; on any transport/parse/decrypt error it emits no section at all (never mistaking an outage for an absent core) and never blocks session creation either way."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/engram_fetch.rs:1-13"
      - "crates/buzz-acp/src/engram_fetch.rs:24-27"
      - "crates/buzz-acp/src/engram_fetch.rs:36-58"
  - statement: "The spec's own Addressing section states the `d`-tag HMAC domain prefix `\"agent-memory/v1/d-tag\"` is version-tagged independently of the NIP's assigned number, and that a future version MUST change that prefix to avoid colliding with deployed v1 records -- the spec's stated forward-compatibility mechanism."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AE.md"
  - statement: "The corpus's interface template (templates/interface.md) states that node.schema.json's type enum encodes PRD #602's combined 'interfaces/events' surface as the single value `interfaces-events`, used for both interface-shaped and event-kind-shaped subject matter, and that this template's own required sections (Interface description, Operations, Contract and stability, Boundary, Relationships, Scope and omissions) is the shape a node like this one should take."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "No corpus node under launchpad/docs/corpus/interfaces/nostr/buzz-nips/ exists on origin/launchpad at the recorded revision, so this node declares no relationships -- a target id that does not yet exist in the loaded corpus is a hard validate.py error, and the template's own precedent is to prose-link, not relationship-link, unmerged sibling nodes."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/interfaces') -> no buzz-nips subtree present at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
---

# NIP-AE (Agent Engrams): interface

This node documents Buzz's custom NIP-AE extension -- **Agent Engrams**, a
Nostr-over-WebSocket interface between an AI agent (`pubkey_a`) and its owner
(`pubkey_o`) that stores persistent, structured agent memory as `kind:30174`
addressable events, NIP-44-encrypted so both agent and owner can decrypt every
record. It is a Buzz-authored NIP (not one of the numbered upstream NIPs),
specified in full at `docs/nips/NIP-AE.md`, which this node cites for wire
detail rather than re-deriving.

## Interface description

Two sides exchange encrypted memory records across a shared Nostr relay
connection: the **agent**, which signs and publishes `kind:30174` events under
its own key, and the **owner**, who can decrypt (but never author) the same
events because the NIP-44 conversation key `K_c` is symmetric. The technology
is a Nostr addressable event (`kind:30174`, NIP-01 replaceable-by-`(kind,
pubkey,d)` semantics) whose `content` is NIP-44 v2 ciphertext; memory is
scoped to exactly one `(pubkey_a, pubkey_o)` pair, and an agent serving
multiple owners holds one independent memory set per pair. This interface has
three distinct access points documented below: the wire-level Nostr event
itself, the `buzz mem` CLI command group that produces and consumes it, and
the ACP harness's automatic session-start read of the `core` record.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `kind:30174` addressable event (wire format) | `docs/nips/NIP-AE.md`; `crates/buzz-core/src/kind.rs:94` (`KIND_AGENT_ENGRAM`) | The Nostr event itself: `d` tag (64-hex HMAC), `p` tag (owner pubkey), NIP-44-encrypted `content` holding a `core` or `memory` body. |
| `engram::build_event` | `crates/buzz-core/src/engram.rs:435` | Constructs and signs a `kind:30174` event for a given body, rejecting bodies over the 65,535-byte NIP-44 plaintext limit. |
| `engram::validate_and_decrypt` | `crates/buzz-core/src/engram.rs:488` | Validates an inbound candidate event against Head-selection rules (1) and (5) and decrypts its body; caller must verify the signature first. |
| `engram::select_head` | `crates/buzz-core/src/engram.rs:564` | Picks the head of a slug from a set of candidate events: greatest `created_at`, ties broken by lowest event id. |
| `buzz mem ls` | `crates/buzz-cli/src/lib.rs:1802-1813`; `crates/buzz-cli/src/commands/mem.rs:740` | Lists non-tombstoned memory entries for the `(agent, owner)` pair. |
| `buzz mem get <slug>` | `crates/buzz-cli/src/lib.rs:1814-1822`; `crates/buzz-cli/src/commands/mem.rs:743` | Prints a slug's current value (memory) or profile (core) to stdout. |
| `buzz mem hash <slug>` | `crates/buzz-cli/src/lib.rs:1823-1831`; `crates/buzz-cli/src/commands/mem.rs:746` | Prints `sha256(value)` in hex, for use as `--base-hash` in `buzz mem patch`. |
| `buzz mem set <slug> <value>` | `crates/buzz-cli/src/lib.rs:1832-1843`; `crates/buzz-cli/src/commands/mem.rs:749` | Writes a slug's value (or reads it from stdin with `-`); rejects an empty write unless `--allow-empty` is passed. |
| `buzz mem patch <slug>` | `crates/buzz-cli/src/lib.rs:1844-1873`; `crates/buzz-cli/src/commands/mem.rs:755` | Applies a unified diff to a slug's current value; refuses to apply if the slug changed since `--base-hash` was captured, or if the hunk's context does not match verbatim. |
| `buzz mem rm <slug>` | `crates/buzz-cli/src/lib.rs:1874-1879`; `crates/buzz-cli/src/commands/mem.rs:776` | Publishes a tombstone for a slug (cannot target `core`). |
| ACP session-start core fetch | `crates/buzz-acp/src/engram_fetch.rs:36` (`build_core_section`) | Fetches the agent's `core` engram once when a new ACP session begins and renders it into the agent's prompt, or emits an onboarding nudge if none exists. |

## Contract and stability

- **Versioning/compatibility.** The `d`-tag HMAC domain prefix
  `"agent-memory/v1/d-tag"` is version-tagged independently of the NIP number
  itself; the spec states a future revision MUST change this prefix rather
  than reuse it, so `v1` records and any future `v2` records address disjoint
  `d`-tag spaces and cannot collide (`docs/nips/NIP-AE.md`, *Addressing*).
- **Authentication/authorization (write).** Publishing a `kind:30174` event
  requires `Scope::UsersWrite`, the same authorization scope ordinary
  user-owned writes need (`crates/buzz-relay/src/handlers/ingest.rs:437-444`).
  The relay additionally enforces the envelope's public shape --
  `validate_engram_envelope` rejects any `kind:30174` event without exactly
  one 64-lowercase-hex `d` tag, exactly one 64-lowercase-hex `p` tag, and a
  syntactically plausible NIP-44 v2 `content` -- before NIP-33 replacement can
  act on it (`crates/buzz-relay/src/handlers/ingest.rs:1341`, invoked at
  `ingest.rs:2728-2730`). The relay never inspects plaintext; it enforces only
  the public envelope.
- **Authentication/authorization (read).** For a global (non-channel-scoped)
  subscription, `engram_filters_authorized` requires any filter that could
  match `kind:30174` to constrain either `authors` or the `#p` generic tag to
  exactly the requester's own authenticated pubkey. This check runs before the
  NIP-50 search branch specifically to stop an authenticated member from using
  full-text search to bypass the author/`#p` restriction
  (`crates/buzz-relay/src/handlers/req.rs:1239-1269`, enforced at
  `req.rs:210-231`).
- **Ordering/idempotency.** Head selection (which record is authoritative for
  a slug) is the greatest `created_at`, ties broken by lowest event id --
  identical logic for reading, write-verification and listing
  (`docs/nips/NIP-AE.md`, *Head selection*; `engram::select_head`,
  `crates/buzz-core/src/engram.rs:564`). Writers compute
  `created_at := max(now, T_head + 1)` (`engram::monotonic_created_at`,
  `crates/buzz-core/src/engram.rs:588`) so a fresh writer with no local state
  still produces a strictly newer event than the current head, and same-second
  NIP-01 tiebreaks (unreliable under NIP-44's random nonces) are avoided.
- **Error/rejection behavior.** A malformed envelope (missing/duplicate `d` or
  `p` tag, wrong hex length, non-lowercase hex, implausible NIP-44 shape) is
  rejected at ingest with an `invalid: ...` error and never reaches storage or
  fan-out (`crates/buzz-relay/src/handlers/ingest.rs:1341`). An unauthorized
  read filter is closed with `"restricted: agent-engram reads require
  authors=[self] or #p=[self]"` (`crates/buzz-relay/src/handlers/req.rs:225-230`).
- **Scoping.** Engrams are never channel-scoped; they are addressed purely by
  `(pubkey_a, kind, d_tag)`, and a stray `h` (channel) tag has no scoping
  effect on them (`crates/buzz-relay/src/handlers/ingest.rs:641-644`).

## Boundary

This node does not describe:
- The full NIP-44 v2 encryption algorithm, or NIP-01's own event-signing and
  replaceable-event semantics -- those are NIP-44's and NIP-01's own
  specifications, cited here, not restated.
- A field-by-field, parameter-by-parameter catalogue of every `buzz mem`
  flag (e.g. `--no-base-hash`, `--dry-run` on `buzz mem patch`) for
  domain-expert readers -- see `docs/nips/NIP-AE.md` and
  `crates/buzz-cli/src/lib.rs`'s `MemCmd` doc comments directly for that
  depth; this node covers the operation list and contract, not exhaustive
  flag semantics.
- Any change to engram behavior -- this node documents the interface as it
  exists at the recorded revision; it does not propose or authorize product
  changes.

## Relationships

None declared. No sibling `interfaces/nostr/buzz-nips/` node exists in the
corpus on `origin/launchpad` at the recorded revision, so there is no valid
`references`/`part-of`/`implements` target yet; a `relationships[].target`
naming an id nothing carries is a hard `validate.py` error. Related Buzz-custom
NIPs mentioned in `docs/nips/` for context, referenced here by filename only
(not as corpus relationship edges, since no corpus node exists for them yet):
`NIP-AM.md` (agent turn metrics), `NIP-AP.md` (persona definitions),
`NIP-ER.md` (event reminders, the closest structural sibling to NIP-AE --
also a `(pubkey, kind, d_tag)`-addressed, never-channel-scoped, encrypted
record type).

## Valid example

A signed, well-formed `kind:30174` event (from the spec's own reference test
vectors, Event 1 -- writing slug `mem/example`; `docs/nips/NIP-AE.md`,
*Reference test vectors*):

```
kind:            30174
pubkey:           79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
created_at:       1700000000
tags:             [["d","72d4f9629106451505d7d341ea85bb3ebad4f654fcfd2aad100d5a35f8a85cba"],
                    ["p","c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5"]]
content:          <NIP-44 v2 ciphertext decrypting to {"slug":"mem/example","value":"hello, agent memory"}>
```

`validate_engram_envelope` accepts this shape: exactly one 64-lowercase-hex `d`
tag, exactly one 64-lowercase-hex `p` tag, syntactically plausible NIP-44
content (`crates/buzz-relay/src/handlers/ingest.rs`, test
`engram_envelope_accepts_canonical`, line 4290).

## Failure example

The same event with its `p` tag removed is rejected at ingest with
`"agent-engram event must have exactly one \`p\` tag (got 0)"`, confirmed by
`engram_envelope_rejects_missing_p`
(`crates/buzz-relay/src/handlers/ingest.rs`, line 4298). On the read side, an
authenticated user submitting `REQ` with `{"kinds":[30174]}` and no `authors`
or `#p` constraint naming their own pubkey is closed by the relay with
`"restricted: agent-engram reads require authors=[self] or #p=[self]"`
(`crates/buzz-relay/src/handlers/req.rs:225-230`).

## Scope and omissions

**This node covers** the `kind:30174` Agent Engram wire format and its Buzz
implementations: the core spec mechanics in `buzz-core::engram`, the `buzz
mem` CLI operation surface, the relay's write-side envelope validation and
authorization scope, the relay's read-side authorization gate, the
never-channel-scoped addressing rule, and the ACP harness's automatic
session-start `core` fetch.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-44 v2's own encryption algorithm | `docs/nips/44.md` (upstream NIP, not reproduced in this repository's `docs/nips/`) |
| NIP-01's event-signing and addressable-replacement semantics | NIP-01 itself |
| Field-by-field `buzz mem` flag reference | `crates/buzz-cli/src/lib.rs`'s `MemCmd` doc comments; `docs/nips/NIP-AE.md` |
| A corpus node for NIP-ER, NIP-AM, or NIP-AP (Buzz's other custom NIPs) | Not yet created; each is its own future corpus task |

**Expected but not verified when this node was written:**
- **No end-to-end (multi-process) test exercising the full write-then-read
  round trip through a live relay was found** for `kind:30174` engrams; the
  evidence above rests on unit tests within `buzz-core`, `buzz-relay`, and
  `buzz-cli` rather than an integration or E2E suite entry
  (`crates/buzz-test-client/tests/` was searched and contains no
  engram-specific test file at the recorded revision).
- **Whether `buzz-sdk` exposes a typed builder for engram events was
  checked and found absent** -- `crates/buzz-sdk/src/builders.rs` has no
  engram-related builder function; `buzz mem`/`engram::build_event` is the
  only construction path found.
