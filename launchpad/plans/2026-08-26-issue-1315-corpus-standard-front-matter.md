Issue #1315 — task: document corpus standard for front matter
Stated size: no `Size` line  ->  cap: 5 steps (per the batch brief: a single document
written against conventions #636 already settled)

Target file: `launchpad/docs/corpus/standards/front-matter.md`
Node id: `corpus-standard-front-matter` (assigned in the task prompt; permanent)
Branch: `task/1315-corpus-standard-front-matter`
Base: `origin/task/636-corpus-agents-md` @ `ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109`
Merge target: `launchpad`

ALREADY TRUE (verified against git, not notes)

- `git status --short` in this worktree is empty; `HEAD` is
  `ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109`, and `git cat-file -e` on it exits 0.
- `launchpad/docs/corpus/standards/` does not exist. `git ls-tree -r --name-only HEAD
  -- launchpad/docs/corpus` lists exactly one node outside `schema/`: `AGENTS.md`.
- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists
  `schema/` only. On the merge target there is no node carrying id `corpus-agents`,
  so a relationship targeting it would validate here and be a hard error there.
- `launchpad/docs/corpus/schema/node.schema.json` exists and sets
  `additionalProperties: false` with `required: [id, type, status, origin, audiences,
  evidence]`. There is no `provenance` property.
- `launchpad/project-intelligence/corpus/validate.py` exists and passes on the tree as
  it stands. `_load_frontmatter` splits on `---\n` with `maxsplit=2` and binds the third
  part to `_body`, which is never read again.
- `AGENTS.md` (the instruction node governing this subtree) already states the create
  procedure, the citation-shape table, and that field lists and enums must not be
  restated in prose. It flags the citation table as provisionally located, moving to
  #1314.
- `grep -rn audiences launchpad/` matches `node.schema.json`, `schema/README.md`,
  `AGENTS.md`, the corpus and schema test fixtures, and four files that use the ordinary
  English word rather than the field (`REQUIREMENTS.md`, the #622 and #636 plans, and
  `scripts/testdata/pr86-compare.json`). No code reads the field: `grep -n audiences
  launchpad/project-intelligence/corpus/validate.py` returns nothing.
- Probes already run against a throwaway `--root` established six behaviours, all
  reproducible: an injected `provenance:` fails `additionalProperties` without naming
  the offending field; a duplicate key is a hard error naming the key only when it is a
  schema property; `status: no` coerces to a bool and fails `enum`; `id: 2026-08-26`
  coerces to a date, fails `type`, and loses the friendly node label; a missing closing
  `---` reports `not enough values to unpack (expected 3, got 2)`; and an unquoted value
  containing ` #` silently truncates and still passes.

STEP 1  Record the front-matter behaviour probes at this `HEAD`   [independent]
        Re-run every probe already drafted, and add the two not yet run: a bare `---`
        line inside front matter, and a `relationships` block placed after it.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py --root
        <scratch>/probe/<case>` has been run for every case, each exit status and message
        recorded in `scratchpad/i1315/probe-results.txt`, and the inner-`---` case is
        confirmed to exit 0 with the post-delimiter fields absent from the parsed mapping.

STEP 2  Write the node's front matter and evidence ledger         [needs 1]
        `launchpad/docs/corpus/standards/front-matter.md` gets the assigned id,
        `type: governance`, `status: active`, `origin: launchpad`,
        `audiences: [agent, reviewer]`, no `relationships`, and a ledger with exactly one
        commit-only FACT (the revision) plus one entry per substantive body claim.
        done when: parsing the file's front matter with PyYAML and printing its sorted
        keys yields exactly `['audiences', 'evidence', 'id', 'origin', 'status', 'type']`,
        and the ledger contains exactly one `commit ` citation.

STEP 3  Write the body                              [needs 2]  <- RUNS HERE
        Scope and authority, MUST vs SHOULD split, a field-purpose table (what each field
        is FOR, never its accepted values), the YAML and delimiter hazards from STEP 1,
        the closed-field-set consequence including the absence of `provenance`, the fields
        nothing consumes yet, enforcement and exception process, an explicit paragraph
        giving the REAL reason this node declares no `relationships` (merge order -- the
        node it would point at is not on `launchpad` yet -- not "the corpus is empty",
        which AGENTS.md records as a false justification two sibling agents already
        produced), and a scope-and-omissions section carrying both the boundary and the
        expected-but-unverified disclosure.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0,
        and `python3 <scratch>/check-no-enum-restatement.py
        launchpad/docs/corpus/standards/front-matter.md
        launchpad/docs/corpus/schema/node.schema.json` exits 0. That script walks every
        `enum` array in the schema at any depth and fails if three or more DISTINCT
        members of any one enum appear in the body as whole words. It replaces a
        hand-written grep an earlier draft used, which a review-plan pass defeated by
        pasting ten of the thirteen `type` members -- the grep matched only the words its
        author thought of. The script is verified in both directions before use: it must
        exit 1 on that same paragraph, and it must report per-enum hit counts rather than
        a bare verdict, so a near-miss (two of five) is visible rather than silently
        passing.

STEP 4  Audit the node against AGENTS.md and the merge target     [needs 3]
        Walk `AGENTS.md`'s create procedure step by step against the finished node, and
        record every point where following it literally did not work.
        done when: `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
        has been re-run and confirms no node id this document targets;
        `git diff --name-only ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109 -- <every path in
        the ledger>` returns empty; and `scratchpad/i1315/agents-md-findings.md` names one
        line per deviation or is explicitly empty.

STEP 5  Re-check the base, run both suites, and commit            [needs 4]
        Re-fetch the base and merge it if it moved, then run each suite and the validator
        as the last segment of its own command so the verify-gate stamp lands.
        done when: `git fetch origin` then `git rev-parse origin/task/636-corpus-agents-md`
        is an ancestor of `HEAD`; `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` exits 0; `python3 -m
        unittest discover -s launchpad/docs/corpus/schema/tests -p "test_*.py"` exits 0;
        `python3 launchpad/project-intelligence/corpus/validate.py` exits 0; and `git log
        --format=%B -1` shows a `Signed-off-by` trailer.

PARALLEL  None of the five may run as parallel subagents. STEPs 2, 3 and 4 all write or
          read the same single file, and STEP 1's recorded behaviours are the evidence
          STEP 3's claims cite, so STEP 3 cannot start before STEP 1 finishes. STEP 1 is
          tagged `[independent]` because it touches no repository file at all -- it runs
          entirely under `--root <scratch>` -- but there is nothing for it to run beside.

GATES     `review-code` after STEP 5; the diff is one authored document, and `review-code`
          is the applicable artefact reviewer. `review-tests` does not apply: the diff adds
          no test file and changes none -- confirm with `git diff --name-only` before
          skipping it, rather than assuming. `review-adjudicate` over every finding raised.
          Then the cross-model Codex final pass, which the batch brief records as failing
          on credits (#1467); if it fails, `review-final` runs as a labelled same-vendor
          stand-in and the PR says so in Not verified. `qa` explore mode does NOT apply:
          the change adds a Markdown document and no runtime interface, and the only
          executable surface it touches -- `validate.py` -- is exercised directly by
          STEP 1's probes and STEP 5's suites.

BUDGET    STEP 3 will eat the budget. The whole difficulty of this issue is writing a
          document about front matter that does not reproduce front matter. The enum
          detector is a floor, not a ceiling: it catches a restated enum, and it cannot
          catch a paraphrased field-combination matrix ("a FACT may not carry a
          confidence") because that sentence names no enum member. Only a reader catches
          that one, which is why `review-code` follows. Expect to draft the field-purpose
          table more than once.

REVIEW    `review-plan` ran on this plan before STEP 1 and was NOT independent -- the
          same session authored it. It raised three findings, all fixed in this document
          rather than deferred, because a plan defect found pre-build is the gate working
          rather than a defect shipping: (1) High -- STEP 3's original grep passed a
          paragraph restating ten of thirteen `type` members verbatim; replaced with the
          schema-derived detector above. (2) Medium -- STEP 3 never required the
          `relationships: none` justification to reach the body, the exact omission
          AGENTS.md records twice; now an explicit body item. (3) Low -- the ALREADY TRUE
          `audiences` claim under-reported its matches; corrected, and the conclusion it
          supported was re-verified directly against `validate.py`. All three are carried
          into the PR body rather than dropped.

OPEN      1. Whether `developer` belongs in `audiences`. The schema offers it and nothing
             in the repository decides it; #636 chose `agent` and `reviewer`. This plan
             follows #636 and states the reason in the body rather than treating the
             question as settled -- the corpus's authors today are agents and its checkers
             are human reviewers, and no part of this document addresses product
             development. Flag it if a reviewer disagrees; do not re-decide it silently.
          2. Whether `type: governance` is right. The enum's nearest alternatives are
             `development` and `agent`. `governance` is chosen because the document states
             policy binding every corpus node rather than instructing one worker, which is
             what distinguishes it from #636's `agent`. A justification, not a fact.
          3. Whether any citation-shape material belongs here at all. `AGENTS.md` says
             that table moves to #1314. This plan reproduces none of it and links #1314.

LEFT OUT  - `confidence` semantics -- owned by #1309.
          - Citation forms and the evidence ledger's own contract -- #1314 and #1308.
          - `id` naming rules -- #1317. `status` semantics -- #1311 and #1323.
            `type` taxonomy -- #1324. Each is referenced, none settled.
          - Generated-artifact provenance -- #1316.
          - Any edit to `launchpad/docs/corpus/AGENTS.md`. Defects found in it are
            reported in the PR body and filed as issues, never fixed on this branch: it is
            another issue's file and a sibling agent may hold it.
          - Fixing the two `validate.py` defects these probes surface (the opaque
            missing-delimiter message, and the inner-`---` truncation passing clean). Both
            are validator behaviour owned by #623's successor work; they are documented as
            hazards here and filed as issues per the findings policy.
