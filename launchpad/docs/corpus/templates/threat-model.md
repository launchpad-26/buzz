---
id: corpus-template-threat-model
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
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template or policy."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's existing meta-documents, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance, so governance is the precedent for a corpus node that documents the corpus's own authoring rules rather than a piece of architecture/capability/etc. content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states depends-on's directionality as 'source requires target to be true/current for source's own claims to hold'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four documents threat modeling or general security subject matter."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The unmerged research note at launchpad/Research/project-documentation-templates.md (branch docs/research-project-doc-templates, PR #1466) has no section on threat modeling, STRIDE, or any security methodology anywhere in its body; its only three mentions of the word 'security' are an optional README banner/section name, one quoted sentence about a bug bounty program, and a reference to a SECURITY.md file's existence, none of which discuss a threat-modeling process."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='(?i)security|threat|stride', scope='launchpad/Research/project-documentation-templates.md', ref='b0553469d9dff25eb3636ce1d0400e60dca1b559') -> 3 matches (lines 87, 98, 195), none discussing threat-modeling methodology"
  - statement: "Microsoft's Threat Modeling Tool documentation defines STRIDE as six threat categories, each with a one-paragraph description: Spoofing ('illegally accessing and then using another user's authentication information'), Tampering ('the malicious modification of data'), Repudiation ('associated with users who deny performing an action without other parties having any way to prove otherwise'), Information Disclosure ('the exposure of information to individuals who are not supposed to have access to it'), Denial of Service ('deny service to valid users'), and Elevation of Privilege ('an unprivileged user gains privileged access and thereby has sufficient access to compromise or destroy the entire system')."
    entry_class: FACT
    evidence:
      - "https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats, ms.date 2017-08-17, updated_at 2026-03-04"
  - statement: "Microsoft's own SDL threat-modeling overview page describes threat modeling as 'an engineering technique you can use to help you identify threats, attacks, vulnerabilities, and countermeasures that could affect your application,' and names five steps: defining security requirements, creating an application diagram, identifying threats, mitigating threats, and validating that threats have been mitigated."
    entry_class: FACT
    evidence:
      - "https://www.microsoft.com/en-us/securityengineering/sdl/threatmodeling"
  - statement: "Microsoft's Threat Modeling Tool getting-started guide models a system as a Data Flow Diagram (DFD) -- a square for an external entity, a circle for a process, parallel lines for a data store -- shows trust boundaries as red dotted lines marking 'where different entities are in control,' summarizes its own process as 'creating a diagram, identifying threats, mitigating them and validating each mitigation,' and defines four threat status values: Not Started (the default), Needs Investigation, Mitigated, and Not Applicable."
    entry_class: FACT
    evidence:
      - "https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started, ms.date 2017-08-17, updated_at 2025-12-10"
  - statement: "OWASP's Threat Modeling Cheat Sheet defines threat modeling as 'a structured, repeatable process used to gain actionable insights into the security characteristics of a particular system,' and structures the activity into four phases -- System Modeling, Threat Identification, Response and Mitigations, and Review and Validation -- stating that 'according to the Threat Modeling Manifesto, the threat modeling process should answer' four questions: 'What are we working on?', 'What can go wrong?', 'What are we going to do about it?', and 'Did we do a good enough job?', one question per phase."
    entry_class: FACT
    evidence:
      - "https://github.com/OWASP/CheatSheetSeries/blob/ad32f17e5d68701bc4c73505b90739bf66bd775b/cheatsheets/Threat_Modeling_Cheat_Sheet.md"
  - statement: "The same OWASP cheat sheet states that 'data flow diagrams (DFDs) are arguably the most common approach' to system modeling because they 'allow one to visually model a system and its interactions with data and other entities,' that a good system model gives 'a clear view of trust boundaries, data flows, data stores, processes, and the external entities which may interact with the system,' and describes STRIDE as 'a mature and popular threat modeling technique and mnemonic originally developed by Microsoft employees' that 'groups threats into one of six general prompts.'"
    entry_class: FACT
    evidence:
      - "https://github.com/OWASP/CheatSheetSeries/blob/ad32f17e5d68701bc4c73505b90739bf66bd775b/cheatsheets/Threat_Modeling_Cheat_Sheet.md"
  - statement: "The Threat Modeling Manifesto (threatmodelingmanifesto.org, licensed CC BY 4.0) states the same four questions as its process definition, was authored by a named group of fifteen security professionals including Adam Shostack, and states as its second principle that 'threat modeling must align with an organization's development practices and follow design changes in iterations that are each scoped to manageable portions of the system.'"
    entry_class: FACT
    evidence:
      - "https://www.threatmodelingmanifesto.org/"
  - statement: "NIST Special Publication 800-154, 'Guide to Data-Centric System Threat Modeling,' has remained an Initial Public Draft since it was first published on 2016-03-14, and a planning note on its own publication page dated 2025-01-23 states NIST 'plans to finalize this publication' -- meaning it had still not been finalized as of that date, nearly nine years after its initial draft -- so it is not cited here as an adopted standard the way STRIDE and the OWASP cheat sheet are."
    entry_class: FACT
    evidence:
      - "https://csrc.nist.gov/publications/detail/sp/800-154/draft"
  - statement: "Mermaid's own current syntax-reference page lists its supported diagram types (flowchart, sequence, class, state, entity relationship, C4, and others) and none of them is named Data Flow Diagram or DFD; a mermaid-js/mermaid community issue titled 'Data Flow Diagram (a la STRIDE Threat Model)' explicitly requested one, stating 'Data Flow Diagrams are common in software Threat Modelling, especially the STRIDE threat model methodology,' and is closed (linked to pull request #2389) -- regardless of that PR's contents, Mermaid's current official diagram-type list carries no entry named Data Flow Diagram or DFD as of this writing."
    entry_class: FACT
    evidence:
      - "https://mermaid.js.org/intro/syntax-reference.html"
      - "https://github.com/mermaid-js/mermaid/issues/1893"
  - statement: "At the recorded revision, exactly one Markdown file in this repository (launchpad/Research/hardening-linux-servers.md, a research note) uses a fenced mermaid code block, so Mermaid is this template's own recommendation rather than an established repository-wide convention it is merely following."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='```mermaid', scope='**/*.md') -> 1 match: launchpad/Research/hardening-linux-servers.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "GitHub's own documentation states that 'diagram rendering is available in GitHub Issues, GitHub Discussions, pull requests, wikis, and Markdown files' for a fenced Mermaid code block."
    entry_class: FACT
    evidence:
      - "https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams"
  - statement: "Because no single primary source reviewed here supplies a ready-to-fill document template for a threat model the way, for example, the Good Docs Project supplies fillable Concept and Reference templates, this template's required-sections structure is synthesized from three converging primary sources -- Microsoft's DFD/trust-boundary/STRIDE/status-value vocabulary, OWASP's four-phase process, and the Threat Modeling Manifesto's four questions -- rather than adapted from one canonical template document."
    entry_class: INFERENCE
    evidence:
      - "https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started"
      - "https://github.com/OWASP/CheatSheetSeries/blob/ad32f17e5d68701bc4c73505b90739bf66bd775b/cheatsheets/Threat_Modeling_Cheat_Sheet.md"
      - "https://www.threatmodelingmanifesto.org/"
    confidence: 0.75
  - statement: "depends-on is the relationship type a threat-model instance node should declare toward the architecture-container or architecture-component node it threat-models, because relationships.schema.json defines depends-on's directionality as 'source requires target to be true/current for source's own claims to hold,' and a threat model's claims about trust boundaries and attack surface stop holding the moment the modeled design changes."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
    confidence: 0.65
  - statement: "architecture is the closer fit of node.schema.json's two plausible type-enum candidates for a threat-model instance node's own front-matter type, because a threat-model node documents the same system an architecture node describes, just from an adversarial angle -- the same reasoning this node's depends-on relationship guidance above rests on -- and no enum value is dedicated to threat modeling or security analysis specifically; verification is a documented override an author may choose instead, but is not equally weighted, since nothing in the enum's own names or in the sources reviewed for this template ties threat modeling to verification more closely than to architecture."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.65
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts,' and this is the acceptance bar this node is built against rather than the MUST/SHOULD/enforcement/escalation checklist that issue #1351's own Definition of Done carries, which the batch dispatch brief for tasks #1307-#1351 identified as boilerplate copied from the standards-track issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent Feature acceptance criteria) and the #1307-#1351 batch dispatch brief for tasks #1331/#1336/#1340/#1346/#1351"
  - statement: "Issue #1180 ('task: document layers/security/threat-model.md', open, parent Feature #607 'identity tenancy authentication authorization and security corpus exists') is a concrete, already-filed future consumer of this exact template, targeting launchpad/docs/corpus/layers/security/threat-model.md as a threat-model instance node distinct from this template node's own path; and #607's own acceptance criteria state that 'every node passes corpus schema/graph/provenance validation and uses the assigned template.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1180 and launchpad-26/buzz#607 (read directly via gh issue view; per AGENTS.md an issue has no openable file and no way to pin one, so it is cited as TEAM_KNOWLEDGE rather than FACT regardless of having been opened and read)"
---

# Template: threat-model

How to write a corpus node whose subject is a structured, attacker-perspective
analysis of one system, container, or data flow: what the node must contain, what
evidence it needs, and the industry model it adapts. This is a template node, not
a policy node -- it prescribes the shape of a future document rather than a
MUST/SHOULD rule about corpus-wide behavior. See *Note on Definition of Done*
below for why that distinction matters for this specific node.

**This topic has no research-note coverage to build on.** Unlike this batch's four
sibling templates, Serina's research note
(`launchpad/Research/project-documentation-templates.md`, unmerged PR #1466) has no
section on threat modeling, STRIDE, or security methodology at all -- verified
directly against the branch tip, not assumed. Every industry-model claim below
comes from a primary source fetched and read for this node specifically.

## Scope and authority

**This node covers** what a corpus node documents when its subject is a
"threat-model" -- an attacker-perspective analysis of one system, container, or
data flow: the required sections such a node's body must carry, the evidence
expectations for the claims it makes, and the industry model it adapts.

**It does not cover** the front-matter contract itself (`node.schema.json` governs
that, unconditionally, for every node type), how to create/update/retire a node
procedurally (`AGENTS.md` governs that), or the architecture templates that
describe a system's design rather than its attack surface (`architecture-context`,
`architecture-container`, `architecture-component` -- separate tasks, separate
templates). See *Boundary: what this template is not* for the full line, drawn
against several kinds of document this one is easy to mistake it for.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `validate.py` runs that schema, and CI
runs `validate.py` on every corpus change. What this node adds is the half no
schema can hold -- which sections a threat-model node needs, what evidence backs a
threat or mitigation claim, and which industry model grounds the whole shape. That
half is enforced by review, the same way the existing corpus standards describe
their own review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| The industry model this template adapts | *Industry model* below, and the primary sources it cites |

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Industry model this template adapts

**STRIDE** (Microsoft, current form documented at
`learn.microsoft.com/.../threat-modeling-tool-threats`) -- a mnemonic that groups
threats into six categories: **S**poofing (illegally using another user's
authentication information), **T**ampering (malicious modification of data),
**R**epudiation (a user denies performing an action with no way to prove
otherwise), **I**nformation Disclosure (exposing information to those not
entitled to it), **D**enial of Service (denying service to valid users), and
**E**levation of Privilege (an unprivileged user gains privileged access).
Microsoft's own SDL overview names five process steps built around this
categorization: define security requirements, create an application diagram,
identify threats, mitigate threats, validate that threats have been mitigated.
The companion getting-started guide models the system as a **Data Flow Diagram**
(DFD) -- external entities, processes, data stores, data flows -- with **trust
boundaries** marked explicitly, and tracks each identified threat through one of
four status values: *Not Started*, *Needs Investigation*, *Mitigated*, *Not
Applicable*.

**OWASP's Threat Modeling Cheat Sheet** (OWASP Cheat Sheet Series,
`cheatsheets/Threat_Modeling_Cheat_Sheet.md`) -- defines threat modeling as *"a
structured, repeatable process used to gain actionable insights into the security
characteristics of a particular system"* and structures it into four phases, each
answering one of the **Threat Modeling Manifesto's** four questions: *System
Modeling* ("What are we working on?"), *Threat Identification* ("What can go
wrong?"), *Response and Mitigations* ("What are we going to do about it?"), and
*Review and Validation* ("Did we do a good enough job?"). It names DFDs as *"the
most common approach"* to system modeling and names STRIDE directly as *"a mature
and popular threat modeling technique and mnemonic originally developed by
Microsoft employees."*

**Why both, together.** STRIDE supplies the threat taxonomy; OWASP's four-phase
process (itself an operationalization of the vendor-neutral Threat Modeling
Manifesto) supplies the lifecycle around it -- model the system, apply the
taxonomy, decide what to do, and close the loop by checking the work was good
enough. Neither source stands alone as "the" template: STRIDE is a categorization
scheme with no document structure of its own, and OWASP's cheat sheet describes a
process, not a fill-in-the-blank artifact. This template combines them into one
document shape.

**What this template deliberately does not adapt.** NIST Special Publication
800-154 ("Guide to Data-Centric System Threat Modeling") was checked as a
candidate primary source and rejected: it has remained an *Initial Public Draft*
since 2016-03-14, and NIST's own publication page still carried a note as of
2025-01-23 saying it *plans* to finalize the document -- meaning it was still not
an adopted standard nearly nine years after its first draft. Citing a document
that has never left draft status as "the industry standard" would be the same
kind of overreach this batch's research note flagged for other document types
with no real canonical form. STRIDE and OWASP's cheat sheet, by contrast, are
live, currently-maintained, widely-cited primary sources -- this is the genuine
case where the record is not thin, unlike some of this PRD's other topics.

**One real gap remains, honestly disclosed rather than papered over.** No source
reviewed here -- Microsoft's, OWASP's, or the Manifesto's -- publishes a
ready-to-fill *document* template comparable to the Good Docs Project's Concept or
Reference templates (used by this batch's `#1331`/`#1346` siblings). All three
describe a *process* and a *notation*, not a *document skeleton*. The **Required
sections** below are this node's own synthesis of that process and notation into
a document shape, not a transcription of a template that already existed
somewhere. See the `INFERENCE` entry in this node's evidence ledger for the
explicit confidence rating on that synthesis.

## Boundary: what this template is not

Read this section before drafting. "Security" is a wide word, and several
existing or plausible corpus subjects sound like this one without being it:

- **Not a `SECURITY.md` vulnerability-disclosure policy.** That document tells an
  external reporter how to responsibly disclose a found vulnerability. A
  threat-model node is a design-time, defender-authored analysis of what could go
  wrong before anything is found. They can cite each other -- a disclosed
  vulnerability may reveal a threat this node's model missed -- but one is not a
  substitute for the other.
- **Not a security-control catalog or org-wide security policy.** A node
  enumerating which controls (encryption at rest, MFA, WAF rules) an organization
  requires across all systems is a `governance`-type policy node with its own
  MUST/SHOULD structure -- the shape the stale DoD checklist in this issue
  actually describes. A threat-model node is scoped to *one* system, container, or
  data flow, and its mitigations reference such controls rather than defining
  them.
- **Not a penetration-test or audit report.** Those are retrospective: they
  record what testing found in a system that already exists. A threat-model node
  is prospective and structural: it reasons about a design's trust boundaries and
  data flows, whether or not anyone has yet tried to break it. A pen-test finding
  is legitimate evidence *for* a threat-model claim (see *Evidence expectations*),
  not the node itself.
- **Not an architecture template (`architecture-context`, `-container`,
  `-component`, none in this batch).** Those describe what a system *is* --
  actors, deployable units, internal building blocks -- from a design
  perspective. A threat-model node describes the same kind of system from an
  *adversarial* perspective, and its required Data Flow Diagram deliberately
  reuses the modeled system's boundaries rather than re-deriving them. A
  threat-model node should `depends-on` the architecture node(s) it analyzes
  (see *Relationships*) rather than re-describing their content.

A node built from this template that drifts into any of the four above has picked
the wrong template, not merely written a long document.

## Front-matter type

A node built from this template carries `type: architecture` in its front
matter by default. `node.schema.json`'s thirteen-member enum (see evidence
ledger) has no value dedicated to threat modeling or security analysis, and a
threat-model node documents the same system an architecture node describes,
just from an adversarial angle -- the same reasoning *Relationships* below uses
to require a `depends-on` edge toward that architecture node. `architecture` is
therefore the closer fit of the enum's two plausible candidates; see the
`INFERENCE` entry in this node's evidence ledger for the confidence rating on
that reasoning.

**`verification` is a documented override, not an equally weighted default.**
An author may choose `type: verification` instead when the node's primary
purpose in their corpus is a security-verification activity rather than a
system description, but the choice must be stated and justified explicitly in
the instance node's own body (for example, in its *Scope and omissions*
section) rather than picked silently -- deviating from the default is a
decision worth its own citation, not a coin flip the template leaves open.

## Required sections

A corpus node using this template (its front-matter `type` should be
`architecture` by default, or `verification` as a documented override -- see
*Front-matter type* above) must carry the following in its body, in addition to
whatever schema-required front matter `node.schema.json` demands of every node:

1. **Purpose and scope statement.** One paragraph naming the system, container, or
   data flow being modeled (by its own corpus node id, once the corresponding
   architecture node exists -- see *Relationships*) and what question the
   analysis answers for a reader, per the Manifesto's "What are we working on?"
2. **Notation legend.** A short table mapping every shape/style used in the
   diagram to its DFD meaning (external entity, process, data store, data flow,
   trust boundary) before the diagram itself. Necessary specifically because the
   notation is borrowed, not native: Mermaid has no built-in DFD diagram type (see
   evidence ledger), so this template's diagrams approximate DFD notation with
   flowchart syntax, and a reader cannot be assumed to already know that mapping.
3. **System model (Data Flow Diagram).** A DFD as a fenced ```` ```mermaid ````
   flowchart block, with explicit trust boundaries (a labeled `subgraph`, per
   Microsoft's "red dotted line" convention above, adapted to Mermaid's actual
   shapes since it has none built for this purpose). GitHub renders a fenced
   Mermaid block natively in Markdown files, keeping the diagram inside the same
   reviewable pull-request diff ADR-0028 chose Markdown to preserve. This is this
   template's own recommendation, not an established repository convention --- at
   the recorded revision only one other file in the repository uses Mermaid, a
   research note rather than an accepted standard.
4. **Threat table (STRIDE).** One row per element or trust-boundary crossing:
   element/interaction, STRIDE category (S/T/R/I/D/E), threat description, and the
   evidence citation for why the threat applies to this system (see *Evidence
   expectations*).
5. **Mitigations and status.** One row per threat: the mitigation (or the
   decision not to mitigate), its status using Microsoft's four values verbatim
   (*Not Started*, *Needs Investigation*, *Mitigated*, *Not Applicable*), an owner,
   and the evidence citation for the mitigation's existence.
6. **Review and validation.** Per the Manifesto's "Did we do a good enough job?":
   who reviewed the model, when, and what would trigger re-review -- the Manifesto
   states threat modeling "must align with an organization's development
   practices and follow design changes in iterations that are each scoped to
   manageable portions of the system," so this section should name the specific
   design changes (to the architecture node this model `depends-on`) that would
   invalidate the current analysis. That same clause is also the Manifesto's own
   guidance on how large a single threat-model node should be: keep one node's
   scope to a manageable portion of the system being modeled, rather than one
   node attempting to threat-model an entire architecture at once -- if the
   system being modeled already decomposes into multiple architecture nodes
   (context, container, component), prefer one threat-model node per
   `depends-on` target over a single node spanning several of them.
7. **Boundary statement.** An explicit paragraph naming what this node does not
   cover, using the four exclusions in *Boundary: what this template is not* as
   the checklist, plus any node-specific exclusion the author found.
8. **Relationships**, per the guidance below.
9. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node
   does not cover, who owns it, and separately, what was expected but could not
   be verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [System/container/data-flow name]: threat model

[One paragraph: what this decomposes, and what question the analysis answers.]

## Notation legend

| Shape | DFD meaning |
|---|---|
| ... | ... |

## System model

```mermaid
[DFD approximated in Mermaid flowchart syntax: external entities, processes,
data stores, data flows, and trust boundaries as labeled subgraphs, matching the
boundaries already decided by the architecture node this analysis depends-on]
```

## Threats (STRIDE)

| Element / interaction | Category | Threat | Evidence |
|---|---|---|---|
| ... | S/T/R/I/D/E | ... | path/symbol/PR citation |

## Mitigations

| Threat | Mitigation | Status | Owner | Evidence |
|---|---|---|---|---|
| ... | ... | Not Started / Needs Investigation / Mitigated / Not Applicable | ... | path/symbol citation |

## Review and validation

- Reviewed by: [who], on [when]
- Re-review triggers: [which changes to the modeled design invalidate this analysis]

## Boundary

This node does not describe:
- [vulnerability-disclosure process -- see SECURITY.md if one exists]
- [org-wide security controls this system merely uses -- see the relevant policy node]
- [pen-test/audit findings -- cited as evidence above, not restated here]
- [the modeled system's own design -- see the architecture node this depends-on]
- [any node-specific exclusion]

## Relationships

- depends-on: <the architecture node's id this threat-models>

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
author opened the cited source, `INFERENCE` means the author reasoned to the
claim and rated the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated statement
attributed to whoever said it. Nothing about this template relaxes or narrows
that. Several expectations follow specifically from the industry model this
template adapts:

- **A threat's applicability is a `FACT` or nothing.** A threat-table row
  asserting "an attacker could tamper with X" with no citation is asserting an
  attack surface that may or may not exist in the real system. Cite the data
  flow, the interface, or the trust-boundary crossing the reader can open to
  confirm the row -- a config file, an API definition, or the architecture node's
  own diagram.
- **A `Mitigated` or `Not Applicable` status is the strongest claim this table
  makes, and needs the strongest evidence.** `Not Applicable` is itself a
  security claim -- "an existing control already covers this" -- not the absence
  of one; `AGENTS.md`'s own evidence rules apply to it exactly as they would to
  any other assertion. Cite the actual control (code, config, test, or an
  accepted decision), not a description of intended behavior.
- **A diagram element with no matching threat-table row is an unmodeled attack
  surface wearing a picture.** `validate.py` never inspects a diagram's content
  -- it is Markdown text to the checker like any other. Every trust-boundary
  crossing in the required diagram needs a corresponding row in the threat
  table; a diagram that shows more than the table analyzes is the failure mode
  `AGENTS.md`'s own evidence section warns about, expressed as a picture instead
  of a sentence.
- **A pen-test finding, an incident, or a security advisory is legitimate
  evidence, cited like any GitHub-hosted source.** Per `AGENTS.md`'s citation
  table, an issue or PR discussing a finding has no openable file and no way to
  pin one -- it lands on `TEAM_KNOWLEDGE` with `provided_by` naming the source,
  never promoted to `FACT` on a bare URL or tool-result citation.

## Relationships

A node built from this template:

- **must** declare `implements` targeting `corpus-template-threat-model` (this
  node's id) once this node is merged. `relationships.schema.json` names *"a
  template instance of a standard"* as `implements`' own worked example -- this
  is exactly that case, not the weaker `references` edge. This is not
  hypothetical: PRD `#607`'s acceptance criteria require *"every node passes
  corpus schema/graph/provenance validation and uses the assigned template,"*
  and issue `#1180` ("document layers/security/threat-model.md", parent `#607`)
  is a concrete, already-filed future task that will need to declare this exact
  edge once both nodes exist and are merged.
- **should** declare `depends-on` targeting the id of the architecture node
  (context, container, or component) it threat-models, once that node exists and
  is merged. Per this node's own `INFERENCE` above, `depends-on`'s schema
  directionality -- "source requires target to be true/current for source's own
  claims to hold" -- matches a threat model's dependency on the design it
  analyzes staying current more closely than any of the schema's other four
  types.
- **may** declare `references` toward a `SECURITY.md` vulnerability-disclosure
  policy, an incident record, or an accepted decision cited as mitigation
  evidence, when those exist as separate documents rather than inline citations.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes
present in `origin/launchpad`'s corpus tree at the recorded revision --
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references` -- are all procedural/meta-documents about
the corpus itself, none of them threat-modeling or general security subject
matter this node would `depends-on`, `references`, or sit `part-of`. None of the
four sibling templates in this batch (`#1331`, `#1336`, `#1340`, `#1346`) target
this node or are targeted by it, deliberately -- all five are authored in
parallel with no merge ordering between them, and none of their subjects
(concept, deployment, glossary-term, reference) is a natural relationship target
for a threat-model template either. The first threat-model instance node is the
natural moment to add a `depends-on` edge toward whatever architecture node it
analyzes, once that exists.

## Note on Definition of Done

Issue `#1351`'s own Definition of Done carries four bullets -- "states scope and
authority/source of the policy," "separates MUST requirements from SHOULD
guidance," "defines enforcement/checks and exception/escalation process," "links
decisions or higher-order policy instead of duplicating them" -- copied verbatim
from the standards-track issues that produced `standards/confidence.md` and
`standards/decision-references.md`. Those describe a **policy/standard** node (a
MUST/SHOULD normative document over existing corpus behavior); this node is a
**template** (a prescription for the shape of a future document). The real
acceptance criterion, from parent Feature `#605` itself, is: *"every template
states its purpose, required sections, evidence expectations and the industry
model/standard it adapts."* This node is built against that sentence -- *Required
sections*, *Evidence expectations* and *Industry model this template adapts*
above answer it directly -- rather than against the standards-track checklist,
which does not fit a document with no MUST/SHOULD normative claims about
existing system behavior to separate.

## Scope and omissions

**This node covers** what a corpus node documents when its subject is a
threat-model analysis of one system, container, or data flow: the required body
sections, the evidence expectations for a threat or mitigation claim, the
industry model (STRIDE + OWASP's four-phase process, grounded in the Threat
Modeling Manifesto) the shape adapts, the explicit boundary against
disclosure-policy/control-catalog/pen-test-report/architecture documents, the
relationship type a node built from this template should use, and the
front-matter `type` such a node should carry.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The architecture templates (context, container, component) a threat model `depends-on` | `#1328`, `#1327`, `#1326` (a prior batch's tasks, PRs #1531/#1529/#1528 open, not merged) |
| A `SECURITY.md` vulnerability-disclosure policy, if this corpus ever wants one as content | Not yet filed as a task at time of writing |
| An org-wide security-control catalog or policy | Not yet filed as a task at time of writing |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |

**No relationships declared in this node's own front matter.** See
*Relationships* above for what was checked and why none of the four nodes that
exist on `origin/launchpad` at the recorded revision are a fit.

**Expected but not verified when this node was written:**

- **No node has yet been authored from this template.** Every claim above about
  what a threat-model node needs is grounded in the STRIDE/OWASP/Manifesto
  primary sources, not in a worked instance. The first real threat-model node --
  once an architecture node exists for it to `depends-on` -- is what will
  actually test whether the required sections above are sufficient or need
  revision.
- **Whether Mermaid's flowchart syntax can faithfully express DFD trust
  boundaries at scale for a complex system was not tested against a real,
  large diagram.** The notation gap (no native DFD support) is verified; how well
  the `subgraph`-as-trust-boundary workaround holds up in practice is not.
