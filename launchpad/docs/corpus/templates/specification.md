---
id: corpus-template-specification
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
  - statement: "node.schema.json's type field is a closed enum of thirteen corpus surfaces (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion), and contains no template or policy member."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every existing corpus meta-document at the recorded revision uses type: governance (README.md, standards/confidence.md, standards/decision-references.md), except AGENTS.md, which uses type: agent because it is itself an agent-facing procedure."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries exactly four validated content nodes outside schema/ (which is excluded from validation): AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md. No templates/ subtree exists there yet."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, schema/** (excluded), standards/confidence.md, standards/decision-references.md"
  - statement: "validate.py excludes only the schema/ top-level subdirectory from corpus discovery and validation, so a node placed under launchpad/docs/corpus/templates/ is discovered and validated exactly like any other corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "RFC 7322 (RFC Style Guide) Section 4 marks Title, Abstract, Status of This Memo, Copyright Notice, Table of Contents, Body of the Memo (including Introduction) and Security Considerations as [Required] components of an RFC's structure, and states plainly: 'All RFCs must contain a section that discusses the security considerations relevant to the specification.'"
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc7322"
  - statement: "RFC 2119 defines MUST as meaning 'the definition is an absolute requirement of the specification,' SHOULD as meaning valid reasons may exist to ignore an item but 'the full implications must be understood and carefully weighed,' and MAY as meaning 'an item is truly optional,' and supplies the original boilerplate sentence directing readers to interpret these words per the RFC."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc2119"
  - statement: "RFC 8174 amends RFC 2119 to state that the key words 'have the meanings specified herein only when they are in all capitals,' so lowercase 'must'/'should' carry no special obligation, and it also states the key words are themselves optional -- 'normative text does not require the use of these key words' -- and supplies an updated BCP 14 boilerplate sentence citing both RFC 2119 and RFC 8174."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc8174"
  - statement: "NIP-01, at the pinned commit already cited by this batch's event-kind template, uses capitalized normative keywords extensively (e.g. 'Relays MUST only accept connections to a single endpoint', 'Clients SHOULD open a single websocket connection') but does not define, explain, or cite RFC 2119 or BCP 14 anywhere in its text."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "The nostr-protocol/nips repository's own README.md, at the same pinned commit, does not describe any required or recommended structure, required sections, or normative-language convention for how an individual NIP document should be written; it lists existing NIPs and repository-acceptance criteria, not an authoring style guide."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/README.md"
  - statement: "docs/nips/NIP-AM.md, one of Buzz's own custom NIP proposal documents (for kind 44200, no upstream Nostr community NIP), is structured as: a title and stability-badge line, Motivation, Definitions, Event (exact JSON tag/content shape), Encryption, Decrypted Payload (with REQUIRED/OPTIONAL fields marked inline), Publisher Behavior, Relay Behavior, Client Behavior, Relationship to Other NIPs, and Security Considerations, using capitalized MUST/SHOULD/MAY throughout without itself citing RFC 2119 or BCP 14."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AM.md"
  - statement: "Of the 16 NIP proposal Markdown files under docs/nips/ at the recorded revision, a heading of exactly '## Motivation' appears in 13 and exactly '## Abstract' in 9. A case-insensitive search for a heading matching 'security considerations', 'security and privacy considerations' or 'security properties' matches 14 of the 16 files; only NIP-PMA.md and NIP-RS.md carry none of those. This shape is a strong repository convention, not a universal or formally mandated one."
    entry_class: FACT
    evidence:
      - "shell(grep -h '^## ' docs/nips/*.md | sort | uniq -c) -> '## Motivation' x13, '## Abstract' x9, out of 16 files"
      - "shell(grep -li 'security considerations\\|security and privacy considerations\\|security properties' docs/nips/*.md | wc -l) -> 14"
      - "shell(comm -23 <(ls docs/nips/*.md | sort) <(grep -li 'security considerations\\|security and privacy considerations\\|security properties' docs/nips/*.md | sort)) -> NIP-PMA.md, NIP-RS.md"
  - statement: "Of the 16 docs/nips/*.md files, exactly 7 (NIP-AA, NIP-CW, NIP-DV, NIP-IA, NIP-MP, NIP-PL, NIP-WP) contain a sentence of the form 'This document uses MUST, MUST NOT, SHOULD[, SHOULD NOT], MAY, and RECOMMENDED as defined in RFC 2119' -- citing RFC 2119 alone, by name, but using neither RFC 8174's updated BCP 14 boilerplate nor the phrase 'BCP 14' itself. A repository-wide search for 'BCP 14', 'BCP14', 'RFC 8174' or 'RFC8174' across docs/nips/*.md returns zero matches. The remaining 9 files (including NIP-AM.md) use capitalized MUST/SHOULD/MAY with no normative-language declaration of any kind."
    entry_class: FACT
    evidence:
      - "shell(grep -l 'RFC 2119\\|RFC2119\\|BCP 14\\|BCP14\\|RFC 8174\\|RFC8174' docs/nips/*.md) -> NIP-AA.md, NIP-PL.md, NIP-WP.md, NIP-CW.md, NIP-DV.md, NIP-IA.md, NIP-MP.md (7 files, all citing RFC 2119 only)"
      - "shell(grep -rn 'BCP 14\\|BCP14\\|RFC 8174\\|RFC8174' docs/nips/*.md) -> no matches"
  - statement: "docs/spec/ contains two TLA+ formal specification files (MultiTenantRelay.tla, GitOnObjectStore.tla) and one Tamarin protocol-verification file (MultiTenantAuth.spthy) -- executable/formal models, not prose documents in the shape docs/nips/*.md uses."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla"
      - "docs/spec/GitOnObjectStore.tla"
      - "docs/spec/MultiTenantAuth.spthy"
  - statement: "crates/buzz-conformance/TRACE_SCHEMA.md states, in its own opening line, that it is 'the contract between the relay's emitter and the independent replay checker,' and that it is 'grounded in docs/spec/MultiTenantRelay.tla' -- i.e. a prose contract document paired with, and subordinate to, a formal model rather than being the formal model itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/TRACE_SCHEMA.md"
  - statement: "This repository's root AGENTS.md states Buzz's 'primary API is NIP-29 over WebSocket,' with the relay's HTTP surface described as 'narrow' and reserved for media, webhooks, git smart HTTP, metadata and generic Nostr-bridge endpoints -- the same statement the event-kind and interface templates already cite for treating Nostr-over-WebSocket, not HTTP, as Buzz's dominant protocol surface."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Fetching ISO's own catalogue page for ISO/IEC/IEEE 29148 (iso.org/standard/72089.html) directly, while authoring this node, returned HTTP 403 Forbidden; a follow-up attempt against an IEEE Xplore document page for the same standard returned no retrievable page content either. Both attempts were made independently of, and reproduce, the unmerged research note's own finding that this standard could not be opened."
    entry_class: FACT
    evidence:
      - "webfetch(https://www.iso.org/standard/72089.html) -> HTTP 403 Forbidden"
      - "webfetch(https://ieeexplore.ieee.org/document/8559686) -> no page content returned"
  - statement: "The unmerged research note at launchpad/Research/project-documentation-templates.md (PR #1466) contains no heading naming 'specification' anywhere in its table of contents, confirming independently that it does not cover this template's topic; its own Open Questions section states ISO/IEC/IEEE 29148:2018's SRS outline is unread ('iso.org returned HTTP 403 to every fetch... Do not cite a clause number from these until someone has read the document'), and its OpenAPI entry describes that specification only as 'the template for HTTP API reference, in the sense that the spec is the document' -- narrower than a general specification template."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note), read directly while authoring this node -- cited as TEAM_KNOWLEDGE only, per the batch dispatch brief, because the PR is unmerged"
  - statement: "Future corpus content for Buzz's own formal/executable specifications (the TLA+ and Tamarin models under docs/spec/) is already tracked as separate, filed tasks under a different parent feature issue (#617): #1369 (git-object-store.md), #1370 (multi-tenant-auth.md), #1371 (multi-tenant-relay.md), #1372 (stateful-gateway.md), #1373 (tamarin.md) and #1374 (tla-plus.md), targeting launchpad/docs/corpus/verification/formal/ -- a different corpus subtree than launchpad/docs/corpus/templates/, and one whose objective boilerplate names it a 'verification' surface, not a specification-template instance."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue view 1369..1374 --repo launchpad-26/buzz, run directly while authoring this node"
  - statement: "The interface template (issue #1342, unmerged branch task/1342-corpus-template-interface) states its own boundary as: 'Not #1337 (event kind)... This template's subject is the boundary itself: a CLI command group, an HTTP route group, a WebSocket subscription surface, or an embedded external protocol implementation,' with required sections for an operation list and a 'Contract and stability' statement of what a caller may rely on staying true."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "task/1342-corpus-template-interface branch (unmerged PR), read directly while authoring this node"
  - statement: "Parent Feature #605 states, as its own acceptance criterion for every template task in this batch, that every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria"
  - statement: "Issue #1348's definition of done carries the same MUST/SHOULD/enforcement/policy checklist copied verbatim from the standards-track issues (compare #1309 and #1312, which produced standards/confidence.md and the still-open diagrams standard), even though #1348 is a template task rather than a policy task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1348 definition of done, compared against launchpad-26/buzz#1309's and #1312's"
  - statement: "type: governance is the closest true fit for this node, because it is a meta-document about how to author a specification corpus node rather than itself being interfaces-events, verification or architecture content, mirroring the same reasoning README.md, standards/confidence.md and standards/decision-references.md already apply to their own meta-documents against the same enum."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
    confidence: 0.8
  - statement: "A real corpus node built from this template does not have one fixed node.schema.json type the way an event-kind instance does (interfaces-events): a specification documenting a wire protocol or event format most plausibly takes interfaces-events, one documenting an internal algorithm central to system design more plausibly takes architecture or implementation, and this template does not mandate a single value because node.schema.json's type enum classifies the corpus surface the subject belongs to, not the document genre this template describes."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.65
  - statement: "This repository's own inconsistent normative-language practice -- 9 of 16 docs/nips/*.md files declaring no RFC 2119/BCP 14 convention at all, the other 7 citing RFC 2119 alone by an outdated attribution sentence, and none citing the current RFC 8174-amended BCP 14 boilerplate -- is a real, checkable gap this template's Required sections close by name, rather than an invented problem: it was found by grepping the actual files, not assumed from Buzz being 'a Nostr relay.'"
    entry_class: INFERENCE
    evidence:
      - "docs/nips/NIP-AM.md"
      - "https://www.rfc-editor.org/rfc/rfc2119"
      - "https://www.rfc-editor.org/rfc/rfc8174"
    confidence: 0.8
  - statement: "relationships.schema.json's relationshipMeta describes implements' directionality as 'source is the concrete realization of target (e.g. a template instance of a standard)' with generated inverse implemented-by, and references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied' with authored inverse referenced-by."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
---

# Template: `specification`

How to write a corpus node that documents the complete normative definition of a
**protocol, algorithm, or wire/data format** -- what must be true for an
implementation to conform, independent of any one interface that exposes it or any
one event kind that carries it. This document is the template itself, not an
instance of one: it states what a specification node must contain, not a
description of any one real Buzz protocol, algorithm, or format.

## Note on this document's structure

Issue #1348's definition-of-done text -- "states scope and authority/source of the
policy," "separates MUST requirements from SHOULD guidance," "defines
enforcement/checks and exception/escalation process," "links decisions or
higher-order policy instead of duplicating them" -- is the identical boilerplate
copied into every template task from the standards-track issues that produced
`standards/confidence.md` (#1309) and the still-open diagrams standard (#1312).
Those describe a **policy/standard** node; this document's subject is a
**template**, which regulates no corpus-wide behaviour and states no MUST/SHOULD
split of its own. This document is built against #605's real acceptance criterion
instead -- *purpose, required sections, evidence expectations, and the industry
model/standard it adapts* -- and the headings below map to those four things
directly. Note the irony deliberately: the SHOULD/MUST split this document's own
DoD boilerplate asks for is, in fact, exactly what *Required sections* below asks
every specification node to state about its own subject -- it is simply not a
claim about this template document's own authoring policy. The DoD's remaining
bullets (one hand-authored document, schema-valid front matter, one independently
maintainable idea, traceable claims, links instead of duplication, checked against
provenance, clean validation) are generic to any corpus node and are satisfied
below the same way any node satisfies them.

## Purpose

A node built from this template answers one question: **what, precisely, must an
implementation do to conform to this protocol, algorithm, or format?** It is the
corpus's normative-definition unit -- the shape a real Nostr protocol extension,
an encryption or signing algorithm, or a wire/data format takes when its rules
need to be stated once, precisely enough to implement and to test against,
independent of who calls it.

**This is not the same unit as three neighbors already in this batch or already
open.** See *Boundary against neighboring corpus content* below before assuming
this template is the right one; a specification node that drifts into any of
those three neighbors has picked the wrong template, not merely written prose
that needs tightening.

If the subject genuinely has no rules to state beyond "call this and get that back"
-- no wire format, no state machine, no encoding rules of its own -- it is
probably an `interface` (#1342) or a plain `reference` (#1346), not a
`specification`.

## The industry model this template adapts

**The two candidates a reader would reach for first both fail, and this section
says so rather than forcing either.**

**ISO/IEC/IEEE 29148:2018** ("Systems and software engineering -- Life cycle
processes -- Requirements engineering") is the nearest thing the industry has to a
standard specification/SRS outline. It cannot be cited here: fetching ISO's own
catalogue page for it returned HTTP 403 Forbidden, and a follow-up attempt against
an IEEE Xplore listing for the same standard returned nothing retrievable either --
both attempts made directly while authoring this node, independently reproducing
the unmerged research note's identical finding. Even setting availability aside,
29148 is a **requirements-engineering** standard -- it specifies how to write and
manage requirements documents (an SRS/StRS), a genre closer to a PRD than to a
protocol or wire-format specification. Nothing here treats a summary of 29148
found in a search result as a substitute for reading the standard; if it becomes
readable later, that is a re-evaluation of this section, not a patch to it.

**OpenAPI** (the specification format itself, currently 3.2.0) is real, versioned,
and freely readable, but it describes exactly one thing: an HTTP API's request and
response shapes. This repository's own root `AGENTS.md` states Buzz's primary API
is Nostr events over WebSocket, with HTTP reserved for a narrow surface (media,
webhooks, git smart HTTP, metadata, generic bridge endpoints). Forcing OpenAPI onto
a Nostr event-kind protocol or a signing algorithm would misdescribe both the
transport and the shape of what is being specified; it is the right adapted model
for a future *HTTP-endpoint-cataloguing* template (see #1532, filed for exactly
this reference-versus-API-reference gap), not for this one.

**What this repository already has, and what this template adapts instead, is its
own domain's specification convention.** Buzz is a Nostr relay, and Nostr's own
protocol-extension mechanism -- a NIP (`docs/nips/*.md` in this very repository)
-- is written in a shape that converges, informally, on the same structure the
**IETF RFC Style Guide (RFC 7322)** makes formally required of an RFC: a title and
status line, a Motivation/Abstract, the normative body, and (in 14 of the 16
files under `docs/nips/`, by heading or by a closely-named variant) a
**Security Considerations** section, which RFC 7322 states plainly *every* RFC
must contain. The convergence is real but informal:
neither `docs/nips/NIP-AM.md` nor NIP-01 itself cites RFC 2119, RFC 8174, or BCP
14 anywhere, despite using capitalized MUST/SHOULD/MAY throughout in exactly the
sense RFC 2119 defines them -- and the upstream `nostr-protocol/nips` repository's
own README, checked directly, defines no authoring style guide of its own that
would explain where the convention came from. This template adapts RFC 7322's
required-structure list and BCP 14's (RFC 2119 + RFC 8174) normative-keyword
convention explicitly, and closes the gap this research found: a specification
node built from this template **must** invoke BCP 14's boilerplate when it uses
MUST/SHOULD/MAY, which this repository's own `docs/nips/*.md` files do not
currently do.

**Formal/executable models are a related but distinct form, already owned
elsewhere.** `docs/spec/MultiTenantRelay.tla`, `docs/spec/GitOnObjectStore.tla`
and `docs/spec/MultiTenantAuth.spthy` are TLA+ and Tamarin models -- executable
specifications, not prose. `crates/buzz-conformance/TRACE_SCHEMA.md` is a prose
contract paired with, and explicitly subordinate to, one of those models. Corpus
content for these formal models is already tracked separately, under parent PRD
#617's issues #1369-#1374, targeting `launchpad/docs/corpus/verification/formal/`
-- a different subtree than `templates/`, and typed for the `verification`
surface rather than an instance of this template. This template covers the prose,
RFC/NIP-shaped normative-definition form; a specification node describing a
protocol backed by a formal model `references` that model's future corpus node
rather than restating or replacing it.

## Boundary against neighboring corpus content

This template covers **the complete normative definition of one protocol,
algorithm, or format.** It does not cover:

- **One Nostr event kind's own wire contract** -- that is `#1337`'s `event-kind`
  template: one `kind:<number>`'s tag shape, content-field semantics, and
  referenced NIP. A specification node may span several event kinds (for example,
  a specification for a whole protocol extension that defines three cooperating
  kinds) or none at all (an encryption algorithm, a signing scheme) -- it
  `references` the event-kind nodes it uses instead of restating their tag
  contracts. A specification node that spends most of its evidence ledger
  describing one kind's own tag shape has picked the wrong template.
- **A callable boundary's operation list and stability contract** -- that is
  `#1342`'s `interface` template: a CLI command group, an HTTP route group, a
  WebSocket subscription surface, or an embedded external protocol
  implementation, with the operations it exposes and what a caller may rely on
  staying true. A specification states what a format or algorithm *means*; an
  interface states what a caller may *do* with it and what promises hold across
  calls. An interface node commonly `implements` a specification node rather than
  restating its rules; a specification node does not restate an interface's
  operation list.
- **One system property that must always hold** -- that is `#1343`'s `invariant`
  template. A specification's normative body may imply several invariants (for
  example, a signing algorithm's specification implies "a signature verifies
  against exactly the key that produced it"), but each such property, if it
  deserves its own independently maintainable node, is filed as an `invariant`
  node that `references` the specification it was derived from -- not folded into
  the specification's own body as a growing checklist.
- **One testable obligation paired with its verifying test** -- that is `#1349`'s
  `test-contract` template. A specification states the rules; a test-contract
  states which specific test proves one specific rule currently holds, and its
  current enforcement status (verified/gated/pending). A specification node does
  not itself claim a rule is tested -- it `references` the test-contract node(s)
  that make that claim once they exist.
- **A formal/executable model** (TLA+, Tamarin) -- covered by the separately
  filed `verification/formal/` track under parent feature #617 (#1369-#1374),
  not by this template. A specification node whose subject is backed by such a
  model `references` that model's future corpus node.
- **The front-matter contract or corpus procedure** -- those are
  `node.schema.json` and `AGENTS.md`'s territory, unconditionally, for every node
  type including this one's own instances.

## Required sections

A node built from this template MUST contain the following, in addition to
whatever front matter `node.schema.json` requires of every node. These are
structural requirements on the node's shape, not a corpus-wide MUST/SHOULD policy
-- see *Note on this document's structure* above for why this document does not
carry one of those.

1. **A purpose and boundary statement.** One paragraph naming the single protocol,
   algorithm, or format in scope, and stating explicitly that the node covers that
   subject's normative definition only -- not any one interface exposing it, not
   any one event kind carrying it, and not the test(s) that verify it.

2. **Motivation.** Why the subject exists and what problem it solves, in the same
   register `docs/nips/NIP-AM.md`'s own Motivation section uses: what happens
   without it, and what it deliberately does not attempt (a Non-Goals subsection,
   if there is a plausible adjacent scope a reader might assume is included).

3. **Definitions.** Terms the normative body depends on, defined once, so the
   body can use them precisely without re-explaining them inline every time.

4. **Normative-language declaration.** A specification node using MUST, SHOULD,
   or MAY in its normative body MUST state, once, that these carry BCP 14 (RFC
   2119 + RFC 8174) meaning, and MUST use the current RFC 8174 boilerplate ("...
   are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and
   only when, they appear in all capitals..."), not RFC 2119's older wording
   alone. This is a real, precisely measured gap, not a hypothetical nicety: of
   Buzz's own 16 `docs/nips/*.md` files, 9 (including `NIP-AM.md`) declare no
   normative-language convention at all, and the other 7 cite RFC 2119 by a
   short attribution sentence, never the current RFC 8174-amended BCP 14
   boilerplate -- zero of the 16 mention RFC 8174 or BCP 14 by name. A lowercase
   "should" and a capitalized "SHOULD" are different claims under RFC 8174, and
   a reader cannot tell which one a node means without this declaration.

5. **The normative body itself** -- the actual precise rules: wire shapes, state
   transitions, encoding rules, ordering guarantees, error semantics, whatever
   makes this subject a specification rather than a description. This is the
   section every other required section exists to support; it is the one this
   template cannot template further, because its shape is dictated entirely by
   the subject.

6. **Versioning and compatibility.** What changes would break an existing
   implementation, and how the specification signals its own maturity --
   mirroring `docs/nips/*.md`'s own stability-badge convention (`draft` /
   `optional` / `relay`, etc.) or an equivalent explicit statement, not left
   implicit.

7. **Security Considerations.** REQUIRED, unconditionally, per RFC 7322's own
   mandatory-section rule and this repository's own strong majority convention
   (14 of 16 `docs/nips/*.md` files carry some security-considerations-shaped
   heading). What can go wrong if this specification is implemented correctly
   but used carelessly, or implemented incorrectly. A specification node with
   nothing to say here MUST say so explicitly and explain why, not omit the
   section.

8. **Relationships**, per the guidance below -- what this specification
   `references` (event-kind nodes it uses, a formal model backing it, a decision
   that established it) and what might `implement` it, without restating any of
   their content.

9. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node
   does not cover and who owns it, and separately, what was expected but could
   not be verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
---
id: specification-<subject-slug>
type: <interfaces-events | architecture | implementation -- pick per the subject's
  own corpus surface, per this template's own type-choice guidance above>
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision <sha>."
    entry_class: FACT
    evidence:
      - "commit <sha>"
  - statement: "<the subject>'s normative body uses BCP 14 (RFC 2119 + RFC 8174) keyword semantics."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc2119"
      - "https://www.rfc-editor.org/rfc/rfc8174"
---

# <Subject name> — specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when,
and only when, they appear in all capitals, as shown here.

## Purpose and boundary

One paragraph: the single protocol/algorithm/format this node documents, and that
it covers only that subject's normative definition.

## Motivation

Why this exists; what happens without it. Non-Goals, if relevant.

## Definitions

Terms used below, defined once.

## Specification

The actual rules. This is the section this template cannot write for you.

## Versioning and compatibility

What would break an implementation; current maturity.

## Security Considerations

What can go wrong. If genuinely nothing, say so and say why.

## Relationships

What this node `references` or expects to be `implemented` by, and why no more
than that.

## Scope and omissions

This node covers <subject> only. It does not cover <related subject>, tracked at
<link once it exists>.
````

## Evidence expectations

Two things are specific to a specification node, on top of the general
FACT/INFERENCE/TEAM_KNOWLEDGE rules `AGENTS.md` already owns:

- **A quoted external standard (a NIP, an RFC, a companion spec) is FACT-citable
  the same way this template document cites RFC 2119/7322/8174 and NIP-01/README
  above: a directly-fetched URL you actually read, or a commit-pinned GitHub blob
  link for a NIP under `docs/nips/` or upstream `nostr-protocol/nips`.** A
  standard you could not open (paywalled, blocked, unread) is never a FACT and
  never a paraphrase presented as one -- name it as checked-and-rejected, the way
  this template names ISO/IEC/IEEE 29148, or leave it out entirely.
- **"This rule is enforced" is a behaviour claim, not a specification claim.**
  This template's Normative body section states what MUST be true; it does not
  itself claim any implementation currently satisfies it. That claim, and its
  evidence, belongs in a `test-contract` node this specification node
  `references` -- conflating "the rule exists" with "the rule is currently
  verified" is the exact failure mode `AGENTS.md`'s evidence section already
  warns against for any corpus node.

## Relationships

**Checked, not assumed absent.** Per `AGENTS.md`, "no relationships, because
nothing exists to point at" is the exact false justification this corpus has
already produced twice, so this section names what was actually checked: at the
recorded revision, `origin/launchpad`'s corpus tree carries `corpus-agents`,
`corpus-readme`, `corpus-standard-confidence` and `corpus-standard-decision-references`,
and no other node.

**This template declares none anyway.** None of those four nodes is specific to
specification content over any other node's evidence, so an edge here would say
nothing a reader does not already get from `AGENTS.md`'s own cross-references.
The most relevant future edges -- toward `#1337`'s `event-kind` template, `#1342`'s
`interface` template, `#1343`'s `invariant` template, and `#1349`'s
`test-contract` template, all of which this document's own *Boundary* section
names by content rather than by a corpus node id -- are not yet targetable: none
of those four is merged into `origin/launchpad` at this revision, and a
`relationships[].target` naming an id no node in the merge-target branch carries
is a hard validation error. The first of those four to merge is the moment to
revisit this section, not before.

**A node built from this template** should expect to declare `references` toward
the event-kind, interface, or formal-model corpus nodes its subject touches, and
`implements` is the direction an `interface` node or a real protocol
implementation would use to point *at* a specification node, not the reverse.
This template does not mandate specific edges for its instances -- the corpus is
still too sparse for a rule about what must exist to make sense.

## Scope and omissions

**This document covers** the purpose of a `specification` corpus node, the
industry model it adapts (RFC 7322's required structure and BCP 14's
normative-keyword convention) and the two models it explicitly rejected (ISO/IEC/
IEEE 29148, unreadable and the wrong genre even if it were; OpenAPI, too narrow
to Buzz's actual HTTP-minority transport), its boundary against four neighboring
templates and one separately-tracked formal-model corpus surface, its required
sections, what evidence a specification node needs, and what relationships this
template document itself does and does not declare.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| One event kind's own wire contract | `#1337` (`event-kind` template) |
| A callable boundary's operations and stability contract | `#1342` (`interface` template) |
| One system property that must always hold | `#1343` (`invariant` template) |
| One testable obligation paired with its verifying test | `#1349` (`test-contract` template) |
| Formal/executable models (TLA+, Tamarin) as corpus content | Feature #617, issues #1369-#1374 |
| How any corpus node should cite an external standard as evidence, generally | `launchpad/docs/corpus/AGENTS.md`'s existing citation-shape rules; no more specific standard was found filed for this |
| Creating, updating and retiring any corpus node, including one built from this template | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No real `specification` node has been built from this template yet.** Whether
  the required-sections list holds up for a subject simpler or more complex than
  the NIP-AM.md-derived example used to ground it -- for instance, an algorithm
  with no wire format at all, like a key-derivation scheme -- is untested. The
  first node built from this template is the real test of it.
- **Whether ISO/IEC/IEEE 29148 would, if ever actually read, contain a
  specification-genre outline distinct from its requirements-engineering framing
  was reasoned about, not confirmed**, because the standard remains unread. If
  institutional access ever makes it readable, this section's rejection of it
  should be re-examined against the actual text, not left standing on inference.
- **Whether the two `docs/nips/*.md` files without any security-considerations-
  shaped heading (`NIP-PMA`, `NIP-RS`) omit one because they genuinely have
  nothing to say, versus an oversight, was not individually investigated** --
  only the mechanical heading search was checked. This template's own Required
  sections treat the omission as always requiring a stated reason; whether
  those two files would satisfy that bar if held to it was not tested here.
- **Whether the `implements` relationship's directionality (`AGENTS.md`'s own
  cited "source is the concrete realization of target, e.g. a template instance
  of a standard") is the right edge for an `interface` node pointing at the
  specification it implements, versus `references`, was reasoned from
  `relationships.schema.json`'s own description and not settled against a real
  example of either edge in use** -- no corpus node currently declares either.
