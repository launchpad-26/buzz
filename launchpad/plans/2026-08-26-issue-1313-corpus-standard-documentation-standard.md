Issue #1313 — task: document corpus standard for documentation standard
Stated size: none  ->  cap: 5 steps (per the batch brief: single document against
established conventions; Serina's 8-step cap for #636 applied only while conventions
were unsettled)

Target file: `launchpad/docs/corpus/standards/documentation-standard.md`
Node id (assigned, permanent): `corpus-standard-documentation-standard`
Branch: `task/1313-corpus-standard-documentation-standard`
Base: `origin/task/636-corpus-agents-md` @ `ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109`

---

THE SUBJECT IS AMBIGUOUS — READ THIS BEFORE THE STEPS

"a corpus standard for documentation standard" has at least three readings, and the
issue body does not settle it. No line in #1313 disambiguates: its Objective is the
family boilerplate ("the single canonical policy node for <topic>", with the topic slot
filled by the string "documentation standard"), and its four subject-specific done
clauses are carried verbatim by all nineteen sibling standard issues (#1307-#1325 —
verified, all 19 contain all four clause strings). So nothing in the issue picks a
reading; the reading is an author decision that this plan must state rather than bury.

The three readings:

  (a) THE META-STANDARD — what a corpus *standard* document must itself be and
      contain: required sections, how it states requirements, how it names what
      enforces them, how it defers instead of duplicating.

  (b) PROSE-QUALITY STANDARD — register, structure, lookup-not-narrative, across all
      corpus nodes.

  (c) APEX/UMBRELLA CHARTER — what "the documentation standard" is as a whole: which
      documents it governs, whose authority it carries, what conformance means.

BUILDING (a). The reasons, in order of weight:

  1. (b) is already owned elsewhere. Of the nineteen sibling standards, #1320 owns
     normative language, #1307 atomicity, #1319 naming, #1324 taxonomy, #1312
     diagrams, #1315 front matter. What (b) would add beyond those is house style,
     and `launchpad/docs/corpus/AGENTS.md` already carries that guidance ("Look up
     the section you need; this is a reference, not a tutorial"). A node whose
     content is other nodes' content violates the very rule #1307 states.

  2. (a) is a demonstrable, currently-unowned gap. The nineteen standards are being
     authored in parallel with no shared shape, and no sibling task defines one:
     #1326-#1351 are twenty-six templates, every one named for a *content* node type
     (component, capability, concept, runbook, ...), none for a standard. #1344 is
     the nearest ("policy corpus template") and does not close the gap — `policy` is
     not a member of the `type` enum in `launchpad/docs/corpus/schema/node.schema.json`,
     while `governance` is, and all four standards drafted so far declare
     `type: governance`.

  3. The gap is already producing measured drift. Four sibling standards exist on
     pushed branches with open PRs. They converged, independently, on a recognisable
     shape (scope-and-authority first, MUST/SHOULD split, an enforcement section that
     states what is *not* enforced, exceptions-and-escalation, scope-and-omissions
     last) and diverged on at least seven points, including four different H1 title
     conventions across four documents. Convergence shows the shape is natural;
     divergence shows nothing holds it.

  4. The requirement (a) would codify exists today only in GitHub issue bodies. Those
     four clauses vanish from the project's reach when the issues close. A corpus
     whose Feature outcome is "the documentation corpus contract is executable" (#605)
     cannot leave its own document contract living in closed issue checklists. This is
     the strongest argument for (a) and is the document's reason to exist.

     CORRECTED AFTER REVIEW-PLAN: an earlier draft of this plan called those four
     clauses the *standards family's* contract. They are not. Sampling the template
     issues (#1326, #1330, #1344, #1346, #1351) shows all five carry the same four
     clause strings verbatim, so they are #605 batch-wide boilerplate covering both
     families, not evidence of a standards-specific contract. The document must say
     that accurately. It scopes them to `standards/` because that is the family this
     file sits in and the only family for which drafted evidence exists — not because
     the clauses are unique to it. The template family's own required-content rule is
     a different list (#605's acceptance criterion: purpose, required sections,
     evidence expectations, and the industry model adapted) and is owned elsewhere.

  5. (c) is not excluded so much as deferred: (c) is what `AGENTS.md` plus #639 (the
     human-facing entry point) already do between them, and #1313's Objective names a
     *standard*, not a charter. Where (a) needs a scope-and-authority statement it
     will make one, which is (c) at the size (a) actually requires.

IF SERINA INTENDS (b) OR (c), the piece that changes is the scope section, not the
whole document — say so and it is a bounded edit, not a rewrite. This is flagged in
OPEN below and will be flagged in the PR body.

---

ALREADY TRUE  (verified against git in this worktree, not from notes)

  - Worktree exists at `__worktrees/task-1313-corpus-standard-documentation-standard`,
    branch `task/1313-corpus-standard-documentation-standard`, HEAD `ebe2daf72`,
    working tree clean (`git status --porcelain` empty).
  - `launchpad/docs/corpus/standards/` does not exist on this branch. The only
    non-`schema/` corpus node here is `launchpad/docs/corpus/AGENTS.md`.
  - On the merge target, `git ls-tree -r --name-only origin/launchpad --
    launchpad/docs/corpus` returns `schema/` paths only. No node id is resolvable
    there, so no `relationships` entry can be declared without a hard CI error.
  - `validate.py` never reads body prose: `_load_frontmatter` splits the file and
    discards `_body`. Nothing downstream of it receives the body.
  - `validate.py` has exactly one directory-keyed rule — `EXCLUDED_TOP_LEVEL_DIRS =
    {"schema"}`, applied by `_is_excluded` — and nothing below it distinguishes
    `standards/` from any other path under the corpus root. (CORRECTED after
    review-code: this line originally claimed *no* directory-keyed rule at all, which
    the cited file falsifies on sight and which `AGENTS.md` already states correctly.
    The corrected claim is what the node now carries.)
  - `node.schema.json` `type` enum contains `governance`; it contains no `policy`.
    `required` is id/type/status/origin/audiences/evidence; `additionalProperties` is
    false, so there is no `provenance` field.
  - Four sibling standards exist and were read at pinned revisions:
    atomicity `b899609f677317ebde4ba16620b3dd23b1510d62` (PR #1470),
    code-references `5f7e1330b2d422129bb92148c5d4a2ee4cc8958e` (PR #1480),
    confidence `e8ba1ec8e2d605ecfbc6a7d9ee0ca058e95a2d24` (PR #1468),
    decision-references `8eb2d2658a707c025ba7bcf1c2f2063f5de2e387` (PR #1477).
    All four PRs are open, so the SHAs stay reachable on GitHub.
  - All nineteen issues #1307-#1325 carry all four policy-node done clauses verbatim
    (checked by string match over `gh issue list --json body`).
  - `codex exec` is reported out of credits as of 2026-08-26 (#1467). The cross-model
    pass is expected to be unavailable; it will still be attempted.

---

STEP 1  Build the evidence inventory and fix the front-matter choices  [independent]
        Per AGENTS.md "Creating a node" step 3, before any drafting.
        Records: the revision; every source path/symbol read; every intended claim
        with its class (FACT / INFERENCE / TEAM_KNOWLEDGE) and its citation; and,
        separately, everything expected but not verifiable. Fixes `type: governance`
        (schema enum has no `policy`; all four siblings chose it), `status: active`,
        `origin: launchpad`, `audiences: [agent, reviewer]` — no `developer`, because
        a standard governing how corpus standards are written addresses the agents
        that write them and the reviewers that hold them, and nothing in it is
        addressed to a developer changing product code; three of the four siblings
        made the same call and code-references, which added `developer`, governs
        citations to source that a developer would write. Fixes `relationships: none`
        with the real reason: merge order, not an empty corpus.
        done when: `scratchpad/i1313/evidence-inventory.md` exists; every intended
        claim in it has a class and at least one citation; and re-running
        `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus |
        grep -cv '^launchpad/docs/corpus/schema/'` prints `0`, confirming the
        no-relationships reason is still true at planning time.

STEP 2  Create the node: front matter plus six section headings  [needs 1]  <- RUNS HERE
        Then validate it against the real checker.
        The ledger carries exactly one commit-only FACT (the recorded revision), and
        every claim about a sibling draft is a FACT citing a pinned
        `blob/<full-sha>/<path>` GitHub URL, since those files exist at no path in
        this tree and a bare path citation would be a hard validation error.
        Claims whose only source is a GitHub issue are TEAM_KNOWLEDGE with
        `provided_by` naming the issue, per AGENTS.md.
        done when: `cd <worktree> && python3
        launchpad/project-intelligence/corpus/validate.py` exits 0 and its output
        contains `PASS`; the new file is present in `git status --porcelain
        launchpad/docs/corpus/standards/`; and `grep -c '^## '` on it returns 6.
        (The heading count is checked HERE, in the step that claims to produce the
        headings — an earlier draft deferred it to step 3, which made this step
        satisfiable by a file with front matter and no body at all.)

STEP 3  Write "Scope and authority" and the normative body                 [needs 2]
        MUST and SHOULD as two separate, individually numbered sections.
        Scope names what the standard governs (documents under
        `launchpad/docs/corpus/standards/`), where its authority comes from (the four
        done clauses #605 puts on every authored document in this batch — stated as
        batch-wide, NOT as standards-specific, per the correction above — plus
        ADR-0028's choice of a human-read Markdown diff as the review surface), and
        the precedence rule: where this and the schema, the validator or an ADR
        disagree, they win. MUSTs cover the required sections and their order; the
        MUST/SHOULD separation; that every requirement names what enforces it or
        declares itself unenforced; and that a standard defers to the
        schema/validator/ADR it depends on rather than restating it.
        NO "one topic per standard" MUST. Review-plan found that it duplicates
        atomicity's A1 ("a corpus node MUST document exactly one independently
        maintainable idea"), which is generic over corpus nodes and so already binds
        a `governance`-typed standard. Duplicating it is the exact defect this
        document exists to prevent and that #1313's own done clause forbids. The
        scope section links #1307 for it instead.
        SHOULDs cover worked examples, an authoritative-sources table, and boundary
        cases.
        done when: validator still exits 0, and `grep -c '^## '` on the file returns
        at least 6, with `grep -n 'MUST\|SHOULD'` showing the two as distinct
        top-level sections rather than one merged list.

STEP 4  Write the enforcement, exceptions and omissions sections           [needs 3]
        Then reconcile the ledger against the finished body.
        Enforcement states the load-bearing fact plainly: `validate.py` discards the
        body, so *no* requirement in this standard — or in any sibling standard — is
        machine-checked, and pull-request review is the whole of enforcement.
        Omissions names the boundaries against #1320 (wording of normative language),
        #1315 (front-matter fields), #1307 (atomicity — including A1, which this
        document does not restate), #1322 (review requirements: who reviews, to what
        checklist, with what authority — added after review-plan found it missing, and
        the nearest neighbour to this document's enforcement section), #1344/#1346
        (templates), and records that four standards already in flight diverge from
        what this
        document requires, so it is retroactive on them and that is a known cost.
        Reconciliation: every ledger `statement` maps to a body claim and every body
        claim maps to a ledger entry.
        done when: validator exits 0; a scratch script confirms the ledger has exactly
        one entry whose only citation matches `^commit `; and the reconciliation table
        in `scratchpad/i1313/ledger-reconciliation.md` shows no unmatched entry in
        either direction.

STEP 5  Re-check the base, run the full corpus unit suite, and commit.    [needs 4]
        Re-fetch `origin/task/636-corpus-agents-md`; if it advanced, merge it (never
        rebase — the branch is pushed), re-verify every claim made *about*
        `AGENTS.md`, and re-run both checks. Commit with `-s`, message written to a
        file and passed with `-F` (never `-m`: backticks in a double-quoted message
        are executed by the shell).
        Also RE-RUN the merge-target check from step 1 — `git ls-tree -r --name-only
        origin/launchpad -- launchpad/docs/corpus | grep -cv
        '^launchpad/docs/corpus/schema/'` — after the re-fetch. All four sibling PRs
        target `launchpad` directly and are open, so one merging mid-task would make
        the "no relationships, reason: merge order" justification stale with nothing
        else catching it. Review-plan found this gap. If the count is no longer 0,
        stop and reconsider the relationships decision before committing.
        done when: `cd <worktree> && python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` exits 0 as the
        last segment of its command (so the verify-gate stamp lands), the validator
        exits 0 in a separate call, the merge-target check above prints `0` (or its
        non-zero result is reconciled in the node's scope section), and
        `git log --format=%B -1 | grep -c 'Signed-off-by'` prints 1.

---

PARALLEL  Nothing here may fan out. Steps 2, 3 and 4 all edit the single file
          `launchpad/docs/corpus/standards/documentation-standard.md`, and steps 3
          and 4 additionally edit the front-matter ledger inside it, so they are
          sequential by the same-file rule regardless of how separable the prose
          looks. Step 1 writes only to the scratchpad and is tagged independent, but
          it is the input to every later step, so running it "in parallel" buys
          nothing. Any file edit also clears the verify-gate stamp, which makes
          concurrent edits actively harmful to step 5.

GATES     `review-plan` on this plan before step 1 (self-authored, therefore NOT an
          independent review — that must be stated in the report). `review-code`
          after step 5. `review-tests` does NOT apply: the diff adds one Markdown
          node and this plan file, and touches no test file — if that changes, it
          applies. `review-adjudicate` over every finding from those. Then a Codex
          cross-model final pass, which is expected to fail on credits (#1467); if it
          does, `review-final` runs as a labelled same-vendor stand-in, never
          presented as the cross-model gate discharged. `qa` explore mode does NOT
          apply: the change is a documentation node with no runtime interface to
          exercise — the only executable surface it touches is `validate.py`, which
          it exercises as a done-condition rather than as behaviour under test.

BUDGET    Step 3 is the step most likely to overrun. Writing MUSTs for the shape of a
          standard while four standards already exist in four different shapes means
          every requirement has to be checked against what the siblings actually did,
          and each divergence has to be either accommodated or knowingly broken with
          the cost named. The second-largest risk is adjacent and cheaper to
          mismanage: drifting into restating #1320's or #1315's content, which is the
          exact failure this document is supposed to prevent, and which no check can
          see.

OPEN      1. The subject reading. #1313 does not choose between (a), (b) and (c)
             above. (a) is being built, for the four reasons given. If Serina wants
             (b) or (c), the scope section is the bounded change.
          2. Whether standards are `governance` or want a `policy` type. The schema
             enum has no `policy`, #1344 is titled "policy corpus template", and
             `COMPATIBILITY.md` governs adding an enum value. Not this issue's to
             decide; it is named, not resolved.
          3. Whether this standard binds the twenty-six templates (#1326-#1351) or
             only the nineteen standards. Scoped to standards, because that is what
             the file sits among and what the evidence covers; the templates have
             their own required-content clause in #605's acceptance criteria.
          4. Whether a retroactive standard obliges the four in-flight sibling PRs to
             change before merge. Out of scope, recorded as a known cost.

LEFT OUT  - Editing `launchpad/docs/corpus/AGENTS.md` or any sibling's file. Forbidden
            by the batch brief; defects found in AGENTS.md are reported, not patched.
          - Any `relationships` entry. No target resolves on `origin/launchpad`, so
            one would validate here and hard-fail in CI.
          - Adding a validator check that reads body structure. That is a real
            follow-up (it would give this standard teeth) but it is a second artefact
            and #1313's out-of-scope list refuses it; it will be filed as an issue if
            a reviewer raises it.
          - Restating enum member lists or the schema's field-combination matrix.
            The validator never reads body prose, so a stale copy stays green forever.
