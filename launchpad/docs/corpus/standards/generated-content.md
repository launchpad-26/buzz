---
id: corpus-standard-generated-content
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
relationships:
  - type: references
    target: corpus-agents
evidence:
  - statement: "This node was authored and checked against repository revision 919886b4192df6251de50c547548ecae5d85afce."
    entry_class: FACT
    evidence:
      - "commit 919886b4192df6251de50c547548ecae5d85afce"
  - statement: "Markdown files with YAML front matter are the one canonical, authored representation of every corpus node; JSON, search indexes, dependency graphs and any other serialization are generated derived views, never hand-authored, always reproducible from the canonical Markdown."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The corpus validator rejects every non-Markdown file under the corpus root (schema/ excluded) that does not live under a generated/ subdirectory, naming it a misplaced generated artifact or hand-authored content in the wrong format."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A non-Markdown file correctly placed under generated/ is rejected today too, because directory placement only proves where a file sits, not that a generator produced it and can reproduce it, and no such generator exists yet."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The validator distinguishes the two rejections in its output: a stray non-Markdown file outside generated/ is reported as 'outside generated/', and a non-Markdown file correctly placed inside generated/ is reported with 'reproducibility' in the message and never with 'outside generated/', so the two failure modes are not the same defect."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/tests/test_validate.py"
  - statement: "Both rejections are hard errors, not the non-fatal UNVERIFIED channel; an earlier revision of the validator reported a correctly-placed-but-unproven generated/ file as a non-fatal notice, and that was rejected in review because it would let a hand-authored artifact print one line and still exit 0."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The validator's ownership check only inspects files whose suffix is not .md; a file with a .md suffix anywhere under the corpus root, including under generated/, is never evaluated by that check and is instead loaded and schema-validated exactly like any other corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "No corpus generator exists yet to reproduce a non-Markdown artifact from canonical Markdown and compare against it, which is the reproducibility half of ADR-0028 that a generated/ directory name alone cannot prove."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "relationships.schema.json marks the inverse of four of the five relationship types -- depends-on, supersedes, implements and part-of -- as generated (depended-on-by, superseded-by, implemented-by, has-part), while the inverse of references (referenced-by) is marked authored."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "node.schema.json's relationships array accepts only the five forward types -- depends-on, supersedes, implements, references, part-of -- and has no field for an inverse edge, so a generated inverse relationship can only exist in a separately generated view, never in a node's own front matter."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #633, 'implement deterministic corpus graph and index generation', is open, is not scoped to author any canonical corpus document, and its own definition of done requires generated outputs to include a do-not-edit marker and generator/source revision, deterministic ordering and formatting, derived (not hand-maintained) inverse graph edges where the schema says so, and tests covering stable no-change regeneration."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#633"
  - statement: "As of this node's recorded revision, launchpad/project-intelligence/corpus/indexes.py -- the file #633 names as the generator's impacted component -- does not exist in the repository."
    entry_class: FACT
    evidence:
      - "file_exists('launchpad/project-intelligence/corpus/indexes.py') -> False"
  - statement: "Issue #891, one of a family of open 'generate corpus document generated/*.md' tasks under parent PRD #621, requires its generated document to have schema-valid front matter, to be reproducible from canonical nodes without authored knowledge, to carry an explicit generated/do-not-edit marker, to name its generator, inputs, inclusion/exclusion rules and deterministic ordering in its own body, and to produce no diff on a no-change rerun at the same revision; its own out-of-scope list bars it from creating a second hand-authored canonical corpus document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#891"
  - statement: "Issue #1339, 'define the generated index corpus template', is open and scoped to create launchpad/docs/corpus/templates/generated-index.md as the per-type authoring template for a generated index node, distinct from this node's scope of policy rather than template."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1339"
  - statement: "Issue #1302, one of a sibling family of open 'generate corpus document specifications/*.md' tasks (parent PRD #621), carries the identical generated-document definition of done as #891 -- not hand-authored, a do-not-edit marker, no-change reruns produce no diff -- but targets a path under specifications/ rather than generated/, so the checker's generated/-placement rule for non-Markdown artifacts does not constrain where a generated Markdown document may live."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1302"
  - statement: "ADR-0027 records that the knowledge crate's human-facing and agent-facing surfaces are both pre-rendered by a pipeline and committed alongside the corpus, but it does not state that those pre-rendered artifacts live under launchpad/docs/corpus/ specifically, so whether they fall under this node's scope is not established here."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0027-knowledge-crate-split-surface.md"
  - statement: "Changes under launchpad/docs/corpus are validated in CI by a workflow triggered on pull requests and on pushes to the launchpad branch, running the same validator command a local run uses."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "The validator has no flag, environment variable or marker-file mechanism that exempts a specific non-Markdown file from the generated/-ownership check; --root is its only command-line option."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Issue #1316 requires this node to state its scope and the authority its policy rests on, to separate MUST requirements from SHOULD guidance, and to define enforcement and an exception or escalation process."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1316 definition of done"
  - statement: "The relationship target corpus-agents exists on the launchpad branch as of the check run for this node (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, run 2026-08-27), alongside corpus-readme, corpus-standard-confidence and corpus-standard-decision-references."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, run against this fork's remote on 2026-08-27"
---

# Standard: generated content

What counts as generated (rather than hand-authored) content in the documentation
corpus, where it may live, what must be true before it may be committed, and what
happens when it cannot be.

This is a policy node. Look up the section you need.

| For | Read |
|---|---|
| Why Markdown+front matter is canonical and everything else is a generated derived view | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| What the checker actually enforces about placement and ownership today | `launchpad/project-intelligence/corpus/validate.py` (`find_ownership_violations`) |
| Creating, updating and retiring a node; the six citation shapes | `launchpad/docs/corpus/AGENTS.md` |
| Relationship types and their directionality, including which are generated | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The front-matter contract every node -- generated or not -- is validated against | `launchpad/docs/corpus/schema/node.schema.json` |
| The generator itself, once it exists | `launchpad-26/buzz#633` |
| The per-type template for a generated index node | `launchpad-26/buzz#1339` |

Those sources are authoritative. Where this document and any of them disagree, **they
win** — this one has drifted and should be fixed.

## Scope and authority

**This node covers** what "generated" means for a file or a front-matter field inside
`launchpad/docs/corpus/`, where a generated artifact must live, what a generator must
be able to prove before its output may be committed, how the validator treats each
class of generated content today, and what happens when a generator does not yet
exist for the content someone wants to commit.

**Its authority is derived, not original.** `ADR-0028` already decided that every
non-canonical serialization is "a generated derived view — never hand-authored, always
reproducible from the canonical Markdown." This document does not create that rule and
cannot relax it; it states what following it means in practice, and states plainly
where practice (the validator) currently enforces more of it than any generator can
yet satisfy. The corresponding structural check is `validate.py`'s
`find_ownership_violations`, run by `just corpus-validate` and in CI on every change
under the corpus root.

**What this node does not decide.** Whether the knowledge crate's own pre-rendered
pages (ADR-0027's human and agent surfaces) fall under this policy is not settled
here — ADR-0027 does not say those artifacts live under `launchpad/docs/corpus/`, and
deciding that they do, or extending this policy to reach them, is an ADR-shaped
question this document does not answer. See *Scope and omissions*.

## Two kinds of generated content, not one

"Generated content" in this corpus is not a single shape. Two different things are
both generated derived views under ADR-0028, and the checker treats them completely
differently:

1. **A non-Markdown artifact** — an index, a graph, a search serialization. This is
   the case ADR-0028 names explicitly and the case `find_ownership_violations` exists
   to police.
2. **A Markdown corpus node produced by a generator instead of a person** — for
   example one of the `generate corpus document generated/*.md` family of tasks
   (`#886`–`#906` and others), or the sibling `generate corpus document
   specifications/*.md` family (`#1302`–`#1306`) that carries the identical
   definition of done but is placed under `specifications/` instead. Because its
   suffix is `.md`, the ownership check never inspects it at all, regardless of which
   subdirectory it lives in. It is loaded and schema-validated exactly like any
   hand-authored node: `id`, `type`, `status`, `origin`, `audiences`, `evidence`, and
   optionally `relationships`, all required, none of them relaxed because a generator
   wrote the file instead of a person.

   **So `generated/` is not "where generated Markdown documents go."** It is one
   subject-based subdirectory among several that happens to hold some of them. The
   directory-placement rule in MUST 2 below governs non-Markdown artifacts only; a
   generated Markdown document is placed by subject, the same as a hand-authored
   one, and the `specifications/*.md` family is the evidence that this is deliberate
   rather than an oversight in one task's naming.

That second point is easy to miss and worth stating plainly: **a `.md` suffix is not
an exemption from anything.** The evidence, provenance and one-idea-per-node rules in
`AGENTS.md` apply to a generated Markdown node exactly as they apply to a hand-authored
one. What makes it "generated" is a claim the *body* and the authoring process make,
not something the schema or the validator can currently detect from the file itself.

## MUST

These are enforced today, or follow directly from what is already enforced. A node or
a generator violating any of them does not merge.

1. **A generated artifact MUST NOT be hand-authored.** It must be reproducible from
   canonical Markdown by a generator. This is ADR-0028 stated as a requirement rather
   than a description.
2. **A non-Markdown generated artifact MUST live under a `generated/` subdirectory
   of the corpus root.** Any other location is a hard validation error, reported as
   a misplaced artifact.
3. **Placement under `generated/` MUST NOT be treated as proof the file was actually
   generated.** The validator does not treat it as proof either: a non-Markdown file
   correctly placed under `generated/` is rejected today with the same severity as one
   placed anywhere else, because nothing establishes that it is reproducible. A
   directory name proves where a file sits, never how it got there.
4. **No non-Markdown generated artifact may be committed under the corpus root
   today, `generated/` included.** This follows from MUST 3 as the validator's
   current, unconditional behavior: every such file is rejected, whether or not it
   sits in the right place, because no generator exists yet that can be pointed at to
   establish reproducibility. This is not a design choice this document is making; it
   is the observed state of `validate.py`, and it holds until a generator exists for
   the specific class of artifact in question.
5. **A generated Markdown corpus node MUST satisfy `node.schema.json` exactly as a
   hand-authored node does.** The ownership check does not run against it, but nothing
   else in the schema or the evidence contract is relaxed for it either.
6. **A node's own front matter MUST NOT hand-author an inverse relationship edge for
   a relationship type whose inverse `relationships.schema.json` marks `generated`** —
   `depended-on-by`, `superseded-by`, `implemented-by`, `has-part`. `node.schema.json`
   has no field for any of those names, so there is no way to write one into a node's
   own front matter today regardless; the requirement is stated so a future generator
   or hand-edit does not invent one. `referenced-by`, the one inverse marked
   `authored`, is the sole exception: a node may hand-author that edge if it wants one,
   because nothing derives it.

## SHOULD

These are the conventions the open generated-document tasks already commit to in
their own definitions of done (`#633`, `#891` and the rest of that family). Nothing
in the validator checks them yet — they are enforced by review and by the generator's
own tests once one exists, not by `find_ownership_violations` or any other run of
`validate.py`. Depart from them with a reason.

- **A generated Markdown node's body SHOULD carry an explicit generated/do-not-edit
  marker.** A reader opening the file should not mistake it for a hand-authored node
  they may safely edit in place.
- **A generator SHOULD produce deterministic ordering and formatting**, so that
  regenerating from the same canonical inputs at the same revision produces no diff.
  A generator whose output reorders itself on every run makes every regeneration look
  like a content change, which defeats the review-diff mechanism ADR-0028 depends on.
- **A generated document SHOULD name its generator, its inputs, its
  inclusion/exclusion rules and its ordering rule in its own body.** A reader
  should be able to tell what produced the file and from what, without reading the
  generator's source.
- **Inverse graph edges SHOULD be derived by the generator, not hand-maintained**,
  for the relationship types `relationships.schema.json` marks `generated`. This is
  the same requirement as MUST 6, restated as a design goal for whatever eventually
  computes those edges into a generated view.

## Enforcement, and where it stops

**Enforced mechanically**, by `validate.py`'s `find_ownership_violations`, run
locally by `just corpus-validate` and in CI on every pull request and push to
`launchpad` touching the corpus: every non-Markdown file under the corpus root
(`schema/` excluded) is rejected, with a distinct message for "outside `generated/`"
versus "correctly placed but unproven."

**Enforced mechanically, but not specially**, for a generated Markdown node: it goes
through the same `node.schema.json` validation as any node. There is no separate
"generated node" code path in the validator today.

**Not enforced by anything:**

| Gap | Consequence |
|---|---|
| Whether a Markdown node under `generated/` was actually produced by a generator, or hand-written to look like one | Indistinguishable to the validator. A hand-written file with a plausible do-not-edit marker passes exactly like a real projection. |
| The do-not-edit marker itself | Nothing checks for its presence or its wording. |
| Deterministic, no-diff regeneration | No generator exists to test this against; `#633`'s own definition of done names it as a requirement on the generator's tests, not on `validate.py`. |
| Naming the generator, inputs and ordering rule in a generated document's body | A reviewer's responsibility; no schema field carries it and no check reads the body for it. |
| A hand-authored inverse-relationship edge, if one somehow reached front matter | `node.schema.json`'s closed enum already prevents this structurally for the four generated-inverse names, so there is currently nothing left for a check to catch — the gap is theoretical, not observed. |

## Exceptions and escalation

**There is no exception process for MUST 2–4, and this document does not create
one.** The validator fails closed: every non-Markdown artifact under the corpus root
is rejected regardless of placement, and there is no flag, environment variable or
marker-file mechanism to except a specific one. An earlier revision of the validator
treated a correctly-placed-but-unproven file as a non-fatal notice instead of an
error; that was rejected in review specifically because it functioned as an ad hoc
exception, letting a hand-authored artifact pass as though it were a real projection.
Reopening that gap here, even as documented policy, would undo the reason it was
closed.

**The only route past MUST 4 is building the generator**, or the specific piece of it
a given artifact needs, and proving reproducibility the way `#633` and `#891`'s
definitions of done already describe — a do-not-edit marker, a source revision, and a
no-change rerun that produces no diff. That is tracked work, not a decision this
document can grant on request.

**A broader exception — for example, allowing a generated artifact to bypass
`generated/` placement, or exempting a class of file from reproducibility
entirely — is a change to ADR-0028's rule, not an application of it.** That is an ADR,
decided by a human, following this repository's normal path: a `type:adr` issue
parented to the PRD raising the question, argued there, and written up as a decision
record in the PR that closes it. This document does not anticipate what such a
decision would say, and does not invent an exception in its absence.

**When you believe you have a legitimate case this document does not cover**, escalate
it as that ADR rather than working around the validator or hand-writing a file into
`generated/` and hoping it passes review. It will not pass `validate.py` either way.

## Scope and omissions

**This document covers** the distinction between generated and hand-authored content
in the corpus, where a non-Markdown generated artifact must live, why placement alone
is not proof, how a generated Markdown node is validated, what the open
generated-document tasks already commit to as convention, which relationship inverses
are meant to be generated rather than hand-authored, what the checker enforces today,
and the (currently absent) exception process.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Building the generator itself | `launchpad-26/buzz#633` |
| The concrete generated documents under `generated/` (e.g. `corpus-index.md`, `test-index.md`, and the rest of that family) | The individual `generate corpus document generated/*.md` tasks, e.g. `#891`, `#892`, `#894`–`#906` |
| The concrete generated documents under `specifications/` (e.g. `INDEX.md`, `normative-documents.md`) | The individual `generate corpus document specifications/*.md` tasks, `#1302`–`#1306` |
| The per-type authoring template for a generated index node | `launchpad-26/buzz#1339` |
| Whether the knowledge crate's own pre-rendered pages (ADR-0027) fall under this policy | Not established here; ADR-0027 does not say those artifacts live under `launchpad/docs/corpus/` |
| The general evidence contract, citation shapes and claim classification | `launchpad/docs/corpus/AGENTS.md`, and the evidence standard, `#1314` |
| Per-type node templates and naming/identifier/status/normative-language standards for the corpus generally | somewhere in `#1307`–`#1351`, per `AGENTS.md`'s own scope table |

**Relationships.** `references -> corpus-agents` is declared because `corpus-agents`
names the exact gap this node fills ("That contract is owned by #1316") and this node
extends that passage without duplicating its create/update/retire procedure. Checked
immediately before finalizing this front matter, not from memory:
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` (run 2026-08-27)
returned `corpus-agents`, `corpus-readme`, `corpus-standard-confidence` and
`corpus-standard-decision-references` — all four already merged to `launchpad`. No
edge is declared to the other three: neither `corpus-readme` nor either sibling
standard states or depends on anything about generated content specifically, and
adding an edge without a claim it supports would be decoration, not a relationship.
This node deliberately does **not** target any of the other four documents drafted
alongside it in the same batch of PRD #605 child tasks — none of them exist on
`launchpad` as of the check above, regardless of what any individual worktree shows.

**Expected but not verified when this node was written**, per the rule in *Creating a
node* step 3 of `launchpad/docs/corpus/AGENTS.md`:

- **No generator has ever run against this corpus**, so nothing here about
  determinism, do-not-edit markers or no-change reruns has been tested against a real
  one — it is read from `#633` and `#891`'s stated intentions, not observed behavior.
- **Whether ADR-0027's pre-rendered knowledge-crate surfaces are meant to live under
  `launchpad/docs/corpus/` was not established.** If a future decision places them
  there, this document's scope would need to be revisited rather than assumed to
  already cover them.
- **No node anywhere in this corpus currently carries a `relationships` entry of any
  of the four generated-inverse types**, because `node.schema.json`'s enum does not
  offer them as forward types either — this was confirmed by reading the schema, not
  by searching the corpus for an instance, since none would validate if one existed.
