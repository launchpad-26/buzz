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
  - statement: "One node carries one recorded revision covering its whole ledger, and moving that revision makes a statement about every claim the node holds rather than only the edited ones."
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
  - statement: "A second copy of content the checker never reads goes stale without any run reporting it, which is why a node links an authoritative source rather than restating it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
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
subject would ever need two of one of them at the same time:

| The subject | The field it splits | Why one node cannot hold it |
|---|---|---|
| Half describes upstream Buzz behaviour, half a Launchpad-only convention | `origin` | The node would claim one provenance for content with two |
| Half is settled policy, half is a proposal not yet accepted | `status` | `active` would lend the proposal authority it does not have; `draft` would withdraw it from the settled half |
| Half documents an interface, half the runbook for operating it | `type` | Whichever value is chosen misfiles the other half for every reader and every generated view that groups by type |

**If any row applies, the answer is two nodes and the procedure stops.** No amount of
careful prose in the body repairs a front-matter field that is wrong about half its
own document.

### 3. The maintenance-clock test

A node carries one recorded revision for its whole ledger, and moving it asserts that
the node's claims were checked at that revision — all of them, not the edited ones.

Ask: is there an ordinary change to this repository that would obsolete half this
node's claims and leave the other half untouched? Not a contrived one — the normal
case.

If there is, the halves are on different maintenance clocks, and every future update
faces a choice with no correct answer: re-verify claims that did not need it, or move a
snapshot that does not cover what it now spans. That is precisely what
*independently maintainable* means, and it is the test that does the most work.

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
moves. Tests 1 and 5 both say "one".

Test 3 beats test 1, so the answer is not one node. Whether it is two turns on test 5.
If the detail can stand as its own node, it is one. **If it cannot, the answer is not to
merge it back — it is that the detail probably does not belong in the corpus.** For
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
