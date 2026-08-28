---
id: corpus-template-interface
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template, policy, or a documentation-form value; the enum names the corpus surface a node documents, not the prose form (tutorial/how-to/reference/explanation) its body takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's four nodes merged to origin/launchpad at the recorded revision, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance -- the precedent for a node that documents the corpus's own authoring rules rather than a piece of architecture/capability/etc. content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states implements' directionality as 'source is the concrete realization of target (e.g. a template instance of a standard)', with references stated separately as 'source cites target as supporting context; no ownership or currency dependency implied'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "Parent Feature #602's success criteria list the corpus's in-scope surfaces as a single combined item -- 'architecture, layers, capabilities, platforms, implementation, interfaces/events, verification, operations, development, release, governance, agent and ingestion' -- so interface-shaped and event-kind-shaped instance nodes share one corpus surface rather than being enumerated as two."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#602 success criteria"
  - statement: "node.schema.json's corresponding enum member for that combined surface is the single hyphenated token interfaces-events, not two separate values."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four is interface-shaped subject matter, and none of the ten open batch-1/batch-2 template PRs (#1527-#1531, #1533-#1537) are merged, so they are not valid relationship targets either."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "This repository's root AGENTS.md states 'Buzz's primary API is NIP-29 over WebSocket' and describes the relay's HTTP surface as deliberately narrow -- 'NIP-11/NIP-05 metadata, POST /events, POST /query, POST /count, workflow webhooks at /hooks/{id}, Blossom media, git smart HTTP, git policy hooks, and health probes' -- with new feature work directed toward a Nostr event kind rather than a new HTTP endpoint."
    entry_class: FACT
    evidence:
      - "AGENTS.md:145-160"
  - statement: "No AsyncAPI or Swagger document or dependency exists anywhere in this repository. The only openapi-adjacent dependency is k8s-openapi (Rust bindings generated from the Kubernetes API server's own OpenAPI-derived types), used exclusively by buzz-backend-kubernetes to talk to the Kubernetes control plane -- not an OpenAPI document Buzz itself authors or maintains for any of its own interfaces."
    entry_class: FACT
    evidence:
      - "grep_repo('asyncapi|swagger', types='rs,toml,md,yaml,yml,json', exclude='node_modules,target') -> zero matches, verified 2026-08-27 against commit a44cf52fc740ebebbdd671427480d14f0bce0115"
      - "crates/buzz-backend-kubernetes/Cargo.toml:15"
      - "Cargo.toml:69"
  - statement: "The OpenAPI Specification's own explainer states it 'provides a consistent means to carry information through each stage of the API lifecycle' and that using it means 'all done using a single version of the truth expressed in the OpenAPI document' -- i.e. the specification document itself is the interface description, not a description of one."
    entry_class: FACT
    evidence:
      - "https://www.openapis.org/what-is-openapi"
  - statement: "An unmerged research note independently frames the same point, calling OpenAPI Specification 3.2.0 (19 September 2025) 'the template for HTTP API reference, in the sense that the spec *is* the document.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note, launchpad/Research/project-documentation-templates.md on branch docs/research-project-doc-templates)"
  - statement: "AsyncAPI 3.0.0 describes itself as a specification for message-driven APIs in a machine-readable format that is protocol-agnostic ('you can use it for APIs that work over any protocol e.g. AMQP, MQTT, WebSockets, Kafka, STOMP, HTTP'), and decomposes an API into channels (addressable message-exchange points), operations (an application sending or receiving on a channel), messages (the payload exchanged) and servers (the broker or program sending/receiving)."
    entry_class: FACT
    evidence:
      - "https://www.asyncapi.com/docs/reference/specification/v3.0.0"
  - statement: "buzz-cli's command surface is defined with clap's derive macros (Parser on the top-level Cli struct, Subcommand on each command-group enum), so the CLI's own contract is generated from the struct definitions rather than hand-written separately -- clap's --help output at any depth is the live, code-derived description of that contract."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:63-64"
      - "crates/buzz-cli/src/lib.rs:175"
  - statement: "buzz-sdk's builders.rs states it provides '38 builders' of 'Typed event builder functions', all returning Result<nostr::EventBuilder, SdkError> for the caller to sign -- a Rust-native library interface, not a wire-protocol document, describing the same underlying Nostr event kinds buzz-core/src/kind.rs declares."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:1-4"
  - statement: "buzz-relay's router.rs registers the relay's narrow HTTP surface as a fixed table of routes -- among them GET / (NIP-11-or-WebSocket), GET /.well-known/nostr.json (NIP-05), POST /events, POST /query, POST /count, POST /hooks/{id}, PUT /upload -- confirming the surface AGENTS.md describes in prose is exactly the route table in code, with no separate interface-description artifact generated from or alongside it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:40-134"
  - statement: "buzz-relay's nip11.rs implements the NIP-11 relay information document (RelayInfo, served at GET / with an Accept: application/nostr+json request), itself a Nostr-protocol-defined interface descriptor distinct from the event-kind wire format NIP-01/NIP-29 define."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:15-25"
  - statement: "buzz-dev-mcp depends on rmcp (the Rust Model Context Protocol SDK crate), imports it at the top of lib.rs, and uses rmcp::service::RoleServer and rmcp::model::Implementation directly, implementing an externally specified protocol (MCP) rather than a Buzz-invented one."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/buzz-dev-mcp/src/lib.rs:1-10"
      - "crates/buzz-dev-mcp/src/lib.rs:47"
      - "crates/buzz-dev-mcp/src/lib.rs:130"
  - statement: "buzz-acp's acp.rs states in its own module doc comment that it manages agent-subprocess communication 'over stdio using JSON-RPC 2.0 (newline-delimited / NDJSON)', implementing the Agent Client Protocol's wire format directly in this repository's own code rather than through an external agent-client-protocol crate dependency (none appears in buzz-acp's Cargo.toml)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1-9"
      - "crates/buzz-acp/Cargo.toml"
  - statement: "Root AGENTS.md documents buzz-cli's own stability contract in prose -- 'All reads return sig-stripped JSON arrays; all writes return {event_id, accepted, message}; creates add the entity ID. Exit codes: 0=ok, 1=input error, 2=network/relay, 3=auth, 4=other, 5=write conflict (NIP-33 LWW)' -- a concrete example of an interface's behavioral contract distinct from its operation list."
    entry_class: FACT
    evidence:
      - "AGENTS.md:217-219"
  - statement: "Issue #1532, filed while drafting the sibling reference template, states that #1342 (this template) and #1337 (event kind) are 'architecture/data-shape templates, not a reference-depth template for cataloguing a full API surface's endpoints and parameters for domain-expert readers' -- i.e. this template is not expected to produce field-by-field API-reference cataloguing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1532"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1342's own copied-over standards-track Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria"
  - statement: "Issue #1342's own Definition of Done is byte-identical to the standards-track boilerplate ('States scope and authority/source of the policy. Separates MUST requirements from SHOULD guidance. Defines enforcement/checks and exception/escalation process. Links decisions or higher-order policy instead of duplicating them.'), the same text independently found copied across #1326-#1351 by the batch dispatch brief for this task set."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1342 definition of done"
---

# Template: interface

How to write a corpus node documenting one **interface** -- a boundary across which
two sides exchange calls, messages or commands under a shared contract (a CLI command
group, an HTTP route group, a WebSocket/Nostr protocol surface, an embedded external
protocol implementation). This template deliberately does **not** adopt a single
existing industry specification format wholesale; *Industry models considered* below
explains why, and what it adapts instead. This is a template node, not a policy
node -- it prescribes the shape of a future document's *body*, not a MUST/SHOULD rule
about corpus-wide behavior. See *Note on Definition of Done* for why that distinction
matters for this specific node.

## Scope and authority

**This node covers** what a corpus node's body must contain when it documents one
interface: the required sections, the evidence expectations for an operation/contract
claim, and the industry models considered (and why none is adopted as-is).

**It does not cover**:
- The front-matter contract itself (`node.schema.json` governs that, unconditionally,
  for every node type) or how to create/update/retire a node procedurally
  (`AGENTS.md` governs that).
- A single Nostr event kind's own wire contract -- kind number, tag shape, content
  semantics -- which is `#1337`'s template (event kind), not this one. See *Boundary*
  below for the exact line.
- Field-by-field, parameter-by-parameter cataloguing of a full API surface for
  domain-expert readers -- the Good Docs Project's **API Reference** depth, which
  `#1346` (reference) and its own escalation `#1532` explicitly found this template
  does not cover. See *Boundary* below.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `validate.py` runs that schema, and CI runs
`validate.py` on every corpus change. What this node adds is the half no schema can
hold -- which sections an interface-shaped node needs, what evidence backs an
operation or contract claim, and which industry models were considered and rejected
or partially adapted. That half is enforced by review, the same way the existing
corpus standards describe their own review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| A single Nostr event kind's wire contract | `#1337`'s template (event kind) |
| Field-by-field API-surface cataloguing | `#1346`/`#1532` (reference / API Reference gap) |

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Industry models considered, and why none is adopted wholesale

**OpenAPI does not fit.** OpenAPI's own explainer describes the specification
document as the interface description itself -- "a single version of the truth
expressed in the OpenAPI document." That framing assumes the interface *is* an HTTP
resource surface described well by paths, verbs and schemas. This repository's own
root `AGENTS.md` says the opposite about its primary API: "Buzz's primary API is
NIP-29 over WebSocket," and the HTTP surface that does exist is "deliberately
narrow" -- NIP-11/NIP-05 metadata, a generic Nostr bridge (`POST /events`,
`/query`, `/count`), webhooks, media, git smart HTTP, and health probes -- with new
feature work explicitly directed toward a Nostr event kind rather than a new HTTP
endpoint. `router.rs`'s actual route table confirms that surface in code. No OpenAPI
document exists anywhere in this repository, and the only OpenAPI-adjacent dependency
(`k8s-openapi`, generated Kubernetes API bindings used by `buzz-backend-kubernetes` to
talk to the Kubernetes control plane) describes a different system's interface
entirely, not one of Buzz's own. Even the narrow HTTP surface that does exist is not
conventional resource-oriented REST that OpenAPI's path/verb/schema model was built to
describe -- most of it bridges Nostr filters and events through generic JSON
envelopes, not per-resource CRUD endpoints. Forcing OpenAPI onto that surface would
document a minority, explicitly-secondary part of the system and would misrepresent it
as more REST-shaped than it is.

**AsyncAPI is a closer conceptual fit, but is still not adopted.** AsyncAPI
describes itself as protocol-agnostic and message-driven -- exactly the shape of
Buzz's primary interface, a WebSocket protocol built from typed events rather than
HTTP resources. Its decomposition into **channels** (addressable exchange points),
**operations** (send/receive on a channel) and **messages** (the payload) maps
cleanly onto "a channel a client subscribes to" and "the events it receives on it."
But three things stop this template from adopting the AsyncAPI document format
itself, not just its concepts:

1. **No AsyncAPI document exists in this repository either** (same grep as above),
   and nothing generates or validates one -- adopting its schema would introduce a
   second, hand-maintained, unchecked description of a wire format the code and the
   Nostr protocol specification already define more precisely.
2. **The wire format already has an owner that outranks a new document.** Event
   shapes are `buzz-core/src/kind.rs`'s kind constants plus NIP-01/NIP-29's own
   text; typed construction is `buzz-sdk/src/builders.rs`'s 38 builder functions.
   An AsyncAPI-style message schema restating those in a different serialization is
   exactly the kind of second, unvalidated description this corpus's own evidence
   discipline (`AGENTS.md`: "the checker never opens [a cited file] and compares it
   against your statement") warns is easy to let drift.
3. **AsyncAPI only fits the WebSocket surface.** buzz-cli's contract is a clap
   struct tree; buzz-dev-mcp's is the externally specified Model Context Protocol
   (`rmcp` crate); buzz-acp's is a hand-rolled JSON-RPC 2.0 over stdio wire format
   implementing the externally specified Agent Client Protocol. None of these is
   channel/message-shaped in AsyncAPI's sense, so a single AsyncAPI-derived template
   would fit one interface shape in this repository and misfit the rest.

**What this template adapts instead.** Not a document format, but a decomposition
habit borrowed from AsyncAPI's own structure -- *a boundary is one or more
operations, and each operation has a message/argument shape someone can point at* --
combined with a discipline this repository's own heterogeneous interfaces already
demonstrate: **when the wire format is owned by an external protocol (Nostr's NIPs,
the Model Context Protocol, the Agent Client Protocol) or by this repository's own
code (`kind.rs`, `builders.rs`, clap's derive structs), the node cites that source
instead of re-describing the format.** A corpus interface node's job is to say what
boundary exists, who owns its shape, and what contract callers may rely on -- not to
re-encode the shape a second time in Markdown.

## A note on `type`

Parent Feature `#602`'s success criteria list the corpus's in-scope surfaces with
interface and event documentation as **one combined item** -- "interfaces/events" --
and `node.schema.json`'s enum encodes that as the single value `interfaces-events`,
not two separate values. A node built from this template therefore carries
`type: interfaces-events`, the same value a node built from `#1337`'s event-kind
template carries. The `type` enum does not distinguish "this documents one interface"
from "this documents one event kind" -- that distinction lives in subject matter and
body shape (see *Boundary* below), not in front matter. This template node itself
carries `type: governance` because it documents the corpus's own authoring rules, per
the precedent in the evidence ledger above, not because interface-shaped nodes in
general use `governance`.

## Boundary: what this template is not

Read this section before drafting.

- **Not `#1337` (event kind).** If a subject's primary identity is stateable as "kind:
  `<number>`" -- one Nostr event kind's own tag shape, content-field semantics and
  referenced NIP -- that is `#1337`'s template, not this one. This template's subject
  is the boundary itself: a CLI command group, an HTTP route group, a WebSocket
  subscription surface, or an embedded external protocol implementation. An interface
  node may legitimately span several event kinds (for example, "the channel
  membership interface" spans kinds 39000/39001/39002 plus the moderation kinds that
  mutate membership) without becoming any one kind's own node -- it `references` the
  event-kind nodes it spans instead of restating their contracts. A node that spends
  most of its evidence ledger describing one kind's tag shape has picked the wrong
  template.
- **Not `#1346`/`#1532` (reference / API Reference), noted but not resolved here.**
  `#1532` itself, filed while drafting `#1346`, names this template and `#1337` as
  "architecture/data-shape templates, not a reference-depth template for cataloguing
  a full API surface's endpoints and parameters." This template's *Required
  sections* below ask for the operation list and the contract's guarantees, not an
  exhaustive parameter-by-parameter catalogue for domain experts -- that depth, if
  the corpus ever builds it, is `#1532`'s decision to scope, and an interface node
  may `references` such a catalogue node once one exists rather than duplicate it.
- **Not the front-matter contract or corpus procedure.** Those are `node.schema.json`
  and `AGENTS.md`'s territory, unconditionally, for every node type including this
  one's own instances.

A node built from this template that drifts into either neighbor has picked the
wrong template, not merely written prose that needs tightening.

## Required sections

A corpus node using this template must carry the following in its body, in addition
to whatever schema-required front matter `node.schema.json` demands of every node:

1. **Interface description.** One paragraph stating which boundary this documents,
   which two sides exchange something across it, and the protocol/technology it
   uses (WebSocket + Nostr event, HTTP + JSON, CLI arguments + stdout JSON, MCP
   tool-call, ACP JSON-RPC method, or similar).
2. **Operations.** The actual list of calls/commands/routes/subscriptions this
   interface exposes, each entry pointing at -- never restating -- its defining
   source: a code symbol (file + function/struct), a NIP number, an MCP method name,
   an ACP method name, or a `buzz-cli` subcommand path.
3. **Contract and stability.** What a caller may rely on staying true: versioning or
   compatibility guarantees, error/failure semantics, ordering guarantees, anything
   that would be a breaking change to alter. Grounded in what the code or spec
   actually promises (for example, `buzz-cli`'s documented exit-code contract), not
   in what the author assumes should be guaranteed.
4. **Boundary statement.** An explicit paragraph naming what this node does not
   cover, using the two exclusions in *Boundary: what this template is not* as the
   checklist (not a single event kind's wire contract; not a domain-expert-depth
   parameter catalogue), plus any node-specific exclusion the author found.
5. **Relationships**, per the guidance below.
6. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node
   does not cover, who owns it, and separately, what was expected but could not be
   verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Interface name]: interface

[One paragraph: which boundary this documents, which two sides exchange something
across it, and the protocol/technology it uses.]

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| ... | [code symbol / NIP number / MCP or ACP method name / buzz-cli subcommand] | ... |

## Contract and stability

[What a caller may rely on: versioning, compatibility, error semantics, ordering.
Cite the code or spec that actually makes the promise.]

## Boundary

This node does not describe:
- [a single event kind's own wire contract -- see the event-kind node for
  <kind>, if one exists]
- [a full parameter-by-parameter catalogue for domain experts -- see the
  API-reference-depth node for <subject>, if one exists]
- [any node-specific exclusion]

## Relationships

- references: <event-kind node(s) this interface spans, if any>
- implements: corpus-template-interface  <!-- optional; see Relationships below -->

## Scope and omissions

**This node covers** ...

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ... | ... |

**Expected but not verified when this node was written:**
- ...
````

## Evidence expectations

The corpus-wide evidence rules in `AGENTS.md` apply unchanged: `FACT` means the
author opened the cited source, `INFERENCE` means the author reasoned to the claim
and rated the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated statement
attributed to whoever said it. Nothing about this template relaxes or narrows that.
Three expectations follow specifically from the industry models considered above:

- **An operation-table row is a `FACT` or nothing.** Cite the code symbol, NIP, or
  external protocol method the row names -- the same discipline `AGENTS.md`'s
  evidence section already requires of every claim. A row naming an operation that
  no cited source confirms is exactly the unverifiable-fact problem a reference-style
  operation table exists to prevent.
- **Do not restate an externally owned protocol's wire format from memory.** When
  the subject implements Nostr's NIPs, the Model Context Protocol, or the Agent
  Client Protocol, cite that protocol's own specification (or, preferably, the
  concrete code that implements it in this repository) rather than paraphrasing the
  format as though this node were the format's authority. This template exists partly
  because none of those protocols is this repository's own to redefine.
- **A contract/stability claim needs the actual promise, not an assumption.** Cite
  the code or documentation that makes the guarantee (an exit-code list, a versioning
  note, a documented compatibility policy) -- not what "should" be guaranteed absent
  a citation.

## Relationships

A node built from this template:

- **may** declare `references` toward one or more event-kind nodes (`#1337`'s
  template) it spans, when the interface's operations correspond to specific Nostr
  event kinds. Per `relationships.schema.json`, `references`' directionality is
  "source cites target as supporting context; no ownership or currency dependency
  implied" -- the loose coupling an interface-to-kind pointer needs, since the
  interface's contract can stay accurate even if an individual kind's node is later
  revised.
- **may** declare `implements` toward this template node itself (target:
  `corpus-template-interface`), once this node is merged, if the author wants the
  generated `implemented-by` edge. This template deliberately prefers `implements`
  over the `references` sibling `#1346`/`corpus-template-reference` suggests for the
  same optional self-link: `relationships.schema.json` states `implements`'
  directionality as "source is the concrete realization of target (e.g. a template
  instance of a standard)" -- a literal description of "this node is an instance of
  this template" -- whereas `references` states no such instance relationship. This
  is optional either way, since a node's own shape (Interface description /
  Operations / Contract and stability) already shows which template it followed.
  **This is a corpus-graph relationship, not a claim about code.** A statement like
  "buzz-dev-mcp implements the Model Context Protocol" belongs in the node's
  evidence ledger as a cited `FACT` about the codebase, never as an `implements`
  edge in `relationships` -- that field's target must be another corpus node's `id`,
  and no corpus node for the Model Context Protocol itself exists or is proposed.
- **may** declare `part-of` toward a broader capability or architecture node this
  interface is a constituent piece of, when one exists.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes present
in `origin/launchpad`'s corpus tree at the recorded revision -- `corpus-agents`,
`corpus-readme`, `corpus-standard-confidence`, `corpus-standard-decision-references`
-- are all procedural/meta-documents about the corpus itself, not interface-shaped
subject matter this template about interface documentation would `references`,
`implements`, or sit `part-of`. None of this batch's four sibling templates
(`#1332`, `#1337`, `#1345`, `#1349`) target this node or are targeted by it,
deliberately: all five are authored in parallel with no merge ordering between them,
so an edge to any of them would be as likely to break in CI as to resolve. The first
interface-shaped instance node is the natural moment to add a `references` or
`implements` edge back to this template, once it exists.

## Note on Definition of Done

Issue `#1342`'s own Definition of Done carries the same four bullets found copied
across `#1326`-`#1351` -- "states scope and authority/source of the policy,"
"separates MUST requirements from SHOULD guidance," "defines enforcement/checks and
exception/escalation process," "links decisions or higher-order policy instead of
duplicating them" -- verbatim from the standards-track issues that produced
`standards/confidence.md` and `standards/decision-references.md`. Those describe a
**policy/standard** node (a MUST/SHOULD normative document over existing corpus
behavior); this node is a **template** (a prescription for the shape of a future
document's body). The real acceptance criterion, from parent Feature `#605` itself,
is: *"every template states its purpose, required sections, evidence expectations
and the industry model/standard it adapts."* This node is built against that
sentence -- *Required sections*, *Evidence expectations* and *Industry models
considered, and why none is adopted wholesale* above answer it directly -- rather
than against the standards-track checklist, which does not fit a document with no
MUST/SHOULD normative claims about existing system behavior to separate.

## Scope and omissions

**This node covers** what a corpus node's body must contain when it documents one
interface: the required sections, the evidence expectations for an operation or
contract claim, the industry models considered (OpenAPI, AsyncAPI) and why neither
is adopted as a document format, the decomposition habit adapted from AsyncAPI
instead, the explicit boundary against the event-kind and reference/API-Reference
neighbors, the note that `type` tracks corpus surface (one combined
`interfaces-events` value) rather than the interface/event-kind distinction, and the
relationship types a node built from this template should use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A single Nostr event kind's own wire contract | `#1337` (event-kind template) |
| Field-by-field, domain-expert-depth API-parameter cataloguing | `#1346`/`#1532` (reference / API Reference gap, undecided) |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**
- **No corpus node instance has yet been drafted from this template.** Every
  required section and the skeleton above is validated only against this
  repository's actual interface-shaped code (`buzz-cli`, `buzz-sdk`, `router.rs`,
  `nip11.rs`, `buzz-dev-mcp`, `buzz-acp`) and against the two industry models
  considered, not against a real instance node passing `validate.py` end to end.
  The first interface node drafted from this template may surface a required
  section that does not fit every interface shape cleanly.
- **Whether `implements` (this template's choice) or `references` (`#1346`'s
  choice) is the corpus-wide convention for a node's optional self-link to its own
  template is not settled anywhere outside this node's own reasoning.** Both are
  schema-legal; no standard adjudicating between them was found under
  `launchpad/docs/corpus/standards/`.
- **The Model Context Protocol's and Agent Client Protocol's own specification
  documents were not fetched or read directly** -- their existence and this
  repository's use of them was verified through this repository's own code
  (`rmcp` dependency, `acp.rs`'s doc comment) rather than through MCP's or ACP's
  primary specification text, unlike the Diátaxis/Good Docs Project/OpenAPI/AsyncAPI
  sources above, which were fetched and read directly.
