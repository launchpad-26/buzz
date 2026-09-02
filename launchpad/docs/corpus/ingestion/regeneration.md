---
id: ingestion-regeneration
type: ingestion
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "ADR-0028 decides that Markdown files with YAML front matter are the one canonical, authored representation of every corpus node, and that JSON, search indexes, dependency graphs and any knowledge-crate-facing serialization are generated derived views -- never hand-authored, always reproducible from the canonical Markdown."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "ADR-0028's Security implications section states plainly that 'Generated views must not silently drop whatever security-relevant provenance their source node carries,' immediately after stating that provenance and claim classification (FACT/INFERENCE/TEAM KNOWLEDGE) must stay structurally encoded and validator-checkable rather than asserted only in free-form body prose."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The corpus's own evidence standard independently restates the same requirement in its own ledger: 'ADR-0028 requires claim classification to stay structurally encoded and validator-checkable rather than asserted only in free-form body prose, requires that generated views must not silently drop security-relevant provenance their source node carries, and leaves the question of how many claims one node holds open.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "validate.py's find_ownership_violations rejects every non-.md file under the corpus root (schema/ excluded) that does not live inside a generated/ subdirectory, and separately rejects a non-.md file correctly placed inside generated/ too, with a distinct error message, because directory placement proves only where a file sits and no generator exists yet to prove it is actually reproducible from canonical Markdown; that reproducibility contract is owned by #1316 until a generator exists."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The corpus-standard-generated-content node, already merged on origin/launchpad, states as its own MUST 1-4 that a generated artifact must not be hand-authored, that a non-Markdown generated artifact must live under generated/, that placement under generated/ is not proof of reproducibility, and that no non-Markdown generated artifact may be committed under the corpus root today -- generated/ included -- because no generator exists yet for any class of artifact."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/generated-content.md"
  - statement: "corpus-standard-generated-content's own scope-and-omissions table names 'Building the generator itself' as owned by launchpad-26/buzz#633 and does not itself state what a future regeneration run must preserve from, or how it is triggered by, a canonical source node changing -- it governs what generated content is and where it lives, not the regeneration act."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/generated-content.md"
  - statement: "AGENTS.md states that every non-.md file under the corpus root is rejected today, including one placed under generated/, because no generator exists to reproduce it from canonical Markdown, and that this contract is owned by #1316 until it lands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "At repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90, the corpus tree on origin/launchpad contains corpus-agents, corpus-standard-generated-content and corpus-template-policy among its merged nodes, and contains no node anywhere under an ingestion/ path; agents-invariants (id of agents/invariants.md) is the only Feature #620 sibling document merged."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, agents/invariants.md, standards/generated-content.md, standards/provenance.md, templates/policy.md, templates/procedure.md, and every other file listed under standards/ and templates/, with no path matching ingestion/*.md"
  - statement: "That a canonical node's committed change is what must trigger regeneration of any generated view derived from it follows from ADR-0028's requirement that a generated view be 'always reproducible from the canonical Markdown': a view that has not been regenerated since its source's last committed change is no longer the reproduction of current canonical content ADR-0028 requires, whether or not anyone has noticed the drift. No source states this trigger as a rule in those words -- it is this node's own reasoning from ADR-0028's reproducibility requirement, not a restatement of an explicit rule found elsewhere."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
    confidence: 0.8
  - statement: "Feature #620 lists issue #967 among 32 child document tasks under an agents/ and ingestion/ path family, with a stated outcome that 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures,' and Feature #620's own out-of-scope list excludes 'implementation of the knowledge-crate runtime,' recording that no corpus generator currently exists."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body"
  - statement: "Issue #967's own definition of done requires this node to have schema-valid front matter with a stable node ID, type, status, origin, audiences, provenance/evidence and typed relationships appropriate to the node, to represent one independently maintainable knowledge node rather than folding in a second concept, and to be checked against the repository revision recorded in its provenance."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#967 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: depends-on
    target: corpus-standard-generated-content
  - type: implements
    target: corpus-template-policy
---

# Policy: regeneration of generated corpus views

This node states what regenerating a generated derived view from its canonical corpus
source MUST preserve and MUST be triggered by, once a corpus generator exists, and what
MUST NOT happen with generated content in the meantime. **No corpus generator exists
today** (`#1316`/`#633` own building one) -- this is forward-looking policy for a
capability not yet built, grounded in invariants `ADR-0028` already decided, not a
description of a generator that runs. Where this node's subject overlaps
`corpus-standard-generated-content` -- what "generated" means and where it may live --
that node is authoritative and this one links to it rather than restating it.

## Scope and authority

**This node governs** the regeneration act itself: what a regenerated generated view
must be reproduced from and must preserve, what change must trigger a fresh
regeneration, and what an author or agent must not do about generated content while no
generator exists to perform that act. **It does not govern** what counts as generated
content, where a non-Markdown artifact must live, or the interim placement-rejection
rule -- `corpus-standard-generated-content` already covers all three, and this node
depends on it rather than duplicating it (see the relationship declared below). It also
does not govern building the generator itself (`#633`), the concrete per-document
generator tasks (the `generate corpus document generated/*.md` and `specifications/*.md`
families), or the general evidence/provenance ledger mechanics
(`corpus-standard-evidence`, `corpus-standard-provenance`).

**Its authority is derived, not original.** `ADR-0028` already decided that a generated
view must always be reproducible from canonical Markdown and must not silently drop
security-relevant provenance its source node carries; this node states what following
those two requirements means specifically for the *act of regenerating*, the half no ADR
text spells out as an operational rule. **Where this node and `ADR-0028`,
`node.schema.json`, `validate.py`, or `corpus-standard-generated-content` disagree, they
win** -- this node has drifted and should be fixed.

| For | Read |
|---|---|
| Why Markdown + front matter is canonical, and the provenance-non-drop requirement this node builds on | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| What "generated" means, where a non-Markdown artifact must live, and today's interim placement rule | `launchpad/docs/corpus/standards/generated-content.md` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The evidence ledger's classes and what a citation establishes | `launchpad/docs/corpus/standards/evidence.md` |
| How a node's checked revision is recorded | `launchpad/docs/corpus/standards/provenance.md` |
| Building the generator itself | `launchpad-26/buzz#633`, tracked under `#1316` |
| The general policy-node shape this document instantiates | `launchpad/docs/corpus/templates/policy.md` |

## MUST

| # | Requirement |
|---|---|
| **R1** | Once a corpus generator exists, regenerating a generated derived view MUST reproduce it from the current canonical Markdown of every node it derives from, replacing the artifact wholesale rather than patching it incrementally. This is `ADR-0028`'s reproducibility requirement stated as a rule for the regeneration act; enforced by nobody today, because no generator exists to run it against. |
| **R2** | Regeneration MUST NOT silently drop any security-relevant provenance a source node's evidence ledger carries into its generated view -- an entry's `entry_class` (`FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`), its citations, and its `confidence` or `provided_by` fields where present. Dropping the classification while keeping the prose is exactly the failure `ADR-0028`'s Security implications section names. Enforced by nobody today; there is no generated view to inspect. |
| **R3** | Regeneration of a generated view MUST be triggered whenever any canonical node it derives from is created, updated, or retired. A view that has not been regenerated since its source's last committed change has stopped being the reproduction of current canonical content `ADR-0028` requires, whether or not the drift has been noticed. Enforced by nobody today -- stated here as this node's own reasoning (see the `INFERENCE` entry in the ledger), for a future generator to be built against. |
| **R4** | Until the generator required by `#1316`/`#633` exists, nobody MUST hand-author a file that a future generator would own -- including placing a hand-written file inside `generated/` to make it resemble a real projection. This is real, checkable behavior **today**: `validate.py`'s `find_ownership_violations` rejects both a stray non-`.md` file outside `generated/` and one correctly placed inside it, with a distinct message for each, and both are hard errors. The underlying placement and ownership rules are `corpus-standard-generated-content`'s MUST 1-6; this node states the regeneration-specific consequence -- don't hand-produce what regeneration will one day own -- and does not restate those rules. |

## SHOULD

| # | Guidance |
|---|---|
| **Q1** | An author who commits a change to a canonical node that already has a generated view derived from it SHOULD note in the pull request that the view is now stale, since no generator exists yet (`#1316`) to regenerate it automatically and nothing else will surface the staleness. |
| **Q2** | Once a generator exists, running it and committing its output SHOULD happen in the same pull request as the canonical change that triggered regeneration under R3, rather than a later one, so a generated view is never observably stale on `launchpad` between the two. |

## Enforcement

**Nothing enforces R1-R3 today**, mechanically or by review, because there is no
generator and no generated view derived from a canonical node to check either
requirement against. `corpus-standard-generated-content` records directly that "no
generator has ever run against this corpus," and that remains true at this node's
recorded revision. R1-R3 exist to be enforced against the generator `#633`/`#1316`
eventually build, not against anything running today.

**R4 is enforced mechanically today**, by `validate.py`'s `find_ownership_violations`,
run locally by `just corpus-validate` and in CI on every pull request and push to
`launchpad` touching the corpus. Both failure modes it names -- a stray non-`.md` file
outside `generated/`, and one correctly placed inside it -- are hard errors, not the
non-fatal `UNVERIFIED` channel.

**What a green `validate.py` run does NOT establish about this node's subject:** that
any generated view exists, that one reflects current canonical content, that
regeneration preserved provenance, or that regeneration was triggered by the right
change. There is nothing yet for the validator to check any of that against -- a passing
run today says only that no forbidden non-Markdown artifact was committed, which is R4's
concern, not R1-R3's.

## Exceptions and escalation

**There is no exception process for R4**, and this node does not create one. This
mirrors `corpus-standard-generated-content`'s own stated position: the validator fails
closed for every non-Markdown artifact regardless of placement, with no flag,
environment variable, or marker-file mechanism to except a specific one. The only route
past it is building the generator and proving reproducibility, which is tracked work
(`#633`, `#1316`), not a decision this document can grant on request.

**R1-R3 have no exception process to state yet**, because nothing implements them to
depart from. Once a generator exists, a case where regeneration cannot meet one of them
is escalated as an issue against whichever feature ships the generator, not resolved by
quietly relaxing this node.

**A case this node does not cover is escalated, not invented.** Raise it as an issue
against parent Feature #620, or against `#1316`/`#633` if it concerns the generator's
own design, describing what was needed and why this node did not reach it.

## Scope and omissions

**This node covers** what regenerating a generated derived view must preserve and be
triggered by once a corpus generator exists (`ADR-0028`'s reproducibility and
provenance-non-drop requirements, applied to the regeneration act specifically), and
what must not happen with generated content in the meantime, honestly stated as policy
for a capability that does not yet exist.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What "generated" means, where a non-Markdown artifact must live, and today's interim placement/ownership rule | `launchpad/docs/corpus/standards/generated-content.md` |
| Building the corpus generator itself | `launchpad-26/buzz#633`, tracked under `#1316` |
| The concrete per-document generator tasks (`generate corpus document generated/*.md`, `specifications/*.md`, and similar families) | the individual tasks in those families |
| The evidence ledger's classes, what a citation establishes, and how conflicting evidence is ranked | `launchpad/docs/corpus/standards/evidence.md`, `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| How a node's checked revision is recorded in its own ledger | `launchpad/docs/corpus/standards/provenance.md` |
| The human-facing entry point to the corpus | `#639` |
| Concrete agent procedures for navigation, ambiguity handling, and the rest of Feature #620's sibling task family | the other `agents/*.md` and `ingestion/*.md` tasks under #620, none merged at this node's authoring time |

**No corpus generator exists as of this node's authoring.** Every MUST above that
concerns the regeneration act (R1-R3) states policy for a capability `#1316` and `#633`
have not yet built, grounded in `ADR-0028`'s already-decided invariants rather than in
any observed generator behavior. Only R4 describes something checkable today.

**This node's own relationships.** Declared: `depends-on corpus-agents` -- real and
resolvable on `origin/launchpad`, the same baseline-authority dependency every sibling in
this batch declares toward `AGENTS.md`. Declared: `depends-on
corpus-standard-generated-content` -- real and resolvable; R4 rests entirely on that
node's already-established MUST 1-6 rather than re-deriving them, so this node's own
claim would not hold if that one changed underneath it. Declared: `implements
corpus-template-policy` -- real and resolvable; this node follows that template's six
required sections in order, the same edge `agents-invariants` declares toward the same
target for the same reason. Checked against `origin/launchpad` immediately before
finalizing this front matter (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`), not from memory: no other Feature #620 sibling task is merged,
so none is declared as a target, and no relationship points at `corpus-standard-evidence`
or `corpus-standard-provenance` because this node's claims do not depend on either
holding true for R1-R4 to stand -- both are named only in the "for X read Y" table and
the omissions table above.

**Expected but not verified when this node was written:**

- **No regeneration has ever run**, against this corpus or any other. Every MUST above
  concerning the regeneration act (R1-R3) is reasoned from `ADR-0028`'s text, not
  observed from a working generator -- there is nothing yet to observe.
- **Whether `#633`'s eventual generator design will find R1-R4 sufficient, or will need
  additional invariants this node did not anticipate**, is unknown. This node states
  what is already decided (`ADR-0028`) and one reasoned trigger rule; it does not predict
  the generator's implementation.
- **Whether R3's "created, updated, or retired" trigger list is complete** was not
  checked against every way a canonical node's committed state can change -- for
  example, whether a change to `relationships` alone (with no change to a node's
  claim-bearing prose) should trigger regeneration of a view that only reflects prose is
  not addressed here.
