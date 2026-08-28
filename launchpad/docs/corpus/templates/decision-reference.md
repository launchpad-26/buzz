---
id: corpus-template-decision-reference
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
  - statement: "node.schema.json requires id, type, status, origin, audiences and evidence, additionally permits relationships, and rejects any field beyond those seven; its type enum is a closed list of thirteen corpus-surface values that contains no \"template\" or \"policy\" value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every existing corpus meta-document that is not itself an agent-facing procedure declares type: governance -- launchpad/docs/corpus/README.md, launchpad/docs/corpus/standards/confidence.md and launchpad/docs/corpus/standards/decision-references.md all do -- while launchpad/docs/corpus/AGENTS.md declares type: agent because it is also resolved as this subtree's own governing AGENTS.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "relationships.schema.json defines five relationship types; references means \"source cites target as supporting context; no ownership or currency dependency implied\" and carries an authored inverse (referenced-by), while depends-on means the source's own claims require the target to stay true or current."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "corpus-standard-decision-references governs how any corpus node cites an accepted decision as evidence for a claim -- which claims a decision may support, how to cite one, and what a superseded or conflicting decision requires -- and does not itself define the structure of a corpus node whose entire subject is one decision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "An accepted decision under launchpad/decisions/ carries front matter (status, date, issue, decided_in, supersedes) that does not satisfy node.schema.json's six required fields (id, type, status, origin, audiences, evidence) -- it has no id, type, origin or evidence at all, and its status values (e.g. Accepted) are not members of node.schema.json's closed status enum -- so a decision record is not itself a loadable corpus node and cannot be the target of a relationships edge; giving a specific decision a place in the corpus's own relationship graph requires a separate, hand-authored corpus node about that decision."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
      - "launchpad/decisions/README.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.85
  - statement: "MADR 4.0.0, released 2024-09-17 and titled \"Markdown Architectural Decision Records,\" structures adr-template.md as: Context and Problem Statement, Decision Drivers (optional), Considered Options, Decision Outcome, Consequences (optional), Confirmation (optional), Pros and Cons of the Options (optional), and More Information (optional), preceded by optional YAML front matter (status, date, decision-makers, consulted, informed)."
    entry_class: FACT
    evidence:
      - "https://github.com/adr/madr/blob/2475fe1973f66a12aaf58a91d8fa7b42c0f5ea3d/template/adr-template.md"
      - "https://github.com/adr/madr/blob/2475fe1973f66a12aaf58a91d8fa7b42c0f5ea3d/README.md"
  - statement: "Michael Nygard's original 2011-11-15 ADR post defines five sections: Title, Context, Decision, Status, and Consequences."
    entry_class: FACT
    evidence:
      - "https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions"
  - statement: "An unmerged research note recommends MADR 4.0.0 as the maintained, versioned ADR template to adapt in this repository, keeping Nygard's original five sections as historical context rather than as the template to copy."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note, branch docs/research-project-doc-templates)"
  - statement: "Issue #605's real acceptance criterion for a template node is that it states its purpose, required sections, evidence expectations and the industry model or standard it adapts; issue #1335's own Definition of Done additionally lists four MUST/SHOULD/enforcement/exception bullets copied verbatim from issue #1310 (the decision-references standard), which describe a normative policy node rather than a template."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria; launchpad-26/buzz#1335 and #1310 definitions of done"
  - statement: "Issues #1341 (\"define the implementation reference corpus template\") and #1346 (\"define the reference corpus template\") are sibling #605 child tasks establishing \"reference\" as a corpus document genre, of which this node's decision-reference is one subject-specific instance."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1341 and #1346 issue objectives"
relationships:
  - type: references
    target: corpus-standard-decision-references
---

# Template: decision-reference

How to author a corpus node whose entire subject is **one accepted decision** — giving
that decision a place in the corpus's own relationship graph, distinct from citing a
decision as supporting evidence inside some other node.

## Purpose

An accepted decision in this repository is recorded once, under `launchpad/decisions/`,
per `launchpad/decisions/README.md`. That record's front matter (`status`, `date`,
`issue`, `decided_in`, `supersedes`) does not satisfy `node.schema.json`'s required
fields, so the decision record itself is never a loadable corpus node and can never be
the `target` of a `relationships` edge (see the ledger's `INFERENCE` entry above). A
**decision-reference** node is the bridge: a hand-authored corpus node, built from this
template, that gives one specific decision a stable corpus `id` other nodes can point
`depends-on`, `implements` or `references` edges at.

This is a different job from `corpus-standard-decision-references` (#1310), which
governs how *any* corpus node cites a decision as one evidence entry among others. This
template governs a node whose *only* subject is the decision — every section below
exists to summarize and index that one decision for corpus consumers, not to make an
unrelated claim that happens to lean on it. The `references` relationship declared
above points there for exactly that reason: an author following this template still
needs that standard's MUST list (cite the Decision section, check `status`, no line
position, handle supersession) once they start writing evidence entries about what the
decision says. `references` rather than `depends-on` because this template's own
structure does not stop being correct if that standard's citation rules change —
only the advice inside it would need re-reading.

## Note on DoD

Issue #1335's Definition of Done carries four bullets — "states scope and
authority/source of the policy," "separates MUST from SHOULD," "defines
enforcement/checks and exception/escalation," "links decisions instead of duplicating
them" — copied verbatim from issue #1310's normative-standard checklist. A template is
not a MUST/SHOULD policy document, so this node has no MUST/SHOULD section and no
enforcement/escalation process of its own. The criterion this node is actually built
against is PRD #605's own acceptance criterion: *"Every template states its purpose,
required sections, evidence expectations and the industry model/standard it adapts."*
Every other DoD item generic to any corpus node — schema-valid front matter, one
independently maintainable idea, traceable claims, links instead of duplication,
checked-against-provenance, clean validator run — is honored as written.

## The industry model this adapts

**MADR 4.0.0** (`adr/madr`, released 2024-09-17) is the maintained, versioned, dated
successor to Michael Nygard's original 2011 five-section format (Title, Context,
Decision, Status, Consequences — kept here as historical context, not as the template
to copy). MADR is a Tier-1 "versioned spec" per the research note cited above: pinnable,
dated, and still actively released, unlike an unversioned canonical template. Its
template file, verified against the pinned commit above rather than taken on the
research note's word, is:

```markdown
---
status: "{proposed | rejected | accepted | deprecated | … | superseded by ADR-0123}"
date: {YYYY-MM-DD when the decision was last updated}
decision-makers: {list everyone involved in the decision}
consulted: {list everyone whose opinions are sought}
informed: {list everyone who is kept up-to-date on progress}
---

# {short title, representative of solved problem and found solution}

## Context and Problem Statement
## Decision Drivers          <!-- optional -->
## Considered Options
## Decision Outcome
### Consequences             <!-- optional -->
### Confirmation             <!-- optional -->
## Pros and Cons of the Options   <!-- optional -->
## More Information          <!-- optional -->
```

The **Confirmation** section is the one MADR section worth calling out specifically:
"describe how the implementation/compliance of the ADR can/will be confirmed." Most
hand-rolled ADR formats omit it, and it is the section that keeps a decision-reference
node from being an unenforced opinion — see *Evidence expectations* below.

## Required sections

A decision-reference instance's front matter is a corpus node's own front matter (this
schema, not MADR's) — do not paste MADR's YAML block into a corpus node's front matter.
MADR's structure maps into the node's **Markdown body** instead:

| MADR section | Required? | In a decision-reference instance |
|---|---|---|
| Title | Required | The node's `# H1`, naming the decision and the ADR it indexes. |
| Context and Problem Statement | Required | Why the question existed. May restate the ADR's own Context, attributed. |
| Decision Drivers | SHOULD | Forces that shaped the decision, if they clarify the Decision Outcome below. |
| Considered Options | SHOULD | Alternatives, when omitting them would make the Decision Outcome look unmotivated. |
| Decision Outcome | Required | What was decided, in this repository's own words. This is the node's central claim — see *Evidence expectations*. |
| Consequences | SHOULD | What follows, good and bad, per the ADR's own Consequences section. |
| Confirmation | Required | How compliance with the decision can be, or is, checked — a fitness function, a test, a lint rule, a review step. If the ADR has none, say so; do not invent one. |
| Pros and Cons of the Options | MAY | Include only if the ADR's own record carries this level of detail and it adds value beyond Decision Drivers. |
| More Information | MAY | Links to related corpus nodes, superseding decisions, or follow-up issues. |
| Scope and omissions | Required | Corpus convention (see `launchpad/docs/corpus/AGENTS.md`), not a MADR section: what this node does not cover, and what was expected but not verified when it was written. |

## Evidence expectations

Every substantive claim about what the decision says is an **intent claim** under
`ADR-0029` and `corpus-standard-decision-references`, so:

- The **Decision Outcome** section's evidence entries **must** cite the accepted
  decision's own **Decision** section (MUST 1 and MUST 5 of `corpus-standard-decision-
  references`) — never the issue that argued it, and never a MADR-shaped paraphrase with
  no citation at all.
- Before writing those entries, open the decision record and confirm its front-matter
  `status` is accepted (MUST 4). A proposed or superseded record cannot back an intent
  claim about what is authorized *today* — the one standing exception is a claim that is
  explicitly *about* that record's own pending or superseded state.
- **Confirmation**'s claims are usually **behaviour** claims ("a lint rule enforces this,"
  "CI checks this on every PR") and so **must not** rest on the decision record alone
  (MUST 2 of `corpus-standard-decision-references`) — cite the executable check itself
  (the script, the workflow, the test). A Confirmation section with no fitness function
  yet is legitimate; say so as a gap in *Scope and omissions* rather than fabricating
  executable evidence to fill the section.
- Context, Decision Drivers and Consequences may draw on the record's other sections, or
  on the issue where the decision was argued, but such claims must be worded as
  rationale or context claims, not authorization claims (MUST 5's "every other section is
  a legitimate source for a claim about something *other than* authorization").
- If the cited decision is later superseded, follow `corpus-standard-decision-
  references`'s three-way rule (move the citation, update the claim, or keep the
  citation and say why it is still the right source for an explicitly historical claim)
  rather than leaving a quietly-stale Decision Outcome in place.
- Classify honestly: `FACT` for what the record's Decision section says, `INFERENCE` for
  reasoning about what it implies (with `confidence`), `TEAM_KNOWLEDGE` for anything an
  issue or a person told the corpus that the record itself does not state.

## Relationships

A decision-reference node's own `relationships` are about the decision's place among
*other decisions and their consequences*, not about citation mechanics:

- `supersedes` — if this decision-reference node's decision replaces an earlier one that
  also has a decision-reference node, per the target's own `supersedes`/`superseded-by`
  directionality.
- `depends-on` — if this node's own claims stop holding when another node's claims stop
  holding (for example, a decision whose rationale rests on a still-open architectural
  claim documented elsewhere).
- Other corpus nodes that carry out the decision (a standard, an implementation node)
  are expected to declare `implements` **targeting this node's id** — `relationships.
  schema.json` names exactly this shape ("a template instance of a standard") as the
  paradigm case for that type's directionality; a decision-reference node does not
  declare that edge itself, since `implements`'s inverse (`implemented-by`) is generated,
  not authored.
- Do not declare `references` back to every node that cites this decision as evidence —
  that citation already lives in the citing node's own `evidence` ledger per
  `corpus-standard-decision-references`, and duplicating it as a relationship edge is the
  kind of second copy that drifts silently.

## Scope and omissions

**This node covers** the purpose, required sections, evidence expectations and industry
model for a corpus node whose subject is one accepted decision, and the boundary between
that and citing a decision as evidence inside some other node.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How any corpus node cites a decision as one evidence entry among others | `corpus-standard-decision-references` (#1310) |
| The decision-record lifecycle itself — numbering, supersession, front matter | `launchpad/decisions/README.md` |
| The general "reference" document genre this node's subject-specific instance belongs to | #1346 ("define the reference corpus template") |
| Whether a decision-reference node is required for every accepted ADR, or only ones another corpus node needs to point at | Not settled anywhere found; treated here as "create one when a relationship target is needed," not as a blanket requirement |

**Expected but not verified when this node was written**, per the rule in *Creating a
node* step 3 of `launchpad/docs/corpus/AGENTS.md`:

- **No decision-reference instance exists yet.** This template is unexercised — the
  Required Sections table and the Evidence Expectations section are built from MADR
  4.0.0, `ADR-0029` and `corpus-standard-decision-references`'s own MUST list, not from a
  worked example. The first real instance will test whether the mapping actually holds.
- **Whether every accepted ADR needs a decision-reference node was not settled.** No
  corpus document found says so either way; this node's own row above states that as an
  open gap rather than asserting an answer.
- **A discrepancy against the research note was found and flagged here, not silently
  corrected in it.** `launchpad-26/buzz#1466`'s note names MADR as "Markdown Any
  Decision Records"; the pinned MADR 4.0.0 README itself states "Markdown Architectural
  Decision Records." Both readings were opened directly for this node — the mismatch is
  most likely the note quoting an earlier MADR version's expansion of the acronym rather
  than an error, but that is this node's own guess, not something either source states.
  This node cites the verified 4.0.0 name and reports the mismatch rather than silently
  picking one or correcting the note.
