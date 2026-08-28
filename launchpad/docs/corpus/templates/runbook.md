---
id: corpus-template-runbook
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "PRD #605's real acceptance criterion for a corpus template is: every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria"
  - statement: "Issue #1347's definition-of-done checklist -- states scope and authority/source of the policy, separates MUST from SHOULD, defines enforcement/checks and exception/escalation process, links decisions instead of duplicating them -- is boilerplate copied verbatim from the standards-track issues, not a requirement written for a template."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1347 definition of done, compared against launchpad-26/buzz#1310's definition of done"
  - statement: "node.schema.json's type enum is a closed list of thirteen corpus surfaces -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and contains no template or policy member."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every merged corpus meta-document about how to author corpus content -- AGENTS.md, standards/confidence.md, standards/decision-references.md -- uses type: governance; README.md, the human-facing entry point, also uses it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "operations is one of the thirteen values in node.schema.json's type enum, and is the enum's own name for the corpus surface an operational document such as a runbook instance belongs to."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The Google SRE Workbook's 'Being On-Call' chapter defines a playbook as high-level instructions on how to respond to automated alerts, explaining the alert's severity and impact and including debugging suggestions and possible actions to mitigate impact and fully resolve the alert, and states that in SRE practice a playbook entry is usually created whenever an alert is created."
    entry_class: FACT
    evidence:
      - "https://sre.google/workbook/on-call/"
  - statement: "The same chapter warns that if a playbook is a deterministic list of commands the on-call engineer runs every time a particular alert fires, the recommended fix is to implement automation instead of documenting the steps."
    entry_class: FACT
    evidence:
      - "https://sre.google/workbook/on-call/"
  - statement: "The Google SRE Book's example postmortem (Appendix D) is a retrospective document written after an incident concludes, built around root-cause analysis, a timeline and a lessons-learned/action-items structure, which is a different purpose from a playbook's real-time prescriptive response guidance."
    entry_class: FACT
    evidence:
      - "https://sre.google/sre-book/example-postmortem/"
  - statement: "An unmerged research note argues the SRE Workbook playbook definition as the grounding model for a runbook template, states the same deterministic-list-should-be-automated caveat, and explicitly treats the SRE Book Appendix D postmortem template as a separate document type from a runbook, not to be merged with it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note), launchpad/Research/project-documentation-templates.md on branch docs/research-project-doc-templates"
  - statement: "A node's evidence array is validated per-entry: entry_class FACT requires evidence and forbids confidence and provided_by; INFERENCE requires both evidence and confidence and forbids provided_by; TEAM_KNOWLEDGE requires provided_by, forbids confidence, and evidence is optional."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A relationships[].target naming an id no node loaded from the validated tree carries is a hard validation error, so an edge may only name a node already merged to the branch being validated against."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "At this node's recorded revision, origin/launchpad's corpus tree carries exactly four authored nodes outside schema/: corpus-agents, corpus-readme, corpus-standard-confidence and corpus-standard-decision-references, and none of them is topically about operational runbooks."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, schema/**, standards/confidence.md, standards/decision-references.md"
  - statement: "The four sibling corpus-template issues in this batch (#1326, #1327, #1328, #1335) are authored in parallel with this one and none of them will be merged before review starts on the others, so no edge among the five templates is declarable yet."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "batch dispatch brief for issues #1326/#1327/#1328/#1335/#1347"
---

# Template: runbook

What a `runbook` corpus node is for, the sections it must carry, how to cite the
claims inside it, and the industry model it adapts. This is a **template node**: it
does not itself document an alert or a system, it defines the shape every runbook
node must take.

## Note on this issue's definition of done

Issue #1347's checklist includes "states scope and authority/source of the policy,"
"separates MUST from SHOULD," "defines enforcement/checks and exception/escalation
process," and "links decisions instead of duplicating them." That text is copied
verbatim from the standards-track issues (compare `#1310`'s definition of done,
which produced [`standards/decision-references.md`](../standards/decision-references.md))
and describes a **policy/standard** node -- a MUST/SHOULD normative document with
its own enforcement and escalation process. A template is a different kind of
artifact: it does not impose obligations on the rest of the corpus, it specifies
the shape one node type must take. This document is built against the criterion
that actually governs it, from the parent Feature:

> Every template states its purpose, required sections, evidence expectations and
> the industry model/standard it adapts.

Everything below is organized around those four things. There is deliberately no
MUST/SHOULD section, no enforcement/escalation process of its own, and no claim of
"authority" beyond the four things above -- a template does not enforce, `AGENTS.md`
and `validate.py` do that for every node including instances of this one.

## Scope and authority

**This node covers** what a `runbook` corpus node documents, its required sections,
how to classify and cite claims inside it, the industry source it adapts, and where
it draws the line against automation and against a different document type
(the postmortem).

**This node does not cover, and does not restate:**

| For | Read |
|---|---|
| The front-matter contract every node -- including a runbook -- must satisfy | [`launchpad/docs/corpus/schema/node.schema.json`](../schema/node.schema.json) |
| How to create, update and retire a node, and the evidence-class rules | [`launchpad/docs/corpus/AGENTS.md`](../AGENTS.md) |
| The `confidence` field on an `INFERENCE` entry | [`launchpad/docs/corpus/standards/confidence.md`](../standards/confidence.md) |
| Citing an accepted decision as evidence | [`launchpad/docs/corpus/standards/decision-references.md`](../standards/decision-references.md) |

If this document and any of those disagree, **they win** -- this one has drifted
and should be fixed.

## Purpose

A `runbook` node documents **how to respond to one specific operational
condition** -- an alert, a failure mode, a degraded state -- for whoever is
on-call when it fires. It is written for the moment of the incident, not for
understanding the system in general (that is an `architecture` node's job) and not
for explaining what happened after the fact (that is a postmortem -- see
*What this is not*, below).

**Grounding model.** The Google SRE Workbook's "Being On-Call" chapter defines a
playbook as:

> "high-level instructions on how to respond to automated alerts. They explain the
> severity and impact of the alert, and include debugging suggestions and possible
> actions to take to mitigate impact and fully resolve the alert."

and notes that "whenever an alert is created, a corresponding playbook entry is
usually created." A `runbook` node is this repository's corpus name for that
document. **High-level** is doing real work in that definition: the chapter is
explicit that a playbook is not a script.

**The automation boundary.** The same chapter states the limit directly:

> "If your playbooks are a deterministic list of commands that the on-call
> engineer runs every time a particular alert fires, we recommend implementing
> automation."

A `runbook` node that has degenerated into an exact, unconditional command
sequence is a sign the corpus is documenting something that should instead be
code. Before writing a runbook, or before adding a new deterministic step to one
that exists, ask whether it should be a script or a workflow instead (see
`buzz-workflow` for this repository's own workflow engine). Documenting judgment,
triage and the *possible* actions an on-call engineer chooses among is the right
use of this template; documenting one fixed sequence with no decision point in it
is not.

## What this is not

**Not a postmortem.** The Google SRE Book's example postmortem (Appendix D) is a
retrospective document, written after an incident closes, organized around root
cause, timeline and lessons learned. A runbook is prescriptive and used *during*
an incident; a postmortem is analytical and written *after* one. They answer
different questions for different readers at different times, and merging them
into one node would make a single document serve two purposes badly. There is no
postmortem template issue in this batch -- if one is needed, it is a separate
node under its own task, not a section added here.

**Not a general operations guide.** A runbook is scoped to *one* alert or failure
condition. A node that tries to cover "how to operate service X" in general is
either an `operations`-type reference node or several runbooks, not one.

**Not a substitute for the alert itself.** A runbook explains what to do once an
alert has fired; it does not define the alert's trigger condition (that lives in
the alerting configuration) beyond citing it for context.

## Required sections

A `runbook` node's body **must** carry the following, each traceable to the SRE
Workbook definition quoted above:

1. **Trigger.** The alert or condition that leads a reader here -- named precisely
   enough that a reader arriving from a paging tool recognizes it, and citing the
   alerting rule or configuration that fires it where one exists in this
   repository.
2. **Severity and impact.** What is actually going wrong for a user or the system
   when this fires, and how urgent it is. This is the SRE Workbook's "explain the
   severity and impact of the alert."
3. **Diagnosis.** Debugging suggestions -- what to check first, and what
   distinguishes this condition from similar-looking ones. This is the "debugging
   suggestions" clause.
4. **Mitigation and resolution.** The possible actions available, in the order a
   responder would reasonably try them, distinguishing an action that reduces
   impact now (mitigation) from one that resolves the underlying condition
   (resolution) when the two differ. This is "possible actions to take to
   mitigate impact and fully resolve the alert."
5. **Escalation.** Who or what to involve if the actions above do not resolve it,
   and after how long a responder should stop trying alone.
6. **Scope and omissions.** As in every corpus node: what this runbook does not
   cover, and what was expected but could not be verified when it was written.

A node missing any of 1-5 has not documented a playbook in the SRE Workbook's
sense -- it has documented something narrower (e.g. only a description of the
alert, with no actions) and should not carry `type: operations` with this
template's `implements` relationship (see *Front matter for a runbook instance*)
until it does.

## Evidence expectations

A runbook's claims follow the same three-class contract as any other corpus node
-- `AGENTS.md` owns that contract in full and it is not restated here. What is
specific to a runbook is *which* claims tend to fall in which class:

- **FACT.** The alert's trigger condition, cited to the alerting rule or
  configuration that defines it. A mitigation command's actual effect, where that
  effect is established by reading the code or configuration it acts on (not by
  having run it once and observed an outcome, which is a single data point, not a
  read source).
- **INFERENCE.** "This condition is usually caused by X" reasoned from logs,
  metrics or past incidents the author actually examined -- carries `confidence`,
  and should be rated using the coarse bands in
  [`standards/confidence.md`](../standards/confidence.md) rather than an invented
  scale.
- **TEAM_KNOWLEDGE.** Tribal know-how that no source corroborates -- "the third
  restart usually works" with no logged reason why -- attributed via
  `provided_by` to whoever said it: an on-call engineer, an incident retro, a
  Slack thread. A runbook is exactly the kind of document tribal knowledge
  accumulates in, and honestly marking it `TEAM_KNOWLEDGE` rather than dressing it
  up as `FACT` is the whole point of the corpus's evidence contract.

**A step is not automatically a claim.** "Run `systemctl restart foo`" is an
instruction, not a statement needing a citation. It becomes a claim, and needs
one, the moment the runbook asserts *why* the step works or *what condition* it
is meant to fix -- "restarting foo clears the stuck connection pool" is a claim
about the system's behavior and needs a `FACT` or `INFERENCE` entry, the same as
any other node.

## The industry model this adapts

**Google SRE Workbook (2018), "Being On-Call" chapter** -- the freely published,
web-hosted continuation of the 2017 SRE Book. It has no version number and its
publication year (2018) is the only date on it; it is not a versioned, dated
specification the way MADR or Keep a Changelog are. Cite it by URL
(`https://sre.google/workbook/on-call/`), not by a version that does not exist.
This template adapts its playbook definition directly (see *Purpose*, above);
nothing in this template is invented independently of it.

## Front matter for a runbook instance

A concrete runbook node -- not this template, an actual node documenting one
alert -- should use `type: operations`. That value is one of the thirteen
surfaces `node.schema.json`'s `type` enum defines, and is the enum's own name for
an operational document; nothing else in the enum fits a document whose subject
is "how to respond when this fires." This template itself uses `type: governance`
because its own subject is corpus-authoring practice, not an operational
condition -- the same reasoning `standards/confidence.md` and
`standards/decision-references.md` use for the same `type` choice, and the reason
this document is not itself an example of what it defines.

A runbook instance that is written as the concrete realization of this template
should declare a `relationships` entry `{type: implements, target:
corpus-template-runbook}` -- `implements` is defined for exactly this case: "the
concrete realization of target (e.g. a template instance of a standard)."

## Scope and omissions

**This node covers** what a `runbook` node documents, its required sections, how
to classify and cite claims inside it, its industry source, and its boundaries
against automation and against the postmortem document type.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The front-matter contract every node satisfies | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node, and the evidence-class rules in general | `launchpad/docs/corpus/AGENTS.md` |
| The `confidence` field's meaning and bands | `launchpad/docs/corpus/standards/confidence.md` |
| A postmortem template | Not owned by any issue in this batch; there is no postmortem issue among #1326-#1351 as dispatched |
| Whether a runbook may itself trigger automation (e.g. a `buzz-workflow` hook) rather than only describing manual steps | Not settled here; flagged as an open question below |

**No `relationships` in this node's own front matter.** `git ls-tree -r
--name-only origin/launchpad -- launchpad/docs/corpus` was run for this node (not
assumed) and shows exactly four authored nodes at the merge target:
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence` and
`corpus-standard-decision-references`. None of them is topically about
operational runbooks, so there is no id in the current merge target this
template's own claims depend on or extend. This mirrors the choice
`standards/confidence.md` and `standards/decision-references.md` already made for
the same reason -- `corpus-agents` would resolve as a target today, but both
chose to add the whole cross-corpus edge set in one later pass once more of the
standard/template siblings land, rather than one edge at a time against a set
still taking shape. This node follows the same practice rather than adding a
single edge in isolation. It also declares no edge to any of the four sibling
template issues in this same batch (`#1326`, `#1327`, `#1328`, `#1335`) --
none of them will be merged before review starts on the others, so none of their
ids exist at any plausible merge target yet.

**Expected but not verified when this node was written:**

- **No runbook instance exists yet in this repository's corpus to check this
  template against.** Everything above is derived from the SRE Workbook's
  definition and from this corpus's own schema and conventions, not from having
  scaffolded and validated a real example. `#605`'s own acceptance criteria
  include "an independent agent can scaffold and validate one example node using
  only the standard/template/schema" -- that has not been attempted for this
  template.
- **Whether a runbook should ever declare `depends-on` toward the alerting
  configuration or service it covers was not resolved.** `depends-on`'s
  directionality ("source requires target to be true/current for source's own
  claims to hold") plausibly fits an alert-trigger citation, but no alerting
  configuration is itself a corpus node today, so there is no id such an edge
  could name, and whether one ever should be is outside what this template
  settles.
- **Whether a runbook may itself specify or trigger automation** (rather than
  only ever describing manual steps a human takes) was raised by the automation
  boundary above but not resolved -- it interacts with `buzz-workflow`, which is
  implementation, not corpus documentation, and settling it is out of scope for
  a template task.
