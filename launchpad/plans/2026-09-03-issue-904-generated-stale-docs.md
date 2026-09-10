Issue: #904 (parent PRD #621)

Stated size: no explicit Size line on #904; every sibling generated/*.md task under #621 is single-document/single-builder-module -> cap: 5 steps.

# Generate launchpad/docs/corpus/generated/stale-docs.md

ALREADY TRUE

- The #633 generator framework (`launchpad/project-intelligence/corpus/indexes.py`)
  is merged on `feature/621-generated-traceability`: builder discovery,
  `GenerationContext`, front-matter rendering and the
  `templates/generated-index.md` body skeleton all exist and need no changes.
- `templates/generated-index.md`'s own boundary table names `stale-docs.md`
  (#904) "An audit report" / "Same reason as `orphaned-docs.md`" -- not
  index-shaped, so `implements -> corpus-template-generated-index` must not be
  declared, mirroring `index_defs/orphaned_docs.py` (#902, merged), the
  closest precedent for shape.
- AGENTS.md (`corpus-agents`) already documents the exact deterministic
  staleness signal this task must implement, in its own "Checking whether
  cited files moved" section: `git diff --name-only <recorded-sha> -- <the
  normalized file paths in the ledger>`, with two hard limits stated in that
  same section -- normalize `path:line`/`path:start-end` before passing to
  git (an un-normalized pathspec matches nothing and reports empty output
  indistinguishable from "unchanged"), and only three of CONTRACT.md's six
  citation shapes name an openable file at all (bare path, file line, file
  range -- graph edge, tool result, commit and both URL forms do not). The
  same section calls this "a narrowing step, not a certification."
- `validate.py`'s `_COMMIT_CITATION_RE` (`^commit\s+[0-9a-fA-F]{7,40}\b`) is
  the existing classifier for the `commit <sha>`-shaped citation the
  provenance FACT (corpus-agents' own example: "checked against repository
  revision <sha>" / evidence `commit <sha>`) uses.
  `coverage.py`'s `_node_file_citations(node)` (#892, merged) already applies
  the identical routing order and returns exactly the three openable, normalized
  (position-stripped) file citations per node, reusable verbatim rather than
  reimplemented here.
- Measured at this revision (read-only scan against the real corpus, 225
  valid nodes): 202 nodes carry exactly one distinct `commit <sha>` citation,
  20 carry none, 3 carry more than one distinct sha (ambiguous). Of the 202,
  every recorded sha resolves locally via `git cat-file -e` (no shallow-clone
  gap hit in this worktree); running `git diff --name-only <sha> -- <cited
  paths>` for each took ~7s total for the whole corpus and reported 192 of
  202 with at least one cited file changed since the recorded revision, 10
  with none changed among their own cited files.
- This worktree's repo is a shallow clone (`git rev-parse
  --is-shallow-repository` -> true), so a recorded sha that predates the
  shallow boundary is a real, expected failure mode the builder must degrade
  out of gracefully (reported as "cannot verify locally", never as stale).

STEP 1 [independent]

Write `launchpad/project-intelligence/corpus/index_defs/stale_docs.py`
exposing `SPEC` (dict form): `name="stale-docs"`,
`output_path="generated/stale-docs.md"`, `node_id="generated-stale-docs"`,
`node_type="governance"` (same reasoning as `orphaned_docs.py`/
`coverage.py`/`decision_index.py`: the subject is the corpus's own currency,
a governance concern about the corpus itself), `audiences=("agent",
"developer", "reviewer")`, `relationships=({"type": "references", "target":
"corpus-agents"},)` only (no `implements`, per ALREADY-TRUE above).
`generate(ctx)` renders two clearly separated sections:
1. **No revision-pinning FACT** (primary, structurally deterministic, no git
   needed): every valid node with zero `commit <sha>`-shaped citations
   anywhere in its evidence ledger. Immediately computable from `ctx` alone.
   Also renders a companion **Ambiguous revision** table: valid nodes citing
   more than one distinct commit sha (no rule picks a winner among them --
   reported, not resolved).
2. **Commit-freshness comparison** (secondary, explicitly labeled
   best-effort): for the remaining nodes (exactly one distinct commit sha),
   loads `coverage.py` as a sibling module (identical pattern
   `orphaned_docs.py` already uses) to reuse `_node_file_citations` for the
   node's other openable citations, then shells `git cat-file -e <sha>`
   scoped to the repository root (three-levels-up derivation copied verbatim
   from `orphaned_docs.py`/`coverage.py`) before ever running `git diff
   --name-only <sha> -- <paths>` -- a sha that does not resolve locally (git
   binary missing, or the shallow-clone gap) lands in a "cannot verify
   locally" bucket, never in "stale". Buckets, each rendered as its own table
   even when empty: cannot verify locally; no other file citations to
   compare; at least one cited file changed since the recorded revision
   ("possibly stale", changed paths named); none of the cited files changed
   ("no signal of staleness"). Every subprocess call is wrapped so a missing
   git binary degrades the whole section to a stated limitation rather than
   crashing generation.
`extra_evidence(ctx)` names the digest, the counts in both sections, and
discloses that the commit-freshness comparison reads live git history
outside `ctx.input_digest` (the same digest-uncovered disclosure pattern
`coverage.py`/`orphaned_docs.py`/`decision_index.py` already use). Module
docstring records the `node_type` reasoning, the audit-report (not index)
framing, and states plainly that the freshness bucket is a narrowing signal
per AGENTS.md's own documented limits, not a certification that a stale-flagged
claim is actually wrong or that a fresh-flagged one still holds.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --only stale-docs` exits 0 and writes `generated/stale-docs.md`.

STEP 2 [needs 1] <- RUNS HERE

Confirm determinism and validity: rerun `--only stale-docs`, diff against the
first write (must be empty, modulo the live-git-read caveat already disclosed
-- rerun back-to-back within the same revision so no intervening commit can
change the answer); run `--check --only stale-docs` (must exit 0); run
`python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0,
pre-existing UNVERIFIED notices allowed).
done when: no-change rerun is byte-identical, `--check` exits 0, and `validate.py` exits 0.

STEP 3 [needs 1]

Write `launchpad/project-intelligence/corpus/tests/test_index_stale_docs.py`
following `test_index_orphaned_docs.py`'s fixture-node pattern and
`test_index_coverage.py`'s fixture-repo-root pattern, extended with a real
hermetic git repository (`git init` + `git config` + `git commit` inside the
temp root) so both the "possibly stale" and "no signal of staleness" buckets
are exercised deterministically rather than only asserted against the live
buzz repository. Cover: builder discovered with declared identity (no
`implements`); two-run byte-identical output; a fixture node with no commit
citation lands in "no revision-pinning FACT"; a fixture node with two
distinct commit citations lands in "Ambiguous revision"; a fixture node
citing a real local commit sha plus a file committed then left unmodified
lands in "no signal of staleness"; a fixture node citing a real local commit
sha plus a file modified after that commit lands in "possibly stale" naming
the changed path; a fixture node citing a sha that does not exist in the
fixture repo lands in "cannot verify locally"; front matter carries
`generated-stale-docs` / `governance`; a read-only smoke test against the
real committed document.
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_index_stale_docs.py"` runs this file's tests standalone and every one passes.

STEP 4 [needs 1, 3]

Self-review the full diff against #904's DoD line by line (exactly one
generated document; generator-produced, proven by the Step 2 rerun-diff;
every evidence citation names a file actually inspected in this task;
`validate.py` exit 0 already confirmed in Step 2; the fallback framing is
honest and does not overclaim a deterministic staleness verdict the tooling
cannot actually support).
done when: self-review completed and noted in the commit body (batch mode: no separate review-code pass).

STEP 5 [needs 1, 3]

Run the full corpus test suite gate command
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
and confirm OK with more than the 225-test base branch baseline, then commit
(builder module, generated file, test file, this plan) as the sole other tool
call.
done when: gate command reports OK and the signed commit exists.

PARALLEL

Steps 1 and (2, 3) are sequential on the builder module existing; 2 and 3 can
run independently of each other once 1 lands, both gating 4 and 5. There is no
genuine multi-agent parallelism available in this single-file, single-builder
task -- everything after Step 1 depends on its output.

GATES

- No-change rerun byte-identical (Step 2).
- `indexes.py --check --only stale-docs` exit 0 (Step 2).
- `validate.py` exit 0 (Step 2).
- Full corpus test suite OK, above the 225-test baseline (Step 5).
- Signed commit only after the gate command passes (Step 5).

BUDGET

One new builder module (~200-260 lines with its docstring, following the
`orphaned_docs.py` precedent length -- somewhat longer because of the git
subprocess plumbing), one generated Markdown file (framework-rendered), one
test file (~180-230 lines following `test_index_orphaned_docs.py`, plus the
small git-fixture setup), this plan file. No edits to `indexes.py`,
`coverage.py`, `validate.py`, or any other shared/framework file.

OPEN

- Whether the "possibly stale" bucket should eventually be tightened (e.g.
  excluding cited files so broadly shared that nearly every node touching
  them is flagged, per the measured 192-of-202 rate) -- left as a reviewer
  call; narrowing the rule to "look fuller" or "look cleaner" is exactly what
  the dispatch brief warns against, so this task reports the honest rate
  rather than filtering it down.
- Whether #1321 (unlanded corpus standard for provenance) later changes what
  "the recorded revision" means well enough to retire the "narrowing step,
  not a certification" framing -- not this task's to decide.

LEFT OUT

- Any claim that the commit-freshness comparison proves a FACT is now false,
  or that an unflagged node's FACT still holds -- AGENTS.md is explicit that
  this is a narrowing step only, and this task does not extend that.
- Recomputing citation-shape classification independently of
  `validate._COMMIT_CITATION_RE` / `coverage._node_file_citations` -- reused
  verbatim so this document cannot silently disagree with what `validate.py`
  itself would classify.
- Any second hand-authored canonical corpus document, or product-behavior
  change -- out of scope per #904's own "Out of scope" list.
- Deciding whether this report becomes a CI or validate gate -- not this
  document's job.
