---
id: ingestion-invariant-extraction
type: ingestion
status: draft
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and the field names the corpus surface a node documents, not the prose form its body takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists agents/invariants.md as the only merged node under either an agents/ or ingestion/ path family, and no ingestion/ directory at all -- this is the first node in that family to land, the same absence ingestion/concept-extraction.md (#955, unmerged) independently recorded for itself."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no ingestion/ directory present, agents/invariants.md the sole agents/ or ingestion/ entry; run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "agents/invariants.md's own introduction states its own method in these words: 'AGENTS.md states these rules as connected prose without stable, citable identifiers -- this node gives each one a short id (I1-I10) so a review comment, a future corpus node, or a validator failure message can point at exactly one of them.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "crates/buzz-core/src/tenant.rs's module doc, under a heading literally named '## The fence', states a MUST-shaped constraint as a condition, not an instruction: 'a request's community is *resolved from the connection host by the server*, never supplied or influenced by the client' -- then states its own enforcement tier honestly in the very next paragraph: 'This is a **lint-and-review fence, not a compiler fence.**' naming that TenantContext::resolved and CommunityId::from_uuid are public, so 'a determined caller elsewhere *could* call them too,' and that a migration-lint harness, not the type system alone, forbids the deliberate path."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs:7-25"
  - statement: "crates/buzz-audit/src/hash.rs's storage_precision_timestamps_survive_a_database_round_trip test carries a comment naming the constraint explicitly as an invariant -- 'The invariant the write path must hold: hash what will be stored, so recomputing from the row reproduces the digest' -- and backs it with a runnable assertion, assert_eq!(compute_hash(&written).unwrap(), compute_hash(&read_back).unwrap()), that would fail if the constraint were violated."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs:201-214"
  - statement: "launchpad/docs/corpus/schema/node.schema.json's evidence array schema encodes a MUST-shaped constraint structurally rather than in prose: an allOf block (lines 115-134) with three if/then branches makes an entry_class of FACT require evidence and forbid confidence/provided_by, INFERENCE require evidence and confidence and forbid provided_by, and TEAM_KNOWLEDGE require provided_by and forbid confidence -- a constraint enforced by JSON Schema validation itself, not by a comment asking an author to remember it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json:115-134"
  - statement: "crates/buzz-db/src/store/thread.rs's increment_reply_count doc comment states a MUST-shaped relationship between two columns as fact -- 'This is correct because reply_count tracks direct children only, while descendant_count tracks ALL descendants at every nesting level' -- but the function itself carries #[allow(dead_code)] and its own doc comment admits the primary path is a separate, inlined copy elsewhere ('The primary increment path is inlined inside insert_thread_metadata's transaction'): the constraint is stated once in prose but actually held, if at all, by more than one independently-maintained call site, with nothing in the type system stopping a future one from omitting it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:246-255"
  - statement: "launchpad/docs/corpus/templates/invariant.md states the test for whether a sentence is genuinely invariant-shaped rather than descriptive prose or policy guidance: 'If the sentence cannot be falsified by inspecting the system directly, it has drifted into Boundary's policy territory,' and separately, distinguishing an invariant from a policy, 'is the claim falsified by inspecting the system's state or behavior directly (an invariant), or only by inspecting whether someone complied with a rule (a policy)?'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/invariant.md"
  - statement: "launchpad/docs/corpus/templates/invariant.md's 'Required sections' item 3, Enforcement today, requires an author to 'name which tier actually holds the invariant, honestly, citing the code' from a named list -- type-system-enforced, structurally enforced, test-enforced, predicate-enforced, or convention-and-review only -- and warns that 'a node that rounds convention-and-review only up to enforced misrepresents exactly the risk this section exists to surface.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/invariant.md"
  - statement: "ingestion/concept-extraction.md (#955, local unmerged commit, worktree __worktrees/task-955-ingestion-concept-extraction, not present on origin/launchpad) states its own Overview as: 'Recognize, while reading a source you are already looking at for another reason ... that a candidate concept exists and is worth turning into a corpus node, before that candidate is checked against the existing corpus for a duplicate,' and its Boundary section states it does not decide 'How many independently maintainable nodes a confirmed-new candidate becomes' or 'Whether a candidate already has a corpus node under a different name' -- a general recognition step with no narrowing to any one candidate shape."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#955 (local unmerged commit, worktree task-955-ingestion-concept-extraction)"
  - statement: "Parent Feature #620 ('corpus agent and ingestion guidance exists') lists 32 child issues: #640-#651 (12 issues, agents/*.md, of which only #649/agents/invariants.md is merged) and #953-#972 (20 issues, ingestion/*.md, of which #955/concept-extraction.md exists only as an unmerged local commit and none are merged) -- the family this node's own subject, #961/ingestion/invariant-extraction.md, belongs to."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, Child issues section"
  - statement: "Issue #961's own Definition of Done requires, in its how-to-shaped tail: states goal, prerequisites and allowed environment/scope; provides ordered steps that are executable and project-specific; defines success verification and rollback/cleanup where relevant; links authoritative commands/config rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#961 definition of done"
  - statement: "Because this node's subject -- recognizing that a MUST-shaped constraint exists in a source already being read for another reason, and giving it a stable citable pointer before it is used -- is one specific candidate shape within the same general recognition step ingestion/concept-extraction.md (#955) covers for concepts broadly, type: ingestion is the better fit than type: agent, matching #955's own reasoning and the corpus plan's own grouping of this task under the ingestion/*.md family rather than the agents/*.md family of general judgment procedures (ambiguity handling, concept resolution, change-impact analysis)."
    entry_class: INFERENCE
    evidence:
      - "gh_issue_view(620) -> Child issues section lists #640-#651 and #953-#972"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.75
relationships:
  - type: references
    target: corpus-agents
  - type: references
    target: agents-invariants
  - type: implements
    target: corpus-template-procedure
---

# Invariant extraction: how-to

Recognize, while reading a source already open for another reason -- a code
comment, a test, a schema constraint, or a policy document's prose -- that a
MUST-shaped constraint exists in it and is worth documenting, and give that
constraint a stable, citable pointer before deciding what happens to it next.

## Before you start

- Read `AGENTS.md`'s "Creating a node" step 2 -- "Check nothing already covers
  it" -- which presupposes a candidate already in hand. This node produces
  that candidate for one specific shape: a MUST-shaped constraint. It is not a
  substitute for step 2, and it does not perform step 2 itself.
- Know that this is a **recognition and identification** step, not the
  **authoring** step. `templates/invariant.md` writes the full body of one
  already-identified invariant -- its scope, its honestly-graded enforcement
  tier, its consequence of violation. This node's job ends before that: notice
  the constraint, confirm it is genuinely invariant-shaped rather than
  descriptive prose or policy guidance, and hand it off with a pointer, not a
  finished write-up.
- Read access to whatever source you were already working from: `crates/*/src/`
  for code comments and tests, `launchpad/docs/corpus/schema/*.json` for
  schema constraints, `AGENTS.md` or a decision record for policy prose.

## Notice a MUST-shaped constraint and extract it

1. **Apply the falsifiability test before calling anything an invariant.**
   `templates/invariant.md` states it directly: a candidate sentence must be
   "falsified by inspecting the system directly" to count -- not a goal
   ("X should stay consistent"), not an instruction to a person. The same
   template's policy-boundary test sharpens this further: is the claim
   falsified by inspecting the system's state or behavior directly (an
   invariant), or only by inspecting whether someone complied with a rule (a
   policy)? A sentence that fails this test is either descriptive prose (a
   fact worth citing but not extracting as a constraint) or SHOULD-shaped
   guidance -- neither is this step's subject.

2. **Branch on the source shape you were reading when you noticed it.** The
   four branches below are the source shapes this node's own task names; a
   real one was worked in each during this node's authoring, not merely
   described.

   **2a. A policy document's connected prose.** This node's own flagship
   precedent: `agents/invariants.md` (#649, merged) extracted ten numbered
   invariants, I1-I10, out of `AGENTS.md`'s connected prose -- prose that
   stated the same rules without any stable, citable identifier. Its own
   introduction names the method outright: giving each a short id "so a
   review comment, a future corpus node, or a validator failure message can
   point at exactly one of them." Read `agents/invariants.md`'s MUST table for
   the worked result; this node generalizes the method it used, it does not
   restate the ten invariants themselves.

   **2b. A code comment claiming an invariant.** `crates/buzz-core/src/tenant.rs`'s
   module doc, under a heading literally named "The fence," states the
   constraint as a condition: "a request's community is resolved from the
   connection host by the server, never supplied or influenced by the
   client." Critically, the same comment states its own enforcement tier
   honestly in the next paragraph -- "a lint-and-review fence, not a compiler
   fence" -- naming that the relevant types are `pub` and a determined caller
   could reach them, so a migration-lint harness, not the type system alone,
   closes the deliberate path. Recognizing this candidate means reading past
   the first sentence to that second paragraph, not stopping once the word
   "invariant" is found. A weaker case sits beside it in the same crate
   family: `crates/buzz-db/src/store/thread.rs`'s `increment_reply_count` doc
   comment states a two-column relationship as fact, but the function itself
   carries `#[allow(dead_code)]` and its own comment admits the constraint is
   actually held (if at all) by a separate, independently-maintained inlined
   copy elsewhere -- nothing in the type system stops a future call site from
   omitting it. Both are genuine MUST-shaped constraints; they sit at
   different enforcement tiers, and noticing which tier is part of confirming
   the candidate is real rather than aspirational.

   **2c. A test that encodes a MUST.** `crates/buzz-audit/src/hash.rs`'s
   `storage_precision_timestamps_survive_a_database_round_trip` test carries a
   comment naming the constraint explicitly -- "The invariant the write path
   must hold: hash what will be stored, so recomputing from the row
   reproduces the digest" -- and backs it with a runnable assertion that would
   fail if the constraint were violated. A test-encoded MUST is the strongest
   case to extract: the comment states intent, and the assertion is
   independent evidence the intent is actually checked, not merely believed.

   **2d. A schema constraint.** `launchpad/docs/corpus/schema/node.schema.json`'s
   evidence-array schema states no prose invariant at all -- the constraint
   ("an entry_class of FACT requires evidence and forbids confidence/
   provided_by," and so on for INFERENCE and TEAM_KNOWLEDGE) exists only as an
   `allOf` block of `if`/`then` conditionals. Recognizing this shape means
   reading structural schema logic as a MUST-shaped claim in its own right,
   not waiting for a comment to state it in words -- the constraint is real
   and citable even though no sentence anywhere asserts it.

3. **Assign a stable, citable pointer before the thread is lost.** Follow
   2a's precedent: a short, locally-scoped id (`agents/invariants.md`'s
   `I1`-`I10` scheme) turned unlabeled prose into something a review comment
   or a validator message could name exactly. That scheme is this precedent's
   own choice for its own document, not a corpus-wide numbering standard --
   no merged node currently requires a specific id shape for constraints
   documented inside a node's body, only `node.schema.json`'s kebab-case rule
   for a node's own top-level `id`. Record, at minimum: the one-sentence
   constraint stated as a condition, the file:line (or schema path) it came
   from, and which enforcement tier it appears to sit at -- enough for the
   next step to work from, not the full write-up `templates/invariant.md`
   itself requires.
4. **Hand off.** A recognized, pointer-bearing candidate has two honest
   destinations, and this step does not choose between them: it may become
   its own node authored from `templates/invariant.md` if it is an
   independently maintainable claim in its own right (per `AGENTS.md`'s "one
   node is one independently maintainable idea" rule), or it may become one
   cited `FACT` evidence entry supporting a different node that needed the
   constraint as supporting context rather than as its own subject. Which one
   applies is `standards/atomicity.md`'s and `AGENTS.md`'s question, not this
   node's.

## See also

- `agents/invariants.md` (#649, merged) -- the worked precedent this node's
  procedure generalizes; read it for the actual ten extracted invariants and
  their MUST/SHOULD/Enforcement structure, not restated here.
- `templates/invariant.md` -- the template for writing the full body of one
  already-identified invariant, once this step's output exists.
- `ingestion/concept-extraction.md` (#955, sibling, not yet merged at this
  node's authoring time) -- the general candidate-recognition step this node
  narrows; see *Boundary* below for the line between them.
- `AGENTS.md` -- the full create/update/retire procedure this node's output
  feeds into at step 2.
- `standards/atomicity.md` -- how many nodes a confirmed candidate becomes.

## Boundary

This node does not decide:

- **Whether a candidate is a general concept, pattern, or explanatory idea
  rather than a MUST-shaped constraint.** That is `ingestion/concept-extraction.md`'s
  (#955) broader territory. #955 states its own subject as recognizing "that
  a candidate concept exists and is worth turning into a corpus node" with no
  narrowing to any one shape; this node narrows specifically to constraints
  that pass the falsifiability test in step 1 above. A candidate that fails
  that test -- a reused rationale between two decision records, a recurring
  pattern with no MUST behind it, a theme across GitHub issue titles -- is
  #955's candidate, not this node's, even when it was noticed the same way.
- **Whether a recognized constraint already has a corpus node under a
  different name.** That is resolution's question
  (`agents/concept-resolution.md`, #642, unmerged), run after recognition,
  never before it.
- **The full write-up of an already-identified invariant** -- its Scope,
  honestly-graded Enforcement today tier, and Consequence of violation. That
  is `templates/invariant.md`'s required sections, applied once this step has
  handed off a candidate; this node's step 2 branches note an apparent tier
  only as part of confirming the candidate is real, not as the finished
  classification that template's own section demands.
- **Whether a recognized candidate becomes its own node or an evidence entry
  inside another node's ledger.** Both are legitimate outcomes named in step
  4 above; choosing between them is `standards/atomicity.md`'s and
  `AGENTS.md`'s question.
- **A catalog of every invariant already documented in this repository's code
  or corpus, for lookup.** That is reference-shaped content this node
  deliberately does not attempt; this node instructs one action --
  recognizing and pointing at a constraint -- using four real, worked
  examples rather than serving as a table of every invariant found.
- **Whether or how to fix any weakly-enforced constraint this node's own
  worked examples surface** (for instance, `thread.rs`'s convention-only
  reply-count/descendant-count relationship). That is separate implementation
  work, not this documentation task.

## Relationships

- **`references: corpus-agents`.** `AGENTS.md`'s "Creating a node" step 2 is
  the procedure this node's output feeds directly into, and its evidence and
  citation-shape rules apply unchanged to every constraint this node's
  procedure extracts; `references`' directionality -- "source cites target as
  supporting context; no ownership or currency dependency implied" -- fits,
  since this node's own steps stay accurate even if `AGENTS.md`'s later
  wording changes.
- **`references: agents-invariants`.** Declared deliberately even though
  `agents-invariants` is policy-shaped (built from `templates/policy.md`)
  rather than reference- or concept-shaped, because it is this node's actual
  worked precedent throughout step 2a above, not merely a document mentioned
  in passing -- exactly the "supporting context" `references`' own
  directionality describes, and the same latitude `ingestion/concept-extraction.md`
  (#955) took in declaring `references: corpus-agents` toward a node that is
  itself agent-shaped rather than reference/concept-shaped.
- **`implements: corpus-template-procedure`.** This node is a how-to-shaped
  instance of that template, per `relationships.schema.json`'s own worked
  example for `implements`: "a template instance of a standard."
- **No edge to `ingestion/concept-extraction.md` (#955) or `templates/invariant.md`.**
  Neither is a valid target: #955 exists only as a local unmerged commit on
  `origin/launchpad` at this node's authoring time (checked via `git ls-tree
  -r --name-only origin/launchpad -- launchpad/docs/corpus`, confirmed above),
  and `templates/invariant.md`, though merged, is discussed only in prose
  (*Before you start*, step 4, *Boundary*, *See also*) as the downstream
  template this node's output feeds -- not a dependency this node's own claims
  require to be true, and not a template this node itself instantiates. A
  `relationships[].target` naming an id no node on the merge-target branch
  carries is a hard validation error there even if it resolves in a local
  worktree, so #955 in particular is withheld for that reason regardless of
  how closely related the two subjects are.

## Scope and omissions

**This node covers** recognizing that a MUST-shaped constraint exists across
four source shapes -- a policy document's connected prose, a code comment
claiming an invariant, a test that encodes a MUST, and a schema constraint --
applying the falsifiability test to confirm the candidate is genuinely
invariant-shaped rather than descriptive or policy-shaped, assigning it a
stable citable pointer, and handing it off. Each source shape is grounded in a
real, currently-existing occurrence in this repository rather than a
hypothetical.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Deciding whether a candidate is a general concept rather than a MUST-shaped constraint | `ingestion/concept-extraction.md` (#955), not yet merged |
| Checking a recognized candidate against the existing corpus for a duplicate | `agents/concept-resolution.md` (#642), not yet merged |
| The full Scope / Enforcement today / Consequence of violation write-up for an already-identified invariant | `templates/invariant.md` |
| Deciding how many nodes a confirmed candidate becomes, or whether it becomes a node at all versus an evidence entry | `standards/atomicity.md`, `AGENTS.md` |
| Recognizing a MUST-shaped constraint from a live conversation, a GitHub issue thread, or a decision record's prose, as opposed to code, a test, or a schema file | not worked as an example here; the same falsifiability-test signal in step 1 is expected to generalize, but no real occurrence of these source shapes was traced during authoring |
| A fourth or later ingestion-family node's own subject (decision extraction, relationship extraction, evidence ranking, and the rest) | `ingestion/decision-extraction.md` (#957), `ingestion/relationship-extraction.md` (#968), `ingestion/evidence-ranking.md` (#959), and the remaining sibling tasks under Feature #620, none merged at this node's authoring time |

**Expected but not verified when this node was written:**

- **Whether the id-numbering precedent in step 3 (`agents/invariants.md`'s
  `I1`-`I10` scheme) should become a corpus-wide convention**, rather than
  each node choosing its own scheme, was not resolved here -- no merged
  standard currently requires or forbids a specific shape for an id assigned
  inside a node's body.
- **Whether a live-conversation or GitHub-issue-thread source of a MUST-shaped
  constraint fits this same four-step procedure as cleanly as the four worked
  branches** was not tested against a real transcript or issue thread in this
  session -- see the omissions table above.
- **Whether `ingestion/concept-extraction.md` (#955), once merged, will
  declare a `references` or other edge back toward this node** is that
  sibling's own edit to make, not decided here.
- **No CI run has exercised this node.** All validator evidence is local to
  this worktree.
