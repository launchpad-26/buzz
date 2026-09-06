Issue #642 — task: document agents/concept-resolution.md
Stated size: none given — the corpus-plan task template has no Size field  ->  cap: 5 steps

Sized by the shape of the deliverable, not by asking: the Definition of Done scopes
this to "exactly one hand-authored canonical corpus document," so the work is one
file plus validation plus the commit gate, not a multi-file build.

ALREADY TRUE  (verified against git, gh, and the live repo in this worktree, not notes)
  launchpad/docs/corpus/agents/concept-resolution.md does not exist yet, on
  origin/launchpad or in this worktree — `git ls-tree -r --name-only origin/launchpad
  -- launchpad/docs/corpus` lists no agents/ file besides invariants.md, and
  `ls launchpad/docs/corpus/agents/` in this worktree confirms the same, one file.
  The sibling agents/invariants.md (id agents-invariants, PR #1906) is merged on
  origin/launchpad and was read in full as the evidence-density/rigor bar for this
  task.
  launchpad/docs/corpus/AGENTS.md (id corpus-agents) was read in full; its "Creating
  a node" step 2 ("Check nothing already covers it... If one is close, you are
  updating, not creating") and its "one node is one independently maintainable idea"
  line are this node's grounding.
  launchpad/docs/corpus/standards/atomicity.md (id corpus-standard-atomicity, active)
  exists on origin/launchpad and was read in full. Its stated scope is "how many
  corpus nodes a subject becomes" for a subject an author has ALREADY decided to
  write about — a five-test decision procedure for splitting NEW content. It never
  addresses whether that subject already has an existing node under a different
  name, and its own scope-and-omissions table does not list that concern either.
  This confirms issue #642's subject — matching a CANDIDATE against the EXISTING
  corpus, a question reached before atomicity's splitting question is even asked —
  is a distinct, not-yet-owned idea, not a duplicate of atomicity.
  launchpad/docs/corpus/templates/procedure.md (id corpus-template-procedure) and
  launchpad/docs/corpus/templates/concept.md (id corpus-template-concept) were both
  read in full. The subject is an ordered decision procedure with a genuine fork
  (match found -> update; no match -> create; ambiguous -> escalate), not a
  discursive explanation of an abstract idea, so procedure.md's How-to shape fits
  and concept.md's Explanation shape does not — confirmed by re-reading both
  templates' own Boundary sections before choosing, not assumed.
  node.schema.json and relationships.schema.json were read in full: type enum has
  13 surface values with no template/policy/procedure member — type tracks corpus
  surface, not documentation form, per procedure.md's own "A note on type" section;
  relationship types are depends-on, supersedes, implements, references, part-of.
  A live RepoQL explore call in this session (scoped to
  file:///launchpad/docs/corpus/**, asking whether an existing node already covers
  "checking whether a candidate concept already exists under a different name")
  returned templates/concept.md as its top (99%) semantic match — verified evidence
  that this session's own explore/keywords tooling addresses a kin concern
  (surfacing near-matches by meaning, not exact title), established by running it
  rather than assumed. A follow-up keywords call in the same scope failed with an
  out-of-memory/DuckDB fatal error — an infrastructure failure, not a corpus-content
  finding, and not cited as evidence about the corpus.
  Issue #642's live body (`gh issue view 642 --repo launchpad-26/buzz`) was read in
  full; its Definition of Done is the copied standards-track/how-to boilerplate
  tail, so this plan builds against Feature #620's real acceptance criteria
  instead: schema/graph/provenance validation passes with a genuinely-fitting
  template; concrete source start points named; no broad overview duplicating
  another node's canonical claims; an independent reader can traverse from this
  node to implementation/verification evidence for a representative question in
  its area.

STEP 1  Draft launchpad/docs/corpus/agents/concept-resolution.md:               [independent]  <- RUNS HERE
        front matter id: agents-concept-resolution, type: agent (matching the
        agents-invariants precedent — same corpus surface AGENTS.md and
        agents-invariants already occupy, not the "governance" precedent template
        meta-documents use, which does not apply to a real instance node), status:
        draft, origin: launchpad, audiences: [agent, reviewer].
        Body follows procedure.md's required sections: Overview; a numbered
        decision sequence with a genuine fork (state the candidate in one sentence
        -> enumerate what exists via git ls-tree against the merge-target branch,
        never assume "nothing to relate to" -> search for near-matches by title and
        claim, not just filename -> for each near-match apply a same-idea test ->
        fork: close match found = update, not create; no match = proceed to author
        and hand off to corpus-standard-atomicity for the how-many-nodes question;
        genuinely ambiguous = record the tension and let the reviewer decide, the
        same author-records/reviewer-decides pattern atomicity's own Exceptions
        section uses); See also; Boundary (not atomicity's splitting question; not
        deciding which template/type a resolved-as-new subject uses; not a tooling
        internals writeup); Relationships; Scope and omissions.
        Evidence ledger: every substantive claim cited to an opened source
        (AGENTS.md, standards/atomicity.md, node.schema.json,
        relationships.schema.json, issue #642's live body as TEAM_KNOWLEDGE, the
        RepoQL explore call as a FACT whose citation is the tool invocation plus
        observed result, following the precedent corpus-agents' own ledger already
        uses for tool-result citations).
        Relationships: references: corpus-agents (this node's authority is derived
        from AGENTS.md's step 2, not original), references:
        corpus-standard-atomicity (the sibling decision procedure this one hands
        off to once "new" is established) — both ids confirmed present on
        origin/launchpad in ALREADY TRUE above, so both are valid targets;
        implements: corpus-template-procedure per that template's own stated
        convention for a How-to instance.
        done when: the file exists with schema-shaped front matter and a body
        carrying every required procedure.md section, each substantive claim
        backed by a real evidence entry citing an opened source.

STEP 2  Validate schema/graph/provenance. Run                                    [needs 1]
        `python3 launchpad/project-intelligence/corpus/validate.py` from the
        worktree root. Fix anything reported (duplicate ids, unresolved
        relationship targets, citation-form errors, schema violations) and re-run
        until exit 0.
        done when: validate.py exits 0 against the full corpus tree including the
        new file.

STEP 3  Self-review against the issue's DoD and Feature #620's acceptance bar.    [needs 2]
        Re-read the diff line by line against issue #642's live DoD and the
        acceptance criteria in ALREADY TRUE: confirm no evidence entry rests only
        on an UNVERIFIED-shape citation while claiming FACT; confirm the node names
        concrete source start points (paths, not vague pointers); confirm nothing
        here duplicates standards/atomicity.md's canonical splitting-procedure
        content instead of linking to it; attempt the review-code skill/agent if
        reachable, otherwise record that it was not reachable and that this step
        was the substitute.
        done when: a passing re-read is recorded (or review-code findings are
        addressed and validate.py re-run to exit 0 if anything changed).

STEP 4  Earn the commit gate. Run, as the sole command in its own tool call:      [needs 3]
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        Confirm OK.
        done when: the suite reports OK with no failures or errors.

STEP 5  Commit locally, no push.                                                 [needs 4]
        `git commit -s -m "docs(corpus): add agents/concept-resolution.md
        procedure node (#642)"` (exact shape word filled from what STEP 1 actually
        produced). Do not push, do not open a PR — this lands in one Feature-wide
        PR later.
        done when: `git log -1` on this branch shows the new commit with a
        Signed-off-by trailer, and the working tree is otherwise clean.

PARALLEL  None of steps 2-5 can run before the step before it; STEP 1 is the only
  independent step, and it is where this plan first runs. Nothing here should be
  fanned out.

GATES  validate.py exit 0 (STEP 2) is a hard gate before self-review. The
  unittest suite reporting OK (STEP 4) is the commit gate; if refused for lacking
  a stamp, that is reported as a finding, not routed around with --no-verify or a
  hand-edited stamp file.

BUDGET  One file created (agents/concept-resolution.md), one file written outside
  the corpus (this plan). No code changes, no other corpus files touched. The
  risk is evidence density, not build complexity: every claim needs a real opened
  source, and the sibling agents-invariants.md sets a high bar for that.

OPEN  Not for a builder to decide.
  Whether a future ingestion/*.md sibling should reference this node once
  ingestion-side duplicate-checking tasks land — left to that sibling's own
  author, not decided here.
  Whether the RepoQL explore/keywords connection generalizes into a stated
  recommendation (vs. the one-off verified observation this plan treats it as) is
  left for a reviewer or a later revision, not decided in this pass.

LEFT OUT  Deliberately excluded.
  Rewriting or re-deciding standards/atomicity.md's five-test splitting procedure
  — out of scope per issue #642's own "Out of scope: creating or materially
  editing a second hand-authored canonical corpus document."
  Building or specifying any actual duplicate-detection tooling/runtime —
  Feature #620's own "Out of scope: implementation of the knowledge-crate
  runtime" excludes this explicitly; the node is agent-facing procedural guidance
  only.
