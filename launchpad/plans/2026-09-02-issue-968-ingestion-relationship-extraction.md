# Issue #968 — corpus node: ingestion/relationship-extraction.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/schema/relationships.schema.json` are on `origin/launchpad`
and define the five-type enum (`depends-on`, `supersedes`, `implements`,
`references`, `part-of`) with directionality/inverse metadata. `git ls-tree -r
--name-only origin/launchpad -- launchpad/docs/corpus` (run at HEAD
aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) confirms: no `ingestion/` directory
exists yet, `agents/invariants.md` (id `agents-invariants`, #649) is the only
merged `agents/*.md` sibling under Feature #620, and `templates/procedure.md` (id
`corpus-template-procedure`) exists and states type tracks corpus *surface*, not
documentation form. The target path `launchpad/docs/corpus/ingestion/
relationship-extraction.md` does not exist. `node.schema.json`'s `type` enum
includes `ingestion` as a member distinct from `agent` — no merged node currently
uses it, so this is the first. Real, merged worked examples of each relationship
type exist already in the wider corpus (found via `grep -rn "type: <x>"
launchpad/docs/corpus`): `part-of` — `layers/configuration/relay-configuration.md`
→ `architecture-containers-relay`, `layers/compute/sprig-runtime.md` →
`architecture-containers-agent-runtime`; `implements` — many capability/config
nodes → their own template ids; `depends-on` — `agents-invariants` →
`corpus-agents`, `standards/evidence.md`, `standards/documentation-standard.md`,
`templates/decision-reference.md`; `references` — the large majority of all
declared edges. **No merged node currently declares a `type: supersedes` edge** —
confirmed by grep; only prose discusses it (AGENTS.md's retirement procedure,
`standards/deprecation.md`). `standards/review-requirements.md` MUST 6 (read in
full) states the exact gap this node exists to close at authoring time: "the
schema enforces only that `type` is one of five enum members... it does not, and
by its own description cannot, confirm that a `supersedes` or `depends-on` edge is
actually true in that direction." `AGENTS.md`'s own documented trap ("There was
nothing to point at") is a false-negative failure (concluding no relationship
exists without enumerating); this node's own genuine value-add is the adjacent,
distinct false-positive-avoidance question — given a relationship already
recognized as real, which of the five types is the honest one — grounded directly
in `relationships.schema.json`'s own directionality text, not a restatement of the
enumeration trap itself. `#642` (`agents/concept-resolution.md`, unmerged, read in
full at `__worktrees/task-642-.../concept-resolution.md`) answers a different
question — whether a *candidate node* duplicates an existing one — and its own
Scope and omissions table explicitly leaves "how an *ingestion*-side agent...
should apply this same resolution question to ingested claims" to the
`ingestion/*.md` family, i.e. to this node's family, not to itself.

STEP 1 — Gather evidence, read in full (already done in this session, restated
here for the record): issue #968's live body (`gh issue view 968`); Feature
#620's live body; `node.schema.json`, `relationships.schema.json` (full text,
directionality + inverse table); `AGENTS.md` (full, including the enumeration
trap paragraph); `agents/invariants.md` (gold standard, full); `templates/
procedure.md` (full, required sections + relationships guidance); `standards/
atomicity.md`, `standards/linking.md`, `standards/review-requirements.md` (MUST
6 specifically), `schema/README.md`'s directionality table; the sibling unmerged
`agents/concept-resolution.md` and `agents/change-impact-analysis.md` for
boundary-drawing and evidence-ledger style; real merged worked examples of each
relationship type via `grep -rn "type: (depends-on|supersedes|implements|
references|part-of)" launchpad/docs/corpus`. RUNS HERE.

STEP 2 — Write front matter: id `ingestion-relationship-extraction`, type
`ingestion` (first node to use this enum member — corpus surface is the
ingestion/evidence-extraction family the file path itself names, not the
`agent` surface `AGENTS.md`/`agents-invariants` occupy), status `draft`, origin
`launchpad`, audiences `[agent, reviewer]`, evidence ledger citing every source
in Step 1 (commit provenance, schema text, `AGENTS.md` trap text, review-
requirements MUST 6, real worked examples per type, the absence of a `supersedes`
worked example, the boundary against #642's own scope table), relationships:
`references: corpus-agents` (the enumeration trap this node's prerequisite step
guards against — supporting context, not a currency dependency, following
`agents-concept-resolution`'s precedent for the identical target rather than
`agents-invariants`'/`agents-change-impact-analysis`'s `depends-on`, since this
node's procedure is original content, not a restatement of `AGENTS.md`'s own
rules), `references: corpus-standard-review-requirements` (MUST 6 is the direct
textual grounding for why type-honesty must be gotten right at authoring time,
before review), `implements: corpus-template-procedure` (template instance, per
that template's own "should declare implements" guidance). Write the body per
`procedure.md`'s required sections: Overview (one line — given a genuine edge
between the node being authored and another node, decide which of the five
`relationships.schema.json` types is the honest one); Before you start
(enumerate the merge-target tree per `AGENTS.md`'s trap, confirm the candidate
target already resolves as a real node id); one numbered task sequence — five
ordered diagnostic tests, one per type, each keyed directly to that type's own
`relationshipMeta` directionality text and, where one exists, a real merged
worked example, explicitly noting `supersedes` has none yet; See also; Boundary
(not #642 — duplicate-node detection vs. edge-typing; not `standards/atomicity.md`
— node-count vs. edge-type; not `standards/linking.md` — body-prose syntax vs.
type selection; not #641 — post-hoc impact of an existing edge vs. choosing one at
drafting time; not a tutorial); Relationships; Scope and omissions. RUNS HERE.

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py` from
the worktree root; fix every reported error and re-run until exit 0. RUNS HERE.

STEP 4 — Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command
in its own tool call, confirm `OK`, then in a separate call commit (plan + node)
with `git commit -s`. RUNS HERE.

STEP 5 — Dispatch an independent `serina:review-code` subagent (fresh context)
against the diff; fix genuine findings and re-run `validate.py`. If the skill is
unreachable, self-review against: every evidence entry actually supports its
statement and was actually opened; no second canonical document created; the
five-test ordering is internally consistent and each test's positive case cites
a real schema quote or worked example; `validate.py` still exits 0. RUNS HERE.

PARALLEL: none — single file, single worktree, no dependency on any sibling
Feature #620 task (only `agents-invariants`, #649, is merged; none of the other
31 — including #642 and #641 — is a valid relationship target).

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report `OK` before commit. Push and PR are explicitly out of
scope for this task — the commit stays local to this worktree's branch for later
batch integration.

BUDGET: single document, one sitting.

OPEN: whether a sixth, "none of the five fit" outcome needs its own worked
example beyond stating that `references` is not mandatory and declaring none is
always valid — deferred to the node's own Boundary/Scope section rather than
resolved here.

LEFT OUT: no relationship edge to `agents-concept-resolution` or
`agents-change-impact-analysis` (#642, #641) — neither is merged at authoring
time, so neither is a valid target; the boundary against both is drawn in prose
only, the same pattern every sibling node in this batch already uses for
unmerged siblings. No attempt to build tooling that automates type selection —
Feature #620 excludes "implementation of the knowledge-crate runtime," and this
is a manual procedure using the existing schema text and `grep`, not new
automation.
