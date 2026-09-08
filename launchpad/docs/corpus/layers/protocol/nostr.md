---
id: layers-protocol-nostr
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "crates/buzz-relay/src/nip11.rs declares SUPPORTED_NIPS as the unconditional list [1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56], and its doc comment states this is the set advertised in the NIP-11 document."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "NIP-43 is the one conditionally advertised NIP: nip11.rs holds it as a separate constant NIP_RELAY_MEMBERSHIP = 43 that RelayInfo::build appends to supported_nips only when advertise_nip43 is true, which nip11_facts derives as (a stable relay signing key is configured) AND (membership enforcement is enabled)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "nip11.rs advertises Buzz's own lettered extensions through a separate supported_extensions field rather than supported_nips: the list is seeded with \"nip-er\" unconditionally, \"buzz-gif\" is pushed when a GIF provider is configured, and nip11_document pushes \"nip-pl\" when a push descriptor is built."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "The NIP-11 document is served on two routes registered in the relay's router — the content-negotiated root handler and a dedicated /info endpoint — both routed through the same nip11_document function so they cannot drift apart."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/router.rs"
  - statement: "Each of NIP-01, NIP-10, NIP-42 and NIP-50 has a dedicated implementing module whose own doc comment names it: protocol.rs is \"NIP-01 client/relay message parsing and formatting\", nip10.rs is \"Shared NIP-10 thread-marker parsing\", buzz-auth's lib.rs documents NIP-42 as WebSocket challenge/response over kind:22242, and buzz-search's query.rs is \"NIP-50 search query against Postgres FTS, community-scoped\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
      - "crates/buzz-core/src/nip10.rs"
      - "crates/buzz-auth/src/lib.rs"
      - "crates/buzz-search/src/query.rs"
  - statement: "NIP-02 (kind:3 contact list) and NIP-38 (kind:30315 user status) reach the relay's real ingest path rather than existing only as kind constants: handlers/ingest.rs names KIND_CONTACT_LIST and KIND_USER_STATUS together in its scope-resolution match arms."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "NIP-16 and NIP-33 are implemented as the two replaceable-event families in the data layer: buzz-db's replaceable.rs handles NIP-16 kinds (0, 3, 41, 10000-19999) and the generic NIP-33 parameterized-replaceable path, and event.rs applies canonical NIP-16 ordering (created_at DESC, id ASC) when selecting the surviving head."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
      - "crates/buzz-db/src/store/event.rs"
  - statement: "NIP-17, NIP-23, NIP-25 and NIP-56 are each carried by a named kind constant in the authoritative registry whose doc comment cites the NIP: KIND_GIFT_WRAP (1059), KIND_LONG_FORM (30023), KIND_REACTION (7) and the kind:1984 report kind respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "nip11.rs carries unit tests that pin individual advertisement decisions rather than only the list's shape: separate tests assert NIP-23, NIP-33, NIP-38 and NIP-56 are present, that the list is sorted, and that NIP-43 is NOT in the static list because advertising it on an open relay misroutes desktop pairing peers to a non-existent /pair sidecar."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "docs/nips/ contains 22 Markdown specifications, every one of them a Buzz-authored lettered code rather than an upstream numbered NIP: NIP-AA (agent authentication), NIP-AE (agent engrams), NIP-AM (agent turn metrics), NIP-AO (agent observability), NIP-AP (agent personas), NIP-CW (channel window), NIP-DV (DM visibility), NIP-ER (event reminders), NIP-FI plus its CONF/DELEG/EDGE/LIFECYCLE/MODEL profiles (federated identity authorization), NIP-GS (git object signing with Nostr keys), NIP-IA (identity archival), NIP-MP (multi-repository projects), NIP-OA (owner attestation), NIP-PL (push leases), NIP-PMA (private managed-agent aggregate), NIP-RS (cross-device read state sync) and NIP-WP (workspace profile)."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md"
      - "docs/nips/NIP-AE.md"
      - "docs/nips/NIP-AM.md"
      - "docs/nips/NIP-AO.md"
      - "docs/nips/NIP-AP.md"
      - "docs/nips/NIP-CW.md"
      - "docs/nips/NIP-DV.md"
      - "docs/nips/NIP-ER.md"
      - "docs/nips/NIP-FI.md"
      - "docs/nips/NIP-FI-CONF.md"
      - "docs/nips/NIP-FI-DELEG.md"
      - "docs/nips/NIP-FI-EDGE.md"
      - "docs/nips/NIP-FI-LIFECYCLE.md"
      - "docs/nips/NIP-FI-MODEL.md"
      - "docs/nips/NIP-GS.md"
      - "docs/nips/NIP-IA.md"
      - "docs/nips/NIP-MP.md"
      - "docs/nips/NIP-OA.md"
      - "docs/nips/NIP-PL.md"
      - "docs/nips/NIP-PMA.md"
      - "docs/nips/NIP-RS.md"
      - "docs/nips/NIP-WP.md"
  - statement: "No upstream numbered NIP specification text is present anywhere in this repository, so a claim about what NIP-01 or NIP-42 themselves require cannot be cited to a repo path."
    entry_class: FACT
    evidence:
      - "find(path='docs/nips', name='NIP-[0-9]*.md') -> 0 matches"
  - statement: "21 of the 22 lettered specifications declare themselves `draft` in their opening status line and most also declare `optional`; the single exception is NIP-FI-MODEL, which is an explicitly non-normative companion stating it \"defines no requirement, invariant, wire value, denial mapping, or conformance claim\"."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-FI-MODEL.md"
      - "docs/nips/NIP-AA.md"
      - "docs/nips/NIP-CW.md"
      - "docs/nips/NIP-WP.md"
  - statement: "Several lettered specifications name their upstream dependencies explicitly in a Depends on line — NIP-AA on NIP-OA/NIP-43/NIP-42, NIP-CW on NIP-01/NIP-11/NIP-29/NIP-98, NIP-IA on NIP-01/NIP-11/NIP-42/NIP-43/NIP-70/NIP-OA, NIP-MP on NIP-01/NIP-34/NIP-09 — so the extension set is written as a layer on top of the numbered NIPs rather than as a replacement for them."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md"
      - "docs/nips/NIP-CW.md"
      - "docs/nips/NIP-IA.md"
      - "docs/nips/NIP-MP.md"
  - statement: "NIP-29 is the channel model itself, not one feature among many: NOSTR.md's opening states \"Buzz is a Nostr relay that speaks NIP-29 (relay-based groups) natively\", and its What Works table enumerates the NIP-29 kinds the relay handles — 9007 group creation, 9000/9001 add/remove user, 9002 edit metadata, 9005 admin delete, 9008 deletion, 9021 join request, 9022 leave, and the relay-signed 39000/39001/39002 discovery events."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "One of the 22 lettered specifications explicitly instructs relays to refuse its own kind: NIP-PMA is a \"protocol/codec reservation only\" and states that relays MUST reject kind 30179 until privacy, transactional CAS, backup/restore, revocation and capability gates are deployed."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PMA.md"
  - statement: "Buzz explicitly declines NIP-90's data-vending-machine kind range: kind.rs records the comment \"Not using NIP-90 kinds (5000-6999) - Buzz requires auth chains (depth <= 3, breadth <= 10)\" directly above the agent job protocol constants it defined at 43001-43006 instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "NOSTR.md records two further declines: \"The old NIP-28 compatibility proxy has been removed\", and a What Doesn't Work row stating that for direct messages \"NIP-17 gift wraps supported; NIP-04/NIP-44 not implemented\" with kind:10050 (DM relay list) deferred."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "Neither NIP-04 nor NIP-28 is referenced anywhere in the Rust sources, corroborating NOSTR.md's statement that they are not implemented rather than merely undocumented."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
      - "grep_r('NIP-04', include='*.rs', path='crates/') -> 0 matches; grep_r('NIP-28', include='*.rs', path='crates/') -> 0 matches"
  - statement: "NIP-44 is nonetheless implemented and used outside the DM path — for pairing payload encryption and for encrypting agent and reminder content to a single reader — so NOSTR.md's \"NIP-44 not implemented\" is scoped to direct messages and is not a repository-wide statement."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/mod.rs"
      - "docs/nips/NIP-AE.md"
      - "docs/nips/NIP-ER.md"
  - statement: "kind.rs also records a narrower decline inside an adopted NIP: KIND_CHANNEL_METADATA (kind:41) is registered with the comment \"NIP-01: Channel metadata (replaceable). Not used by Buzz today.\", so registration in the kind registry is not by itself evidence that a kind is in use."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Several NIPs are implemented but never advertised in supported_nips, among them NIP-98 (a dedicated buzz-auth/src/nip98.rs module verifying kind:27235 HTTP auth), NIP-34 (patch-based git push governance in buzz-core/src/git_perms.rs), NIP-70 (the protected-event `-` tag built and checked in buzz-sdk and buzz-cli), and NIP-05, NIP-09, NIP-51 and NIP-65, each carried by named kind constants or profile-sync behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
      - "crates/buzz-core/src/git_perms.rs"
      - "crates/buzz-sdk/src/builders.rs"
      - "crates/buzz-core/src/kind.rs"
      - "NOSTR.md"
  - statement: "supported_nips is therefore a curated interoperability claim about what a third-party client may rely on, not an inventory of every NIP the codebase touches — 39 distinct numbered NIPs are referenced across the Rust sources against the 14 in SUPPORTED_NIPS."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-auth/src/nip98.rs"
      - "grep_ro('NIP-[0-9]{2}', include='*.rs', path='crates/', unique=true) -> 39 distinct numbered NIPs, against 14 in SUPPORTED_NIPS"
    confidence: 0.75
  - statement: "NIP-AB (device pairing) is implemented across the Rust sources — buzz-pair-relay's crate doc calls itself an \"Ephemeral sidecar relay for NIP-AB device pairing handshakes\" and buzz-core carries a NIP-AB pairing session state machine — yet no docs/nips/NIP-AB.md exists, so an implemented Buzz extension has no written specification in this repository."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs"
      - "crates/buzz-core/src/pairing/session.rs"
      - "grep_r('NIP-AB', include='*.rs', path='crates/') -> 50 matches; find(path='docs/nips', name='NIP-AB.md') -> 0 matches"
  - statement: "The reverse asymmetry also exists: docs/nips/NIP-AA.md specifies agent authentication in full, but NIP-AA is referenced zero times in the Rust sources, so a written Buzz extension has no implementation reference in the crates."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md"
      - "grep_r('NIP-AA', include='*.rs', path='crates/') -> 0 matches"
  - statement: "Issue #1159's definition of done requires that this be exactly one hand-authored canonical node, that any second concept discovered while drafting be filed as its own task rather than folded in, and that the draft be checked against the repository revision recorded in provenance."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1159 definition of done"
  - statement: "No corpus node existed under launchpad/docs/corpus/layers/protocol/ before this one, so this node opens the protocol surface rather than joining an existing set of siblings there."
    entry_class: FACT
    evidence:
      - "git_ls_tree(--name-only, origin/launchpad, 'launchpad/docs/corpus/layers/') -> compute, configuration, data, lifecycle, observability; no protocol entry"
relationships:
  - type: references
    target: architecture-principles-nostr-first
  - type: references
    target: architecture-context-nostr-network
  - type: references
    target: verification-contracts-nostr
  - type: references
    target: implementation-crates-buzz-core
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: development-protocol-changes
  - type: references
    target: development-event-kind-changes
---

# Nostr, as Buzz uses it

Nostr is the open, relay-and-signed-event protocol Buzz is built on. This node's
subject is not Nostr itself — it is **Buzz's relationship to Nostr**: which parts of
the protocol Buzz adopts, which it extends with specifications of its own, and which
it looks at and refuses.

That distinction is the whole point of the node. A generic explanation of Nostr would
be unverifiable here, because no upstream NIP text exists anywhere in this repository
(`find(path='docs/nips', name='NIP-[0-9]*.md')` returns nothing). What *is*
documentable, and is documented nowhere else in the corpus, is the boundary Buzz has
drawn around the protocol.

## Definition

**A NIP** is one numbered specification in the upstream `nostr-protocol/nips`
repository, each describing one piece of wire behavior a relay or client may support.
(The acronym's expansion is not defined anywhere in this repository, so it is not
stated here.) **A relay's `supported_nips` list**, served in its NIP-11 information
document, is that relay's public claim about which of them it honors.

Buzz relates to that vocabulary in three distinct ways, and this node's job is to keep
them apart:

| Relationship | What it means here | Where it is recorded |
|---|---|---|
| **Adopts** | Buzz implements the upstream NIP and advertises it, so a third-party client may rely on it | `SUPPORTED_NIPS` in `crates/buzz-relay/src/nip11.rs` |
| **Extends** | Buzz needed behavior no upstream NIP covers and wrote its own lettered specification for it | the 22 files in `docs/nips/` |
| **Declines** | Buzz considered an upstream NIP and deliberately did not implement it, or removed it | comments in `crates/buzz-core/src/kind.rs`; `NOSTR.md` |

**What this is not.** "Nostr" here does not mean the public Nostr network of
interconnected relays. Buzz does not federate at the relay level — that boundary is
`architecture-context-nostr-network`'s to state, and this node does not restate it.
Nor does "adopts" mean "conforms": advertising a NIP is a claim made by a constant in
one file, and only the tests in `verification-contracts-nostr` exercise any of it
against a live relay.

## What Buzz adopts

`crates/buzz-relay/src/nip11.rs` declares one unconditional list:

```
SUPPORTED_NIPS: &[u32] = &[1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56]
```

Fourteen NIPs, sorted (a unit test in the same file asserts the sorting). Each has
implementing code, located and named here rather than assumed:

| NIP | Subject | Corroborated in |
|---|---|---|
| 01 | Base event and client/relay message format | `crates/buzz-relay/src/protocol.rs` — module doc: "NIP-01 client/relay message parsing and formatting" |
| 02 | Contact list (kind:3) | `crates/buzz-core/src/kind.rs` (`KIND_CONTACT_LIST`), reaching `handlers/ingest.rs` scope resolution |
| 10 | Threading markers on `e` tags | `crates/buzz-core/src/nip10.rs` — "Shared NIP-10 thread-marker parsing" |
| 11 | Relay information document | `crates/buzz-relay/src/nip11.rs`, routed at `/` and `/info` |
| 16 | Replaceable events | `crates/buzz-db/src/store/replaceable.rs`; canonical ordering in `event.rs` |
| 17 | Gift-wrapped private DMs (kind:1059) | `crates/buzz-core/src/kind.rs` (`KIND_GIFT_WRAP`) |
| 23 | Long-form content (kind:30023) | `crates/buzz-core/src/kind.rs` (`KIND_LONG_FORM`) |
| 25 | Reactions (kind:7) | `crates/buzz-core/src/kind.rs` (`KIND_REACTION`) |
| 29 | Relay-based groups — the channel model | `crates/buzz-relay/src/handlers/ingest.rs`; surface table in `NOSTR.md` |
| 33 | Parameterized replaceable events | `crates/buzz-db/src/store/replaceable.rs` |
| 38 | User status (kind:30315) | `crates/buzz-core/src/kind.rs` (`KIND_USER_STATUS`), reaching ingest |
| 42 | Client authentication to relays (kind:22242) | `crates/buzz-auth/src/lib.rs` |
| 50 | Search filters | `crates/buzz-search/src/query.rs` — "NIP-50 search query against Postgres FTS" |
| 56 | Reporting (kind:1984) | `crates/buzz-core/src/kind.rs`; queue handling in `handlers/ingest.rs` |

**NIP-43 is the one conditional entry**, and the reason is instructive. It lives in a
separate constant, `NIP_RELAY_MEMBERSHIP = 43`, appended to `supported_nips` only when
the relay both holds a stable signing key and enforces membership. `nip11.rs` states
why in a test: the desktop pairing probe keys off this NIP, so advertising it on an
open relay misroutes pairing peers to a `/pair` sidecar that is not there. A
`debug_assert` in `RelayInfo::build` refuses `advertise_nip43` without a `self` pubkey,
because NIP-43 events are verified against it.

**Advertisement is narrower than implementation.** Several NIPs are implemented and
never advertised — NIP-98 has a dedicated `crates/buzz-auth/src/nip98.rs` verifying
kind:27235 HTTP auth events; NIP-34 governs patch-based git push in
`crates/buzz-core/src/git_perms.rs`; NIP-70's protected-event `-` tag is built in
`buzz-sdk` and checked in `buzz-cli`; NIP-05, NIP-09, NIP-51 and NIP-65 each have named
kind constants or profile-sync behavior. Thirty-nine distinct numbered NIPs are
referenced across the Rust sources against the fourteen advertised. So
`supported_nips` reads as a curated claim about what a third-party client may depend
on, not as an inventory.

**And registration is not use.** `kind.rs` registers `KIND_CHANNEL_METADATA` (kind:41)
with the comment "NIP-01: Channel metadata (replaceable). Not used by Buzz today." A
kind constant existing proves the number is reserved, not that anything emits it.

## What Buzz extends

When Buzz needs behavior no upstream NIP covers, it writes a specification rather than
inventing wire format silently. Those live in `docs/nips/` as 22 Markdown files, all
using lettered codes so they cannot collide with an upstream number. Twenty-one of the
twenty-two declare themselves `draft` and most also `optional`; the exception is
`NIP-FI-MODEL`, an explicitly non-normative companion that "defines no requirement,
invariant, wire value, denial mapping, or conformance claim." Several open with an
explicit **Depends on** line naming the upstream NIPs they build atop — `NIP-CW` on
NIP-01/11/29/98, `NIP-IA` on NIP-01/11/42/43/70 plus `NIP-OA`, `NIP-MP` on
NIP-01/34/09.

| Specification | Subject |
|---|---|
| `NIP-AA` | Agent authentication (depends on NIP-OA, NIP-43, NIP-42) |
| `NIP-AE` | Agent engrams — addressable, encrypted agent memory |
| `NIP-AM` | Agent turn metrics — per-turn token usage and cost |
| `NIP-AO` | Agent observability — ephemeral session telemetry |
| `NIP-AP` | Agent personas — the blueprint an agent is spawned from |
| `NIP-CW` | Channel window |
| `NIP-DV` | DM visibility |
| `NIP-ER` | Event reminders — encrypted, author-only, with a public due time |
| `NIP-FI` | Federated identity authorization, core |
| `NIP-FI-CONF` | Conformance evidence profile for NIP-FI |
| `NIP-FI-DELEG` | Delegated agent authorization profile |
| `NIP-FI-EDGE` | Trusted enterprise edge profile |
| `NIP-FI-LIFECYCLE` | Binding lifecycle profile |
| `NIP-FI-MODEL` | Composed authorization model (explicitly non-normative) |
| `NIP-GS` | Git object signing with Nostr keys |
| `NIP-IA` | Identity archival |
| `NIP-MP` | Multi-repository projects |
| `NIP-OA` | Owner attestation — an owner key authorizing an agent key |
| `NIP-PL` | Push leases |
| `NIP-PMA` | Private managed-agent aggregate |
| `NIP-RS` | Cross-device read state sync |
| `NIP-WP` | Workspace profile |

**These are advertised through a different field.** Only two of the twenty-two ever
reach the NIP-11 document, and not via `supported_nips`: `nip11.rs` seeds a separate
`supported_extensions` array with `"nip-er"` unconditionally and pushes `"nip-pl"` when
a push descriptor is configured (alongside `"buzz-gif"`, which is not a NIP at all).
The other twenty are invisible to a client reading NIP-11.

**Two asymmetries are worth knowing before trusting either list as complete:**

- **NIP-AB is implemented but unwritten.** `crates/buzz-pair-relay`'s crate doc calls
  itself an "Ephemeral sidecar relay for NIP-AB device pairing handshakes" and
  `buzz-core/src/pairing/session.rs` is a "NIP-AB pairing session state machine" — 50
  references across the Rust sources — yet `docs/nips/NIP-AB.md` does not exist.
- **NIP-AA is written but unreferenced.** `docs/nips/NIP-AA.md` specifies agent
  authentication in full, and `NIP-AA` appears zero times in `crates/`.

So `docs/nips/` is neither a superset nor a subset of what the code implements. Read
both.

## What Buzz declines

Refusals are recorded, not merely absent — which is what makes them documentable:

- **NIP-90 (data vending machines).** `crates/buzz-core/src/kind.rs` carries
  `// Not using NIP-90 kinds (5000–6999) — Buzz requires auth chains (depth ≤ 3,
  breadth ≤ 10).` immediately above the agent job protocol kinds Buzz defined instead
  at 43001–43006. The stated reason is a capability the upstream kind range does not
  carry, not a preference.
- **NIP-28 (public chat).** `NOSTR.md`'s opening states "The old NIP-28 compatibility
  proxy has been removed"; NIP-29 relay-based groups is the channel model. `NIP-28` is
  referenced zero times in the Rust sources.
- **NIP-04 (legacy encrypted DMs).** `NOSTR.md`'s *What Doesn't Work* table states
  "NIP-17 gift wraps supported; NIP-04/NIP-44 not implemented" for DMs, with kind:10050
  deferred. `NIP-04` is likewise referenced zero times in the sources.

**One caution on that last row.** The "NIP-44 not implemented" clause is scoped to the
DM path only. NIP-44 v2 *is* implemented elsewhere — it encrypts pairing payloads in
`crates/buzz-core/src/pairing/mod.rs`, and both `NIP-AE` and `NIP-ER` specify NIP-44
encryption for their content. Reading that table row as a repository-wide statement
would be wrong.

**A refusal can also live inside a Buzz specification.** `NIP-PMA` is marked
"protocol/codec reservation only" and states that relays MUST reject kind 30179 until
privacy, transactional CAS, backup/restore, revocation and capability gates are
deployed. A written spec is not a claim that the kind is accepted.

## Diagram

```mermaid
flowchart TB
    upstream["Upstream NIPs<br/>(nostr-protocol/nips —<br/>text NOT in this repo)"]

    upstream -->|adopts, advertises| adopted["SUPPORTED_NIPS<br/>1, 2, 10, 11, 16, 17, 23,<br/>25, 29, 33, 38, 42, 50, 56<br/>(+43 conditionally)"]
    upstream -->|implements, does NOT advertise| silent["NIP-98, 34, 70, 05,<br/>09, 51, 65, ..."]
    upstream -->|declines| declined["NIP-90 → kinds 43001-43006<br/>NIP-28 → NIP-29 groups<br/>NIP-04 → NIP-17 gift wrap"]
    upstream -->|insufficient, so extends| own["docs/nips/ — 22 lettered<br/>specifications (21 draft)"]

    adopted --> doc["NIP-11 document<br/>GET / and /info"]
    own -->|only nip-er, nip-pl| ext["supported_extensions"]
    ext --> doc
```

## Use cases

**Answering "does Buzz support NIP-N?"** The honest answer has three parts, and this
node's tables give all three: is it advertised, is it implemented, and was it
explicitly declined. Answering from `SUPPORTED_NIPS` alone will say "no" for NIP-98,
which Buzz implements thoroughly.

**Deciding where new protocol behavior goes.** If an upstream NIP covers it, adopt and
advertise. If none does, the precedent is a lettered draft in `docs/nips/` plus kinds in
`buzz-core/src/kind.rs` — not silent wire format. `development-protocol-changes` and
`development-event-kind-changes` own the procedures.

**Judging third-party client compatibility.** A client that speaks NIP-01, NIP-29 and
NIP-42 can connect. What it will not render is anything in the Buzz-custom kind ranges,
because no lettered NIP is advertised to it in `supported_nips` at all.

**Not mistaking advertisement for conformance.** Nothing in `nip11.rs` tests wire
behavior against upstream spec text; its tests assert which integers are in a list.

## Scope and omissions

**This node covers** the adopt/extend/decline relationship between Buzz and Nostr: the
advertised list and where each entry is implemented, the 22 Buzz-authored lettered
specifications and how the two of them that are advertised reach clients, and the
recorded refusals.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The design principle of modelling features as events and keeping HTTP narrow | `architecture-principles-nostr-first` |
| Nostr as an external system — actors, the community/host boundary, non-federation | `architecture-context-nostr-network` |
| Whether the interop behavior is actually exercised against a live relay | `verification-contracts-nostr` |
| Any single protocol primitive — the event, filters, tags, subscriptions, the kind registry, the NIP-11 document as a document, NIP-29 groups, NIP-42 auth | one #609 sibling node each; none merged at this revision, so none is a relationship target here |
| The procedure for changing the protocol or adding a kind | `development-protocol-changes`, `development-event-kind-changes` |
| What any upstream NIP actually requires | `nostr-protocol/nips`, which is not in this repository |

**Expected but not verified when this node was written:**

- **No conformance check was run against upstream NIP text.** Every "adopts" row above
  establishes that implementing code exists and names the NIP — not that the
  implementation satisfies the specification. The specifications are not in this
  repository to check against.
- **The low-frequency tail of unadvertised NIP references was not individually
  confirmed as implementations.** NIP-98, NIP-34, NIP-70, NIP-05, NIP-09, NIP-51 and
  NIP-65 were each traced to a named file or kind constant. Nine further numbered NIPs
  appear exactly once in the sources; a single mention can be a passing reference
  rather than an implementation — NIP-90's single occurrence is precisely that, and it
  is a *refusal*. The 39-against-14 ratio is therefore an INFERENCE about reference
  counts, not a count of implementations.
- **`docs/nips/` has no index or README**, so the subject line for each specification
  was read from that file's own opening abstract. No source cross-checks the 22 against
  each other or against the kind registry.
- **Whether the relay's live `/info` response matches `SUPPORTED_NIPS`** was not
  observed — no relay was run. The claim rests on reading `nip11.rs` and `router.rs`.
- **NIP-AA's zero code references were established by grep on `crates/` only.** Whether
  it is implemented in the desktop, mobile or web trees under a different spelling was
  not checked.
