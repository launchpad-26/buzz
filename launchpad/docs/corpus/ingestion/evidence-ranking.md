---
id: corpus-ingestion-evidence-ranking
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
  - statement: "ADR-0029 ranks evidence contextually by claim type -- executable evidence (code, config, schema, passing tests) is authoritative for claims about current behavior, accepted normative decisions are authoritative for claims about intended or authorized behavior -- and requires that two authoritative sources of the *same* claim type which contradict each other be escalated (left unestablished/flagged) rather than resolved by the corpus author."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "corpus-standard-evidence's own Scope and authority section states that it governs the ledger, naming 'how conflicting evidence is ranked' explicitly among the subjects it treats, and calls itself 'the canonical treatment of those subjects for the corpus.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "corpus-standard-evidence's SHOULD 2 states 'Cite the narrowest source that actually supports the claim, and only that. A second citation added \"for context\" is a second thing that can rot, and the checker will never tell you which one did' -- one line of guidance, carrying no MUST, no worked test, and no statement of when candidates should instead be split rather than narrowed."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "corpus-standard-evidence's SHOULD 4 states 'Split a compound claim into separate entries. If one half rests on code and the other on a conversation, one entry cannot be classified honestly and the class you pick will misdescribe half of it.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "corpus-standard-evidence's 'Class is not a ranking' section states that entry_class records how a claim came to be known, not how strongly it is held, and that reaching for FACT because it sounds stronger is a mislabelling its own MUST 2 forbids -- a rule about honest classification, not about how many same-class citations one entry should carry."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "node.schema.json requires exactly id, type, status, origin, audiences and evidence, permits relationships as the only other property, and rejects any additional field (additionalProperties: false); its type enum includes ingestion as one of thirteen members, naming the corpus surface a node documents rather than its normative shape."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "corpus-template-policy requires a policy-shaped node to carry six sections in this relative order -- Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and omissions -- with additional sections permitted between them but none of the six absent, reordered among themselves, or silently empty."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/policy.md"
  - statement: "At the recorded revision, git ls-tree of origin/launchpad's corpus root contains no ingestion/ directory and no node for any of Feature #620's other 31 sibling tasks; corpus-agents (AGENTS.md), corpus-standard-evidence (standards/evidence.md), and corpus-template-policy (templates/policy.md) are all present and validated, and corpus-standard-atomicity, corpus-standard-provenance and corpus-standard-confidence are present but govern different questions (one-node-vs-many, the recorded-revision entry, and the confidence number, respectively -- none of the three claims the redundancy-narrowing question this node states)."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, agents/invariants.md, architecture/**, capabilities/**, development/**, layers/**, schema/**, standards/atomicity.md, standards/code-references.md, standards/confidence.md, standards/decision-references.md, standards/deprecation.md, standards/diagrams.md, standards/documentation-standard.md, standards/evidence.md, standards/front-matter.md, standards/generated-content.md, standards/identifiers.md, standards/linking.md, standards/naming.md, standards/normative-language.md, standards/provenance.md, standards/review-requirements.md, standards/status.md, standards/taxonomy.md, standards/test-references.md, templates/**, no ingestion/ directory -- at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "standards/atomicity.md's Scope and authority states it 'governs one question: given a subject you are about to document, is it one node or more than one?' -- a granularity question distinct from ranking or narrowing citations within one already-chosen claim."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/atomicity.md"
  - statement: "standards/provenance.md's Scope and authority states it governs 'the evidence entry that records the repository revision a corpus node was authored and checked against,' settling when that one entry may be moved and what happens to the rest of the ledger on partial re-verification -- not the general ranking or narrowing of a node's other evidence entries."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
  - statement: "AGENTS.md's step 9 for creating a node requires relationship targets to be checked against the branch being merged INTO (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus), not the author's own worktree, because a target that resolves locally can be a hard validation error once merged if that target does not yet exist on origin/launchpad."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "standards/naming.md's MUST 3 requires a document's id to be recognizable on sight as its filename: strip .md, lowercase the stem, prefix corpus-, and for a document one level below the corpus root in a purpose-named subdirectory, insert that subdirectory's singular form before the stem -- binding every corpus document created from that standard's merge onward."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
  - statement: "agents/invariants.md, a merged policy-shaped node, declares relationships depends-on: corpus-agents and implements: corpus-template-policy, reasoning that the first names where its own authority is derived from and the second names the general template it instantiates -- the same relationship shape this node adopts toward corpus-agents, corpus-standard-evidence and corpus-template-policy."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "Neither ADR-0029 nor corpus-standard-evidence states a procedure for the specific case where an ingesting agent already holds multiple candidate sources of the identical entry_class, all genuinely supporting one identical statement with no disagreement among them, and must decide how many of those candidates to actually write into the ledger. ADR-0029's ranking operates across claim types and its escalation clause is triggered only by contradiction between same-type authorities; corpus-standard-evidence's only statement on this exact case is its single SHOULD 2 line, which carries no MUST, no test for when narrowing is honest, and no statement of the boundary against splitting (SHOULD 4)."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "launchpad/docs/corpus/standards/evidence.md"
    confidence: 0.85
  - statement: "Issue #959's own Objective section states this node's target file is created 'as the single canonical policy node for evidence ranking,' language that -- read against corpus-standard-evidence's own 'canonical treatment' claim over the same general subject -- would put two governance-shaped nodes claiming the same canonical authority; this node resolves that tension by explicitly narrowing its own claimed authority rather than asserting the issue's literal phrase."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#959, Objective section"
  - statement: "Issue #959's definition of done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them -- the same four-clause shape corpus-template-policy's own Definition of Done history and agents/invariants.md both already satisfy."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#959 definition of done"
  - statement: "Issue #958 ('task: document ingestion/evidence-conflicts.md') is a sibling task under the same parent Feature #620 and is not merged at this node's authoring time, so it is not a valid relationships target; this node's title alone (not its content, which is unread by design during this batch run) is the basis for stating the conflicts/ranking boundary below."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 child task list; launchpad-26/buzz#958 title"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: depends-on
    target: corpus-standard-evidence
  - type: implements
    target: corpus-template-policy
---

# Policy: narrowing redundant same-class evidence during ingestion

This node states the binding rule for one narrow ingestion-time case: an agent building a
corpus node's provenance ledger has found **more than one candidate source of the identical
`entry_class`, each genuinely supporting one identical claim, with no disagreement between
them** -- and must decide how many of those candidates actually belong in the ledger. It does
not restate how a claim is classified, how conflicting evidence across claim types is ranked,
or what happens when candidates disagree; those are settled elsewhere and cited, not repeated.

## Scope and authority

**This node governs** the narrowing decision an ingesting agent makes when multiple
same-`entry_class` candidate sources converge on one identical statement with no contradiction
among them: how many of those candidates to write into the `evidence` ledger, and the test for
whether a candidate may honestly be dropped. It does not govern classification (which
`entry_class` a claim takes), ranking across claim types, or what happens when candidates
disagree -- see *Boundary* below for exactly where each of those already lives.

**Its authority is derived, not original**, in the same sense every corpus standard already
describes for itself. `ADR-0029` is the accepted decision on evidence precedence; `corpus-
standard-evidence` is the canonical standard on the ledger, on classification, and on ranking
generally, including the one line (SHOULD 2) this node expands into an ingestion-time
procedure. This node adds only the half neither states: a MUST-level test for the specific
redundancy case, and the boundary that keeps it from silently duplicating either source. Where
this node and `ADR-0029` or `corpus-standard-evidence` disagree, they win -- this one has
drifted and should be fixed.

**On issue #959's own Objective text.** The task that produced this node describes it as "the
single canonical policy node for evidence ranking." Read literally, that would put this node in
direct conflict with `corpus-standard-evidence`, which already states in its own Scope and
authority that it is "the canonical treatment" of, among other things, "how conflicting evidence
is ranked." This node does not assert the issue's literal phrase. It claims canonical authority
over one narrow question -- redundancy narrowing among same-class, non-contradictory candidates
-- and explicitly defers general ranking, classification, and cross-claim-type precedence to
the two sources named above. A reader who came here expecting a restatement of `ADR-0029` or of
`corpus-standard-evidence` in full will not find one; that is deliberate, per `AGENTS.md`'s own
one-idea-per-node rule and per the duplication risk this task was drafted under.

**Where the rules below come from.** Issue #959's definition of done asks this node to state
scope and authority, separate MUST from SHOULD, and define enforcement and an exception
process. The MUST and SHOULD statements below are this document's own normative statements
issued under that delegated authority, not findings derived from a cited source.

| For | Read |
|---|---|
| How conflicting evidence is ranked across claim types, and when to escalate | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| The ledger's structure, the three `entry_class` values and what each is for, citation forms and what validation establishes | `launchpad/docs/corpus/standards/evidence.md` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The general policy-shape this node instantiates | `launchpad/docs/corpus/templates/policy.md` |
| Whether a subject is one node or more | `launchpad/docs/corpus/standards/atomicity.md` |
| The recorded-revision entry specifically | `launchpad/docs/corpus/standards/provenance.md` |
| An `INFERENCE`'s `confidence` number | `launchpad/docs/corpus/standards/confidence.md` |

## MUST

1. **When two or more candidate sources share the identical `entry_class` and each genuinely
   supports the identical statement, with no disagreement among them, the author MUST narrow
   the ledger entry to the fewest of those candidates that still let an independent reader
   verify the statement.** The test: for each candidate, would removing it change what the
   statement can honestly claim to have checked? If not, it MUST NOT be added merely because it
   was touched during ingestion. An uncurated dump of every source scanned is not a ledger; it
   is ingestion notes that were never narrowed.
2. **This narrowing procedure MUST NOT be applied when candidates disagree, even partially.**
   Any disagreement between two authoritative sources is `ADR-0029`'s territory, not this
   node's: record the disagreement and follow `ADR-0029`'s escalation rule (`status: flagged`
   when it is material) rather than silently keeping the candidate that "wins."
3. **Narrowing MUST NOT cross an `entry_class` boundary.** If candidate sources of different
   character exist for one statement (a source you opened directly and a source that only told
   the corpus something), that is a classification question -- `corpus-standard-evidence`'s
   three-class test decides which class the entry takes -- and this node's procedure applies
   only after that question is already settled, within the one class chosen.
4. **When candidates support only overlapping topics rather than the identical statement, the
   author MUST split them into separate entries** per `corpus-standard-evidence`'s SHOULD 4,
   rather than force a single narrowed entry across two claims. Narrowing removes redundant
   *proof of the same claim*; it must never be used to merge two different claims into one
   citation list.
5. **Dropping a redundant candidate MUST NOT be recorded in the ledger itself.** The schema
   defines no field for a discarded citation, and inventing one anywhere in the entry violates
   `node.schema.json`'s closed shape. Where the decision needs a record for a reviewer, it goes
   in the pull request, not the node.

## SHOULD

1. **When more than one candidate survives MUST 1's cut, prefer the candidate with the
   narrowest scope** -- a specific symbol or line over a whole file, a whole file over a
   directory-level description -- as the tiebreak `corpus-standard-evidence`'s SHOULD 2 states
   in general and this node applies concretely to the redundancy case.
2. **An author SHOULD note, in the pull request rather than the ledger, which candidates were
   found and dropped as redundant**, so a reviewer checking `FACT` classification against the
   cited source can also see what else was considered without re-deriving the ingestion scan.
3. **An author SHOULD re-run this narrowing check when a new same-class candidate for an
   already-written claim turns up before merge**, rather than leaving the ledger keyed to
   whatever the scan first found.

## Enforcement

**Nothing here is mechanically enforced.** `validate.py` discards a node's body before any
check runs and never counts how many citations one `evidence` entry carries, so a ledger entry
listing five redundant `FACT` citations for one claim passes identically to one listing the
single narrowest citation MUST 1 asks for. The same is true of MUST 2 through MUST 4: none of
"do these candidates actually agree," "is this truly one class," or "is this truly one claim"
is checkable by a schema that never opens a cited file or compares two citations against each
other. All five MUSTs and all three SHOULDs are held by a reviewer reading the ledger against
the sources it cites, the same enforcement model `corpus-standard-evidence` and `corpus-
template-policy` both already describe for their own review-only halves.

Run `python3 launchpad/project-intelligence/corpus/validate.py` (or `just corpus-validate` with
Hermit activated) for the structural half this node does not add to: schema shape, citation
form recognition, and relationship-target resolution. Exit 0 says nothing about whether this
node's own narrowing rules were followed.

## Exceptions and escalation

**There is no exception process for MUST 1 through MUST 5.** They describe when a citation is
honestly redundant, not a cost that can be waived; a ledger entry that cannot meet them has not
finished being narrowed, not found an acceptable shortcut.

**A disagreement between candidates is never handled here.** The moment two sources touching
one statement say different things, this node's procedure stops applying and `ADR-0029`'s
ranking-and-escalation rule takes over. Do not attempt to force a disagreement through MUST 1's
narrowing test by discarding the inconvenient candidate -- that is exactly the "resolved by
whichever agent happens to author the node" outcome `ADR-0029` rejects.

**A case this node does not reach** -- for example, whether a given pair of statements counts
as "identical" or merely "overlapping" under MUST 4 -- is a reviewer judgement call recorded in
the pull request. A repeated disagreement on that judgement is filed as an issue against this
node's parent, Feature #620, rather than settled ad hoc a second time.

## Scope and omissions

**This document covers** the narrowing test for multiple same-`entry_class`, non-contradictory
candidate sources supporting one identical claim during ingestion, the boundary that keeps that
test from being used to paper over an actual disagreement, and the review-only enforcement
model that follows from `validate.py` never comparing citations against each other.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Ranking evidence across claim types (current-behavior vs. intended/authorized), and escalation when two same-type authorities genuinely contradict | `ADR-0029` |
| The ledger's structure, the three `entry_class` values and what each is for, citation forms, and what a passing validation run does and does not establish | `corpus-standard-evidence` |
| What to do once sources are recognized as actively disagreeing, beyond `ADR-0029`'s escalation rule itself | issue #958 (`ingestion/evidence-conflicts.md`), not merged at this node's authoring time |
| What an `INFERENCE`'s `confidence` value means and how to choose one | `corpus-standard-confidence` |
| The citation forms that name code specifically | `corpus-standard-code-references` |
| Whether a subject is one node or several | `corpus-standard-atomicity` |
| The recorded-revision entry itself, and whether it may stay put across an edit | `corpus-standard-provenance` |

**No relationship to issue #958's node.** `ingestion/evidence-conflicts.md` is not merged at
this node's authoring time, so no `corpus-ingestion-evidence-conflicts` id exists to target;
declaring one would validate on this branch and hard-error once merged, the exact trap
`AGENTS.md` step 9 names. The boundary above is stated in prose, pointing at #958 by issue
number, and the machine-readable edge is a follow-up once that node lands.

**Expected but not verified when this node was written:**

- **Issue #958's actual content was not read**, by this task's own instruction, so the boundary
  stated above rests on its title and on Feature #620's child-task list, not on its drafted
  text. If #958 lands describing something other than conflict-handling, this node's boundary
  section needs re-checking against what actually merged.
- **No case has yet arisen in a real, merged corpus node** where this narrowing procedure was
  applied and reviewed. The MUST/SHOULD statements above are drawn from reading `ADR-0029` and
  `corpus-standard-evidence` in full and finding the gap between them, not from observing an
  author hit the gap in practice.
