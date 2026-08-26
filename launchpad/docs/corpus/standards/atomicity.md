---
id: corpus-standard-atomicity
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 60d4947b7145a6ef25f185b9c25d43e43d99de3c."
    entry_class: FACT
    evidence:
      - "commit 60d4947b7145a6ef25f185b9c25d43e43d99de3c"
  - statement: "The corpus instruction node states the atomicity rule in one line -- one node is one independently maintainable idea -- and refers the full treatment to the per-type standards it does not itself carry."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "One authored Markdown file with YAML front matter is one corpus node, so deciding how many nodes a subject becomes is deciding how many files it becomes."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Naming, identifiers, linking, provenance, status, taxonomy, diagrams and evidence each have their own standard task, distinct from this one."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The sibling standard tasks this node names carry these subjects: 1313 documentation standard, 1314 evidence, 1316 generated content, 1317 identifiers, 1318 linking, 1319 naming, 1320 normative language, 1322 review requirements, 1324 taxonomy."
    entry_class: FACT
    evidence:
      - "gh_issue_list(repo='launchpad-26/buzz', search='corpus standard in:title') -> titles read for issues 1307 through 1325, all open"
  - statement: "A second concept, contract or procedure discovered while drafting is filed as a separate task rather than folded into the document being written."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1307 definition of done: 'any newly discovered second concept/contract/procedure is filed as a separate task instead of being folded into this document'"
  - statement: "A node's id is assigned once and never renamed, because generated projections derive from it reproducibly."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "type, status and origin each hold exactly one string value per node, whereas audiences is an array that may hold several."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A subject that would need two simultaneous values of a single-valued front-matter field cannot be described accurately by one node, because the node must then assert one of the two values of content it does not hold."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
    confidence: 0.9
  - statement: "AGENTS.md states that a node carries one recorded revision for its whole ledger and that moving it asserts every claim was checked at that revision, and records this as that document's own working practice rather than a corpus-wide rule, because whether a recorded revision may stay put while a node is edited is #1321's to decide and is unlanded."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Two halves of a node whose claims go stale on different schedules force every update to choose between re-verifying claims that did not need it and moving a snapshot that does not cover them."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.8
  - statement: "A relationship's target is another node's id, so every typed edge attaches to a whole node and there is no way to point at part of one."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The checker confirms only that a relationship target matches some loaded node's id; it never establishes that the target still covers the subject the edge was drawn for."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Retiring a node is a status change that keeps the file, so inbound edges keep resolving and the replacement node declares supersedes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "The corpus create procedure requires a node's body to state what it does not cover, and the instruction node names an owner for each gap it declares."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The checker never reads a node's body prose, so a copy of content held there goes stale without any run reporting it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Deciding node count by document length tracks prose volume rather than subject boundaries, so it cannot produce the one-idea-per-node property that defines a node."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.85
  - statement: "The create procedure names two contracts, and a concept together with the procedure that uses it, as cases that are two nodes rather than one."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "flagged names an unresolved contradiction between two authoritative sources of the same claim type awaiting a human, not a general low-confidence marker."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "part-of declares that the source is a constituent section or child of the target, and like every relationship type its target is another node's id."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "For claims about how the system currently behaves, executable evidence is authoritative over documentation, so a corpus node restating a volatile implementation detail adds a copy that can only fall behind its own source."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.7
  - statement: "The deterministic checker validates front matter against the schema and checks duplicate ids, relationship targets, citation forms, non-canonical files and non-Markdown files, and none of those checks concerns how many ideas a node holds."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Changes under the corpus root run that checker in CI on pull requests."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "The corpus is authored as Markdown specifically so it stays reviewable as a human-read pull-request diff, which ADR-0028 names as the enforcement mechanism the rest of Ruling 12 depends on."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The instruction node already names one convention no check enforces -- a ledger carrying more than one commit-only FACT -- and states that a reviewer has to hold it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "At the revision recorded in this ledger the corpus holds exactly one node besides this one, whose id is corpus-agents, so that id is available as a relationship target."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The standards set is receiving its typed edges in a single follow-up pass once the sibling nodes have landed, rather than each node declaring edges as it is written."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "the feature #605 task brief for the corpus standard documents: 'Edges get added in a follow-up once the set has landed.'"
  - statement: "Correcting an over-merged node later fails silently while correcting an over-split one fails visibly, so a call the tests leave balanced should resolve toward two nodes."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.7
---

# Atomicity

How many corpus nodes a subject becomes, and how an author decides.

## Scope and authority

**This standard governs one question:** given a subject you are about to document,
is it one node or more than one?

That question is worth a standard because the answer is not recoverable later. A
subject wrongly split stays split behind edges that resolve; a subject wrongly merged
stays merged behind an `id` that cannot be renamed. Neither state is detectable by any
check, so the decision is made once, by an author, at the moment of drafting.

**Where the authority comes from.** `launchpad/docs/corpus/AGENTS.md` is the
instruction node for corpus work and states the rule in a line: one node is one
independently maintainable idea. It does not say how to apply it, and refers per-type
standards, including this one, to their own tasks. This node is that treatment. Where
the two disagree, the instruction node is the one an agent is handed, so a
disagreement is a defect in this document and should be fixed here.

**Why "one node" and "one file" are the same question.** ADR-0028 makes Markdown with
YAML front matter the single canonical authored representation of a node, with every
other serialization generated from it. There is no sub-node unit to author into, so
granularity decisions land on file boundaries and nowhere else.

**What this standard does not decide.** Each of these is its own task, and folding one
in here would break the very rule this node states:

| Not decided here | Owned by |
|---|---|
| Which `type` a node takes, and what the surfaces mean | #1324, taxonomy |
| What an `id` looks like and how it is chosen | #1317, identifiers |
| What a node or its file is called | #1319, naming |
| How a node points at another, and in which direction | #1318, linking |
| What MUST, SHOULD and MAY mean as normative keywords | #1320, normative language |
| Whether a node needs a scope section at all, and what belongs in it | #1313, documentation standard |
| How evidence is classified and cited | #1314, evidence |

This node uses MUST and SHOULD in the ordinary normative sense and links #1320 rather
than defining them.

## Requirements

### MUST

| | Requirement |
|---|---|
| **A1** | A corpus node MUST document exactly one independently maintainable idea. |
| **A2** | A subject that would require two simultaneous values of `type`, `status` or `origin` MUST be authored as two or more nodes. |
| **A3** | A second concept, contract or procedure discovered while drafting MUST be filed as its own task, and MUST NOT be folded into the node in progress. |
| **A4** | A node that split its subject MUST record what it declined and where that went — the sibling node's `id` if one exists, otherwise the task that owns it. |
| **A5** | A node MUST NOT be split solely to shorten it, and MUST NOT be merged solely to reduce the number of files. |

**A2 is the only requirement here a machine could hold**, and nothing holds it — see
*Enforcement*. It is a MUST rather than a SHOULD because the merged state is not
merely untidy: the front matter would have to assert one of two values as though it
covered content it does not.

**A4 is what makes a split legible.** A subject that quietly became two nodes, with
neither saying so, reads to the next author as two subjects that were never related —
and they will not know to look for the other half.

### SHOULD

| | Guidance |
|---|---|
| **B1** | Apply the tests below in order, and stop at the first decisive answer. |
| **B2** | Where the tests leave the call genuinely balanced, choose two nodes. |
| **B3** | File the second task at the moment the second concept surfaces, not at the end of the draft. |
| **B4** | Link the node or task that owns an adjacent subject rather than summarising it. |
| **B5** | Where a subject seems to resist the tests, record the tension in the node and name it in the pull request rather than deciding it silently. |

**B2 is not a preference for small nodes.** It follows from the two mistakes having
different repair costs, which *The asymmetry* below sets out. A5 still holds: prefer
two nodes when the call is *balanced*, never merely when the document is long.

**Which of these rows are claims, and which are editorial.** A1–A5, B2 and B4 assert
something about how this corpus behaves, and each has an entry in this node's ledger.
B1, B3 and B5 do not: they are this document's own procedure for using itself — the
order to apply the tests in, when to file, and what to do when you disagree. They are
grounded in nothing but the design of this node, which is what they should be grounded
in, and inventing a citation for them would be exactly the move this corpus's evidence
rules exist to prevent.

## The decision procedure

Five tests, in order. Test 2 is decisive on its own; tests 3 and 4 are strong; test 1
is a cheap screen that catches most cases before the others are needed; test 5 argues
the other way and exists to stop the procedure running away.

### 1. State it in one sentence

Write the subject as a single sentence in which no conjunction joins two nouns. If the
sentence needs an *and* or an *or* to be true, you are holding two subjects.

This proves nothing — a sentence can always be rewritten — but it is free, and an
author who cannot say what the node is about without a conjunction usually already
knows why.

### 2. The single-value test

`type`, `status` and `origin` each carry exactly one value per node. (`audiences` is an
array and carries several; the difference is in `node.schema.json`.) Ask whether this
subject would ever need two of one of them at the same time. The rows below are
illustrations, not a list of the values each field admits — that list is in
`node.schema.json`, and a copy of it here would drift:

| The subject | The field it splits | Why one node cannot hold it |
|---|---|---|
| Half describes upstream Buzz behaviour, half a Launchpad-only convention | `origin` | The node would claim one provenance for content with two |
| Half is settled policy, half is a proposal not yet accepted | `status` | `active` would lend the proposal authority it does not have; `draft` would withdraw it from the settled half |
| Half documents an events surface, half the operational procedure for running it | `type` | Whichever value is chosen misfiles the other half for every reader and every generated view that groups by type |

**If any row applies, the answer is two nodes and the procedure stops.** No amount of
careful prose in the body repairs a front-matter field that is wrong about half its
own document.

### 3. The maintenance-clock test

A node carries one recorded revision for its whole ledger, and on `AGENTS.md`'s working
practice, moving it asserts that the node's claims were checked at that revision — all of
them, not the edited ones.

**That premise is working practice, not settled policy.** `AGENTS.md` says so itself:
whether a recorded revision may stay put while a node is edited, and what an author owes
when only some claims are re-verified, is **#1321's** to decide and has not landed. This
test therefore rests on the strictest reading currently in force, and defers to #1321 when
it lands.

Ask: is there an ordinary change to this repository that would obsolete half this
node's claims and leave the other half untouched? Not a contrived one — the normal
case.

If there is, the halves are on different maintenance clocks, and every future update
faces a choice with no correct answer: re-verify claims that did not need it, or move a
snapshot that does not cover what it now spans. That is precisely what
*independently maintainable* means, and it is the test that does the most work.

**If #1321 settles that a revision may stay put across a partial edit, the dilemma
softens but the test survives** — two halves on different clocks still force a choice
about what the recorded revision covers. The test is worth running either way; only its
sharpness depends on the ruling.

### 4. The edge test

A relationship's `target` is another node's `id`. Every typed edge therefore attaches
to a whole node; there is no syntax for pointing at part of one.

Ask: can you name a plausible future node that would want to depend on, supersede or
implement **half** of this one? If you can, that half is a node.

The cost of getting this wrong is concrete. `supersedes` declares that the source
replaces the target and the target becomes historical — so superseding a merged node
retires content that is still current, while declining to supersede it leaves a
replaced claim live and resolving.

### 5. The standalone test

The first four tests all push toward more nodes. This one pushes back, and it runs
last so that it can veto them.

Ask: can each candidate node's body state its own claim without inlining the other's
content? If a reader must have the neighbour open for this node to mean anything, you
have divided one idea rather than separated two.

A node whose body is a pointer to another node is not atomic; it is a fragment. Length
is not the measure in either direction — a long node covering one idea passes, a short
node covering two fails.

## The asymmetry

The two ways to get this wrong do not cost the same, which is why B2 breaks ties
toward two nodes.

**Over-merging fails silently.** Splitting a node later moves half its content to a new
`id`. Every inbound edge that meant the departed half still resolves, because the
checker confirms only that a target matches some loaded node's `id` — never that the
target still covers what the edge was drawn for. The edges now point somewhere wrong
and no run will ever say so.

**Over-splitting fails visibly.** Merging two nodes later retires one by status change.
The file stays, so inbound edges keep resolving; the retired node's body says what
replaced it; the survivor declares `supersedes`. A reader arriving on an old edge is
told where to go.

Neither repair is free — an `id` is spent permanently either way, because it is
assigned once and never renamed. But one repair leaves a trail and the other leaves a
silence, and a silence is what nobody finds.

## Which test wins

The tests disagree often enough that the precedence has to be stated, or every
boundary case below becomes an argument.

- **Test 2 is decisive and cannot be vetoed.** The schema cannot express the merged
  state, so no reading of the other tests rescues it.
- **Test 5 vetoes tests 1, 3 and 4.** If neither half can stand alone, they are not two
  nodes — whatever the other tests say.
- **A test 5 veto means "not two nodes". It does not mean "one node".** The third
  possibility is that the content does not belong in the corpus at all, and case C
  below is where that lands.
- **Test 1 never overrides anything.** A sentence can always be rewritten. It is a
  screen, not a verdict.

## Boundary cases

Six calls the procedure does not make by itself. Each resolves one way.

### A. A concept and the procedure that uses it — **two nodes**

The create procedure names this pair outright, alongside two contracts, as a case that
is two nodes.

Test 3 says why: a procedure changes when the tooling it drives changes, and a concept
changes when the design changes. Those are different clocks in the ordinary case, not
by coincidence.

### B. A rule and its exception — **one node**

An exception condition is not a second idea. It is part of the rule's own boundary, it
is written in the rule's terms, and it goes stale exactly when the rule does — test 3
finds one clock. Test 5 agrees: an exception node whose body is "except when X, see the
rule" cannot state a claim standing alone.

**The line is between a condition and a procedure.** "This does not apply to generated
files" is a condition and stays. An escalation *process* — who is asked, in what order,
with what outcome — is a procedure, and case A applies to it.

### C. A stable concept and a volatile detail — **two nodes, or neither**

Here test 3 fires alone: the concept is steady and the detail moves whenever the code
moves. Test 1 says one, because the subject states cleanly in a single sentence.

Test 1 never overrides anything, so it does not settle this. Test 5 does, and it
decides between the two outcomes still live. **If the detail can stand as its own node,
the answer is two nodes. If it cannot, the answer is not to merge it back — it is that
the detail probably does not belong in the corpus.** For
claims about current behaviour the executable source is authoritative anyway, so a node
restating it adds a copy that can only fall behind, and nothing in the corpus will
report that it has.

### D. A flagged claim beside settled ones — **two nodes**

`status` holds one value, and `flagged` names a specific state: two authoritative
sources of the same claim type contradict each other and no human has resolved it.

A node holding one flagged claim among settled ones has no honest value to carry.
`flagged` overstates the doubt across everything else in it; `active` asserts a
confidence the conflict denies. This is test 2's `status` row, and it resolves the same
way: the contested claim is its own node.

**This is not a way to make a conflict disappear.** A4 still requires the split to be
recorded, and the flagged node has to be reachable from the settled one. Splitting to
quarantine an inconvenient conflict out of a reader's path is the same act done for the
opposite reason, and a reviewer should treat it as one.

### E. A node too small to stand alone — **one node**

A file whose body is a sentence and a link is a fragment, not a node. Test 5 vetoes
whatever tests 1 and 4 said, and the content folds into the node that gives it meaning.

**Short is not the same as small.** A node that states one complete idea in four lines
is atomic and passes. The test is whether the body means anything with the neighbour
closed, not how many lines it runs to.

### F. Splitting a node into sections joined by `part-of` — **not permitted**

`part-of` declares that the source is a constituent section or child of the target, and
its target is a node `id` like every other relationship's. It is an edge between two
nodes, each of which must satisfy tests 1–5 on its own.

It is therefore a description of a structure that already exists, never a licence to
create one. Using it to break a single idea into chapters produces exactly the fragments
case E rejects, and each of them spends an `id` permanently.

## When the second concept turns up mid-draft

A3 forbids folding it in. This is what to do instead, and the order matters more than it
looks.

1. **Stop at the sentence where it appeared.** Not at the end of the paragraph — the
   paragraph is where folding happens, because by the end of it the second concept has
   an introduction, a justification and a place in the argument.
2. **Run test 2 and test 3 on the pair.** Not the whole procedure; those two settle it
   in nearly every case, and test 2 settles it conclusively.
3. **File the task now**, per B3, naming the concept and stating in one line why it is
   not in the node you are writing. Filing it at the end of the draft means filing it
   after you have already written around it.
4. **Record the boundary** in the node you are writing, per A4: the task number, or the
   sibling `id` once one exists.
5. **Resume — and do not summarise what you split off.** A short summary "for context"
   is the second copy this corpus's linking rules exist to prevent, and it is the exact
   shape folding takes once an author has agreed not to fold. Link it. A reader who
   needs it can open it.

## Enforcement

**Nothing automated enforces any requirement on this page.**

The deterministic checker validates front matter against the schema and reports
duplicate ids, relationship targets matching no loaded node, citations whose form it
cannot recognise or whose path does not resolve, Markdown that resolves outside the
corpus root, and non-Markdown files. Every one of those is a property of a node's
structure. None of them is a property of how many ideas the node holds. CI runs that
same checker on pull requests touching the corpus, so it adds coverage, not a different
kind of check.

A node covering six subjects passes exactly as cleanly as one covering one. So does a
node split into six fragments.

**Enforcement is therefore the pull-request review**, and that is not a gap left by
accident. ADR-0028 chose Markdown over a machine-readable record format precisely
because the corpus is reviewed as a human-read diff at the pull request that changes
it, and named that review as the enforcement mechanism the rest of Ruling 12 depends
on. Atomicity is one of the things it is relied on for.

This is not the first such convention. The instruction node already names another — a
ledger carrying more than one commit-only `FACT` — and says outright that a reviewer
has to hold it because no check will. Atomicity belongs to the same class, and the only
failure mode either has is a reviewer who does not look.

### What a reviewer checks

Five questions, in the order that finds problems fastest:

1. **Can the node's subject be stated in one sentence with no conjunction joining two
   nouns?** If the pull-request description needed one, that is the same signal.
2. **Does any part of the body want a different `type`, `status` or `origin` than the
   one declared?** This is the decisive test and the only one that settles the question
   on its own. Read the body against the front matter, not the front matter alone.
3. **Would an ordinary repository change obsolete half the claims and leave the rest?**
   If so, the recorded revision cannot honestly cover both halves under the working
   practice in force today — see §3 for what #1321 may change about that.
4. **Where the node declined a subject, is the boundary recorded** with a sibling `id`
   or a task number, per A4?
5. **Is a split-off subject also summarised in the body?** This is the tell worth
   knowing: an author who filed the task and then wrote a paragraph of context anyway
   has folded the concept in while appearing not to. The filed issue makes it look
   handled.

## Exceptions and escalation

**There is no exemption from A1.** Every node is one idea; a node is not granted the
right to be two. What can genuinely be disputed is whether a particular subject *is*
one idea, and that is a judgement, not an exception — so the process below settles
disagreements rather than granting waivers.

1. **The author records the tension** in the node and names it in the pull request, per
   B5. A silent decision cannot be reviewed.
2. **The reviewer decides.** The reviewer is where enforcement lives, so this is the
   ordinary path and it ends here almost always.
3. **If author and reviewer do not agree, the node ships as two nodes** — B2's tie-break
   applied to a human disagreement rather than to an author's own uncertainty, for the
   same reason: over-merging is the mistake that leaves no trace.
4. **File the disagreement as an issue against this standard.** A boundary two people
   read differently is a defect in the procedure above, and the procedure is the thing
   that should change.

### `status: flagged` is not this process

`flagged` means two authoritative sources of the same claim type contradict each other
and no human has resolved it. It is a statement about a node's **evidence**.

A granularity disagreement is a statement about a node's **boundary**. Setting
`flagged` for one would tell every reader, and every generated view, that the node's
content is contested when nothing about it is. Use the four steps above.

## Scope and omissions

**This node covers** how many corpus nodes a subject becomes: the requirements, the
tests that decide, which test wins when they disagree, the boundary cases, what to do
when a second concept appears mid-draft, and who enforces any of it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The adjacent subjects listed in *Scope and authority* — taxonomy, identifiers, naming, linking, normative language, evidence, and the general scope-section convention | #1324, #1317, #1319, #1318, #1320, #1314, #1313 |
| How the two halves of a split subject should link to each other in practice, and which relationship type expresses it | #1318, linking |
| Whether a generated projection must preserve node granularity or may merge nodes into one view | #1316, generated content |
| Whether a reviewer's atomicity check belongs in a stated review requirement | #1322, review requirements |

**No `relationships` in this node's front matter.**
This node declares no `relationships`, and the absence is deliberate rather than an
oversight. Two different reasons apply, and they should not be confused:

- **The sibling standards cannot be targeted yet.** Every one this document points at —
  #1313, #1314, #1316, #1317, #1318, #1319, #1320, #1322, #1324 — is an open task with
  no node, so it carries no `id`. A `relationships[].target` naming an id no node
  carries is a hard validation error, so those edges wait until the nodes exist.
- **The instruction node could be targeted, and deliberately is not.** `corpus-agents`
  exists at the revision recorded in this ledger and would resolve cleanly. This node
  derives its authority from it, which is the obvious candidate for an edge. Which type
  expresses that, and in which direction, is #1318's to decide, and the whole set of
  standards is getting its edges in one pass once it has landed. Declaring one edge
  ahead of that rule would be this node guessing at a sibling's subject — the move its
  own scope table refuses.

The distinction matters because a reader who saw only the first reason would conclude
no target was available, which is not true.

**Expected but not verified when this node was written:**

- **No test in this procedure has been applied to a real second corpus subject.** The
  instruction node is the only other node in the corpus, so the five tests are derived
  from the schema, the ADRs and the instruction node rather than distilled from a body
  of practice. They are reasoned, not measured, and the first few real uses should be
  treated as evidence about the procedure as much as about the nodes.
- **The reviewer checklist has never been run by a reviewer.** It is proposed on the
  same basis, and its ordering — the claim that these five questions find problems
  fastest — is a design judgement with nothing behind it yet.
- **Case C's third outcome is untested.** Whether "the detail belongs in the executable
  source rather than the corpus" is a call authors will actually make, or one they will
  route around by merging anyway, is unknown until a subject reaches it.
