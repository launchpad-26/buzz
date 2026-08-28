---
id: corpus-template-event-kind
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
  - statement: "node.schema.json's type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no template or policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every corpus meta-document that exists on origin/launchpad at the recorded revision -- AGENTS.md excepted, which is type: agent -- uses type: governance: README.md, standards/confidence.md and standards/decision-references.md all do. No templates/ subtree exists on origin/launchpad at this revision (see the git_ls_tree entry below), so this claim is checked against what is actually merged, not against the unmerged batch-1/batch-2 template PRs."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "This node is a meta-document about how to author a corpus node describing one Nostr event kind, not itself an event-kind node, so governance is chosen by the same reasoning corpus-readme already recorded for its own type choice (a meta-document about the corpus is not itself a member of the surface it describes), rather than as an independent precedent this node invents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
    confidence: 0.6
  - statement: "A real corpus node instance authored from this template -- documenting one actual Buzz event kind -- would most plausibly take node.schema.json's interfaces-events type, since that is the enum's own dedicated value for the corpus's protocol/interface surface; this template document itself is not such an instance and does not decide that choice on the instance's behalf."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries exactly four validated content nodes: AGENTS.md (corpus-agents), README.md (corpus-readme), standards/confidence.md (corpus-standard-confidence) and standards/decision-references.md (corpus-standard-decision-references); schema/ is present but excluded from validation. None of the ten template/standard PRs opened by the two prior corpus-template batches (#1527-#1537) are merged as of this revision."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md; schema/ present but excluded from validation"
      - "gh_pr_list(launchpad-26/buzz, search:'corpus-template') -> #1527-#1537 all state OPEN at this revision"
  - statement: "NIP-01 defines an event's kind field interpretation with four numeric categories: regular for kind n such that 1000<=n<10000 || 4<=n<45 || n==1 || n==2; replaceable for 10000<=n<20000 || n==0 || n==3; ephemeral for 20000<=n<30000; and addressable for 30000<=n<40000."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "NIP-01 defines a tag's structure as: 'The first element of the tag array is referred to as the tag name or key and the second as the tag value,' with elements after the second carrying no conventional name."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "NIP-01 illustrates the content field's role concretely for kind 0: content is set to a stringified JSON object shaped {name, about, picture}."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "Buzz's own plaintext-content custom kinds tend to follow NIP-01's content-as-stringified-JSON pattern (e.g. KIND_TEAM_CATALOG's content is documented in kind.rs as 'a versioned JSON body'), while its encrypted-content kinds (e.g. KIND_AGENT_TURN_METRIC, KIND_PERSONA) instead carry opaque ciphertext at the wire level whose *decrypted* payload follows the same JSON-object convention -- this is this template's own generalization from reading multiple kind.rs entries side by side, not a rule NIP-01 itself states."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
    confidence: 0.7
  - statement: "NIP-29 requires that events sent by users to groups (chat messages, text notes, moderation events, etc.) MUST have an h tag with the value set to the group id -- the exact convention this repository's own AGENTS.md cites as the basis for Buzz's channel scoping."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
  - statement: "NIP-29 documents each group-state/moderation action in its own kinds:9000-9020 range as its own kind with its own required tags -- for example put-user (kind 9000) requires a p tag shaped [\"p\", \"<pubkey-hex>\", \"<optional-roles>\"] -- rather than one generic moderation-event kind with an action field in content. NIP-29 keeps the two user-initiated group-membership kinds, join-request (9021) and leave-request (9022), as a textually separate category from that 9000-9020 moderation range, though both categories share the one-kind-per-action shape this template's Required section 4 draws on."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
  - statement: "buzz-core/src/kind.rs states in its own module doc comment that it 'is the authoritative source for Buzz kind numbers,' and that every constant is u32 because 'NIP-01 specifies kind as an unsigned integer, and u32 covers the full range without truncation.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's doc comments name, per constant, the referenced NIP (or 'Buzz custom'/a NIP-XX label), and for the newer Buzz-specific kinds also the delivery classification, tag shape/cardinality and content-field shape -- older NIP-derived constants (e.g. KIND_PROFILE, KIND_MUTE_LIST, KIND_REACTION) carry only a one-line NIP reference with no such breakdown, so this density is a property of the newer entries, not a uniform convention across the whole file. For example KIND_AGENT_TURN_METRIC (44200) is documented in kind.rs as 'Regular stored event (append-only, never replaced) ... Tags: exactly one `p` (owner pubkey) and one `agent` (agent pubkey == event pubkey); no `h` tag,' with content NIP-44 encrypted and owner-scoped (p-gated) reads only; the companion phrasing 'a regular event by Buzz convention ... stored, append-only, never replaced' and 'Events MUST have exactly one p tag (the owner) and exactly one agent tag' is docs/nips/NIP-AM.md's own wording, not kind.rs's."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "docs/nips/NIP-AM.md"
  - statement: "kind.rs cross-checks its own classification with compile-time assertions (e.g. 'assert!(is_parameterized_replaceable(KIND_PERSONA))') and a runtime unit test, no_duplicate_kind_values, that asserts every value in ALL_KINDS is unique -- the two enforced invariants a new kind's number must satisfy before it can be documented as final."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines named sets governing per-kind read access control independently of the referenced NIP text: AUTHOR_ONLY_KINDS, P_GATED_KINDS, SHARED_GATED_KINDS and RESULT_GATED_KINDS. Each set's own doc comment states which relay chokepoints consult it, but only SHARED_GATED_KINDS's doc comment also states an explicit non-membership rationale for a specific kind (KIND_TEAM is documented as deliberately NOT a member because 'its writers never emit shared'); AUTHOR_ONLY_KINDS and RESULT_GATED_KINDS name their chokepoints and members without a comparable per-kind inclusion/exclusion rationale."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "docs/nips/NIP-AM.md is Buzz's own custom-NIP proposal document for kind 44200 (a kind with no existing Nostr community NIP), structured as: a title and stability badges line ('draft optional relay'), a Motivation section, a Definitions section, an Event section giving the exact JSON tag/content shape and tag cardinality in prose, an Encryption section naming the exact key-derivation and cipher, and a Decrypted Payload section giving the exact JSON field shape of the plaintext, with REQUIRED/optional fields marked inline."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AM.md"
  - statement: "This repository's root AGENTS.md states: 'All event kind integers are defined in buzz-core/src/kind.rs. New features get new kind integers -- add them here first, then implement handling in the relay,' and separately: 'Channels use h tags (NIP-29 group tag), not e tags... Addressable events that describe a channel carry its id in their d tag instead: kind:39000 (metadata), kind:39001, kind:39002 (membership).'"
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "AGENTS.md (corpus) states that one node is one independently maintainable idea, and that a second concept, contract or procedure discovered while writing does not get folded in but is filed as its own task and linked instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md (corpus) states that every non-.md file under the corpus root is rejected today, including one placed under generated/, because no generator exists yet to reproduce it from canonical Markdown (issue #1316), so any worked-example sequence diagram in an event-kind node must be authored as inline text (e.g. a Mermaid fenced code block), never a linked image."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "relationships.schema.json defines the implements relationship type's directionality as 'source is the concrete realization of target (e.g. a template instance of a standard),' with a generated inverse edge (implemented-by) -- the mechanism by which a real event-kind instance node would point back at this template rather than restating its requirements in prose."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "Issue #605 (parent PRD) states the acceptance criterion for every template task in this batch as: every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts -- distinct from the byte-identical MUST/SHOULD/enforcement/policy checklist copied into this node's own issue #1337 from the standards-track issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent PRD, relayed via the corpus-templates batch dispatch brief)"
  - statement: "Issue #1337's definition of done otherwise requires one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links instead of duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1337 definition of done"
  - statement: "Issue #1342 (task: define the interface corpus template) exists as an open, filed sibling template task being authored in parallel by a different agent in this same batch, so the boundary this node draws against interface-typed content names a real filed issue rather than a hypothetical future one; its actual template text did not exist to read at the time this node was authored."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue view 1342 --repo launchpad-26/buzz, run directly while authoring this node"
  - statement: "The research note at launchpad/Research/project-documentation-templates.md (unmerged PR #1466) does not cover event-kind or Nostr-kind documentation at all -- confirmed by inspecting the note's own structure and topic list rather than assumed from the batch dispatch brief's claim of the same fact."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note), read directly while authoring this node"
  - statement: "At the recorded revision, docs/nips/ contains 16 Markdown NIP-proposal files (plus two non-Markdown fixture files for NIP-MP that are not proposal documents), none of which states whether a docs/nips/NIP-XX.md file is a prerequisite for a corpus event-kind node rather than an alternative to one."
    entry_class: FACT
    evidence:
      - "shell(ls docs/nips/*.md | wc -l) -> 16"
---

# Template: event-kind

How to write a corpus node whose subject is an **event kind** — one Nostr `kind`
integer that Buzz defines or adopts, together with the wire contract that makes an
event of that kind meaningful: its referenced NIP, its tag shape, its content-field
semantics, and its access-control and storage model. This node is the template
itself, not an instance of one: it states what an event-kind node must contain, not
a description of any one real Buzz kind.

## Scope and authority

**This node covers** the purpose of an event-kind document, the sections it must
contain, what evidence each section needs, and the industry model it adapts —
which, uniquely among this batch's five templates, is not drawn from Serina's
research note at all, but from this repository's own domain: Buzz *is* a Nostr
relay, and a Nostr event's `kind` field is the protocol's own load-bearing concept.

**A note on this node's own definition of done.** Issue #1337's checklist carries a
MUST/SHOULD/enforcement/exception block copied verbatim from the standards-track
issues that produced `standards/confidence.md` and `standards/decision-references.md`
— documents whose subject is a normative policy. This node's subject is a template,
and the parent PRD (#605) states the acceptance bar that actually applies to a
template task: *every template states its purpose, required sections, evidence
expectations and the industry model/standard it adapts.* This document is built
against that sentence. The rest of #1337's checklist — one hand-authored document,
schema-valid front matter, one independently maintainable idea, traceable claims,
links instead of duplication, a check against the recorded revision, a clean
validator run — is generic to any corpus node and is honoured below regardless.

**Its authority is derived, not original.** `node.schema.json` is the front-matter
law; `AGENTS.md` (corpus) is the create/update/retire procedure; `standards/confidence.md`
and `standards/decision-references.md` are the two evidence-mechanics standards
merged so far. This document adds nothing to any of those. What it adds is the part
none of them can: what an *event-kind-scoped* node must say, and where that shape
comes from.

| For | Read |
|---|---|
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Evidence classes and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| Relationship types and directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The base Nostr event envelope, kind ranges, tags, primary source | `https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md` |
| Group/channel scoping and moderation-kind conventions, primary source | `https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md` |
| Buzz's own kind registry (the authoritative list of what exists today) | `crates/buzz-core/src/kind.rs` |
| A worked example of a Buzz custom-NIP kind proposal | `docs/nips/NIP-AM.md` (any file under `docs/nips/` is a peer example) |
| This repository's own instruction for adding a kind | `AGENTS.md` (repo root), "Event kinds" and "Channel scoping" sections |

If this file and any of those disagree, **they win** — this one has drifted and
should be fixed.

## Purpose

An event-kind node exists to answer, for a reader who needs to produce or consume
events of one specific Nostr kind, four questions in one place: *what number is
this, what specification governs it, what wire shape must an event of this kind
have, and who is allowed to write or read one?* It is reference-oriented in Diátaxis
terms — it is a technical description of a piece of machinery, meant to be looked
up while implementing or reviewing code that touches the kind — but it is narrower
than a generic reference document, because its subject is fixed to exactly one
`kind` integer and everything that number implies under NIP-01.

**The failure this template exists to prevent.** Left unscoped, an event-kind
document drifts in one of two directions: it restates the referenced NIP's general
text without ever pinning down what *this repository's* implementation actually
does with the kind (which tags it enforces at ingest, which access-control set it
belongs to, whether `kind.rs`'s classification agrees with the NIP's stated range)
— or it describes the *feature* built on top of the kind (a UI flow, a CLI
subcommand, an API route) rather than the kind's own wire contract, which is a
different form with a different job (issue #1342's territory — see *Boundary*
below). The sections below exist to keep both drifts out: every required section
below is checkable against a specific source in this repository, not against
general Nostr knowledge.

## The industry model this adapts

**NIP-01, the base event envelope** (`nostr-protocol/nips`, `01.md`). This is the
primary source for what `kind` *means at all*: "Kinds specify how clients should
interpret the meaning of each event and the other fields of each event." NIP-01
also defines the four numeric categories every kind falls into — regular,
replaceable, ephemeral, addressable — purely by the value of the integer, and
defines a tag as an array whose "first element ... is referred to as the tag name
or key and the second as the tag value," with any elements after the second
carrying no fixed meaning. Every event-kind node inherits this vocabulary directly;
this template does not restate NIP-01's full text, it requires each instance to
state where *its* kind lands against it.

**NIP-29, group/channel and moderation-kind conventions** (`nostr-protocol/nips`,
`29.md`). This is the source for the `h`-tag convention this repository's own
`AGENTS.md` cites as the basis for Buzz's channel scoping ("Channels use `h` tags
(NIP-29 group tag), not `e` tags"), and it is also a worked precedent for exactly
the shape this template asks an instance to describe: NIP-29 documents each
moderation action as *its own kind number* with *its own required tag shape*
(`put-user`, kind 9000, requires a `p` tag shaped `["p", "<pubkey-hex>",
"<optional-roles>"]`) rather than one generic kind carrying an action field in
`content`. Buzz's own moderation kinds (`KIND_NIP29_PUT_USER` through
`KIND_NIP29_LEAVE_REQUEST` in `kind.rs`) follow that same one-kind-per-action shape
directly.

**This repository's own kind registry, `crates/buzz-core/src/kind.rs`.** This is
not an external standard, but it is this corpus's most directly relevant industry
model, because it is the actual, currently-enforced documentation contract for a
Buzz kind: a `u32` constant with a doc comment naming the referenced NIP (or "Buzz
custom"), its delivery classification when not obvious from range alone, its tag
shape and cardinality, and — for a meaningful fraction of kinds — its access-control
model, cross-checked by `const _: () = assert!(...)` compile-time checks and a
`no_duplicate_kind_values` test. This template's *Required sections* below is this
convention made explicit and portable to prose, not an independent invention.

**Buzz's own custom-NIP proposal documents, `docs/nips/NIP-*.md`.** For a kind with
no governing community NIP, this repository already has a worked precedent for how
to fully specify one: `docs/nips/NIP-AM.md` (kind 44200) is structured as a title
and stability badge line, Motivation, Definitions, an Event section stating the
exact tag shape and cardinality with a JSON example, an Encryption section, and a
Decrypted Payload section giving the plaintext's exact field shape with
REQUIRED/optional markers. A corpus event-kind node is not a replacement for a
`docs/nips/NIP-*.md` file when Buzz is *proposing* a new protocol-level kind — that
document is the specification. The corpus node's job, for such a kind, is the
reference lookup that points at the spec and adds the corpus's own evidence
ledger and relationships; for a kind that already has an external NIP, the corpus
node *is* the reference lookup, because no second internal spec document exists.

## Required sections

An event-kind node MUST contain the following. ("MUST" here is this template's own
requirement for the shape of an instance node, not a restatement of any MUST/SHOULD
normative-policy framework — this document is a template, not a standard, per the
*Scope and authority* note above.)

1. **Title and kind identity.** The kind's name, its integer number, and its exact
   constant name in `crates/buzz-core/src/kind.rs` (e.g. `KIND_AGENT_TURN_METRIC =
   44200`). If the kind is proposed but not yet implemented, say so explicitly and
   name the constant it will need — do not let a reader assume every documented
   kind already ships.

2. **Referenced NIP.** Name the exact specification the kind conforms to: a
   numbered NIP in `nostr-protocol/nips` (pin the citation to a commit SHA, per
   `AGENTS.md`'s pinning rule), or one of Buzz's own `docs/nips/NIP-XX.md`
   proposals for a kind with no existing community NIP. State which, and link the
   exact source. A kind that does not map cleanly onto any NIP is a signal that the
   custom-NIP document needs writing first — this section is not the place to
   improvise a specification.

3. **Kind range and delivery classification.** State which of NIP-01's four
   categories the kind's number falls in — regular, replaceable, ephemeral, or
   addressable/parameterized-replaceable — and cross-check it against `kind.rs`'s
   own `is_replaceable` / `is_parameterized_replaceable` / `is_ephemeral` helpers
   (or their absence, for a plain regular kind). A mismatch between the number's
   raw NIP-01 range and what `kind.rs` asserts about it is a real bug in one of the
   two, and an author who skips this cross-check cannot catch it.

4. **Tag shape.** Every tag the event MUST or MAY carry, in order, stating
   cardinality explicitly ("exactly one," "zero or more"): any channel/group
   scoping tag (`h`, per NIP-29, when the kind is channel-scoped), any addressing
   tag (`d`, when the kind is parameterized-replaceable), and any reference tags
   (`p`, `e`, `a`) the kind's semantics depend on. `kind.rs`'s own doc comments do
   this for most of the newer, Buzz-specific custom kinds (e.g.
   `KIND_AGENT_TURN_METRIC`'s comment: "Tags: exactly one `p` (owner pubkey) and
   one `agent` (agent pubkey == event pubkey); no `h` tag") — a tag-shape section
   that is vaguer than the source it summarizes has failed at its one job.

5. **Content field semantics.** State whether `content` is plaintext, empty, a
   stringified JSON object (give its exact field shape), or ciphertext (NIP-44 or
   otherwise) — and if encrypted, which keys derive the conversation key and what
   the decrypted payload's exact shape is, with required/optional fields marked.
   `docs/nips/NIP-AM.md`'s "Decrypted Payload" section is the worked example this
   requirement is drawn from directly.

6. **Access control and storage model (required whenever it is not the
   uncontroversial default).** State whether the kind is stored at all (ephemeral
   kinds are not), who may read a stored event of this kind (world-readable,
   author-only, `p`-gated, `shared`-tag-gated), and whether it is client-authored,
   relay-authored, or both. Buzz encodes most of this as membership in a named set
   in `kind.rs` (`AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`, `SHARED_GATED_KINDS`,
   `RESULT_GATED_KINDS`) rather than in the referenced NIP's own text — for a
   Buzz-specific kind, this section is usually restating that membership (or its
   deliberate absence, as `kind.rs` itself does for `KIND_TEAM`) with the reason,
   not inventing a new access model.

7. **Worked example.** One complete example event as JSON (signature redacted or
   clearly marked illustrative — e.g. `"sig": "..."`), exercising every tag and
   every content-field case named in sections 4–5. A tag-shape section without a
   worked example leaves a reader unable to tell whether the prose was actually
   checked against something that would parse.

8. **Versioning and supersession (optional; required if applicable).** If the kind
   replaces an earlier, retired kind number, name the old number and state why it
   changed. `kind.rs`'s own comments record this history inline as a matter of
   course (e.g. "V1 used kind:10001 (replaceable range — wrong), then 40001") —
   an event-kind node inherits that discipline rather than starting a document
   with no memory of what came before.

9. **Relationships to other kinds and nodes (optional).** Prefer a typed
   `relationships` entry over prose whenever the target is a corpus node:
   `depends-on` when the kind is only meaningful alongside another kind (e.g. a
   moderation-resolve kind pointing at the report kind it resolves), `references`
   for a related-but-independent kind, and — per `relationships.schema.json`'s own
   description of the type — `implements` targeting `corpus-template-event-kind`
   itself, marking the node as a realized instance of this template rather than an
   independent restatement of its requirements.

## Evidence expectations

**Sections 1–5 are where FACT is directly reachable, almost without exception.**
The kind number, its NIP, its range classification, its tag shape and its content
shape are all things `kind.rs` and/or the referenced NIP state in writing. Do not
describe a kind's wire shape from memory or from having seen it used in a log —
open `kind.rs` and, where the kind proposes new protocol behaviour, the relevant
`docs/nips/NIP-*.md` file, and cite them directly.

**Section 6 (access control) is the one most often reasoned about rather than
read.** If the kind's membership in `AUTHOR_ONLY_KINDS` / `P_GATED_KINDS` /
`SHARED_GATED_KINDS` is stated explicitly in `kind.rs` (as a doc comment or as
literal set membership), that is FACT. If an author is inferring that a kind
*should* be gated a certain way because of what it contains, rather than reading
that the code already gates it that way, that is INFERENCE with `confidence` set
honestly — conflating the two is exactly the "reasoning versus deciding" failure
`standards/confidence.md` names, and it matters more here than in most node types,
because an access-control claim that is wrong is a security-relevant
misdocumentation, not merely a stale fact.

**Section 8 (versioning) is frequently TEAM_KNOWLEDGE or INFERENCE.** *Why* a kind
was renumbered is sometimes stated in a code comment (FACT, cite it directly, as
several of `kind.rs`'s own comments already do) and sometimes known only from a PR
discussion or an issue with no corroborating comment in code (TEAM_KNOWLEDGE, with
`provided_by` naming the source) — do not promote the second case into a FACT
merely because the renumbering itself is a fact.

## Boundary against interface (#1342)

**The line this node draws, from the event-kind side.** An event-kind node owns
the kind as a *protocol and registry citizen*: its number, its entry (or proposed
entry) in `kind.rs`, the NIP it conforms to, and the wire shape — tags and content
— that makes an event of that kind well-formed and correctly gated, independent of
any particular caller. An "interface" node (#1342, filed and open, authored by a
sibling agent in this same batch — its own template text did not exist to read
while this node was written) most plausibly owns a *consumer-facing operation
surface* built using one or more event kinds: a `buzz-cli` subcommand's contract,
a `buzz-sdk` typed event-builder function, or a narrow HTTP route — describing how
a caller invokes the operation, not re-deriving the kind's own wire shape from
scratch.

**The tell.** "What tags and content make an event of kind N well-formed, and who
may read one" belongs here. "How do I call the thing that produces or consumes an
event of kind N" belongs to an interface node, which should reach this node with a
`depends-on` relationship rather than restating sections 3–6 above in its own
words.

**This is a real, unresolved overlap risk, not a settled boundary.** Both this
node and #1342 exist as templates being authored in parallel by different agents
in the same batch, and an "interface describing an event kind's wire contract"
is exactly the case the batch dispatch brief flagged as plausibly belonging to
either. This node states its own position; it does not and cannot bind #1342's
author to the same line, since that document did not exist to check against. If
#1342 lands drawing the boundary differently, that conflict needs reconciling
before both templates are treated as settled — this is named explicitly in this
node's PR body under Escalations, not resolved unilaterally here.

## Scope and omissions

**This document covers** the purpose of an event-kind node, the sections it must
contain, what evidence each section needs, and the industry model it adapts. It
does not itself document any real Buzz event kind.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The interface document form and its required sections | #1342 |
| The procedure/how-to document form and its required sections | #1345 |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Evidence classification mechanics beyond what this template's own sections need | `launchpad/docs/corpus/AGENTS.md`, `standards/confidence.md` |
| Whether every Buzz-proposed kind is required to have a `docs/nips/NIP-XX.md` file before it may get a corpus event-kind node, versus the corpus node alone being sufficient | Not yet filed as its own issue at the recorded revision |
| Whether a diagram-authoring convention (e.g. a fixed Mermaid style for a worked-example sequence diagram) should be standardized corpus-wide | Not yet filed as its own issue at the recorded revision |

**No `relationships` in this node's own front matter.** Checked before deciding
that rather than assuming it: at the recorded revision, `origin/launchpad`'s
`launchpad/docs/corpus` tree carries exactly four validated content nodes
(`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references`), and none has Nostr event kinds, NIP-01,
NIP-29, or corpus templates as its subject. An edge to any of them would be a
citation duplicate of what this node's evidence ledger already cites directly, not
a substantive typed relationship. The likeliest future edge is a `references` (or
mutual `depends-on`) relationship to the interface template (#1342) once both
merge and their boundary is actually reconciled — which does not exist yet on
`origin/launchpad`.

**Expected but not verified when this node was written:**

- **No real event-kind instance has been authored from this template yet.**
  Whether the section list above actually produces a legible document for a real
  Buzz kind, rather than merely sounding complete in the abstract, is untested —
  the first real instance is where that gets found out.
- **The `implements`-targeting-this-template guidance in required section 9 is
  untested against a real reviewer's expectations.** No prior corpus-template
  node in this batch or the two before it was checked for whether it actually
  received an `implements` edge from any instance, because no instance of any
  template exists yet.
- **Whether every Buzz-proposed kind is expected to get a `docs/nips/NIP-XX.md`
  file, versus that being optional for kinds with no protocol-level ambition
  beyond this repository, was not settled by reading any decision record** — it is
  named above as a gap rather than answered by inference from the 16 `.md` files
  currently under `docs/nips/` (verified by `ls docs/nips/*.md | wc -l` at the
  recorded revision).
- **This node's own boundary against #1342 was not checked against #1342's actual
  text**, because that text did not exist on `origin/launchpad` or in any open PR
  at the time of authoring — see *Boundary against interface* above.
