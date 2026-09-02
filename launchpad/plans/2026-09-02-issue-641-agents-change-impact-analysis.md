# Issue #641 — corpus node: agents/change-impact-analysis.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md` (id `corpus-agents`), and
`launchpad/docs/corpus/agents/invariants.md` (id `agents-invariants`, PR #1906,
merged) are on `origin/launchpad` (confirmed via `git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus`). The target file
`launchpad/docs/corpus/agents/change-impact-analysis.md` does not exist yet
(confirmed with `test -f`). `launchpad/docs/corpus/templates/procedure.md` (id
`corpus-template-procedure`) and `templates/runbook.md` (id
`corpus-template-runbook`) both exist on `origin/launchpad` and were read in full;
`procedure.md`'s own Boundary section states the procedure-vs-runbook split
explicitly: a procedure is "a task the reader chooses to perform on their own
schedule," a runbook is for "a condition that has already occurred and demands a
response... triggered by an alert or failure, not chosen." Change-impact analysis
is performed *before* an author chooses to edit or retire a node — no alert fires
— so `procedure.md` is the fitting template, not `runbook.md`. Front matter uses
`type: agent` (not `governance`): per `agents-invariants`' own precedent, `agent`
is used for nodes documenting the corpus's own agent-facing authoring surface
(the same surface `AGENTS.md` itself documents), while `governance` is reserved
in this corpus for the `standards/` and `templates/` meta-document families —
this node is neither a standard nor a template, it is a procedure an authoring
agent follows, the same family as `agents-invariants`.

STEP 1 — Gather evidence, read in full (no re-derivation from memory): issue
#641's live body (`gh issue view 641`); `AGENTS.md`'s *Updating a node* and
*Retiring a node* sections (already read — the two places AGENTS.md does
change-impact analysis in miniature: "find what points at it," "decide what
replaces it," "re-verify the claims you are touching," "decide whether the
recorded revision moves"); `agents-invariants.md` in full (gold-standard sibling,
already read); `templates/procedure.md` in full (already read — required
sections, evidence expectations, Boundary, relationships guidance); `standards/
atomicity.md` (the five-test node-count procedure, boundary cases, "over-merging
fails silently / over-splitting fails visibly" asymmetry — directly relevant to
"would a change here invalidate an existing template/standard instance," i.e.
atomicity's own boundary-case D "a flagged claim beside settled ones"); `standards/
linking.md` (`relationships[]` vs. body-prose distinction, and its own MUST 1 —
"a body-prose pointer MUST name a target that currently exists" — the exact
discipline change-impact analysis exists to protect); `relationships.schema.json`
(five relationship types + directionality — `depends-on`'s "source requires
target to be true/current for source's own claims to hold" is the type whose
semantics this node's "what depends on this" search is finding);
`node.schema.json` (`status` enum: draft/active/deprecated/retired/flagged);
`validate.py` lines 408 (`find_duplicate_ids`), 437
(`find_unresolved_relationship_targets`) — confirms mechanically that a
`relationships[].target` naming a still-loaded id is a hard error, and that
deleting a node (vs. status-changing it) is what breaks that check for every
inbound edge. RUNS HERE.

STEP 2 — Write front matter (id `agents-change-impact-analysis`, type `agent`,
status `draft`, origin `launchpad`, audiences `[agent, reviewer]`, evidence
ledger with real citations gathered in Step 1, `relationships: [{depends-on:
corpus-agents}, {implements: corpus-template-procedure}]` — mirroring
`agents-invariants`' own declared edges for the identical reasoning: this node's
authority is derived from `AGENTS.md`, and it is a procedure-shaped instance of
`templates/procedure.md`). Write the body per `procedure.md`'s required
sections: Overview (one line: assess blast radius before editing/retiring a
node), Before you start, one numbered task sequence (the two AGENTS.md
miniatures generalized: find inbound relationships via `grep`/search over the
corpus for the node's id, find claim-sharing siblings whose evidence cites the
same fact, find template/standard instances that a template/standard edit would
invalidate), See also, Boundary statement (not a general node-authoring
procedure — `AGENTS.md`; not the retirement/update procedures themselves, which
this generalizes and links back to, not replaces; not atomicity's node-count
test), Relationships, Scope and omissions. RUNS HERE.

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py` from
the worktree root; fix every reported error and re-run until exit 0. RUNS HERE.

STEP 4 — Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command
in its own call, confirm `OK`, then commit (plan + node) in a separate call with
`git commit -s`. RUNS HERE.

STEP 5 — Self-review (or `review-code` skill if reachable) against the diff:
every evidence entry actually supports its statement; no second canonical
document created; `validate.py` still exits 0 after any fix. RUNS HERE.

PARALLEL: none — single file, single worktree, no dependency on any sibling
Feature #620 task (none of the other 31 are merged, so none is a valid
relationship target per `AGENTS.md`'s own merge-target rule).

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report `OK` before commit. Push and PR are explicitly out of
scope for this task — the commit stays local to this worktree's branch for
later batch integration.

BUDGET: single document, one sitting — no multi-hour scope expected.

OPEN: whether change-impact analysis should also cover a "generated projection"
consumer (something a future knowledge-crate-facing index/graph view would need
re-derived when a node changes) is explicitly out of scope per Feature #620's
own "implementation of the knowledge-crate runtime" exclusion — the node states
this as a boundary rather than silently omitting it.

LEFT OUT: no relationship edge to any other `agents/*.md` or `ingestion/*.md`
sibling task under Feature #620 — none are merged at authoring time, so none is
a valid target, the same reasoning `agents-invariants` already recorded for
itself. No attempt to encode change-impact analysis as tooling (e.g. a script
that greps the corpus for an id) — this is a procedure a human/agent follows,
not new automation; per Feature #620's stated exclusion, no ingestion-pipeline
or knowledge-crate runtime is implemented here.
