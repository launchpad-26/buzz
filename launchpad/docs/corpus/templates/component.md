---
id: corpus-template-component
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
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template, policy, or component."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's existing meta-documents, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance, so governance is the precedent for a corpus node that documents the corpus's own authoring rules rather than a piece of architecture/implementation/etc. content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states depends-on's directionality as 'source requires target to be true/current for source's own claims to hold' and part-of's as 'source is a constituent section/child of target', with generated inverses depended-on-by and has-part respectively."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four documents a specific software component."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The already-drafted, unmerged architecture-component template (issue #1326, branch task/1326-corpus-template-architecture-component) scopes its subject to the C4 model's Component diagram: one container's internal building blocks, decomposed with a required Mermaid diagram, front matter type: architecture, and a required part-of relationship toward the container it decomposes. It states in its own Boundary section that class/function-level design is not its concern and names #1341 (implementation-reference) as the owner of that deeper level, not this node's subject."
    entry_class: FACT
    evidence:
      - "git_show(ref='origin/task/1326-corpus-template-architecture-component', path='launchpad/docs/corpus/templates/architecture-component.md') -> full document read at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "At the recorded revision, 6 of this repository's 30 crates carry a README.md -- buzz-agent, buzz-pairing-cli, buzz-cli, buzz-acp, git-credential-nostr, git-sign-nostr -- and each is structured as an install/usage guide (headings such as Install, Authentication, Usage, Configuration), not as a systematic responsibility/interface/dependency description; the other 24 crates carry no README.md at all."
    entry_class: FACT
    evidence:
      - "find_crates_readmes() -> crates/buzz-agent/README.md, crates/buzz-pairing-cli/README.md, crates/buzz-cli/README.md, crates/buzz-acp/README.md, crates/git-credential-nostr/README.md, crates/git-sign-nostr/README.md, out of `ls -d crates/*/` counting 30 crate directories, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "crates/buzz-core/src/lib.rs opens with a crate-level `//!` doc comment reading 'buzz-core -- zero-I/O foundation types for the Buzz relay. Provides StoredEvent, filter matching, kind constants, and event verification. All other Buzz crates depend on this one.', followed by a `///` doc comment on every `pub mod` declaration naming that module's responsibility (for example 'NIP-AM: Agent Turn Metric -- payload type and encrypt/decrypt helpers.' on `pub mod agent_turn_metric`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/lib.rs"
  - statement: "At the recorded revision, 12 of this repository's 30 crates carry `#![warn(missing_docs)]` in their crate root -- buzz-audit, buzz-core, buzz-pubsub, buzz-sdk, buzz-workflow, buzz-conformance, buzz-auth, buzz-db, buzz-deletion, buzz-relay, buzz-test-client, buzz-search -- a lint that, per its upstream description, 'detects missing documentation for public items' so that a library's public interface stays documented."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='missing_docs', scope='crates/*/src/lib.rs') -> 12 matches: crates/buzz-audit/src/lib.rs:2, crates/buzz-core/src/lib.rs:2, crates/buzz-pubsub/src/lib.rs:2, crates/buzz-sdk/src/lib.rs:2, crates/buzz-workflow/src/lib.rs:2, crates/buzz-conformance/src/lib.rs:39, crates/buzz-auth/src/lib.rs:2, crates/buzz-db/src/lib.rs:2, crates/buzz-deletion/src/lib.rs:2, crates/buzz-relay/src/lib.rs:2, crates/buzz-test-client/src/lib.rs:2, crates/buzz-search/src/lib.rs:2, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The `missing_docs` lint is 'allow' by default in upstream Rust ('this lint is \"allow\" by default because it can be noisy, and not all projects may want to enforce everything to be documented'), so this repository's `#![warn(missing_docs)]` in 12 crates is a deliberate local tightening of the language default, not something Rust does for every crate automatically."
    entry_class: FACT
    evidence:
      - "https://doc.rust-lang.org/rustc/lints/listing/allowed-by-default.html"
  - statement: "The Rustdoc Book states that lines starting with `//!` at the top of a crate's lib.rs 'indicate module-level or crate-level documentation' composing 'the front-page' of the generated docs, while `///` documents individual items, and recommends each item's documentation follow the structure: a short sentence explaining what it is, a more detailed explanation, at least one runnable code example, and a Panics section when edge cases can be reached."
    entry_class: FACT
    evidence:
      - "https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html"
  - statement: "At the recorded revision, 16 of this repository's other crates declare `buzz-core` as a dependency in their Cargo.toml, corroborating buzz-core's own lib.rs claim that 'all other Buzz crates depend on this one.'"
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='^buzz-core', scope='crates/*/Cargo.toml', exclude='crates/buzz-core/Cargo.toml') -> 16 matches: crates/buzz-audit, crates/buzz-acp, crates/buzz-media, crates/buzz-pubsub, crates/buzz-auth, crates/buzz-sdk, crates/buzz-search, crates/buzz-db, crates/buzz-admin, crates/buzz-test-client, crates/buzz-deletion, crates/buzz-cli, crates/buzz-pairing-cli, crates/buzz-dev-mcp, crates/buzz-relay, crates/buzz-workflow, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The unmerged research note (launchpad-26/buzz#1466, launchpad/Research/project-documentation-templates.md on branch docs/research-project-doc-templates) does not devote a section to 'component' as a template kind, but one aside in its 'When to use it -- and when not to' section reads verbatim: 'arc42 is too heavy for a component. Twelve sections on a single crate produces ten empty ones. Use it for a system, or lift only §5/§9.' -- naming a single crate as its own working example of what a component-scale document is."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note, launchpad/Research/project-documentation-templates.md on branch docs/research-project-doc-templates)"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than the MUST/SHOULD/enforcement/escalation checklist that issue #1330's own Definition of Done carries."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent Feature acceptance criteria) and the #1330/#1338/#1339/#1341/#1344/#1350 batch dispatch brief, which identified #1330's DoD text as boilerplate copied from the standards-track issues"
  - statement: "Because issue #1330 is titled plainly 'component' with no 'architecture-' prefix, unlike #1326's explicit 'architecture-component' title, and because the already-drafted #1326 template's own Boundary section reserves class/function-level detail for #1341 while reserving container-level decomposition and diagram notation for itself, a node built from this template should document one software component (a crate, or a cohesive module inside one) as a standalone knowledge artifact -- its responsibility, public interface and real dependency edges -- independent of whether it is ever drawn in an architecture-component diagram, rather than being a second template for the same C4 Component-diagram subject #1326 already covers."
    entry_class: INFERENCE
    evidence:
      - "git_show(ref='origin/task/1326-corpus-template-architecture-component', path='launchpad/docs/corpus/templates/architecture-component.md') -> full document read at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
    confidence: 0.75
  - statement: "This template directs authors of a component node to set type: implementation, since node.schema.json defines that enum member as one of PRD #602's named in-scope corpus surfaces with no further distinguishing description, and a component's responsibility/interface/dependency content is code-level realization detail rather than the decomposition-and-diagram content #1326 already claims for type: architecture."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
  - statement: "Because this repository's own dominant, tooling-adjacent convention for documenting one component's responsibility and public surface is the rustdoc crate-level/item-level doc-comment pair (used in all 30 crates' lib.rs at some level, with 12 additionally enforcing missing_docs) rather than the ad hoc README pattern present in only 6 of 30 crates, this template grounds its industry model in the rustdoc convention -- verified against Rust's own primary-source documentation -- instead of reaching for an external architecture framework like C4 or arc42, both of which #1326/#1327/#1328 already adapt and which the unmerged research note itself calls too heavy for a single crate."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/lib.rs"
      - "https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html"
    confidence: 0.65
  - statement: "part-of is the relationship type a node built from this template should declare, optionally, toward an architecture-component node whose building-block table names this component, because relationships.schema.json defines part-of as 'source is a constituent section/child of target', which matches a single documented building block's relationship to the decomposition document that lists it more closely than any of the schema's other four types; the relationship is optional rather than required because this template's own INFERENCE above treats a component node's validity as independent of any architecture-component node existing."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "git_show(ref='origin/task/1326-corpus-template-architecture-component', path='launchpad/docs/corpus/templates/architecture-component.md') -> full document read at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
    confidence: 0.6
---

# Template: component

How to write a corpus node whose subject is one software component -- a
crate, or a cohesive module inside one -- documented as a standalone
knowledge artifact: what the node must contain, what evidence it needs, and
the industry model it adapts. This is a template node, not a policy node --
it prescribes the shape of a future document rather than a MUST/SHOULD rule
about corpus-wide behavior. See *Note on Definition of Done* below for why
that distinction matters for this specific node.

## Scope and authority

**This node covers** what a corpus node documents when its subject is a
single software component: its responsibility, its public interface, and its
real dependency edges in both directions. It states the required sections
such a node's body must carry, the evidence expectations for the claims it
makes, and the industry model it adapts.

**It does not cover** the front-matter contract itself (`node.schema.json`
governs that, unconditionally, for every node type), how to create/update/
retire a node procedurally (`AGENTS.md` governs that), or the container-level
decomposition-with-diagram subject that `#1326`'s architecture-component
template already owns. See *Boundary* below for the full, explicit line
between the two.

**Its authority is derived, not original.** The structural half is already
law: `node.schema.json` enforces front matter, `validate.py` runs that
schema, and CI runs `validate.py` on every corpus change. What this node adds
is the half no schema can hold -- which sections a component node needs, what
evidence backs a responsibility or interface claim, and which industry model
grounds the whole shape. That half is enforced by review, the same way the
existing corpus standards describe their own review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| One container's internal decomposition, with a required diagram | `launchpad/docs/corpus/templates/architecture-component.md` (`#1326`) |
| The industry model this template adapts | *Industry model* below, and the primary sources it cites |

If this node and any of those disagree, **they win** -- this one has drifted
and should be fixed.

## Industry model this template adapts

**Rustdoc's crate-level and item-level documentation convention**
(`doc.rust-lang.org/rustdoc`) -- the convention this repository's own source
already follows for every one of its 30 crates at some level. A crate-level
`//!` doc comment at the top of `lib.rs` states the crate's responsibility in
prose; the Rustdoc Book calls these lines the ones that *"compose the
front-page"* of the generated documentation. Item-level `///` doc comments
document individual public items -- modules, functions, types -- and the
Rustdoc Book recommends a fixed shape for each: *"a short sentence explaining
what it is; a more detailed explanation; at least one code example ...; even
more advanced explanations if necessary"*, plus a Panics section "every time
edge cases in your code can be reached if known." Twelve of this repository's
crates additionally enable the `missing_docs` lint, which upstream describes
as detecting *"missing documentation for public items"* and which is "allow"
by default in the language itself -- so enabling it here is this repository's
own deliberate choice to hold its public interfaces to a documented standard,
not something Rust does automatically.

**Why this instead of C4 or arc42.** `#1326`, `#1327` and `#1328` already
adapt the C4 model and arc42 for architecture-context/-container/-component;
reaching for either again here would be citing the same industry model for a
second, narrower purpose it was not designed for. The unmerged research note
(`launchpad-26/buzz#1466`, cited as `TEAM_KNOWLEDGE` above because it is not
an accepted decision) independently makes the same call about arc42
specifically: *"arc42 is too heavy for a component. Twelve sections on a
single crate produces ten empty ones."* -- naming a single crate as its own
example of component scale, which matches this template's subject exactly.
This repository does not need to borrow an external documentation framework
for what a component is; it already has one, in its own source tree, adopted
consistently enough (30/30 crates carry crate-level docs at some level, 12/30
enforce coverage on public items) that a template built from it does not
have to invent conventions the codebase does not already follow.

## Boundary: what this template is not

Read this section before drafting. The naming similarity between
`component` (`#1330`, this node) and `architecture-component` (`#1326`,
already drafted) is real and is addressed head-on, not by silent adjacency:

- **Not architecture-component (`#1326`).** `#1326` documents **one
  container's internal decomposition** -- a required Mermaid component
  diagram, a building-block table enumerating every component inside that
  container, and a `part-of` relationship toward the container. A node built
  from *this* template documents **one component**, standing alone: it does
  not decompose a container, it does not require a diagram, and its
  existence and validity do not depend on any architecture-component node
  existing at all. A component node *may* optionally be the deeper detail
  behind one row of an architecture-component's building-block table --
  see *Relationships* below -- but that linkage is optional, not the
  reason the node exists.
- **Not implementation-reference (`#1341`).** Per `#1326`'s own Boundary
  section, class/function-level design detail is `#1341`'s concern, not
  `#1326`'s -- and it is not this template's either. `#1341` (per the
  batch dispatch brief that produced both templates in parallel) is a
  traceability artifact: how a piece of code concretely realizes a spec,
  decision or contract, using the schema's `implements` relationship type.
  This template's subject is different in kind: a component node states
  what a component *is and exposes*, not how it *satisfies* some other
  document. The two may share the `implementation` surface value (`type:
  implementation`) -- surface and document genre are orthogonal, the same
  distinction `#1346`/reference draws between corpus surface and
  documentation form -- without being the same template.
- **Not the ad hoc crate README.** 6 of this repository's 30 crates carry a
  `README.md`, each shaped as an install/usage guide (Install,
  Authentication, Usage, Configuration headings). That is real, valuable
  content, but it is not this template's subject and this template does not
  ask an author to write a second one. A component node documents
  responsibility, interface and dependencies as **corpus-governed,
  evidence-cited, schema-validated** content; a crate README remains a
  separate, ungoverned convenience document for a human trying to run the
  crate. A component node **should** link to an existing crate README as a
  citation when one exists (see *Evidence expectations*), not restate its
  content.

A node built from this template that drifts into any of the three above has
picked the wrong template, not merely written a long document.

## Required sections

A corpus node using this template's `type: implementation` must carry the
following in its body, in addition to whatever schema-required front matter
`node.schema.json` demands of every node:

1. **Purpose and scope statement.** One paragraph naming the component (the
   crate, or the module and the crate it lives inside) and what question the
   node answers for a reader.
2. **Responsibility.** What the component is for, in prose, cited to its
   crate-level (`//!`) doc comment or nearest equivalent if the language or
   subsystem has no such comment.
3. **Public interface.** The contract other code relies on -- exported
   types, functions, traits, or (for a non-Rust component) the equivalent
   public surface -- each cited to the real declaration, not to a
   description of what the author believes it does.
4. **Dependencies**, in both directions (see *Evidence expectations* for
   what each direction is cited to):
   - **Depends on** -- what this component requires to build or run.
   - **Depended on by** -- what else in the repository requires this
     component.
5. **Boundary statement.** An explicit paragraph naming what this node does
   not cover, using the three exclusions in *Boundary: what this template is
   not* as the checklist, plus any node-specific exclusion the author found.
6. **Relationships**, per the guidance below.
7. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the
   node does not cover, who owns it, and separately, what was expected but
   could not be verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Component name]

[One paragraph: what this component is (crate, or module within a named
crate), and what question this node answers about it.]

## Responsibility

[What the component is for, cited to its crate-level doc comment or nearest
equivalent.]

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| ... | fn / type / trait / module | one sentence | path/symbol citation |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| ... | ... | Cargo.toml / equivalent manifest citation |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| ... | ... | Cargo.toml / equivalent manifest citation |

## Boundary

This node does not describe:
- [the container-level decomposition this component may sit inside -- see
  the architecture-component node for <container>, if one exists]
- [how this component satisfies any spec/decision/contract -- see
  #1341's implementation-reference template, if instantiated]
- [install/usage instructions for a human running this component -- see
  <crate>/README.md, if one exists]
- [any node-specific exclusion]

## Relationships

- part-of: <the architecture-component node's id, if this component is one
  row of its building-block table -- optional>
- depends-on: <another component node this one's claims require to stay
  current -- only once that node exists in the corpus>

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

The corpus-wide evidence rules in `AGENTS.md` apply unchanged: `FACT` means
the author opened the cited source, `INFERENCE` means the author reasoned to
the claim and rated the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated
statement attributed to whoever said it. Nothing about this template relaxes
or narrows that. Three expectations follow specifically from the industry
model this template adapts:

- **A responsibility claim is a `FACT` or nothing.** Cite the component's
  crate-level doc comment (`//!` in `lib.rs`, or the nearest equivalent for
  a non-Rust component) if one exists. If none exists, that absence is
  itself worth stating in *Scope and omissions* -- a component with no
  authored responsibility statement anywhere in its own source is a real
  gap, not something to paper over by inventing prose for it.
- **A public-interface row is a `FACT` citing the real declaration, never a
  description of intended behavior.** `validate.py` never inspects whether
  a citation supports its row -- the same caution `AGENTS.md` gives for
  every other claim applies doubly here, since an interface table is the
  part of this node most likely to be read as a contract.
- **A dependency claim is cited to the manifest, never to prose
  recollection.** `Cargo.toml` (or the equivalent for a non-Rust component)
  is real, verifiable, structural evidence for the *depends on* direction. A
  reverse *depended on by* claim is established the same way, by finding
  every other manifest that names this component -- not by describing the
  system from memory. Do not cite a deployment manifest, process list, or
  runtime topology for either direction: those describe how components are
  *run*, not what one component's own build-time contract requires, and
  conflating the two is the same category error `#1326`'s Evidence
  expectations section warns against for deployment evidence at the
  container level.
- **An existing crate README, if one exists, is real evidence for the
  Responsibility or Public interface section** -- cite it directly rather
  than restating its content in different words, per *Boundary*'s
  instruction not to write a second README.

## Relationships

A node built from this template:

- **may** declare `part-of` targeting the id of an architecture-component
  node, if one exists and its building-block table names this component.
  Per this node's own `INFERENCE` above, this is optional: a component
  node's validity never depends on an architecture-component node existing.
- **may** declare `depends-on` toward another component node, when this
  node's own claims depend on that other node being true/current -- and
  only once that target node exists in the corpus being merged into. This
  is distinct from the body's own *Dependencies* section: a Cargo.toml
  dependency on a crate with no corpus node yet is real, citable content for
  the body, but it cannot become a front-matter `relationships[].depends-on`
  edge until a node exists for it to target. Do not conflate "this crate
  depends on that crate" with "this corpus node depends on that corpus
  node" -- the first is a body-level fact about code, the second is a
  graph edge that must resolve or the check fails.
- **may** declare `references` toward this template node itself (target:
  `corpus-template-component`) once this node is merged, if the author
  wants the generated `referenced-by` edge; this is optional, since a
  node's use of `type: implementation` and its shape already show which
  template it followed.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target
  against `origin/launchpad` (or whatever the merge-target branch is at the
  time), never against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes
present in `origin/launchpad`'s corpus tree at the recorded revision --
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references` -- are all procedural/meta-documents
about the corpus itself, not a specific software component this template's
subject matter would `depends-on`, `references`, or sit `part-of`. None of
the sibling batch tasks in flight in parallel (`#1338`, `#1339`, `#1341`,
`#1344`, `#1350`) target this node or are targeted by it, deliberately: all
six are authored in parallel with no merge ordering between them, so an edge
to any of them would be as likely to break in CI as to resolve. `#1326`
(architecture-component) is also unmerged at the time of writing and is
therefore not a valid relationship target either, despite the close
conceptual relationship documented above in *Boundary* -- the first real
component node, once written after both templates land, is the natural
moment to add that `part-of` edge.

## Note on Definition of Done

Issue `#1330`'s own Definition of Done carries four bullets -- "states scope
and authority/source of the policy," "separates MUST requirements from
SHOULD guidance," "defines enforcement/checks and exception/escalation
process," "links decisions or higher-order policy instead of duplicating
them" -- copied verbatim from the standards-track issues that produced
`standards/confidence.md` and `standards/decision-references.md`. Those
describe a **policy/standard** node (a MUST/SHOULD normative document over
existing corpus behavior); this node is a **template** (a prescription for
the shape of a future document). The real acceptance criterion, from parent
Feature `#605` itself, is: *"every template states its purpose, required
sections, evidence expectations and the industry model/standard it adapts."*
This node is built against that sentence -- *Required sections*, *Evidence
expectations* and *Industry model this template adapts* above answer it
directly -- rather than against the standards-track checklist, which does
not fit a document with no MUST/SHOULD normative claims about existing
system behavior to separate.

## Scope and omissions

**This node covers** what a corpus node documents when its subject is one
software component, standing alone: the required body sections, the evidence
expectations for a responsibility/interface/dependency claim, the industry
model (rustdoc's crate-level/item-level documentation convention) the shape
adapts, the explicit boundary against the architecture-component and
implementation-reference templates and against the ad hoc crate README
pattern, and the relationship types a node built from this template should
use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| One container's internal decomposition, with a required diagram | `#1326` (architecture-component), unmerged at time of writing |
| How a component satisfies a spec/decision/contract | `#1341` (implementation-reference), open and not yet drafted at time of writing |
| Install/usage instructions for a human running a component | The component's own `README.md`, when one exists (only 6 of 30 crates have one today) |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| Whether a non-Rust component (desktop TypeScript, mobile Dart) needs a different evidence anchor than a crate-level doc comment | Not resolved here; flagged below as unverified |

**No relationships declared in this node's own front matter.** See
*Relationships* above for what was checked and why none of the four nodes
that exist on `origin/launchpad` at the recorded revision are a fit, and why
`#1326` -- the closest conceptual neighbor -- is not a valid target either
while it remains unmerged.

**Expected but not verified when this node was written:**

- **No node has yet been authored from this template.** Every claim above
  about what a component node needs is grounded in this repository's own
  rustdoc/Cargo.toml precedent and in `#1326`'s already-reviewed shape, not
  in a worked instance. The first real component node -- most plausibly one
  of the crates already carrying `#![warn(missing_docs)]`, since those have
  the strongest existing interface-documentation discipline to cite -- is
  what will actually test whether the required sections above are
  sufficient or need revision.
- **Whether this template's rustdoc-grounded shape transfers cleanly to a
  non-Rust component was not checked.** The evidence anchors above
  (`//!` crate doc comment, `Cargo.toml`, `missing_docs`) are Rust-specific.
  `desktop/` (TypeScript) and `mobile/` (Dart) each have their own module
  conventions that were not inspected for this node; a component node for
  either would need to identify its own language-appropriate equivalent of
  a crate-level doc comment and a dependency manifest, which this template
  does not name.
- **Whether the six existing crate READMEs contain responsibility or
  interface content this template's *Evidence expectations* section would
  accept as a citation, versus only install/usage prose, was not checked
  file-by-file.** *Boundary* above characterizes all six by their heading
  shape (Install, Authentication, Usage, Configuration) from a headline
  read, not a full read of each file's body content.
