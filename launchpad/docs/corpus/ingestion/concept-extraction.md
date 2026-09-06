---
id: ingestion-concept-extraction
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
  - statement: "node.schema.json's type enum has thirteen members including ingestion, and describes the field as naming 'the corpus surface this node documents,' not the documentation form a node's prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no ingestion/ directory at all, so this node has no merged sibling under ingestion/ to follow as type precedent; it is the first node in that family."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no ingestion/ path present; run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Parent Feature #620 lists 32 child issues (#640-#651, #953-#972). Of these, #640-#648 and #650-#651 (agents/*.md) plus the merged #649 (agents/invariants.md) total 12 issues under an agents/ path family, while #953-#972 total 20 issues under an ingestion/ path family; #953 is 'ingestion/ci.md', #954 is 'ingestion/commits.md', #956 is 'ingestion/configuration.md', and #972 is 'ingestion/tests.md' -- naming specific kinds of source material (CI output, commit history, configuration, tests) as the ingestion family's subjects, distinct from the agents/ family's subjects (ambiguity handling, evidence resolution, repository navigation, documentation creation/update/validation, concept resolution, change-impact analysis, stale documentation), which are about an agent's general judgment procedures rather than a specific evidence source."
    entry_class: FACT
    evidence:
      - "gh_issue_view(620) -> Child issues section lists #640-#651 and #953-#972"
      - "gh_issue_view(953) -> title 'task: document ingestion/ci.md'"
      - "gh_issue_view(954) -> title 'task: document ingestion/commits.md'"
      - "gh_issue_view(956) -> title 'task: document ingestion/configuration.md'"
      - "gh_issue_view(972) -> title 'task: document ingestion/tests.md'"
  - statement: "Because this node's subject -- recognizing, while reading any kind of source material, that a candidate concept exists and is worth documenting -- is the general recognition step that precedes drawing evidence from any one of the ingestion family's specific source types (CI output, commits, configuration, tests, code, decisions, issues), type: ingestion is the better fit than type: agent, even though the subject is agent-performed judgment in the same way #642's agents/concept-resolution.md is; the corpus plan itself already grouped this task with ci.md and commits.md rather than with concept-resolution.md, ambiguity-handling.md or the other agents/*.md tasks, and this node follows that placement rather than overriding it."
    entry_class: INFERENCE
    evidence:
      - "gh_issue_view(620) -> Child issues section lists #640-#651 and #953-#972"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "AGENTS.md's 'Creating a node' step 2 states: 'Check nothing already covers it. Read the existing nodes under launchpad/docs/corpus/. If one is close, you are updating, not creating.' -- a check that presupposes a candidate concept has already been identified; nothing in AGENTS.md's numbered procedure names how that candidate first gets noticed."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "templates/procedure.md requires a corpus node built from it to carry, in its body: an Overview stating the task in one line; an optional Before you start section; one numbered task sequence per logical goal, which Diátaxis's own words permit to fork rather than stay strictly linear when a task 'sometimes need[s] to fork and overlap' and 'ha[s] multiple entry and exit-points'; a See also section; an explicit Boundary statement; a Relationships section; and a Scope and omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "templates/procedure.md's own Boundary section requires a how-to-shaped instance node to state, as an explicit checklist, that it is not reference (`templates/reference.md`, information-oriented lookup content), not a tutorial (acquisition-of-skill for a newcomer), and not concept/explanation (`templates/concept.md`, understanding-oriented discussion of why a design exists), plus any node-specific exclusion the author found."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
      - "launchpad/docs/corpus/templates/reference.md"
      - "launchpad/docs/corpus/templates/concept.md"
  - statement: "The sibling agents/concept-resolution.md (local unmerged commit, worktree __worktrees/task-642-agents-concept-resolution, not present on origin/launchpad) states its own subject as: deciding, for a candidate subject already identified, whether it is genuinely new or an existing corpus node in different clothes, and names AGENTS.md's 'Creating a node' step 2 as the procedure it makes concrete -- a step that itself presupposes a candidate has already been named. It does not address how the candidate is first noticed."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#642 (local unmerged commit, worktree task-642-agents-concept-resolution)"
  - statement: "crates/buzz-db/src/store/thread.rs defines increment_reply_count (line 256) and decrement_reply_count (line 297), each independently issuing an UPDATE against thread_metadata's reply_count and, when a root_event_id is known, descendant_count -- the same pair of columns, updated by hand-written SQL in two separate functions rather than one shared helper."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:256"
      - "crates/buzz-db/src/store/thread.rs:297"
  - statement: "crates/buzz-db/src/store/event.rs independently reimplements the identical reply_count/descendant_count UPDATE idiom twice more: once inside soft_delete_event_and_update_thread (function starts line 897; the two SET clauses are at lines 920 and 931) and once inside the reply-insert branch of a large event-insertion function (the UPDATE statements are at lines 1296 and 1309) -- a third and fourth independent occurrence of the same two-column maintenance idiom already seen in thread.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:897"
      - "crates/buzz-db/src/store/event.rs:920"
      - "crates/buzz-db/src/store/event.rs:931"
      - "crates/buzz-db/src/store/event.rs:1296"
      - "crates/buzz-db/src/store/event.rs:1309"
  - statement: "crates/buzz-db/src/store/relay_admin_actions.rs's execute_delete_with_marker (line 698) attempts a fifth occurrence of the same maintenance idiom at lines 747-748 ('UPDATE events SET reply_count = GREATEST(reply_count - 1, 0) ... WHERE community_id = $1 AND id = $2'), but targets the events table rather than thread_metadata, and never updates descendant_count at all (its root_event_id parameter is prefixed _root_event_id, unused)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_admin_actions.rs:698"
      - "crates/buzz-db/src/store/relay_admin_actions.rs:747"
      - "crates/buzz-db/src/store/relay_admin_actions.rs:748"
  - statement: "schema/schema.sql's events table definition (CREATE TABLE events, starting line 203) has no reply_count or descendant_count column; those two columns exist only on the separate thread_metadata table (CREATE TABLE thread_metadata, starting line 514, with reply_count and descendant_count declared at lines 524-525). Running relay_admin_actions.rs's query against a real database would fail with an undefined-column error."
    entry_class: FACT
    evidence:
      - "schema/schema.sql:203"
      - "schema/schema.sql:514"
      - "schema/schema.sql:524"
  - statement: "The only test exercising execute_delete_with_marker (crates/buzz-relay/src/api/admin/mod.rs, the call at line 5002) passes None for the parent_event_id argument ('// no parent'), which skips the entire 'if let Some(parent) = parent_event_id' branch containing the broken query -- so the bug has never actually executed in any test run, and CI passing is not evidence the query works."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:5002"
  - statement: "/home/serina/Launchpad/buzz/CLAUDE.md's 'Common Gotchas' section already states, as gotcha 7: 'Thread counters: reply_count and descendant_count are materialized on thread root events. Any code that inserts replies must update these counters -- check existing reply handlers for the pattern.' -- itself a corpus-adjacent artifact recording that this exact recurring pattern had already been noticed and written down once before this session re-derived it independently from the source."
    entry_class: FACT
    evidence:
      - "CLAUDE.md:195"
  - statement: "Filed block/buzz#7227 during this authoring session, reporting that execute_delete_with_marker updates the wrong table and skips descendant_count -- a genuine, previously unfiled product defect that surfaced only from enumerating every occurrence of the reply_count/descendant_count maintenance idiom rather than stopping after the first one or two seen."
    entry_class: FACT
    evidence:
      - "gh_issue_create(repo='block/buzz') -> https://github.com/block/buzz/issues/7227"
  - statement: "launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md's Context section states 'This record generalises that precedent,' referring to launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md's own reasoning, quoted there as: a copy 'trad[es] a conflict that Git *shows you* for a divergence that nothing does,' and 'A conflict you must resolve is better than a copy you forget to.'"
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md"
      - "launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md"
  - statement: "block/buzz#3293 ('Mobile: live threaded replies never reach the channel window store, so thread summaries never update') and block/buzz#3799 ('Missing replies in thread view after replying to non-latest messages') are two independently filed, still-open upstream issues that both describe a rendered/derived thread reply summary failing to reflect reality under specific event orderings -- one on mobile's live-update path, one on desktop's thread panel."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "block/buzz#3293 and block/buzz#3799 (issue bodies)"
  - statement: "Reading #3293's and #3799's bodies in full shows both describe client-side derived/rendered state (a mobile channel-window store never receiving a live event; a desktop thread panel failing to render a reply to a non-latest message) rather than the Postgres-side thread_metadata counters the reply_count/descendant_count idiom maintains -- so despite both areas sharing the words 'reply' and 'thread summary,' they are a related but distinct concept from the backend counter-maintenance idiom, not the same one recurring a sixth and seventh time; treating them as the same concept would be exactly the kind of unearned connection this node's own procedure warns against drawing without reading past the title."
    entry_class: INFERENCE
    evidence:
      - "gh_issue_view(3293, repo='block/buzz') -> body describes a mobile channel-window store, not a Postgres counter"
      - "gh_issue_view(3799, repo='block/buzz') -> body describes a desktop thread-panel render gap, not a Postgres counter"
      - "crates/buzz-db/src/store/thread.rs:256"
    confidence: 0.85
  - statement: "Issue #955's own Definition of Done requires that every substantive factual claim be traceable to current code, test, specification, accepted decision, migration/configuration, or attributed GitHub evidence with FACT, INFERENCE and TEAM_KNOWLEDGE not conflated; that the document link relevant implementation/verification/decision/neighboring nodes without duplicating their canonical content; and that it state goal, prerequisites, allowed scope, ordered executable project-specific steps, and success verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#955 definition of done"
  - statement: "Parent Feature #620's Out of scope section states: 'Work owned by sibling corpus Features, implementation of the knowledge-crate runtime, and any artifact not required by this Feature outcome or its declared child issues' -- confirming no ingestion pipeline or tool is expected from this node, only agent-facing procedural guidance for a step a human or agent performs while reading source material."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, Out of scope section"
relationships:
  - type: references
    target: corpus-agents
  - type: implements
    target: corpus-template-procedure
---

# Concept extraction: how-to

Recognize, while reading a source you are already looking at for another reason —
code, a decision record, a GitHub issue thread, or a conversation — that a candidate
concept exists and is worth turning into a corpus node, before that candidate is
checked against the existing corpus for a duplicate.

## Before you start

- Read `AGENTS.md`'s "Creating a node" steps 1-2. Step 2 — "Check nothing already
  covers it" — is what this node makes possible to run at all: it needs a candidate
  already in hand. This node is the step before step 2, not a replacement for it.
- Know that this is a **recognition** step, not the **resolution** step. The sibling
  `agents/concept-resolution.md` (#642) runs immediately after this one and answers a
  different question — see *Boundary* below before assuming either one covers the
  other.
- Read access to whatever source you were already working from: `crates/*/src/` for
  code, `launchpad/decisions/ADR-*.md` for decision records, `gh issue list`/`gh issue
  view` for GitHub issues.

## Notice a candidate concept

1. **Notice you are seeing the same shape twice, or that something took real effort
   to reconstruct.** Extraction starts as a felt sense while doing something else —
   drafting a different node, tracing a bug, reading an issue thread — not a
   scheduled search. The signal is repetition (the same idea recurs) or friction (an
   idea was hard to piece together and would be exactly as hard to piece together
   again next time, for the next reader).
2. **Branch on what you were reading when you noticed it.** The three branches below
   are the source shapes named in this node's own task; a real one was worked in each
   during this node's authoring, not merely described.

   **2a. A recurring pattern across `crates/*/src/`.**
   1. Grep for every occurrence of the suspected shape, not just the two you happened
      to see first — stopping early is how a real inconsistency hides in plain sight.
   2. Read each occurrence's surrounding context, not only the matching line: do all
      occurrences serve the same invariant, or has one drifted into a different one?
   3. **Worked in this session:** `crates/buzz-db/src/store/thread.rs` maintains
      `thread_metadata`'s `reply_count`/`descendant_count` in two independent
      functions (`increment_reply_count`, `decrement_reply_count`).
      `crates/buzz-db/src/store/event.rs` reimplements the identical idiom twice
      more, inline, inside two different functions. Enumerating a fifth occurrence in
      `crates/buzz-db/src/store/relay_admin_actions.rs` surfaced that it targets the
      wrong table (`events`, which has no such column at all — see
      `schema/schema.sql`) and skips `descendant_count` entirely — a real,
      previously unfiled inconsistency (filed as `block/buzz#7227`) found only
      because the fifth occurrence was checked at all, not because it looked
      different from the first four at a glance. `/home/serina/Launchpad/buzz/CLAUDE.md`
      already carries a "Common Gotchas" entry for this exact pattern, itself
      evidence that recognizing it was worth doing once before.

   **2b. A rationale stated in a decision record.**
   1. Read the record's Context section for language that *reuses* an earlier
      record's reasoning, not only for the surface decision being made.
   2. **Worked in this session:** `ADR-0043-prefer-fork-owned-overrides.md`'s Context
      section states outright, "This record generalises that precedent," naming
      `ADR-0005-launchpad-deployment-boundary.md`'s reasoning — a copy "trad[es] a
      conflict that Git *shows you* for a divergence that nothing does." The
      candidate concept is the *reused reasoning itself* (override-vs-copy divergence
      handling), not either record's specific subject (a deployment boundary, a
      general fork-ownership rule). A decision record that explicitly says it is
      reapplying an earlier one's logic is telling you, in its own words, that the
      logic is a concept independent of both records.

   **2c. A recurring theme across GitHub issues on a subject.**
   1. Search issues on the suspected subject and read the bodies, not just the
      titles — two issues can share vocabulary while describing unrelated things.
   2. **Worked in this session:** `block/buzz#3293` (mobile) and `block/buzz#3799`
      (desktop) are two independently filed, still-open bugs that both describe a
      thread's rendered reply summary failing to reflect reality under specific
      event orderings. Reading both bodies in full — not just matching on "reply
      count" — shows they describe client-side derived state (a store never
      receiving a live event; a panel failing to render a reply to a non-latest
      message), which is a **related but distinct** concept from 2a's
      Postgres-side counter idiom, not a sixth and seventh occurrence of the same
      one. Telling those two apart, rather than merging them because they share a
      word, is itself part of this step — see the evidence ledger's INFERENCE entry
      for the reasoning, rated 0.85 rather than treated as settled.
3. **Write down what was noticed before the thread is lost.** A scratch note or an
   issue comment is enough; it need not be committed. Capture the candidate stated in
   one sentence, plus the concrete occurrences — file:line, decision record names,
   issue numbers — that made it feel recurring rather than one-off. A candidate that
   cannot be stated in one sentence without an *and* may already be two candidates;
   note that too, rather than resolving it here (`standards/atomicity.md`'s question,
   not this one's).
4. **Hand off.** A written-down candidate's next stop is checking it against the
   existing corpus for a near-duplicate under a different name — a distinct step this
   node deliberately does not perform. See *Boundary*.

## See also

- `agents/concept-resolution.md` (#642, sibling, not yet merged at this node's
  authoring time) — the step that runs immediately after this one, checking a
  now-identified candidate against the existing corpus.
- `standards/atomicity.md` — the step after resolution answers "genuinely new,"
  deciding how many nodes the candidate becomes.
- `AGENTS.md` — the full create/update/retire procedure this node's output feeds
  into at step 2.

## Boundary

This node does not decide:

- **Whether a candidate already has a corpus node under a different name.** That is
  resolution's question (`agents/concept-resolution.md`, #642), run immediately
  after this node, never before it — recognizing that something is candidate
  material does not by itself establish that it is new.
- **How many independently maintainable nodes a confirmed-new candidate becomes.**
  That is `standards/atomicity.md`'s five-test procedure, run only after resolution
  has answered "new."
- **Whether or how to fix `block/buzz#7227`**, the defect this node's own worked
  example surfaced. That is separate implementation work owned by whoever picks up
  that issue, not this documentation task.
- **Whether the reply_count/descendant_count backend idiom and the #3293/#3799
  client-side thread-summary bugs should eventually become one corpus node or two
  related ones.** Both are real, but this node only establishes that they are
  distinct candidates worth separately screening — which one, both, or neither
  becomes a merged node, and under what `id`, is resolution's and atomicity's
  question, not this node's.
- **How to acquire the underlying judgment from scratch, for someone who has never
  done this before.** That is a tutorial's territory (acquisition of skill), and no
  corpus template currently covers that form; this node assumes a reader who already
  knows how to read code, a decision record, and a GitHub issue, and needs only the
  procedure for noticing a concept while doing so.
- **A catalog of every existing corpus node, source-material shape, or evidence
  citation form for lookup.** That is reference material (`templates/reference.md`
  governs that form); this node instructs one action — noticing — rather than
  serving as a table an author consults mid-task for a fact.
- **Why an extraction step needs to exist at all, or the theory behind Diátaxis's
  four documentation forms.** That is a concept/explanation node's territory
  (`templates/concept.md`); this node's steps stop at instructing the action, not
  discussing the idea of concept extraction for its own sake.

## Relationships

- **`references: corpus-agents`.** `AGENTS.md`'s "Creating a node" step 2 is the
  procedure this node's output feeds directly into; `references`' directionality —
  "source cites target as supporting context; no ownership or currency dependency
  implied" — is the right coupling, since this node's own procedure stays accurate
  even if `AGENTS.md`'s later steps are later reworded.
- **`implements: corpus-template-procedure`.** This node is a how-to-shaped instance
  of that template, per `relationships.schema.json`'s own worked example for
  `implements`: "a template instance of a standard."
- **No edge to `agents/concept-resolution.md` (#642) or any other Feature #620
  sibling.** None besides `agents-invariants` are merged on `origin/launchpad` at
  this node's authoring time (checked via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), and
  `agents-invariants` is not a genuine dependency of this node's own subject —
  declaring either edge before the target exists would be a hard validation error
  the moment CI runs against the real merge target.

## Scope and omissions

**This node covers** noticing that a candidate concept exists across three source
shapes — a recurring pattern in code, a rationale reused across decision records, and
a recurring theme across GitHub issues — writing the candidate down, and handing it
off to the resolution step. It grounds each source shape in a real occurrence found
during this node's own authoring rather than a hypothetical.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Checking a candidate against the existing corpus for a near-duplicate | `agents/concept-resolution.md` (#642), not yet merged |
| Deciding how many nodes a confirmed-new candidate becomes | `standards/atomicity.md` |
| Creating, updating or retiring the resulting node | `AGENTS.md` |
| Fixing the `reply_count`/`descendant_count` table-and-column defect this node's worked example surfaced | `block/buzz#7227` |
| Recognizing a candidate from a live conversation (as opposed to code, a decision record, or a GitHub issue) | not worked as an example here; the same notice-repetition-or-friction signal in step 1 is expected to generalize, but no real conversation-sourced occurrence was traced during authoring |
| A fourth or later ingestion-family node's own subject (CI output, commit history, configuration, tests) | `ingestion/ci.md` (#953), `ingestion/commits.md` (#954), `ingestion/configuration.md` (#956), `ingestion/tests.md` (#972), none merged at this node's authoring time |

**Expected but not verified when this node was written:**

- **Whether the conversation-sourced signal generalizes as cleanly as the three
  worked branches** was not tested against a real transcript in this session — see
  the table above.
- **Whether `block/buzz#7227`'s reported defect is confirmed by a maintainer, or is
  itself a misreading of intentionally dead code** was not established beyond this
  node's own reading of the schema and the one test that exercises the function; the
  issue is filed, not resolved.
- **Whether `agents/concept-resolution.md` (#642) will, once merged, declare a
  `depends-on` or `references` edge back to this node** is that sibling's own edit to
  make, not decided here.
